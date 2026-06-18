## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc.c

### Purpose
`shm_ipc.c` implements a simple shared-memory IPC channel used by qtnfmac transports. It sends one packet through a 4 KiB MMIO/shared region, signals the peer via a caller-provided interrupt callback, and waits for an ACK flag; inbound packets are drained from workqueue context and delivered to a receive callback.

### Important APIs, Types, And Functions
Public functions are `qtnf_shm_ipc_init()`, `qtnf_shm_ipc_free()`, and `qtnf_shm_ipc_send()`. Internal handlers are `qtnf_shm_ipc_has_new_data()`, `qtnf_shm_handle_new_data()`, `qtnf_shm_ipc_irq_work()`, `qtnf_shm_ipc_irq_inbound_handler()`, and `qtnf_shm_ipc_irq_outbound_handler()`.

### Control Flow
Initialization validates shared-region layout at build time, stores callbacks, selects an inbound or outbound IRQ handler, initializes work and completion state, and clears counters. Inbound IRQ handling checks `NEW_DATA`, queues work, validates `data_len`, calls the RX callback, writes `ACK`, flushes the MMIO write, and interrupts the peer. Outbound send writes `data_len`, copies payload with `memcpy_toio()`, orders writes with barriers, sets `NEW_DATA`, interrupts the peer, waits up to two seconds for completion, then clears `waiting_for_ack`.

### State, Persistence, And Dependencies
State is in `struct qtnf_shm_ipc`: direction, shared-region pointer, counters, `waiting_for_ack`, callbacks, workqueue, and completion. Persistent peer-visible state is `flags`, `data_len`, and data bytes in the shared region. It depends on MMIO accessors, memory barriers, workqueues, completions, and transport-specific interrupt functions.

### Integration Points
Bus implementations use this as a low-level control/data path before higher QLINK command/event handling. RX callbacks usually wrap the shared data into skb/control packets.

### Risks
Only one outstanding TX is modeled; concurrent `qtnf_shm_ipc_send()` calls would race without external serialization. ACK completion can arrive after timeout, so `waiting_for_ack` ordering is important. Inbound data is passed as `__iomem` and must be copied safely by callbacks. Free completes waiters but does not flush queued work here.

### Test Signals
Exercise normal send/ACK, ACK timeout, inbound zero/oversized length rejection, repeated inbound drain while `NEW_DATA` remains set, teardown with a blocked sender, barrier-sensitive payload integrity, and interrupt callback ordering.
