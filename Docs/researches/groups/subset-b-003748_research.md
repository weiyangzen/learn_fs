# Research Group subset-b-003748

Source-tree-aligned grouped research for subset B work item `subset-b-003748`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_enc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_enc.c

## Purpose

`sun4i_hdmi_enc.c` implements the legacy Allwinner A10/A10s/A31 HDMI encoder, connector, hotplug polling, EDID retrieval, CEC pin glue, component binding, and SoC variant data. It drives the HDMI MMIO block directly and creates the internal TMDS clock and DDC I2C adapter used by the DRM HDMI connector.

## Important APIs, Types, And Functions

Key entry points are `sun4i_hdmi_bind()`, `sun4i_hdmi_unbind()`, `sun4i_hdmi_enable()`, `sun4i_hdmi_disable()`, `sun4i_hdmi_get_modes()`, `sun4i_hdmi_connector_detect()`, and `sun4i_hdmi_connector_clock_valid()`. The variant tables `sun4i_variant`, `sun5i_variant`, and `sun6i_variant` encode pad, PLL, TMDS divider, reset, DDC clock, and regmap-field differences. DRM integration is through encoder helper funcs, connector funcs, `drmm_connector_hdmi_init()`, and `drm_atomic_helper_connector_hdmi_update_infoframes()`.

## Control Flow

Probe adds a component. Bind allocates `struct sun4i_hdmi`, maps registers, deasserts optional reset, enables bus/mod clocks, creates a regmap, registers the TMDS clock, creates the HDMI DDC adapter, optionally gets an external `ddc-i2c-bus`, initializes the DRM encoder/connector, configures optional CEC, and attaches encoder to connector. Atomic enable sets mod/TMDS rates from connector HDMI state, reprograms pad/timing/polarity/infoframe registers, enables the TMDS clock, and turns on video output. Disable clears video enable and disables TMDS.

## State And Persistence Behavior

Persistent state lives in `struct sun4i_hdmi`: MMIO base, regmap, clocks, reset, connector, encoder, CEC adapter, internal/external DDC adapters, and variant pointer. Hardware state persists in pad, PLL, timing, packet, HPD, CEC, and video-control registers until disabled or reset.

## Dependencies And Integration Points

It depends on DRM atomic HDMI helpers, EDID/DDC helpers, CEC pin ops, Linux component framework, clocks, resets, regmap, platform resources, `sun4i_hdmi_i2c_create()`, and `sun4i_tmds_create()`. It integrates with TCON channel 1 through possible CRTCs from OF graph and with `sun4i_tcon_mode_set()` via the TMDS encoder type.

## Risks And Test Signals

Risks include incomplete HDMI VSI/clear-infoframe support, no HPD IRQ so polling latency is expected, fragile undocumented pad/PLL values, clock rounding limited to 165 MHz, and cleanup paths that must balance clocks, DDC adapters, CEC, and resets. Test by probing all compatibles, EDID over internal and external DDC, HPD connect/disconnect, HDMI vs DVI sinks, CEC pin toggling, mode validation around 165 MHz, and enable/disable/suspend cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_i2c.c

## Purpose

`sun4i_hdmi_i2c.c` exposes the HDMI controller's DDC engine as a Linux I2C adapter so EDID can be read when no external DDC bus is supplied. It hides SoC register-layout differences behind regmap fields supplied by the HDMI variant.

## Important APIs, Types, And Functions

The exported function is `sun4i_hdmi_i2c_create()`. Internal flow is split across `sun4i_hdmi_init_regmap_fields()`, `sun4i_hdmi_i2c_xfer()`, `xfer_msg()`, and `fifo_transfer()`. The `sun4i_hdmi_i2c_algorithm` advertises `master_xfer` and `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

## Control Flow

Creation first calls `sun4i_ddc_create()` to derive `hdmi->ddc_clk`, allocates regmap fields for enable/start/reset/address/status/FIFO/byte-count/command/SDA/SCK controls, allocates an adapter, binds `hdmi` as adapter data, and registers it. Each transfer validates all messages, enables and fixes the DDC clock at 100 kHz, resets the controller, enables SDA/SCK, then processes each message. `xfer_msg()` selects FIFO direction when required, clears address and FIFO state, programs address, thresholds, byte count, and implicit read/write command, clears interrupts, starts transfer, streams FIFO chunks, waits for start to clear, and checks transfer-complete/error bits.

## State And Persistence Behavior

The adapter persists in `hdmi->i2c`; regmap fields are devm-managed. Runtime state is transient per transfer, but hardware FIFO, DDC control, interrupt-status, and line-enable registers are rewritten on each message. The DDC clock is enabled only around transfer windows.

## Dependencies And Integration Points

It depends on `struct sun4i_hdmi` variant field descriptors from `sun4i_hdmi_enc.c`, the common clock framework, I2C core, MMIO FIFO helpers, and regmap field polling. The HDMI connector uses this adapter through `drm_edid_read_ddc()`.

## Risks And Test Signals

Risks include timeout/error handling around FIFO request and transfer-complete bits, off-by-one FIFO threshold semantics across variants, rejecting zero-length or too-large messages, and assuming 100 kHz byte timing for polling delays. Test with EDID reads on sun4i/sun5i/sun6i variants, multi-message DDC transactions, injected NACK/arbitration/bus errors, FIFO boundary sizes, and cleanup via `i2c_del_adapter()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_tmds_clk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_tmds_clk.c

## Purpose

`sun4i_hdmi_tmds_clk.c` registers the legacy HDMI TMDS clock as a common-clock provider backed by HDMI PLL and pad-control registers. It lets HDMI mode validation and enable paths request exact or nearest TMDS character rates.

## Important APIs, Types, And Functions

`struct sun4i_tmds` wraps `clk_hw`, `struct sun4i_hdmi *`, and a divider offset. Public creation is `sun4i_tmds_create()`. Clock ops are `sun4i_tmds_determine_rate()`, `sun4i_tmds_recalc_rate()`, `sun4i_tmds_set_rate()`, `sun4i_tmds_get_parent()`, and `sun4i_tmds_set_parent()`. `sun4i_tmds_calc_divider()` searches the HDMI divider and optional half-clock bit.

## Control Flow

