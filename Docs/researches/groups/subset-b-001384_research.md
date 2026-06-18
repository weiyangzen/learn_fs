# Research Group subset-b-001384

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.c

## Purpose
This file implements the legacy ATOM BIOS command-table dispatcher for AMD display BIOS parser instances. `dal_bios_parser_init_cmd_tbl()` probes the command table parameter revisions exposed by the VBIOS and fills `bp->cmd_tbl` with revision-specific handlers for encoder, transmitter, clock, CRTC, DAC, external encoder, power-gating, and DCE clock commands.

## Important APIs, Types, And Functions
- `dal_bios_parser_init_cmd_tbl()` is the external initializer consumed by the BIOS parser.
- `EXEC_BIOS_CMD_TABLE`, `BIOS_CMD_TABLE_REVISION`, and `BIOS_CMD_TABLE_PARA_REVISION` wrap `amdgpu_atom_execute_table()` and `amdgpu_atom_parse_cmd_header()` against `adev->mode_info.atom_context`.
- DIG encoder handlers cover legacy split tables (`DIG1EncoderControl`, `DIG2EncoderControl`) and `DIGxEncoderControl` parameter revisions 3, 4, and 5.
- Transmitter handlers cover `UNIPHYTransmitterControl` command revisions 2, 3, 4, 1.5, and 1.6.
- Pixel clock handlers cover `SetPixelClock` revisions 3, 5, 6, and 7; `program_clock_v5/v6()` reuse that VBIOS table to program display/engine clocks.
- Spread-spectrum, display PLL adjustment, CRTC source/timing, CRTC enable/memory request, DAC encoder/output/load detection, external encoder control, display power gating, and `SetDCEClock` each have revision-gated handlers.

## Control Flow
Initialization probes every relevant ATOM command table and assigns either a compatible handler or `NULL`. Runtime callers go through the function pointers in `struct cmd_tbl`, so unsupported VBIOS revisions naturally become unavailable operations. Each handler builds a packed ATOM parameter structure, translates DC enums through `bp->cmd_helper`, converts units and endian fields, calls the VBIOS table, and returns a `bp_result`.

Key conversion flow includes KHz to 10 KHz or 100 Hz units, HDMI deep-color pixel/symbol clock inflation, DP lane/link-rate selection, controller and PLL ID translation, and interlace polarity/timing bit packing. Some handlers also consume VBIOS outputs, such as adjusted display PLL frequency and `SetDCEClock` returning the actual programmed frequency.

## State And Persistence
The file persists no standalone data. It mutates `bp->cmd_tbl` during initialization and updates caller-provided parameter objects when VBIOS returns adjusted clock values, divisors, or DFS bypass clocks. Hardware and firmware state changes are performed through ATOM BIOS table execution.

## Dependencies And Integration Points
Dependencies include `amdgpu_atom_execute_table()`, ATOMBIOS structures/macros from `atom.h`, BIOS parser public/internal types, `bios_parser_helper`, `dm_services`, and the selected `command_table_helper`. It integrates with upper display core code through `dc_bios->funcs`, which delegates into the initialized command table operations.

## Risks
Revision handling is brittle: unrecognized command table revisions silently disable function pointers or fall back to older flows. Several paths assume helper function pointers are populated for the active DCE family. Unit conversions and 16-bit fields can truncate unexpected clocks. Some invalid inputs only trigger debugger assertions and continue with defaults. Legacy DAC/CRT and external-encoder paths have narrow enum support and return `BADINPUT` for unsupported combinations.

## Test Signals
Useful validation signals are successful display light-up across DCE generations, DP/HDMI/DVI clock accuracy including deep color, spread-spectrum enable/disable behavior, DP link training on different lane counts, suspend/resume with CRTC memory requests, DAC load detection on SI/CI hardware, and kernel logs from `dm_output_to_console`, `dm_error`, assertions, or ATOM table execution failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.h

## Purpose
This header declares the legacy BIOS command-table dispatch structure and initializer for the display BIOS parser.

## Important APIs, Types, And Functions
- `struct cmd_tbl` is a table of function pointers for all legacy ATOM command operations supported by the parser.
- `dal_bios_parser_init_cmd_tbl(struct bios_parser *bp)` initializes those function pointers based on VBIOS command table revisions.
- Forward declarations cover `struct bios_parser` and `struct bp_encoder_control`; the remaining parameter types are expected from included BIOS parser type headers before use.

## Control Flow
The header does not implement control flow. It defines the ABI that command table implementation files populate and BIOS parser callers invoke.

## State And Persistence
Instances of `struct cmd_tbl` are embedded in `struct bios_parser`. The function pointers persist for the parser lifetime and encode the active VBIOS capability set.

## Dependencies And Integration Points
It is consumed by `command_table.c` and parser code that invokes BIOS command functions. The function pointer signatures bind this module to display core BIOS types such as `bp_pixel_clock_parameters`, `bp_transmitter_control`, and `controller_id`.

## Risks
Because the dispatch table contains nullable function pointers, callers must check availability or rely on parser wrappers to do so. Signature changes are ABI-sensitive across all parser implementations.

## Test Signals
Compile coverage catches signature drift. Runtime coverage should verify that every initialized parser path checks or handles absent function pointers for unsupported VBIOS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table2.c

