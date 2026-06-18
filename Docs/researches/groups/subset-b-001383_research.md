# subset-b-001383 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser.c

Purpose: implements the legacy ATOMBIOS-backed `dc_bios` parser used when the ROM header is older than atomfirmware v2.2. It translates ATOM master/object data tables into Display Core object, GPIO, firmware, spread-spectrum, embedded-panel, layout, and command-table services exposed through `dc_vbios_funcs`.

Important APIs and functions: `bios_parser_create()` allocates `struct bios_parser`, calls `bios_parser_construct()`, and returns `&bp->base`. `bios_parser_destroy()` frees the local BIOS image, integrated info, and parser object. `bios_parser_construct()` validates `bp_init_data`, computes ROM size from byte 2 times 512, reads the ATOM ROM header and master data table, rejects newer ROM revisions, initializes object-info v1.1/v1.3 pointers, initializes command-table dispatch, builds `integrated_info`, and caches firmware info validity. The `vbios_funcs` table exports connector enumeration, source-object lookup, I2C/HPD/device-tag queries, spread-spectrum queries, embedded panel info, GPIO pin lookup, encoder caps, scratch helpers, device support checks, command wrappers, and board layout info.

Control flow: object queries first locate an `ATOM_OBJECT` via `get_bios_object()`, then walk record lists until `LAST_RECORD_TYPE` or a zero-sized record. Firmware and panel parsing dispatch on ATOM table major/minor revisions: firmware info supports v1.4, v2.1, and v2.2; LCD info supports v1.0-v1.2 through `get_embedded_panel_info_v1_2()` and v1.3 through `get_embedded_panel_info_v1_3()`. Spread-spectrum flow maps `as_signal_type` to legacy ASIC internal IDs, then chooses `SS_Info`, `ASIC_InternalSS_Info` v2.1, or v3.1 parsers. Command functions are thin guards around `bp->cmd_tbl` entries and return failure/unsupported if a command is missing.

State and persistence: the parser stores persistent ROM-derived pointers and offsets in `struct bios_parser`: `base.bios`, `base.bios_size`, `master_data_tbl`, `object_info_tbl`, `object_info_tbl_offset`, `cmd_tbl`, and `cmd_helper`. It also writes hardware-visible state through BIOS scratch registers indirectly via helper calls and, for DAC load detection, directly clears and re-reads `BIOS_SCRATCH_0`. `integrated_info` and `fw_info` are materialized during construction and live on `dc_bios`.

Dependencies and integration points: depends on `atom.h`, `dc_bios_types.h`, Display Core object definitions, logging, `command_table.c`, `command_table_helper.c`, `bios_parser_helper.c`, and shared `object_id_from_bios_object_id()`. It is selected by `bios_parser_interface.c` only after `firmware_parser_create()` fails, so it covers older ASIC/VBIOS layouts. The command wrappers integrate with ATOM command tables for transmitter, encoder, CRTC, PLL, DCE clock, power gating, and DAC detection operations.

Risks: most parsing uses ROM offsets and variable-sized records, so malformed sizes, offsets, or revision mismatches can cause `BADBIOSTABLE`, silent unsupported paths, or skipped data. `bios_get_image()` bounds checks are central; callers often assume returned records contain enough trailing array data after only minimal `struct_size()` checks. Several fields are converted from 10 kHz to kHz and percentage dividers vary between tables; regressions here can affect clock programming and bandwidth calculations. Scratch-register updates and DAC load detection have hardware side effects. Object-info v1.3 generic table handling is revision-sensitive.

Test signals: exercise both parser selection paths with old ROM headers, mock `bios_get_image()` tables for object-info v1.1/v1.3, validate connector/source/I2C/HPD/device-tag lookups, validate firmware v1.4/v2.1/v2.2 conversions, check SS entry counts for `SS_Info`, internal SS v2.1, and v3.1, and verify command-table wrappers return failure when function pointers are absent. Hardware or register-mock tests should cover BIOS scratch and DAC load-detection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser.h

Purpose: declares the public constructor for the legacy ATOMBIOS parser implementation.

Important API: `struct dc_bios *bios_parser_create(struct bp_init_data *init, enum dce_version dce_version);` returns a `dc_bios` interface on success or `NULL` when the ROM is unsupported or invalid. The implementation lives in `bios_parser.c`.

Control flow and integration: callers do not include this as the primary API; `bios_parser_interface.c` uses it as a fallback after the atomfirmware parser fails. The header intentionally exposes no internals; private layout is in `bios_parser_types_internal.h`.

State, dependencies, risks, and tests: state is owned by the returned `dc_bios` and destroyed through the function table, not this header. The main dependency risk is forward declarations being supplied by including translation units. Test signals are compile coverage and parser-selection tests that confirm fallback creation calls this constructor for legacy ROM revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser2.c