Creation names two parents from `pll-0` and `pll-1`, allocates the clock wrapper, sets `CLK_SET_RATE_PARENT`, and stores the variant divider offset. Rate determination iterates all parents, half divisors 1/2, and divider values to find an exact parent rate or closest rounded parent. `set_rate()` recomputes the divider, toggles `SUN4I_HDMI_PAD_CTRL1_HALVE_CLK`, and writes `SUN4I_HDMI_PLL_CTRL_DIV()`. Parent ops read/write the parent select field in `PLL_DBG0`.

## State And Persistence Behavior

Software state is the devm-allocated `sun4i_tmds` and `hdmi->tmds_clk`. Hardware state persists in the HDMI pad half-clock bit, PLL divider field, and parent-select bits. The clock framework caches rates and parents around these register ops.

## Dependencies And Integration Points

It depends on common clock APIs, HDMI register definitions in `sun4i_hdmi.h`, and clocks acquired by `sun4i_hdmi_bind()`. `sun4i_hdmi_connector_clock_valid()` and `sun4i_hdmi_enable()` use the registered clock to validate and program HDMI modes.

## Risks And Test Signals

Risks include divider-offset differences on sun6i, using only two parents, closest-rate selection that can fail HDMI tolerance, and preserving unrelated pad/PLL bits. Test by checking `clk_round_rate()` near common HDMI pixel clocks, parent switching, half-rate cases, mode validation tolerance, and register values after enable on each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_tmds_clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.c

## Purpose

`sun4i_layer.c` implements DRM plane objects for the older DE1 backend pipeline. It owns plane state allocation, format/modifier advertisement, atomic update/disable behavior, and the initialization of primary/overlay layers backed by `sun4i_backend` and optionally `sun4i_frontend`.

## Important APIs, Types, And Functions

The public API is `sun4i_layers_init()`. Important helpers are `sun4i_backend_layer_reset()`, duplicate/destroy state callbacks, `sun4i_backend_layer_atomic_update()`, `sun4i_backend_layer_atomic_disable()`, `sun4i_layer_format_mod_supported()`, and `sun4i_layer_init_one()`. Supported format lists differ depending on whether a frontend is available, and modifiers include linear plus Allwinner tiled when the frontend can be used.

## Control Flow

`sun4i_layers_init()` allocates a sentinel-terminated plane array and creates `SUN4I_BACKEND_NUM_LAYERS` planes, with layer 0 primary and the rest overlays. Atomic update clears previous backend layer programming, then either routes through the frontend for formats requiring conversion/scaling to XRGB8888 or programs backend format/buffer directly. It always updates coordinates, zpos, and layer enable. Atomic disable disables the backend layer and, if old state used the frontend, marks `backend->frontend_teardown` under `frontend_lock`.

## State And Persistence Behavior

Per-plane persistent state is `struct sun4i_layer`; per-atomic state is `struct sun4i_layer_state`, especially `uses_frontend`. Hardware state persists through backend/frontend register programming until the next atomic update or disable. The frontend teardown flag coordinates deferred cleanup with vblank-side backend behavior.

## Dependencies And Integration Points

It depends on DRM plane/atomic/blend helpers, `sun4i_backend`, `sun4i_frontend`, and `sunxi_engine` layer initialization. The CRTC obtains these planes through the engine ops during display pipeline setup.

## Risks And Test Signals

Risks include mismatched `uses_frontend` transitions, frontend teardown races, format/modifier advertisement inconsistent with backend/frontend support, zpos bounds tied to hardware layer count, and cleanup when partial plane init fails. Test with atomic plane enable/disable, frontend-required tiled/YUV formats, overlay z-order changes, alpha/zpos properties, and repeated format switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.h

## Purpose

`sun4i_layer.h` declares the DE1 layer plane structures and conversion helpers shared by the backend layer implementation and related pipeline code.

## Important APIs, Types, And Functions

`struct sun4i_layer` embeds a `drm_plane`, backend pointer, driver pointer, and hardware layer id. `struct sun4i_layer_state` extends `drm_plane_state` with `pipe` and `uses_frontend`; `uses_frontend` records whether the frontend was part of the committed plane path. Inline helpers `plane_to_sun4i_layer()` and `state_to_sun4i_layer_state()` implement container conversions. `sun4i_layers_init()` is the exported initializer.

## Control Flow

The header has no executable flow. Its inline conversions are used by DRM plane callbacks to recover driver-private state from generic DRM objects.

## State And Persistence Behavior

The structures persist as DRM plane objects and atomic plane states. `uses_frontend` is copied during duplicate-state and read during disable/update to decide whether frontend teardown is required. `pipe` is present as private state but is not manipulated in the researched implementation.

## Dependencies And Integration Points

It forward-declares `struct sunxi_engine` and relies on DRM plane types through consumers. It is included by `sun4i_layer.c` and any code that needs DE1 plane-private state.

## Risks And Test Signals

Risks are mostly ABI drift within the driver: changing struct layout or state fields requires matching reset/duplicate/destroy callbacks. Test by building all sun4i DRM code and exercising atomic plane duplication/destruction with KMS plane updates that enter and leave frontend usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.c

## Purpose

`sun4i_lvds.c` creates a DRM LVDS encoder and optional connector for TCON channel 0 when a panel-lvds or bridge is connected. It manages only DRM/panel lifecycle; TCON timing and LVDS PHY programming are handled by `sun4i_tcon.c`.

## Important APIs, Types, And Functions

The exported entry point is `sun4i_lvds_init()`. `struct sun4i_lvds` contains a connector, encoder, and panel pointer. Helpers include `sun4i_lvds_get_modes()`, connector destroy funcs, and encoder `enable`/`disable` callbacks that prepare/enable or disable/unprepare the panel.

## Control Flow

TCON bind calls `sun4i_lvds_init()` when OF graph port 1 resolves to an LVDS panel and LVDS prerequisites are available. Init finds a panel or bridge from the TCON node, initializes a simple LVDS encoder, restricts possible CRTCs to the owning TCON CRTC, creates and attaches an LVDS connector for panel outputs, or attaches a bridge when present. Enable/disable callbacks only sequence panel power.

## State And Persistence Behavior

The LVDS object is devm-allocated for the DRM device lifetime. Connector/encoder registration persists until driver cleanup. Hardware state is not directly programmed here; persistent display output state is in the panel, bridge, and TCON LVDS registers touched by other files.

