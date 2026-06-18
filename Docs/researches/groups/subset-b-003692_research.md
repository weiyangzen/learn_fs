# subset-b-003692 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc.h

## Purpose
`dispc.h` is the DISPC register-address contract shared by the DISPC implementation and scaling coefficient provider. It defines common register offsets, overlay register address macros, the FIR coefficient structure, the coefficient lookup prototype, and inline helpers that map logical OMAP channels/planes to the register offsets used by different generations of the OMAP display controller.

## Important APIs, Types, And Data
- Common register constants cover revision, sysconfig/status, IRQ status/enable, control/config registers, global alpha, multiple LCD manager controls/configs, clock divisor, global FIFO/MFLAG control, and gamma table registers.
- Overlay register macros such as `DISPC_OVL_BA0(n)`, `DISPC_OVL_ATTRIBUTES(n)`, `DISPC_OVL_FIR(n)`, `DISPC_OVL_CONV_COEF(n, i)`, `DISPC_OVL_PRELOAD(n)`, and `DISPC_OVL_MFLAG_THRESHOLD(n)` compose a plane base address with a plane-specific offset helper.
- `struct dispc_coef` contains five signed/unsigned coefficient fields used by the scaler writer in `dispc.c`; `dispc_ovl_get_scale_coef()` is implemented in `dispc_coefs.c`.
- Manager helpers include `DISPC_DEFAULT_COLOR()`, `DISPC_TRANS_COLOR()`, `DISPC_TIMING_H/V()`, `DISPC_POL_FREQ()`, `DISPC_DIVISORo()`, `DISPC_SIZE_MGR()`, `DISPC_DATA_CYCLE1/2/3()`, and `DISPC_CPR_COEF_R/G/B()`.
- Overlay helpers include `DISPC_OVL_BASE()` and per-plane offsets for base addresses, UV addresses, position, size, attributes, FIFO threshold/status, row/pixel increments, GFX CLUT/window skip, FIR/FIR2, picture size, accumulator registers, FIR coefficient arrays, color conversion coefficients, preload, and MFLAG thresholds.

## Control Flow
This header has no runtime control flow beyond inline switch dispatch. The caller supplies `enum omap_channel` or `enum omap_plane_id`; the helper returns the hardware offset for that logical resource. Unsupported combinations call `BUG()` and return zero only to satisfy control-flow analysis. `dispc.c` uses these helpers in register read/write macros, context save/restore, debugfs dumping, overlay setup, timing programming, FIFO initialization, gamma restore, and errata workarounds.

## State And Persistence Behavior
`dispc.h` stores no mutable state. Its constants are compile-time mappings from logical DSS resources to hardware register offsets. The only persistent contract is ABI-like within the driver: if a helper maps a plane/channel incorrectly, every user of that macro writes the wrong MMIO address.

## Dependencies And Integration Points
The header depends on local enum definitions from `omapdss.h` being visible before use, kernel integer types, and `BUG()`. It is included by `dispc.c` and `dispc_coefs.c`. It encodes hardware layout knowledge from OMAP2 through OMAP5/DRA7 DISPC generations, including special offsets for VIDEO3 and writeback, which differ from earlier GFX/VIDEO1/VIDEO2 layouts.

## Risks And Edge Cases
- The helper functions intentionally crash on invalid channels/planes. This is appropriate for internal invariants but makes caller-side validation important.
- Some helpers are only valid for LCD managers and reject DIGIT; others are invalid for GFX or writeback. Misusing generic-looking macros can hit `BUG()` or write nonsensical offsets.
- `DISPC_OVL_MFLAG_THRESHOLD(n)` expands directly to an absolute offset helper, unlike most overlay macros that add `DISPC_OVL_BASE(n)`. This is correct for the global MFLAG threshold register layout but easy to misuse if assumed to follow the base-plus-offset pattern.
- Offset differences for VIDEO3/WB and second UV/scaler registers are subtle. Adding a new plane or SoC generation requires a full audit of every switch.

## Test Signals
Compile coverage is the first signal because many helpers are inline. Additional validation can assert known offsets for every manager and plane, exercise debugfs register dump address coverage, and run plane setup paths for each plane type to ensure no valid caller path reaches a `BUG()`. Hardware bring-up should compare dumped register addresses against the TRM for OMAP2/3/4/5/DRA7 and verify VIDEO3/WB/NV12 paths specifically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc_coefs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc_coefs.c

