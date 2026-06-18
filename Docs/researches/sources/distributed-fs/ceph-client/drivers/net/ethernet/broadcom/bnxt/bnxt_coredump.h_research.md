# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_coredump.h

Purpose: Defines the private coredump file format and debug DMA helper contracts used by `bnxt_coredump.c`. It names the component/segment IDs used for firmware version, driver-owned backing-store memory, firmware trace backing stores, and crash dump sizing.

Important APIs, types, and functions: Key format types are `bnxt_coredump_segment_hdr`, `bnxt_coredump_record`, `bnxt_driver_segment_record`, `bnxt_coredump`, `bnxt_hwrm_dbg_dma_info`, `hwrm_dbg_cmn_input`, and `hwrm_dbg_cmn_output`. The header exports `bnxt_fill_coredump_seg_hdr()`, `bnxt_get_coredump()`, `bnxt_hwrm_get_dump_len()`, and `bnxt_get_coredump_length()`. Constants include segment signatures, `BNXT_VER_GET_COMP_ID`, `BNXT_DRV_COMP_ID`, context-memory segment IDs, 8 MiB crash dump default length, and debug DMA slice sizes.

Control flow: There is no executable control flow in the header. It provides the structure layout consumed by the coredump implementation: each data segment gets a segment header, optional driver segment records can precede backing-store data, and the whole dump ends with a `bnxt_coredump_record` containing system/time/status metadata.

State and persistence behavior: The definitions describe serialized diagnostic state. Most fields are little-endian on output and become part of the coredump artifact handed to userspace through ethtool/devlink style consumers. The header itself has no mutable state.

Dependencies and integration points: It includes kernel utsname/time/rtc declarations and relies on Broadcom HSI identifiers pulled through including source files. It is directly paired with `bnxt_coredump.c` and indirectly with devlink health dump and ethtool dump paths.

Risks: Structure layout and endian fields are externally visible to dump parsers, so changing sizes or signatures can break tooling. `BNXT_COREDUMP_BUF_LEN(len)` subtracts the trailing record size and is used in bounds checks; misuse with small lengths can underflow if callers are not careful. Context segment ID mappings must stay aligned with `bnxt.h` backing-store type constants.

Test signals: Compile-test coredump users, verify generated dumps have `sEgM` segment signatures and final `cOrE` records, check driver-context segment IDs against backing-store types, and run parsers against live, crash, and driver dumps after any format change.