## Dependencies And Integration Points

It depends on DRM panel/bridge/connector helpers, `drm_simple_encoder_init()`, OF graph lookup, and `struct sun4i_tcon`. `sun4i_tcon_mode_set()` and `sun4i_tcon_set_status()` use encoder type `DRM_MODE_ENCODER_LVDS` to choose channel 0 and LVDS PHY behavior.

## Risks And Test Signals

Risks include returning success when no panel/bridge exists, cleanup paths shared between panel and bridge cases, and panel power sequencing without error propagation. Test with LVDS panels and bridges, missing LVDS reset/clock properties in the TCON, mode enumeration from panel, encoder possible CRTC mask, and enable/disable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.h

## Purpose

`sun4i_lvds.h` is the narrow declaration header for LVDS output initialization on sun4i TCON channel 0.

## Important APIs, Types, And Functions

It declares `sun4i_lvds_init(struct drm_device *drm, struct sun4i_tcon *tcon)`. The function creates the LVDS encoder/connector or bridge attachment for the given TCON.

## Control Flow

No code runs in the header. It allows `sun4i_tcon.c` to call the LVDS initializer when OF graph detection says the channel 0 output is an LVDS panel.

## State And Persistence Behavior

The header stores no state. State is owned by the LVDS implementation, DRM objects, and the TCON instance passed to the initializer.

## Dependencies And Integration Points

Consumers must have visible declarations for `struct drm_device` and `struct sun4i_tcon`. It forms the compile-time link from TCON bind logic to LVDS output creation.

## Risks And Test Signals

Risk is limited to prototype drift. Build coverage of `sun4i_tcon.c` and LVDS-enabled configurations, plus runtime LVDS probe, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.c

## Purpose

`sun4i_rgb.c` creates the parallel RGB encoder and optional panel connector or bridge for TCON channel 0. It also validates RGB bridge modes against TCON register field limits and dot-clock tolerance.

## Important APIs, Types, And Functions

The exported initializer is `sun4i_rgb_init()`. `struct sun4i_rgb` holds connector, encoder, TCON, panel, and bridge pointers. Important callbacks are `sun4i_rgb_mode_valid()`, `sun4i_rgb_get_modes()`, `sun4i_rgb_encoder_enable()`, and `sun4i_rgb_encoder_disable()`.

## Control Flow

Init resolves a panel or bridge from the TCON OF graph. It creates a simple `DRM_MODE_ENCODER_NONE` encoder bound only to the TCON CRTC, creates a connector for direct panels, or attaches the bridge. Mode validation checks hsync/vsync widths, display/total field limits, and for bridge outputs rounds `tcon->dclk` with divider bounds 6..127 against a 0.5 percent tolerance. Panel outputs skip clock validation because panel timing tolerance may need future adjustment.

## State And Persistence Behavior

The RGB object is devm-allocated and persists with DRM registration. Panel power state is changed on enable/disable. `sun4i_rgb_mode_valid()` mutates `tcon->dclk_min_div` and `dclk_max_div` before clock rounding, so validation has side effects on the TCON clock search window.

## Dependencies And Integration Points

It depends on DRM panel/bridge helpers, TCON dot clock, `sun4i_tcon_mode_set()` for actual RGB timing programming, and OF graph port 1. Encoder type `DRM_MODE_ENCODER_NONE` selects TCON channel 0 RGB programming.

## Risks And Test Signals

Risks include clock validation side effects, skipping clock checks for panels, handling no panel/bridge as non-fatal disabled output, and bridge cleanup after partial init. Test with direct RGB panels, RGB-to-bridge outputs, invalid sync/size limits, dot-clock rounding near tolerance, bus flags for polarity in TCON mode set, and panel enable/disable sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.h

## Purpose

`sun4i_rgb.h` declares the parallel RGB output initializer used by the TCON component when channel 0 is connected to a non-LVDS panel or bridge.

## Important APIs, Types, And Functions

It exposes `sun4i_rgb_init(struct drm_device *drm, struct sun4i_tcon *tcon)`.

## Control Flow

There is no runtime flow in the header. It enables `sun4i_tcon.c` to instantiate RGB output support during TCON bind.

## State And Persistence Behavior

The header has no state. The implementation owns the DRM connector/encoder object and references the TCON passed by caller.

## Dependencies And Integration Points

Consumers need declarations for DRM device and TCON structures. It is part of the channel 0 output-selection split between RGB and LVDS support.

## Risks And Test Signals

Only prototype consistency is material. Build coverage with RGB support enabled and runtime probe of a panel or bridge connected to TCON port 1 validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.c

## Purpose

`sun4i_tcon.c` is the central Allwinner timing-controller driver. It binds a TCON to a display engine, creates the CRTC, programs channel 0/1 timings for RGB/LVDS/DSI/HDMI/TV, handles vblank IRQs/page-flip completion, creates channel 0 dot clock support, instantiates RGB or LVDS outputs, and provides SoC-specific output muxing quirks.

## Important APIs, Types, And Functions

Exported APIs are `sun4i_tcon_set_status()`, `sun4i_tcon_mode_set()`, `sun4i_tcon_enable_vblank()`, and `sun4i_tcon_of_table`. Major helpers include connector/pixel-depth lookup, LVDS PHY setup, channel enable/clock exclusivity, dithering setup, `sun4i_tcon0_mode_set_cpu/lvds/rgb()`, `sun4i_tcon1_mode_set()`, IRQ handler/page-flip finish, clock/regmap/IRQ init, engine matching through OF graph traversal or endpoint IDs, component bind/unbind, and platform mux callbacks for A10/A13/A31/R40/TCON TOP.

## Control Flow

Probe verifies panel/bridge dependencies for channel 0 and registers a component. Bind finds the matching `sunxi_engine`, allocates TCON state, resets hardware, handles optional eDP/LVDS resets and LVDS alternate clock availability, initializes clocks/regmap/IRQ, creates `dclk`, initializes the CRTC, creates LVDS or RGB output for channel 0, applies backend muxing quirks, and appends the TCON to the driver list. Atomic mode set dispatches by encoder type: DSI uses channel 0 CPU/8080-style trigger path, LVDS and RGB use channel 0 timing registers, HDMI/TV use channel 1 timing registers and output mux. Status enable toggles global enable, LVDS interface/PHY, channel gate, and clock exclusivity.

