# Research: subset-b-003697

Grouped research for DRM panel drivers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83102.c

## Purpose

This driver supports several Himax HX83102 based MIPI DSI panels, mainly 1200x1920 tablet-class panels plus a 720x1600 Holitech panel. It maps each device-tree compatible string to an `hx83102_panel_desc` containing a fixed DRM mode, physical size, optional DCS backlight support, and a panel-specific initialization callback.

## Important APIs, Types, And Functions

`struct hx83102` owns the `drm_panel`, `mipi_dsi_device`, panel descriptor, orientation, regulators (`pp1800`, `avdd`, `avee`), and enable GPIO. `struct hx83102_panel_desc` describes mode/size/backlight/init data.

Panel lifecycle is implemented by `hx83102_prepare()`, `hx83102_enable()`, `hx83102_disable()`, and `hx83102_unprepare()`. `hx83102_get_modes()` duplicates the descriptor mode and fills connector display info. `hx83102_get_orientation()` returns the DT panel orientation. `hx83102_probe()` allocates the panel, configures 4-lane RGB888 video DSI with sync pulse and low-power command mode, registers the panel, and attaches to the DSI host.

The file contains vendor command definitions and several init callbacks: `starry_himax83102_j02_init()`, `boe_nv110wum_init()`, `csot_pna957qt1_1_init()`, `ivo_t109nw41_init()`, `kingdisplay_kd110n11_51ie_init()`, `starry_2082109qfh040022_50e_init()`, and `holitech_htf065h045_init()`. These callbacks use `mipi_dsi_multi_context` and `mipi_dsi_dcs_write_seq_multi()` to send long manufacturer command tables.

## Control Flow

Probe obtains match data, sets DSI bus parameters, calls `hx83102_panel_add()`, stores driver data, then calls `mipi_dsi_attach()`. `hx83102_panel_add()` obtains regulators and GPIO, reads orientation, binds a DT backlight if present, and creates a DCS backlight fallback only for descriptors with `has_backlight`.

Prepare holds the enable GPIO low, powers `pp1800`, then `avdd` and `avee`, sends a DCS NOP, toggles the enable GPIO through the panel reset sequence, calls the descriptor init callback, exits sleep, waits 120 ms, and turns the display on. Error paths disable supplies in reverse order. Disable clears LPM, sends display-off and sleep-in, restores LPM, and waits 150 ms. Unprepare disables the GPIO and supplies.

## State And Persistence

There is no persistent storage. Runtime state is the panel descriptor selected from OF match data, the current orientation, DSI mode flags, backlight brightness through DCS, regulator enable state, and enable GPIO level. Brightness state is held by the DRM backlight core and read/written with 12-bit DCS large brightness helpers.

## Dependencies And Integration Points

The driver depends on DRM panel, DRM connector modes, MIPI DSI helpers, `video/mipi_display.h`, regulator, GPIO, OF match data, and backlight APIs. It integrates with device tree compatibles for BOE, CSOT, IVO, Kingdisplay, Starry, and Holitech panels. It expects supplies named `avdd`, `avee`, and `pp1800`, an `enable` GPIO, and optional backlight/orientation properties.

## Risks

The largest risk is panel-specific command-table fragility: small byte changes can prevent bring-up or alter voltage, GIP, gamma, or MIPI timing behavior. `ctx->desc->init(ctx)` returns only the accumulated DSI write status, so semantic failures in a table are not detected. The fallback DCS backlight temporarily clears LPM, which must stay compatible with the host. Regulator sequencing and GPIO timing are tightly coupled to hardware. The generic init path assumes all descriptors work with the same 4-lane RGB888 sync-pulse video configuration.

## Test Signals

Useful validation includes successful module bind and `mipi_dsi_attach()`, absence of regulator/GPIO probe errors, a connector with the expected fixed mode and physical size, correct orientation from DT, visible image after prepare/enable, reliable suspend/resume through disable/unprepare/prepare, and working DCS brightness reads/writes on Holitech or other DCS-backlight variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83112a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83112a.c

## Purpose

This generated DRM panel driver supports the `djn,9a-3r063-1102b` HX83112A MIPI DSI panel. It provides a fixed 1080x2340 mode and a vendor initialization sequence derived from downstream panel data.

