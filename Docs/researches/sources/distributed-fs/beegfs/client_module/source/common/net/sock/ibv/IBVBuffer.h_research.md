# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.h

Purpose: Declares the RDMA buffer object used by `IBVSocket` when `BEEGFS_RDMA` is enabled.

Important APIs/types/functions: Exposes `IBVBuffer_init`, `IBVBuffer_initRegistration`, `IBVBuffer_free`, `IBVBuffer_fill`, and struct fields for fragment pointers, `ib_sge` list, optional memory region, buffer size/count, active SGE length, and DMA direction.

Control flow: Consumers initialize buffers against an `IBVCommContext`, optionally prepare memory registration for RDMA READ/WRITE, fill send buffers from iterators, and free during context teardown.

State and persistence behavior: Header declares ownership of DMA-mapped memory for one communication context. No persistence.

Dependencies and integration points: Compiled only with RDMA support and used by `IBVSocket` queue-pair setup and data path.

Risks: The struct is unavailable without `BEEGFS_RDMA`; callers must compile-guard direct access. Buffer fields are low-level and require disciplined teardown.

Test signals: RDMA build compilation plus integration tests that allocate, register, send, receive, and free buffers.
