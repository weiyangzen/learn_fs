# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/reg_fields.h

Purpose: centralizes Data Fabric register field masks used by ATL address translation. It documents revision-specific register names, access types, and bit ranges for coherent-station IDs, fabric masks, DRAM base/limit, offset, interleave, remap, socket, die, node, and hash-control fields.

Important definitions: masks include `DF2_COH_ST_FABRIC_ID`, `DF4p5_COH_ST_FABRIC_ID`, `DF3_COMPONENT_ID_MASK`, `DF4_COMPONENT_ID_MASK`, destination fabric ID masks, `DF_ADDR_RANGE_VAL`, `DF2_BASE_ADDR`, `DF4_BASE_ADDR`, `DF_DRAM_HOLE_BASE_MASK`, `DF2_DRAM_LIMIT_ADDR`, `DF4_DRAM_LIMIT_ADDR`, hash-control bits, high-address offset masks, interleave address/channel/die/socket masks, `DF_LOG2_ADDR_64K_SPACE0`, DF major/minor revision fields, node/socket/die masks and shifts, and DF4 remap controls.

Control flow: this header has no executable flow. Its macros are consumed by `system.c` to determine DF revision and ID masks, by `map.c` to decode address maps, and by translation logic elsewhere in ATL to interpret register fields consistently.

State and persistence: no state is held. It is compile-time metadata expressed with `GENMASK()` and `BIT()` macros.

Dependencies and integration: included through ATL internal headers. It depends on Linux bitfield conventions and assumes the associated register comments remain synchronized with AMD DF documentation. It is the contract between low-level register reads and semantic fields in `df_cfg` and `ctx->map`.

Risks: wrong masks silently corrupt address translation. Several fields vary by DF revision while sharing similar register names, so copy/paste mistakes are high impact. `DF4_HI_ADDR_OFFSET` deliberately includes reserved bits to follow reference code; future hardware changes may need more precise masking. The comments contain a likely duplicated DF3 destination fabric ID row, which is harmless to compilation but a documentation review signal.

Test signals: build coverage for all ATL users, register-decoding unit tests with synthetic values per DF revision, MI300 offset decoding, remap select decoding, and comparisons against platform reference address translations.
