# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.c

Purpose: this file implements OWL mux clocks and mux helper routines used by composites.

Important functions: `owl_mux_helper_get_parent()` reads the mux register, shifts and masks the parent index, and returns it. `owl_mux_helper_set_parent()` clears the mux bitfield and writes the requested parent index. `owl_mux_ops` exposes get/set parent plus `__clk_mux_determine_rate`.

Control flow/state: parent selection is stored in a hardware register field. There is no software cache or validation of index range inside the helper; the common clock framework supplies the selected index from registered parents.

Dependencies and integration: depends on regmap and common clock mux helpers. Used by standalone `OWL_MUX` declarations and by all mux-capable composite clocks.

Risks and tests: the mask expression `BIT(width) - 1` assumes `width` is the number of bits and must be nonzero and sensible. Set-parent does not preserve invalid-index protection at this layer. Test signals are parent switching under `clk_set_parent()`, rate determination with parent changes, and register field inspection.
