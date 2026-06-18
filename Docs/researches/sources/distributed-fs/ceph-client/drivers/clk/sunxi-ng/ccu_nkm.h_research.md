# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.h

## Purpose
This header declares the N*K/M clock class used for PLLs that multiply by N and K then divide by M.

## Important APIs, Types, And Functions
Important items are `struct ccu_nkm`, `SUNXI_CCU_NKM_WITH_MUX_GATE_LOCK`, `SUNXI_CCU_NKM_WITH_GATE_LOCK`, factor fields, optional fixed postdivider, and ratio constraints.

## Control Flow
No runtime flow lives here. It provides descriptors for `ccu_nkm.c`.

## State And Persistence
State is descriptor-only until probe initializes `ccu_common`; hardware factor fields are then read/written by ops.

## Dependencies And Integration Points
It depends on CCF and common/div/mult headers. SoC PLL descriptors use it for DDR and similar clocks.

## Risks
Ignoring `max_m_n_ratio` or `min_parent_m_ratio` can let rate selection choose unstable hardware combinations.

## Test Signals
Build plus PLL rate tests with constrained descriptors validate it.
