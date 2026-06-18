# subset-b-005568 Research

Grouped source research for the OMAP2/3/4/5/DRA7 DSS DPI, DSI, DSS core, DSS feature tables, and HDMI4 files. Each section is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dpi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dpi.c

## Purpose

This file implements the OMAP DSS DPI output driver. It registers a DPI `omap_dss_device`, parses DT display ports when present, connects the output to a downstream panel/encoder, calculates pixel clocks from either the DSS functional clock or a DSI/video PLL, programs the LCD manager, and enables/disables the display path. The complete 887-line source was read.

## Important APIs, Types, and Functions

Private state is `struct dpi_data`, containing the platform device, optional `vdds_dsi` regulator, optional `struct dss_pll`, mutex, cached timings, LCD manager config, data-line width, output device, and DT port initialization flag. The external surface is `dpi_init_platform_driver()`, `dpi_uninit_platform_driver()`, `dpi_init_port()`, and `dpi_uninit_port()`, plus the `omapdss_dpi_ops` callbacks: `connect`, `disconnect`, `enable`, `disable`, `check_timings`, `set_timings`, `get_timings`, and `set_data_lines`.

Key helpers are `dpi_get_pll()`, `dpi_get_alt_clk_src()`, `dpi_dsi_clk_calc()`, `dpi_dss_clk_calc()`, `dpi_set_dsi_clk()`, `dpi_set_dispc_clk()`, `dpi_set_mode()`, `dpi_config_lcd_manager()`, `dpi_init_regulator()`, `dpi_init_pll()`, and `dpi_get_channel()`.

## Control Flow

Non-DT probing registers a component; bind allocates `dpi_data`, initializes its lock, and registers `dpi.0`. DT DSS port initialization allocates one `dpi_data` per port, reads endpoint `data-lines`, derives the port name and DISPC channel from SoC generation and `reg`, and registers the output.

Connect initializes the regulator and optional PLL, obtains the hardcoded overlay manager for the output channel, connects the manager, then links the downstream device. Enable is serialized by `dpi->lock`: it verifies regulator/manager availability, enables `vdds_dsi` on older SoCs that require it, gets DISPC runtime PM, selects the DPI source in DSS, enables the PLL if used, computes and programs clocks/timings, sets LCD manager config, delays 2 ms, and enables the manager. Disable reverses manager enable, clock source, PLL, DISPC PM, and regulator state.

Clock selection first tries an exact DSI/video PLL path when available; otherwise it widens the acceptable pixel-clock range across repeated DSS fclk/divider searches. High pixel clocks reject odd dividers to avoid uneven duty cycles through level shifters.

## State and Persistence Behavior

All state is in memory and hardware registers. Cached state includes requested/current timings, data-line width, manager clock config, optional PLL pointer, and regulator pointer. Enable mutates DSS clock-source registers, DISPC manager timing/config registers, PLL configuration, runtime PM references, and regulator state. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on the OMAP DSS output/manager API, DISPC runtime and divider helpers, DSS PLL registration, DSS feature flags, Linux regulators, OF graph parsing, and the component framework. It integrates with `dss.c` for port initialization and source muxing, `dss_features.c` for SoC limits/features, `pll.c`/`video-pll.c`/DSI PLL providers for clock generation, and downstream panel drivers through `omapdss_output_set_device()`.

## Risks and Edge Cases

Pixel-clock calculation may silently adjust `timings->pixelclock` when exact rates are unavailable. Several channel choices are hardcoded by SoC generation, so unusual board routing depends on DT port numbering matching driver assumptions. DT `dpi_init_port()` returns success without initializing anything if a port has no endpoint, so `dpi_uninit_port()` relies on `port_initialized` only after `port->data` exists. PLL verification temporarily enables the PLL and can cause probe failure or fallback to DSS fclk if a DSI/video PLL is not operational. Error paths must preserve regulator, DISPC runtime PM, PLL, and manager balance.

## Test Signals

Useful validation includes boot/probe on OMAP3, OMAP4, OMAP5, AM43xx, and DRA7 variants; DT ports with `reg` 0/1/2 and valid `data-lines`; connect/disconnect to panels; enable/disable loops under runtime PM; pixel-clock checks around 100 MHz and rates requiring widened DSS fclk tolerance; regulator deferral/failure injection; PLL unavailable/failing cases; and visible output timing validation with DISPC manager register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dsi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss-of.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss-of.c

## Purpose

