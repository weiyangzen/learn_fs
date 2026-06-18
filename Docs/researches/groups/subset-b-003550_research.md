# Research: subset-b-003550

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it66121.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it66121.c

## Purpose

This file implements the ITE IT6610/IT66121/IT66122 HDMI transmitter DRM bridge. It drives the chip over I2C/regmap, attaches to a downstream HDMI connector/bridge, exposes HPD and EDID operations, programs RGB input and HDMI AVI infoframes during modeset, handles the analog front end, and optionally registers an HDMI codec device for I2S audio.

## Important APIs, Types, And Functions

The central state is `struct it66121_ctx`, which owns the regmap, DRM bridge, current connector pointer for ELD access, reset GPIO, bus width, chip id, a mutex guarding registers and mutable state, cached AVI infoframe state, and HDMI audio codec fields. `it66121_regmap_config` uses a 0x200 logical register space with bank selection through `IT66121_CLK_BANK_REG`. `it66121_chip_info` maps probed vendor/device IDs to `ID_IT6610`, `ID_IT66121`, and `ID_IT66122`.

Important bridge functions are `it66121_bridge_attach()`, `it66121_bridge_mode_set()`, `it66121_bridge_mode_valid()`, `it66121_bridge_detect()`, `it66121_bridge_edid_read()`, `it66121_bridge_hpd_enable()`, and atomic bus-format callbacks. The enable/disable callbacks mute and unmute video and maintain `ctx->connector`.

The EDID/DDC path is implemented by `it66121_preamble_ddc()`, `it66121_wait_ddc_ready()`, `it66121_abort_ddc_ops()`, and `it66121_get_edid_block()`, then exposed through `drm_edid_read_custom()`. Audio integration is handled by `it66121_audio_codec_init()` and `hdmi_codec_ops` callbacks: `it66121_audio_hw_params()`, `it66121_audio_startup()`, `it66121_audio_shutdown()`, `it66121_audio_mute()`, and `it66121_audio_get_eld()`.

## Control Flow

Probe validates I2C, allocates a DRM bridge, reads the input endpoint `bus-width`, finds the downstream bridge from port 1, enables `vcn33`, `vcn18`, and `vrf12`, toggles reset, initializes regmap, reads chip IDs, optionally requests the threaded IRQ, registers HDMI audio if `#sound-dai-cells` is present, and adds the DRM bridge. Attach requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, attaches the next bridge, powers clocks/AFE bits, releases resets, and waits for the transmitter to settle.

During modeset, `it66121_bridge_mode_set()` builds an AVI infoframe from the adjusted mode and current connector, writes the packet payload/checksum, enables HDMI mode, temporarily powers off TXCLK for IT66121/IT66122, configures RGB input/DDR mode from `bus_width`, configures the AFE according to pixel clock, and restores TXCLK. Atomic enable clears AV mute; atomic disable asserts AV mute.

EDID reads take the mutex, switch DDC master to host mode, select EDID DDC address, read 32-byte FIFO chunks, and abort DDC on timeout/error. The IRQ thread reads system and interrupt status, clears HPD interrupt/status bits, and calls `drm_bridge_hpd_notify()` after dropping the mutex.

## State And Persistence

Runtime state is in `it66121_ctx`; register access, audio setup, EDID reads, and IRQ status handling are serialized by `ctx->lock`. Hardware state persists in chip registers across callbacks until reset or overwritten: AVI packet registers, HDMI mode, mute state, AFE configuration, DDC command state, audio channel/N/CTS/channel-status registers, and IRQ masks. The driver does not implement runtime PM or suspend/resume; regulators are devm-enabled for the device lifetime. `ctx->connector` is transient and exists only while the bridge is atomically enabled.

## Dependencies And Integration Points

The driver depends on I2C, regmap, GPIO, regulator bulk enablement, OF graph, DRM bridge/atomic/EDID helpers, media bus formats, and `sound/hdmi-codec.h`. It integrates upstream with a parallel RGB or DDR RGB source and downstream with a bridge/connector found from DT port 1. Optional audio integration registers `HDMI_CODEC_DRV_NAME` and reads ELD from the active DRM connector.

## Risks And Edge Cases

The driver only supports 12-bit DDR and 24-bit RGB input and has TODOs for broader YCbCr and bus-format handling. `it66121_bridge_mode_set()` logs failures only implicitly through early exits and returns void, so modeset failures can be hard to propagate. EDID supports standard segment/block flow but depends on DDC status bits and abort sequencing. Audio N/CTS auto mode can poll for a long time while holding the mutex. The IRQ handler ignores non-HPD interrupt causes except clearing the global IRQ bit. Probe calls `it66121_audio_codec_init()` without acting on its return value, so audio init failure does not fail display probe.

## Test Signals

Useful tests include module build with DRM bridge and HDMI codec enabled, DT probe for all three compatible strings and both bus widths, HPD connect/disconnect IRQs, EDID reads including one extension block, 25 MHz to 148.5 MHz modes with 24-bit input and 74.25 MHz ceiling for 12-bit DDR input, bridge chaining with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, I2S playback at supported rates/widths, ELD reads while enabled/disabled, and reset/regulator failure-injection during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it66121.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8713sx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8713sx.c

## Purpose

This file implements a Lontium LT8713SX DRM bridge driver. Display-side bridge behavior is intentionally simple: it attaches a downstream bridge found from DT port 1 and advertises a DisplayPort connector type. Most file complexity is a sysfs-triggered firmware updater for the bridge's internal flash, including firmware loading, CRC preparation, SRAM staging, flash erase/write, and post-write CRC checks.

## Important APIs, Types, And Functions

