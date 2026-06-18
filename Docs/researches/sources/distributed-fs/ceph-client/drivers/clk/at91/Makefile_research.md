# sources/distributed-fs/ceph-client/drivers/clk/at91/Makefile

Purpose: this Makefile builds Microchip/Atmel AT91 clock controller support.

Important build rules: common PMC and clock class objects (`pmc.o`, `sckc.o`, `clk-slow.o`, `clk-main.o`, `clk-pll.o`, `clk-plldiv.o`, `clk-master.o`, `clk-system.o`, `clk-peripheral.o`, `clk-programmable.o`) are always built when the directory is selected. Feature objects build for symbols such as `HAVE_AT91_AUDIO_PLL`, `HAVE_AT91_UTMI`, `HAVE_AT91_USB_CLK`, and `HAVE_AT91_GENERATED_CLK`. SoC descriptor objects are selected by SoC symbols, often with `dt-compat.o`.

Control flow/state: no runtime state; this file controls which reusable clock classes and SoC setup files are linked.

Dependencies and risks: some SoC lines include shared descriptor files multiple times under the same symbol family; object duplication is avoided by kbuild object semantics but should be reviewed when changing SoC coverage. Test signals are AT91 defconfig builds, allmodconfig, and ensuring selected SoC objects have their needed feature helpers.
