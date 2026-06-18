<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.h

## Purpose
Private register map and bitfield header for the NXP/Freescale XCVR digital audio block. It describes the SPDIF, ARC, and eARC transceiver register layout, FIFO sizing, IRQ bits, channel-status encodings, PHY access registers, and PLL/GP-PLL controls used by the corresponding DAI driver.

## APIs, Types, and Functions
This header exports macros only. Important groups are `FSL_XCVR_MODE_*`, FIFO constants such as `FSL_XCVR_FIFO_SIZE`, top-level register offsets from `FSL_XCVR_VERSION` through `FSL_XCVR_DEBUG_REG_1`, RX/TX datapath registers, channel status registers, `FSL_XCVR_IRQ_*` masks, PHY AI register controls, PLL register offsets, PHY control bits, IEC60958 channel-status sample-rate and channel-count encodings, and GP PLL numerator/denominator/divider masks.

## Control Flow, State, and Persistence
There is no executable control flow or persistent object state. Runtime state is held by the C driver that includes this header, while this file defines the fixed hardware contract: which bits reset command/data paths, disable DMA directions, select SPDIF/ARC/eARC mode, program watermarks, acknowledge channel/user-data updates, control PLL/PHY power, and encode channel status.

## Dependencies and Integration
The file assumes Linux bit helpers such as `BIT()` and `GENMASK()` are available before or through including contexts. It integrates with the XCVR platform driver, ALSA DAI setup, DMA configuration, interrupt handling, eARC firmware/PHY management, and IEC channel-status programming.

## Risks and Test Signals
Risks are register drift against SoC reference manuals, fragile ternary helper macros where `t` selects TX versus RX bits, and incorrect channel-status constants causing receiver compatibility problems. Test signals are clean compile with the XCVR driver, SPDIF/ARC/eARC playback and capture, FIFO watermark DMA behavior, IRQ status/clear handling, PLL lock and PHY enable sequencing, and channel-status sample-rate validation on external sinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audio-rpmsg.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audio-rpmsg.c

## Purpose
RPMsg bus glue for i.MX audio offload channels. It binds remote-processor audio and micfil RPMsg endpoints, creates the platform PCM component device, creates the `imx-audio-rpmsg` machine-card platform device, and routes remote period notifications or command responses to the PCM RPMsg state.

## APIs, Types, and Functions
`struct imx_audio_rpmsg` stores the spawned PCM and card platform devices. `imx_audio_rpmsg_cb()` handles incoming `struct rpmsg_r_msg` packets. `imx_audio_rpmsg_probe()` registers platform devices named after the RPMsg channel and `imx-audio-rpmsg`; `imx_audio_rpmsg_remove()` unregisters them. The RPMsg ID table matches `rpmsg-audio-channel` and `rpmsg-micfil-channel`.

## Control Flow, State, and Persistence
Probe allocates private state on the RPMsg device, then spawns child platform devices. Incoming type-C notifications update TX/RX period-done message tails under the per-stream spinlock and invoke the stored DMA callback. Type-B responses copy the message into `info->r_msg` and complete `cmd_complete`, unblocking synchronous sends in `imx-pcm-rpmsg.c`. State persists in the child platform device's `struct rpmsg_info`, not in this file.

## Dependencies and Integration
Depends on `linux/rpmsg.h`, platform-device registration, and `imx-pcm-rpmsg.h` protocol structures. It integrates tightly with `imx-pcm-rpmsg.c` via `platform_get_drvdata(rpmsg_pdev)` and with `imx-rpmsg.c` through the card platform device data containing the channel name.

## Risks and Test Signals
Risks include callbacks arriving before the child platform driver has initialized `rpmsg_info`, unchecked callback function pointers, modulo by `num_period` before a stream is fully configured, and partial cleanup if the first child device succeeds and the second registration fails. Test signals are endpoint probe for both channel names, platform child creation, type-B response completion, type-C period elapsed callbacks for playback/capture, and remove without dangling platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audio-rpmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmix.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmix.c

## Purpose
i.MX AUDMIX machine driver that creates DPCM frontend and backend DAI links around the AUDMIX hardware and connected SAI ports. It exposes playback/capture frontends and internal AUDMIX backends with generated DAPM routes.

## APIs, Types, and Functions
`struct imx_audmix` owns the card, AUDMIX device pointers, DAI links, codec-conf prefixes, and routes. Frontend ops are `imx_audmix_fe_startup()` and `imx_audmix_fe_hw_params()`, constraining channels/formats and programming SAI format/sysclk/TDM slots. Backend ops use `imx_audmix_be_hw_params()` to configure AUDMIX DAI format for playback. `imx_audmix_probe()` builds all links from the parent AUDMIX node's `dais` phandles.

## Control Flow, State, and Persistence
Probe finds the parent AUDMIX platform device, requires exactly `FSL_AUDMIX_MAX_DAIS` phandles, then creates one extra output/capture link and doubles that set for FE and BE links. Each FE has CPU/platform components pointing at SAI nodes and a dummy codec; each BE points at the AUDMIX CPU DAI and is marked `no_pcm`. Playback links are marked playback-only, the last is capture-only, and DAPM routes connect SAI playback/capture widgets through AUDMIX streams. Runtime state is per-card devm allocation and ASoC DPCM link state.

## Dependencies and Integration
Depends on ASoC DPCM, OF phandles, `fsl_sai.h`, `fsl_audmix.h`, dummy codec components, and `snd_soc_pm_ops`. It integrates with the AUDMIX platform device, SAI CPU DAIs, and generic DMA-engine PCM platforms.

## Risks and Test Signals
Risks include hard-coded assumptions about exactly two input DAIs plus one output link, static name arrays indexed by generated link count, TDM mask `BIT(channels) - 1` for arbitrary channel counts, and leaked OF node references on some error paths. Test signals are card registration from an AUDMIX parent, FE/BE DPCM link creation, 1-8 channel playback/capture startup constraints, DSP_A/TDM slot programming, and DAPM route visibility for each generated SAI path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.c

## Purpose
Global AUDMUX routing driver for i.MX21/i.MX31-style SSI audio mux hardware. It maps the AUDMUX registers, exposes exported configuration helpers for board drivers, restores cached port settings, and optionally provides debugfs inspection.

