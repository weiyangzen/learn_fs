# Research: subset-b-004475

Grouped research for Intel ICE driver files under `sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice`. Each section is source-tree aligned for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.c

## Purpose
`ice_nvm.c` implements the ICE driver's low-level NVM/flash access and version discovery path. It wraps Admin Queue NVM commands, provides flat flash and Shadow RAM readers, discovers flash bank geometry, extracts active/inactive NVM, Option ROM, and netlist version data, validates checksums, and exposes firmware update staging/activation commands.

## Important APIs, Types, and Functions
- AdminQ wrappers: `ice_aq_read_nvm()`, `ice_aq_update_nvm()`, `ice_aq_erase_nvm()`, `ice_nvm_write_activate()`, `ice_aq_nvm_update_empr()`, `ice_nvm_set_pkg_data()`, and `ice_nvm_pass_component_tbl()`.
- Locking helpers: `ice_acquire_nvm()` and `ice_release_nvm()` acquire/release `ICE_NVM_RES_ID`, except in blank NVM mode.
- Read helpers: `ice_read_flat_nvm()`, `ice_read_sr_word_aq()`, `ice_read_sr_word()`, `ice_read_flash_module()`, `ice_read_nvm_module()`, `ice_read_nvm_sr_copy()`, and `ice_read_netlist_module()`.
- Discovery/version helpers: `ice_discover_flash_size()`, `ice_determine_active_flash_banks()`, `ice_determine_css_hdr_len()`, `ice_get_nvm_ver_info()`, `ice_get_orom_civd_data()`, `ice_get_orom_ver_info()`, and `ice_get_netlist_info()`.
- Public version readers: `ice_get_inactive_nvm_ver()`, `ice_get_inactive_orom_ver()`, and `ice_get_inactive_netlist_ver()`.
- PFA/PBA helpers: `ice_get_pfa_module_tlv()` walks Preserved Field Area TLVs and `ice_read_pba_string()` decodes the part number string.

## Control Flow
Initialization enters through `ice_init_nvm()`: it reads `GLNVM_GENS` for Shadow RAM size, checks `GLNVM_FLA_LOCKED_M` to reject unsupported blank mode, discovers flash size by bisection, determines active banks and module sizes from Shadow RAM control words, computes CSS header lengths for active/inactive NVM banks, then fills `hw->flash.nvm`, `hw->flash.orom`, and `hw->flash.netlist` from active bank contents. Reads are serialized through `ice_acquire_nvm()`, split by `ice_read_flat_nvm()` into 4 KiB AdminQ/sector-sized commands, and dispatched by `ice_aq_read_nvm()`.

Inactive version reads are bank-relative: `ice_get_flash_bank_offset()` maps active vs inactive NVM/OROM/netlist modules from cached `hw->flash.banks` pointers and sizes, and the specific version helpers read from that computed offset. Option ROM versioning reads the full OROM bank into a `vzalloc()` buffer and scans 512-byte boundaries for a valid `$CIV` record with a zero modulo checksum. Netlist versioning validates the link topology module and reads the netlist ID block in one flash read.

## State and Persistence
The code does not persist data itself, but it mutates the in-memory hardware state in `hw->flash`: Shadow RAM word count, blank mode flag, total flash size, active-bank selection, module pointers/sizes, CSS header lengths, and active version structures. Firmware update functions modify device NVM state through AdminQ commands and may trigger activation or EMP reset behavior. The caller must treat flash writes/activation as persistent hardware changes.

## Dependencies and Integration Points
This file depends on `ice_common.h`, AdminQ descriptor layouts/opcodes, `ice_osdep.h` register and debug helpers, Linux allocation APIs (`kcalloc`, `vzalloc`, `vfree`), endianness helpers, overflow helpers, and `ice_hw_to_dev()` for warnings. It integrates with probe/init through `ice_init_nvm()`, devlink/ethtool style version display through version readers, PBA access through `ice_read_pba_string()`, and firmware update flows through package/component/activate AdminQ commands.

