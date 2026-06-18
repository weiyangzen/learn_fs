# sources/distributed-fs/ceph-client/drivers/clk/eswin/Makefile

Purpose: maps ESWIN Kconfig symbols to build objects.

Important APIs/types/functions: `obj-$(CONFIG_COMMON_CLK_ESWIN) += clk.o` builds shared registration/PLL/divider helpers. `obj-$(CONFIG_COMMON_CLK_EIC7700) += clk-eic7700.o` builds the EIC7700 SoC provider.

Control flow: no runtime flow; kbuild includes object files based on selected symbols.

State and persistence: no runtime state.

Dependencies and integration points: the SoC provider depends on exported helper symbols from `clk.o`. Because `COMMON_CLK_EIC7700` selects `COMMON_CLK_ESWIN`, normal configurations include both.

Risks: if symbol visibility changes, `clk-eic7700.o` can be built without helper symbols. Module build combinations should ensure exported GPL helper symbols are visible to the provider.

Test signals: compile EIC7700 as built-in and module under `COMPILE_TEST`; verify no unresolved exports from `clk.o`.
