# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.c

## Purpose

`dcn42_hubbub.c` implements DCN4.2 Hubbub support. It reuses many DCN3.5 and DCN4.01 helpers but restores A-D watermark programming, adds DCN4.2-specific self-refresh semantics, fixed SDPIF request-limit programming, and an arbiter variant where p-state stall threshold is left to firmware.

## Important APIs, Types, And Functions

- Watermark helpers: `hubbub42_program_urgent_watermarks`, `hubbub42_program_stutter_watermarks`, `hubbub42_program_pstate_watermarks`, `hubbub42_program_usr_watermarks`, `hubbub42_program_stutter_z8_watermarks`, and `hubbub42_program_watermarks`.
- Runtime controls: `hubbub42_allow_self_refresh_control`, `hubbub42_set_sdp_control`, `hubbub42_set_request_limit`, and `dcn42_program_arbiter`.
- Lifecycle: `hubbub42_construct` and `hubbub42_funcs`.

## Control Flow

Construction initializes the Hubbub object, installs `hubbub42_funcs`, stores register tables, and computes detile, pixel-chunk, and CRB segment counts with 64 KiB segments.

Top-level watermark programming optionally hands SDPIF control to DF and disables self-refresh before unsafe watermark raises when `disable_stutter_for_wm_program` is set. It then programs urgent, stutter, UCLK/FCLK p-state, USR, and Z8 stutter watermarks for sets A-D using `watermarks->dcn4x`. It writes saturation and DF/QoS thresholds, restores self-refresh when safe or forced by debug settings, restores SDPIF control after safe lowering, and applies USR force.

`hubbub42_allow_self_refresh_control` differs from the inherited helper by forcing value 0 and enabling the force bit only when self-refresh should be disallowed. `hubbub42_set_request_limit` ignores memory-channel inputs and programs a fixed `SDPIF_REQUEST_RATE_LIMIT` value of 96. `dcn42_program_arbiter` mirrors DCN4.01 bit-5 debug handling for `allow_sdpif_rate_limit_when_cstate_req` but intentionally does not program the p-state stall threshold because firmware handles it.

The function table reuses DCN31 VM sys-context init, older DCC support (`hubbub3_get_dcc_compression_cap`), DCN35 watermark read/init/refclock and DCHVM init, and DCN401 segment CRB helpers.

## State And Persistence Behavior

The file updates cached DCN4x watermark fields for sets A-D, `allow_sdpif_rate_limit_when_cstate_req`, detile/pixel/CRB sizes, and inherited DET/compbuf caches. It writes DCHUBBUB watermark, p-state, USR, Z8, self-refresh force, SDPIF control/rate-limit, DF outstanding, QoS, debug, DET/compbuf, DCHVM, and VM registers through reused helpers.

## Dependencies And Integration Points

It depends on DCN30, DCN31, DCN32, DCN35, DCN401, and DCN42 headers, plus register helpers. It integrates with DCN4.2 resource construction, DML/DML2 watermark and arbiter programming, power management, DCHVM init, older DCC validation paths, and DC debug stutter/USR controls.

## Risks And Edge Cases

- The fixed SDPIF request limit of 96 ignores topology and memory-channel parameters; platforms with different fabric characteristics need validation.
- The function table uses older DCC helpers rather than DCN401 address-v3 two-plane DCC helpers; this must match DCN4.2 hardware/register expectations.
- `dcn42_program_arbiter` does not program p-state stall threshold, so firmware availability becomes part of correctness.
- The top-level watermark path marks pending before unsafe raises when stutter-for-WM is disabled, even if all later writes succeed; callers must interpret this consistently.
- Self-refresh force semantics differ from inherited helpers and should be tested with debug `disable_stutter` and normal stutter transitions.

## Test Signals

Runtime tests should cover A-D urgent/stutter/UCLK/FCLK/USR/Z8 watermarks, stutter disable during unsafe raises, SDPIF control restoration after safe lowering, fixed request-limit register value, firmware-owned p-state stall behavior, DCHVM init, DCN401 segment DET/compbuf helpers, and inherited DCC capability behavior on DCN4.2 surfaces.
