# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.h

## Purpose

`dcn30_hubbub.h` is the DCN 3.0 Hubbub interface header. It extends the DCN2.1 Hubbub register model with DCN3 watermark, VM fault, urgent bandwidth, trip-to-memory, and p-state-control fields, and declares the DCN3 shared Hubbub construction and programming entry points consumed by ASIC-specific Hubbub implementations.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN3AG(id)` and `HUBBUB_MASK_SH_LIST_DCN3AG(mask_sh)` alias the DCN2.1 register and mask/shift lists for the AG variant.
- `HUBBUB_REG_LIST_DCN30(id)` combines common DCN2.0 registers, self-refresh watermark registers, fractional urgent bandwidth registers for sets A-D, and refcycle-per-trip registers for sets A-D.
- `HUBBUB_MASK_SH_LIST_DCN30(mask_sh)` defines field bindings for global timer refdiv, VM framebuffer/AGP apertures, urgent and VM-row watermarks, DCHUBBUB memory trip metrics, VM fault reporting and interrupt controls, and stutter/self-refresh masks.
- Exported functions include `hubbub3_construct`, `hubbub3_init_dchub_sys_ctx`, `hubbub3_dcc_support_swizzle`, `hubbub3_get_dcc_compression_cap`, `hubbub3_program_watermarks`, `hubbub3_force_wm_propagate_to_pipes`, `hubbub3_force_pstate_change_control`, `hubbub3_init_watermarks`, and `hubbub3_read_reg_state`.

## Control Flow

This header does not execute control flow directly. It supplies the generation-specific register maps that C files expand into `struct dcn_hubbub_registers`, `struct dcn_hubbub_shift`, and `struct dcn_hubbub_mask` tables, then declares the functions that operate on those tables. Runtime control flow enters through a generation constructor, installs a `struct hubbub_funcs` table, and later calls the declared helpers through DC resource and HWSS paths.

## State And Persistence Behavior

No state is owned by the header. Its macros determine which MMIO registers and fields can be addressed by DCN3 Hubbub code. The declared functions mutate in-memory `struct dcn20_hubbub` cache fields and hardware registers in their implementation files, especially watermarks, VM aperture registers, DCC capability outputs, p-state force bits, and register-state snapshots.

## Dependencies And Integration Points

The header depends on `dcn21/dcn21_hubbub.h` for base Hubbub macros, structs, and inherited function declarations. It integrates with AMD Display Core resource construction, ASIC register table generation, Hubbub function-table dispatch, DCC capability checks used by surface validation, watermark programming used by bandwidth/DML decisions, and VM aperture setup used during display init.

## Risks And Edge Cases

- Macro expansion order is critical: missing or duplicate register fields can silently misalign generated register tables with later `REG_*` calls.
- DCN30 still inherits many DCN2.1 definitions; ASIC variants must verify that reused field names are valid for their register headers.
- VM fault and watermark fields are exposed here but only safe when the selected C implementation uses matching masks and shifts.
- The header declares shared functions used by later generations; signature drift would break multiple ASIC implementations at compile time.

## Test Signals

Build coverage is the main signal: register-table expansion errors, missing field names, and function prototype mismatches fail kernel compilation. Runtime signals include successful display init, DCC capability selection, watermark programming without register access faults, VM aperture setup, and debug reads from `hubbub3_read_reg_state`.
