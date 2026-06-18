# Research: subset-b-005998

Grouped source-tree-aligned research for the listed UAPI headers. Each source file section is delimited for deterministic reconciliation into the mapped per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/xilinx_sdfec.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/xilinx_sdfec.h

## Purpose
Defines the userspace ABI for the Xilinx Soft Decision FEC misc device. It exposes LDPC table address bounds, Turbo/LDPC configuration structures, runtime status and error counters, and the ioctl command set used to start, stop, configure, query, and reset the SD-FEC core.

## Important APIs, Types, and Functions
Read coverage: 448 lines and 12341 bytes. Visible type families include enum xsdfec_code, enum xsdfec_order, enum xsdfec_turbo_alg, enum xsdfec_state, enum xsdfec_axis_width, enum xsdfec_axis_word_include, struct xsdfec_turbo, struct xsdfec_ldpc_params, struct xsdfec_status, struct xsdfec_irq, struct xsdfec_config, struct xsdfec_stats, struct xsdfec_ldpc_param_table_sizes. Important macros/constants include __XILINX_SDFEC_H__, XSDFEC_LDPC_SC_TABLE_ADDR_BASE, XSDFEC_LDPC_SC_TABLE_ADDR_HIGH, XSDFEC_LDPC_LA_TABLE_ADDR_BASE, XSDFEC_LDPC_LA_TABLE_ADDR_HIGH, XSDFEC_LDPC_QC_TABLE_ADDR_BASE, XSDFEC_LDPC_QC_TABLE_ADDR_HIGH, XSDFEC_SC_TABLE_DEPTH, XSDFEC_LA_TABLE_DEPTH, XSDFEC_QC_TABLE_DEPTH, XSDFEC_MAGIC, XSDFEC_START_DEV, XSDFEC_STOP_DEV, XSDFEC_GET_STATUS, XSDFEC_SET_IRQ, XSDFEC_SET_TURBO, XSDFEC_ADD_LDPC_CODE_PARAMS, XSDFEC_GET_CONFIG, XSDFEC_GET_TURBO, XSDFEC_SET_ORDER, XSDFEC_SET_BYPASS, XSDFEC_IS_ACTIVE, XSDFEC_CLEAR_STATS, XSDFEC_GET_STATS, XSDFEC_SET_DEFAULT_CONFIG. Explicit ioctl-style command names include XSDFEC_START_DEV, XSDFEC_STOP_DEV, XSDFEC_GET_STATUS, XSDFEC_SET_IRQ, XSDFEC_SET_TURBO, XSDFEC_GET_CONFIG, XSDFEC_GET_TURBO, XSDFEC_SET_ORDER, XSDFEC_SET_BYPASS, XSDFEC_IS_ACTIVE, XSDFEC_CLEAR_STATS, XSDFEC_GET_STATS, XSDFEC_SET_DEFAULT_CONFIG.

## Control Flow
Userspace opens the misc device, configures static parameters while the core is stopped, optionally loads LDPC code parameters, sets ordering/bypass/IRQ policy, then starts the core. Status and activity ioctls observe processing, statistics are accumulated by the driver until cleared, and stop/default-config ioctls return the hardware to a known state. Several setters are explicitly valid only in `XSDFEC_STOPPED` state, so the ABI encodes a stopped-configure-start lifecycle.

## State and Persistence Behavior
Persistent state is in the device driver and hardware registers: selected code mode, Turbo algorithm, LDPC tables, AXIS widths, bypass/order flags, IRQ enablement, and accumulated ISR/ECC counters. The header is layout-only, but its table sizes and fixed arrays define the userspace buffer sizes that the kernel copies.

## Dependencies and Integration Points
It depends on fixed-width Linux integer types, ioctl encoding, and userspace-visible `bool`. It integrates with the Xilinx SD-FEC misc driver and hardware blocks that expose Turbo and LDPC datapaths. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
ABI risks center on fixed-size LDPC arrays, 32/64-bit bool and unsigned-long ioctl payloads, table address range changes, and enforcing stopped-state restrictions before mutating hardware. The bypass comment contains a likely wording error around false/true semantics, so implementation and tests should be treated as authoritative.

## Test Signals
Exercise ioctl number compatibility, stopped-state rejection for setters, LDPC table bounds, Turbo and LDPC mode-specific validation, start requiring order configuration, IRQ/stat clear behavior, and 32-bit userspace compatibility for `unsigned long` and `bool` arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/xilinx_sdfec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/inftl-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/inftl-user.h

## Purpose
Defines the historical INFTL on-flash layout structures used by userspace tooling and kernel code to inspect or format M-Systems-style flash translation layer media.

## Important APIs, Types, and Functions
Read coverage: 92 lines and 1644 bytes. Visible type families include struct inftl_bci, struct inftl_unithead1, struct inftl_unithead2, struct inftl_unittail, union inftl_uci, struct inftl_oob, struct INFTLPartition, struct INFTLMediaHeader. Important macros/constants include __MTD_INFTL_USER_H__, OSAK_VERSION, PERCENTUSED, SECTORSIZE, INFTL_BINARY, INFTL_BDTL, INFTL_LAST. Explicit ioctl-style command names include none.

## Control Flow
There are no callable routines. Tools read OOB bytes into `struct inftl_oob`, interpret the unit-control union, and parse `INFTLMediaHeader` partitions and erase-unit metadata to discover virtual-unit chains and formatted size.

## State and Persistence Behavior
The structures describe persistent media state stored in NAND OOB and header erase units: block control information, erase mark values, virtual unit numbers, previous/next chains, free/deleted sectors, partition records, and boot-record identifiers.

## Dependencies and Integration Points
It uses Linux fixed-width integer aliases and little-endian on-media fields. It integrates with legacy INFTL/NAND tooling and any compatibility code that still parses INFTL volumes. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
This is an on-flash ABI; packing, field width, array size, and endian assumptions must not change. Corrupt headers or OOB values can create invalid erase-unit chains, and modern MTD code must avoid treating these legacy structures as native-endian kernel-only data.

## Test Signals
Validate structure sizes against known INFTL images, parse representative good and corrupt media headers, check endian conversion on big-endian builds, and run old userspace format/inspect tools against the exported header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/inftl-user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-abi.h

## Purpose
Defines the primary userspace ABI for Linux Memory Technology Devices: erase, OOB, ECC, OTP, bad-block, lock, read/write, and file-mode ioctl structures and command numbers.

## Important APIs, Types, and Functions
Read coverage: 342 lines and 11879 bytes. Visible type families include struct erase_info_user, struct erase_info_user64, struct mtd_oob_buf, struct mtd_oob_buf64, struct mtd_write_req, struct mtd_read_req_ecc_stats, struct mtd_read_req, struct mtd_info_user, struct region_info_user, struct otp_info, struct nand_oobinfo, struct nand_oobfree, struct nand_ecclayout_user, struct mtd_ecc_stats, enum mtd_file_modes. Important macros/constants include __MTD_ABI_H__, MTD_ABSENT, MTD_RAM, MTD_ROM, MTD_NORFLASH, MTD_NANDFLASH, MTD_DATAFLASH, MTD_UBIVOLUME, MTD_MLCNANDFLASH, MTD_WRITEABLE, MTD_BIT_WRITEABLE, MTD_NO_ERASE, MTD_POWERUP_LOCK, MTD_SLC_ON_MLC_EMULATION, MTD_CAP_ROM, MTD_CAP_RAM, MTD_CAP_NORFLASH, MTD_CAP_NANDFLASH, MTD_CAP_NVRAM, MTD_NANDECC_OFF, MTD_NANDECC_PLACE, MTD_NANDECC_AUTOPLACE, MTD_NANDECC_PLACEONLY, MTD_NANDECC_AUTOPL_USR, MTD_OTP_OFF, MTD_OTP_FACTORY, MTD_OTP_USER, MEMGETINFO, ... (+26 more). Explicit ioctl-style command names include MEMGETINFO, MEMERASE, MEMWRITEOOB, MEMREADOOB, MEMLOCK, MEMUNLOCK, MEMGETREGIONCOUNT, MEMGETREGIONINFO, MEMGETOOBSEL, MEMGETBADBLOCK, MEMSETBADBLOCK, OTPSELECT, OTPGETREGIONCOUNT, OTPGETREGIONINFO, OTPLOCK, ECCGETLAYOUT, ECCGETSTATS, MTDFILEMODE, MEMERASE64, MEMWRITEOOB64, MEMREADOOB64, MEMISLOCKED, MEMWRITE, OTPERASE, MEMREAD.

## Control Flow
Userspace opens an MTD character device, queries geometry with `MEMGETINFO`, optionally queries region/OOB/ECC layout, erases regions, performs data or OOB reads/writes, marks or queries bad blocks, changes lock/OTP state, or selects raw/OOB/place/ECC file modes. Newer flows use 64-bit erase/OOB structures and `MEMREAD`/`MEMWRITE` request structures for mode-aware I/O and ECC statistics.

## State and Persistence Behavior
The header stores no runtime state, but the ioctls mutate persistent flash content, bad-block tables, OTP regions, lock state, and ECC/OOB placement. `mtd_info_user` and related structures snapshot kernel device geometry and capability flags for userspace.

## Dependencies and Integration Points
It depends on ioctl numbering, Linux integer and loff_t types, and legacy NAND OOB layout definitions. It integrates with MTD char devices, NAND/NOR flash drivers, UBI attachment, flash filesystems, and flash-management tools. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Compatibility risks include legacy 32-bit offsets versus 64-bit offsets, variable OOB layouts, raw mode bypassing ECC, irreversible OTP locking, bad-block marking, and ABI-preserved deprecated fields. Incorrect bounds checks can erase or write outside intended flash regions.

## Test Signals
Run MTD char-device ioctl tests on nandsim/mtdram and real devices, cover 32-bit compat ioctls, OOB and raw modes, ECC statistics, OTP lock/erase behavior, bad-block operations, and UBI attach after erase/write cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-user.h

## Purpose
Provides the libc-facing compatibility include for MTD userspace by including `mtd-abi.h` and defining the historical typedef aliases such as `mtd_info_t` and `erase_info_t`.