## Risks
NVM access is hardware-stateful and timing-sensitive. Incorrect bank pointer/size interpretation can read the wrong bank or expose inactive pending firmware incorrectly. `ice_read_flat_nvm()` may partially update caller buffers before returning an error. Several parsers assume firmware-provided layouts and use raw casts to little-endian data, so malformed flash data can lead to rejected initialization or misleading version data. OROM scanning allocates the full OROM bank and can fail under memory pressure. Update commands have persistent device impact and must be sequenced with firmware expectations.

## Test Signals
Good signals include successful `ice_init_nvm()` on supported hardware, correct active/inactive version reporting before and after staged updates, checksum validation success/failure coverage, PBA TLV parsing including malformed TLV length/overflow cases, flat NVM reads crossing 4 KiB boundaries, and firmware update command error propagation. Fault injection around AdminQ failures, invalid Shadow RAM control words, missing CIVD records, and short netlist modules would exercise the main defensive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.h

## Purpose
`ice_nvm.h` is the public NVM interface for the ICE driver. It declares the packed Option ROM CIVD structure and the NVM, Shadow RAM, version, checksum, erase/write, package-data, and activation APIs implemented by `ice_nvm.c`.

## Important APIs, Types, and Functions
- `struct ice_orom_civd_info` describes the `$CIV` Option ROM combo-image version record: signature, checksum, combo version, name length, and UTF-16 combo name.
- Resource APIs: `ice_acquire_nvm()` and `ice_release_nvm()`.
- Read APIs: `ice_aq_read_nvm()`, `ice_read_flat_nvm()`, `ice_read_sr_word()`, `ice_get_pfa_module_tlv()`, and `ice_read_pba_string()`.
- Version/init APIs: `ice_init_nvm()`, `ice_get_inactive_orom_ver()`, `ice_get_inactive_nvm_ver()`, and `ice_get_inactive_netlist_ver()`.
- Write/update APIs: `ice_aq_update_nvm()`, `ice_aq_erase_nvm()`, `ice_nvm_validate_checksum()`, `ice_nvm_write_activate()`, `ice_aq_nvm_update_empr()`, `ice_nvm_set_pkg_data()`, and `ice_nvm_pass_component_tbl()`.

## Control Flow
The header is included by ICE common and update code that needs NVM access. It separates direct AdminQ command wrappers from higher-level helpers, so callers can either perform raw module operations or use parsed version/PBA/init routines. The update declarations indicate a multi-stage flow: set package data, pass component tables, write/update/erase as needed, validate checksum, activate, and optionally request EMP reset.

## State and Persistence
The header declares functions that mutate `struct ice_hw` flash cache and, for update paths, persistent device NVM. It does not define storage. Persistent state is entirely in hardware flash and Shadow RAM, while runtime state is held in `hw->flash`.

## Dependencies and Integration Points
The declarations rely on ICE core types from surrounding headers: `struct ice_hw`, AdminQ resource access enums, `struct ice_sq_cd`, and version structures such as `struct ice_orom_info`, `struct ice_nvm_info`, and `struct ice_netlist_info`. It is the integration point between NVM implementation and driver initialization, diagnostics, and firmware update paths.

## Risks
Because the API exposes both safe parsed helpers and raw AdminQ update/erase commands, caller misuse can cause persistent NVM changes. Buffer lengths and pointer validity are caller responsibilities for low-level read/write functions. `struct ice_orom_civd_info` is packed and hardware-layout-dependent, so changes must match firmware layout exactly.

## Test Signals
Compile coverage should ensure all callers include this header without incomplete type issues. Runtime tests should exercise every public declaration through initialization, version read, checksum validation, and firmware update error paths. ABI-sensitive tests should verify `sizeof(struct ice_orom_civd_info)` and field offsets against firmware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_osdep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_osdep.h

## Purpose
`ice_osdep.h` provides the Linux OS adaptation layer used by the ICE shared code. It centralizes kernel includes, MMIO register access macros, polling, flush behavior, DMA memory representation, and debug/hex-dump wrappers.

## Important APIs, Types, and Functions
- MMIO macros: `wr32()`, `rd32()`, `wr64()`, and `rd64()` access registers relative to `struct ice_hw::hw_addr`.
- Polling and flush: `rd32_poll_timeout()` wraps `read_poll_timeout()`, and `ice_flush()` reads `GLGEN_STAT`.
- `ICE_M()` builds shifted unsigned masks from a mask and shift.
- `struct ice_dma_mem` stores virtual address, DMA address, and allocation size.
- `ice_hw_to_dev()` maps ICE hardware state to a Linux `struct device`.
- Debug macros: `ice_debug()`, `_ice_debug_array()`, `ice_debug_array()`, and `ice_debug_array_w_prefix()`.