## Purpose
This file implements the newer ATOM firmware v2 command-table dispatcher. It parallels the legacy command-table code but uses `atom_master_list_of_command_functions_v2_1` indices and can route selected VBIOS operations through DMUB commands when `dc->debug.dmub_command_table` is enabled.

## Important APIs, Types, And Functions
- `dal_firmware_parser_init_cmd_tbl()` initializes the firmware-parser command table.
- Command execution macros use lowercase ATOM firmware table names such as `digxencodercontrol`, `dig1transmittercontrol`, `setpixelclock`, and `setdceclock`.
- `encoder_control_digx_v1_5()`, `transmitter_control_v1_6()`, `transmitter_control_v1_7()`, `set_pixel_clock_v7()`, `set_crtc_using_dtd_timing_v3()`, `enable_crtc_v1()`, `enable_disp_power_gating_v2_1()`, `set_dce_clock_v2_1()`, `get_smu_clock_info_v3_1()`, and `enable_lvtma_control()` form the primary operation set.
- DMUB helpers build `union dmub_rb_cmd` payloads for DIG encoder, transmitter, pixel clock, display power gating, and LVTMA control.

## Control Flow
Initialization probes table revisions and assigns revision-specific handlers, with fallback handlers for DMUB-capable systems where a VBIOS table revision is absent or unsupported. Runtime handlers build atomfirmware parameter structures and either send a DMUB VBIOS command or execute the VBIOS command table.

The v1.7 transmitter path also computes HPO instance IDs, finds the `dc_link` by PHY ID, prepares ACPI PHY transition interlock parameters when the link advertises a transition bitmask, sends pre/post interlock calls around the DMUB transmitter command, and propagates link workarounds such as `skip_phy_ssc_reduction`.

## State And Persistence
State changes are in firmware/hardware. The file mutates `bp->cmd_tbl` and updates caller parameters such as returned DCE clock frequency. It reads live DC state, links, debug flags, and DMUB service pointers. `get_smu_clock_info_v3_1()` returns VBIOS-provided clock values without storing them.

## Dependencies And Integration Points
Dependencies include `atomfirmware.h`, `ObjectID.h`, `amdgpu_atom_*`, `dc_dmub_srv`, `dc`, DMUB command definitions, ACPI transition interlock support, and `command_table_helper2`. It integrates with DC link state, HPO engines, SMU clock queries, panel/LVTMA power sequencing, and the firmware parser path selected for newer ASICs/DCN generations.

## Risks
Fallback handlers succeed only when DMUB command-table routing is present; otherwise operations fail. `get_link_by_phy_id()` assumes `p_dc->links[link_id]` and `link_enc` are valid. Some operations remain stubs or TODOs, notably external encoder control returning OK without programming. DMUB and VBIOS paths must remain parameter-compatible, especially for v1.7 transmitter payloads and ACPI interlock sequencing.

## Test Signals
Signals include DMUB command completion, DP/HDMI light-up on DCN systems, HPO and PHY transition interlock behavior, panel power sequencing via LVTMA, SMU clock-info reads, `DC_LOG_BIOS` clock traces, and absence of fallback failures when command-table revisions differ by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table2.h

## Purpose
This header declares the firmware-parser variant of the BIOS command dispatch table.

## Important APIs, Types, And Functions
- `struct cmd_tbl` defines function pointers for firmware command operations. Compared with the legacy header, it omits select-CRTC-source, DAC load detection, and some legacy DAC action signatures, and adds `get_smu_clock_info` and `enable_lvtma_control`.
- `dal_firmware_parser_init_cmd_tbl(struct bios_parser *bp)` initializes the table.

## Control Flow
The header defines the callable surface used after `command_table2.c` probes firmware command revisions and assigns handlers.

## State And Persistence
The populated function table persists within `struct bios_parser` for the parser lifetime.

## Dependencies And Integration Points
The header is tied to firmware parser internals and DC BIOS parameter structures. The added SMU and LVTMA hooks connect display clock management and embedded-panel power sequencing to firmware/DMUB paths.

## Risks
This header reuses the name `struct cmd_tbl`, so it must not be included in a translation unit expecting the legacy layout at the same time. Nullable function pointers and variant-specific fields require parser wrappers to use the correct parser type.

## Test Signals
Build coverage should catch mismatched parser layout use. Runtime coverage should exercise firmware-parser command availability on DCN-era ASICs and verify that SMU/LVTMA pointers are initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.c

## Purpose
This file contains shared legacy command-table helper routines that translate Display Core enums and objects into ATOMBIOS encodings, and selects the DCE-family-specific helper table.

## Important APIs, Types, And Functions
- `dal_bios_parser_init_cmd_tbl_helper()` selects DCE60, DCE80, DCE110, or DCE112 helper tables by `enum dce_version`.
- `dal_cmd_table_helper_controller_id_to_atom()`, `*_transmitter_bp_to_atom()`, `*_encoder_mode_bp_to_atom()`, `*_clock_source_id_to_ref_clk_src()`, and `*_encoder_id_to_atom()` translate common IDs.
- `dal_cmd_table_helper_assign_control_parameter()` packs legacy `DIG_ENCODER_CONTROL_PARAMETERS_V2`.
- `phy_id_to_atom()`, `clock_source_id_to_atom_phy_clk_src_id()`, and `engine_bp_to_atom()` support newer transmitter and CRTC-source command parameters.

