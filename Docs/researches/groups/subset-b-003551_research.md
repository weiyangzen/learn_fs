# Research: subset-b-003551

Grouped research for six DRM bridge source files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge`. Each source section is bounded by the reconciliation markers required by the research pipeline.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8640.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8640.c

## Purpose

`parade-ps8640.c` drives the Parade PS8640 MIPI DSI-to-eDP bridge. It exposes a DRM bridge that accepts a fixed 4-lane RGB888 MIPI DSI input, links to a downstream eDP panel bridge, and provides a `drm_dp_aux` channel for EDID and panel AUX transactions. The chip is addressed as eight adjacent I2C pages, each wrapped in a no-cache 8-bit regmap.

## Important APIs, Types, And Functions

The main state is `struct ps8640`: DRM bridge, downstream panel bridge, DP AUX object, generated MIPI DSI device, page clients/regmaps, `vdd12`/`vdd33` regulators, reset/powerdown GPIOs, a stateless device link, `pre_enabled`, `need_post_hpd_delay`, and `aux_lock`.

Important callbacks are `ps8640_probe()`, `ps8640_bridge_get_dsi_resources()`, `ps8640_bridge_link_panel()`, `ps8640_bridge_attach()/detach()`, `ps8640_atomic_pre_enable()`, `ps8640_atomic_post_disable()`, runtime PM `ps8640_resume()/suspend()`, and AUX operations `ps8640_aux_transfer()` and `ps8640_wait_hpd_asserted()`. Register-level helpers include `_ps8640_wait_hpd_asserted()`, `ps8640_aux_transfer_msg()`, and `ps8640_bridge_vdo_control()`.

## Control Flow

Probe allocates the bridge, obtains regulators and GPIOs, records eDP connector type, discovers the upstream DSI host from port 0, creates a DSI device, builds dummy I2C clients/regmaps for pages 1-7, initializes DP AUX, enables runtime PM autosuspend, and links the downstream panel either through an AUX bus child or directly through port 1. Attach registers the AUX channel, creates a device link from DRM device to I2C device, and attaches the panel bridge after this bridge.

Runtime resume powers regulators, deasserts powerdown, performs a double reset, marks that a first-HPD delay is needed, and waits 200 ms for firmware. Pre-enable runtime-resumes the chip, waits for GPIO9-as-HPD, disables panel MCS, enables I2C bypass for EDID access, and enables DSI video. Post-disable disables video and synchronously suspends runtime PM under `aux_lock` so AUX transfers cannot keep the bridge powered during shutdown.

AUX transfers serialize with `aux_lock`, runtime-resume the chip, wait for HPD, program SWAUX address/length/request registers, optionally push write payload bytes, trigger `SWAUX_SEND`, poll completion, translate hardware ACK/NACK/DEFER/TIMEOUT into DP AUX replies, and pull read payload from the internal FIFO.

## State And Persistence Behavior

Driver state is volatile and device scoped. `need_post_hpd_delay` survives only across one resume-to-first-HPD sequence. `pre_enabled` tracks display pipeline state but is not otherwise used for persistence. Register caches are disabled, so every regmap operation reaches hardware. Power state is managed by runtime PM with a 2 second autosuspend delay to avoid repeated 300 ms power cycles during EDID/AUX activity.

## Dependencies And Integration Points

The driver integrates with DRM bridge, DRM DP AUX bus, MIPI DSI host registration, OF graph port 0/1 topology, regulator and GPIO frameworks, runtime PM, regmap, and device links. It depends on downstream panel bridge discovery and may defer probe until the upstream DSI host or downstream panel is available.

## Risks

Risks include the undocumented HPD-on-GPIO9 behavior, hard-coded reset delays, AUX transaction error handling, fixed four-lane RGB888 DSI assumptions, and the need to keep power sequencing synchronized with AUX operations. The code ignores the return from some regmap writes/polls in `ps8640_aux_transfer_msg()`, so failures can be reported later or as misleading status. Incorrect OF graph wiring prevents either DSI registration or panel linking.

## Test Signals

Useful signals are successful probe with eight I2C pages, runtime PM resume/suspend without regulator or GPIO errors, EDID reads through AUX, HPD wait behavior after reset, display enable/disable with video control toggling, no AUX timeout during connector probing, and suspend/resume cycles without stale power references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/samsung-dsim.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/samsung-dsim.c

## Purpose

`samsung-dsim.c` implements the Samsung/Exynos-style MIPI DSI host controller as a DRM bridge and MIPI DSI host. In this tree it supports multiple Exynos controller generations plus i.MX8MM/i.MX8MP variants through `struct samsung_dsim_driver_data`, which supplies register offsets, PLL constraints, bit positions, clock names, FIFO quirks, reset behavior, and PHY timing tables.

## Important APIs, Types, And Functions

The state type is `struct samsung_dsim` from `include/drm/bridge/samsung-dsim.h`: MIPI DSI host, DRM bridge, mapped registers, PHY, clocks, regulators, IRQs, optional TE GPIO, PLL/burst/escape clock rates, lane count, format, mode flags, mode copy, lane polarity swaps, state flags, completion, transfer spinlock/list, and platform/driver data. `struct samsung_dsim_transfer` models queued DSI packets with completion and TX/RX progress.

Key functions include exported `samsung_dsim_probe()`, `samsung_dsim_remove()`, and `samsung_dsim_pm_ops`; bridge callbacks `samsung_dsim_atomic_pre_enable()`, `atomic_enable()`, `atomic_disable()`, `atomic_post_disable()`, `atomic_check()`, `mode_set()`, and `attach()`; host ops `samsung_dsim_host_attach()`, `host_detach()`, and `host_transfer()`; register setup helpers `samsung_dsim_set_pll()`, `enable_clock()`, `set_phy_ctrl()`, `init_link()`, `set_display_mode()`, and FIFO/IRQ transfer helpers.

## Control Flow

Probe allocates the bridge, initializes transfer synchronization, records SoC data from OF match, obtains regulators and SoC-specific clocks, maps MMIO, obtains optional DSI PHY, requests the controller IRQ with `IRQF_NO_AUTOEN`, parses DT clock properties and lane polarities, enables runtime PM, configures bridge type/timings, and registers the MIPI DSI host through platform host ops.

When a DSI peripheral attaches, the host locates a child panel or graph-connected downstream bridge, wraps panels with `devm_drm_panel_bridge_add()`, adds this bridge, optionally registers a TE IRQ for command-mode panels, lets platform host ops run, then stores lanes/format/mode flags. Host transfers require `DSIM_STATE_ENABLED`, lazily initialize hardware, create a MIPI packet, enqueue a `samsung_dsim_transfer`, start FIFO writes, and wait for completion or timeout. IRQ handling acknowledges interrupt status, completes reset waits, and advances queued transfers on RX done or FIFO-empty events.

Atomic pre-enable runtime-resumes the controller and, for non-Exynos platforms, initializes the link immediately. Atomic enable programs display timings and turns on main display output. Disable clears display enable and post-disable drops runtime PM. Exynos behavior differs because downstream panel/bridge command transfers may trigger initialization.

## State And Persistence Behavior

`dsi->state` tracks enabled, initialized, command-LPM, and video-output-available state. Runtime suspend tears down clocks, IRQs, PHY, and regulators and clears initialized/CMD-LPM state. Mode, lanes, pixel format, and clock rates remain in software across runtime PM and are used to reprogram hardware. Transfers are transient list entries protected by a spinlock; completion signals synchronous callers.

## Dependencies And Integration Points

The file depends on DRM bridge/panel helpers, MIPI DSI host APIs, Linux clk/regulator/PHY/runtime PM/IRQ frameworks, OF graph, media bus formats, and MIPI display packet definitions. It exports generic probe/remove/PM symbols for platform glue and also declares i.MX8MM/i.MX8MP OF matches directly.

## Risks

PLL programming is sensitive to `pll_fin_*`, `m_min/m_max`, offsets, and requested burst/pixel clock; incorrect data can silently produce bad DSI clocks. FIFO control has generation-specific quirks such as broken header-empty reporting. Transfer completion depends on IRQ delivery; missed IRQs produce 100 ms timeouts and transfer removal. `samsung_dsim_parse_dt()` assumes an endpoint when counting data lanes and can be fragile on malformed DT. i.MX sync-polarity and HFP lane rounding in `atomic_check()` are platform-specific behavioral adjustments that can affect mode compatibility.

## Test Signals

Signals include probe on each supported compatible, correct runtime PM regulator/clock/PHY sequencing, DSI panel attach/detach, command-mode transfers including reads and BTA, video-mode enable with stable PLL and stop-state detection, TE IRQ delivery for command panels, suspend/resume with reinitialization, and mode tests around lane counts and i.MX polarity/HFP adjustment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/samsung-dsim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sii902x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sii902x.c

## Purpose

`sii902x.c` drives Silicon Image SII902x RGB-to-HDMI transmitters, especially `sil,sii9022`. It is a DRM HDMI bridge with optional legacy connector creation, HPD/EDID support, a DDC I2C mux implemented through the transmitter pass-through mode, and optional HDMI audio codec registration for I2S audio.

## Important APIs, Types, And Functions

`struct sii902x` stores the I2C client, unlocked regmap, DRM bridge/connector, reset GPIO, DDC mux, input bus width, a mutex shared by video/audio/DDC register sequences, and audio state containing codec platform device, optional `mclk`, and I2S FIFO mappings.

Important DRM callbacks are `sii902x_bridge_attach()`, `sii902x_bridge_mode_set()`, `sii902x_bridge_atomic_enable()/disable()`, `sii902x_bridge_detect()`, `sii902x_bridge_edid_read()`, `sii902x_bridge_atomic_get_input_bus_fmts()`, `sii902x_bridge_atomic_check()`, and `sii902x_bridge_mode_valid()`. Connector callbacks provide detect/get-modes when the bridge creates its own connector. Audio is exposed through `hdmi_codec_ops`: `sii902x_audio_hw_params()`, `audio_shutdown()`, `audio_mute()`, `audio_get_eld()`, and `audio_get_dai_id()`.

## Control Flow

Probe checks SMBus byte support, allocates state, creates an I2C regmap with locking disabled, obtains optional reset GPIO, reads input `bus-width` from port 0, optionally finds a downstream bridge from port 1, initializes the mutex, enables `iovcc` and `cvcc12`, then runs `sii902x_init()`.

Initialization resets the chip, writes TPI request byte, validates chip ID byte 0 as `0xb0`, clears pending interrupts, enables/request HPD IRQ when present, initializes optional HDMI codec, creates a one-channel I2C mux for DDC, sets bridge OF node/timings/type/ops, enables HPD ops if IRQ-backed, and adds the bridge.

Mode set writes TPI video timing bytes derived from adjusted mode, builds an AVI infoframe, and writes the packed payload minus the HDMI header but with checksum. Atomic enable selects HDMI vs DVI from connector display info, exits D0 power state, and clears powerdown; disable sets powerdown. EDID reads lock the shared mutex and use the mux adapter, whose select/deselect callbacks request and release the DDC bus using raw SMBus transfers because the parent adapter lock is already held.

## State And Persistence Behavior

The driver maintains no persistent configuration beyond DT-derived bus width, downstream bridge pointer, audio lane mapping, and connector ELD. Hardware registers are volatile and uncached. The mutex preserves atomicity of multi-register sequences across video, audio, HPD, and DDC paths. Audio `mclk` is prepared during hw_params and disabled on shutdown or error.

## Dependencies And Integration Points

Dependencies include DRM bridge/connector/EDID helpers, regmap, I2C mux, GPIO, regulator, optional clock, and ASoC HDMI codec APIs. It integrates with OF graph ports for RGB input and optional downstream bridge output, `#sound-dai-cells` plus `sil,i2s-data-lanes` for audio, and DRM HPD notification when an IRQ is available.

