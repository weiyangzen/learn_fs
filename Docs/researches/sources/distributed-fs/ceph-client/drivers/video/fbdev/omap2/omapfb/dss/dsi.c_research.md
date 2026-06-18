# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dsi.c

## Purpose

This file implements the OMAP DSS MIPI DSI host/output driver. It owns the DSI protocol engine, ComplexIO PHY, DSI PLL, virtual-channel packet I/O, command/video-mode timing calculation, lane configuration, TE/framedone update handling, runtime PM, IRQ dispatch, DT child population, and output registration. The complete 5,585-line source was read.

## Important APIs, Types, and Functions

The main state is `struct dsi_data`, which stores mapped protocol/PHY/PLL bases, module id, IRQ, runtime enable flag, fclk and PLL objects, regulator state, four VC records, mutex and bus semaphore, IRQ callback tables, command update state, TE/ULPS flags, framedone timeout work, clock/timing caches, lane configuration, line buffer size, manager config, current DSS DSI mode, and the registered `omap_dss_device`.

The exported/registered surface is `dsi_init_platform_driver()`, `dsi_uninit_platform_driver()`, `dsi_dump_clocks()`, `dsi_get_pixel_size()`, and `omapdss_dsi_ops`: bus lock/unlock, enable/disable, high-speed enable, pin configure, config set, video-output enable/disable, update, TE enable, VC allocation/id/release, DCS and generic reads/writes, BTA sync, and max RX packet size.

Important internal clusters are IRQ handling (`omap_dsi_irq_handler()`, ISR table registration, error/stat collection), PLL/runtime/regulator (`dsi_pll_enable()`, `dsi_pll_uninit()`, `dsi_set_lp_clk_divisor()`), ComplexIO (`dsi_cio_init()`, `dsi_cio_timings()`, `dsi_enter_ulps()`), VC packet I/O (`dsi_vc_send_short()`, `dsi_vc_send_long()`, `dsi_vc_read_rx_fifo()`), display lifecycle (`dsi_display_init_dsi()`, `dsi_display_init_dispc()`, `dsi_enable_video_output()`), and timing calculation (`dsi_cm_calc()`, `dsi_vm_calc()`, `dsi_vm_calc_blanking()`).

## Control Flow

Probe adds a component. Bind allocates `dsi_data`, initializes locks/work/timers, maps protocol/PHY/PLL register windows by name or legacy offsets, requests the shared IRQ, resolves module id from DT compatible/address or platform id, initializes VC state, gets clocks, registers a DSS PLL, enables runtime PM, reads revision/lane capabilities, computes line buffer size, registers `dsi.0` or `dsi.1`, parses DT lanes, populates DSI child devices, and adds debugfs dumps.

Panel drivers first lock the DSI bus, configure pins, call `set_config()` to calculate PLL, DISPC, LP clock, and DSI video timings, connect the output, and then enable. Enable gets runtime PM, initializes IRQ masks, enables/configures the DSI PLL, switches DSS DSI clock source to the PLL hsdiv, powers/configures ComplexIO lanes, programs PHY/protocol timings, sets LP divisor and FIFO/VC state, enables all VCs and the interface, and forces TX stop mode. Video output then initializes DISPC, optionally programs a video-mode long-packet header, and enables the manager. Command-mode updates configure the update VC to video-port source, program TE size/header, schedule a framedone timeout, start DISPC update, and optionally wait for TE through BTA. Disable synchronizes all VCs, optionally enters ULPS, disables interface/VCs, restores DSS clock sources, powers down ComplexIO/PLL, and drops runtime PM.

## State and Persistence Behavior

State is volatile but extensive: PLL clock info, LP clock divisors, VC ownership and VC IDs, lane mappings/polarity, runtime PM enabled flag, regulator enable flag, TE/ULPS state, pending framedone callback data, IRQ error bits, optional IRQ statistics, and current DSS/DISPC/DSI timings. Hardware-visible state spans DSI IRQ masks/status, VC FIFOs, protocol timing registers, PHY timing/config registers, PLL registers, DSS clock muxes, DISPC manager state, pad enable state, and regulator power. No file-backed persistence exists.

## Dependencies and Integration Points

The driver depends on MIPI DSI packet definitions, OMAP DSS output/manager APIs, DISPC clock and manager helpers, DSS PLL framework, DSS feature flags and SoC limits, Linux regulator/clock/runtime-PM/IRQ/debugfs/OF/component infrastructure, and `of_platform_populate()` for child panel devices. It integrates with DSS pad control through `dss_dsi_enable_pads()`, with DSS clock muxes through `dss_select_dsi_clk_source()` and `dss_select_lcd_clk_source()`, and with panel drivers through `omapdss_dsi_ops`.

## Risks and Edge Cases

This file has many timing-sensitive paths. DSI clock calculations reject configurations when DISPC and DSI throughput cannot be aligned, when blanking cannot fit, or when LP clock bounds fail. VC operations assume the caller holds the bus semaphore, and several helpers only warn rather than enforce. Long writes are limited by the configured TX FIFO size. BTA/read paths can timeout or surface ACK-with-error packets. ULPS exit uses manual lane override because hardware reset state does not know prior ULPS state. Runtime suspend uses `is_enabled`, memory barriers, and `synchronize_irq()` to stop IRQ access before clocks are removed. Some cleanup paths depend on balanced SCP clock refcounts, regulator flags, and optional lane disconnect. DT module id matching is address-based, so resource start addresses must match the static tables.

## Test Signals

Validation should cover OMAP3/4/5 DSI probe, both DSI modules where present, DT lane parsing with polarity, child panel population, runtime suspend/resume with IRQ storms, regulator deferral, PLL registration and clock calculation boundaries, command-mode DCS/generic short/long write/read/BTA flows, video-mode pulse/event/burst timings, TE enabled and missing-TE timeout paths, framedone timeout and success paths, ULPS enter/exit cycles, VC allocation/id errors, FIFO overflow/underflow IRQ reporting, and debugfs clock/register/IRQ dumps while displays are active and suspended.
