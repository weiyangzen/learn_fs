# Research: subset-b-003698

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9881c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9881c.c

## Purpose

This is a DRM panel driver for MIPI DSI panels built around the Ilitek ILI9881C controller. It supports several board and panel compatibles through descriptor records that select a fixed display mode, DSI mode flags, lane count, an optional default address mode, and a panel-specific vendor initialization table. The driver is not a generic runtime-configurable panel stack; almost all panel variance is encoded in static command arrays and OF match data.

## Important APIs, Types, And Functions

- `struct ili9881c_instr` models the panel init script as either `ILI9881C_SWITCH_PAGE` or `ILI9881C_COMMAND`.
- `struct ili9881c_desc` binds an init script, default mode, DSI flags, address mode, and lane count to one compatible.
- `struct ili9881c` stores the `drm_panel`, attached `mipi_dsi_device`, descriptor, `power` regulator, optional reset GPIO, orientation, and computed DCS address mode.
- `ili9881c_switch_page()` sends private page selection bytes using command `0xff`.
- `ili9881c_send_cmd_data()` sends one command/data pair through `mipi_dsi_dcs_write_buffer_multi()`.
- `ili9881c_prepare()` is the main power-on path: enable regulator, reset, replay the descriptor init table, return to page 0, optionally program `MIPI_DCS_SET_ADDRESS_MODE`, enable tearing, exit sleep, delay, and turn display on.
- `ili9881c_unprepare()` sends display off and sleep mode, disables power, and asserts reset.
- `ili9881c_get_modes()` duplicates the descriptor mode, marks it preferred, fills physical size and subpixel order, and propagates panel orientation.
- `ili9881c_dsi_probe()` allocates the panel, gets resources, reads orientation, handles bottom-up address-mode correction, configures DSI lanes/format/flags, and attaches to the host.

## Control Flow

Probe is driven by the MIPI DSI bus and `ili9881c_of_match`. The match data selects one of the descriptors for compatibles such as `bananapi,lhr050h41`, `bestar,bsd1218-a101kl68`, `feixin,k101-im2byl02`, `startek,kd050hdfia020`, `tdo,tl050hdv35`, `wanchanglong,w552946aaa`, `wanchanglong,w552946aba`, `ampire,am8001280g`, `raspberrypi,dsi-5inch`, and `raspberrypi,dsi-7inch`. After `drm_panel_add()`, the driver sets `dsi->mode_flags`, `dsi->format = MIPI_DSI_FMT_RGB888`, and `dsi->lanes`, then calls `mipi_dsi_attach()`.

At prepare time, the driver powers the panel and toggles reset before iterating every instruction in the selected static init array. These arrays are long register scripts grouped by controller page and cover timing, gamma, source/gate mapping, power, and panel tuning values. Once the script finishes, the driver sends common DCS commands to start scanning. Mode enumeration is independent from hardware reads; it duplicates one fixed `drm_display_mode` from the descriptor.

## State And Persistence

There is no persistent storage, runtime calibration, EDID, or NVM handling. Driver state is in memory only and rebuilt on probe. The persistent external state is the panel controller's volatile register state, which is reprogrammed on each prepare. `orientation` comes from device tree, while `address_mode` is derived from the descriptor and adjusted if the DT orientation is bottom-up.

## Dependencies And Integration Points

The driver integrates with the DRM panel framework, the MIPI DSI helpers, DT OF match data, regulator framework, GPIO descriptors, and optional DRM backlight lookup. It relies on `mipi_dsi_multi_context` for accumulated DSI command errors. Connector integration occurs through `get_modes()` and `get_orientation()`. `prepare_prev_first = true` requests bridge sequencing where the panel prepare should happen before the previous element in the pipeline.

## Risks

The largest risk is descriptor accuracy: one wrong register value, lane count, DSI flag, or reset/power delay can produce a blank, unstable, or electrically stressed panel. Several descriptors omit `.lanes`, which means a zero lane count unless intentionally accepted by surrounding code or fixed elsewhere; this should be checked when modifying those entries. Error unwinding in `ili9881c_prepare()` disables the regulator but does not explicitly assert reset after a failed command script. `ili9881c_unprepare()` ignores accumulated DCS errors. Orientation handling rewrites bottom-up to normal by flipping address-mode bits, so changes around panel rotation need hardware verification.

## Test Signals

