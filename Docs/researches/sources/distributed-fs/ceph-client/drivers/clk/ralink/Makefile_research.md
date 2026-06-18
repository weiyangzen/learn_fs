# sources/distributed-fs/ceph-client/drivers/clk/ralink/Makefile

Purpose: This Makefile maps Ralink clock Kconfig symbols to object files.

Important APIs, types, and functions: It has two object assignments: `obj-$(CONFIG_CLK_MT7621) += clk-mt7621.o` and `obj-$(CONFIG_CLK_MTMIPS) += clk-mtmips.o`.

Control flow: During kernel build, kbuild expands the two `obj-$()` expressions based on Kconfig values. Enabled symbols compile the corresponding clock/reset provider into the built-in object list for this directory.

State and persistence: No runtime state. It affects build graph state only.

Dependencies and integration: This file is consumed by kbuild after the parent clock Makefile descends into `drivers/clk/ralink`. It depends on symbol definitions in the adjacent Kconfig and on the two C files existing with matching names.

Risks: The simplicity reduces risk. The main risk is stale symbol/object naming if either C file or Kconfig symbol is renamed. Because these drivers use `arch_initcall` and `CLK_OF_DECLARE_DRIVER`, build inclusion directly affects early boot clock availability.

Test signals: Configure each symbol independently and run `make drivers/clk/ralink/`. Inspect build logs or `scripts/Makefile.build` output to ensure only the selected object compiles.
