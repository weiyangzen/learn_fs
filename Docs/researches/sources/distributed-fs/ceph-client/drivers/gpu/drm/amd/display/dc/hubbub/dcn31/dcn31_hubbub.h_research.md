# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.h

## Purpose

`dcn31_hubbub.h` defines the DCN3.1 Hubbub register and field map and declares the DCN3.1 constructor and initialization helpers. It builds on DCN3.0/DCN2.1 and adds HVM, DET, compbuf, SDPIF, clock, memory-power, and Z8 self-refresh watermark fields.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN31(id)` appends DCHVM registers, DET0-DET3 controls, compbuf controls, reserved compbuf space, debug, clock, SDPIF, memory power, and Z8 watermark registers.
- `HUBBUB_MASK_SH_LIST_DCN31(mask_sh)` binds VM aperture fields, HVM/RIOMMU fields, urgent bandwidth fields, DET/compbuf fields, Z8 watermark fields, VM fault fields, clock gate fields, SDPIF control, and DET memory power low-speed mode.
- Prototypes: `hubbub31_init_dchub_sys_ctx`, `hubbub31_init`, and `hubbub31_construct`.

## Control Flow

The header contributes register metadata only. Runtime flow is implemented in `dcn31_hubbub.c`, where the constructor installs `hubbub31_funcs`; the declared init and sys-context functions are invoked by display init and VM setup paths.

## State And Persistence Behavior

No state is stored in the header. Its macros enable DCN3.1 code to cache and program DET, compbuf, watermark, HVM, VM fault, SDPIF, clock, and memory-power register state through `struct dcn20_hubbub`.

## Dependencies And Integration Points

The file includes `dcn21/dcn21_hubbub.h` and relies on DCN common Hubbub macro families. It integrates with generated ASIC register tables, DCN3.1 resource construction, DCHVM setup, DCC capability decisions, watermark programming, and debug register-state reads.

## Risks And Edge Cases

- Register-list duplication or omission affects every `REG_*` call in the C file.
- The header exposes only DET0-DET3 fields, so code is tied to four tracked DET instances.
- Z8 watermark fields must align with the `union dcn_watermark_set` layout used by DCN3.1 programming.
- HVM fields are present even when RIOMMU init may not become active; callers must handle inactive status.

## Test Signals

Compilation validates field names and prototypes. Runtime checks include DET/compbuf programming, HVM init, Z8 watermark writes, SDPIF ownership programming, clock-gate debug paths, and VM fault status read/clear behavior.
