# subset-b-003702 research

Grouped research for DRM panel drivers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8aa5x01-ams561ra01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8aa5x01-ams561ra01.c

## Purpose
Implements a MIPI DSI DRM panel driver for the Samsung AMS561RA01 panel using the S6E8AA5X01 controller. The file provides panel power sequencing, DSI command initialization, a fixed 720x1480 video mode, and a custom backlight implementation based on precomputed gamma and AID command tables rather than the normal DCS brightness register.

## Important APIs, types, and functions
- `struct s6e8aa5x01_ams561ra01_ctx` owns the `drm_panel`, DSI device, backlight device, reset GPIO, and two regulators.
- `s6e8aa5x01_ams561ra01_cmds[]` maps each software brightness index to a 34-byte gamma command and 3-byte AID command.
- `s6e8aa5x01_ams561ra01_update_status()` unlocks manufacturer command access, writes the selected gamma/AID pair, triggers gamma update, and locks access again.
- Panel operations are `prepare`, `unprepare`, `enable`, `disable`, and `get_modes` through `s6e8aa5x01_ams561ra01_panel_funcs`.
- Probe uses `devm_drm_panel_alloc()`, `devm_regulator_bulk_get_const()`, optional reset GPIO lookup, `devm_backlight_device_register()`, `drm_panel_add()`, and `devm_mipi_dsi_attach()`.

## Control flow
Probe allocates the context, binds it to the DSI device, gets `vdd` and `vci`, registers a platform backlight with max brightness equal to the command-table length minus one, configures four RGB888 video-mode lanes with burst and no-HFP flags, marks `prepare_prev_first`, adds the panel, and attaches to the DSI host. Prepare enables both supplies and toggles reset low, high, low with millisecond delays. Enable exits sleep, unlocks level-two manufacturer commands, writes panel-specific setup commands for pentile, PCD, error flags, display control, and LTPS control, locks commands again, then turns display on. Backlight updates are ignored while the DRM panel is not enabled. Disable turns the display off, waits, enters sleep, and waits again. Unprepare asserts reset and disables the regulators.

## State and persistence
Driver state is entirely device-managed except for hardware state in the panel controller. The software brightness property persists in the Linux backlight device; the actual gamma/AID setting persists in the panel until another brightness update, panel sleep, reset, or power removal. Regulator and GPIO states track the DRM prepare/unprepare lifecycle. The fixed display mode and DSI mode flags are static per compatible.

## Dependencies and integration points
The driver depends on DRM panel helpers, MIPI DSI multi-context helpers, the Linux backlight framework, regulator bulk APIs, GPIO descriptors, and device tree compatible `samsung,s6e8aa5x01-ams561ra01`. It integrates as a `mipi_dsi_driver` and exposes a DSI connector with one fixed mode through `drm_connector_helper_get_modes_fixed()`.

## Risks
The backlight index directly indexes `s6e8aa5x01_ams561ra01_cmds[]`; correctness depends on the backlight core clamping to `max_brightness`. The large gamma/AID table is calibration-sensitive and not self-validating. Error handling in enable and backlight update uses `mipi_dsi_multi_context` accumulated errors, so command failures are reported only after a batch. Reset polarity and timing are panel-specific, and wrong device tree GPIO flags or regulator names can leave the panel held in reset or partially powered.

## Test signals
Useful checks are successful probe and DSI attach, no regulator or reset GPIO probe errors, a single 720x1480 preferred mode, visible sleep-exit/display-on behavior, brightness stepping across all table indices, no out-of-range brightness writes, and clean suspend/resume or remove paths with reset asserted and regulators disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8aa5x01-ams561ra01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8fc0-m1906f9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8fc0-m1906f9.c

## Purpose
Implements a Samsung S6E8FC0 MIPI DSI panel variant used by the M1906F9 device family. It provides reset and regulator sequencing, a vendor command initialization sequence, fixed 720x1560 mode reporting, and a raw 10-bit DCS backlight.

## Important APIs, types, and functions
- `struct s6e8fc0_ctx` stores the DRM panel, DSI device, reset GPIO, and `vdd`/`vci` regulators.
- `s6e8fc0_m1906f9_reset()` toggles reset with panel-specific delays.
- Test-key macros write `0xf0` and `0xfc` unlock/lock values for level 2 and level 3 command pages.
- `s6e8fc0_m1906f9_on()` sends the initialization sequence, exits sleep, enables display, and programs vendor registers.
- `s6e8fc0_bl_update_status()` and `s6e8fc0_bl_get_brightness()` use large DCS brightness set/get helpers with low-power mode temporarily disabled.
- `s6e8fc0_m1906f9_probe()` allocates the panel, creates the backlight, configures DSI lanes/format/flags, adds the panel, and attaches to the host.