## Risks

DDC pass-through is delicate: select/deselect must avoid regmap locking and touch only DDC request/grant bits in `SII902X_SYS_CTRL_DATA`. Mode support is capped to 25-165 MHz pixel clock. `sii902x_bridge_atomic_get_input_bus_fmts()` leaks its allocation if an unsupported `bus_width` is configured because it returns NULL after allocating. Audio sample-rate table uses 44000 and 88000 entries, which look suspicious for 44.1/88.2 kHz style rates. Shared register access relies on callers consistently taking `mutex`.

## Test Signals

Useful tests include probe/chip ID validation, connector HPD IRQ and polling behavior, EDID reads through the mux including timeout/release paths, mode validation around clock limits, HDMI/DVI output-mode selection, AVI infoframe programming, 16/18/24-bit input bus format negotiation, I2S audio startup/shutdown/mute and ELD readback, and remove cleanup of bridge, mux, and codec device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sii902x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sii9234.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sii9234.c

## Purpose

`sii9234.c` drives the Silicon Image SII9234 HDMI/MHL bridge. It is primarily an interrupt-driven MHL discovery and link-state driver rather than a full atomic video programming bridge: the DRM bridge surface only validates the maximum MHL1 pixel clock, while the device logic manages power, CBUS discovery, RGND detection, RSEN, HPD, and TMDS enablement.