## State And Persistence Behavior

Persistent state is `struct sun4i_tcon`: DRM/device pointers, regmap, clocks, resets, CRTC pointer, ID, quirks, and list entry. Hardware state persists in timing, polarity, mux, LVDS, dithering, interrupt, and channel-control registers. Page-flip event state lives in `sun4i_crtc` and is completed under `dev->event_lock` from the IRQ handler.

## Dependencies And Integration Points

It depends on Linux component, regmap, clock/reset, IRQ, OF graph, DRM CRTC/encoder/connector/panel/bridge/vblank helpers, `sun4i_crtc`, `sunxi_engine`, RGB/LVDS/DSI helpers, TCON TOP, and `sun4i_tcon_dclk`. It is the timing bridge between display engines/mixers/backends and output encoders.

## Risks And Test Signals

Risks include fragile DT graph engine matching, legacy endpoint ID compatibility, LVDS property fallback disabling output, undocumented dithering/LVDS/mux bits, clock divider side effects, interlace vertical-total handling, IRQ ack semantics, and unbalanced clock exclusivity. Test on each compatible, RGB/LVDS/DSI/HDMI/TV modes, vblank/page flips, TCON TOP routing, old and corrected DT graphs, suspend/resume, and LVDS 18/24-bit panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.h

## Purpose

`sun4i_tcon.h` defines the TCON register map, bitfield helpers, driver-private TCON structures, quirk callbacks, and exported functions used across the sun4i DRM pipeline.

## Important APIs, Types, And Definitions

The header provides many register offsets and bitfield macros for global control/interrupts, channel 0/1 control/timing/polarity/IO tristate, CPU trigger/DSI path, LVDS interface/analog controls, frame-rate-control dithering, mux control, and safe-period/ECC FIFO registers. `struct sun4i_tcon_quirks` describes SoC capabilities such as channel presence, LVDS support, alternate LVDS PLL, DE backend muxing, polarity register placement, eDP reset, minimum dclk divider, mux callback, and LVDS PHY setup callback. `struct sun4i_tcon` stores runtime TCON state. Exports include `sun4i_tcon_mode_set()`, `sun4i_tcon_set_status()`, `sun4i_tcon_enable_vblank()`, and `sun4i_tcon_of_table`.

## Control Flow

No standalone control flow runs here. Macros encode register values consumed by `sun4i_tcon.c` mode-setting, IRQ, bind, and PHY helpers, and by dot-clock code in `sun4i_tcon_dclk.c`.

## State And Persistence Behavior

The structures model persistent per-device state; register macros target persistent hardware state. `dclk_min_div` and `dclk_max_div` are mutable clock-search parameters shared between mode validation/programming and the dot-clock provider.

## Dependencies And Integration Points

It includes DRM modes, regmap, reset, and kernel list/clock declarations indirectly through consumers. It is included by TCON, RGB, LVDS, DSI, and dot-clock code and is part of the external match table used by the sun4i driver.

## Risks And Test Signals

Risks include incorrect bitfield widths, generation-specific register differences hidden behind shared names, and quirk mismatches with compatible strings. Test by compiling all sun4i variants and checking register programming on RGB, LVDS, DSI, HDMI, TV, and TCON TOP systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.c

## Purpose

`sun4i_tcon_dclk.c` registers TCON channel 0 dot clock as a common-clock provider backed by `SUN4I_TCON0_DCLK_REG` and output-polarity phase bits. It lets panels/bridges and TCON mode setting derive exact pixel clocks from the channel 0 source clock.

## Important APIs, Types, And Functions

`struct sun4i_dclk` wraps `clk_hw`, regmap, and TCON pointer. Public APIs are `sun4i_dclk_create()` and `sun4i_dclk_free()`. Clock ops include enable/disable/is_enabled, `sun4i_dclk_recalc_rate()`, `sun4i_dclk_determine_rate()`, `sun4i_dclk_set_rate()`, `sun4i_dclk_get_phase()`, and `sun4i_dclk_set_phase()`.

## Control Flow

Creation reads the output clock name from `clock-output-names`, uses `tcon->sclk0` as parent, registers a `CLK_SET_RATE_PARENT` clock, and stores it in `tcon->dclk`. Rate determination iterates from `tcon->dclk_min_div` through `dclk_max_div`, rounds the parent to `requested * divider`, and chooses exact or closest result while guarding `ULONG_MAX` overflow. Set-rate writes the divider field. Enable/disable toggles the gate bit, and phase maps 0/120/240 degree steps to bits 29:28 of the IO polarity register.

## State And Persistence Behavior

Software state persists in the registered clock and TCON pointer. Hardware state persists in the DCLK gate/divider and output phase bits. Divider search bounds are mutable TCON state set by RGB/LVDS/DSI mode paths.

## Dependencies And Integration Points

It depends on common clock provider APIs, regmap, TCON register definitions, and the TCON bind/unbind lifecycle. RGB mode validation and TCON channel 0 mode programming rely on this clock for pixel-clock feasibility and output timing.

## Risks And Test Signals

Risks include divider truncation in `parent_rate / rate`, shared phase bits with polarity programming, mutable divider bounds from callers, and manual `clk_register()`/`clk_unregister()` lifecycle. Test round-rate/set-rate for RGB/LVDS/DSI dividers, gate behavior during enable/disable, phase programming, overflow path, and TCON unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.h

## Purpose

`sun4i_tcon_dclk.h` declares the TCON channel 0 dot-clock creation and destruction functions.

## Important APIs, Types, And Functions

It exposes `sun4i_dclk_create(struct device *dev, struct sun4i_tcon *tcon)` and `sun4i_dclk_free(struct sun4i_tcon *tcon)`.

## Control Flow

The header has no executable flow. TCON bind calls create after regmap/clock setup, and bind error/unbind paths call free when channel 0 exists.

## State And Persistence Behavior

No state is stored in the header. The implementation stores the registered clock in `tcon->dclk` and manipulates TCON hardware registers.

## Dependencies And Integration Points

It forward-declares `struct sun4i_tcon` and relies on `struct device` from consumers. It links TCON lifecycle code with the common-clock provider implementation.

## Risks And Test Signals

