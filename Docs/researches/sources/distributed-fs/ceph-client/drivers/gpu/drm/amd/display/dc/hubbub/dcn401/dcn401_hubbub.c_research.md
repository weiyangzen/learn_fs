# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.c

## Purpose

`dcn401_hubbub.c` implements DCN4.01 Hubbub support. It introduces DCN4-style A/B watermark programming, dual-plane address-v3 DCC capability calculation, segment-based DET/compbuf APIs, long DET update waits, and a DML2 arbiter hook for timeout and SDPIF rate-limit behavior.

## Important APIs, Types, And Functions

- CRB and segment helpers: `dcn401_init_crb`, `dcn401_program_det_segments`, `dcn401_program_compbuf_segments`, and `dcn401_wait_for_det_update`.
- Watermarks: `hubbub401_program_urgent_watermarks`, `hubbub401_program_stutter_watermarks`, `hubbub401_program_pstate_watermarks`, `hubbub401_program_usr_watermarks`, `hubbub401_program_watermarks`, `hubbub401_init_watermarks`, and `hubbub401_wm_read_state`.
- DCC capability: `hubbub401_dcc_support_swizzle`, `hubbub401_dcc_support_pixel_format`, `hubbub401_get_blk256_size`, `hubbub401_det_request_size`, and `hubbub401_get_dcc_compression_cap`.
- Arbiter: `dcn401_program_arbiter`.
- Lifecycle: `hubbub401_construct` and `hubbub4_01_funcs`.

## Control Flow

Construction installs `hubbub4_01_funcs`, stores context and register tables, and computes detile/pixel/CRB segment fields. CRB init reads DET0-DET3 and compbuf current segment counts and programs 64B reserved compbuf space.

Watermark programming uses `watermarks->dcn4x` rather than the older DCN3 fields. DCN4.01 programs only sets A and B for urgent, stutter, p-state, and USR values. Urgent watermarks include fractional MALL bandwidth and separate refcycles per metadata trip. Stutter programming mirrors A/B SR enter/exit values into three additional watermark tiers because dGPU Z states are not applicable. P-state programming includes UCLK/FCLK and TEMP_READ/PPT secondary watermark registers. The top-level function composes the phases, restores self-refresh based on debug `disable_stutter`, and applies USR force.

DCC flow first checks global disable and optional plane-width limits, clamps dimensions by format family, determines plane0/plane1 bytes per element, validates address-v3 swizzle/pitch support, computes whether 128B requests are needed for each plane and scan direction, then enables the most permissive valid DCC controls. Dual-plane formats evaluate luma and chroma separately and include P010 3:2 packing adjustment.

Segment programming writes DET size segments directly per HUBP and warns if DET plus compbuf segments exceed CRB capacity. Compbuf segment programming only grows when safe, waits for DET current values before growth, asserts capacity, and updates the cached segment count. DET update waiting can wait up to 100000 iterations, described as one vupdate at 10 Hz. `dcn401_program_arbiter` programs p-state stall threshold and bit 5 of `DCHUBBUB_HW_DEBUG` according to `allow_sdpif_rate_limit_when_cstate_req`, deferring unsafe lowers with `wm_pending`.

## State And Persistence Behavior

Cached state lives in `struct dcn20_hubbub`: watermark `dcn4x` fields, DET/compbuf segment sizes, detile/pixel/CRB values, and `allow_sdpif_rate_limit_when_cstate_req`. Hardware side effects include DCHUBBUB watermark, MALL bandwidth, metadata-trip, SR tier, p-state, USR, DET, compbuf, timeout, HW debug, SDPIF request-limit, self-refresh, and VM registers.

## Dependencies And Integration Points

The file depends on DCN30 and DCN401 headers, register helpers, DML2 arbiter register structs, DC DCC surface parameters, DC debug flags, inherited DCN2/DCN3 helpers, and DCN4 watermark union layout. It integrates with DCN4.01 resource construction, DML2 bandwidth/arbiter programming, plane validation for DCC, display init, and HWSS power/watermark sequencing.

## Risks And Edge Cases

- DCN4.01 supports only A/B watermark sets in this implementation; callers must not expect C/D fields to be programmed.
- DCC linear swizzle support requires `plane_pitch * bpe` to be 256-byte aligned.
- `hubbub401_det_request_size` assumes valid nonzero BPE values; unsupported formats must be filtered first.
- `DCC_HALF_REQ_DISALBE` is enforced only in the single-plane path, not the dual-plane path.
- `dcn401_program_arbiter` treats any lower `allow_sdpif_rate_limit_when_cstate_req` as pending when unsafe, even though it is a boolean-like field.
- Long DET waits can stall modeset/update paths on hardware that never applies the new current size.

## Test Signals

Test signals include DCN4.01 kernel builds, DML2 watermark/arbiter programming, DCC validation for single-plane, YUV420, P010, RGBE alpha, linear and 2D swizzles, plane-width-limit behavior, DET/compbuf segment warnings, DET apply wait completion, and readback of A/B watermarks plus SR tier registers.