## Control Flow
Shared ICE code uses these macros directly rather than calling Linux APIs everywhere. Register reads/writes inline to `readl`/`writel` and `readq`/`writeq`. Debug output either maps to `dev_dbg()` under dynamic debug, to `dev_info()` gated by `hw->debug_mask`, or to hex dump helpers depending on `CONFIG_DYNAMIC_DEBUG` and `DEBUG`.

## State and Persistence
The file itself has no storage. Its MMIO macros read and write persistent hardware register state, while debug behavior depends on `hw->debug_mask` and kernel config. `ice_flush()` causes an MMIO read used to flush posted writes.

## Dependencies and Integration Points
It depends on Linux kernel headers for types, IO, bitops, ethtool, ethernet, polling, PCI IDs, and UDP tunnel support. It is pulled into ICE common code and underpins nearly every hardware-facing source file in the driver.

## Risks
Register macros assume a valid mapped `hw_addr`; misuse before mapping or after teardown can fault. `wr64()`/`rd64()` require the non-atomic lo-hi compatibility include on non-64-bit configs. Debug array formatting in the non-DEBUG fallback manually loops over lengths and depends on `u16 len_l`, so callers should avoid unexpectedly large debug buffers.

## Test Signals
Build coverage across `CONFIG_DYNAMIC_DEBUG`, `DEBUG`, 32-bit, and 64-bit configurations is important. Runtime smoke tests should include register reads/writes through common initialization paths and debug-mask toggling to ensure logs remain bounded and readable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_osdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser_rt.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_parser_rt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.c

## Purpose
`ice_pf_vsi_vlan_ops.c` initializes the VLAN operation vector for a PF VSI. It chooses whether VLAN add/delete, stripping, insertion, and filtering operations should be wired to the VSI's outer-VLAN or inner-VLAN operation table based on whether Double VLAN Mode is enabled.

## Important APIs, Types, and Functions
- `ice_pf_vsi_init_vlan_ops(struct ice_vsi *vsi)` is the only function.
- It fills `struct ice_vsi_vlan_ops` function pointers with `ice_vsi_add_vlan()`, `ice_vsi_del_vlan()`, outer or inner stripping/insertion helpers, and shared RX VLAN filtering helpers.
- It selects `vsi->outer_vlan_ops` when `ice_is_dvm_ena(&vsi->back->hw)` is true, otherwise `vsi->inner_vlan_ops`.

## Control Flow
The function reads the hardware VLAN mode through the PF back pointer. In DVM mode, it points the active operation table at outer VLAN operations. In non-DVM/SVM mode, it points at inner VLAN operations. Add/delete and RX filtering functions are common in both branches; stripping and insertion functions differ by inner vs outer VLAN context.

## State and Persistence
The function mutates function pointers inside the `ice_vsi` instance. It does not directly program hardware, persist settings, or allocate memory. Later VLAN operations persist or clear hardware state through the selected function pointers.

## Dependencies and Integration Points
It depends on `ice_vsi_vlan_ops.h`, `ice_vsi_vlan_lib.h`, `ice_vlan_mode.h`, `ice.h`, and its own header. It integrates with VSI setup paths that need the correct VLAN behavior before netdev or switchdev VLAN operations are invoked.

## Risks
The function assumes `vsi`, `vsi->back`, and `vsi->back->hw` are valid. If called before VLAN mode is finalized or after a mode transition without reinitialization, later operations may target the wrong inner/outer VLAN context. Function pointer initialization is partial to one table per mode, so users must call the correct table for the active mode.

## Test Signals
Tests should verify that DVM mode initializes `outer_vlan_ops` with outer stripping/insertion functions and SVM mode initializes `inner_vlan_ops` with inner functions. Integration signals include successful VLAN add/delete, RX filtering enable/disable, and insertion/stripping behavior on PF VSIs in both VLAN modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.h

## Purpose
`ice_pf_vsi_vlan_ops.h` declares the PF VSI VLAN operation initialization API and forward-declares `struct ice_vsi`.

