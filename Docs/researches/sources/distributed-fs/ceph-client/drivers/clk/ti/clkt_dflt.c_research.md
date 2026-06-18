# sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dflt.c

Purpose: default OMAP module clock operations for legacy non-clkctrl clocks. It enables/disables module clocks, coordinates clockdomain use counts, and waits for modules to leave idle through default companion/IDLEST register discovery.

Important APIs/types/functions: `omap2_dflt_clk_enable()`, `omap2_dflt_clk_disable()`, `omap2_dflt_clk_is_enabled()`, `omap2_clk_dflt_find_companion()`, `omap2_clk_dflt_find_idlest()`, and exported `clkhwops_wait`. Internal helpers `_omap2_module_wait_ready()` and `_wait_idlest_generic()` implement readiness waits.

Control flow: enable optionally enables the clockdomain, sets or clears the enable bit depending on `INVERT_ENABLE`, performs an OCP barrier read, and calls the clock's `find_idlest` path. Readiness checks optionally require a companion functional/interface clock before waiting on CM IDLEST or a generic external IDLEST register. Disable clears the hardware enable bit and decrements the clockdomain if enabled.

State and persistence: no private allocations. State is held in hardware enable/IDLEST registers and in low-level clockdomain use counts. `clkhwops_wait` plugs default `find_idlest`/`find_companion` behavior into `clk_hw_omap` instances.

Dependencies/integration: depends on `ti_clk_ll_ops` for CM register access, `ti_clk_features` for IDLEST polarity, and clockdomain callbacks. Used by gate and interface clock setup.

Risks: register offset derivation assumes old CM register layouts (`FCLKEN`, `ICLKEN`, `IDLEST`). Generic wait has a large busy-wait timeout. Incorrect feature IDLEST polarity or companion offsets can skip waits or report false failures.

Test signals: enable legacy OMAP interface/function clocks, confirm modules become ready without timeout logs, test inverted enables, and validate clockdomain use count transitions.
