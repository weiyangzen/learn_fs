# subset-b-003552 Research

Work item: subset-b-003552

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/simple-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/simple-bridge.c

Purpose: implements a transparent DRM bridge for simple display-adapter parts that mostly need graph attachment, optional power enable, and connector exposure. It covers VGA DACs, HDMI level shifters/converters, composite adapters, and TI/ADI DAC timing variants through OF match data rather than chip-specific register programming.

Important APIs/types/functions: `struct simple_bridge_info` carries optional `drm_bridge_timings` and connector type; `struct simple_bridge` embeds the DRM bridge and connector plus optional `vdd` regulator and `enable` GPIO. `simple_bridge_probe()` allocates the bridge, resolves the output endpoint at port 1 to the next bridge, obtains optional resources, assigns timings, and registers with `devm_drm_bridge_add()`. `simple_bridge_attach()` attaches the next bridge and creates a connector unless `DRM_BRIDGE_ATTACH_NO_CONNECTOR` is requested. Connector callbacks provide EDID-based modes or no-EDID XGA fallback, and detect through the downstream bridge. Enable/disable toggle regulator and GPIO.

Control flow: probe is devicetree graph driven: find remote node, find downstream bridge, defer if unavailable, then register this bridge. Attach always attaches the downstream bridge with no connector first; when this bridge owns the connector, it initializes a DDC-aware connector using the downstream bridge's DDC adapter and attaches it to the encoder. Runtime enable powers `vdd` before asserting `enable`; disable reverses that order.

State and persistence: there is no persistent configuration beyond devm-managed resources and match data. Hardware state is only the regulator/GPIO output level. EDID state is managed by DRM connector helpers and refreshed during mode probing.

Dependencies and integration: depends on DRM bridge/connector helpers, OF graph bindings for two-port bridges, optional regulator/GPIO consumer APIs, EDID helpers, and downstream bridge EDID/detect/DDC support. OF compatibles map connector types and timings for `dumb-vga-dac`, `adi,adv7123`, several HDMI adapters, `ti,opa362`, and TI THS813x DACs.

Risks: `bridge.next_bridge` is required and a missing graph endpoint fails probe. `simple_bridge_enable()` logs regulator enable failure but still asserts GPIO, so boards with mandatory power rails can attempt to drive an unpowered adapter. Fallback modes may expose unusable modes when DDC is broken. New compatibles must choose connector type and bus timings carefully because there is no register-level correction later.

Test signals: boot/probe with valid and missing port-1 graph endpoints, deferred downstream bridge probing, EDID and no-EDID mode enumeration, HPD/detect through downstream bridge, regulator/GPIO sequencing during atomic enable/disable, and connector type correctness in userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/simple-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ssd2825.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ssd2825.c

Purpose: implements the Solomon SSD2825 SPI-controlled RGB/parallel-to-MIPI-DSI bridge. It exposes a MIPI DSI host to panel drivers, attaches its own DRM bridge between the RGB input and DSI output, programs SSD2825 timing/PLL/packet registers, and sequences reset, regulators, and optional reference clock.

Important APIs/types/functions: `struct ssd2825_priv` stores SPI, reset GPIO, three regulators, optional `tx_clk`, `mipi_dsi_host`, DRM bridge, output panel/bridge, mutex, RGB bus width, DSI lane count, PLL-derived rates, and timing delay properties. Low-level helpers `ssd2825_write_raw()`, `ssd2825_write_reg()`, `ssd2825_read_raw()`, and `ssd2825_read_reg()` implement 9-bit SPI command/data cycles. `ssd2825_dsi_host_attach()` validates lanes and video mode, resolves the downstream panel/bridge, records DSI format/lane state, reads input `bus-width`, and registers the bridge. `ssd2825_dsi_host_transfer()` sends DCS/generic write packets through the packet-drop FIFO. `ssd2825_setup_pll()` computes divider/multiplier/range bits and LP clock divisor. Bridge callbacks program display timings in atomic pre-enable, finish video enable in atomic enable, and shut down hardware in atomic disable.

