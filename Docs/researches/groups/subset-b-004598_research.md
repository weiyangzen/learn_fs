# subset-b-004598 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_debug.c

## Purpose

`qed_debug.c` is the QLogic/Marvell `qed` NIC driver's debug collection, binary dump formatting, and debugfs-facing dispatch implementation. It gathers hardware and firmware diagnostic features from QED devices, including GRC register and memory dumps, idle checks, MCP trace, register FIFO, IGU FIFO, protection override window, firmware assertions, ILT page snapshots, NVRAM images, and all-data bundles. It also contains parsers that turn several binary feature dumps into human-readable text when `cdev->dbg_bin_dump` is not requested.

The file is split into two major roles:

- Low-level producer path: initializes debug metadata from firmware-provided binary arrays, sizes feature buffers with a dry run, reads hardware/NVRAM/firmware state through `qed_rd()`, `qed_wr()`, DMAE, MCP commands, PTT access, and context-manager state, then emits a self-describing sectioned dword stream with a final CRC section.
- User/parser path: parses idle-check, MCP trace, FIFO, protection override, firmware assert, and attention results using debug binary lookup tables and formats text for logs or debugfs output.

## Important APIs, Types, And Tables

Public and cross-file entry points implemented here include:

- `qed_dbg_pf_init()` and `qed_dbg_pf_exit()`: lifecycle hooks that load debug binary buffers from firmware data, set tool version, initialize per-hwfn debug arrays, select engine 0 by default, and free allocated feature buffers at shutdown.
- `qed_dbg_feature()` and `qed_dbg_feature_size()`: generic debugfs-facing feature dispatcher and size query. They acquire a PTT, route through `qed_features_lookup`, allocate/format internal buffers, copy results to the caller, and release the PTT.
- Feature wrappers: `qed_dbg_grc()`, `qed_dbg_idle_chk()`, `qed_dbg_reg_fifo()`, `qed_dbg_igu_fifo()`, `qed_dbg_protection_override()`, `qed_dbg_fw_asserts()`, `qed_dbg_ilt()`, `qed_dbg_mcp_trace()` and corresponding `*_size()` functions.
- Bundle APIs: `qed_dbg_all_data()` and `qed_dbg_all_data_size()` produce a multi-feature dump with compact headers for each feature and optional NVRAM images.
- Debug engine APIs: `qed_get_debug_engine()` and `qed_set_debug_engine()` read/write `cdev->engine_for_debug`.
- Debug binary setup: `qed_dbg_set_bin_ptr()` and `qed_dbg_user_set_bin_ptr()` translate firmware binary headers into `p_hwfn->dbg_arrays[]`; `qed_dbg_alloc_user_data()` allocates parser/user state.
- GRC configuration: `qed_dbg_grc_config()` validates and applies GRC parameters and presets; `qed_dbg_grc_set_params_default()` restores non-persistent defaults.
- Attention APIs: `qed_dbg_read_attn()` reads attention/parity status for a block; `qed_dbg_parse_attn()` decodes and prints attention bit names.
- Parser APIs: `qed_get_*_results_buf_size()` and `qed_print_*_results()` for idle check, MCP trace, reg FIFO, IGU FIFO, protection override, and firmware asserts.

Important local data structures include:

- Static platform/debug descriptors: `struct chip_defs`, `hw_type_defs`, `storm_defs`, `grc_param_defs`, `rss_mem_defs`, `vfc_ram_defs`, `big_ram_defs`, `phy_defs`, `split_type_defs`, and `rbc_reset_defs`.
- Dump encoder helpers: `qed_dump_str_param()`, `qed_dump_num_param()`, `qed_dump_section_hdr()`, `qed_dump_common_global_params()`, and `qed_dump_last_section()`.
- Hardware read helpers: `qed_grc_dump_addr_range()`, `qed_grc_dump_reg_entry()`, `qed_grc_dump_registers()`, `qed_grc_dump_mem()`, `qed_grc_dump_memories()`, and specialized GRC dump routines for RSS, VFC, Big RAM, MCP, PHY, MCP HW dump, static debug, context, and reset/modified registers.
- Parser helpers: `qed_read_param()`, `qed_read_section_hdr()`, `qed_print_section_params()`, cyclic MCP trace readers, and per-feature parse functions.
- `qed_features_lookup[]`: central dispatch table mapping `enum qed_dbg_features` values to feature names, size functions, dump functions, optional print functions, and result-size functions.
- Status and formatting lookup tables: `s_status_str[]`, idle severity strings, MCP trace levels, access/privilege/protection/master strings, REG FIFO errors, IGU FIFO source/error strings, and IGU address decoding ranges.