## Important APIs, Types, And Functions

`struct sii9234` stores four I2C clients (`I2C_MHL`, `I2C_TPI`, `I2C_HDMI`, `I2C_CBUS`), DRM bridge, device, reset GPIO, last I2C error, four regulators, a mutex, and current `enum sii9234_state` (`ST_OFF`, `ST_D3`, `ST_RGND_INIT`, `ST_RGND_1K`, `ST_RSEN_HIGH`, `ST_MHL_ESTABLISHED`, and failure states).

Register access is centralized through `sii9234_writeb()`, `writebm()`, `readb()`, and macros for the four register pages. Initialization helpers include `sii9234_power_init()`, `sii9234_cbus_reset()`, `sii9234_cbus_init()`, `sii9234_hdmi_init()`, `sii9234_mhl_tx_ctl_int()`, `sii9234_reset()`, and `sii9234_goto_d3()`. Runtime state handlers include `sii9234_rgnd_ready_irq()`, `sii9234_mhl_established()`, `sii9234_hpd_change()`, `sii9234_rsen_change()`, and `sii9234_irq_thread()`.

## Control Flow

Probe allocates the bridge, validates SMBus byte support and IRQ presence, requests the threaded IRQ with `IRQ_NOAUTOEN`, obtains reset GPIO and regulators, creates dummy I2C clients for TPI/HDMI/CBUS, adds the bridge, and calls `sii9234_cable_in()`.

