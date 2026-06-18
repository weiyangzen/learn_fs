<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_rxe.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_rxe.h

## Purpose
Defines the Soft-RoCE RXE userspace shared queue ABI: address vectors, send/receive work queue entries, SGEs, memory-region info, queue buffers, and object creation responses.

## Important APIs, Types, and Functions
Read coverage: 231 lines and 5127 bytes. Visible type families include union rxe_gid, struct rxe_global_route, struct rxe_av, struct sockaddr_in, struct sockaddr_in6, struct rxe_send_wr, struct ib_mr, struct rxe_sge, struct mminfo, struct rxe_dma_info, struct rxe_send_wqe, struct rxe_recv_wqe, struct rxe_create_ah_resp, struct rxe_create_cq_resp, struct rxe_resize_cq_resp, struct rxe_create_qp_resp, struct rxe_create_srq_resp, struct rxe_modify_srq_cmd, struct rxe_queue_buf. Important macros/constants include RDMA_USER_RXE_H. Explicit ioctl-style command names include none.

## Control Flow
The rxe provider maps queue buffers, builds `rxe_send_wqe` and `rxe_recv_wqe` entries using address-vector and SGE structures, receives object IDs for AH/CQ/QP/SRQ creation, modifies SRQs, and shares producer/consumer queue state with the kernel software RDMA engine.

## State and Persistence Behavior
State is in mmaped RXE queues and kernel objects: WQE arrays, queue indices, GIDs, AV routing data, DMA/memory metadata, and response object IDs. The header defines the shared memory contract.

## Dependencies and Integration Points
It depends on Linux integer types and generic RDMA concepts. It integrates with the rxe software provider, rdma-core, IP/UDP networking, and uverbs object creation. Direct includes are #include <linux/types.h>, #include <linux/socket.h>, #include <linux/in.h>, #include <linux/in6.h>.

## Risks and Edge Cases
Shared queue layout, WQE opcode/flags, SGE counts, and memory info are compatibility-sensitive. Because RXE is software, invalid userspace queue contents can directly stress kernel validation and packet generation.

## Test Signals
Run rxe rdma-core tests, shared-queue producer/consumer stress, send/recv opcode coverage, AH/CQ/QP/SRQ create/resize/modify paths, invalid WQE/SGE counts, and 32-bit layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_rxe.h -->