Purpose: implements the atomfirmware-era `dc_bios` parser, preferred for ROM headers v2.2 and newer. It parses atomfirmware master data tables and display object path tables, exposing Display Core services for connectors, GPIO/I2C/HPD, firmware clocks, spread spectrum, embedded panels, VRAM/UMC info, SOC bounding-box data, LTTPR flags, connector speed/capability records, board layout, command tables, and DC golden table values.

Important APIs and functions: `firmware_parser_create()` allocates the parser and calls `bios_parser2_construct()`. `firmware_parser_destroy()` frees allocations. `bios_parser2_construct()` validates ROM header revision, reads `atom_master_data_table_v2_1`, loads display object info v1.4 or v1.5, initializes `command_table2` and helper2 dispatch, builds integrated info, firmware info, VRAM info, and SOC BB info. `vbios_funcs` exports the parser operations, including atomfirmware-only hooks such as `pack_data_tables`, `get_atom_dc_golden_table`, `enable_lvtma_control`, `get_soc_bb_info`, `get_disp_connector_caps_info`, `get_lttpr_caps`, `get_lttpr_interop`, and `get_connector_speed_cap_info`.

Control flow: display object table minor revision drives many branches. v1.4 paths use `atom_display_object_path_v2`; v1.5 paths use `atom_display_object_path_v3` and separate helpers for HPD, connector caps, connector speeds, and bracket layout. Connector count ignores paths with zero encoder object IDs. I2C queries support generic object IDs by treating the object ID as an I2C ID; otherwise they walk display records and resolve GPIO pins through `gpio_pin_lut`. Firmware info dispatches among atom firmware v3.1, v3.2/v3.3, v3.4, and v3.5, combining firmware, DCE, SMU, and command-table SMU clock data. Spread spectrum dispatches on DCE info v4.1-v4.5 and sometimes uses integrated info or SMU info. Integrated info dispatches v1.11/v1.12/v2.1/v2.2/v2.3 and fills external display paths, retimer settings, eDP fields, and forced driver override fields.

State and persistence: persistent parser state mirrors the legacy parser but points to atomfirmware structures. Construction eagerly caches `base.integrated_info`, `base.fw_info`, `base.vram_info`, and `base.bb_info`. Runtime functions are mostly read-only ROM parsers, except scratch-register helpers and driver-config overrides that mutate integrated-info caps such as forced fixed voltage swing. Several functions use static `enum bp_result` locals, which persist across calls and can make stale status a review point if early return paths are changed.

Dependencies and integration points: depends on `atomfirmware.h`, `core_types.h`, `command_table2`, `command_table_helper2`, shared object-ID conversion, helper ROM access/scratch helpers, and Display Core config values such as `force_bios_enable_lttpr` and `force_bios_fixed_vs`. It is the first parser attempted by `dal_bios_parser_create()`. Command wrappers integrate with atomfirmware command tables for transmitter, DIG encoder, CRTC, clocks, power gating, and LVTMA control.

Risks: version branching is dense and often assumes table fields from a compatible minor version after only header checks. v1.5 object paths are not supported by every helper; encoder cap records are explicitly unavailable under some configs for v1.5. GPIO/I2C parsing in parser2 fills fewer GPIO fields than the legacy parser and contains TODOs. `bios_parser_get_src_obj()` returns OK even if no matching path overwrote the output. Forced config overrides change BIOS-derived data, which is intentional but should be visible in tests. Frequency fallbacks hard-code 27 MHz or 100 MHz when BIOS fields are zero. Any atomfirmware table expansion needs careful update of structure sizes and revision dispatch.

