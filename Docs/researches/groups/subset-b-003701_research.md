# subset-b-003701 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ronbo-rb070d30.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ronbo-rb070d30.c

Purpose: Ronbo RB070D30 is a simple 1024x600 MIPI-DSI video-mode panel driver. It exposes one fixed preferred mode, controls one regulator named `vcc-lcd`, and drives reset, power, up/down, and shift-left/right GPIOs. The two orientation GPIOs are forced low at probe and never changed later.

Important APIs, control flow, and state: `rb070d30_panel_dsi_probe()` allocates a `drm_panel`, fetches resources, attaches OF backlight, sets four DSI lanes, RGB888, video burst, and LPM flags, then attaches to the DSI host. `prepare()` enables the regulator, asserts panel power and reset with 20 ms gaps; `enable()` exits DCS sleep; `disable()` enters sleep; `unprepare()` drops reset, power, and regulator. `get_modes()` duplicates `default_mode`, sets 8 bpc, physical size, and RGB888 bus format. There is no software prepared/enabled flag, no cached hardware state, and no persistent data beyond the devm-managed context.

Dependencies, integration, risks, and tests: integration is the DRM panel framework, MIPI DSI host, GPIO/regulator/backlight descriptors, and `ronbo,rb070d30` DT binding. Main risks are strict GPIO polarity and sequencing assumptions, no rollback if later GPIO steps fail after regulator enable, and no panel-specific DCS init beyond sleep exit. Test signals are successful DSI attach, correct fixed mode exposure, backlight discovery, clean suspend/resume sequencing, and visible video without orientation or RGB-order issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ronbo-rb070d30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ams581vf01.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ams581vf01.c

Purpose: This is a Samsung AMS581VF01 command-mode DSI panel driver for a 1080x2340 AMOLED-like panel. It owns reset, four supplies (`vdd3p3`, `vddio`, `vsn`, `vsp`), a fixed mode, and a raw 10-bit DCS brightness backlight.

Important APIs, control flow, and state: probe allocates `struct ams581vf01`, bulk-gets supplies, gets an active-high reset GPIO, configures four RGB888 lanes with burst, non-continuous clock, and LPM, creates a devm backlight, adds the panel, and uses `devm_mipi_dsi_attach()`. `prepare()` enables supplies, toggles reset high-to-low, runs `ams581vf01_on()`, and rolls back reset plus supplies on failure. The on sequence exits sleep, enables TE, unlocks manufacturer commands, programs MIC, column/page windows, control display, sync settings, waits 110 ms, and sets display on. `unprepare()` runs display off/sleep in plus VCI operating-mode change, asserts reset, and disables supplies. Brightness update clears LPM, writes large DCS brightness, and restores LPM.

Dependencies, integration, risks, and tests: dependencies are DRM panel/probe helper fixed modes, DSI multi-context DCS helpers, Linux backlight, GPIO, and regulator APIs under `samsung,ams581vf01`. Risks are command-sequence magic values, mode-flag mutation in backlight callbacks without locking, and a one-way brightness API with no get callback. Test signals include fixed mode enumeration, regulator/reset timing on runtime PM paths, DCS command success from `accum_err`, backlight writes at 0/511/1023, and no blanking when switching LPM around brightness updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ams581vf01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ams639rq08.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ams639rq08.c

Purpose: Samsung AMS639RQ08 is a 1080x2340 command-mode DSI panel driver with local DCS backlight control. It resembles AMS581VF01 but has a longer vendor initialization path, a wider 11-bit brightness range, and a brightness readback callback.

Important APIs, control flow, and state: `ams639rq08_probe()` allocates the panel, obtains the same four supply rails as AMS581, configures reset and four-lane RGB888 DSI burst/non-continuous/LPM mode, creates a raw backlight with max 2047, and attaches. `prepare()` bulk-enables supplies, resets, runs `ams639rq08_on()`, and disables supplies on init failure. The on flow unlocks two password levels, changes VCI/bias/current state, exits sleep, enables TE, programs DBV smoothing, edge dimming, page address, HFP/OFC/ERR_FG settings, writes control display and initial brightness, disables power save, waits 67 ms, and sets display on. `unprepare()` sends display off, sleep in, waits 120 ms, asserts reset, and disables supplies.

