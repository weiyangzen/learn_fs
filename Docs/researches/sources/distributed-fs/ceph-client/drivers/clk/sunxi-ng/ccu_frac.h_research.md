# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.h

## Purpose
This header defines the internal fractional-rate descriptor embedded in sunxi-ng PLL classes.

## Important APIs, Types, And Functions
It declares `struct ccu_frac_internal`, `_SUNXI_CCU_FRAC()`, and prototypes for the fractional helpers.

## Control Flow
There is no runtime flow here; it supplies descriptor data for `ccu_frac.c`.

## State And Persistence
State is limited to register bit masks and the two supported rates stored in static descriptors.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration is via `ccu_nm.h` and `ccu_mult.h` macros.

## Risks
The descriptor assumes exactly two fractional rates and active-low enable semantics implemented by the helper. Wrong masks can invert or misselect PLL frequencies.

## Test Signals
Build and exact-rate PLL tests validate that descriptors initialize correctly.