This file provides small OF graph helpers for OMAP DSS. It finds the device node owning a DSS port, reads a port number, and resolves the DSS source output connected to the first endpoint of a downstream device. The complete 78-line source was read.

## Important APIs, Types, and Functions

The public helpers are `dss_of_port_get_parent_device()`, `dss_of_port_get_port_number()`, and exported `omapdss_of_find_source_for_first_ep()`. They operate on `struct device_node`, OF graph endpoints and remote ports, and `struct omap_dss_device` returned by `omap_dss_find_output_by_port_node()`.

## Control Flow

`dss_of_port_get_parent_device()` walks up at most two parents from a port until it finds a node with a `compatible` property, returning a referenced node or `NULL`. `dss_of_port_get_port_number()` reads `reg`, defaulting to 0. `omapdss_of_find_source_for_first_ep()` gets endpoint 0 from a consumer node, finds its remote port, resolves that port to a registered OMAP DSS output, drops OF references, and returns either the output or `ERR_PTR(-EPROBE_DEFER)` if the output has not registered yet.

## State and Persistence Behavior

The file owns no persistent state. Its only state transitions are OF node reference count gets/puts. It returns borrowed DSS output pointers from the global OMAP DSS output registry.

## Dependencies and Integration Points

It depends on Linux OF graph APIs and the OMAP DSS output registry. Panel/encoder drivers use `omapdss_of_find_source_for_first_ep()` to discover their upstream DSS source, while DSS port registration code uses the port helpers to interpret graph layout.

## Risks and Edge Cases

Invalid or incomplete graphs return `-EINVAL`; a valid graph whose source driver has not registered returns `-EPROBE_DEFER`. Parent walking is intentionally shallow and assumes the DSS DT structure places a compatible node within two levels. Reference handling is small but important: endpoint and remote port references must be released on all paths.

## Test Signals

Test with valid panel-to-DSS graphs, missing endpoint 0, endpoints without remote ports, delayed DSS output registration, `reg` present and absent on ports, and graph layouts with intermediate `ports` nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.c

## Purpose

This file implements the core OMAP DSS hardware driver. It maps the DSS register block, owns global DSS clocks and clock-source mux state, saves/restores DSS context across runtime PM, initializes DT display ports, manages video PLL discovery, exposes SDI/VENC/HDMI/DPI clock/source helpers, and acts as the component master for DSS child IP blocks. The complete 1,296-line source was read.

## Important APIs, Types, and Functions

Global state lives in the static `dss` struct: platform device, MMIO base, optional syscon PLL control regmap/offset, parent and fck clocks, cached clock calculation data, DSI/DISPC/LCD clock-source selections, saved register context, SoC feature table, and optional video PLLs. Local `struct dss_features` describes SoC fck dividers, parent clock, exposed ports, and DPI source selection callback.

Important public functions include `omapdss_is_initialized()`, `dss_runtime_get()`, `dss_runtime_put()`, `dss_ctrl_pll_enable()`, `dss_ctrl_pll_set_control_mux()`, `dss_sdi_init()/enable()/disable()`, `dss_select_dsi_clk_source()`, `dss_select_lcd_clk_source()`, `dss_dpi_select_source()`, `dss_div_calc()`, `dss_set_fck_rate()`, `dss_select_hdmi_venc_clk_source()`, and platform driver init/uninit.

## Control Flow

The platform probe creates a component master match for child devices, skipping RFBI. Master bind selects SoC DSS features from `omapdss_get_version()`, maps registers, obtains clocks, sets a default fck, probes optional syscon/video PLLs and DT ports, enables runtime PM, resumes the block, initializes DSS control clock sources and VENC-related bits, prints hardware revision, drops runtime PM, binds all child components, adds a debugfs register dump, disables VT switching, and marks DSS initialized.

Runtime suspend saves `DSS_CONTROL` plus SDI registers when relevant, drops bus throughput, and selects sleep pinctrl state. Runtime resume restores pinctrl, requests high bus throughput, and restores saved context. Unbind reverses child binding, PLLs, DT ports, PM, and clocks.

Clock helpers select between DSS fck and DSI/DSI2 PLL hsdivs for DISPC/LCD/DSI consumers, using feature-specific register fields and SoC-specific LCD source availability. `dss_div_calc()` walks possible DSS fck dividers using the SoC parent clock and fck multiplier or delegates to `clk_round_rate()` on AM43xx-style direct clocks.

## State and Persistence Behavior