## APIs, Types, and Functions
Exports `imx_audmux_v1_configure_port()` and `imx_audmux_v2_configure_port()`. Internal helpers include `audmux_read_file()` and debugfs setup/removal when `CONFIG_DEBUG_FS` is enabled. Probe identifies `fsl,imx21-audmux` or `fsl,imx31-audmux`, maps IO, gets the clock, initializes `regcache`, and applies cached values.

## Control Flow, State, and Persistence
The driver keeps global static state: `audmux_clk`, `audmux_base`, `regcache`, `reg_max`, and `audmux_type`. Configuration helpers validate the hardware generation, enable the clock, write V1 PCR or V2 PTCR/PDCR registers, cache values, then disable the clock. Probe replay writes existing cached values, so routing survives driver rebind as long as the module-global cache remains allocated. Debugfs reads enable the clock, snapshot PTCR/PDCR, and format clock/frame/data-source state.

## Dependencies and Integration
Depends on platform/OF matching, MMIO, clocks, debugfs, and exported symbols consumed by machine drivers such as `imx-es8328.c` and `imx-sgtl5000.c`. `imx-audmux.h` defines the port constants and bitfield builders.

## Risks and Test Signals
Risks include single global state preventing multiple AUDMUX instances, no locking around exported configuration writes, debugfs interpretation limited to MX31 port names, and stale cached routes after suspend/reset outside this driver. Test signals are successful probe for both compatible strings, route setup from board drivers, debugfs register dumps, clock enable/disable balance, and functional SSI audio after v1/v2 port configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.h

## Purpose
Public AUDMUX interface for i.MX machine drivers. It exposes port constants, bitfield macros, and configuration function prototypes.

## APIs, Types, and Functions
Defines MX31 port numbers such as `MX31_AUDMUX_PORT1_SSI0` through SSI pins port 7, V2 PTCR/PDCR bit builders for sync, clock/frame direction and selection, RX data selection, and prototypes for `imx_audmux_v1_configure_port()` and `imx_audmux_v2_configure_port()`.

## Control Flow, State, and Persistence
No runtime state. The header encodes how callers build the PCR/PTCR/PDCR values persisted by `imx-audmux.c` into hardware registers and its static cache.

## Dependencies and Integration
Used by SSI-based board drivers including ES8328 and SGTL5000 machine drivers. The prototypes are backed by exported symbols in `imx-audmux.c`.

## Risks and Test Signals
Risks are off-by-one port handling in callers because hardware manuals number ports from 1 while the API uses zero-based indexes, and incorrect bitfield composition causing swapped clocks or data sources. Test signals are build coverage of users and working audio after configuring internal and external mux ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-card.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-card.c

## Purpose
Generic Freescale/NXP i.MX ASoC machine driver for device-tree-described cards. It supports plain CPU-codec links, ASRC DPCM front/back ends, TDM and DSD handling, and codec-specific rate/channel/MCLK policy for AKM codecs, CS42888, and WM8524.

## APIs, Types, and Functions
Key types are `enum codec_type`, `struct imx_akcodec_fs_mul`, `struct imx_akcodec_tdm_fs_mul`, `struct imx_card_plat_data`, `struct dai_link_data`, and `struct imx_card_data`. Important functions are `format_is_dsd()`, `format_is_tdm()`, `codec_is_akcodec()`, `akcodec_get_mclk_rate()`, `imx_aif_hw_params()`, `ak5558_hw_rule_rate()`, `imx_aif_startup()`, `imx_aif_shutdown()`, `be_hw_params_fixup()`, `imx_card_parse_of()`, and `imx_card_probe()`.

## Control Flow, State, and Persistence
Probe allocates card/private/platform data, parses the `model`, optional `audio-routing`, and one child node per DAI link. Each link gets CPU/platform components, optional codec components or dummy codec, link direction flags, DAI format, TDM slot count/width, and ASRC-specific dynamic/no-pcm behavior. Runtime startup applies channel/rate constraints from codec type and may add an AK5558 rate rule. `hw_params()` normalizes non-TDM streams to I2S or PDM for DSD, programs CPU and codec DAI formats and TDM slots, computes MCLK, sets CPU sysclk output and codec sysclk input, and shutdown clears sysclks. ASRC backends use fixed rate/format from the ASRC node.

## Dependencies and Integration
Depends on ASoC core, `simple-card-utils`, OF graph direction parsing, `fsl_sai.h`, ALSA PCM constraints, and codec DAI names for type detection. Integrates with SAI CPU DAIs, ASRC front/back end naming conventions (`HiFi-ASRC-FE`/`HiFi-ASRC-BE`), AKM/CS/WM codecs, and card-level DAPM routes.

## Risks and Test Signals
Risks include global mutation of `ak4497_fs_mul` based on one link's `fsl,mclk-equal-bclk`, static constraint-list objects shared across startups, reliance on codec DAI name strings, using the last codec DAI after a loop for sysclk, and DAPM route assumptions when the number of codecs or links varies. Test signals are card registration for single-link and three-link ASRC cards, I2S/TDM/DSD playback, codec-specific rate/channel constraint enforcement, MCLK frequency measurements, ASRC fixed output format, and suspend/resume through `snd_soc_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-es8328.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-es8328.c

## Purpose
Board/machine driver for i.MX systems using an ES8328 codec over an SSI interface with AUDMUX routing and optional headset GPIO detection.

## APIs, Types, and Functions
`struct imx_es8328_data` stores the card, single DAI link, component name buffers, and optional jack GPIO. `imx_es8328_dai_init()` creates a headset jack and attaches GPIO detection. `imx_es8328_probe()` validates mux ports, configures AUDMUX, resolves SSI and codec phandles, builds the DAI link, parses card name/routing, and registers the card.

## Control Flow, State, and Persistence
Probe reads `mux-int-port` and `mux-ext-port`, validates 1..7 values, converts them to zero-based AUDMUX API indexes, programs internal and external ports, finds `ssi-controller` and `audio-codec`, and registers an I2S codec-provider link with CPU/platform on SSI and codec DAI `es8328-hifi-analog`. Jack state is stored in static `headset_jack` structures and the optional GPIO descriptor in card private data.

## Dependencies and Integration
Depends on `imx-audmux.h`, OF phandles, GPIO descriptors, ASoC jack/DAPM APIs, and the ES8328 codec driver. It integrates with device-tree `fsl,imx-audio-es8328`, `model`, and `audio-routing`.

