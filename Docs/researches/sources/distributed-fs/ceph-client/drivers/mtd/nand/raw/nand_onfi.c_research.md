# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_onfi.c

Purpose: this file detects and parses ONFI-compliant NAND devices. It validates parameter pages, recovers damaged parameter data by bitwise majority, fills memory-organization and ECC requirements, records optional command/timing capabilities, and parses the extended parameter page when needed.

Important APIs, types, and functions: `nand_onfi_detect()` is the main entry point, `onfi_crc16()` computes ONFI CRCs, `nand_flash_detect_ext_param_page()` extracts extended ECC requirements, and `nand_bit_wise_majority()` reconstructs a parameter page from three reads.

Control flow: detection reads ID address `0x20` and requires the `ONFI` signature. It reads up to three parameter pages, accepts the first valid CRC, or performs bitwise-majority recovery and revalidates CRC. Manufacturer fixups may patch the page before parsing. The code selects the highest supported ONFI version, sanitizes strings, fills MTD and NAND memory geometry, handles 16-bit bus flags, sets ECC requirements from either the base or extended parameter page, records SET/GET FEATURES timing support and read-cache support, and stores selected timing values in `chip->parameters.onfi`.

State and persistence: parsed model string and `struct onfi_params` are allocated and stored in `chip->parameters`. Geometry and ECC requirements are copied into `nand_memory_organization`, `mtd_info`, and `nand_device` state; there is no persistent flash mutation.

Dependencies and integration points: this code uses raw NAND read-id/read-param/change-column/data helpers, manufacturer fixup hooks, `nand_legacy_adjust_cmdfunc()` for extended parameter reads on legacy controllers, string sanitization, and ONFI structures from the raw NAND internals.

Risks: non-power-of-two page/block counts are truncated to match MTD expectations. Extended parameter parsing depends on Change Read Column support and may only warn if it fails. Model string allocation can fail after some state has been partially parsed. Majority recovery can accept only data that still passes CRC.

Test signals: test ONFI and non-ONFI ID paths, valid and invalid CRC handling, majority recovery, unsupported revision rejection, extended ECC section parsing, 16-bit bus detection, SET/GET timing feature bits, read-cache capability, manufacturer fixup invocation, and cleanup on allocation failure.
