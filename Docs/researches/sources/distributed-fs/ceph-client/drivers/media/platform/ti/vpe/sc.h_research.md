# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.h

## Purpose
Defines TI scaler register offsets, masks, feature bits, coefficient geometry, frame-size limits, state structure, and exported scaler helper prototypes.

## Important APIs, Types, and Functions
Important definitions include `CFG_SC0` feature bits, accumulator/size/threshold masks for registers SC1-SC25, `SC_NUM_PHASES`, `SC_H_NUM_TAPS`, `SC_V_NUM_TAPS`, `SC_NUM_TAPS_MEM_ALIGN`, max dimensions, `SC_COEF_SRAM_SIZE`, and `struct sc_data`. Prototypes expose register dump, coefficient setup, scaler config, and resource creation.

## Control Flow
No executable control flow is present, but constants encode the register contract used by `sc.c` and hardware payload builders.

## State and Persistence
`struct sc_data` tracks mapped registers, coefficient load flags, loaded coefficient DMA addresses, and platform device pointer. The rest is compile-time configuration.

## Dependencies and Integration Points
Used by `sc.c` and TI VPE/VIP drivers. Coefficient geometry must match `sc_coeff.h` array dimensions and the VPDMA/scaler coefficient SRAM payload layout.

## Risks and Edge Cases
Incorrect masks or shifts can corrupt unrelated register fields. Max width/height of 2047 must be enforced by callers before `sc_config_scaler()`. Coefficient SRAM size depends on phase count, two luma/chroma sets, aligned taps, and 16-bit coefficients.

## Test Signals
Compile-time array sizing, register-payload tests for known dimensions, hardware scaling validation at min/max sizes, and coefficient DMA loading checks are the main signals.
