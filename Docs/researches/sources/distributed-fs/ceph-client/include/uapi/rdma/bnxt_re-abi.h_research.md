<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/bnxt_re-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/bnxt_re-abi.h

## Purpose
Defines the Broadcom NetXtreme-E RoCE userspace ABI for uverbs command private data and provider-specific ioctl objects such as doorbell pages, toggle memory, packet pacing, and query-device extensions.

## Important APIs, Types, and Functions
Read coverage: 268 lines and 6832 bytes. Visible type families include enum bnxt_re_wqe_mode, struct bnxt_re_uctx_req, struct bnxt_re_uctx_resp, struct bnxt_re_pd_resp, struct bnxt_re_cq_req, enum bnxt_re_resp_cq_mask, enum bnxt_re_req_cq_mask, struct bnxt_re_cq_resp, struct bnxt_re_resize_cq_req, enum bnxt_re_qp_mask, struct bnxt_re_qp_req, struct bnxt_re_qp_resp, struct bnxt_re_srq_req, enum bnxt_re_srq_mask, struct bnxt_re_srq_resp, enum bnxt_re_shpg_offt, enum bnxt_re_objects, enum bnxt_re_alloc_page_type, enum bnxt_re_var_alloc_page_attrs, enum bnxt_re_alloc_page_attrs, enum bnxt_re_alloc_page_methods, enum bnxt_re_notify_drv_methods, enum bnxt_re_get_toggle_mem_type, enum bnxt_re_var_toggle_mem_attrs, enum bnxt_re_toggle_mem_attrs, enum bnxt_re_toggle_mem_methods, struct bnxt_re_packet_pacing_caps, struct bnxt_re_query_device_ex_resp, ... (+5 more). Important macros/constants include __BNXT_RE_UVERBS_ABI_H__, BNXT_RE_ABI_VERSION, BNXT_RE_CHIP_ID0_CHIP_NUM_SFT, BNXT_RE_CHIP_ID0_CHIP_REV_SFT, BNXT_RE_CHIP_ID0_CHIP_MET_SFT. Explicit ioctl-style command names include none.

## Control Flow
libibverbs/provider code allocates a context, receives chip and doorbell capabilities, allocates PD/CQ/QP/SRQ resources with driver-private request/response payloads, mmaps doorbell or toggle pages, and uses provider ioctl methods for DPI/DBR allocation and driver notification.

## State and Persistence Behavior
State resides in kernel RDMA objects and mapped hardware pages: user context identifiers, doorbell page indices, CQ/QP/SRQ IDs, WQE mode, pacing capabilities, toggle memory and default DBR resources. The structures carry handles and offsets between userspace and the driver.

## Dependencies and Integration Points
It depends on Linux integer types and `rdma_user_ioctl_cmds.h`. It integrates with the bnxt_re kernel provider, rdma-core provider library, uverbs mmap, and device memory used for doorbells. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_ioctl_cmds.h>.

## Risks and Edge Cases
Provider ABI layout is fixed; reserved fields and masks must be validated. Doorbell and toggle-memory mapping types are security-sensitive, and chip capability bits must match firmware/hardware behavior to avoid invalid queue programming.

## Test Signals
Run rdma-core bnxt_re provider tests, create/destroy context/PD/CQ/QP/SRQ resources, test DPI/DBR/toggle mappings under 32-bit compat, verify packet pacing reports, and fuzz reserved bits in ioctl payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/bnxt_re-abi.h -->