Dependencies, integration, risks, and tests: integration points are MIPI DSI DCS multi-context helpers, DRM fixed mode helper, devm backlight, regulator bulk APIs, and DT compatible `samsung,ams639rq08`. Risks include vendor commands with unknown names, backlight get/update temporarily mutating `dsi->mode_flags`, and brightness read failure leaving LPM cleared because the early return happens before restoring it. Tests should cover brightness set/get, failure injection around DCS reads, prepare rollback, DSI attach/remove, and visible 60 Hz scanout with TE enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ams639rq08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-atna33xc20.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-atna33xc20.c

Purpose: Samsung ATNA33XC20 is an eDP panel driver that cannot use `panel-simple` because EL_ON3/backlight and HPD timing require custom runtime-PM sequencing. It binds as a DP AUX endpoint, reads EDID over AUX, and uses DP AUX backlight when available.

Important APIs, control flow, and state: `atana33xc20_probe()` allocates `struct atana33xc20_panel`, stores the AUX handle, gets `power`, `enable`, and optional `hpd` GPIO resources, enables runtime PM with autosuspend, attempts `drm_panel_dp_aux_backlight()`, and adds the panel. `prepare()` runtime-resumes the device; `enable()` waits at least 400 ms after power-on then asserts EL_ON3; `disable()` deasserts EL_ON3, records the timestamp, marks `el3_was_on`, and waits 20 ms; `unprepare()` forces synchronous runtime suspend. Runtime resume enforces 500 ms power-off minimum, enables the regulator, marks DPCD powered, and waits for HPD through GPIO, AUX callback, or fixed delay for `no-hpd`. Runtime suspend waits 150 ms after EL_ON3 off, powers DPCD down, disables the regulator, and records `powered_off_time`. `get_modes()` runtime-resumes, caches EDID in `drm_edid`, updates connector modes, and autosuspends.

Dependencies, integration, risks, and tests: dependencies are DP AUX bus, DPCD helpers, EDID helpers, runtime PM, GPIO/regulator APIs, and `samsung,atna33xc20`. Risks are subtle timestamp ordering, stale cached EDID after panel replacement, non-fatal DP AUX backlight failure, and WARN/`-EIO` if enable happens after EL_ON3 drop without a power cycle. Test signals include HPD timeout behavior, EDID mode discovery, autosuspend around AUX-only reads, system suspend/resume, backlight registration, and repeated disable/unprepare/prepare/enable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-atna33xc20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-db7430.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-db7430.c

Purpose: DB7430 drives the Samsung LMS397KF04 480x800 DPI RGB panel through an SPI MIPI-DBI control channel and an external DPI pixel bus. It programs controller power, RGB timing, gamma, and CABC/display-on sequences while advertising one fixed DPI mode.

Important APIs, control flow, and state: probe allocates `struct db7430`, obtains `vci`/`vccio`, reset GPIO, initializes `mipi_dbi` over SPI, hooks an OF backlight, and registers a DPI connector panel. `prepare()` enables regulators, delays, pulses reset, and writes a long DBI setup sequence: address mode twice, access protection, panel/source/gate/timing controls, RGB sync, RGB gamma curves, bias/DDV/gamma ref/DCDC/VCL controls. `enable()` exits sleep, sends NVM load commands, waits 150 ms, enables CABC-related settings, and sets display on. `disable()` sends display off and sleep in; `unprepare()` asserts reset and disables regulators. `get_modes()` duplicates 480x800 mode, sets RGB888 bus format, 8 bpc, negative pixel-data edge, and physical size.

Dependencies, integration, risks, and tests: dependencies are SPI, DRM MIPI DBI helpers, DRM panel, media bus formats, regulator/GPIO, and compatible `samsung,lms397kf04`. Risks include undocumented command values, no error checking on most DBI command writes after power-on, duplicated address-mode write hinting at unreliable first transfer, and a TODO for internal backlight. Tests should cover SPI DBI command success, display orientation/RGB order, external DPI timing, regulator/reset sequencing, OF backlight binding, and suspend/resume without leaving the panel active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-db7430.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ld9040.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ld9040.c

