# subset-b-003641 research

Grouped research for selected MediaTek and Amlogic Meson DRM display driver files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dsi.c

## Purpose
Implements the MediaTek MIPI DSI controller as both a DRM bridge and a `mipi_dsi_host`. It owns controller register programming, D-PHY timing setup, panel/bridge attachment, command-mode transfers, video-mode start/stop, and component binding into the MediaTek DRM pipeline.

## Important APIs, types, and functions
- `struct mtk_dsi` stores host, bridge, encoder, connector, PHY, clocks, current videomode, format/lanes/mode flags, IRQ wait state, and SoC-specific `mtk_dsi_driver_data`.
- `mtk_dsi_poweron()` and `mtk_dsi_poweroff()` are the main refcounted hardware sequencing paths.
- Bridge callbacks include `mtk_dsi_bridge_attach()`, `mtk_dsi_bridge_mode_set()`, atomic pre-enable/enable/disable/post-disable, and `mtk_dsi_bridge_mode_valid()`.
- Host callbacks are `mtk_dsi_host_attach()`, `mtk_dsi_host_detach()`, and `mtk_dsi_host_transfer()`.
- DDP integration exports `mtk_dsi_ddp_start()`, `mtk_dsi_ddp_stop()`, and `mtk_dsi_encoder_index()`.

## Control flow
Probe allocates the bridge-backed DSI object, resolves engine/digital/HS clocks, MMIO, D-PHY, IRQ, initializes the wait queue, registers the MIPI DSI host, and installs an IRQ handler. Host attach records the attached panel/bridge parameters, resolves the next bridge from the OF graph with an old-DT fallback, adds the DRM bridge, and registers the component. Component bind creates the DRM encoder, attaches the internal bridge, and creates a bridge connector.

During atomic pre-enable, `mtk_dsi_poweron()` calculates HS data rate from pixel clock, bpp, and lanes, sets `hs_clk`, powers the PHY, enables clocks, enables/reset the controller, programs optional shadow-control bypass, computes D-PHY timing, writes pixel stream and video timing registers, enables DSI interrupts, prepares lanes, and enters HS clock mode. Atomic enable sets command/video mode and starts the engine. Disable/post-disable clear the enabled flag and then stop the engine, wait for video-mode completion, reset, enter ULPM, pull down lanes, disable clocks, and power down the PHY.

Command transfers temporarily stop video mode if needed, switch to command mode using VM-done IRQ synchronization, prepare lane state, write CMDQ payload/registers, start the engine, wait for CMD-done and optional LPRX-ready interrupts, read up to 16 bytes from RX registers, clamp to caller buffer length, and restore the previous video mode.

## State and persistence
Runtime state lives in `struct mtk_dsi`: `refcount`, `enabled`, `lanes_ready`, `irq_data`, `data_rate`, cached display mode and DSI bus parameters. Hardware state persists in controller, PHY, CMDQ, timing, interrupt, lane, and mode registers until reset or poweroff. The code uses a wait queue plus IRQ status bits as transient synchronization state for mode switches and command completion.

## Dependencies and integration points
Depends on DRM bridge/bridge-connector helpers, MIPI DSI host APIs, DRM OF graph bridge lookup, MediaTek component/DDP helpers, `mtk_find_possible_crtcs()`, Linux PHY and clock APIs, optional reset control, and SoC match data for register offsets/features. It integrates with downstream panels/bridges through the MIPI host and with the display pipeline through the component framework and DDP start/stop hooks.

## Risks
Timing and lane sequencing are hardware-sensitive. Errors in bpp/lane-derived HS rate, per-frame versus per-line low-power timing, CMDQ packet sizing, or ULPM transitions can produce blank panels or transfer timeouts. `mtk_dsi_recv_cnt()` computes long-read length as `read_data[1] + read_data[2] * 16`, which is notable because MIPI long packet length is normally byte-low plus byte-high shifted by 8. Refcounted power paths also rely on balanced DDP and bridge calls.

## Test signals
Useful signals are DSI IRQ timeout warnings, `failed to switch cmd mode`, mode-valid rejections above 1.5 Gbps/lane, panel command read logs, and visible panel bring-up across command and video modes. Test matrices should cover all matched SoC data variants, 1-4 lane panels, RGB565/666/888, burst/sync-pulse/sync-event modes, non-continuous clock, suspend/resume, and command transfers while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.c

## Purpose
Implements the MediaTek ETHDR display block, including mixer setup, HDR front-end/back-end bypass configuration, layer blending, vblank IRQ callback plumbing, clocks, resets, and component binding for the DRM pipeline.

## Important APIs, types, and functions
- `struct mtk_ethdr` stores seven MMIO subcomponents, 13 bulk clocks, MMSYS device pointer, optional IRQ, reset control, and vblank callback state.
- `mtk_ethdr_config()` initializes HDR blocks in bypass mode and configures mixer ROI, background, datapath, and MMSYS HDR routing.
- `mtk_ethdr_layer_config()` programs per-layer size, offset, alpha/blend mode, and MMSYS mixer input configuration.
- `mtk_ethdr_start()`, `mtk_ethdr_stop()`, `mtk_ethdr_clk_enable()`, and `mtk_ethdr_clk_disable()` are lifecycle hooks.
- `mtk_ethdr_register_vblank_cb()`, `mtk_ethdr_enable_vblank()`, and related helpers connect frame-complete interrupts to the CRTC.

## Control flow
Probe maps all ETHDR sub-block resources by index, optionally captures CMDQ client register bases, acquires named clocks, requests an IRQ if present, obtains reset controls, and adds a component. Bind stores the MMSYS device pointer supplied by the master. Configuration first bypasses VDO/GFX HDR front-ends and VDO back-end, enables function DCM, sets mixer ROI/background/source defaults, enables layer 0, then asks MMSYS to configure HDR half-width routing and mixer channel swap. Per-layer updates either clear the layer size to disable without switching mixer mode or program aligned even width, offset, alpha, premultiplied/non-premultiplied mode, and source enable bit through CMDQ writes.

## State and persistence
Persistent driver state is limited to mapped resources, clocks, callback pointers, and reset control. Per-frame or per-atomic state arrives from `struct mtk_plane_state` and is committed into hardware registers through CMDQ packets. The vblank callback pointer remains valid until explicitly unregistered; hardware interrupt enable state persists in the mixer registers.

