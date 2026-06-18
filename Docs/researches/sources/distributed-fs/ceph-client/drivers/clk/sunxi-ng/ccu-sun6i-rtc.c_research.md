# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.c

## Purpose

This file provides a reusable RTC-domain CCU setup for newer Allwinner RTC blocks, currently matched for H616, R329, and A523 style RTC compatibles. It models the internal 16 MHz RC oscillator, derived/calibrated 32 kHz clocks, external 32 kHz gate, RTC 32 kHz mux, 24 MHz-derived 32 kHz gate, and osc32k fanout.

## Important APIs, types, and functions

The main exported function is `sun6i_rtc_ccu_probe(struct device *dev, void __iomem *reg)`, not a standalone platform-driver probe. Key local types and data are `struct sun6i_rtc_match_data`, `sun6i_rtc_ccu_match`, `sun6i_rtc_ccu_desc`, `sun6i_rtc_ccu_hw_clks`, and the custom ops `ccu_iosc_ops` and `ccu_iosc_32k_ops`. Custom callbacks implement IOSC enable/disable/is_enabled, rate recalculation, accuracy reporting, and calibration prepare/unprepare.

## Control flow, state, and persistence

`sun6i_rtc_ccu_probe()` first verifies the device matches the newer RTC variants, selects per-compatible match data, and stores calibration support in the file-scope `have_iosc_calibration`. If an external 32 kHz oscillator is supported, it obtains it by `ext-osc32k` or by old unnamed binding fallback and connects `ext_osc32k_gate_clk` to the parent hardware. If no external oscillator is present, it removes that exported hw slot and narrows the osc32k mux to one parent. H616 can also force `rtc-32k` to a single parent. Finally it fills fanout parent data and calls `devm_sunxi_ccu_probe()`.

## Dependencies and integration points

The file depends on Linux clk APIs, OF matching, `linux/clk/sunxi-ng.h`, and the generic CCU gate/div/mux helpers. It integrates with RTC drivers that map the RTC register block and invoke this helper, with firmware clocks named `hosc`, `losc`, `iosc`, `pll-32k`, and optional `ext-osc32k`, and with consumers needing stable 32 kHz RTC/fanout clocks.

## Risks and test signals

Important risks are global mutable init data and the static `have_iosc_calibration`, which is acceptable for one RTC CCU instance but would be fragile if multiple differing instances were registered. Calibration register interpretation affects reported IOSC rates and 32 kHz accuracy. Test on each compatible with and without external oscillator properties, verify `rtc-32k` remains critical, check clk rates around 32768 Hz, confirm fanout parent selection, and watch for orphaned `ext-osc32k-gate` behavior.
