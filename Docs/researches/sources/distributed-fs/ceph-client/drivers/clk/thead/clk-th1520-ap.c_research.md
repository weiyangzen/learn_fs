# sources/distributed-fs/ceph-client/drivers/clk/thead/clk-th1520-ap.c

## Purpose

`clk-th1520-ap.c` is the T-HEAD TH1520 clock-controller driver for AP and VO clock domains. It provides PLL, mux, divider, gate, fixed-factor, and CPU DVFS-safe clock switching support through the Linux common clock framework.

## Important APIs, Types, And Functions

The file defines TH1520 PLL bitfields for feedback divider, reference divider, postdividers, bypass, VCO reset, fractional mode, and lock status. `struct ccu_common` wraps shared clock metadata and regmap state. `struct ccu_pll`, `struct ccu_div`, `struct ccu_mux`, and `struct ccu_gate` model the custom and standard CCF clock types. `ccu_div_ops` implements enable, parent, rate, and divider programming. `clk_pll_ops` implements PLL enable/disable, lock polling, rate lookup, and rate programming from discrete `struct ccu_pll_cfg` tables.

The special `c910_clk_ops` implements glitchless CPU clock DVFS by selecting the unused parent, programming that parent rate, then reparenting. `c910_clk_notifier_cb()` keeps `c910_bus_clk` below `TH1520_C910_BUS_MAX_RATE` during CPU rate changes. Static topology data defines CPU PLL0/1, GMAC, VIDEO, DPU0/1, TEE PLLs, CPU/bus/peripheral/AXI/VO dividers, AP gates, VO gates, UART muxing, and fixed-factor clocks.

## Control Flow

The platform driver matches `thead,th1520-clk-ap` and `thead,th1520-clk-vo`, each with different `th1520_plat_data`. Probe allocates a `clk_hw_onecell_data`, maps MMIO, creates a regmap, then registers PLLs, dividers, muxes, and gates from the platform-data arrays. For AP data it additionally registers `osc_12m`, `gmac-pll-clk-100m`, `emmc-sdio-ref`, and a notifier on the C910 clock. Finally it publishes the onecell provider.

PLL rate changes disable the PLL by asserting VCO reset, write the best matching table configuration, update fractional/integer mode bits, re-enable, poll `TH1520_PLL_STS`, and delay for stability. Divider rate changes temporarily clear the divider-enable bit, write the new divisor, then re-enable it; read-only dividers reject mismatched rate changes. Gate and mux clocks use standard `clk_gate_ops` and `clk_mux_ops` once their MMIO register pointers are set.

## State And Persistence Behavior

Persistent state lives in the TH1520 clock registers: PLL configuration and reset bits, mux selectors, dividers, and gate bits. The driver's static clock descriptors receive the runtime regmap or MMIO register pointer at probe. Critical flags keep CPU, bus, NPU/VP/VO infrastructure, and selected PLLs enabled. The CPU bus notifier changes divider state around CPU clock transitions and therefore has persistent hardware side effects.

## Dependencies And Integration Points

The driver depends on DT binding IDs from `thead,th1520-clk-ap.h`, CCF, regmap MMIO, platform devices, and device-tree parent index 0 for `osc_24m`. It exposes AP and VO onecell clock providers to CPU, display, HDMI, MIPI DSI, GPU, GMAC, eMMC/SDIO, UART, SPI, QSPI, I2C, GPIO, DMA, watchdog, timer, mailbox, SRAM, and NPU consumers.

## Risks And Edge Cases

The C910 path is sensitive: parent switching and the bus-divider notifier must maintain the 750 MHz bus limit during both scale-up and scale-down. The PLL code chooses nearest table entries, so unsupported requested rates silently round. Divider programming assumes the enable bit can be toggled safely around divisor writes. Divider clocks with `div_en == 0` are treated as read-only by `ccu_div_set_rate()`, so callers requesting unsupported rates will receive `-EINVAL` rather than hardware reprogramming. VO gate clocks use register offsets `0x0` and `0x4`, so the AP/VO compatible must map the correct MMIO region.

## Test Signals

Compile with `CONFIG_CLK_THEAD_TH1520_AP=y` and treat warnings around initializers as blockers. Boot TH1520 AP and VO DT nodes and inspect `clk_summary` for PLLs, C910, AP bus clocks, peripheral gates, DPU pixel clocks, HDMI, MIPI DSI, and GPU clocks. Stress CPU frequency changes while monitoring `c910-bus` rate. Exercise display pipelines, GMAC, eMMC/SDIO, UART/I2C/SPI/QSPI, timers, watchdogs, and GPIO. Validate PLL output rates against table values and register fields.
