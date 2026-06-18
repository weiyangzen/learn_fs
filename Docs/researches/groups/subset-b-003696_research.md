# Research group subset-b-003696

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-nl6.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-nl6.c

### Purpose

`panel-boe-tv101wum-nl6.c` is a MIPI-DSI DRM panel driver for a family of 10.1-11 inch 1200x1920 or 1200x2000 video-mode panels using related BOE, AUO, Innolux, and Starry modules. The file is table driven: each compatible selects a `panel_desc` that supplies the display mode, DSI lane/format/mode flags, physical size, bpc, power sequencing quirks, and a panel-specific DCS initialization routine.

### Important APIs, types, and functions

The central types are `struct panel_desc` and `struct boe_panel`. `panel_desc` stores the fixed `drm_display_mode`, DSI bus parameters, init callback, and quirks such as `discharge_on_disable` and `lp11_before_reset`. `boe_panel` holds the `drm_panel`, DSI device, orientation, four regulators (`pp3300`, `pp1800`, `avdd`, `avee`), and the enable/reset GPIO.

Panel-specific init functions include `boe_tv110c9m_init()`, `inx_hj110iz_init()`, `boe_init()`, `auo_kd101n80_45na_init()`, `auo_b101uan08_3_init()`, and `starry_qfh032011_53g_init()`. `boe_init()` is the common long register sequence used by the BOE TV101WUM variants. The DRM callbacks are `boe_panel_prepare()`, `boe_panel_enable()`, `boe_panel_disable()`, `boe_panel_unprepare()`, `boe_panel_get_modes()`, and `boe_panel_get_orientation()`. Device registration is handled by `boe_panel_probe()`, `boe_panel_add()`, `boe_panel_remove()`, and `module_mipi_dsi_driver()`.

### Control flow

Probe allocates the `boe_panel`, reads match data from `boe_of_match`, applies DSI lane/format/mode flags from the descriptor, obtains the four regulators, gets the `enable` GPIO, reads panel orientation, registers optional backlight support, adds the DRM panel, and attaches to the DSI host. `prepare()` powers rails in order (`pp3300`, `pp1800`, `avdd`, `avee`), optionally sends a DSI NOP before reset to force LP11, toggles the enable GPIO through the panel reset sequence, then calls the descriptor-specific init callback. The init callbacks write vendor command pages, gamma tables, GOA/source timing values, sleep-out/display-on commands, or simple `0x11`/`0x29` sequences depending on the panel. `enable()` only waits 130 ms after init; the panel is already commanded on by the init path. `disable()` sends display-off and sleep-in around LPM flag handling, and `unprepare()` turns off GPIO and rails with either normal or discharge-oriented ordering.

### State and persistence behavior

Runtime state is device-local and not persisted outside the kernel object. The selected descriptor is immutable match data. Power state is represented implicitly by the regulator/GPIO state and DRM panel prepare/enable lifecycle rather than by explicit booleans. Orientation comes from device tree and is returned through both `get_orientation()` and the legacy connector orientation call in `get_modes()`. DSI mode flags are mutated during disable to leave low-power mode enabled after sleep-in. The long vendor register sequences program panel IC state until the next reset or power loss.

### Dependencies

The driver depends on DRM panel and connector helpers, MIPI DSI DCS helpers including `mipi_dsi_multi_context`, OF match data, regulator and GPIO consumer APIs, `drm_panel_of_backlight()`, and `of_drm_get_panel_orientation()`. It integrates with the MIPI DSI bus through `struct mipi_dsi_driver` and with the DRM display pipeline through `struct drm_panel_funcs`.

### Integration points

Supported compatibles are `boe,tv101wum-nl6`, `auo,kd101n80-45na`, `boe,tv101wum-n53`, `auo,b101uan08.3`, `boe,tv105wum-nw0`, `boe,tv110c9m-ll3`, `innolux,hj110iz-01a`, and `starry,2081101qfh032011-53g`. Board DTS must provide the named regulators, enable GPIO, optional backlight, and orientation. The DSI host uses descriptor-supplied video-mode flags, usually four lanes and RGB888. Connectors receive one fixed preferred mode plus physical size and bpc.

### Risks