State is global and volatile. The driver caches clock rates and mux selections in memory and programs corresponding DSS control bits in hardware. Runtime PM context save/restore persists selected DSS registers across clock/power loss during a boot session. DT port initialization stores per-port output data in `port->data` through DPI/SDI helpers. There is no disk persistence.

## Dependencies and Integration Points

The file depends on Linux platform, clock, runtime PM, pinctrl, regmap/syscon, regulator, OF graph, suspend, and component APIs. It integrates with `dss_features.c` for limits and feature bits, DISPC for runtime and manager programming, DPI/SDI port drivers for DT output registration, video PLL code for DRA7/OMAP5-style PLLs, HDMI/VENC/DSI code through shared mux helpers, and debugfs through `dss_debugfs_create_file()`.

## Risks and Edge Cases

The core uses one global `dss` object, so multiple DSS instances are not supported. Port initialization loops can skip unsupported/out-of-range DT ports; partial failures call `dss_uninit_ports()`. Some invalid source selections use `BUG()` or `BUG_ON()`, so callers must validate channel/source combinations. Clock-rate setting warns if the clock framework returns a nearby rate rather than the requested rate. The SDI enable path has multiple 500 ms polling timeouts. Video PLL cleanup must handle partially initialized PLL1/PLL2. Runtime context is restored only after `ctx_valid` has been set by suspend.

## Test Signals

Test signals include probe/bind/unbind on all compatible SoC versions, DT ports for DPI/SDI including DRA7 multi-DPI ports, video PLL resources and `syscon-pll-ctrl`, runtime suspend/resume register preservation, fck rate and divider calculations, HDMI/VENC clock-source selection on SoCs with one or both outputs, SDI PLL lock/reset timeouts, child component bind failures, and debugfs DSS register/clock dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.h

## Purpose

This header is the internal OMAP DSS subsystem contract. It centralizes logging macros, bitfield helpers, clock-source and PLL types, LCD manager clock/config structs, and function prototypes shared by DSS core, DISPC, DSI, DPI, SDI, VENC, HDMI, overlay, manager, PLL, and compatibility layers. The complete 519-line header was read.

## Important APIs, Types, and Functions

Key macros are `DSSDBG`, `DSSERR`, `DSSINFO`, `DSSWARN`, `FLD_MASK`, `FLD_VAL`, `FLD_GET`, and `FLD_MOD`. Important enums include `omap_dss_clk_source`, `dss_io_pad_mode`, `dss_hdmi_venc_clk_source_select`, `dss_dsi_content_type`, and `dss_pll_id`.

Important structs are `dss_pll_clock_info`, `dss_pll_ops`, `dss_pll_hw`, `dss_pll`, `dispc_clock_info`, `dss_lcd_mgr_config`, and `dss_mgr_ops`. The prototypes cover runtime PM, display suspend/resume/disable, sysfs init, overlay manager setup/checks, overlay setup/checks, DSS clock/source control, OF helpers, SDI/DPI/DSI/DISPC/VENC/HDMI platform driver entry points, PLL registration/calculation/programming, and legacy manager operation wrappers.

## Control Flow

There is no runtime flow in the header, but it defines the call graph used by the subsystem. Core init files register platform drivers declared here; output drivers call manager and clock helpers declared here; DISPC exports low-level manager/overlay programming used through wrappers; PLL providers register `struct dss_pll` objects whose operations are invoked by DPI, DSI, HDMI, and video PLL users.

## State and Persistence Behavior

The header stores no state. It defines the in-memory structures that carry PLL dividers/rates, DISPC clock divisors, and LCD manager config between calculation code and hardware programming code. The bitfield macros are used throughout the subsystem for hardware register state.

## Dependencies and Integration Points

It depends on Linux interrupt declarations and OMAP DSS public video types. It is included by most files in `omapfb/dss`, making it the main integration boundary between component drivers. Compile-time feature guards provide no-op DPI/SDI helpers when those drivers are not built and a warning fallback for `dsi_get_pixel_size()` when DSI is disabled.

## Risks and Edge Cases

Because this header is widely included, signature drift can break many drivers. The bitfield helpers use `1 << width` style arithmetic and assume valid field widths below the integer limit. Several prototypes expose low-level functions that rely on caller-side PM, locking, or valid channel/source combinations. Stubs can hide missing feature support at compile time while runtime graph data still names a disabled output type.

## Test Signals

