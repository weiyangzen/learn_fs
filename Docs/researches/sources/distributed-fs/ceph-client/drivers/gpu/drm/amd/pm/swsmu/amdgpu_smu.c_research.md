<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/amdgpu_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/amdgpu_smu.c

## Purpose
This file is the top-level AMDGPU software SMU integration layer. It wires the SMC/MP1 IP block into the AMDGPU IP lifecycle, selects ASIC-specific `pptable_funcs`, starts and checks SMU firmware, allocates and transfers SMU tables, enables power-management features, and exports the common powerplay operations through `swsmu_pm_funcs`. It is the coordination point between generic AMDGPU power management, display clock requirements, RAS, reset paths, debugfs STB capture, WBRF RF-interference handling, and per-ASIC PMFW command/table implementations.

## Important APIs, Types, and Functions
- IP lifecycle: `smu_early_init`, `smu_sw_init`, `smu_hw_init`, `smu_late_init`, `smu_hw_fini`, `smu_sw_fini`, `smu_suspend`, `smu_resume`, `smu_reset`, and exported `smu_ip_funcs` plus `smu_v11_0_ip_block` through `smu_v15_0_ip_block`.
- ASIC dispatch: `smu_set_funcs` selects Navi10, Sienna Cichlid, Renoir, Vangogh, Arcturus, Aldebaran, Cyan Skillfish, SMU v13/v14/v15 tables by MP1 IP version and adjusts OD/GFXOFF feature defaults.
- Table and memory setup: `smu_smc_table_sw_init`, `smu_init_fb_allocations`, `smu_alloc_memory_pool`, `smu_alloc_dummy_read_table`, `smu_update_gpu_addresses`, `smu_smc_hw_setup`, `smu_smc_hw_cleanup`.
- User and sysfs-facing PM operations: clock forcing, performance level, OD edits, power limits, pp table upload, pp feature mask, power profile modes, fan control, sensors, metrics, watermarks, and display clock voltage requests.
- Exported helpers: `is_support_sw_smu`, `is_support_cclk_dpm`, `smu_set_soft_freq_range`, `smu_get_dpm_freq_range`, `smu_set_ac_dc`, `smu_mode1_reset`, `smu_link_reset`, RAS helpers, GFXOFF helpers, ECC/HBM bad page messaging, SDMA/VCN reset helpers, PM policy helpers, and STB debugfs setup.

## Control Flow
Initialization starts in `smu_early_init`, which allocates `struct smu_context`, records `adev`, sets defaults, installs `swsmu_pm_funcs`, selects per-ASIC callbacks, and requests microcode. `smu_sw_init` initializes feature bitmaps, work items, atomic power-gate state, delayed thermal shutdown work, SMU table contexts, VBIOS boot values, PPTable microcode, IRQ handling, and fan capability flags. `smu_hw_init` starts/checks the SMC engine, evaluates WBRF support, powers APU media blocks as needed, initializes allowed feature masks, then runs `smu_smc_hw_setup`. Hardware setup pre-sets display count, sends driver/tool/memory-pool addresses, sets up and transfers the PPTable unless SCPM owns it, runs BTC, enables WBRF UCLK shadow, pushes allowed features, updates PCIe caps, enables system features, captures enabled feature masks, builds default DPM tables, fetches thermal limits, enables thermal alerts, notifies display state, sets minimum deep sleep DCEFCLK, and registers WBRF work.

Runtime operations mostly enter through `swsmu_pm_funcs`, validate `pm_enabled` and `adev->pm.dpm_enabled`, convert generic enums into SMU enums, and delegate to `smu->ppt_funcs`. Power-state changes run through `smu_handle_task` and `smu_adjust_power_state_dynamic`, which apply display changes, clock rules, SMC display notification, ASIC performance level selection, and workload profile updates. Suspend and fini paths cancel work, disable thermal alerting, selectively disable DPM features depending on BACO/S0ix/reset/ASIC/SCPM state, gate media blocks, clear watermarks/workloads, and save GFXOFF entry counts for continuity.

## State and Persistence Behavior
`struct smu_context` persists from early init to late fini and owns powerplay state, table buffers, feature masks, DPM levels, workload refcounts, user DPM profile, WBRF notifier state, work items, STB configuration, and cached limits/metrics. User settings are intentionally sticky: `smu_restore_dpm_user_profile` replays saved power limits, manual clock masks, fan mode/speed, and OD settings after suspend/resume while suppressing recursive profile updates with `SMU_DPM_USER_PROFILE_RESTORE`. `hardcode_pptable` persists a user-uploaded PPTable and triggers a full SMU reset. Metrics and temp tables use cache buffers and jiffies-based validity. Atomic power-gate fields mirror VCN/JPEG/VPE/ISP/UMSCH state so repeated gate requests are skipped. Delayed work persists for SW CTF shutdown and WBRF event coalescing until cleanup.

## Dependencies and Integration Points
- Depends on AMDGPU core device/IP infrastructure, firmware loading, PSP firmware mode, BO allocation, IRQ registration, PCIe capability masks, VBIOS boot values, power supply AC/DC state, debugfs, RAS, XCP, and display manager PP interfaces.
- Integrates with ASIC-specific `ppt_funcs` providers such as Navi10, Arcturus, Aldebaran, Cyan Skillfish, and SMU v13/v14/v15 backends.
- PMFW communication and table identifiers come from `amdgpu_smu.h`, `smu_internal.h`, `smu_types.h`, and pmfw interface headers.
- WBRF integration uses `linux/acpi_amd_wbrf.h` to consume Wi-Fi exclusion ranges and forward them to PMFW.
- Display integration uses DC callbacks for clocks, watermarks, display count, memory clock switching, and max sustainable clocks.

## Risks
- The file is callback-heavy; missing `ppt_funcs` members normally degrade to `-EOPNOTSUPP` or no-op, but an incorrectly selected callback table will misprogram firmware.
- State gates differ by path: reset/MP1/BACO functions intentionally work when DPM is down, while sysfs-like paths reject calls. Mixing those semantics can break suspend, reset, or runpm.
- PPTable upload resets the SMU and changes `power_play_table` backing storage, so size checks, lifetime, and reset error handling are important.
- Table BO sizes, DMA addresses, and cache sizes must match PMFW ABI expectations; mismatches can corrupt metrics, watermarks, or firmware tables.
- User DPM restoration can reapply stale power, clock, fan, or OD values after resume if validation rules change.
- WBRF delayed work and thermal shutdown work must be cancelled on fini to avoid use-after-free of `smu_context`.

## Test Signals
- Build with AMDGPU PM enabled and the relevant ASIC configs; compiler coverage should catch missing callback prototypes and PMFW table type mismatches.
- Boot or probe tests should show successful SMC firmware version check, PPTable transfer, DPM enablement, thermal alert enablement, and `SMU is initialized successfully`.
- Exercise sysfs/debugfs paths for `pp_dpm_*`, `power_dpm_force_performance_level`, `pp_power_profile_mode`, fan control, pp feature masks, metrics, and `amdgpu_smu_stb_dump`.
- Suspend/resume, runpm, BACO, mode1/mode2/link reset, and custom PPTable upload are critical regression paths.
- Negative tests should cover unsupported callbacks returning `-EOPNOTSUPP`, out-of-range power limits, invalid fan speed `U32_MAX`, invalid OD/clock types, and cache expiry for metrics tables.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/amdgpu_smu.c -->
