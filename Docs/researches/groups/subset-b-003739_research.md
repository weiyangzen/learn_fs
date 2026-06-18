# subset-b-003739 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sid.h

## Purpose
`sid.h` is the Southern Islands ASIC hardware definition header for the Radeon DRM driver. It supplies SI-family register addresses, bitfield helpers, golden configuration constants, PM4 packet encoders, DMA packet encoders, and media/display/VM/power-management register definitions used by the SI display, command processor, DMA, SMC, UVD, VCE, interrupt, memory-controller, and DPM code.

## Important APIs, types, and definitions
- ASIC topology and golden constants: `TAHITI_RB_BITMAP_WIDTH_PER_SH`, `*_GB_ADDR_CONFIG_GOLDEN`, and maximum masks for shader engines, SIMDs, backends, pipes, LDS, and TCCs.
- SMC and clock/power registers: `SMC_IND_*`, `SMC_MESSAGE_0`, `CG_SPLL_*`, `CG_UPLL_*`, `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, thermal/fan registers, CAC/ULV controls, and power-gating flags.
- VM and memory-controller definitions: `VM_L2_CNTL*`, `VM_CONTEXT*_CNTL`, fault status fields, invalidation registers, FB/AGP/system aperture registers, MC timing/training registers, and memory-clock PLL fields.
- Display and interrupt definitions: DMIF/LB priority and watermarks, vblank/vline/pflip interrupt bits, HPD status/control registers, DCE6 audio endpoint registers, audio DTO registers, and AFMT source selection.
- Graphics and CP/RLC definitions: `GRBM_*`, soft reset masks, `GRBM_GFX_INDEX`, CP ring registers, interrupt bits, scratch registers, shader/tiling/backend registers, and RLC power-gating/register save-restore fields.
- Packet helpers: `PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`, many `PACKET3_*` opcodes and field helpers, async DMA ring registers, `DMA_PACKET`, `DMA_IB_PACKET`, `DMA_PTE_PDE_PACKET`, and DMA opcodes.
- Media definitions: UVD ring/status/clock-gating registers and VCE firmware, ring, cache, command, and PLL definitions.

## Control flow and integration points
The file has no executable control flow. It is included by SI implementation files such as `si.c`, `si_dma.c`, `si_dpm.c`, `si_smc.c`, DCE6 audio/display code, and Radeon VCE support. Those consumers use the macros to compose MMIO writes, indirect SMC accesses, CP command streams, DMA command streams, VM invalidation sequences, media firmware setup, display interrupt handling, and power-management transitions.

## State and persistence behavior
All persistent state represented by this header lives in hardware registers or command streams emitted to hardware. Writes using these definitions configure clocks, voltage/power gates, PLLs, memory mappings, VM contexts, interrupts, CP rings, RLC state, display/audio state, DMA rings, UVD, and VCE. Packet macros create transient CPU-side dwords that become persistent GPU state after ring execution.

## Dependencies and constraints
Consumers must provide Radeon packet constants such as `RADEON_PACKET_TYPE0`, `RADEON_PACKET_TYPE3`, and `REG_SET`, plus MMIO/indirect access helpers. Register addresses and bitfields are SI-specific; they must not be reused for CIK or Sumo without verifying the register map. Many helpers shift values without full range validation, so call sites must mask, clamp, and respect ordering requirements for PLL changes, VM invalidation, CP packets, and DMA packets.

## Risks and test signals
The risk is high because a wrong address, mask, shift, or packet count can hang the GPU, misprogram clocks, corrupt VM translations, lose interrupts, break modesets, or corrupt copy/render/media command streams. Useful validation signals include SI probe and modeset, vblank/pflip/HPD interrupts, ring and IB tests, DMA copy tests, VM fault/invalidation tests, DPM transitions, suspend/resume, UVD decode, VCE encode, and register readback against known-good traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sislands_smc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sislands_smc.h

## Purpose
`sislands_smc.h` defines the packed firmware-facing data structures and helper prototypes used to configure Southern Islands SMC dynamic power management. It describes SMC state tables, DPM2 and PAPM power-limit state, clock/voltage performance levels, fan/CAC/DTE tables, memory-controller register tables, firmware header offsets, and the low-level SI SMC SRAM/message API.

## Important APIs, types, and definitions
- Packed SMC state structures: `SISLANDS_SMC_SCLK_VALUE`, `SISLANDS_SMC_MCLK_VALUE`, `SISLANDS_SMC_VOLTAGE_VALUE`, `SISLANDS_SMC_HW_PERFORMANCE_LEVEL`, `SISLANDS_SMC_SWSTATE`, `SISLANDS_SMC_SWSTATE_SINGLE`, and `SISLANDS_SMC_STATETABLE`.
- Power-control structures: `PP_SIslands_Dpm2PerfLevel`, `PP_SIslands_DPM2Status`, `PP_SIslands_DPM2Parameters`, `PP_SIslands_PAPMStatus`, and `PP_SIslands_PAPMParameters`.
- Thermal/fan/power-estimation tables: `PP_SIslands_FanTable`, `PP_SIslands_CacConfig`, and `Smc_SIslands_DTE_Configuration`.
- Memory-controller tables: `SMC_SIslands_MCRegisters`, `SMC_SIslands_MCRegisterAddress`, `SMC_SIslands_MCRegisterSet`, `SMC_SIslands_MCArbDramTimingRegisters`, and `SMC_SISLANDS_SPLL_DIV_TABLE`.
- Firmware layout constants: `SISLANDS_SMC_FIRMWARE_HEADER_LOCATION` and header offsets for soft registers, state table, fan table, CAC config, MC register tables, SPLL table, DTE configuration, and PAPM parameters.
- SMC access prototypes: `si_copy_bytes_to_smc`, `si_start_smc`, `si_reset_smc`, `si_program_jump_on_start`, `si_stop_smc_clock`, `si_start_smc_clock`, `si_is_smc_running`, `si_send_msg_to_smc`, `si_wait_for_smc_inactive`, `si_load_smc_ucode`, `si_read_smc_sram_dword`, and `si_write_smc_sram_dword`.

## Control flow and integration points
The header contains no executable implementation. `si_smc.c` implements the declared SRAM and message operations, while `si_dpm.c` and related SI power code populate these packed structures from AtomBIOS power tables and copy them into SMC SRAM. The SMC firmware then consumes the data asynchronously during DPM, fan, thermal, memory-clock, and voltage transitions.

## State and persistence behavior
The structures are CPU-side representations of persistent SMC SRAM state. Once written to the SMC, state tables, voltage masks, fan parameters, CAC/DTE parameters, SPLL dividers, and MC timing tables persist in firmware-owned memory until reloaded, reset, or overwritten. The prototypes mutate SMC clock/reset state, firmware code memory, and SMC mailbox state.

## Dependencies and constraints
The file includes `ppsmc.h` for message/result types and uses fixed-width integer types plus `struct radeon_device`. `#pragma pack(push, 1)` is central: any layout drift breaks the firmware ABI. The flexible-array `levels[]` in `SISLANDS_SMC_SWSTATE` is followed by a fixed `dpmLevels` backing array in `SISLANDS_SMC_STATETABLE`, so consumers must size and copy state tables carefully.