## Control Flow
Callers initialize `bp->cmd_helper` once by DCE version. Command-table handlers then call the function pointers or these exported helpers while building ATOM parameter blocks. Translation functions usually return `bool` for mappings with out parameters, or a default ATOM value with a debugger break on invalid inputs.

## State And Persistence
The file stores no mutable state. It assigns a pointer to a static helper table owned by DCE-family helper files. Parameter-packing functions mutate caller-provided ATOM structures.

## Dependencies And Integration Points
It depends on `atom.h`, display BIOS parser types, DCE-family helper headers, and `command_table_helper_struct.h`. It is central to `command_table.c` and DCE helper variants.

## Risks
Invalid mappings may return a default value after `BREAK_TO_DEBUGGER()`, allowing firmware programming with an unintended ID if callers do not handle failure. The DCE version switch must be kept current for newly supported ASIC versions. Conditional SI support under `CONFIG_DRM_AMD_DC_SI` changes coverage for DCE6.

## Test Signals
Compile-time signals include all helper table function pointers matching `struct command_table_helper`. Runtime signals are correct controller/encoder/transmitter mapping in VBIOS command traces, no debugger breaks on supported IDs, and successful light-up across DCE versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.h

## Purpose
This header exposes the legacy command-table helper selection and shared translation routines.

## Important APIs, Types, And Functions
It declares `dal_bios_parser_init_cmd_tbl_helper()`, controller/transmitter/encoder/clock-source mapping helpers, legacy DIG encoder parameter packing, PHY ID mapping, PHY clock source mapping, and engine-to-ATOM encoder mapping.

## Control Flow
No executable control flow is present. The included DCE helper headers make the family-specific table providers visible to the implementation.

## State And Persistence
The header defines no state. It exposes functions that either return static helper tables or fill caller-provided outputs.

## Dependencies And Integration Points
It includes DCE60 conditionally, DCE80, DCE110, DCE112, and `command_table_helper_struct.h`. It is included by legacy command-table code and DCE-specific helper implementations.

## Risks
Because the interface exposes raw ATOM conversion helpers, callers must know which helper fields are valid for their DCE generation. The header shape also ties SI/DCE6 availability to build configuration.

## Test Signals
Build coverage for all enabled DCE configs catches missing helper providers. Runtime light-up on DCE6, DCE8, DCE11, and DCE11.2 validates the dispatch table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.c

## Purpose
This file provides the atomfirmware-era helper selection and shared enum translation functions for `command_table2.c`.

## Important APIs, Types, And Functions
- `dal_bios_parser_init_cmd_tbl_helper2()` selects helper tables for DCE and DCN versions, using the DCE112 helper2 table for DCE11.2+, DCE12, and all listed DCN versions.
- `dal_cmd_table_helper_controller_id_to_atom2()`, `*_transmitter_bp_to_atom2()`, `*_encoder_mode_bp_to_atom2()`, `*_clock_source_id_to_ref_clk_src2()`, and `*_encoder_id_to_atom2()` provide firmware-parser mappings.

## Control Flow
The DCE/DCN version switch assigns a static helper table pointer and returns whether the version was explicitly recognized. Translation helpers use switch statements and return failure for unsupported IDs.

## State And Persistence
No mutable state is stored. The selected helper table pointer becomes parser state in the caller.

## Dependencies And Integration Points
It depends on `ObjectID.h`, `atomfirmware.h`, BIOS parser types, and DCE helper table providers. It integrates directly with `command_table2.c` DMUB/VBIOS parameter construction.

## Risks
The default case assigns a DCE112 helper2 table but returns `false`, which can be surprising if callers use the pointer after a failed init result. Some legacy mappings are TODO-disabled, such as underlay controller and DCPLL ref-clock source. Unsupported IDs trigger debugger breaks and can return default object IDs.

## Test Signals
Runtime coverage should verify helper initialization return values for every DCN version listed in the switch. Command-table2 operations should be checked for correct controller, encoder, and clock-source encoding on DCN hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.h

## Purpose
This header exposes firmware-parser helper selection and shared atomfirmware translation helpers.

## Important APIs, Types, And Functions
It declares `dal_bios_parser_init_cmd_tbl_helper2()` plus controller, encoder mode, clock-source, transmitter, and encoder object ID mapping helpers with a `2` suffix.

## Control Flow
No executable control flow is present. Header inclusion selects the helper provider headers needed by the implementation.

## State And Persistence
The header defines no persistent state. Implementations return static helper table pointers and fill caller-provided outputs.

## Dependencies And Integration Points
It conditionally includes DCE60 plus DCE80, DCE110, DCE112 helper2, and the shared helper struct. It is the helper interface for `command_table2.c`.

## Risks
The interface is similar but not identical to `command_table_helper.h`; mixing legacy and firmware helper functions can produce incorrect mappings. Not every legacy helper is exported in the v2 interface.

## Test Signals
Build coverage should ensure all declared functions are linked in firmware parser builds. Runtime signals are successful DCN firmware command execution using mapped controller, PLL, transmitter, and encoder IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper_struct.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper_struct.h

## Purpose
This header defines `struct command_table_helper`, the function-pointer vtable used by both legacy and firmware command-table implementations to convert DC abstractions into ATOM/firmware encodings.

