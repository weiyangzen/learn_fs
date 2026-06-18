# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.h

## Purpose
Declares the command queue ABI and software state for HINIC firmware command submission. It defines command queue context bitfields, doorbell encoding, command-buffer limits, queue types, and the public API used by IO and device setup.

## Important APIs, Types, and Functions
Key types are `hinic_cmdq_buf`, `hinic_cmdq_arm_bit`, `hinic_cmdq_ctxt_info`, `hinic_cmdq_ctxt`, `hinic_cmdq`, and `hinic_cmdqs`. Public functions are `hinic_alloc_cmdq_buf`, `hinic_free_cmdq_buf`, `hinic_cmdq_direct_resp`, `hinic_init_cmdqs`, and `hinic_free_cmdqs`. Macros such as `HINIC_CMDQ_CTXT_PAGE_INFO_SET`, `HINIC_CMDQ_CTXT_BLOCK_INFO_SET`, `HINIC_SAVED_DATA_SET`, and `HINIC_CMDQ_DB_INFO_SET` encode hardware fields.

## Control Flow
The header has no runtime control flow. Its declarations support the init path in `hinic_hw_io.c`, command submission in `hinic_hw_cmdq.c`, and firmware context validation in PF mailbox handling.

## State and Persistence Behavior
The header defines in-memory software state plus hardware-serialized context layouts. `curr_wqe_page_pfn`, `wq_block_pfn`, CEQ id, arm/en flags, wrapped bit, command type, and function ids are persistent for the lifetime of the hardware command queue context.

## Dependencies and Integration Points
Includes Linux PCI, spinlock, completion, and HINIC hardware interface/work-queue headers. It is integrated with CEQ event `HINIC_CEQ_CMDQ`, management command `HINIC_COMM_CMD_CMDQ_CTXT_SET`, and VF mailbox validation of command queue contexts.

## Risks
Bitfield masks and shifts are hardware ABI. The command buffer size allows only `HINIC_CMDQ_MAX_DATA_SIZE` after reserved bytes; callers that exceed it fail validation. Include order matters because `struct hinic_hwdev` and `struct hinic_cmdq_pages` are supplied by other HINIC headers.

## Test Signals
Compile coverage, command queue context setup for PF/VF, VF command queue context mailbox validation, boundary command buffer sizes, and CEQ command completions are the main signals.