## Risks and Test Signals
Risks include static jack objects shared across potential instances, hard-coded codec DAI name, AUDMUX configuration before confirming all phandles are present, and no runtime PM ops beyond component defaults. Test signals are probe on a valid DT, correct AUDMUX register programming, card routing with Headphone/Mic/Speaker/audio-amp widgets, jack GPIO events, and I2S playback/capture through ES8328.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-es8328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-hdmi.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-hdmi.c

## Purpose
i.MX HDMI audio machine driver connecting SAI/eARC-style CPU DAIs to the generic HDMI codec. It configures DAI format, TDM slots, and CPU sysclk IDs for HDMI playback and capture-capable links.

## APIs, Types, and Functions
`struct cpu_priv` stores per-direction sysclk IDs and slot width; `struct imx_hdmi_data` stores the card, DAI link, CPU private data, and jack state. Main helpers include HDMI startup/hw_params/init routines, jack status callback wiring, and the platform probe that builds a single card from DT phandles.

## Control Flow, State, and Persistence
Probe allocates card data and link components, resolves CPU and HDMI codec endpoints, parses the card name, initializes HDMI DAPM/jack support, and registers the card. Runtime `hw_params()` derives slots/channels and slot width, programs the CPU DAI format and TDM slots, and sets CPU sysclk using direction-specific IDs. Link and jack state persist in devm card data.

## Dependencies and Integration
Depends on `sound/hdmi-codec.h`, ASoC jack and PCM parameter APIs, `fsl_sai.h`, OF platform helpers, and `snd_soc_pm_ops`. Integrates with the generic HDMI codec and i.MX SAI/HDMI audio DT bindings.

## Risks and Test Signals
Risks include DT-dependent clock ID selection, channel/slot assumptions for HDMI multichannel audio, jack callback behavior depending on the HDMI codec implementation, and possible mismatch between playback-only hardware and bidirectional link configuration. Test signals are card probe, ELD/jack state updates, HDMI sink detection, 2/8-channel playback, correct BCLK/LRCLK with configured slot width, and suspend/resume audio recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-dma.c

## Purpose
Small helper that registers the generic DMA-engine PCM component for i.MX audio platform devices.

## APIs, Types, and Functions
Exports `imx_pcm_dma_init(struct platform_device *pdev)` and `imx_pcm_dma_exit(struct platform_device *pdev)`. The init path builds `snd_dmaengine_pcm_config` flags and calls `devm_snd_dmaengine_pcm_register()`.

## Control Flow, State, and Persistence
No private runtime state is created here. The DMA-engine PCM core owns PCM allocation and DMA channel binding after registration. Exit is intentionally empty because devm cleanup handles component lifetime.

## Dependencies and Integration
Depends on `sound/dmaengine_pcm.h`, ASoC component registration, and `imx-pcm.h`. Called by i.MX SSI/SAI-style CPU DAI drivers that choose DMA mode instead of FIQ mode.

## Risks and Test Signals
Risks are mostly integration-level: incorrect DMA filter/DT channel data in the CPU DAI driver or a mismatch between component registration flags and hardware capabilities. Test signals are successful component registration, DMA channel allocation, mmap/read-write PCM operation, and clean device detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-fiq.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-fiq.c

## Purpose
Legacy i.MX SSI PCM backend using ARM FIQ code instead of DMA-engine PCM. It allocates fixed write-combined buffers, installs an SSI FIQ handler, tracks hardware position from FIQ registers, and reports periods through an hrtimer.

## APIs, Types, and Functions
`struct imx_pcm_runtime_data` stores period sizing, current offset, hrtimer, substream, and playback/capture atomics. Main component callbacks are `snd_imx_open()`, `snd_imx_close()`, `snd_imx_pcm_hw_params()`, `snd_imx_pcm_prepare()`, `snd_imx_pcm_trigger()`, `snd_imx_pcm_pointer()`, `snd_imx_pcm_new()`, and `snd_imx_pcm_free()`. Exports `imx_pcm_fiq_init()` and `imx_pcm_fiq_exit()`.

## Control Flow, State, and Persistence
Open allocates runtime data and initializes the hrtimer. `hw_params()` computes period bytes/count and timer polling interval. Prepare writes the ring-buffer end into ARM FIQ registers r8/r9. Trigger START sets active atomics, starts the hrtimer, and enables the FIQ; STOP clears atomics and disables FIQ when both directions are inactive. The hrtimer snapshots r8/r9 low bits into `offset` and calls `snd_pcm_period_elapsed()`. PCM creation sets fixed buffers and exposes their virtual addresses through global FIQ symbols.

## Dependencies and Integration
Depends on ARM FIQ APIs, `imx-ssi.h` FIQ symbols, `imx-pcm.h`, ALSA PCM component callbacks, and platform data containing SSI base/IRQ and DMA params. It integrates with SSI drivers that select FIQ mode.

## Risks and Test Signals
Risks include global FIQ ownership (`claim_fiq`) preventing coexistence, register-based pointer width limitations, timer period arithmetic overflow/rounding, no cleanup in `imx_pcm_fiq_exit()`, and architecture specificity. Test signals are successful FIQ claim, fixed buffer setup, playback/capture pointer movement, period elapsed cadence, start/stop without stuck FIQ, and underrun-free SSI audio on supported ARM i.MX systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-fiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-rpmsg.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-rpmsg.c

## Purpose
PCM component for i.MX remote-processor audio over RPMsg. It translates ALSA PCM operations into SRTM/RPMsg audio commands, manages fixed shared buffers, period notifications, low-power audio pointer updates, workqueue serialization, and suspend/resume commands.

## APIs, Types, and Functions
Important functions include `imx_rpmsg_pcm_send_message()`, `imx_rpmsg_insert_workqueue()`, `imx_rpmsg_pcm_open()`, `imx_rpmsg_pcm_close()`, `imx_rpmsg_pcm_hw_params()`, `imx_rpmsg_prepare_and_submit()`, `imx_rpmsg_async_issue_pending()`, `imx_rpmsg_restart()`, `imx_rpmsg_pause()`, `imx_rpmsg_terminate_all()`, `imx_rpmsg_pcm_trigger()`, `imx_rpmsg_pcm_ack()`, `imx_rpmsg_pcm_pointer()`, `imx_rpmsg_pcm_new()`, `imx_rpmsg_pcm_work()`, probe/remove, and PM callbacks. It registers `imx_rpmsg_soc_component` as `IMX_PCM_DRV_NAME`.