The highest risk is sequencing: panel rails, LP11-before-reset, reset timing, and discharge ordering are panel-specific and easy to break when adding variants. Error unwinding in `boe_panel_prepare()` disables `avee`, `avdd`, and `pp1800` but does not disable `pp3300`, so failures after the first rail may leave one supply enabled until later cleanup. Init callbacks return `0` directly instead of `ctx.accum_err`, so accumulated DSI write failures are not propagated for these sequences. The descriptor table must stay consistent with DSI host capabilities, because wrong mode flags, lane count, or timings can produce blank panels or unstable links.

### Test signals

Useful validation includes kernel build coverage with `CONFIG_DRM_PANEL_BOE_TV101WUM_NL6`, probe/remove on each compatible, regulator/GPIO trace checks for prepare and unprepare order, DSI host logs for attach and command failures, visual bring-up through sleep-out/display-on, suspend/resume and blank/unblank cycles, orientation reporting, backlight binding, and mode enumeration confirming the expected resolution, bpc, and physical dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-nl6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-dsi-cm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-dsi-cm.c

### Purpose

`panel-dsi-cm.c` implements a generic MIPI-DSI command-mode panel driver for older mobile/tablet panels such as TPO Taal, Nokia Himalaya, and Motorola Droid 4. It handles DCS sleep/display sequencing, optional DSI-native backlight control, external backlight integration, basic sysfs diagnostics, fixed command-mode geometry, and TE enablement for panels that support tearing-effect synchronization.

### Important APIs, types, and functions

`struct dsic_panel_data` describes per-compatible geometry, refresh, physical size, DSI high-speed/low-power rates, and TE support. `struct panel_drv_data` holds the DSI device, `drm_panel`, synthesized `drm_display_mode`, mutex, optional native and external backlight devices, guard timing fields, reset GPIO, two regulators (`vpnl`, `vddi`), and runtime flags such as `enabled` and `intro_printed`.

Core helpers include `dsicm_bl_power()`, `hw_guard_start()`, `hw_guard_wait()`, `dsicm_dcs_read_1()`, `dsicm_dcs_write_1()`, `dsicm_sleep_in()`, `dsicm_sleep_out()`, `dsicm_get_id()`, and `dsicm_set_update_window()`. DRM panel callbacks are `dsicm_prepare()`, `dsicm_enable()`, `dsicm_disable()`, `dsicm_unprepare()`, and `dsicm_get_modes()`. Sysfs attributes are implemented by `num_dsi_errors_show()` and `hw_revision_show()`. Backlight callbacks are `dsicm_bl_update_status()` and `dsicm_bl_get_intensity()`.

### Control flow

Probe allocates panel state, reads compatible match data, gets the reset GPIO, creates the fixed mode from `dsic_panel_data`, obtains the `vpnl` and `vddi` supplies, locates an external backlight or registers a DSI backlight, performs an early hardware reset, creates sysfs files, sets DSI lanes/format/rates/mode flags, adds the panel, and attaches the DSI host. `prepare()` only enables regulators. `enable()` takes the mutex and calls `dsicm_power_on()`: reset, force low-power mode, exit sleep with guard timing, read ID registers, set brightness/control display/pixel format/update window, set display on, optionally enable TE, wait for a panel quirk, mark enabled, print the revision once, and clear low-power mode. Backlight power is enabled after the panel is on. Disable reverses this by disabling backlight, taking the lock, sending display-off and sleep-in, and marking disabled. Unprepare disables supplies.

### State and persistence behavior

`enabled` gates sysfs reads and DSI brightness writes, preventing diagnostics or brightness updates while the panel is off. `hw_guard_end` and `hw_guard_wait` persist across sleep-in/sleep-out calls to enforce the DCS 120 ms guard interval. `intro_printed` suppresses repeated panel revision logs after the first successful enable. The mode is synthesized once at probe and kept in `ddata->mode`. External backlight device references are held until remove and released with `put_device()`.

### Dependencies

The file depends on DRM panel, connector, and mode helpers; MIPI DSI DCS read/write helpers; Linux backlight, GPIO, regulator, jiffies, and sysfs APIs; and OF match data. It uses `devm_of_find_backlight()` for an external backlight and `devm_backlight_device_register()` for native DSI brightness control.

### Integration points