## Risks and test signals
Risks include endian/layout mismatches, incorrect level counts, bad voltage masks, out-of-bounds SMC SRAM copies, stale firmware-header offsets, and timing-table errors that can cause unstable clocks, memory corruption, fan failures, or SMC hangs. Test signals include SI DPM enable, SMC firmware load/start, SMC message acknowledgements, power-state transitions under load, fan response, memory-clock switching, thermal throttling, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sislands_smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7.h

## Purpose
`smu7.h` defines shared packed SMU7 firmware ABI primitives for Radeon CI/KV-era power management. It provides common limits, DPM state constants, scratch-register bit layouts, the PID-controller structure, feature/handshake masks, the SMU7 firmware header layout, and display PHY configuration IDs used by the discrete and fusion SMU7 table headers.

## Important APIs, types, and definitions
- Context IDs: `SMU7_CONTEXT_ID_SMC` and `SMU7_CONTEXT_ID_VBIOS`.
- DPM table capacities: maximum VDDC, VDDCI, MVDD, VDDNB, graphics, memory, GIO, PCIe link, UVD, VCE, ACP, SAMU, and SMIO entries.
- DPM action constants: `DPM_NO_LIMIT`, `DPM_NO_UP`, `DPM_GO_DOWN`, `DPM_GO_UP`, and first-level constants for graphics/memory.
- Scratch B bitfields track target/current PCIe, UVD, VCE, ACP, and SAMU indices.
- `SMU7_PIDController` defines firmware PID control parameters for activity-based DPM loops.
- Feature masks indicate which DPM domains and controllers are configured; handshake masks disable MCLK/SCLK handshakes for ACP, UVD, and VCE.
- `SMU7_Firmware_Header` records digest, version, code sizes, entry point, and SRAM offsets for soft registers, DPM table, fan table, CAC tables, MC tables, fuse table, globals, and signature.
- `enum DisplayConfig` enumerates display PHY modes such as power-down, DisplayPort lane/rate combinations, HDMI, and LVDS.

