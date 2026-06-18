# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.c

## Purpose

`dcn32_hubbub.c` implements DCN3.2 Hubbub programming. It extends DCN3.1-style CRB and watermark handling with SDPIF request-rate controls, UCLK/FCLK split p-state watermarks, USR retraining watermarks and force control, MALL status reporting, and DCN3.2-specific init behavior.

## Important APIs, Types, And Functions

- CRB and request controls: `dcn32_init_crb`, `hubbub32_set_sdp_control`, `hubbub32_set_request_limit`, `dcn32_program_det_size`, and `dcn32_program_compbuf_size`.
- Watermarks: `hubbub32_program_urgent_watermarks`, `hubbub32_program_stutter_watermarks`, `hubbub32_program_pstate_watermarks`, `hubbub32_program_usr_watermarks`, `hubbub32_program_watermarks`, `hubbub32_init_watermarks`, and `hubbub32_wm_read_state`.
- Runtime controls: `hubbub32_force_usr_retraining_allow`, `hubbub32_force_wm_propagate_to_pipes`, `hubbub32_get_mall_en`, and `hubbub32_init`.
- Lifecycle: `hubbub32_construct` and `hubbub32_funcs`.

## Control Flow

Construction directly initializes the Hubbub object, installs `hubbub32_funcs`, records register tables, sets p-state debug index `0xB`, stores detile and pixel-chunk sizes, and computes CRB segment capacity with 64 KiB segments.

CRB init reads current DET/compbuf segment state, programs compbuf reserved space, and uses a larger debug DET depth than DCN3.1. DET programming rounds KiB to segments and writes per-HUBP DET registers; if the sum exceeds CRB capacity, it logs a warning instead of immediately asserting because seamless ODM transitions can temporarily overcommit. Compbuf growth waits for DET current registers and asserts capacity before programming.

Watermark flow is split into urgent, stutter, p-state, and USR phases. Urgent programming is similar to DCN3.1. Stutter watermarks program normal SR enter/exit for sets A-D with 16-bit clamp values. P-state programming writes UCLK and FCLK watermark registers separately. USR programming writes retraining watermarks for sets A-D. The top-level `hubbub32_program_watermarks` optionally disables stutter and hands SDPIF control to DF before unsafe watermark raises on selected GC 11.0.0/11.0.3 revisions, restores self-refresh and SDPIF ownership after safe lowering, and enforces the debug `force_usr_allow` value.

Initialization sets optional clock-gate disables, gives SDPIF control to DC, sets max outstanding SDPIF requests to 512, and programs min/max DF outstanding requests to 512. MALL status reads `MALL_IN_USE` and `MALL_PREFETCH_COMPLETE` and reports true only when both are set.

## State And Persistence Behavior

The file caches DET, compbuf, watermark, request-limit, detile, pixel-chunk, and CRB segment state in `struct dcn20_hubbub`. It mutates hardware registers for watermarks, SDPIF control and outstanding requests, DCHUBBUB request limits, USR force, MALL status reads, clock gates, and self-refresh control. There is no file persistence.

## Dependencies And Integration Points

It depends on DCN30/DCN32 headers, `dm_services.h`, `reg_helper.h`, ASIC revision helpers from `dal_asic_id.h`, inherited Hubbub helpers, DML-generated `union dcn_watermark_set`, and DC debug flags. It integrates with display init, bandwidth/watermark programming, MALL/SubVP checks, power management, and resource construction for DCN3.2 ASICs.

## Risks And Edge Cases

- `hubbub32_set_request_limit` comments say the field is 24 bits, but the code clamps/asserts against `0xFFF`; hardware field width should be verified.
- Request-limit inputs that compute zero skip programming after an assertion, leaving old hardware state.
- Watermark lowering while `safe_to_lower` is false depends on `wm_pending` being honored by callers.
- SDPIF handoff for `disable_stutter_for_wm_program` is ASIC-revision gated; new revisions needing the workaround must be added explicitly.
- Init comments note zero frame buffer mode must restore outstanding limits, but this file only programs the normal mode values.
- DET overcommit is only warned in `dcn32_program_det_size`; compbuf programming still asserts on over-capacity.

## Test Signals

Useful tests include kernel builds, register-table coverage, CRB programming during ODM changes, watermark raise/lower sequencing, USR force toggling, GC 11.0.0/11.0.3 stutter-disable handoff, MALL prefetch/in-use status reads, zero frame buffer mode transitions, and bandwidth log validation for urgent, stutter, UCLK, FCLK, and USR sets.