Purpose: LD9040 is an SPI-controlled AMOLED DPI panel driver with DT-provided video timing and a built-in gamma-table backlight model. It is derived from older fbdev/backlight code and sends 9-bit SPI DCS words manually.

Important APIs, control flow, and state: `struct ld9040` stores supplies (`vdd3`, `vci`), reset GPIO, DT delays, videomode, physical size, brightness index, and an error latch. `ld9040_spi_write_word()` sends a 16-bit word where command/data is encoded by ORing data bytes with `0x100`. `ld9040_dcs_write()` stops future transfers after the first error until `ld9040_clear_error()`. Probe parses videomode and panel dimensions from DT, sets `spi->bits_per_word = 9`, registers a non-linear raw backlight, and adds a DPI panel. `prepare()` powers on, resets, sends user/panel/display/power/ELVSS/gamma/sleep-out/display-on setup, then checks the error latch. `unprepare()` sends display off/sleep in, clears errors, and disables regulators. Brightness updates write one of 25 gamma rows and trigger gamma control.

Dependencies, integration, risks, and tests: dependencies are SPI, regulator/GPIO, DT videomode properties, Linux backlight, and DRM panel APIs under `samsung,ld9040`. Risks include 9-bit SPI controller support, no locking between backlight updates and panel disable, DT timing dependence, and latent errors being collapsed into one latch. Test signals include valid SPI setup, all brightness indices 0-24, mode creation from DT, display-on after prepare, and clean error rollback on transfer failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ld9040.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ltl106hl02.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ltl106hl02.c

Purpose: Samsung LTL106HL02-001 is a straightforward 1920x1080 video-mode DSI panel. It controls one `power` regulator, optional reset GPIO, an OF-described backlight, and exposes one fixed preferred mode.

Important APIs, control flow, and state: probe allocates `struct samsung_ltl106hl02`, gets resources, configures four-lane RGB888 DSI with video and LPM flags, attaches OF backlight, adds the panel, and uses `devm_mipi_dsi_attach()`. `prepare()` enables the regulator, optionally toggles reset, exits DCS sleep, waits 70 ms, sets display on, waits 5 ms, and returns the DSI multi-context accumulated error. `unprepare()` sends display off, waits 50 ms, enters sleep, waits 150 ms, asserts reset if present, and disables the regulator. `get_modes()` delegates to `drm_connector_helper_get_modes_fixed()`.

Dependencies, integration, risks, and tests: dependencies are MIPI DSI multi-context helpers, DRM fixed mode helper, regulator/GPIO/backlight APIs, and `samsung,ltl106hl02-001`. Risks are minimal command sequencing with no panel-specific init, no rollback if display-on fails after regulator enable, and optional reset path differences across boards. Test signals include fixed-mode enumeration, external backlight binding, correct regulator/reset polarity, DSI attach/remove, and reliable resume from sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-ltl106hl02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d16d0.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d16d0.c

Purpose: S6D16D0 is an 864x480 command-only MIPI DSI AMOLED panel driver. Because the panel uses command mode, its timing values mainly satisfy DRM mode plumbing rather than video-stream timing.

Important APIs, control flow, and state: probe allocates `struct s6d16d0`, sets two DSI lanes, RGB888, explicit HS/LP rates, non-continuous clock, `vdd1` supply, and optional reset GPIO defaulting asserted. `prepare()` enables the regulator, pulses reset, waits 120 ms, enables TE at vblank, and exits sleep. `enable()` sets display on; `disable()` sets display off; `unprepare()` enters sleep, asserts reset, and disables supply. `get_modes()` duplicates a fixed 864x480 mode and sets physical dimensions. Persistent software state is only resource pointers; no prepared flag or brightness/backlight is managed here.

Dependencies, integration, risks, and tests: dependencies are DRM panel, MIPI DSI DCS helpers, regulator/GPIO APIs, and compatible `samsung,s6d16d0`. Risks include command-mode timing assumptions, no cleanup if TE or sleep-out fails after regulator enable, and no backlight integration despite AMOLED brightness likely being external or fixed. Tests should cover TE enable success, sleep/display transitions, HS/LP rate compatibility with the host, mode enumeration, and regulator/reset behavior on error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d16d0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d27a1.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d27a1.c