## Dependencies and integration points
Depends on MediaTek CMDQ/DDP write helpers, MMSYS mixer/HDR routing helpers, DRM blend constants, component framework, reset controller API, and platform clocks. It is called by MediaTek CRTC/display component code for blend capability discovery, layer configuration, top-level mode configuration, and vblank handling.

## Risks
Layer widths are aligned down to an even number and odd x coordinates use MMSYS even-extend mode, so off-by-one behavior can show as shifted or clipped output. Disabling a layer by zeroing size instead of `MIX_SRC_CON` is intentional hardware workaround territory. Callback registration is unsynchronized with IRQ handling, so callers must manage lifetime carefully. Missing CMDQ base lookup is only debug-logged, which may matter on systems that require command-queue programming.

## Test signals
Signals include frame-complete IRQ delivery, vblank callback behavior, layer enable/disable without screen shift, premultiplied/coverage/pixel-none blend results, odd x positions, four-layer limits, reset behavior on stop, and clock/reset errors during probe or enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.h

## Purpose
Declares the ETHDR component interface consumed by MediaTek display pipeline code.

## Important APIs, types, and functions
The header declares lifecycle hooks (`mtk_ethdr_start()`, `mtk_ethdr_stop()`, clock enable/disable), mode configuration (`mtk_ethdr_config()`), blend-mode discovery (`mtk_ethdr_get_blend_modes()`), layer programming (`mtk_ethdr_layer_config()`), and vblank callback registration/control helpers.

## Control flow
There is no runtime control flow in this header. It exposes a narrow procedural API around an opaque `struct device *` so callers do not need access to `struct mtk_ethdr`.

## State and persistence
No state is stored here. The declared functions mutate ETHDR hardware and internal callback state in `mtk_ethdr.c`.

## Dependencies and integration points
The declarations reference `struct cmdq_pkt`, `struct mtk_plane_state`, and Linux/DRM scalar types through transitive includes. The integration point is MediaTek CRTC/DDP component orchestration.

## Risks
Because the API is device-pointer based, incorrect device routing will not be caught by type checking. Header changes have build impact on MediaTek display component users.

## Test signals
Build coverage catches signature drift. Runtime validation belongs to ETHDR CRTC integration, especially blend modes, layer programming, vblank enable/disable, and clock sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi.c

## Purpose
Implements the original MediaTek HDMI transmitter driver for MT2701/MT8167/MT8173-era HDMI IP. It provides DRM bridge callbacks, hardware register programming, CEC-backed HPD, EDID reads over DDC, audio codec callbacks, infoframe emission, PLL/PHY sequencing, and SoC-specific mode limits.

## Important APIs, types, and functions
- Uses shared `struct mtk_hdmi` from `mtk_hdmi_common.h`.
- Hardware helpers cover register write authorization, reset, DVI/HDMI mode, AV mute/unmute, video blacking, deep color, N/CTS, audio routing, I2S/SPDIF setup, and infoframes.
- Bridge callbacks are collected in `mtk_hdmi_bridge_funcs`.
- Codec callbacks are collected in `mtk_hdmi_audio_codec_ops`.
- `mtk_hdmi_probe()` calls `mtk_hdmi_common_probe()`, requires CEC, and enables audio clocks.

## Control flow
Common probe performs allocation and DT parsing; this v1 probe then requires a CEC device because HPD status is delegated through `mtk_cec_hpd_high()` and registers a CEC HPD event callback on bridge attach. Atomic pre-enable makes HDMI registers writable, optionally through secure monitor call unless `tz_disabled`, enables HDMI 1.4 mode, and marks the block powered. Atomic enable retrieves the connector from atomic state, calls `mtk_hdmi_output_set_display_mode()`, enables PLL/pixel clocks, powers the PHY, sends audio/AVI/SPD/vendor infoframes, and marks enabled.

Mode programming blacks video, mutes audio, sends AV mute, powers the PHY off, sets the HDMI PLL to pixel clock, toggles system FIFO/deep-color bits, resets/configures HDMI registers, powers PHY on, configures audio output, then unblacks/unmutes. Audio hw params validate shared audio parameters, program channel mapping, input type, sample size, channel status, MCLK, and N/CTS, then enable audio packets.

## State and persistence
`struct mtk_hdmi` persists current mode, `dvi_mode`, `powered`, `enabled`, `audio_enable`, audio params, current connector pointer, CEC/DDC devices, clocks, PHY, and callback registration. Hardware state persists in GRL and syscon registers, PHY state, PLL clock rate, infoframe registers, and CEC HPD callback wiring.

## Dependencies and integration points
Depends on the shared HDMI common library, `mtk_cec`, HDMI codec framework, DRM bridge/EDID/infoframe helpers, regmap/syscon, SMC secure-register service, clocks, PHY, DDC I2C adapter, and OF graph bridge chaining. It integrates as a DRM bridge and as a platform-provided HDMI codec device.

## Risks
Power sequencing is delicate: register write authorization, HDMI_ON/ANLG_ON, 1.4 mode, PLL, PHY, and infoframes must happen in the right order. HPD depends on CEC, making v1 probe fail without CEC. EDID read sets `dvi_mode` using raw EDID audio detection rather than the newer connector display-info path. Audio hw params ignore return from `mtk_hdmi_audio_params()` in the callback. Mode validation has both generic HDMI limits and SoC-specific CEA/max-clock filters.

## Test signals
Signals include HPD notifications from CEC, EDID read success, mode validation at 27 MHz/297 MHz and MT8167 148.5 MHz CEA-only limits, audio startup/hw_params/mute/shutdown, N/CTS values, DVI-mode behavior for no-audio monitors, suspend/resume audio clock recovery, and visible AV mute/unmute during modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.c

## Purpose
Provides shared infrastructure for MediaTek HDMI v1 and v2 drivers: ACR N/CTS calculation, audio parameter validation/storage, ELD and plugged-callback helpers, bridge mode storage, DT parsing, CEC/DDC discovery, audio codec registration, bridge initialization, and common probe allocation.

## Important APIs, types, and functions
- `mtk_hdmi_get_ncts()` computes HDMI recommended N and expected CTS.
- `mtk_hdmi_audio_params()` validates codec DAI params and stores normalized `struct hdmi_audio_param`.
- `mtk_hdmi_audio_get_eld()` and `mtk_hdmi_audio_set_plugged_cb()` serve HDMI codec callbacks.
- `mtk_hdmi_bridge_mode_fixup()` and `mtk_hdmi_bridge_mode_set()` are shared bridge callbacks.
- `mtk_hdmi_common_probe()` is the exported common probe entry for both hardware versions.

