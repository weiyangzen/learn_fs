# subset-b-003738 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.c

## Purpose
`si_dpm.c` implements Southern Islands Radeon dynamic power management. It translates AtomBIOS PowerPlay tables and board-specific limits into SMC-resident state tables, programs clock/voltage/memory timing registers, manages PowerTune/CAC/DTE behavior, controls thermal/fan policy, and exposes the SI DPM hooks used by the Radeon ASIC dispatch table.

The file is specific to SI-family chips such as Tahiti, Pitcairn, Verde, Oland, and Hainan. Its large static front matter is not generic data: it contains ASIC and device-id-specific CAC weights, leakage coefficients, PowerTune defaults, and DTE thermal-estimator tables that directly affect throttling and power containment.

## Important APIs, types, and functions
- Public DPM lifecycle hooks: `si_dpm_init`, `si_dpm_setup_asic`, `si_dpm_enable`, `si_dpm_late_enable`, `si_dpm_disable`, `si_dpm_pre_set_power_state`, `si_dpm_set_power_state`, `si_dpm_post_set_power_state`, `si_dpm_fini`, and `si_dpm_display_configuration_changed`.
- Public controls and observability: `si_dpm_force_performance_level`, `si_dpm_debugfs_print_current_performance_level`, `si_dpm_get_current_sclk`, `si_dpm_get_current_mclk`, fan percent/mode helpers, and exported memory-clock ratio helpers `si_get_ddr3_mclk_frequency_ratio`, `si_get_mclk_frequency_ratio`, and `si_trim_voltage_table_to_fit_state_table`.
- SMC table builders: `si_init_smc_table`, `si_upload_sw_state`, `si_upload_ulv_state`, `si_populate_smc_tdp_limits`, `si_initialize_smc_cac_tables`, `si_initialize_smc_dte_tables`, `si_init_smc_spll_table`, `si_populate_mc_reg_table`, and `si_upload_mc_reg_table`.
- Clock and voltage conversion helpers: `si_calculate_sclk_params`, `si_populate_sclk_value`, `si_populate_mclk_value`, `si_construct_voltage_tables`, `si_populate_voltage_value`, `si_get_std_voltage_value`, `si_populate_phase_shedding_value`, and `si_convert_power_level_to_smc`.
- State adjustment and transition helpers: `si_apply_state_adjust_rules`, `si_convert_power_state_to_smc`, `si_restrict_performance_levels_before_switch`, `si_set_sw_state`, `si_halt_smc`, `si_resume_smc`, `si_enable_smc_cac`, `si_enable_power_containment`, and ULV/PCIe/VCE helpers.
- Important local data includes the ASIC-specific `si_cac_config_reg` arrays, `si_powertune_data` instances, DTE tables, `union power_info`, `union pplib_clock_info`, and `union pplib_power_state`. Runtime state lives primarily in `struct si_power_info`, defined in `si_dpm.h`, and its embedded `ni_power_info`/`evergreen_power_info`/`rv7xx_power_info` ancestry.

## Control flow
Initialization begins in `si_dpm_init`. It allocates `struct si_power_info`, derives PCIe capabilities, reads leakage values, patches voltage dependency tables, parses platform and extended power tables, parses SI PowerPlay states, initializes display-clock voltage rules, detects voltage control mechanisms, configures feature defaults, and selects PowerTune/CAC/DTE tables according to chip family and PCI device id.

ASIC setup in `si_dpm_setup_asic` loads MC firmware, detects memory type, snapshots boot clock registers, and enables ACPI static power management. Full enablement in `si_dpm_enable` is a strict hardware bring-up sequence: enable voltage control, build voltage and MC timing tables, enable spread spectrum and thermal protection, program SCLK trend/filter defaults, load SMC firmware, read SMC firmware table offsets, initialize SMC state/SPLL/ARB/MC/CAC/DTE/TDP/fan tables, program response times and deep-sleep registers, start the SMC, enable SCLK/DPM, register thermal throttling, start the thermal controller, and set the current power state to the boot state.

