# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h

## Purpose
`dcn10_opp.h` defines the DCN1.0 OPP private structure, register-list macros, field mask/shift lists, and function prototypes used by `dcn10_opp.c` and later OPP generations.

## Important APIs, types, and functions
Key macros are `TO_DCN10_OPP()`, `OPP_SF()`, `OPP_REG_LIST_DCN()`, `OPP_REG_LIST_DCN10()`, `OPP_COMMON_REG_VARIABLE_LIST`, `OPP_MASK_SH_LIST_DCN()`, `OPP_MASK_SH_LIST_DCN10()`, and `OPP_DCN10_REG_FIELD_LIST()`. Types include `struct dcn10_opp_registers`, `struct dcn10_opp_shift`, `struct dcn10_opp_mask`, and `struct dcn10_opp`. Prototypes expose construction, format programming, bit-depth reduction, stereo, pipe clock control, destruction, and register readback.

## Control flow
The header has no executable flow. It supplies the generated register metadata consumed by register-helper macros in the C file. Later headers include it to inherit common FMT/OPPBUF/OPP_PIPE definitions.

## State and persistence behavior
`struct dcn10_opp` carries runtime object identity, register metadata, and `is_write_to_ram_a_safe`; persistent display state lives in hardware registers programmed through the C implementation.

## Dependencies and integration points
It depends on `opp.h`, AMD register naming macros such as `SRI`, and shared DC color/timing structures referenced by function prototypes. It integrates with DC resource factories and later OPP generations.

## Risks and edge cases
Register field macros must match hardware-generated register definitions. `OPP_COMMON_REG_VARIABLE_LIST` includes `OPP_PIPE_CRC_CONTROL` although DCN10 function code mostly reads it for diagnostics. Fields for OPPBUF segmentation are declared even when generation-specific behavior is minimal.

## Test signals
Compile coverage across DCN10 and derived generations, successful register-table initialization, and mode-set paths that touch every declared FMT/OPPBUF/OPP_PIPE field are the main signals.
