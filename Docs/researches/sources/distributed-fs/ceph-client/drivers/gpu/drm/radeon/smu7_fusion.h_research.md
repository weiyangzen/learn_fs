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
