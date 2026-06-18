# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/security.h

Purpose: declares the common Habanalabs security/protection-bit data contracts used by ASIC-specific security setup code and the generic implementation in `security.c`.

Important APIs/types/functions: constants define global error address/cause offsets and address masks. `struct hl_special_block_info` describes repeated ASIC special-block addressing by block type, base, major/minor/sub_minor counts, and offsets. `struct hl_automated_pb_cfg` models generated protection-bit programming for a block type, including `prot_map`, `data_map`, and data arrays. `struct hl_special_blocks_cfg` groups privileged/secured automated PB configuration and skip policy. `struct hl_skip_blocks_cfg` defines block-type, range, and hook-based exclusions. `struct iterate_special_ctx` carries an iterator callback and opaque data. The header declares `hl_iterate_special_blocks()` and `hl_check_for_glbl_errors()`.

Control flow: consumers populate these structures from generated per-ASIC security data, then pass them to generic iteration and checking code. The iterator callback receives block id and major/minor/sub_minor coordinates for each included special-block instance. Skip hooks can suppress individual instances dynamically before the callback runs.

State and persistence behavior: the header defines in-memory metadata only. The structures point to generated arrays and callback hooks owned by ASIC-specific code. Hardware persistence is handled by code that consumes these definitions, not by the header.

Dependencies and integration points: depends on Linux `io-64-nonatomic-lo-hi.h`, `struct range`, and forward-declared `struct hl_device`. It is included by the common security implementation and ASIC-specific security sources such as Gaudi/Gaudi2/Goya security files.

Risks and test signals: risks are ABI-style structure drift between generated headers and generic code, incorrect interpretation of FW-facing base addresses, and callback signature mismatch. Test signals are successful builds of all ASIC security files, iteration over known generated special-block tables, skip hook coverage, and global error address decoding matching ASIC register maps.