## Control flow
Probe resolves supplies and reset GPIO, sets four RGB888 DSI lanes in video burst mode with non-continuous clock, enables `prepare_prev_first`, creates the backlight, registers the panel, and attaches. Prepare enables supplies, resets the panel, then calls the on sequence. The on sequence opens a vendor command page, initializes brightness/control display state, exits sleep, waits 50 ms, turns display on, writes several vendor register blocks, and closes the command pages. Unprepare calls the off sequence, reports but suppresses off errors, asserts reset, and disables regulators. Backlight update/get clear `MIPI_DSI_MODE_LPM`, perform high-speed DCS brightness access, then restore LPM.

## State and persistence
Persistent software state is minimal and device-managed. Brightness is held by the backlight core and by the panel's DCS brightness register after writes. Panel register programming persists until reset, sleep/power loss, or another command sequence. The DSI mode flags are mutated around brightness transfers, so callers depend on single-threaded panel/backlight access through the DRM and backlight frameworks.

## Dependencies and integration points
The driver depends on DRM panel, MIPI DSI, regulator, GPIO, and backlight APIs. It binds through OF compatible `samsung,s6e8fc0-m1906f9` and integrates with a DSI host as a `mipi_dsi_driver`. Fixed mode publication uses `drm_connector_helper_get_modes_fixed()`.

## Risks
The generated vendor sequence has little semantic validation; any byte drift can break panel bring-up. The code toggles `dsi->mode_flags` in backlight paths without explicit locking in this file, relying on subsystem serialization. Unprepare always returns success even if the off command fails, which can hide shutdown issues. Probe uses non-devm `mipi_dsi_attach()` and manually detaches in remove, so attach/remove order remains important.

## Test signals
Expected signals include successful regulator/reset acquisition, DSI attach, one 720x1560 preferred mode, successful sleep exit/display-on, functional 0..1023 brightness set/get, no persistent loss of LPM flag after brightness I/O, and clean detach/remove logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8fc0-m1906f9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-sofef00.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-sofef00.c

## Purpose
Provides a DRM MIPI DSI panel driver for Samsung SOFEF00 DDIC panels, including the AMS628NW01 compatible. It handles three power rails, reset sequencing, a small vendor setup sequence, a fixed 1080x2280 mode, display enable/disable operations, and DCS large-brightness backlight control.

## Important APIs, types, and functions
- `struct sofef00_panel` contains the DRM panel, DSI device, regulator bulk pointer, and reset GPIO.
- `sofef00_supplies[]` defines required `vddio`, `vci`, and `poc` regulators.
- `sofef00_panel_on()` exits sleep, enables TE, writes vendor register `0xb6`, enables display control and disables power save.
- `sofef00_enable()`, `sofef00_disable()`, `sofef00_panel_prepare()`, and `sofef00_panel_unprepare()` implement the DRM lifecycle.
- `sofef00_panel_bl_update_status()` writes 16-bit brightness with `mipi_dsi_dcs_set_display_brightness_large()`.
- `sofef00_panel_probe()` creates the panel/backlight, configures the DSI endpoint, and attaches it to the host.

## Control flow
Probe obtains regulators and reset GPIO, configures four RGB888 DSI lanes with burst, non-continuous clock, and LPM, creates a platform backlight with range 0..1023, registers the panel, and attaches. Prepare enables all supplies, performs the reset pulse sequence, and executes panel-on setup. Enable only sends DCS display on. Disable sends display off and sleep-in through `sofef00_panel_off()`. Unprepare disables the regulator bulk without an extra reset toggle.

## State and persistence
Panel state lives in the hardware command registers and in DRM panel prepared/enabled flags. Backlight brightness persists in the DCS brightness register while the panel remains powered. Regulator and reset state is not otherwise cached. The driver mutates `dsi->mode_flags` for backlight writes by clearing and restoring LPM, and `sofef00_panel_on()` leaves LPM set for initialization.

