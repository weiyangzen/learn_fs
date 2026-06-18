# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c

## Purpose
`smu_v13_0.c` is the shared SMU v13 backend used by multiple AMDGPU PPT implementations. It provides common firmware loading, PPT selection, SMU table lifecycle, boot-value parsing, mailbox setup, DPM querying and soft limits, fan and thermal control, interrupt processing, BACO/reset helpers, PCIe override, and WBRF exclusion upload.

## Important APIs And Functions
Firmware and PPT paths include `smu_v13_0_init_microcode`, `smu_v13_0_fini_microcode`, `smu_v13_0_load_microcode`, `smu_v13_0_init_pptable_microcode`, `smu_v13_0_setup_pptable`, and `smu_v13_0_get_pptable_from_firmware`. State allocation is handled by `smu_v13_0_init_smc_tables`, `smu_v13_0_fini_smc_tables`, `smu_v13_0_init_power`, and `smu_v13_0_fini_power`.

DPM helpers include `smu_v13_0_get_dpm_ultimate_freq`, `smu_v13_0_set_soft_freq_limited_range`, `smu_v13_0_set_performance_level`, `smu_v13_0_get_boot_freq_by_index`, `smu_v13_0_get_dpm_freq_by_index`, and `smu_v13_0_set_single_dpm_table`. Thermal and IRQ functions include `smu_v13_0_register_irq_handler`, `smu_v13_0_enable_thermal_alert`, `smu_v13_0_disable_thermal_alert`, `smu_v13_0_irq_process`, and `smu_v13_0_interrupt_work`.

## Control Flow
Bring-up requests SMU firmware unless in SR-IOV VF mode, registers PSP-loaded firmware when applicable, reads VBIOS boot values, allocates SMU tables, selects VBIOS or firmware PPT data, sends DRAM table locations to PMFW, and applies allowed feature masks. Runtime operations usually map generic SMU IDs through ASIC-specific maps, pack PMFW arguments, and send `smu_cmn_send_smc_msg_with_param`.

Performance-level control computes target min/max ranges from DPM tables or `smu->pstate_table`, applies IP-specific exceptions, sends soft-min/soft-max messages, and updates cached current pstate ranges. IRQ processing handles thermal high/low, critical-temperature shutdown, AC/DC transitions, throttling logging, and fan abnormal/recovery threshold changes.

## State And Persistence
The file owns runtime allocations under `smu->smu_table`, `smu->smu_dpm`, and `smu->smu_power`, including driver PPT, overdrive tables, metrics/watermark/ecc buffers, DPM contexts, and max sustainable clocks. It updates cached fields such as current power limit, BACO state, pstate current limits, and WBRF table content. Firmware state lives in `adev->pm.fw` until finalized.

## Dependencies And Integration Points
It integrates with Linux firmware loading, ATOM BIOS, PSP firmware loading, AMDGPU IRQs, SOC15 register access, `smu_cmn` messaging, RAS/throttling notification, runpm/BACO, VCN/JPEG control, display notification, PCIe capability management, and WBRF Wi-Fi exclusion ranges. It relies on ASIC PPT files to install message, clock, power-source, table, and workload mappings.

## Risks
PPT source selection can bind incompatible tables if driver overrides, SR-IOV, SCPM, or emulation rules are wrong. DPM table population assumes PMFW-reported counts fit cached arrays. Thermal interrupt paths can trigger system shutdown and must keep source IDs and thresholds exact. BACO/reset paths alter hardware access and scratch registers. WBRF Hz-to-MHz conversion must preserve exclusion coverage.

## Test Signals
Relevant tests include boot on each supported SMU v13 ASIC, firmware load/unload logs, VBIOS and firmware PPT paths, SR-IOV VF no-firmware path, DPM sysfs levels, performance-level transitions, power-limit set/get, fan PWM/RPM control, thermal alert enable/disable, AC/DC interrupt reenable, BACO enter/exit, mode1 reset recovery, PCIe clamping, and WBRF add/remove updates.
