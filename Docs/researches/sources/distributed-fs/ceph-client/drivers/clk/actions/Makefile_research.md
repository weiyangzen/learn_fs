# sources/distributed-fs/ceph-client/drivers/clk/actions/Makefile

Purpose: this Makefile builds the Actions OWL common clock support and the per-SoC clock controller objects.

Important build structure: `obj-$(CONFIG_CLK_ACTIONS) += clk-owl.o` produces a composite object from `owl-common.o`, `owl-gate.o`, `owl-mux.o`, `owl-divider.o`, `owl-factor.o`, `owl-composite.o`, `owl-pll.o`, and `owl-reset.o`. The SoC files `owl-s500.o`, `owl-s700.o`, and `owl-s900.o` are built independently by their SoC Kconfig symbols.

Control flow/state: the common object contains reusable `clk_ops` and reset ops used by every SoC descriptor file. The SoC objects register platform drivers at `core_initcall` time.

Dependencies and risks: all helper object names must stay synchronized with the headers used by the SoC files. If `CLK_ACTIONS` is disabled but a SoC object is enabled, unresolved helper symbols would result; the Kconfig `if CLK_ACTIONS` nesting prevents that. Test signals are build coverage for each SoC option and link verification for `clk-owl.o`.
