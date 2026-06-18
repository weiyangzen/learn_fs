# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h

## Purpose

`dcn42_hubbub.h` declares the DCN4.2 Hubbub constants, register list, field list, and constructor. It exposes a larger 1792 KiB CRB configuration, A-D DCN4x watermark registers, DCHVM fields, Z8 watermarks, timeout/status fields, and DCN4.2-specific control bits.

## Important APIs, Types, And Functions

- Constants: `DCN42_CRB_SIZE_KB`, `DCN42_DEFAULT_DET_SIZE`, and `DCN42_CRB_SEGMENT_SIZE_KB`.
- `HUBBUB_REG_LIST_DCN42(id)` enumerates A-D urgent/stutter/frac/refcycle/p-state/USR/Z8 watermarks, VM aperture/fault registers, DET/compbuf, SDPIF, clock, memory power, DCHVM, host VM QoS, and QoS force registers.
- `HUBBUB_MASK_SH_LIST_DCN4_2(mask_sh)` inherits DCN3.2 fields and adds HVM, compbuf, FGCg, A-D watermark fields, deep-sleep force, QoS thresholds, VM fault, timeout detection, ROB overflow, urgent zero-size request enable, and cstate swath check fields.
- `hubbub42_construct(...)` initializes the runtime object.

## Control Flow

No executable control flow exists in the header. Its macros are expanded into register/mask/shift tables for the C implementation, and the constructor is called by DCN4.2 resource construction.

## State And Persistence Behavior

The header owns no state. Its field coverage permits `dcn42_hubbub.c` and reused helpers to mutate A-D watermark caches, self-refresh/deep-sleep force registers, DCHVM state, DET/compbuf segment state, timeout/debug fields, and VM fault state.

## Dependencies And Integration Points

It includes `dcn32/dcn32_hubbub.h` and is consumed by DCN4.2 ASIC resource code. It bridges older DCN3.2-style helper declarations with newer DCN4.2 register coverage and reused DCN35/DCN401 functions.

## Risks And Edge Cases

- The mask list contains repeated groups inherited from DCN3.2 and explicitly redeclared A-D fields; register-table generation must tolerate this and keep the intended field mapping.
- DCN42 exposes both DCFCLK deep-sleep force and self-refresh force fields; power-management tests must distinguish them.
- Timeout/status fields include diagnostic clear/status bits, so accidental writes can hide hardware faults.
- Constructor only declared here; all behavior depends on function-table choices in `dcn42_hubbub.c`.

## Test Signals

Builds validate macro fields and constructor linkage. Runtime checks should verify A-D watermark programming/readback, DCHVM init, deep-sleep and self-refresh force behavior, timeout/status register access, fixed CRB segment sizing, and SDPIF/debug field programming.
