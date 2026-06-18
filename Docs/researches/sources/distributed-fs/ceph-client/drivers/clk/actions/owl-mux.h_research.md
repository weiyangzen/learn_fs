# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.h

Purpose: this header declares the OWL mux descriptor model and standalone mux macro.

Important types/macros: `struct owl_mux_hw` stores register offset, shift, and width. `struct owl_mux` embeds the descriptor and `owl_clk_common`. `OWL_MUX_HW` creates reusable descriptors for composites; `OWL_MUX` creates a standalone parent-array clock initialized with `CLK_HW_INIT_PARENTS`.

Control flow/state: mux callbacks convert `clk_hw` back to `owl_mux` and operate on the descriptor's register field. State is the parent index persisted in hardware.

Dependencies and integration: consumed by `owl-mux.c`, `owl-composite.h`, and SoC files for CPU, bus, and device source selection.

Risks and tests: parent arrays must stay in the same order as the hardware mux encoding. A width mismatch will expose wrong parents or overwrite neighboring bits. Test signals are DT-visible clock parent names, parent index reads after bootloader configuration, and explicit parent switching tests.
