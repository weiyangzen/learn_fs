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
