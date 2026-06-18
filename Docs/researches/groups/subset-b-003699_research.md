# subset-b-003699 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-khadas-ts050.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-khadas-ts050.c

Purpose: This file implements a DRM MIPI-DSI panel driver for Khadas TS050 and TS050v2 portrait touch display panels. It provides the panel lifecycle hooks needed by DRM bridge/connector code, programs vendor-specific DSI initialization tables, exposes a fixed 1080x1920 video mode, and binds the panel to `khadas,ts050` / `khadas,ts050v2` device-tree compatibles.

Important APIs, types, and functions: `struct khadas_ts050_panel` stores the `drm_panel`, DSI device, power regulator, reset/enable GPIOs, and matched `khadas_ts050_panel_data`. `struct khadas_ts050_panel_cmd` and `struct khadas_ts050_panel_data` describe static DCS command tables; `ts050_init_code` is a long undocumented page-switching table, and `ts050v2_init_code` is a shorter alternate table. `khadas_ts050_panel_prepare()` enables power, toggles GPIO reset/enable, writes the selected init table, exits sleep, enables tearing at vblank, and turns the display on. `khadas_ts050_panel_disable()` sends display-off. `khadas_ts050_panel_unprepare()` enters sleep and powers down. `khadas_ts050_panel_get_modes()` duplicates `default_mode`, fills size and 8 bpc metadata, and adds the mode. Probe configures four DSI lanes, RGB888, video burst/LPM/no-EoT flags, allocates the panel with `devm_drm_panel_alloc()`, resolves match data, registers backlight via `drm_panel_of_backlight()`, and attaches to DSI.

Control flow: Device matching selects one of two init-code descriptors. Probe sets DSI bus parameters before attach, then DRM later calls `prepare` before scanout. The prepare path asserts enable low, enables the `power` regulator, asserts enable high, resets the panel, writes preliminary page-4 commands, sleeps 100 ms, iterates every selected init command with `mipi_dsi_dcs_write()`, exits sleep, returns to CMD1, enables tear-on, and sets display-on. On any DSI failure after power-up, the common `poweroff` path deasserts enable, asserts reset, disables the regulator, and returns the DSI error. Disable only turns display off; unprepare handles sleep and power removal.

State and persistence: Driver state is per panel instance and stored in the DSI drvdata. Persistent hardware state is mostly the vendor register table written during prepare and the DSI host mode flags chosen at probe. No software prepared/enabled flags are kept, so the DRM core is expected to serialize lifecycle calls. GPIO polarity is important: the code uses reset high as asserted/off in error and unprepare paths, and enable high during operation.

Dependencies and integration points: This driver depends on DRM panel helpers, DRM MIPI-DSI helpers, regulator and GPIO consumer APIs, the optional device-tree backlight binding, and OF match data. Integration is through `module_mipi_dsi_driver()`, the `drm_panel_funcs` callbacks, `mipi_dsi_attach()`, and compatible strings. The DSI host must support four-lane RGB888 video burst operation and low-power command writes during initialization.

Risks: The init arrays are vendor/undocumented register programming; command order, page selection, and per-compatible table selection are high-risk. The prepare loop passes `&...data` rather than the array expression itself; it is the same address for the first element but fragile style. Preliminary DSI writes before the loop ignore return values, so early page-select failures may only surface later. There is no explicit display-off in unprepare; callers should use the normal disable/unprepare sequence. Reset/enable GPIO polarity must match the binding or the panel can remain held in reset or powered while disabled.

Test signals: Build coverage should include `CONFIG_DRM_PANEL_KHADAS_TS050` and OF matching for both compatibles. Runtime signals are successful DSI attach, a single fixed 1080x1920 mode with 64x118 mm size and 8 bpc, backlight association, no DSI transfer errors during prepare, visible scanout after display-on, clean sleep/power-off on unprepare, and correct behavior for both TS050 and TS050v2 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-khadas-ts050.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-kingdisplay-kd097d04.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-kingdisplay-kd097d04.c

Purpose: This is a DRM MIPI-DSI panel driver for the Kingdisplay KD097D04 9.7-inch 1536x2048 panel. It provides fixed-mode reporting, panel power sequencing, a vendor-supplied generic-write initialization table, optional enable GPIO handling, and DSI registration under `kingdisplay,kd097d04`.

Important APIs, types, and functions: `struct kingdisplay_panel` holds the `drm_panel`, `mipi_dsi_device`, power regulator, and optional enable GPIO. `struct kingdisplay_panel_cmd` stores two-byte generic register writes. `init_code[]` contains voltage, VCOM, gamma, GOA mux/timing, and GOE settings. `kingdisplay_panel_prepare()` enables `power`, waits, sets enable high, writes every init command via `mipi_dsi_generic_write()`, exits sleep, and turns display on. `kingdisplay_panel_disable()` sends display-off, and `kingdisplay_panel_unprepare()` sends sleep-in, waits 120 ms, lowers enable, and disables the regulator. `kingdisplay_panel_get_modes()` adds the fixed 1536x2048 mode and display metadata.

Control flow: Probe fixes the DSI link to four lanes, RGB888, video burst, low-power commands, and no EoT packet. It then allocates/registers the panel, requests resources, and attaches to the DSI host. At prepare time, regulator and GPIO setup precede all generic writes. If any command or DCS sleep/display command fails, the error path lowers enable and disables the regulator. Normal shutdown expects `disable` to turn the display off before `unprepare` puts it in sleep and removes power.

State and persistence: Software state is only the device resources and DSI drvdata; panel registers persist until sleep/power loss. The optional enable GPIO is allowed to be absent; `gpiod_set_value_cansleep()` tolerates NULL. The init table values become persistent panel analog/gamma/GOA state for the current power cycle.

Dependencies and integration points: The file integrates with the DSI panel subsystem through `module_mipi_dsi_driver()`, DRM panel callbacks, `drm_panel_of_backlight()`, and the OF compatible. It depends on a `power` regulator and may use an `enable` GPIO and external backlight phandle. DSI command transfer uses generic writes for vendor table entries and DCS helpers for sleep/display state.

Risks: The init table is not sourced from the public datasheet, so regressions are hard to reason about without hardware. `devm_gpiod_get_optional()` errors other than probe defer are downgraded to NULL after a debug message, so a misconfigured enable GPIO may silently turn into "no GPIO." The fixed mode has no explicit sync flags, so host-side interpretation relies on defaults. Removing the panel before a normal DRM disable path can leave only `drm_panel_remove()` cleanup, not a direct power-down.

Test signals: Probe should attach without DSI errors and report one preferred 1536x2048 mode with 147x196 mm size and 8 bpc. Runtime validation should cover prepare/unprepare cycles, regulator disable on failed init write, optional versus present enable GPIO, backlight binding, and visible scanout with stable gamma/GOA output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-kingdisplay-kd097d04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-leadtek-ltk050h3146w.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-leadtek-ltk050h3146w.c

Purpose: This driver supports several related Leadtek 5-inch 720x1280 MIPI-DSI panels: `leadtek,ltk050h3146w`, `leadtek,ltk050h3146w-a2`, and `leadtek,ltk050h3148w`. It abstracts panel variants with per-compatible display modes, DSI mode flags, and initialization routines, while sharing the same regulator, reset, backlight, and DRM panel plumbing.