## Control flow
N/CTS calculation first selects HDMI-spec recommended N for common TMDS clocks and sample families, then computes CTS from exact 1000/1001-adjusted pixel-clock values where needed. Audio params accept only 2/4/6/8 channels, common sample rates, and I2S or SPDIF, then populate the shared audio state used by hardware-specific code. DT parsing obtains all version-specific clocks, IRQ, register regmap, optional next bridge, DDC adapter from the connector's `ddc-i2c-bus`, optional CEC device/syscon, and device-managed put actions. Common probe allocates a bridge-backed `struct mtk_hdmi`, stores config, parses DT, gets the PHY, initializes the plugged-callback mutex, registers an `hdmi-codec` platform device, fills bridge operations and HDMI infoframe capabilities, and adds the bridge.

## State and persistence
Shared persistent state is `struct mtk_hdmi`, including mode, audio params, callback pointers, DDC/CEC references, clocks, PHY, register maps, current connector, and bridge metadata. Audio codec platform device lifetime is tied to devm cleanup. The function stores bridge mode and audio params for later hardware-specific programming.

## Dependencies and integration points
Depends on DRM HDMI/EDID/bridge helpers, Linux HDMI codec framework, OF graph and phandle parsing, I2C adapter lookup, regmap/syscon, PHY, platform devices, and version-specific `mtk_hdmi_conf` supplied as OF match data. It is the shared ABI used by `mtk_hdmi.c` and `mtk_hdmi_v2.c`.

## Risks
The DDC adapter and external bridge are probe-order sensitive. CEC lookup is optional in common code but mandatory for v1. The registered codec data advertises `max_i2s_channels = 2` even though shared audio params accept up to 8 channels, so hardware-specific expectations need care. `mtk_hdmi_audio_get_eld()` depends on `curr_conn` being valid when `enabled`.

## Test signals
Signals include successful bridge registration, audio codec platform device creation, DDC adapter discovery, optional CEC unavailable log, mode storage logs, accepted/rejected audio params, and correct N/CTS values for 25.175/74.176/148.352/296.703 MHz and common sample rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.h

## Purpose
Defines the shared MediaTek HDMI data model, audio enums, SoC/version configuration, and common function declarations used by HDMI v1/v2 implementations and their HDMI codec integration.

## Important APIs, types, and functions
- Audio enums describe input type, I2S format, MCLK ratio, many CEA channel layouts, and channel swap modes.
- `struct hdmi_audio_param` wraps HDMI codec parameters plus normalized MediaTek audio choices.
- `struct mtk_hdmi_ver_conf` describes per-IP bridge functions, codec ops, clock names/count, and interlace support.
- `struct mtk_hdmi_conf` describes per-SoC quirks such as TrustZone disablement, CEA-only modes, max clock, and v2 TX config register.
- `struct mtk_hdmi` is the shared runtime object used by all HDMI files.

## Control flow
The header only contains the `hdmi_ctx_from_bridge()` container helper. All other behavior is implemented in common or version-specific C files.

## State and persistence
The central persistent state definition is `struct mtk_hdmi`: bridge, current connector, device/config pointers, PHY, CEC/DDC resources, clocks, current mode, DVI flag, register maps, audio codec platform device, audio params, powered/enabled flags, IRQ/HPD state, plugged callback, and callback mutex.

## Dependencies and integration points
Includes DRM atomic/bridge/CRTC/EDID/print headers, Linux clock/device/HDMI/I2C/regmap/mutex/PHY/platform headers, and `sound/hdmi-codec.h`. It is the common contract between `mtk_hdmi_common.c`, `mtk_hdmi.c`, `mtk_hdmi_v2.c`, and DDC/codec users.

## Risks
This header is broad and exposes many audio channel enum values; semantic mismatch between shared enums and hardware-specific channel maps can cause audio layout bugs. The include guard and function declarations are compile-time critical for both HDMI modules.

## Test signals
Build coverage across v1 and v2 is the primary signal. Runtime coverage is shown by shared audio params, bridge callbacks, HPD callback storage, and the same `struct mtk_hdmi` supporting both HDMI IP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc.c

## Purpose
Implements the original MediaTek HDMI DDC controller as a Linux I2C adapter for EDID and HDMI sink transactions.

## Important APIs, types, and functions
- `struct mtk_hdmi_ddc` stores the I2C adapter, DDC clock, and MMIO base.
- `mtk_hdmi_ddc_xfer()` is the adapter transfer implementation.
- `mtk_hdmi_ddc_read_msg()` and `mtk_hdmi_ddc_write_msg()` perform hardware start/address/data/read/write sequences.
- `ddcm_trigger_mode()` selects a DDCM mode, triggers it, and polls completion.
- Probe registers the adapter named `mediatek-hdmi-ddc`.

## Control flow
Probe obtains the `ddc-i2c` clock and MMIO resource, enables the clock for adapter lifetime, initializes adapter metadata, and calls `i2c_add_adapter()`. Each transfer enables clock stretching and state-machine mode, rejects a busy trigger bit, writes the fixed clock divider, then executes each I2C message. Writes emit START, address byte, one payload byte, expect ACK mask `0x03`, and stop. Reads emit START, address-read byte, then read in chunks of up to 8 bytes with ACK on intermediate chunks and NACK on the final chunk, copying hardware data registers back into the caller buffer. All paths send STOP on completion or error.

## State and persistence
The adapter and enabled DDC clock persist while the platform device exists. Hardware state persists in DDCM control/data registers during a transaction. No runtime PM is used; the clock is prepared at probe and disabled at remove.

## Dependencies and integration points
Depends on Linux I2C core, platform MMIO/clock APIs, polling helpers, and the HDMI bridge's DT `ddc-i2c-bus` phandle lookup in common HDMI code. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

## Risks
Write support only sends address plus `msg->buf[0]`, so it is tailored to EDID offset writes rather than arbitrary long writes. Poll return from `ddcm_trigger_mode()` is ignored, which can hide timeout details. ACK bit interpretation is hardware-specific and transaction failures may appear as `-ENXIO`, `-EIO`, or `-EBUSY`. The clock is always on after probe.

## Test signals
Signals include `i2c ack err`, `ddc line is busy`, `Address NACK`, EDID reads through `drm_edid_read_ddc()`, adapter registration/removal, and repeated hotplug EDID access under marginal cable/sink conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc_v2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc_v2.c

