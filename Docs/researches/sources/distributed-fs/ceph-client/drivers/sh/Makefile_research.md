# sources/distributed-fs/ceph-client/drivers/sh/Makefile

Purpose: build orchestration for SuperH specific driver subtrees and common runtime PM support.

Important build rules: `CONFIG_SH_INTC` adds `intc/`; legacy `clk/` is built for `CONFIG_HAVE_CLK` only when `CONFIG_COMMON_CLK` is not enabled; `CONFIG_MAPLE` adds `maple/`; `pm_runtime.o` is always included for this directory.

Control flow: Kbuild evaluates config symbols and descends into selected subdirectories. Runtime behavior is in the compiled objects, not this file.

State and dependencies: no runtime state. Dependencies include Kbuild, SH architecture configuration, clock framework selection, and Maple/INTC config symbols. Risks are duplicate clock framework builds if `COMMON_CLK` gating is wrong, always-built `pm_runtime.o` on unsupported configurations, and missing subdir objects when symbols move. Test signals are allmodconfig/allyesconfig builds across SuperH and COMPILE_TEST, plus object inclusion checks for legacy clk versus common clk.