## Dependencies and integration points
The driver uses DRM panel helpers, MIPI DSI multi-context helpers, regulator bulk APIs, GPIO descriptors, backlight registration, and OF matching for `samsung,sofef00` and `samsung,sofef00-ams628nw01`. It is a `mipi_dsi_driver` consumed by DSI host drivers and bridge/display pipelines.

## Risks
The legacy compatible aliases the same panel behavior, so board files using it must really match the AMS628NW01-style timings and commands. `sofef00_disable()` ignores the return from `sofef00_panel_off()`, hiding DSI command errors. Power-down does not assert reset, which may be intentional but leaves panel state dependent on regulator behavior. Brightness updates assume the panel accepts high-speed DCS writes after temporary LPM clearing.

## Test signals
Validation should check regulator order and reset pulse timing, DSI attach success, one 1080x2280 preferred mode, TE/display-control setup, display on/off transitions, brightness writes across 0..1023, suspend/resume behavior, and absence of detach errors on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-sofef00.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-seiko-43wvf1g.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-seiko-43wvf1g.c

## Purpose
Implements a platform DRM panel driver for the Seiko 43WVF1G parallel/DPI panel. It is a descriptor-driven fixed-timing driver with two regulators, an optional enable GPIO, optional backlight lookup, and mode/timing publication for a single 800x480 panel.

## Important APIs, types, and functions
- `struct seiko_panel_desc` describes modes, display timings, bpc, physical size, bus format, and bus flags.
- `struct seiko_panel` stores the DRM panel, descriptor, `dvdd` and `avdd` regulators, and enable GPIO.
- `seiko_panel_get_fixed_modes()` duplicates `display_timing` or `drm_display_mode` entries and fills connector display info.
- `seiko_panel_prepare()` enables `dvdd`, waits 100 ms, enables `avdd`, and asserts enable GPIO.
- `seiko_panel_unprepare()` deasserts enable, disables `avdd`, waits 100 ms, and disables `dvdd`.
- `seiko_panel_get_timings()` returns the descriptor timing array for consumers that query panel timings directly.

## Control flow
The platform probe matches the OF compatible `sii,43wvf1g`, passes its descriptor to `seiko_panel_probe()`, allocates the DRM panel as a DPI connector, gets the two regulators and optional enable GPIO, resolves any OF backlight, adds the panel, and stores drvdata. Runtime prepare and unprepare implement the required power order from the datasheet. Mode enumeration converts the descriptor's `display_timing` to a DRM mode, marks the sole mode preferred, and publishes bpc, dimensions, bus format, and bus flags.

## State and persistence
There is no panel register state because this is a simple DPI panel. Software state is descriptor pointer plus regulator/GPIO handles. The only persistent hardware state is whether rails are enabled and whether the enable GPIO is asserted. Backlight state is delegated to a separate backlight device when present in device tree.

## Dependencies and integration points
The file depends on DRM panel APIs, videomode/display timing conversion, regulator and GPIO frameworks, media bus format definitions, and OF platform matching. It integrates with DPI display controllers that consume `drm_panel` modes, bus format, and bus flags.

## Risks
The descriptor has a single timing and assumes fixed 8 bpc RGB888 with DE high and pixel data driven on the negative edge. If board wiring or sampling edge differs, the panel may show unstable output. Error handling on `avdd` enable disables `dvdd`, but later runtime calls assume the DRM lifecycle remains serialized. Optional backlight lookup can fail probe if the referenced backlight is not ready.

## Test signals
Look for successful `dvdd`/`avdd` acquisition, one 800x480 preferred mode, correct connector width/height, media bus format `RGB888_1X24`, expected bus flags, visible power sequencing delays, and correct blank/unblank behavior through prepare/unprepare and backlight integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-seiko-43wvf1g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq079l1sx01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq079l1sx01.c

## Purpose
Implements a dual-link MIPI DSI DRM panel driver for the Sharp LQ079L1SX01 panel. It drives both left and right DSI hosts, powers four regulators, performs a simple DCS bring-up sequence on both links, and exposes a fixed 1536x2048 mode.

## Important APIs, types, and functions
- `struct sharp_panel` stores the DRM panel, two DSI devices, reset GPIO, regulator bulk pointer, and display mode pointer.
- `sharp_supplies[]` names the `avdd`, `vddio`, `vsp`, and `vsn` supplies.
- `mipi_dsi_dual_dcs_write_seq_multi()` is used to send the same DCS command to both DSI links.
- `sharp_panel_probe()` discovers the secondary DSI host via OF graph port 1 and registers a second DSI peripheral with name `sharp-link1`.
- `sharp_panel_prepare()` powers supplies, resets the panel, exits sleep on both links, sets brightness/power/control display registers, and turns display on.
- `sharp_panel_unprepare()` sends display-off and sleep-in to both links, asserts reset, and disables regulators.