Useful checks include successful module bind and DSI attach, regulator/reset GPIO sequencing on a scope or logs, a single preferred mode with expected resolution and physical size, correct subpixel order and orientation, backlight binding, and clean suspend/resume or repeated enable/disable cycles. Hardware validation should verify that each compatible lights reliably after cold boot and after runtime PM or display blanking, with no color channel swap, upside-down image, tearing misconfiguration, or flicker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9881c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9882t.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9882t.c

## Purpose

This DRM panel driver supports panels based on Ilitek ILI9882T-class controllers, plus the Tianma `tl121bvms07-00` path using an IL79900A command-page convention and DSC. It describes each panel with static mode, physical size, bpc, DSI format, lane count, mode flags, optional DSC configuration, and a dedicated init callback.

## Important APIs, Types, And Functions

- `struct panel_desc` is the per-compatible contract: mode, optional `drm_dsc_config`, dimensions, bpc, DSI flags, pixel format, init callback, and lane count.
- `struct ili9882t` holds the `drm_panel`, DSI device, descriptor, orientation, four regulators (`pp3300`, `pp1800`, `avee`, `avdd`), enable GPIO, and copied DSC config.
- `ili9882t_switch_page()` and `il79900a_switch_page()` encode the two private page-switch protocols.
- `starry_ili9882t_init()` is a large ILI9882T vendor init script ending with exit sleep and display on.
- `tianma_il79900a_init()` writes IL79900A registers, packs a DSC PPS with `drm_dsc_pps_payload_pack()`, sends the picture parameter set, enables DSI compression mode, exits sleep, and turns the display on.
- `ili9882t_prepare()` sequences rails, sends a DSI NOP to establish LP11 before reset, toggles the enable/reset line pattern, and calls the descriptor init function.
- `ili9882t_disable()` sends display off and sleep mode.
- `ili9882t_unprepare()` disables GPIO and regulators in reverse-ish power order.
- `ili9882t_probe()` copies descriptor DSI settings into `mipi_dsi_device`, installs DSC on `dsi->dsc` when present, adds the panel, and attaches to the DSI host.

## Control Flow

Probe selects either `starry,ili9882t` or `tianma,tl121bvms07-00`. The Starry path is a 1200x1920 RGB888 4-lane video-mode panel. The Tianma path is a 1600x2560 3-lane RGB888 video-mode panel using DSC 1.2 with two 800-pixel slices, 8 bpc, and packed PPS programming before compression mode is enabled.

Prepare first drives the enable GPIO low, enables `pp3300` and `pp1800`, then `avdd` and `avee`, sends a NOP to force LP11, toggles the enable GPIO low/high/low/high with delays, and invokes the selected init callback. Disable performs DCS display-off/sleep. Unprepare drops `avee`, `avdd`, `pp1800`, and `pp3300`. Mode enumeration duplicates exactly one descriptor mode and exposes size and bpc. Orientation is read from device tree and returned through `get_orientation()`.

## State And Persistence

The driver has no persistent storage. It caches only descriptor-derived state and a copied DSC configuration in memory. Panel register state is volatile and is rebuilt on every prepare. Backlight state is delegated to the DRM panel backlight integration and is not directly persisted here.

## Dependencies And Integration Points

The file depends on the DRM panel, DRM connector/mode APIs, MIPI DSI helpers, regulator and GPIO frameworks, OF orientation parsing, and DRM DSC helpers. DSC integration is an important host contract: `dsi->dsc` must be set before attach for the host to allocate and transmit the compressed stream correctly. The init paths use `mipi_dsi_multi_context` so command failures accumulate and abort prepare.

## Risks

Power sequencing is delicate because four regulators and the enable GPIO must meet panel timing requirements. The prepare error path does not disable `pp3300` when `pp1800` enable fails, and the later `poweroff1v8` path disables `pp1800` but not `pp3300`, so failures can leave the 3.3 V rail enabled. `ili9882t_disable()` always uses the ILI9882T page-switch command even for the IL79900A-compatible panel, which deserves scrutiny when changing the Tianma path. DSC parameters, slice width/count, lane count, and PPS payload must match the DSI host and panel exactly.

## Test Signals

