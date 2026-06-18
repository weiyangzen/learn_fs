# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.c

## Purpose
Implements TI VPE/VIP scaler helper logic. It maps scaler resources, dumps registers, chooses horizontal/vertical coefficient tables, lays them into coefficient memory with hardware alignment, and fills scaler register shadows for bypass, linear scaling, decimation, polyphase vertical scaling, or RAV vertical downscaling.

## Important APIs, Types, and Functions
Exports `sc_dump_regs()`, `sc_set_hs_coeffs()`, `sc_set_vs_coeffs()`, `sc_config_scaler()`, and `sc_create()`. It depends on `struct sc_data` and coefficient arrays from `sc_coeff.h`.

## Control Flow
`sc_set_hs_coeffs()` chooses upscaling, one-to-one/downscale, or less-than-N/16 tables after accounting for up to two 2x horizontal decimation stages, then copies luma and chroma phases into 8-slot-aligned coefficient memory. `sc_set_vs_coeffs()` chooses vertical tables by output/input ratio. `sc_config_scaler()` clears feature bits, bypasses if dimensions match, otherwise enables linear scaling, configures horizontal decimation and accumulator increments, selects RAV for >4x vertical downscale or polyphase otherwise, then fills the caller's register shadow blocks.

## State and Persistence
`struct sc_data` stores MMIO base/resource, platform device, last loaded coefficient DMA addresses, and `load_coeff_h/load_coeff_v` flags set when new coefficient memory is prepared. Runtime register values are shadowed by the caller and volatile in hardware.

## Dependencies and Integration Points
Depends on platform resources, MMIO mapping, Linux division helpers, exported symbols for TI VPE/VIP drivers, register definitions from `sc.h`, and static coefficients from `sc_coeff.h`.

## Risks and Edge Cases
Dimension equality bypasses all scaling. Downscale ratio selection clamps table index at 8/16 minimum; very small destinations rely on caller validation. Register pointer arithmetic assumes the caller's payload layout matches scaler MMR block ordering. RAV accumulator math has signed intermediate cases that need careful regression coverage.

## Test Signals
Test 1:1 bypass, horizontal upscales, 2x/4x decimation, downscale buckets from 8/16 to 16/16, vertical RAV for >4x downscale, coefficient memory layout size/alignment, and resource mapping failures.
