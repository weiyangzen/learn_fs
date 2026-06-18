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