Power-state changes are split across pre/set/post hooks. `si_dpm_pre_set_power_state` copies the requested state into the SI/Evergreen requested state and applies display, UVD/VCE, voltage, dependency-table, DC-limit, and forced-clock adjustments. `si_dpm_set_power_state` then disables ULV and active power containment, requests PCIe speed changes when needed, halts the SMC, uploads the new driver state, display timing soft registers, ULV state, MC register data, and memory timing data, resumes the SMC, asks it to switch to the software state, adjusts UVD/VCE clocks, optionally re-enables ULV, CAC, DTE, and power containment, and refreshes TDP limits through `si_power_control_set_level`. `si_dpm_post_set_power_state` commits the requested state as current.

Disable reverses the policy stack: it stops thermal/fan management, disables ULV, clears voltage control tuning, disables containment and CAC, disables spread spectrum and thermal throttle sources, stops global DPM, asks the SMC to reset to defaults, resets/stops the SMC, switches MC arbitration back to F0, and restores the boot power state in driver state.

## State and persistence behavior
The file mutates several layers of persistent state. Driver-owned persistent state includes `rdev->pm.dpm.priv`, the parsed power-state array and `ps_priv` allocations, dynamic dependency tables, current/requested/boot power-state pointers, fan mode snapshots, leakage tables, SMC firmware offsets, cached clock registers, and feature flags such as `enable_dte`, `enable_ppm`, `voltage_control_svi2`, `vddc_phase_shed_control`, and `fan_is_controlled_by_smc`.

Hardware state is programmed through MMIO registers for SCLK/MPLL/SPLL control, CAC, thermal interrupts, fan/tach PWM, display gap handling, voltage control, PCIe link/lane settings, MC timing, MC low-power mirror registers, and global DPM enablement. SMC-resident state is persisted by writes into SMC SRAM at firmware-advertised offsets for `SISLANDS_SMC_STATETABLE`, MC register tables, CAC configuration, DTE configuration, SPLL division tables, PAPM parameters, fan tables, and soft registers. These writes use big-endian SMC structures and remain active until overwritten, firmware reset, SMC reset, or device reset.

Memory ownership is explicit but scattered: `si_dpm_init` allocates `si_power_info`, per-state `struct ni_ps`, `rdev->pm.dpm.ps`, and a display-clock voltage dependency table; `si_dpm_fini` frees those and the extended power table. Several table builders allocate temporary SMC-format buffers with `kzalloc_obj` and free them after `si_copy_bytes_to_smc`.

## Dependencies and integration points
`si_dpm.c` sits in the Radeon kernel driver power-management stack. It depends on AtomBIOS helpers for PowerPlay parsing, clock dividers, memory PLL dividers, voltage tables, leakage indices, spread-spectrum data, MC timing programming, and default voltage queries. It uses lower-generation helpers from `r600_dpm.c`, `rv770`, `evergreen`, `btc`, and `ni_dpm` for platform caps, dependency-rule enforcement, UVD clock ordering, memory arbitration switching, and shared power-info structures.

SMC interaction depends on `si_smc.c` and `sislands_smc.h` for SRAM access and PPSMC message definitions. Hardware register names and bitfields come from `sid.h`, `si.h`, and related Radeon headers. VCE integration is through `vce_v1_0_enable_mgcg` and `radeon_set_vce_clocks`. PCIe integration uses PCI capability helpers, Radeon PCIe lane/speed helpers, and optional ACPI performance requests. The public DPM hooks are wired through `radeon_asic.c`/`radeon_asic.h`.

## Risks and edge cases
- The enable and state-switch sequences are order-sensitive. Halting/resuming the SMC, uploading SMC tables, switching MC arbitration sets, and changing voltage/clock/PCIe policy out of order can hang the GPU or leave unsafe clocks active.
- Many fields are endian-converted into SMC structures. Missing `cpu_to_be16`/`cpu_to_be32` conversions or copying host-endian data into SMC SRAM would corrupt firmware interpretation.
- Static CAC/DTE/PowerTune tables are keyed by chip family and PCI device id. Wrong table selection can mis-estimate leakage or thermal behavior and cause under-throttling, over-throttling, fan problems, or instability.
- Voltage table handling has several fallback paths. GPIO LUT, SVI2, MVDD, VDDCI, leakage-index patching, and phase shedding must all agree with the AtomBIOS data and maximum SMC level counts.
- Several functions intentionally disable features on errors and continue, for example CAC or dynamic AC timing. This avoids hard failures but can hide performance or thermal-policy regressions.
- Display, UVD, VCE, and multi-CRTC constraints can force high clocks or disable switching. Regressions here commonly show up as flicker, underruns, video decode/encode failures, or excessive idle power.
- There are legacy `#if 0` blocks and comments marking incomplete validation, especially around ULV and display requirements. These paths should be treated conservatively.

