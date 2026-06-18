<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.c

## Purpose
Implements the `bng_re` RoCE firmware communication channel. It allocates command and completion queues, maps doorbell/mailbox BAR regions, starts/stops the CREQ IRQ and tasklet, sends command queue messages, waits for completions, processes firmware events, and initializes/deinitializes firmware.

## Important APIs, Types, And Functions
- `bng_re_alloc_fw_channel()` allocates CREQ and CMDQ hardware queues plus the command-response shadow table `crsqe_tbl`.
- `bng_re_free_rcfw_channel()` frees the shadow table and both hardware queues.
- `bng_re_rcfw_send_message()` is the main synchronous command path used by higher-level slow-path code.
- `__send_message_basic_sanity()` rejects commands during firmware stall, duplicate initialization, or unsupported commands before firmware initialization.
- `__send_message()` assigns a cookie, records a `bng_re_crsqe`, copies the request into 16-byte CMDQ slots, advances producer state, and rings the CMDQ mailbox doorbell.
- `__wait_for_resp()` sleeps on `cmdq.waitq`, manually services CREQ on timeout intervals, and returns when the shadow entry is no longer in use.
- `bng_re_service_creq()` drains CREQ entries in a tasklet up to `BNG_FW_CREQ_ENTRY_POLL_BUDGET`, dispatching QP events and function events, advancing consumer/epoch state, ringing the NQ doorbell, and waking waiters.
- `bng_re_process_qp_event()` handles command completions by cookie and copies firmware response data into the caller's response buffer.
- `bng_re_map_cmdq_mbox()` and `bng_re_map_creq_db()` map PCI BAR regions for command producer/trigger and CREQ consumer doorbells.
- `bng_re_rcfw_start_irq()` / `bng_re_rcfw_stop_irq()` request/free CREQ IRQs and manage tasklet lifetime.
- `bng_re_enable_fw_channel()` maps MMIO, starts IRQs, writes initial CMDQ context to firmware, and prepares the first command doorbell.
- `bng_re_init_rcfw()` sends `INITIALIZE_FW`; `bng_re_deinit_rcfw()` sends `DEINITIALIZE_FW`.

## Control Flow
Allocation starts with a CREQ queue sized by `BNG_FW_CREQE_MAX_CNT`, then a CMDQ queue sized by `BNG_FW_CMDQE_MAX_CNT`, then a zeroed `crsqe_tbl` indexed by command cookie. Channel enablement initializes sequence and waitqueue state, maps the CMDQ mailbox and CREQ doorbell, starts the IRQ/tasklet, arms the CREQ/NQ doorbell, and writes `cmdq_init` to the mapped mailbox.

To send a command, `bng_re_rcfw_send_message()` extracts the opcode, runs sanity checks, calls `__send_message()`, derives the cookie from the request, waits for response, and reports firmware status as `-EIO`. `__send_message()` holds the CMDQ lock while checking free slots, filling the cookie, recording waiter state, setting side-buffer response address/size if present, copying request bytes across command queue entries, incrementing sequence/producer state, and issuing MMIO writes with a write barrier.

The interrupt handler schedules the CREQ tasklet. The tasklet loops while entries are valid for the current epoch, uses a DMA read barrier before reading the entry body, dispatches event type, advances the consumer and epoch via `bng_re_hwq_incr_cons()`, rings the NQ doorbell if entries were processed, and wakes command waiters. Teardown masks interrupts, synchronizes and frees IRQ, kills/disables the tasklet, unmaps BARs, deinitializes firmware, frees stats resources in the caller, and frees queues.

## State And Persistence
Persistent channel state is in `struct bng_re_rcfw`: PCI device, resource root, CMDQ context, CREQ context, shadow response table, cookie table lock, depth, timeout, and interrupt-enabled count. CMDQ state includes hardware queue indices, mailbox MMIO pointers, flags such as `FIRMWARE_INITIALIZED_FLAG`, `FIRMWARE_STALL_DETECTED`, and `FIRMWARE_FIRST_FLAG`, a waitqueue, and sequence number. CREQ state includes hardware queue, doorbell info, event stats, tasklet, ring id, MSI-X vector, IRQ name, and IRQ availability.

## Dependencies And Integration Points
Depends on `bng_roce_hsi.h` command and event layouts, `bng_res` hardware queue and doorbell helpers, `bng_sp` for device attributes consumed during initialization, PCI BAR mapping APIs, Linux IRQ/tasklet/waitqueue primitives, DMA barriers, and BNGE-provided ring ids/MSI-X information passed from `bng_dev.c`.

## Risks And Edge Cases
`__wait_for_resp()` loops forever unless completion arrives because it does not return a timeout after repeated `wait_event_timeout()` expirations; callers may hang on firmware loss. `bng_re_rcfw_send_message()` only sets `FIRMWARE_STALL_DETECTED` when `rc == -ENODEV`, but `__wait_for_resp()` as written does not produce that status. The sanity path maps `-ENXIO` through `bng_re_map_rc()`, but current checks mostly return `-ETIMEDOUT`, `-EINVAL`, or `-EOPNOTSUPP`. In `bng_re_map_creq_db()`, the zero-resource check tests `reg.bar_id` instead of `reg.bar_base`, so it can log incorrectly and miss a zero BAR base. IRQ start and stop must balance tasklet setup/enable/disable/kill exactly to avoid use-after-free or disabled tasklets.

## Test Signals
Build and boot tests should verify successful CMDQ/CREQ allocation, BAR mapping, IRQ request, first doorbell write, `INITIALIZE_FW`, and `DEINITIALIZE_FW`. Firmware command tests should exercise multi-slot commands, side-buffer responses, full CMDQ returning `-EAGAIN`, firmware status errors, and CREQ event dispatch. Fault injection should cover BAR map failure, IRQ request failure, command timeout/stall, and remove while interrupts are active. Lockdep/KCSAN and DMA debug are useful for CMDQ/CREQ locking and barrier correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_fw.c -->
