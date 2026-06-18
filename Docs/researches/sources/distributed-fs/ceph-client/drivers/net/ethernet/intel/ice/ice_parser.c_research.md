# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser.c

## Purpose
`ice_parser.c` builds and manages the software representation of the ICE packet parser from DDP/package sections. It parses binary section entries into typed tables, provides TCAM/CAM match helpers, creates/destroys parser instances, allows runtime adjustment of DVM and tunnel-port boost entries, runs packets through the runtime executor, and converts parser results into field-vector profiles for switch/ACL/FD/RSS blocks.

## Important APIs, Types, and Functions
- Section/table framework: `ice_parser_sect_item_get()` chooses item sizes by section ID, and `ice_parser_create_table()` allocates and fills typed tables using `ice_pkg_enum_entry()`.
- Table parsers: IMEM (`ice_imem_parse_item()`), metadata init (`ice_metainit_parse_item()`), parse graph CAM/spill/nomatch (`ice_pg_cam_parse_item()`, `ice_pg_sp_cam_parse_item()`, `ice_pg_nm_cam_parse_item()`, `ice_pg_nm_sp_cam_parse_item()`), boost TCAM (`ice_bst_parse_item()`), labels (`ice_parse_lbl_item()`), marker PTYPE TCAM, marker groups, protocol groups, flag redirection, and XLT key builders.
- Match helpers: `ice_pg_cam_match()`, `ice_pg_nm_cam_match()`, `ice_bst_tcam_match()`, `ice_bst_tcam_search()`, `ice_ptype_mk_tcam_match()`, and `ice_flg_redirect()`.
- Parser lifecycle/API: `ice_parser_create()`, `ice_parser_destroy()`, `ice_parser_run()`, `ice_parser_result_dump()`, `ice_parser_dvm_set()`, tunnel setters, `ice_parser_profile_init()`, and `ice_parser_profile_dump()`.
- Key builder conversion: `ice_xlt_kb_flag_get()` maps 64-bit packet flags into 16-bit block-specific key flags.

## Control Flow
`ice_parser_create()` allocates `struct ice_parser`, stores `hw`, links the embedded runtime back to the parser, then builds every required table from `hw->seg`. Any failed table creation routes to `ice_parser_destroy()` for cleanup and returns the original error pointer. `ice_parser_run()` resets the runtime, loads the packet, and delegates execution to `ice_parser_rt_execute()` in `ice_parser_rt.c`.

The parsing helpers are mostly bitfield unpackers: each package section has fixed entry sizes and a table length from `ice_parser.h`; raw bytes are shifted/masked into typed structures. CAM matching is linear over the relevant table and compares only valid key portions. Boost and marker TCAMs use ternary matching through `key`/`key_inv` arrays. DVM and tunnel setters mutate boost TCAM keys in memory by finding labeled entries and marking them valid/invalid or programming UDP port bytes.

`ice_parser_profile_init()` starts from a parser result and packet/mask buffers, chooses block-specific flags and default masks, then walks the mask buffer in two-byte windows. For each masked word, it finds the nearest parsed protocol offset and emits a field-vector entry until `ICE_PARSER_FV_MAX`.

## State and Persistence
Parser state is allocated memory owned by `struct ice_parser`: all table pointers plus the embedded runtime. It is derived from the package segment `hw->seg` and freed by `ice_parser_destroy()`. `ice_parser_dvm_set()` and tunnel setters intentionally mutate the in-memory boost TCAM table but do not write the package or hardware NVM. Runtime packet state is transient in `psr->rt`.

## Dependencies and Integration Points
The file depends on `ice_common.h`, package enumeration helpers, section IDs, Linux allocation/bitfield helpers, and debug output via `ice_hw_to_dev()`/`ice_debug()`. It integrates with parser runtime execution (`ice_parser_rt.c`), parser type definitions (`ice_parser.h`), flow profile generation for `enum ice_block`, and DDP package contents loaded into `hw->seg`.

## Risks
Most binary parsers use raw casts such as `*(u64 *)buf`; they depend on package alignment and native endian assumptions matching the DDP layout. Table creation does not visibly bounds-check computed `idx` against `length`, so malformed section offsets could index beyond allocated tables. TCAM/CAM searches are linear and can be expensive but table sizes are bounded. `ice_tunnel_port_set()` uses an `||` match when deleting high/low UDP port bytes, which may remove a slot if either byte matches rather than requiring a full port match. Profile generation reads two-byte words from packet/mask buffers and assumes enough alignment/length for `off < buf_len - 1`.

## Test Signals
Useful tests include parser creation against known-good and intentionally incomplete DDP segments, table entry decoding golden vectors, CAM/TCAM ternary match fixtures, DVM/tunnel mutation tests that add/remove labels correctly, parser runs over representative packets, and profile generation for SW/ACL/FD/RSS blocks with mask buffers at edge lengths and more than 24 candidate fields.