## Test signals
Useful validation includes SI ASIC probe and DPM enable/disable, suspend/resume, runtime power-state switching on AC and DC, forced low/high/auto levels, debugfs current SCLK/MCLK reporting, thermal interrupt delivery, fan auto/static mode changes, UVD playback, VCE encode clock changes, multi-monitor modesets, high pixel-clock displays, PCIe speed/lane transitions, and GPU stability under power/thermal stress. Kernel logs should be checked for the explicit `DRM_ERROR` messages emitted by firmware upload, SMC header parsing, SMC table initialization, CAC/DTE setup, MC timing upload, and state switch failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.h

## Purpose
`si_dpm.h` defines the Southern Islands DPM private state schema and a small cross-file helper API. It bridges generic Northern Islands/Evergreen/RV7xx DPM structures with SI-specific SMC tables, PowerTune/CAC/DTE data, memory-controller register tables, ULV parameters, PCIe policy, SVI2 metadata, and fan-control bookkeeping.

## Important APIs, types, and data
- Includes `ni_dpm.h` and `sislands_smc.h`, so the header depends on shared DPM state, Atom voltage-table types, and SMC structure definitions.
- `enum si_cac_config_reg_type` distinguishes normal MMIO register configuration from SMC clock-gating indexed register configuration.
- `struct si_cac_config_reg` describes one CAC register field patch: offset, mask, shift, value, and register-space type.
- `struct si_powertune_data`, `struct si_dyn_powertune_data`, and `struct si_dte_data` carry static and runtime PowerTune/CAC/DTE parameters such as leakage coefficients, CAC windows, long-term-average settings, temperature filters, thresholds, and enable defaults.
- `struct si_clock_registers` snapshots boot SPLL/MPLL/DLL registers so SMC power levels can be populated from known hardware state.
- `struct si_mc_reg_entry` and `struct si_mc_reg_table` store AtomBIOS memory-controller timing entries and the SI SMC register-address/value form.
- `struct si_leakage_voltage` maps special leakage-index pseudo-voltages to real board voltages read from AtomBIOS.
- `struct si_ulv_param` stores ultra-low-voltage support, its power level, control registers, delay, and PCIe x1 preference.
- `struct si_power_info` is the central SI private power state. It embeds `struct ni_power_info` as its first field, then adds cached registers, SMC scratch tables, voltage tables, leakage data, ULV info, PCIe state, feature flags, SMC firmware offsets, PowerTune/DTE pointers, SVI2 GPIO IDs, and fan control state.
- Exported helpers are `si_get_ddr3_mclk_frequency_ratio`, `si_get_mclk_frequency_ratio`, and `si_trim_voltage_table_to_fit_state_table`.

## Control flow and integration points
The header has no executable control flow, but its layout shapes the runtime behavior of `si_dpm.c`. `si_dpm_init` allocates `struct si_power_info` and stores it in `rdev->pm.dpm.priv`; helper accessors then cast it back and access embedded NI/Evergreen/RV7xx state. SMC table builders fill the scratch SMC structures stored in `si_power_info`, while firmware header parsing fills the SMC offset fields. Consumers outside `si_dpm.c`, especially CIK DPM code, reuse the exported memory-clock ratio and voltage-table trimming helpers.

## State and persistence behavior
This header defines persistent driver state rather than mutating it. Instances of `struct si_power_info` persist for the DPM lifetime and are freed by `si_dpm_fini`. The SMC offset fields persist after firmware header parsing and are used for later SMC SRAM writes. Cached clock registers represent boot hardware state used repeatedly when constructing initial, ACPI, ULV, and driver power levels. Fan fields persist the pre-manual default mode so manual fan control can be reverted.

