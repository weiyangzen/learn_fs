# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-nsp.c

## Purpose
Defines Broadcom Northstar Plus iProc clock descriptors for ARM PLL, GENPLL, and LCPLL0 blocks and binds them to early DT clock setup.

## Important APIs, Types, And Functions
`nsp_armpll_init` delegates to `iproc_armpll_setup`. Descriptor macros initialize `genpll`, `genpll_clk`, `lcpll0`, and `lcpll0_clk`. `nsp_genpll_clk_init` and `nsp_lcpll0_clk_init` call `iproc_pll_clk_setup`, and `CLK_OF_DECLARE` binds compatible strings `brcm,nsp-armpll`, `brcm,nsp-genpll`, and `brcm,nsp-lcpll0`.

## Control Flow
At OF clock initialization, the matching wrapper invokes the common iProc implementation with fractional NDIV and embedded power-control descriptors. The common code registers the PLL root and channel outputs with channel-specific enable and MDIV fields.

## State And Persistence
The file contributes static register descriptors only. Hardware register state and allocated `clk_hw` structures are owned by the shared iProc implementation. Several outputs are always-on and therefore persist through disable attempts.

## Dependencies And Integration Points
Uses `dt-bindings/clock/bcm-nsp.h`, `clk-iproc.h`, and OF clock declaration infrastructure. The DT resource and `clock-output-names` ordering must match the binding enum indexes.

## Risks And Edge Cases
Incorrect fractional NDIV, PDIV, reset, or status offsets can make PLL rate changes fail or hang waiting for lock. The ARM PLL path is external to this file, so platform support depends on that helper being linked.

## Test Signals
Probe-time registration under all three compatible strings, PLL recalc with fractional NDIV, lock behavior after rate changes, stable output indexes, and always-on disable protection are the main signals.