## Important APIs, Types, And Functions

`struct hx83112a_panel` contains the DRM panel, DSI device, three regulators, and reset GPIO. `hx83112a_on()` sends the long manufacturer command sequence, exits sleep, and turns the display on. `hx83112a_disable()` sends display-off and sleep-in. `hx83112a_prepare()` enables supplies, resets the panel, and calls `hx83112a_on()`. `hx83112a_unprepare()` asserts reset and disables supplies. `hx83112a_get_modes()` delegates to `drm_connector_helper_get_modes_fixed()`.

## Control Flow

Probe allocates the panel with `devm_drm_panel_alloc()`, gets supplies `vdd1`, `vsn`, and `vsp`, obtains the `reset` GPIO, sets four-lane RGB888 burst video DSI flags with HSE and non-continuous clock, enables `prepare_prev_first`, wires optional DT backlight, adds the panel, and attaches DSI. Runtime prepare performs bulk regulator enable, reset low-high-low with waits, DCS init in LPM, and display-on. Disable and unprepare are separate: disable sends DCS sleep commands, while unprepare drops reset and power.

## State And Persistence

The driver has no persistent state. It stores only the DSI pointer, regulator descriptors, and GPIO handle. Brightness is delegated to a backlight supplied by device tree rather than a DCS backlight created in this file.

## Dependencies And Integration Points

It depends on DRM panel/probe helper, MIPI DSI helpers, regulator bulk APIs, GPIO descriptors, and OF matching. Integration requires correct regulator names, a reset GPIO, optional backlight phandle, and the `djn,9a-3r063-1102b` compatible.

## Risks

The generated init table touches power, display, driver, bank, gamma LUT, TCON, GIP, TP, and clock registers. Those values are opaque and panel-specific. The mode is a single fixed 60 Hz timing with dimensions embedded in the mode. `hx83112a_on()` forces LPM but `hx83112a_disable()` clears LPM and does not restore it, which may matter if later commands assume a specific mode flag state. Error handling in prepare powers off on initialization failure, but disable ignores power sequencing and assumes the panel is still command-responsive.

## Test Signals

Check probe logs for regulator, reset GPIO, backlight, and DSI attach success. Runtime evidence includes the expected 1080x2340 mode, visible image after resume, no DSI command failures during the generated init sequence, and suspend/resume ordering where DCS disable occurs before supplies are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83112a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83112b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83112b.c

## Purpose

This generated driver supports a DJN HX83112B-based MIPI DSI panel, compatible `djn,98-03057-6598b-i`. It exposes a fixed 1080x2160 display mode and creates a DCS backlight for 12-bit brightness control.

## Important APIs, Types, And Functions

`struct hx83112b_panel` stores the DRM panel, DSI device, constant regulator bulk data, and reset GPIO. `hx83112b_on()` sends a long initialization sequence and sets display brightness/control-display/tear-on after display-on. `hx83112b_off()` performs display-off and sleep-in. `hx83112b_prepare()` powers regulators, resets, and initializes; `hx83112b_unprepare()` sends off, asserts reset, and disables supplies. `hx83112b_bl_update_status()` writes large DCS brightness through a registered raw backlight device.

## Control Flow

Probe obtains constant supplies `iovcc`, `vsn`, and `vsp`, gets the reset GPIO, sets DSI to four-lane RGB888 burst video with non-continuous clock, no-HSA, and LPM, creates a DCS backlight, adds the panel, and attaches the DSI device. Prepare enables supplies, toggles reset, sends the vendor register table, exits sleep, turns display on, initializes brightness to zero, enables brightness control, and enables tearing effect. Unprepare tries DCS off first and then powers down regardless of DCS errors.

## State And Persistence

State is volatile: the reset GPIO, bulk regulator enable state, DSI mode flags, panel registration, and backlight core brightness. No calibration or brightness values are persisted by this file.

## Dependencies And Integration Points

The driver integrates with DRM panel, MIPI DSI, raw backlight, GPIO, and regulator frameworks. It expects device tree to provide the compatible, reset GPIO, and regulators named in `hx83112b_supplies`.

## Risks