## Control flow and integration points
The header contains no functions. `smu7_discrete.h` and `smu7_fusion.h` include it to share constants and structures. CI and KV DPM code uses these definitions when loading SMU firmware, locating firmware tables, populating DPM table domains, and interpreting scratch-register state.

## State and persistence behavior
The definitions describe state persisted in SMU firmware memory and scratch registers. The CPU writes firmware headers, tables, PID parameters, feature masks, and enabled-level masks into SMU-visible memory; firmware uses them to control clocks, voltage rails, PCIe links, and media blocks until reset or table reload.

## Dependencies and constraints
The file relies on SMU enum constants such as `SMU__NUM_SCLK_DPM_STATE`, `SMU__NUM_MCLK_DPM_LEVELS`, `SMU__NUM_LCLK_DPM_LEVELS`, and `SMU__NUM_PCIE_DPM_LEVELS` being defined by the including context. The duplicate context-ID defines are harmless but should not diverge. Packed layout is required for firmware ABI compatibility.

## Risks and test signals
Incorrect capacities, firmware-header offsets, or scratch bit masks can make table uploads corrupt adjacent firmware memory or misreport active DPM states. Test signals include CI/KV SMU firmware load, DPM table upload/readback, enabled-level masks matching expected domains, media block clock changes, PCIe level transitions, and suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7_discrete.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7_discrete.h

## Purpose
`smu7_discrete.h` defines the packed SMU7 table ABI for discrete GPUs. It builds on `smu7.h` with soft registers, voltage rails, graphics/memory/PCIe/media DPM levels, ACPI and ULV states, MC timing/register tables, fan tables, and PM fuse data used by CI-family discrete Radeon power management.

## Important APIs, types, and definitions
- `SMU7_SoftRegisters` contains firmware runtime configuration including reference clock, PM timer, feature/handshake enables, display PHY config bytes, activity averages, enabled DPM level masks, DRAM log addresses, ULV controls, and training/voltage timing fields.
- Voltage and level structures: `SMU7_Discrete_VoltageLevel`, `SMU7_Discrete_GraphicsLevel`, `SMU7_Discrete_ACPILevel`, `SMU7_Discrete_Ulv`, `SMU7_Discrete_MemoryLevel`, `SMU7_Discrete_LinkLevel`, `SMU7_Discrete_UvdLevel`, and `SMU7_Discrete_ExtClkLevel`.
- `SMU7_Discrete_StateInfo` summarizes selected clock, voltage, watermark, MC, sequence, and PCIe indices for a state.
- `SMU7_Discrete_DpmTable` is the main firmware DPM table: PID controllers, system flags, SMIO masks, voltage-level arrays, level counts, graphics/memory/link/media levels, ULV state, intervals, boot levels, thermal limits, SVI/VR GPIO fields, package power limits, TDP targets, BAPM arrays, boot voltages, and low-SCLK interrupt threshold.
- MC tables: `SMU7_Discrete_MCArbDramTimingTable`, `SMU7_Discrete_MCRegisters`, and related address/set entries.
- `SMU7_Discrete_FanTable` and `SMU7_Discrete_PmFuses` encode fan response and board-specific leakage/load-line/TDC/fuzzy-fan/LPML fuse values.