Control flow: SPI probe configures 9-bit SPI, allocates bridge state, reads resources/properties, initializes host ops, and registers the DSI host. DSI attach is the point where the downstream panel bridge is created and the DRM bridge is made visible. Atomic pre-enable enables the reference clock and regulators, resets the chip, software-resets it, selects pixel format, obtains adjusted mode from atomic state, writes porch/sync/active timings, lane count, PLL, and base DSI config, then enables the panel if present. Atomic enable turns on video mode (`VEN`) and PLL. Disable waits, exits active DSI config, asserts reset, disables supplies, and disables the clock.

State and persistence: driver state persists in `ssd2825_priv` for attached DSI device, panel/bridge, lane count, bus width, PLL frequency, and delay properties. Hardware state is entirely volatile SSD2825 registers and is rebuilt on each pre-enable. Host transfer serialization uses `mlock`; there is no nonvolatile state.

Dependencies and integration: integrates SPI, DRM bridge, MIPI DSI host, panel bridge, OF graph, optional clock, reset GPIO, and `dvdd`/`avdd`/`vddio` regulators. It depends on MIPI DSI pixel format helpers, DRM atomic state lookup, bridge timings, and devicetree properties `solomon,hs-zero-delay-ns`, `solomon,hs-prep-delay-ns`, and optional endpoint `bus-width`.

Risks: RX transfers and DSI reads are unsupported, so panel drivers requiring reads will fail or get no response. Transfer handling returns 0 for unsupported read request types rather than a positive byte count, which callers must tolerate. PLL/delay math depends on nonzero derived `nibble_freq_khz` and sane `hpd`/`hzd`; bad properties can underflow delay fields. Many register writes in enable paths ignore return values after power-up, so partial SPI failure may leave the bridge half-programmed. Mode validation hard-limits active width/height to 1366.

Test signals: SPI 9-bit read/write with known device ID, DSI panel attach/detach, regulator/reset/clock sequencing, video-mode panels with 1-4 lanes and RGB565/666/888 formats, DCS/generic init command delivery, mode rejection over 1366x1366, suspend/resume or modeset disable/enable, and error injection for SPI/regulator/clock failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ssd2825.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Kconfig

Purpose: defines Kconfig symbols for Synopsys DesignWare DRM bridge cores and their optional audio/CEC companion blocks.

Important APIs/types/functions: symbols include `DRM_DW_DP`, `DRM_DW_HDMI`, `DRM_DW_HDMI_AHB_AUDIO`, `DRM_DW_HDMI_I2S_AUDIO`, `DRM_DW_HDMI_GP_AUDIO`, `DRM_DW_HDMI_CEC`, `DRM_DW_HDMI_QP`, `DRM_DW_HDMI_QP_CEC`, `DRM_DW_MIPI_DSI`, and `DRM_DW_MIPI_DSI2`. The hidden core symbols select DRM display helpers, HDMI/DP helpers, KMS helpers, and `REGMAP_MMIO`; user-visible companion symbols depend on the core plus ALSA/ASoC/CEC prerequisites.

Control flow: this file influences build-time dependency selection only. Platform drivers select the hidden core symbols, then optional audio/CEC entries expose user choices when their sound/CEC dependencies are present.

State and persistence: no runtime state. The selected symbols persist in kernel configuration and determine which objects are built.

Dependencies and integration: integrates the Synopsys bridge objects with DRM helper libraries, ALSA PCM/IEC958/ELD, ASoC HDMI codec, CEC core/notifier, and regmap. `DRM_DW_HDMI_QP_CEC` is a bool tied to the QP HDMI bridge rather than a standalone module.

Risks: missing selects can produce link failures in platform drivers that expect helper APIs. Overly broad selects can pull CEC or audio support into configurations that do not need it. The help text has minor spelling issues and `DRM_DW_HDMI_CEC` says "CE interface", but behavior is unaffected.