The long vendor command sequence includes many undocumented commands and bank switches, making regressions difficult to detect by static review. The backlight update temporarily clears LPM and restores it only on success; a failed brightness write returns before restoring LPM. The panel funcs omit `.disable`, so all display-off behavior is in unprepare rather than the normal disable stage. Initial brightness is set to zero, so a missing user-space/backlight update can look like a blank panel even if the panel initialized correctly.

## Test Signals

Verify the connector advertises the 1080x2160 mode and physical size, DSI attach succeeds, backlight device is created with max 4095, brightness writes generate DCS commands, TE enable does not upset the host, and suspend/resume calls unprepare/prepare without regulator or DSI errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83112b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83121a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83121a.c

## Purpose

This driver supports Himax HX83121A panels, currently BOE and CSOT PPC357DB1-4 variants used on dual-DSI 1600x2560 panels. It can operate in a normal non-DSC mode or an optional DSC mode selected by the `enable_dsc` module parameter.

## Important APIs, Types, And Functions

`struct himax` contains the DRM panel, up to two DSI devices, descriptor, mutable DSC config, reset GPIO, regulators, and backlight. `struct panel_desc` captures physical size, bpc, DSI lanes/format/flags, DSC config and modes, non-DSC modes, init callbacks, dual-DSI status, and DCS backlight support.

`himax_probe()` handles both primary and secondary DSI host registration. `himax_prepare()` powers supplies, resets, chooses the DSC or non-DSC init callback, optionally packs and sends the DSC picture parameter set, enables compression mode, and enables backlight. `himax_get_modes()` chooses between `dsc_modes` and `modes` based on the module parameter. `himax_create_backlight()` creates a raw DCS brightness backlight.

## Control Flow

Probe allocates the panel, obtains `vddi`, `avdd`, and `avee`, reads reset GPIO, loads descriptor data, copies the DSC configuration, then registers a secondary DSI device from OF graph port 1 when `is_dual_dsi` is true. It creates either a DCS backlight or a DT-provided backlight, adds the panel, applies descriptor DSI bus settings to one or both links, assigns `dsi->dsc` only when DSC is enabled, and attaches each DSI device with devm-managed attach.

Prepare enables regulators, toggles reset, sends the selected BOE or CSOT init sequence, then sends PPS and enables compression if `enable_dsc` is true. Unprepare sends sleep-in on the primary command DSI (`dsi[1]` for dual DSI), asserts reset, and disables regulators.

## State And Persistence

The only cross-call state is in memory: the selected descriptor, DSI pointers, copied DSC config, module parameter value, reset GPIO, regulators, and backlight. The module parameter is global to the module and affects exposed modes, init sequence, DSI DSC pointer assignment, and runtime compression setup. There is no persistent storage.

## Dependencies And Integration Points

The driver depends on DRM panel, MIPI DSI, OF graph for the secondary DSI host, DRM DSC helpers, backlight, regulators, and GPIO. It exposes OF matches `boe,ppc357db1-4` and `csot,ppc357db1-4`. Dual-DSI integration requires a valid graph connection for the secondary host. DCS brightness is sent through the command-primary link selected by `to_primary_dsi()`.

## Risks

`enable_dsc` is a module-wide switch, not a per-panel or per-connector setting, so mixed deployments are risky. DSC and non-DSC mode lists differ in refresh-rate support and timing; choosing the wrong path can mismatch host bandwidth, PPS, and panel register state. Dual-DSI attach relies on OF graph correctness and uses DSI1 as command sync, which must match hardware wiring. Backlight enable is called after panel init but errors from DCS brightness mapping are not calibrated, and a TODO notes raw brightness mapping is incomplete.

## Test Signals

Validate both module-parameter paths: non-DSC 60 Hz and DSC modes including 120 Hz/60 Hz. Confirm two DSI devices attach on dual-DSI panels, `dsi->dsc` is populated only in DSC mode, PPS/compression commands succeed, the expected BOE or CSOT sequence is selected from OF match data, and backlight brightness works after prepare and across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83121a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8394.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8394.c

## Purpose

This driver supports several Himax HX8394 or closely related HX8399 MIPI DSI panels: HannStar HSD060BHW4, Huiling HL055FHAV028C, Powkiddy X55, and Microchip AC40T08A. It provides descriptor-driven DSI mode setup, fixed modes, orientation handling, and vendor initialization sequences.