## Control flow and integration points
This header has no code. `ci_dpm.h` includes it, and CI DPM code populates the structures from VBIOS powerplay tables, voltage/fuse tables, and board policy before copying them into SMU SRAM. Firmware uses the DPM table to perform activity, thermal, voltage, PCIe, and media clock transitions without host code in the fast path.

## State and persistence behavior
The structures become persistent SMU-owned table state after upload. DPM levels define durable target frequencies and voltage requirements; soft-register enabled-level masks, logging addresses, boot levels, intervals, thermal thresholds, and fuse values persist until table update, SMU reset, or firmware reload.

## Dependencies and constraints
The header requires `smu7.h` and the SMU level-count macros it references. `#pragma pack(push, 1)` is mandatory for binary compatibility. Array sizes must match firmware expectations; consumers must clamp counts to `SMU7_MAX_LEVELS_*`, endian-convert table fields where needed, and keep voltage phase/SMIO/fuse semantics aligned with the board design.

## Risks and test signals
Risks include table-size drift, bad level counts, wrong voltage minima or phase data, broken MC timing matrices, incorrect BAPM/fuse scaling, and invalid PCIe/media levels. Failures can appear as unstable clocks, black screens, memory errors, thermal runaway, fan misbehavior, or SMU crashes. Test signals include DPM table upload/readback, CI clock/voltage transitions, memory DPM stress, PCIe retraining, media playback/encode, fan and thermal tests, and overdrive/table-update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7_discrete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7_fusion.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7_fusion.h

## Purpose
`smu7_fusion.h` defines the packed SMU7 table ABI for Fusion/APU devices. It specializes the shared SMU7 model for integrated GPU and northbridge power management, covering graphics SCLK levels, GIO/LCLK levels, UVD/VCE/ACP/SAMU clocks, NB DPM policy, ACPI state, and the main APU DPM/GIO tables.

## Important APIs, types, and definitions
- Fusion constants set DTE dimensions for CPU/GPU/non-thermal entities and thermal sinks.
- `SMU7_SoftRegisters` carries common runtime configuration: reference clock, PM timer, feature/handshake enables, display PHY config bytes, activity averages, enabled DPM masks, DRAM log addresses, and ULV controls.
- Level structures: `SMU7_Fusion_GraphicsLevel`, `SMU7_Fusion_GIOLevel`, `SMU7_Fusion_UvdLevel`, `SMU7_Fusion_ExtClkLevel`, and `SMU7_Fusion_ACPILevel`.
- `SMU7_Fusion_NbDpm` encodes NB pstate ranges, PSI1, skip policy, hysteresis, and polling behavior.
- `SMU7_Fusion_StateInfo` summarizes selected SCLK, LCLK, media clocks, watermark, MC index, and clock indices.
- `SMU7_Fusion_DpmTable` holds system flags, graphics/GIO PID controllers, level counts, graphics/media levels, boot levels, sampling intervals, graphics slow-clock settings, CAC/low-SCLK thresholds, and DRAM log buffer addresses.
- `SMU7_Fusion_GIODpmTable` isolates GIO level data, PID controller, enable state, boot/target/current states, thermal throttle state, and temperature limits.

## Control flow and integration points
The header is declarative. `kv_dpm.h` includes it, and Kaveri/Sea Islands APU DPM code uses these structures to prepare firmware tables for the SMU. Runtime DPM decisions are then performed by firmware using the table data and host-provided enabled-level masks.