Compile coverage should include `CONFIG_DRM_PANEL_ILITEK_ILI9882T` with DRM DSC helpers. Runtime tests should confirm all four supplies and the enable GPIO transition in the documented order, DSI attach succeeds with `dsi->dsc` populated for Tianma, the mode list contains one preferred mode, orientation is honored, and repeated blank/unblank cycles do not leave rails enabled. For Tianma, inspect host logs for DSC enable/PPS transmission and verify visual output for compression artifacts or blanking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9882t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-ej030na.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-ej030na.c

## Purpose

This is an SPI-controlled DRM panel driver for the Innolux/Chimei EJ030NA TFT LCD panel. Unlike the DSI panel drivers in this group, the panel exposes an SPI register interface for initialization and control and a DPI connector for pixel data.

## Important APIs, Types, And Functions

- `struct ej030na_info` describes the available modes, panel size, media bus format, and bus flags.
- `struct ej030na` stores the `drm_panel`, SPI device, regmap, matched panel info, `power` regulator, and reset GPIO.
- `ej030na_init_sequence` is a static `reg_sequence` table written through regmap during prepare.
- `ej030na_prepare()` enables power, pulses reset, and writes the full init sequence with `regmap_multi_reg_write()`.
- `ej030na_unprepare()` asserts reset and disables the power regulator.
- `ej030na_enable()` writes register `0x2b = 0x01` to leave standby and delays 120 ms before backlight use.
- `ej030na_disable()` writes register `0x2b = 0x00` to enter standby.
- `ej030na_get_modes()` publishes two fixed modes and sets 8 bpc, physical size, bus format, and bus flags.
- `ej030na_probe()` allocates a DPI panel, initializes SPI regmap, gets regulator/GPIO/backlight, and adds the panel.

## Control Flow

The SPI driver matches `innolux,ej030na`. Probe builds an 8-bit register/8-bit value regmap over SPI and stores static panel info from match data. Prepare powers and resets the panel before programming the register table. Enable and disable only toggle standby through register `0x2b`; backlight is handled by the panel framework after the prepare/enable callbacks. Removal unregisters the panel and explicitly calls disable and unprepare.

The mode list contains 320x480 timings at 60 Hz and 50 Hz. Because two modes are exposed, neither path marks the mode preferred through the single-mode shortcut. The connector is configured for `MEDIA_BUS_FMT_RGB888_3X8_DELTA`, positive-edge pixel sampling, and active-low data-enable.

## State And Persistence

The driver keeps only volatile kernel object state. Hardware register state is reloaded on every prepare. There is no EDID, persistent brightness storage, or dynamic mode detection. Standby state is represented only by the panel callbacks and register `0x2b`.

## Dependencies And Integration Points

Integration points are the SPI bus, regmap SPI backend, regulator framework, reset GPIO, DRM panel API, optional OF backlight, Linux media bus format definitions, and DPI connector bus flags. The display controller that consumes this panel must honor the RGB888 delta bus format and DE/pixel-clock flags.

## Risks

Failures in `ej030na_enable()` and `ej030na_disable()` ignore `regmap_write()` return values, so standby transitions can silently fail. The driver depends on exact bus flags and timing values for a DPI panel; mismatches may look like shifted image, wrong colors, or no sync. The removal path calls disable/unprepare after `drm_panel_remove()`, which is common in older panel drivers but should be considered when refactoring lifecycle behavior. Multi-mode exposure without a preferred bit may leave mode choice to userspace policy.

## Test Signals

Check SPI probe and regmap initialization, successful acquisition of the `power` regulator and `reset` GPIO, full init table write success, correct standby writes on enable/disable, and both 320x480 modes in connector probing. Hardware validation should inspect RGB bus polarity, colors, frame stability at both refresh rates, and backlight delay behavior after exiting standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-ej030na.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-p079zca.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-p079zca.c

## Purpose

This DRM MIPI DSI panel driver covers Innolux `p079zca` and `p097pfg` style panels. It uses a descriptor table to support one simpler 768x1024 panel and one higher-resolution 1536x2048 panel with a long vendor register initialization sequence derived from a working register dump.

## Important APIs, Types, And Functions