## Important APIs, Types, And Functions

`struct hx8394` stores the device, DRM panel, reset GPIO, `vcc` and `iovcc` regulators, orientation, and descriptor. `struct hx8394_panel_desc` stores one mode, lane count, mode flags, pixel format, and an init sequence callback.

`hx8394_prepare()` controls reset and regulators. `hx8394_enable()` sends the descriptor init sequence, exits sleep, waits 120 ms, and turns display on. `hx8394_disable()` enters sleep mode. `hx8394_unprepare()` asserts reset and disables regulators. `hx8394_get_modes()` duplicates the descriptor mode and fills display info. `hx8394_probe()` reads orientation, supplies, optional backlight, descriptor data, and attaches the DSI device.

## Control Flow

Probe configures the DSI device from the matched descriptor before panel add and DSI attach. At runtime, prepare only establishes hardware power/reset state and waits 180 ms. Enable performs the command-table programming and display-on sequence. If display-on fails after sleep-out, the error path attempts to enter sleep mode. Disable and unprepare reverse those steps across DCS sleep and regulator shutdown.

## State And Persistence

There is no persistence. State is limited to descriptor data, regulator/reset state, panel orientation, and DSI host attachment. Backlight, when present in DT, is owned by the DRM panel framework rather than this file.

## Dependencies And Integration Points

The driver depends on DRM panel, MIPI DSI helpers, regulators, GPIO, OF match data, panel orientation, and optional panel backlight binding. Compatibles are `hannstar,hsd060bhw4`, `huiling,hl055fhav028c`, `powkiddy,x55-panel`, and `microchip,ac40t08a-mipi-panel`.

## Risks

Initialization is split across prepare and enable; hosts or bridges that expect panel programming during prepare may expose ordering issues. The HL055FHAV028C sequence is for an HX8399-related panel despite sharing this driver, so command meanings differ from HX8394 comments. The init tables include many undocumented commands and bank switches. `devm_gpiod_get_optional()` may return NULL, but reset operations call `gpiod_set_value_cansleep()` which tolerates NULL in gpiod APIs; this relies on that API contract.

## Test Signals

Confirm each compatible reports the expected fixed resolution, physical size, lane count, and DSI flags. Hardware tests should verify prepare/enable ordering, panel orientation, optional backlight discovery, visible image after sleep-out/display-on, and reliable suspend/resume with DCS sleep before regulators are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8394.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-hydis-hv101hd1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-hydis-hv101hd1.c

## Purpose

This is a compact DRM panel driver for the Hydis HV101HD1 MIPI DSI panel. It exposes a fixed 1366x768 mode and basic DCS sleep/display-on sequencing.

## Important APIs, Types, And Functions

`struct hv101hd1` stores the DRM panel, DSI device, and bulk regulator data. `hv101hd1_prepare()` enables `vdd` and `vio`, exits sleep, waits, and turns the display on. `hv101hd1_disable()` sends display-off and sleep-in. `hv101hd1_unprepare()` disables regulators. `hv101hd1_get_modes()` duplicates the fixed mode.

## Control Flow

Probe allocates the panel, obtains constant supplies, sets two-lane RGB888 video DSI with LPM, gets a DT backlight through `drm_panel_of_backlight()`, adds the panel, and attaches to the DSI host. Runtime prepare powers the panel and sends standard DCS commands. Disable sends DCS off/sleep commands; unprepare removes power.

## State And Persistence

The driver has no persistent state and no private brightness state. It holds only device pointers and regulator descriptors. Any brightness state is provided by the DT backlight device.

## Dependencies And Integration Points

It integrates with DRM panel, MIPI DSI, regulator bulk APIs, and panel backlight bindings. Required resources are the `hydis,hv101hd1` compatible and regulators named `vdd` and `vio`.

## Risks

The prepare and disable callbacks ignore `ctx.accum_err` from the multi-context DSI operations and return zero, so DCS command failures may be hidden. There is no reset GPIO, orientation handling, or explicit bus flags. The display mode hardcodes dimensions and timing, so variants need a separate driver or descriptor extension.

## Test Signals

