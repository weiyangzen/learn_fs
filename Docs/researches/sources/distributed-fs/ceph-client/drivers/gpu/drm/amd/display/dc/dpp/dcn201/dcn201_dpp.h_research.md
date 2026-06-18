# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.h

## Purpose
`dcn201_dpp.h` defines the DCN 2.0.1 DPP object and register contract. It reuses the DCN20 register and field macro sets while providing DCN201-specific struct names, a downcast macro, and the `dpp201_construct()` declaration.

## Important APIs, types, and functions
- `TO_DCN201_DPP()` downcasts a generic `struct dpp *` to `struct dcn201_dpp *`.
- `TF_REG_LIST_DCN201()`, `TF_REG_LIST_SH_MASK_DCN201()`, and `TF_REG_FIELD_LIST_DCN201()` alias the DCN20 macro families.
- `struct dcn201_dpp_shift` and `struct dcn201_dpp_mask` expand DCN20 field lists into DCN201-named field tables.
- `struct dcn201_dpp_registers` uses `DPP_DCN2_REG_VARIABLE_LIST`, which omits the DCN20 append list for B-bank ICSC/gamut registers.
- `struct dcn201_dpp` embeds the generic DPP base, register tables, scaler filter caches, line-buffer capability fields, safe-RAM flag, scaler snapshot, and PWL data.
- `dpp201_construct()` is the constructor consumed by resource code.

## Control flow
The header has no executable control flow. It shapes how DCN201 resource code creates a DPP: generated register tables using the DCN201 macros are passed to `dpp201_construct()`, implementation callbacks downcast through `TO_DCN201_DPP()`, and shared DCN10/DCN20 helpers access registers through the stored tables.

## State and persistence behavior
State is runtime-only. `struct dcn201_dpp` mirrors the cache fields used by DCN10/DCN20 implementations: scaler coefficient table pointers, line-buffer support, last scaler data, and PWL parameters. Hardware state is represented by register addresses and masks supplied at construction and programmed later by implementation callbacks.

## Dependencies and integration points
The header includes `dcn20/dcn20_dpp.h` and inherits its dependency on `dcn10_dpp.h`, display core types, and generated register symbols. It is included by `dcn201_dpp.c` and by ASIC resource files that instantiate DCN201 DPP objects.

## Risks and edge cases
The register struct intentionally does not include `DPP_DCN2_REG_VARIABLE_LIST_CM_APPEND`, yet `dcn201_dpp.c` reuses some DCN20 color functions through the function table. Any callback that expects appended B-bank registers would be unsafe unless DCN201 never exercises that path or compatible symbols are supplied elsewhere. Macro aliasing also means DCN20 field-list changes automatically affect DCN201, which can break builds or subtly expose unsupported fields.

## Test signals
Build tests for DCN201 resource files are essential. Runtime validation should instantiate a DCN201 DPP, run setup/scaler/color function-table callbacks, verify no callback references absent register fields, and compare register traces against DCN201 hardware documentation for converter, cursor, scaler, gamut, degamma, blend, shaper, and 3D LUT paths.