- `struct panel_desc` stores the fixed mode, bpc, physical size, DSI flags/format/lane count, optional init callback, regulator names, and power-down delays.
- `struct innolux_panel` stores the `drm_panel`, DSI link, descriptor, regulator bulk array, and optional enable GPIO.
- `innolux_panel_prepare()` enables supplies, toggles enable GPIO, runs the descriptor init callback when present, exits sleep mode, waits 120 ms, and sets display on.
- `innolux_panel_unprepare()` sends display off and sleep mode, waits descriptor-specific delays, deasserts enable, and disables regulators.
- `innolux_panel_write_multi()` wraps generic DSI writes and adds a DCS NOP after each write because the panel sometimes missed commands without an inter-command delay or transaction.
- `innolux_p097pfg_init()` sends multiple command pages of power, gamma, mapping, and timing register values.
- `innolux_panel_probe()` applies descriptor DSI settings, adds the panel, and attaches to the DSI host.

## Control Flow

OF match data selects `innolux,p079zca` or `innolux,p097pfg`. The p079zca descriptor has one `power` regulator, no custom init callback, a 768x1024 mode, 4 RGB888 DSI lanes, and an 80 ms power-down delay. The p097pfg descriptor has `avdd` and `avee` regulators, a 1536x2048 mode, a large init script, and a 100 ms sleep-mode delay.

Prepare starts from enable GPIO low, turns on all descriptor supplies, waits about 20 ms, sets enable high, waits again, runs optional init, exits sleep, waits 120 ms, and turns the display on. On failure it drops enable and regulators. Unprepare sends DCS display-off and enter-sleep before powerdown. `get_modes()` exposes one preferred mode by duplicating descriptor timing and setting physical size and bpc.

## State And Persistence

No persistent or discovered state is used. The descriptor and resource handles are the only software state. The panel's volatile vendor registers are programmed at prepare time for the p097pfg and otherwise rely on panel defaults plus standard DCS sleep/display commands.

## Dependencies And Integration Points

The driver integrates with DRM panel, MIPI DSI, OF matching, regulator bulk APIs, optional enable GPIO, and optional panel backlight. It depends on a DSI host that supports 4-lane RGB888 video mode with sync pulse and low-power command transfers (`MIPI_DSI_MODE_LPM`).

## Risks

The p097pfg init sequence is explicitly documented as coming from a register dump rather than manufacturer sequencing, so it is high-risk for undocumented panel revisions. `innolux_panel_write_multi()` adds a NOP after each command based on empirical behavior; removing it may reintroduce intermittent missed commands. Optional enable GPIO errors are downgraded to debug and then ignored by setting the pointer to NULL, which is fine for optional wiring but can mask DT mistakes if a board actually requires enable. Timing values are shared/commented across panel variants and should be validated per datasheet or hardware.

## Test Signals

Confirm DSI attach, correct regulator names per compatible, the optional enable GPIO behavior, and one preferred mode with expected dimensions. On p097pfg hardware, repeated cold boot and resume cycles should verify that the entire page-switch init script is accepted with no blank panel or partial gamma/mapping failure. For p079zca, verify standard sleep/display commands are sufficient without vendor init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-p079zca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jadard-jd9365da-h3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jadard-jd9365da-h3.c

## Purpose

This DRM MIPI DSI panel driver supports several panels using the Jadard JD9365DA-H3 controller family. It is descriptor-driven: each compatible supplies a fixed mode, lane count, DSI format, init callback, optional timing quirks for LP11/reset/powerdown, and optional mode flags.

## Important APIs, Types, And Functions

- `struct jadard_panel_desc` contains the fixed mode, lane/format settings, init callback, LP11/reset/powerdown timing quirks, and DSI mode flags.
- `struct jadard` stores the `drm_panel`, DSI device, descriptor, orientation, `vdd` and `vccio` regulators, and reset GPIO.
- `jd9365da_switch_page()` writes the controller page select command `0xe0`.
- `jadard_enable_standard_cmds()` unlocks or enables standard command access using `0xe1`, `0xe2`, `0xe3`, and `0x80`.
- `jadard_prepare()` enables regulators, optionally sends LP11 NOP before reset, toggles reset, waits for panel readiness, and runs the selected init callback.
- `jadard_disable()` sends display off and sleep mode with descriptor-configured delays around those transitions.
- `jadard_unprepare()` controls reset and disables `vdd` and `vccio`, optionally asserting reset before power-off for selected panels.
- Panel init callbacks such as `radxa_display_8hd_ad002_init_cmds()`, `cz101b4001_init_cmds()`, `kingdisplay_kd101ne3_init_cmds()`, `melfas_lmfbx101117480_init_cmds()`, `anbernic_rgds_init_cmds()`, and `taiguan_xti05101_01a_init_cmds()` encode long page-based vendor scripts.