## Control Flow, State, and Persistence
Probe allocates `struct rpmsg_info`, finds the parent `rpmsg_device`, creates an ordered high-priority workqueue, initializes message headers, locks, and completion, then registers the component. Open sends TX/RX open, resets period counters and pointer offsets, derives buffer limits from the CPU DAI's `struct fsl_rpmsg`, sets runtime constraints, and initializes a per-stream timer. `hw_params()` maps ALSA formats/channels/rates into protocol fields. START queues buffer setup and start; pause/resume/stop queue corresponding commands. In low-power audio mode, `prepare()` sets `ignore_suspend` and `force_lpa`; `ack()` sends or delays type-C period pointer notifications based on available data. `send_message()` serializes RPMsg sends, waits for type-B replies for command messages, and mirrors responses into `info->msg`.

## Dependencies and Integration
Depends on `imx-pcm-rpmsg.h`, `fsl_rpmsg.h`, RPMsg core, DMA mask/fixed-buffer APIs, ASoC component callbacks, PM QoS, timers, workqueues, completions, mutexes, and spinlocks. It is paired with `imx-audio-rpmsg.c` for inbound callbacks and `imx-rpmsg.c` for the card/DAI link.

## Risks and Test Signals
Risks include the ring-workqueue full check using equal indexes with write index initialized to 1, silent ignored return from `send_message()` in `hw_params()`, response command indexing assumptions, timer/work races during close and terminate, low-power `ignore_suspend` side effects, physical address truncation in protocol fields on wider DMA addresses, and callback invocation before setup. Test signals are open/hw_params/start/stop command exchange, timeout handling when the M core is absent, fixed buffer address visibility to firmware, period notification accuracy, low-power playback across A-core suspend, workqueue drop counters staying zero, and runtime/system PM command traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-rpmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-rpmsg.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-rpmsg.h

## Purpose
Protocol and shared-state header for i.MX audio RPMsg PCM. It documents the SRTM audio packet format and defines command IDs, message types, response codes, format/channel codes, packet structures, workqueue nodes, timers, and the central `rpmsg_info` state object.

## APIs, Types, and Functions
Defines `RPMSG_TIMEOUT`, TX/RX command macros from `TX_OPEN` through `RX_POINTER`, message counts, `MSG_TYPE_A/B/C`, response constants, RPMsg audio format/channel codes, category/version constants, stream aliases `TX`/`RX`, packed structs `rpmsg_head`, `param_s`, `param_r`, `rpmsg_s_msg`, `rpmsg_r_msg`, `rpmsg_msg`, plus `work_of_rpmsg`, `stream_timer`, `dma_callback`, and `struct rpmsg_info`.

## Control Flow, State, and Persistence
The header has no executable logic, but `struct rpmsg_info` is the persistent state shared between RPMsg bus callbacks and PCM operations: the parent endpoint, command completion, PM QoS request, response scratch message, per-command message array, notification cache, ordered workqueue ring, drop counters, period counts, period callbacks, send function pointer, per-stream spinlocks, workqueue spinlock, send mutex, and per-stream timers.

## Dependencies and Integration
Depends on PM QoS, interrupts/work structs, and ALSA DMA-engine headers. Included by both `imx-audio-rpmsg.c` and `imx-pcm-rpmsg.c`, and indirectly defines the ABI expected by the remote M-core firmware.

## Risks and Test Signals
Risks include packed little-endian protocol fields without explicit endian conversion, 32-bit buffer address fields limiting DMA addressability, comments with stale names/typos, command-number ABI drift with firmware, and concurrency complexity concentrated in a public struct. Test signals are compile-time struct layout compatibility, firmware command/response interoperability, correct format/channel translation, and bidirectional period notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-rpmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm.h

## Purpose
Shared private declarations for i.MX PCM backends. It defines buffer sizing and the small interface used by SSI/SAI drivers to register either DMA-engine or FIQ PCM support.

## APIs, Types, and Functions
Defines default DMA buffer sizes such as `IMX_SSI_DMABUF_SIZE`/`IMX_DEFAULT_DMABUF_SIZE`, `struct imx_pcm_fiq_params` for FIQ initialization, and prototypes for `imx_pcm_dma_init()`, `imx_pcm_dma_exit()`, `imx_pcm_fiq_init()`, and `imx_pcm_fiq_exit()`.

## Control Flow, State, and Persistence
No control flow lives here. The FIQ params structure carries SSI base, IRQ, and DMA parameter pointers from a CPU DAI driver into the FIQ backend, while DMA-mode state is owned by the DMA-engine PCM core.

## Dependencies and Integration
Used by `imx-pcm-dma.c`, `imx-pcm-fiq.c`, and i.MX SSI/SAI CPU DAI drivers. Depends on platform devices and DMA slave config types from ALSA/DMA headers through including contexts.

## Risks and Test Signals
Risks are ABI drift between backend prototypes and CPU DAI callers, and buffer-size constants being too small or too large for particular latency/use cases. Test signals are successful builds of DMA and FIQ backends, component registration from CPU drivers, and ALSA buffer allocation matching expected size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-rpmsg.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-rpmsg.c

## Purpose
ASoC machine driver for i.MX RPMsg audio cards. It creates a simple one-link card using the RPMsg CPU DAI/platform component and a dummy codec, and configures format switching for PCM versus DSD.

## APIs, Types, and Functions
`struct imx_rpmsg` contains the single DAI link, card, sysclk, and low-power-audio flag. `imx_rpmsg_hw_params()` detects DSD formats, switches the DAI format to PDM for DSD, and calls `snd_soc_dai_set_fmt()` on CPU and codec DAIs. The probe path parses platform data from the RPMsg-created card device and registers the card with DAPM widgets for headphone, speaker, and microphones.

## Control Flow, State, and Persistence
The platform device is created by `imx-audio-rpmsg.c` with channel-name platform data. Probe builds a card whose CPU and platform components reference the RPMsg channel, with a dummy codec and DAPM widgets. Runtime hw_params adapts the link format and ignores `-ENOTSUPP` from DAI format operations. Card state persists in devm allocations and is subject to normal ASoC PM.