## Important APIs, Types, and Functions
Read coverage: 33 lines and 1242 bytes. Visible type families include typedef mtd_info_t, typedef erase_info_t, typedef region_info_t, typedef nand_oobinfo_t, typedef nand_ecclayout_t. Important macros/constants include __MTD_USER_H__. Explicit ioctl-style command names include none.

## Control Flow
No control flow exists. Userspace includes this wrapper and receives the canonical MTD ABI definitions plus old typedef names expected by existing tools.

## State and Persistence Behavior
No state is defined here; all persistent flash state and ioctl payloads are inherited from `mtd-abi.h`.

## Dependencies and Integration Points
It directly depends on `mtd-abi.h` and integrates with mtd-utils and older applications that still compile against typedef names rather than struct tags. Direct includes are #include <mtd/mtd-abi.h>.

## Risks and Edge Cases
The main risk is accidental removal or renaming of compatibility typedefs, which would break source compatibility even though the binary ABI lives in `mtd-abi.h`.

## Test Signals
Compile representative old mtd-utils sources against the header, verify typedef names resolve, and run the broader `mtd-abi.h` ioctl tests for behavioral coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/nftl-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/nftl-user.h

## Purpose
Defines the legacy NFTL on-flash metadata layout for NAND Flash Translation Layer media, including OOB records, media headers, erase-zone constants, sector states, and fold markers.

## Important APIs, Types, and Functions
Read coverage: 91 lines and 2116 bytes. Visible type families include struct nftl_bci, struct nftl_uci0, struct nftl_uci1, struct nftl_uci2, union nftl_uci, struct nftl_oob, struct NFTLMediaHeader. Important macros/constants include __MTD_NFTL_USER_H__, MAX_ERASE_ZONES, ERASE_MARK, SECTOR_FREE, SECTOR_USED, SECTOR_IGNORE, SECTOR_DELETED, FOLD_MARK_IN_PROGRESS, ZONE_GOOD, ZONE_BAD_ORIGINAL, ZONE_BAD_MARKED. Explicit ioctl-style command names include none.

## Control Flow
There are no functions. Userspace and kernel compatibility paths read OOB metadata, decode unit control information, inspect the media header, and use sector state constants to interpret free, used, ignored, and deleted sectors.

## State and Persistence Behavior
Persistent state is the NFTL media format itself: virtual unit numbers, erase marks, sector replacement information, erase-zone bookkeeping, bad-zone classification, and fold-in-progress markers stored on flash.

## Dependencies and Integration Points
It depends on Linux integer aliases and legacy NAND/NFTL conventions. It integrates with historical NFTL drivers and flash-maintenance tools that must understand old M-Systems formats. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
NFTL state is on-media and often encountered during recovery, so parsers must tolerate corrupt OOB/header data. Structure layout and magic constants are compatibility-sensitive and endian-sensitive.

## Test Signals
Check structure sizes and constants against known NFTL images, parse good and intentionally damaged media, validate big-endian behavior, and compile old NFTL tools against the exported header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/nftl-user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/ubi-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/ubi-user.h

## Purpose
Defines the complete userspace ioctl ABI for UBI control devices, UBI character devices, and UBI volume devices. It covers MTD attach/detach, volume create/remove/resize/rename, volume update, LEB map/unmap/change/query, erase-counter reporting, volume properties, and read-only block device creation.

## Important APIs, Types, and Functions
Read coverage: 506 lines and 19854 bytes. Visible type families include struct ubi_set_vol_prop_req, struct ubi_attach_req, struct ubi_mkvol_req, struct ubi_rsvol_req, struct ubi_rnvol_req, struct ubi_ecinfo_req, struct ubi_leb_change_req, struct ubi_map_req, struct ubi_blkcreate_req. Important macros/constants include __UBI_USER_H__, UBI_VOL_NUM_AUTO, UBI_DEV_NUM_AUTO, UBI_MAX_VOLUME_NAME, UBI_IOC_MAGIC, UBI_IOCMKVOL, UBI_IOCRMVOL, UBI_IOCRSVOL, UBI_IOCRNVOL, UBI_IOCRPEB, UBI_IOCSPEB, UBI_IOCECNFO, UBI_CTRL_IOC_MAGIC, UBI_IOCATT, UBI_IOCDET, UBI_VOL_IOC_MAGIC, UBI_IOCVOLUP, UBI_IOCEBER, UBI_IOCEBCH, UBI_IOCEBMAP, UBI_IOCEBUNMAP, UBI_IOCEBISMAP, UBI_IOCSETVOLPROP, UBI_IOCVOLCRBLK, UBI_IOCVOLRMBLK, MAX_UBI_MTD_NAME_LEN, UBI_MAX_RNVOL, UBI_VOL_VALID_FLGS. Explicit ioctl-style command names include UBI_IOC_MAGIC, UBI_IOCMKVOL, UBI_IOCRMVOL, UBI_IOCRSVOL, UBI_IOCRNVOL, UBI_IOCRPEB, UBI_IOCSPEB, UBI_IOCECNFO, UBI_CTRL_IOC_MAGIC, UBI_IOCATT, UBI_IOCDET, UBI_VOL_IOC_MAGIC, UBI_IOCVOLUP, UBI_IOCEBER, UBI_IOCEBCH, UBI_IOCEBMAP, UBI_IOCEBUNMAP, UBI_IOCEBISMAP, UBI_IOCSETVOLPROP, UBI_IOCVOLCRBLK, UBI_IOCVOLRMBLK.

## Control Flow
Control-device flows attach an MTD device with `UBI_IOCATT` or detach with `UBI_IOCDET`. UBI device flows create, remove, resize, atomically rename, scrub, or query erase counters. Volume-device flows start an update by declaring byte count, write exactly that image, erase or atomically change LEBs, map/unmap/query LEB mappings, set properties such as direct-write, and create/remove UBI block devices.

## State and Persistence Behavior
The ABI mutates persistent UBI metadata on flash: device attachment records, volume tables, volume names and IDs, logical-to-physical eraseblock mappings, erase counters, update transactions, and volume flags such as skip-CRC-check. Some operations are transactional or asynchronous, such as unmap scheduling erase without waiting.

## Dependencies and Integration Points
It depends on Linux integer types and ioctl encoding. It integrates with MTD devices, UBI core, UBIFS, ubiblock, and userspace tools such as ubiattach, ubimkvol, ubirename, ubiupdatevol, and ubinfo. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Risks include fixed maximum name and rename counts, ABI-preserved 64-bit update-size encoding, asynchronous unmap persistence after power loss, atomic rename validation, autoresize semantics, and reserved padding that must remain zero/ignored for forward compatibility.

## Test Signals
Run UBI/UBIFS tests on nandsim, cover attach/detach, create/remove/resize/rename including atomic multi-volume rename, interrupted volume updates, LEB map/unmap/change across power-cut simulation, erase-counter queries, property setting, and ubiblock create/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/ubi-user.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/cxgb4-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/cxgb4-abi.h

## Purpose
Defines Chelsio T4/T5/T6 iWARP uverbs private ABI structures for context allocation, CQ/QP/SRQ creation, PD allocation, and status-page mappings.

## Important APIs, Types, and Functions
Read coverage: 115 lines and 3122 bytes. Visible type families include struct c4iw_create_cq, struct c4iw_create_cq_resp, struct c4iw_create_qp_resp, struct c4iw_create_srq_resp, struct c4iw_alloc_ucontext_resp, struct c4iw_alloc_pd_resp. Important macros/constants include CXGB4_ABI_USER_H, C4IW_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates a context to receive status-page, page-size, and queue key information, creates CQs and QPs with user queue addresses, optionally creates SRQs, and rings Chelsio-specific doorbells through mapped resources.

## State and Persistence Behavior
Runtime state is in provider-owned queue memory and kernel RDMA objects: CQ/QP/SRQ IDs, queue sizes, doorbell/status-page keys, and write-combining mappings. The ABI structures move these identifiers across uverbs calls.

## Dependencies and Integration Points
It depends on Linux integer types and the generic uverbs command path. It integrates with the cxgb4 RDMA driver and rdma-core c4iw provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Queue address and size fields must be validated against user memory registration and hardware limits. ABI version 3 compatibility and status-page mmap key semantics are fragile across provider/kernel combinations.

## Test Signals
Exercise c4iw context allocation, PD/CQ/QP/SRQ create and teardown, queue overflow limits, 32-bit userspace layouts, and provider/kernel ABI-version negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/cxgb4-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/efa-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/efa-abi.h

## Purpose
Defines the Amazon Elastic Fabric Adapter userspace ABI, including context, PD, CQ, QP, AH, extended query-device, and provider ioctl definitions for memory-region query methods.

## Important APIs, Types, and Functions
Read coverage: 166 lines and 3747 bytes. Visible type families include struct efa_ibv_alloc_ucontext_cmd, enum efa_ibv_user_cmds_supp_udata, struct efa_ibv_alloc_ucontext_resp, struct efa_ibv_alloc_pd_resp, struct efa_ibv_create_cq, struct efa_ibv_create_cq_resp, struct efa_ibv_create_qp, struct efa_ibv_create_qp_resp, struct efa_ibv_create_ah_resp, struct efa_ibv_ex_query_device_resp, enum efa_query_mr_attrs, enum efa_mr_methods. Important macros/constants include EFA_ABI_USER_H, EFA_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates a context, discovers supported user-data commands and device capabilities, creates PD/CQ/QP/AH objects with EFA private payloads, and uses ioctl methods to query MR attributes. CQ/QP responses return mmap keys, queue identifiers, sub-CQ layout, and device capabilities needed for direct datapath use.

## State and Persistence Behavior
State is in EFA hardware queues, mmaped rings, queue IDs, inline and RDMA read capability masks, AH numbers, and provider-supported command bitmaps. Reserved fields preserve forward extension space.

## Dependencies and Integration Points
It depends on Linux integer types and `ib_user_ioctl_cmds.h`. It integrates with the EFA kernel provider, rdma-core EFA provider, userspace queue mmap, and cloud fabric capabilities. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_ioctl_cmds.h>.

## Risks and Edge Cases
The file documents strict 8-byte alignment and reserved-field naming rules; breaking them would break ABI. Capability masks must gate optional command payloads, and mmap keys/sub-CQ counts must be checked for overflow or mismatched provider assumptions.