## Control Flow

Probe matches compatibles including `anbernic,rg-ds-display-bottom`, `anbernic,rg-ds-display-top`, `chongzhou,cz101b4001`, `kingdisplay,kd101ne3-40ti`, `melfas,lmfbx101117480`, `radxa,display-10hd-ad001`, `radxa,display-8hd-ad002`, and `taiguanck,xti05101-01a`. If a descriptor does not provide DSI mode flags, the default is video burst with no EOT packet. The driver reads panel orientation from DT, registers optional backlight handling, adds the panel, and attaches to the DSI host.

Most descriptors are 800x1280 4-lane RGB888 panels with different sizes and register scripts. The Anbernic descriptor is a 640x480 panel with negative sync flags and non-continuous clock/LPM DSI flags. The Anbernic init path branches on whether the top or bottom compatible is used, changing at least one vendor register value. The disable/unprepare split means display-off/sleep happens in `.disable`, while reset and regulator shutdown happen in `.unprepare`.

## State And Persistence

There is no persistent storage. The driver caches descriptor selection, orientation, and resource handles. All panel controller state is volatile and reloaded from the init callback during prepare. Compatible-specific behavior is encoded in device tree match data and, for Anbernic, a runtime compatible check against the panel node.

## Dependencies And Integration Points

The file depends on DRM panel, MIPI DSI multi-context helpers, DT OF matching/orientation, regulator framework, reset GPIO, and optional backlight. It integrates with the connector through `get_modes()` and `get_orientation()`. The DSI host must support command-mode writes during prepare and the selected video-mode flags during scanout.

## Risks

There is a power-leak risk in `jadard_prepare()`: if enabling `vdd` fails after `vccio` succeeds, or if LP11 NOP/init fails after regulators are enabled, the function returns without disabling previously enabled rails. The long vendor scripts are opaque and panel-revision sensitive. Some timing quirks are descriptor-specific; applying one descriptor to a board with different reset or LP11 requirements can cause intermittent boot failures. Since `.disable` returns accumulated DSI errors but `.unprepare` always powers down, callers may see command failures only during the disable stage.

## Test Signals

Tests should verify OF match selection, DSI lane/mode-flag assignment, regulator and reset sequencing, and the single preferred mode's timing and physical size. Hardware validation should exercise cold boot, display blank/unblank, suspend/resume, and both Anbernic top/bottom compatibles. Logs should be checked for DSI command errors from multi-context accumulation, especially around display off, sleep mode, and long init scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jadard-jd9365da-h3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-fhd-r63452.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-fhd-r63452.c

## Purpose

This is a DRM MIPI DSI panel driver for a JDI FHD R63452 command-mode panel. It was generated from downstream Android panel data and exposes one fixed 1080x1920 mode.

## Important APIs, Types, And Functions

- `struct jdi_fhd_r63452` stores the `drm_panel`, DSI device, and reset GPIO.
- `jdi_fhd_r63452_reset()` performs the reset GPIO low/high/low pulse sequence.
- `jdi_fhd_r63452_on()` switches the DSI link to low-power command mode and sends the panel init sequence, including TE enable, address mode, pixel format, column/page address, brightness/control-display/power-save settings, display on, sleep exit, and extra vendor page writes.
- `jdi_fhd_r63452_off()` clears LPM, sends vendor setup, display off, sleep mode, and a 120 ms delay.
- `jdi_fhd_r63452_prepare()` resets the panel and calls the on sequence.
- `jdi_fhd_r63452_unprepare()` calls off and asserts reset, deliberately returning success even if off commands failed.
- `jdi_fhd_r63452_get_modes()` exposes the fixed preferred 1080x1920 mode and physical size.
- `jdi_fhd_r63452_probe()` gets reset GPIO, configures 4-lane RGB888 DSI video burst with non-continuous clock, sets `prepare_prev_first`, finds backlight, adds the panel, and attaches.

## Control Flow

The DSI driver matches `jdi,fhd-r63452`. Probe configures DSI format and mode flags, then registers the panel. Prepare only controls reset and DCS/vendor command setup; there are no regulators in this driver, so board power must be handled elsewhere or by the DSI host/PM topology. Unprepare attempts a clean display-off/sleep transition, then asserts reset regardless.

