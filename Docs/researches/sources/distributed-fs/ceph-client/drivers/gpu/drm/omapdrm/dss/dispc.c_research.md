# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc.c

## Purpose
`dispc.c` is the OMAP DRM DSS Display Controller implementation. It owns the memory-mapped DISPC register block, SoC feature tables, overlay/plane programming, LCD/DIGIT manager setup, IRQ forwarding, debug register dumps, runtime PM context save/restore, gamma table handling, FIFO/MFLAG setup, and platform/component binding for `omapdss_dispc`. Higher OMAP DRM layers ask this file to validate modes, compute divider/scaler settings, program overlay state, enable managers, and expose DISPC interrupt/status operations.

## Important APIs, Types, And Data
- `struct dispc_device` is the central private state: platform device, register base, parent `dss_device`, IRQ callback, cached clocks, FIFO sizes/assignments, saved register context array, per-channel gamma tables, selected `struct dispc_features`, runtime enabled flag, and optional syscon polarity regmap.
- `struct dispc_features` describes per-SoC limits and quirks: timing field widths, max pixel clocks, scaler limits, FIFO units, manager/overlay counts, color-mode matrices, feature flags, writeback/gamma availability, errata bits, and scaling/core-clock callback functions.
- `mgr_desc[]` maps OMAP channels to names, IRQ masks, gamma-table layout, and manager control/config bitfields, allowing common code to target LCD, DIGIT, LCD2, and LCD3.
- Exported/internal integration entry points include `dispc_runtime_get/put`, `dispc_mgr_*` timing/clock/setup/enable/gamma/IRQ helpers, `dispc_ovl_*` setup/enable/capability/color-mode/FIFO helpers, `dispc_div_calc`, `dispc_calc_clock_rates`, `dispc_request_irq/free_irq`, `dispc_read_irqstatus`, `dispc_clear_irqstatus`, `dispc_write_irqenable`, `dispc_get_memory_bandwidth_limit`, and the `omap_dispchw_driver` platform driver.
- Static feature tables (`omap24xx_dispc_feats`, `omap34xx_*`, `omap36xx`, `am43xx`, `omap44xx`, `omap54xx`) select hardware limits from compatible strings plus `soc_device_match()` for OMAP3/AM variants.

## Control Flow
Probe is component based. `dispc_probe()` registers `dispc_component_ops`; `dispc_bind()` allocates `struct dispc_device`, selects the feature table, initializes the i734 gamma workaround buffer when required, maps MMIO, obtains IRQ, optionally resolves a `syscon-pol` regmap, allocates default gamma tables, enables runtime PM, performs `_omap_dispc_initial_config()`, reads the hardware revision, publishes `dss->dispc`, and creates debugfs. `dispc_unbind()` reverses debugfs, runtime PM, errata buffer, and allocation state.

Runtime resume checks whether register context was lost by reading DISPC load mode. If lost, it re-applies initial config, performs the i734 workaround on affected SoCs, restores saved registers, and reloads gamma tables before marking `is_enabled`. Runtime suspend clears `is_enabled`, synchronizes the IRQ line, and saves the full manager/overlay context gated by hardware features.

Overlay programming flows through `dispc_ovl_setup()`. It first routes the plane to a manager, then `dispc_ovl_setup_common()` validates physical addresses and color modes, adjusts interlaced field mode, calculates scaling/predecimation through the SoC-specific `feat->calc_scaling`, computes field offsets and row/pixel increments, writes base addresses including NV12 UV planes, sets color mode, burst/rotation attributes, input/output sizes, FIR coefficients, CSC coefficients, z-order, alpha, and replication. Enabling the overlay is a separate bit write through `dispc_ovl_enable()`.

Manager programming is split between content policy and timing/clock policy. `dispc_mgr_setup()` writes default color, transparency key, alpha mode, and optional CPR matrix. `dispc_mgr_set_lcd_config()` configures pad mode, stall/FIFO handcheck, LCD divisors, data-line width, LCD enable polarity, and TFT mode. `dispc_mgr_set_timings()` validates against feature limits, writes LCD timing/polarity registers or TV/double-pixel control, then writes manager size. `dispc_mgr_go()` raises GO after checking the manager is enabled and not already busy.

Clock calculation is callback based. `dispc_div_calc()` scans LCD and pixel clock divisors within hardware and policy limits and calls a caller-supplied predicate when a candidate clock pair is found. DPI and other output code use this to negotiate mode clocks. `dispc_calc_clock_rates()` simply materializes `lck` and `pck` from selected dividers.

## State And Persistence Behavior
The file persists no on-disk state. Runtime state is device-private and hardware-backed: register context is saved in `dispc->ctx`, gamma tables are cached in `dispc->gamma_table[]`, current core/TV clock rates are cached in fields, FIFO assignments are initialized at runtime, and `is_enabled` gates IRQ forwarding. PM save/restore deliberately restores CONTROL and IRQENABLE last to avoid enabling managers or interrupts before dependent registers are restored. Gamma tables are memory cached and rewritten after context loss; `dispc_mgr_set_gamma()` interpolates a DRM LUT into hardware table depth and writes immediately only when DISPC is enabled.

## Dependencies And Integration Points
This code depends on Linux platform/component/PM-runtime/MMIO/IRQ/debugfs/regmap/syscon/DMA APIs, DRM FourCC/blending/color LUT definitions, and the local DSS abstractions in `omapdss.h`, `dss.h`, and `dispc.h`. It is the hardware backend used by OMAP DRM display outputs such as DPI/DSI/HDMI/VENC through `dss->dispc`. It integrates with device tree compatible matching, optional `max-memory-bandwidth`, optional `syscon-pol`, SoC matching, debugfs register dumps, and DSS PLL/clock-source helpers (`dss_get_*`, `dss_set_*`, `dss_pll_*`).

## Risks And Edge Cases
- Many register helpers use `BUG()`/`BUG_ON()` for impossible enum values. Bad caller validation can become a kernel crash instead of a recoverable error.
- Scaler setup is dense and SoC-specific; downscale, predecimation, five-tap filtering, interlace, YUV chroma, TILER rotation, and writeback paths can fail with `-EINVAL` when limits are exceeded.
- Hardware errata/workarounds are central: OMAP3 timing restrictions, OMAP4/5 NV12 rotation workaround, GFX/WB FIFO swap, MFLAG force-on workaround, Smart Standby workaround, missing last pixel increment, and i734 gamma workaround all alter behavior by SoC.
- Runtime PM ordering matters. IRQ forwarding is blocked by `is_enabled` and `smp_wmb()` barriers; incorrect ordering could forward interrupts while registers are invalid or miss wake/resume state.
- Address math for field mode, interlaced output, YUV subsampling, and rotation can produce incorrect DMA offsets if upstream mode/fb metadata is inconsistent.

## Test Signals
Useful validation signals include KUnit or targeted tests around `dispc_div_calc()`, `dispc_calc_clock_rates()`, supported color-mode tables, and scaler failure/success boundaries; DRM mode validation on all OMAP SoC families; runtime suspend/resume with forced context loss; gamma LUT programming including default and interpolated LUTs; debugfs register dumps under active PM; plane setup for RGB, YUYV/UYVY, NV12, interlace, TILER rotation, writeback, and high downscale; IRQ request/free and IRQ gating behavior; and device-tree probing with and without optional `syscon-pol` and `max-memory-bandwidth`.