## Test Signals
Run EFA rdma-core tests for context/CQ/QP/AH creation, query-device capability parsing, MR query ioctl methods, reserved-field zero validation, 32-bit ABI layout, and unsupported-command negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/efa-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/erdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/erdma-abi.h

## Purpose
Defines Alibaba ERDMA userspace ABI version 1 for CQ creation, QP creation, and context allocation private response data.

## Important APIs, Types, and Functions
Read coverage: 49 lines and 811 bytes. Visible type families include struct erdma_ureq_create_cq, struct erdma_uresp_create_cq, struct erdma_ureq_create_qp, struct erdma_uresp_create_qp, struct erdma_uresp_alloc_ctx. Important macros/constants include __ERDMA_USER_H__, ERDMA_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Provider code creates CQs and QPs with user doorbell and queue buffer addresses, receives object IDs and mmap hints, and allocates context to discover device IDs and page-size information.

## State and Persistence Behavior
State lives in ERDMA kernel objects and mapped queues: CQ/QP IDs, queue depths, user DB records, mmap offsets, and context identity values.

## Dependencies and Integration Points
It depends only on Linux integer types and integrates with the ERDMA kernel RDMA provider plus rdma-core userspace provider code. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
The ABI is compact, so any field insertion would be breaking. User-provided queue addresses and mmap offsets require strict validation and alignment checks.

## Test Signals
Cover ABI-version negotiation, create/destroy CQ and QP with boundary queue sizes, context allocation responses, 32-bit layout checks, and invalid user address rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/erdma-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_ioctl.h

## Purpose
Defines the HFI1 character-device ioctl payload structures for assigning contexts, querying context/base information, and managing expected TID mappings.

## Important APIs, Types, and Functions
Read coverage: 174 lines and 6618 bytes. Visible type families include struct hfi1_user_info, struct hfi1_ctxt_info, struct hfi1_tid_info, struct hfi1_base_info. Important macros/constants include _LINUX__HFI1_IOCTL_H. Explicit ioctl-style command names include _LINUX__HFI1_IOCTL_H.

## Control Flow
Userspace supplies `hfi1_user_info` to request a context and capabilities, retrieves context and base mapping information, then updates or frees TID mappings through `hfi1_tid_info` arrays used for expected receive buffers.

## State and Persistence Behavior
Driver state includes allocated user contexts, subcontext mappings, receive header/eager buffers, runtime flags, credits, and TID pages. The structures expose offsets, sizes, counts, and IDs needed to mmap and manage that state.

## Dependencies and Integration Points
It depends on Linux fixed-width types and is consumed by ioctl numbers in `rdma_user_ioctl.h`. It integrates with Intel Omni-Path HFI1 userspace drivers and PSM/libfabric stacks. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
TID arrays carry user pointers and page counts, so bounds and pinning are critical. Version/capability negotiation must prevent old userspace from misinterpreting context mapping layouts.

## Test Signals
Exercise assign-context, context/base info queries, TID update/free/invalidation, subcontext sharing, invalid count/address handling, and compat layout against PSM/libfabric users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_user.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_user.h

## Purpose
Defines the HFI1 userspace shared ABI: software version fields, capability and event bits, status flags, SDMA completion and request formats, packet/KDETH headers, and user register offsets.

## Important APIs, Types, and Functions
Read coverage: 268 lines and 9298 bytes. Visible type families include enum hfi1_sdma_comp_state, struct hfi1_sdma_comp_entry, struct hfi1_status, enum sdma_req_opcode, struct sdma_req_info, struct hfi1_kdeth_header, struct hfi1_pkt_header, enum hfi1_ureg. Important macros/constants include _LINUX__HFI1_USER_H, HFI1_USER_SWMAJOR, HFI1_USER_SWMINOR, HFI1_SWMAJOR_SHIFT, HFI1_CAP_DMA_RTAIL, HFI1_CAP_SDMA, HFI1_CAP_SDMA_AHG, HFI1_CAP_EXTENDED_PSN, HFI1_CAP_HDRSUPP, HFI1_CAP_TID_RDMA, HFI1_CAP_USE_SDMA_HEAD, HFI1_CAP_MULTI_PKT_EGR, HFI1_CAP_NODROP_RHQ_FULL, HFI1_CAP_NODROP_EGR_FULL, HFI1_CAP_TID_UNMAP, HFI1_CAP_PRINT_UNIMPL, HFI1_CAP_ALLOW_PERM_JKEY, HFI1_CAP_NO_INTEGRITY, HFI1_CAP_PKEY_CHECK, HFI1_CAP_STATIC_RATE_CTRL, HFI1_CAP_OPFN, HFI1_CAP_SDMA_HEAD_CHECK, HFI1_CAP_EARLY_CREDIT_RETURN, HFI1_CAP_AIP, HFI1_RCVHDR_ENTSIZE_2, HFI1_RCVHDR_ENTSIZE_16, HFI1_RCVDHR_ENTSIZE_32, _HFI1_EVENT_FROZEN_BIT, ... (+26 more). Explicit ioctl-style command names include HFI1_SDMA_REQ_IOVCNT_MASK, HFI1_SDMA_REQ_IOVCNT_SHIFT.

## Control Flow
After ioctl context setup, userspace mmaps shared pages, reads status and event bits, programs SDMA request descriptors, polls completion entries, acknowledges events, and uses register offsets to interact with assigned context resources.

## State and Persistence Behavior
Shared state includes hardware status words, context events, SDMA completion rings, request descriptors, packet headers, and mapped user registers. These structures persist in shared memory between kernel and userspace for the context lifetime.

## Dependencies and Integration Points
It depends on Linux integer types and the HFI1 ioctl setup path. It integrates with HFI1 hardware, PSM/libfabric, SDMA queues, receive header queues, and accelerated IP/TID RDMA capabilities. Direct includes are #include <linux/types.h>, #include <rdma/rdma_user_ioctl.h>.

## Risks and Edge Cases
Shared-memory ABIs are sensitive to version, alignment, volatile producer/consumer ordering, and bit definitions. Capability bits must match kernel setup, and SDMA iovec counts and opcode/version fields must be validated before DMA.

## Test Signals
Run HFI1 userspace stack tests across SW major/minor negotiation, capability masks, SDMA submit/completion/error paths, event ack, register mmap offsets, and memory-ordering stress on shared rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hns-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/hns-abi.h

## Purpose
Defines HiSilicon HNS RoCE provider private uverbs ABI for CQ/SRQ/QP creation, context allocation, congestion flags, QP response capabilities, PD allocation, and AH creation.

## Important APIs, Types, and Functions
Read coverage: 156 lines and 3973 bytes. Visible type families include struct hns_roce_ib_create_cq, enum hns_roce_cq_cap_flags, struct hns_roce_ib_create_cq_resp, enum hns_roce_srq_cap_flags, enum hns_roce_srq_cap_flags_resp, struct hns_roce_ib_create_srq, struct hns_roce_ib_create_srq_resp, enum hns_roce_congest_type_flags, enum hns_roce_create_qp_comp_mask, struct hns_roce_ib_create_qp, enum hns_roce_qp_cap_flags, struct hns_roce_ib_create_qp_resp, struct hns_roce_ib_modify_qp_resp, struct hns_roce_ib_alloc_ucontext_resp, struct hns_roce_ib_alloc_ucontext, struct hns_roce_ib_alloc_pd_resp, struct hns_roce_ib_create_ah_resp. Important macros/constants include HNS_ABI_USER_H. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates context and PD resources, creates CQs/SRQs/QPs with queue buffer addresses and capability masks, receives object numbers and hardware capabilities, and uses AH response data for address-handle programming.

## State and Persistence Behavior
State is in HNS RoCE kernel objects and user queues: queue IDs, db addresses, congestion algorithm flags, SRQ/QP capabilities, context config, and hardware version/capability values.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with the hns_roce driver and rdma-core provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Compatibility hazards include capability mask interpretation, congestion type flags, queue address validation, and reserved response fields for older provider versions.

## Test Signals
Cover context/PD/CQ/SRQ/QP/AH creation with min/max queue sizes, congestion-capability negotiation, reserved-bit rejection, 32-bit layout, and provider/kernel mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hns-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_cmds.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_cmds.h

## Purpose
Defines the generic RDMA uverbs ioctl object, method, and attribute ID namespace used by modern ioctl-based verbs APIs.

## Important APIs, Types, and Functions
Read coverage: 437 lines and 11155 bytes. Visible type families include enum uverbs_default_objects, enum uverbs_methods_device, enum uverbs_attrs_invoke_write_cmd_attr_ids, enum uverbs_attrs_query_port_cmd_attr_ids, enum uverbs_attrs_query_port_speed_cmd_attr_ids, enum uverbs_attrs_get_context_attr_ids, enum uverbs_attrs_query_context_attr_ids, enum uverbs_attrs_create_cq_cmd_attr_ids, enum uverbs_attrs_destroy_cq_cmd_attr_ids, enum uverbs_attrs_create_flow_action_esp, enum uverbs_attrs_modify_flow_action_esp, enum uverbs_attrs_destroy_flow_action_esp, enum uverbs_attrs_create_qp_cmd_attr_ids, enum uverbs_attrs_destroy_qp_cmd_attr_ids, enum uverbs_methods_qp, enum uverbs_attrs_create_srq_cmd_attr_ids, enum uverbs_attrs_destroy_srq_cmd_attr_ids, enum uverbs_methods_srq, enum uverbs_methods_cq, enum uverbs_attrs_create_wq_cmd_attr_ids, enum uverbs_attrs_destroy_wq_cmd_attr_ids, enum uverbs_methods_wq, enum uverbs_methods_actions_flow_action_ops, enum uverbs_attrs_alloc_dm_cmd_attr_ids, enum uverbs_attrs_free_dm_cmd_attr_ids, enum uverbs_methods_dm, enum uverbs_attrs_alloc_dmah_cmd_attr_ids, enum uverbs_attrs_free_dmah_cmd_attr_ids, ... (+31 more). Important macros/constants include IB_USER_IOCTL_CMDS_H, UVERBS_ID_NS_MASK, UVERBS_ID_NS_SHIFT. Explicit ioctl-style command names include IB_USER_IOCTL_CMDS_H.

