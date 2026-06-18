# subset-b-003700 Research

Grouped research for DRM panel source files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/`. Each section is wrapped with the exact source path markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36523.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36523.c

Purpose: DRM MIPI-DSI panel driver for Novatek NT36523-based panels used by Lenovo J606F and Xiaomi Elish BOE/CSOT variants. It supports both single-DSI and dual-DSI topologies and hides variant differences behind `struct panel_desc`.

Important APIs, types, and functions: `struct panel_info` stores the `drm_panel`, up to two `mipi_dsi_device` links, reset GPIO, `vddio`, orientation, and optional DCS backlight. `struct panel_desc` provides timings, DSI lanes/format/mode flags, device info for the second DSI, and the variant init callback. Main functions are `nt36523_probe()`, `nt36523_prepare()`, `nt36523_disable()`, `nt36523_unprepare()`, `nt36523_get_modes()`, and the variant command sequences `elish_boe_init_sequence()`, `elish_csot_init_sequence()`, and `j606f_boe_init_sequence()`.

Control flow: probe allocates the panel, gets `vddio` and reset GPIO, loads match data, optionally follows OF graph port 1 to register the secondary DSI device, reads panel orientation, sets `prepare_prev_first`, wires backlight, adds the panel, configures all DSI links, and attaches them. Prepare enables `vddio`, toggles reset, then runs the descriptor init sequence. Disable sends display-off and sleep-mode to each active DSI link; unprepare asserts reset and disables power.

State and persistence: no disk state. Runtime state is descriptor selection, DSI link array, orientation, and backlight object. The DCS brightness handlers temporarily clear `MIPI_DSI_MODE_LPM` and restore it after large-brightness transactions.

Dependencies and integration points: integrates with DRM panel, MIPI DSI, OF graph, regulator, GPIO, orientation, and backlight frameworks. Compatible strings are `lenovo,j606f-boe-nt36523w`, `xiaomi,elish-boe-nt36523`, and `xiaomi,elish-csot-nt36523`.

Risks and test signals: dual-DSI probe depends on valid graph wiring and secondary host availability. The magic vendor command sequences and reset timings are fragile. Attach failure after `drm_panel_add()` removes no panel in this function, so host attach paths deserve probe/remove stress testing. Test with DT binding validation, dual-DSI probe deferral, mode enumeration, suspend/resume, DCS backlight read/write, and panel orientation reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672a.c

Purpose: descriptor-driven DRM MIPI-DSI driver for Novatek NT36672A-based Tianma FHD+ video panels, with comments noting use in some Xiaomi/Poco F1 variants and possible extension to related NT37762A panels.

Important APIs, types, and functions: `struct nt36672a_panel_desc` carries the display mode, physical size, DSI configuration, and split on/off command arrays. `struct nt36672a_panel` stores the `drm_panel`, DSI link, descriptor, regulator bulk data, and reset GPIO. Core functions are `nt36672a_panel_probe()`, `nt36672a_panel_add()`, `nt36672a_panel_prepare()`, `nt36672a_panel_unprepare()`, `nt36672a_panel_power_on()`, `nt36672a_panel_power_off()`, `nt36672a_send_cmds()`, and `nt36672a_panel_get_modes()`.

Control flow: probe allocates panel state, fetches OF match data, copies descriptor DSI mode flags/format/lanes into the DSI device, registers state with `mipi_dsi_set_drvdata()`, calls add, then attaches to the host. Add configures three regulators (`vddio`, `vddpos`, `vddneg`) with load hints, gets reset GPIO, binds an OF backlight, and adds the DRM panel. Prepare enables regulators, applies a long reset sequence, sends first init commands, exits sleep, enables display, sends trailing commands, then waits. Unprepare sends panel off commands, forces display-off and sleep-mode even after prior command errors, waits DCS-specified delays, then powers off.

State and persistence: state is fully volatile. The descriptor and regulator arrays define all panel behavior; no cached mode changes or persisted settings exist.

Dependencies and integration points: DRM panel, MIPI DSI, regulator bulk, GPIO, OF match data, and DRM panel backlight. The sole compatible is `tianma,fhd-video`.

Risks and test signals: reset delays are intentionally inflated to avoid white-screen failures, so timing changes are risky. Command arrays use fixed two-byte DCS buffers; extending to wider commands requires changing `struct nt36672a_panel_cmd`. Probe cleanup detaches/removes on attach failure, but regulator rollback on prepare command failure only resets GPIO, relying on later unprepare. Test probe deferral, regulator failures, DSI attach/detach, mode timing at 1080x2246, backlight acquisition, and suspend/resume with repeated prepare/unprepare cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672e.c

Purpose: DRM MIPI-DSI panel driver for Novatek NT36672E panels, centered on a 1080x2408 60 Hz FHD+ configuration with vendor page-switch command programming.

Important APIs, types, and functions: `struct panel_desc` carries fixed mode, physical dimensions, DSI flags, format, lanes, panel name, and an init-sequence callback. `struct nt36672e_panel` keeps `drm_panel`, `mipi_dsi_device`, reset GPIO, three regulator supplies, and descriptor. Key functions include `nt36672e_1080x2408_60hz_init()`, `nt36672e_power_on()`, `nt36672e_power_off()`, `nt36672e_on()`, `nt36672e_off()`, panel prepare/unprepare, get-modes, probe, and remove.

Control flow: probe allocates panel state, validates match data, fills supplies from `vddi`, `avdd`, and `avee` with load hints, gets reset GPIO, configures DSI lanes/format/mode flags, binds OF backlight, marks `prepare_prev_first`, adds the panel, then attaches. Prepare enables all regulators, performs the documented out/in/out reset pulse, sends the descriptor init sequence in low-power mode, exits sleep, turns the display on, and waits. Unprepare sends display-off and sleep-mode with low-power cleared, then disables regulators and drives reset low.

State and persistence: no persistent state. Runtime state is descriptor data and current DSI mode flags. Error accumulation uses `mipi_dsi_multi_context`; prepare rolls power off if `nt36672e_on()` fails.

Dependencies and integration points: DRM panel, MIPI DSI multi-context helpers, regulator bulk, GPIO, OF, and panel backlight. Compatible string is `novatek,nt36672e`.

Risks and test signals: the long page-based vendor init sequence has no independent validation in the driver. `nt36672e_panel_unprepare()` ignores the return from `nt36672e_off()` and returns success after best-effort power-off, which can hide DSI failures. Test should cover regulator sequencing, reset polarity, DSI command error injection, 1080x2408 mode export, backlight phandle handling, attach failure cleanup, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt36672e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt37700f.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt37700f.c

Purpose: generated DRM MIPI-DSI driver for a Tianma panel using Novatek NT37700F command sequences, exposing a 1080x2160 60 Hz DSI panel and a DCS-backed raw backlight.

Important APIs, types, and functions: `struct nt37700f_tianma` contains the DRM panel, DSI device, single `power` regulator, and reset GPIO. Main functions are `nt37700f_tianma_probe()`, `nt37700f_tianma_prepare()`, `nt37700f_tianma_disable()`, `nt37700f_tianma_unprepare()`, `nt37700f_tianma_on()`, `nt37700f_tianma_get_modes()`, and the backlight ops.

Control flow: probe allocates with `devm_kzalloc()`, obtains the regulator and reset GPIO, sets DSI lanes to 4, RGB888 format, burst/non-continuous/LPM flags, initializes and adds the DRM panel, creates a DCS large-brightness backlight with 2047 max, then attaches. Prepare enables the supply, toggles reset, and runs a vendor DCS page sequence that sets address windows, control display, tearing, exits sleep, and turns display on. Disable sends display-off then sleep-mode. Unprepare asserts reset and disables the regulator.

State and persistence: no persistent state. The backlight handlers mutate `dsi->mode_flags` around brightness transactions by clearing and restoring `MIPI_DSI_MODE_LPM`.

Dependencies and integration points: DRM panel, MIPI DSI DCS helpers, DRM probe helper fixed-mode path, regulator, GPIO, and backlight core. Compatible string is `novatek,nt37700f`.

Risks and test signals: prepare failure after regulator enable asserts reset but does not disable the regulator, so error-path tests are important. The display mode is marked driver type but not preferred in the mode literal, relying on fixed-mode helper behavior. DCS backlight assumes large-brightness support. Test signals include DSI attach/detach, regulator failure injection, reset timing validation, brightness get/set, display-off/sleep ordering, and 1080x2160 mode enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt37700f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt37801.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt37801.c

Purpose: DRM MIPI-DSI driver for Novatek NT37801/NT37810 AMOLED panels requiring Display Stream Compression. It exposes a 1440x3200 120 Hz mode and configures DSC unconditionally.

Important APIs, types, and functions: `struct novatek_nt37801` stores the DRM panel, DSI device, `drm_dsc_config`, reset GPIO, and regulator bulk pointer. Core functions are `novatek_nt37801_probe()`, `novatek_nt37801_prepare()`, `novatek_nt37801_unprepare()`, `novatek_nt37801_on()`, `novatek_nt37801_off()`, `novatek_nt37801_get_modes()`, and DCS backlight update.

Control flow: probe allocates panel state, obtains constant supplies `vddio`, `vci`, and `vdd`, gets reset GPIO, configures four-lane RGB888 DSI with no-EOT and non-continuous clock flags, marks `prepare_prev_first`, registers a raw 12-bit DCS backlight, adds the panel, fills `dsi->dsc` with DSC 1.1 parameters, and attaches. Prepare enables regulators, resets the panel, sends vendor command pages, packs and transmits a PPS, enables DSI compression mode, and waits. Unprepare sends display-off/sleep-mode, asserts reset, and disables regulators.

State and persistence: no durable state. The important runtime state is `ctx->dsc` and `dsi->dsc`, which must remain valid for the host while attached. Backlight writes temporarily leave low-power mode.

Dependencies and integration points: DRM panel, MIPI DSI, DRM DSC helper, regulator bulk const API, GPIO, backlight, and fixed-mode helper. Compatible string is `novatek,nt37801`.

Risks and test signals: DSC parameters are hard-coded and must match host capabilities and panel firmware. Compression enable happens after panel command init, so PPS and compression command failures must power down cleanly. The driver does not expose non-DSC fallback. Test with a DSI host that validates DSC, 1440x3200@120 mode timing, PPS transmission, compression enable, brightness update, regulator failure rollback, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt37801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt39016.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt39016.c

Purpose: SPI-controlled DRM DPI panel driver for Novatek NT39016 TFT LCD controllers, currently matched to Kingdisplay KD035G6-54NT 320x240 panels with 50 Hz and 60 Hz modes.

Important APIs, types, and functions: `enum nt39016_regs` names controller registers. `struct nt39016_panel_info` carries mode table, dimensions, bus format, and bus flags. `struct nt39016` stores `drm_panel`, regmap, regulator, panel info, and reset GPIO. Key functions are `nt39016_probe()`, `nt39016_prepare()`, `nt39016_enable()`, `nt39016_disable()`, `nt39016_unprepare()`, and `nt39016_get_modes()`.

Control flow: probe allocates a DPI panel, reads OF match data, gets `power` regulator and reset GPIO, configures SPI as 8-bit mode 3 3-wire, initializes a regmap with 6-bit register and 8-bit value fields, binds optional backlight, and adds the panel. Prepare enables power, pulses reset, then writes the initialization register table through `regmap_multi_reg_write()`. Enable writes `NT39016_REG_SYSTEM` with reset-not and standby bits, and waits before backlight use. Disable clears standby, while unprepare asserts reset and disables power.

State and persistence: no durable state. Regmap uses `REGCACHE_FLAT`, so register values are cached in memory; hardware is reinitialized on prepare.

Dependencies and integration points: DRM panel over DPI, SPI, regmap, regulator, GPIO, media bus formats, and optional OF backlight. Compatible string is `kingdisplay,kd035g6-54nt`.

Risks and test signals: regmap access restrictions must align with the controller protocol. Remove calls disable/unprepare after panel removal, which can report errors if hardware is already off. SPI mode and 3-wire support are host-dependent. Test SPI setup, regmap writes, reset pulse timing, both display modes, bus format `MEDIA_BUS_FMT_RGB888_1X24`, backlight delay, and remove after failed/partial prepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt39016.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-olimex-lcd-olinuxino.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-olimex-lcd-olinuxino.c

Purpose: I2C-described DRM DPI panel driver for Olimex LCD-OLinuXino modules. Instead of hard-coded timings, it reads a 256-byte panel EEPROM over I2C and builds DRM modes from that data.

Important APIs, types, and functions: packed `struct lcd_olinuxino_eeprom` contains header, ID, revision, serial, panel info, up to four serialized mode records in `reserved`, and CRC checksum. `struct lcd_olinuxino` holds the DRM panel, I2C client, mutex, regulator, enable GPIO, and EEPROM copy. Core functions are `lcd_olinuxino_probe()`, `lcd_olinuxino_prepare()`, `lcd_olinuxino_unprepare()`, and `lcd_olinuxino_get_modes()`.

Control flow: probe verifies I2C functionality, allocates a DPI panel, initializes a mutex, reads 256 EEPROM bytes in SMBus block chunks, validates CRC32 and magic header, logs name/revision/serial, caps `num_modes` to four, obtains `power` regulator and `enable` GPIO, binds OF backlight, and adds the panel. Prepare enables the regulator and enable GPIO. Unprepare clears enable GPIO and disables power. Get-modes decodes each stored timing record into a DRM mode, marks the first preferred, and copies width, height, bpc, bus format, and bus flags from EEPROM.

State and persistence: the panel module EEPROM is persistent hardware data; the driver caches it in memory at probe and does not reread on each mode query. No software persistence is used.

Dependencies and integration points: I2C/SMBus, CRC32, mutex, regulator, GPIO, DRM panel, video timing concepts, media bus format values carried from EEPROM, and OF backlight. Compatible string is `olimex,lcd-olinuxino`.

Risks and test signals: EEPROM content is trusted after checksum, including mode arithmetic and bus flags. The mode data is read from `reserved` by casting, so struct layout and endianness are ABI-like. Test corrupted checksum/header, overlarge mode count, short I2C reads, backlight phandle errors, enable sequencing, and multiple EEPROM configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-olimex-lcd-olinuxino.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-ota5601a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-ota5601a.c

Purpose: SPI/regmap DRM DPI panel driver for Orisetech OTA5601A controllers, currently used for FocalTech GPT3-compatible 640x480 panels.

Important APIs, types, and functions: `struct ota5601a_panel_info` defines mode table, dimensions, bus format, and bus flags. `struct ota5601a` stores the DRM panel, regmap, regulator, panel info, and reset GPIO. Major functions are `ota5601a_probe()`, `ota5601a_prepare()`, `ota5601a_enable()`, `ota5601a_disable()`, `ota5601a_unprepare()`, and `ota5601a_get_modes()`.

Control flow: probe obtains panel info from the SPI device ID table, gets the `power` regulator and reset GPIO, configures SPI mode 3 3-wire, creates an 8-bit regmap, binds OF backlight, and adds the panel. Prepare enables power, applies reset timing, writes the register initialization table, and waits 120 ms. Enable writes `OTA5601A_CTL_ON`; disable writes `OTA5601A_CTL_OFF`; unprepare asserts reset and disables the regulator. Get-modes exports both 60 Hz and 50 Hz 640x480 timings and display bus metadata.

State and persistence: no persistent software state. Register programming is reapplied during prepare; regmap stores only volatile in-memory transaction state.

Dependencies and integration points: SPI core, regmap, regulator, GPIO, DRM panel, media bus format, and OF/SPI matching. Compatible is `focaltech,gpt3`, with SPI ID `gpt3`.

Risks and test signals: OF matching supplies no `.data`, so the driver depends on SPI ID data being available; platforms relying only on OF modalias behavior need confirmation. Remove calls disable and unprepare after removing the panel. SPI 3-wire support and timing values are hardware-sensitive. Test SPI ID matching, register init failures, 50/60 Hz mode export, backlight delay, bus flags, reset polarity, and power-off cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-ota5601a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-otm8009a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-otm8009a.c

Purpose: DRM MIPI-DSI driver for Orise Tech OTM8009A panels, providing two 480x800 modes and a DSI-command-based raw backlight implementation.

Important APIs, types, and functions: `struct otm8009a` stores device, DRM panel, backlight device, reset GPIO, regulator, and `prepared` flag. Large MCS command macros encode address-shifted manufacturer commands. Core functions are `otm8009a_probe()`, `otm8009a_init_sequence()`, `otm8009a_prepare()`, `otm8009a_enable()`, `otm8009a_disable()`, `otm8009a_unprepare()`, `otm8009a_get_modes()`, and `otm8009a_backlight_update_status()`.

Control flow: probe allocates the panel, gets optional reset GPIO and `power` regulator, configures two-lane RGB888 DSI video burst with LPM and non-continuous clock, registers an internal raw backlight, adds the panel, and attaches. Prepare enables power, toggles reset, sends a long manufacturer initialization sequence, exits sleep, sets address windows/pixel format/CABC, turns display on, starts memory write, and marks `prepared`. Enable turns the internal backlight on. Disable disables the backlight, then sends display-off and sleep-mode. Unprepare asserts reset, disables power, and clears `prepared`.

State and persistence: no durable state. The `prepared` flag prevents DSI brightness writes before panel initialization. Backlight properties hold volatile brightness/power state.

Dependencies and integration points: DRM panel, MIPI DSI, regulator, optional GPIO, backlight core, and OF match `orisetech,otm8009a`.

Risks and test signals: if `otm8009a_init_sequence()` fails, prepare returns without disabling the regulator, so error rollback is incomplete. `get_modes()` copies physical size from the last duplicated mode pointer after the loop, which is safe only because both mode entries use the same size. Test command failure paths, backlight before prepare, mode ordering/preferred flag, regulator rollback, reset-optional systems, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-otm8009a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-osd-osd101t2587-53ts.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-osd-osd101t2587-53ts.c

Purpose: small DRM MIPI-DSI video panel driver for the OSD Displays OSD101T2587-53TS 10.1-inch 1920x1200 panel.

Important APIs, types, and functions: `struct osd101t2587_panel` holds a DRM panel, DSI device, `power` regulator, and default mode pointer. Key functions are `osd101t2587_panel_probe()`, `osd101t2587_panel_add()`, `osd101t2587_panel_prepare()`, `osd101t2587_panel_enable()`, `osd101t2587_panel_disable()`, `osd101t2587_panel_unprepare()`, and `osd101t2587_panel_get_modes()`.

Control flow: probe matches the OF node to retrieve mode data, configures four-lane RGB888 DSI video burst/sync-pulse/no-EOT flags, allocates panel state, stores the default mode, adds the panel, and attaches to the DSI host. Prepare enables the regulator. Enable calls `mipi_dsi_turn_on_peripheral()`. Disable calls `mipi_dsi_shutdown_peripheral()`. Unprepare disables the regulator. Get-modes duplicates the fixed WUXGA timing and sets physical dimensions to 217 mm by 136 mm.

State and persistence: no persistent state and minimal runtime state. The mode pointer is set once from OF match data.

Dependencies and integration points: DRM panel, MIPI DSI peripheral helpers, regulator framework, OF match table, and optional OF backlight. Compatible string is `osddisplays,osd101t2587-53ts`.

Risks and test signals: the driver has no reset GPIO or custom command sequence, relying on generic peripheral on/off behavior. It does not set explicit mode type preferred in `get_modes()`. Attach failure removes the panel but no DSI detach path is needed because attach failed. Test regulator enable/disable, generic DSI peripheral commands on the target host, WUXGA timing, backlight phandle handling, and repeated enable/disable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-osd-osd101t2587-53ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-panasonic-vvx10f034n00.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-panasonic-vvx10f034n00.c

Purpose: DRM MIPI-DSI panel driver for Panasonic VVX10F034N00 / Novatek NT1397-based WUXGA 1920x1200 video-mode panels.

Important APIs, types, and functions: `struct wuxga_nt_panel` stores DRM panel, DSI device, `power` regulator, `earliest_wake`, and mode pointer. Main functions are `wuxga_nt_panel_probe()`, `wuxga_nt_panel_add()`, `wuxga_nt_panel_prepare()`, `wuxga_nt_panel_disable()`, `wuxga_nt_panel_unprepare()`, `wuxga_nt_panel_get_modes()`, and helper `wuxga_nt_panel_on()`.

Control flow: probe configures four-lane RGB888 DSI video mode with HSE, non-continuous clock, and LPM, allocates panel state, gets power/backlight, adds the panel, and attaches. Prepare enforces the panel’s minimum 500 ms off-time using `earliest_wake`, enables the regulator, waits 250 ms for command readiness, then calls `mipi_dsi_turn_on_peripheral()`. Disable shuts down the DSI peripheral. Unprepare disables power and records the next permitted wake time. Get-modes duplicates the fixed WUXGA timing and sets dimensions.

State and persistence: no durable state, but `earliest_wake` is important volatile timing state that survives between unprepare and the next prepare within the device lifetime.

Dependencies and integration points: DRM panel, MIPI DSI peripheral helpers, regulator, ktime, OF backlight, and OF match `panasonic,vvx10f034n00`.

Risks and test signals: the lack of reset pin makes off-time enforcement critical; tests should verify immediate re-enable waits correctly. The mode pointer field is set but `get_modes()` uses the static mode directly. Test DSI host support for turn-on/shutdown peripheral commands, regulator failures, wake-delay math, suspend/resume, and WUXGA mode export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-panasonic-vvx10f034n00.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raspberrypi-touchscreen.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raspberrypi-touchscreen.c

Purpose: Raspberry Pi 7-inch touchscreen panel driver. The hardware combines a DPI LCD, Toshiba TC358762 DSI-to-DPI bridge, and I2C Atmel ATTINY88 microcontroller; the driver presents a DRM DSI panel while coordinating both I2C power/PWM and a synthetic DSI device.

Important APIs, types, and functions: `struct rpi_touchscreen` holds the DRM panel, DSI device, and I2C client. Register defines cover ATTINY I2C registers and Toshiba bridge DSI/PPI/LCDC registers. Key functions are I2C read/write helpers, `rpi_touchscreen_write()` for generic DSI bridge writes, panel prepare/enable/disable/get-modes, I2C probe/remove, `rpi_touchscreen_dsi_probe()`, and custom module init/exit registering both drivers.

Control flow: I2C probe allocates the panel, validates ATTINY firmware ID, powers the panel off, discovers the DSI host via OF graph, registers a DSI child device named `rpi-ts-dsi`, then adds the panel. The DSI driver probe configures one-lane RGB888 video sync-pulse LPM and attaches. Prepare powers on through I2C, polls `REG_PORTB`, programs TC358762 bridge registers over generic DSI writes, and starts PPI/DSI. Enable sets PWM to 255 and default horizontal flip. Disable sets PWM and power off.

State and persistence: no persisted software state. Hardware microcontroller and bridge registers hold volatile configuration after prepare.

Dependencies and integration points: I2C/SMBus, OF graph, MIPI DSI host/device registration, DRM panel, media bus format, and module lifecycle. Compatible string is `raspberrypi,7inch-touchscreen-panel`; DSI child driver name is `rpi-ts-dsi`.

Risks and test signals: the power-on poll has no delay and no timeout error if the bit never appears; DSI generic writes ignore return values. Remove detaches and unregisters the synthetic DSI device. Test firmware revision detection, graph probe deferral, DSI child attach, bridge register programming, PWM/backlight behavior, mode 800x480 export, and remove ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raspberrypi-touchscreen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67191.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67191.c

Purpose: DRM MIPI-DSI driver for Raydium RM67191 1080x1920 panels, with a long vendor manufacturer command set and an internal DCS backlight.

Important APIs, types, and functions: `struct cmd_set_entry` stores command/parameter pairs. `struct rad_panel` stores DRM panel, DSI, optional reset GPIO, backlight, regulator bulk data, supply count, and `prepared`. Important functions include `rad_panel_probe()`, `rad_init_regulators()`, `rad_panel_prepare()`, `rad_panel_enable()`, `rad_panel_disable()`, `rad_panel_unprepare()`, `rad_panel_push_cmd_list()`, `color_format_from_dsi_format()`, and backlight ops.

Control flow: probe allocates panel state, configures RGB888 video flags, optionally reads `video-mode`, requires `dsi-lanes`, registers reset GPIO and raw backlight, gets `v3p3` and `v1p8` supplies, adds the panel, then attaches. Prepare enables regulators and toggles reset, then marks `prepared`. Enable switches to LPM, sends manufacturer commands, returns to user command set, soft-resets, sets DSI mode, tearing, tear scanline, pixel format, exits sleep, turns display on, and enables backlight. Disable disables backlight, sends display-off and sleep-mode. Unprepare toggles reset specially to keep touch active, disables regulators, and clears `prepared`.

State and persistence: no durable state. `prepared` gates backlight get/set. DSI mode flags are changed during enable and backlight operations.

Dependencies and integration points: DRM panel, MIPI DSI DCS/generic writes, regulator bulk, GPIO, backlight, OF properties `video-mode` and `dsi-lanes`, and media bus formats. Compatible string is `raydium,rm67191`.

Risks and test signals: `dsi-lanes` is mandatory and can block probe. Backlight functions clear LPM but do not restore it, unlike other drivers. The reset release during unprepare is designed for touch-controller access and must be board-validated. Test all `video-mode` values, lane property errors, brightness before/after prepare, regulator rollback, touch behavior after display off, and mode/bus-format reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67191.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67200.c

Purpose: descriptor-driven DRM MIPI-DSI driver for Raydium RM67200-equipped panels, currently the Wanchanglong W552793BAA 1080x1920 panel.

Important APIs, types, and functions: `struct raydium_rm67200_panel_info` contains the fixed mode, regulator list, regulator count, and setup callback. `struct raydium_rm67200` stores DRM panel, panel info, DSI, reset GPIO, and supplies. Key functions are `raydium_rm67200_probe()`, `raydium_rm67200_prepare()`, `raydium_rm67200_disable()`, `raydium_rm67200_unprepare()`, `raydium_rm67200_get_modes()`, and the long `w552793baa_setup()` sequence.

Control flow: probe allocates panel state, gets match data, obtains the descriptor’s supplies (`vdd`, `iovcc`, `vsp`, `vsn`), optionally gets reset GPIO, configures four-lane RGB888 DSI video burst LPM, marks `prepare_prev_first`, binds OF backlight, adds the panel, and attaches. Prepare enables supplies, resets, waits, runs the panel setup command sequence through generic writes, exits sleep, turns display on, and waits. Disable sends display-off and sleep-mode. Unprepare asserts reset, disables supplies, and waits.

State and persistence: no persistent state. Runtime behavior is entirely descriptor-driven, so additional RM67200 variants can be added by new `panel_info` records.

Dependencies and integration points: DRM panel, MIPI DSI multi-context generic writes, regulator bulk const API, optional GPIO, OF backlight, fixed-mode helper, and device property match data. Compatible string is `wanchanglong,w552793baa`.

Risks and test signals: `raydium_rm67200_prepare()` ignores `mctx.accum_err` and returns 0 even if setup or DCS commands fail, so DSI error propagation is weak. Optional reset handling is partly guarded in reset but unprepare unconditionally calls `gpiod_set_value_cansleep(ctx->reset_gpio, 1)`, which must be checked for NULL safety expectations. Test command-error injection, optional reset absent, regulator sequencing, backlight binding, fixed mode, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm67200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm68200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm68200.c

Purpose: DRM MIPI-DSI panel driver for Raydium RM68200 720x1280 panels with manufacturer command-page initialization.

Important APIs, types, and functions: `struct rm68200` contains device, DRM panel, reset GPIO, and power regulator. DCS helpers `rm68200_dcs_write_buf()` and `rm68200_dcs_write_cmd()` wrap writes with ratelimited errors. Macros `dcs_write_seq` and `dcs_write_cmd_seq` encode normal and per-address command writes. Main functions are `rm68200_probe()`, `rm68200_prepare()`, `rm68200_unprepare()`, `rm68200_init_sequence()`, and `rm68200_get_modes()`.

Control flow: probe allocates the DSI panel, gets optional reset GPIO and `power` regulator, configures two-lane RGB888 DSI video burst LPM non-continuous clock, binds OF backlight, adds panel, and attaches. Prepare enables power, toggles reset if present, sends a multi-page manufacturer sequence, exits sleep, waits, turns display on, and waits. Unprepare sends display-off and sleep-mode with warnings on failure, waits, asserts reset if present, and disables power. Get-modes exports the single 720x1280 timing.

State and persistence: no persistent state. Initialization is replayed on each prepare. The helper write errors are logged but `rm68200_init_sequence()` itself does not accumulate or return failures.

Dependencies and integration points: DRM panel, MIPI DSI, regulator, optional GPIO, OF backlight, and fixed panel mode. Compatible string is `raydium,rm68200`.

Risks and test signals: command write failures during the manufacturer init sequence are not propagated, so prepare can continue to sleep-exit/display-on after failed setup. Optional reset and regulator sequencing are board-sensitive. Test DSI error handling, power failure rollback, 720x1280 mode export, backlight phandle, attach failure cleanup, and suspend/resume under command-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm68200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm692e5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm692e5.c

Purpose: generated DRM MIPI-DSI driver for RM692E5-equipped AMOLED panels, specifically `fairphone,fp5-rm692e5-boe`, using DSC and a 1224x2700 90 Hz mode.

Important APIs, types, and functions: `struct rm692e5_panel` stores DRM panel, DSI device, `drm_dsc_config`, three regulators, and reset GPIO. Core functions are `rm692e5_probe()`, `rm692e5_prepare()`, `rm692e5_disable()`, `rm692e5_unprepare()`, `rm692e5_on()`, `rm692e5_get_modes()`, and DCS large-brightness backlight ops.

Control flow: probe sets supplies `vddio`, `dvdd`, and `vci`, gets reset GPIO, configures four-lane RGB888 DSI with no-EOT and non-continuous clock, sets `prepare_prev_first`, creates a raw 4095-level DCS backlight, adds the panel, assigns `dsi->dsc`, fills DSC 1.1 parameters, and attaches. Prepare enables regulators, toggles reset, sends vendor generic command pages, exits sleep/display-on, packs and sends DSC PPS, enables DSC compression, waits, switches to a command page to select 90 Hz, and returns accumulated errors. Disable leaves LPM, switches page 0, sends display-off and sleep-mode. Unprepare asserts reset and disables regulators.

State and persistence: no durable state. `ctx->dsc` is the key runtime configuration shared with the DSI host. Backlight get/set toggles LPM around DCS brightness transactions.

Dependencies and integration points: DRM panel, MIPI DSI, DRM DSC helpers, regulator bulk, GPIO, backlight, and OF match `fairphone,fp5-rm692e5-boe`.

Risks and test signals: the comment notes a TODO for `slice_per_pkt = 2`, so DSC host interoperability is a risk. The mode is 90 Hz and prepare explicitly selects 90 Hz with `0xbd = 0x05`. Test DSC PPS/compression, refresh-rate command, brightness read/write, regulator rollback on accumulated errors, attach failure, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm692e5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm69380.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm69380.c

Purpose: DRM MIPI-DSI driver for Raydium RM69380-equipped Lenovo J716F EDO panels, supporting optional dual-DSI attachment and a 2560x1600 90 Hz mode.

Important APIs, types, and functions: `struct rm69380_panel` contains DRM panel, two possible DSI links, two regulators (`vddio`, `avdd`), and reset GPIO. Main functions are `rm69380_probe()`, `rm69380_prepare()`, `rm69380_unprepare()`, `rm69380_on()`, `rm69380_off()`, `rm69380_get_modes()`, and DCS large-brightness backlight ops.

Control flow: probe allocates state, gets supplies and reset GPIO, checks OF graph port 1 for a secondary DSI host and registers a second DSI device when present, sets drvdata on DSI links, marks `prepare_prev_first`, creates a raw DCS backlight, adds the panel, then iterates over existing DSI links to configure four-lane RGB888 burst/non-continuous flags and attach. Prepare enables both supplies, resets, sends DCS page commands on DSI0, enables LPM on both links, exits sleep, and turns display on. Unprepare sends display-off/sleep through DSI0, asserts reset, and disables regulators.

State and persistence: no persistent state. Runtime state is the two-element DSI array and DSI mode flags on both links. Brightness operations act on the primary DSI link.

Dependencies and integration points: DRM panel, MIPI DSI, OF graph, regulator bulk, GPIO, fixed-mode helper, and backlight. Compatible string is `lenovo,j716f-edo-rm69380`.

Risks and test signals: command traffic is only sent through primary DSI, so dual-link panel synchronization depends on host/panel behavior. Attach loop removes the panel on attach failure. The module author string appears to miss a closing quote character in the literal content. Test single-link and dual-link DT graphs, secondary host deferral, brightness, fixed 90 Hz mode, regulator rollback, attach failure, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm69380.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r61307.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r61307.c

Purpose: DRM MIPI-DSI driver for Renesas R61307-based 768x1024 panels, matched to HIT and KOE TX13D100VM0EAA-compatible panels.

Important APIs, types, and functions: `struct renesas_r61307` stores DRM panel, DSI device, `vcc` and `iovcc` regulators, optional reset GPIO, and configuration booleans for contrast/inversion plus gamma index. `gamma_setting` contains selectable gamma tables. Main functions are `renesas_r61307_probe()`, `renesas_r61307_prepare()`, `renesas_r61307_enable()`, `renesas_r61307_disable()`, `renesas_r61307_unprepare()`, and get-modes.

Control flow: probe allocates state, gets regulators and optional reset GPIO, reads optional device properties `renesas,column-inversion`, `renesas,contrast`, and `renesas,gamma`, configures four-lane RGB888 video sync-pulse non-continuous LPM DSI, binds OF backlight, adds panel, and attaches with devm. Prepare enables `vcc`, then `iovcc`, waits between rails, and resets. Enable exits sleep, sets address mode and pixel format, disables manufacturer command protection, optionally programs contrast/gamma/inversion, re-enables protection, then turns display on. Disable sends display-off and sleep. Unprepare waits, asserts reset, then disables `iovcc` and `vcc`.

State and persistence: no durable state. Probe-time device properties persist in memory as booleans and gamma index, controlling enable-time command choices.

Dependencies and integration points: DRM panel, MIPI DSI multi-context writes, regulator framework, GPIO, generic device properties, OF backlight, and fixed-mode helper. Compatible strings are `hit,tx13d100vm0eaa` and `koe,tx13d100vm0eaa`.

Risks and test signals: `renesas,gamma` is not bounds-checked before indexing `gamma_setting`, so invalid DT values can read past the table. If `iovcc` enable fails, `vcc` is left enabled. Test property validation, regulator failure rollback, gamma variants, inversion/contrast branches, mode export, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r61307.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r69328.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r69328.c

Purpose: DRM MIPI-DSI driver for Renesas R69328-based JDI DX12D100VM0EAA-compatible 720x1280 panels.

Important APIs, types, and functions: `struct renesas_r69328` holds the DRM panel, DSI device, `vdd` and `vddio` regulators, and optional reset GPIO. Main functions are `renesas_r69328_probe()`, `renesas_r69328_prepare()`, `renesas_r69328_enable()`, `renesas_r69328_disable()`, `renesas_r69328_unprepare()`, `renesas_r69328_reset()`, and `renesas_r69328_get_modes()`.

Control flow: probe allocates the panel, gets `vdd` and `vddio`, gets optional reset GPIO, configures four-lane RGB888 video sync-pulse non-continuous LPM DSI, binds OF backlight, adds the panel, and attaches using devm. Prepare enables `vdd`, waits, enables `vddio`, waits, then toggles reset. Enable sets address mode and 24-bit pixel format, exits sleep, disables manufacturer access protection, writes power and three gamma tables, re-enables protection, turns display on, and waits. Disable sends display-off, waits, and enters sleep. Unprepare asserts reset, waits, then disables `vddio` and `vdd`.

State and persistence: no persistent state and no configurable runtime state beyond acquired resources and fixed mode.

Dependencies and integration points: DRM panel, MIPI DSI multi-context helpers, regulators, optional GPIO, OF backlight, and fixed-mode helper. Compatible string is `jdi,dx12d100vm0eaa`.

Risks and test signals: if enabling `vddio` fails after `vdd` is enabled, the code returns without disabling `vdd`. Vendor power/gamma tables are hard-coded. Test regulator failure rollback, optional reset absence, DSI command error propagation through `ctx.accum_err`, 720x1280 mode export, backlight phandle, attach failure cleanup, and suspend/resume timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-renesas-r69328.c -->
