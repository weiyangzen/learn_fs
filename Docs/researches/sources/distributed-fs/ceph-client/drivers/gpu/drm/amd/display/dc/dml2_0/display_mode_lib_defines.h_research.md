# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_lib_defines.h

## Purpose
`display_mode_lib_defines.h` provides compile-time constants, common typedefs, and base DML dependencies for the legacy DML 2.0 core. It fixes the model dimensions and feature presence expected by the rest of the DML source.

## Important APIs, types, and functions
Important defines include `DCN_DML__NUM_PLANE` as 8, `DCN_DML__NUM_CURSOR` as 1, `DCN_DML__NUM_PWR_STATE` as 30, `DCN_DML__VM_PRESENT`, `DCN_DML__HOST_VM_PRESENT`, `__DML_MIN_DCFCLK_FACTOR__`, `__DML_MAX_VRATIO_PRE__`, `__DML_MAX_VRATIO_PRE_ENHANCE_PREFETCH_ACC__`, and `__DML_PIPE_NO_PLANE__`. It defines `dml_int_t`, `dml_uint_t`, `dml_float_t`, and `dml_bool_t`.

## Control flow
There is no runtime control flow. Preprocessor constants determine array sizes, debug inclusion, and formula limits used by calculation and debug helper code.

## State and persistence behavior
The file creates no runtime state. It constrains the memory layout of every structure that uses the fixed plane, cursor, and power-state constants.

## Dependencies and integration points
It includes `dml_depedencies.h`, `dml_logging.h`, and `dml_assert.h`, making logging and assertion behavior available to all including DML headers. It is included by `display_mode_core_structs.h` and thereby becomes a core dependency for most DML code.

## Risks and edge cases
Changing plane or power-state counts is ABI-like for the local DML structures. `__DML_VBA_DEBUG__` is enabled unconditionally here, so debug print paths can be compiled into builds depending on downstream macro handling. The comments note historical VBA type compatibility; changing typedef widths would break layout and formula assumptions.

## Test signals
Build tests should verify all DML users compile with the fixed dimensions. Runtime tests should include eight-plane stress cases, power-state table bounds, and debug logging builds with assertions enabled and disabled.