## Control Flow

Initialization starts in `qed_dbg_pf_init()`. It sets the static application/tool version to `TOOLS_VERSION`, derives the debug-values region from the loaded firmware image by using the first firmware dword as an offset, and installs those binary debug arrays for every hardware function. Most public feature paths then call `qed_dbg_dev_init()` lazily. That routine detects BB/K2 chip type, ASIC mode, port mode, CMT/100G mode, number of ports/PFs/VFs, initializes GRC params, enables DMAE use, and records `dbg_info.initialized`.

Most feature dump APIs follow a common two-pass pattern:

1. A `*_get_dump_buf_size()` function initializes the debug device and calls the same internal dump routine with `dump=false`. In dry-run mode the dump routine returns the exact number of dwords it would emit without touching most payload buffers.
2. The corresponding `*_dump()` function validates caller capacity, updates reset state when needed, calls the internal routine with `dump=true`, and generally resets non-persistent GRC parameters to defaults afterward.

The generic debugfs path is `qed_dbg_feature()` -> PTT acquire -> `qed_dbg_dump()` -> feature-specific `get_size`/`perform_dump` -> optional `format_feature()` -> copy to caller -> PTT release. `qed_dbg_dump()` frees stale per-feature buffers, refuses oversized features over `MAX_DBG_FEATURE_SIZE_DWORDS`, uses `vmalloc()`, handles MCP-trace missing-NVRAM-meta as a binary-success special case, and converts binary output to text if a parser is available and `dbg_bin_dump` is false.

The GRC flow is the largest:

- `qed_grc_dump()` writes global params and dump metadata, optionally dumps reset registers, unresets blocks, asks MCP to mask parities, dumps attention/stall registers before mutating them, optionally stalls Storms, dumps regular registers and special TDIF/RDIF skip-pattern registers, dumps debug-array-described memories, MCP scratch/cpu/reg state, CM context, RSS memories, Big RAM, VFC memories, K2 PHY TBUS data, MCP hardware dump from NVRAM, and static debug bus lines.
- Register dumps are driven by binary debug arrays split by port/PF/VF. `qed_grc_dump_addr_range()` handles split pretend mode, DMAE fallback, wide-bus protection, GRC register reads, and progress logging.
- Memory dumps use debug memory descriptors and `qed_grc_is_mem_included()` to honor GRC include parameters and Storm association.
- Static debug temporarily disables the debug bus, resets/configures the DBG block, iterates all blocks/lines, reads calendar output data, and shuts the debug bus back down.
- Cleanup at the end may unstall Storms if `DBG_GRC_PARAM_UNSTALL` is set, clears parity statuses, and unmasks parities if they were masked.

Idle check flow reads rule/condition/immediate metadata from binary arrays. It evaluates mode trees, skips blocks in reset, reads condition registers or memory entries, runs a condition function from `cond_arr[]`, and emits failure records with condition and info register values. Parsing later maps rule IDs and register IDs back to human-readable strings, printing both firmware and LSI idle-check messages.

MCP trace flow validates the trace signature in MCP scratchpad, optionally halts MCP for a consistent read, dumps the trace cyclic buffer, finds the matching metadata image in NVRAM by running bundle ID, validates NVRAM metadata signatures, and stores it in the dump. Parsing allocates module/format metadata, walks the cyclic trace from `trace_oldest` to `trace_prod`, decodes variable-width parameters, and formats messages with the module and trace level.

FIFO and protection override flows dump bounded hardware windows. REG FIFO and IGU FIFO drain valid entries up to fixed depths using wide-bus-safe reads. Protection override reads the valid override window count and clamps to maximum depth. Parsers validate section names, element counts, and decode packed bitfields into text.

