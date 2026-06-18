## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ipc.c

### Purpose
`ivpu_ipc.c` implements the host-firmware IPC transport over shared memory and hardware FIFOs. It allocates TX/RX buffers, sends JSM messages, receives synchronous and callback responses, drains IPC interrupts, and aborts consumers on shutdown.

### Important APIs, Types, And Functions
Public APIs include `ivpu_ipc_init()`, `ivpu_ipc_fini()`, `ivpu_ipc_enable()`, `ivpu_ipc_disable()`, `ivpu_ipc_reset()`, `ivpu_ipc_irq_handler()`, `ivpu_ipc_irq_work_fn()`, consumer add/delete, `ivpu_ipc_send()`, `ivpu_ipc_receive()`, `ivpu_ipc_send_receive_internal()`, `ivpu_ipc_send_receive()`, and `ivpu_ipc_send_and_wait()`. Internal helpers prepare/release TX buffers, mark RX buffers free, match consumers by channel/request ID, and queue received messages.

### Control Flow
Init allocates global WC/mappable TX and RX BOs, creates a 64-byte-aligned gen_pool over TX memory, initializes locks/lists, and resets shared memory. Send locks IPC state, rejects sends when disabled, allocates a TX buffer, fills IPC and JSM headers/payload/request ID, flushes with `wmb()`, and writes the TX VPU address to the hardware FIFO. IRQ handling drains all RX FIFO entries, translates VPU addresses into RX BO CPU pointers, validates JSM payloads, enforces a max queued RX count, matches a consumer, and either queues synchronous messages or callback work. Receive waits on the consumer queue, handles aborts/timeouts, copies headers/payloads, checks JSM result, traces, marks buffers free, and removes the queued message. High-level send/receive wraps runtime PM and probes firmware heartbeat on timeout to trigger recovery if the heartbeat also times out.

### State, Persistence, And Dependencies
State lives in `struct ivpu_ipc_info`: TX gen_pool, TX/RX BOs, consumer/callback lists, request counter, RX message count, lock, and on/off flag. Each `ivpu_ipc_consumer` stores channel, last TX address, request ID, abort state, callback, RX list, spinlock, and waitqueue. Shared memory status fields persist until firmware/driver marks them free. Dependencies include ivpu GEM global BOs, hardware IPC FIFO wrappers, PM runtime, JSM API/messages, tracepoints, genalloc, waitqueues, and spinlocks.

### Integration Points
Firmware boot waits for the boot IPC channel. JSM command helpers, debugfs trace/control, PM, jobs, and metric streamer use IPC send/receive. Hardware IRQ dispatch calls `ivpu_ipc_irq_handler()` on HOST_IPC_FIFO interrupts.

### Risks
IPC must drain the FIFO fully or future interrupts may not fire. TX buffers are freed when consumers are deleted, so long-lived consumers must be managed carefully. Callback messages are processed in workqueue context after IRQ. `data_size` is currently set to `sizeof(*req)` rather than the exact union payload, noted by a TODO. Timeouts can trigger PM recovery only after heartbeat also fails. Shared memory barriers are required for firmware visibility.

### Test Signals
Test boot message receive, synchronous request/response, async callback consumers, timeout and heartbeat recovery, IPC disable abort wakeups, RX FIFO out-of-range addresses, max RX queue drop, JSM result error propagation, consumer deletion freeing TX buffers, and concurrent consumers with same channel but distinct request IDs.