## Purpose
Implements the HDMI v2 DDC controller as a Linux I2C adapter backed by the parent HDMI register map. It supports EDID/SCDC-style offset writes followed by reads, FIFO-based data movement, bus recovery, and HDCP polling disablement around foreground DDC transfers.

## Important APIs, types, and functions
- `struct mtk_hdmi_ddc` stores device, parent regmap, clock, and I2C adapter.
- `mtk_hdmi_ddc_v2_xfer()` implements adapter transfers and carries the last offset write into following reads.
- `mtk_ddcm_read_hdmi()` and `mtk_ddcm_write_hdmi()` program the DDC command engine.
- `mtk_ddc_check_and_rise_low_bus()` detects low bus/no-ACK and clocks SCL to recover.
- Probe registers the devm-managed adapter named `mediatek-hdmi-ddc-v2`.

## Control flow
Probe obtains the parent HDMI regmap, enables the unnamed DDC clock, enables runtime PM, takes a runtime reference, and registers the I2C adapter. Transfers validate message buffers. Writes pass `buf[0]` as the DDC offset and remaining bytes as payload; one-byte writes to EDID or SCDC slave addresses update the saved offset. Reads use that saved offset because the hardware emits the offset write internally as part of the read command.

Read flow clears FIFO, chooses 16-byte chunks, selects EDID-slower or normal delay counts, handles segment-address flow control for `0x51..0x53`, emits sequential/enhanced read commands, polls `DDC_I2C_IN_PROG`, checks no-ACK/low-bus status, then drains each byte through `SI2C_CTRL` read/confirm cycles. Write flow fills a 16-byte FIFO when payload exists, emits a sequential write command, polls completion, and rechecks bus status.

## State and persistence
Adapter and clock state persist for device lifetime. Runtime PM is enabled and a reference is taken at probe. Transfer-local state includes the saved offset in `mtk_hdmi_ddc_v2_xfer()`. Hardware state includes DDC delay count, FIFO contents, HDCP poll-disable bit, command status, and SCDC segment field.

## Dependencies and integration points
Depends on the parent HDMI v2 regmap, HDMI v2 register definitions, Linux I2C/PM runtime/clock APIs, DRM EDID constants, and SCDC I2C address behavior. The HDMI common probe later obtains this adapter through the connector's `ddc-i2c-bus`.

## Risks
The offset variable is local to one `master_xfer()` call, so clients must use normal combined write-then-read messages. A write with `msg->len == 0` would underflow `msg->len - 1` before lower-level validation. Debug reads in no-ACK handling are currently unused. Probe takes a runtime PM reference without an obvious paired put, intentionally or not keeping the block active.

## Test signals
Signals include EDID reads, SCDC reads/writes for scrambling, no-ACK errors, DDC I2C timeout logs, invalid read count warnings, FIFO chunk boundaries above 16 bytes, segment reads, and behavior across HDMI controller reset during EDID reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs.h

## Purpose
Defines register offsets, bit masks, and secure monitor call ID for the original MediaTek HDMI transmitter IP used by `mtk_hdmi.c`.

## Important APIs, types, and functions
The header covers GRL interrupt, control, status, infoframe, audio, channel status, N/CTS, ABIST, video config, and HDMI system configuration registers. Key masks include audio packet controls, DVI mode, AV mute/unmute, channel swap, I2S format, MCLK ratios, deep color, HDMI output FIFO, analog/HDMI enable, reset, and `MTK_SIP_SET_AUTHORIZED_SECURE_REG`.

## Control flow
This file is declarative. Callers combine these constants with regmap/syscon updates in the v1 HDMI driver.

## State and persistence
No C state is stored. The definitions describe persistent hardware register bits that control video, audio, infoframes, system power, and secure output authorization.

## Dependencies and integration points
Requires `BIT()` and related kernel bit macros from includers. It is tightly coupled to `mtk_hdmi.c` and indirectly to SoC syscon layout through `HDMI_SYS_CFG1C/20`.

## Risks
Incorrect bit definitions can directly break HDMI bring-up, audio routing, AV mute, or secure register access. The header contains a repeated `GRL_INT_MASK` definition with the same value; harmless for preprocessing, but it signals that edits should be checked carefully. Several fields are plain shifted masks rather than `GENMASK()`, so callers must pass already-aligned values or use update masks correctly.

## Test signals
Compile-time use catches missing symbols. Runtime signals are v1 HDMI modeset success, audio packet delivery, DVI mode selection, infoframe enablement, syscon power/reset behavior, and SMC/syscon authorization on TrustZone-enabled and `tz_disabled` SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs_v2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs_v2.h

## Purpose
Defines register offsets, bit fields, and DDC command enum for the newer MediaTek HDMI v2 transmitter used by `mtk_hdmi_v2.c` and `mtk_hdmi_ddc_v2.c`.

## Important APIs, types, and functions
The header covers HDMI top config, infoframe packet registers, audio mapping and AIP registers, video mute, downsampling, interrupts, HDCP/HPD/DDC/SCDC registers, SoC-specific TX config offsets, and `enum mtk_hdmi_ddc_v2_cmds`.

## Control flow
No runtime control flow exists in the header. The DDC command enum documents command values used by the DDC engine; all other definitions are consumed by regmap field programming in HDMI v2 and DDC v2 code.

## State and persistence
No C state is stored. The constants describe persistent HDMI controller state: scrambling, HDMI/DVI mode, TMDS packing, ABIST, infoframe enable/repeat bits, audio reset/mute/input format, downsampling, HPD/PORD status, DDC command/status, HDCP overrides, and TX reset/HPD/YUV420 mode.

## Dependencies and integration points
Uses `BIT()`, `GENMASK()`, and `FIELD_PREP/FIELD_GET` conventions from includers. It is shared by the v2 bridge driver and v2 DDC adapter, so it is the key integration contract between display, audio, HPD, DDC, SCDC, and HDCP-adjacent hardware setup.

## Risks
Register definitions are platform-specific and include MT8188 versus MT8195 TX config offsets; a wrong `reg_hdmi_tx_cfg` value can break reset, HPD override, or YUV420 mode. Audio bitfield polarity and packet layout flags are easy to misprogram. DDC command values control bus transactions directly and can hang or abort EDID/SCDC access if wrong.

