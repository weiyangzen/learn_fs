<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0.c

## Purpose

This is the common SMU v15 support layer used by SMU15 PPT implementations. It handles firmware acquisition/loading, soft PPTABLE source selection, common SMC table memory lifetimes, VBIOS boot-value parsing, driver/tool/memory-pool table address notification, feature-mask programming, generic power limits, clock limit messages, DPM table queries, performance-level transitions, media block power control, deep sleep and ULV feature toggles, BACO/BAMACO state control, thermal/MP1 IRQ registration, reset-complete event handling, and generic overdrive clock editing.

## Important APIs And Types

Exported functions include `smu_v15_0_init_microcode()`, `smu_v15_0_fini_microcode()`, `smu_v15_0_load_microcode()`, `smu_v15_0_init_pptable_microcode()`, `smu_v15_0_check_fw_status()`, `smu_v15_0_get_pptable_from_firmware()`, `smu_v15_0_setup_pptable()`, `smu_v15_0_init_smc_tables()`, `smu_v15_0_fini_smc_tables()`, `smu_v15_0_init_power()`, `smu_v15_0_fini_power()`, `smu_v15_0_get_vbios_bootup_values()`, address setters, feature controls, DPM helpers, media enable helpers, BACO helpers, `smu_v15_0_set_performance_level()`, `smu_v15_0_od_edit_dpm_table()`, and thermal alert helpers. It uses `smu_context`, `amdgpu_device`, firmware header structs, ATOM firmware info structs, `smu_15_0_dpm_context`, SMU table contexts, `smu_msg_args`, and AMDGPU IRQ source structures.

## Control Flow

Firmware initialization skips SR-IOV VFs, decodes the MP1 firmware prefix, requests `amdgpu/<prefix>.bin`, records the PM firmware version, and registers SMC firmware with PSP loading when applicable. Direct loading writes firmware dwords to MP1 SRAM and waits for the firmware interrupt-enabled flag. PPTABLE setup chooses between VBIOS and firmware tables based on SR-IOV state, emulator mode, boot `pp_table_id`, and optional `amdgpu_smu_pptable_id`; firmware tables support SMC header v2.0 and v2.1 entry tables.

Common table initialization allocates `driver_pptable`, max sustainable clocks, optional overdrive/boot/user OD tables, and `combo_pptable`; finalization frees those plus metrics, watermarks, ECC, DPM contexts, golden contexts, and power-state allocations. Boot-value parsing reads ATOM `firmwareinfo` and optional `smu_info` revisions to fill boot clocks, voltages, cooling ID, and PPTABLE ID. Runtime helpers send mailbox messages either through `smu_cmn_send_smc_msg*()` or directly through `smu->msg_ctl.ops->send_msg()` with multi-argument payloads.

Performance-level control computes per-clock min/max targets from DPM tables and UMD pstate values, then sends soft limits for GFX, UCLK, SOCCLK, VCLK/DCLK per unharvested VCN instance, and FCLK. BACO state control sends enter/exit messages and updates `smu_baco->state`; exit also clears VBIOS scratch registers for reinitialization. IRQ handling enables MP1 software interrupts and THM thermal interrupts, processes high/low thermal events, and schedules delayed software CTF work.

## State And Persistence

The file mutates firmware pointers, `adev->pm.fw_version`, PSP firmware size accounting, `smu->pptable_firmware`, `smu->smu_table.boot_values`, SMC table allocations, `smu_power.power_context`, DPM/current pstate bounds, `smu->current_power_limit`, `smu_baco->state`, IRQ source setup, and OD fine-grain GFX min/max fields. Most state is in-memory driver state and is reconstructed on device init/resume; firmware and VBIOS data are persistent external inputs.

## Dependencies And Integration Points

It depends on AMDGPU firmware helpers, PSP firmware loading, ATOMBIOS table readers, MP1/THM register definitions, common SWSMU message helpers, RAS/IRQ infrastructure, VCN/JPEG harvest metadata, BACO runpm policy, and global module parameters such as `amdgpu_smu_pptable_id` and `amdgpu_emu_mode`. ASIC-specific PPT files call these helpers from their `pptable_funcs`.

## Risks And Edge Cases

`smu_v15_0_load_microcode()` only assigns `mp1_fw_flags` inside `if (smu->is_apu)`, leaving non-APU direct-load behavior dependent on an uninitialized local if ever used. Many helpers return success when DPM is disabled, which is intentional for fallback but can hide missing feature enablement. Firmware PPTABLE parsing rejects non-v2 headers and unknown v2 minors. `smu_v15_0_init_smc_tables()` requires table sizes to be initialized by the ASIC file before allocation. OD editing only supports SCLK min/max and only in manual mode. IRQ register selection differs for APUs and dGPUs, so wrong `smu->is_apu` setup can mask or misroute interrupts.

## Test Signals

Build and boot tests should cover PSP and non-PSP firmware paths, SR-IOV VF bypass, VBIOS and firmware PPTABLE selection, ATOM firmware revisions 3.1, 3.3, 3.4, SMU info revisions 3.6 and 4.0, DPM table reads, forced performance levels, VCN/JPEG power toggles, BACO enter/exit, thermal interrupt handling, OD manual edits, and power-limit get/set sysfs paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0.c -->