The compatible table maps `tpo,taal`, `nokia,himalaya`, and `motorola,droid4-panel` to fixed panel data. Board DTS must expose `reset`, `vpnl`, `vddi`, and optionally a backlight. Runtime sysfs files under the device expose DSI error count and hardware revision while enabled. The DSI host receives two-lane RGB888 configuration, non-continuous clock, no-EOT packet mode, and per-panel HS/LP rate caps.

### Risks

This driver talks to powered-on panels through DCS reads and writes under a mutex, so missing `enabled` checks or lock coverage can trigger bus errors during suspend or disable. The hardware guard math uses jiffies subtraction and assumes calls are not delayed beyond the guard window. `dsicm_power_on()` resets the panel on command failure but leaves regulator state to higher layers. Native backlight writes are ignored while disabled, so brightness state can diverge from panel hardware until the next enable. The OF match entry for `nokia,himalaya` relies on positional initializer syntax for `.data`, which is valid but easy to misread.

### Test signals

Test with `CONFIG_DRM_PANEL_DSI_CM`, panel probe/attach for all compatibles, sysfs reads while enabled and disabled, native DSI backlight brightness changes, external backlight reference cleanup, TE enable on Taal, repeated enable/disable with sleep guard tracing, DSI error-count reads, and suspend/resume cycles that verify regulator and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-dsi-cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ebbg-ft8719.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ebbg-ft8719.c

### Purpose

`panel-ebbg-ft8719.c` is a compact DRM/MIPI-DSI panel driver for EBBG FT8719 video-mode panels. It provides the FT8719 reset and power sequence, sends a short DCS initialization sequence for brightness/control/power-save/sleep/display state, exposes one fixed 1080x2246 preferred mode, and binds optional backlight support through the DRM panel framework.

### Important APIs, types, and functions

`struct ebbg_ft8719` stores the `drm_panel`, DSI device, three regulator bulk supplies, and reset GPIO. `regulator_names` names `vddio`, `vddpos`, and `vddneg`; `regulator_enable_loads` applies expected regulator loads during probe. Key helpers are `ebbg_ft8719_reset()`, `ebbg_ft8719_on()`, and `ebbg_ft8719_off()`. DRM panel callbacks are `ebbg_ft8719_prepare()`, `ebbg_ft8719_unprepare()`, and `ebbg_ft8719_get_modes()`. Bus integration uses `ebbg_ft8719_probe()`, `ebbg_ft8719_remove()`, `ebbg_ft8719_of_match`, and `module_mipi_dsi_driver()`.

### Control flow

Probe allocates managed panel state, fills regulator bulk entries, obtains regulators, sets load values for each rail, acquires an active-low-style reset GPIO initially high, sets DSI data, applies four-lane RGB888 video burst non-continuous clock mode, binds optional backlight, adds the panel, and attaches the DSI host. `prepare()` enables all supplies, pulses reset low-high-low with panel-specific delays, and calls `ebbg_ft8719_on()`. The on sequence forces LPM, writes brightness `0x00ff`, control-display `0x24`, power-save `0x00`, exits sleep, waits 90 ms, and turns display on. `unprepare()` calls `ebbg_ft8719_off()`, asserts reset, and disables supplies. The off path clears LPM, sends display-off, waits, sends sleep-in, and waits 90 ms.

### State and persistence behavior

The driver has no explicit prepared/enabled flags; state follows the DRM panel lifecycle and hardware rails. DSI `mode_flags` are modified at runtime to use LPM for initialization and not for display-off/sleep-in commands. Regulator load settings persist while regulator consumers exist. Panel register state is volatile and reprogrammed on every prepare. The fixed display mode is static data.

### Dependencies

Dependencies are DRM panel/mode helpers, MIPI DSI DCS multi-context helpers, regulator bulk APIs, GPIO consumer APIs, OF matching, `drm_panel_of_backlight()`, and standard module registration. The driver expects a DSI host capable of four-lane RGB888 video burst with non-continuous clock.

### Integration points

The sole compatible is `ebbg,ft8719`. DTS must provide `vddio`, `vddpos`, `vddneg`, `reset-gpios`, and optional backlight. The connector gets one preferred mode with 1080x2246 timing and 68 mm by 141 mm dimensions. Runtime integration is the normal DRM bridge/panel prepare, unprepare, and mode enumeration path.

### Risks

