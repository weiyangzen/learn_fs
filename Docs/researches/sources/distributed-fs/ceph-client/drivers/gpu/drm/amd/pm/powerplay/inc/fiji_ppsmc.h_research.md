# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/fiji_ppsmc.h

## Purpose
`fiji_ppsmc.h` defines Fiji-era PowerPlay SMC protocol constants. It maps software state flags, thermal types, system flags, DPM state flags, return codes, SMC message IDs, event status bits, and the `PPSMC_Msg` typedef used by Fiji PM code.

## Important APIs, Types, and Functions
Important definitions include software state flags for DC/UVD/VCE, thermal-protect constants, GPIO/system flags, DPM2 flags, display watermark levels, hardware performance state flags, Gemini mode constants, `PPSMC_Result_*` values, and a large list of `PPSMC_MSG_*` IDs covering DPM control, power gating, CAC, voltage/thermal control, logging, BACO, I2C, AVFS, telemetry, and PSM commands. `typedef uint16_t PPSMC_Msg;` identifies command values passed to the SMC layer.

## Control Flow
The header has no executable control flow. ASIC-specific PM implementations use these macros to select firmware actions.

## State and Persistence
No runtime state is stored. The macros describe firmware commands and bit meanings that operate on firmware-managed state.

## Dependencies and Integration Points
It is a packed firmware ABI header for Fiji PowerPlay components. It integrates with generic SMC send helpers and ASIC-specific managers that need stable numeric command identifiers.

## Risks
The header contains many overlapping command names also present in other ASIC headers, but with potentially different numeric values. Incorrectly mixing Fiji and non-Fiji protocol constants is a high-risk firmware ABI bug. Comments note some temporary or legacy commands, so stale command support must be checked against firmware.

## Test Signals
Fiji hardware DPM, fan, thermal, BACO, voltage, and logging operations should complete without `UnknownCmd` or failed SMC responses. Compile boundaries should prevent conflicting message definitions from being used in the wrong ASIC path.
