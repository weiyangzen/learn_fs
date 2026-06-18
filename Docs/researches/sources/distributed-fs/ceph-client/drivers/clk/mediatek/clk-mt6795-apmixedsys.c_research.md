# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-apmixedsys.c

## Purpose

This MT6795 apmixedsys driver registers PLLs, PLL frequency-hopping metadata, and the `ref2usb_tx` clock, then performs a modem-domain MD1 setup sequence. It is the PLL root provider for the MT6795 clock tree and supplies main, universal, multimedia, storage, video, audio, and CPU PLLs to topckgen and subsystem consumers.

## Important APIs, types, and functions

The file defines `plls[]` using `struct mtk_pll_data`, `pllfhs[]` using `struct mtk_pllfh_data`, and the helper `clk_mt6795_apmixed_setup_md1()`. The probe uses `devm_platform_ioremap_resource()`, `mtk_alloc_clk_data()`, `fhctl_parse_dt()`, `mtk_clk_register_pllfhs()`, `mtk_clk_register_ref2usb_tx()`, and `of_clk_add_hw_provider()`. Remove reverses the provider, `ref2usb_tx`, PLLFH, and onecell allocation. The compatible is `"mediatek,mt6795-apmixedsys"`.

## Control flow, state, and persistence

Probe maps the apmixedsys register bank, allocates `CLK_APMIXED_NR_CLK`, parses FHCTL data for `"mediatek,mt6795-fhctl"`, registers PLL/FH clocks, registers `ref2usb_tx` from `REG_REF2USB`, publishes the clock provider, then clears MD1 power/isolation/clock/memory-off bits in `REG_AP_PLL_CON7`. The only persistent effects are CCF registrations and hardware register writes until reset. The MD1 writes are read-modify-write sequences, so concurrent firmware ownership would matter.

## Dependencies and integration points

Dependencies include `clk-fhctl.h`, `clk-pllfh.h`, `clk-pll.h`, `clk-mtk.h`, and `dt-bindings/clock/mediatek,mt6795-clk.h`. It feeds topckgen parent names such as `mainpll`, `univpll`, `mmpll`, `msdcpll`, `vcodecpll`, `vencpll`, `tvdpll`, `apll1`, and `apll2`. FHCTL integration lets configured PLLs use spread-spectrum or DVFS-safe frequency hopping.

## Risks and test signals

Risks include incorrect PLL PCW fields, FHCTL offsets, or MD1 setup ordering causing unstable clocks or random modem crashes. The file calls `platform_get_drvdata()` in remove, so the generic registration helpers must have stored `clk_data`. Test signals are successful boot, stable MD1/modem bring-up, USB PHY reference operation, clk summary showing all PLLs, and unload/reload cleanup if built as a module.