Error handling in `prepare()` returns immediately if `ebbg_ft8719_on()` fails after supplies are enabled, only asserting reset and not disabling regulators, leaving cleanup to later unprepare or device removal. `unprepare()` ignores errors from `ebbg_ft8719_off()`. Toggling `mode_flags` inside power callbacks assumes no concurrent DSI transfer users. Regulator load values must match board power constraints. Reset polarity/timing mismatches can leave the panel unresponsive.

### Test signals

Validate build, probe with `ebbg,ft8719`, regulator load acceptance, DSI attach, reset waveform, successful DCS multi-context command completion, mode enumeration, backlight binding, repeated prepare/unprepare cycles, suspend/resume, and visual confirmation that brightness/control-display programming enables expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ebbg-ft8719.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-edp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-edp.c

### Purpose

`panel-edp.c` is the generic DRM driver for simple embedded DisplayPort panels. It covers both statically described eDP panels and generic `edp-panel` devices discovered through EDID over AUX/DDC. The file owns eDP power sequencing delays, HPD waiting, runtime PM based prepare/unprepare, EDID mode enumeration, fixed-mode/timing fallbacks, DP AUX backlight registration, debugfs reporting of detected panel identity, and a large table of known EDID panel IDs mapped to safe delay profiles.

### Important APIs, types, and functions

`struct panel_delay` describes eDP timing requirements such as HPD reliability, HPD absent fallback, powered-on-to-enable, prepare-to-enable, enable, disable, and unprepare delays. `struct panel_desc` stores hard-coded modes or timings, bpc, size, and delays. `struct edp_panel_entry` maps `drm_edid_ident` values to delay profiles and optional EDID mode overrides. `struct panel_edp` stores DRM panel state, HPD/no-HPD flags, timestamps, descriptor, regulator, DDC or AUX handles, GPIOs, detected panel entry, cached EDID, override mode, and orientation.

Core functions include `panel_edp_get_modes()`, `panel_edp_get_non_edid_modes()`, `panel_edp_prepare_once()`, `panel_edp_resume()`, `panel_edp_suspend()`, `panel_edp_prepare()`, `panel_edp_enable()`, `panel_edp_disable()`, `panel_edp_unprepare()`, `panel_edp_parse_panel_timing_node()`, `generic_edp_panel_probe()`, `find_edp_panel()`, `panel_edp_probe()`, `panel_edp_remove()`, and `panel_edp_shutdown()`. Registration uses both a `platform_driver` and a `dp_aux_ep_driver`.

### Control flow

Probe allocates a panel, records the descriptor and optional AUX endpoint, reads `no-hpd`, HPD GPIO, power regulator, enable GPIO, orientation, and DDC source, parses a `panel-timing` override when applicable, initializes backlight handling, enables runtime PM/autosuspend, and either uses fixed descriptor data or powers the generic panel briefly to read EDID and infer delay data. Generic EDID probing reads `hpd-reliable-delay-ms` and `hpd-absent-delay-ms`, powers the panel via runtime resume, reads the EDID base block, finds a known entry, or falls back to conservative timings.

`prepare()` is runtime-PM get; resume calls `panel_edp_prepare_once()` up to five times on HPD timeout. That function enforces the previous unprepare delay, enables the supply, asserts enable GPIO, powers DPCD, waits for HPD reliability/absence timing, optionally polls HPD through GPIO or AUX, and records prepare and power-on timestamps. `enable()` enforces fixed enable, prepare-to-enable, and powered-on-to-enable delays before backlight use. `get_modes()` reads EDID if DDC is available, adds EDID or override EDID modes unless hard-coded modes exist, then adds fixed timings/modes when present.

### State and persistence behavior

The driver persists timestamp state across lifecycle calls to enforce minimum power-cycle intervals. Runtime PM keeps slow power operations off the direct panel callback path and autosuspends after transient EDID reads. `drm_edid` is cached after the first read. `detected_panel` records known, hardcoded, or unknown/conservative detection state and is exposed through debugfs. `override_mode` is populated only if a device-tree timing fits descriptor bounds. No user data is persisted; all state is per-device kernel memory.

### Dependencies

Dependencies include DRM panel/mode/EDID helpers, DP AUX helpers, `drm_dp_dpcd_set_powered()`, DP AUX bus endpoint registration, Linux runtime PM, debugfs, regulators, GPIOs, I2C adapters, OF display timing parsing, `readx_poll_timeout()`, and videomode conversion. The driver is tightly coupled to DT bindings for simple eDP panels and to EDID identity helpers.

