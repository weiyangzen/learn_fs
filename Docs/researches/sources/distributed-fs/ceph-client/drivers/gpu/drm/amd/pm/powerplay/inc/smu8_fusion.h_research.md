# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu8_fusion.h

## Purpose
`smu8_fusion.h` defines SMU8 fusion/APU-specific packed tables. It focuses on compute-unit power gating, port 80 monitoring, power-management separation settings, and clock breakdown tables for SCLK, LCLK, UVD, VCE/ECLK, ACP/ACLK, and related clocks.

## Important APIs, Types, And Constants
- CU constants: `SMU8_MAX_CUS`, `SMU8_PSMS_PER_CU`, and `SMU8_CACS_PER_CU`.
- `SMU8_GfxCuPgScoreboard` models graphics CU power-gating state.
- `SMU8_Port80MonitorTable` stores port 80 monitor values.
- `PWRMGT_*` shift/mask constants encode separation time and CPU C-state/P-state disable flags.
- Clock level counts include `NUM_SCLK_LEVELS`, `NUM_LCLK_LEVELS`, `NUM_UVD_LEVELS`, `NUM_ECLK_LEVELS`, and `NUM_ACLK_LEVELS`.
- `SMU8_Fusion_ClkLevel` and the SCLK/LCLK/ECLK/VCLK/DCLK/ACLK breakdown table structs are grouped by `SMU8_Fusion_ClkTable`.

## Control Flow And Data Flow
The driver or firmware fills clock breakdown arrays with frequency/divider data. Firmware uses the clock tables to select operating points for graphics, memory/GIO, and multimedia blocks. Power-management mask fields influence CPU state separation behavior on the APU.

## State And Persistence
Tables are volatile packed firmware-memory structures. Clock data may be derived from firmware/VBIOS policy but is represented here as runtime tables. Port 80 and CU PG scoreboards are runtime status/control structures.

## Dependencies And Integration Points
- Includes `smu8.h` for firmware header and address constants.
- Integrates with SMU8 APU powerplay setup, CU power gating, multimedia clock selection, and CPU power-state coordination.

## Risks
- Fixed level counts require producers to avoid overflow and fill unused entries deterministically.
- CPU P-state/C-state disable masks affect platform-wide power behavior.
- CU PG constants are small and platform-specific; using them for larger GPU configurations would be wrong.

## Test Signals
- Runtime clock table reads match expected frequencies for SCLK/LCLK/UVD/VCE/ACP.
- CU power-gating scoreboard changes with workload/idleness.
- CPU power-state coordination does not regress suspend/resume or multimedia playback.
