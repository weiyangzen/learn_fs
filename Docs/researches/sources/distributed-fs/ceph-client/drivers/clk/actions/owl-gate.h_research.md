# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.h

Purpose: this header defines OWL gate clock descriptors, standalone gate macros, and helper prototypes.

Important types/macros: `struct owl_gate_hw` stores register offset, bit index, and gate flags. `struct owl_gate` embeds that descriptor and `owl_clk_common`. `OWL_GATE_HW` is used in composites; `OWL_GATE` and `OWL_GATE_NO_PARENT` create standalone `clk_hw` objects with or without a named parent.

Control flow/state: callbacks recover the outer `owl_gate` through `hw_to_owl_gate()` and operate on the described bit. Persistent state is the hardware gate bit.

Dependencies and integration: included by composites and SoC descriptors. It exposes `owl_gate_set()` and `owl_gate_clk_is_enabled()` for composite code.

Risks and tests: macro definitions include trailing backslashes and caller-provided initializer fragments; bad gate flags or bit indices can invert or touch the wrong clock. Gates without parents should only be used for hardware clocks whose parent relationship is unknown or irrelevant to the framework. Test signals are clock tree registration, enable-count behavior, and unused-clock disabling behavior.