## Dependencies and Integration
Depends on ASoC card/link APIs, OF/reserved-memory headers, jack/control/DAPM headers, and `imx-pcm-rpmsg.h`. Integrates with the platform PCM component named after the RPMsg channel and remote firmware that implements the audio endpoint.

## Risks and Test Signals
Risks include dummy codec limitations, DSD format switching relying on CPU DAI support for PDM, sparse DT/property parsing compared with hardware-specific cards, and low-power-audio state coordination with `imx-pcm-rpmsg.c`. Test signals are card registration after RPMsg endpoint probe, PCM and DSD hw_params calls, CPU DAI format changes, DAPM widget visibility, and playback/capture over the remote endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-rpmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-sgtl5000.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-sgtl5000.c

## Purpose
Machine driver for i.MX boards using an SGTL5000 codec over an SSI interface. It configures AUDMUX, codec clocking, a single I2S link, DAPM widgets/routes, and card registration.

## APIs, Types, and Functions
`struct imx_sgtl5000_data` stores the card, DAI link, codec clock, and clock frequency. `imx_sgtl5000_dai_init()` programs codec sysclk using the codec clock rate. `imx_sgtl5000_probe()` reads mux ports, configures AUDMUX, resolves SSI/codec devices, gets the codec clock, builds link components, parses card metadata, and registers the card. `imx_sgtl5000_remove()` releases the codec clock.

## Control Flow, State, and Persistence
Probe converts one-based DT mux port numbers to zero-based AUDMUX indexes and programs symmetric internal/external routing. It then defers until SSI and I2C codec devices exist, obtains the codec clock, sets the link to I2S normal-bitclock/frame with codec as clock provider, and stores private data in the card. Runtime init passes the clock frequency to SGTL5000. Persistent state is card data plus the acquired `clk`.

## Dependencies and Integration
Depends on `imx-audmux.h`, OF phandles, I2C device lookup, clocks, ASoC DAPM, and the SGTL5000 codec DAI named `sgtl5000`. Integrates with `fsl,imx-audio-sgtl5000`, `model`, `audio-routing`, and SSI CPU DAIs.

## Risks and Test Signals
Risks include no explicit mux-port upper-bound validation here, manual `clk_get`/`clk_put` instead of devm clock management, hard-coded codec DAI name, and static clock-frequency use if the codec clock changes. Test signals are probe defer until codec/SSI availability, AUDMUX routing, sysclk programming on DAI init, successful playback/capture, and balanced clock put on remove/error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-sgtl5000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-ssi.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-ssi.h

## Purpose
Private SSI header for i.MX sound drivers. It defines SSI register offsets/bitfields, buffer sizing, driver names, and external FIQ symbols used by the legacy FIQ PCM path.

## APIs, Types, and Functions
Defines `DRV_NAME`, SSI register offsets such as STX/RX, SCR, SIER, STCCR/SRCCR, SFCSR, SOR, bit masks for enable, interrupt, FIFO, clock, network and AC97 behavior, and extern symbols for FIQ handler boundaries and FIQ buffer/base variables.

## Control Flow, State, and Persistence
No executable logic is in the header. The register constants drive CPU DAI setup and FIQ assembly behavior; extern globals persist the DMA buffer addresses and SSI base used by the installed FIQ handler.

## Dependencies and Integration
Included by `imx-pcm-fiq.c` and SSI CPU DAI implementations. It is tied to ARM FIQ support, i.MX SSI hardware, and ALSA PCM buffer configuration.

## Risks and Test Signals
Risks include register definition drift across SSI variants, global FIQ symbol coupling, and bitfield misuse in callers. Test signals are build coverage with SSI and FIQ enabled, correct register programming under playback/capture, and FIQ pointer updates using the exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/imx-ssi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-i2s.c

## Purpose
ASoC CPU DAI driver for NXP LPC32xx/LPC3xxx I2S controllers. It configures I2S word size, mono/stereo mode, clock dividers, DMA thresholds, stream start/stop, and registers the paired DMA-engine PCM component.

## APIs, Types, and Functions
Important functions are `__lpc3xxx_find_clkdiv()`, `lpc3xxx_i2s_startup()`, `lpc3xxx_i2s_shutdown()`, `lpc3xxx_i2s_set_dai_sysclk()`, `lpc3xxx_i2s_set_dai_fmt()`, `lpc3xxx_i2s_hw_params()`, `lpc3xxx_i2s_trigger()`, `lpc3xxx_i2s_dai_probe()`, and `lpc32xx_i2s_probe()`. The driver exposes one DAI with 1-2 channels, rates 16 kHz through 96 kHz, and S8/S16_LE/S32_LE formats.

## Control Flow, State, and Persistence
Probe maps registers through regmap, gets the clock, records base clock rate, initializes mutex and DMA addresses, registers the DAI component, and calls `lpc3xxx_pcm_register()`. Startup serializes access, enforces one playback and one capture stream, and enables the clock on the first stream. `hw_params()` computes word-width bits, mono flag, and best x/y clock divider, then writes DMA and rate/control registers per direction. Trigger clears or sets STOP/RESET bits. Shutdown resets the relevant direction and disables the clock when no streams remain.

## Dependencies and Integration
Depends on regmap-mmio, clocks, OF platform matching `nxp,lpc3220-i2s`, ALSA DAI APIs, and `lpc3xxx-pcm.c` for DMA-engine PCM registration. It integrates with DMA via `snd_soc_dai_init_dma_data()` and `lpc3xxx-i2s.h` register definitions.

## Risks and Test Signals
Risks include brute-force divider selection with approximate rates, `freq` needing to be set by machine driver sysclk before hw_params, symmetric rate/channel/sample-bit constraints limiting independent streams, and ignoring regmap write errors. Test signals are probe and PCM registration, correct BCLK/LRCLK across supported rates and widths, concurrent playback/capture clock refcounting, mono mode, trigger start/stop register changes, and DMA transfer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-i2s.h

## Purpose
Register and private-state header for the LPC3xxx/LPC32xx I2S driver.

## APIs, Types, and Functions
Defines register offsets for DAO/DAI, TX/RX FIFOs, status, DMA controls, IRQ, and TX/RX rate registers. Defines control bits for word width, half-period word select, mono, stop/reset, and DMA thresholds. `struct lpc3xxx_i2s_info` stores device, clock, regmap, DMA configs, base clock rate, requested frequency, stream-in-use mask, and mutex. Declares `lpc3xxx_pcm_register()`.

