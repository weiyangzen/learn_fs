# sources/distributed-fs/ceph-client/drivers/clk/sifive/fu540-prci.h

Purpose: FU540 PRCI descriptor data included by the common SiFive PRCI driver.

Important APIs/types/functions: WRPLL metadata for core, DDR, and GEMGXL PLLs; ops tables for programmable WRPLL, read-only WRPLL, and TLCLK; `__prci_init_clocks_fu540[]`; `prci_clk_fu540`.

Control flow: OF match data selects this descriptor for `"sifive,fu540-c000-prci"`. The common driver iterates the array, caches WRPLL config, and registers four clocks.

State and persistence behavior: static descriptors persist for module lifetime; each `__prci_wrpll_data.c` caches current WRPLL config after probe and set-rate.

Dependencies/integration points: `dt-bindings/clock/sifive-fu540-prci.h`, common PRCI helpers, CCF, and WRPLL library. Core PLL uses HFCLK bypass during rate changes.

Risks: array indices are DT ABI; DDRPLL is read-only by ops choice; bypass callback mistakes can glitch core clocks.

Test signals: FU540 boot/probe, four-clock provider coverage, core/GEMGXL rate changes, DDRPLL recalc-only behavior, and TLCLK divider validation.