## Important APIs, Types, And Functions
The struct contains callbacks for controller IDs, encoder actions/modes/IDs, engine IDs, control parameter assignment, PLL/ref-clock IDs, transmitter IDs, PHY IDs, signal modes, HPD selection, DIG encoder selection, power-gating actions, DCE clock types, and transmitter color depth.

## Control Flow
The header defines a dispatch contract only. DCE-family helper source files instantiate static const tables that fill appropriate callbacks.

## State And Persistence
Static instances of this struct are selected during BIOS parser initialization and stored through `bp->cmd_helper`. The pointed-to table is immutable.

## Dependencies And Integration Points
It includes DCE helper headers and forward-declares the legacy DIG encoder parameter type. It is shared by command-table helpers and command-table implementations.

## Risks
Several callbacks may be `NULL` for DCE generations that do not need them. Command-table code must only call callbacks guaranteed by the active helper table and command revision. Any struct layout change affects both legacy and firmware helper providers.

## Test Signals
Compile coverage catches missing members in designated initializers. Runtime validation should exercise command paths that use every non-NULL callback for each supported DCE/DCN family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.c

## Purpose
This file defines the DCE10/DCE11 command-table helper vtable, mapping DC signal, HPD, PLL, action, and power-gating enums into ATOM values appropriate for DCE110-era VBIOS tables.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce110_get_table()` returns the static helper table.
- Static mappings include `signal_type_to_atom_dig_mode()`, `hpd_sel_to_atom()`, `dig_encoder_sel_to_atom()`, `clock_source_id_to_atom()`, `encoder_action_to_atom()`, and `disp_power_gating_action_to_atom()`.

## Control Flow
The mapping functions are switch-based and are referenced through `command_table_helper_funcs`. For DCE110 and later, `dig_encoder_sel_to_atom()` always returns zero because the link encoder programs DIG front-end selection outside these VBIOS commands.

## State And Persistence
The helper table is immutable static data. No runtime state is stored.

## Dependencies And Integration Points
It depends on `atom.h`, BIOS parser types, and the shared legacy helper functions from `command_table_helper.h`. It is selected by `dal_bios_parser_init_cmd_tbl_helper()` for DCE10 and DCE11.0.

## Risks
The helper table leaves some callbacks `NULL`, including legacy control parameter assignment and ref-clock source translation. Command paths requiring those callbacks must not be selected for DCE110. Defaults for unknown signal types fall back to DVI-style modes.

## Test Signals
Useful signals are successful UNIPHY transmitter programming on DCE110, correct HPD routing, no calls into NULL callbacks, and expected command parameters for DP MST, HDMI, DVI, and eDP links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.h

## Purpose
This header declares the DCE110 command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce110_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
The header has no runtime flow; it exposes the provider used by shared helper selection.

## State And Persistence
No state is defined. The provider returns immutable static data from the C file.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by helper selection and helper struct headers.

## Risks
Only the provider is declared; consumers must include the shared helper struct for member semantics. Header guard naming is DCE110-specific and should remain unique.

## Test Signals
Compile/link success verifies the provider is present when DCE110 helper selection is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.c

## Purpose
This file defines the firmware-parser helper vtable used for DCE11.2, DCE12, and DCN versions in `command_table_helper2.c`.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table2()` returns the static helper table.
- Static mappings cover signal type to DIG mode, HPD selection, DIG encoder selection, combo PHY/display PLL IDs, encoder actions, display power-gating actions, DCE clock types, and transmitter color-depth ratios.
- The table uses `dal_cmd_table_helper_controller_id_to_atom2()`, `dal_cmd_table_helper_encoder_id_to_atom2()`, and `dal_cmd_table_helper_encoder_mode_bp_to_atom2()`.

## Control Flow
All mappings are switch-based. Combo PHY PLL IDs map to `ATOM_COMBOPHY_PLL*`, DFS maps to `ATOM_GCK_DFS`, and VCE/DP DTO map to `ATOM_DP_DTO`. DIG encoder selection returns zero because front-end selection is programmed elsewhere.

## State And Persistence
The file has no mutable state; it exposes an immutable helper table.

## Dependencies And Integration Points
It depends on `atom.h`, BIOS parser types, both legacy and firmware helper headers, and is selected by the firmware helper initializer for DCE11.2+ and DCN.

## Risks
Unsupported clock source IDs return failure, which can cause command-table operations to return `BADINPUT`. The helper lacks `assign_control_parameter` and ref-clock callbacks, so legacy paths must not use this table. Unknown color depths assert and return zero.

## Test Signals
Test by executing firmware command-table operations that require combo PHY PLLs, DP DTO, HDMI deep-color ratios, and DP MST signal modes on DCN hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.h

## Purpose
This header declares the DCE112 helper provider for the firmware-parser helper table.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table2()` returns a `const struct command_table_helper *`.

## Control Flow
No runtime flow is defined in the header.

## State And Persistence
No state is defined. The implementation returns an immutable static helper table.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by `command_table_helper2.h`.

## Risks
The closing comment references DCE110, which is cosmetic but can confuse maintainers. Consumers need the shared helper struct to know which callbacks are valid.

## Test Signals
Build/link coverage ensures the provider is present for firmware parser builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.c

## Purpose
This file defines the legacy helper vtable for DCE11.2 and DCE11.22, adding combo PHY PLL, DCE clock type, and transmitter color-depth mapping needed by later ATOM command table revisions.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table()` returns the helper table.
- Static functions map signal modes, HPD selection, clock sources, encoder actions, display power gating, DCE clock type, and transmitter color depth.
- The table reuses legacy shared helpers for controller, engine, PHY, encoder ID, and encoder mode conversions.