## Dependencies and constraints
`struct si_power_info` must keep `struct ni_power_info ni` first because existing helper code treats SI state as NI/Evergreen/RV7xx state through embedded base structures. Array sizes are tied to SMC ABI constants such as `SMC_SISLANDS_MC_REGISTER_ARRAY_SIZE`, `SMC_SISLANDS_DTE_MAX_FILTER_STAGES`, and `SISLANDS_MAX_HARDWARE_POWERLEVELS`. Callers must respect these fixed counts when copying AtomBIOS tables and building SMC payloads.

## Risks and test signals
The main risks are ABI and layout drift. Reordering the first field breaks inherited power-info access; changing table sizes or indexes breaks SMC SRAM payload construction; changing defaults for DPM2, ULV, or leakage constants changes throttling behavior. Compile coverage catches many type/layout errors, but runtime signals are DPM initialization, power-state switching, CAC/DTE enablement, MC timing upload, fan control, and reuse of the exported helpers by later Radeon DPM code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_reg.h

## Purpose
`si_reg.h` is a compact SI register-definition header focused on display hotplug GPIO and primary graphics surface control. It supplies the register addresses and bitfield packing macros used by Radeon display code to program SI scanout format, tiling, bank, tile-split, macro-tile, array-mode, and pipe-configuration fields.

## Important APIs, types, and definitions
- Hotplug GPIO registers: `SI_DC_GPIO_HPD_MASK`, `SI_DC_GPIO_HPD_A`, `SI_DC_GPIO_HPD_EN`, and `SI_DC_GPIO_HPD_Y`.
- Main display surface control register: `SI_GRPH_CONTROL`.
- Field packers for `SI_GRPH_CONTROL`: `SI_GRPH_DEPTH`, `SI_GRPH_NUM_BANKS`, `SI_GRPH_Z`, `SI_GRPH_BANK_WIDTH`, `SI_GRPH_FORMAT`, `SI_GRPH_BANK_HEIGHT`, `SI_GRPH_TILE_SPLIT`, `SI_GRPH_MACRO_TILE_ASPECT`, `SI_GRPH_ARRAY_MODE`, and `SI_GRPH_PIPE_CONFIG`.
- Enumerated field values cover 8/16/32 bpp surface formats, bank counts, bank width/height, tile split sizes from 64 bytes through 4 KiB, macro-tile aspect, linear and tiled array modes, and several SI pipe configurations.

## Control flow and integration points
The file contains only preprocessor definitions. It is included by `radeon_reg.h`, making these SI display definitions available to the broader Radeon driver. Display modeset, framebuffer, and scanout programming paths compose values with these macros before writing `SI_GRPH_CONTROL` or the hotplug GPIO registers.

## State and persistence behavior
All state represented by this file is hardware register state. Writes using these macros persist in the display engine until another modeset, framebuffer update, power transition, or reset overwrites them. The header itself owns no runtime state and performs no validation.

## Dependencies and constraints
The macros assume callers pass already-normalized field values. Each macro masks only the local field width and shifts into the SI register layout; it does not verify that the chosen depth/format/tiling/pipe combination is valid for the active framebuffer, ASIC, or memory layout. Consumers must pair these values with the correct surface address, pitch, tiling metadata, and display mode.

## Risks and test signals
Incorrect bit definitions or caller misuse can produce corrupted scanout, blank screens, hotplug failures, memory tiling mismatches, or display underruns. Test signals include SI modeset tests, framebuffer format coverage across 8/16/32 bpp where supported, tiled and linear scanout, hotplug detection, suspend/resume display restoration, and register readback comparison against expected modeset programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_smc.c

## Purpose
`si_smc.c` implements low-level Southern Islands System Management Controller access. It provides serialized SMC SRAM reads/writes, SMC microcode loading, SMC reset/start/clock control, and synchronous PPSMC message delivery. Higher-level DPM code in `si_dpm.c` depends on this file to load firmware, populate SMC tables, and issue runtime power-management commands.