Test signals: allmodconfig/allyesconfig builds, platform configs selecting each hidden core, modular builds for AHB/GP/I2S/CEC companions, and compile tests with CEC/SND/SND_SOC disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Makefile

Purpose: maps Synopsys DesignWare DRM bridge Kconfig symbols to object files.

Important APIs/types/functions: builds `dw-dp.o`, `dw-hdmi.o`, `dw-hdmi-ahb-audio.o`, `dw-hdmi-gp-audio.o`, `dw-hdmi-i2s-audio.o`, `dw-hdmi-cec.o`, `dw-hdmi-qp.o`, `dw-mipi-dsi.o`, and `dw-mipi-dsi2.o` under their corresponding `CONFIG_DRM_DW_*` symbols.

Control flow: kbuild includes exactly the objects enabled by the kernel configuration. There is no runtime behavior.

State and persistence: no state beyond build products.

Dependencies and integration: complements the local Kconfig file and lets platform-specific drivers link against exported core library symbols such as `dw_dp_bind()` and `dw_hdmi_qp_bind()`.

Risks: object/Kconfig mismatches cause missing drivers or unresolved symbols. Optional QP CEC is compiled into `dw-hdmi-qp.o` through C preprocessor guards, so there is no separate Makefile object for it.

Test signals: incremental and clean kernel builds for each symbol as built-in and module, plus link coverage for platform users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-dp.c

Purpose: implements a reusable Synopsys DesignWare DisplayPort transmitter core library. It provides the DRM bridge, AUX channel, DPCD/EDID access, HPD handling, PHY configuration, link training, bandwidth/output-format negotiation, SDP programming, and video timing programming used by platform-specific DP wrappers.

Important APIs/types/functions: `struct dw_dp` is the main object with bridge, regmap, PHY, clocks, reset, IRQ, AUX adapter, link state, platform data, HPD work, and SDP bank bitmap. `struct dw_dp_link` caches DPCD, link rate/lane count, sink count, VSC SDP capability, caps, training state, and DP descriptor. `struct dw_dp_bridge_state` stores the selected adjusted mode, video mapping, color format, bpc, and bpp. Exported `dw_dp_bind()` allocates/registers the bridge, MMIO regmap, PHY, clocks, reset, AUX, IRQ, and attaches to the encoder. Key internals are `dw_dp_link_parse()`, `dw_dp_phy_configure()`, `dw_dp_link_train_full()`, `dw_dp_link_train_fast()`, `dw_dp_video_enable()`, `dw_dp_aux_transfer()`, and HPD IRQ/work handlers.

Control flow: bind initializes resources, registers AUX, attaches bridge without connector, initializes hardware interrupts, initializes PHY, and requests IRQ. Detection checks HPD, powers the PHY, parses DPCD/sink count, and powers PHY back off. EDID read powers PHY and uses AUX DDC. Atomic bus-format negotiation filters supported RGB/YUV formats by sink color formats, max bpc, YCbCr420 rules, and link bandwidth. Atomic check stores the chosen mapping and fixes DP timing minima. Atomic enable marks SDP bank 0 reserved, powers PHY/link, powers up sink DPCD, trains the link, writes video/transfer-unit/MSA registers, enables stream, and sends VSC SDP for YCbCr420 when supported. Atomic disable disables video, powers down link/PHY, clears SDP allocation, and resets the controller.

State and persistence: link and training state persist in `dp->link` across detects and modesets; successful training enables later fast training. `dp->sdp_reg_bank` tracks allocated hardware SDP slots during stream enable. AUX transfers synchronize through a completion signaled by IRQ. HPD state is protected by `irq_lock` and processed in workqueue context. Hardware state is volatile MMIO/DPCD/PHY state and is rebuilt after reset.