Build coverage is the main signal: all relevant Kconfig combinations for DPI, DSI, SDI, HDMI4/5, VENC, DISPC, debugfs, and IRQ stats should compile. Runtime validation should exercise PLL registration/lookups, manager wrappers, clock-source helpers, and disabled-driver stubs on configs that omit optional outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.c

## Purpose

This file is the OMAP DSS SoC capability database. It records register field layouts, supported feature flags, manager/overlay counts, display/output matrices, color modes, overlay capabilities, clock-source names, numeric limits, rotation support, and FIFO units for OMAP2, OMAP3, AM35xx, AM43xx, OMAP4, OMAP5, and DRA7-class DSS variants. The complete 940-line source was read.

## Important APIs, Types, and Functions

Private types are `struct dss_reg_field`, `struct dss_param_range`, and `struct omap_dss_features`. Static tables cover feature ids, register fields, supported displays/outputs, supported color modes, overlay capabilities, clock-source names, parameter ranges, and per-SoC `omap_dss_features` instances.

The public query functions are `dss_feat_get_num_mgrs()`, `dss_feat_get_num_ovls()`, `dss_feat_get_param_min()`, `dss_feat_get_param_max()`, `dss_feat_get_supported_displays()`, `dss_feat_get_supported_outputs()`, `dss_feat_get_supported_color_modes()`, `dss_feat_get_overlay_caps()`, `dss_feat_color_mode_supported()`, `dss_feat_get_clk_source_name()`, `dss_feat_get_buffer_size_unit()`, `dss_feat_get_burst_size_unit()`, `dss_has_feature()`, `dss_feat_get_reg_field()`, `dss_feat_rotation_type_supported()`, and `dss_features_init()`.

## Control Flow

Early DSS initialization calls `dss_features_init(version)`, which selects one static feature table into `omap_current_dss_features`. All later query functions dereference that selected table directly. Feature presence is tested by linear search through the selected feature-id array; register-field queries bounds-check with `BUG_ON`; display/output/color/capability queries index arrays by channel or plane.

## State and Persistence Behavior

The only mutable state is the static pointer `omap_current_dss_features`. All feature data is compile-time constant. There is no file-backed persistence and no runtime mutation of the capability tables after initialization.

## Dependencies and Integration Points

This file depends on OMAP DSS public enums/types and the internal feature enum declarations in `dss_features.h`. It feeds constraints into DSS core clock setup, DISPC overlay validation and FIFO programming, DSI/DPI clock calculations, HDMI audio/CTS feature checks, VENC quirks, and rotation/scaling/format capability checks exposed to upper display layers.

## Risks and Edge Cases

All query functions assume `dss_features_init()` was called with a supported version. Unsupported versions leave the pointer unset after only logging a warning, which would make later queries unsafe. DRA7 maps to the OMAP5 capability table here, while `dss.c` has a separate DRA7 port/clock feature table; keeping those aligned is important. Array sizes must match enum channel/plane indexes used elsewhere. Feature-list omissions can silently disable hardware paths such as HDMI audio MCLK, DSI PHY DCC, MFLAG, or DPI regulator handling.

## Test Signals

Validation includes booting each supported SoC version and checking manager/overlay counts, display/output masks, color mode acceptance/rejection, scaler/downscale and line-width limits, FIFO units, rotation support, clock-source names in debugfs, and feature-gated paths such as LCD clock source selection, DSI VC OCP width, HDMI CTS software mode, and AM35xx/AM43xx regulator differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.h

## Purpose

This header declares the DSS feature identifiers, register-field identifiers, numeric-range identifiers, maximum DSS resource counts, and feature-query API implemented by `dss_features.c`. The complete 97-line header was read.

## Important APIs, Types, and Functions

Constants define `MAX_DSS_MANAGERS`, `MAX_DSS_OVERLAYS`, `MAX_DSS_LCD_MANAGERS`, and `MAX_NUM_DSI`. `enum dss_feat_id` lists hardware capabilities and quirks such as LCD enable polarity, line-buffer split, independent core clock divider, LCD clock source, DSI PLL power bug, DSI VC features, DPI `vdds_dsi` usage, HDMI CTS/audio MCLK, FIFO merge, burst 2D, DSI PHY DCC, and MFLAG. `enum dss_feat_reg_field` names SoC-specific bitfield layouts; `enum dss_range_param` names numeric limits for DSS fck, pixel clock divisor, DSI PLL LP divisor, DSI fck, downscale, and line width.

The declared API exposes feature presence, register field lookup, parameter min/max, supported displays/outputs, supported color modes, overlay caps, clock-source names, FIFO units, rotation support, and initialization by `omapdss_version`.

