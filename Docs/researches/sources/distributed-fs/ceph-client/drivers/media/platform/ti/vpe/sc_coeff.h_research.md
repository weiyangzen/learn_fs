# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc_coeff.h

## Purpose
Provides static horizontal and vertical polyphase scaler coefficient tables for the TI VPE/VIP scaler.

## Important APIs, Types, and Functions
Defines horizontal table indices `HS_UP_SCALE`, `HS_LT_9_16_SCALE` through `HS_LE_16_16_SCALE`, vertical indices `VS_UP_SCALE` through `VS_1_TO_1_SCALE`, and two static arrays: `scaler_hs_coeffs[13][SC_NUM_PHASES * 2 * SC_H_NUM_TAPS]` and `scaler_vs_coeffs[15][SC_NUM_PHASES * 2 * SC_V_NUM_TAPS]`.

## Control Flow
No functions execute here. `sc_set_hs_coeffs()` and `sc_set_vs_coeffs()` select rows by scale ratio and copy luma/chroma phase coefficients into hardware-aligned coefficient memory.

## State and Persistence
The arrays are read-only compiled data. They persist as part of the module/kernel image and are shared by all scaler instances.

## Dependencies and Integration Points
Requires `SC_NUM_PHASES`, tap counts, and related constants from `sc.h` before inclusion. Coefficient dimensions and ordering must match the copy loops in `sc.c` and hardware coefficient SRAM expectations.

## Risks and Edge Cases
The declared array has more rows than the named indices currently used, so size and index assumptions should be reviewed before edits. Any value/order change can alter image quality or cause hardware coefficient misalignment. Luma and chroma sections are packed back-to-back for every table.

## Test Signals
Compile array bounds with `sc.c`, verify coefficient memory layout for horizontal 7-tap and vertical 5-tap copies, compare known scaling output quality, and regression-test all ratio buckets including 1:1, upscaling, and strongest downscaling.
