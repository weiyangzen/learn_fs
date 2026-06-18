# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa1928.c

Purpose: OF clock setup for PXA1928 split into separate MPMU, APMU, and APBC compatible nodes.

Important APIs/functions: `pxa1928_mpmu_clk_init`, `pxa1928_apmu_clk_init`, and `pxa1928_apbc_clk_init` are separate `CLK_OF_DECLARE` entries. Helpers register root/factor clocks, APBC mux/gates, APMU SDH/USB gates, and reset cells.

Control flow: MPMU init maps the PLL bank and registers fixed roots/factors plus `uart_pll`. APMU init creates an APMU onecell provider and registers one shared SDH mux/div plus gates for USB/HSIC/SDH0-4. APBC init creates an APBC onecell provider, registers UART/SSP muxes, APB gates for TWSI/GPIO/KPC/RTC/PWM/UART/SSP, and reset mappings.

State and persistence: each compatible node allocates its own `pxa1928_clk_unit`; MMIO registers hold clock state. Reset cells are derived from APBC gate table entries.

Dependencies and integration: uses PXA1928 DT clock bindings, MMP helper registration, and reset controller APIs. Root clocks are registered by name for cross-node parent references.

Risks: split providers mean parent names must be globally registered before consumers request derived clocks. Several fixed roots have id zero and are not exported by onecell ID. APMU uses the SDH0 register fields for the shared SDH mux/div while gates are per SDH register, so hardware assumptions are central.

Test signals: DT boot ordering across MPMU/APMU/APBC nodes, UART/SSP/SDH rate queries, reset phandle lookup by clock ID, and smoke tests for all exported PXA1928 clock IDs.
