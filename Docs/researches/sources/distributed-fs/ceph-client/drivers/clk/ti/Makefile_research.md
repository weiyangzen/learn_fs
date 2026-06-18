# sources/distributed-fs/ceph-client/drivers/clk/ti/Makefile

## Purpose

The TI clock Makefile selects the common TI/OMAP clock framework objects and SoC-specific clock initialization files for OMAP2+, AM33xx, TI81xx, OMAP3/4/5, DRA7xx, AM43xx, and the optional ADPLL platform driver.

## Important APIs, Types, And Functions

When `CONFIG_ARCH_OMAP2PLUS=y`, `obj-y` includes foundational objects `clk.o`, `autoidle.o`, and `clockdomain.o`. `clk-common` expands to DPLL, composite, divider, gate, fixed-factor, mux, APLL, clock-type, and clkctrl helpers. SoC blocks add `clk-33xx.o`, `clk-814x.o`, `clk-816x.o`, `clk-2xxx.o`, `clk-3xxx.o`, `clk-44xx.o`, `clk-54xx.o`, `clk-7xx.o`, `clk-dra7-atl.o`, and DPLL variant files as needed. Outside the OMAP2PLUS block, `obj-$(CONFIG_COMMON_CLK_TI_ADPLL) += adpll.o` builds the ADPLL driver.

## Control Flow

Kbuild evaluates SoC config symbols and includes the correct combination of shared clock infrastructure and SoC init data. The ADPLL object is controlled independently by its own Kconfig symbol.

## State And Persistence Behavior

This file has no runtime state. Build composition determines which init functions, clock data tables, and platform drivers are available.

## Dependencies And Integration Points

The Makefile encodes coupling between SoC init files and helper implementations. For example, OMAP3 and AM33xx need `dpll3xxx.o`, OMAP4/5/DRA7 need `dpll44xx.o`, and legacy OMAP2/3 include `interface.o`.

## Risks And Edge Cases

Incorrect object combinations can compile but fail at runtime with missing init symbols or unregistered clock types. New SoC support must include both common helper files and the right DPLL variant. Moving `adpll.o` inside the OMAP2PLUS conditional would reduce compile-test coverage and break module builds for its independent symbol.

## Test Signals

Run representative builds for AM33xx, AM43xx, OMAP2, OMAP3, OMAP4, OMAP5, DRA7xx, TI81xx, and `COMMON_CLK_TI_ADPLL=m`. Link errors are strong signals of missing Makefile dependencies.