Test signals: cover parser selection on v2.2+ ROM headers, display object v1.4 and v1.5 connector enumeration, I2C/HPD records, device tags, connector caps and speed thresholds, firmware v3.1/v3.2/v3.4/v3.5 clock conversions, DCE info v4.1-v4.5 spread-spectrum and LTTPR capability flags, VRAM info v2.3/v2.4/v2.5/v3.0 and UMC v4.0 fallback, integrated info v1.11/v2.1/v2.2, and forced BIOS config mutations. Fuzzing malformed record sizes and missing data table offsets is useful because most failures should produce `BP_RESULT_BADBIOSTABLE`, `UNSUPPORTED`, or `NORECORD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser2.h

Purpose: declares the public constructor for the atomfirmware parser implementation.

Important API: `struct dc_bios *firmware_parser_create(struct bp_init_data *init, enum dce_version dce_version);` returns a `dc_bios` interface for atomfirmware ROMs or `NULL` when unsupported. The implementation lives in `bios_parser2.c`.

Control flow and integration: `bios_parser_interface.c` calls this constructor first, so this header is the preferred parser entry point for modern ASICs. Private parser state is intentionally hidden in `bios_parser_types_internal2.h`.

State, dependencies, risks, and tests: the header owns no state; lifecycle is through the returned function table. Risk is mainly ABI/compile drift if `bp_init_data` or `dce_version` declarations are not visible to includers. Test signals are compile coverage and parser-selection tests proving modern ROMs use this constructor before legacy fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.c

Purpose: centralizes conversion from packed BIOS graphics object IDs to Display Core `graphics_object_id` values. Both legacy and atomfirmware parsers depend on this so object identity is consistent across parser generations.

Important functions: `object_id_from_bios_object_id()` is the exported function. It calls private helpers to extract object type, enum ID, and type-specific ID from `OBJECT_TYPE_MASK`, `ENUM_ID_MASK`, and `OBJECT_ID_MASK`. Type-specific mapping covers GPU raw IDs, many internal/external encoder IDs, connector IDs including USB-C, and a small set of generic objects.

Control flow: invalid object type or enum ID returns a zeroed `graphics_object_id`. Unknown encoders assert and return `ENCODER_ID_UNKNOWN`; unknown connectors/generic objects return unknown IDs without asserting. Valid values are assembled with `dal_graphics_object_id_init()`.

State and persistence: stateless pure translation; no allocation or hardware access.

Dependencies and integration points: depends on `bios_parser_common.h`, `grph_object_ctrl_defs.h`, `ObjectID.h`, and Display Core graphics object enums. Used heavily by connector enumeration, source-object lookup, integrated-info external paths, board layout, and atomfirmware display path parsing.

Risks: any new ATOM object ID not added here can become `UNKNOWN`, which can hide connectors/encoders from the display stack. Encoder unknowns assert, so newly introduced encoder IDs are more disruptive than connector additions. Because both parsers share this function, mapping bugs have broad blast radius.

Test signals: table-driven tests for all known encoder, connector, generic, enum, and type encodings; negative tests for unknown type/enum/object IDs; integration tests showing parser connector IDs match expected Display Core IDs for representative VBIOS images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.h

Purpose: declares the shared BIOS object-ID conversion API and includes the type definitions needed by both parser implementations.

Important API: `struct graphics_object_id object_id_from_bios_object_id(uint32_t bios_object_id);`.

Control flow and integration: the header is included by `bios_parser.c`, `bios_parser2.c`, and the implementation file. It intentionally exposes only the conversion API, keeping all mapping tables private to `bios_parser_common.c`.

State, dependencies, risks, and tests: no state. Depends on `dm_services.h` and `ObjectID.h`. Risks are compile/API drift if graphics object definitions move. Test signals are compile coverage for both parser implementations and direct conversion tests through the exported function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.c

Purpose: provides shared low-level BIOS parser helpers: bounded ROM image access and BIOS scratch register helpers.

Important functions: `bios_get_image()` returns `bp->bios + offset` only when a BIOS image exists and `offset + size < bp->bios_size`; otherwise it returns `NULL`. `bios_is_accelerated_mode()` reads `BIOS_SCRATCH_6.S6_ACC_MODE`. `bios_set_scratch_acc_mode_change()` writes that field. `bios_set_scratch_critical_state()` writes `BIOS_SCRATCH_6.S6_CRITICAL_STATE`.

Control flow: parser files use the `GET_IMAGE(type, offset)` macro from the header, which delegates all pointer construction to `bios_get_image()`. Scratch helpers use `reg_helper.h` macros with `bios->ctx` and `bios->regs`.

State and persistence: ROM access is read-only and returns pointers into the parser-owned BIOS image. Scratch helpers persist state in hardware registers and are externally visible to VBIOS/driver coordination.

Dependencies and integration points: depends on `atom.h`, parser internal types, command-table headers, `reg_helper.h`, and `dc_bios` register definitions. Both parser implementations rely on this file for bounds checks and scratch state.

Risks: the bounds check uses strict `<`, so a request ending exactly at `bios_size` is rejected. Arithmetic overflow in `offset + size` would be dangerous if untrusted values reached it without wider validation. Many parser safety properties depend on every ROM pointer going through this helper. Register helpers require valid `bios->regs` and context.

Test signals: unit tests for valid, out-of-range, boundary, null BIOS, and oversized requests; register-mock tests for accelerated-mode and critical-state bit operations; parser fuzz tests that verify malformed offsets fail through `NULL` returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.h

Purpose: exposes shared helper functions and the `GET_IMAGE` macro used by both BIOS parser generations.

Important APIs: `bios_get_image()`, `bios_is_accelerated_mode()`, `bios_set_scratch_acc_mode_change()`, and `bios_set_scratch_critical_state()`. `GET_IMAGE(type, offset)` assumes a local variable named `bp` and expands to a typed pointer from `bios_get_image(&bp->base, offset, sizeof(type))`.

Control flow and integration: parser code relies on `GET_IMAGE` for concise table reads. Scratch functions are exposed through `dc_vbios_funcs` and parser wrappers.

State, dependencies, risks, and tests: the macro’s dependency on local variable name `bp` is convenient but fragile for refactors. The header forward-declares `struct bios_parser`, but the macro accesses `bp->base`, so callers must have the internal parser definition visible. Test signals are compile coverage across all parser files and direct helper tests from `bios_parser_helper.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_interface.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_interface.c

