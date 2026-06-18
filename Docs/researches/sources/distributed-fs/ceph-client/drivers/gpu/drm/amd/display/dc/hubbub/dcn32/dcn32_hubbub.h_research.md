# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.h

## Purpose

`dcn32_hubbub.h` declares the DCN3.2 Hubbub field map and exported helper prototypes. It expands DCN3-era Hubbub coverage with global timer enable, soft reset, watermark-change control, request limiting, USR retraining, UCLK/FCLK p-state watermarks, SDPIF controls, MALL status fields, and CRB/DET/compbuf fields.

## Important APIs, Types, And Functions

- `HUBBUB_MASK_SH_LIST_DCN32(mask_sh)` lists all field masks and shifts needed by DCN3.2 Hubbub C code, including self-refresh/p-state force, request outstanding limits, urgent watermarks, VM aperture, DET/compbuf, USR retraining, UCLK/FCLK p-state, VM fault status, SDPIF rate/max outstanding, memory power, and MALL status.
- Exported functions include `hubbub32_program_urgent_watermarks`, `hubbub32_program_stutter_watermarks`, `hubbub32_program_pstate_watermarks`, `hubbub32_program_usr_watermarks`, `hubbub32_force_usr_retraining_allow`, `hubbub32_force_wm_propagate_to_pipes`, `hubbub32_init`, `dcn32_program_det_size`, `dcn32_program_compbuf_size`, `hubbub32_set_request_limit`, `hubbub32_get_mall_en`, and `hubbub32_construct`.

## Control Flow

The header has no runtime control flow. It enables generation-specific C files to build a `hubbub_funcs` table and exposes helpers reused by later DCN35/DCN42 implementations.

## State And Persistence Behavior

No state is persisted here. The declared helpers update cached `struct dcn20_hubbub` watermarks and CRB segment fields and write DCHUBBUB registers at runtime.

## Dependencies And Integration Points

It includes `dcn21/dcn21_hubbub.h`. It is consumed by DCN3.2 resource construction and later-generation files that reuse DCN3.2 watermark, DET, request-limit, MALL, and USR helpers.

## Risks And Edge Cases

- This header declares only a mask/shift list, so the matching register list must come from ASIC-specific resource files or inherited macros; mismatches break `REG_*` access.
- Later generations reuse prototypes from this header but may have different register semantics.
- MALL and USR fields are optional by hardware generation; function-table selection must match field availability.

## Test Signals

Compile-time macro expansion is the first signal. Runtime tests should exercise USR retraining, UCLK/FCLK watermarks, MALL status reads, SDPIF rate-limit programming, DET/compbuf programming, VM faults, and self-refresh/p-state force controls.