Purpose: S6D27A1 supports a Samsung 480x800 DPI RGB panel with SPI MIPI-DBI command control. It initializes panel controller state over SPI and exposes a DPI scanout mode with RGB888 bus format.

Important APIs, control flow, and state: probe allocates `struct s6d27a1`, gets `vci`/`vccio`, reset GPIO, initializes `mipi_dbi`, registers custom read commands for MTP ID reads, attaches OF backlight, and adds the panel. `prepare()` enables supplies, pulses reset, sends sleep-out twice, unlocks level 2 controls, programs resolution, ASG/manual/display/power/source/panel controls, locks level 2, and logs MTP ID. `enable()` sends display on; `disable()` display off; `unprepare()` enters sleep, waits 120 ms, asserts reset, and disables regulators. `get_modes()` returns the 480x800 mode, 8 bpc, RGB888 bus format, and negative pixel-data edge.

Dependencies, integration, risks, and tests: dependencies are SPI, DRM MIPI DBI, regulator/GPIO/backlight APIs, media bus format helpers, and `samsung,s6d27a1`. Risks are undocumented command values, no return checking for most `mipi_dbi_command()` calls, reliance on custom read-command whitelist for ID reads, and panel-specific DPI bus flags. Test signals include readable MTP ID, correct 480x800 scanout, external backlight binding, no DBI init errors, and stable suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d27a1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d7aa0.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d7aa0.c

Purpose: S6D7AA0 is a descriptor-driven MIPI DSI LCD controller driver covering `samsung,lsl080al02`, `samsung,lsl080al03`, and `samsung,ltl101at01`. It provides per-panel mode, init/off functions, extra DSI flags, and optional internal DCS backlight fallback.

Important APIs, control flow, and state: `struct s6d7aa0_panel_desc` selects panel type, init/off callbacks, mode, bus flags, `has_backlight`, and password-level behavior. Probe obtains match data, `power`/`vmipi` regulators, reset GPIO, configures four-lane RGB888 video burst plus descriptor flags, checks OF backlight, creates a DSI raw backlight if needed, and attaches. `prepare()` enables regulators, resets, and calls descriptor init; `disable()` calls descriptor off then display off/sleep in; `unprepare()` asserts reset and disables regulators. LSL080AL02 has its own OTP/backlight/address-mode sequence; LSL080AL03 and LTL101AT01 share init with panel-type branches. Brightness callbacks use DCS brightness set/get.

Dependencies, integration, risks, and tests: dependencies are DRM panel, MIPI DSI multi-context, regulator/GPIO/backlight APIs, and DT match data. Risks include inverted password3 lock/unlock values, shared init code with panel-type conditionals, fallback backlight only for selected descriptors, and lack of regulator rollback when init fails after reset. Tests should cover all three compatibles, OF versus DSI-created backlight, mode dimensions, DSI flags per descriptor, brightness get/set, and remove detach error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6d7aa0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3fa7.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3fa7.c

Purpose: S6E3FA7 is a generated-style command-mode DSI panel driver for the Samsung AMS559NK06 variant. It exposes a 1080x2220 mode and a raw 10-bit DCS backlight.

Important APIs, control flow, and state: probe allocates `struct s6e3fa7_panel`, gets reset GPIO, configures four-lane RGB888 DSI burst/non-continuous/LPM mode, sets `prepare_prev_first`, creates a backlight, adds the panel, and attaches. `prepare()` resets then calls `s6e3fa7_panel_on()`, which exits sleep, waits 120 ms, enables TE, unlocks `0xf0`, writes a power/config sequence to `0xf4`, locks, writes control-display brightness enable, and sets display on. `disable()` sends display off and sleep in with a 120 ms wait; `unprepare()` only asserts reset. Brightness update/get use large DCS brightness commands.

Dependencies, integration, risks, and tests: dependencies are DRM panel, MIPI DSI DCS helpers, backlight, reset GPIO, and compatible `samsung,s6e3fa7-ams559nk06`. Risks are no regulator management in this driver, no LPM flag toggling for brightness reads/writes, generated magic command values, and reset-only unprepare depending on board power outside the driver. Test signals include DSI command success, backlight range 0-1023, visible fixed-mode scanout, TE behavior, and clean detach/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3fa7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3fc2x01.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3fc2x01.c

