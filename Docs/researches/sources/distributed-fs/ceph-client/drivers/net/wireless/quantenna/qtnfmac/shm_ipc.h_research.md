## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.h

### Purpose
`shm_ipc.h` declares the qtnfmac shared-memory IPC object, callback contracts, direction enum, ACK timeout, and public send/init/free interface.

### Important APIs, Types, And Functions
Key types are `struct qtnf_shm_ipc_int`, `struct qtnf_shm_ipc_rx_callback`, `enum qtnf_shm_ipc_direction`, and `struct qtnf_shm_ipc`. The inline `qtnf_shm_ipc_irq_handler()` dispatches to the direction-specific handler installed by initialization.

### Control Flow
Callers allocate `struct qtnf_shm_ipc`, initialize it with a shared region, workqueue, interrupt callback, and RX callback, then call `qtnf_shm_ipc_irq_handler()` from hardware/bus IRQ handling. Outbound users call `qtnf_shm_ipc_send()` and inbound users receive data through the callback.

### State, Persistence, And Dependencies
The structure stores packet and timeout counters, a `waiting_for_ack` byte observed with `READ_ONCE`/`WRITE_ONCE` in the implementation, a work item, and completion. It depends on workqueue, completion, mutex/spinlock headers, and `shm_ipc_defs.h`.

### Integration Points
PCI or other bus transport code embeds this object for bidirectional host/firmware signaling, using separate inbound and outbound instances over shared MMIO regions.

### Risks
The header does not encode locking requirements for callers; external send serialization and teardown/workqueue flushing are part of integration discipline. Callback pointers are copied and assumed valid for the IPC lifetime.

### Test Signals
Compile-time coverage for both directions, IRQ dispatch before and after init, send serialization tests, callback lifetime teardown tests, and counter inspection under error paths are useful.
