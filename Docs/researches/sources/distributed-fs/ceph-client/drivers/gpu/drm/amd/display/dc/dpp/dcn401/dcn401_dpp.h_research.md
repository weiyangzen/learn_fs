# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.h

## Purpose
`dcn401_dpp.h` defines the DCN401 DPP register map, field map, concrete DPP structure, scaler mode enum, and cross-file prototypes. It extends DCN3 definitions with DCN4 cursor matrix, EASF, iSharp, luma keyer, line-buffer power, and extra scaler-init fields.

## Important APIs, types, and functions
- `TO_DCN401_DPP()` casts a base DPP to `struct dcn401_dpp`.
- `DPP_REG_LIST_SH_MASK_DCN401_COMMON()` enumerates DCN401 register field mappings for CM, CNVC, cursor, DSCL, EASF, iSharp, and scaler init.
- `DPP_REG_FIELD_LIST_DCN401()` extends the DCN3 field list with cursor matrix, EASF horizontal/vertical, scaler color matrix, iSharp, luma keyer, and related low-power fields.
- `DPP_REG_VARIABLE_LIST_DCN401`, `struct dcn401_dpp_registers`, `struct dcn401_dpp_shift`, and `struct dcn401_dpp_mask` define register offset and field tables.
- `struct dcn401_dpp` embeds `struct dpp`, register tables, filter cache pointers, line-buffer properties, `struct scaler_data`, and `struct pwl_params`.
- `enum dcn401_dscl_mode_sel` defines hardware scaler modes for 444 bypass/RGB/YCbCr, 420 combined/luma/chroma bypass, and full DSCL bypass.
- Prototypes expose construction, DPP setup, scaler manual programming, cursor callbacks, line-buffer calculators, read state, and cursor matrix setup.

## Control flow
There is no executable flow in the header. Its macros expand into ASIC register tables used by `dcn401_dpp.c`, `dcn401_dpp_cm.c`, `dcn401_dpp_dscl.c`, and DCN42 code. The enum and prototypes establish contracts used by scaler mode selection and DPP function-table callbacks.

## State and persistence behavior
The header defines runtime state shape only. `struct dcn401_dpp` caches the last scaler data and filter pointers so `dcn401_dpp_dscl.c` can skip redundant programming and detect filter updates. Register tables are static configuration. There is no durable persistence.

## Dependencies and integration points
The header depends on DCN20, DCN30, and DCN32 DPP headers. It is included by DCN401 implementation files and by DCN42, which extends it. ASIC resource files must provide register offsets, shifts, and masks matching the field list.

## Risks and edge cases
This is a large macro map with many hardware-specific fields. Missing or duplicated field entries can silently target wrong registers if generated tables remain type-compatible. DCN42 includes this header and extends the field list, so any incompatible structural change affects newer code. The register struct contains both `ALPHA_2BIT_LUT` through the common list and `ALPHA_2BIT_LUT01/23`, requiring generation code to select the correct fields for each ASIC. The enum values must match hardware `DSCL_MODE` encodings.

## Test signals
Compile coverage across DCN401 and DCN42 ASIC table instantiations, DPP construction, cursor matrix programming, EASF/iSharp scaler programming, SPL and non-SPL scaler paths, and register read/write tests are the main signals.