Purpose: S6E3FC2X01 is a Samsung DDIC driver for the AMS641RW 1080x2340 panel. It handles three supplies, reset, multi-level test-key command sequences, fixed mode reporting, and a platform/raw DCS backlight.

Important APIs, control flow, and state: probe bulk-gets `vddio`, `vci`, and `poc`, gets reset GPIO default low to preserve flicker-free state, configures four-lane RGB888 burst/non-continuous/LPM DSI, creates a backlight, adds the panel, and attaches. `prepare()` enables supplies, resets, and runs a long init sequence with level 1/2/3 keys, sleep-out, MIC/sync/window/ELVSS/brightness/power-save settings. `enable()` wraps display-on in level-1 key; `disable()` runs a detailed off sequence with display off, vendor B9/F4 writes, sleep in, and waits; `unprepare()` asserts reset and disables supplies. Backlight update clears LPM, writes large brightness, and restores LPM.

Dependencies, integration, risks, and tests: dependencies are MIPI DSI multi-context DCS helpers, regulator bulk const get, backlight APIs, DRM fixed mode helper, and compatible `samsung,s6e3fc2x01-ams641rw`. Risks include many undocumented commands, error paths that can leave test keys enabled if later commands fail, mode-match `.data` not used, and LPM restoration missing on brightness write failure. Test signals include full prepare/enable/disable/unprepare sequencing, brightness writes, regulator rollback on init failure, and no flicker/regression from reset polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3fc2x01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3ha2.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3ha2.c

Purpose: S6E3HA2 is a MIPI DSI AMOLED panel driver supporting HA2 and HF2 variants through match-data descriptors. It owns a custom backlight whose brightness maps into gamma and VINT tables rather than simple DCS DBV writes.

Important APIs, control flow, and state: `struct s6e3ha2` stores the panel, registered backlight, `vdd3`/`vci` supplies, reset/enable GPIOs, and variant descriptor. Probe configures four-lane RGB888 command-ish video flags without HFP/HBP/HSA, registers a non-devm backlight named `s6e3ha2`, sets default brightness 80/100, adds the panel, and attaches. `prepare()` enables supplies, toggles enable/reset, exits sleep, and programs single-DSI and frequency-calibration sequences with F0/FC keys. `enable()` enables TE, writes many common/pentile/POC/PCD/ERR/brightness/AOR/ELVSS/ACL/HBM settings, sets display on, and marks backlight power on. `disable()` enters sleep then display off and marks reduced power; `unprepare()` disables regulators. Brightness updates validate range and power state, unlock F0, write indexed gamma, AOR, VINT, and relock.

Dependencies, integration, risks, and tests: dependencies are DRM panel, MIPI DSI DCS write-buffer APIs, regulator/GPIO/backlight, and compatibles `samsung,s6e3ha2`/`samsung,s6e3hf2`. Risks include large static gamma tables, order-sensitive test-key handling, non-devm backlight cleanup, possible display-off ordering after sleep-in, and brightness writes rejected when powered off. Tests should cover both modes, brightness 0/80/100, gamma/VINT index boundaries, attach failure cleanup, and suspend/resume display recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3ha2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3ha8.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3ha8.c

Purpose: S6E3HA8 is a generated MIPI DSI panel driver for a 1440x2960 WQHD Samsung panel that requires DSC. It configures a `drm_dsc_config`, enables DSI compression mode, and sends PPS during prepare.

Important APIs, control flow, and state: probe allocates `struct s6e3ha8`, gets `vdd3`, `vci`, and `vddr` supplies, gets reset GPIO, configures four-lane RGB888 non-continuous/no-HFP/no-HBP/no-HSA/no-EOT DSI flags, attaches `dsi->dsc` to the panel DSC config, and sets DSC 1.1, 720-pixel slices, 40-line slice height, 8 bpc, 8 bpp, and block prediction. `prepare()` enables supplies, waits 120 ms, runs a three-edge reset, executes the vendor on sequence, packs PPS with `drm_dsc_pps_payload_pack()`, writes it under level-1 key, and waits 28 ms. `enable()` wraps display-on in level-1 key. `disable()` display-offs, disables AFC through level-2 key, and waits 160 ms. `unprepare()` only disables supplies. `get_modes()` returns the fixed WQHD mode.

