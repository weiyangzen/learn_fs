# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.h

Purpose: this header declares the composite OWL clock type and the macros used by SoC files to instantiate composite clocks declaratively.

Important types/macros: `union owl_rate` holds either `owl_divider_hw`, `owl_factor_hw`, or `clk_fixed_factor`. `struct owl_composite` embeds mux and gate descriptors, the rate union, optional fixed-factor ops, and `owl_clk_common`. `OWL_COMP_DIV`, `OWL_COMP_DIV_FIXED`, `OWL_COMP_FACTOR`, `OWL_COMP_FIXED_FACTOR`, and `OWL_COMP_PASS` create initialized static objects with the correct `CLK_HW_INIT*` form and ops table.

Control flow/state: the macros hard-code parent names or parent arrays, the register fields, and clock flags. Runtime callbacks use `hw_to_owl_comp()` to recover the surrounding composite object and then operate on the relevant register fields.

Dependencies and integration: depends on `owl-common`, `owl-mux`, `owl-gate`, `owl-factor`, `owl-fixed-factor`, and `owl-divider`. SoC descriptor files use these macros as their primary clock declaration language.

Risks and tests: macro arguments are not type-safe and shared register fields can be misdeclared. `OWL_COMP_DIV_FIXED` uses the divider ops without mux parents, so any accidental parent manipulation would be invalid. Test signals are compile errors for bad macro use, clock tree inspection, and exercising each composite flavor through common clock framework APIs.
