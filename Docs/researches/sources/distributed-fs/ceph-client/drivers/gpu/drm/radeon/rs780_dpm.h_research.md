# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.h

## Purpose
`rs780_dpm.h` declares the private RS780/RS880 IGP DPM data model and default tuning constants used by `rs780_dpm.c`. It captures voltage-level enums, BIOS-derived power-info fields, per-power-state clock/voltage fields, feedback-divider/PWM defaults, clock-gating defaults, and fallback UVD clocks.

## Important APIs, Types, And Functions
The important types are `enum rs780_vddc_level`, `struct igp_power_info`, and `struct igp_ps`. `igp_power_info` holds feature flags, PWM/voltage limits, boot UMA clock, system config, active CRTC/refresh rate, and voltage timing values. `igp_ps` holds low/high SCLK, low/high voltage levels, and flags. The rest of the header is default constants for FVTHROT timing, PWM ranges, RS780D/RS880D feedback-divider ranges, slow-clock feedback, clock gating, and default UVD VCLK/DCLK.

## Control Flow
The header has no execution. `rs780_dpm.c` fills these structs during BIOS parsing, then uses the constants while initializing FVTHROT, voltage scaling, clock scaling, activity thresholds, and fallback UVD clocks.

## State, Persistence, And Dependencies
Instances of the structs persist as allocated DPM private state under `rdev->pm.dpm`. The constants become persistent hardware settings only after `rs780_dpm.c` writes the corresponding registers. The header depends on kernel integer and bool definitions already provided by including C files and on RS780 ATOM table semantics.

## Integration Points
This header is included only by the RS780 DPM implementation. Its struct layout is the bridge between ATOM PowerPlay/integrated-system-info parsing and later transition code. Its default constants pair with bitfield definitions in `rs780d.h`.

## Risks
Wrong defaults or struct interpretation can produce bad voltage/PWM ranges or unstable feedback-divider behavior. `RS880D_FVTHROTPWMFBDIVRANGEREG2_DFLT` uses mixed-case hex spelling but resolves correctly; any value changes must be validated on real hardware. If future BIOS revisions encode different units, the current fields would be insufficient.

## Test Signals
Test by parsing crev 1 and crev 2 integrated-system-info tables, enabling voltage and non-voltage-control paths, comparing programmed PWM/feedback-divider registers with expected defaults per device ID, verifying fallback UVD clocks for UVD states missing VCLK/DCLK, and checking forced/per-state SCLK behavior.
