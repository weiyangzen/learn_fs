<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mthca-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mthca-abi.h

## Purpose
Defines the Mellanox mthca InfiniBand provider ABI for first-generation hardware, including context, PD, MR registration, CQ/SRQ/QP create and resize payloads.

## Important APIs, Types, and Functions
Read coverage: 112 lines and 3055 bytes. Visible type families include struct mthca_alloc_ucontext_resp, struct mthca_alloc_pd_resp, struct mthca_reg_mr, struct mthca_create_cq, struct mthca_create_cq_resp, struct mthca_resize_cq, struct mthca_create_srq, struct mthca_create_srq_resp, struct mthca_create_qp. Important macros/constants include MTHCA_ABI_USER_H, MTHCA_UVERBS_ABI_VERSION, MTHCA_MR_DMASYNC. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates a context and PD, registers memory with optional DMA sync, creates CQs/SRQs/QPs using user queue addresses and keys, and receives object numbers for direct userspace queue management.

## State and Persistence Behavior
State includes UAR mapping, PD numbers, MR keys, CQ/SRQ/QP IDs, queue buffers, and resize metadata held by the mthca driver and hardware.

## Dependencies and Integration Points
It depends on Linux integer types and legacy uverbs. It integrates with old Mellanox InfiniHost/Arbel hardware and rdma-core mthca provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Old hardware ABI must remain source and binary compatible. DMA sync flags, queue address validation, and 32/64-bit pointer-as-u64 fields are the main hazards.

## Test Signals
Compile and run mthca provider lifecycle tests where hardware or emulation is available, check MR DMA-sync behavior, CQ resize, QP/SRQ creation, and ABI layout compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mthca-abi.h -->
