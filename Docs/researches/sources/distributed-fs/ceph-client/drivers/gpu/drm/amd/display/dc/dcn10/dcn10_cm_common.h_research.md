# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.h

## Purpose
Defines register descriptor structures and function prototypes for DCN1 color-management helper code.

## Important APIs, Types, And Functions
Macros `TF_HELPER_REG_FIELD_LIST`, `TF_HELPER_REG_LIST`, and `TF_CM_REG_FIELD_LIST` generate shift/mask/register fields. Types include `xfer_func_shift`, `xfer_func_mask`, `xfer_func_reg`, `cm_color_matrix_shift`, `cm_color_matrix_mask`, and `color_matrices_reg`. Prototypes expose matrix programming/readback, transfer-function programming, software-to-hardware curve translation, degamma translation, and custom-float conversion.

## Control Flow
No executable flow. The macro-generated structures define the shape used by register-specific DPP/OPP code when calling helpers.

## State And Persistence
No runtime state; all structures are caller-owned constant register maps or temporary descriptors.

## Dependencies And Integration Points
Consumed by `dcn10_cm_common.c` and display block implementations that populate register lists. It is part of the shared color-management contract for DCN1 and later code that reuses DCN1 helpers.

## Risks
Field names must match the `REG_SET*` calls in the implementation. The misspelled `exp_resion_start_segment` is part of the ABI between macros and code and must not be “fixed” without updating all users. Header lacks explicit type includes for several structs used in prototypes, relying on include order.

## Test Signals
Compile-time field resolution is the primary signal. Runtime color tests validate that generated register descriptors match the expected hardware fields.