### Integration points

Static compatibles in `platform_of_match` select hard-coded panel descriptors. The generic `edp-panel` compatible is only supported through the DP AUX bus path, while static panels can be platform devices. DDC can come from `ddc-i2c-bus` or AUX. DP AUX backlight registration is attempted when no backlight was provided and AUX exists. Debugfs exposes `detected_panel`, and connector setup receives EDID modes, fallback modes, bpc, size, and orientation.

### Risks

Power sequencing is the main risk: inaccurate delay table entries can cause intermittent panel bring-up, backlight-before-video artifacts, or HPD timeouts. Generic unknown panels fall back to conservative delays, which is safe but slow and intentionally noisy. EDID reads require temporarily powering the panel, so runtime PM and DDC/AUX lifetime ordering must be correct. The known-panel table must be sorted by vendor and product ID for maintainability, and duplicate panel IDs are resolved with identity matching first. `panel_edp_prepare()` must balance runtime PM get/put paths on errors. Hard-coded modes and EDID modes are deliberately not both exposed as preferred modes.

### Test signals

Test static-panel probe, generic `edp-panel` AUX probe, EDID detection for known and unknown IDs, HPD GPIO and AUX HPD paths, `no-hpd` behavior, retry-on-timeout, runtime autosuspend after mode reads, DP AUX backlight registration, debugfs `detected_panel`, device-tree timing override validation, suspend/resume through runtime and system PM, and connector mode lists with EDID-only, fixed-only, and override-EDID cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-edp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-elida-kd35t133.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-elida-kd35t133.c

### Purpose

`panel-elida-kd35t133.c` is a MIPI-DSI DRM panel driver for the Elida KD35T133 3.5 inch display. It performs a vendor-supplied initialization sequence for gamma, power, VCOM, pixel format, inversion, and display control, exposes a 320x480 preferred mode, handles two regulators and an optional reset GPIO, and reports panel orientation from device tree.

### Important APIs, types, and functions

The main state type is `struct kd35t133`, containing the device pointer, `drm_panel`, reset GPIO, `vdd` and `iovcc` regulators, and `enum drm_panel_orientation`. Command constants define manufacturer-specific DSI registers such as `KD35T133_CMD_POSITIVEGAMMA`, `KD35T133_CMD_POWERCONTROL1`, `KD35T133_CMD_VCOMCONTROL`, and `KD35T133_CMD_ADJUSTCONTROL3`. `kd35t133_init_sequence()` sends the vendor register table. DRM panel callbacks are `kd35t133_prepare()`, `kd35t133_unprepare()`, `kd35t133_get_modes()`, and `kd35t133_get_orientation()`. Probe/remove are `kd35t133_probe()` and `kd35t133_remove()`.

### Control flow

Probe allocates panel state, gets optional reset GPIO initially low, obtains `vdd` and `iovcc`, reads required panel orientation, sets DSI drvdata, configures one-lane RGB888 video burst low-power/no-EOT/non-continuous-clock mode, binds optional backlight, adds the panel, and attaches the DSI host. `prepare()` enables `vdd`, enables `iovcc`, waits 20 ms, toggles reset high then low, waits again, exits sleep, waits 250 ms, runs the vendor init sequence, sets display on, waits 50 ms, and unwinds regulators on accumulated DSI error. `unprepare()` sends display-off and sleep-in through `mipi_dsi_multi_context`, asserts reset, and disables `iovcc` then `vdd`.

### State and persistence behavior

The file stores only static mode data and per-device handles. There are no explicit prepared or enabled flags; hardware state follows the DRM panel lifecycle. Orientation persists from DT and is returned through `get_orientation()`. The init sequence programs volatile panel controller registers each time the panel is prepared. `mipi_dsi_multi_context.accum_err` carries sequential command failure state through prepare/unprepare command batches.

### Dependencies

Dependencies include DRM panel/mode helpers, MIPI DSI DCS multi-context helpers, regulator and GPIO consumer APIs, OF orientation helpers, and `drm_panel_of_backlight()`. The panel uses DSI video mode with one RGB888 lane and no EOT packet.

### Integration points