## Control Flow
Userspace builds an `ib_uverbs_ioctl_hdr` containing object/method IDs from this file and an array of typed attributes. The uverbs core dispatches by object and method, validates mandatory attributes, and calls driver/core handlers for device, CQ, QP, SRQ, WQ, MR, DM, counter, PD, AH, flow, event, and query operations.

## State and Persistence Behavior
The header itself is stateless, but IDs map to persistent uverbs objects and file-descriptor/object-handle lifetimes in the kernel. Attribute IDs define how request/response state is copied, referenced, created, or destroyed.

## Dependencies and Integration Points
It defines the namespace consumed by `rdma_user_ioctl_cmds.h`, `ib_user_ioctl_verbs.h`, provider ioctl headers, the uverbs core, and rdma-core. Direct includes are none.

## Risks and Edge Cases
ID stability is the central ABI risk. Reusing object/method/attribute numbers, changing mandatory/optional interpretation, or crossing namespace bits can break all providers. Mandatory netlink-style attribute flags must be preserved.

## Test Signals
Run uverbs ioctl selftests, rdma-core ABI tests, attribute fuzzer coverage for missing/extra/wrong-size attrs, object lifetime tests, and provider command coverage across old and new kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_verbs.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_verbs.h

## Purpose
Defines data structures and enums for the generic ioctl uverbs verb payloads, including access flags, QP/WQ/SRQ types, flow-action ESP structures, counter flags, driver IDs, and GID table entries.

## Important APIs, Types, and Functions
Read coverage: 276 lines and 8006 bytes. Visible type families include enum ib_uverbs_core_support, enum ib_uverbs_access_flags, enum ib_uverbs_srq_type, enum ib_uverbs_wq_type, enum ib_uverbs_wq_flags, enum ib_uverbs_qp_type, enum ib_uverbs_qp_create_flags, enum ib_uverbs_query_port_cap_flags, enum ib_uverbs_query_port_flags, enum ib_uverbs_flow_action_esp_keymat, enum ib_uverbs_flow_action_esp_keymat_aes_gcm_iv_algo, struct ib_uverbs_flow_action_esp_keymat_aes_gcm, enum ib_uverbs_flow_action_esp_replay, struct ib_uverbs_flow_action_esp_replay_bmp, enum ib_uverbs_flow_action_esp_flags, struct ib_uverbs_flow_action_esp_encap, struct ib_uverbs_flow_action_esp, enum ib_uverbs_read_counters_flags, enum ib_uverbs_advise_mr_advice, enum ib_uverbs_advise_mr_flag, struct ib_uverbs_query_port_resp_ex, struct ib_uverbs_query_port_resp, struct ib_uverbs_qp_cap, enum rdma_driver_id, enum ib_uverbs_gid_type, struct ib_uverbs_gid_entry. Important macros/constants include IB_USER_IOCTL_VERBS_H, RDMA_UAPI_PTR, IB_UVERBS_ACCESS_OPTIONAL_FIRST, IB_UVERBS_ACCESS_OPTIONAL_LAST. Explicit ioctl-style command names include IB_USER_IOCTL_VERBS_H.

## Control Flow
These structures are nested as attributes in the ioctl command namespace. Userspace supplies access flags, object types, flow-action ESP key/replay/encap payloads, MR advice, and receives query-port or GID-entry responses through the uverbs ioctl dispatcher.

## State and Persistence Behavior
State lives in RDMA objects created or modified by ioctl verbs: memory access permissions, QP/WQ/SRQ types, flow action security parameters, counter read behavior, and GID table snapshots.

## Dependencies and Integration Points
It depends on Linux integer types and `rdma_user_ioctl_cmds.h`. It integrates with the generic uverbs ioctl layer, rdma-core, IPsec/ESP offload flow actions, and driver ID reporting. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_verbs.h>.

## Risks and Edge Cases
Access flags share optional ranges and must not collide with provider bits. ESP structures carry security-sensitive keys, IV algorithms, replay state, and encap data, so length and padding validation matters. Driver IDs are externally visible and must remain stable.

## Test Signals
Validate ioctl attributes for QP/WQ/SRQ creation, MR access/advice flags, ESP flow action create/modify/destroy, query-port extended responses, GID table queries, and bad optional flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_mad.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_mad.h

## Purpose
Defines the userspace Management Datagram ABI for `/dev/infiniband/umad*`: MAD packet headers, registration requests, method masks, ABI version, and registration flags.

## Important APIs, Types, and Functions
Read coverage: 234 lines and 8530 bytes. Visible type families include struct ib_user_mad_hdr_old, struct ib_user_mad_hdr, struct ib_user_mad, typedef packed_ulong, struct ib_user_mad_reg_req, struct ib_user_mad_reg_req2. Important macros/constants include IB_USER_MAD_H, IB_USER_MAD_ABI_VERSION, IB_USER_MAD_LONGS_PER_METHOD_MASK, IB_USER_MAD_REG_FLAGS_CAP. Explicit ioctl-style command names include none.

## Control Flow
Applications register an agent on QP0 or QP1, optionally enable P_Key-index-aware packet headers, send and receive `ib_user_mad` packets with address/GRH metadata, and unregister agents when done. `REGISTER_AGENT2` supports extended flags such as userspace RMPP handling.

## State and Persistence Behavior
Kernel state includes registered MAD agents, assigned agent IDs, method masks, QP bindings, RMPP policy, and file-handle mode for old versus P_Key-aware headers. Packet headers carry per-message routing and retry/timeout state.

## Dependencies and Integration Points
It depends on Linux integer types and `rdma_user_ioctl.h`. It integrates with the ib_umad driver, subnet administration, performance management, vendor MAD agents, and userspace SM/SA tools. Direct includes are #include <linux/types.h>, #include <rdma/rdma_user_ioctl.h>.

## Risks and Edge Cases
The file calls out historical 32/64-bit and big-endian `method_mask` ambiguity, so compat handling is critical. Header mode must be enabled before other actions, QPN must be restricted, and RMPP/user flags must be validated.

## Test Signals
Run umad registration/send/receive tests, P_Key enablement ordering, REGISTER_AGENT and REGISTER_AGENT2 compatibility, 32-bit big-endian method-mask layout checks, timeout/retry behavior, and invalid QPN/method mask rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_mad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_sa.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_sa.h

## Purpose
Defines userspace-facing InfiniBand Subnet Administration record payloads for path and service records.

## Important APIs, Types, and Functions
Read coverage: 91 lines and 2522 bytes. Visible type families include struct ib_path_rec_data, struct ib_user_path_rec, struct ib_user_service_rec. Important macros/constants include IB_USER_SA_H. Explicit ioctl-style command names include none.

## Control Flow
SA clients exchange path or service record data with subnet administration interfaces. The structures carry GIDs, LIDs, P_Key, SL/QoS, MTU/rate/lifetime selectors, service IDs, service names, and service data in fixed ABI layouts.

## State and Persistence Behavior
No local state is stored. The structures represent SA database records returned by subnet managers or supplied in SA requests.

## Dependencies and Integration Points
It depends on Linux integer types and integrates with RDMA CM, SA query libraries, subnet managers, and applications that resolve IB paths or services. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Field packing, endian interpretation, and selector semantics must match IBTA SA records. Service name sizes and reserved fields are fixed ABI.

## Test Signals
Validate path and service record sizes, query a live or simulated subnet manager, check endian conversion, and compile rdma-core SA consumers against the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_sa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_verbs.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_verbs.h

## Purpose
Defines the legacy write-based uverbs ABI: command numbers, command/response structures, work requests, flow specs, object lifecycle payloads, query responses, and device capability flags.

## Important APIs, Types, and Functions
Read coverage: 1380 lines and 29479 bytes. Visible type families include enum ib_uverbs_write_cmds, enum ib_placement_type, enum ib_selectivity_level, struct ib_uverbs_async_event_desc, struct ib_uverbs_comp_event_desc, struct ib_uverbs_cq_moderation_caps, struct ib_uverbs_cmd_hdr, struct ib_uverbs_ex_cmd_hdr, struct ib_uverbs_get_context, struct ib_uverbs_get_context_resp, struct ib_uverbs_query_device, struct ib_uverbs_query_device_resp, struct ib_uverbs_ex_query_device, enum ib_uverbs_odp_general_cap_bits, enum ib_uverbs_odp_transport_cap_bits, struct ib_uverbs_odp_caps, struct ib_uverbs_rss_caps, struct ib_uverbs_tm_caps, struct ib_uverbs_ex_query_device_resp, struct ib_uverbs_query_port, struct ib_uverbs_query_port_resp, struct ib_uverbs_alloc_pd, struct ib_uverbs_alloc_pd_resp, struct ib_uverbs_dealloc_pd, struct ib_uverbs_open_xrcd, struct ib_uverbs_open_xrcd_resp, struct ib_uverbs_close_xrcd, struct ib_uverbs_reg_mr, ... (+100 more). Important macros/constants include IB_USER_VERBS_H, IB_USER_VERBS_ABI_VERSION, IB_USER_VERBS_CMD_THRESHOLD, IB_USER_VERBS_CMD_COMMAND_MASK, IB_USER_VERBS_CMD_FLAG_EXTENDED, IB_USER_VERBS_MAX_LOG_IND_TBL_SIZE, IB_DEVICE_NAME_MAX. Explicit ioctl-style command names include none.

## Control Flow
Userspace writes command structures to the uverbs file to get context, query device/port/GID/P_Key, allocate/deallocate PD/MR/MW/CQ/QP/AH/SRQ/WQ/flows, post send/receive work requests, poll or arm CQs, attach multicast, and query/modify objects. Responses return handles, capabilities, object numbers, and bad-WR indices.

## State and Persistence Behavior
State is in persistent uverbs objects bound to the file/context: PDs, MRs, MWindows, CQs, QPs, AHs, multicast membership, flow steering rules, SRQs, WQs, and receive indirection tables. Work request structures describe transient queue entries copied or consumed by providers.