## Important APIs, Types, and Functions
- Includes `ice_vsi_vlan_ops.h` so the operation-table type is available to callers.
- Forward declaration: `struct ice_vsi`.
- Public function: `ice_pf_vsi_init_vlan_ops(struct ice_vsi *vsi)`.

## Control Flow
The header provides the declaration used by VSI setup code to call the implementation in `ice_pf_vsi_vlan_ops.c`. There is no executable control flow in the header.

## State and Persistence
No state is declared here. The declared function mutates VSI operation pointers at runtime.

## Dependencies and Integration Points
The header is an integration point between PF VSI setup and the VLAN operation implementation. It relies on `ice_vsi_vlan_ops.h` and avoids requiring the full `struct ice_vsi` definition at declaration sites.

## Risks
The header is simple, but include-order issues can arise if callers need the full VSI definition and only include this file. The API name is PF-specific; using it for non-PF VSI types would require checking whether the selected operation table semantics still apply.

## Test Signals
Compile coverage for all callers is the primary signal. Runtime behavior is covered through tests of `ice_pf_vsi_init_vlan_ops()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_protocol_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_protocol_type.h

## Purpose
`ice_protocol_type.h` defines ICE protocol identifiers, tunnel types, hardware protocol IDs, packet header layouts, metadata IDs/offsets, packet flag masks, and extraction structures used by switch/flow recipe logic. It is a shared vocabulary for matching packet fields and metadata in the ICE pipeline.

## Important APIs, Types, and Functions
- Recipe limits: `ICE_NUM_WORDS_RECIPE`, `ICE_MAX_CHAIN_RECIPE`, `ICE_MAX_CHAIN_RECIPE_RES`, `ICE_MAX_CHAIN_WORDS`, and `ICE_CHAIN_FV_INDEX_START`.
- Protocol enums: `enum ice_protocol_type`, `enum ice_sw_tunnel_type`, and `enum ice_prot_id`.
- Hardware protocol constants such as `ICE_MAC_OFOS_HW`, `ICE_IPV4_OFOS_HW`, `ICE_UDP_OF_HW`, and related tunnel/header IDs.
- Header structures: Ethernet, ethertype, VLAN, IPv4, IPv6, SCTP, L4, UDP tunnel, GTP, PFCP, PPPoE, L2TPv3, NVGRE, and `struct ice_hw_metadata`.
- Metadata definitions: MDID IDs, offsets, packet flag masks, and `enum ice_pkt_flags`.
- Extraction structures: `union ice_prot_hdr`, `struct ice_prot_ext_tbl_entry`, and `struct ice_prot_lkup_ext`.

## Control Flow
This is a declarative header with no functions. Flow/recipe code uses these constants and structures to map software protocol types to hardware protocol IDs, compute field offsets, interpret metadata words, and build lookup extraction lists. The comments document MDID bit layouts that downstream code uses when matching VLAN, tunnel, TCP, and error flags.

## State and Persistence
No mutable state is defined. The structures describe packet and metadata layouts, and caller-owned instances may be used to build persistent hardware recipes elsewhere.

## Dependencies and Integration Points
The file depends on Ethernet constants, bit macros, endian types, and `struct ice_fv_word` from surrounding ICE/common headers. It integrates with switch recipe construction, flow director, ACL/RSS matching, parser profile generation, and any logic that maps parsed protocol offsets into field vectors.

## Risks
Layout definitions must match hardware parser and firmware expectations. Several structures intentionally model wire format with big-endian fields; consumers must avoid host-endian comparisons. Metadata comments encode bit meanings that can vary by package/version, and the file notes that not all MDIDs are available to the switch block. Recipe chain limits and field-vector indexes are hard bounds; overflow or misuse can lead to invalid hardware recipes.

## Test Signals
Compile-time checks for structure sizes/offsets and enum/constant consistency are valuable. Runtime flow tests should cover recipes for outer/inner MAC/IP/L4, VLAN flags, tunnel flags, metadata source VSI/PTYPE/length, and chained recipes near `ICE_MAX_CHAIN_WORDS`. Packet classification tests should verify big-endian header fields and protocol offsets are interpreted correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_protocol_type.h -->
