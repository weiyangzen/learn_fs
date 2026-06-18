# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-zynqmp.h

Purpose: defines shared ZynqMP clock topology types, firmware flag bits, and registration prototypes used by all clock subdrivers.

Important APIs/types/functions: `enum topology_type`, `struct clock_topology`, common flag macros such as `ZYNQMP_CLK_SET_RATE_PARENT`, divider/mux type flags, `zynqmp_clk_map_common_ccf_flags()`, and `zynqmp_clk_register_pll/gate/divider/mux/fixed_factor()`.

Control flow: `clkc.c` fills `struct clock_topology` entries from firmware query responses and dispatches to the registration functions declared here.

State and persistence: no state; it is a compile-time contract between the topology parser and the individual clock implementations.

Dependencies and integration points: includes `linux/firmware/xlnx-zynqmp.h` for PM APIs and `linux/spinlock.h`; consumed only by the ZynqMP clock directory.

Risks: flag definitions must stay synchronized with firmware ABI encoding. Reusing names similar to generic CCF flags can hide bit-number mismatches. `MAX_NODES` and topology type enum assumptions in `clkc.c` depend on these definitions remaining stable.

Test signals: successful build of all ZynqMP clock objects, firmware topology parsing across PLL/divider/mux/gate/fixed-factor nodes, and ABI compatibility tests with PM firmware versions.
