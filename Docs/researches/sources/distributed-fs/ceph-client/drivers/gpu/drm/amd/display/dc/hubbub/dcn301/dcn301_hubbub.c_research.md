# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.c

## Purpose

`dcn301_hubbub.c` constructs the DCN3.01 Hubbub object. It is intentionally small: it selects a DCN3.01 `hubbub_funcs` table that mostly reuses DCN2/DCN2.1/DCN3 helpers, wires register/mask/shift tables into `struct dcn20_hubbub`, and sets the generation-specific p-state debug index and detile-buffer size.

## Important APIs, Types, And Functions

- `hubbub301_funcs`: static `struct hubbub_funcs` table. It maps core operations to `hubbub2_update_dchub`, `hubbub21_init_dchub`, `hubbub2_init_vm_ctx`, `hubbub3_dcc_support_swizzle`, `hubbub2_dcc_support_pixel_format`, `hubbub3_get_dcc_compression_cap`, `hubbub21_wm_read_state`, `hubbub2_get_dchub_ref_freq`, `hubbub3_program_watermarks`, self-refresh/p-state helpers, watermark propagation, watermark init, and `hubbub2_read_state`.
- `hubbub301_construct(...)`: exported constructor that initializes context, function table, register table pointers, masks, shifts, `debug_test_index_pstate`, and `detile_buf_size`.

## Control Flow

Construction is linear. The caller provides prebuilt register/mask/shift tables. `hubbub301_construct` stores the context and table pointers, assigns `&hubbub301_funcs` to `hubbub3->base.funcs`, sets `debug_test_index_pstate` to `0xB`, and fixes the detile buffer size at 184 KiB. All later runtime behavior is dispatched through the function table to inherited helpers.

## State And Persistence Behavior

The file mutates only the in-memory Hubbub object during construction. Persistent effects happen later through the installed callbacks, which program DCHUB, VM context, watermarks, self-refresh, p-state force, and DCC capability outputs. There is no on-disk persistence.

## Dependencies And Integration Points

The implementation includes `dm_services.h`, `dcn301_hubbub.h`, and `reg_helper.h`, and it depends on inherited helpers from DCN1, DCN2, DCN2.1, and DCN3. It integrates with the resource pool constructor for the DCN3.01 ASIC path and with hardware sequencing through `struct hubbub_funcs`.

## Risks And Edge Cases

- The function table deliberately mixes generations; a helper that assumes different register availability would fail only at runtime unless covered by build-time register tables.
- `hubbub21_init_dchub` is selected rather than the DCN3 sys-context init helper, so DCN3.01 VM/HVM behavior depends on the header-supplied register list and inherited DCN2.1 expectations.
- `detile_buf_size` is hard-coded to 184 KiB, so DCC capability decisions rely on that value matching hardware.
- The duplicated `REG`, `CTX`, and `FN` macro definitions are harmless but increase maintenance noise.

## Test Signals

Compile tests catch missing callback symbols and struct layout drift. Runtime validation should confirm DCN3.01 display init, VM context programming, DCC capability decisions for tiled and linear surfaces, watermark programming, p-state verification through debug index `0xB`, and register reads through `hubbub2_read_state`.