Purpose: provides the single parser factory/destructor API used by the rest of Display Core.

Important functions: `dal_bios_parser_create()` first calls `firmware_parser_create()` for atomfirmware ROMs, then falls back to `bios_parser_create()` for older ATOMBIOS ROMs. `dal_bios_parser_destroy()` delegates destruction through `bios->funcs->bios_parser_destroy`.

Control flow: parser selection is optimistic for the newer parser. A `NULL` return from parser2 is not fatal; it is the signal to try the legacy parser. Destruction assumes the caller passes a non-null pointer to a valid `dc_bios`.

State and persistence: no own state. It returns whichever concrete parser owns the allocated memory and function table.

Dependencies and integration points: depends on both parser headers, logging/services, and the public BIOS parser interface include. This file is the boundary that hides parser-generation differences from higher Display Core code.

Risks: no null checks in `dal_bios_parser_destroy()` before dereferencing `*dcb`, so callers must avoid destroying null/uninitialized parser handles. Parser selection relies on constructors cleanly returning `NULL` for unsupported ROMs without side effects.

Test signals: create tests with mock ROM headers for parser2 success, parser2 fail plus legacy success, and both fail. Destruction tests should verify the concrete parser destructor nulls the caller pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal.h

Purpose: defines private data structures for the legacy ATOMBIOS parser.

Important types: `struct atom_data_revision` stores major/minor table revisions. `struct object_info_table` stores revision plus a union of `ATOM_OBJECT_HEADER *v1_1` and `ATOM_OBJECT_HEADER_V3 *v1_3`. `enum spread_spectrum_id` defines legacy SS info table IDs. `struct bios_parser` embeds `struct dc_bios base`, object-info state, master data table pointer, helper pointers, command table dispatch, and `remap_device_tags`. `BP_FROM_DCB()` converts the public `dc_bios` pointer back to this private container.

Control flow and integration: included by `bios_parser.c`, `bios_parser_helper.c`, and command-table code that needs parser internals. The embedded `dc_bios` makes concrete parser memory compatible with the public interface and function-table callbacks.

State and persistence: this header defines all long-lived parser state for the legacy parser: ROM table pointers, offsets, command dispatch, and helper selection. The actual allocation/free path is in `bios_parser.c`.

Dependencies and risks: depends on `dc_bios_types.h` and `bios_parser_helper.h`; transitive ATOM types must be visible in implementation units. Because `struct bios_parser` has the same tag name as parser2’s private type, these internal headers must not be included together in one translation unit in a way that conflicts. Macro misuse on a non-legacy `dc_bios` would reinterpret memory incorrectly.

Test signals: compile coverage for every legacy parser and command-table translation unit, plus lifecycle tests that ensure `BP_FROM_DCB()` callbacks operate on objects allocated by `bios_parser_create()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal2.h

Purpose: defines private data structures for the atomfirmware parser.

Important types: `struct atom_data_revision` mirrors the legacy helper. `struct object_info_table` stores revision plus a union of `display_object_info_table_v1_4 *` and `display_object_info_table_v1_5 *`. `enum spread_spectrum_id` keeps the same legacy SS constants for compatibility. `struct bios_parser` embeds `struct dc_bios base`, atomfirmware display object table state, `atom_master_data_table_v2_1 *master_data_tbl`, helper pointers, command table dispatch, and `remap_device_tags`. `BP_FROM_DCB()` casts public callbacks back to the atomfirmware parser container.

Control flow and integration: included by `bios_parser2.c`, helper code, and command-table2 code. Its object-info union is the root of parser2’s repeated v1.4/v1.5 branch decisions.

State and persistence: defines the parser2 lifetime state allocated by `firmware_parser_create()` and freed by `firmware_parser_destroy()`. ROM pointers point into `dc_bios.base.bios`; derived info is stored separately on `base`.

Dependencies and risks: depends on `dc_bios_types.h`, `bios_parser_helper.h`, and atomfirmware type declarations from implementation units. Like the legacy internal header, it defines `struct bios_parser` and `struct atom_data_revision` names, so it is intended for separate parser2 translation units rather than shared inclusion with legacy internals. Misusing `BP_FROM_DCB()` with a legacy parser object would corrupt interpretation.

Test signals: compile coverage for parser2 and command-table2, constructor tests for display object table v1.4/v1.5, and callback tests proving parser2 function-table methods receive parser2-owned `dc_bios` objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_types_internal2.h -->
