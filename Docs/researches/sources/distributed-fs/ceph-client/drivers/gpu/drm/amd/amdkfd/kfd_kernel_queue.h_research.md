# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.h

Purpose: declares the KFD kernel queue interface and the `struct kernel_queue` state shared with queue users.

Important APIs/types/functions: declares `kq_acquire_packet_buffer`, `kq_submit_packet`, and `kq_rollback_packet`. `struct kernel_queue` contains the owning `kfd_node`, MQD manager, `struct queue`, pending 32/64-bit write pointers, NOP packet, GTT memory objects and CPU/GPU addresses for rptr/wptr/PQ/EOP/fence, and a list node.

Control flow: callers reserve packet space through `kq_acquire_packet_buffer`, write packet dwords into the returned buffer, then call `kq_submit_packet`; on construction failure after reservation they call `kq_rollback_packet`. The struct fields are filled by `kfd_kernel_queue.c` initialization and consumed by packet builders and teardown paths.

State and persistence: the header defines all persistent in-memory queue state. The union of `wptr64_kernel` and `wptr_kernel` mirrors hardware doorbell-size differences. GPU addresses are persisted while the kernel queue lives and are embedded into MQDs and hardware registers.

Dependencies/integration: includes `kfd_priv.h` for KFD core types and Linux list/types headers. It is used by DQM/HIQ code that submits commands through kernel queues.

Risks: external users can access fields directly, so layout changes have broad impact. The union demands correct doorbell-size checks before dereference. Test signals are mostly exercised through `kfd_kernel_queue.c`: packet reservation/submit, queue creation/destruction, and doorbell-size variants.
