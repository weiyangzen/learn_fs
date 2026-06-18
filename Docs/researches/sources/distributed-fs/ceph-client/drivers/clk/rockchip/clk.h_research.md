# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.h

Purpose: shared header for Rockchip clock-controller drivers. It defines CRU register-offset macros for many SoCs, PLL/rate/provider data structures, branch construction macros, reset registration hooks, and exported common-clock helper prototypes.

Important APIs/types/functions: `HIWORD_UPDATE()`, SoC register macros such as `RV1126B_*`, `RK3506_*`, `RK3528_*`, `RK3562_*`, `RK3576_*`, and `RK3588_*`, `enum rockchip_pll_type`, `struct rockchip_pll_rate_table`, `struct rockchip_pll_clock`, `struct rockchip_clk_provider`, `struct rockchip_clk_branch`, `struct rockchip_cpuclk_rate_table`, `struct rockchip_cpuclk_reg_data`, and `struct rockchip_gate_link_platdata`. Branch macros include `PLL`, `PNAME`, `COMPOSITE*`, `MUX*`, `DIV*`, `GATE*`, `GATE_LINK`, `MMC*`, `INVERTER`, `FACTOR*`, and half-divider variants.

Control flow: the header does not execute logic, but it determines how SoC table initializers populate branch fields consumed by `clk.c`. Inline lookup helpers read and write `ctx->clk_data.clks[id]`. Reset init prototypes connect SoC clock init files to reset mapping files.

State and persistence: defines provider state shape: CRU MMIO base, onecell data, OF node, main and auxiliary GRF regmaps, and a spinlock. Branch entries encode hardware register offsets, shifts, flags, lookup IDs, linked IDs, and optional child muxes.

Dependencies and integration: Linux CCF, IO, hashtable support, reset controller optional compile path, and Rockchip dt-binding IDs. It is the ABI between SoC-specific table files and common Rockchip CCF implementation.

Risks: macro argument ordering is easy to misuse; mistakes silently map into wrong registers or flags. Register-offset definitions span many hardware generations, so overlapping naming and CRU base arithmetic must be kept exact. `SGRF_GATE()` intentionally models secure-only clocks as fixed factors, which can hide hardware control limitations.

Test signals: compile coverage for all SoC clock drivers, Coccinelle/static checks for macro initializers, boot-time clock registration on affected SoCs, and dt-binding ID to onecell lookup validation.
