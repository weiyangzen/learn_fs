# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.h

## Purpose
`dcn35_dpp.h` defines DCN35-specific DPP register field additions and prototypes. It layers on DCN32/DCN30 definitions and adds FGCg and DISPCLK gate fields needed by the DCN35 implementation.

## Important APIs, types, and functions
- `DPP_REG_LIST_SH_MASK_DCN35()` extends the DCN30 common shift/mask list with `DPP_FGCG_REP_DIS` and `DISPCLK_R_GATE_DISABLE`.
- `DPP_REG_FIELD_LIST_DCN35()` embeds the DCN3 field list and adds `DPP_FGCG_REP_DIS`.
- `struct dcn35_dpp_shift` and `struct dcn35_dpp_mask` are the DCN35 field-table types.
- Prototypes cover `dpp35_dppclk_control()`, `dpp35_construct()`, `dpp35_set_fgcg()`, and `dpp35_program_bias_and_scale_fcnv()`.

## Control flow
The header contains no executable control flow. Its macro expansions produce register field tables, and its prototypes connect resource construction and DPP function-table callbacks to `dcn35_dpp.c`.

## State and persistence behavior
No state is stored here. It defines table layouts and function signatures for runtime state held in DPP objects and hardware registers.

## Dependencies and integration points
The header depends on `dcn32/dcn32_dpp.h` and therefore on DCN30 structures. ASIC resource files must instantiate compatible shift/mask tables when using `dpp35_construct()`.

## Risks and edge cases
`DPP_REG_LIST_SH_MASK_DCN35()` lists `DPP_FGCG_REP_DIS` twice, which may be harmless but can obscure generated table intent. `DPP_REG_FIELD_LIST_DCN35()` only adds `DPP_FGCG_REP_DIS`, while `dpp35_dppclk_control()` also references `DISPCLK_R_GATE_DISABLE` through inherited masks; table-generation correctness is essential. The closing comment names `__DCN35_DPP_H` without trailing underscores, which is cosmetic but inconsistent.

## Test signals
Compile tests for DCN35 register table generation, `dpp35_construct()` callers, and function-table linkage are the primary signals, with runtime DPP clock and FGCg tests from the C file.