Important APIs, types, and functions: `struct ltk050h3146w_desc` carries `mode_flags`, a fixed `drm_display_mode`, and an `init()` callback. `struct ltk050h3146w` stores the panel, reset GPIO, `vci` and `iovcc` regulators, and matched descriptor. Variant init functions are `ltk050h3146w_init_sequence()`, `ltk050h3146w_a2_init_sequence()`, and `ltk050h3148w_init_sequence()`. The A2 path uses `ltk050h3146w_a2_select_page()` and `ltk050h3146w_a2_write_page()` to write page-specific generic command tables (`page1_cmds`, `page3_cmds`, `page4_cmds`). `ltk050h3146w_prepare()` powers regulators, toggles reset, runs the descriptor init, exits sleep, and sets display-on. `ltk050h3146w_unprepare()` sends display-off and sleep-in through `mipi_dsi_multi_context`, then disables regulators.

Control flow: OF match data selects the descriptor before probe sets DSI lanes, format, and descriptor flags. Prepare enables `vci` before `iovcc`, pulses reset high then low, waits, runs the variant-specific command sequence, exits sleep, waits 120 ms, and turns display on. `mipi_dsi_multi_context` accumulates DSI errors across the init sequence, so the final error check powers down both supplies on failure. Get-modes duplicates the descriptor mode and marks it preferred.

State and persistence: The only persistent software state is the descriptor pointer and resource handles. Panel hardware state consists of page-selected vendor register values, tear-on configuration, and display-on/sleep state. The code does not keep a prepared flag. DSI command writes use the DSI host derived from `ctx->dev`, so the device must stay associated with the DSI device.

Dependencies and integration points: This file depends on DRM MIPI-DSI multi-context helpers, fixed DRM display modes, GPIO/regulator APIs, and OF match data. It integrates with external backlight via `drm_panel_of_backlight()`, with DSI via `mipi_dsi_attach()`, and with DRM through `drm_panel_funcs`. It uses both DCS and generic DSI writes depending on the variant.

Risks: All three vendor init sequences are sparsely documented; the A2 comments explicitly question page selection and tear-on parameter provenance. Power sequencing is strict, and the error path must disable `iovcc` and `vci` in reverse order. Unprepare returns immediately on accumulated DSI error before disabling regulators, so a sleep/display-off transfer failure can leave supplies enabled. Variant mode flags differ; mixing descriptors can produce a panel that attaches but does not scan out correctly.

Test signals: Build should cover all three compatibles. Runtime tests should verify each compatible reports its correct 720x1280 timing and size, DSI flags match the descriptor, both regulators are enabled/disabled around prepare/unprepare, init sequences complete with no accumulated DSI errors, reset polarity is correct, backlight binds, and repeated suspend/resume does not leave regulators on after DSI failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-leadtek-ltk050h3146w.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-leadtek-ltk500hd1829.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-leadtek-ltk500hd1829.c

Purpose: This driver supports Leadtek LTK500HD1829 and LTK101B4029W MIPI-DSI panels using shared four-lane RGB888 video-burst setup and per-compatible vendor initialization tables. It reports fixed 720x1280 or 800x1280 modes, sequences `vcc`/`iovcc` regulators and reset GPIO, and registers with the DRM panel/DSI subsystems.

Important APIs, types, and functions: `struct ltk500hd1829_cmd` stores two-byte vendor register writes. `struct ltk500hd1829_desc` maps a fixed mode to an init table and count. `ltk101b4029w_init[]` and `ltk500hd1829_init[]` contain page-based voltage, gamma, GIP, and timing configuration. `ltk500hd1829_prepare()` enables `vcc` then `iovcc`, pulses reset, writes the descriptor init sequence with `mipi_dsi_generic_write()`, exits sleep, and turns display on. `ltk500hd1829_unprepare()` sends display-off and sleep-in, waits 120 ms, then disables `iovcc` and `vcc`. `ltk500hd1829_get_modes()` duplicates descriptor mode and marks it preferred.

Control flow: Probe fetches match data, resources, backlight, registers the panel, and attaches the DSI device. DSI parameters are fixed to four lanes, RGB888, video burst, low-power command mode, and no EoT. During prepare, any regulator, generic write, sleep-out, or display-on failure jumps to a cleanup label that disables already-enabled supplies. During normal unprepare, DSI sleep/display-off errors are logged but do not prevent power removal.

State and persistence: Persistent software state is the descriptor and resource pointers stored in DSI drvdata. Hardware state persists only across a powered session and is dominated by the selected init table. There are no explicit enabled/prepared flags or cached brightness; external backlight state is owned by the DRM/backlight framework.

Dependencies and integration points: The driver depends on DRM panel, MIPI-DSI, GPIO, regulator, OF match-data, and optional external backlight APIs. The bindings must provide `vcc`, `iovcc`, and optionally reset/backlight resources for the selected compatible. It integrates with DSI through `mipi_dsi_attach()` and with DRM through `drm_panel_funcs`.

Risks: Both initialization arrays are vendor data with many undocumented register writes; copying or reordering commands can break panel power rails, gamma, or scan direction. Probe manually handles `-EPROBE_DEFER` logging for regulators instead of `dev_err_probe()` everywhere. The reset pulse is very short (`10-20 us`) and depends on panel timing tolerances. The DSI mode flags are not descriptor-specific even though the supported panels have different resolutions.

Test signals: Validate that each compatible reports the expected mode and physical dimensions, DSI attach succeeds with four lanes, prepare writes all table entries without transfer errors, sleep/display-off failures still lead to power removal, and regulator sequencing is correct under error injection. Hardware tests should include repeated suspend/resume and visual checks for gamma/GIP orientation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-leadtek-ltk500hd1829.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-lb035q02.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-lb035q02.c

Purpose: This is a SPI-controlled DRM DPI panel driver for the LG.Philips LB035Q02 320x240 LCD. It initializes panel registers over SPI, exposes a fixed DPI mode and bus flags, and uses an enable GPIO for runtime on/off.

Important APIs, types, and functions: `struct lb035q02_device` contains the `drm_panel`, SPI device, and enable GPIO. `lb035q02_write()` performs the panel's two-part SPI transaction: register index (`0x70`) followed by value (`0x72`) with chip-select change between transfers. `lb035q02_init()` writes the datasheet initialization table. `lb035q02_enable()` and `lb035q02_disable()` toggle the enable GPIO. `lb035q02_get_modes()` duplicates `lb035q02_mode`, adds width/height metadata, and sets DPI bus flags.

Control flow: Probe allocates the panel as `DRM_MODE_CONNECTOR_DPI`, requests the mandatory enable GPIO low, immediately initializes the panel over SPI, and registers it with DRM. DRM enable/disable callbacks only control the enable GPIO; there are no prepare/unprepare callbacks. Remove unregisters the panel and calls `drm_panel_disable()`.

State and persistence: The SPI-programmed LCD register state persists while the panel remains powered by board-level supplies outside this driver. Software does not track the current register state after probe. The enable GPIO state is the only runtime state toggled by DRM callbacks.