Dependencies, integration, risks, and tests: dependencies are DRM DSC helpers, MIPI DSI compression/PPS helpers, regulator/GPIO APIs, and `samsung,s6e3ha8`. Risks include DSC being mandatory and host-dependent, no reset assertion in unprepare, vendor scaler/FFC/brightness commands, and `WARN_ON` only checking slice divisibility. Tests should verify DSC negotiation with the host, PPS packet contents, WQHD scanout, disable/re-enable, and no blank frame after compression mode enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e3ha8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63j0x03.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63j0x03.c

Purpose: S6E63J0X03 is a 1.63 inch 320x320 MIPI DSI AMOLED panel driver. It manages two supplies, reset, a custom gamma-table backlight, MTP keys, and a one-lane DSI link.

Important APIs, control flow, and state: probe allocates `struct s6e63j0x03`, sets one-lane RGB888 DSI video flags without porch/sync packets, gets `vdd3`/`vci`, reset GPIO, registers a backlight named `s6e63j0x03`, sets max/default brightness, and attaches. `prepare()` powers on, resets, unlocks level-2/MTP, programs porch/frame frequency, column/page window with `FIRST_COLUMN`, LTPS timing, TE edge, exits sleep, and marks backlight reduced. `enable()` waits, applies MTP key, writes ELVSS/address mode/default DBV/control display/power save/TE, locks MTP, sets display on, and marks backlight on. `disable()` display-offs, marks reduced, enters sleep, waits 120 ms; `unprepare()` disables supplies and marks off. Brightness maps 0-100 into 9 gamma rows, writes under MTP key, and stores the requested brightness.

Dependencies, integration, risks, and tests: dependencies are MIPI DSI DCS helpers, regulator/GPIO/backlight APIs, and compatible `samsung,s6e63j0x03`. Risks are coarse brightness quantization, no range validation in backlight update, command ordering around MTP key off on errors, and unusual column offset. Test signals include 320x320 visible scanout, brightness index boundaries, sleep/resume recovery, reset polarity, and one-lane host compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63j0x03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0-dsi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0-dsi.c

Purpose: This file is the MIPI DSI transport adapter for the shared S6E63M0 panel core. It provides DCS read/write callbacks, configures DSI link parameters, and delegates panel lifecycle to `s6e63m0_probe()`/`s6e63m0_remove()`.

Important APIs, control flow, and state: `s6e63m0_dsi_probe()` sets two lanes, RGB888, HS/LP rates, video burst flags, then calls `s6e63m0_probe(dev, NULL, read, write, true)`. If the core probes successfully, it attaches to the DSI host; attach failure removes the core panel. The write callback splits long DCS payloads into chunks of at most 15 parameter bytes. After the first chunk it writes `MCS_GLOBAL_PARAM` (`0xb0`) with the byte offset before sending the next chunk for the same command. Reads fetch one byte with `mipi_dsi_dcs_read()`. Each write sleeps 8-9 ms.

Dependencies, integration, risks, and tests: dependencies are DRM MIPI DSI APIs and the shared header/core. Risks include chunk offset correctness, the fixed one-byte read size, both DSI and SPI adapters matching the same compatible string, and cleanup responsibility split across DSI attach and core remove. Tests should cover long gamma/ACL writes that require chunking, MTP ID reads, DSI attach failure cleanup, and successful display bring-up through the shared core in DSI mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0-dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0-spi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0-spi.c

Purpose: This file is the SPI/MIPI-DBI transport adapter for the shared S6E63M0 panel core. It lets the same panel logic operate over a DBI command bus instead of DSI.

Important APIs, control flow, and state: probe allocates a `mipi_dbi`, initializes it with `mipi_dbi_spi_init()`, installs a read-command whitelist for MTP ID commands (`MCS_READ_ID1/2/3`), and calls `s6e63m0_probe(dev, dbi, read, write, false)`. The read callback calls `mipi_dbi_command_read()`. The write callback uses `mipi_dbi_command_stackbuf()` with `data[0]` as command and the remaining bytes as parameters, then waits 300-310 us. Remove delegates to `s6e63m0_remove()`.