Risks are limited to lifecycle/prototype drift. Build with TCON channel 0 support and runtime create/free during probe failure and normal remove are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tv.c

## Purpose

`sun4i_tv.c` implements the Allwinner A10 composite TV encoder as a DRM TVDAC encoder and composite connector. It programs fixed PAL/NTSC register tables, exposes the DRM TV mode property, and applies display-engine color correction for analog output.

## Important APIs, Types, And Functions

Important structs are `struct tv_mode` plus small level/gain/resync parameter structs, and `struct sun4i_tv`. Key functions are `sun4i_tv_bind()`, `sun4i_tv_unbind()`, `sun4i_tv_enable()`, `sun4i_tv_disable()`, `sun4i_tv_find_tv_by_mode()`, and connector reset helpers using `drm_atomic_helper_connector_tv_reset()`. Static `tv_modes[]` holds PAL and NTSC programming constants.

## Control Flow

Probe registers a component. Bind maps and regmaps TVE registers, deasserts reset, enables clock, creates a simple TVDAC encoder, discovers possible CRTCs from OF graph, creates a composite connector, enables interlace, creates TV properties for NTSC/PAL, sets NTSC default, and attaches encoder. Atomic enable reads connector TV mode state, selects `tv_mode`, programs DAC mapping, TV standard, DAC levels, chroma frequency, porches, line count, blank/black levels, burst/gain/sync/VBI/active-line/resync registers, applies engine color correction, and enables TVE. Disable clears enable and disables color correction.

## State And Persistence Behavior

Persistent driver state is connector, encoder, clock, reset, regmap, and driver pointer. Hardware state persists in the TVE analog registers and engine color-correction configuration. Connector TV mode is DRM atomic state and defaults to NTSC.

## Dependencies And Integration Points

It depends on DRM TV connector helpers, component framework, regmap, clocks/resets, OF CRTC matching, `sunxi_engine_apply_color_correction()`, and TCON channel 1 timing selected through encoder type `DRM_MODE_ENCODER_TVDAC`.

## Risks And Test Signals

Risks include hardcoded vendor/BSP analog constants, limited mode table to PAL/NTSC, interlace timing sensitivity, no load-detect implementation despite status register definitions, and color-correction pairing on disable. Test PAL/NTSC modes, connector property changes, interlaced CRTC timing, enable/disable, analog output quality, probe error unwinds, and color-correction state after TV off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_drc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_drc.c

## Purpose

`sun6i_drc.c` is a minimal component driver for the Allwinner Dynamic Range Control block. In this snapshot it only powers, resets, and clocks the block so it can participate in the display component graph.

## Important APIs, Types, And Functions

`struct sun6i_drc` stores bus clock, module clock, and reset. Component callbacks are `sun6i_drc_bind()` and `sun6i_drc_unbind()`. Platform callbacks add/remove the component, and the OF table covers A31/A31s/A23/A33/A80 DRC compatibles.

## Control Flow

Probe adds the component. Bind allocates state, gets and deasserts reset, enables the AHB bus clock, gets the module clock, sets it exclusive to 300 MHz, enables it, and returns. Error paths unwind clock and reset state. Unbind releases the exclusive rate, disables both clocks, and asserts reset.

## State And Persistence Behavior

Driver state is the devm-allocated clock/reset holder. Hardware state persists only as reset deassertion and enabled fixed-rate clocks; the file programs no DRC processing registers.

## Dependencies And Integration Points

It depends on Linux component, clock, reset, platform, and OF matching. It likely exists so display pipeline component binding can account for DRC hardware even before feature programming is implemented.

## Risks And Test Signals

Risks include taking an exclusive 300 MHz module clock with no register use, unbind ordering around `clk_rate_exclusive_put()`, and component graph dependencies that can block DRM probe if DRC resources are absent. Test probe/unbind on each compatible, clock-rate conflicts, reset/clock error paths, and full display pipeline boot with DRC nodes enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_drc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.c

## Purpose

`sun6i_mipi_dsi.c` implements the Allwinner MIPI DSI host and DRM DSI encoder/connector. It programs the DSI instruction engine, pixel/video timing packets, D-PHY configuration, panel lifecycle, and low-power DCS command transfers.

## Important APIs, Types, And Functions

Important areas include ECC/CRC helpers (`sun6i_dsi_ecc_compute()`, `sun6i_dsi_crc_compute()`), packet builders, instruction setup/start/wait helpers, video timing helpers (`sun6i_dsi_setup_burst()`, `sun6i_dsi_setup_format()`, `sun6i_dsi_setup_timings()`), encoder enable/disable callbacks, connector get/detect callbacks, DCS transfer helpers, MIPI host ops (`attach`, `detach`, `transfer`), component bind/unbind, and platform probe/remove. Variants control presence and exclusivity of the module clock.

## Control Flow

Probe maps registers, gets regulator/reset/clocks/D-PHY, attaches bus clock to regmap, optionally sets exclusive 297 MHz module clock, registers the MIPI host, and adds the DRM component. Attach stores panel/device only after DRM is registered and emits a hotplug event. Component bind creates a DSI encoder and connector. Encoder enable powers regulator/reset/mod clock, enables DSI, initializes instruction slots, computes video start delay, burst/loop/format/timing packets, configures and powers the D-PHY, prepares/enables the panel, then starts high-speed clock and data instructions. Host transfer waits for idle, clears command flags, and handles supported short writes, long writes, and one-byte reads in LP mode.

## State And Persistence Behavior

Persistent state lives in `struct sun6i_dsi`: connector, encoder, host, clocks, regmap, regulator, reset, D-PHY, attached device, panel, DRM pointer, and variant. Hardware state persists in DSI instruction, pixel, timing, command FIFO, and PHY registers until disable/reset. Attached panel/device pointers are updated by MIPI host attach/detach.

## Dependencies And Integration Points

It depends on DRM DSI/panel/simple-encoder helpers, Linux MIPI D-PHY phy APIs, regulator/clock/reset/regmap/component frameworks, and `sun4i_tcon.c`, which treats DSI as TCON channel 0 CPU interface with `SUN6I_DSI_TCON_DIV`.

## Risks And Test Signals