## Control Flow
The helper uses V6 ATOM transmitter modes and combo PHY clock source constants. It maps `ENCODER_CONTROL_SETUP` to `ATOM_ENCODER_CMD_STREAM_SETUP`, unlike older helpers that use `ATOM_ENCODER_CMD_SETUP`.

## State And Persistence
The helper table is immutable static data and stores no mutable state.

## Dependencies And Integration Points
It depends on `atom.h`, BIOS parser types, and `command_table_helper.h`. It is selected by the legacy helper initializer for DCE11.2-family ASICs.

## Risks
Unsupported clock source IDs cause helper failure and upstream command failure. Unknown DCE clock types assert but still return `true`, which may hide an invalid output if not examined. Several legacy callbacks are intentionally `NULL`.

## Test Signals
Signals include successful `SetPixelClock` v7, `SetDCEClock`, and UNIPHY transmitter programming on DCE11.2, plus correct deep-color ratios for HDMI pixel-clock programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.h

## Purpose
This header declares the legacy DCE112 command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
No executable flow is present.

## State And Persistence
No state is defined; the implementation returns a static immutable table.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by shared helper headers and selection code.

## Risks
The closing comment references DCE110, which is minor documentation drift. Consumers must know the table is for the legacy helper path, not helper2.

## Test Signals
Compile/link coverage verifies availability for DCE112 legacy parser builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.c

## Purpose
This file provides the command-table helper vtable for SI/DCE6 display hardware.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce60_get_table()` returns the DCE60 helper table.
- Static mappings translate encoder actions, clock sources, signal DIG modes, HPD selection, DIG encoder selection, and display power-gating actions.
- The table uses legacy shared helpers for controller, engine, ref-clock, transmitter, encoder ID, encoder mode, PHY, and DIG control parameter packing.

## Control Flow
The mapping logic mirrors DCE80-era V5 ATOM transmitter fields. `dig_encoder_sel_to_atom()` maps DIGA through DIGG to explicit `ATOM_TRANMSITTER_V5__DIG*` selections, unlike DCE110+ where this returns zero.

## State And Persistence
The helper table is immutable and has no mutable runtime state.

## Dependencies And Integration Points
It depends on `atom.h`, graph object headers, BIOS parser types, and the shared legacy helper. It is selected only when `CONFIG_DRM_AMD_DC_SI` enables SI support.

## Risks
Unsupported values often break to debugger and then return default ATOM selections, especially DVI/DIGA defaults. Because SI support is conditional, build/test coverage may be absent in some kernels.

## Test Signals
SI display bring-up, DP/eDP/DVI/HDMI mode programming, HPD routing, DIG FE selection, and VBIOS command traces are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.h

## Purpose
This header declares the DCE60/SI command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce60_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
No executable flow is defined.

## State And Persistence
No state is defined; the implementation returns static immutable data.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included conditionally by the shared helper interface when SI support is configured.

## Risks
Consumers must guard use with `CONFIG_DRM_AMD_DC_SI` availability.

## Test Signals
Build coverage with SI enabled verifies provider linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.c

## Purpose
This file provides the helper vtable for DCE8 display hardware, using V5 ATOM transmitter encodings.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce80_get_table()` returns the static helper table.
- Static mapping functions cover encoder action, clock source, signal mode, HPD selection, DIG encoder selection, and display power gating.
- It reuses shared helpers for controller, engine, DIG control packing, ref-clock, transmitter, encoder ID, encoder mode, PHY ID, and PHY clock source mapping.

## Control Flow
The control flow is switch-based enum translation. DIG encoder selection explicitly maps DIGA-DIGG to V5 transmitter FE selection constants.

## State And Persistence
No mutable state exists. The returned helper table is static const data.

## Dependencies And Integration Points
It depends on `atom.h`, graph object headers, BIOS parser types, and `command_table_helper.h`. It is selected for DCE8.0, DCE8.1, and DCE8.3.

## Risks
DCE60 and DCE80 helper code is nearly identical, so fixes can diverge if applied to one copy only. Unsupported inputs fall back to defaults after debugger breaks.

## Test Signals
Validate on DCE8 ASICs with DP, HDMI, DVI, LVDS/eDP, and MST paths, checking VBIOS command parameters and display light-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.h

## Purpose
This header declares the DCE80 command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce80_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
No runtime flow is defined.

## State And Persistence
No state is defined; the provider returns immutable static helper data.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by shared helper interfaces and selection code.

## Risks
The header is small; risk is mainly provider linkage or accidental mismatch with the shared helper struct.

## Test Signals
Build/link coverage and DCE8 helper selection at runtime validate this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/Makefile

## Purpose
This makefile wires the Display Core clock-manager subcomponent into the AMD display build.

## Important APIs, Types, And Functions
- `CLK_MGR` contributes the common `clk_mgr.o`.
- DCE object groups add DCE100, DCE110, DCE112, and DCE120 managers unconditionally.
- Under `CONFIG_DRM_AMD_DC_FP`, DCN clock manager and SMU support objects from DCN10 through DCN42 are added.
- `AMD_DISPLAY_FILES += ...` is the integration output for the parent build.

