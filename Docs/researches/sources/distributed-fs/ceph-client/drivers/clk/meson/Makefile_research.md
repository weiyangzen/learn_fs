# sources/distributed-fs/ceph-client/drivers/clk/meson/Makefile

Purpose: this Makefile maps Meson Kconfig symbols to the common helper and SoC-specific clock-controller objects built by Kbuild.

Important entries: common helper objects include `meson-clkc-utils.o`, `meson-aoclk.o`, `clk-cpu-dyndiv.o`, `clk-dualdiv.o`, `clk-mpll.o`, `clk-phase.o`, `clk-pll.o`, `clk-regmap.o`, `sclk-div.o`, `vid-pll-div.o`, and `vclk.o`. Controller objects include `axg.o`, `axg-aoclk.o`, `axg-audio.o`, `a1-pll.o`, `a1-peripherals.o`, C3, GXBB, G12A, Meson8, S4, and T7 objects.

Control flow: Kbuild expands each `obj-$(CONFIG_...)` assignment based on configuration. For `COMMON_CLK_AXG`, both `axg.o` and `axg-aoclk.o` are built together. Other controllers map one symbol to one object.

State and persistence: this file has no runtime state. It contributes build graph state during kernel compilation.

Dependencies and integration points: it relies on Kconfig to select helper symbols before SoC objects that reference them. It integrates with module or built-in builds through standard Kbuild `obj-*` semantics.

Risks: object lists must stay synchronized with Kconfig and source files. Missing helper objects surface as unresolved symbols, while stale object entries break builds when files are removed. Bundling `axg.o axg-aoclk.o` under one symbol means AXG main and AO clock support are compiled together.

Test signals: compile all Meson clock configs as built-in and modules under `ARCH_MESON`/ARM64 and `COMPILE_TEST`. Confirm `modules.order` and built object lists include the expected files for each selected symbol.