Dependencies and integration: depends on DRM bridge/atomic/EDID helpers, DP helper library, regmap MMIO, Linux PHY DP options, APB/AUX/HDCP clocks, optional audio clocks, reset controls, platform `dw_dp_plat_data` (`pixel_mode`, `max_link_rate`), and devicetree-provided MMIO/PHY/IRQ resources. It integrates with bridge connector helpers through bridge ops for detect, EDID, HPD, output bus formats, mode validation, atomic check/enable/disable.

Risks: AUX read handling subtracts one from `AUX_BYTES_READ` and compares it to requested size, so off-by-one interpretation must match hardware. `dw_dp_bind()` performs an unused `devm_kzalloc()` before `devm_drm_bridge_alloc()`, which wastes a small allocation. Link downgrade only reduces rate, not lane count, and depends on stored bridge state. If video enable fails after link enable, the link remains powered until later disable. HPD reset waits on a hot-plug bit but ignores timeout. Timing and TU threshold formulas are hardware-sensitive, especially multi-pixel and YCbCr420 modes.

Test signals: AUX native/I2C transactions including timeouts and NACKs, EDID reads through branch devices, HPD plug/unplug/IRQ pulses, DPCD parsing with zero sink count, full and fast link training at RBR/HBR/HBR2/HBR3 with 1/2/4 lanes, bandwidth rejection and bus-format fallback, YCbCr420 VSC SDP output, atomic disable/reset/re-enable, and suspend/resume through platform wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-ahb-audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-ahb-audio.c

Purpose: implements the legacy ALSA PCM driver for the DesignWare HDMI AHB audio DMA engine, originally targeted at i.MX6. It owns a sound card/PCM device, reformats userspace audio into the HDMI DMA hardware format, and cycles DMA periods through the HDMI AHB DMA registers.

Important APIs/types/functions: `struct snd_dw_hdmi` stores card/PCM, spinlock, platform `dw_hdmi_audio_data`, active substream, reformatter callback, vmalloc source buffer, preallocated DMA destination buffer, DMA address, period/buffer offsets, channel count, revision, and generated IEC60958 channel-status bits. `dw_hdmi_open()`, `dw_hdmi_hw_params()`, `dw_hdmi_prepare()`, `dw_hdmi_trigger()`, `dw_hdmi_pointer()`, and `dw_hdmi_close()` implement PCM ops. `dw_hdmi_reformat_iec958()` and `dw_hdmi_reformat_s24()` convert data into the hardware layout. `snd_dw_hdmi_irq()` handles DONE interrupts, reports period elapsed, and starts the next period. Probe validates core revision, creates the ALSA card and PCM, preallocates DMA pages, and registers the card.

Control flow: open applies ELD-derived constraints, rate limits, integer period constraints, clears FIFO, configures interrupt polarity/masks, requests the shared IRQ, and unmutes DONE. `hw_params` allocates/resizes the vmalloc userspace buffer. Prepare chooses DMA burst/threshold based on HDMI revision, sets HDMI sample rate/channel count/channel allocation, chooses reformatter by PCM format, and records buffer geometry. START locks, resets offset, records substream, reformats/programs first DMA period, and enables HDMI audio; each DONE IRQ advances ALSA period and queues the next DMA period. STOP clears active substream, stops DMA, and disables HDMI audio.

State and persistence: PCM runtime state is split between vmalloc userspace buffer and preallocated DMA buffer. `dw->substream` and `buf_offset` are protected by a spinlock for trigger/IRQ coordination. IEC channel-status bit tables persist per prepare. Hardware state includes AHB DMA start/stop/threshold/mask/conf registers and HDMI audio packet configuration.

Dependencies and integration: depends on platform data from the parent DW-HDMI core (`base`, IRQ, physical address, `hdmi`, `get_eld`), ALSA core/PCM, DRM ELD constraints, IEC958 helpers, and exported `dw_hdmi_set_*()` / `dw_hdmi_audio_enable/disable()` APIs.