## Control Flow, State, and Persistence
The header has no control flow; it declares the state persisted by `lpc3xxx-i2s.c` across probe and active streams. DMA config fields are initialized at probe and consumed by DAI DMA setup.

## Dependencies and Integration
Used by `lpc3xxx-i2s.c` and `lpc3xxx-pcm.c`. Depends on regmap, clk, mutex, and `snd_dmaengine_dai_dma_data` types.

## Risks and Test Signals
Risks are stale register offsets/bit masks, especially DMA0/DMA1 naming for TX/RX depth fields, and state-field misuse without holding the mutex. Test signals are compile coverage and correct register writes visible during I2S playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-pcm.c

## Purpose
DMA-engine PCM registration helper for LPC3xxx/LPC32xx I2S.

## APIs, Types, and Functions
Defines `lpc3xxx_pcm_config` with `SNDRV_DMAENGINE_PCM_FLAG_COMPAT` and a compatibility DMA channel filter. Exports `lpc3xxx_pcm_register(struct platform_device *pdev)`, which calls `devm_snd_dmaengine_pcm_register()`.

## Control Flow, State, and Persistence
No private state is maintained. Registration delegates PCM device creation and DMA channel management to the generic DMA-engine PCM framework for the lifetime of the platform device.

## Dependencies and Integration
Depends on ASoC DMA-engine PCM APIs. Called from `lpc32xx_i2s_probe()` after DAI component registration.

## Risks and Test Signals
Risks are limited to DMA channel compatibility matching and platform DT/resource mismatches. Test signals are PCM device creation, DMA channel allocation for both directions, and successful audio transfer through the I2S DAI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.c

## Purpose
ASoC PCM/DMA backend for Freescale MPC5200 PSC audio using BestComm DMA tasks. It handles fixed ALSA buffers, BestComm buffer descriptor cycling, period notifications, PSC error accounting, and component registration for PSC-based I2S/AC97 drivers.

## APIs, Types, and Functions
Exports `mpc5200_audio_dma_create()` and `mpc5200_audio_dma_destroy()`. Important internals include `psc_dma_status_irq()`, `psc_dma_bcom_enqueue_next_buffer()`, `psc_dma_bcom_irq()`, `psc_dma_trigger()`, `psc_dma_open()`, `psc_dma_close()`, `psc_dma_pointer()`, and `psc_dma_new()`. It registers `mpc5200_audio_dma_component`.

## Control Flow, State, and Persistence
Create maps PSC registers, reads `cell-index`, allocates `struct psc_dma`, initializes locks, BestComm RX/TX tasks, resets PSC state, programs FIFO alarms, requests PSC status and BestComm IRQs, stores drvdata, and registers the component. START initializes period indexes, resets the relevant task, queues period buffers until the BestComm queue is full, enables DMA, and clears PSC errors. BestComm IRQs dequeue completed buffers, enqueue replacements, advance `period_current`, and call `snd_pcm_period_elapsed()` when active. STOP disables and resets the task. Pointer reports `period_current * period_bytes`.

## Dependencies and Integration
Depends on OF address/IRQ parsing, MPC52xx PSC register definitions, BestComm APIs, ALSA SoC component callbacks, and `mpc5200_dma.h`. Used by `mpc5200_psc_ac97.c` and `mpc5200_psc_i2s.c`.

## Risks and Test Signals
Risks include manual `kzalloc` lifetime combined with devm component registration, OR-combined `request_irq` return values obscuring which IRQ failed, queue depth assumptions versus ALSA period count, pointer granularity only at completed periods, and shared PSC status IRQ handling. Test signals are create/destroy without leaks, BestComm IRQ cadence, underrun/overrun counters, correct pointer movement, fixed buffer allocation, and playback/capture on MPC5200 PSC hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.h

## Purpose
Shared data structures and public functions for MPC5200 PSC audio DMA support.

## APIs, Types, and Functions
Defines `PSC_STREAM_NAME_LEN`, `struct psc_dma_stream`, `struct psc_dma`, helper `to_psc_dma_stream()`, and prototypes for `mpc5200_audio_dma_create()` and `mpc5200_audio_dma_destroy()`. Stream state includes runtime, active flag, BestComm task, IRQ, period indexes/counts/bytes, substream pointer, and AC97 slot bits. Device state includes PSC/FIFO register pointers, locks, SICR/sysclk/IMR/id/slots, playback/capture streams, and error counters.

## Control Flow, State, and Persistence
No executable logic beyond `to_psc_dma_stream()`. The structs define persistent PSC DMA state shared by the DMA backend and PSC protocol drivers.

## Dependencies and Integration
Depends on ALSA PCM, platform device, BestComm task, and MPC52xx PSC types through including contexts. Included by AC97, I2S, and DMA implementation files.

## Risks and Test Signals
Risks include shared mutable fields such as `slots` and `sicr` being manipulated by protocol drivers and DMA callbacks, and assumptions that substream stream IDs map directly to playback/capture members. Test signals are compile coverage across all MPC5200 PSC drivers and correct per-stream state updates during simultaneous playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_psc_ac97.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_psc_ac97.c

## Purpose
MPC5200 PSC AC97 CPU DAI driver. It configures the PSC into AC97 mode, exposes analog and IEC958 DAIs, implements AC97 bus read/write/reset operations, and uses the shared MPC5200 BestComm DMA backend.

## APIs, Types, and Functions
Global `psc_dma` stores the single AC97 PSC instance required by ALSA AC97 ops. Key functions are `psc_ac97_read()`, `psc_ac97_write()`, `psc_ac97_warm_reset()`, `psc_ac97_cold_reset()`, `psc_ac97_hw_analog_params()`, `psc_ac97_hw_digital_params()`, `psc_ac97_trigger()`, `psc_ac97_probe()`, `psc_ac97_of_probe()`, and `psc_ac97_of_remove()`. Two DAIs are registered: analog `mpc5200-psc-ac97.0` and SPDIF `mpc5200-psc-ac97.1`.

## Control Flow, State, and Persistence
OF probe creates DMA state, installs AC97 bus ops, registers DAIs, configures PSC SICR for AC97, and clears active slots. AC97 read/write serialize on `psc_dma->mutex`, poll PSC command/data-valid status bits, and access AC97 command/data registers. Analog hw_params computes AC97 slot enable bits based on stream direction and channel count. Trigger START/STOP updates `psc_dma->slots` and writes `ac97_slots`. Cold reset toggles board GPIO reset through `mpc5200_psc_ac97_gpio_reset()`, notifies PSC, enables RX/TX, waits, then warm-resets.