Dependencies and integration points: The driver depends on SPI core, DRM panel/mode APIs, GPIO consumer APIs, OF/SPI device ID matching, and DPI bus consumers that use `connector->display_info.bus_flags`. It integrates with board device tree via `lgphilips,lb035q02` and with SPI modalias `lb035q02`.

Risks: Initialization happens in probe, not in prepare, so suspend/resume or power loss outside the driver may require reprobe or additional PM support. The bus edge flags include a FIXME noting datasheet and Gumstix board code disagree on pixel data sampling edge. The SPI transaction format relies on chip-select behavior (`cs_change = 1`); controller quirks can corrupt register writes. No regulator/backlight handling is present.

Test signals: Compile and probe should succeed on SPI with an enable GPIO. Runtime signals are successful SPI init writes, one preferred 320x240 DPI mode with 70x53 mm size, correct DE/sync/pixel sampling on real hardware, and enable GPIO toggling visible in panel blank/unblank tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-lb035q02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-ld070wx3.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-ld070wx3.c

Purpose: This file implements a DRM MIPI-DSI panel driver for the LG LD070WX3-SL01 800x1280 panel. It sequences two regulators, sends a short DCS setup sequence after reset/soft-reset, exposes a fixed mode, and supports an external backlight.

Important APIs, types, and functions: `lg_ld070wx3_supplies[]` declares `vdd` and `vcc`. `struct lg_ld070wx3` stores the panel, DSI device, and devm-allocated regulator bulk array. `lg_ld070wx3_prepare()` bulk-enables supplies, waits 115 ms, sends DCS soft reset, configures differential input impedance and MIPI clock drive through test-mode commands, and returns accumulated DSI errors. `lg_ld070wx3_unprepare()` sends sleep-in, waits 50 ms, disables regulators, and enforces a 1 second off time. `lg_ld070wx3_get_modes()` uses `drm_connector_helper_get_modes_fixed()`.

Control flow: Probe obtains constant regulator bulk data, fixes DSI to four lanes RGB888 video/LPM, resolves external backlight, registers the panel, and uses `devm_mipi_dsi_attach()`. Prepare is regulator-first, delay, soft-reset, test command writes. Unprepare is sleep-in, supply-off, mandatory off-delay. Remove only removes the panel because DSI attach is devm-managed.

State and persistence: Software state is limited to resource handles. Hardware state includes the short set of DCS/test-mode configuration registers and sleep state. The enforced 1 second delay after regulator disable is a persistent timing requirement rather than a stored state variable.

Dependencies and integration points: Dependencies include DRM panel/helper APIs, MIPI DSI multi-context helpers, GPIO headers though no GPIO is used, regulator bulk APIs, OF match, and optional backlight lookup. The DSI host must support video mode and LPM command writes.

Risks: `lg_ld070wx3_unprepare()` ignores `ctx.accum_err` from sleep-in and always returns 0 after disabling supplies. The 115 ms mdelay is a busy wait, not sleep, which is unusual for panel bring-up. The DCS test-mode writes are not guarded by detailed comments or descriptors, so panel revisions may need different values. No reset GPIO is handled, so boards requiring external reset sequencing need binding/driver changes.

Test signals: Validate regulator bulk acquisition, DSI attach, fixed 800x1280 mode with 94x151 mm size, no DSI errors in prepare, visible panel output, and suspend/resume that observes the 1 second power-off requirement. Backlight binding should be checked with a DT backlight phandle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-ld070wx3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-lg4573.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-lg4573.c

Purpose: This is a SPI-controlled DRM DPI panel driver for LG4573-based 480x800 LCD panels. It sends DCS-like 16-bit SPI command/data words for display, power, and gamma configuration, and exposes a fixed DPI mode through DRM.

Important APIs, types, and functions: `struct lg4573` stores the DRM panel, SPI device, and an unused `videomode` field. `lg4573_spi_write_u16()` writes a big-endian 16-bit word over SPI; command words use `0x70xx`, data words use `0x72xx`. `lg4573_display_mode_settings()`, `lg4573_power_settings()`, and `lg4573_gamma_settings()` send static u16 arrays. `lg4573_init()` runs those three blocks. `lg4573_enable()` initializes and then sends exit-sleep/display-on. `lg4573_disable()` sends display-off, waits 120 ms, and enters sleep. `lg4573_get_modes()` exposes the default 480x800 mode.

Control flow: Probe allocates a DPI panel, stores SPI drvdata, forces `bits_per_word = 8`, calls `spi_setup()`, and adds the panel. Enable is the full initialization path each time DRM enables the panel. Disable is the display-off/sleep path. Remove calls display-off and removes the panel.

State and persistence: Panel register configuration is resent on every enable. The driver does not manage regulators, reset GPIOs, or a backlight, so those states are external. There is no cached enabled state; SPI/DPI panel state persists until sleep or external power/reset.

Dependencies and integration points: The driver uses SPI core, DRM panel/mode APIs, MIPI DCS constants, and OF matching on `lg,lg4573`. It integrates as a DPI connector because pixel data is supplied outside the SPI control channel.

Risks: `lg4573_enable()` ignores the return value of `lg4573_init()` and proceeds to display-on even if configuration writes fail. No power/reset sequencing is present despite including regulator/GPIO headers. Fixed timings may not match all LG4573-attached panels. SPI word format depends on the panel's 9/16-bit command encoding and on SPI controller byte ordering.

Test signals: Tests should verify SPI setup, successful writes of init arrays, one preferred 480x800 mode with 61x103 mm metadata, clean display-off on disable/remove, and visible DPI scanout. Error injection should confirm the ignored init error does not mask real hardware bring-up failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-lg4573.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-sw43408.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-sw43408.c

Purpose: This driver supports the LG SW43408 / LH546WF1-ED01 1080x2160 MIPI-DSI panel, including Display Stream Compression setup and an internal DSI brightness backlight. The panel is exposed as a fixed DSI mode and requires DSC parameters on the DSI device.

Important APIs, types, and functions: `struct sw43408_panel` stores the panel, DSI link, bulk supplies, reset GPIO, and `drm_dsc_config`. `sw43408_prepare()` enables supplies, runs `sw43408_reset()`, and calls `sw43408_program()`. `sw43408_program()` writes panel setup commands, exits sleep, sets display on, temporarily clears `MIPI_DSI_MODE_LPM` to send the DSC PPS, packs PPS via `drm_dsc_pps_payload_pack()`, sends it with `mipi_dsi_picture_parameter_set_multi()`, restores LPM, and enables DSC compression mode with an offset selector. `sw43408_backlight_update_status()` sends 16-bit large display brightness over DSI. Probe initializes DSC version, slice dimensions, bpc/bpp, block prediction, assigns `dsi->dsc`, and attaches.

Control flow: Probe sets DSI to four lanes RGB888 LPM-only initially, registers regulators/reset/backlight, marks `prepare_prev_first`, configures DSC, and attaches. Prepare bulk-enables `vddi` and `vpnl`, waits, performs a reset pulse pattern, and runs the full DSI program. Unprepare sends display-off and sleep-in, waits, asserts reset, and disables supplies.

