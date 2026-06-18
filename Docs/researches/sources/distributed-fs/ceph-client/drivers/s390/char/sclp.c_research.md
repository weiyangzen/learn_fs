<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp.c

**Purpose:** `sclp.c` is the central Service Call Logical Processor core. It serializes SCLP service calls, manages event masks, dispatches incoming event buffers, supports synchronous waiting during early/console contexts, and exposes console-related driver attributes.

**Important APIs and functions:** Public APIs are `sclp_add_request()`, `sclp_sync_wait()`, `sclp_register()`, `sclp_unregister()`, `sclp_remove_processed()`, `sclp_deactivate()`, `sclp_reactivate()`, and `sclp_init()`. Internal state machines track running request state, read-event state, activation state, and mask-initialization state. `sclp_interrupt_handler()` completes service-call requests and queues read-event requests when pending events exist.

**Control flow, state, and persistence:** Requests are appended to `sclp_req_queue` under `sclp_lock`, optionally with queue timeouts. Only one command is active at a time through `active_cmd` and `sclp_running_state`. Interrupts locate the completed request by physical SCCB address, mark it done, call its callback outside the lock, then process the next queued request. Event readers are synthetic read-event requests whose callback dispatches event buffers to registered `struct sclp_register` listeners. Registration recalculates masks and issues Write Event Mask commands.

**Dependencies and integration:** This file integrates with external IRQ subclass `EXT_IRQ_SERVICE_SIG`, s390 `servc`, debugfs-style debug areas, timers, reboot notifiers, and the platform driver named `sclp`. It is the shared backend for console, tty, PCI/AP/CPU/memory configuration, OCF, SD/SDIAS, FTP, and control interfaces.

**Risks and test signals:** Risks include request timeout recovery, callback reentrancy, mask collision handling, malformed event-buffer lengths, synchronous waits with timer interrupts disabled, and deactivation during reboot. Test signals include successful initialization, mask compatibility fallback, event delivery to only registered receivers, queue timeout callbacks, reboot mask reset, sysfs `con_*` attributes, and stress with concurrent request producers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.c -->