Risks: only HDMI revisions `0x0a` and `0x1a` are accepted. Hardware position reporting is approximate because DMA position reads are racy. Period size is capped at 8 KiB for a documented erratum, which affects ALSA configuration. The PM implementation is compiled out behind `IS_NOT_BROKEN`. Error/lost/retry/buffer interrupts are cleared but not surfaced to ALSA recovery. Reformat loops assume period byte counts align to 32-bit samples and channel layout.

Test signals: ALSA playback for S24_LE and IEC958_SUBFRAME_LE at 32-192 kHz, 2-8 channels, ELD constraint application, underrun/error interrupt observation, period cycling over buffer wrap, trigger start/stop races, revision rejection, and audio enable/disable integration with display modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-ahb-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-audio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-audio.h

Purpose: provides the platform-data contracts shared between the main DW-HDMI bridge driver and its AHB/I2S/GP audio companion drivers.

Important APIs/types/functions: forward-declares `struct dw_hdmi`. `struct dw_hdmi_audio_data` carries MMIO physical/base addresses, IRQ, parent HDMI pointer, and `get_eld()` callback for AHB and GP audio paths. `struct dw_hdmi_i2s_audio_data` carries parent HDMI pointer plus register read/write callbacks and `get_eld()` for the I2S codec path.

Control flow: no executable code. Parent HDMI code instantiates platform devices with one of these data blocks; audio drivers consume the callbacks/resources during probe and codec/PCM operations.

State and persistence: no owned state. The structures reference parent-owned MMIO and HDMI state; lifetime must outlive child platform devices.

Dependencies and integration: requires Linux integer/address types and the opaque DW-HDMI core. Integrates DRM ELD access, HDMI audio control APIs, and register access indirection for child drivers.

Risks: platform data is copied by some consumers and referenced by others, so parent lifetime and callback validity are critical. Wrong IRQ/base pairing can break AHB DMA audio. Missing `get_eld` would crash consumers because they call it unconditionally.

Test signals: build coverage for all DW-HDMI audio companions and runtime child device creation/removal with valid ELD and register callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.c

Purpose: implements the standalone CEC adapter driver for classic DesignWare HDMI blocks. It bridges Linux CEC framework operations to DW-HDMI CEC registers through parent-provided read/write/enable/disable callbacks.

Important APIs/types/functions: `struct dw_hdmi_cec` stores parent HDMI pointer, CEC ops, logical address mask, CEC adapter, RX message, TX status flags, notifier, IRQ, and suspend-saved interrupt register values. `dw_hdmi_cec_log_addr()` programs logical/broadcast addresses. `dw_hdmi_cec_transmit()` writes up to 16 TX bytes, count, and control mode based on signal-free time. `dw_hdmi_cec_hardirq()` acknowledges CEC status, maps DONE/NACK/ARBLOST/ERROR to CEC TX statuses, reads RX frames on EOM, and wakes the threaded handler. `dw_hdmi_cec_thread()` reports transmit completion and received messages to the CEC core. Probe allocates/registers the adapter, requests IRQ, registers a CEC notifier, and registers the adapter.

Control flow: probe initializes hardware to masked/idle, allocates a CEC adapter with default capabilities and connector info, installs cleanup for failed probe, requests shared threaded IRQ, registers notifier, then registers adapter. Adapter enable unmasks selected CEC status bits, clears lock/status, resets logical addresses, and calls parent enable; disable masks interrupts, clears polarity, and calls parent disable. Suspend caches polarity/mask/mute registers; resume restores logical addresses and those registers.

State and persistence: logical address bits persist in `cec->addresses` and are restored after resume. RX/TX completion flags are handed from hard IRQ to thread. Suspend state stores three interrupt-control registers. Hardware FIFOs/status/lock are volatile.

Dependencies and integration: depends on `dw-hdmi-cec.h` platform data, Linux CEC core, CEC notifier, DRM EDID include, platform device framework, and parent DW-HDMI register callbacks. Userspace sees a CEC chardev associated with the parent HDMI device.