Firmware assertions read per-Storm `fw_info` from Storm RAM, locate the assert ring section, and dump the last assert list element for each active Storm. ILT dumping walks context-manager ILT shadow descriptors, connection/task PF/VF page ranges, and SRC pages. Unlike most features, ILT can partially dump to the caller-provided buffer and records both full and actual dump sizes before the final CRC section.

`qed_dbg_all_data()` serializes a collection bundle under `qed_dbg_lock`. It switches engines, forces binary dump mode, collects two idle checks, reg FIFO, IGU FIFO, protection override, firmware asserts, optional ILT, and GRC per engine, then collects MCP trace and selected NVRAM images once. Each segment is prefixed by a compact `REGDUMP_HEADER_*` header from `qed_calc_regdump_header()`.

## State And Persistence Behavior

Persistent or mutable state is mostly in `struct qed_dev`, `struct qed_hwfn`, and static file variables:

- `s_app_ver` is a file-static global set by `qed_dbg_set_app_ver()`. If not set, `qed_dbg_dev_init()` fails with `DBG_STATUS_APP_VERSION_NOT_SET`.
- `p_hwfn->dbg_info` holds debug initialization state, chip/mode information, GRC parameter values, reset-state cache, DMAE availability, pretend state, idle-check cached size, bus state, and register-read counters.
- `p_hwfn->dbg_arrays[]` holds pointers and sizes into the firmware-provided binary debug arrays. These arrays are essential for register/memory descriptors, mode trees, attention metadata, parsing strings, idle-check rules, and MCP trace/attention parsing.
- `p_hwfn->dbg_user_info` holds parser/user data such as MCP trace metadata and optional user-supplied MCP trace metadata buffer.
- `cdev->dbg_features[]` stores per-feature allocated dump buffers, byte sizes, and dumped dword counts. `qed_dbg_dump()` may free and replace these buffers; `qed_dbg_pf_exit()` frees any remaining buffers.
- `cdev->engine_for_debug`, `cdev->dbg_bin_dump`, `cdev->disable_ilt_dump`, and `cdev->print_dbg_data` control engine selection, binary/text output, ILT inclusion, and logging of formatted debug data.

The file does not persist state to disk. It reads persistent firmware/NVRAM data through MCP commands and may include NVRAM images in dumps. It also temporarily mutates hardware state while collecting diagnostics: PXP pretend settings, MCP halt/resume, MCP parity mask/unmask, Storm stalls, reset registers for RBC/debug blocks, debug bus client/line configuration, and parity status clears. Most paths attempt to restore key state, but some actions are inherently destructive for debug state, especially FIFO draining and parity clear reads.

GRC configuration has a persistent-parameter distinction within the driver. `s_grc_param_defs[].is_persistent` prevents some params, such as MCP trace meta size, from being reset by `qed_dbg_grc_set_params_default()`. Presets like `DBG_GRC_PARAM_EXCLUDE_ALL` and `DBG_GRC_PARAM_CRASH` mass-update non-persistent params.

## Dependencies And Integration Points

The file depends on Linux kernel facilities and QED internals:

- Kernel APIs: `vmalloc()`, `vzalloc()`, `vfree()`, `kcalloc()`, `kzalloc()`, `kfree()`, `mutex`, `crc32()`, `msleep()`, `cond_resched()`, endian helpers, bit macros, `snprintf()`, `sprintf()`, `strscpy()`, and module/debug logging primitives.
- QED hardware access: `qed_rd()`, `qed_wr()`, `qed_ptt_acquire()`, `qed_ptt_release()`, pretend helpers, DMAE GRC-to-host reads, device/chip predicates, `for_each_hwfn()`, and context-manager helpers for ILT/CDUT/CDUC sizing.
- MCP/NVRAM integration: `qed_mcp_nvm_rd_cmd()`, `qed_mcp_get_nvm_image_att()`, `qed_mcp_get_nvm_image()`, `qed_mcp_halt()`, `qed_mcp_resume()`, and `qed_mcp_mask_parities()`.
- Generated hardware/debug definitions from `qed_hsi.h`, `qed_dbg_hsi.h`, `qed_reg_addr.h`, and related headers provide block IDs, binary-buffer IDs, debug dump structures, mode tree encodings, attention layouts, register addresses, NVRAM image IDs, and firmware structures.
- Debugfs or upper-layer driver code calls the wrappers declared in `qed_debug.h`. The actual file operations are elsewhere, but this file owns the feature collection, sizing, and formatting behavior those operations expose.