State and persistence: `ctx->dsc` persists for the lifetime of the DSI device and is referenced by `dsi->dsc`. The driver mutates `dsi->mode_flags` during programming to leave low-power mode while sending PPS, then restores it. Panel state includes DSC/PPS selection, compression mode, gamma/brightness registers, and sleep/display state. Backlight brightness is controlled by a registered platform backlight device.

Dependencies and integration points: The driver depends on DRM DSC helpers, DRM MIPI-DSI helpers, regulator bulk APIs with load hints, GPIO, backlight registration, and `drm_connector_helper_get_modes_fixed()`. The DSI host and encoder must support DSC and PPS transmission. OF compatibles include legacy `lg,sw43408` and `lg,sw43408-lh546wf1-ed01`.

Risks: The panel works only in DSC mode; missing or incompatible host DSC support will prevent usable scanout despite successful probe. Temporarily changing `mode_flags` around PPS transmission is sequencing-sensitive. Backlight registration is internal rather than `drm_panel_of_backlight()`, so board bindings must not expect an external backlight for this path. Unprepare returns regulator-disable error preferentially over accumulated DSI errors only through `ret ? : ctx.accum_err`, which is concise but can hide the second failure.

Test signals: Verify the fixed 1080x2160 mode, DSC parameters on `dsi->dsc`, successful PPS/compression commands, display output without corruption, large-brightness DCS writes from backlight changes, regulator/reset sequencing, and suspend/resume. Host logs should show no DSI errors when switching LPM around PPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-sw43408.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lincolntech-lcd197.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lincolntech-lcd197.c

Purpose: This file implements a DRM MIPI-DSI driver for the Lincoln Technologies LCD197 1080x1920 panel. It sequences a single power regulator with enable/reset GPIOs, sends a long vendor DSI initialization block, and exposes separate prepare/enable and disable/unprepare phases.

Important APIs, types, and functions: `struct lincoln_lcd197_panel` stores the DRM panel, DSI pointer, `power` regulator, enable GPIO, and reset GPIO. `lincoln_lcd197_panel_prepare()` powers and resets the panel, sends Himax-like vendor commands, sets address mode, exits sleep, and waits. `lincoln_lcd197_panel_enable()` sends display-on. `lincoln_lcd197_panel_disable()` sends display-off. `lincoln_lcd197_panel_unprepare()` enters sleep, lowers enable, asserts reset, and disables the regulator. `lincoln_lcd197_panel_get_modes()` returns the fixed `lcd197_mode`.

Control flow: Probe fixes DSI to four-lane RGB888 video burst, allocates the panel, requests mandatory supply/GPIOs/backlight, adds the panel, and attaches to DSI. Prepare drives enable low, enables the regulator, enable high, reset high then low, waits 50 ms, writes the vendor init sequence with `mipi_dsi_dcs_write_seq_multi()`, exits sleep, and on accumulated error powers the panel down. Enable is intentionally separate and only sends display-on.

State and persistence: Software state is resource pointers in drvdata. Hardware state includes the vendor init register set, display address mode, sleep state, and display on/off state. No prepared/enabled booleans are cached. The fixed mode lacks `DRM_MODE_TYPE_PREFERRED`, only `DRM_MODE_TYPE_DRIVER`.

Dependencies and integration points: The driver uses DRM panel, DSI multi-context helpers, regulator/GPIO APIs, fixed-mode helper, external backlight lookup, and OF compatible `lincolntech,lcd197`. It integrates with MIPI hosts through `module_mipi_dsi_driver()`.

Risks: The init sequence has an apparent page-register issue: after writing `0xbd, 0x01`, the next `0xd8` write is immediately followed by another `0xd8` before changing to page 2, which may be intentional vendor behavior but is difficult to validate. The mode sets `htotal = 1080 + 204` and `vtotal = 1920 + 79` rather than explicit porch sums, so edits must preserve timing intent. Mandatory GPIO polarity must match binding defaults. Failure in enable/disable only reports accumulated DSI errors; power state remains for normal DRM sequencing.

Test signals: Confirm DSI attach, one fixed 1080x1920 mode with 79x125 mm size, external backlight binding, no accumulated errors in prepare/enable/disable, and correct power/reset behavior on error. Hardware tests should inspect orientation/address mode and gamma after the vendor sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lincolntech-lcd197.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lvds.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lvds.c

Purpose: This is a generic platform-driver DRM panel for simple LVDS panels described entirely by device tree. It parses timing, data mapping, data mirroring, orientation, optional supply/GPIO/backlight resources, and exposes the resulting mode and bus format to DRM.

Important APIs, types, and functions: `struct panel_lvds` stores the panel, device, label, parsed `drm_display_mode`, bus flags/format, optional regulator, optional enable/reset GPIOs, and orientation. `panel_lvds_parse_dt()` calls `of_drm_get_panel_orientation()`, `of_get_drm_panel_display_mode()`, `drm_of_lvds_get_data_mapping()`, and checks `data-mirror`. `panel_lvds_prepare()` enables the optional supply and enable GPIO. `panel_lvds_unprepare()` disables enable GPIO and supply. `panel_lvds_get_modes()` duplicates the parsed mode, sets width/height, bus formats/flags, and orientation. `panel_lvds_get_orientation()` returns the parsed orientation.

Control flow: Probe allocates an LVDS connector panel, parses DT first, then requests optional power, enable/reset GPIOs, and backlight. It registers the panel and stores drvdata. Runtime prepare/unprepare only toggles supply and enable. The reset GPIO is requested with default asserted/high but is not toggled afterward.

State and persistence: The parsed display mode, bus mapping, flags, and orientation persist in the driver instance. There is no hardware register state because LVDS panels are treated as timing-only devices. Optional supply and enable GPIO are the only runtime-managed states. The reset GPIO remains at the devm-requested initial value unless changed externally, which may be a binding/design issue for panels requiring reset release.

Dependencies and integration points: This file depends on platform bus, DRM panel, DRM OF helpers, LVDS data mapping parser, display-timing DT bindings, regulator/GPIO/backlight APIs, and compatible `panel-lvds`. It integrates with LVDS encoders/bridges through connector display-info bus formats and flags.

Risks: The generic driver deliberately does not support ordered multi-supply or complex reset timing; panels needing that require a dedicated driver. `panel_lvds_get_modes()` returns 0 rather than `-ENOMEM` on duplicate failure, which may hide allocation errors. Reset GPIO is acquired but not otherwise used. Invalid or missing `data-mapping` fails probe, so bindings must be complete. Orientation is set both through legacy connector helper and panel callback for compatibility.

Test signals: DT validation should cover `panel-timing`, `data-mapping`, optional `data-mirror`, orientation, regulator, enable/reset GPIO, and backlight. Runtime signals are one preferred mode matching DT, correct LVDS bus format/bit order, proper connector orientation, and supply/enable toggles around panel prepare/unprepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lxd-m9189a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lxd-m9189a.c

Purpose: This driver supports the LXD M9189A 1024x600 MIPI-DSI panel using EK79007AD3 manufacturer commands. It handles power, reset, standby GPIOs, gamma setup, sleep/display state, fixed-mode reporting, and external backlight binding.

