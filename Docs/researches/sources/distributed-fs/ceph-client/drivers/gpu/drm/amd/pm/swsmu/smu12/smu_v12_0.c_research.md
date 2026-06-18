# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c

## Purpose

`smu_v12_0.c` provides common SMU12 helper logic used by Renoir-class APUs. It covers firmware status polling, SDMA/GFX power-gating messages, GFXOFF status/control, SMU table finalization/default loading, mode2 reset, clock range programming, driver table address notification, VBIOS boot value parsing, and SMU message-control initialization.

## Important APIs, Types, and Functions

Exported functions include `smu_v12_0_check_fw_status`, `smu_v12_0_powergate_sdma`, `smu_v12_0_set_gfx_cgpg`, `smu_v12_0_get_gfxoff_status`, `smu_v12_0_gfx_off_control`, `smu_v12_0_fini_smc_tables`, `smu_v12_0_set_default_dpm_tables`, `smu_v12_0_mode2_reset`, `smu_v12_0_set_soft_freq_limited_range`, `smu_v12_0_set_driver_table_location`, `smu_v12_0_get_vbios_bootup_values`, and `smu_v12_0_init_msg_ctl`.

The key local helper is `smu_v12_0_atom_get_smu_clockinfo`. Important structures include `struct smu_context`, `struct amdgpu_device`, `struct smu_table_context`, `struct atom_firmware_info_v3_1`, and `struct atom_firmware_info_v3_3`.

## Control Flow

Firmware status reads `smnMP1_FIRMWARE_FLAGS` through PCIe and checks the interrupt-enabled bit. Power gating sends SMU messages only where appropriate: SDMA is gated only for APUs, and GFX CGPG exits early if the device lacks `AMD_PG_SUPPORT_GFX_PG` or is in S0ix.

GFXOFF control sends allow/disallow messages; disable waits up to 500 ms for `smu_v12_0_get_gfxoff_status` to report status `2` (not in GFXOFF). GFXOFF status is extracted from `SMUIO_GFX_MISC_CNTL.PWR_GFXOFF_STATUS`.

Soft frequency range programming maps common clock types to SMU12-specific messages: GFX uses hard-min/soft-max GFXCLK, FCLK/MCLK/UCLK share FCLK messages, SOCCLK uses SOC messages, and VCLK uses VCN messages.

VBIOS boot parsing reads the ATOM `firmwareinfo` table, supports format revision 3 content revisions through the v3.1 and v3.3 layouts, stores boot values, then queries ATOM `getsmuclockinfo` for SOC, DCEF, VCLK, DCLK, optional FCLK, and LCLK boot clocks.

Message control configures the SMU v1 message registers at MP1 C2PMSG 66/90/82 and installs the caller-supplied message map.

## State and Persistence Behavior

The file frees and nulls `clocks_table`, `metrics_table`, and `watermarks_table`, and finalizes the GPU metrics driver table. It reads/writes no persistent host files. Firmware/hardware state is changed by SDMA, CGPG, GFXOFF, reset, DPM range, DPM clock table, and driver-table-address SMU messages, and by reading SMUIO/MP1 registers.

## Dependencies

Dependencies include AMDGPU core, ATOM firmware helpers, `smu_v12_0.h`, SOC15 helpers, SMU common helpers, MP 12.0 and SMUIO 12.0 generated register headers, and SMU message v1 ops.

## Integration Points

`renoir_ppt.c` uses this file for most common callbacks. Display and PM code indirectly call GFXOFF, DPM range, watermarks/default table, and VBIOS boot helpers through `pptable_funcs`. The message-control setup is the foundation for all Renoir SMU message traffic.

## Risks and Edge Cases

The file undefines `mmPWR_MISC_CNTL_STATUS` from the SMUIO12 header because some SMU12 ASICs use older offset tables, highlighting register-map ambiguity. GFXOFF disable logs but does not return a timeout error if status never reaches on-state. Clock handling maps MCLK/UCLK to FCLK, which is Renoir-specific and should not be generalized blindly. VBIOS parsing rejects non-format-3 firmware info. Driver table address messages are skipped silently when `mc_address` is zero.

## Test Signals

Test signals include firmware status success, Renoir GFXOFF status/control, SDMA power gate on APU, CGPG enable/disable with S0ix guard, default DPM table transfer, mode2 reset, DPM clock range sysfs operations, correct VBIOS boot clocks, and successful SMU message traffic using MP1 C2P registers.