## Control flow
Probe allocates the panel on the primary DSI device, gets all supplies and optional reset GPIO, locates the second DSI host through the graph, registers the secondary MIPI DSI device, resolves an OF backlight, adds the panel, configures both links as four-lane RGB888 video/LPM endpoints, and attaches each link with devm attach. Prepare enables regulators, waits 24 ms, toggles reset if present, waits 32 ms, then sends sleep-out, brightness, power save, control display, and display-on commands to both DSI devices. Unprepare sends display-off/sleep-in to both, waits, asserts reset, and disables all supplies.

## State and persistence
The driver tracks two DSI endpoints and shared power/reset state. Panel command state is mirrored to both links. Brightness is initialized to `0xff` in prepare, while ongoing backlight control is delegated to an external OF backlight instead of custom callbacks. Device-managed DSI attach and secondary device registration own most resource lifetime.

## Dependencies and integration points
It depends on DRM panel helpers, MIPI DSI dual-write helpers, OF graph discovery, regulator bulk APIs, GPIO, backlight lookup, and compatible `sharp,lq079l1sx01`. Integration requires a board device tree with two DSI hosts wired as expected.

## Risks
The secondary DSI host is mandatory; probe defers or fails without graph port 1. The prepare function does not return `dsi_ctx.accum_err`, so DSI command failures during bring-up are not propagated. Both links use identical mode flags, which must match host capabilities. Reset GPIO is optional, but actual hardware may require it for reliable startup.

## Test signals
Test by checking both DSI links attach, one 1536x2048 preferred mode appears, regulators enable/disable as a group, both panel halves wake and sleep together, the OF backlight controls brightness after initial setup, and no secondary-host probe deferral remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq079l1sx01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq101r1sx01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq101r1sx01.c

## Purpose
Implements the Sharp LQ101R1SX01 dual-link MIPI DSI panel. It registers a DRM panel only for the primary DSI link, uses the second link for split output, programs panel registers through generic DSI writes, and exposes a 2560x1600 mode.

## Important APIs, types, and functions
- `struct sharp_panel` stores primary and secondary DSI devices, regulator supply, and active mode.
- `sharp_panel_write()` sends a 16-bit register offset plus value over generic DSI to link1, followed by a DCS NOP and a short delay.
- `sharp_panel_read()` is a debug/helper read path marked `__maybe_unused`.
- `sharp_setup_symmetrical_split()` sets DCS column/page windows so left and right links cover half the horizontal resolution.
- `sharp_panel_prepare()` powers the panel, exits sleep, programs left-right split mode and command mode, sets RGB888 pixel format, configures the split, turns display on, and waits six frames.
- `sharp_panel_probe()` attaches both DSI endpoints but only creates the panel object when probing the DSI-LINK1 endpoint that references `link2`.

## Control flow
Each DSI endpoint probes with four RGB888 lanes and LPM. The primary link locates the secondary DSI peripheral through the `link2` phandle. When found, the driver allocates and registers a panel, obtains the `power` regulator and optional OF backlight, stores both links, and attaches the primary. The secondary probe may simply attach without a panel if it has no `link2`. Prepare enables power, waits for panel readiness, exits sleep on link1, enables left-right and command modes through vendor registers, sets pixel format, programs link1 and link2 address windows, turns display on, and waits frame-derived time. Unprepare waits four frames, sends display-off and sleep-in on link1, waits 120 ms, and disables power.

## State and persistence
State includes the secondary DSI device reference obtained with `of_find_mipi_dsi_device_by_node()`, released in `sharp_panel_del()`. Hardware state includes split mode, command mode, DCS address windows, pixel format, and display/sleep state. The panel mode pointer is static. Backlight state is external through `drm_panel_of_backlight()`.

## Dependencies and integration points
The driver depends on DRM panel APIs, MIPI DSI DCS/generic helpers, OF phandle lookup, regulators, and optional backlight. It binds `sharp,lq101r1sx01` and integrates with host drivers that expose two coordinated DSI peripherals.