## State and persistence behavior
Uploaded Fusion tables persist in SMU firmware memory. They determine SCLK/LCLK/media clocks, NB voltage minima, GNB slow and forced-NB policies, thermal throttling limits, logging buffers, boot states, and activity-control parameters until the SMU is reset or the tables are rebuilt.

## Dependencies and constraints
The header depends on `smu7.h` and packed binary layout. It uses APU-specific voltage concepts such as VDDNB rather than the discrete VDDC/VDDCI/MVDD split. Callers must keep level counts within the fixed arrays, respect firmware ordering of graphics/GIO/media states, and populate bypass controls consistently with the SoC clock tree.

## Risks and test signals
Incorrect table contents can cause unstable APU SCLK/LCLK changes, broken UVD/VCE/ACP/SAMU clocks, bad NB pstate decisions, thermal throttling errors, or firmware table corruption. Test signals include KV DPM initialization, graphics and GIO clock transitions, media playback, ACPI low-power entry/exit, thermal throttle behavior, DRAM logging, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7_fusion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.c

## Purpose
`sumo_dpm.c` implements dynamic power management for Sumo/Palm APUs in the Radeon driver. It parses AtomBIOS integrated-system and PowerPlay tables, constructs Sumo-specific power-state data, programs SCLK DPM levels, voltage indices, deep-sleep dividers, GNB/NB policy, boost state, UVD clocks, thermal thresholds, and clock/power gating, and exposes the ASIC DPM callbacks registered in `radeon_asic.c`.

## Important APIs, types, and functions
- Public lifecycle callbacks: `sumo_dpm_init`, `sumo_dpm_setup_asic`, `sumo_dpm_enable`, `sumo_dpm_late_enable`, `sumo_dpm_disable`, `sumo_dpm_fini`.
- Power-state transition callbacks: `sumo_dpm_pre_set_power_state`, `sumo_dpm_set_power_state`, `sumo_dpm_post_set_power_state`, and `sumo_dpm_force_performance_level`.
- Query/debug callbacks: `sumo_dpm_get_sclk`, `sumo_dpm_get_mclk`, `sumo_dpm_get_current_sclk`, `sumo_dpm_get_current_mclk`, `sumo_dpm_get_current_vddc`, `sumo_dpm_print_power_state`, and `sumo_dpm_debugfs_print_current_performance_level`.
- Table helpers: `sumo_parse_sys_info_table`, `sumo_parse_power_table`, `sumo_parse_pplib_clock_info`, `sumo_parse_pplib_non_clock_info`, `sumo_construct_boot_and_acpi_state`, `sumo_construct_sclk_voltage_mapping_table`, `sumo_construct_vid_mapping_table`, and display-voltage table construction.
- Register programming helpers cover graphics/memory clock gating, graphics power gating, BSP/AT/TP/SSTP/VC timing, DPM level enable bits, SCLK dividers, VID fields, deep-sleep dividers, voltage scaling, ACPI/boot levels, thermal thresholds, and NB pstate forcing.
- SMU integration uses functions from `sumo_smc.c`: M3 arbiter initialization, power-gating initialization, boost timer setup, boost state enable, alt-VDDNB notification, TDP limit programming, and firmware version readback.

## Control flow
Initialization allocates `sumo_power_info`, sets conservative feature flags and Palm workarounds, parses the AtomBIOS integrated-system table revision 6, constructs SCLK/VID/display voltage maps, reads platform caps, parses PowerPlay states into `radeon_ps` plus `sumo_ps`, and enables DPM policy. ASIC setup initializes M3 arbiter data, reads SMC firmware version, programs ACPI SCLK/voltage, enables static ACPI PM, and hands display PHY control policy to the selected owner.

Enable programs boot state and BSP, resets/starts the activity monitor, programs trend parameters, activity thresholds, thermal throttling, DC timeout, voltage scaling, SSTP, VC, and CNB thermal overrides, starts SCLK DPM, waits for level 0, enables deep sleep, and initializes boost timer when supported. Late enable applies clock/power gating and thermal IRQ range setup. Disable reverses clock/power gating, deep sleep, VC, DPM enable, voltage scaling, and thermal IRQ state.