## Important APIs and functions
- `si_copy_bytes_to_smc` copies arbitrary bytes to SMC SRAM with alignment and limit checks. It writes full dwords in SMC big-endian byte order and performs read-modify-write for trailing partial dwords.
- `si_start_smc`, `si_reset_smc`, `si_stop_smc_clock`, `si_start_smc_clock`, and `si_is_smc_running` control or inspect SMC reset and clock bits.
- `si_program_jump_on_start` writes a small startup jump sequence at SMC address zero before releasing the SMC.
- `si_send_msg_to_smc` writes a PPSMC message to `SMC_MESSAGE_0`, polls `SMC_RESP_0` up to `rdev->usec_timeout`, and returns the firmware response code.
- `si_wait_for_smc_inactive` polls SMC clock-control state after halt-style messages.
- `si_load_smc_ucode` loads either newer header-described firmware or legacy family-specific firmware at known SMC addresses and sizes.
- `si_read_smc_sram_dword` and `si_write_smc_sram_dword` provide locked indexed dword access to SMC SRAM.
- Internal helper `si_set_smc_sram_address` validates alignment/range and programs the indexed SMC SRAM address.

## Control flow
All SRAM access goes through the SMC indexed register pair. Address setup validates 4-byte alignment and the caller-supplied SRAM limit, writes `SMC_IND_INDEX_0`, and disables auto-increment unless the bulk firmware loader explicitly enables it. Byte copying serializes on `rdev->smc_idx_lock`, writes big-endian dwords, and preserves untouched bytes in the last dword.

Firmware loading first validates that firmware is present. For new firmware it parses `smc_firmware_header_v1_0` to get the ucode start, size, and payload offset; for legacy firmware it selects family-specific start and size constants for Tahiti, Pitcairn, Verde, Oland, or Hainan. It then enables SMC auto-increment, streams big-endian dwords to `SMC_IND_DATA_0`, disables auto-increment, and releases the lock.

Message delivery first checks `si_is_smc_running`; if reset or clock-disabled, it fails immediately. Otherwise it writes the message and polls for any nonzero response. DPM callers interpret only `PPSMC_Result_OK` as success for most transitions.

## State and persistence behavior
Persistent hardware state includes SMC SRAM contents, loaded SMC firmware, SMC reset state, SMC clock-gate state, SMC message/response registers, and the SMC indexed access auto-increment setting. The spinlock protects the shared indexed register window from concurrent users on the CPU side. The file does not allocate persistent memory; it consumes `rdev->smc_fw`, `rdev->new_fw`, `rdev->family`, `rdev->usec_timeout`, and `rdev->smc_idx_lock`.

## Dependencies and integration points
The file depends on Radeon MMIO accessors and SI register definitions from `radeon.h`, `sid.h`, `ppsmc.h`, `radeon_ucode.h`, and `sislands_smc.h`. It is called heavily by `si_dpm.c` for firmware upload, SMC firmware header reads, SMC state/table writes, soft register writes, CAC/DTE/fan table uploads, and PPSMC state-transition messages. `sislands_smc.h` exposes the function prototypes to the DPM layer.

## Risks and edge cases
- SMC SRAM is big-endian, so byte order is critical. Incorrect packing corrupts firmware or SMC data tables.
- Alignment and limit checks are the primary protection against bad SRAM accesses. Callers must pass the correct firmware-discovered SRAM end and table offsets.
- Partial dword writes perform read-modify-write; failure to serialize indexed access would corrupt unrelated bytes, which is why the spinlock is required.
- `si_send_msg_to_smc` treats any nonzero response as completion and returns the raw response. Callers must check for `PPSMC_Result_OK`.
- Legacy firmware loading uses a `BUG()` on unknown ASIC family, making unsupported family routing fatal.
- `si_wait_for_smc_inactive` currently returns OK after polling regardless of timeout details, so higher-level code may not distinguish a slow or stuck SMC.

## Test signals
Useful validation includes successful SI SMC firmware load, DPM enablement, SMC firmware header parsing from SRAM, repeated state transitions, fan-control start/stop messages, CAC/DTE enable messages, suspend/resume, and failure-path tests for missing firmware, unaligned SMC addresses, oversized copies, and SMC-not-running message sends. Kernel logs around `si_upload_firmware`, `si_process_firmware_header`, and DPM state-switch failures are the most direct runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_smc.c -->
