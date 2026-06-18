# subset-b-003703 Research

This grouped report covers Linux DRM panel drivers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/`. Each section is source-tree aligned for deterministic split into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7701.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7701.c

## Purpose
This driver supports panels based on the Sitronix ST7701 controller, with both MIPI DSI and SPI/DBI transport variants. It presents the panel through `drm_panel`, advertises fixed modes for specific compatible strings, programs ST7701 command-bank registers, and sequences regulators, reset GPIO, display on/off, and sleep state.

## Important APIs, Types, And Functions
The main data model is `struct st7701`, which owns `struct drm_panel`, optional `mipi_dsi_device`, `mipi_dbi`, two supplies (`VCC`, `IOVCC`), reset GPIO, orientation, and a transport-specific `write_command` callback. `struct st7701_panel_desc` holds the fixed mode, DSI lane/format data, panel sleep delay, gamma and power tuning fields, and an optional `gip_sequence`.

Key helpers are `st7701_dsi_write()`, `st7701_dbi_write()`, `st7701_switch_cmd_bkx()`, `st7701_vgls_map()`, and `st7701_init_sequence()`. Panel operations are `st7701_prepare()`, `st7701_enable()`, `st7701_disable()`, `st7701_unprepare()`, `st7701_get_modes()`, and `st7701_get_orientation()`. Probe is shared through `st7701_probe()`, then specialized by `st7701_dsi_probe()` and `st7701_spi_probe()`.

## Control Flow
Probe allocates a managed panel, fetches descriptor data from OF match data, gets regulators and reset GPIO, reads panel orientation, derives sleep delay as 120 ms plus descriptor extra delay, wires OF backlight support, adds the panel, and registers a managed cleanup action. DSI probe selects DSI connector type, validates that the descriptor has lanes, sets video burst/LPM/non-continuous mode flags, and attaches to the DSI host. SPI probe selects DPI connector type, initializes `mipi_dbi` from SPI plus optional D/C GPIO, and disables DBI reads.

Prepare enables supplies, toggles reset, runs the generic ST7701 initialization sequence, applies optional GIP commands, and returns to command set 1. Enable and disable send `MIPI_DCS_SET_DISPLAY_ON/OFF`. Unprepare sends sleep-in, waits for the panel-specific sleep delay, asserts reset, waits again, and disables regulators.

## State And Persistence
Runtime state is in `struct st7701`; descriptor constants are immutable per compatible string. There is no persistent storage. The only retained dynamic state is transport selection, `sleep_delay`, orientation, and panel lifecycle state tracked by DRM. `prepare_prev_first` is set so bridge/pipeline ordering prepares the panel before previous components where required.

## Dependencies And Integration Points
The driver integrates with DRM panel core, MIPI DSI, MIPI DBI/SPI, regulator, GPIO, device tree OF match data, `drm_panel_of_backlight()`, and orientation helpers. It registers one DSI driver and one SPI driver in the same module init/exit path, guarded by `CONFIG_DRM_MIPI_DSI` and `CONFIG_SPI`.

## Risks
The ST7701 command data is highly panel-specific and mostly not self-validating; incorrect descriptor voltages, gamma arrays, or GIP sequences can produce blank panels or image artifacts. `ST7701_WRITE` ignores command return values, so many initialization failures are not propagated. SPI and DSI share setup but differ in command transport and connector type, so adding a panel to the wrong OF match table can fail late. Sleep/reset delays are conservative but undocumented for some panels.

## Test Signals
Useful validation is successful probe/attach, regulator and GPIO acquisition, backlight binding, correct single fixed mode from `get_modes()`, correct orientation propagation, and a hardware smoke test of prepare/enable/disable/unprepare. For new descriptors, test both boot-from-off and bootloader-left-on cases, and verify panel-specific GIP/gamma behavior visually.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7703.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7703.c

## Purpose
This is a DRM MIPI DSI panel driver for panels based on the Sitronix ST7703 controller and close clones. It provides fixed modes and panel-specific vendor initialization sequences for Rocktech, Xingbangda, Anbernic, Powkiddy, and GameForce panels.

## Important APIs, Types, And Functions
`struct st7703` stores the DRM panel, reset GPIO, `vcc` and `iovcc` regulators, debugfs root, descriptor, and orientation. `struct st7703_panel_desc` provides mode, lanes, mode flags, pixel format, and an `init_sequence()` callback. Each panel has a static init function such as `jh057n_init_sequence()`, `xbd599_init_sequence()`, `rg353v2_init_sequence()`, `rgb30panel_init_sequence()`, `rgb10max3_panel_init_sequence()`, and `gameforcechi_init_sequence()`.

The panel ops are `st7703_prepare()`, `st7703_enable()`, `st7703_disable()`, `st7703_unprepare()`, `st7703_get_modes()`, and `st7703_get_orientation()`. Debug support is exposed through `allpixelson_set()` and `st7703_debugfs_init()`.

## Control Flow
Probe allocates the panel, acquires reset GPIO, stores match descriptor data, configures the DSI device from the descriptor, fetches `vcc` and `iovcc`, reads orientation, binds an optional OF backlight, adds the panel, attaches to the DSI host, logs the resolved mode, and creates debugfs. Prepare asserts reset, enables `iovcc` then `vcc`, waits for stabilization, deasserts reset, and waits again. Enable executes the descriptor init sequence through `mipi_dsi_multi_context`, exits sleep, waits 120 ms, and turns the display on. Disable turns display off, enters sleep, and waits 120 ms. Unprepare asserts reset and disables regulators.

## State And Persistence
No persistent state is written. The descriptor and debugfs pointer are retained for the device lifetime. The debugfs `allpixelson` file temporarily drives all pixels on, sleeps for a caller-provided number of seconds, and then cycles the panel through disable/unprepare/prepare/enable to restore video.

## Dependencies And Integration Points
The driver uses DRM panel APIs, MIPI DSI multi-context helpers, regulator and GPIO frameworks, OF match data, media bus format reporting, orientation helpers, OF backlight binding, and debugfs. It is registered with `module_mipi_dsi_driver()`.

## Risks
Many command sequences are vendor-provided or for clone controllers, so parameter meanings are partly undocumented. The debugfs all-pixels-on operation assumes the panel was already on and intentionally power-cycles it, making it unsuitable as a general userspace interface. Get-modes reports a single RGB888 bus format for all descriptors, which should match host expectations. Failure paths around DSI attach remove the panel, while later managed resources are released by device core.

## Test Signals
Validation should confirm DSI attach, regulator sequencing, orientation, backlight binding, debugfs creation/removal, and a working fixed mode for each compatible. Hardware tests should include suspend-like disable/unprepare cycles and the debugfs all-pixels-on recovery path on a non-production setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7703.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7789v.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7789v.c

## Purpose
This SPI-based DRM panel driver supports ST7789V-compatible LCD controllers attached as DPI panels controlled over 9-bit SPI. It programs controller timing, RGB interface polarity, gamma/power settings, optional inversion, and optional partial-mode row limits.

## Important APIs, Types, And Functions
`struct st7789_panel_info` describes the fixed mode, bus format, bus flags, inversion, and partial mode window. `struct st7789v` holds the DRM panel, selected panel info, SPI device, optional reset GPIO, power regulator, and orientation. SPI access is implemented by `st7789v_spi_write()`, `st7789v_write_command()`, `st7789v_write_data()`, and `st7789v_read_data()`. `st7789v_check_id()` optionally verifies display ID when RX is available.

Panel operations are `st7789v_prepare()`, `st7789v_enable()`, `st7789v_disable()`, `st7789v_unprepare()`, `st7789v_get_modes()`, and `st7789v_get_orientation()`. Probe configures 9-bit SPI and binds regulator, reset, backlight, and orientation.

## Control Flow
Probe allocates the panel, sets `spi->bits_per_word = 9`, runs `spi_setup()`, fetches match data, gets `power`, reset GPIO, OF backlight, and orientation, then adds the panel. Prepare derives pixel format and polarity from `info->bus_format`, display mode flags, and bus flags. It enables the regulator, toggles reset, optionally checks the display ID, exits sleep, waits 120 ms, programs address mode, pixel format, porch/gate/VCOM/power/gamma/RGB control registers, handles inversion, and optionally enters partial mode with configured row bounds. Enable sends display-on. Disable sends display-off. Unprepare sends sleep-in and disables the regulator.

## State And Persistence
The driver stores only static panel info and runtime hardware handles. There is no nonvolatile state. Orientation and display info are reported through connector state. The controller is fully reprogrammed on each prepare.

## Dependencies And Integration Points
It uses DRM panel and connector APIs, SPI, regulator, GPIO, MIPI DCS command definitions, media bus formats, bus flags, OF/SPI match tables, OF backlight, and orientation helpers. It exposes SPI IDs and OF compatibles for several panels.

## Risks
`st7789v_read_data()` implements unusual 9-bit read packing; ID reads are skipped on `SPI_NO_RX` and only warn on mismatch in prepare, so a wrong panel can still proceed. Bus format support is limited to RGB666 and RGB565; unsupported descriptors fail prepare. Partial mode assumes userspace uses the advertised mode, as noted in the source comment. Several ST7789V register settings are fixed rather than per-panel, which can be a problem for new compatibles.

## Test Signals
Check `spi_setup()` with 9-bit transfers, regulator/reset timing, optional ID warning behavior, fixed mode and bus format propagation, inversion/partial-mode behavior, and display recovery after disable/unprepare. For new panel info, test both RX-capable and no-RX SPI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7789v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-acx565akm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-acx565akm.c

## Purpose
This SPI/DPI DRM panel driver supports the Sony ACX565AKM family and related MIPI DBI-like panels historically used on Nokia/OMAP hardware. It detects panel ID over SPI, controls sleep/display state, exposes a DRM fixed mode, registers an internal backlight device when supported, and exposes CABC controls through sysfs.

## Important APIs, Types, And Functions
`struct acx565akm_panel` tracks the DRM panel, SPI device, reset GPIO, backlight, mutex, detected name/model/revision, feature flags, enabled flag, CABC mode, and hardware guard timing. SPI transfers are centralized in `acx565akm_transfer()` with helpers `acx565akm_cmd()`, `acx565akm_write()`, and `acx565akm_read()`.

Important behavior is in `acx565akm_detect()`, `acx565akm_power_on()`, `acx565akm_power_off()`, `acx565akm_set_sleep_mode()`, `acx565akm_set_display_state()`, backlight ops, and `cabc_mode` sysfs handlers. Panel ops are `enable`, `disable`, and `get_modes`; this older driver does not split power into prepare/unprepare.

## Control Flow
Probe allocates the panel, sets `SPI_MODE_3`, gets reset GPIO default high, detects display status and ID, derives feature flags, initializes backlight/CABC when supported, and adds the panel. Detection may leave reset asserted low if the bootloader did not already enable the panel. Enable locks the mutex, performs reset/sleep-out/display-on/CABC/backlight programming, and records `enabled`. Disable locks the mutex, sends display-off and sleep-in, waits for required frame/reset delays, asserts reset, and clears `enabled`.

## State And Persistence
Mutable state includes `enabled`, `cabc_mode`, hardware guard jiffies, and detected panel identity. CABC mode persists only in memory and is applied when the panel is enabled. Backlight brightness is read from and written to panel registers. The mutex serializes panel register access from DRM, backlight, and sysfs paths.

## Dependencies And Integration Points
The file integrates with DRM panel, SPI, GPIO, backlight core, sysfs attributes, MIPI DCS command definitions, mutexes, jiffies, and scheduler sleep for guard timing. OF and SPI ID tables bind compatible `sony,acx565akm`.

## Risks
The file contains TODOs noting untested backlight modernization and prepare/unprepare separation. SPI transfer helpers do not propagate errors to most callers. The CABC sysfs parser has a duplicated `return -EINVAL;` line after the invalid-mode check, harmless but visibly stale. Power sequencing uses FIXME delay comments and legacy assumptions. Since display ID controls feature flags, failed or noisy reads can prevent probe.

## Test Signals
Hardware validation should cover ID detection for each supported ID, bootloader-enabled and disabled startup states, CABC sysfs reads/writes, brightness get/update, sleep guard timing, and repeated enable/disable. Static review should watch for ignored SPI errors and legacy backlight behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-acx565akm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-td4353-jdi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-td4353-jdi.c

## Purpose
This driver supports Sony Xperia XZ2/XZ2 Compact JDI TD4353-based MIPI DSI panels. It exposes one fixed 1080x2160 60 Hz mode and sequences panel and touch reset GPIOs together with three regulators.

## Important APIs, Types, And Functions
`struct sony_td4353_jdi` stores the DRM panel, DSI device, three supplies (`vddio`, `vsp`, `vsn`), panel reset GPIO, touch reset GPIO, and a type selector. `sony_td4353_jdi_on()` programs DCS address/window/TE/pixel-format/partial-row commands, exits sleep, starts memory write, and turns the display on. `sony_td4353_jdi_off()` turns display off, disables TE, and enters sleep. `sony_td4353_assert_reset_gpios()` drives both reset lines.

Panel functions are prepare, unprepare, and get_modes. Probe handles regulator/GPIO acquisition, DSI setup, backlight binding, `prepare_prev_first`, panel add, and DSI attach.

## Control Flow
Probe allocates the panel from OF match data, configures regulators and reset GPIOs, sets DSI to four RGB888 lanes with non-continuous clock, binds a backlight, adds the panel, and attaches to the DSI host. Prepare enables regulators, waits 100 ms, asserts both reset GPIOs, then runs the panel-on DCS sequence. If panel-on fails, it deasserts reset and disables regulators. Unprepare sends off/sleep commands, deasserts both resets, and disables regulators.

## State And Persistence
The only variant state is `type`; currently only `TYPE_TAMA_60HZ` is implemented. There is no persistent storage. The panel is fully initialized on each prepare. The driver mutates `dsi->mode_flags` to enter low-power mode during on and clears it during off.

## Dependencies And Integration Points
It uses DRM panel, MIPI DSI multi-context DCS helpers, regulator bulk APIs, GPIO descriptors, OF match data, and OF backlight. The compatible is `sony,td4353-jdi-tama`.

## Risks
Touch reset is coupled to panel reset, so sequencing errors can affect the touch controller. The mode selection enum has expansion comments but only one implemented path; unknown types return `-EINVAL` in get_modes. Width/height and timing are hard-coded. The on/off paths modify DSI mode flags and assume host tolerance for LPM transitions.

## Test Signals
Tests should confirm all three regulators, both reset GPIOs, DSI attach, backlight binding, fixed 1080x2160 mode, and clean rollback on panel-on failure. Hardware tests need display-on, display-off, and touch-controller survival across prepare/unprepare cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-td4353-jdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-tulip-truly-nt35521.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-tulip-truly-nt35521.c

## Purpose
This DRM MIPI DSI panel driver supports the Sony Tulip Truly NT35521 panel. It provides a fixed 720x1280 mode, lengthy vendor initialization sequence, DSI brightness backlight, and a separate GPIO-controlled backlight enable line.

## Important APIs, Types, And Functions
`struct truly_nt35521` stores the DRM panel, DSI device, two regulators (`positive5`, `negative5`), reset GPIO, and backlight-enable GPIO. `nt35521_switch_page()` wraps the page unlock/select command. `truly_nt35521_on()` emits the multi-page vendor command sequence, exits sleep, waits, turns display on, and writes control display. `truly_nt35521_off()` turns display off and enters sleep.

Panel ops are prepare, unprepare, enable, disable, and get_modes. Backlight ops use `mipi_dsi_dcs_set_display_brightness()` and `mipi_dsi_dcs_get_display_brightness()`.

## Control Flow
Probe allocates the panel, gets positive/negative regulators, reset and backlight GPIOs, configures four-lane RGB888 video burst DSI with HSE, no EOT, and non-continuous clock, creates a managed raw backlight, adds the panel, and attaches to the DSI host. Prepare enables regulators, performs the reset sequence, then sends the large vendor init. On failure it logs and asserts reset but does not explicitly disable regulators in the failure branch. Enable drives the backlight GPIO high; disable drives it low. Unprepare sends off/sleep, asserts reset, and disables regulators.

## State And Persistence
There is no persistent storage. Brightness state is held by the backlight core and mirrored to the panel over DCS. The panel is reinitialized from scratch on prepare. DSI mode flags are switched into LPM for initialization and cleared in off.

## Dependencies And Integration Points
The driver uses DRM panel, MIPI DSI multi-context helpers, regulator bulk APIs, GPIO, managed backlight registration, and OF match binding. It is registered as a MIPI DSI driver under compatible `sony,tulip-truly-nt35521`.

## Risks
The vendor command sequence is long and opaque; small changes are high risk. The reset helper sets reset high twice before low, which likely reflects active-low hardware but should be checked against bindings and board schematics. Prepare failure after regulators are enabled leaves cleanup mostly to later paths unless the caller unprepares. Brightness get returns only the low 8 bits.

## Test Signals
Validation should cover DSI attach, regulator enable/disable, reset polarity, GPIO backlight enable, DCS brightness set/get, fixed mode reporting, and repeated prepare/enable/disable/unprepare. A panel-init failure injection or host error path is useful to inspect regulator cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sony-tulip-truly-nt35521.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-startek-kd070fhfid015.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-startek-kd070fhfid015.c

## Purpose
This driver supports the Startek KD070FHFID015 1200x1920 MIPI DSI panel. It sequences two regulators, reset and power-enable GPIOs, emits a short DCS/vendor init sequence, reports a fixed mode, and registers a DSI DCS backlight.

## Important APIs, Types, And Functions
`struct stk_panel` owns the fixed mode pointer, backlight, DRM panel base, enable/reset GPIOs, DSI device, and two supplies (`iovcc`, `power`). `stk_panel_init()` performs soft reset, sleep-out, interface register programming, brightness/control-display/pixel-format setup, and column/page address programming. `stk_panel_on()` sends display-on, while `stk_panel_off()` sends display-off and sleep-in.

Panel ops are prepare, unprepare, and get_modes. Backlight ops `dsi_dcs_bl_get_brightness()` and `dsi_dcs_bl_update_status()` temporarily clear and restore `MIPI_DSI_MODE_LPM` around DCS brightness commands.

## Control Flow
Probe configures DSI for four RGB888 lanes in video LPM mode, allocates state, adds the panel resources through `stk_panel_add()`, and attaches to the DSI host. Add fetches regulators/GPIOs, creates managed backlight, initializes the DRM panel, and adds it. Prepare asserts reset and enable low, enables IOVCC, waits, enables power, waits, drives enable/reset high, initializes the panel, and turns it on. Failure disables already-enabled regulators and restores GPIOs. Unprepare sends off/sleep, disables regulators, drives reset low, and drives enable high.

## State And Persistence
Runtime state is limited to hardware handles and the fixed mode pointer. Backlight brightness is maintained by the backlight core and panel DCS registers. No persistent storage exists.

## Dependencies And Integration Points
The driver integrates with DRM panel, MIPI DSI multi-context DCS helpers, regulators, GPIOs, backlight core, OF match, and module MIPI DSI registration. Its compatible is `startek,kd070fhfid015`.

## Risks
GPIO polarity is subtle: unprepare drives `enable_gpio` high after disabling supplies, while prepare initially drives it low and later high. If a board inverts this line differently, power sequencing can fail. Backlight operations mutate `dsi->mode_flags`; concurrent panel state changes would need host tolerance. There is no separate enable/disable panel op, so prepare includes display-on.

## Test Signals
Check regulator order, GPIO polarity, DSI attach, fixed 1200x1920 mode, brightness get/set, and failure rollback from each prepare stage. Hardware testing should include repeated full modesets and suspend/resume-like cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-startek-kd070fhfid015.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-summit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-summit.c

## Purpose
This compact MIPI DSI panel driver models Apple Summit as a non-desktop display with a fixed 60x2008 mode and a raw DCS brightness backlight. It primarily provides mode enumeration and brightness control rather than explicit power sequencing.

## Important APIs, Types, And Functions
`struct summit_data` stores the DSI device, backlight, and DRM panel. `summit_set_brightness()` sends `mipi_dsi_dcs_set_display_brightness()` with the current backlight level. `summit_get_modes()` marks the connector non-desktop and delegates mode creation to `drm_connector_helper_get_modes_fixed()`. Suspend/resume PM uses `summit_suspend()` and `summit_set_brightness()`.

## Control Flow
Probe allocates the panel, stores DSI driver data, reads `max-brightness` from firmware properties, registers a raw backlight using that maximum, adds the panel, and attaches to the DSI host. Remove detaches and removes the panel. There are no explicit prepare/enable/disable/unprepare ops; brightness is used by backlight and PM callbacks.

## State And Persistence
State is limited to the DSI pointer, backlight object, and panel. Brightness is managed by backlight core and sent to the panel on update/resume. No persistent state is written.

## Dependencies And Integration Points
The file depends on DRM panel/mode/helper APIs, MIPI DSI DCS brightness, backlight core, generic device properties, non-desktop connector property support, and simple dev PM ops. It binds `apple,summit`.

## Risks
The mode is unusual (`hdisplay = 60`, `vdisplay = 2008`) and intentionally non-desktop, so generic desktop assumptions should not be applied. Missing `max-brightness` fails probe. There is no regulator/GPIO sequencing, so hardware must be powered by other platform components. DSI mode flags are not configured in this driver, relying on host/default setup or firmware assumptions.

## Test Signals
Validation should confirm property parsing, backlight registration with expected max brightness, non-desktop connector flag/property, fixed mode reporting, DSI attach/detach, suspend brightness zeroing, and resume brightness restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-summit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-r63353.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-r63353.c

## Purpose
This MIPI DSI driver supports panels using the Synaptics R63353 controller, currently described by the Sharp LS068B3SX02 descriptor. It powers two regulators, controls reset, emits a descriptor-defined init command list, and reports a fixed RGB888 DSI mode.

## Important APIs, Types, And Functions
`struct r63353_instr` and `R63353_INSTR()` encode initialization commands. `struct r63353_desc` stores the panel name, init list, mode, and dimensions. `struct r63353_panel` contains the DRM panel, DSI device, reset GPIO, `dvdd` and `avdd`, and descriptor pointer.

Core helpers are `r63353_panel_power_on()`, `r63353_panel_power_off()`, `r63353_panel_activate()`, and `r63353_panel_deactivate()`. DRM ops are prepare, unprepare, and get_modes. Shutdown calls `drm_panel_unprepare()` to put the panel down on system shutdown.

## Control Flow
Probe allocates the panel, stores match descriptor, configures the DSI device for two RGB888 lanes with video, HSE, LPM, sync pulse, no EOT, and non-continuous clock, acquires `dvdd`, `avdd`, and reset GPIO, marks `prepare_prev_first`, binds optional backlight, adds the panel, and attaches to DSI. Prepare enables `avdd`, waits, enables `dvdd`, waits 300-350 ms, deasserts reset, soft-resets the controller, enters sleep, writes the descriptor init commands, waits 120 ms, exits sleep, then turns display on. Unprepare sends display-off/sleep and powers off.

## State And Persistence
State is descriptor-driven and held in memory only. There is no persistent storage. The init list is immutable. Hardware is reinitialized on each prepare.

## Dependencies And Integration Points
The driver uses DRM panel, MIPI DSI multi-context helpers, regulators, GPIOs, OF match data, media bus format reporting, OF backlight, and DSI shutdown handling.

## Risks
The init sequence contains brightness/control-display/display-on commands before sleep-out, so ordering is panel-specific. `r63353_panel_power_on()` uses a long regulator stabilization wait; shortening it may break real hardware. `r63353_panel_activate()` enters sleep after soft reset before writing init commands, which should not be generalized without datasheet evidence. The descriptor pointer is typed non-const in state despite pointing to static data.

## Test Signals
Check regulator sequencing and long delay, reset polarity, DSI attach, fixed mode dimensions, RGB888 bus format, backlight binding, shutdown unprepare, and error rollback when activation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-r63353.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-tddi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-tddi.c

## Purpose
This driver supports Synaptics TDDI DSI panels, currently `syna,td4101-panel` and `syna,td4300-panel`. It uses firmware-provided panel timings, descriptor-provided lane counts and enable/disable delays, regulator/reset/backlight GPIO sequencing, and a managed backlight device.

## Important APIs, Types, And Functions
`struct tddi_panel_data` stores lanes and panel-specific sleep/display delays. `struct tddi_ctx` stores the DRM panel, DSI device, parsed DRM mode, backlight device, descriptor data, regulator array, reset GPIO, and optional backlight GPIO. `tddi_update_status()` writes DCS brightness only when `ctx->panel.enabled` is true.

Panel functions are `tddi_prepare()`, `tddi_unprepare()`, `tddi_enable()`, `tddi_disable()`, and `tddi_get_modes()`. Probe uses `of_get_drm_panel_display_mode()` rather than hard-coded mode constants.

## Control Flow
Probe allocates the panel, gets constant regulator bulk data for `vio`, `vsn`, and `vsp`, gets optional backlight and reset GPIOs, parses the fixed mode from device tree, registers a platform backlight, configures DSI lanes/format/video flags from descriptor data, sets `prepare_prev_first`, adds the panel, and attaches with `devm_mipi_dsi_attach()`. Prepare enables regulators, toggles reset low-high-low, and drives the backlight GPIO low. Enable sends power-save/control-display commands, exits sleep, waits descriptor delay, synchronizes brightness, turns display on, and waits display-on delay. Disable performs display-off and sleep-in with descriptor delays. Unprepare drives backlight GPIO high, reset high, and disables regulators.

## State And Persistence
The parsed display mode and descriptor timing data persist for device lifetime. Brightness lives in the backlight core and is sent at enable/update time. There is no nonvolatile state.

## Dependencies And Integration Points
The driver integrates with DRM panel and probe helper fixed-mode support, MIPI DSI multi-context helpers, regulator bulk const APIs, GPIO, backlight core, OF display timing parsing, and managed DSI attach.

## Risks
Reset and backlight GPIOs are optional but used unconditionally via `gpiod_set_value_cansleep()`, which is safe for NULL descriptors but requires correct polarity in bindings. Brightness updates are skipped while the panel is disabled; callers must rely on enable to sync stored brightness. Mode correctness depends entirely on device-tree timings.

## Test Signals
Validate both compatibles for lane count and delays, device-tree timing parsing, regulator/GPIO handling when optional GPIOs are absent, brightness sync on enable, and repeated enable/disable with DSI host error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-synaptics-tddi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tdo-tl070wsh30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tdo-tl070wsh30.c

## Purpose
This MIPI DSI panel driver supports the TDO TL070WSH30 1024x600 panel. It supplies fixed mode information and a simple regulator/reset plus DCS sleep/display-on sequence.

## Important APIs, Types, And Functions
`struct tdo_tl070wsh30_panel` stores the DRM panel base, DSI link, power regulator, and reset GPIO. Core ops are `tdo_tl070wsh30_panel_prepare()`, `tdo_tl070wsh30_panel_unprepare()`, `tdo_tl070wsh30_panel_get_modes()`, and `tdo_tl070wsh30_panel_add()`.

## Control Flow
Probe configures four-lane RGB888 DSI in video burst LPM mode, allocates state, initializes resources in `panel_add()`, and attaches to the DSI host. Add gets the `power` regulator, reset GPIO, initializes the panel, binds an optional OF backlight, and adds the panel. Prepare enables the regulator, toggles reset high then low, waits 200 ms, exits sleep, waits 200 ms, sets display on, and waits 20 ms. Unprepare sends display-off, waits, enters sleep, waits, and disables the regulator.

## State And Persistence
The driver has no persistent state. It stores only the hardware handles and always replays the DCS sequence during prepare. Backlight, if present, is externally described through OF.

## Dependencies And Integration Points
It depends on DRM panel, DRM mode helpers, MIPI DSI DCS helpers, regulators, GPIOs, OF match data, and OF backlight support. It registers with `module_mipi_dsi_driver()`.

## Risks
If `mipi_dsi_dcs_set_display_on()` fails, prepare disables the regulator but does not explicitly enter sleep or reset; the next prepare must recover. Unprepare returns an error if sleep-in fails, before disabling the regulator, which can leave power enabled. Timing is conservative but hard-coded. No width/height is in the mode object, only connector display info.

## Test Signals
Tests should verify DSI attach, fixed 1024x600 timing, bpc/display dimensions, regulator cleanup on sleep-out/display-on failures, backlight binding, and repeated prepare/unprepare cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tdo-tl070wsh30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-td028ttec1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-td028ttec1.c

## Purpose
This SPI/DPI DRM panel driver supports the Toppoly TD028TTEC1 panel and backward-compatible `toppoly,td028ttec1` device tree name. It configures a JBT6K74-like controller through 9-bit SPI register writes and exposes a fixed 480x640 DPI mode.

## Important APIs, Types, And Functions
`struct td028ttec1_panel` stores the DRM panel and SPI device. `jbt_ret_write_0()`, `jbt_reg_write_1()`, and `jbt_reg_write_2()` send command-only, one-byte, and two-byte register writes, using an optional shared error pointer to stop subsequent writes after the first failure. Panel ops are prepare, enable, disable, unprepare, and get_modes.

## Control Flow
Probe allocates the panel, configures SPI mode 3 and 9 bits per word, binds OF backlight, and adds the panel. Prepare sends a long register initialization sequence: wake/deep-standby exit, RGB interface setup, power rails, output control, sleep-out, display mode, booster, voltage, gamma, blanking, and timing registers. Enable sends display-on. Disable sends display-off. Unprepare sets output control, enters sleep, and powers off. Remove removes the panel and calls disable/unprepare.

## State And Persistence
There is no stored mutable panel configuration beyond the SPI pointer. Controller register state is programmed every prepare. Backlight state is managed externally through DRM panel OF backlight.

## Dependencies And Integration Points
The driver uses DRM panel, SPI, OF/SPI match tables, MIPI-like command constants encoded locally, and OF backlight. It presents a DPI connector and fixed bus flags.

## Risks
The SPI command format depends on 9-bit transfers and host support. The source contains a FIXME that sync signals should be sampled on a datasheet-rising edge, while legacy code indicates falling edge; bus flags therefore need real-hardware validation. Disable/unprepare ignore errors. The initialization sequence is legacy and magic-value heavy.

## Test Signals
Confirm SPI 9-bit setup, fixed mode and bus flags, backlight binding, command error propagation during prepare, and real hardware visual behavior, especially sync polarity and color/flicker. Regression tests should cover both compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-td028ttec1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-td043mtea1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-td043mtea1.c

## Purpose
This SPI/DPI driver supports the Toppoly TD043MTEA1 panel. It controls panel power through a regulator and reset GPIO, programs mode/gamma/mirror registers over 16-bit SPI, exposes sysfs controls for mode, vertical mirror, and gamma, and handles SPI suspend/resume ordering.

## Important APIs, Types, And Functions
`struct td043mtea1_panel` stores the DRM panel, SPI device, VCC regulator, reset GPIO, current mode, 12-entry gamma table, vertical mirror flag, and power/PM flags. Hardware access is via `td043mtea1_write()`, `td043mtea1_write_gamma()`, and `td043mtea1_write_mirror()`. Power is handled by `td043mtea1_power_on()` and `td043mtea1_power_off()`.

Sysfs attributes are `vmirror`, `mode`, and `gamma`. DRM panel ops are prepare, unprepare, and get_modes. PM callbacks are `td043mtea1_suspend()` and `td043mtea1_resume()`.

## Control Flow
Probe allocates the panel, initializes default 800x480 mode and gamma, gets regulator and reset GPIO, configures SPI mode 0 with 16 bits per word, creates the sysfs group, and adds the panel. Prepare powers on unless SPI is suspended. Power-on enables VCC, waits 160 ms, deasserts reset, writes mode/control/PWM/mirror/gamma registers, and marks powered. Unprepare powers off unless SPI is suspended. Suspend powers off but preserves the logical powered-on flag, marks SPI suspended, and resume reprograms if the panel was logically on.

## State And Persistence
Mode, gamma, mirror, and logical power flags live in memory only. Sysfs changes immediately write hardware and update memory, then are reapplied on later power-on. No persistent storage exists across reboot.

## Dependencies And Integration Points
The driver integrates with DRM panel, SPI, regulator, GPIO, sysfs device attributes, PM ops, and OF/SPI matching. It exposes a DPI connector and fixed mode with bus flags.

## Risks
Sysfs writes call SPI programming regardless of power state, so userspace changes while unpowered can fail or talk to an inactive controller. Gamma parsing uses `sscanf()` and accepts values wider than 10 bits, later truncating by register packing. The mode/bus flag FIXME mirrors legacy uncertainty about sync sampling edge. The suspend path intentionally preserves logical powered state while powering off, which is easy to break in refactors.

## Test Signals
Validate sysfs attribute creation/removal, mode/gamma/mirror writes, SPI 16-bit setup, power-on/off idempotency, suspend/resume with panel on and off, fixed mode reporting, and bus polarity on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-td043mtea1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-tpg110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-tpg110.c

## Purpose
This SPI/DPI driver supports the TPO TPG110 LCD controller. Because the chip drives several possible LCD resolutions, the driver detects the configured resolution over SPI, maps it to a supported DRM mode, reads physical dimensions from device tree, and toggles standby through controller registers.

## Important APIs, Types, And Functions
`struct tpg110_panel_mode` maps controller magic values to mode names, `drm_display_mode`, and bus flags. `struct tpg110` stores device/SPI/panel handles, detected panel mode, width/height, and reset GPIO `grestb`. SPI access is in `tpg110_readwrite_reg()`, with `tpg110_read_reg()` and `tpg110_write_reg()` wrappers.

`tpg110_startup()` deasserts reset, performs a communication test, logs chip ID and resolution, maps dual-scan variants to producer-side modes, selects the panel mode, and takes software control of resolution/standby. Panel ops are enable, disable, and get_modes.

## Control Flow
Probe allocates the panel, reads `width-mm` and `height-mm`, gets reset GPIO initially asserted, configures SPI for 8-bit 3-wire high-impedance mode, stores the SPI device, runs startup detection, binds optional OF backlight, sets driver data, and adds the panel. Enable reads the power-management control bit and sets it. Disable reads the same register and clears it. Get-modes duplicates the detected mode and sets connector dimensions and bus flags.

## State And Persistence
Detected panel mode and dimensions are kept for the device lifetime. The controller remains configured for software control after startup. There is no persistent software storage.

## Dependencies And Integration Points
The driver depends on DRM panel, SPI 3-wire Hi-Z support, GPIO reset, OF properties for dimensions, OF/SPI match tables, and OF backlight. It exposes a DPI connector.

## Risks
The code logs missing width/height properties but does not fail, so zero dimensions can be reported. SPI read/write returns `u8`, so negative `spi_sync()` errors are truncated when returned from `tpg110_readwrite_reg()`, which can hide failures in callers expecting register values. `tpg110_disable()` and `tpg110_enable()` use `TPG110_CTRL2_PM` as the register address even though it is a bit definition, which deserves careful audit against the datasheet. Unsupported hardware-configured resolutions fail probe.

## Test Signals
Test SPI communication test failure, all supported resolution magic values, width/height property handling, standby enable/disable, backlight binding, and real bus flag behavior. Static tests should flag the bit-vs-register ambiguity in enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-tpg110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-truly-nt35597.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-truly-nt35597.c

## Purpose
This driver supports a dual-DSI Truly NT35597 2K panel, including Qualcomm SDM845 MTP configuration. It registers and attaches a secondary DSI device from the graph, drives both DSI links in parallel for commands, sequences regulators with load votes, controls reset/mode GPIOs, and exposes a fixed 1440x2560 mode.

## Important APIs, Types, And Functions
`struct cmd_set` stores up to four command bytes and size. `struct nt35597_config` describes dimensions, panel name, on-command list, command count, and display mode. `struct truly_nt35597` holds device, DRM panel, three supplies (`vdda`, `vdispp`, `vdispn`), reset/mode GPIOs, optional backlight pointer, two DSI devices, and config.

`truly_dcs_write()` and `truly_dcs_write_buf()` broadcast commands to both DSI links. Power sequencing is in `truly_35597_power_on()` and `truly_nt35597_power_off()`. Panel ops are disable, unprepare, prepare, enable, and get_modes.

## Control Flow
Probe allocates state, gets match config, resolves the remote graph endpoint for the second DSI host, registers a second DSI device, stores both links, adds the panel resources, then configures and attaches both DSI devices. Panel add gets regulators, reset and mode GPIOs, forces dual-port mode via mode GPIO low, initializes and adds the panel. Prepare powers on regulators with enable loads, performs reset toggling, enables LPM on both DSI links, broadcasts the config command list, exits sleep, waits 120 ms, sets display-on, and waits another 120 ms. Unprepare clears DSI mode flags, broadcasts display-off and sleep-in, then powers off and reduces regulator loads.

## State And Persistence
State includes both DSI device pointers, config pointer, GPIO handles, and regulator load state. There is no persistent storage. The command list is static and replayed at each prepare.

## Dependencies And Integration Points
The driver integrates with DRM panel, MIPI DSI, OF graph, secondary DSI device registration, regulators with load setting, GPIOs, optional backlight core, and DSI mode flags. It requires the device tree graph to expose a second DSI host.

## Risks
The dual-DSI attach path has complex cleanup: if attaching the second link fails, already-attached first-link detach is not explicit before panel removal and secondary unregister. `truly_dcs_write()` logs failures but continues and returns the last `ret`, which can mask an earlier DSI failure if a later link succeeds. Backlight pointer is never initialized in this file, so enable/disable backlight calls are currently no-ops unless assigned externally. The vendor command table is large and opaque.

## Test Signals
Test graph resolution and probe deferral for missing second DSI host, secondary device registration/unregistration, both-link command failures, regulator load transitions, reset/mode GPIO polarity, fixed 1440x2560 mode, and attach-failure cleanup. Hardware testing must confirm both DSI links are active and synchronized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-truly-nt35597.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-g2647fb105.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-g2647fb105.c

## Purpose
This MIPI DSI driver supports the Visionox G2647FB105 AMOLED panel. It provides a fixed 1080x2340 mode, sequences four regulators and reset, sends a short vendor initialization sequence, and registers a high-range DCS backlight.

## Important APIs, Types, And Functions
`struct visionox_g2647fb105` holds the DRM panel, DSI device, reset GPIO, and managed regulator bulk array. The regulator list is `vdd3p3`, `vddio`, `vsn`, and `vsp`. `visionox_g2647fb105_reset()` toggles reset. `visionox_g2647fb105_on()` writes vendor pages/registers, enables TE, sets brightness to zero, exits sleep, waits 100 ms, and turns display on. `visionox_g2647fb105_off()` sends display-off and sleep-in.

Panel ops are prepare, unprepare, and get_modes. Backlight update uses `mipi_dsi_dcs_set_display_brightness_large()` with a 2047 maximum.

## Control Flow
Probe allocates state, gets constant regulator bulk data, gets reset GPIO default high, configures four-lane RGB888 DSI in burst/non-continuous/LPM mode, initializes the DRM panel, creates a managed raw backlight, adds the panel, and attaches with `devm_mipi_dsi_attach()`. Prepare enables all regulators, resets, and runs the on sequence. Unprepare runs off, asserts reset high, and disables regulators. Backlight update temporarily clears LPM, writes large brightness, then restores LPM.

## State And Persistence
No persistent state is stored. Brightness is managed by backlight core; the init sequence sets brightness to zero before display-on, while later updates apply user brightness. Regulator handles are managed through a bulk pointer allocated by the devm helper.

## Dependencies And Integration Points
It depends on DRM panel, MIPI DSI multi-context helpers, regulator bulk const API, GPIO, managed backlight registration, DCS large brightness helper, and managed DSI attach. Compatible is `visionox,g2647fb105`.

## Risks
Prepare failure after regulators are enabled does not explicitly disable them if `visionox_g2647fb105_on()` fails. Backlight updates mutate DSI LPM flags, which can race conceptually with panel lifecycle unless higher layers serialize calls. The file sets `prepare_prev_first` before and after `drm_panel_init()`, with the first assignment occurring before panel init and therefore not useful. Vendor command meanings are mostly opaque.

## Test Signals
Validate regulator cleanup paths, reset polarity, DSI attach, fixed mode dimensions, TE enable, brightness range and large-brightness command, and repeated prepare/unprepare. A host-command failure test is useful for regulator leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-g2647fb105.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-r66451.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-r66451.c

## Purpose
This driver supports the Visionox R66451 AMOLED DSI panel with Display Stream Compression (DSC). It configures DSC parameters, sends a large vendor initialization sequence, sends PPS during enable, and exposes fixed 1080x2340 timing plus raw DCS brightness.

## Important APIs, Types, And Functions
`struct visionox_r66451` stores the DRM panel, DSI device, reset GPIO, and two supplies (`vddio`, `vdd`). `visionox_r66451_on()` sends vendor page/register setup, TE enable, and address-window commands. `visionox_r66451_prepare()` enables supplies, resets, runs init, and enables DSI compression mode. `visionox_r66451_enable()` packs DSC PPS using `drm_dsc_pps_payload_pack()`, sends it via `mipi_dsi_picture_parameter_set_multi()`, exits sleep, waits 120 ms, and turns display on.

Panel ops include prepare, unprepare, enable, disable, and get_modes. Backlight update uses 16-bit brightness with max 4095.

## Control Flow
Probe allocates the panel and a managed `drm_dsc_config`, fills DSC version 1.2, slice dimensions, two slices, 8 bpc, 8 bpp, and block prediction, assigns it to `dsi->dsc`, gets regulators and reset GPIO, configures four RGB888 lanes with LPM/non-continuous clock, creates a raw backlight, adds the panel, and attaches to DSI. Prepare powers and initializes vendor registers, then enables compression mode. Enable requires `dsi->dsc`, sends PPS, exits sleep, and turns display on. Disable sends display-off and sleep-in. Unprepare clears LPM, asserts reset, and disables regulators.

## State And Persistence
State includes the DSI DSC config pointer, regulator handles, and reset GPIO. No persistent storage is used. The panel initialization and DSC PPS are replayed during lifecycle transitions.

## Dependencies And Integration Points
The driver integrates with DRM panel, MIPI DSI, DRM DSC helpers, PPS payload packing, regulator bulk APIs, GPIO, backlight core, and fixed-mode helper. Compatible is `visionox,r66451`.

## Risks
DSC configuration is hard-coded and must match the DSI host and panel; a mismatch can produce no image despite successful attach. `get_modes()` uses `drm_connector_helper_get_modes_fixed()` and then returns 1, relying on helper success without checking return. Mode physical dimensions are zero. `visionox_r66451_off()` only clears LPM; actual display-off/sleep is in disable, so lifecycle ordering matters. Backlight brightness maximum is 4095 but DCS helper takes `u16`, so userspace scale must be correct.

## Test Signals
Validate DSC host support and PPS payload transmission, compression mode enabling, fixed mode timing, backlight range, regulator/reset sequencing, and full prepare/enable/disable/unprepare ordering. Hardware tests should include DSC visual integrity and failure behavior when `dsi->dsc` is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-r66451.c -->