## Control Flow

There is no executable flow. Consumers include this header, call `dss_features_init()` during core setup, and then issue query calls throughout DSS, DISPC, DPI, DSI, and HDMI logic.

## State and Persistence Behavior

The header has no runtime state. It defines enum values that must stay in sync with the table indexes in `dss_features.c`.

## Dependencies and Integration Points

It depends on OMAP DSS public enums from `video/omapfb_dss.h` through users of the prototypes. It is the compile-time contract between capability tables and feature-gated hardware code in the DSS subtree.

## Risks and Edge Cases

Adding a feature id, register field, or range parameter requires updating every relevant per-SoC table. Mismatched enum/table ordering can produce incorrect register writes or limits. Resource maxima bound static arrays in the DSS core and DSI code, so increasing hardware support requires reviewing array users.

## Test Signals

Build all DSS configurations after enum changes, boot feature-table initialization on supported versions, and run targeted checks for each feature-gated path whose identifier is changed or added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi.h

## Purpose

This header defines the shared internal HDMI contract for OMAP DSS HDMI drivers. It provides wrapper, PLL, and PHY register offsets, IRQ bits, HDMI/video/audio enums and structs, MMIO helpers, wrapper/PLL/PHY/common/audio function prototypes, and the aggregate `struct omap_hdmi` state used by HDMI4. The complete 360-line header was read.

## Important APIs, Types, and Functions

Important defines include HDMI wrapper registers (`HDMI_WP_*`), IRQ flags (`HDMI_IRQ_*`), PLL control registers (`PLLCTRL_*`), and PHY registers (`HDMI_TXPHY_*`). Enums describe PLL and PHY power commands, HDMI vs DVI mode, packing mode, audio channel/type/justification/sample order/sample size/transfer/layout/CTS/MCLK settings.

Important structs are `hdmi_video_format`, `hdmi_config`, `hdmi_audio_format`, `hdmi_audio_dma`, `hdmi_core_audio_i2s_config`, `hdmi_core_audio_config`, `hdmi_wp_data`, `hdmi_pll_data`, `hdmi_phy_data`, `hdmi_core_data`, and `omap_hdmi`. Inline helpers are `hdmi_write_reg()`, `hdmi_read_reg()`, `REG_FLD_MOD`, `REG_GET`, `hdmi_wait_for_bit_change()`, and `hdmi_mode_has_audio()`.

The prototypes cover wrapper video/IRQ/PHY/PLL/audio DMA operations, PLL compute/init/uninit, PHY configure/init/lane parsing, OF lane parsing, ACR computation, and HDMI audio programming.

## Control Flow

The header has no standalone runtime flow. HDMI4 code initializes `omap_hdmi.wp`, `.pll`, `.phy`, and `.core`, then calls wrapper/PLL/PHY/core helpers through these declarations during power-on, audio setup, EDID reads, IRQ handling, and debug dumps.

## State and Persistence Behavior

No state is stored in the header. It defines state containers used at runtime: MMIO bases, physical DMA address, PHY lane function/polarity, current HDMI config, regulator/core/display/audio flags, child audio platform device, audio config cache, and locks for audio/display coordination.

## Dependencies and Integration Points

It depends on Linux IO/delay/platform headers, HDMI infoframe types, OMAP DSS public types, OMAP HDMI audio pdata, and internal DSS helpers. It integrates HDMI wrapper, PLL, PHY, common parsing, audio, and HDMI4/HDMI5 core code behind a common state and register helper API.

## Risks and Edge Cases

The polling helper waits up to about 10 ms and returns the last observed value, so callers must compare carefully. Register helpers assume valid MMIO bases and bitfield ranges. `struct omap_hdmi` mixes mutex-protected display state and spinlock-protected audio playback state; users must follow the documented lock split. Enum values are hardware encodings, so renumbering is unsafe.

## Test Signals

Build HDMI4/HDMI5 with audio enabled, exercise wrapper register dumps, PLL/PHY init and power transitions, OF lane parsing, HDMI vs DVI mode audio gating, audio DMA address setup, ACR calculation, and IRQ bit handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4.c

## Purpose

This file implements the OMAP4 HDMI DSS output driver. It binds the HDMI wrapper, PLL, PHY, and HDMI4 core helpers into an `omap_dss_device`, handles full/core-only power transitions, EDID reads, HDMI/DVI infoframe mode, hotplug IRQ PHY state, runtime PM, and an `omap-hdmi-audio` child device. The complete 812-line source was read.