Cable-in powers regulators, toggles reset, runs `sii9234_goto_d3()`, and enables IRQ after the hardware is in a known D3 discovery state. Reset programming performs power/TMDS/HDMI/CBUS initialization, loads local MHL devcap values, configures discovery thresholds and interrupts, toggles USB ID switch override for RGND measurement, and forces upstream HPD low until MHL is established. IRQ handling reads MHL and CBUS interrupt/status registers, dispatches state-specific handlers, clears interrupt sources, and recovers failures by resetting back to D3 or powering discovery down.

HPD changes read CBUS abort/status reason and enable or disable TMDS output. RSEN changes validate state, debounce loss, and reset discovery on failure. Remove calls cable-out, disables IRQ, powers down through TPI DPD and regulators, and removes the bridge.

## State And Persistence Behavior

All meaningful state is volatile: current finite-state-machine state, accumulated `i2c_error`, and hardware register state. The `i2c_error` field short-circuits subsequent register accesses in a sequence until `sii9234_clear_error()`, making multi-register programming fail-fast. Regulators and reset GPIO define physical persistence; no software state is stored across remove or power loss.

## Dependencies And Integration Points

The driver depends on DRM bridge mode validation, MHL capability constants from `drm/bridge/mhl.h`, Linux I2C dummy clients, threaded IRQs, GPIO, regulators, and mutex locking. It expects DT supplies and a reset GPIO. It does not expose EDID, HPD, or connector operations through DRM bridge ops.

## Risks

The state machine is sensitive to IRQ ordering and current state; unexpected RSEN or RGND interrupts push the driver into failure recovery. Many register values are magic hardware-sequencing constants from vendor code and are hard to validate. I2C failures during power-down are expected in one path and cleared manually. Mode validation only enforces 75 MHz MHL1 maximum and does not negotiate downstream capabilities. Lack of DRM HPD/EDID ops limits integration visibility.

## Test Signals

Test signals include successful creation of all four I2C clients, regulator/reset sequencing, IRQ transitions from D3 to RGND to established MHL, TMDS enable/disable on HPD, RSEN loss recovery, discovery-failure handling without IRQ storms, mode rejection above 75 MHz, and clean cable-out/remove with IRQ disabled before power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sii9234.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.c

