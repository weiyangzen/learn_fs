# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.h

## Purpose
This header defines CV18xx PLL descriptors, limits, field masks, and declaration macros for integral and fractional PLL clocks.

## Important APIs, Types, And Functions
`struct cv1800_clk_pll_limit` contains min/max ranges for `pre_div`, `div`, `post_div`, `ictrl`, and `mode`. `struct cv1800_clk_pll_synthesizer` describes fractional synthesizer enable, half-clock, control, and set registers. `struct cv1800_clk_pll` embeds the common clock state, PLL register, power-down bit, status bit, limit pointer, and optional synthesizer pointer.

Field masks and accessors cover PLL pre-divider, post-divider, mode, divider, and current-control fields. `PLL_COPY_REG()` preserves unrelated bits while copying the programmable PLL fields. Macros `CV1800_INTEGRAL_PLL()` and `CV1800_FACTIONAL_PLL()` instantiate PLL objects with the correct operation table.

## Control Flow
The header has no runtime flow. Its macros bind objects to `cv1800_clk_ipll_ops` or `cv1800_clk_fpll_ops`; the implementation file interprets field masks and limit ranges during rate operations.

## State And Persistence
The structures are static descriptors completed at probe with base and lock through the embedded common object. Hardware register fields persist PLL configuration and status.

## Dependencies And Integration Points
It depends on `clk-cv18xx-common.h` for common clock state and bit descriptors. Top-level CV1800 declarations use this header for every root PLL and fractional synthesizer.

## Risks
The limit pointer is untyped with respect to array length, yet fractional implementation indexes beyond the first element. Incorrect limits can cause invalid hardware programming or excessive search time. Positional macro arguments for status and power-down bits are easy to mix up.

## Test Signals
Build tests ensure macro consumers compile. Runtime PLL tests should validate field extraction, `PLL_COPY_REG()` preservation, and both integral and fractional declarations under rate changes.