## Control Flow
Build flow is declarative: object lists are prefixed with `$(AMDDALPATH)/dc/clk_mgr/` and appended to the global AMD display object list. Floating-point DCN managers are gated by `CONFIG_DRM_AMD_DC_FP`.

## State And Persistence
No runtime state. Build state is the object list produced for the kernel build.

## Dependencies And Integration Points
The file integrates with the AMDGPU display build system via `AMDDALPATH`, `AMD_DISPLAY_FILES`, and kernel config symbols. It must stay aligned with constructors referenced by `clk_mgr.c`.

## Risks
Missing an object here yields unresolved symbols for constructors or destroy functions. Adding constructor cases in `clk_mgr.c` without matching object inclusion breaks builds, especially under config-specific paths.

## Test Signals
Kernel build coverage across configs with and without `CONFIG_DRM_AMD_DC_FP` is the key signal. Linker failures catch stale object lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/clk_mgr.c

## Purpose
This file provides common clock-manager helpers, power-state transitions, the ASIC-family clock-manager factory, and destruction logic.

## Important APIs, Types, And Functions
- `clk_mgr_helper_get_active_display_cnt()` counts non-phantom active displays and streams with planes or switch-in-progress.
- `clk_mgr_helper_get_active_plane_cnt()` sums stream plane counts.
- `clk_mgr_exit_optimized_pwr_state()` and `clk_mgr_optimize_pwr_state()` coordinate HW sequencer optimized power states with PSR/Replay allow-active settings on eDP links.
- `dc_clk_mgr_create()` allocates and constructs the correct clock manager for SI/CI/KV/CZ/VI/AI and many DCN families.
- `dc_destroy_clk_mgr()` invokes family-specific destroy functions for DCN managers and frees the allocation.

## Control Flow
The factory switches on `ctx->asic_id.chip_family`, then often on hardware revision or `ctx->dce_version`. It allocates a structure sized for the selected manager, calls the generation-specific constructor, and returns the embedded base pointer. The destroy path switches on the same family/revision categories for managers that need explicit teardown before `kfree()`.

## State And Persistence
The file creates persistent `struct clk_mgr` or generation-specific derived objects for the lifetime of the DC instance. Power-state helpers temporarily cache PSR allow-active state in `clk_mgr->psr_allow_active_cache` and manipulate eDP PSR/Replay permissions.

## Dependencies And Integration Points
It depends on ASIC ID macros, DCCG, `clk_mgr_internal`, DC state helpers, link service, and every generation-specific clock-manager constructor header. It integrates clock management into DC initialization and teardown.

## Risks
The factory must stay synchronized with supported ASIC revisions, constructor object sizes, and Makefile object lists. Some branches allocate `struct clk_mgr_internal`, others allocate derived DCN structs, making destroy casts sensitive. The active display count deliberately skips SubVP phantom streams, so changes to SubVP classification affect power management.

## Test Signals
Boot/display initialization on every supported ASIC family, correct constructor selection in logs/debug traces, successful suspend/resume, PSR/Replay behavior around optimized power states, and leak/error checks on destroy are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.c

## Purpose
This file implements the shared DCE6/DCE8/DCE10-era clock-manager base behavior: DP reference clock calculation, spread-spectrum adjustment, clock-state selection, display clock programming, VBIOS integrated-info parsing, and PPLIB display-requirement updates.

## Important APIs, Types, And Functions
- `dentist_get_divider_from_did()` converts DENTIST DID register encodings to divider values.
- `dce_adjust_dp_ref_freq_for_ss()` applies downspread adjustment to DP reference clocks.
- `dce_get_dp_ref_freq_khz()`, `dce12_get_dp_ref_freq_khz()`, and `dce60_get_dp_ref_freq_khz()` calculate DP reference clock by generation.
- `dce_get_max_pixel_clock_for_all_paths()` scans active pipe contexts for max pixel/symbol clock.
- `dce_get_required_clocks_state()` selects the minimum PP clock state satisfying display and pixel-clock needs.
- `dce_set_clock()` programs display clock through `program_display_engine_pll`.
- `dce_clock_read_integrated_info()` and `dce_clock_read_ss_info()` load VBIOS clock and spread-spectrum information.
- `dce_clk_mgr_construct()` initializes the common manager fields and function table.

## Control Flow
Construction chooses default max clock tables for DCE6 or DCE8+, attaches register definitions, loads static PP clock info, reads VBIOS integrated info, and records spread-spectrum settings. Updates compute required PP power level, request PPLIB changes when needed, program display clock if `should_set_clock()` allows, and apply display requirements.

## State And Persistence
Persistent state lives in `struct clk_mgr_internal`: max clock tables, current minimum PP state, dentist VCO, DFS bypass flags and cached clock, DPREF spread-spectrum percentage/divider, and base `clks`. Runtime calls update `base.clks.dispclk_khz` and may update DMCU PSR wait-loop timing.

## Dependencies And Integration Points
Dependencies include register helpers for DCE8 common registers, DC fixed-point math, PPLIB/PP SMU functions, VBIOS integrated/spread-spectrum info, DMCU, bandwidth context, and DCE110 display-config helpers. It is the base constructor and shared utility layer for DCE110, DCE112, and DCE120 managers.