`struct lt8713sx` stores the DRM bridge, next bridge, 16-bit paged regmap, `ocm_lock`, reset and enable GPIOs, firmware pointers/buffer, main CRC, bank CRC values, and bank count. `lt8713sx_regmap_config` exposes a 0x0000-0xffff logical register space through page register `0xff` and disables caching.

Firmware functions include `lt8713sx_prepare_firmware_data()`, `lt8713sx_firmware_update()`, `lt8713sx_firmware_upgrade()`, `lt8713sx_block_erase()`, `lt8713sx_write_data()`, `lt8713sx_load_main_fw_to_sram()`, `lt8713sx_load_bank_fw_to_sram()`, and result check helpers. The sysfs attribute is `lt8713sx_firmware` via `DEVICE_ATTR_WO()`. Bridge integration is `lt8713sx_bridge_attach()`.

## Control Flow

Probe validates I2C, allocates the bridge, initializes `ocm_lock` and regmap, finds the downstream panel/bridge on port 1, acquires reset/optional enable GPIOs, enables `vdd` then `vcc`, resets the chip, registers the bridge, and populates the CRC8 table.

Writing the sysfs attribute calls `lt8713sx_firmware_update()`: take `ocm_lock`, stop/enable host I2C access to the on-chip MCU, request `lt8713sx_fw.bin`, allocate a 256 KiB padded buffer, copy main firmware and bank firmware, append/compute CRCs, configure flash parameters, erase eight 32 KiB blocks, write 256-byte pages through SRAM to flash, validate main and bank CRCs by loading flash regions back to SRAM, disable I2C access, reset on success, and release firmware/buffer.

## State And Persistence

Firmware bytes are transient in `fw_buffer`, but successful writes persist in the chip's flash. `ocm_lock` serializes all register accesses that require stopping the on-chip MCU. Regmap has no cache, which is appropriate for firmware command/status registers. Regulators and GPIO state are device-managed; the optional enable GPIO is acquired high and not otherwise toggled after probe.

## Dependencies And Integration Points

The driver depends on I2C, firmware loading, CRC8, regmap, mutex guards, GPIO, regulators, DRM bridge, and OF graph bridge lookup. It exposes `MODULE_FIRMWARE("lt8713sx_fw.bin")`. The display pipeline depends on a downstream bridge/panel; no mode callbacks, EDID, HPD, or bus-format negotiation are implemented locally.

## Risks And Edge Cases

Firmware preparation assumes a main area of 64 KiB and bank granularity of 12 KiB. There is a potential boundary risk because `bank_crc_value` has 17 entries but firmware size checks allow nearly 256 KiB. Many low-level `regmap_write()` calls are unchecked, so flash operation failures may be detected only by CRC logging, and CRC mismatch helpers do not convert mismatch into a failing return. `lt8713sx_block_erase()` stops polling after a fixed count but does not report timeout. Sysfs update is a privileged destructive operation that can leave flash partially rewritten after power loss or I2C errors.

## Test Signals

Validate build coverage, DT probe, regulator/GPIO failures, bridge chaining, sysfs firmware update success/failure paths, missing/oversized firmware, flash busy timeout behavior, CRC mismatch handling, reset after update, repeated sysfs updates, and display operation before/after firmware update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8713sx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8912b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8912b.c

## Purpose

This driver supports the Lontium LT8912B bridge, converting MIPI DSI input to an HDMI output path with auxiliary LVDS-related programming. It registers a DRM bridge, attaches a DSI peripheral to the upstream DSI host, delegates EDID/HPD to the downstream HDMI connector bridge when available, and can create a connector itself when the upstream encoder does not request connectorless attachment.

## Important APIs, Types, And Functions

`struct lt8912` owns the DRM bridge and optional connector, two I2C clients/regmaps (`I2C_MAIN` at 0x48 and `I2C_CEC_DSI` at 0x49), the upstream DSI host node/device, reset GPIO, current `videomode`, seven regulators, DSI lane count, and `is_power_on`. Register programming is split across `lt8912_write_init_config()`, `lt8912_write_mipi_basic_config()`, `lt8912_write_dds_config()`, `lt8912_write_rxlogicres_config()`, `lt8912_write_lvds_config()`, and `lt8912_video_setup()`.

Bridge callbacks include attach/detach, mode_set, enable, mode_valid, detect, and edid_read. Connector helpers are `lt8912_connector_detect()` and `lt8912_connector_get_modes()`. PM callbacks are `lt8912_bridge_suspend()` and `lt8912_bridge_resume()`.

## Control Flow

Probe parses reset GPIO, data lanes from input endpoint, DSI host node from port 0, HDMI connector bridge from port 1, regulator names, initializes dummy I2C client 0x49, registers the bridge with EDID and detect ops, and attaches a DSI device with RGB888 video/LPM/no-EOT flags.