## Important APIs, Types, and Functions

State is the single static `struct omap_hdmi hdmi` declared in `hdmi.h`. Important functions include `hdmi_runtime_get()/put()`, `hdmi_irq_handler()`, `hdmi_init_regulator()`, `hdmi_power_on_core()`, `hdmi_power_off_core()`, `hdmi_power_on_full()`, `hdmi_power_off_full()`, display timing callbacks, `hdmi_display_enable()/disable()`, `hdmi_core_enable()/disable()`, `hdmi_connect()/disconnect()`, `hdmi_read_edid()`, `hdmi_set_infoframe()`, `hdmi_set_hdmi_mode()`, `hdmi_probe_of()`, HDMI audio callbacks, `hdmi_audio_register()`, `hdmi4_bind()/unbind()`, runtime PM callbacks, and platform driver init/uninit.

The registered `omapdss_hdmi_ops` supplies connect, disconnect, enable, disable, timing check/set/get, EDID read, infoframe set, and HDMI mode set. Audio registration supplies `omap_hdmi_audio_ops` for startup, shutdown, start, stop, and config.

## Control Flow

Component bind initializes the global state, parses optional DT lane data, initializes wrapper/PLL/PHY/core blocks, requests the HDMI IRQ, enables runtime PM, registers the HDMI output, registers the audio child platform device, and creates debugfs. Connect lazily initializes the VDDA regulator, connects the DIGIT overlay manager, and links the downstream display.

Full display enable locks `hdmi.lock`, verifies a manager, powers core resources, clears/disables IRQs, computes HDMI PLL settings from the configured pixel clock, enables/configures the PLL, configures PHY, powers PHY to LDO, configures HDMI4 core/wrapper, disables TV gamma, sets manager timings, starts wrapper video, enables the manager, and enables connect/disconnect IRQs. Disable stops audio, clears IRQs, disables the manager, stops video, powers PHY off, disables PLL, drops runtime PM, and disables VDDA.

EDID reads use core-only power if full display power is not already active. The IRQ handler acknowledges wrapper IRQs and moves PHY power among off, LDO, and TX states for connect/disconnect, with a special restart sequence when both bits are set. Audio callbacks require HDMI mode with display enabled, cache audio config, start/stop wrapper/core audio under a spinlock, and abort cached audio if display re-enable cannot restore it.

## State and Persistence Behavior

State is volatile and global for one HDMI4 instance: current timings/infoframe/mode, regulator pointer, `core_enabled`, display/audio enabled flags, cached audio config, audio callback pointer, output registration, child audio platform device, and wrapper idle mode. Hardware state includes PLL/PHY/core/wrapper registers, DISPC TV pixel clock, DSS HDMI/VENC source mux, manager timing/enable, IRQ masks, and regulator/runtime PM state. There is no file persistence.

## Dependencies and Integration Points

The file depends on HDMI4 core helpers, HDMI wrapper/PLL/PHY/common helpers, DSS clock muxing, DISPC runtime and TV pixel clock, OMAP DSS manager/output APIs, Linux regulators, IRQs, runtime PM, OF graph, component framework, and OMAP HDMI audio platform data. It integrates with panels/connectors through `omapdss_hdmi_ops`, with sound through the `omap-hdmi-audio` platform child, and with debugfs via `dss_debugfs_create_file()`.

## Risks and Edge Cases

The global `hdmi` object implies one HDMI4 instance. `read_edid()` uses `BUG_ON()` if runtime PM resume fails. `hdmi_power_on_full()` returns `-EIO` for several distinct lower-level failures, losing detailed error codes. Audio shutdown writes `audio_playing` under the mutex rather than the audio spinlock used elsewhere, so lock ordering and races should be reviewed carefully. IRQ hotplug handling assumes wrapper IRQ semantics and PHY power commands succeed in interrupt context. Runtime PM for HDMI proxies DISPC PM, so imbalance affects both blocks.

## Test Signals

Test probe/bind/unbind, regulator deferral, DT lane parsing, connect/disconnect to HDMI displays, EDID reads before and during display enable, HDMI and DVI modes, common CEA/VESA timings, PLL/PHY failure injection, hotplug connect/disconnect IRQs including simultaneous bits, runtime suspend/resume, audio startup/config/start/stop/shutdown, display disable while audio is playing, and debugfs HDMI dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4.c -->