## Test signals
Runtime signals include HDMI v2 hotplug interrupts, SCDC scrambling toggles, RGB/YUV444/YUV422/YUV420 output, infoframe updates through DRM HDMI helpers, DDC EDID reads, audio startup/mute/reset, ABIST debugfs behavior, and MT8188/MT8195-specific bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs_v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_v2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_v2.c

## Purpose
Implements MediaTek HDMI v2 transmitter support for MT8188/MT8195-class hardware. It provides DRM bridge and HDMI helper callbacks, HPD/PORD IRQ handling, runtime PM and clock sequencing, SCDC scrambling, color downsampling, infoframe programming, audio codec support, PHY configuration, and debugfs ABIST control.

## Important APIs, types, and functions
- `mtk_v2_hdmi_bridge_funcs` includes attach/detach, HPD enable/disable, EDID, detect, HDMI infoframe write/clear callbacks, TMDS-rate validation, atomic enable/disable sequencing, and debugfs init.
- `mtk_hdmi_v2_enable()` / `mtk_hdmi_v2_disable()` wrap runtime PM and four clocks.
- `mtk_hdmi_v2_change_video_resolution()` programs reset, HPD override, HDCP-related HPD state, packing, deep color, HDMI mode, mute, scrambling, and output format downsampling.
- Audio helpers configure I2S, SPDIF, HBR, DSD, channel maps, N/CTS, channel status, infoframes, mute, reset, and packet drop.
- `mtk_hdmi_v2_isr()` and threaded handler debounce HPD/PORD changes.

## Control flow
Probe populates subdevices, calls common HDMI probe, initializes HPD state, disables and clears all interrupts, requests a threaded IRQ with `IRQ_NOAUTOEN`, and enables runtime PM. Bridge attach chains any downstream bridge, powers the controller, enables HPD/PORD debounce, enables the IRQ, performs an immediate non-debounced status check via the ISR thread helper, then powers down again.

Atomic pre-enable powers the controller/clocks, retrieves connector and connector state, configures HDMI controller and PHY before DPI output starts, powers the PHY, and marks powered. Atomic enable updates DRM HDMI infoframes, unmutes video, notifies the audio codec as plugged, and marks enabled. Disable sends GCP AV mute, mutes video/audio with delays, and post-disable powers the PHY off, notifies codec disconnect, and releases clocks/runtime PM.

HPD IRQ top half disables HPD/PORD interrupts, clears status, and wakes the thread. The thread debounces 30 ms, reads HPD/PORD pins, updates `hdmi->hpd`, notifies DRM hotplug if changed, and reenables interrupts. HPD enable/disable bridge ops power the controller solely to manage IRQs.

## State and persistence
Shared `struct mtk_hdmi` stores current mode, current connector, HPD enum, powered/enabled flags, audio params, callback state, clocks, PHY, IRQ, and regmap. Hardware state includes TOP/AIP/infoframe/HDCP/DDC/TX config registers, SCDC sink state for scrambling, PHY link rate, and debugfs ABIST enablement.

## Dependencies and integration points
Depends on `mtk_hdmi_common`, HDMI v2 register definitions, DRM HDMI state/helper APIs, SCDC helpers, DRM EDID, runtime PM, Linux PHY, debugfs, clocks, threaded IRQs, and parent DDC subdevice population. It is the modern MediaTek HDMI bridge and HDMI codec implementation.

## Risks
The enable path is order-sensitive because HDMI must be configured before DPI output. Scrambling toggles both local registers and SCDC sink state and depends on `curr_conn`. HPD/PORD handling deliberately disables interrupts during debounce to avoid storms. Audio channel mapping is complex for PCM, DSD, HBR over I2S/SPDIF, and multichannel layouts. The debugfs write checks an unsigned value for `< 0`, which is ineffective though bounded by `> 1`.

## Test signals
Signals include HPD/PORD interrupt logs and hotplug events, EDID reads through v2 DDC, modes at 27-594 MHz, 340 MHz scrambling threshold and SCDC state, RGB/YUV444/YUV422/YUV420 output, DRM HDMI infoframe updates, audio codec plugged notifications, multichannel/HBR/DSD playback, runtime suspend/resume, and `hdmi_abist` debugfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.c

## Purpose
Implements a MediaTek MDP RDMA display component that reads framebuffer memory into the display pipeline. It exposes format support, CMDQ-backed configuration, start/stop, clock/runtime PM helpers, and component registration.

## Important APIs, types, and functions
- `struct mtk_mdp_rdma` stores MMIO, clock, and optional CMDQ client register base.
- `mtk_mdp_rdma_config()` programs source format, address, pitch, crop offset, size, clip, FIFO/ultra settings, compression disable, output mode, and YUV-to-RGB CSC.
- `mtk_mdp_rdma_start()` / `mtk_mdp_rdma_stop()` toggle enable and reset.
- `mtk_mdp_rdma_get_formats()` and `mtk_mdp_rdma_get_num_formats()` expose supported DRM formats.
- Power/clock helpers wrap PM runtime and clock APIs.

## Control flow
Probe maps MMIO, gets the clock, optionally gets CMDQ register metadata, enables runtime PM, and adds a component. Configuration converts DRM fourcc into hardware input format plus swap/10-bit flags, enables uniform config, sets ARGB output when appropriate, writes base address and pitch, disables AFBC/UFBDC, enables 10-bit/simple output fields, selects CSC matrix for YUV formats, calculates byte offset from crop x/y, and writes source/clip dimensions. Start sets enable; stop clears enable and pulses reset.

## State and persistence
Driver state is resource-oriented: registers, clock, CMDQ metadata. Frame-specific state comes from `struct mtk_mdp_rdma_cfg` and is written into hardware registers via `mtk_ddp_write*()` with optional CMDQ packet persistence until command execution.

## Dependencies and integration points
Depends on DRM format info, MediaTek DDP/CMDQ helpers, component framework, platform clocks/MMIO, PM runtime, and the config struct declared in `mtk_mdp_rdma.h`. It integrates with MediaTek CRTC/overlay-adaptor paths that need an RDMA memory source.

## Risks
`drm_format_info(cfg->fmt)` is assumed non-NULL. The exported `formats[]` list omits some formats that `rdma_fmt_convert()` can handle, which may be intentional for caller policy but should be understood before expanding. Address is `unsigned int` in the config header, so DMA addresses above 32 bits need scrutiny. CSC selection only distinguishes BT.709 and BT.601.