Risks include many magic timing formulas, only partial command-mode support, panel enable before HS mode due to DCS limitations, limited read support, command completion bits noted unreliable, possible DSI_START_HSD jump-table fragility, and mod-clock exclusivity. Test with RGB565/666/888 panels, burst and non-burst video, LP DCS short/long/read commands, D-PHY timing, hotplug attach/defer, enable/disable, and malformed transfer types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.h

## Purpose

`sun6i_mipi_dsi.h` defines the private state and variant contract for the Allwinner DSI host plus helper conversions used by the DSI implementation and TCON CPU-interface path.

## Important APIs, Types, And Definitions

`SUN6I_DSI_TCON_DIV` defines the fixed TCON-to-DSI divider used by TCON channel 0 programming. `struct sun6i_dsi_variant` records `has_mod_clk` and `set_mod_clk`. `struct sun6i_dsi` embeds DRM connector/encoder, `mipi_dsi_host`, clocks, regmap, regulator, reset, D-PHY, device/panel/DRM pointers, and variant. Inline helpers convert host, connector, and encoder back to `struct sun6i_dsi`.

## Control Flow

The header has only inline container conversions. Runtime behavior is in `sun6i_mipi_dsi.c`; TCON mode setting uses `encoder_to_sun6i_dsi()` to get attached DSI device parameters.

## State And Persistence Behavior

The struct persists for the platform device lifetime. `device` and `panel` are mutable attachment state, while `drm` is set during component bind and cleared at unbind. Clock/reset/regulator/phy pointers define power state resources.

## Dependencies And Integration Points

It depends on DRM connector/encoder and MIPI DSI host declarations. It is included by DSI implementation and TCON code that needs DSI lane/format details for channel 0 CPU trigger setup.

## Risks And Test Signals

Risks include stale attached-device pointers across detach/unbind and variant flags that must match clock names in DT. Build all DSI/TCON paths and test attach/defer/detach, TCON mode programming, and variant-specific clock setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.c

## Purpose

`sun8i_csc.c` configures color-space conversion for DE2/DE3 mixer layers. It enables or disables YUV-to-RGB conversion and loads the proper coefficient table based on DRM framebuffer format, color encoding, color range, and channel layout.

## Important APIs, Types, And Functions

The public API is `sun8i_csc_config(struct sun8i_layer *layer, struct drm_plane_state *state)`. Internal types include `enum sun8i_csc_mode`. Important helpers are `sun8i_csc_get_mode()`, `sun8i_csc_setup()` for DE2 CCSC units, and `sun8i_de3_ccsc_setup()` for DE3 blender CSC. Coefficient tables cover limited/full range BT.601/BT.709 for DE2 and limited/full BT.601/BT.709/BT.2020 for DE3.

## Control Flow

`sun8i_csc_config()` first derives mode: off for invisible/no-CRTC/non-YUV planes, YVU2RGB for YVU formats, otherwise YUV2RGB. DE3 layers use blender CSC control bits indexed by layer channel. Older layouts pick a CCSC base from `ccsc_base[layer->cfg->ccsc][layer->channel]`. YVU modes write coefficients with U/V coefficient positions swapped; normal modes bulk-write all 12 values. Finally the CSC enable bit is updated.

## State And Persistence Behavior

There is no software state. Hardware coefficient registers and enable bits persist until the next plane update/config call or mixer reset. The function relies on current DRM plane state color encoding/range.

## Dependencies And Integration Points

It depends on DRM format/color management definitions and `sun8i_mixer` layer config/address helpers. VI/UI layer atomic update code calls it when programming YUV-capable layers.

## Risks And Test Signals

Risks include table indexing if unsupported encodings reach DE2, channel/base layout mismatch, YVU coefficient swapping errors, and stale CSC enable when planes become invisible. Test YUV and RGB formats, NV/YVU variants, full/limited and BT.601/709/2020 states, DE2/DE3/D1 CCSC layouts, plane disable, and visual color accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.h

## Purpose

`sun8i_csc.h` declares CSC register offsets, coefficient register helpers, and the public mixer-layer CSC configuration function.

## Important APIs, Types, And Definitions

It defines CCSC base offsets for mixer0/mixer1/D1 layouts, `SUN8I_CSC_CTRL(base)`, `SUN8I_CSC_COEFF(base, i)`, and `SUN8I_CSC_CTRL_EN`. It declares `sun8i_csc_config(struct sun8i_layer *layer, struct drm_plane_state *state)`.

## Control Flow

The header has no executable control flow. Macros are consumed by `sun8i_csc.c` to address hardware coefficient and enable registers.

## State And Persistence Behavior

No software state is stored. The macros describe persistent hardware CSC registers that remain programmed across commits until changed or reset.

## Dependencies And Integration Points

It includes DRM color management declarations and forward-declares plane/layer structures. It is included by mixer/layer code that updates color conversion for YUV planes.

## Risks And Test Signals

Risks include stale offsets for SoC-specific layouts and incorrect coefficient address calculation. Compile coverage plus visual YUV playback tests on mixer0/mixer1/D1/DE3 variants validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.c

## Purpose

`sun8i_dw_hdmi.c` wraps the Synopsys DesignWare HDMI bridge for newer Allwinner SoCs. It binds a DRM TMDS encoder, powers/reset-enables the controller and regulator, obtains the companion Allwinner HDMI PHY, provides SoC mode limits, and registers both HDMI controller and PHY platform drivers from one module.

## Important APIs, Types, And Functions

Key functions are `sun8i_dw_hdmi_bind()`, `sun8i_dw_hdmi_unbind()`, `sun8i_dw_hdmi_encoder_mode_set()`, `sun8i_dw_hdmi_find_possible_crtcs()`, mode validators for A83T and H6, and module init/exit registering `sun8i_dw_hdmi_pltfm_driver` plus `sun8i_hdmi_phy_driver`. Quirks are in `struct sun8i_dw_hdmi_quirks`.

## Control Flow

Bind computes possible CRTCs directly or through TCON TOP port 4, gets reset, TMDS clock, and `hvcc` regulator, enables regulator/reset/clock, parses the `phys` phandle, obtains and initializes the Allwinner PHY, initializes a simple TMDS encoder, fills `dw_hdmi_plat_data` with mode validation/infoframe flags and PHY ops/config, then calls `dw_hdmi_bind()`. Mode set updates the TMDS clock rate from the selected CRTC clock. Unbind reverses DW-HDMI, PHY, clock, reset, and regulator state.