The compatible is `elida,kd35t133`. DTS must provide `vdd`, `iovcc`, optional `reset-gpios`, orientation, and optional backlight. The connector receives one 320x480 preferred mode with 42 mm by 82 mm dimensions. The driver registers as a `mipi_dsi_driver` named `panel-elida-kd35t133`.

### Risks

The vendor initialization sequence is minimally documented, so changes to register values are hard to reason about without hardware. `kd35t133_unprepare()` returns immediately if display-off or sleep-in fails, which can skip reset assertion and regulator disable on command failure. Probe treats missing orientation as fatal, so board descriptions must be complete. The reset GPIO is optional but later set unconditionally through gpiod helpers, relying on NULL-safe semantics. Timing values around sleep-out are long and should not be shortened without panel validation.

### Test signals

Validate build/probe, regulator enable failure unwinding, one-lane DSI attach, reset timing, successful sleep-out/init/display-on sequence, fixed mode enumeration, orientation reporting, backlight binding, repeated prepare/unprepare, and suspend/resume. Hardware tests should watch for gamma/inversion correctness and any DSI errors during the vendor sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-elida-kd35t133.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feixin-k101-im2ba02.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feixin-k101-im2ba02.c

### Purpose

`panel-feixin-k101-im2ba02.c` drives the Feixin K101 IM2BA02 MIPI-DSI LCD panel. It is a command-table based four-lane RGB888 video panel driver with three bulk regulators, reset GPIO control, a long page-based initialization table, a delayed display-on/TE enable step, and one fixed 800x1280 preferred mode.

### Important APIs, types, and functions

`struct k101_im2ba02` stores the DRM panel, DSI device, three bulk supplies (`dvdd`, `avdd`, `cvdd`), and reset GPIO. `struct k101_im2ba02_init_cmd` wraps two-byte command/data pairs. `k101_im2ba02_init_cmds` contains the long vendor sequence covering command pages, password/unlock values, lane count, VCOM, gamma power, gate power, panel/BGR configuration, TCON parameters, gamma tables, GIP configuration, and sleep-out. `timed_cmds` holds display-on and tear-on commands, though enable uses only the second entry after an explicit DCS display-on helper. DRM callbacks are `k101_im2ba02_prepare()`, `k101_im2ba02_enable()`, `k101_im2ba02_disable()`, `k101_im2ba02_unprepare()`, and `k101_im2ba02_get_modes()`.

### Control flow

Probe allocates state, assigns regulator bulk names, obtains regulators and reset GPIO, binds optional backlight, adds the panel, sets DSI video mode/RGB888/four lanes, and attaches. `prepare()` bulk-enables supplies, waits, toggles reset high-low-high with long settling delays, then iterates the complete two-byte init table using `mipi_dsi_dcs_write_buffer()`. If a command fails, it drives reset low, waits, and disables supplies. `enable()` waits 150 ms after prepare, sends DCS display-on, waits 50 ms, then sends the second timed command (`0x35, 0x00`) to enable tearing effect. `disable()` sends display-off. `unprepare()` sends display-off and sleep-in, waits 200 ms, drives reset low, waits, and disables all supplies.

### State and persistence behavior

There is no explicit software power state; the regulator bulk and reset GPIO encode hardware state. Vendor command state is volatile and rebuilt on each prepare. The fixed mode and init arrays are static. Backlight state is delegated to the DRM panel backlight helper. DSI errors in prepare stop the init loop and power down, while unprepare logs but ignores display-off/sleep-in failures before disabling rails.

### Dependencies

The driver depends on DRM panel/mode helpers, MIPI DSI DCS write helpers, Linux regulator bulk and GPIO APIs, OF match data, and `drm_panel_of_backlight()`. It expects a four-lane DSI host with RGB888 video mode support.

### Integration points

The compatible is `feixin,k101-im2ba02`. DTS must provide `dvdd`, `avdd`, `cvdd`, `reset`, and optional backlight. The connector gets one preferred 800x1280 mode at 70 MHz with 136 mm by 217 mm dimensions. Runtime integration follows the standard panel prepare/enable/disable/unprepare path.

### Risks