## Dependencies and Integration Points
It depends on Linux integer and ioctl types and is the compatibility layer beneath rdma-core's older command path. It integrates with all RDMA providers and coexists with the newer ioctl ABI. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
This is a broad stable ABI with many deprecated but preserved fields. Risks include 32/64-bit pointer encoding through aligned u64 values, command-number stability, structure alignment comments, flow-spec length validation, bad WR reporting, and capability flag bits reserved due to old kernels.

## Test Signals
Run rdma-core verbs tests across all major providers, 32-bit compat command tests, create/query/modify/destroy lifecycle tests, post-send/recv bad-WR handling, flow steering filters, multicast attach/detach, and ABI structure size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ionic-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ionic-abi.h

## Purpose
Defines AMD/Pensando Ionic RDMA provider ABI version 1 for context, queue descriptors, AH/CQ/QP/SRQ requests and responses, combined-memory-bar options, and expanded doorbell sizing.

## Important APIs, Types, and Functions
Read coverage: 115 lines and 1774 bytes. Visible type families include struct ionic_ctx_req, struct ionic_ctx_resp, struct ionic_qdesc, struct ionic_ah_resp, struct ionic_cq_req, struct ionic_cq_resp, struct ionic_qp_req, struct ionic_qp_resp, struct ionic_srq_req, struct ionic_srq_resp. Important macros/constants include IONIC_ABI_H, IONIC_ABI_VERSION, IONIC_EXPDB_64, IONIC_EXPDB_128, IONIC_EXPDB_256, IONIC_EXPDB_512, IONIC_EXPDB_SQ, IONIC_EXPDB_RQ, IONIC_CMB_ENABLE, IONIC_CMB_REQUIRE, IONIC_CMB_EXPDB, IONIC_CMB_WC, IONIC_CMB_UC. Explicit ioctl-style command names include none.

## Control Flow
Userspace requests a context with optional CMB and expanded doorbell preferences, receives device and doorbell capability data, creates AH/CQ/QP/SRQ resources with queue descriptors, and maps queue and doorbell resources for datapath use.

## State and Persistence Behavior
State includes provider context IDs, admin/user queue descriptors, CMB allocation policy, doorbell format capabilities, and object IDs for CQs, QPs, SRQs, and AHs.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with the Ionic RDMA kernel driver and rdma-core provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
CMB requirement versus enablement flags must be negotiated carefully. Doorbell size and SQ/RQ flags affect mmap layout, and queue descriptor addresses/lengths must be validated.

## Test Signals
Cover context allocation with each CMB mode, expanded doorbell sizes, AH/CQ/QP/SRQ create/destroy, invalid queue descriptors, ABI version checks, and 32-bit layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ionic-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/irdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/irdma-abi.h

## Purpose
Defines Intel iRDMA/iWARP/RoCE provider ABI version 5, retaining compatibility with legacy i40iw generation-1 userspace while covering context, PD, CQ, SRQ, QP, MR registration, QP modification, and AH responses.

## Important APIs, Types, and Functions
Read coverage: 134 lines and 2681 bytes. Visible type families include enum irdma_memreg_type, struct irdma_alloc_ucontext_req, struct irdma_alloc_ucontext_resp, struct irdma_alloc_pd_resp, struct irdma_resize_cq_req, struct irdma_create_cq_req, struct irdma_create_srq_req, struct irdma_create_srq_resp, struct irdma_create_qp_req, struct irdma_mem_reg_req, struct irdma_modify_qp_req, struct irdma_create_cq_resp, struct irdma_create_qp_resp, struct irdma_modify_qp_resp, struct irdma_create_ah_resp. Important macros/constants include IRDMA_ABI_H, IRDMA_ABI_VER. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates a context with feature flags and hardware limits, creates PD/CQ/SRQ/QP resources, registers memory using typed registration requests, modifies QP state, and receives response IDs and mmap keys for queues and doorbells.

## State and Persistence Behavior
State is in iRDMA hardware/kernel objects: queue IDs, push-page and doorbell mappings, WQE allocation state, memory-registration type, QP modification responses, and AH IDs.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with Intel irdma kernel provider, legacy i40iw compatibility, and rdma-core. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Legacy ABI version compatibility is explicit and high risk. Memory-registration type interpretation, push-mode support, queue mmap keys, and reserved fields must match both old and new providers.

## Test Signals
Run iWARP and RoCE provider tests, legacy i40iw userspace compatibility checks, MR registration variants, QP modify paths, queue-size limits, 32-bit layouts, and unsupported feature fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/irdma-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mana-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mana-abi.h

## Purpose
Defines the Microsoft Azure MANA RDMA userspace ABI for CQ, QP, RC QP, WQ, RSS QP creation, RX hash flags, and RSS indirection responses.

## Important APIs, Types, and Functions
Read coverage: 90 lines and 1616 bytes. Visible type families include enum mana_ib_create_cq_flags, struct mana_ib_create_cq, struct mana_ib_create_cq_resp, struct mana_ib_create_qp, struct mana_ib_create_qp_resp, struct mana_ib_create_rc_qp, struct mana_ib_create_rc_qp_resp, struct mana_ib_create_wq, enum mana_ib_rx_hash_function_flags, struct mana_ib_create_qp_rss, struct rss_resp_entry, struct mana_ib_create_qp_rss_resp. Important macros/constants include MANA_ABI_USER_H, MANA_IB_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Userspace creates CQs and queue pairs, optionally uses RC-specific creation payloads or RSS QP creation with hash-function flags and indirection table information, and receives queue IDs plus mmap handles needed for datapath rings.

## State and Persistence Behavior
Kernel/hardware state includes MANA queue IDs, CQ/QP memory mappings, WQ descriptors, RSS configuration, and response-table entries used by accelerated networking.

## Dependencies and Integration Points
It depends on Linux integer types and integrates with the MANA RDMA kernel driver, Azure netvsc/MANA hardware, and rdma-core provider support. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_ioctl_verbs.h>.

## Risks and Edge Cases
RSS hash-function flags and response-entry counts must be validated. Azure device capabilities can vary, so provider code must not assume RC/RSS support without kernel response bits.

## Test Signals
Test CQ/QP/RC-QP/WQ/RSS creation, invalid RSS table sizes, hash flag negotiation, mmap handle use, provider/kernel ABI version, and teardown under active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mana-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx4-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx4-abi.h

## Purpose
Defines Mellanox mlx4 userspace ABI versions 3 and 4 for context, PD, CQ, SRQ, QP, WQ, RSS, TSO, and extended query-device data.

## Important APIs, Types, and Functions
Read coverage: 191 lines and 5117 bytes. Visible type families include struct mlx4_ib_alloc_ucontext_resp_v3, struct mlx4_ib_alloc_ucontext_resp, struct mlx4_ib_alloc_pd_resp, struct mlx4_ib_create_cq, struct mlx4_ib_create_cq_resp, struct mlx4_ib_resize_cq, struct mlx4_ib_create_srq, struct mlx4_ib_create_srq_resp, struct mlx4_ib_create_qp_rss, struct mlx4_ib_create_qp, struct mlx4_ib_create_wq, struct mlx4_ib_modify_wq, struct mlx4_ib_create_rwq_ind_tbl_resp, enum mlx4_ib_rx_hash_function_flags, enum mlx4_ib_rx_hash_fields, struct mlx4_ib_rss_caps, enum query_device_resp_mask, struct mlx4_ib_tso_caps, struct mlx4_uverbs_ex_query_device_resp. Important macros/constants include MLX4_ABI_USER_H, MLX4_IB_UVERBS_NO_DEV_CAPS_ABI_VERSION, MLX4_IB_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates context and PD resources, creates CQs/SRQs/QPs/WQs with private queue buffers, queries RSS/TSO/device capability responses, and uses response fields for BlueFlame, UAR, and queue programming.

## State and Persistence Behavior
State includes UAR/BlueFlame mappings, queue numbers, CQ/SRQ/QP/WQ IDs, RSS indirection table handles, TSO capabilities, and device capability masks.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with mlx4_ib, older ConnectX devices, and rdma-core mlx4 provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
The header explicitly forbids native pointer types to keep 32/64-bit layouts compatible. ABI v3/v4 response differences, RSS hash flags, and query-device masks must remain stable.

## Test Signals
Run mlx4 provider lifecycle tests, v3 no-dev-caps compatibility, 32-bit layout checks, CQ/QP/SRQ/WQ/RSS creation, TSO capability query, and invalid hash field rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx4-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5-abi.h

## Purpose
Defines Mellanox/NVIDIA mlx5 legacy uverbs private ABI for context allocation, device capability queries, CQ/SRQ/QP/WQ/MW/AH/flow creation, packet pacing, CQE compression, RSS, striding RQ, DCI streams, mmap commands, and clock info.

## Important APIs, Types, and Functions
Read coverage: 530 lines and 14059 bytes. Visible type families include struct mlx5_ib_alloc_ucontext_req, enum mlx5_lib_caps, enum mlx5_ib_alloc_uctx_v2_flags, struct mlx5_ib_alloc_ucontext_req_v2, enum mlx5_ib_alloc_ucontext_resp_mask, enum mlx5_user_cmds_supp_uhw, enum mlx5_user_inline_mode, struct mlx5_ib_alloc_ucontext_resp, struct mlx5_ib_alloc_pd_resp, struct mlx5_ib_tso_caps, struct mlx5_ib_rss_caps, enum mlx5_ib_cqe_comp_res_format, struct mlx5_ib_cqe_comp_caps, enum mlx5_ib_packet_pacing_cap_flags, struct mlx5_packet_pacing_caps, enum mlx5_ib_mpw_caps, enum mlx5_ib_sw_parsing_offloads, struct mlx5_ib_sw_parsing_caps, struct mlx5_ib_striding_rq_caps, struct mlx5_ib_dci_streams_caps, enum mlx5_ib_query_dev_resp_flags, enum mlx5_ib_tunnel_offloads, struct mlx5_ib_query_device_resp, struct mlx5_ib_uapi_reg, enum mlx5_ib_create_cq_flags, struct mlx5_ib_create_cq, struct mlx5_ib_create_cq_resp, struct mlx5_ib_resize_cq, ... (+25 more). Important macros/constants include MLX5_ABI_USER_H, MLX5_IB_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates a context, negotiates command support and capability masks, creates PD/CQ/SRQ/QP/WQ and related objects with private payloads, maps UAR/doorbell/clock pages using mmap command IDs, and consumes rich query-device responses for offloads and packet processing features.