The fixed mode computes the pixel clock from 1080 horizontal active plus porch/sync values and 1920 vertical active plus porch/sync values at 60 Hz. Mode enumeration marks it driver and preferred and sets 64 mm by 114 mm display size.

## State And Persistence

The driver keeps no persistent state and performs no panel reads except through DSI helper side effects. Brightness is programmed to `0x00ff` during init, but ongoing backlight policy is external through `drm_panel_of_backlight()`. The panel's register state is volatile and recreated on prepare.

## Dependencies And Integration Points

Dependencies are DRM panel, MIPI DSI DCS/generic helpers, reset GPIO, DT OF matching, and optional OF backlight. The source comment points to generated downstream LineageOS panel data, making the init sequence an imported hardware contract rather than self-describing logic.

## Risks

The driver has no regulator handling, so integration depends on board-level power being enabled before prepare. `jdi_fhd_r63452_off()` ignores `dsi_ctx.accum_err`; this is intentional in unprepare but can hide DSI shutdown failures. The on sequence sets display on before exit sleep, which is unusual compared with many DCS panels and should not be reordered without hardware evidence. Toggling `dsi->mode_flags` LPM bits inside on/off can interact with host expectations.

## Test Signals

Check successful DSI attach, reset pulse timing, one preferred 1080x1920 mode, backlight lookup, and clean repeated prepare/unprepare. Hardware should verify TE behavior, brightness/control-display operation, no address-window clipping, and that resume works despite the command order inherited from downstream data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-fhd-r63452.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-lpm102a188a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-lpm102a188a.c

## Purpose

This DRM driver supports the JDI LPM102A188A command-mode panel used as a dual-link MIPI DSI display. It registers a DRM panel only for the primary DSI link and uses a `link2` phandle to find and control the secondary DSI device.

## Important APIs, Types, And Functions

- `struct jdi_panel` stores the panel, primary and secondary DSI links, `power` and `ddi` regulators, backlight, enable/reset GPIOs, and fixed mode pointer.
- `jdi_wait_frames()` converts a frame count to a delay using the fixed mode refresh rate.
- `jdi_panel_prepare()` disables backlight, enables both DSI links in LPM, powers `power` then `ddi`, asserts enable/reset sequencing, configures split addressing and TE/pixel format on both links, exits sleep on both links, writes DCDC registers, waits 150 ms, and turns both halves on.
- `jdi_setup_symmetrical_split()` programs both DSI devices for a left/right split with column range `0..hdisplay/2-1` and full vertical range.
- `jdi_write_dcdc_registers()` unlocks manufacturer commands and changes VGH/VGL divider ratios on both links.
- `jdi_panel_unprepare()` sends display off and sleep mode to both links with independent error contexts, then resets and powers down.
- `jdi_panel_dsi_probe()` attaches each DSI interface, but allocates/adds the DRM panel only when the secondary link is found from the primary node.
- `jdi_panel_dsi_remove()` treats a DSI instance without panel drvdata as the secondary link and only detaches it.

## Control Flow

Both DSI devices match `jdi,lpm102a188a`. Each probe sets 4 lanes, RGB888 format, and zero initial mode flags. On the node with a `link2` phandle, the driver finds the secondary DSI device, allocates the panel, records `link1` and `link2`, gets regulators/GPIO/backlight, and adds the panel. It then attaches the current DSI device. On the secondary interface, no panel is registered; the device simply attaches and later detaches.

Prepare is dual-link from the start: command helpers such as `mipi_dsi_dual()` and `mipi_dsi_dual_generic_write_seq_multi()` target both links. The driver currently supports only a symmetrical left-right split. Enable waits for image data to flow before enabling backlight. Disable turns the backlight off and waits two frames before command shutdown.

## State And Persistence

No persistent state exists. The panel mode is a fixed 2560x1800 60 Hz timing with 211 mm by 148 mm physical size and 8 bpc. The driver holds a device reference to `link2` until panel deletion. Panel and DCDC state are volatile and reprogrammed on prepare.

## Dependencies And Integration Points

The driver integrates with DRM panel, dual-link MIPI DSI helper APIs, OF phandle lookup, regulator framework, GPIO descriptors, and backlight lookup through `devm_of_find_backlight()`. It relies on the DSI host and device tree representing both links correctly. The TODO notes a host/panel contract gap for even-odd split modes: only left-right split is currently supported.