Validate DSI attach, fixed 1366x768 mode, regulator enable/disable behavior, visible output after prepare, backlight discovery, and suspend/resume logs. Because DSI errors are not propagated, command tracing or host error counters are useful during bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-hydis-hv101hd1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9322.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9322.c

## Purpose

This SPI-controlled DRM panel driver supports Ilitek ILI9322 TFT LCD controllers, including the D-Link DIR-685 panel. The controller accepts multiple input formats, including serial RGB, parallel RGB, YUV, and BT.656; the driver chooses a DRM mode according to the configured or probed input mode.

## Important APIs, Types, And Functions

`struct ili9322_config` describes board-specific physical size, flips, input format, voltage settings, sync polarity/mode, and gamma correction. `struct ili9322` stores the device, config, DRM panel, regmap, supplies, reset GPIO, selected input, gamma and voltage register values.

SPI register access is abstracted through `ili9322_regmap_spi_write()` and `ili9322_regmap_spi_read()` with bit 7 selecting read versus write. `ili9322_init()` resets the controller, applies voltage/gamma/polarity/interface/input registers, and logs the selected input mode. `ili9322_get_modes()` chooses the DRM mode and bus flags for the selected input. `ili9322_probe()` validates board config, derives register encodings, enables regmap, reads the chip ID, optionally probes the entry register, and registers the panel.

## Control Flow

Probe is SPI-only and creates a DPI connector panel. It requires OF match data with a board configuration; the generic `ilitek,ili9322` match has NULL data and intentionally fails as missing configuration. It configures regulators and voltage constraints, optional reset GPIO, SPI 8-bit mode, regmap, and chip ID. Prepare powers regulators, releases reset, then initializes registers. Enable writes power-control normal mode; disable writes standby; unprepare disables supplies.

## State And Persistence

No state is persisted. Runtime state includes selected input mode, derived voltage register values, gamma table, and regmap cache. The regmap uses `REGCACHE_MAPLE`, but the driver performs explicit initialization during prepare and does not rely on persistent hardware state.

## Dependencies And Integration Points

The driver depends on SPI, regmap, regulator bulk APIs, GPIO, DRM panel, video mode definitions, and device-tree match data. Board integration must provide a concrete `ili9322_config`, supplies `vcc`, `iovcc`, `vci`, and optional reset GPIO. It exposes a DPI connector because pixel data enters through an external RGB/YUV/BT.656 path, not through SPI.

## Risks

Board configuration is mandatory and highly hardware-specific; bad voltage or gamma values can produce electrical or display-quality issues. The conversion for `vcom_amplitude_percent == 0` assigns `ili->vcom_high = U8_MAX` instead of `ili->vcom_amplitude`, which looks suspicious and can leave `vcom_amplitude` uninitialized unless config supplies it. Probe rejects missing chip ID, so boards with inaccessible ID wiring will not bind. Mode selection depends on input encoding and only covers known input modes.

## Test Signals

Check SPI regmap read of chip ID `0x96`, regulator voltage setup, correct input-mode log, expected connector mode for the configured input, bus flags matching polarity properties, register writes during prepare, standby/normal power-control writes during disable/enable, and visual validation of scaling for YUV/BT.656 modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9322.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9341.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9341.c

## Purpose

This SPI/DBI controlled DRM panel driver supports an Ilitek ILI9341 panel in DPI/RGB mode, currently the `st,sf-tc240t-9370-t` panel on the STM32F429 Discovery board. SPI is used for command setup through MIPI DBI while pixel data is supplied over a DPI RGB interface.

## Important APIs, Types, And Functions

`struct ili9341_config` stores the fixed mode and all controller register payloads needed for power, timing, VCOM, address mode, RGB interface, pixel format, and gamma setup. `struct ili9341` stores config, panel, reset/data-command GPIOs, `mipi_dbi`, SPI speed, and regulators.

`ili9341_dpi_init()` sends the register program using `mipi_dbi_command()` and `mipi_dbi_command_stackbuf()`. `ili9341_dpi_power_on()` and `ili9341_dpi_power_off()` control reset and regulators. DRM panel funcs implement prepare, enable, disable, unprepare, and get-modes. `ili9341_probe()` gets reset and D/C GPIOs and delegates to `ili9341_dpi_probe()`.

