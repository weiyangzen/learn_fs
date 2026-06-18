# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-s10.c

Purpose: gate-clock constructors and ops for Stratix10, Agilex, and Agilex5.

Important APIs/types/functions: normal/debug recalc functions; `socfpga_gate_get_parent()`; `socfpga_agilex_gate_get_parent()`; constructors `s10_register_gate()`, `agilex_register_gate()`, and `agilex5_register_gate()`.

Control flow: SoC table drivers call constructors per gate descriptor. Each constructor allocates state, assigns gate/divider/bypass metadata, chooses ops, initializes parent data/names, registers the clock, and returns it.

State and persistence behavior: per-clock state stores MMIO gate/divider/bypass pointers and fixed dividers. Parent reporting reads bypass registers, with special EMAC boot-clock bypass logic.

Dependencies/integration points: `stratix10-clk.h`, shared `clk.h`, CCF gate ops, and SoC descriptor tables.

Risks: mutable static `gateclk_ops`; family-specific bypass offset subtraction can read wrong registers if descriptors drift; debug divider has special behavior; Agilex5 uses parent-name arrays.

Test signals: gate toggling, EMAC parent under bypass modes, `cs_pdbg_clk` rate validation, and boot checks on S10/Agilex/Agilex5.
