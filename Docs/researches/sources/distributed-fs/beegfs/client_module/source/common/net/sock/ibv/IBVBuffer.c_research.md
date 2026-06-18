# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.c

Purpose: Manages DMA-mapped buffer fragments used by BeeGFS RDMA send/receive and RDMA READ/WRITE registration paths.

Important APIs/types/functions: `IBVBuffer_init`, `IBVBuffer_initRegistration`, `IBVBuffer_free`, and `IBVBuffer_fill` allocate fragment arrays, map them for DMA, optionally allocate/map an `ib_mr`, unmap/free resources, and copy data from `iov_iter` into fragments.

Control flow: Initialization computes fragment count, allocates buffer and SGE arrays, kmallocs each fragment, maps it with `ib_dma_map_single`, and unwinds through `IBVBuffer_free` on failure. Registration builds scatterlist entries and maps them into an MR.

State and persistence behavior: Owns kernel buffers, DMA addresses, optional MR, fragment counts, and DMA direction until freed.

Dependencies and integration points: Used by `IBVSocket` communication contexts and RDMA key registration. Depends on kernel RDMA verbs and `iov_iter`.

Risks: Any allocation/mapping failure must unwind fully. DMA direction/length mismatches can corrupt transfers; `IBVBuffer_fill` mutates SGE lengths and list length based on copied data.

Test signals: Fragmented allocation, map failure unwind, registration failure, fill across multiple fragments, and free idempotence under partial initialization.
