# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/adminq.c

## Purpose
`adminq.c` implements the AMD/Pensando core AdminQ and NotifyQ completion path. It posts administrative commands to firmware, waits for completions, processes asynchronous notifications, returns interrupt credits, and bridges queue interrupts to a workqueue context. This is the central command transport used by firmware setup, devlink operations, auxiliary clients, and feature control.

## Important APIs, Types, And Functions
`pdsc_process_notifyq` consumes `union pds_core_notifyq_comp` entries and dispatches link-change and reset events through `pdsc_notify`. `pdsc_process_adminq` drains NotifyQ and AdminQ completions, copies firmware completion data into each waiting command's destination, completes the per-descriptor `struct completion`, flips CQ color at ring wrap, returns interrupt credits, and drops the AdminQ reference. `pdsc_adminq_isr` queues `pdsc_work_thread` to process completions outside hard IRQ context. `pdsc_adminq_post` is exported and synchronously posts a `union pds_core_adminq_cmd` with a caller-provided completion buffer and optional fast-poll behavior.

## Control Flow
Posting starts by taking an AdminQ reference with `pdsc_adminq_inc_if_up`, which rejects posts while the driver is stopping or firmware is marked dead. `__pdsc_adminq_post` takes `adminq_lock`, checks ring space, verifies firmware is running, copies the command into the descriptor at `head_idx`, reinitializes its completion, advances `head_idx`, and rings the kernel doorbell page with the queue id plus new index. The public `pdsc_adminq_post` waits in short slices for completion, checking firmware health between waits. It exponentially backs off polling unless `fast_poll` is requested, converts completion status through `pdsc_err_to_errno`, and queues health work on timeout or lost firmware.

Interrupt flow starts in `pdsc_adminq_isr`, which validates AdminQ availability, queues `adminqcq.work`, and exits. The worker calls `pdsc_process_adminq`; this first processes NotifyQ events by comparing event IDs against `last_eid`, then drains AdminQ completions while CQ color matches. For each completion it copies the completion into `q_info->dest` and completes the waiting command. Credits are returned for both NotifyQ and AdminQ work.

## State And Persistence
State is held in `pdsc->adminqcq`, `pdsc->notifyqcq`, `pdsc->last_eid`, queue head/tail indices, completion objects, CQ done color, `accum_work`, `adminq_refcnt`, and driver state flags. No persistent storage is used. Reference counting is a key lifetime guard: teardown sets firmware-dead state and waits until the AdminQ refcount falls to one before freeing queues.

## Dependencies And Integration Points
The file depends on queue structures from `core.h`, firmware ABI types from `pds_adminq.h`/`pds_core_if.h`, dynamic debug hex dumps, interrupt credit helpers from `pds_intr.h`, workqueues, completions, refcounts, and the blocking notifier wrapper in `core.c`. It is used by `auxbus.c`, `devlink.c`, `fw.c`, and core setup paths.

## Risks
Ring full detection and head/tail arithmetic must leave one descriptor empty; off-by-one errors can corrupt in-flight commands. Completion waiting deliberately completes timed-out descriptors to prevent later waits from hanging, but late firmware writes can still race with command-lifetime expectations. NotifyQ processing assumes event IDs increase and stops when the next event ID is not greater than `last_eid`. Firmware health loss while commands are outstanding must route to health recovery without freeing queues under active users.

## Test Signals
Tests should exercise successful AdminQ commands, ring-full returns, timeout and firmware-down paths, NotifyQ link/reset event propagation, interrupt-to-workqueue completion, `PDS_AQ_FLAG_FASTPOLL` behavior, and teardown while commands are active. Dynamic debug command/completion dumps and `debugfs` queue counters are useful observability signals.