Dependencies, integration, risks, and tests: dependencies are SPI, DRM MIPI DBI helpers, and the shared S6E63M0 core/header. Risks include no explicit `spi_set_drvdata()` here because the core sets device drvdata, reliance on DBI read-command registration for ID reads, and the same DT compatible as the DSI adapter requiring bus topology to select the right driver. Tests should cover DBI init, ID reads, all core brightness/gamma writes over SPI, and remove without DSI detach semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0.c

Purpose: This is the shared S6E63M0 AMOLED panel core used by DSI and SPI transports. It owns regulator/reset/backlight resources, panel mode registration, LCD type detection, initialization, and gamma/ACL/ELVSS brightness programming through transport-provided DCS callbacks.

Important APIs, control flow, and state: `s6e63m0_probe()` allocates `struct s6e63m0`, stores transport data and callbacks, reads optional `max-brightness`, gets `vdd3`/`vci` and reset GPIO, initializes a DSI or DPI `drm_panel`, registers a raw backlight, and adds the panel. `prepare()` powers on, unlocks level-2 and MTP keys, reads MTP ID bytes, derives `lcd_type` and `elvss_pulse`, sends variant-dependent panel-condition and gamma/pentile/source/ELVSS setup, and checks the error latch. `enable()` exits sleep, display-ons, writes error-check settings, and enables backlight. `disable()` disables backlight, display-offs, sleeps in, and waits; `unprepare()` clears errors and powers off. Brightness update indexes gamma, ACL, and ELVSS tables, clamps ELVSS pulse to 0x1f, writes commands, then clears the error latch.

Dependencies, integration, risks, and tests: dependencies are exported symbols consumed by the DSI/SPI adapters, DRM panel/backlight, regulator/GPIO/property APIs, and the shared MCS header. Risks include transport callback correctness, persistent error-latch behavior, table index constraints tied to `MAX_BRIGHTNESS`, detection fallback for unknown LCD type, and no explicit MTP lock after prepare. Tests should cover both transports, max-brightness DT override, ID read fallback, brightness table endpoints, panel mode/bus flags, and error propagation from read/write callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0.h

Purpose: This header is the shared contract between the S6E63M0 core and its DSI/SPI transport adapters. It defines the manufacturer command-set opcodes and exports the core probe/remove interfaces.

Important APIs, control flow, and state: the `MCS_*` macro namespace covers ELVSS, temperature SWIRE, pentile controls, gamma delta tables, MIE/BC mode, error check, MTP read IDs, level/MTP keys, display/source/interface/panel controls, and positive gamma control. `s6e63m0_probe()` accepts the parent device, opaque transport pointer, DCS read/write callbacks, and a `dsi_mode` boolean that selects connector type and DSI-specific init values in the core. `s6e63m0_remove()` removes the core panel from the device drvdata. The header stores no state but fixes the ABI between transport files and core command logic.

Dependencies, integration, risks, and tests: dependencies are Linux `struct device`, `u8`, `size_t`, and the core/adapter compilation units. Risks are command macro drift breaking table writes in the core, callback prototype changes desynchronizing adapters, and duplicate compatible handling across buses depending on this shared interface. Test signals are successful compilation of all three S6E63M0 objects, both transport probes invoking the exported core, ID read commands matching DBI whitelist, and modpost/export resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e63m0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e88a0-ams427ap24.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e88a0-ams427ap24.c

Purpose: This driver supports Samsung AMS427AP24 panels with an S6E88A0 controller. It exposes a 540x960 two-lane DSI video panel and a custom raw backlight that maps user brightness to candela, AID, ELVSS, and gamma tables.

