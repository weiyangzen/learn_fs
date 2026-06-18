# sources/distributed-fs/ceph-client/drivers/clk/ti/dpll.c

Purpose: device-tree registration layer for TI/OMAP DPLL clocks. It binds compatible strings to appropriate `clk_ops` and `dpll_data` templates, parses DPLL register resources and optional spread-spectrum data, and registers DPLL or DPLLx2 clocks with CCF.

Important APIs/types/functions: `_register_dpll()`, `_register_dpll_x2()`, `of_ti_dpll_setup()`, and many `CLK_OF_DECLARE()` setup functions for OMAP2, OMAP3, OMAP4, OMAP5, AM3, AM4, DRA7, J-type, M4XEN, no-gate, and x2 variants. It wires ops from `clkt_dpll.c`, `dpll3xxx.c`, and `dpll44xx.c`.

Control flow: setup duplicates a DPLL data template, allocates `clk_hw_omap` and `clk_init_data`, fills parent names, parses control/idlest/mult-div/autoidle/SSC registers, reads mode properties, adjusts min divider, then calls `_register_dpll()`. `_register_dpll()` obtains clk-ref and clk-bypass parents; if unavailable, it schedules retry. Successful registration adds a simple OF clock provider and frees init-time parent arrays.

State and persistence: registered DPLL clocks keep `dpll_data` with register descriptors, masks, mode flags, parent `clk_hw` pointers, and cached rounded values. Init allocations become CCF clock state; failed registrations free them.

Dependencies/integration: depends on `clock.h`, CCF, OF, TI register mapping, SoC config guards, and DPLL runtime ops from other TI files.

Risks: compatible strings must select the exact mask template. Parent ordering is fixed: reference parent first, bypass parent second. Retry list hides order dependencies but only if callbacks eventually succeed. SSC fields are optional but must be complete to program spread spectrum.

Test signals: boot each compatible family, verify DPLL providers appear, test missing-parent retry, set rates for normal/J-type/M4XEN/no-gate variants, validate x2 recalc, and suspend/resume through save/restore ops.