Attach first attaches the downstream bridge with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`. If a connector is requested, it initializes a connector, enables downstream HPD if supported, and attaches the encoder. Then it hard-powers the chip, deasserts reset, and runs soft power-on initialization. Mode set stores adjusted timings in `lt->mode`; enable programs video timings, DDS, RX logic reset, and LVDS/HDMI register sequences. Suspend powers off; resume powers on, reapplies soft config, and reruns video setup.

## State And Persistence

`lt->mode` persists the last adjusted mode for enable/resume. `is_power_on` prevents duplicate soft initialization and is cleared only by hard power-off. Regulator and reset state define hardware power state. Dummy I2C client lifetime is explicit and released in remove/error paths. Connector display info is updated from downstream EDID and bus format is forced to RGB888.

## Dependencies And Integration Points

The driver depends on DRM bridge/connector helpers, MIPI DSI registration, OF graph, regmap, GPIO, regulators, videomode conversion, and downstream HDMI connector bridge operations. It expects an `hdmi-connector` compatible node on output port 1 and a DSI host on input port 0.

## Risks And Edge Cases

Many register writes are ORed into a single return value, losing exact failure location. Hardcoded DDS/LVDS sequences may not fit all modes despite timing register updates. `lt8912_bridge_enable()` ignores `lt8912_video_on()` errors. DSI attach happens during probe, so probe ordering depends on DSI host availability. Connector init mixes self-created connector behavior with a downstream bridge and must keep HPD enable/disable balanced. Mode validation caps at 1920x1080 and 150 MHz.

## Test Signals

Exercise DT probe ordering with missing DSI host or connector, dummy I2C client creation/removal, all regulator failures, connectorless and connector-creating attach paths, HPD delegation, EDID mode enumeration, suspend/resume preserving the last mode, 720p/1080p modes, DSI lane counts 1-4, and power-cycle recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8912b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9211.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9211.c

## Purpose

This file implements the Lontium LT9211 bridge for a supported subset of the chip: MIPI DSI input to LVDS output. It handles DSI host attachment, LVDS panel/bridge discovery, dual-link LVDS pixel ordering, register initialization, RX autodetection, timing programming, PLL setup, and LVDS transmitter configuration in atomic enable/disable callbacks.

## Important APIs, Types, And Functions

`struct lt9211` contains the DRM bridge, device, paged regmap, DSI device, panel bridge, reset GPIO, `vccio` regulator, and LVDS dual-link flags. `lt9211_regmap_config` restricts read/write access to known register ranges and uses `REGCACHE_MAPLE`.

Core routines are `lt9211_read_chipid()`, `lt9211_system_init()`, `lt9211_configure_rx()`, `lt9211_autodetect_rx()`, `lt9211_configure_timing()`, `lt9211_configure_plls()`, `lt9211_configure_tx()`, `lt9211_atomic_enable()`, and `lt9211_atomic_disable()`. DT/DSI integration is split between `lt9211_parse_dt()` and `lt9211_host_attach()`.

## Control Flow

Probe holds reset low, parses `vccio`, dual-link LVDS port ordering from ports 2/3, and panel/bridge from port 2. It initializes regmap, adds the bridge, and attaches to a DSI host discovered from port 0. DSI is configured as RGB888 video sync-pulse mode with several no-HSA/HFP/HBP flags.

Atomic enable enables `vccio`, releases reset, inspects the negotiated output LVDS bus format and flags, finds the adjusted CRTC mode through connector state, verifies chip ID, initializes system/RX, autodetects the incoming DSI stream and checks active size, writes output timing, configures PLLs based on pixel clock, and enables LVDS TX with JEIDA/SPWG, 18/24 bpp, DE polarity, and dual-link ordering. Atomic disable asserts reset, disables `vccio`, and marks regcache dirty.

## State And Persistence

Persistent driver state is limited to DSI pointer, regmap, panel bridge, regulator/reset handles, and LVDS link flags. Hardware register configuration is rebuilt on every atomic enable after reset. Regcache is marked dirty on disable because reset/regulator-off invalidates cached hardware state.

## Dependencies And Integration Points

The driver integrates DRM bridge atomic state, MIPI DSI, DRM panel bridge helpers, OF graph LVDS dual-link helpers, media bus formats, GPIO, regulators, and regmap. The output bridge/panel must provide or tolerate LVDS format negotiation; unsupported formats fall back to SPWG24 with a warning.

## Risks And Edge Cases

Atomic enable returns void; failed register operations abort silently after logging and can leave the regulator on if a later step fails. RX autodetection requires live DSI input before proceeding and rejects unsupported pixel formats. Only pixel clocks 25-176 MHz are valid. The supported conversion mode is much narrower than the chip's hardware capabilities. Dual-link detection depends on correct DT graph ordering.

## Test Signals

Test single and dual-link LVDS DTs, odd/even and even/odd pixel ordering, panel and bridge outputs, all supported LVDS bus formats plus fallback, reset/regulator sequencing, chip ID failure, DSI stream autodetect mismatch, clock boundaries at 25/176 MHz, enable/disable cycles, and regcache behavior after disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611.c

## Purpose

This driver supports the Lontium LT9611 MIPI DSI to HDMI bridge. It handles one or two DSI inputs, HDMI HPD/EDID, mode programming, PLL/PCR setup, HDMI PHY and infoframes, and HDMI audio through DRM bridge HDMI audio callbacks.

## Important APIs, Types, And Functions

`struct lt9611` stores the bridge, next bridge, regmap, DSI endpoint nodes/devices, AC/DC HDMI PHY mode, reset/enable GPIOs, power/sleep flags, two regulators, cached connector status, and a 256-byte EDID buffer. The regmap uses page register `0xff`.

Configuration functions include `lt9611_mipi_input_analog()`, `lt9611_mipi_input_digital()`, `lt9611_mipi_video_setup()`, `lt9611_pll_setup()`, `lt9611_pcr_setup()`, `lt9611_hdmi_tx_digital()`, `lt9611_hdmi_tx_phy()`, and `lt9611_video_check()`. Bridge ops include detect, EDID, HPD enable, atomic pre_enable/enable/disable/post_disable, input bus format, HDMI infoframe write/clear hooks, TMDS rate validation, and HDMI audio startup/prepare/shutdown.

## Control Flow

Probe validates I2C, initializes regmap, parses DSI0/DSI1 endpoints and output bridge on port 2, gets GPIOs/regulators, asserts optional 5V enable, powers and resets the chip, reads revision, requests the threaded IRQ, disables the default audio infoframe, fills HDMI bridge metadata/audio capabilities, adds the bridge, attaches primary and optional secondary DSI devices, and enables HPD interrupts.

Atomic enable locates the active connector and adjusted mode, configures DSI input selection for single/dual/port-B modes, programs TX PLL postdivider based on pixel clock, writes MIPI timing registers, sets PCR, ensures chip power-on, configures analog MIPI input, updates HDMI infoframes, selects HDMI/DVI digital mode, configures PHY, waits, logs video check values, and enables HDMI output. Post-disable enters sleep setup; pre-enable exits sleep. EDID reading powers the chip and reads two 128-byte blocks through an internal DDC engine.

## State And Persistence

`power_on` and `sleep` prevent duplicate power setup and select resume behavior. `status` caches detect result. `edid_buf` stores the latest two-block EDID read. DSI endpoint references are retained until remove. Registers retain mode/audio/infoframe state until power-off, sleep, or reset.

## Dependencies And Integration Points

The driver integrates I2C/regmap, DRM bridge HDMI operations, DRM HDMI state helper, MIPI DSI, OF graph, GPIO, regulators, IRQs, and HDMI codec bridge callbacks. It attaches a downstream bridge found at DT port 2 and advertises `DRM_BRIDGE_OP_HDMI`, audio, SPD infoframe, EDID, detect, HPD, and modes.

## Risks And Edge Cases

EDID support is limited to base plus one extension block. Mode validation allows up to 3840 horizontal pixels but requires dual DSI for width above 2000 and caps TMDS at 297 MHz. Atomic enable can fail mid-sequence without rollback. IRQ handling reports HPD/video-input changes but does not inspect every error source. HDMI audio prepare only accepts 48 kHz and 96 kHz. DSI lanes are fixed to 4 in attach. Register writes are often unchecked.

## Test Signals

Validate single DSI0, single DSI1, and dual DSI routing; HPD IRQs; EDID reads; 1080p and 4K30 dual-port modes; HDMI versus DVI sink infoframe behavior; sleep/post-disable and pre-enable; 48/96 kHz HDMI audio; regulator/GPIO/IRQ failures; and removal after both DSI devices attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611uxc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611uxc.c

## Purpose

This file implements the Lontium LT9611UXC MIPI DSI to HDMI bridge. Compared with `lontium-lt9611.c`, more behavior is delegated to firmware; the driver mainly provides DSI attachment, fixed-mode validation, timing writes, HPD/EDID handling, HDMI audio notifications, and firmware update/readback through sysfs.

## Important APIs, Types, And Functions

`struct lt9611uxc` stores bridge state, regmap, `ocm_lock`, waitqueue/work item, DSI nodes/devices, GPIOs, regulators, HPD/EDID flags, HDMI connection state, and firmware version. `lt9611uxc_lock()` and `lt9611uxc_unlock()` stop/restart the on-chip MCU around register access by writing `0x80ee`.

The fixed mode table is `lt9611uxc_modes[]`; validation is `lt9611uxc_bridge_mode_valid()`. HDMI paths include detect, EDID wait/read, `hpd_notify`, and no-op audio prepare/shutdown. Firmware paths include `lt9611uxc_firmware_update()`, page read/write helpers, sysfs `lt9611uxc_firmware`, and automatic update when firmware version reads as zero.

## Control Flow

Probe validates I2C, allocates the bridge, initializes mutex/regmap, parses mandatory DSI0, optional DSI1, and output bridge, gets GPIOs/regulators, asserts optional 5V, powers and resets the chip, reads chip revision and firmware version, optionally updates firmware and retries version detection, initializes waitqueue/work, requests IRQ, sets bridge ops including HPD only for firmware version >= 0x40, adds the bridge, and attaches DSI devices.

IRQ handling locks the MCU, reads interrupt and HPD status, clears interrupt status, wakes EDID waiters on EDID-ready events, updates `hdmi_connected` and schedules HPD work on connect changes, then unlocks. EDID reads wait up to 500 ms for `edid_read`, then read one of two 128-byte blocks from internal memory. Mode set locks, writes timing registers, and unlocks.

Firmware update requests `lt9611uxc_fw.bin`, locks MCU, erases flash twice with long waits, writes 32-byte pages, reads back the image, compares it, unlocks, resets, and releases firmware.

## State And Persistence

`hdmi_connected` and `edid_read` are shared across IRQ, waitqueue, workqueue, detect, and EDID paths and are protected by `ocm_lock` when touching registers or shared connection state. Firmware writes persist in flash. `fw_version` is cached for sysfs display. DSI endpoint node references persist until remove. The driver does not perform detailed power state transitions on atomic enable/disable; firmware appears to manage most HDMI state.

## Dependencies And Integration Points

Dependencies include I2C/regmap, firmware loader, mutex/waitqueue/workqueue, IRQ, GPIO, regulators, OF graph, MIPI DSI, DRM bridge/EDID helpers, and HDMI audio notification helpers. It exposes `MODULE_FIRMWARE("lt9611uxc_fw.bin")` and a sysfs firmware attribute.

## Risks And Edge Cases

The firmware readback comparison appears inverted: `!memcmp(readbuf, fw->data, fw->size)` logs failure even when buffers match. EDID is only two blocks and depends on an interrupt-driven ready flag; stale `edid_read` state may affect later reads. HPD support depends on firmware version. Register access must consistently use MCU lock/unlock, and firmware update holds the MCU stopped for long erase/write periods. Mode support is a fixed whitelist. DSI lanes are fixed to 4.

## Test Signals

Test firmware version zero update path, manual sysfs update, readback comparison, HPD-supported and non-HPD firmware versions, EDID wait timeout and success, two-block EDID reads, fixed-mode whitelist rejection, DSI0-only and dual-DSI DTs, IRQ/workqueue teardown, HDMI audio plugged notifications, and regulator/GPIO/IRQ failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611uxc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lvds-codec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lvds-codec.c

## Purpose

`lvds-codec.c` is a generic DRM bridge driver for simple LVDS encoders and decoders that need power control and panel bridging but no register programming. It covers `lvds-decoder`, `lvds-encoder`, and `thine,thc63lvdm83d` compatibles.

## Important APIs, Types, And Functions

`struct lvds_codec` stores the device, DRM bridge, downstream panel bridge, bridge timings, `power` regulator, optional `powerdown` GPIO, connector type, and input bus format. Bridge ops are attach, enable, disable, atomic state helpers, and `atomic_get_input_bus_fmts()`.

Probe allocates the bridge, derives connector type from match data, gets the regulator/GPIO, finds the panel from output port 1, wraps it with `devm_drm_panel_bridge_add_typed()`, parses decoder data mapping for non-LVDS connector type, parses optional `pclk-sample` for LVDS encoders, attaches bridge timings, and registers the bridge.

## Control Flow

Attach simply attaches the wrapped panel bridge. Enable turns on the regulator and deasserts powerdown. Disable asserts powerdown then disables the regulator. Bus-format negotiation returns the configured LVDS/RGB input format.

## State And Persistence

There is no mutable display mode state. Persistent state is limited to regulator and GPIO power state plus the parsed bus format/timing flags. Hardware behavior is mostly strapped or board-defined.

## Dependencies And Integration Points

The driver depends on platform device probing, OF graph, GPIO, regulators, DRM bridge/panel helpers, LVDS data-mapping helpers, media bus formats, and DRM bus flags. It bridges a source on port 0 to a panel on port 1.

## Risks And Edge Cases

Missing `data-mapping` is only a warning for decoder-style use, leaving `bus_format` at zero if no legacy fallback applies. `pclk-sample` is only parsed for LVDS connector type. Enable failure leaves the bridge off but cannot propagate an error through the void bridge callback. The driver assumes the downstream panel is present at probe time.

## Test Signals

Validate all compatibles, panel probe deferral, missing/invalid `data-mapping`, `pclk-sample` flags, powerdown GPIO polarity, regulator enable/disable failures, and bus-format negotiation with panels requiring specific LVDS mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lvds-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/megachips-stdpxxxx-ge-b850v3-fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/megachips-stdpxxxx-ge-b850v3-fw.c

## Purpose

This board-specific driver models the GE B850v3 display pipeline containing two MegaChips devices with GE firmware: STDP4028 LVDS-to-DP and STDP2690 DP-to-DP++. The chips self-configure video; the driver exists to expose one DRM bridge/connector, read EDID through the STDP2690 I2C device, and handle HPD/link interrupts from the STDP4028 I2C device.

## Important APIs, Types, And Functions

`struct ge_b850v3_lvds` contains a DRM connector, DRM bridge, and two I2C client pointers. A global `ge_b850v3_lvds_ptr` plus `ge_b850v3_lvds_dev_mutex` coordinates the two independent I2C drivers until both physical devices are probed.

EDID functions are `stdp2690_read_block()`, `ge_b850v3_lvds_edid_read()`, and `ge_b850v3_lvds_get_modes()`. Detection is `ge_b850v3_lvds_bridge_detect()` using STDP4028 status. Connector creation is `ge_b850v3_lvds_create_connector()`. Registration is delayed until both `stdp4028_ge_b850v3_fw_probe()` and `stdp2690_ge_b850v3_fw_probe()` have run.

## Control Flow

Module init registers two I2C drivers. Each probe initializes or reuses the global bridge object, stores its I2C client, and returns early if the other half is not present. Once both are present, `ge_b850v3_register()` sets bridge ops/type/of_node, adds the bridge, clears pending STDP4028 interrupts, and requests the HPD IRQ if provided. Attach enables STDP4028 interrupt output and hotplug/link-change interrupts, then creates a DisplayPort connector unless connectorless attach was requested.

## State And Persistence

The singleton global object persists while both I2C devices are bound. Removal only tears down the DRM bridge when both client pointers are populated, avoiding double removal but also making global lifetime/order important. HPD interrupt enablement and pending status are stored in STDP4028 registers. EDID is read directly from STDP2690 on demand.

## Dependencies And Integration Points

The driver depends on I2C SMBus/transfer operations, DRM bridge/connector/EDID helpers, IRQ threading, and OF matching for both physical chips. It integrates with KMS as one DisplayPort bridge/connector despite the two-chip hardware pipeline.

## Risks And Edge Cases

The global singleton design is fragile for multiple boards/devices. Remove ordering leaves client pointers intact and depends on devm allocation, so late callbacks must not occur after one device disappears. I2C transfer errors in EDID read return `-1` rather than a normal errno. Detect uses exact link-state equality and returns unknown for partial states. Bridge `of_node` is taken from STDP4028 only. Connector creation is legacy and skipped for connectorless attach.

## Test Signals

Test both probe orders, one-chip-missing behavior, IRQ absent/present, HPD connect/disconnect, EDID reads through STDP2690, connectorless and connector-owning attach, removal in both orders, duplicate device instances, and SMBus error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/megachips-stdpxxxx-ge-b850v3-fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/microchip-lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/microchip-lvds.c

## Purpose

This platform driver exposes the Microchip SAM9X75 LVDS controller as a DRM bridge to an LVDS panel. It maps the LVDS controller registers, enables the pixel clock and runtime PM, programs the serializer for JEIDA 24-bit LVDS with high DE polarity, and attaches the downstream panel bridge.

## Important APIs, Types, And Functions

`struct mchp_lvds` contains the device, MMIO base, pixel clock, panel pointer, DRM bridge, and panel bridge. Register helpers are `lvds_readl()` and `lvds_writel()`. `lvds_serialiser_on()` unlocks write protection, waits for configuration status to clear, writes `LVDSC_CFGR`, and enables serialization with `LVDSC_CR_SER_EN`.

Bridge callbacks are `mchp_lvds_attach()`, `mchp_lvds_enable()`, and `mchp_lvds_disable()`.

## Control Flow

Probe requires OF, allocates the bridge, maps MMIO, gets `pclk`, finds the panel from output port 1, gets the panel bridge via `devm_drm_of_get_bridge()`, sets connector type LVDS, enables runtime PM, and registers the bridge. Enable prepares/enables `pclk`, resumes runtime PM, and turns on the serializer. Disable drops runtime PM and disables the clock.

## State And Persistence

The driver has no per-mode state and no suspend/resume-specific storage. LVDS controller configuration persists in MMIO registers while the hardware remains powered. Runtime PM and clock state control register access and serializer operation.

## Dependencies And Integration Points

Dependencies include platform MMIO resources, clocks, PM runtime, OF graph, DRM bridge/panel helpers, and low-level register access. It integrates as a simple bridge between a display controller and an LVDS panel.

## Risks And Edge Cases

`mchp_lvds_enable()` returns void and does not unwind `clk_prepare_enable()` if `pm_runtime_get_sync()` fails. The serializer configuration is hardcoded to JEIDA, 24-bit, high DE, and unbalanced DC, with no bus-format negotiation. `lvds_serialiser_on()` times out with only an error log. There is no remove callback to explicitly remove the bridge, relying on platform/device lifetime behavior.

## Test Signals

Test build/probe for `microchip,sam9x75-lvds`, missing MMIO/clock/panel resources, runtime PM failures, serializer status timeout, enable/disable cycles, panel bridge attachment, and visual validation for JEIDA 24-bit LVDS timing/polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/microchip-lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.c

## Purpose

This file implements the Northwest Logic MIPI DSI host/bridge used on i.MX8. It registers both a `mipi_dsi_host` for panel command transfers and a DRM bridge for video output, configures the DSI host, DPHY, DPI timing generator, resets, clocks, mux input selection, and interrupt-driven packet transfer completion.

## Important APIs, Types, And Functions

`struct nwl_dsi` stores the DRM bridge, DSI host, PHY/config, quirk flags, MMIO regmap, IRQ, four resets, input mux, five clocks, attached DSI lane/format/mode flags, current display mode, sticky register error, and active packet transfer pointer. `struct nwl_dsi_transfer` tracks one MIPI DSI transaction, including packet, completion, status, direction, BTA need, command byte, and RX/TX lengths.

Key functions include `nwl_dsi_config_host()`, `nwl_dsi_config_dpi()`, `nwl_dsi_get_dphy_params()`, `nwl_dsi_mode_set()`, `nwl_dsi_disable()`, `nwl_dsi_host_attach()`, `nwl_dsi_host_transfer()`, `nwl_dsi_begin_transmission()`, `nwl_dsi_read_packet()`, `nwl_dsi_finish_transmission()`, `nwl_dsi_irq_handler()`, bridge mode_set/atomic_check/enable/disable/attach, and DT parsing/input mux selection.

## Control Flow

Probe allocates the bridge, parses PHY, clocks, mux, MMIO regmap, IRQ, and resets, requests IRQ, registers the MIPI DSI host, detects SoC quirks, sets bridge metadata/timings, enables runtime PM, selects LCDIF or DCSS input through the mux based on graph endpoints, and adds the bridge.

When a DSI peripheral attaches, `nwl_dsi_host_attach()` stores lane count, pixel format, and mode flags. Bridge mode_set computes DPHY timings, stores the adjusted mode, resumes runtime PM, enables LCDIF and core clocks, deasserts PCLK reset, initializes PHY/host/DPI/interrupts, then deasserts ESC and BYTE resets so command transfers can run. Atomic enable deasserts DPI reset, starting pixel flow. Atomic disable powers down PHY, disables TX escape clock, asserts DPI/BYTE/ESC/PCLK resets, disables clocks, and drops runtime PM.

DSI host transfer builds a packet, chooses send/receive, enables RX escape clock, writes payload/header, starts transfer, waits up to 500 ms for IRQ completion, and returns bytes transferred or error. The IRQ handler logs FIFO/timeout errors and completes send/RX transactions when status bits arrive.

## State And Persistence

Attached DSI parameters and the current adjusted mode persist in `struct nwl_dsi`. `dsi->error` accumulates regmap read/write failures until cleared by `nwl_dsi_clear_error()`. `dsi->xfer` points to a stack transfer only during synchronous host transfers and is completed by IRQ. Hardware state spans reset lines, clocks, PHY power, mux selection, and DSI/DPI registers.

## Dependencies And Integration Points

The driver depends on platform resources, regmap MMIO, PHY MIPI DPHY helpers, clocks, resets, mux consumer API, runtime PM, IRQs, SoC matching for i.MX8MQ errata, DRM bridge/atomic helpers, MIPI DSI host APIs, OF graph, and `nwl-dsi.h` register definitions. It attaches downstream bridge/panel from output port 1.

## Risks And Edge Cases

The active transfer pointer is not protected by a lock, so transfers assume serialization by the MIPI DSI framework/panel setup. Some error paths in mode_set jump to runtime put without undoing already enabled clocks/resets. The i.MX8MQ E11418 workaround changes HS mode for payload patterns with zero high bytes. Mode validity depends on lane count/format already being attached; before attach, format/lane values may be incomplete. Reset sequencing comments note that panel bridge command setup and DPI deassertion are not ideally ordered.

## Test Signals

Test DSI host attach for 1-4 lanes and RGB565/RGB666/RGB888, command writes and reads with short/long packets, IRQ completion and timeout paths, FIFO overflow/HS timeout logs, LCDIF versus DCSS mux selection, runtime PM and reset sequencing, i.MX8MQ rev 2.0 quirk behavior, mode clock limits, suspend/remove cleanup, and panel init command timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.h

## Purpose

This header defines the register offsets and bitfield helpers for the Northwest Logic MIPI DSI host used by `nwl-dsi.c`. It is the hardware contract for host configuration, DPI video timing, packet TX/RX, interrupt status/masks, packet-control fields, RX header decoding, video mode selection, and pixel-format encoding.

## Important APIs, Types, And Macros

Register groups include `NWL_DSI_CFG_*` host timing/control registers, DPI registers such as `NWL_DSI_PIXEL_PAYLOAD_SIZE`, `NWL_DSI_INTERFACE_COLOR_CODING`, `NWL_DSI_PIXEL_FORMAT`, sync polarity, video mode, porch/sync sizes, BLLP/null-packet controls, and virtual channel. Packet registers include `NWL_DSI_TX_PAYLOAD`, `NWL_DSI_PKT_CONTROL`, `NWL_DSI_SEND_PACKET`, FIFO levels, `NWL_DSI_RX_PAYLOAD`, and `NWL_DSI_RX_PKT_HEADER`.

IRQ definitions cover status/mask bits for TX completion, DPHY direction, FIFO overflow/underflow, RX header/payload, BTA/LP/HS timeouts, and ECC/CRC errors. `NWL_DSI_WC()`, `NWL_DSI_TX_VC()`, `NWL_DSI_TX_DT()`, `NWL_DSI_HS_SEL()`, `NWL_DSI_BTA_TX()`, and `NWL_DSI_BTA_NO_TX()` compose packet-control fields. `NWL_DSI_RX_DT()` and `NWL_DSI_RX_VC()` decode RX headers.

## Control Flow

The header has no runtime flow. `nwl-dsi.c` uses these constants to program host timing from DPHY settings, DPI timing from DRM modes, send/receive MIPI DSI packets, mask interrupts, and decode IRQ/RX status.

## State And Persistence

No software state is stored here. The named registers represent hardware state that persists while the DSI block remains powered and out of reset.

## Dependencies And Integration Points

The header relies on kernel bit helpers (`BIT`, `GENMASK`, `FIELD_PREP`, `FIELD_GET`) from including translation units. It is tightly coupled to `nwl-dsi.c` and the MMIO regmap stride/max register setup.

## Risks And Edge Cases

Incorrect offsets or field masks break low-level hardware programming with little compile-time visibility. Packet-control field helpers assume input values fit their field widths. IRQ bits include error classes not all handled by the current driver. The comment typo around DPI color coding is harmless but indicates generated/manual mixed content.

## Test Signals

Validation is indirect through `nwl-dsi.c`: register writes in trace/debug, packet TX/RX, interrupt masking, video mode programming, pixel format mapping, and static review against the NWL hardware manual.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nxp-ptn3460.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nxp-ptn3460.c

## Purpose

This file implements the NXP PTN3460 eDP-to-LVDS bridge. It controls powerdown/reset GPIOs, selects one of the chip's EDID emulation entries, reads EDID over I2C, optionally creates an LVDS connector, and attaches a downstream panel bridge.

## Important APIs, Types, And Functions

`struct ptn3460_bridge` contains a connector, I2C client, DRM bridge, panel bridge, powerdown/reset GPIOs, selected EDID emulation index, and an `enabled` flag. Low-level accessors are `ptn3460_read_bytes()` and `ptn3460_write_byte()`. `ptn3460_select_edid()` loads the selected EDID into SRAM and enables emulation. Bridge callbacks are `ptn3460_pre_enable()`, `ptn3460_disable()`, `ptn3460_bridge_attach()`, and `ptn3460_edid_read()`.

## Control Flow

Probe wraps the downstream bridge from DT port 0 endpoint 0, acquires powerdown and reset GPIOs, reads the required `edid-emulation` property, sets bridge EDID op/type/of_node, adds the bridge, and stores client data. Pre-enable powers the chip, pulses reset, waits 90 ms to avoid false HPD, selects EDID, and marks enabled. Disable marks disabled, asserts reset high, and powers down. EDID read temporarily powers the bridge if needed, reads one 128-byte EDID block from address 0, allocates a DRM EDID object, and powers off again if it was originally off.

## State And Persistence

`enabled` tracks whether GPIO power sequencing has completed. The selected EDID emulation persists in chip registers/SRAM while powered. The driver does not manage regulators; board power is represented through GPIOs. Connector state exists only if the driver creates a connector during attach.

## Dependencies And Integration Points

Dependencies include I2C master send/receive, GPIO, OF properties, DRM bridge/connector/EDID helpers, and `devm_drm_of_get_bridge()` for the downstream panel. It integrates as an LVDS connector/bridge in the DRM chain.

## Risks And Edge Cases

Only a single EDID block is read; extension blocks are not supported. The `edid-emulation` property is not range-checked against chip-supported entries. `gpiod_set_value()` is used rather than cansleep variants, so GPIO provider context matters. Attach registers a connector manually when not connectorless and triggers an HPD helper event. Power sequencing delays are fixed from datasheet assumptions.

## Test Signals

Test EDID emulation indices, missing property, GPIO failures, connectorless and connector-owning attach, EDID read while off/on, false HPD timing, remove after connector registration, and I2C transfer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nxp-ptn3460.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/panel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/panel.c

## Purpose

`panel.c` provides the common DRM panel bridge adapter. It wraps a `struct drm_panel` as a `struct drm_bridge`, optionally creates a connector, forwards mode and prepare/enable/disable/unprepare calls to the panel, propagates bus format, exposes panel debugfs, and provides managed helpers for device-managed and DRM-managed lifetimes.

## Important APIs, Types, And Functions

`struct panel_bridge` stores the bridge, connector, panel pointer, and connector type. Exported APIs include `drm_bridge_is_panel()`, `drm_panel_bridge_add()`, `drm_panel_bridge_add_typed()`, `drm_panel_bridge_remove()`, `drm_panel_bridge_set_orientation()`, `devm_drm_panel_bridge_add()`, `devm_drm_panel_bridge_add_typed()`, `drmm_panel_bridge_add()`, `drm_panel_bridge_connector()`, `devm_drm_of_get_bridge()`, and `drmm_of_get_bridge()`.

Bridge callbacks implement attach/detach, atomic pre_enable/enable/disable/post_disable, get_modes, bus-format propagation, and debugfs. Connector helpers call `drm_panel_get_modes()`.

## Control Flow

Creation allocates a `panel_bridge`, stores panel/type, sets bridge `of_node`, `DRM_BRIDGE_OP_MODES`, type, and `pre_enable_prev_first` from the panel, then calls `drm_bridge_add()`. Attach creates a connector unless `DRM_BRIDGE_ATTACH_NO_CONNECTOR` is set, sets panel orientation on the connector, attaches the encoder, and registers the connector if the DRM device is already registered.

Atomic pre_enable/enable call `drm_panel_prepare()` and `drm_panel_enable()` unless entering from self-refresh. Atomic disable/post_disable call `drm_panel_disable()` and `drm_panel_unprepare()` unless transitioning into self-refresh. OF helpers find either an existing bridge or panel and wrap panels automatically.

## State And Persistence

Panel bridge state is a thin lifetime wrapper; persistent display state belongs to the underlying `drm_panel`, connector state, and DRM bridge chain. Managed variants use devres or drmm actions to remove the bridge automatically. `detach()` cleans up the connector if it was initialized.

## Dependencies And Integration Points

This file is central to DRM bridge/panel integration and is used by many display drivers through exported symbols. It depends on DRM bridge, connector, encoder, managed cleanup, OF graph/panel lookup, debugfs, and panel APIs.

## Risks And Edge Cases

The lifetime model is historically awkward: `drm_panel_bridge_remove()` still calls `devm_drm_put_bridge()` and `detach()` has a FIXME about connector cleanup. Deprecated typed helpers remain for panels without connector types. Self-refresh checks skip panel power transitions and depend on correct CRTC state lookup. Connector registration during attach must handle devices already registered. Calling panel bridge APIs on non-panel bridges is guarded but still a caller bug.

## Test Signals

Test exported helper users, connectorless attach, connector creation/cleanup, panel orientation propagation, self-refresh transitions, managed devres and drmm cleanup, OF bridge lookup for panel versus bridge nodes, debugfs delegation, and bus-format propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/panel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8622.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8622.c

## Purpose

This driver supports Parade PS8622/PS8625 eDP-to-LVDS bridge chips. It performs strict power/reset/sleep sequencing, writes a large fixed configuration over page-offset I2C addressing, attaches a downstream panel bridge, and optionally exposes the chip's internal PWM backlight.

## Important APIs, Types, And Functions

`struct ps8622_bridge` stores the I2C client, DRM bridge, panel bridge, optional 1.2 V regulator, optional backlight device, sleep/reset GPIOs, max/current DP lane counts, and enabled flag. `ps8622_set()` writes one register to `client->addr + page`. `ps8622_send_config()` programs HPD low/high, analog tuning, DPCD fields, lane counts, PWM mode/brightness, LVDS output mapping, spread spectrum, and logic/clock settings.

Bridge callbacks are `ps8622_pre_enable()`, `ps8622_disable()`, `ps8622_post_disable()`, and `ps8622_attach()`. Backlight updates use `ps8622_backlight_update()`.

## Control Flow

Probe gets the downstream panel bridge from port 0, optional `vdd12`, required sleep/reset GPIOs, determines max lane count from I2C ID, reads optional `lane-count`, registers a backlight unless `use-external-pwm` is set, sets bridge type/of_node, adds the bridge, and stores client data.

Pre-enable asserts reset low, enables the regulator, exits sleep, waits within datasheet T1/T2 bounds, deasserts reset, waits 20 ms, sends configuration, and marks enabled. Disable only waits for panel PWM-off timing. Post-disable enters sleep, disables regulator, waits for rail fall, asserts reset, and waits the power-off interval. Backlight writes register `0x01:0xa7` only when enabled.

## State And Persistence

`enabled` guards repeated sequencing and backlight writes. Backlight brightness persists in `bl->props` and is pushed to hardware during config/update. The chip's page-addressed register state is fully reprogrammed on each pre-enable. Power state is controlled by GPIOs and optional regulator.

## Dependencies And Integration Points

Dependencies include I2C transfer, GPIO, regulators, backlight subsystem, DRM bridge/panel helpers, OF properties, and I2C ID data. It integrates between an eDP source and LVDS panel bridge.

## Risks And Edge Cases

`ps8622_set()` returns boolean-style failure rather than errno and logs with `pr_warn`, so detailed failure context is limited. The fixed configuration is highly board/chip specific, including 6-bit VESA single-channel LVDS and spread-spectrum values. `ps8622_attach()` uses `ps8622->bridge.encoder` rather than the `encoder` argument, which relies on bridge core state being set. Backlight registration is non-devm and must be unregistered on remove. Internal PWM updates fail while disabled.

## Test Signals

Test PS8622 and PS8625 IDs, lane-count clamping, external versus internal PWM, backlight brightness update while enabled/disabled, regulator absent/present, exact power/reset timing with scope or logs, I2C write failure during config, panel attach, repeated enable/disable cycles, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8622.c -->