Important APIs, control flow, and state: probe allocates `struct s6e88a0_ams427ap24`, bulk-gets `vdd3`/`vci`, reset GPIO, configures two-lane RGB888 video burst/no-EOT/no-HFP DSI, reads optional `flip-horizontal`, registers a raw backlight with max 255/default 180, adds the panel, and attaches. `prepare()` enables supplies, runs a reset pulse sequence, unlocks level keys, programs source latch/AVDD, exits sleep, writes level-3/pixel-clock settings, optionally flips display, relocks, applies current brightness, and sets display on. `unprepare()` sends display off/sleep in, waits 120 ms, asserts reset, and disables supplies. Brightness update walks a threshold table to a candela enum, chooses AID/ELVSS/gamma payloads, writes them under key `0xf0`, disables ACL, triggers gamma update, and relocks.

Dependencies, integration, risks, and tests: dependencies are MIPI DSI multi-context APIs, DRM fixed mode helper, devm backlight, regulator/GPIO/property APIs, and `samsung,s6e88a0-ams427ap24`. Risks include large calibration tables, brightness threshold off-by-one behavior, candela-to-AID grouping, comment-style vendor magic, and LPM flag changes during on/off. Tests should cover brightness 0/10/111/180/255, flip-horizontal, prepare rollback, table boundary indices, and visual gamma stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e88a0-ams427ap24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e88a0-ams452ef01.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e88a0-ams452ef01.c

Purpose: This is a simpler S6E88A0-based panel driver for Samsung AMS452EF01. It exposes a fixed 540x960 two-lane DSI video mode and sends a static default brightness/gamma/AOR/ELVSS initialization sequence, with no Linux backlight device.

Important APIs, control flow, and state: probe allocates `struct s6e88a0_ams452ef01`, gets `vdd3`/`vci`, reset GPIO, configures two-lane RGB888 video burst DSI, adds the panel, and attaches. `prepare()` enables supplies, toggles reset high-low-high, and runs `on()`: enable level-2 commands, set pixel-clock divider polarity, exit sleep, wait 120 ms, write default gamma table to `0xca`, default AOR to `0xb2`, ELVSS to `0xb6`, power save off, gamma update `0xf7`, lock commands, and display on. `unprepare()` display-offs, waits, sleeps in, asserts reset low, and disables supplies. `get_modes()` duplicates the fixed 540x960 mode and physical size.

Dependencies, integration, risks, and tests: dependencies are MIPI DSI multi-context helpers, regulator/GPIO APIs, and compatible `samsung,s6e88a0-ams452ef01`. Risks are no runtime backlight control, fixed gamma/brightness assumptions, reset polarity differences from AMS427AP24, and limited error handling after DSI init failure. Test signals include display-on after prepare, correct fixed mode, suspend/resume, regulator/reset sequencing, and acceptable default luminance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e88a0-ams452ef01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8aa0.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8aa0.c

Purpose: S6E8AA0 is a 5.3 inch MIPI DSI AMOLED panel driver with DT-provided videomode, variant detection through MTP ID, version-specific gamma tables, optional horizontal/vertical flip handling, and an internal error-latch pattern.

Important APIs, control flow, and state: `struct s6e8aa0` stores supplies, reset GPIO, DT delays, videomode, physical dimensions, flip booleans, detected version/id/variant, brightness index, and error. Probe configures four-lane RGB888 video burst with auto vertical mode, parses DT timing/delays/size/flip flags, gets `vdd3`/`vci`, reset GPIO, sets default brightness to the highest gamma index, adds the panel, and attaches. `prepare()` powers on, sets maximum return packet size, reads three-byte MTP ID from `0xd1`, selects a variant for versions 32/96/142/210, unlocks level keys, exits sleep, programs panel/display/source/pentile/power/ELVSS conditions, writes version-specific gamma, and sets display on. `unprepare()` enters sleep, display-offs, clears error, and disables supplies. `get_modes()` converts the DT videomode into a DRM mode.

Dependencies, integration, risks, and tests: dependencies are MIPI DSI DCS read/write, DT videomode properties, regulator/GPIO APIs, and compatible `samsung,s6e8aa0`. Risks include unsupported MTP versions causing probe-time prepare failure, large hard-coded gamma tables, flip logic altering many panel condition bits, no registered backlight despite brightness infrastructure, and error latch hiding later writes after one failure. Tests should cover multiple panel IDs where available, DT flip flags, read-packet-size setup, timing parsing, prepare rollback on unsupported version, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-samsung-s6e8aa0.c -->