## Dependencies and Integration
Depends on ALSA AC97 bus ops, MPC52xx PSC register access, platform OF matching, `mpc5200_dma.h`, and board support for AC97 GPIO reset. Integrates with machine fabric such as `pcm030-audio-fabric.c` and WM9712-style AC97 codecs.

## Risks and Test Signals
Risks include the static single-instance `psc_dma`, polling timeouts on a wedged AC97 bus, no cleanup of DMA state if component registration fails after DMA creation, global AC97 ops conflicts, and slot-bit mistakes for multichannel analog playback. Test signals are AC97 codec reset/read/write, analog playback/capture slot activation, IEC958 playback, PSC AC97 SICR setup, and remove restoring AC97 ops and DMA resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_psc_ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_psc_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_psc_i2s.c

## Purpose
MPC5200 PSC I2S CPU DAI driver. It configures PSC serial interface control for I2S, validates DAI format/clocking, and uses the shared MPC5200 DMA backend for PCM data movement.

## APIs, Types, and Functions
Core callbacks include `psc_i2s_set_fmt()`, `psc_i2s_hw_params()`, `psc_i2s_trigger()`, `psc_i2s_probe()`, `psc_i2s_of_probe()`, and remove. The registered DAI supports playback/capture over PSC I2S with big-endian sample formats appropriate for the hardware FIFO.

## Control Flow, State, and Persistence
OF probe creates shared DMA state, registers the I2S component/DAI, then configures PSC registers for I2S mode. `set_fmt()` interprets master/slave and polarity settings into `psc_dma->sicr`. `hw_params()` programs frame size/slot behavior and FIFO/interrupt state based on sample format and channels. Trigger starts or stops PSC TX/RX in coordination with the DMA backend's trigger behavior. State persists in `struct psc_dma`.

## Dependencies and Integration
Depends on MPC52xx PSC register definitions, ASoC DAI APIs, OF platform matching for PSC I2S compatibles, and `mpc5200_dma.h`. It integrates with board machine drivers that connect the PSC DAI to codecs.

## Risks and Test Signals
Risks include strict format/clocking support, endian/sample-width assumptions, shared DMA state mutations without broader machine-driver validation, and cleanup ordering between component registration and DMA destruction. Test signals are DAI format negotiation, correct LRCLK/BCLK polarity and provider mode, playback/capture at supported rates/formats, PSC trigger register changes, and BestComm DMA period interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_psc_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/p1022_ds.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/p1022_ds.c

## Purpose
Freescale P1022DS board machine driver connecting SSI, DMA channels, and WM8776 codec playback/capture DAIs. It also programs board-level GUTS PMUX/DMUX registers for SSI signal and DMA routing.

## APIs, Types, and Functions
`struct machine_data` stores two DAI links, card, DAI format, clock directions/frequency, SSI ID, DMA controller/channel IDs, and platform names. Helpers include `guts_set_dmuxcr()`, `p1022_ds_machine_probe()`, `p1022_ds_startup()`, `p1022_ds_machine_remove()`, `p1022_ds_probe()`, `p1022_ds_remove()`, and module init/exit.

## Control Flow, State, and Persistence
Module init locates the `fsl,p1022-guts` physical address. Probe runs as a child of an SSI device, resolves `codec-handle`, allocates two DAI links for separate WM8776 playback and capture DAIs, parses `cell-index`, `fsl,mode`, codec clock frequency for slave modes, playback/capture DMA phandles, and registers the card. Card probe maps GUTS, enables SSI Tx/Rx pinmux and routes DMA channels to SSI. Startup sets codec DAI format and sysclk. Card remove clears PMUX/DMUX routing.

## Dependencies and Integration
Depends on PowerPC/Freescale GUTS registers, `fsl_dma.h`, `fsl_ssi.h`, `fsl_utils.h`, OF phandles, and the WM8776 codec DAI names. It integrates with SSI child platform devices and Freescale DMA channels named by DT properties.

## Risks and Test Signals
Risks include manual `kzalloc`/free with mixed devm component arrays, GUTS global state shared with other board functions, strict legacy `fsl,mode` string parsing, requiring nonzero `clk_frequency` even in master modes unless provided elsewhere, and cleanup gaps on late registration failure. Test signals are module init finding GUTS, card registration under SSI, PMUX/DMUX bit changes, codec sysclk/format setup for each mode, DMA phandle resolution, and playback/capture through WM8776.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/p1022_ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/p1022_rdk.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/p1022_rdk.c

## Purpose
Freescale/iVeia P1022 RDK machine driver connecting SSI and DMA channels to a WM8960 codec. It programs P1022 board GUTS routing and registers separate playback/capture links using the same codec DAI.

## APIs, Types, and Functions
It mirrors the DS driver's `struct machine_data` shape and GUTS DMUX helper, with board-specific `p1022_rdk_machine_probe()`, `p1022_rdk_startup()`, `p1022_rdk_machine_remove()`, `p1022_rdk_probe()`, `p1022_rdk_remove()`, and late init/exit. Codec DAI name is `wm8960-hifi`.

## Control Flow, State, and Persistence
Late init locates `fsl,p1022-guts` and registers the platform driver. Probe, under an SSI device, resolves `codec-handle`, allocates two DAI links, clones playback to capture, forces I2S slave mode with codec as clock provider, reads codec `clock-frequency`, resolves playback/capture DMA phandles, and registers the card. Card probe maps GUTS and programs PMUX/DMUX; remove unregisters card and clears routing.

## Dependencies and Integration
Depends on Freescale GUTS, SSI and DMA helper headers, OF properties, and WM8960 codec support. It integrates with legacy SSI nodes and Freescale DMA platform names derived by `fsl_asoc_get_dma_channel()`.

## Risks and Test Signals
Risks include ignoring legacy `fsl,mode`, hard-coded I2S slave topology, manual memory lifetime, missing `of_node_put(codec_np)` on the successful path in the visible probe flow, and global GUTS side effects. Test signals are late init after GUTS availability, card registration, PMUX/DMUX programming and restoration, codec sysclk setup from DT clock frequency, and WM8960 playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/p1022_rdk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/pcm030-audio-fabric.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/pcm030-audio-fabric.c