Important APIs, types, and functions: Manufacturer command macros define gamma registers and panel control. `struct m9189_panel` stores the DRM panel, DSI device, `power` regulator, reset GPIO, and standby GPIO. `m9189_reset()` performs a low/high/low reset sequence. `m9189_on()` sets LPM, writes gamma values, configures four-lane panel control, exits sleep, and turns display on. `m9189_disable()` clears LPM, enters sleep, and asserts standby. `m9189_prepare()` enables power, deasserts standby, resets, and runs `m9189_on()`. `m9189_unprepare()` asserts standby/reset and disables the regulator. Probe uses manual `devm_kzalloc()` plus `drm_panel_init()` rather than `devm_drm_panel_alloc()`.

Control flow: Probe requests mandatory regulator/reset/standby resources, fixes DSI to four lanes RGB888 video burst, initializes the panel with `prepare_prev_first = true`, binds an external backlight, adds the panel, and attaches to DSI. Prepare powers and resets, then executes the DSI init. Disable and unprepare are separate; disable performs DCS sleep-in while unprepare removes power and asserts control GPIOs.

State and persistence: Runtime software state is the DSI device and resources. The code mutates `dsi->mode_flags` in enable/disable paths to add or remove LPM, leaving bus mode dependent on last lifecycle stage. Hardware state includes gamma values, four-lane configuration, sleep/display state, standby GPIO, and reset/power state.

Dependencies and integration points: The driver depends on DRM panel, DRM probe fixed-mode helper, MIPI-DSI multi-context helpers, regulator/GPIO APIs, OF matching, and `drm_panel_of_backlight()`. Compatible string is `lxd,m9189a`.

Risks: `nt->mode_flags` changes are asymmetric: `m9189_on()` ORs LPM, while `m9189_disable()` clears it, which may interact with host assumptions. `m9189_disable()` enters sleep without an explicit display-off. Probe uses manual allocation but still devm-managed memory; cleanup relies on remove. Reset/standby polarity must match the generated vendor sequence. Error path in prepare asserts reset high and disables supply but does not reassert standby.

Test signals: Validate one fixed 1024x600 mode with 154x86 mm size, successful DSI attach and backlight binding, correct standby/reset waveform, gamma writes without accumulated errors, visible output after prepare, sleep entry on disable, and clean power-off on unprepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lxd-m9189a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-magnachip-d53e6ea8966.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-magnachip-d53e6ea8966.c

Purpose: This file implements a hybrid SPI DBI plus DSI video DRM panel driver for Magnachip d53e6ea8966-controller panels, currently Samsung AMS495QA01. SPI/MIPI DBI is used for panel commands and gamma/backlight programming, while a child MIPI-DSI device is registered and attached for pixel transport.

Important APIs, types, and functions: `struct d53e6ea8966_panel_info` describes modes, size, bus flags, init callback, and optional backlight registration. `struct d53e6ea8966` stores device, `mipi_dbi`, `drm_panel`, reset/enable GPIOs, VDD/ELVDD regulators, child DSI device, backlight, and panel info. `ams495qa01_gamma[][]` and `ams495qa01_elvss[]` map 16 brightness levels to gamma/ELVSS values. `ams495qa01_update_gamma()` writes gamma and ELVSS. `ams495qa01_panel_init()` unlocks manufacturer commands and configures analog power/gate/gamma. `d53e6ea8966_prepare()/enable()/disable()/unprepare()` handle regulator/GPIO power and DCS sleep/display commands over DBI. Probe initializes DBI over SPI, locates the DSI host with `drm_of_get_dsi_bus()`, registers a child DSI device, optionally registers a raw backlight, adds the DRM panel, and attaches DSI.

Control flow: Probe starts from the SPI device but creates the DSI endpoint internally. Prepare enables VDD, optional ELVDD, optional enable GPIO, waits, toggles reset, and runs the panel init sequence. Enable exits sleep and turns display on. Backlight updates call the same gamma update path as initialization. Get-modes duplicates all panel-info modes and sets RGB888 bus format. Unprepare disables optional enable, asserts reset, disables ELVDD then VDD, and waits.

State and persistence: Software state spans two buses: SPI DBI control and the registered DSI video child. Gamma brightness is persisted in panel registers but not cached in the driver except through the backlight framework. The panel info table selects two modes for AMS495QA01 and bus flags. Power state is implicit in DRM lifecycle; no booleans guard duplicate calls.

Dependencies and integration points: The driver depends on DRM MIPI DBI, DRM MIPI DSI, SPI, OF graph DSI lookup, regulator/GPIO APIs, backlight framework, and media-bus format constants. It integrates with `samsung,ams495qa01` compatible and SPI ID `ams495qa01`, plus a connected DSI host found from device tree.

Risks: Multi-bus setup is fragile: SPI probe must find and register a DSI child, and cleanup must handle both sides. Optional ELVDD errors are collapsed to NULL even for non-ENODEV failures, which can hide regulator problems. `ams495qa01_update_gamma()` always returns 0 and does not propagate DBI command errors. Backlight changes program gamma tables rather than standard display brightness, so perceived brightness depends on OLED gamma data. Prepare does not unwind ELVDD if later init commands fail because the init callback has no error return.

Test signals: Validate SPI DBI init, DSI host lookup/child registration, DSI attach, both 960x544 modes, RGB888 bus format and bus flags, regulator/GPIO sequencing, display sleep/display-on, and raw backlight updates across all 16 gamma levels. Error testing should include missing DSI host, failed optional/required regulators, and DBI command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-magnachip-d53e6ea8966.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-mantix-mlaf057we51.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-mantix-mlaf057we51.c

Purpose: This driver supports Mantix MLAF057WE51-X and YS YS57PSS36BH5GQ 720x1440 MIPI-DSI panels. It manages three power rails, reset and touch-reset GPIOs, a short vendor initialization sequence, fixed mode selection by compatible, and external backlight binding.

Important APIs, types, and functions: `struct mantix` stores the panel, device, reset GPIO, `mantix,tp-rstn` GPIO, `avdd`, `avee`, `vddi` regulators, and selected default mode. `mantix_init_sequence()` sends vendor generic commands (`OTP_STOP_RELOAD_MIPI`, `INT_CANCEL`, `SPI_FINISH`, VCOM). `mantix_prepare()` enables `vddi`, `avdd`, and `avee` with datasheet delays, then releases touch and panel reset. `mantix_enable()` sends init sequence, exits sleep, and turns display on. `mantix_disable()` turns display off and enters sleep. `mantix_unprepare()` disables rails in reverse-ish order and asserts touch reset and panel reset. `mantix_get_modes()` duplicates the compatible-selected mode and sets RGB888 bus format.

Control flow: OF match data selects between two timing structures. Probe requests GPIOs/regulators/backlight, fixes DSI to four lanes RGB888 video burst sync-pulse LPM, adds the panel, and attaches. Runtime prepare performs only power/reset sequencing; enable performs DSI programming and display-on. Disable and unprepare split DSI sleep from power-down.