## State and Persistence Behavior
State spans hardware context, UARs, doorbells, queue buffers, object IDs, flow counters, clock synchronization data, offload capability bitmaps, and provider command support masks.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with mlx5_ib, ConnectX/NVIDIA hardware, rdma-core mlx5 provider, flow steering, DevX-adjacent capabilities, and timestamp/clock mapping. Direct includes are #include <linux/types.h>, #include <linux/if_ether.h>	/* For ETH_ALEN. */, #include <rdma/ib_user_ioctl_verbs.h>, #include <rdma/mlx5_user_ioctl_verbs.h>.

## Risks and Edge Cases
Large capability structures are compatibility-sensitive; masks must gate every optional field. Mmap command IDs expose hardware pages, CQE compression and packet pacing values must match firmware, and clock-info layout affects timestamp accuracy.

## Test Signals
Run mlx5 rdma-core tests for context negotiation, query-device flags, CQ/QP/SRQ/WQ creation, RSS/TSO/packet pacing/CQE compression, mmap command coverage, clock-info validation, and 32-bit layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_cmds.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_cmds.h

## Purpose
Defines mlx5 provider-specific uverbs ioctl object, method, and attribute IDs for DevX, device memory, UAR/VAR, flow matcher/flow/action, steering anchors, PD query, port query, DMA-BUF MR registration, and Data Direct sysfs path queries.

## Important APIs, Types, and Functions
Read coverage: 365 lines and 11234 bytes. Visible type families include enum mlx5_ib_create_flow_action_attrs, enum mlx5_ib_dm_methods, enum mlx5_ib_dm_map_op_addr_attrs, enum mlx5_ib_query_dm_attrs, enum mlx5_ib_alloc_dm_attrs, enum mlx5_ib_devx_methods, enum mlx5_ib_devx_other_attrs, enum mlx5_ib_devx_obj_create_attrs, enum mlx5_ib_devx_query_uar_attrs, enum mlx5_ib_devx_obj_destroy_attrs, enum mlx5_ib_devx_obj_modify_attrs, enum mlx5_ib_devx_obj_query_attrs, enum mlx5_ib_devx_obj_query_async_attrs, enum mlx5_ib_devx_subscribe_event_attrs, enum mlx5_ib_devx_query_eqn_attrs, enum mlx5_ib_devx_obj_methods, enum mlx5_ib_var_alloc_attrs, enum mlx5_ib_var_obj_destroy_attrs, enum mlx5_ib_var_obj_methods, enum mlx5_ib_uar_alloc_attrs, enum mlx5_ib_uar_obj_destroy_attrs, enum mlx5_ib_uar_obj_methods, enum mlx5_ib_devx_umem_reg_attrs, enum mlx5_ib_devx_umem_dereg_attrs, enum mlx5_ib_pp_obj_methods, enum mlx5_ib_pp_alloc_attrs, enum mlx5_ib_pp_obj_destroy_attrs, enum mlx5_ib_devx_umem_methods, ... (+28 more). Important macros/constants include MLX5_USER_IOCTL_CMDS_H, MLX5_IB_DW_MATCH_PARAM. Explicit ioctl-style command names include MLX5_USER_IOCTL_CMDS_H.

## Control Flow
Userspace issues generic uverbs ioctl commands using these IDs to allocate/query/destroy mlx5-specific objects, submit DevX commands, subscribe to async events, register UMEM, create flow matchers and flows, allocate packet pacing and UAR resources, query PD/port/device context, and create flow actions.

## State and Persistence Behavior
Persistent state is in mlx5 uverbs objects: DevX objects, UMEM registrations, async command/event fds, VAR/UAR/page-pacing handles, flow matchers, steering anchors, flow handles, and flow actions.

## Dependencies and Integration Points
It depends on Linux integer types and `ib_user_ioctl_cmds.h`. It integrates with mlx5_ib's ioctl uAPI, rdma-core mlx5 provider, DevX low-level command access, flow steering, DMA-BUF MR registration, and sysfs Data Direct support. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_ioctl_cmds.h>.

## Risks and Edge Cases
ID stability and mandatory attribute validation are critical. DevX exposes low-level firmware commands, so input/output buffer sizes, object lifetimes, event subscription IDs, and flow match parameter sizes must be tightly checked.

## Test Signals
Run mlx5 DevX and flow steering tests, UMEM/VAR/UAR/page-pacing lifecycle tests, async event fd tests, DMA-BUF MR registration, bad attribute fuzzing, and flow matcher/action create/destroy coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_verbs.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_verbs.h

## Purpose
Defines mlx5 ioctl payload enums and small structures shared by the mlx5 provider-specific ioctl command IDs, including flow action flags, flow table types, packet reformat types, DMA-BUF registration flags, DevX async headers, device-memory types, UAR allocation types, query-port flags, VAR flags, and query responses.

## Important APIs, Types, and Functions
Read coverage: 124 lines and 3907 bytes. Visible type families include enum mlx5_ib_uapi_flow_action_flags, enum mlx5_ib_uapi_flow_table_type, enum mlx5_ib_uapi_flow_action_packet_reformat_type, enum mlx5_ib_uapi_reg_dmabuf_flags, struct mlx5_ib_uapi_devx_async_cmd_hdr, enum mlx5_ib_uapi_dm_type, enum mlx5_ib_uapi_devx_create_event_channel_flags, struct mlx5_ib_uapi_devx_async_event_hdr, enum mlx5_ib_uapi_pp_alloc_flags, enum mlx5_ib_uapi_uar_alloc_type, enum mlx5_ib_uapi_query_port_flags, enum mlx5_ib_uapi_var_alloc_flags, struct mlx5_ib_uapi_reg, struct mlx5_ib_uapi_query_port. Important macros/constants include MLX5_USER_IOCTL_VERBS_H. Explicit ioctl-style command names include MLX5_USER_IOCTL_VERBS_H.

## Control Flow
These payloads are carried in mlx5 ioctl attributes. Userspace reads async command/event headers from fds, describes packet reformat/flow actions, selects DM/UAR/VAR allocation modes, supplies DMA-BUF flags, and receives register or port-query responses.

## State and Persistence Behavior
State is held by the corresponding mlx5 ioctl objects and async fds: event cookies, command output sizes, DM object type, UAR/VAR handles, and queried hardware register/port values.

## Dependencies and Integration Points
It depends on Linux integer types and is paired with `mlx5_user_ioctl_cmds.h`. It integrates with DevX, flow action offload, DMA-BUF memory registration, UAR allocation, and port query paths. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Async headers must be stable for fd read ABI. Packet reformat and flow table enums must match firmware expectations, and DMA-BUF flags alter memory pinning/import behavior.

## Test Signals
Validate DevX async command/event reads, flow action packet reformat creation, DM/UAR/VAR allocation variants, query-port flags, DMA-BUF MR flag handling, and size/alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_verbs.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ocrdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ocrdma-abi.h

## Purpose
Defines Emulex/Broadcom OCRDMA userspace ABI for context, PD, CQ, QP, and SRQ allocation, including BE RoCE compatibility versioning and fixed page-array limits.

## Important APIs, Types, and Functions
Read coverage: 152 lines and 4116 bytes. Visible type families include struct ocrdma_alloc_ucontext_resp, struct ocrdma_alloc_pd_ureq, struct ocrdma_alloc_pd_uresp, struct ocrdma_create_cq_ureq, struct ocrdma_create_cq_uresp, struct ocrdma_create_qp_ureq, struct ocrdma_create_qp_uresp, struct ocrdma_create_srq_uresp. Important macros/constants include OCRDMA_ABI_USER_H, OCRDMA_ABI_VERSION, OCRDMA_BE_ROCE_ABI_VERSION, MAX_CQ_PAGES, MAX_QP_PAGES, MAX_UD_AV_PAGES. Explicit ioctl-style command names include none.

## Control Flow
Provider code allocates context/PD, creates CQs and QPs by passing page arrays and queue attributes, optionally creates SRQs, and receives IDs, DB page indices, and queue metadata for hardware programming.

## State and Persistence Behavior
State is in OCRDMA objects and user queue pages: CQ/QP/SRQ IDs, page-list mappings, doorbell resources, firmware/hardware capability values, and compatibility version fields.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with the ocrdma kernel provider and rdma-core provider for older Emulex/Broadcom RoCE adapters. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Fixed `MAX_CQ_PAGES`, `MAX_QP_PAGES`, and `MAX_UD_AV_PAGES` arrays require strict count validation. Version compatibility with BE RoCE and page-list pinning are high-risk areas.

## Test Signals
Cover context/PD/CQ/QP/SRQ create/destroy, page count boundary checks, BE RoCE ABI version negotiation, invalid page arrays, 32-bit layout, and teardown after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ocrdma-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/qedr-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/qedr-abi.h

## Purpose
Defines QLogic qedr RoCE provider ABI version 8 for context flags, doorbell page mapping, DPM/EDPM capabilities, PD/CQ/QP/SRQ creation, and user doorbell records.

## Important APIs, Types, and Functions
Read coverage: 174 lines and 4307 bytes. Visible type families include enum qedr_alloc_ucontext_flags, struct qedr_alloc_ucontext_req, enum qedr_rdma_dpm_type, struct qedr_alloc_ucontext_resp, struct qedr_alloc_pd_ureq, struct qedr_alloc_pd_uresp, struct qedr_create_cq_ureq, struct qedr_create_cq_uresp, struct qedr_create_qp_ureq, struct qedr_create_qp_uresp, struct qedr_create_srq_ureq, struct qedr_create_srq_uresp, struct qedr_user_db_rec. Important macros/constants include __QEDR_USER_H__, QEDR_ABI_VERSION, QEDR_LDPM_MAX_SIZE, QEDR_EDPM_TRANS_SIZE, QEDR_EDPM_MAX_SIZE. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates a context with optional flags, receives DPM mode and doorbell information, allocates PDs, creates CQs/QPs/SRQs with queue and doorbell-record addresses, and uses response fields for low-latency DPM/EDPM datapaths.