## Risks
Only left-right split is supported; even-odd split would need host/panel coordination not present here. `sharp_wait_frames()` uses integer frame math and warns if asked for more frames than refresh. Register writes go only over link1, so hardware must propagate global settings appropriately. If probe order makes `link2` unavailable, the primary returns `-EPROBE_DEFER`.

## Test signals
Important signals are successful primary/secondary probe ordering, no leaked secondary device reference on failure/remove, correct 2560x1600 mode, both panel halves displaying their expected columns, clean power-on/off timing, and stable external backlight behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-lq101r1sx01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls037v7dw01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls037v7dw01.c

## Purpose
Provides a platform DRM panel driver for the Sharp LS037V7DW01 DPI LCD. It controls a single regulator plus several GPIOs for reset, enable, mode, and scan direction, and exposes a fixed 480x640 mode with bus flags.

## Important APIs, types, and functions
- `struct ls037v7dw01_panel` stores the DRM panel, platform device, `envdd` regulator, and GPIOs `enable`, `reset`, and indexed `mode` lines.
- `ls037v7dw01_prepare()` enables the power regulator.
- `ls037v7dw01_enable()` waits for a couple of vsyncs, deasserts reset, and asserts the enable/INI GPIO.
- `ls037v7dw01_disable()` deasserts enable and reset, then waits at least five vsyncs.
- `ls037v7dw01_get_modes()` duplicates the fixed mode and fills width, height, and bus flags.
- `ls037v7dw01_remove()` removes the panel and explicitly disables/unprepares it.

## Control flow
Probe allocates the DPI panel, stores platform drvdata, gets the `envdd` regulator, requires enable and reset GPIOs, and requires three `mode` GPIOs. These mode GPIOs are requested low, selecting 480x640 and conventional scanning according to the comments. It then adds the panel. Prepare enables power. Enable waits 50 ms, releases reset, and turns the panel on through `ini_gpio`. Disable turns off `ini_gpio`, asserts reset, and waits 100 ms. Unprepare disables power.

## State and persistence
The driver has no command interface and no register state. The persistent state is the physical level of regulator and GPIO lines. Mode GPIOs are initialized during probe and otherwise left unchanged, so they define panel orientation/resolution for the lifetime of the device. The DRM panel core tracks prepared/enabled state around these callbacks.

## Dependencies and integration points
It depends on platform device probing, DRM panel and connector helpers, regulators, GPIO descriptors, and compatible `sharp,ls037v7dw01`. It integrates with DPI display controllers through the fixed mode and bus flags.

## Risks
The bus flag comment notes uncertainty: the datasheet says rising-edge sampling, but legacy code suggests negative-edge pixel sampling. Mode GPIO defaults are hard-coded to low and may not match all board wiring. Remove calls `drm_panel_remove()` before disable/unprepare, which is a historical pattern but makes lifecycle assumptions about active users. Missing any required GPIO fails probe.

## Test signals
Test signals include successful acquisition of `envdd`, `enable`, `reset`, and three `mode` GPIOs, one 480x640 preferred mode, correct DE/sync/pixel bus behavior on real hardware, visible reset/enable sequencing, and no warnings or regulator imbalance during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls037v7dw01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls043t1le01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls043t1le01.c

## Purpose
Implements a Sharp LS043T1LE01 qHD panel using a Novatek NT35565-style MIPI DSI controller. The driver manages one `avdd` regulator, reset GPIO, panel init/on/off DCS commands, fixed 540x960 mode reporting, and optional OF backlight integration.

## Important APIs, types, and functions
- `struct sharp_nt_panel` stores the DRM panel, DSI device, regulator, and reset GPIO.
- `sharp_nt_panel_init()` exits sleep, waits 120 ms, selects Novatek two-lane operation, and sets both MCU and RGB interfaces to 24 bpp.
- `sharp_nt_panel_on()` sends DCS display on in LPM.
- `sharp_nt_panel_off()` clears LPM and sends display off plus enter sleep.
- `sharp_nt_panel_prepare()` enables power, toggles reset, initializes the panel, and turns it on.
- `sharp_nt_panel_probe()` configures two-lane RGB888 video mode with sync pulse, HSE, non-continuous clock, and no EOT packet.