## Purpose
`dispc_coefs.c` provides the scaler FIR coefficient tables used by DISPC overlay programming. It isolates the static 3-tap and 5-tap coefficient sets from the main controller code and exposes a single lookup function that maps a requested FIR increment to the closest supported hardware table.

## Important APIs, Types, And Data
- The file defines paired arrays `coef3_M*` and `coef5_M*`, each with eight `struct dispc_coef` entries for the eight FIR phases. The suffix represents the coefficient family selected by the normalized increment bucket.
- `dispc_ovl_get_scale_coef(int inc, int five_taps)` is the only function. It returns a pointer to one of the static coefficient arrays or `NULL` if the increment falls outside known buckets.
- The tables cover downscaling and upscaling buckets: direct buckets from `M8` through `M32`, plus special upscaling buckets for normalized increments 3, 2, and 0..1 that intentionally use `M11`, `M16`, and `M19` to avoid visible artifacts.

## Control Flow
The lookup divides the caller-supplied increment by 128, then scans a small ordered table of `{Mmin, Mmax, coef_3, coef_5}` descriptors. On the first inclusive range match it returns either the 5-tap or 3-tap coefficient pointer depending on `five_taps`. If no range matches, it returns `NULL`; `dispc.c` logs an error and skips coefficient programming in that case.

## State And Persistence Behavior
All coefficient tables are `static const`; the file has no mutable state, allocation, hardware access, or persistence. Returned pointers remain valid for the lifetime of the module and are read by `dispc_ovl_set_scale_coef()` when programming FIR registers.

## Dependencies And Integration Points
The file depends on `struct dispc_coef` and `dispc_ovl_get_scale_coef()` declared in `dispc.h`, local DSS definitions from `omapdss.h`, and `ARRAY_SIZE` from the kernel. Its only direct integration point is the scaler code in `dispc.c`, which separately requests horizontal coefficients and vertical coefficients, with vertical selection depending on whether five-tap mode is active.

## Risks And Edge Cases
- `inc` is integer-divided by 128 before matching, so boundary behavior depends on truncation. Incorrect increment calculation in the caller can select a neighboring coefficient family.
- The function accepts `int five_taps` rather than `bool`; any nonzero value selects 5-tap coefficients.
- Returning `NULL` leaves the caller unable to program coefficients. Current caller logs but does not fail the whole overlay setup at that exact point, so prior validation must keep increments inside supported ranges.
- Visual quality depends on these magic tables. Changes need image-quality and artifact testing, not just compile testing.

## Test Signals
Unit-level tests can cover bucket boundaries after `inc / 128`, special upscaling mappings for normalized increments 0..3, and 3-tap versus 5-tap selection. Integration tests should exercise scaling ratios around bucket edges, five-tap fallback behavior, and visual/hardware validation for upscaling beyond 2x where the special tables are used to reduce blockiness/outlines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc_coefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dpi.c

## Purpose
`dpi.c` implements the OMAP DSS DPI output as a DRM bridge. It chooses the DISPC manager channel and clock source for a DPI port, computes and applies PLL/DSS/DISPC clock divisors for a requested display mode, configures LCD manager parameters, sequences regulator/PLL/DISPC enablement, and registers an `omap_dss_device` output connected to the next bridge in the device-tree graph.

## Important APIs, Types, And Data
- `struct dpi_data` is the private output state: platform device, DSS model, parent `dss_device`, DPI port id, optional OMAP3-family `vdds_dsi` regulator, selected DSS clock source, optional PLL, LCD manager config, current pixel clock, data-line count, `omap_dss_device` output, and embedded `drm_bridge`.
- `struct dpi_clk_calc_ctx` carries clock-search inputs and outputs across nested DSS/PLL/DISPC divisor callbacks: pixel clock min/max, PLL clock info, selected fck, and DISPC divider info.
- DRM bridge operations are `dpi_bridge_attach`, `dpi_bridge_mode_valid`, `dpi_bridge_mode_fixup`, `dpi_bridge_mode_set`, `dpi_bridge_enable`, and `dpi_bridge_disable`.
- Public lifecycle functions are `dpi_init_port()` and `dpi_uninit_port()`, called by DSS core while walking output ports.