## Test signals
Signals include component probe/runtime PM, correct scanout for each advertised format, YUV CSC output, crop offsets, 10-bit formats if enabled by callers, RDMA reset on stop, CMDQ versus direct write behavior, and underflow/ultra FIFO behavior under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.h

## Purpose
Defines the configuration payload for MediaTek MDP RDMA programming.

## Important APIs, types, and functions
`struct mtk_mdp_rdma_cfg` carries pitch, base address, width, height, crop origin, DRM format, and DRM color encoding.

## Control flow
The header has no control flow. It is a data contract consumed by `mtk_mdp_rdma_config()`.

## State and persistence
The struct represents transient per-plane/per-update configuration; persistence occurs only after the implementation writes the values to RDMA registers or CMDQ packets.

## Dependencies and integration points
Used by MediaTek display code that prepares RDMA memory-source configuration. The fields line up with DRM framebuffer geometry and color metadata.

## Risks
`addr0` is `unsigned int` instead of `dma_addr_t`, which is a potential limitation on platforms or IOMMU setups with addresses beyond 32 bits. The header does not declare the functions implemented in `mtk_mdp_rdma.c`, so callers likely get those prototypes from `mtk_disp_drv.h`.

## Test signals
Build coverage catches struct field use. Runtime validation is correct RDMA scanout for base address, pitch, crop, format, and color encoding combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_mdp_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_padding.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_padding.c

## Purpose
Implements the MediaTek display padding component, currently used in bypass mode while ensuring padding registers are cleared to avoid undefined hardware behavior.

## Important APIs, types, and functions
- `struct mtk_padding` stores the module clock, MMIO base, and optional CMDQ register metadata.
- `mtk_padding_clk_enable()` / `mtk_padding_clk_disable()` wrap clock control.
- `mtk_padding_start()` enables the block in bypass mode and clears size, horizontal, vertical, and color registers.
- `mtk_padding_stop()` disables the control register.
- Probe maps resources, gets CMDQ metadata, enables runtime PM, and adds the component.

## Control flow
Probe obtains clock and MMIO, optionally retrieves GCE client register data, stores drvdata, enables runtime PM, and registers a component. Start writes `PADDING_ENABLE | PADDING_BYPASS`, then writes zero to all configuration registers because bypass still requires clean settings. Stop clears the control register. Bind/unbind are no-op component hooks.

## State and persistence
Persistent driver state is clock/MMIO/CMDQ resource data. Hardware state is only the padding control and cleared configuration registers. Runtime PM is enabled, but explicit exported start/stop and clock hooks are responsible for active use.

## Dependencies and integration points
Depends on component framework, platform MMIO/clock, PM runtime, optional MediaTek CMDQ, and `mtk_disp_drv.h` declarations. It integrates as a display pipeline component for MT8188-compatible padding nodes.

## Risks
The driver intentionally bypasses functionality, so future non-bypass padding support would need real geometry/color programming. `component_add()` failure manually calls `pm_runtime_disable()` despite using `devm_pm_runtime_enable()`, which is worth noting if cleanup paths change. CMDQ metadata is required when reachable and probe-fatal on failure.

## Test signals
Signals include successful component bind, clock enable/disable, bypass output with no artifacts, cleared register state after start, stop disable behavior, and PM runtime cleanup during probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_padding.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.c

## Purpose
Implements MediaTek DRM plane state management, atomic validation/update/disable, cursor async update support, framebuffer DMA address derivation, AFBC address calculations, and plane property initialization.

## Important APIs, types, and functions
- `mtk_plane_init()` creates a universal plane with formats/modifiers, immutable zpos, optional rotation, alpha, and blend-mode properties.
- Custom plane funcs handle reset, duplicate/destroy state, modifier support, and atomic update helpers.
- `mtk_plane_update_new_state()` translates DRM plane state and framebuffer metadata into `mtk_plane_pending_state`.
- Async helpers `mtk_plane_atomic_async_check()` and `mtk_plane_atomic_async_update()` are for cursor updates.

## Control flow
Reset allocates or clears `struct mtk_plane_state`, initializes DRM state, and defaults pending format/modifier. Atomic check calls MediaTek CRTC plane validation and DRM helper no-scaling checks. Atomic update returns for no CRTC/fb, disables invisible planes, otherwise computes pending state from framebuffer DMA object, source crop, destination rectangle, rotation, modifier, format, pitch, and color encoding, then marks pending dirty. Disable marks pending disabled and calls CRTC plane disable for the old CRTC. Async update copies positional state into the live state, recomputes pending state, swaps framebuffer references, marks `async_dirty`, and calls `mtk_crtc_async_update()`.

## State and persistence
Persistent plane state is `struct mtk_plane_state`, whose `pending` sub-struct is the handoff to CRTC/component programming. It stores enable/config flags, DMA addresses, AFBC header address/pitch, pitch, format, modifier, position, dimensions, rotation, dirty flags, and color encoding. Hardware persistence happens later when CRTC code consumes pending state.

## Dependencies and integration points
Depends on DRM atomic, GEM DMA, framebuffer format/modifier metadata, blend/rotation helpers, MediaTek CRTC hooks, and AFBC layout constants from `mtk_plane.h`. It integrates with all MediaTek display components that consume `mtk_plane_state`.

## Risks
Only `DRM_FORMAT_MOD_LINEAR` is reported as supported by `mtk_plane_format_mod_supported()`, while AFBC calculations exist and `mtk_plane_init()` can pass modifier lists when `supports_afbc` is true; modifier policy should be checked with callers. Address arithmetic uses `int offset` before adding to `dma_addr_t`, which is guarded by comments but still sensitive to large dimensions. Async update is restricted to the CRTC cursor and existing framebuffer.

## Test signals
Signals include atomic check failures, cursor async movement, primary/overlay scanout, disable paths, zpos immutability, alpha/blend property behavior, rotation property creation, AFBC-capable caller behavior, and correct DMA offsets for cropped framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.h

## Purpose
Defines MediaTek DRM plane state extensions and AFBC layout constants, and declares plane initialization.

## Important APIs, types, and functions
- AFBC constants define 32x8 data blocks, 16-byte header blocks, and 1024-byte header alignment.
- `struct mtk_plane_pending_state` carries configuration to be consumed by CRTC/display components.
- `struct mtk_plane_state` embeds `struct drm_plane_state` plus pending state.
- `to_mtk_plane_state()` provides container conversion.
- `mtk_plane_init()` is the exported initializer.

