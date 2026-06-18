# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.c

Purpose: implements KFD kernel-owned queues, especially HIQ, used to submit PM4/MES packets from the driver to hardware. It allocates queue memory, doorbells, MQDs, and pointer buffers, exposes packet acquire/submit/rollback, and tears queues down safely.

Important APIs/types/functions: `kernel_queue_init`/`kernel_queue_uninit` are public constructors/destructors. `kq_acquire_packet_buffer` reserves dwords in the ring and handles wrap with NOP padding. `kq_submit_packet` publishes the write pointer and rings the kernel doorbell, supporting 32-bit and 64-bit doorbells. `kq_rollback_packet` discards pending write-pointer reservations. Internal `kq_initialize` and `kq_uninitialize` allocate/free GTT suballocations, initialize `struct queue`, allocate/init MQDs, and load HIQ MQDs.

Control flow: initialization obtains a kernel doorbell, allocates packet queue, EOP memory on newer ASICs, read-pointer and write-pointer buffers, zeros them, initializes queue properties, creates a `struct queue`, allocates and initializes an MQD via the HIQ MQD manager, and loads it into the fixed HIQ pipe/queue for HIQ type. Packet acquisition reads hardware rptr and pending wptr, computes modulo free space with one dword left empty, NOP-fills to the ring end if wrapping, and advances pending pointers. Submission checks fatal-error detection, orders ring writes with barriers, updates wptr memory, and writes the doorbell. Uninit destroys loaded HIQ MQDs under reset-domain read lock when possible, then frees MQD, GTT allocations, doorbell, and queue.

State and persistence: `struct kernel_queue` persists pending pointers, GPU/CPU addresses for PQ/EOP/rptr/wptr, doorbell, queue object, MQD manager, and NOP packet. Hardware-visible state is in GTT allocations and doorbell writes; it is not durable across device reset.

Dependencies/integration: depends on KFD GTT suballocator, kernel doorbell allocator, queue initialization helpers, DQM MQD managers, amdgpu reset domain, and PM4 packet definitions. Consumers build packets using `kq_acquire_packet_buffer` then call submit or rollback.

Risks: ring arithmetic assumes power-of-two queue size and one unused slot. Failed EOP allocation on CIK path relies on NULL-safe free. Destroying HIQ is skipped if reset-domain read lock is unavailable, leaving teardown to reset handling. Test signals include wraparound/NOP padding, rollback, 32/64-bit doorbell submission, FED `-EIO` path, allocation unwinding, and reset/uninit races.
