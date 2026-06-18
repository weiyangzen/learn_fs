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
