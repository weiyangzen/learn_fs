# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h

## Purpose
`dcn20_dpp.h` extends the DCN10 DPP contract for DCN 2.0. It adds register and field definitions for blend gamma, shaper LUT, 3D LUT, alpha keying, two-bit alpha LUT, floating conversion controls, OBUF power control, and double-buffered DCN20 CSC/gamut banks, and declares the DCN20 object and exported functions.

## Important APIs, types, and functions
- Register macros include `TF_REG_LIST_DCN20_COMMON()`, `TF_REG_LIST_DCN20_COMMON_UPDATED()`, `TF_REG_LIST_DCN20_COMMON_APPEND()`, and `TF_REG_LIST_DCN20()`.
- Field macros include `TF_REG_LIST_SH_MASK_DCN20_COMMON()`, `TF_REG_LIST_SH_MASK_DCN20_UPDATED()`, `TF_REG_LIST_SH_MASK_DCN20()`, and debug-status macros for DCN20.
- `TF_REG_FIELD_LIST_DCN2_0(type)` extends the DCN10 field list with DCN20-only fields such as blend gamma, shaper, 3D LUT, keyer, alpha LUT, conversion clamps, cursor ROM, and OBUF memory force.
- `struct dcn2_dpp_registers`, `struct dcn2_dpp_shift`, `struct dcn2_dpp_mask`, and `struct dcn20_dpp` define the concrete object contract.
- Enums `dcn20_input_csc_select` and `dcn20_gamut_remap_select` define bypass and A/B bank selections.
- Declared functions cover constructor, state readback, degamma, gamut remap, input CSC, blend LUT, shaper, 3D LUT, alpha keyer, line-buffer partition calculations, cursor attributes, OBUF power, HDR multiplier, and gamut readback.

## Control flow
As a header, this file supplies the static metadata needed by DCN20 implementation files and ASIC resource code. DCN20 register tables are built from the macros, passed into `dpp2_construct()`, and then consumed by `REG_*` helpers. Function declarations are used to populate `dcn20_dpp_funcs` and by DCN201, which reuses much of the same implementation.

The control model encoded here differs from DCN10 in color management: input CSC and gamut remap use A/B banks rather than COMA/COMB naming, while blend gamma, shaper, and 3D LUT get explicit register fields and APIs. Legacy regamma and input LUT hooks remain declared as dummy/no-op helpers in `dcn20_dpp.c`.

## State and persistence behavior
The header describes volatile state only. `struct dcn20_dpp` mirrors DCN10 cache fields for scaler filters and transfer functions, adds `dispclk_r_gate_disable`, and points to DCN20-specific register/shift/mask tables. Persistent state lives only in hardware registers while the device is powered; the software object is rebuilt on driver initialization.

## Dependencies and integration points
The header includes `dcn10/dcn10_dpp.h` and therefore inherits DCN10 register fields, macros, and function declarations. It depends on generated DCN20 register naming, display core structures, and common LUT/CSC/gamma types. It is included by `dcn20_dpp.c`, `dcn20_dpp_cm.c`, and `dcn201_dpp.h`.

## Risks and edge cases
This header has high coupling to generated hardware definitions. The append list adds B-bank CSC/gamut registers, but `struct dcn2_dpp_registers` must include matching fields or implementation code will not compile. Field masks for debug status determine active-bank readback in `dcn20_dpp_cm.c`; incorrect shifts/masks can corrupt double-buffering. Since DCN201 reuses this macro family but defines a narrower register struct, macro reuse must match that ASIC's actual register inventory.

## Test signals
Build coverage across DCN20 and DCN201 is the first signal. Runtime tests should validate every function-table callback that depends on DCN20-only fields: A/B input CSC and gamut updates, blend gamma, shaper, 3D LUT, color keyer, alpha LUT, cursor ROM enable, OBUF power, and state readback fields.
