## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.h

### Purpose
`ivpu_ipc.h` defines the ivpu IPC shared-memory ABI, consumer/message structures, IPC state, and transport API.

### Important APIs, Types, And Functions
It defines boot channel constants, IPC alignment, header status values, `struct ivpu_ipc_hdr`, callback type `ivpu_ipc_rx_callback_t`, `struct ivpu_ipc_rx_msg`, `struct ivpu_ipc_consumer`, and `struct ivpu_ipc_info`. It declares IPC lifecycle, enable/disable/reset, IRQ, consumer, send, receive, and send/receive helper functions.

### Control Flow
The header itself has no flow. The structure design supports two receive paths: synchronous consumers wait on `rx_msg_wq`, while callback consumers queue messages for workqueue processing.

### State, Persistence, And Dependencies
`ivpu_ipc_hdr` is packed and 64-byte aligned because it is shared with firmware. IPC state persists in global BOs, gen_pool allocations, lists, locks, atomic counters, waitqueues, and the on/off flag. Dependencies include Linux interrupt/spinlock APIs and JSM firmware API types.

### Integration Points
It is included by the main driver, firmware boot, JSM message layer, PM, jobs, and any code that sends firmware commands or handles firmware responses.

### Risks
The shared header layout is firmware ABI and must not change without firmware coordination. Consumers must be removed to avoid stale list entries. The boot message uses a special channel and magic data address instead of a JSM payload.

### Test Signals
ABI tests should verify `ivpu_ipc_hdr` size/alignment/field offsets, boot message constants, consumer add/delete behavior, synchronous and callback receive paths, and disabled/reset state transitions.