For power-state changes, `pre_set` copies the requested state and dynamically patches it for thermal states, boost/UI-performance states, battery/SD/HD NBPS1 forcing, minimum SCLK, deep-sleep dividers, and GNB slow policy. `set_power_state` sequences UVD clock changes relative to SCLK direction, disables boost, notifies alt-VDDNB when leaving forced NBPS1, forces level 0, programs new DPM levels, watermark/limit bits, BSP and activity thresholds, NB state, releases forced mode, sends post alt-VDDNB notifications, re-enables boost, and updates UVD clocks after SCLK changes if needed. `post_set` commits requested state as current.

## State and persistence behavior
Driver state lives in `rdev->pm.dpm.priv` as `struct sumo_power_info`, in allocated `rdev->pm.dpm.ps[]` entries with `struct sumo_ps` private data, and in cached `current_rps/current_ps` and `requested_rps/requested_ps`. Persistent hardware state is written through Sumo registers in `sumod.h`, including DPM level dividers, valid bits, VID fields, deep-sleep controls, thermal interrupt thresholds, clock/power gating, activity monitor timing, UVD clocks, and RCU boost/TDP registers. Parsed VBIOS data is copied into driver-owned structures and used across transitions until `sumo_dpm_fini` frees it.

## Dependencies and integration points
The implementation includes `radeon.h`, `radeon_asic.h`, `sumod.h`, `r600_dpm.h`, `cypress_dpm.h`, `sumo_dpm.h`, and `linux/seq_file.h`. It relies on AtomBIOS parsers, endian conversion helpers, Radeon MMIO macros, `r600_calculate_u_and_p`, UVD clock setup, thermal IRQ infrastructure, debugfs seq output, platform-cap parsing, and the ASIC callback table in `radeon_asic.c`.

## Risks and test signals
High-risk areas include VBIOS table revision assumptions, allocation cleanup on partial init failure, divider/VID bit programming, boost level 7 handling, forced-mode timing loops that do not report timeout errors, Palm power-gating workarounds, UVD clock ordering, and DPM state copies with private pointers. Test signals include Sumo/Palm boot with DPM enabled, debugfs current performance level, forced low/high/auto transitions, UVD playback while DPM changes, battery/performance/thermal PowerPlay states, thermal IRQ range programming, suspend/resume, and absence of SCLK/voltage stalls or GPU hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.h

## Purpose
`sumo_dpm.h` is the private Sumo DPM interface and state header. It defines Sumo power-level/power-state structures, BIOS-derived system information, persistent DPM private state, default timing constants, and cross-file prototypes shared by `sumo_dpm.c`, `sumo_smc.c`, Trinity/Sumo-adjacent code, and Radeon ASIC registration.

## Important APIs, types, and definitions
- `struct sumo_pl` describes one hardware power level: SCLK, VDDC index, deep-sleep and short-sleep divider IDs, GNB-slow permission, and SCLK DPM TDP limit.
- `struct sumo_ps` contains up to `SUMO_MAX_HARDWARE_POWERLEVELS` levels plus flags for forced NBPS1 and boost state.
- Mapping/system structures: display-clock voltage map, VID mapping table, SCLK voltage map, and `struct sumo_sys_info`, which stores boot/min clocks, UMA clock, NB voltage, HTC limits, M3 arbiter tables, boost/TDP margins, boost SCLK/VID, and boost enablement.
- `struct sumo_power_info` is the DPM private state with timing parameters, feature flags, firmware version, system info, boot/ACPI/boost levels, and cached current/requested Radeon/Sumo power states.
- Default timing constants configure UTC/DTC arrays, activity hysteresis, response limits, VC, clock-gating, voltage-drop, and power-gating timings.
- Prototypes expose Sumo DPM helpers such as clock-gating initialization, VC/SSTP programming, SMU control, mapping table constructors, VID conversion, sleep divider selection, and `sumo_get_pi`, plus SMC helper calls for M3 arbiter, PG init, TDP limit, alt-VDDNB notification, boost, timer, and firmware version.