## Control Flow
Initialization starts in `dpi_init_port()`. It allocates `struct dpi_data` as a managed DRM bridge object, finds the first endpoint, reads the endpoint `data-lines` property, stores parent/model references, initializes any needed OMAP3-family `vdds_dsi` regulator, and calls `dpi_init_output_port()`. Output-port initialization adds the DRM bridge, reads the port `reg` number as `dpi->id`, names the output (`dpi.0`..`dpi.2`), selects a hardcoded manager channel with `dpi_get_channel()`, initializes/registers the `omap_dss_device`, and links it to the bridge. Cleanup unregisters the output and removes the bridge.

Clock source selection is model-specific. OMAP2/3 use FCK because sharing DSI PLL with DISPC fclk can break other outputs. OMAP4/5 use fixed PLL outputs for certain LCD managers. DRA7 probes available PLL sources per LCD channel and falls back to FCK. `dpi_init_pll()` verifies a candidate PLL by enabling/disabling it once before storing it.

Mode validation and fixup call `dpi_clock_update()`, which attempts either PLL-backed clock calculation or DSS fck/divider calculation and returns the realizable pixel clock. `dpi_pll_clk_calc()` handles PLL type A through nested PLL, HSDIV, and DISPC divider searches; PLL type B uses direct PLL calculation with 1:1 DISPC divisors. `dpi_dss_clk_calc()` widens the accepted pixel-clock range over multiple attempts because FCK-only clocking has few exact combinations.

Bridge enable sequences hardware in dependency order: enable `vdds_dsi` if present, runtime-get DISPC, select the DPI source for this port/channel, enable the PLL if present, set the mode clocks, configure LCD manager state (`DSS_IO_PAD_MODE_BYPASS`, no stall/FIFO handcheck, data-line width, lcden polarity), delay 2 ms, enable the manager, and finally call `omapdss_device_enable()` for downstream output state. Error labels unwind PLL, DISPC runtime PM, and regulator. Disable reverses output/manager, switches LCD clock source back to FCK when a PLL was used, disables PLL, releases DISPC runtime PM, and disables the regulator.

## State And Persistence Behavior
The file persists no on-disk state. Runtime state lives in `dpi_data` and in DSS/DISPC hardware: selected pixel clock, manager divisor config, selected clock source, PLL configuration, regulator enable count, and the bridge/output registration. `port->data` stores the `dpi_data` pointer for uninitialization. Mode setting stores `adjusted_mode->clock * 1000` in `dpi->pixelclock`; actual hardware programming is deferred to bridge enable.

## Dependencies And Integration Points
`dpi.c` depends on Linux clk/regulator/platform/of_graph/SoC helpers, DRM bridge APIs, and local DSS/DISPC/PLL helpers. It integrates tightly with `dispc.c` through `dispc_runtime_get/put` and `dispc_div_calc`, with DSS core through `dss_select_lcd_clk_source`, `dss_dpi_select_source`, `dss_set_fck_rate`, `dss_div_calc`, `dss_mgr_set_lcd_config`, `dss_mgr_enable/disable`, and with PLL providers through `dss_pll_*`. Device tree supplies the DPI port number and endpoint `data-lines`; downstream bridge attachment requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR`.

## Risks And Edge Cases
- The manager-channel mapping is hardcoded by DSS model and DPI id. New boards or SoCs with different routing need code changes.
- DPI bridge attach rejects callers that expect it to create a connector; the DRM pipeline must attach with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`.
- Mode validation rejects widths not divisible by 8 and zero clocks. FCK-only clocking may accept an adjusted clock significantly widened from the requested target because the search range expands up to roughly 15 MHz.
- High pixel clocks skip odd LCD/pixel dividers to avoid duty-cycle problems after level shifting, which can reduce available modes.
- Enable failure paths must keep regulator, PLL, and runtime PM balanced; regression here can leave clocks/regulators on or DISPC references leaked.
- `dpi_init_port()` returns success when no endpoint exists, leaving no output initialized for that port; callers must treat this as an absent graph connection rather than a fatal error.

## Test Signals
Validation should include mode-valid/fixup tests for zero clock, non-8-aligned widths, PLL and FCK clock paths, high-clock odd-divider filtering, DRA7 source fallback, and adjusted clock results. Integration tests should cover bridge attach flags, enable/disable reference balancing with and without PLL/regulator, regulator probe deferral, missing endpoint behavior, data-lines parsing, port `reg` to output name/id/channel mapping, and full DRM modeset smoke tests on OMAP2/3/4/5/DRA7 hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dpi.c -->