Risks: hard IRQ and thread share booleans/message without a lock, relying on IRQ threading and barriers around RX data. RX reads all available bytes but clamps oversize frames. Probe error after notifier registration unregisters notifier only on adapter registration failure. A formatting anomaly leaves leading spaces in suspend assignments but compiles. Parent callbacks must be valid during IRQ handling and suspend/resume.

Test signals: CEC adapter registration, logical address allocation/clear, transmit outcomes for OK/NACK/arbitration lost/error, receive EOM frames of 1-16 bytes, enable/disable masking, suspend/resume retaining addresses, and shared IRQ behavior when no CEC status is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.h

Purpose: declares the callback and platform-data contract for the classic DW-HDMI CEC companion platform driver.

Important APIs/types/functions: `struct dw_hdmi_cec_ops` provides parent callbacks for register `write`, register `read`, hardware CEC `enable`, and `disable`. `struct dw_hdmi_cec_data` passes the parent `dw_hdmi` pointer, ops table, and IRQ to the CEC child.

Control flow: no executable code. The parent HDMI driver creates a `dw-hdmi-cec` platform device with this data; `dw-hdmi-cec.c` consumes it at probe and during CEC adapter operations.

State and persistence: no owned state; all fields are references to parent state or IRQ resources.

Dependencies and integration: depends on an opaque `struct dw_hdmi` and CEC companion driver agreement about register offsets.

Risks: invalid ops pointers or IRQ cause runtime failures. The ABI is private to in-kernel platform data but still must stay synchronized with parent DW-HDMI code.

Test signals: compile coverage for parent and child, CEC platform device creation, and callback invocation during adapter enable/transmit/receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-gp-audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-gp-audio.c

Purpose: provides a lightweight HDMI-codec based audio interface for the DesignWare HDMI General Purpose Audio path, mainly used by NXP platforms.

Important APIs/types/functions: `struct snd_dw_hdmi` stores copied `dw_hdmi_audio_data` and the registered HDMI codec platform device. `audio_hw_params()` programs sample rate, channel count, channel allocation, non-PCM flag, sample width, and IEC958 subframe mode through DW-HDMI core APIs. `audio_mute_stream()` toggles DW-HDMI audio enable/disable. `audio_get_eld()` copies ELD from the parent connector. `audio_hook_plugged_cb()` registers HDMI hotplug callback. Probe registers an `HDMI_CODEC_DRV_NAME` child with I2S enabled, SPDIF disabled, max 8 channels, and the ops table.

Control flow: the platform driver receives parent-provided `dw_hdmi_audio_data`, copies it, and creates an hdmi-codec device. During playback setup the ASoC HDMI codec calls `hw_params`, then mute/unmute controls audio start/stop. Remove unregisters the codec device.

State and persistence: driver-owned state is only copied platform data and codec pdev pointer. Audio parameters are pushed to parent DW-HDMI state on each hw_params call; no local stream state is tracked.

Dependencies and integration: depends on `sound/hdmi-codec.h`, ALSA IEC958 constants, DRM ELD/connector headers, and DW-HDMI exported audio control functions. It shares channel allocation defaults with the AHB driver.

Risks: `params->channels - 2` indexes a seven-entry table without local bounds checks, relying on hdmi-codec constraints. `audio_shutdown()` is empty, so mute callbacks must perform actual stop. Probe assumes non-NULL platform data. GP-specific hardware enablement is delegated entirely to the parent core.

Test signals: hdmi-codec registration, 2-8 channel LPCM and IEC958 formats, ELD reads with and without connector, plug callback propagation, mute/unmute behavior, and remove/unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-gp-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-i2s-audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-i2s-audio.c

Purpose: implements the ASoC HDMI-codec bridge for the DesignWare HDMI I2S audio input. It configures DW-HDMI audio registers through parent-provided read/write callbacks and exposes codec operations for SoC audio graphs.

