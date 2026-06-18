# sources/distributed-fs/ceph-client/drivers/char/apm-emulation.c

## Purpose

`apm-emulation.c` provides a BIOS-less `/dev/apm_bios` compatibility layer, originally for ARM, on top of Linux power-management notifiers. It lets legacy APM userspace read power events, acknowledge suspend requests, request suspend, and read `/proc/apm` status supplied by platform code.

## Important APIs, Types, And Functions

- `struct apm_queue` is a 16-event circular buffer.
- `enum apm_suspend_state` models per-file suspend acknowledgement state.
- `struct apm_user` is per-open state, including reader/writer/root flags, suspend result/state, and event queue.
- Exported hooks: `apm_get_power_status` function pointer and `apm_queue_event()`.
- Device operations: `apm_open()`, `apm_release()`, `apm_read()`, `apm_poll()`, and `apm_ioctl()`.
- PM/event machinery: `kapmd()`, `apm_suspend_notifier()`, `queue_event()`, and queue helpers.
- Init/exit: miscdevice `apm_device`, proc show function `proc_apm_show()`, PM notifier registration, `apm_setup()` boot parameter.

## Control Flow

Init creates `kapmd`, creates `/proc/apm` when procfs is enabled, registers `/dev/apm_bios`, and registers a PM notifier. External kernel code calls `apm_queue_event()`, which queues to `kapmd_queue` under spinlock and wakes `kapmd`. The thread forwards status-change events to all readers or calls `pm_suspend()` for suspend events. During PM suspend/hibernate prepare, the notifier queues suspend events to privileged reader/writer file handles, increments `suspend_acks_pending`, wakes readers, and waits up to five seconds for `APM_IOC_SUSPEND` acknowledgements. Post-suspend queues resume events and wakes acknowledged waiters.

## State And Persistence Behavior

State persists in the global user list, per-open event queues, suspend counters, inhibit counter, `kapmd_queue`, waitqueues, and exported power-status callback. The driver does not persist data across module unload. Event queues drop the oldest event on overflow and log only the first overflow.

## Dependencies And Integration Points

Dependencies include miscdevice, procfs/seq_file, PM notifier APIs, suspend core, freezer-aware waits, capability checks, and APM UAPI definitions. It integrates with platform code through `apm_get_power_status` and `apm_queue_event()`, and with legacy userspace through `/dev/apm_bios`, `APM_IOC_SUSPEND`, poll/read, and `/proc/apm`.

## Risks And Edge Cases

`apm_read()` waits interruptibly but does not check the wait return before reading the queue, so a signal can lead to a zero-length result rather than `-ERESTARTSYS`/`-EINTR`. Queue operations for per-user queues are protected by list locks for producer iteration and state mutex for suspend transitions, but individual queue head/tail updates are not separately locked against concurrent read and PM notifier access. Suspend acknowledgement has deliberate races around timeout: late ACKs become `-ETIMEDOUT`. Only users that opened the device with read/write and had `CAP_SYS_ADMIN` at open time participate in ACKs.

## Test Signals

Functional tests should open `/dev/apm_bios` as reader/writer root, inject `apm_queue_event()` from a platform/test module, verify read/poll events, request suspend via `APM_IOC_SUSPEND`, and test timeout behavior with multiple open handles. PM tests should watch `suspend_acks_pending`, resume events, and `/proc/apm` formatting with and without `apm_get_power_status`. Static analysis should focus on queue concurrency and interruptible wait semantics.