## Control flow
Probe allocates the context with `devm_kzalloc()`, sets DSI drvdata, records the DSI device, adds the DRM panel through `sharp_nt_panel_add()`, then attaches to the DSI host. Add obtains the `avdd` regulator, gets reset GPIO, initializes the DRM panel manually with `drm_panel_init()`, sets `prepare_prev_first`, resolves backlight, and adds the panel. Prepare enables the regulator, waits, performs a high-low-high reset pulse, runs init, then display-on. Unprepare sends off/sleep commands, disables the regulator, and drives reset low if present.

## State and persistence
State is limited to the DSI device, regulator, reset line, and DRM panel flags. Panel controller state includes two-lane mode, pixel format, sleep/display state, and any backlight state managed externally. The DSI mode flags are modified in init/on/off to choose LPM or high-speed command behavior.

## Dependencies and integration points
The file uses DRM panel, MIPI DSI helpers, regulator and GPIO frameworks, OF matching for `sharp,ls043t1le01-qhd`, and optional backlight lookup. It integrates as a normal `mipi_dsi_driver`.

## Risks
The reset GPIO is requested as mandatory but errors are converted into a NULL reset GPIO after logging, which may allow probe on hardware that will not reliably reset. Off commands return errors and abort unprepare before regulator disable, so a DSI failure can leave power on. The mode has no explicit physical mode type flags in the static struct; get_modes duplicates and publishes it without marking preferred.

## Test signals
Useful tests include DSI attach, correct two-lane host configuration, reset waveform, successful sleep-out and display-on, one 540x960 mode with 54x95 mm dimensions, backlight lookup behavior, and regulator disable on unprepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls043t1le01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls060t1sx01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls060t1sx01.c

## Purpose
Implements a Sharp LS060T1SX01 1080p MIPI DSI video-mode panel. It manages four named regulators with strict sequencing, reset GPIO, a short panel-on/off DCS sequence, fixed 1080x1920 mode reporting, and external backlight integration.

## Important APIs, types, and functions
- `struct sharp_ls060` stores DRM panel, DSI device, `vddi`, `vddh`, `avdd`, `avee` regulators, and reset GPIO.
- `sharp_ls060_reset()` performs a low-high-low reset pulse with 10 ms gaps.
- `sharp_ls060_on()` enables LPM, writes a vendor register `0xbb`, starts memory write, exits sleep, waits, turns display on, and waits again.
- `sharp_ls060_off()` clears LPM, sends display off, waits a few milliseconds, enters sleep, and waits 121 ms.
- `sharp_ls060_prepare()` enables regulators in order with delays and unwinds them on errors.
- `sharp_ls060_probe()` configures four-lane RGB888 DSI video burst with no EOT and non-continuous clock.

## Control flow
Probe allocates the panel, gets all four regulators and reset GPIO, sets DSI drvdata and link parameters, resolves an OF backlight, adds the panel, and attaches to the DSI host. Prepare enables `vddi`, then `avdd`, delays, enables `avee`, delays, enables `vddh`, delays, resets the panel, then sends the on sequence. If any later stage fails, it disables already-enabled rails in reverse-ish order and asserts reset. Unprepare sends off/sleep commands, disables `vddh`, waits, disables `avee` and `avdd`, asserts reset, then disables `vddi`.

## State and persistence
Persistent state is mostly physical: regulator enable state, reset GPIO level, DSI controller mode flags, and panel sleep/display state. Brightness is external through `drm_panel_of_backlight()`. The fixed mode and dimensions are static.

## Dependencies and integration points
The driver depends on DRM panel APIs, MIPI DSI, regulator framework, GPIO, OF backlight, and compatible `sharp,ls060t1sx01`. It integrates into DSI host pipelines as a video-mode DSI panel.

## Risks
Power sequencing is rail-order sensitive; incorrect device tree supplies or delays can damage bring-up reliability. `sharp_ls060_off()` has no return value and ignores accumulated DSI errors, so unprepare always continues. The on sequence writes `MIPI_DCS_WRITE_MEMORY_START` before sleep-out, which is panel-specific and should not be generalized. Reset polarity must match the GPIO descriptor.

## Test signals
Check successful rail acquisition, ordered rail transitions with delays, reset pulse timing, DSI attach, one preferred 1080x1920 mode with 75x132 mm dimensions, visible sleep-out/display-on, working external backlight, and clean regulator unwind on forced command or attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sharp-ls060t1sx01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-simple.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-simple.c