## State and Persistence Behavior
State includes DB page mapping, DPI, DPM mode, PD/CQ/QP/SRQ IDs, queue addresses, user DB records, and inline data size limits tied to hardware firmware.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with qedr, qede/qed hardware support, and rdma-core provider code. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
EDPM/LDPM size constants and doorbell mapping fields must match hardware. User DB records and queue addresses require validation, and ABI version 8 must remain compatible with deployed providers.

## Test Signals
Run qedr provider create/destroy tests, DPM/EDPM mode negotiation, max inline boundary cases, DB record validation, 32-bit layout, and failure unwinding for CQ/QP/SRQ creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/qedr-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_netlink.h

## Purpose
Defines RDMA netlink families, client/op encoding helpers, iWARP port mapper attributes, local service resolution headers, NLDEV command and attribute IDs, counter modes, device types, name assignment, and notification events.

## Important APIs, Types, and Functions
Read coverage: 669 lines and 16882 bytes. Visible type families include struct rdma_ls_resolve_header, struct rdma_ls_ip_resolve_header, struct rdma_nla_ls_gid, enum rdma_nldev_command, enum rdma_nldev_print_type, enum rdma_nldev_attr, enum rdma_nl_counter_mode, enum rdma_nl_counter_mask, enum rdma_nl_dev_type, enum rdma_nl_name_assign_type, enum rdma_nl_notify_event_type. Important macros/constants include _UAPI_RDMA_NETLINK_H, RDMA_NL_GET_CLIENT, RDMA_NL_GET_OP, RDMA_NL_GET_TYPE, IWPM_UABI_VERSION_MIN, IWPM_UABI_VERSION, IWPM_NLA_MAPINFO_SEND_MAX, IWPM_NLA_REMOVE_MAPPING_MAX, RDMA_NL_LS_F_ERR, LS_DEVICE_NAME_MAX, RDMA_NLA_F_MANDATORY, RDMA_NLA_TYPE_MASK. Explicit ioctl-style command names include none.

## Control Flow
Userspace sends netlink messages whose type encodes RDMA client and operation. IWPM flows register/query/add/remove mappings; LS flows resolve IB path or IP data; NLDEV flows query and configure devices, ports, resources, links, statistics, counters, system parameters, char devices, and notifications using the enumerated commands and attributes.

## State and Persistence Behavior
The header names netlink state exposed by RDMA core: device/port identities, resource handles, QP/MR/CQ/CM_ID/counter records, namespace/netdev links, stat modes, char-device paths, and notification events. Persistent state is maintained in kernel RDMA core and drivers.

## Dependencies and Integration Points
It depends on Linux netlink attribute conventions and integrates with rdma-core tools (`rdma`), kernel RDMA netlink, iwcm/iwarp port mapping, LS resolution, network namespaces, and driver stats. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Netlink attribute IDs are stable ABI. Mandatory attribute bits, nested/net-byteorder flags, command ID growth, and large enum tables require careful append-only changes. Misreporting resource IDs or namespace data can break management tools.

## Test Signals
Run rdma netlink selftests and `rdma` tool queries, fuzz missing/wrong mandatory attributes, test IWPM version negotiation, LS resolve success/failure, NLDEV dump consistency under device hotplug, and counter mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_cm.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_cm.h

## Purpose
Defines the RDMA userspace connection manager ABI for `/dev/infiniband/rdma_cm`: command IDs, port spaces, command payloads, connection parameters, multicast, events, options, migration, IB service resolution, and event injection structures.

## Important APIs, Types, and Functions
Read coverage: 381 lines and 7961 bytes. Visible type families include enum rdma_ucm_port_space, struct rdma_ucm_cmd_hdr, struct rdma_ucm_create_id, struct rdma_ucm_create_id_resp, struct rdma_ucm_destroy_id, struct rdma_ucm_destroy_id_resp, struct rdma_ucm_bind_ip, struct sockaddr_in6, struct rdma_ucm_bind, struct __kernel_sockaddr_storage, struct rdma_ucm_resolve_ip, struct rdma_ucm_resolve_addr, struct rdma_ucm_resolve_route, struct rdma_ucm_query, struct rdma_ucm_query_route_resp, struct ib_user_path_rec, struct rdma_ucm_query_addr_resp, struct rdma_ucm_query_path_resp, struct ib_path_rec_data, struct rdma_ucm_query_ib_service_resp, struct ib_user_service_rec, struct rdma_ucm_conn_param, struct rdma_ucm_ud_param, struct ib_uverbs_ah_attr, struct rdma_ucm_ece, struct rdma_ucm_connect, struct rdma_ucm_listen, struct rdma_ucm_accept, ... (+14 more). Important macros/constants include RDMA_USER_CM_H, RDMA_USER_CM_ABI_VERSION, RDMA_MAX_PRIVATE_DATA, RDMA_USER_CM_IB_SERVICE_NAME_SIZE. Explicit ioctl-style command names include none.

## Control Flow
Userspace creates an ID, binds or resolves addresses/routes, queries route/address/path data, listens or connects, accepts/rejects/disconnects, initializes QP attributes, joins/leaves multicast, reads events, sets options, migrates IDs between fds, and handles IB service resolution or written CM events.

## State and Persistence Behavior
Kernel state includes CM IDs, route resolution, event queues, QP association, private data, multicast memberships, ECE data, options, and file ownership. Events report asynchronous state transitions and carry response payloads.

## Dependencies and Integration Points
It depends on Linux integer and socket storage types. It integrates with rdma_cm, cma, ib_cm/iw_cm, RDMA providers, multicast, and rdma-core/librdmacm. Direct includes are #include <linux/types.h>, #include <linux/socket.h>, #include <linux/in6.h>, #include <rdma/ib_user_verbs.h>, #include <rdma/ib_user_sa.h>.

## Risks and Edge Cases
Private data is capped at 256 bytes, sockaddr storage layouts must remain compatible, event ordering and ACK semantics are critical, and ID migration changes ownership/lifetime. Port-space and option enums must remain stable.

## Test Signals
Run librdmacm tests for resolve/connect/listen/accept/reject/disconnect, multicast join/leave, event read/ack ordering, ID migration, ECE/private-data limits, IPv4/IPv6/IB service resolution, and 32-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl.h

## Purpose
Collects ioctl command numbers for legacy RDMA character devices, including user MAD agent registration and HFI1 context/TID/control operations.

## Important APIs, Types, and Functions
Read coverage: 85 lines and 3751 bytes. Visible type families include none. Important macros/constants include RDMA_USER_IOCTL_H, IB_IOCTL_MAGIC, IB_USER_MAD_REGISTER_AGENT, IB_USER_MAD_UNREGISTER_AGENT, IB_USER_MAD_ENABLE_PKEY, IB_USER_MAD_REGISTER_AGENT2, HFI1_IOCTL_ASSIGN_CTXT, HFI1_IOCTL_CTXT_INFO, HFI1_IOCTL_USER_INFO, HFI1_IOCTL_TID_UPDATE, HFI1_IOCTL_TID_FREE, HFI1_IOCTL_CREDIT_UPD, HFI1_IOCTL_RECV_CTRL, HFI1_IOCTL_POLL_TYPE, HFI1_IOCTL_ACK_EVENT, HFI1_IOCTL_SET_PKEY, HFI1_IOCTL_CTXT_RESET, HFI1_IOCTL_TID_INVAL_READ, HFI1_IOCTL_GET_VERS. Explicit ioctl-style command names include RDMA_USER_IOCTL_H, IB_IOCTL_MAGIC, IB_USER_MAD_REGISTER_AGENT, IB_USER_MAD_UNREGISTER_AGENT, IB_USER_MAD_ENABLE_PKEY, IB_USER_MAD_REGISTER_AGENT2, HFI1_IOCTL_ASSIGN_CTXT, HFI1_IOCTL_CTXT_INFO, HFI1_IOCTL_USER_INFO, HFI1_IOCTL_TID_UPDATE, HFI1_IOCTL_TID_FREE, HFI1_IOCTL_CREDIT_UPD, HFI1_IOCTL_RECV_CTRL, HFI1_IOCTL_POLL_TYPE, HFI1_IOCTL_ACK_EVENT, HFI1_IOCTL_SET_PKEY, HFI1_IOCTL_CTXT_RESET, HFI1_IOCTL_TID_INVAL_READ, HFI1_IOCTL_GET_VERS.

## Control Flow
UMAD users issue register/unregister/P_Key ioctls with `ib_user_mad` payloads. HFI1 users issue context assignment, info queries, TID update/free/invalidation, credit update, receive control, poll type, event ack, P_Key setting, context reset, and version queries.

## State and Persistence Behavior
The ioctls operate on per-file kernel state: MAD agent registrations and HFI1 user contexts, TID mappings, event bits, receive modes, poll policy, and P_Key settings.

## Dependencies and Integration Points
It depends on `rdma_user_ioctl_cmds.h`, `ib_user_mad.h`, and HFI1 ioctl payload headers. It integrates with ib_umad and hfi1 character-device implementations. Direct includes are #include <rdma/ib_user_mad.h>, #include <rdma/hfi/hfi1_ioctl.h>, #include <rdma/rdma_user_ioctl_cmds.h>.

## Risks and Edge Cases
Ioctl numbers are stable ABI and share the RDMA magic. Payload structure compatibility, HFI1 high command numbers, and operation ordering such as enabling P_Key headers before use are key hazards.

## Test Signals
Run umad and hfi1 ioctl suites, verify command numbers with ioctl decoders, test invalid payload sizes, 32-bit compat, HFI1 context lifecycle, and MAD register/unregister error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl_cmds.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl_cmds.h

## Purpose
Defines the generic RDMA ioctl syscall envelope: magic number, ioctl command encoding, `ib_uverbs_attr`, attribute flags, and `ib_uverbs_ioctl_hdr`.

## Important APIs, Types, and Functions
Read coverage: 87 lines and 2617 bytes. Visible type families include struct ib_uverbs_attr, struct ib_uverbs_ioctl_hdr. Important macros/constants include RDMA_USER_IOCTL_CMDS_H, RDMA_IOCTL_MAGIC, RDMA_VERBS_IOCTL. Explicit ioctl-style command names include RDMA_USER_IOCTL_CMDS_H, RDMA_IOCTL_MAGIC, RDMA_VERBS_IOCTL.