## Risks
Incorrect spread-spectrum adjustment affects DP audio/timing. Clock-state selection depends on VBIOS and PP clock tables, with fallback defaults that may not match every board. `dce_set_clock()` has special DCE6 PLL handling and DFS bypass behavior that can regress resume or PSR timing. Display requirement comparison uses whole-struct `memcmp`, so padding or uninitialized fields would be risky.

## Test Signals
Signals include DP ref clock readback, spread-spectrum link stability, PPLIB clock-state requests, display clock programming across safe-to-lower transitions, PSR wait-loop behavior, and display bring-up on DCE6/DCE8/DCE10 ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.h

## Purpose
This header exposes shared DCE clock-manager utilities and the DCE base constructor.

## Important APIs, Types, And Functions
It declares DP reference clock helpers, clock-state calculation, max pixel-clock scan, `dce_clk_mgr_construct()`, spread-spectrum info loading, DCE12 DP ref helper, `dce_set_clock()`, `dce_clk_mgr_destroy()`, and dentist divider decoding.

## Control Flow
The header provides declarations only. Implementations are used by DCE100 and later DCE clock-manager files.

## State And Persistence
No state is defined here; declarations operate on `struct clk_mgr`, `struct clk_mgr_internal`, and `struct dc_state`.

## Dependencies And Integration Points
It includes `dc.h` and is included by DCE110, DCE112, and DCE120 manager implementations. It is the shared clock-manager API for DCE generations.

## Risks
The declared `dce_clk_mgr_destroy(struct clk_mgr **clk_mgr)` is not implemented in the read C file and may be stale. Signature changes affect multiple generation-specific managers.

## Test Signals
Compile/link coverage detects stale declarations. Runtime coverage should exercise shared helpers through every DCE manager that includes this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.c

## Purpose
This file specializes the common DCE clock manager for DCE110/CZ-era hardware with DCE11 register definitions, clock-state limits, display-configuration reporting, and PPLIB requirement programming.

## Important APIs, Types, And Functions
- `determine_sclk_from_bounding_box()` selects an SCLK level from `dc->sclk_lvls`.
- `dce110_get_min_vblank_time_us()` calculates the minimum vblank duration across streams.
- `dce110_fill_display_configs()` populates `dm_pp_display_configuration` per active stream.
- `dce11_pplib_apply_display_requirements()` fills power-management requirements including memory/engine clocks and display configs.
- `dce11_update_clocks()` applies PP clock-state changes, programs display clock with a 115% workaround when DFS bypass is inactive, and sends PPLIB requirements.
- `dce110_clk_mgr_construct()` builds on `dce_clk_mgr_construct()` and overrides registers, max clock table, and function pointers.

## Control Flow
The update path computes a patched display clock, requests the required PP power state if safe or necessary, calls `dce_set_clock()` when needed, stores the current display clock, and applies display requirements. Display config filling scans streams, finds their pipe contexts, skips DPMS-off streams, and records signal/link/timing metadata for PPLIB.

## State And Persistence
Persistent state includes the DCE110 max clock table and function table in `clk_mgr_internal`. Runtime updates mutate `cur_min_clks_state`, `base.clks.dispclk_khz`, and `context->pp_display_cfg`.

## Dependencies And Integration Points
Dependencies include DCE11 register definitions, common DCE clock manager utilities, PPLIB, bandwidth context, link settings, timing generators, and ASIC ID/memory type information. It is reused by DCE112 and DCE120 via exported display requirement helpers.

## Risks
The 115% patched display-clock workaround can over-request clocks and affects power. Display config filling asserts a pipe context exists for each stream; malformed state can trip assertions. Memory clock calculations depend on VBIOS bandwidth data and special Vega20/HBM handling.

## Test Signals
Validate PPLIB display configs for multi-display, DPMS-off, varying link settings, HBM/Vega20 cases, and safe-to-lower transitions. Check actual display clock, SCLK/MCLK requests, and vblank-derived switch time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.h

## Purpose
This header exposes DCE110 clock-manager construction and shared DCE11 display-requirement helpers.

## Important APIs, Types, And Functions
It declares `dce110_clk_mgr_construct()`, `dce110_fill_display_configs()`, `dce11_pplib_apply_display_requirements()`, and `dce110_get_min_vblank_time_us()`.

## Control Flow
No runtime flow is defined; the declarations are implemented in the C file and reused by later DCE managers.

## State And Persistence
No state is declared. Functions operate on `dc_context`, `clk_mgr_internal`, `dc_state`, and PP display configuration objects.

## Dependencies And Integration Points
The header is consumed by `clk_mgr.c`, DCE112, and DCE120 manager code. It provides common PPLIB display-configuration behavior for DCE11+.

## Risks
Because helper declarations are shared across DCE generations, behavior changes in DCE110 code can affect DCE112/DCE120 managers.

## Test Signals
Compile coverage plus runtime validation of DCE112/DCE120 PPLIB display requirements confirm compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c

## Purpose
This file specializes the DCE clock manager for DCE11.2/Polaris-era hardware, using `SetDCEClock` VBIOS commands for display clock and DP reference clock programming.

## Important APIs, Types, And Functions
- `dce112_set_clock()` programs display clock then programs DPREFCLK in one combined flow.
- `dce112_set_dispclk()` programs only display clock and updates DMCU PSR wait-loop timing.
- `dce112_set_dprefclk()` programs only DPREFCLK and returns the VBIOS-selected target.
- `dce112_update_clocks()` applies PP state changes, sets the patched display clock, and applies DCE11 PPLIB display requirements.
- `dce112_clk_mgr_construct()` builds on the common DCE constructor and installs DCE11.2 registers, clock limits, and functions.

