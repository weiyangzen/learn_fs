## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-memory-errors.c

### Purpose
`opal-memory-errors.c` handles asynchronous OPAL memory error messages and converts affected physical address ranges into Linux `memory_failure()` calls.

### Important APIs, Types, And Functions
Key elements are `struct OpalMsgNode`, `opal_memory_err_event()`, `mem_error_work`, `handle_memory_error()`, `handle_memory_error_event()`, and `opal_mem_err_init()`.

### Control Flow
The initcall registers a notifier for `OPAL_MSG_MEM_ERR`. The notifier filters message type, allocates a queue node with `GFP_ATOMIC`, copies the `opal_msg`, appends it to a spinlock-protected list, and schedules work. The worker drains the list outside the spinlock, decodes resilience or dynamic-deallocation ranges from `OpalMemoryErrorData`, and calls `memory_failure()` for each page in the firmware-provided range.

### State, Persistence, And Dependencies
State is the one-time registration flag, a queued message list, and its spinlock. Persistent system effects are page poison/offline handling triggered through the memory failure subsystem. Dependencies include OPAL message notifiers from `opal.c`, endian conversion, kernel workqueues, and memory error data structures.

### Integration Points
This file plugs firmware memory health events into Linux memory failure handling. It is initialized as a PowerNV device initcall, after OPAL message infrastructure is available.

### Risks
The notifier can drop events on allocation failure. Large address ranges schedule one `memory_failure()` per page and may be expensive. Unknown event types are silently ignored, and there is no unregister path. Correctness depends on firmware range end values and page alignment behavior.

### Test Signals
Inject OPAL memory error messages for resilience and dynamic deallocation, unknown types, empty and large ranges, allocation failure paths, concurrent queued events, and verify `memory_failure()` receives page frame numbers derived from big-endian physical addresses.