Important APIs/types/functions: `dw_hdmi_i2s_hw_params()` validates codec clock-provider roles, resets I2S FIFOs, enables I2S lanes by channel count, selects sample width and I2S/left/right-justified/DSP format, then programs DW-HDMI sample rate, channel status, count, allocation, and audio registers. Startup/shutdown enable/disable HDMI audio. `dw_hdmi_i2s_get_eld()` returns parent ELD. `dw_hdmi_i2s_get_dai_id()` maps OF graph port 2 to DAI id 0. Probe registers an `HDMI_CODEC_DRV_NAME` platform device with I2S support and max 8 channels.

Control flow: parent creates this child with `dw_hdmi_i2s_audio_data`. Probe wraps it in hdmi-codec pdata. On stream startup the codec enables HDMI audio; hw_params applies register configuration; shutdown disables audio. OF DAI lookup lets sound-card graph bindings identify the HDMI audio port.

State and persistence: no substantial local state after registering the codec pdev. Hardware audio format state persists in DW-HDMI registers until changed or reset.

Dependencies and integration: depends on ASoC HDMI codec, DRM bridge DW-HDMI headers for register constants, OF graph endpoint parsing, DMA mask setup for the codec pdev, and parent callbacks from `dw-hdmi-audio.h`.

Risks: uses bitwise OR in the clock-provider check; this works for booleans/bit values but is less idiomatic than logical OR. Unsupported sample widths leave `conf1` width bits at zero rather than failing unless format is unsupported. Lane enable depends on channel count constraints from upper layers. DAI id is hard-coded to OF port 2.

Test signals: ASoC card binding through port 2, hw_params for 2/4/6/8 channels, I2S/left/right/DSP formats, 16/24/32-bit samples, ELD propagation, plug callback, and startup/shutdown around display hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-i2s-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-qp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-qp.c

Purpose: implements the Synopsys DesignWare HDMI QP transmitter core library. It provides the DRM HDMI bridge, MMIO regmap access, DDC/I2C controller, HDMI infoframe packet programming, HDMI audio callbacks, optional CEC adapter callbacks, top-level IRQ handling, and bind/suspend/resume entry points used by platform-specific PHY wrappers.

Important APIs/types/functions: `struct dw_hdmi_qp` stores DRM bridge, device, DDC adapter state, optional CEC state, platform PHY ops/data, reference clock rate, regmap, main IRQ, current TMDS character rate, and `no_hpd`. Exported `dw_hdmi_qp_bind()` validates PHY ops, maps/registers MMIO, initializes hardware, requests IRQ, creates DDC adapter, fills bridge HDMI/audio/CEC metadata, adds the bridge, and attaches to the encoder. Audio helpers compute/program N/CTS (`dw_hdmi_qp_find_n()`, `dw_hdmi_qp_find_cts()`, `dw_hdmi_qp_set_cts_n()`), configure I2S input, channel status, and audio infoframes. DDC helpers implement `i2c_algorithm` over QP I2CM registers. Bridge ops cover detect, EDID, TMDS rate validation, infoframe clear/write, audio startup/prepare/shutdown, and optional CEC init/enable/log/transmit.

Control flow: bind initializes masks/timer/I2CM and platform HPD, requests the main IRQ used for I2C completion, reads `no-hpd`, then registers bridge capabilities. Detect either reads EDID over DDC when HPD is unavailable or delegates HPD to PHY ops. Atomic enable determines HDMI vs DVI mode from connector display info, records TMDS rate for audio, initializes PHY, bypasses HDCP2, sets DVI/HDMI op mode, and asks DRM HDMI helpers to emit infoframes. Atomic disable clears TMDS rate and disables PHY. Infoframe write callbacks clear packet scheduler bits, write packed header/body words to packet content registers, and enable the relevant scheduler bits. Audio prepare requires a live TMDS rate, configures I2S/audio packet registers, computes N/CTS, sets channel status, and updates the audio infoframe.