## Control Flow

Probe obtains GPIOs, allocates a DPI connector panel, allocates a DBI context, gets supplies `vci`, `vddi`, and `vddi-led`, initializes SPI DBI, loads match config, and registers the panel. Prepare powers the panel and sends the full initialization table, including sleep-out and display-on. Enable sends display-on again. Disable sends display-off. Unprepare asserts reset and disables supplies.

## State And Persistence

All configuration is static match data. Runtime state is limited to GPIO, regulator, DBI, and panel registration state. There is no persistent storage or runtime mode switching.

## Dependencies And Integration Points

The driver depends on SPI, MIPI DBI helpers, DRM panel, DRM bus flags, GPIO, regulator bulk APIs, and OF/SPI device IDs. It exposes a DPI connector and communicates control commands over SPI using a D/C GPIO.

## Risks

Only one board-specific config is present; adding panels means adding a full register table. `max_spi_speed` is stored but not visibly applied to `spi->max_speed_hz` in this file. `ili9341_dpi_prepare()` does not check command return values from the init sequence, so DBI command failures may not abort prepare. The init sequence includes long fixed sleeps and repeated display-on/write-memory-start commands that are hardware-specific.

## Test Signals

Validate SPI DBI initialization, GPIO acquisition, regulator enable order, expected 240x320 mode with correct bus flags and sync flags, visible RGB scanout after prepare, DBI command traces during initialization, and clean display-off/reset/power-off during unprepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9805.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9805.c

## Purpose

This MIPI DSI DRM panel driver supports Ilitek ILI9805 controller panels, with descriptors for Giantplus GPM1790A0 and Tianma TM041XDHG01. It uses descriptor-provided command arrays and fixed display modes.

## Important APIs, Types, And Functions

`struct ili9805_instr` represents one DCS write buffer plus an optional delay. `struct ili9805_desc` stores the panel name, init array, fixed mode, and physical dimensions. `struct ili9805` owns the DRM panel, DSI device, descriptor, `dvdd`/`avdd` regulators, and reset GPIO.

`ili9805_power_on()` enables regulators and toggles reset. `ili9805_activate()` iterates descriptor commands with `mipi_dsi_dcs_write_buffer()`, exits sleep, waits, and turns display on. `ili9805_deactivate()` sends display-off and sleep-in. `ili9805_prepare()` and `ili9805_unprepare()` compose power and DCS activation/deactivation. Probe configures two-lane RGB888 DSI video and attaches the panel.

## Control Flow

Probe allocates the panel, stores descriptor match data, configures DSI flags including HSE, sync pulse, non-continuous clock, LPM, and no-EOT, obtains regulators and reset GPIO, gets a DT backlight, adds the panel, and attaches DSI. Prepare enables `avdd`, then `dvdd`, releases reset, waits 120 ms, sends the descriptor init table, exits sleep, and turns display on. Unprepare sends display-off/sleep-in and then disables power.

## State And Persistence

There is no persistent state. Panel behavior is determined by static descriptor arrays selected from OF match data. Runtime state is the DSI attachment, regulators, reset GPIO, and optional DT backlight.

## Dependencies And Integration Points

The driver integrates with DRM panel, MIPI DSI, GPIO, regulators, and OF match data. It requires supplies `dvdd` and `avdd`, a `reset` GPIO, a backlight binding when needed, and compatibles `giantplus,gpm1790a0` or `tianma,tm041xdhg01`.

## Risks

The descriptor width/height fields are not copied into the `drm_display_mode`; `ili9805_get_modes()` uses `mode->width_mm` and `mode->height_mm`, which are unset in the provided timing structures. The code logs DSI failures in activation/deactivation but `ili9805_unprepare()` ignores a deactivate failure before powering off. Command arrays are opaque and panel-specific. The two compatibles share DSI bus configuration even though they have different vertical resolutions.

## Test Signals

Check DSI attach, correct fixed 480x480 or 480x768 mode selection, physical size reporting, backlight binding, reset and regulator sequencing, command-array writes with delays, visible output after sleep-out/display-on, and suspend/resume behavior when DCS sleep commands fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9805.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.c

## Purpose

