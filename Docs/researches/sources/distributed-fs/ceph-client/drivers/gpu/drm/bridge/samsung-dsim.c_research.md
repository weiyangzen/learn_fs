# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/samsung-dsim.c

## Purpose

`samsung-dsim.c` implements the Samsung/Exynos-style MIPI DSI host controller as a DRM bridge and MIPI DSI host. In this tree it supports multiple Exynos controller generations plus i.MX8MM/i.MX8MP variants through `struct samsung_dsim_driver_data`, which supplies register offsets, PLL constraints, bit positions, clock names, FIFO quirks, reset behavior, and PHY timing tables.

## Important APIs, Types, And Functions

The state type is `struct samsung_dsim` from `include/drm/bridge/samsung-dsim.h`: MIPI DSI host, DRM bridge, mapped registers, PHY, clocks, regulators, IRQs, optional TE GPIO, PLL/burst/escape clock rates, lane count, format, mode flags, mode copy, lane polarity swaps, state flags, completion, transfer spinlock/list, and platform/driver data. `struct samsung_dsim_transfer` models queued DSI packets with completion and TX/RX progress.

Key functions include exported `samsung_dsim_probe()`, `samsung_dsim_remove()`, and `samsung_dsim_pm_ops`; bridge callbacks `samsung_dsim_atomic_pre_enable()`, `atomic_enable()`, `atomic_disable()`, `atomic_post_disable()`, `atomic_check()`, `mode_set()`, and `attach()`; host ops `samsung_dsim_host_attach()`, `host_detach()`, and `host_transfer()`; register setup helpers `samsung_dsim_set_pll()`, `enable_clock()`, `set_phy_ctrl()`, `init_link()`, `set_display_mode()`, and FIFO/IRQ transfer helpers.

## Control Flow

Probe allocates the bridge, initializes transfer synchronization, records SoC data from OF match, obtains regulators and SoC-specific clocks, maps MMIO, obtains optional DSI PHY, requests the controller IRQ with `IRQF_NO_AUTOEN`, parses DT clock properties and lane polarities, enables runtime PM, configures bridge type/timings, and registers the MIPI DSI host through platform host ops.

When a DSI peripheral attaches, the host locates a child panel or graph-connected downstream bridge, wraps panels with `devm_drm_panel_bridge_add()`, adds this bridge, optionally registers a TE IRQ for command-mode panels, lets platform host ops run, then stores lanes/format/mode flags. Host transfers require `DSIM_STATE_ENABLED`, lazily initialize hardware, create a MIPI packet, enqueue a `samsung_dsim_transfer`, start FIFO writes, and wait for completion or timeout. IRQ handling acknowledges interrupt status, completes reset waits, and advances queued transfers on RX done or FIFO-empty events.

Atomic pre-enable runtime-resumes the controller and, for non-Exynos platforms, initializes the link immediately. Atomic enable programs display timings and turns on main display output. Disable clears display enable and post-disable drops runtime PM. Exynos behavior differs because downstream panel/bridge command transfers may trigger initialization.

## State And Persistence Behavior

`dsi->state` tracks enabled, initialized, command-LPM, and video-output-available state. Runtime suspend tears down clocks, IRQs, PHY, and regulators and clears initialized/CMD-LPM state. Mode, lanes, pixel format, and clock rates remain in software across runtime PM and are used to reprogram hardware. Transfers are transient list entries protected by a spinlock; completion signals synchronous callers.

## Dependencies And Integration Points

The file depends on DRM bridge/panel helpers, MIPI DSI host APIs, Linux clk/regulator/PHY/runtime PM/IRQ frameworks, OF graph, media bus formats, and MIPI display packet definitions. It exports generic probe/remove/PM symbols for platform glue and also declares i.MX8MM/i.MX8MP OF matches directly.

## Risks

PLL programming is sensitive to `pll_fin_*`, `m_min/m_max`, offsets, and requested burst/pixel clock; incorrect data can silently produce bad DSI clocks. FIFO control has generation-specific quirks such as broken header-empty reporting. Transfer completion depends on IRQ delivery; missed IRQs produce 100 ms timeouts and transfer removal. `samsung_dsim_parse_dt()` assumes an endpoint when counting data lanes and can be fragile on malformed DT. i.MX sync-polarity and HFP lane rounding in `atomic_check()` are platform-specific behavioral adjustments that can affect mode compatibility.

## Test Signals

Signals include probe on each supported compatible, correct runtime PM regulator/clock/PHY sequencing, DSI panel attach/detach, command-mode transfers including reads and BTA, video-mode enable with stable PLL and stop-state detection, TE IRQ delivery for command panels, suspend/resume with reinitialization, and mode tests around lane counts and i.MX polarity/HFP adjustment.
