# sources/distributed-fs/ceph-client/io_uring/register.c

Purpose: implements the `io_uring_register()` syscall dispatch and ring configuration/resource registration operations.

Important APIs/types/functions: `io_probe()`, personality register/unregister, restriction parsing, task restrictions, BPF filter registration, ring enable, io-wq affinity/limits, clock registration, ring resize, memory-region registration, blind registration, and `SYSCALL_DEFINE4(io_uring_register)` are central. `io_ring_ctx_rings` stages resize state.

Control flow: syscall normalizes `IORING_REGISTER_USE_REGISTERED_RING`, handles blind `fd == -1` opcodes, resolves the ring file, locks `ctx->uring_lock`, and dispatches through `__io_uring_register()`. Dispatch validates arguments per opcode and calls resource, eventfd, pbuf, NAPI, zcrx, resize, query, restriction, and BPF helpers. Resize allocates new shared ring/SQE regions, copies pending SQ/CQ entries, swaps under mmap and completion locks, RCU-publishes new rings, and frees old regions after synchronization. Enabling disabled rings sets single-issuer state before releasing `R_DISABLED`.

State and persistence: mutates ring context flags, personalities xarray, restrictions, registered files/buffers, eventfd, io-wq settings, SQPOLL state, mapped ring regions, clock source, parameter memory region, and BPF filters. State persists for the lifetime of the ring or current task restrictions.

Dependencies/integration: integrates nearly every io_uring subsystem: resources, SQPOLL, task context, eventfd, kbuf, NAPI, msg_ring, memmap, zcrx, query, cancel, and BPF filter code, plus VFS fd lookup and credentials.

Risks/test signals: risks include restriction bypass, wrong lock ordering during SQPOLL/io-wq updates, resize races with mmap/userspace ring access, registered-ring fd semantics, and partial userspace copy failures. Test with every register opcode, disabled-ring restrictions, blind query/restriction/filter paths, ring resize overflow, registered ring fd lookup, SQPOLL affinity, and BPF filter enforcement.