State and persistence: The selected mode pointer and resource handles are the only software state. Panel register state is written on each enable. The touch reset GPIO is controlled together with panel reset, implying a board-level dependency between display and touch controller reset state.

Dependencies and integration points: Dependencies include MIPI-DSI multi-context helpers, DRM panel/mode APIs, media bus format, GPIO/regulator/backlight APIs, and OF match data. It exposes compatible strings for both Mantix and YS panels and logs panel readiness after DSI attach.

Risks: Error handling in `mantix_prepare()` does not disable already-enabled regulators if enabling a later rail fails, so failed `avdd`/`avee` paths can leak power. The vendor init sequence is short but undocumented. Touch reset is a non-standard panel GPIO name and may couple unrelated device state to panel lifecycle. The compatible-specific modes are very similar but differ in vertical porch/clock; wrong match data can produce subtle refresh issues.

Test signals: Verify both compatibles select the correct mode, DSI attach succeeds, bus format is RGB888, external backlight binds, power rails are enabled/disabled in expected order, touch and panel reset signals are correct, and enable/disable cycles produce no accumulated DSI errors. Error injection should focus on regulator enable cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-mantix-mlaf057we51.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-motorola-mot.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-motorola-mot.c

Purpose: This is a DRM MIPI-DSI panel driver for a Motorola MOT 540x960 panel. It sequences `vddio`/`vdd` supplies, reset GPIO, a long vendor ES2 initialization sequence with gamma tables, fixed mode reporting, and external backlight binding.

Important APIs, types, and functions: `mot_panel_supplies[]` defines the two rails. `struct mot_panel` stores DRM panel, DSI device, reset GPIO, and regulator bulk array. `mot_panel_reset()` asserts/deasserts reset with long delays. `mot_es2()` writes manufacturer/vendor command sequences, exits sleep early, waits, programs gamma for R/G/B/W, sets display control and tear-on. `mot_panel_prepare()` enables regulators, resets, unlocks command pages, runs `mot_es2()`, and sets display on. `mot_panel_disable()` sends display-off and sleep-in. `mot_panel_unprepare()` asserts reset and disables supplies. `mot_panel_get_modes()` exposes the fixed mode.

Control flow: Probe uses bulk regulators, optional reset GPIO, DSI two-lane RGB888 LPM mode, external backlight, panel add, and devm DSI attach. Prepare performs the full vendor init and display-on. There is no separate `enable` hook; display-on is in prepare. Disable sends sleep commands; unprepare handles reset and power removal.

State and persistence: Software state is resource-only. Hardware state includes command-page unlocks, gamma tables, CABC/display control, tear-on, sleep/display state, and reset/power state. The panel runs over two DSI lanes and starts in LPM; no mode flag mutation is done later.

Dependencies and integration points: The driver depends on DRM fixed-mode helper, MIPI-DSI multi-context helpers, regulator bulk APIs, GPIO, backlight lookup, and OF compatible `motorola,mot-panel`.

Risks: The ES2 sequence exits sleep before most gamma/power commands, so ordering must not be "cleaned up" casually. `mot_panel_prepare()` returns accumulated DSI errors but does not power off on failure after regulators are enabled. The reset GPIO is optional; if absent, the reset helper silently does nothing, which may not work on boards needing reset. Panel identity is broad (`motorola,mot-panel`) with no revision data beyond the ES2 sequence.

Test signals: Confirm fixed 540x960 mode with 51x91 mm size, successful two-lane DSI attach, backlight binding, correct reset timing, no accumulated DSI errors through ES2 init, display-on after prepare, sleep entry on disable, and regulator disable on unprepare. Fault testing should inspect power cleanup after failed DSI writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-motorola-mot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-nec-nl8048hl11.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-nec-nl8048hl11.c

Purpose: This file implements a SPI-controlled DRM DPI panel driver for the NEC NL8048HL11 800x480 panel. It writes a large register initialization sequence over 32-bit SPI words, exposes fixed DPI timing/bus flags, controls reset GPIO for enable/disable, and provides simple suspend/resume reinitialization.

Important APIs, types, and functions: `struct nl8048_panel` stores the DRM panel, SPI device, and reset GPIO. `nl8048_write()` packs `{ value, 0x01, addr, 0x00 }` into a four-byte SPI write. `nl8048_init()` iterates `nl8048_init_seq[]`, waits 20 us, and writes register 2 to 0. `nl8048_enable()` sets reset high; `nl8048_disable()` sets reset low. `nl8048_suspend()` writes register 2 to 1 and waits; `nl8048_resume()` re-runs `spi_setup()`, writes register 2 to 0, and reinitializes. Probe sets SPI mode 0, 32 bits per word, initializes the panel, and registers it.

Control flow: Probe allocates a DPI panel, requests reset low, configures SPI, writes initialization registers, then adds the DRM panel. Enable/disable are reset GPIO toggles. PM suspend/resume act directly on SPI registers. Remove unregisters the panel and calls disable/unprepare.

State and persistence: Panel register state is initialized in probe and resume, not prepare. Reset GPIO represents display enable/reset state. No regulators or backlight are managed. The SPI register state must persist unless the panel loses power or suspend reinitializes it.

Dependencies and integration points: The driver depends on SPI, DRM panel/modes, GPIO, PM helpers, OF and SPI ID matching. It integrates as a DPI connector with display info bus flags for DE high, sync negative-edge sample, and pixel data negative-edge sample.

Risks: Register initialization outside prepare makes runtime power-management assumptions board-specific. Suspend/resume ignores return values from `nl8048_write()` and `nl8048_init()`. The SPI word packing is panel-specific and requires `bits_per_word = 32`; controller support must be verified. No supply handling is present. `drm_panel_unprepare()` is called in remove despite no unprepare hook, which is harmless but not a true power-off.

Test signals: Validate SPI setup at 32 bits, successful register init, fixed 800x480 mode with 89x53 mm size, correct bus edge flags, reset GPIO enable/disable behavior, PM suspend/resume reinitialization, and no SPI write failures in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-nec-nl8048hl11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-newvision-nv3051d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-newvision-nv3051d.c

Purpose: This driver supports NewVision NV3051D-based MIPI-DSI handheld panels for Anbernic/Powkiddy devices. It provides a long vendor DCS initialization sequence, per-compatible mode lists and DSI mode flags, regulator/reset handling, external backlight binding, and shutdown/remove power-down support.

Important APIs, types, and functions: `struct nv3051d_panel_info` stores display modes, physical size, bus flags, and DSI mode flags. `struct panel_nv3051d` stores panel, reset GPIO, panel info, and `vdd` regulator. `panel_nv3051d_init_sequence()` writes multiple command pages for power, gamma, gate mapping, and interface settings. `panel_nv3051d_prepare()` enables `vdd`, toggles reset, runs init, exits sleep, waits 200 ms, and turns display on. `panel_nv3051d_unprepare()` sends display-off, sleep-in, asserts reset, and disables `vdd`. `panel_nv3051d_get_modes()` exposes all modes from the panel info, marking the mode preferred only when there is one mode. Shutdown calls unprepare and disable.

