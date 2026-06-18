# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.c

## Purpose

`dcn35_hubbub.c` implements DCN3.5 Hubbub behavior by reusing much of DCN3.2 and adding DCN3.5-specific CRB depth, Z8 stutter watermarks, reference-clock bring-up handling, QoS/DF threshold programming, fine-grain clock gating control, and DCHVM/RIOMMU initialization.

## Important APIs, Types, And Functions

- CRB helpers: `dcn35_init_crb` and `dcn35_program_compbuf_size`.
- Watermark helpers: `hubbub35_program_stutter_z8_watermarks`, `hubbub35_program_watermarks`, `hubbub35_init_watermarks`, and `hubbub35_wm_read_state`.
- Clock/init helpers: `hubbub35_get_dchub_ref_freq`, `hubbub35_set_fgcg`, `hubbub35_init`, and `dcn35_dchvm_init`.
- Lifecycle: `hubbub35_construct` and `hubbub35_funcs`.

## Control Flow

Construction assigns the DCN3.5 function table, stores register table pointers, sets debug p-state index `0xB`, and computes detile, pixel-chunk, and CRB segment sizes with 64 KiB segments.

CRB initialization reads DET0-DET3 and compbuf current sizes, programs reserved compbuf space for 64B and ZS chunks, and sets DET depth to `0x5FF`. Compbuf programming follows the DCN3.x pattern: only grow when safe, wait for DET current values before growth, assert total CRB capacity, update the compbuf register, cache the segment count, and check `CONFIG_ERROR`.

Watermark programming calls DCN3.2 urgent, stutter, p-state, and USR helpers, then programs DCN3.5 Z8 stutter enter/exit watermarks for sets A-D. It writes saturation and DF outstanding thresholds, sets host VM QoS commit threshold, optionally restores self-refresh, and applies the debug USR force. Watermark initialization and readback copy/read all normal, UCLK/FCLK, USR, and Z8 sets.

`hubbub35_get_dchub_ref_freq` reads global timer refdiv/enable and returns 24 MHz or 12 MHz; if disabled, it programs refdiv/enable as a bring-up workaround and asserts critical. `hubbub35_init` applies debug clock-gate disables, sets fine-grain clock gating from debug flags, gives SDPIF control to DC, sets max outstanding to 256, programs DF outstanding limits, and clears cached p-state watermark state for set A. `dcn35_dchvm_init` requests HOSTVM init, polls RIOMMU active, disables memory/clock gating while prefetching, requests RIOMMU prefetch, waits for completion, restores gating, and marks `hubbub->riommu_active`.

## State And Persistence Behavior

State is cached in `struct dcn20_hubbub` and `struct hubbub`: DET/compbuf segment sizes, watermark caches, detile/pixel/CRB sizes, debug p-state index, and `riommu_active`. Hardware side effects include DCHUBBUB watermarks, DF/QoS thresholds, SDPIF controls, clock gates, compbuf/DET registers, global timer enable/refdiv, DCHVM/RIOMMU registers, and self-refresh/USR force controls.

## Dependencies And Integration Points

The file includes DCN30, DCN31, DCN32, and DCN35 headers plus register helpers. It integrates with DCN3.5 resource construction, DML bandwidth programming, DCHVM host-VM startup, power management, fine-grain clock gating debug policy, and inherited DCC/VM/watermark support.

## Risks And Edge Cases

- `hubbub35_program_stutter_z8_watermarks` ignores `safe_to_lower` for set A enter, unlike most other watermark fields.
- Reference-clock disabled handling both mutates hardware and asserts critical; this is useful for bring-up but noisy if a platform intentionally starts disabled.
- DCHVM init silently leaves `riommu_active` false after 100 polling attempts; callers must tolerate inactive host VM acceleration.
- The commented-out request-limit implementation means DCN3.5 does not expose a request-limit callback in the function table.
- `hubbub35_init` clears only set A `cstate_pstate` cached state, which could interact with later safe-to-lower comparisons.

## Test Signals

Signals include successful DCHVM init with `riommu_active`, HOSTVM prefetch completion, watermark readback including Z8 fields, DF/QoS threshold register values, fine-grain clock-gating toggles, global timer enable/refdiv state, compbuf config-error assertions, and display power-management tests covering stutter, Z8, UCLK/FCLK, and USR behavior.