## Risks

Dual-link probe ordering can defer until the secondary DSI device exists. Misconfigured `link2` phandles, missing secondary attach, or host split assumptions will produce half-screen or no-screen failures. `jdi_panel_prepare()` uses a shared multi-context for many dual commands, so one half's failure can abort the whole sequence after power rails are already enabled; the poweroff path handles regulators but does not explicitly lower GPIOs in every failure branch. DCDC divider changes are hardware-specific and may interact with backlight noise differently on board revisions.

## Test Signals

Validate both DSI devices probe and attach, the primary node finds `link2`, only one DRM panel is registered, and both links receive DCS commands during prepare/unprepare. Hardware tests should check full-width image alignment, no left/right swap, TE behavior, backlight blanking before power transitions, suspend/resume, and absence of backlight noise after DCDC register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-lpm102a188a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-lt070me05000.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-lt070me05000.c

## Purpose

This DRM MIPI DSI driver supports the JDI LT070ME05000 WUXGA panel. It includes panel power sequencing, DCS initialization, and an internally registered DSI DCS backlight device.

## Important APIs, Types, And Functions

- `struct jdi_panel` stores the panel, DSI device, two bulk regulators (`vddp`, `iovcc`), enable/reset/DCDC GPIOs, DCS backlight device, and fixed mode pointer.
- `jdi_panel_init()` enters low-power command mode, sends soft reset, sets 24-bit pixel format, programs column/page address windows, enables DCS backlight control, disables CABC, exits sleep, and writes vendor interface/video-mode settings.
- `jdi_panel_on()` sends DCS display on.
- `jdi_panel_off()` clears LPM, sends display off, resets accumulated error, enters sleep, and waits 100 ms.
- `jdi_panel_prepare()` enables regulators, sequences DCDC/reset/enable GPIOs, runs init, and turns the panel on.
- `jdi_panel_unprepare()` powers down by sending panel off, disabling regulators, and lowering GPIOs.
- `dsi_dcs_bl_get_brightness()` and `dsi_dcs_bl_update_status()` implement raw backlight operations using DCS brightness get/set.
- `drm_panel_create_dsi_backlight()` registers the DSI backlight with max/default brightness 255.

## Control Flow

Probe matches `jdi,lt070me05000`, configures DSI for 4-lane RGB888 video mode with HSE and non-continuous clock, allocates the panel, gets regulators and GPIOs, creates the DCS backlight, adds the panel, and attaches to the DSI host. Prepare enables supplies, waits 20 ms, enables DCDC, releases reset, enables the panel, runs the DCS init script, and turns display on. Enable/disable only manage the backlight. Unprepare performs DCS sleep then drops supplies and GPIOs.

The fixed display mode is 1200x1920 with a 155493 kHz pixel clock and physical size 95 mm by 151 mm. `get_modes()` duplicates that mode into the connector but does not set bpc.

## State And Persistence

No persistent storage is used. Brightness is held by the Linux backlight core and written to the panel via DCS; reading brightness asks the panel using `mipi_dsi_dcs_get_display_brightness()`. Panel configuration and address windows are volatile and reinitialized on prepare.

## Dependencies And Integration Points

The file depends on DRM panel and MIPI DSI helpers, regulator bulk APIs, GPIO descriptors, and the backlight subsystem. Unlike drivers that use `drm_panel_of_backlight()`, this one creates its own DCS backlight device. The display pipeline must support the configured video-mode flags and 4-lane RGB888 stream.

## Risks

The prepare error path overwrites the original init/on failure code with the return value from `regulator_bulk_disable()` if regulator disable succeeds, causing a failed init to potentially return 0. Brightness get/set temporarily clear LPM and then set it again, which can race conceptually with other DSI mode-flag users if brightness operations happen during panel transitions. `jdi_panel_off()` intentionally resets accumulated DSI errors before sleep so shutdown continues, but that hides display-off failures. Very short GPIO delays of 10-20 microseconds should be verified against board requirements.

## Test Signals

Tests should check regulator bulk names, GPIO sequencing, DSI attach, one 1200x1920 mode, DCS backlight registration, brightness read/write, and repeated enable/disable/prepare/unprepare cycles. Hardware validation should confirm color format, address window coverage, CABC off behavior, no random pixels before backlight enable, and correct failure reporting from prepare after any future error-path fix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-lt070me05000.c -->
