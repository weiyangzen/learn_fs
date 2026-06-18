# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mult.h

## Purpose
This header declares the simple multiplier clock class used by CPU PLLs and similar clocks.

## Important APIs, Types, And Functions
It defines `struct ccu_mult_internal`, `_SUNXI_CCU_MULT*` helpers, `struct ccu_mult`, `SUNXI_CCU_N_WITH_GATE_LOCK`, and `ccu_mult_ops`.

## Control Flow
There is no runtime flow. Static descriptors built here are handled by `ccu_mult.c`.

## State And Persistence
State fields include enable mask, lock bit, optional fractional descriptor, multiplier bitfield, optional mux, and common register metadata.

## Dependencies And Integration Points
It depends on `ccu_common`, `ccu_frac`, and `ccu_mux`. It integrates with SoC PLL descriptors, notably A80 CPU PLLs.

## Risks
Offset/min/max fields encode hardware-specific multiplier semantics. Incorrect min values can program out-of-range CPU PLL frequencies.

## Test Signals
Compile and PLL rate-change tests validate this header.