## Purpose

`sil-sii8620.c` drives the Silicon Image SiI8620 Mobile HD Transmitter, an HDMI/MHL bridge with MHL1/2 and MHL3/eCBUS support. It handles hardware power, MHL discovery, CBUS MSC messaging, eMSC burst transfers, EDID fetch and upstream EDID priming, HPD control, video format/link setup, optional RCP input events, extcon cable detection, and DRM bridge mode validation/fixup.

## Important APIs, Types, And Functions

`struct sii8620` stores bridge/device pointers, optional RC input device, XTAL clock, reset/int GPIOs, regulators, mutex, sticky `error`, packed-pixel decision, current mode, sink type, CBUS status, MHL status/devcap/xdevcap arrays, EDID pointer, feature flags, extcon state/work, MSC transmit queue, and eMSC burst buffers. `struct sii8620_mt_msg` represents queued MSC commands with send/receive callbacks and continuations.

Core helpers include raw paged I2C access (`sii8620_read_buf()`, `readb()`, `write_buf()`, `write_seq()`, `setbits()`), message queue helpers (`sii8620_mt_*`), eMSC burst helpers (`sii8620_burst_*`), EDID helpers (`sii8620_fetch_edid()`, `set_upstream_edid()`), power/init/disconnect helpers (`hw_on()`, `hw_off()`, `disconnect()`, `mhl_init()`), mode/video helpers (`set_mode()`, `set_format()`, `set_infoframes()`, `start_video()`), IRQ subhandlers, extcon handlers, and bridge callbacks `attach()`, `detach()`, `mode_valid()`, and `mode_fixup()`.

## Control Flow

Probe allocates state, initializes mutex and message queue, gets XTAL clock, requests a disabled threaded IRQ, gets reset GPIO and regulators, initializes extcon if present, adds the DRM bridge, and either waits for extcon MHL events or powers on immediately. Cable-in enables regulators/clock, releases reset, reads chip ID, programs XTAL rate, calls `sii8620_disconnect()` to reset link state, configures CBUS drive controls, and enables IRQ.

The main IRQ thread reads `REG_FAST_INTR_STAT`, dispatches discovery, Gen2 write-burst, CoC, TDM, MSC, error, eMSC block, EDID, DDC, and SCDT handlers, then drains received bursts, advances queued MSC work, sends pending bursts, and disconnects on accumulated error. Discovery checks RGND and MHL established bits; MHL init writes local capabilities, configures peer-specific state, starts Gen2 write burst, and announces DCAP ready. MSC status/interrupt handlers react to DCAP ready, path enable, HPD changes, feature requests/completion, RCP/RAP messages, and transition to MHL3/eCBUS when supported.

Sink detection waits for both downstream HPD and devcap read, fetches EDID over the internal DDC engine, primes upstream EDID FIFO, identifies HDMI vs DVI, and enables HPD after MHL3 feature completion when required. SCDT change starts video: it selects packed-pixel mode if needed, writes TPI formats and infoframes, programs MHL1 link mode or MHL3 AV link rate/zone, and sends burst pixel-format descriptors.

## State And Persistence Behavior

State is in-memory and hardware-volatile. `mode` moves through disconnected, discovery, MHL1, MHL3, and eCBUS-S. `devcap`, `xdevcap`, `stat`, and `xstat` mirror peer-visible MHL registers and are cleared on disconnect. `edid` is dynamically allocated and replaced on new sink detection. The sticky `error` short-circuits I2C sequences until cleared, and any IRQ-time error forces MHL disconnection. Extcon `cable_state` gates cable-in/out work.

## Dependencies And Integration Points

The file depends on `sil-sii8620.h`, DRM bridge/EDID/encoder APIs, MHL protocol constants, I2C, regulator, GPIO, clock, threaded IRQ, extcon, workqueue, and optional RC core. It assumes a paged I2C map whose page addresses are in `sii8620_i2c_page[]`. The bridge integrates only mode validation/fixup; actual HPD/EDID behavior is implemented by programming upstream-visible EDID/HPD hardware.

## Risks