State and persistence: `tmds_char_rate` gates audio availability and is reset on atomic disable. `dw_hdmi_qp_i2c` persists DDC transfer state (`slave_reg`, segment flag, completion, IRQ status) and serializes transfers with a mutex. Optional CEC state stores logical addresses, RX message, and TX/RX done flags. Hardware state in reset manager, I2CM, packet scheduler, audio packetizer, CEC, and PHY is volatile and refreshed by init/resume or modeset paths.

Dependencies and integration: depends on DRM HDMI bridge/state helpers, DRM HDMI CEC helper, CEC core types, hdmi-codec types, regmap MMIO, Linux I2C adapter framework, completions, platform `dw_hdmi_qp_plat_data` PHY callbacks, and register definitions in `dw-hdmi-qp.h`. Platform wrappers supply MMIO, IRQs, ref clock rate, supported formats/max bpc, and PHY behavior.

Risks: TMDS rate validation caps at HDMI 1.4 340 MHz and the TODO notes `no_hpd` should reject scrambling-required modes; HDMI 2.0+ paths are therefore intentionally limited. DDC/CI is blacklisted because the controller cannot support needed multi-byte operations. I2C read/write timeouts reset the I2CM controller but leave higher-level retry policy to callers. Audio table indexes and sample-rate handling rely on hdmi-codec constraints. CEC IRQ reads four 32-bit RX data registers regardless of clamped frame length, which is acceptable for a 16-byte FIFO but should remain aligned with hardware. Suspend only disables the main IRQ; platform code must handle PHY/power state.

Test signals: DDC EDID reads including segment pointer reads and NACK/timeouts, HPD and `no-hpd` detect paths, HDMI vs DVI modesets, AVI/VSI/HDR/SPD/audio infoframe emission and clearing, TMDS rate rejection above 340 MHz, I2S audio startup/prepare/shutdown at common sample rates, CEC transmit/receive/logical address when enabled, and suspend/resume reinitializing I2CM and IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-qp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-qp.h

Purpose: defines the register map and bit fields for the DesignWare HDMI QP transmitter used by `dw-hdmi-qp.c` and platform wrappers.

Important APIs/types/functions: the header covers main-unit identification/config/reset/timer/CMU, I2CM/DDC, SCDC/FRL training, video interface and packing, audio interface and audio packetizer, frame composer, video monitor, HDCP2/HDCP1.4, scrambler/link config, TMDS/FRL packet scheduler, general packet content registers, EMP packetizer, CEC registers, eARC RX CMDC/DMAC registers, and main/AVP/CEC/eARC interrupt registers. It provides masks such as `I2CM_WR_MASK`, `PKTSCHED_*_TX_EN`, `AUDPKT_*`, `CEC_STAT_*`, and interrupt clear/mask bits.

Control flow: no executable flow; C code uses these constants with regmap read/write/update operations to reset blocks, perform I2C transfers, program infoframes/audio, handle CEC, and manage interrupts.

State and persistence: no driver state. The definitions describe volatile hardware register fields, many of which preserve state until reset or explicit write.

Dependencies and integration: includes `linux/bits.h` for `BIT`/`GENMASK`. It is tightly coupled to the QP hardware programming model and the offsets used by the bridge library. Platform code should use exported library APIs rather than directly reprogramming these registers unless implementing PHY-specific setup.

Risks: register definitions are low-level and largely untyped; incorrect masks or offsets can silently corrupt unrelated hardware blocks. Several blocks such as FRL/eARC/HDCP are defined even when the current C implementation only uses a subset, so future code must validate hardware version support. Comments contain minor typos but not behavioral issues.

Test signals: compile use by `dw-hdmi-qp.c`, register access smoke tests through probe/init, DDC/audio/infoframe/CEC paths that exercise the used masks, and review against Synopsys/Rockchip register documentation when enabling currently unused FRL/eARC/HDCP fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-qp.h -->