## Control flow and integration points
The header has no executable control flow. It defines the shared contract between the Sumo DPM implementation and the Sumo SMU helper implementation. Radeon ASIC callback prototypes are also declared in `radeon_asic.h`, but this header carries the Sumo-private helpers used within the power-management subsystem.

## State and persistence behavior
The structures persist as driver heap state across the DPM lifecycle. `sumo_power_info` is allocated during `sumo_dpm_init`, referenced through `rdev->pm.dpm.priv`, updated during state transitions, and freed in `sumo_dpm_fini`. Its fields mirror persistent hardware and firmware state but are not themselves written to disk.

## Dependencies and constraints
The file includes `atom.h` and `radeon.h`, tying it to AtomBIOS table types and Radeon core structures. Counts are fixed: five normal hardware power levels, 15 trend-control entries, ten M3 arbiter parameter sets, and four voltage entries. Callers must not exceed those bounds when translating BIOS tables.

## Risks and test signals
Layout or semantic drift between this header and `sumo_dpm.c`/`sumo_smc.c` can break DPM state transitions, boost handling, or firmware notifications. Test signals include successful compile linkage, Sumo DPM init/enable/fini, PowerPlay table parsing, boost and forced NBPS1 transitions, debugfs output, and suspend/resume state restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_smc.c

## Purpose
`sumo_smc.c` implements Sumo/Palm SMU mailbox and RCU helper routines used by Sumo DPM. It sends service requests to the firmware, initializes M3 arbiter parameter tables, notifies firmware about alternate VDDNB policy, initializes graphics power gating, configures boost timer and TDP limits, toggles boost state, and reads the running firmware version.

## Important APIs and functions
- `sumo_send_msg_to_smu` is the internal mailbox routine. It waits for `INT_DONE`, writes `GFX_INT_REQ` with `SERV_INDEX(id) | INT_REQ`, waits for request/ack/done bits, then clears `INT_REQ`.
- `sumo_initialize_m3_arb` writes default, UVD, and fullscreen-3D M3 arbiter parameter sets into RCU/MCU parameter space when dynamic M3 arbiter support is enabled.
- `sumo_smu_notify_alt_vddnb_change` writes policy bits to `RCU_ALTVDDNB_NOTIFY` and sends the alt-VDDNB service request if the feature and firmware version support it.
- `sumo_smu_pg_init` sends the graphics power-gating initialization service request.
- `sumo_enable_boost_timer` derives a timer period from XCLK and the LCLK prescaler, writes boost/throttle/GNB/TDP margins, and sends SMU service id 20.
- `sumo_set_tdp_limit` updates 12-bit per-level TDP fields across `RCU_SclkDpmTdpLimit01`, `23`, and `47` for levels 0, 1, 2, 3, 4, and boost level 7.
- `sumo_boost_state_enable` clears or sets `RCU_GPU_BOOST_DISABLE` bit 0; `sumo_get_running_fw_version` reads `RCU_FW_VERSION`.

## Control flow and integration points
`sumo_dpm_setup_asic` initializes M3 arbiter data and reads firmware version. `sumo_gfx_powergating_initialize` calls `sumo_smu_pg_init` multiple times while staging RCU power-gating control fields. `sumo_dpm_enable` calls `sumo_enable_boost_timer` when boost is enabled. Runtime state changes call alt-VDDNB notifications around NBPS1 transitions, TDP programming for levels, and boost enable/disable when entering or leaving boost-capable states.

## State and persistence behavior
The file persists state in RCU/SMU hardware registers and firmware-visible parameter tables. M3 arbiter arrays are copied from `pi->sys_info`; boost and TDP values come from BIOS-derived `sumo_power_info`. Mailbox state is transient but firmware service effects persist until later SMU commands or reset.