## Control Flow
Display clock programming builds `bp_set_dce_clock_parameters` with `CLOCK_SOURCE_ID_DFS` and `DCECLOCK_TYPE_DISPLAY_CLOCK`, enforcing a minimum dentist VCO divider threshold. DPREFCLK programming passes a zero target and `DCECLOCK_TYPE_DPREFCLK`, allowing VBIOS to choose the frequency, with genlock-source flags disabled for Vega20.

## State And Persistence
The manager stores DCE11.2 max clocks and register tables. Runtime programming updates `cur_min_clks_state`, `dfs_bypass_disp_clk`, `base.clks.dispclk_khz`, and DMCU PSR wait-loop timing.

## Dependencies And Integration Points
Dependencies include DCE11.2 registers, common DCE helpers, DCE110 display requirements, ASIC ID macros, VBIOS `set_dce_clock`, PPLIB, and DMCU.

## Risks
The combined `dce112_set_clock()` always follows display clock programming with DPREFCLK programming, which may have side effects on link/audio timing. The 115% workaround remains in the update path. Minimum divider threshold differs from the older `/64` logic. Vega20 exception handling must align with DCE120/DCE121 behavior.

## Test Signals
Validate display clock readback, DPREFCLK stability, PSR timing, VegaM/Polaris constructor selection, safe-to-lower transitions, and DP audio/link behavior after clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.h

## Purpose
This header declares the DCE112 clock-manager constructor and split clock-programming helpers.

## Important APIs, Types, And Functions
It declares `dce112_clk_mgr_construct()`, `dce112_set_clock()`, `dce112_set_dispclk()`, and `dce112_set_dprefclk()`.

## Control Flow
No executable flow is present.

## State And Persistence
No state is declared. Functions operate on `clk_mgr` and `clk_mgr_internal` objects.

## Dependencies And Integration Points
It is included by `clk_mgr.c` and DCE120 manager code, making DCE112 `SetDCEClock` helpers shared with later DCE12.

## Risks
Any change to these helper signatures affects DCE120 and factory construction. The split helper APIs expose partially programmed states if used incorrectly.

## Test Signals
Compile coverage plus runtime DCE112/DCE120 clock programming validate the shared API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.c

## Purpose
This file specializes clock management for DCE12/Vega-era hardware, including separate display PHY voltage requests and Vega20 DCE12.1 XGMI spread-spectrum handling.

## Important APIs, Types, And Functions
- `dce121_clock_patch_xgmi_ss_info()` reads XGMI spread-spectrum info and reuses it for DPREFCLK adjustment when XGMI is enabled.
- `dce12_update_clocks()` programs display clock through DCE112 helpers, sends PP clock-for-voltage requests for display and PHY clocks, and applies DCE11 display requirements.
- `dce120_clk_mgr_construct()` initializes DCE12 defaults and sets a 600 MHz DPREFCLK.
- `dce121_clk_mgr_construct()` adjusts DPREFCLK to 625 MHz and patches XGMI spread-spectrum info when hardware sequence reports XGMI enabled.

## Control Flow
The update path patches display clock by 115% when DFS bypass is inactive, optionally spread-spectrum adjusts it for XGMI, programs the display clock, requests display-clock voltage, then independently requests PHY clock voltage based on the max pixel/symbol clock across paths.

## State And Persistence
Persistent manager state includes DCE12 max clock limits, base DPREFCLK, XGMI enable state, and spread-spectrum fields. Runtime updates mutate `base.clks.dispclk_khz`, `base.clks.phyclk_khz`, and PP display configuration state.

## Dependencies And Integration Points
It depends on DCE112 clock setters, DCE110 PPLIB display requirement helpers, DCE100 shared helpers, VBIOS spread-spectrum queries, PP clock-for-voltage APIs, and `dce121_xgmi_enabled()` from DCE120 HW sequence.

## Risks
XGMI spread-spectrum data intentionally overwrites DPREFCLK SS values, which can affect audio/display clock adjustment. Display and PHY voltage requests are separate, so missed `should_set_clock()` transitions can leave stale PP voltage requests. The 115% workaround continues to affect power.

## Test Signals
Validate Vega10 and Vega20 constructor selection, DPREFCLK values, XGMI-enabled spread-spectrum behavior, display/PHY voltage requests, multi-display PHY clock requirements, and DP audio/link stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.h

## Purpose
This header declares DCE12 and DCE12.1 clock-manager constructors.

## Important APIs, Types, And Functions
- `dce120_clk_mgr_construct()` constructs the base DCE12 manager.
- `dce121_clk_mgr_construct()` constructs the Vega20/DCE12.1 variant with adjusted DPREFCLK and XGMI handling.

## Control Flow
No runtime flow is implemented in the header.

## State And Persistence
No state is declared. Constructors initialize `struct clk_mgr_internal` instances.

## Dependencies And Integration Points
It is included by `clk_mgr.c` for FAMILY_AI clock-manager selection.

## Risks
Constructor declaration drift would break AI-family factory wiring. The header intentionally exposes only constructors, so DCE12 internals remain private.

## Test Signals
Build/link coverage plus AI/Vega20 runtime constructor selection validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.h -->
