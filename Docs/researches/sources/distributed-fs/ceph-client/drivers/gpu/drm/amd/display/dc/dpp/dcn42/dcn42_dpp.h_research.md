# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h

## Purpose
`dcn42_dpp.h` extends the DCN401 DPP register and field map for DCN42. It adds CM histogram registers/fields, split 2-bit alpha LUT register variables, and the concrete `struct dcn42_dpp` plus constructor prototype.

## Important APIs, types, and functions
- `TO_DCN42_DPP()` casts a base DPP to `struct dcn42_dpp`.
- `DPP_REG_LIST_SH_MASK_DCN42_COMMON()` is the DCN42 field-map macro, largely extending DCN401 with histogram fields and DCN42 register names.
- `DPP_REG_FIELD_LIST_DCN42()` appends histogram control/status/data/scale/bias/coefficient fields to the DCN401 field list.
- `DPP_REG_VARIABLE_LIST_DCN42` adds `ALPHA_2BIT_LUT01`, `ALPHA_2BIT_LUT23`, and CM histogram registers to the DCN401 variable list.
- `struct dcn42_dpp_registers`, `struct dcn42_dpp_shift`, `struct dcn42_dpp_mask`, and `struct dcn42_dpp` define the DCN42 table and object layouts.
- `dpp42_construct()` is the constructor consumed by resource code.

## Control flow
The header has no executable flow. Its macros generate register table shape, while the struct definitions and constructor prototype are consumed by `dcn42_dpp.c` and ASIC resource construction.

## State and persistence behavior
`struct dcn42_dpp` mirrors `struct dcn401_dpp` in layout style: it stores base DPP, register tables, cached filter pointers, line-buffer properties, scaler data, and PWL data. Histogram state itself is hardware-register-backed and caller-buffer-backed, not stored in the DPP object. No durable persistence exists.

## Dependencies and integration points
The header depends on `dcn401/dcn401_dpp.h` and therefore inherits DCN401/DCN30/DCN32 types. It integrates with DCN42 resource files that instantiate register lists and with DPP histogram callbacks implemented in `dcn42_dpp.c`.

## Risks and edge cases
The macro is very large and inherits all DCN401 map fragility while adding histogram fields. It duplicates some field entries such as `CM_HIST_DATA`, and also includes both DCN401 and DCN42 alpha LUT naming. `dcn42_dpp.c` relies on structural compatibility with `struct dcn401_dpp` in at least one cast, so changing field order in `struct dcn42_dpp` can break runtime register access. Histogram field masks must match hardware bin read sequencing.

## Test signals
Compile coverage for DCN42 ASIC register tables, DPP construction, histogram callback linkage, alpha LUT programming, inherited DCN401 scaler/cursor paths, and runtime histogram read/control tests are the key signals.
