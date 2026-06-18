# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.c

## Purpose
`dcn21_dccg.c` implements the DCN 2.1 DCCG variant. It customizes DPP DTO programming for DMCUB power-saving semantics and preserves an S0i3 golden-init workaround marker during initialization.

## Important APIs And Functions
`dccg21_update_dpp_dto` computes DTO modulo as `ref_dppclk / 10000` and phase as ceiling `req_dppclk / 10000`. If phase exceeds modulo it clamps to modulo to avoid corruption. If `req_dppclk` is zero, it sets phase to 10 and still enables the DTO to divide down unused pipe clock for power saving and to avoid hard hangs when accessing unused DPP registers. It writes phase/modulo and enables DTO when `ref_dppclk` is present, then records `pipe_dppclk_khz`.

`dccg21_init` checks `dccg2_is_s0i3_golden_init_wa_done`; if the BIOS marker is present, it skips `dccg2_init` so later BIOS golden init workaround logic can see the marker. Otherwise it calls DCN2 init.

`dccg21_funcs` reuses most DCN2 functions with the DCN21 DTO and init overrides. `dccg21_create` allocates and initializes the DCCG object and table pointers.

## Control Flow And State
Runtime state is the shared `struct dcn_dccg`, plus cached per-pipe DPP clocks. The key control branches are ref_dppclk availability, requested DPP clock zero/nonzero, phase clamp, and S0i3 marker detection.

## Dependencies And Integration Points
It includes `reg_helper.h`, `core_types.h`, `dcn20/dcn20_dccg.h`, and `dcn21_dccg.h`. It integrates with DCN21 clock programming, DMCUB runtime clock lowering, BIOS golden init, and S0i3 resume paths.

## Risks
The modulo calculation can become zero if `ref_dppclk` is below 10 MHz, which would make phase clamping and register programming invalid; platform assumptions likely prevent this. The zero-request path intentionally leaves DTO enabled, which differs from DCN2. Skipping init on S0i3 marker relies on later BIOS logic to handle needed initialization.

## Test Signals
DCN21 mode sets, unused-pipe DPP access after DTO programming, DMCUB power-saving clock lowering, S0i3 resume with marker preserved, and phase/modulo boundary modes such as high-pixel-clock HDMI are key signals.