## Dependencies and constraints
The implementation includes `radeon.h`, `sumod.h`, `sumo_dpm.h`, and `ppsmc.h`. It depends on `sumo_get_pi`, Radeon MMIO accessors, RCU accessors, `radeon_get_xclk`, `udelay`, `rdev->usec_timeout`, family IDs, and firmware version `>= 0x00010C00` for alt VDDNB on Sumo/Sumo2. The timeout loops do not return errors, so callers cannot distinguish success from late/missing firmware acknowledgement.

## Risks and test signals
Risks include silent SMU mailbox timeout, incorrect service IDs, bad TDP level-to-register mapping, boost timer overflow/scaling mistakes, firmware-version gating errors, and register alias confusion around RCU/MCU addresses. Test signals include SMC firmware version logging, successful DPM enable with power-gating init, boost entry/exit, battery/performance NBPS1 transitions, TDP limit readback, and absence of hangs in mailbox wait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumod.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumod.h

## Purpose
`sumod.h` is the Sumo/Palm register definition header for DPM, clock gating, graphics power gating, RCU/SMU communication, voltage scaling, deep sleep, thermal interrupts, and a few hardware revision/address-config registers. It is the hardware map used by `sumo_dpm.c` and `sumo_smc.c`.

## Important APIs, types, and definitions
- RCU/SMU registers: firmware version, power-gating sequence/control registers, alt-VDDNB notify, LCLK scaling control, boost disable, M3 arbiter parameter/index registers, boost/throttle margins, GNB/TDP limits, and PCIe power-gating args.
- Mailbox bits: `GFX_INT_REQ`, `SERV_INDEX`, `INT_REQ`, `GFX_INT_STATUS`, `INT_ACK`, and `INT_DONE`.
- SCLK and DPM controls: `CG_SCLK_CNTL`, `CG_SCLK_STATUS`, `SCLK_PWRMGT_CNTL`, profile index fields, `CG_SCLK_DPM_CTRL*`, valid/divider fields, forced-state bits, thermal throttle masks, DPM enable, GNB slow/forced NB pstate bits, and bootup state fields.
- Timing/activity registers: `CG_GCOOR`, `CG_FTV`, `CG_FFCT_0`, `CG_GIT`, `CG_SSP`, `CG_AT_*`, `CG_BSP_0`, and related field helpers.
- Voltage and power-gating controls: `CG_CG_VOLTAGE_CNTL`, `CG_ACPI_VOLTAGE_CNTL`, `CG_DPM_VOLTAGE_CNTL`, `CG_PWR_GATING_CNTL`, and associated enable, level, period/unit, and gating parameter fields.
- Deep-sleep and thermal controls: `DEEP_SLEEP_CNTL`, `DEEP_SLEEP_CNTL2`, `CG_THERMAL_INT`, high/low interrupt masks, and scratch/address-config registers.

## Control flow and integration points
The file has no functions. `sumo_dpm.c` uses these definitions to program clocks, voltage, DPM levels, thermal interrupts, and gating. `sumo_smc.c` uses them for RCU mailbox traffic, M3 arbiter tables, boost/TDP programming, and firmware version readback.

## State and persistence behavior
All definitions refer to hardware state. MMIO/RCU writes persist in the GPU/SMU until overwritten, gated, or reset. Many registers are updated in multi-step sequences: for example graphics power gating stages RCU sequence and timing registers around SMU service calls, while DPM transitions program level values before toggling valid bits and forced mode.

## Dependencies and constraints
Consumers must use the correct access path: some offsets are RCU-space and are accessed through `RREG32_RCU/WREG32_RCU`, while others are normal MMIO. The file notes an address overlap between `RCU_PWR_GATING_CNTL_5` and `MCU_M3ARB_INDEX` spaces and between boost/parameter offsets depending on access path, so accessors matter. Field macros do shifting but not validation.

## Risks and test signals
Misusing an offset, accessor, shift, or mask can corrupt DPM levels, voltage selection, thermal IRQ thresholds, boost/TDP limits, or firmware mailbox state. Test signals include Sumo DPM enable/disable, forced performance levels, boost transitions, thermal interrupt programming, power-gating entry/exit, RCU firmware version readback, and register readback during debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumod.h -->
