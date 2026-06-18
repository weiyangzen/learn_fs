<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_afmt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_afmt.c

## Purpose
`amdgpu_afmt.c` calculates HDMI audio clock regeneration values for amdgpu display code. It returns CTS/N timing values for 32 kHz, 44.1 kHz, and 48 kHz audio rates for a given pixel clock, using a table for common HDMI clocks and a fallback calculation for odd clocks.

## Important APIs, types, and functions
- `amdgpu_afmt_predefined_acr[]` stores known-good ACR values for common clocks such as 25.175 MHz, 27 MHz, 74.25 MHz, and 148.5 MHz, including 1000/1001 variants.
- `amdgpu_afmt_calc_cts()` computes CTS and N using GCD reduction and a multiplier chosen to avoid truncation.
- `struct amdgpu_afmt_acr amdgpu_afmt_acr(uint32_t clock)` is the exported helper declared in `amdgpu.h`.
- The return type stores the clock and CTS/N pairs for 32 kHz, 44.1 kHz, and 48 kHz.

## Control flow
`amdgpu_afmt_acr()` scans the predefined table and returns an exact match when the pixel clock is known. If no entry matches, it calls `amdgpu_afmt_calc_cts()` three times for 32000, 44100, and 48000 Hz, then fills `res.clock`.

The fallback starts with safe but large values, reduces the fraction by `gcd(n, cts)`, computes a multiplier based on the ideal `128 * freq / 1000` target, scales N and CTS, warns if N is outside the HDMI spec range, and returns the computed values.

## State and persistence behavior
The file has no mutable state. The predefined table is static const, and calculated results are returned by value. No persistent state or hardware programming happens here.

## Dependencies and integration points
The file depends on Linux HDMI definitions, `gcd()`, DRM debug logging, and the `struct amdgpu_afmt_acr` declaration in `amdgpu.h`. Display encoder code calls `amdgpu_afmt_acr()` before programming HDMI/AFMT audio timing registers.

## Risks and edge cases
The fallback calculation can produce values outside spec for unusual clocks; it warns but still returns a value. The predefined table must remain authoritative for common CEA clocks because small arithmetic differences can affect HDMI audio compatibility. The clock unit is kHz, and mixing Hz/kHz units would produce invalid CTS values.

## Test signals
Good signals include correct HDMI audio at common display modes, no warnings for predefined clocks, expected warnings for truly odd pixel clocks, and register programming that matches HDMI compliance values. Unit-style tests can compare table lookups and known fallback calculations for selected non-table clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_afmt.c -->
