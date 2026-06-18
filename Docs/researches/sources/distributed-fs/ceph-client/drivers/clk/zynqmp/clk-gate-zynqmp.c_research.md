# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-gate-zynqmp.c

Purpose: implements firmware-controlled gate clocks for ZynqMP and Versal clock topologies.

Important APIs/types/functions: `struct zynqmp_clk_gate` wraps `clk_hw`, firmware flags, and `clk_id`. `zynqmp_clk_register_gate()` allocates and registers the gate. `zynqmp_clk_gate_enable()`, `zynqmp_clk_gate_disable()`, and `zynqmp_clk_gate_is_enabled()` call PM firmware clock enable/disable/getstate APIs.

Control flow: the main clock controller discovers a topology node of type `TYPE_GATE` and calls this registration helper. Runtime CCF operations translate directly to `zynqmp_pm_clock_enable()`, `zynqmp_pm_clock_disable()`, and `zynqmp_pm_clock_getstate()`.

State and persistence: gate state is owned by platform firmware and hardware. The driver keeps only the `clk_id` and flags in heap memory for the life of the registered clock.

Dependencies and integration points: depends on CCF, `clk-zynqmp.h`, and `linux/firmware/xlnx-zynqmp.h` PM calls. Integrated by `clkc.c` through the topology function table.

Risks: `num_parents` passed to the helper is ignored and `init.num_parents` is hardcoded to 1. Firmware errors are mostly debug-logged; disable failures cannot propagate through the void CCF callback. The `flags` member is stored but not used.

Test signals: enable/disable/is_enabled operations on gate clocks, firmware error-path tracing, clock summary validation, and peripheral probe tests that require gate transitions.
