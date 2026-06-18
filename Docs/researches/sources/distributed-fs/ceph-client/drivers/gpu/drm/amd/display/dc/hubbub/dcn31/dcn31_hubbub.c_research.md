# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.c

## Purpose

`dcn31_hubbub.c` implements DCN3.1 Hubbub behavior. It programs configurable return buffer resources, watermarks, DCC capability limits, VM aperture/VMID setup, DCHUB reference clock reporting, p-state allow verification, and basic Hubbub initialization. It installs these operations through a DCN3.1 `struct hubbub_funcs`.

## Important APIs, Types, And Functions

- CRB/DET helpers: `dcn31_init_crb`, `dcn31_program_det_size`, `dcn31_wait_for_det_apply`, and `dcn31_program_compbuf_size`.
- Watermark helpers: `convert_and_clamp`, `hubbub31_program_urgent_watermarks`, `hubbub31_program_stutter_watermarks`, `hubbub31_program_pstate_watermarks`, and `hubbub31_program_watermarks`.
- DCC helpers: `hubbub3_get_blk256_size`, `hubbub31_det_request_size`, and `hubbub31_get_dcc_compression_cap`.
- VM and clock helpers: `hubbub31_init_dchub_sys_ctx`, `hubbub31_get_dchub_ref_freq`, and `hubbub31_verify_allow_pstate_change_high`.
- Public lifecycle: `hubbub31_init` and `hubbub31_construct`.
- `hubbub31_funcs`: function table selecting the DCN3.1 implementations and inherited DCN1/DCN2/DCN3 helpers.

## Control Flow

`hubbub31_construct` first calls `hubbub3_construct`, then replaces the function table with `hubbub31_funcs`, stores byte-sized DET/pixel chunk values, computes CRB segment capacity using 64 KiB segments, and sets p-state debug index `0x6`.

CRB initialization reads current DET0-DET3 and compbuf segment counts from hardware, programs reserved compbuf space from `pixel_chunk_size`, and sets debug DET depth. DET programming rounds requested KiB up to 64 KiB segments, writes the per-HUBP DET register, updates cached segment counts, and asserts that all DET plus compbuf segments fit within `crb_size_segs`. Compbuf growth waits for all current DET sizes to apply before increasing the compbuf register.

Watermark programming follows a safe-to-lower policy. Each set A-D is updated immediately when `safe_to_lower` is true or the new value is higher than the cached value; lower unsafe values leave hardware unchanged and return `wm_pending = true`. Urgent programming handles urgency, fractional urgent flip/nominal bandwidth, and refcycles per trip. Stutter programming handles normal and Z8 self-refresh enter/exit watermarks. P-state programming handles DRAM clock change watermarks. `hubbub31_program_watermarks` composes those helpers and toggles self-refresh according to `disable_stutter`.

DCC capability calculation validates global DCC debug policy, pixel format support, swizzle support, and detile-buffer request sizing. It picks a DCC control mode based on scan direction, segment order, 128B request need, and a 64KB_R_X exception, then fills the RGB DCC capability fields.

VM setup writes framebuffer and AGP aperture registers, initializes VMID 0 and VMID 15 from GART config when present, invokes optional DCHVM init, and returns `NUM_VMID` as 16. P-state verification polls a debug bit for up to 100 us; on timeout it forces allow-pstate-change high to avoid a hang and logs the debug data.

## State And Persistence Behavior

The file maintains cached hardware state in `struct dcn20_hubbub`: DET segment sizes, compbuf segment size, watermark values, `detile_buf_size`, `pixel_chunk_size`, `crb_size_segs`, and `debug_test_index_pstate`. It writes VM aperture, watermark, DET, compbuf, clock, SDPIF, DCHVM, and p-state force registers. Static locals in `hubbub31_verify_allow_pstate_change_high` retain the last forced-pstate workaround and max sampled wait across calls.

## Dependencies And Integration Points

It depends on DCN3/DCN3.1 headers, `dm_services.h`, `reg_helper.h`, `struct hubbub`, `struct dcn20_hubbub`, `union dcn_watermark_set`, DCC surface types, VMID setup from DCN2, and inherited DCN1/DCN2/DCN3 helpers. It integrates with DML bandwidth output, DC resource construction, plane validation/DCC capability checks, HWSS watermark propagation, DCHVM initialization, and display init sequencing.

## Risks And Edge Cases

- The p-state watermark state B lower path sets `wm_pending = false` rather than true, unlike the other states, which can hide a pending unsafe lower.
- `convert_and_clamp` asserts on watermark overflow and clamps; bad DML inputs may mask underflow risk after the assert.
- DET and compbuf sizing depends on cached segment counts matching hardware current registers.
- Unsupported `bytes_per_element` in block-size calculation leaves zero dimensions and can corrupt DCC request decisions if upstream pixel-format filtering fails.
- P-state verification forces a hardware override on timeout; that is a hang-avoidance workaround with power-management side effects.
- DCC capability only fills RGB capability fields and assumes the input is not a dual-plane DCN4-style case.

## Test Signals

Build tests catch register field and callback mismatches. Runtime signals include successful init with 16 VMIDs, CRB config assertions or warnings, DCC capability results across swizzles/formats/scan directions, bandwidth logs for A-D watermarks, p-state warning logs, self-refresh state changes, and no stalls in DET apply waits or p-state polling.