## Purpose
Provides the generic DRM "simple panel" driver for panels that need only a power rail, optional enable GPIO, optional backlight, optional DDC, and static mode/timing metadata. Most of the file is a large descriptor registry mapping OF compatibles to `panel_desc` or `panel_desc_dsi` data for DPI, LVDS, and a small set of DSI panels.

## Important APIs, types, and functions
- `struct panel_desc` describes fixed `drm_display_mode` entries or bounded `display_timing` entries, bpc, physical size, delays, media bus format, bus flags, and connector type.
- `struct panel_desc_dsi` wraps `panel_desc` with DSI mode flags, pixel format, and lane count.
- `struct panel_simple` stores the DRM panel, descriptor, power regulator, optional DDC adapter, enable GPIO, cached EDID, override mode, orientation, and last unprepare timestamp.
- Mode helpers include `panel_simple_get_timings_modes()`, `panel_simple_get_display_modes()`, `panel_simple_get_non_edid_modes()`, `panel_simple_get_modes()`, and `panel_simple_get_timings()`.
- Power helpers include `panel_simple_suspend()`, `panel_simple_resume()`, `panel_simple_prepare()`, `panel_simple_unprepare()`, `panel_simple_enable()`, and `panel_simple_disable()`.
- Probe helpers include `panel_dpi_probe()`, `panel_simple_parse_panel_timing_node()`, `panel_simple_override_nondefault_lvds_datamapping()`, `panel_simple_get_desc()`, and `panel_simple_probe()`.
- Registration is split between `panel_simple_platform_driver` and, when enabled, `panel_simple_dsi_driver`, both installed from `panel_simple_init()`.

## Control flow
For platform devices, OF match data normally supplies a descriptor; the special `panel-dpi` compatible builds one from the `panel-timing` node. For DSI devices, match data supplies a `panel_desc_dsi`, and the DSI probe later copies flags/format/lanes to the MIPI DSI device before attach. Common probe validates connector type and bus fields, allocates the DRM panel, gets the `power` regulator and optional `enable` GPIO, reads panel orientation, optionally resolves `ddc-i2c-bus`, accepts a DT timing override only when it fits descriptor timing bounds, optionally overrides LVDS data mapping, enables runtime PM with autosuspend, resolves backlight, and adds the panel.

Prepare and unprepare are runtime-PM wrappers. Runtime resume waits for any required minimum unprepare interval, enables the regulator, asserts the enable GPIO, and waits the descriptor prepare delay. Runtime suspend deasserts enable, disables power, records `unprepared_time`, and frees cached EDID. Enable/disable only wait descriptor delays for valid frame appearance/disappearance. Mode enumeration reads EDID through DDC while temporarily runtime-resuming the panel, then adds static or override modes and applies display info and orientation.

## State and persistence
Persistent software state includes descriptor pointer, optional cached EDID, override mode from DT, orientation, and `unprepared_time` used to enforce power-off minimums across prepare cycles. Hardware state is limited to the power regulator and enable GPIO because this driver intentionally avoids panel-specific command sequences. The descriptor tables are compile-time static and encode the supported panel database.

## Dependencies and integration points
The driver depends on DRM panel, EDID, OF, MIPI DSI, runtime PM, regulators, GPIO, I2C/DDC, videomode/display timing, LVDS data-mapping helpers, and media bus format definitions. It integrates with many board device trees via the large platform `of_device_id` table, with DSI panels through `dsi_of_match`, and with display controllers through `drm_panel` mode, timing, bus format, bus flag, backlight, orientation, and connector-type APIs.

## Risks
Descriptor correctness is the main risk: wrong timing, bus flags, bus format, bpc, connector type, or delays can cause blank panels or subtle signal integrity problems. The common driver warns for likely LVDS/DPI/DSI descriptor mistakes but still falls back in some cases for compatibility. EDID reads require powering the panel briefly and rely on runtime PM balance. Shutdown contains explicit disable/unprepare calls as compatibility glue for older modeset drivers and warns not to copy that pattern. DSI error cleanup in `panel_simple_dsi_probe()` removes the panel but relies on common remove paths for other resources.

## Test signals
Test signals include successful probe for representative platform, `panel-dpi`, LVDS with `data-mapping`, DDC/EDID, and DSI descriptors; correct runtime PM prepare/unprepare balance; expected modes from EDID plus static descriptors; accepted and rejected DT timing overrides; correct orientation reporting; backlight discovery; and clean module init/exit registration of both platform and DSI drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-simple.c -->