Control flow: Probe selects panel info by compatible, requests optional reset and `vdd`, sets DSI to four lanes RGB888 and info-specific flags, binds backlight, adds the panel, and attaches to DSI. Prepare performs power/reset/init/display-on. Remove first calls the shutdown helper before detaching and removing the panel.

State and persistence: Per-compatible panel info is persistent software state. Hardware state is fully programmed during prepare and lost on power-off. Multiple refresh-rate modes are supported for RG351V/RG353P variants, while RK2023 has one timing. Bus flags advertise DE low and negative-edge pixel drive.

Dependencies and integration points: The driver depends on DRM MIPI-DSI helpers, regulator/GPIO APIs, OF match data, external backlight lookup, and media bus flag definitions. It integrates with compatibles `anbernic,rg351v-panel`, `anbernic,rg353p-panel`, and `powkiddy,rk2023-panel`.

Risks: `panel_nv3051d_init_sequence()` uses `mipi_dsi_multi_context` but always returns 0, so accumulated DSI init errors are not propagated to prepare. The shutdown helper calls unprepare before disable even though no disable hook exists, and unprepare already sends display-off. The long vendor command table is undocumented and revision-sensitive. Error cleanup after init/sleep/display failures disables `vdd` but does not assert reset except in the unprepare path.

Test signals: Validate each compatible selects the correct mode list and DSI flags, all modes are reported with correct physical size and bus flags, DSI attach works, backlight binds, reset/power sequencing is correct, init command failures are visible in logs, and shutdown/remove leave the panel asleep and regulator disabled. Hardware tests should check 60/100/120 Hz modes where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-newvision-nv3051d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-newvision-nv3052c.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-newvision-nv3052c.c

Purpose: This is a SPI/MIPI-DBI DRM DPI panel driver for NewVision NV3052C IPS LCD panels. It supports several 640x480 panels by combining per-compatible register tables with common gamma/GIP/interface initialization, fixed mode lists, bus format/flags, reset/power handling, and external backlight binding.

Important APIs, types, and functions: `struct nv3052c_reg` stores one command/value pair. `struct nv3052c_panel_info` stores modes, physical size, bus format/flags, and panel-specific register table. `struct nv3052c` stores device, DRM panel, `mipi_dbi`, panel info, supply, and reset GPIO. `common_init_regs[]` applies shared gamma, GIP timing, pad mapping, and access-control settings. `ltk035c5444t_panel_regs[]`, `fs035vg158_panel_regs[]`, and `wl_355608_a8_panel_regs[]` customize page-1 analog/interface values. `nv3052c_prepare()` enables power, resets the chip, writes panel-specific then common registers via `mipi_dbi_command()`, and exits sleep. `nv3052c_enable()/disable()` send display-on/off. `nv3052c_get_modes()` exposes all modes and bus information.

Control flow: SPI probe selects panel info, obtains `power` and reset GPIO, initializes DBI over SPI, disables DBI reads, binds backlight, adds the panel, and returns. DRM prepare handles all register programming and sleep-out. Enable waits 120 ms before backlight if a backlight is present. Remove removes the panel and calls disable/unprepare.

State and persistence: The panel info pointer and DBI configuration are persistent software state. Panel registers are reprogrammed on every prepare, so they recover from power loss. `priv->dbi.read_commands = NULL` makes this a write-only DBI control path. No brightness state is held by this driver; backlight is external.

Dependencies and integration points: Dependencies include SPI, DRM MIPI DBI, DRM panel/mode APIs, regulator/GPIO/backlight APIs, media bus formats, OF and SPI ID tables. Compatibles include `leadtek,ltk035c5444t`, `fascontek,fs035vg158`, and `anbernic,rg35xx-plus-panel`.

Risks: The common register table uses C++-style comments in C source, acceptable in kernel C but visually inconsistent. Any panel-specific table mismatch can produce wrong VCOM/gamma/interface behavior while still probing successfully. Prepare exits sleep but does not wait the usual 120 ms until enable/backlight, so panel readiness relies on the later enable path. If a DBI command fails, reset remains deasserted while the regulator is disabled. The SPI ID `rg35xx-plus-panel` maps only through ID name, with OF data required for actual panel info in this probe path.

Test signals: Validate all compatibles report their expected modes and physical sizes, RGB888 bus format, DE/pixel-drive flags, DBI SPI initialization, write-only command mode, successful register programming, display-on/off behavior, 120 ms backlight delay, and proper regulator/reset cleanup on DBI command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-newvision-nv3052c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35510.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35510.c

Purpose: This is a configurable DRM MIPI-DSI driver for panels built around the Novatek NT35510 controller. It models the controller's manufacturer command pages, power/gamma/timing parameters, optional internal brightness/CABC control, and two concrete panel configurations: Hydis HVA40WV1 command-mode and Frida FRD400B25025 video-mode.

Important APIs, types, and functions: `struct nt35510_config` is the central per-panel configuration, containing dimensions, DRM mode, DSI mode flags, command-enable bitmask, analog voltage/boost tables, VCOM, display-output controls, panel timing values, gamma curves, and brightness/CABC defaults. `struct nt35510` stores device, config, DRM panel, two regulators (`vdd`, `vddi`), and optional reset GPIO. `nt35510_send_long()` chunks long DCS writes into 15-byte segments for manufacturer commands. `nt35510_read_id()` reads DCS IDs. `nt35510_setup_power()` writes page-1 power/booster/gamma voltage settings. `nt35510_setup_display()` writes page-0 DOPCTR, MADCTL, source/gate EQ, frame timing, tear-on, and display timing control. `nt35510_power_on()` enables regulators, resets, sends MTP/manufacturer unlocks, reads ID, selects pages, and calls setup helpers. `nt35510_prepare()` exits sleep, optionally writes brightness/CABC control, and turns display on. `nt35510_set_brightness()` writes DCS brightness for the internal backlight path.

Control flow: Probe fixes DSI to two lanes RGB888, sets explicit HS/LP rates, gets per-compatible config, sets DSI mode flags from config, gets and voltage-bounds regulators, requests optional reset GPIO, attaches either external backlight from DT or an internal raw backlight, registers the panel, and attaches DSI. Prepare powers on and configures manufacturer pages, exits sleep, optionally writes control-display/power-save/min-brightness commands, then display-on. Unprepare sends display-off, enters sleep, waits, then disables regulators and asserts reset.

State and persistence: Per-compatible configuration is immutable and drives every setup command. Backlight brightness is held by the backlight framework and written directly to the panel. Hardware state includes manufacturer page selection, voltage/booster settings, gamma tables, frame timing, tear-on, MADCTL rotation, CABC, and sleep/display state. Software does not track current page after setup, so each setup path explicitly selects pages.

Dependencies and integration points: The driver depends on DRM MIPI-DSI, DRM panel, regulator bulk APIs, GPIO, OF match data, and backlight framework. It integrates through compatibles `frida,frd400b25025` and `hydis,hva40wv1`. DSI hosts must tolerate the hard-coded HS/LP rates or future configs need per-panel rates.