The initialization table is long and largely magic-number driven; accidental edits can change power, gamma, GIP, or lane behavior. `timed_cmds[0]` duplicates display-on but is unused, which can confuse maintenance. `prepare()` returns the result of regulator disable on the powerdown path rather than preserving the original DSI write error if disable succeeds, potentially hiding the real failure. Reset polarity and the 200 ms settling delay are critical. Any mismatch between the table lane command and DSI host lane count can cause link failure.

### Test signals

Validate probe and DSI attach, bulk regulator sequencing, reset waveform, failure unwinding from an injected DSI write error, mode enumeration, backlight binding, display-on plus tear-on behavior, repeated suspend/resume, and visual checks for gamma/GIP correctness across the whole panel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feixin-k101-im2ba02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feiyang-fy07024di26a30d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feiyang-fy07024di26a30d.c

### Purpose

`panel-feiyang-fy07024di26a30d.c` is a DRM/MIPI-DSI panel driver for the Feiyang FY07024DI26A30-D 1024x600 LCD. It implements the panel's two-regulator power sequence, optional reset GPIO, a short initialization command table, display on/off handling, and one fixed preferred video-burst mode.

### Important APIs, types, and functions

`struct feiyang` stores the `drm_panel`, DSI device, `dvdd` and `avdd` regulators, and optional reset GPIO. `struct feiyang_init_cmd` stores fixed two-byte initialization commands in `feiyang_init_cmds`. Panel callbacks are `feiyang_prepare()`, `feiyang_enable()`, `feiyang_disable()`, `feiyang_unprepare()`, and `feiyang_get_modes()`. Probe/remove are `feiyang_dsi_probe()` and `feiyang_dsi_remove()`.

### Control flow

Probe allocates managed panel state, gets `dvdd` and `avdd`, gets optional reset, binds optional backlight, adds the panel, configures DSI video burst, RGB888, four lanes, and attaches to the DSI host. `prepare()` enables `dvdd`, waits 10 ms, enables `avdd`, waits 20 ms, toggles reset low then high with panel timing comments, waits 200 ms, and sends seven two-byte DCS/vendor commands. `enable()` waits another 200 ms before sending display-on. `disable()` sends display-off. `unprepare()` sends display-off and sleep-in with logged errors, waits 200 ms, drives reset low, disables `avdd`, waits 10 ms, and disables `dvdd`.

### State and persistence behavior

The driver has no explicit enabled/prepared flags. Hardware state is represented by rail and reset state plus panel DCS state. The init command table is static and replayed on every prepare. The display mode is static and returned by duplication in `get_modes()`. The reset GPIO is optional and gpiod calls are NULL-safe.

### Dependencies

Dependencies include DRM panel/mode helpers, MIPI DSI DCS write helpers, regulator consumer APIs, GPIO consumer APIs, OF match tables, and `drm_panel_of_backlight()`. The DSI host must support four-lane RGB888 burst video.

### Integration points

The only compatible is `feiyang,fy07024di26a30d`. DTS must provide `dvdd`, `avdd`, optional `reset`, and optional backlight. The connector receives one 1024x600 preferred mode at 55 MHz. The panel driver name is `feiyang-fy07024di26a30d`.

### Risks

If enabling `avdd` fails, `prepare()` returns immediately without disabling already-enabled `dvdd`, leaving a rail on until later cleanup. DSI init failures also return without resetting or disabling regulators. `unprepare()` logs DSI failures but continues power-off, which is usually acceptable but can hide bus issues. The timing comments are part of the hardware contract; shortening waits risks intermittent panel start. The mode lacks physical dimensions, so connector size reporting is limited.

### Test signals

Use build/probe checks, regulator failure injection, GPIO waveform validation, DSI command trace for the seven init commands, mode enumeration, display-on/off behavior, repeated prepare/unprepare, suspend/resume, and visual confirmation of stable 1024x600 output after the documented delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feiyang-fy07024di26a30d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8279.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8279.c

### Purpose

`panel-himax-hx8279.c` is a descriptor-driven DRM/MIPI-DSI driver for panels built around the Himax HX8279 display controller. It supports single-DSI and dual-DSI wiring, validates controller configuration data before writing potentially persistent/OTP-like registers, programs MIPI timing, GOA mux/config/timing, analog and digital gamma, voltage settings, advanced engineer-page controls, and exposes fixed modes for supported Aoly and Startek panels.

### Important APIs, types, and functions

