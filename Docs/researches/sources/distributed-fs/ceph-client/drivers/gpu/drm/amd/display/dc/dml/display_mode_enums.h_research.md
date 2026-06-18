# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_enums.h

## Purpose
This header centralizes DML enum contracts for display formats, tiling, validation results, power-state policies, output links, and mode-support decisions. These values are shared across DML calculators, pipe population code, SoC bounding-box setup, and register packing.

## Important APIs, Types, And Functions
The file defines enums for output encoders/formats/BPC, source formats, scan direction, swizzle modes, line-buffer depth, voltage states, macro tile size, cursor BPP, DRAM clock-change support, output standards, MPC affinity, request type, self-refresh affinity, validation status, writeback config, ODM combine modes/policies, immediate flip requirement, unbounded requesting policy, rotation angle, MALL use, DP link rate, FCLK-change support, prefetch modes, output type, and output rate.

## Control Flow And State
There is no control flow or state. The numeric values form ABI-like contracts inside the driver: DML calculations, resource policy, and status logging all assume stable enum meanings. Some enums alias values intentionally, such as mono formats mapping to 444 formats.

## Dependencies And Integration Points
Included by `display_mode_structs.h`, `display_mode_lib.h`, DCN utility headers, and numerous generated DML implementations. `display_mode_lib.c` maps `dm_validation_status` to user-readable strings. DCN32 RQ/DLG code uses format, rotation, swizzle, ODM, and output enums to choose register packing behavior.

## Risks
Changing numeric order can break table indexing, validation status mapping, and hardware policy interpretation. The status-to-string mapper in `display_mode_lib.c` does not cover all enum values in this file, so new statuses can appear as "Unknown Status" unless kept in sync. Some enum names are historical and cross-generation, increasing risk of using the wrong policy enum in newer DCN paths.

## Test Signals
Compile coverage catches missing enum names, but behavior tests should verify DML validation messages, ODM policy behavior, MALL and prefetch mode selection, output link selection, and immediate flip requirements. Static review should flag new enum values that need logging or DML2 translation updates.