This file provides the shared core for Ilitek ILI9806E panel transports. It owns common panel allocation, supplies, reset GPIO, backlight binding, power sequencing, and exported helper APIs used by DSI and SPI transport drivers.

## Important APIs, Types, And Functions

`struct ili9806e` contains a transport pointer, DRM panel, supply count and array, and reset GPIO. Exported symbols are `ili9806e_get_transport()`, `ili9806e_power_on()`, `ili9806e_power_off()`, `ili9806e_probe()`, and `ili9806e_remove()`.

`ili9806e_probe()` allocates core state, stores the caller-provided transport pointer, chooses supplies (`vdd` plus optional `vccio` for Densitron and Ortustech DSI panels), gets reset GPIO, initializes the DRM panel with transport-supplied funcs and connector type, attaches a DT backlight, optionally sets `prepare_prev_first`, and adds the panel.

## Control Flow

Transport probe allocates its own bus-specific state and calls `ili9806e_probe()`. Later transport panel callbacks call `ili9806e_power_on()` before bus-specific init and `ili9806e_power_off()` during unprepare. Removal calls `ili9806e_remove()` after transport detach if needed.

## State And Persistence

The core keeps only volatile driver data in `dev_set_drvdata()`. The transport pointer is an untyped pointer back to the DSI or SPI wrapper state. There is no persistent storage.

## Dependencies And Integration Points

The core depends on DRM panel, regulators, GPIO descriptors, OF compatible checks, device properties, backlight binding, and exported GPL symbols. It is integrated by `panel-ilitek-ili9806e-dsi.c` and `panel-ilitek-ili9806e-spi.c`.

## Risks

Supply selection is based on hard-coded compatible checks in the core, so adding new transports or compatibles may require core changes. The untyped `void *transport` relies on the transport driver and panel funcs agreeing on the concrete type. `ili9806e_probe()` sets drvdata on the same device used by transport drivers, so ordering with bus-level drvdata must be considered. The core does not unwind panel add through devm, so transports must call `ili9806e_remove()` on later attach failure.

## Test Signals

Validate exported symbol linkage for both transport modules, regulator and reset GPIO acquisition, backlight binding, correct `prepare_prev_first` on compatible panels, clean power on/off sequencing, and panel removal after DSI attach failure or SPI driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.h

## Purpose

This header declares the shared ILI9806E core interface used by bus-specific DSI and SPI panel drivers.

## Important APIs, Types, And Functions

It declares `ili9806e_get_transport()` for recovering bus-specific state from a `drm_panel`, `ili9806e_power_on()` and `ili9806e_power_off()` for shared regulator/reset sequencing, `ili9806e_probe()` for common panel creation, and `ili9806e_remove()` for panel removal.

## Control Flow

Transport drivers include this header, allocate their own state, call `ili9806e_probe()` with their transport pointer and panel funcs, and then use `ili9806e_get_transport()` inside those funcs to recover their state. Power helpers are called from transport prepare/unprepare paths.

## State And Persistence

The header stores no state. Its contract implies that core state is stored as device driver data and that the transport pointer remains valid for the panel lifetime.

## Dependencies And Integration Points

The declarations depend on `struct drm_panel`, `struct device`, and `struct drm_panel_funcs` being visible from including source files. It is a local integration point between the core, DSI, and SPI files.

## Risks

Because the transport handle is `void *`, type safety is enforced only by convention. The header does not document ownership or lifetime rules, so transport drivers must preserve the transport allocation for at least as long as the DRM panel is registered.

## Test Signals

Build tests should confirm all prototypes match the exported definitions. Runtime validation is indirect through DSI and SPI transport probe, prepare, unprepare, and remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-dsi.c

## Purpose

This is the MIPI DSI transport driver for ILI9806E panels using the shared core. It supports Densitron DMT028VGHMCMI-1D and Ortustech COM35H3P70ULC panels, each with a descriptor-provided fixed mode and initialization sequence.

## Important APIs, Types, And Functions

`struct ili9806e_dsi_panel_desc` describes a mode, DSI flags, pixel format, lane count, and optional init sequence. `struct ili9806e_dsi_panel` stores the DSI device, descriptor, and orientation.