`struct hx8279` stores the DRM panel, up to two DSI devices, `vdd`/`iovcc` regulator bulk entries, enable/reset GPIOs, descriptor, cached `last_page`, and skip flags derived from validation. Descriptor types include `struct hx8279_panel_mode`, `struct hx8279_goa_mux`, `struct hx8279_analog_gamma`, `struct hx8279_digital_gamma`, and `struct hx8279_panel_desc`. Register macros define page selection and fields for pages 0 through 12.

Programming helpers are `hx8279_set_page()`, `hx8279_set_module_config()`, `hx8279_set_gmux()`, `hx8279_set_analog_gamma()`, `hx8279_set_goa_timing()`, `hx8279_set_goa_cfg()`, `hx8279_set_mipi_cfg()`, `hx8279_set_adv_cfg()`, and `hx8279_set_digital_gamma()`. Validation helpers are `hx8279_init_vregs()`, `hx8279_check_gmux_config()`, `hx8279_check_goa_config()`, `hx8279_check_dig_gamma()`, and `hx8279_check_params()`. DRM callbacks are `hx8279_prepare()`, `hx8279_enable()`, `hx8279_disable()`, `hx8279_unprepare()`, and `hx8279_get_modes()`.

### Control flow

Probe allocates the panel, obtains and voltage-checks `vdd` and `iovcc`, reads match data, validates descriptor values, gets optional enable and required reset GPIOs, optionally discovers a secondary DSI host from graph port 1, registers a managed DSI device for the right side, binds backlight, adds the DRM panel, configures every present DSI device with descriptor lane count, RGB888 format, non-continuous clock and LPM, adds video sync-pulse flags for video modes, and attaches both devices. `prepare()` enables regulators, asserts enable and reset with short delays, sets LPM on both DSI devices, calls `hx8279_on()` to program pages 5, 1, 2, 3, 0, 6, and 7-12, exits sleep, and waits 130 ms. `enable()` sends display-on; `disable()` sends display-off; `unprepare()` enters sleep, waits, clears LPM, resets/powers off, and disables regulators.

### State and persistence behavior

`last_page` avoids redundant page-select writes during one programming pass and persists until the device is reinitialized. Skip flags are computed at probe to avoid programming absent voltage, GOA, MIPI timing, or GOA timing blocks. The descriptor data is immutable static match data. Hardware register programming is volatile in normal operation but the comments warn some fields may be OTP in some driver ICs, motivating validation. Dual-DSI state stores both device pointers, but command programming is issued through the primary DSI device.

### Dependencies

The driver depends on Linux bitfield helpers, OF graph helpers for secondary DSI discovery, regulator and GPIO APIs, DRM panel/mode/connector helpers, MIPI DSI generic and DCS multi-context helpers, and device match data. It uses managed DSI attachment and managed registration for the secondary DSI endpoint.

### Integration points

Supported compatibles are `aoly,sl101pm1794fog-v15` and `startek,kd070fhfid078`. Their descriptors provide modes, voltages, GOA muxes, timing values, MIPI timing, engineer controls, and optional analog/digital gamma tables. Board DTS supplies `vdd`, `iovcc`, reset, optional enable, optional backlight, and optional second DSI graph connection. Connectors receive descriptor modes, bpc, and physical dimensions.

### Risks

The descriptor validation is essential but contains fragile logic: bounds compare values against bit masks rather than decoded maxima in several places, and the GOA timing validity counters are non-obvious. `hx8279_set_goa_timing()` writes `goa_odd_timing` for both odd and even register loops, which looks suspicious when `goa_even_timing` differs. `hx8279_set_digital_gamma()` reuses loop variable `i` in nested loops, so the intended two-pass positive/negative programming may not execute as written. Command programming only uses `dsi[0]`, so dual-DSI panels rely on mirrored controller behavior or host-side routing. Display-on/off helpers ignore accumulated DSI errors and return zero.

### Test signals

Run build coverage, probe both compatibles, validation failure tests for voltages/GOA/gamma descriptors, single- and dual-DSI attach paths, regulator voltage support checks, command traces verifying page order and gamma programming, sleep/display transitions, repeated suspend/resume, mode enumeration, backlight binding, and hardware image checks for GOA/gamma correctness. Static review should specifically cover the even-timing and digital-gamma loop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8279.c -->
