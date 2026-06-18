# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.h

## Purpose
This header defines the common sunxi-ng descriptor state shared by all CCU clock classes and provider drivers.

## Important APIs, Types, And Functions
It declares feature flags such as `CCU_FEATURE_FRACTIONAL`, predivider/postdivider flags, lock-register, MMC timing, SDM, key-field, closest-rate, dual-div, and update-bit support. It defines `struct ccu_common`, `struct sunxi_ccu_desc`, `struct ccu_pll_nb`, conversion helpers, and exported common APIs.

## Control Flow
There is no runtime code except inline container conversion. The definitions drive compile-time construction of SoC clock descriptors and runtime behavior in class ops.

## State And Persistence
State fields include MMIO base, register offsets, rate limits, feature flags, a shared lock pointer, and embedded `clk_hw`. These are initialized by `ccu_common.c` during provider probe.

## Dependencies And Integration Points
Dependencies are Linux CCF/compiler headers and adjacent reset map declarations. Integration is universal across sunxi-ng gate, mux, divider, PLL, phase, SDM, and SoC provider files.

## Risks
Feature flag semantics are cross-cutting. Adding or changing bits can alter rate calculations, register writes, or locking behavior across many SoCs. `struct ccu_common` layout assumptions underpin all `container_of` conversions.

## Test Signals
Compile coverage plus multi-SoC boot/probe tests validate this header. Specific signals include correct rate limits, update-bit behavior, PLL lock waits, and MMC timing support.