`ili9806e_dsi_on()` sends the optional init sequence, exits sleep, waits 120 ms, and turns display on. `ili9806e_dsi_off()` sends display-off and sleep-in. Panel funcs call shared power helpers and use `ili9806e_get_transport()` to recover DSI state. `ili9806e_dsi_probe()` configures the DSI bus, reads orientation, calls the shared core probe, and attaches DSI.

## Control Flow

Probe allocates DSI transport state, gets match data, stores DSI drvdata, applies descriptor DSI flags/format/lanes, reads panel orientation, invokes `ili9806e_probe()` with DSI connector funcs, then attaches the DSI device. Prepare powers on through the core, runs the init sequence, exits sleep, and sets display on. Unprepare sends off/sleep commands, powers off, and returns power-off status.

## State And Persistence

No state is persisted. Runtime state is descriptor match data, orientation, DSI device pointer, and core-owned regulators/reset/backlight. The init sequences program volatile controller pages.

## Dependencies And Integration Points

This file depends on the ILI9806E core header, DRM panel/probe helper, MIPI DSI helpers, OF/device match data, and panel orientation. It integrates with the core by passing transport state and with device tree through `densitron,dmt028vghmcmi-1d` and `ortustech,com35h3p70ulc`.

## Risks

The shared core overwrites device drvdata with its own core state after this file sets DSI drvdata, so remove paths avoid using `mipi_dsi_get_drvdata()` and call the core directly. This is intentional but fragile if future code expects DSI drvdata to be the transport. Init sequences are large page-based register tables and are not validated beyond DSI accumulated error. `mipi_dsi_detach()` return is ignored in remove.

## Test Signals

Check orientation parsing, fixed mode reporting, successful core probe and DSI attach, correct lane/format/mode flags per compatible, visible display after init/sleep-out/display-on, DT backlight binding through the core, and clean DSI detach plus panel removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-spi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-spi.c

## Purpose

This is the SPI/MIPI DBI transport driver for ILI9806E panels using the shared core. It supports the Rocktech RK050HR345-CT106A panel as a DPI connector with SPI command initialization.

## Important APIs, Types, And Functions

`struct ili9806e_spi_panel` stores the SPI device, embedded `mipi_dbi`, and descriptor. `struct ili9806e_spi_panel_desc` stores a fixed mode, media bus format, bus flags, and init callback.

`ili9806e_spi_prepare()` powers on through the core and runs the descriptor init sequence. `ili9806e_spi_unprepare()` sends display-off/sleep-in via DBI and powers off. `ili9806e_spi_get_modes()` duplicates the fixed mode and fills connector physical size, bus flags, and bus format. `ili9806e_spi_probe()` initializes DBI over SPI and calls the shared core probe with a DPI connector type.

## Control Flow

Probe allocates transport state, stores SPI and descriptor pointers, initializes MIPI DBI without a D/C GPIO argument, and delegates common panel setup to the core. Prepare powers on, sends page-based DBI commands for interface, power, timing, gamma, GIP, address mode, sleep-out, waits, and display-on. Unprepare sends display-off and sleep-in before core power-off. Remove only removes the core panel because there is no DSI host detach.

## State And Persistence

There is no persistence. Runtime state is the DBI context, SPI device, descriptor, and core-owned power/backlight resources. Bus format and bus flags are descriptor constants exposed during mode query.

## Dependencies And Integration Points

The driver depends on SPI, MIPI DBI helpers, DRM panel, media bus formats, the shared ILI9806E core, and OF/SPI IDs. It exposes compatible `rocktech,rk050hr345-ct106a` and SPI ID `rk050hr345-ct106a`.

## Risks

DBI command helpers used in the init and off paths do not propagate errors here, so prepare can return success despite failed SPI commands. The core power-off return is logged but `ili9806e_spi_unprepare()` returns zero. The DBI init call has no D/C GPIO, so it depends on the SPI wiring/protocol supported by `mipi_dbi_spi_init()`. Any new panel requires careful bus format and bus flag selection, since these affect the upstream display controller.

## Test Signals

Validate SPI DBI initialization, core regulator/reset/backlight setup, 480x854 mode and RGB888 bus format reporting, display-on after the init sequence, command traces for sleep-out/display-on, and suspend/resume behavior where DBI off and core power-off both execute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-spi.c -->