The driver contains many hardware magic sequences and tight state coupling between discovery, MSC queue, eMSC burst, and video start. `sii8620_fetch_edid()` performs manual DDC polling and dynamic EDID reallocation; timeout or cable drop paths must free correctly. `sii8620_detach()` unregisters then frees `rc_dev`, which is risky because `rc_unregister_device()` normally owns release. Packed-pixel mode is stored from `mode_fixup()` under lock but consumed later in IRQ/video paths. Any paged I2C address mismatch in the header breaks broad areas of the driver.

## Test Signals

Signals include chip ID read after cable-in, extcon-triggered cable state changes, RGND/MHL established/disconnect IRQs, MSC queue progress and timeout-free completions, MHL1 and MHL3/eCBUS negotiation, EDID fetch and upstream HPD assertion, HDMI vs DVI sink detection, video start on SCDT with correct packed-pixel decision, RCP key events when RC core is enabled, and error recovery returning to disconnected discovery state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.h

## Purpose

`sil-sii8620.h` is the private register map for `sil-sii8620.c`. It defines the paged register addresses, bit masks, field masks, and composed values needed to program the SiI8620 transmitter. It has no functions, structs, or storage; its contract is exact hardware ABI naming for the C driver.

## Important APIs, Types, And Macros

The public surface is C preprocessor constants. Major groups are system identity/control (`REG_VND_ID*`, `REG_DEV_ID*`, `REG_SYS_CTRL1`, `REG_DPD`, `REG_PWD_SRST`), fast interrupt routing (`REG_FAST_INTR_STAT` and `BIT_FAST_INTR_STAT_*`), HPD/GPIO/TMDS/DDC controls, TDM/HSIC/eMSC controls, TMDS receiver and packet filter registers, EDID/devcap FIFO controls, MHL datapath/PLL/CBUS/CoC/DoC analog controls, HDCP2.x registers, MHL3 HDMI-to-MHL controls, TPI input/output/infoframe/system-control registers, MHL devcap/status/scratchpad base registers, MDT Gen2 write-burst controls, CBUS MSC command/status/interrupt registers, and discovery controls/status bits for RGND, MHL1/2, MHL3, and disconnect events.

Convenience composed values include `VAL_M3_CTRL_MHL1_2_VALUE`, `VAL_M3_CTRL_MHL3_VALUE`, `VAL_TPI_FORMAT(_fmt, _qr)`, `VAL_DISC_CTRL4()`, MHL PLL clock ratio values, CBUS drive/RGND values, TX zone values, and `VAL_CBUS_MHL_DISCON`.

## Control Flow

The header has no runtime control flow. Its macros drive control flow in `sil-sii8620.c`: `REG_FAST_INTR_STAT` bits select IRQ subhandlers, `REG_CBUS_DISC_INTR0` bits control discovery and disconnect paths, `REG_CBUS_INT_0` bits drive MSC receive/transmit handling, `REG_INTR9` and `REG_INTR3` bits complete devcap/EDID/DDC operations, and MHL/TPI/DP/PLL registers are programmed during disconnect, discovery, eCBUS transition, and video start.

## State And Persistence Behavior

No software state is stored here. The named registers represent volatile hardware state, sticky interrupt bits cleared by writeback, FIFO ports, MHL peer-visible capability/status memory, DDC/EDID buffers, power/reset state, and analog/link training controls. Persistence behavior is entirely hardware-defined and managed by `sil-sii8620.c`.

## Dependencies And Integration Points

The header assumes Linux `BIT()` is available through including C files. It is tightly coupled to the `sii8620_i2c_page[]` mapping in the C file: register high bytes select I2C page indices, so a register address and page table must stay synchronized. It also relies on MHL constants from DRM bridge MHL headers for array offsets and protocol values used beside these register definitions.

## Risks

Incorrect register addresses or masks can misroute interrupts, break DDC/EDID, corrupt MHL capability/status exchange, or damage discovery/link training sequences. Several fields are analog tuning or vendor-derived magic values, so accidental refactoring is high risk. Naming is not generated in a standard `REG_FIELD` style, so compile-time validation is limited to direct macro references.

## Test Signals

Static signals are successful build of `sil-sii8620.c` and absence of undefined macros. Runtime signals include correct chip ID reads, expected interrupt demux, successful MHL discovery, devcap/xdevcap reads, EDID FIFO operation, eMSC burst activity, SCDT video start, and stable MHL1/MHL3 mode validation across packed and normal pixel modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.h -->
