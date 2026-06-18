# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.h

## Purpose
`user_sdma.h` defines the constants, helpers, queue structures, request structures, and public APIs for hfi1 userspace SDMA. It is the shared contract between `user_sdma.c`, pinning/MMU helpers, expected receive support, and tracepoints.

## Important APIs and Types
Key constants are `MAX_VECTORS_PER_REQ`, `MAX_PKTS_PER_QUEUE`, `BTH_SEQ_MASK`, AHG KDETH descriptor positions, PBC/LRH conversion macros, `TXREQ_FLAGS_REQ_ACK`, `TXREQ_FLAGS_REQ_DISABLE_SH`, and `SDMA_IOWAIT_TIMEOUT`. Helpers include `num_pages()`, request control field decoders `req_opcode()`, `req_version()`, `req_iovcnt()`, and `ahg_header_set()`. `struct hfi1_user_sdma_pkt_q` owns request slots, in-use bitmap, txreq cache, iowait, waitqueue, MMU handler, and lock accounting. `struct hfi1_user_sdma_comp_q` describes the completion ring. `struct user_sdma_request` is the main in-flight request record. `struct user_sdma_txreq` wraps a packet header, SDMA txreq, list node, request pointer, flags, and sequence number.

## Control Flow
Userspace SDMA lifecycle is queue allocation, repeated request processing, completion polling, and queue free. Requests copy user metadata into `user_sdma_request`, generate one or more `user_sdma_txreq` packets, submit via SDMA, and update the completion ring from callbacks.

## State, Persistence, and Dependencies
The header defines state ownership boundaries but stores no data itself. Queue state persists for the open file/context; request and txreq state lasts until callbacks complete or error cleanup runs. Dependencies include Linux device/wait APIs and local `common.h`, `iowait.h`, `user_exp_rcv.h`, `mmu_rb.h`, `pinning.h`, and `sdma.h`.

## Integration Points
`user_sdma.c` implements the declared APIs. Tracepoints include this header to inspect queue and request fields. Expected receive types are included because expected SDMA requests carry TID vectors and KDETH offsets. Pinning/MMU helpers manage user pages referenced by request iovecs.

## Risks and Test Signals
Risks include macro field masks drifting from uAPI definitions, request/txreq cacheline-sharing assumptions, fixed AHG array sizing, completion-ring size limits, and incorrect use of queue state outside SRCU protection. Test signals include structure compile coverage, max-vector rejection, AHG descriptor bounds checks, completion-ring wrap/reuse tests, and queue free while requests are active.