## State And Persistence Behavior

Persistent state is `struct sun8i_dw_hdmi`: TMDS clock, device, DW-HDMI handle, encoder, PHY pointer, platform data, regulator, quirks, and reset. Hardware state persists in controller reset/clock/regulator, DW-HDMI bridge registers, PHY state, and TCON TOP routing selected elsewhere.

## Dependencies And Integration Points

It depends on DRM bridge/dw_hdmi, component framework, OF graph, clocks/resets/regulator, `sun8i_hdmi_phy_*()` functions, and optional `sun8i_tcon_top` routing. It integrates with TCON channel 1 through possible CRTC masks and TCON TOP for R40/H6-like paths.

## Risks And Test Signals

Risks include CRTC discovery through TCON TOP, lifetime coupling between controller and PHY drivers, missing cleanup if `drm_simple_encoder_init()` return is ignored, mode clock caps differing by SoC, and regulator/reset ordering. Test A83T 297 MHz cap, H6 594 MHz cap and DRM infoframes, TCON TOP paths, probe deferral on PHY/CRTC, hotplug/modeset, and unbind failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.h

## Purpose

`sun8i_dw_hdmi.h` defines the Allwinner-specific DW-HDMI wrapper, PHY register map, PHY/clock variant structures, and cross-file APIs connecting the DW-HDMI component with the HDMI PHY and PHY clock provider.

## Important APIs, Types, And Definitions

The header names HDMI PHY debug, REXT, read-enable, unscramble, analog, PLL, status, and CEC registers with bitfields. `struct sun8i_hdmi_phy_variant` selects PHY clock availability, second PLL, DW-HDMI PHY tables or ops, and init callback. `struct sun8i_hdmi_phy` stores clocks, regmap, reset, calibration, and variant. `struct sun8i_dw_hdmi_quirks` stores mode validation and infoframe behavior. `struct sun8i_dw_hdmi` stores controller runtime state. APIs include `sun8i_hdmi_phy_get/init/deinit/set_ops()` and `sun8i_phy_clk_create()`.

## Control Flow

No standalone flow runs here. The DW-HDMI component calls PHY APIs declared here; the PHY driver and clock provider use the register macros and structures to initialize hardware and expose clock ops.

## State And Persistence Behavior

The structures persist for platform device lifetimes. `rcal` stores calibration read from PHY analog status. `phy->clk_phy` may be created dynamically during PHY init and then used by mode programming.

## Dependencies And Integration Points

It includes DW-HDMI bridge declarations, DRM encoder, clocks, regmap, regulator, and reset APIs. It is the shared contract among `sun8i_dw_hdmi.c`, `sun8i_hdmi_phy.c`, and `sun8i_hdmi_phy_clk.c`.

## Risks And Test Signals

Risks include register macro mistakes, variant table mismatches, and lifecycle assumptions around optional PHY clock creation. Test by building all three files together and running HDMI modes across A83T/H3/R40/A64/H6 variants, including PHY init/deinit and clock parent/divider paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy.c

## Purpose

`sun8i_hdmi_phy.c` implements the Allwinner HDMI PHY companion for DW-HDMI systems. It initializes PHY register access, calibration, PLL/analog settings, HPD/DDC/CEC pin behavior, per-SoC DW-HDMI PHY ops or tables, and exposes the PHY instance to the DW-HDMI wrapper.

## Important APIs, Types, And Functions

Public APIs are `sun8i_hdmi_phy_get()`, `sun8i_hdmi_phy_init()`, `sun8i_hdmi_phy_deinit()`, and `sun8i_hdmi_phy_set_ops()`, plus exported `sun8i_hdmi_phy_driver`. Key internals include `sun8i_a83t_hdmi_phy_config/disable()`, `sun8i_h3_hdmi_phy_config/disable()`, `sun8i_hdmi_phy_unlock()`, `sun8i_hdmi_phy_init_a83t()`, `sun8i_hdmi_phy_init_h3()`, and `sun50i_hdmi_phy_init_h6()`. Variant tables cover A83T, H3, R40, A64, and H6.

## Control Flow

Probe maps PHY registers, creates regmap, gets bus/mod clocks, optional PLL parents, shared PHY reset, stores variant, and publishes drvdata. DW-HDMI bind calls `sun8i_hdmi_phy_get()` and `sun8i_hdmi_phy_init()`. Init deasserts reset, enables bus/mod clocks, optionally creates/enables a PHY clock, then runs the variant init sequence. H3-like init unlocks scrambled registers, powers/calibrates analog blocks, enables DDC pins, clears CEC to hardware control, and records `rcal`. Per-mode PHY ops program polarity and frequency-dependent PLL/analog values; A83T uses DW PHY I2C writes, while H3-like variants use native PHY registers. H6 supplies DW-HDMI MPLL/current/PHY tables instead of custom ops.

## State And Persistence Behavior

Persistent state is `struct sun8i_hdmi_phy` with clocks, regmap, reset, variant, and calibration value. Hardware state persists in analog/PLL/debug/REXT/CEC registers and optional PHY clock divider/parent until disabled or reset.

## Dependencies And Integration Points

It depends on platform/OF, regmap, clock/reset, delays, DW-HDMI PHY helpers, and the shared header. `sun8i_dw_hdmi.c` uses it to supply `dw_hdmi_plat_data` PHY ops/config and to initialize/deinitialize hardware.

## Risks And Test Signals

Risks include undocumented magic values, long sleeps in mode set, ignored calibration poll return, preserving clock parent/divider while rewriting PLL regs, variant-specific second PLL handling, and probe deferral if drvdata is not ready. Test all compatibles, 27/74.25/148.5/297/594 MHz modes, HPD/DDC/CEC behavior, PHY clock parent/divider, suspend/resume, and repeated mode switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy_clk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy_clk.c

## Purpose

`sun8i_hdmi_phy_clk.c` registers the optional HDMI PHY output clock used by H3/R40/A64-like PHY variants. It exposes PLL parent selection and predivider programming through common clock ops.

## Important APIs, Types, And Functions

`struct sun8i_phy_clk` wraps `clk_hw` and a PHY pointer. The public API is `sun8i_phy_clk_create()`. Clock ops are `sun8i_phy_clk_determine_rate()`, `sun8i_phy_clk_recalc_rate()`, `sun8i_phy_clk_set_rate()`, `sun8i_phy_clk_get_parent()`, and `sun8i_phy_clk_set_parent()`.

