# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu72_discrete.h

## Purpose
`smu72_discrete.h` specializes `smu72.h` for discrete boards. It defines the packed DPM table and companion tables used to program SMU72 discrete SCLK, MCLK, PCIe, UVD/VCE/ACP/SAMU, ULV, fan, fuse, CAC, logging, and power status behavior.

## Important APIs, Types, And Constants
- SMIO definitions `SMIO_Pattern` and `SMIO_Table` map voltage phases and VID patterns.
- Level structs include `SMU72_Discrete_GraphicsLevel`, `ACPILevel`, `Ulv`, `MemoryLevel`, `LinkLevel`, `UvdLevel`, and `ExtClkLevel`.
- `SMU72_Discrete_DpmTable` combines PID controllers, rail-level arrays, DPM level arrays, VR config, boot levels, intervals, SVI2/GPIO selectors, DTE/BAPM fields, TDP/power limits, ULV config, and display CAC.
- MC programming is represented by `SMU72_Discrete_MCRegisters`; MCARB timing is represented by `SMU72_Discrete_MCArbDramTimingTable`.
- Runtime and diagnostics include `SMU7_MclkDpmScoreboard`, `SMU7_UlvScoreboard`, `VddgfxSavedRegisters`, `SMU7_VddGfxScoreboard`, TDC/pkg power/BAPM/ACPI scoreboards, log header/control tables, CAC collection/verification tables, and PM status tables.

## Control Flow And Data Flow
Host code populates this file's tables from VBIOS, fuse data, and policy settings, then points the firmware to them through the SMU72 firmware header. Firmware consumes count fields and boot indices to move between DPM states, using hysteresis, activity thresholds, thermal clamps, voltage requests, and PCIe thresholds to choose target levels.

## State And Persistence
The structures are firmware-resident state. Fan tables and fuses derive from board-persistent sources, but once copied they are mutable runtime inputs. Scoreboards track live state such as current/target levels, clamp modes, residency counters, ULV/VddGfx transitions, and power-limit status.

## Dependencies And Integration Points
- Includes `smu72.h`; relies on its `SMU72_MAX_LEVELS_*`, `SMU72_PIDController`, voltage encodings, clock-gating masks, and firmware header.
- Integrated by SMU72/Tonga-family powerplay setup paths that upload discrete DPM and fan tables.
- Interacts with mailbox messages from `smu7_ppsmc.h` for feature enablement, table upload, fan control, and telemetry.

## Risks
- This is a packed binary ABI. Even renaming is harmless, but reordering or changing widths is not.
- DPM count fields and array dimensions must remain consistent; firmware likely trusts counts.
- Several shared structs are named `SMU7_*`, which can hide version-specific layout differences from casual readers.
- Log/CAC/PM status buffers include host/firmware addresses; wrong address programming can corrupt memory or produce bogus telemetry.

## Test Signals
- `sizeof(SMU72_Discrete_DpmTable)` and offsets should match firmware symbols.
- Runtime tests should exercise boot levels, SCLK/MCLK/PCIe transitions, fan table programming, CAC collection, VddGfx save/restore, and AC/DC GPIO clamp behavior.
