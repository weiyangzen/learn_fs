# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-a10.c

Purpose: Arria10 gate-clock helper.

Important APIs/types/functions: `socfpga_gate_clk_recalc_rate()`, `__socfpga_gate_init()`, and `socfpga_a10_gate_init()`.

Control flow: parses gate/divider/fixed-divider/output-name/parent DT properties, allocates a gate clock, optionally enables CCF gate ops, registers a hardware clock, and adds a simple provider.

State and persistence behavior: allocated state stores gate, divider, and fixed-divider metadata; hardware registers store actual enable/divider state.

Dependencies/integration points: global `clk_mgr_a10_base_addr`, shared SoCFPGA `clk.h`, CCF gate ops, and OF clock nodes.

Risks: static `gateclk_ops` is mutated; helper assumes the Arria10 PLL mapper has initialized the global base; divider math is table/property-sensitive.

Test signals: Arria10 boot, gate enable/disable, divided rate inspection, and init-order validation.