## Control Flow
Userspace calls ioctl with `RDMA_VERBS_IOCTL`, passing a header containing length, object ID, method ID, number of attributes, and driver ID. The kernel copies the attribute array, interprets each `ib_uverbs_attr` as pointer/object/ID data according to command metadata, and dispatches to the uverbs handler.

## State and Persistence Behavior
No state is stored in the header. The envelope references uverbs objects and user buffers that the kernel validates and may create, destroy, or mutate during dispatch.

## Dependencies and Integration Points
It depends on Linux ioctl and integer types. It is the low-level container used by `ib_user_ioctl_cmds.h`, `ib_user_ioctl_verbs.h`, and provider-specific ioctl headers. Direct includes are #include <linux/types.h>, #include <linux/ioctl.h>.

## Risks and Edge Cases
Length/count arithmetic, pointer alignment, mandatory flags, attr data union interpretation, and driver-id filtering are safety-critical. The ioctl magic and structure layout cannot change.

## Test Signals
Fuzz ioctl headers and attributes, test zero/large attr counts, wrong driver IDs, unknown object/method IDs, 32-bit pointer layouts, and object lifetime under failing dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl_cmds.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rvt-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rvt-abi.h

## Purpose
Defines the RDMA Verbs Transport shared ABI used by hfi1/qib-style providers for receive work queues, completion queue entries, SGEs, and atomic head/tail wrappers.

## Important APIs, Types, and Functions
Read coverage: 66 lines and 1771 bytes. Visible type families include struct rvt_wqe_sge, struct rvt_cq_wc, struct ib_uverbs_wc, struct rvt_rwqe, struct rvt_rwq. Important macros/constants include RVT_ABI_USER_H, RDMA_ATOMIC_UAPI. Explicit ioctl-style command names include none.

## Control Flow
Userspace maps receive and completion queues, posts `rvt_rwqe` entries containing SGEs, and observes `rvt_cq_wc` completions. Atomic wrapper macros preserve shared head/tail fields in mmaped memory.

## State and Persistence Behavior
State is shared queue memory: RWQ head/tail, max work requests/SGEs, WQE arrays, and CQ completion entries derived from `ib_user_verbs` work completions.

## Dependencies and Integration Points
It depends on Linux integer types and `ib_user_verbs.h`. It integrates with rdmavt-based providers such as hfi1 and qib. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_verbs.h>.

## Risks and Edge Cases
Queue memory is shared between kernel and userspace, so alignment, atomicity, and producer/consumer ordering are critical. SGE counts and array bounds must be enforced by providers.

## Test Signals
Exercise rdmavt provider receive queues and CQ polling, shared head/tail wraparound, max SGE validation, 32-bit layout, and stress under concurrent post/poll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rvt-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/siw-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/siw-abi.h

## Purpose
Defines the Software iWARP provider ABI: context/CQ/QP/SRQ/MR responses, opcodes, SGEs, send/receive queue elements, completion entries, CQ notification flags, and shared CQ control.

## Important APIs, Types, and Functions
Read coverage: 186 lines and 3426 bytes. Visible type families include struct siw_uresp_create_cq, struct siw_uresp_create_qp, struct siw_ureq_reg_mr, struct siw_uresp_reg_mr, struct siw_uresp_create_srq, struct siw_uresp_alloc_ctx, enum siw_opcode, struct siw_sge, enum siw_wqe_flags, struct siw_sqe, struct siw_rqe, enum siw_notify_flags, enum siw_wc_status, struct siw_cqe, struct ib_qp, struct siw_cq_ctrl. Important macros/constants include _SIW_USER_H, SIW_NODE_DESC_COMMON, SIW_ABI_VERSION, SIW_MAX_SGE, SIW_UOBJ_MAX_KEY, SIW_INVAL_UOBJ_KEY, SIW_MAX_INLINE. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates context and objects, registers memory, posts SQ/RQ elements with SIW opcodes and flags, uses inline data storage within SGE space, polls `siw_cqe` completions, and arms CQs through shared control fields.

## State and Persistence Behavior
State is in software iWARP queues and shared control memory: object keys, queue IDs, work queue entries, completion entries, notification flags, and memory registration keys.

## Dependencies and Integration Points
It depends on Linux integer types and integrates with the siw kernel provider, rdma-core, and TCP/iWARP software datapath. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Inline data depends on `SIW_MAX_SGE >= 2`; shared CQ arming requires memory ordering; opcode/status values must match userspace provider expectations; and software validation must reject malformed WQEs.

## Test Signals
Run siw loopback RDMA tests, MR registration, all send/RDMA/atomic opcode paths, inline send limits, CQ notification/arming, error completions, and invalid WQE fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/siw-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/vmw_pvrdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/vmw_pvrdma-abi.h

## Purpose
Defines VMware paravirtual RDMA userspace ABI: UAR doorbell bits, work request opcodes, completion status/opcode/flags, network types, object create responses, address vectors, SGEs, SQ/RQ WQE headers, masked atomics, and CQEs.

## Important APIs, Types, and Functions
Read coverage: 310 lines and 8011 bytes. Visible type families include enum pvrdma_wr_opcode, enum pvrdma_wc_status, enum pvrdma_wc_opcode, enum pvrdma_wc_flags, enum pvrdma_network_type, struct pvrdma_alloc_ucontext_resp, struct pvrdma_alloc_pd_resp, struct pvrdma_create_cq, struct pvrdma_create_cq_resp, struct pvrdma_resize_cq, struct pvrdma_create_srq, struct pvrdma_create_srq_resp, struct pvrdma_create_qp, struct pvrdma_create_qp_resp, struct pvrdma_ex_cmp_swap, struct pvrdma_ex_fetch_add, struct pvrdma_av, struct pvrdma_sge, struct pvrdma_rq_wqe_hdr, struct pvrdma_sq_wqe_hdr, struct pvrdma_cqe. Important macros/constants include __VMW_PVRDMA_ABI_H__, PVRDMA_UVERBS_ABI_VERSION, PVRDMA_UAR_HANDLE_MASK, PVRDMA_UAR_QP_OFFSET, PVRDMA_UAR_QP_SEND, PVRDMA_UAR_QP_RECV, PVRDMA_UAR_CQ_OFFSET, PVRDMA_UAR_CQ_ARM_SOL, PVRDMA_UAR_CQ_ARM, PVRDMA_UAR_CQ_POLL, PVRDMA_UAR_SRQ_OFFSET, PVRDMA_UAR_SRQ_RECV. Explicit ioctl-style command names include none.

## Control Flow
Guest userspace creates RDMA objects through uverbs, mmaps a paravirtual UAR, posts SQ/RQ WQEs using PVRDMA layouts, rings doorbells with send/recv/CQ/SRQ bits, and polls CQEs returned by the hypervisor-backed device.

## State and Persistence Behavior
State is shared between guest userspace, guest kernel driver, and virtual device: UAR doorbell pages, queue memory, object handles, AV data, WQE headers, completion entries, and ABI versioned capabilities.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with VMware PVRDMA virtual hardware, hypervisor transport, and rdma-core provider support. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
This is a guest/hypervisor ABI; doorbell bit definitions, queue layouts, and completion codes must remain stable across host and guest versions. Masked atomic fields and network type enums need strict validation.

## Test Signals
Run PVRDMA guest/provider tests for object creation, SQ/RQ posting, CQ polling and arming, masked atomic operations, UAR doorbells, live migration/version compatibility, and malformed WQE rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/vmw_pvrdma-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/regulator/regulator.h -->
# sources/distributed-fs/ceph-client/include/uapi/regulator/regulator.h

## Purpose
Defines the userspace generic-netlink ABI for regulator event notifications, including event bit masks, event payload structure, family name/version, multicast group, and command/attribute IDs.

## Important APIs, Types, and Functions
Read coverage: 86 lines and 2878 bytes. Visible type families include struct reg_genl_event. Important macros/constants include _UAPI_REGULATOR_H, REGULATOR_EVENT_UNDER_VOLTAGE, REGULATOR_EVENT_OVER_CURRENT, REGULATOR_EVENT_REGULATION_OUT, REGULATOR_EVENT_FAIL, REGULATOR_EVENT_OVER_TEMP, REGULATOR_EVENT_FORCE_DISABLE, REGULATOR_EVENT_VOLTAGE_CHANGE, REGULATOR_EVENT_DISABLE, REGULATOR_EVENT_PRE_VOLTAGE_CHANGE, REGULATOR_EVENT_ABORT_VOLTAGE_CHANGE, REGULATOR_EVENT_PRE_DISABLE, REGULATOR_EVENT_ABORT_DISABLE, REGULATOR_EVENT_ENABLE, REGULATOR_EVENT_UNDER_VOLTAGE_WARN, REGULATOR_EVENT_OVER_CURRENT_WARN, REGULATOR_EVENT_OVER_VOLTAGE_WARN, REGULATOR_EVENT_OVER_TEMP_WARN, REGULATOR_EVENT_WARN_MASK, REG_GENL_ATTR_MAX, REG_GENL_CMD_MAX, REG_GENL_FAMILY_NAME, REG_GENL_VERSION, REG_GENL_MCAST_GROUP_NAME. Explicit ioctl-style command names include none.

## Control Flow
Kernel regulator core publishes generic-netlink multicast messages on `reg_event`/`reg_mc_group` when voltage/current/temperature/enable/disable events occur. Userspace subscribes, receives `reg_genl_event`, and interprets the bitmask plus regulator name attribute.

## State and Persistence Behavior
The header stores no state. Runtime state is in regulator devices and the generic-netlink multicast notification path; events represent transient condition changes and warnings.

## Dependencies and Integration Points
It depends on Linux integer types and generic-netlink conventions. It integrates with regulator core notifiers, power-management daemons, monitoring tools, and device-specific regulator drivers. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Event bit stability and family/group names are userspace ABI. Warning-mask composition must include only warn bits, and regulator names must be bounded and consistently encoded in netlink attributes.

## Test Signals
Trigger each regulator notifier event in test drivers or fault-injection setups, verify generic-netlink family discovery, multicast subscription, event bit decoding, name attribute presence, and compatibility with older userspace listeners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/regulator/regulator.h -->