## Risks And Edge Cases

- Hardware side effects are substantial. GRC dump can unreset blocks, mask/unmask parities, clear parity statuses, stall Storms, reset/configure the debug bus, halt/resume MCP, and use pretend settings. FIFO dumps drain hardware FIFOs. Tests and callers must treat dumps as diagnostic operations, not passive reads.
- Error cleanup is not uniformly centralized. For example, early returns from VFC or parity-mask-safe failures can occur after some state changes. MCP halt failure continues in some flows with a corruption warning, while MCP resume failure is only logged.
- Buffer-size calculations rely on the `dump=false` dry run matching `dump=true`. Dynamic hardware contents can change between size and data passes, especially FIFO depth, MCP trace data/meta availability, NVRAM images, or firmware assert ring positions.
- Several parsers use `sprintf()` into caller-provided buffers based on a prior size-calculation pass that writes into `s_temp_buf` via `qed_get_buf_ptr(NULL, offset)`. The size pass assumes formatted output is deterministic and below `MAX_MSG_LEN` per append target use.
- The MCP trace parser uses metadata-controlled format strings with up to three numeric parameters. Corrupt or incompatible metadata can cause parse failures and is guarded by signatures and bounds checks, but format-string trust remains tied to firmware/NVRAM authenticity.
- Some allocation error paths in MCP trace metadata setup update counts before returning but do not immediately free partially allocated allocations; the next explicit free or reload can recover, but callers should check status.
- The static debug, register, and memory loops depend on firmware-provided binary debug array integrity. There are recursion-depth guards for mode trees and range/status checks in selected places, but many offsets and sizes are trusted after basic array-presence checks.
- `qed_dbg_all_data()` stores GRC params from one `dev_data` pointer before iterating engines and restores through that same pointer before each GRC dump, so multi-engine parameter preservation should be reviewed carefully if per-engine GRC params diverge.
- ILT dump has special partial-dump semantics and byte/dword arithmetic around page descriptors and memory copies. Any consumer must honor `dump-size-full` and `dump-size-actual`, not just requested feature size.
- `qed_calc_regdump_header()` can only encode a 24-bit feature size and logs if truncation would occur; the all-data size cap mitigates but does not eliminate the importance of checking feature sizes.

## Test Signals

Useful validation signals include:

- Compile coverage for exported prototypes, generated HSI definitions, format strings, and bitfield macros.
- Unit-style parser tests with synthetic dumps for idle check, MCP trace, REG FIFO, IGU FIFO, protection override, firmware asserts, and attention parsing, including malformed section names, bad sizes, out-of-range enum values, and missing metadata.
- Dry-run versus dump consistency checks for every `*_get_dump_buf_size()`/`*_dump()` pair, including binary and formatted output modes.
- Hardware or simulator diagnostics for BB and K2 chips, single and CMT/multi-engine devices, multiple port modes, PF/VF split registers, blocks in reset, and unavailable MCP/NVRAM.
- Fault-injection signals: PTT acquisition failure, DMAE failure fallback, MCP halt/resume/mask failure, NVRAM image missing or non-aligned, corrupt debug binary arrays, VFC timeout, vmalloc/kzalloc failures, and oversized feature buffers.
- State-restoration checks after GRC/static debug collection: PXP pretend reset to original PF, MCP resumed, parity mask restored, debug block disabled, debug clients disabled, and Storm unstall behavior matching `DBG_GRC_PARAM_UNSTALL`.
- All-data bundle verification that headers decode correctly, feature sizes sum to `qed_dbg_all_data_size()`, ILT is omitted when the max dump cap is exceeded, and NVRAM image endian conversion is correct except for `QED_NVM_IMAGE_NVM_META`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_debug.h

## Purpose

`qed_debug.h` is the narrow public interface for the QED driver's debug feature collection layer. It declares the feature identifiers and callable APIs used by the rest of the driver or debugfs plumbing to size, collect, and manage debug dumps implemented in `qed_debug.c`.

## Important APIs And Types

The header defines `enum qed_dbg_features`, which indexes the driver-supported debug features:

- `DBG_FEATURE_GRC`
- `DBG_FEATURE_IDLE_CHK`
- `DBG_FEATURE_MCP_TRACE`
- `DBG_FEATURE_REG_FIFO`
- `DBG_FEATURE_IGU_FIFO`
- `DBG_FEATURE_PROTECTION_OVERRIDE`
- `DBG_FEATURE_FW_ASSERTS`
- `DBG_FEATURE_ILT`
- `DBG_FEATURE_NUM`

It forward-declares `struct qed_dev` and `struct qed_hwfn`, then declares three API families:

- Per-feature dump and size APIs: `qed_dbg_grc()`, `qed_dbg_idle_chk()`, `qed_dbg_reg_fifo()`, `qed_dbg_igu_fifo()`, `qed_dbg_protection_override()`, `qed_dbg_fw_asserts()`, `qed_dbg_ilt()`, `qed_dbg_mcp_trace()`, plus matching `*_size()` functions. Dump calls take a `struct qed_dev *`, caller-provided buffer, and `u32 *num_dumped_bytes`.
- Generic dispatch APIs: `qed_dbg_feature()` and `qed_dbg_feature_size()` accept `enum qed_dbg_features` and route to the same implementation used by the feature-specific wrappers.
- Device-level debug management: `qed_dbg_all_data()`, `qed_dbg_all_data_size()`, `qed_dbg_phy_size()`, `qed_get_debug_engine()`, `qed_set_debug_engine()`, `qed_dbg_pf_init()`, and `qed_dbg_pf_exit()`.

## Control Flow And Integration

The header does not implement logic; it exposes the contract consumed by other QED modules. Typical use is:

1. Call `qed_dbg_pf_init()` during PF/device initialization after firmware data is available so the implementation can install debug binary arrays and set the tool version.
2. Query a feature's size with a `*_size()` function or `qed_dbg_feature_size()`.
3. Allocate/provide a buffer of that size and call the corresponding dump function.
4. Optionally use `qed_dbg_all_data_size()` and `qed_dbg_all_data()` to collect a bundled debug package across engines and NVRAM images.
5. Call `qed_dbg_pf_exit()` during teardown to release any allocated debug buffers.

`qed_get_debug_engine()` and `qed_set_debug_engine()` expose engine selection for multi-hwfn devices; all per-feature collection functions operate against `cdev->engine_for_debug` inside the implementation.

## State And Persistence Behavior

The header itself holds no state. Its APIs operate on state stored in `struct qed_dev` and `struct qed_hwfn`, including selected debug engine, feature buffers, loaded firmware debug arrays, and implementation-specific debug info. `qed_dbg_pf_init()` and `qed_dbg_pf_exit()` are the lifecycle boundaries for that state.

The public contract makes callers responsible for buffer ownership at the API boundary: callers supply the destination buffer, and dump functions report `num_dumped_bytes`. Internal implementation buffers are managed by `qed_debug.c`.

## Dependencies

The declarations assume kernel integer types such as `u32` and `u8` are already available through the including compilation unit's kernel headers. The header intentionally avoids including large implementation-specific headers and only forward-declares QED device types.

Its main integration points are debugfs/diagnostic call sites in the QED driver and the implementation in `qed_debug.c`. The `enum qed_dbg_features` values must remain aligned with `qed_features_lookup[]` in the implementation.

## Risks And Test Signals

- Enum/order drift is the main interface risk. `DBG_FEATURE_*` order is used as an index into implementation lookup tables and `cdev->dbg_features[]`; adding or reordering values requires synchronized implementation changes.
- Size/dump API pairing is part of the contract. Callers should test that every `*_size()` result is sufficient for the matching dump function and that short buffers are rejected by the implementation.
- Lifecycle ordering matters. Calling dump APIs before `qed_dbg_pf_init()` or after `qed_dbg_pf_exit()` risks missing debug arrays or freed buffers in the implementation.
- Multi-engine callers should test `qed_set_debug_engine()` bounds and behavior indirectly through feature collection, since the setter accepts an `int` and does not expose validation in the header.
- Build tests should ensure all prototypes stay consistent with `qed_debug.c`, especially when adding features or changing `enum qed_dbg_features`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_debug.h -->
