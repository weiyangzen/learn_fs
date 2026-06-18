# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser_rt.c

## Purpose
`ice_parser_rt.c` is the software interpreter for the ICE parser tables created by `ice_parser.c`. It resets runtime registers from metadata init, loads packet bytes, iterates IMEM/boost/parse-graph actions, executes the supported ALU subset, tracks parser flags, markers, protocol offsets, and resolves final PTYPE and block-specific flags into `struct ice_parser_result`.

## Important APIs, Types, and Functions
- Public runtime APIs: `ice_parser_rt_reset()`, `ice_parser_rt_pktbuf_set()`, and `ice_parser_rt_execute()`.
- Register helpers: `ice_rt_tsr_set()`, `ice_rt_ho_set()`, `ice_rt_np_set()`, `ice_rt_nn_set()`, `ice_rt_flag_set()`, `ice_rt_gpr_set()`, and `ice_rt_err_set()`.
- Key builders: `ice_bst_key_init()`, `ice_pk_build()`, `ice_imem_pgk_init()`, and `ice_bst_pgk_init()`.
- Execution helpers: ALU source extraction through `ice_hv_bit_sel()`/`ice_reg_bit_sel()`, pending updates through `ice_gpr_add()`, `ice_flg_add()`, `ice_err_add()`, and commit through `ice_pu_exe()`.
- Result helpers: `ice_marker_update()`, `ice_proto_off_update()`, `ice_ptype_resolve()`, `ice_proto_off_resolve()`, and `ice_result_resolve()`.

## Control Flow
`ice_parser_rt_reset()` saves the parser pointer, clears runtime state, loads metadata init entry 0 into TSR/header offset/program counter/next node, and initializes parser flags. `ice_parser_rt_pktbuf_set()` copies up to `ICE_PARSER_MAX_PKT_LEN` bytes into the runtime buffer, records the original length, and refreshes the header-vector GPR window from the current header offset.

`ice_parser_rt_execute()` loops until a last-round action, error, parse graph miss, or header offset beyond packet length. Each round loads the IMEM entry at the current program counter, builds a boost TCAM key, optionally matches a boost entry, chooses parse-graph key builders and ALUs from either IMEM or boost depending on boost-main override bits, matches parse graph CAM or nomatch CAM/spill tables, executes parse graph and ALUs in priority order, commits pending register/flag/error updates, adjusts header offset, updates markers and protocol offsets, and proceeds to the next node/program counter.

At the end, result resolution copies parser flags, redirects exposed packet flags, builds SW/FD/RSS flags from XLT key builders, serializes collected protocol/offset pairs, and resolves PTYPE through marker TCAM.

## State and Persistence
Runtime state is transient in `struct ice_parser_rt`: GPRs, packet buffer, current parser keys, ALU pointers, pending update buffer, marker bitmap, protocol presence, and offsets. It mutates no persistent hardware or package data. It does mutate the embedded runtime owned by `struct ice_parser`, so callers should treat a parser instance as single-run state unless externally serialized.

## Dependencies and Integration Points
The runtime depends on decoded parser tables and match helpers from `ice_parser.c`, constants and structures from `ice_parser.h`, debug helpers from `ice_common.h`, and bit-reversal/bitfield utilities. It is called by `ice_parser_run()` and feeds profile construction through `struct ice_parser_result`.

## Risks
Only a subset of ALU opcodes is implemented; unsupported instructions are logged and otherwise ignored, which can make software parser results diverge from hardware for packages requiring more operations. `ice_err_add()` appears to update `pu->flg_val` rather than `pu->err_val`, which means pending error updates may not commit as intended. Packet length handling copies only the capped buffer length but stores original `pkt_len`, so header offset checks can pass for offsets beyond copied bytes if callers pass packets longer than the cap. Protocol offset result arrays have fixed sizes and `ice_proto_off_resolve()` relies on table bounds to avoid overflow.

## Test Signals
Good tests include golden packet parses compared with hardware/DDP expected PTYPE, protocol offsets, and flags; round-by-round CAM/boost selection tests; ALU opcode fixtures for each supported opcode; packet length edge cases at 0, short, 504, and longer than 504 bytes; and marker/PTYPE resolution tests. A targeted test should cover error register ALU writes to confirm or expose the `err_val` pending-update behavior.