## Control flow
Only the inline `to_mtk_plane_state()` helper executes code; it maps a DRM plane state pointer to the MediaTek wrapper.

## State and persistence
The pending state fields persist across atomic state duplication and are copied in `mtk_plane_duplicate_state()`. Dirty flags indicate whether CRTC code must program new state, including async updates.

## Dependencies and integration points
Depends on DRM CRTC types and Linux scalar types. The header is consumed by MediaTek plane, CRTC, ETHDR, RDMA, and other display component code that reads pending plane configuration.

## Risks
The pending state is a cross-module contract; adding fields or changing semantics requires updating every component that consumes it. The `config` and `async_config` fields are declared here but not managed in `mtk_plane.c`, so their meaning is owned elsewhere.

## Test signals
Build coverage catches struct layout/prototype changes. Runtime signals are correct CRTC consumption of pending enable, dirty, async_dirty, address, format, modifier, geometry, rotation, blend, and color-encoding fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Kconfig

## Purpose
Defines Kconfig options for the Amlogic Meson DRM display controller and optional Synopsys HDMI/DSI encoder support.

## Important APIs, types, and functions
- `DRM_MESON` is the base tristate for the display controller.
- `DRM_MESON_DW_HDMI` enables Meson-specific DesignWare HDMI support.
- `DRM_MESON_DW_MIPI_DSI` enables Meson-specific DesignWare MIPI DSI support.

## Control flow
Kconfig dependency resolution selects DRM helper libraries, DMA GEM helpers, bridge connector support, display connector helpers, videomode helpers, MMIO regmap, Meson canvas, and optional CEC core. HDMI/DSI child options depend on the base driver and default to `y` when `DRM_MESON` is enabled.

## State and persistence
No runtime state is stored. Build configuration persists in kernel config and determines which objects are compiled.

## Dependencies and integration points
The base driver depends on DRM, OF, ARM/ARM64 or compile-test, and ARCH_MESON or compile-test. HDMI selects `DRM_DW_HDMI` and implies I2S audio. DSI selects `DRM_DW_MIPI_DSI` and `GENERIC_PHY_MIPI_DPHY`.

## Risks
Because child options default to enabled with the base driver, build and probe coverage includes HDMI/DSI unless explicitly disabled. Missing selects would show as link failures in the Makefile object set or runtime missing helpers.

## Test signals
Signals include allmodconfig/allyesconfig builds, Meson-only builds with and without HDMI/DSI options, CEC notifier combinations, and module load behavior for `meson-drm`, `meson_dw_hdmi`, and `meson_dw_mipi_dsi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Makefile

## Purpose
Builds the Meson DRM driver core and optional HDMI/DSI bridge modules from their source objects.

## Important APIs, types, and functions
`meson-drm-y` aggregates core objects: driver, plane, CRTC, CVBS/HDMI/DSI encoders, VIU, VPP, VENC, VCLK, overlay, RDMA, and AFBCD. `obj-$(CONFIG_DRM_MESON)` builds the aggregate, while HDMI and DSI configs build `meson_dw_hdmi.o` and `meson_dw_mipi_dsi.o`.

## Control flow
There is no runtime control flow. Kbuild includes object files according to the Kconfig symbols.

## State and persistence
No state is stored. Build outputs depend on selected config symbols.

## Dependencies and integration points
Ties the Kconfig options to compilation units. The core object list mirrors the initialization sequence in `meson_drv.c`, where encoders, planes, overlays, CRTC, VIU/VPP/VENC/VCLK/RDMA, and AFBCD code are all used.

## Risks
Adding a new core source without updating `meson-drm-y` causes link or missing-feature failures. Optional HDMI/DSI objects are separate modules/objects and must match Kconfig dependencies.

## Test signals
Signals are successful kernel builds for `DRM_MESON=y/m`, optional HDMI/DSI combinations, and no unresolved symbols from the aggregate object list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.c

## Purpose
Implements the Amlogic Meson DRM CRTC. It controls vblank enable/disable, atomic CRTC enable/disable/begin/flush, VPP/VIU blender setup, OSD1 and VD1 register commits at vblank, AFBC enable/disable paths, canvas programming, and vblank event delivery.

## Important APIs, types, and functions
- `struct meson_crtc` wraps `drm_crtc` and stores pending vblank event, private driver pointer, SoC-specific enable callbacks, VIU offset, and vblank force/disable flags.
- `meson_crtc_create()` initializes the CRTC with primary plane and SoC-specific helper callbacks.
- `meson_crtc_irq()` is called from the top-level driver IRQ and performs deferred register commits and event handling.
- Helper callbacks include GX/GXL/GXM and G12A atomic enable/disable variants and OSD/VD enable callbacks.

## Control flow
CRTC creation allocates the wrapper, calls `drm_crtc_init_with_planes()`, then selects G12A-specific or legacy helper functions. Atomic enable programs postblend/preblend and output sizes, then turns vblank on. Atomic disable turns vblank off, clears OSD1/VD1 enabled and commit flags, disables legacy postblend paths where applicable, and sends inactive-state events.

Atomic begin steals any pending CRTC event into `meson_crtc->event` after taking a vblank reference. Atomic flush marks OSD1 and VD1 commit flags. On each vblank IRQ, if OSD1 is enabled and committed, the handler writes cached VIU and scaler registers, handles AFBC setup/reset/enable/disable, configures canvas for linear OSD, enables OSD1 blending, and clears the commit flag. If VD1 is enabled and committed, it programs AFBC or canvas state, many VD1/VD2 IF0 and scaler registers, enables VD1, and clears the commit flag. Finally, if vblank is not disabled, it calls `drm_crtc_handle_vblank()` and sends any stored event.

## State and persistence
The CRTC itself stores only event and vblank control flags; most display state persists in `priv->viu` fields prepared by plane/overlay code and consumed in IRQ context. Hardware register state persists in VPP, VIU, AFBC, and canvas blocks. `vsync_forced` keeps vblank enabled while AFBC setup needs IRQ-driven updates.

## Dependencies and integration points
Depends on DRM atomic/vblank helpers, Meson canvas API, Meson VIU/VPP/VENC/RDMA/AFBCD helpers, and `meson_drm` private state. The top-level `meson_irq()` calls `meson_crtc_irq()` after clearing VENC interrupt flags.

## Risks
The IRQ handler writes a large cached register set and assumes `priv->viu` was prepared coherently by atomic plane paths. Event delivery depends on balanced vblank get/put and lock ordering. G12A uses a different VIU offset and blending setup, so SoC detection is critical. AFBC paths force vsync and reset external AFBCD ops, making compressed-buffer transitions sensitive.

## Test signals
Signals include vblank interrupts/events, page flip completion, OSD1/VD1 visibility, AFBC and linear transitions, GXM/G12A behavior, scaler output, canvas IDs, vblank disable/enable behavior, suspend/resume modesets, and absence of missed page-flip events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.h

## Purpose
Declares the Meson CRTC creation and IRQ entry points for the DRM driver.

## Important APIs, types, and functions
- `int meson_crtc_create(struct meson_drm *priv);`
- `void meson_crtc_irq(struct meson_drm *priv);`

## Control flow
No complex control flow exists in the header. It includes `meson_drv.h` so callers share the `struct meson_drm` definition.

## State and persistence
No state is stored. The declared functions create the CRTC object and consume persistent `meson_drm` private state in IRQ context.

## Dependencies and integration points
Used by `meson_drv.c` for CRTC creation and top-level IRQ dispatch. It is intentionally narrow, keeping `struct meson_crtc` private to the implementation.

## Risks
Signature changes affect top-level driver build. The header exposes no way to query CRTC internals, so all cross-file state must flow through `struct meson_drm`.

## Test signals
Build coverage catches declaration drift. Runtime validation is CRTC creation and IRQ handling through `meson_drv.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.c

