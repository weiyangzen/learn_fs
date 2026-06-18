# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h

## Purpose
`dcn30_dpp.h` is the private DCN 3.0 DPP interface and register map definition. It extends DCN2 DPP register fields with DCN3 color-management, CNVC, DSCL, cursor, low-power, and LUT registers, defines `struct dcn3_dpp`, and declares the DCN3 DPP programming functions implemented across `dcn30_dpp.c` and `dcn30_dpp_cm.c`.

## Important APIs, types, and functions
- `TO_DCN30_DPP()` casts a base `struct dpp` to `struct dcn3_dpp`.
- `DPP_REG_LIST_DCN30_COMMON()`, `DPP_REG_LIST_DCN30()`, `DPP_REG_LIST_SH_MASK_DCN30_COMMON()`, `DPP_REG_LIST_SH_MASK_DCN30_UPDATED()`, and `DPP_REG_LIST_SH_MASK_DCN30()` are macro inventories consumed by ASIC resource register table generation.
- `DPP_REG_FIELD_LIST_DCN3()` defines the shift/mask field set used by `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask`.
- `DPP_DCN3_REG_VARIABLE_LIST_COMMON` and `struct dcn3_dpp_registers` define register-offset storage.
- `struct dcn3_dpp` embeds `struct dpp` and stores register tables, cached scaler filter pointers, line-buffer capabilities, scaler data, and PWL data.
- Public prototypes include construction, GAMCOR, CM dealpha/bias/gamut remap, pre-degamma, cursor attributes, post-CSC, state readback, and tap-selection helpers.

## Control flow
The header has no executable runtime flow. Its macros are expanded by generated/static register table definitions for each ASIC instance. C files use the resulting offset/shift/mask structures through `REG()`, `FN()`, and `REG_*` helpers to program hardware. Function prototypes define the callable surface that generational DPP constructors reuse in DCN32, DCN35, DCN401, and DCN42.

## State and persistence behavior
The header defines runtime state shape only. `struct dcn3_dpp` persists cached filter pointers and last scaler/PWL data in memory for the lifetime of a DPP object. Register offset, shift, and mask structures are read-only tables supplied by ASIC-specific resource code. There is no persistent storage outside kernel memory and hardware registers.

## Dependencies and integration points
The header depends on `dcn20/dcn20_dpp.h` for base DCN2 fields and types. It is included by DCN30 implementation files and by later generation headers that reuse DCN3 structures. The register-list macros must align with generated register headers and the ASIC resource files that instantiate register tables.

## Risks and edge cases
Macro-maintained hardware maps are brittle: duplicate entries, missing fields, or mismatched field names produce incorrect register writes or compile failures depending on where the mismatch appears. The file includes repeated register/field entries such as `CM_GAMCOR_LUT_INDEX` and duplicate cursor control fields, which may be intentional compatibility baggage but increase maintenance risk. `struct dcn3_dpp` is reused by later generations, so adding fields or changing type assumptions can affect DCN32/DCN35 code.

## Test signals
Build coverage across ASIC configurations is the primary signal for macro/table correctness. Runtime validation should include DPP construction, register writes for every callback in `dcn30_dpp.c` and `dcn30_dpp_cm.c`, debug readback, and later-generation builds that include this header through DCN32/DCN35/DCN401/DCN42.