## Purpose
Machine/fabric driver for the Phytec PCM030 board using the MPC5200 PSC AC97 interface and a WM9712 AC97 codec. It creates analog and IEC958 DAI links and instantiates the legacy codec platform device.

## APIs, Types, and Functions
`struct pcm030_audio_data` stores the card and allocated codec platform device. Static DAI link definitions connect CPU DAIs `mpc5200-psc-ac97.0`/`.1` to `wm9712-codec` DAIs `wm9712-hifi` and `wm9712-aux`. `pcm030_fabric_probe()` validates machine compatibility, assigns platform OF nodes, requests the codec module, creates the codec platform device, and registers the card. Remove unregisters the card and codec device.

## Control Flow, State, and Persistence
Probe only runs on `phytec,pcm030`, reads `asoc-platform`, assigns it to each DAI link platform, loads `snd-soc-wm9712`, allocates/adds `wm9712-codec`, then registers the static `pcm030_card`. State is partly static card/link data and partly per-device `pcm030_audio_data`.

## Dependencies and Integration
Depends on MPC5200 AC97 CPU DAIs from `mpc5200_psc_ac97.c`, WM9712 codec module, OF machine compatibility, and ASoC card registration. The `asoc-platform` phandle ties the fabric to the PSC AC97 platform component.

## Risks and Test Signals
Risks include static card/link structures limiting multi-instance use, manual codec platform-device lifetime, weak handling when `platform_device_alloc()` fails before `platform_device_add()`, and legacy module autoload assumptions. Test signals are probe only on PCM030, WM9712 module load and platform device creation, both AC97 analog and IEC958 links registered, and card removal releasing the codec device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/pcm030-audio-fabric.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/generic/Kconfig

## Purpose
Kconfig menu for generic ASoC machine/helper drivers.

## APIs, Types, and Functions
Defines tristate symbols `SND_SIMPLE_CARD_UTILS`, `SND_SIMPLE_CARD`, `SND_AUDIO_GRAPH_CARD`, `SND_AUDIO_GRAPH_CARD2`, `SND_AUDIO_GRAPH_CARD2_CUSTOM_SAMPLE`, and `SND_TEST_COMPONENT`. Simple/audio graph cards select `SND_SIMPLE_CARD_UTILS`; graph drivers and test component depend on OF where needed.

## Control Flow, State, and Persistence
There is no runtime flow. The file controls build-time inclusion and dependency selection for generic sound-card drivers.

## Dependencies and Integration
Integrated by the parent sound/soc Kconfig. The symbols map to objects in the adjacent Makefile and make generic DT-described card drivers available to platforms.

## Risks and Test Signals
Risks include misspelled help text, missing dependency selections for OF-only parsers, and unintentional module/built-in combinations if utility code is not selected. Test signals are Kconfig dependency resolution for built-in and module builds and successful compilation of each selected generic driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/generic/Makefile

## Purpose
Build rules for generic ASoC card and helper drivers.

## APIs, Types, and Functions
Maps composite object names to source objects: `snd-soc-simple-card-utils`, `snd-soc-simple-card`, `snd-soc-audio-graph-card`, `snd-soc-audio-graph-card2`, `snd-soc-audio-graph-card2-custom-sample`, and `snd-soc-test-component`. Adds each object to `obj-$(CONFIG_...)` using the Kconfig symbols.

## Control Flow, State, and Persistence
No runtime flow. Build state is determined by Kconfig and Kbuild when compiling modules or built-ins.

## Dependencies and Integration
Consumes the symbols defined in `Kconfig` and integrates the generic ASoC drivers into the kernel build.

## Risks and Test Signals
Risks are object-name mismatch, missing object when a Kconfig symbol is enabled, or stale source references after file renames. Test signals are `make sound/soc/generic/` and full kernel builds with each config as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card.c -->
# sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card.c

## Purpose
Generic ASoC machine driver for OF graph-described audio cards. It parses CPU/codec endpoints listed in `dais`, creates normal or DPCM DAI links, handles conversion properties, link directions, trigger ordering, optional amplifier GPIO control, and card registration.

## APIs, Types, and Functions
Exports `audio_graph_parse_of()`. Key helpers are `graph_outdrv_event()`, `soc_component_is_pcm()`, `graph_parse_convert()`, `graph_parse_node()`, `graph_link_init()`, `graph_dai_link_of()`, `graph_dai_link_of_dpcm()`, `parse_as_dpcm_link()`, `__graph_for_each_link()`, `graph_for_each_link()`, `graph_count_noml()`, `graph_count_dpcm()`, `graph_get_dais_count()`, and `graph_probe()`.

## Control Flow, State, and Persistence
Probe allocates `simple_util_priv`, installs an amplifier DAPM widget, sets card probe to `graph_util_card_probe`, enables DPCM selectability for `audio-graph-scu-card`, and calls `audio_graph_parse_of()`. Parsing first counts normal/DPCM links by walking every CPU port endpoint in the top-level `dais` list. It then initializes private link arrays, gets optional `pa` GPIO, parses widgets/routing, walks links again to populate CPU/codec components, TDM, clocks, DAI format, direction flags, convert-rate/channels/sample-format data, names, DPCM FE/BE flags, codec prefixes, trigger order, and component chaining behavior. Finally it parses the card name and registers the card.

## Dependencies and Integration
Depends on OF graph APIs, GPIO descriptors, `sound/graph_card.h`, and the simple-card utility layer. Compatible strings are `audio-graph-card` and `audio-graph-scu-card`; removal delegates to `simple_util_remove()` and PM to `snd_soc_pm_ops`.

## Risks and Test Signals
Risks include complex OF graph lifetime/refcount handling, DPCM detection based on codec port endpoint count or convert properties, random topology issues if CPU/codec walk ordering changes, `SNDRV_MAX_LINKS` limits, optional pluggable codec endpoint handling, and component-chaining `no_pcm` decisions based on whether the CPU component exposes PCM. Test signals are normal one-link cards, multi-CPU/single-codec DPCM cards, convert-rate/format/channel fixups, link direction properties at top/port/endpoint scopes, PA GPIO toggling on DAPM power events, component chaining BE-to-BE paths, and clean reference cleanup on parse errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card.c -->