## Purpose
Implements the top-level Amlogic Meson DRM platform driver. It allocates and registers the DRM device, maps VPU/HHI registers, initializes canvas, VPU/VENC/VPP/VIU/AFBCD blocks, binds component HDMI devices, creates encoders/planes/CRTC, handles vblank IRQ dispatch, and manages suspend/resume/shutdown.

## Important APIs, types, and functions
- `meson_drv_bind_master()` is the main device bring-up routine.
- `meson_drv_probe()` decides between direct bind and component-master binding based on OF graph endpoints.
- `meson_irq()` clears VENC interrupt flags and delegates to `meson_crtc_irq()`.
- `meson_dumb_create()` enforces 64-byte pitch alignment and page-aligned dumb buffer size.
- `meson_vpu_init()` programs VPU read/write arbitration.

## Control flow
Probe scans endpoint remote ports. If endpoints exist and some match DesignWare HDMI component nodes, it registers as component master; if endpoints exist without components, it binds directly; no endpoints means no-op. Master bind verifies at least one connector endpoint, gets SoC match data, allocates DRM and private state, maps VPU and HHI registers, initializes HHI regmap, obtains Meson canvas and four canvas IDs, initializes vblank, applies SoC-specific HDMI PHY limits, removes conflicting firmware framebuffers, initializes mode config, initializes hardware blocks, optional AFBCD, CVBS encoder, external components, HDMI encoder, optional G12A DSI encoder, primary/overlay planes, CRTC, IRQ, mode config reset, polling, DRM registration, and client setup.

Unbind unregisters DRM, stops polling, performs atomic shutdown, frees IRQ, drops DRM reference, removes encoders, unbinds components, exits AFBCD, and frees canvases. Suspend uses DRM mode-config helper suspend; resume reinitializes VPU/VENC/VPP/VIU/AFBCD before helper resume. Shutdown stops polling and performs atomic shutdown.

## State and persistence
Persistent state is `struct meson_drm` in `drm->dev_private`, containing MMIO/regmap resources, canvas IDs, planes, CRTC, encoders, SoC compatibility, limits, and cached VIU/VENC/RDMA/AFBCD state. Hardware state is reset and reinitialized on bind/resume and shut down through DRM atomic helpers.

## Dependencies and integration points
Depends on DRM core, GEM DMA/fbdev helpers, component framework, OF graph, aperture conflict removal, Meson canvas, sys_soc matching, Meson encoder/plane/overlay/CRTC/VIU/VPP/VENC/VCLK/RDMA/AFBCD modules, and DesignWare HDMI/DSI component nodes.

## Risks
Error unwinding is long and includes calls to encoder remove/component unbind after partial initialization; changes must preserve ordering. `meson_drv_unbind()` frees canvas IDs before unregistering DRM, so consumers must be inactive by then. Connector endpoint discovery controls whether the driver binds at all. SoC-specific limits are applied by `soc_device_match()` and may silently be absent on unknown package IDs.

## Test signals
Signals include probe logs for queued outputs, DRM device registration, fbdev/client setup, vblank IRQ operation, dumb buffer pitch alignment, CVBS/HDMI/DSI output creation, component bind failures, suspend/resume display recovery, shutdown blanking, and builds across GXBB/GXL/GXM/G12A match data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.h

## Purpose
Defines the shared private state and SoC compatibility data for the Amlogic Meson DRM driver.

## Important APIs, types, and functions
- `enum vpu_compatible` distinguishes GXBB, GXL, GXM, and G12A display hardware.
- Encoder indices identify CVBS, HDMI, DSI, and the array limit.
- `struct meson_drm_match_data` carries compatibility and AFBCD ops.
- `struct meson_drm_soc_limits` carries SoC/package limits such as maximum HDMI PHY frequency.
- `struct meson_drm` is the central private object for registers, canvas IDs, DRM objects, encoders, limits, VIU/VENC/RDMA/AFBCD cached state, and helper data.
- `meson_vpu_is_compatible()` is the inline compatibility test.

## Control flow
The only executable code is the inline compatibility comparison. The rest is shared data shape.

## State and persistence
`struct meson_drm` persists for the DRM device lifetime and is the primary state bus between planes, CRTC, encoders, VENC/VPP/VIU/RDMA, and AFBCD helpers. It stores both resource handles and cached register values that are committed later, often in vblank IRQ context.

## Dependencies and integration points
Includes Linux device/OF/regmap types and forward declares DRM and AFBCD structures. Nearly every Meson DRM source includes this header, making it the main internal ABI.

## Risks
The private state is large and tightly coupled; fields such as `viu` cached registers must remain consistent with writer and IRQ consumer code. Adding SoC families requires updating compatibility checks and match data. Because many modules write shared fields, concurrency and atomic commit ordering matter.

## Test signals
Build coverage across all Meson DRM objects catches struct/signature mismatches. Runtime signals include correct SoC-specific paths, AFBCD operations, encoder indexing, VIU/VENC cached state commits, and HDMI PHY limit use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_drv.h -->