Risks: `nt35510_send_long()` splits long payloads into repeated writes with incremented command bytes; this encodes controller-specific addressing and is risky to modify. Power-on returns immediately on setup failures without disabling already-enabled regulators, so some error paths can leak power. Gamma arrays must be monotonically valid 10-bit curves. Command-mode and video-mode configs differ substantially; using the wrong compatible can misprogram timing and brightness controls. Internal backlight creation uses raw DCS brightness and optional CABC bits, which may conflict with external backlight expectations.

Test signals: Validate both compatibles, regulator voltage constraints, DSI attach at configured rates, ID reads, manufacturer page writes, sleep/display transitions, internal or external backlight behavior, fixed mode metadata, and suspend/resume power-off. Error injection should verify cleanup for failed manufacturer writes and long gamma transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35510.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35560.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35560.c

Purpose: This driver supports Novatek NT35560-based Sony ACX424AKP and ACX424AKM AMOLED MIPI-DSI panels. It can run in command mode by default or video mode when the `enforce-video-mode` property is present, manages a single `vddi` regulator and reset GPIO, reads panel IDs, provides an internal PWM-like DCS backlight, and reports mode data based on selected mode type.

Important APIs, types, and functions: `struct nt35560_config` stores video-mode and command-mode display modes. `struct nt35560` stores config, DRM panel, device, supply, reset GPIO, and `video_mode` boolean. `nt35560_set_brightness()` translates backlight brightness to a nonstandard one-byte DCS brightness ratio plus PWMDIV programming through CMD2 unlock/page commands, then enables display backlight control. `nt35560_read_id()` reads ID1/ID2/ID3 and logs Sony-known IDs. `nt35560_power_on()` enables regulator and toggles reset. `nt35560_prepare()` powers on, reads ID, enables tear-on, writes `NT35560_DCS_SET_MDDI` to select DSI, exits sleep, turns display on, and in video mode sends `mipi_dsi_turn_on_peripheral_multi()`. `nt35560_get_modes()` chooses the video or command mode.

Control flow: Probe reads `enforce-video-mode`, selects config, sets two-lane RGB888 DSI with explicit LP/HS rates, chooses video-burst flags or command-mode non-continuous clock, obtains `vddi` and optional reset GPIO, registers the raw backlight, adds the panel, and attaches DSI. Prepare handles the full DSI bring-up. Unprepare sends display-off and sleep-in, waits 85 ms, and powers off.

State and persistence: `video_mode` determines both DSI mode flags and reported timing for the lifetime of the device. Backlight state is managed by the registered backlight and written to panel PWM registers. Hardware state includes selected DSI/MDDI interface, tear-on, sleep/display state, and PWM brightness divisor. No cached prepared flag exists.

Dependencies and integration points: The file depends on DRM MIPI-DSI multi-context helpers, regulator/GPIO APIs, OF properties, and backlight framework. It integrates with `sony,acx424akp` and `sony,acx424akm` compatibles. DSI host support for the hard-coded 420.16 MHz HS and 19.2 MHz LP rates is assumed.

Risks: The brightness conversion uses `max()` with integer arithmetic and subtracts one after scaling, so low brightness behavior is controller-specific and should be checked visually. ID read failures abort prepare through accumulated error. The MDDI command is only described by analogy to other drivers. Video mode requires an explicit peripheral-on command; missing this in future refactors would blank video-mode panels. Probe always registers the internal backlight rather than consulting `drm_panel_of_backlight()`.

Test signals: Validate both Sony compatibles, command and enforced-video mode paths, ID logging, internal backlight brightness and blanking, correct mode dimensions for AKP vs AKM, DSI rates/flags, regulator/reset sequencing, display-on in video mode including peripheral-on, and unprepare power-off after sleep-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35560.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35950.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35950.c

Purpose: This driver supports Novatek NT35950 DriverIC panels, currently the dual-DSI Sharp LS055D1SX04. It manages dual DSI registration/attach, four regulators, reset sequencing, mode-dependent scaling/compression/output-control programming, and fixed-mode reporting for a 1080x1920 mode with scaler/SRAM settings.

Important APIs, types, and functions: `struct nt35950` stores the DRM panel, connector pointer, up to two DSI devices, four regulators, reset GPIO, descriptor, current mode index, and last selected manufacturer page. `struct nt35950_panel_mode` pairs a DRM mode with flags for SRAM, video mode, scaler, compression, and SPR. `struct nt35950_panel_desc` describes model name, secondary DSI info, mode table, dual-DSI flag, lane count, and mode count. Helpers include `nt35950_set_cmd2_page()`, `nt35950_set_data_compression()`, `nt35950_set_scaler()`, `nt35950_set_scale_mode()`, `nt35950_inject_black_image()`, and `nt35950_set_dispout()`. `nt35950_get_current_mode()` matches the active CRTC mode against descriptor modes. `nt35950_on()` programs page 0 compression/scaler/output, tear-on, page 1/7 vendor settings, black image injection, sleep-out/display-on, and exits LPM. `nt35950_prepare()` sequences regulators and reset, then calls `nt35950_on()`.

Control flow: Probe initializes regulator descriptors and voltage-support checks, gets the panel descriptor and reset GPIO, optionally discovers/registers a secondary DSI host from graph port 1, binds backlight, adds the panel, configures/attaches every DSI link, and holds reset low before power-on. Prepare enables `vddio`, `dvdd`, `avdd`, and `avee` with required delays, resets, and programs the panel. Get-modes stores the connector pointer so prepare can discover the selected mode later. Unprepare sends display-off/sleep-in, asserts reset low, and disables all regulators. Remove detaches both DSIs and unregisters the secondary one.

State and persistence: `last_page` tracks manufacturer CMD2 page only for command programming during a power session. `cur_mode` is selected at prepare based on connector CRTC state, defaulting to 0 when unavailable. `nt->connector` is cached from `get_modes()`, coupling mode selection to normal connector enumeration. Hardware state includes scaler, compression, SRAM/video-mode output bits, SPR, tear scanline, and sleep/display state. The secondary DSI child is persistent until remove.

Dependencies and integration points: The driver depends on DRM panel/connector/mode APIs, OF graph lookup, MIPI-DSI host/device registration, regulator bulk APIs, GPIO, and backlight lookup. It integrates with dual-DSI topologies through `of_graph_get_remote_node()` and `mipi_dsi_device_register_full()`. Compatible is `sharp,ls055d1sx04`.

Risks: `nt35950_on()` unconditionally accesses `nt->dsi[1]->mode_flags`; the current descriptor is dual-DSI, but adding a single-DSI descriptor would crash unless guarded. Regulator error paths in `nt35950_prepare()` jump to one bulk-disable label but may call `regulator_bulk_disable()` on regulators that were not all enabled. Secondary DSI attach failure after DSI0 attach unregisters DSI1 but does not detach DSI0 in that path. Mode selection depends on cached connector/CRTC state and can fall back silently to mode 0. DSC support is noted as TODO for the native 2160x3840 mode.

Test signals: Validate dual-DSI graph discovery, both DSI attaches/detaches, regulator voltage support checks, reset waveform, fixed 1080x1920 mode, backlight binding, current-mode matching, scaler/SRAM/compression programming, black-image injection before sleep-out, and clean unprepare. Future tests for single-DSI descriptors should add guards around `dsi[1]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt35950.c -->
