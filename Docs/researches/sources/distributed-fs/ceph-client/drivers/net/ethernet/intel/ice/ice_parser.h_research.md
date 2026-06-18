# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser.h

## Purpose
`ice_parser.h` defines the ICE software parser's binary-section constants, decoded table structures, runtime state, parser result/profile structures, and public parser APIs. It is the contract between DDP package table decoding, runtime packet parsing, and flow profile construction.

## Important APIs, Types, and Functions
- Section entry sizes and table sizes for IMEM, metadata init, CAM/spill/nomatch, boost TCAM, labels, marker/PTYPE, marker groups, protocol groups, flag redirection, and XLT key builders.
- Program structures: `struct ice_imem_item`, `struct ice_alu`, `struct ice_np_keybuilder`, `struct ice_pg_keybuilder`, and `struct ice_bst_main`.
- Match/action structures: `struct ice_pg_cam_key`, `struct ice_pg_nm_cam_key`, `struct ice_pg_cam_action`, `struct ice_pg_cam_item`, `struct ice_pg_nm_cam_item`, and `struct ice_bst_tcam_item`.
- Runtime/result structures: `struct ice_parser_rt`, `struct ice_parser_result`, `struct ice_parser_proto_off`, and `struct ice_gpr_pu`.
- Parser lifecycle and configuration APIs: `ice_parser_create()`, `ice_parser_destroy()`, `ice_parser_run()`, `ice_parser_dvm_set()`, and tunnel setters.
- Profile structures/APIs: `struct ice_parser_fv`, `struct ice_parser_profile`, `ice_parser_profile_init()`, and `ice_parser_profile_dump()`.

## Control Flow
The header models the parser as package-derived tables plus a runtime interpreter. `struct ice_parser` owns all decoded tables and embeds `struct ice_parser_rt`; execution returns `struct ice_parser_result`; profile initialization then converts the result and a packet mask into `struct ice_parser_profile` entries for a hardware block.

## State and Persistence
All state described here is in memory. Table pointers in `struct ice_parser` cache DDP-derived parser data. `struct ice_parser_rt` contains transient GPRs, packet buffer, boost/parse graph keys, pending updates, markers, protocol presence, and offsets for one run. `struct ice_parser_profile` is caller-owned derived state used to program or match flow profiles elsewhere.

## Dependencies and Integration Points
The header depends on ICE flow definitions for `ICE_FLOW_PTYPE_MAX`, `struct ice_fv_word`, and `enum ice_block`, plus kernel bitmaps and bit macros through common headers. It is consumed by `ice_parser.c`, `ice_parser_rt.c`, and flow/filter code that needs parser output or profile data.

## Risks
Many constants encode hardware/DDP binary formats; any mismatch with firmware package layout breaks parser creation or packet interpretation. Array sizes are fixed and must remain synchronized with runtime assumptions (`ICE_PARSER_PROTO_OFF_PAIR_SIZE`, `ICE_PO_PAIR_SIZE`, and flag/GPR indexes). Public profile limits (`ICE_PARSER_FV_MAX`) must be enforced by callers and implementation to avoid overflowing fixed arrays.

## Test Signals
Compile-time signals include all structures matching expected sizes and no missing declarations across parser modules. Runtime signals include parser table allocation with expected table lengths, packet parses that fill `ptype`, protocol offsets, and flags, and profile initialization respecting field-vector and PTYPE bitmap bounds.
