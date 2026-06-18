# sources/distributed-fs/ceph-client/drivers/clk/Makefile

Purpose: this Makefile maps clock Kconfig symbols to common framework objects, KUnit objects, standalone clock providers, and vendor subdirectories. It is the build integration point for `drivers/clk`.

Important build APIs: `obj-$(CONFIG_HAVE_CLK)` builds legacy/common API support helpers (`clk-devres.o`, `clk-bulk.o`, `clkdev.o`). `obj-$(CONFIG_COMMON_CLK)` builds core common clock objects such as `clk.o`, `clk-divider.o`, `clk-fixed-factor.o`, `clk-fixed-rate.o`, `clk-gate.o`, `clk-mux.o`, `clk-composite.o`, `clk-fractional-divider.o`, and `clk-gpio.o`. KUnit targets compose their test object plus DT overlay objects. Standalone provider objects are listed by Kconfig symbol, while vendor directories are enabled with `obj-y` or architecture-specific symbols.

Control flow/state: no runtime state; build order controls which drivers are linked. The comments request lexicographic ordering for file-path and directory sections.

Dependencies and risks: the file depends on names matching Kconfig symbols and object filenames. Several directories are always visited (`actions`, `analogbits`, `aspeed`, many vendor folders), letting their local Makefiles decide whether objects build. Misordered or missing entries create link gaps, unbuilt drivers, or stale Kconfig options. Test signals include allmodconfig, allyesconfig, vendor defconfigs, and KUnit target builds.