## Control Flow

Creation gets `pll-0` and optional `pll-1` parent names from the PHY, allocates the wrapper, registers `hdmi-phy-clk` with `CLK_SET_RATE_PARENT`, and stores it in `phy->clk_phy`. Rate determination scans all parents and dividers 1..16, choosing exact or closest parent/divider combination. Recalc reads the PLL CFG2 predivider field. Set-rate searches the best divider not above target and writes `SUN8I_HDMI_PHY_PLL_CFG2_PREDIV()`. Parent ops read/write the CKIN select field in PLL CFG1.

## State And Persistence Behavior

The registered clock persists after PHY init. Hardware state persists in PLL CFG1 parent select and CFG2 predivider fields. The PHY mode-setting code must preserve those fields when rewriting PLL configuration.

## Dependencies And Integration Points

It depends on the common clock framework, regmap, and `sun8i_dw_hdmi.h` register definitions. `sun8i_hdmi_phy_init()` creates this clock for variants with `has_phy_clk`, and `sun8i_h3_hdmi_phy_config()` sets its rate to the HDMI pixel clock.

## Risks And Test Signals

Risks include zero `best_m` if no divider satisfies a too-high target, optional second-parent setup, and race with PHY PLL writes that also touch CFG1/CFG2. Test rate rounding, parent switching, divider programming from 27 MHz through high TMDS clocks, and mode changes on H3/R40/A64 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy_clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.c

## Purpose

`sun8i_mixer.c` implements the DE2/DE3/DE33 display mixer as a `sunxi_engine`. It maps DRM formats to hardware formats, creates VI/UI planes, commits blender routing/coordinates/z-order, programs output size/interlace mode, resets and initializes mixer registers, and binds mixer instances into the sun4i DRM engine list.

## Important APIs, Types, And Functions

The exported format helper is `sun8i_mixer_drm_format_to_hw()`. Engine ops are `sun8i_mixer_commit()`, `sun8i_layers_init()`, and `sun8i_mixer_mode_set()`. Lifecycle helpers are `sun8i_mixer_of_get_id()`, `sun8i_mixer_init()`, `sun8i_mixer_bind()`, and `sun8i_mixer_unbind()`. Variant config tables describe VI/UI counts, scaler masks, CCSC layout, DE generation, scanline limits, module clock rate, and DE33 channel map.

## Control Flow

Bind enforces a 32-bit DMA mask, allocates mixer/engine state, optionally sets the DRM DMA device, derives an engine id from OF endpoint, maps main and for DE33 top/display regmaps, deasserts reset, enables bus/mod clocks and optional fixed mod rate, adds the engine to `drv->engine_list`, clears DE2/DE3 register ranges, disables unused sub-engines, then initializes blender defaults. Plane initialization creates VI planes first, then UI planes, assigning primary role based on available channels and DE33 physical channel mapping. Commit scans DRM planes for the target CRTC, routes enabled layers to blender pipes by normalized zpos, writes pipe coordinates and sizes, then updates route/pipe-enable and double-buffer control. Mode set updates global/blender output size and interlace bit.

## State And Persistence Behavior

Persistent state is `struct sun8i_mixer`, embedded `sunxi_engine`, regmaps, clocks, reset, and variant config. Hardware state persists in global, channel, blender, sub-engine, double-buffer, route, and size registers until next commit/mode-set/reset. DRM plane state controls visible layers and zpos.

## Dependencies And Integration Points

It depends on DRM atomic/plane helpers, DMA mask APIs, component framework, OF graph, clocks/resets/regmap, `sun8i_ui_layer`, `sun8i_vi_layer`, CSC/scaler code via layer updates, and TCON engine matching through `drv->engine_list`.

## Risks And Test Signals

Risks include 32-bit DMA limitations, CRTC id fallback for old DTs, DE33 split regmap/channel map handling, clearing guessed register ranges, route/zpos correctness, disabled sub-engine assumptions, and fixed mod-clock requirements. Test all compatible mixer configs, VI/UI plane creation, YUV/RGB formats, zpos routing, interlace output, DE33 H616 mapping, high DMA addresses, and repeated commits with disabled planes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.h

## Purpose

`sun8i_mixer.h` defines DE2/DE3/DE33 mixer register offsets, hardware format codes, sub-engine disable registers, layer and mixer configuration structures, runtime mixer/layer state, and helper conversions used by mixer, UI/VI layer, CSC, and scaler code.

## Important APIs, Types, And Definitions

Key macros encode sizes/coordinates, global control/status/double-buffer/size registers, blender attributes/routes/modes/CSC, channel base/size for DE2/DE3/DE33, framebuffer format values for RGB/YUV/P010/P210, and unused sub-engine enable registers. Enums describe CCSC layout, mixer generation, and layer type. `struct sun8i_layer_cfg` and `struct sun8i_mixer_cfg` describe hardware capabilities. `struct sun8i_mixer` embeds `sunxi_engine`; `struct sun8i_layer` embeds `drm_plane`. Inline helpers convert plane/engine to private types and compute blender regmap/base and channel base. It declares `sun8i_mixer_drm_format_to_hw()`.

## Control Flow

The header only provides inline calculations. Runtime code uses `sun8i_blender_base()`, `sun8i_blender_regmap()`, and `sun8i_channel_base()` to choose correct addresses for DE generation and DE33 split register spaces.

## State And Persistence Behavior

Configuration structs are static per compatible; runtime structs persist for mixer and plane lifetimes. Register macros target persistent hardware state. The DE33 `map[]` translates logical DRM layer ordering to sparse physical channels.

## Dependencies And Integration Points

It includes clock/regmap/reset and DRM plane definitions plus `sunxi_engine.h`. It is included by mixer, UI/VI layer, CSC, and scaler implementations.

## Risks And Test Signals

Risks include wrong register offsets for DE generations, ambiguous format numeric values between RGB and YUV paths, scanline/scaler mask mismatches, and helper selection of wrong regmap for DE33. Test compile coverage plus runtime plane programming on DE2, DE3, DE33, D1 CCSC, RGB/YUV/P010/P210 formats, scaler availability, and route/channel mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.h -->
