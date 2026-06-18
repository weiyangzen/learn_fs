<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/j721e-evm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/j721e-evm.c

## Purpose
ASoC machine driver for TI J721E/J7200 common processor board audio, optionally with the IVI extension. It describes PCM3168A codec links, McASP CPU DAIs, DAPM board endpoints, and clock-parent/rate policy for the CPB and IVI audio domains.

## APIs, Types, and Functions
Key state is `struct j721e_priv`, which owns the card, dynamic DAI links, codec prefixes, rate interval, PLL/HSDIV rates, two `struct j721e_audio_domain` instances, and a mutex. Important helpers are `j721e_configure_refclk()`, `j721e_audio_startup()`, `j721e_audio_hw_params()`, `j721e_audio_shutdown()`, `j721e_audio_init()`, `j721e_audio_init_ivi()`, `j721e_get_clocks()`, `j721e_calculate_rate_range()`, `j721e_soc_probe_cpb()`, `j721e_soc_probe_ivi()`, and `j721e_soc_probe()`. OF compatibles select CPB, CPB+IVI, or J7200 clock data.

## Control Flow, State, and Persistence
Probe parses the card model, phandles for McASP and PCM3168A codec nodes, named codec/McASP clocks, and creates playback/capture DAI links. Startup serializes domain use, enforces a shared active sample rate across domains when any stream is active, and resets CPU/codec TDM slots to stereo 32-bit. `hw_params` chooses 16- or 32-bit slots, selects a 48 kHz or 44.1 kHz PLL family, reparents codec and McASP clocks, sets SCKI to 256/512/768 x sample rate, and records the domain rate. Shutdown clears the domain rate when the active count reaches zero.

## Dependencies and Integration
Depends on ASoC machine-card APIs, OF phandles/properties, common clock framework, PCM3168A codec DAI names, and TI McASP `MCASP_CLK_HCLK_AUXCLK`. It integrates with device tree bindings using `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `ti,ivi-mcasp`, `ti,ivi-codec-a`, and `ti,ivi-codec-b`.

## Risks and Test Signals
Risks include shared-rate constraints blocking mixed-rate domain usage, missing optional 44.1 kHz parents on J7200 limiting rate families, stale `hsdiv_rates` when two domains share parent IDs, OF node reference lifetime leaks on success paths, and `-ENOTSUPP` masking if a codec cannot accept TDM/sysclk setup. Test signals are probe for all compatibles, CPB-only and IVI route creation, 44.1/48 kHz family playback and capture, simultaneous CPB/IVI stream constraints, 16-bit versus wider slot width, and failure paths for absent clocks/phandles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/j721e-evm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/n810.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/n810.c

## Purpose
Legacy ASoC machine driver for Nokia N810 and N810 WiMAX boards using OMAP McBSP and a TLV320AIC33 codec. It wires board DAPM endpoints, GPIO amplifier controls, SYS_CLKOUT2 clocking, and user-selectable speaker/jack/input modes.

## APIs, Types, and Functions
The file defines one `snd_soc_card`, one `snd_soc_dai_link`, DAPM widgets/routes, and external mixer controls. Core helpers are `n810_ext_control()`, `n810_startup()`, `n810_shutdown()`, `n810_hw_params()`, enum get/put handlers for speaker, jack, and DMIC input selection, DAPM GPIO events `n810_spk_event()`/`n810_jack_event()`, and module init/exit `n810_soc_init()`/`n810_soc_exit()`.

## Control Flow, State, and Persistence
Module init only continues on N810-compatible DT machines, creates a `soc-audio` platform device, obtains `sys_clkout2_src`, `sys_clkout2`, and `func_96m_ck`, sets a 12 MHz output clock, and requests headphone/speaker GPIOs. Runtime startup constrains channels to stereo, syncs DAPM pin state from static control variables, and enables SYS_CLKOUT2. `hw_params` sets the codec sysclk to 12 MHz. The selected speaker, jack mode, and input source are process-global static integers persisted for the module lifetime.

## Dependencies and Integration
Depends on legacy platform-device ASoC registration, OMAP McBSP DAI name `48076000.mcbsp`, TLV320AIC3x codec `tlv320aic3x-codec.1-0018`, GPIO descriptors named `headphone` and `speaker`, and board clocks. It includes McBSP public clock IDs but only uses McBSP through the static link format.

## Risks and Test Signals
Risks include static global state preventing multiple instances, legacy machine matching, no DT phandle-based DAI lookup, cleanup asymmetry for `func96m_clk` on one error branch, and analog headset mic marked TODO. Test signals are N810/N810 WiMAX module load, 12 MHz SYS_CLKOUT2 enable/disable per stream, stereo-only constraint, DAPM pin toggles from mixer controls, GPIO amplifier transitions, and TLV320AIC33 sysclk success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/n810.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-abe-twl6040.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-abe-twl6040.c

## Purpose
Device-tree ASoC machine driver for OMAP ABE boards with TWL6040 codec and optional OMAP DMIC capture. It sets up McPDM-to-TWL6040 audio, optional DMIC-to-dmic-codec capture, board routing, headset jack detection, and TWL6040 trim-based McPDM offset cancellation.

## APIs, Types, and Functions
`struct abe_twl6040` embeds the card, two possible DAI links, jack-detection flag, and TWL6040 MCLK frequency. Important functions are `omap_abe_hw_params()`, `omap_abe_dmic_hw_params()`, `omap_abe_twl6040_init()`, `omap_abe_dmic_init()`, `omap_abe_probe()`, plus module init/exit that registers a simple `dmic-codec` platform device.

## Control Flow, State, and Persistence
Probe parses `ti,model`, `ti,audio-routing`, required `ti,mcpdm`, optional `ti,dmic`, `ti,jack-detection`, and required `ti,mclk-freq`. The TWL6040 link sets codec sysclk based on `twl6040_get_clk_id()`: HPPLL uses board MCLK, LPPLL uses 32.768 kHz. The DMIC link programs input PAD_CLKS at 19.2 MHz and ABE DMIC output clock at 2.4 MHz. Link init reads TWL6040 HS output trim and passes offsets to the McPDM CPU DAI; jack detection is registered only when enabled by DT.

## Dependencies and Integration
Depends on TWL6040 codec helpers, OMAP McPDM exported `omap_mcpdm_configure_dn_offsets()`, OMAP DMIC clock IDs, ASoC jack/DAPM APIs, and OF phandles. It integrates codec names `twl6040-codec`/`twl6040-legacy` and `dmic-codec`/`dmic-hifi` with CPU/platform nodes from device tree.

## Risks and Test Signals
Risks include the first link being named `DMIC` while streaming TWL6040, mandatory MCLK property, static global `hs_jack`/`dmic_codec_dev`, no explicit `of_node_put()` for parsed phandles, and dependency on TWL6040 trim values before McPDM stream start. Test signals are card probe with and without optional DMIC, jack reports, HPPLL and LPPLL sysclk paths, route parsing, McPDM downlink offset programming, and DMIC capture clock setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-abe-twl6040.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.c

## Purpose
ASoC CPU DAI driver for the OMAP4 digital microphone controller. It exposes capture-only S32_LE streams, programs DMIC clocks/dividers/FIFO/DMA, and registers an sDMA PCM platform.

## APIs, Types, and Functions
`struct omap_dmic` stores MMIO base, functional clock, PM QoS request, selected input/output clocks, divider, threshold, enabled channel mask, active flag, mutex, and DMA data. Key functions include `omap_dmic_select_fclk()`, `omap_dmic_select_outclk()`, `omap_dmic_select_divider()`, DAI ops for startup/shutdown/hw_params/prepare/trigger/set_sysclk, and platform probe `asoc_dmic_probe()`.

## Control Flow, State, and Persistence
Probe maps `mpu` registers, uses `dma` resource plus `OMAP_DMIC_DATA_REG` as the DMA address, gets `fck`, sets default sysclk source to sync mux, registers the DAI/component, and registers sDMA with `up_link`. DAI probe enables runtime PM, clears CTRL, initializes threshold to max-3, and installs DMA data. `set_sysclk` validates and stores input fclk and output DMIC clock, optionally reparents the fclk mux while runtime PM is active. `hw_params` computes a legal divider, enables 1/2/3 stereo DMIC uplinks for 2/4/6 channels, sets DMA burst and latency. Prepare writes FIFO threshold, left-justified format, polarity bits, and divider. Trigger starts/stops channel and DMA enable bits.

## Dependencies and Integration
Depends on OMAP DMIC register definitions, common clock framework, runtime PM, CPU latency QoS, ASoC DAI APIs, DMAengine PCM, and the TI sDMA helper. The OF match is `ti,omap4-dmic`; machine drivers must call `set_sysclk` for both input and output clocks before `hw_params`.

## Risks and Test Signals
Risks include no interrupt handling, `pm_runtime_get_sync()` return values ignored, reparenting while active only guarded when hardware lines are enabled, repeated CTRL writes in prepare, strict clock/rate combinations for 96/192 kHz, and global single-stream `active` policy. Test signals are valid/invalid clock divider matrix coverage, 2/4/6 channel capture, 96 kHz and 192 kHz operation, DMA burst sizing, runtime PM transitions, and rejection of reparent attempts during active capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.h

## Purpose
Private register and clock definition header for the OMAP DMIC ASoC driver and machine drivers that configure DMIC clocks.

## APIs, Types, and Functions
Defines DMIC register offsets, IRQ/DMA/CTRL/FIFO bit masks, output format constants, FIFO threshold maximum, and `enum omap_dmic_clk` values: PAD_CLKS, SLIMBUS, sync mux, and ABE DMIC output clock. It contains no functions or runtime storage.

## Control Flow, State, and Persistence
This header is compile-time configuration only. Its values are consumed by `omap-dmic.c` for MMIO programming and by `omap-abe-twl6040.c` to request the correct input/output clocks through `snd_soc_dai_set_sysclk()`.

## Dependencies and Integration
Included by OMAP DMIC controller and ABE/TWL6040 machine code. The clock enum is part of the internal machine-driver contract and must match the `set_sysclk` implementation in `omap-dmic.c`.

## Risks and Test Signals
Risks are primarily register-definition drift against hardware manuals, misspelled `OMAP_DMIC_SYSCLK_SLIMBLUS_CLKS`, and callers depending on enum numeric values. Test signals are successful DMIC build, correct bitfields in CTRL/FIFO/DMA registers under capture, and machine-driver clock configuration acceptance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-hdmi.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-hdmi.c

## Purpose
ASoC HDMI audio glue for OMAP4/OMAP5 DSS. It creates a playback-only card and CPU DAI around DSS HDMI audio callbacks, DMAengine PCM, IEC60958 channel status, and CEA-861 audio infoframes.

## APIs, Types, and Functions
`struct hdmi_audio_data` stores the card, DSS ops/device, DMA data, DSS audio metadata, IEC/CEA structs, and current PCM stream guarded by a mutex. Core functions are `hdmi_dai_abort()`, `hdmi_dai_startup()`, `hdmi_dai_hw_params()`, `hdmi_dai_trigger()`, `hdmi_dai_shutdown()`, and `omap_hdmi_audio_probe()`. Two DAI templates differ by supported formats: OMAP4 permits S16/S24, OMAP5 only S16.

## Control Flow, State, and Persistence
Probe consumes platform data with DSS device, ops, version, and DMA address, registers the component on the DSS device, registers sDMA using `audio_tx`, and creates a dummy-codec ASoC card. Startup imposes 128-byte period/buffer alignment, binds DMA data, records the current stream, and calls DSS `audio_startup()` with an abort callback. `hw_params` chooses DMA maxburst, fills IEC60958 status and CEA infoframe fields based on format/rate/channels, then calls DSS `audio_config()`. Trigger starts/stops DSS audio; shutdown calls DSS `audio_shutdown()` and clears current stream.

## Dependencies and Integration
Depends on `sound/omap-hdmi-audio.h` platform data callbacks, ALSA IEC/CEA definitions, ASoC DAI/card APIs, DMAengine PCM, and TI sDMA registration. The display subsystem can asynchronously abort playback through the registered callback.

## Risks and Test Signals
Risks include platform-data-only binding, channel allocation limited to hard-coded 2/6/other mappings, current-stream WARNs rather than recoveries, OMAP5 format restriction mismatch with hardware expectations, and concurrent display disable during PCM operations. Test signals are probe for version 4 and 5, DSS callback ordering, abort on display disable, all supported rates in IEC status, 2/6/8 channel CEA mappings, S16/S24 rejection by version, and aligned DMA periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-priv.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-priv.h

## Purpose
Private register, bitfield, cached-MMIO, and state header for the OMAP McBSP ASoC DAI driver and sidetone support.

## APIs, Types, and Functions
Defines McBSP register indices, bit macros for SPCR/PCR/RCR/XCR/SRGR/MCR/CCR/SYSCON/IRQ registers, DMA operating mode constants, clock-source constants, `struct omap_mcbsp_reg_cfg`, forward declaration of sidetone data, and central `struct omap_mcbsp`. Inline helpers `omap_mcbsp_write()` and `omap_mcbsp_read()` update both hardware and a u16/u32 register cache, with macros for cached and uncached access. It declares sidetone init/start/stop.

## Control Flow, State, and Persistence
The header itself does not execute runtime control flow, but it defines the persistent McBSP state shared by controller and sidetone code: device/clock/MMIO, IRQs, active/configured/free flags, platform data, register cache pointer, DMA data, FIFO thresholds, format, input frequency, latency, word length, clock divider, and PM QoS request.

## Dependencies and Integration
Depends on `linux/platform_data/asoc-ti-mcbsp.h` for SoC quirks and callbacks. Used by `omap-mcbsp.c` and `omap-mcbsp-st.c`; the public machine-driver boundary is kept in `omap-mcbsp.h`.

## Risks and Test Signals
Risks include cache coherency assumptions for write-only or status bits, u16/u32 register-size branching, direct casts into `reg_cache`, SoC revision differences hidden behind `has_ccr`/`has_wakeup`, and `mcbsp_omap1()` compile-time behavior. Test signals are register programming on OMAP1/2/3/4 variants, cached interrupt-clear behavior, sidetone register access, and FIFO threshold/CCR paths on hardware with and without those blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-st.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-st.c

## Purpose
Sidetone support for OMAP3 McBSP ports. It manages sidetone FIR coefficients, channel gains, sysfs taps, ALSA mixer controls, and hardware enable/disable sequencing alongside the main McBSP stream state.

## APIs, Types, and Functions
`struct omap_mcbsp_st_data` holds sidetone MMIO, optional interface clock, running/enabled flags, 128 FIR taps, tap count, and two signed gains. Exported functions are `omap_mcbsp_st_init()`, `omap_mcbsp_st_start()`, `omap_mcbsp_st_stop()`, and `omap_mcbsp_st_add_controls()`. Internal helpers program sidetone core registers, FIR taps, gains, sysfs `st_taps`, and controls for McBSP2/McBSP3.

## Control Flow, State, and Persistence
Init is optional: if no `sidetone` memory resource exists it returns success without sidetone state. When present it maps sidetone registers, gets optional `ick`, creates the `st_taps` sysfs group, and attaches state to `mcbsp`. Enabling sidetone sets `enabled`, starts if possible, writes all 128 FIR coefficients, writes gains, disables autoidle, enables McBSP SSELCR sidetone and sidetone-core enable bits, and may force the interface clock on through platform data. Stop reverses enable bits and autoidle. ALSA controls persist signed gain and switch state; sysfs persists current FIR taps in memory.

## Dependencies and Integration
Depends on the main McBSP private state, platform `force_ick_on` callback, ASoC DAI controls, sysfs device attributes, and McBSP2/3 port IDs. Main `omap-mcbsp.c` invokes start/stop around stream start/stop.

## Risks and Test Signals
Risks include parsing unlimited comma-separated tap input without checking `i < 128`, polling FIR write completion with no delay, controls only for ports 2 and 3, possible sleep/clock callbacks under spinlock, and sidetone start depending on `mcbsp->free`. Test signals are sidetone resource absent/present probe, sysfs tap validation, gain control updates while enabled, McBSP2/3 controls, FIR load completion, stream start/stop clock gating, and no lockdep warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.c

## Purpose
ASoC CPU DAI driver for OMAP McBSP serial ports, providing I2S/left-justified/DSP_A/DSP_B playback and capture over sDMA with SoC-specific register layout, FIFO thresholds, clock-source selection, runtime PM, IRQ diagnostics, and optional sidetone.

## APIs, Types, and Functions
Important paths are `omap_mcbsp_request()`/`omap_mcbsp_free()`, `omap_mcbsp_config()`, `omap_mcbsp_start()`/`omap_mcbsp_stop()`, DAI ops startup/shutdown/prepare/trigger/delay/hw_params/set_fmt/set_clkdiv/set_sysclk, `omap2_mcbsp_set_clks_src()`, FIFO threshold sysfs handlers, and platform probe/remove. The DAI supports 1-16 channels, 8-96 kHz, S16_LE/S32_LE, reduced to S16 on 16-bit-register variants.

## Control Flow, State, and Persistence
Platform probe merges OF match data and optional platform quirks, maps MMIO, discovers IRQs and DMA resources, sets DMA register addresses, gets `fck`, initializes FIFO thresholds and optional sysfs controls, initializes sidetone, registers the component, and registers sDMA. Startup reserves the port on first active stream, allocates a register cache, requests IRQs, and adds FIFO constraints. `set_fmt`, `set_clkdiv`, and `set_sysclk` build cached register configuration before `hw_params`. `hw_params` derives word length, frame format, FIFO packet size, DMA burst, latency QoS budget, frame period/width, and writes configuration once for the first stream. Trigger maintains active count and toggles SRG/frame sync/TX/RX/CCR bits. Shutdown frees the port and cache after the last stream.

## Dependencies and Integration
Depends on OMAP platform data or OF compatibles, DMAengine PCM via `sdma_pcm_platform_register()`, runtime PM, CPU latency QoS, common clock framework, ASoC DAI APIs, and sidetone helpers. Machine drivers use the public clock IDs/divider from `omap-mcbsp.h`.

## Risks and Test Signals
Risks include register cache lifetime tied to reservation, global static DAI format mutation for 16-bit-register devices, IRQ request/free paths across combined versus split IRQs, threshold-mode divider edge cases, PM QoS add/update/remove sequencing, reparenting clocks while active, and startup ignoring return values from several constraint calls. Test signals are all supported formats/master modes, full-duplex shared configuration, FIFO threshold sysfs, packet versus threshold DMA, delay reporting, suspend/resume with runtime PM, sync-error IRQs, and OMAP2420/2430/3/4 variant probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.h

## Purpose
Public McBSP ASoC header for machine drivers. It exposes clock-source IDs, divider IDs, and the sidetone control-registration helper without leaking private register definitions.

## APIs, Types, and Functions
Defines `enum omap_mcbsp_clksrg_clk` with internal FCLK, external CLKS, internal ICLK, external CLKX, and external CLKR sources. Defines `enum omap_mcbsp_div` with `OMAP_MCBSP_CLKGDV`. Declares `omap_mcbsp_st_add_controls(struct snd_soc_pcm_runtime *rtd, int port_id)`.

## Control Flow, State, and Persistence
No runtime state is stored here. The constants are passed by board drivers into `snd_soc_dai_set_sysclk()` and `snd_soc_dai_set_clkdiv()`; the sidetone helper adds controls to an existing DAI at runtime.

## Dependencies and Integration
Includes `sound/dmaengine_pcm.h` for ASoC/DMA-related types and is included by OMAP machine drivers such as N810, Pandora, OSK, RX51, and TWL4030 boards.

## Risks and Test Signals
Risks are ABI drift between enum values and `omap-mcbsp.c`, plus machine drivers calling `set_sysclk` before `set_fmt` in cases documented as order-sensitive. Test signals are build coverage of all machine drivers, clock/divider calls accepted by McBSP, and RX51 sidetone controls appearing for port 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcbsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.c

## Purpose
ASoC CPU DAI driver for OMAP4 McPDM, used primarily with TWL6040/Phoenix codec PDM audio. It handles playback/capture channel masks, FIFO/DMA thresholds, IRQ diagnostics, PM QoS latency, suspend/resume, and downlink offset cancellation.

## APIs, Types, and Functions
`struct omap_mcpdm` stores device/MMIO/IRQ, PM QoS, mutex, per-direction `mcpdm_link_config`, downlink RX offsets, restart flag, suspend runtime-PM active count, and DMA data. Important functions are `omap_mcpdm_open_streams()`, `omap_mcpdm_close_streams()`, `omap_mcpdm_start()`, `omap_mcpdm_stop()`, DAI startup/shutdown/hw_params/prepare/probe/remove, component suspend/resume, exported `omap_mcpdm_configure_dn_offsets()`, and platform probe.

## Control Flow, State, and Persistence
Probe maps `mpu`, uses `dma` resource plus DN/UP data offsets for DMA, gets IRQ, registers the component, and registers sDMA channels `dn_link` and `up_link`. DAI probe enables runtime PM, clears CTRL, requests IRQ, sets default thresholds, and initializes DMA data. Startup opens streams on first active substream, enabling watchdog, IRQs, offsets, thresholds, and DMA. `hw_params` maps 1-5 playback or 1-3 capture channels to PDM link masks, sets peer defaults when the other direction is idle, computes DMA maxburst and latency, and marks restart when channel masks change. Prepare applies PM QoS and starts or restarts hardware. Suspend closes active hardware and records runtime PM references; resume restores them and restarts active streams.

## Dependencies and Integration
Depends on McPDM register macros, runtime PM, IRQs, CPU latency QoS, DMAengine PCM, TI sDMA helper, and ASoC DAI/component APIs. Machine drivers such as ABE/TWL6040 call the exported offset function using TWL6040 trim data.

## Risks and Test Signals
Risks include IRQ requested from DAI probe rather than platform probe, `pm_runtime_get_sync()` ignored, peer link-mask defaults creating implicit stereo channels, restart needed for runtime channel changes, limited rates to 88.2/96 kHz S32_LE, and no explicit trigger op. Test signals are 1-5 channel playback, 1-3 channel capture, duplex startup/shutdown, offset cancellation writes, IRQ logs, suspend/resume with active streams, DMA thresholds/latency, and channel-mask restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.h

## Purpose
Private/public McPDM definition header. It provides register offsets, bitfields, thresholds, offset-cancellation macros, and the machine-driver helper prototype for configuring downlink offsets.

## APIs, Types, and Functions
Defines McPDM register addresses for IRQ, DMA, control, data, FIFO, and offset registers; IRQ and DMA bits; uplink/downlink channel mask macros; reset/watchdog/output format bits; FIFO threshold maxima; downlink RX1/RX2 offset enable/value macros; and `omap_mcpdm_configure_dn_offsets()`.

## Control Flow, State, and Persistence
No logic executes in the header. The macros determine how `omap-mcpdm.c` persists channel masks and offset values in hardware registers; the exported function lets a machine driver set per-codec trim-derived offsets before stream start.

## Dependencies and Integration
Included by `omap-mcpdm.c` and `omap-abe-twl6040.c`. The function prototype depends on ASoC runtime type visibility through included build context.

## Risks and Test Signals
Risks include channel-number macros assuming one-based channel indexes, offset fields silently masking to five bits, and consumers depending on exact CTRL bit layout. Test signals are build coverage, McPDM link-mask programming for all channel counts, and TWL6040 trim offset writes being visible in `MCPDM_REG_DN_OFFSET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-twl4030.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-twl4030.c

## Purpose
Generic ASoC machine driver for TI OMAP boards with a TWL4030 codec. It replaces several older board-specific drivers by supporting DT or platform-data routing, HiFi and optional voice links, headset jack GPIO detection, and stereo/TDM format selection.

## APIs, Types, and Functions
`struct omap_twl4030` stores the headset jack. Important code paths are `omap_twl4030_hw_params()` for channel-count-dependent DAI format, `omap_twl4030_init()` for jack and optional pin disconnects, `twl4030_disconnect_pin()`, static HiFi/voice DAI links, and `omap_twl4030_probe()`.

## Control Flow, State, and Persistence
Probe handles either DT or legacy platform data. DT parses `ti,model`, required `ti,mcbsp`, optional `ti,mcbsp-voice`, and optional `ti,audio-routing`; with routing it marks the card fully routed. Platform data supplies card name, voice link presence, and optional custom routing booleans. HiFi `hw_params` sets I2S provider mode for stereo and DSP_A provider mode for four-channel TDM. Runtime init adds jack GPIO support only if `ti,jack-det-gpio` is present and disables unconnected pins for custom platform-data routing.

## Dependencies and Integration
Depends on TWL4030 codec DAI names `twl4030-hifi`/`twl4030-voice`, OMAP McBSP CPU DAIs, ASoC jack GPIO APIs, OF phandles, and legacy `omap-twl4030` platform data.

## Risks and Test Signals
Risks include static global card/link structures mutated per probe, optional `of_node_put()` omissions, property name mismatch between `ti,jack-det-gpio` and GPIO descriptor lookup, only 2- and 4-channel HiFi formats, and mixed DT/platform-data paths. Test signals are DT and platform-data probe, HiFi stereo and four-channel streams, optional voice link, jack GPIO reporting, custom routing pin disables, and audio-routing parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-twl4030.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap3pandora.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap3pandora.c

## Purpose
Legacy ASoC machine driver for the OMAP3 Pandora handheld. It connects an external PCM1773 playback DAC and TWL4030 capture paths through two McBSP links, with board-specific DAC regulator, DAC power GPIO, headphone amplifier GPIO, and DAPM routing.

## APIs, Types, and Functions
Important functions are `omap3pandora_hw_params()`, `omap3pandora_dac_event()`, `omap3pandora_hp_event()`, `omap3pandora_out_init()`, `omap3pandora_in_init()`, and module init/exit. Static card data defines two links, DAPM widgets, and routes for PCM DAC output and TWL4030 inputs.

## Control Flow, State, and Persistence
Module init checks `machine_is_omap3_pandora()`, creates a `soc-audio` platform device, gets `dac` and `amp` GPIOs, and obtains the `vcc` regulator. `hw_params` sets codec sysclk to 26 MHz, McBSP sysclk to external CLKS at 256 x rate, and McBSP divider to 8. DAPM events power the PCM1773 regulator and /PD GPIO with required delays, and toggle headphone amp GPIO. Link init disables unused TWL4030 pins.

## Dependencies and Integration
Depends on legacy machine ID matching, OMAP McBSP clock IDs, TWL4030 codec DAI, regulator framework, GPIO descriptors, and platform-device ASoC registration. McBSP2 handles playback; McBSP4 handles line/mic input.

## Risks and Test Signals
Risks include legacy non-DT binding, static regulator/GPIO globals, external clock assumptions, no cleanup for GPIO-managed state beyond platform device lifetime, and typographical route comments. Test signals are Pandora-only load, DAC regulator sequencing with 1 ms delays, headphone amp DAPM toggle, playback and capture links, McBSP external clock/divider setup across sample rates, and disabled unused TWL4030 pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap3pandora.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/osk5912.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/osk5912.c

## Purpose
Legacy ASoC machine driver for OMAP OSK5912 using McBSP1 and a TLV320AIC23 codec. It provides fixed DAPM routes and 12 MHz codec MCLK management.

## APIs, Types, and Functions
Defines startup/shutdown/hw_params ops, one DSP_B DAI link, one card, DAPM widgets/routes, and module init/exit. `osk_soc_init()` allocates the `soc-audio` device, obtains `mclk`, and programs it to `CODEC_CLOCK` when needed.

## Control Flow, State, and Persistence
Module init checks `machine_is_omap_osk()`, creates the ASoC platform device, gets the codec MCLK, and sets it to 12 MHz. Startup enables the MCLK; shutdown disables it. `hw_params` sets codec sysclk to 12 MHz. The MCLK pointer and platform device are static module-lifetime state.

## Dependencies and Integration
Depends on legacy machine ID matching, TLV320AIC23 codec DAI `tlv320aic23-hifi`, McBSP1 CPU/platform DAI names, and OMAP clock APIs.

## Risks and Test Signals
Risks include legacy non-DT binding, fixed DSP_B format, minimal error recovery, old-style `printk`, and static single-instance state. Test signals are OSK-only module load, MCLK set/enable/disable, TLV320AIC23 sysclk setup, headphone/line/mic route availability, and playback/capture over McBSP1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/osk5912.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/rx51.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/rx51.c

## Purpose
ASoC machine driver for Nokia RX-51/N900 audio. It connects TLV320AIC34, an auxiliary codec, TPA6130A2 headphone amplifier, McBSP sidetone controls, AV jack GPIO detection, speaker/DMIC/jack mode controls, and board GPIO routing for TV-out and amplifiers.

## APIs, Types, and Functions
`struct rx51_audio_pdata` stores TV-out selection, ECI switch, and speaker amp GPIOs. Important functions are `rx51_ext_control()`, startup/hw_params ops, control get/put handlers, `rx51_spk_event()`, `rx51_aic34_init()`, and `rx51_soc_probe()`. Static card data includes one DAI link, two aux devices, codec prefixes, DAPM widgets/routes, and controls.

## Control Flow, State, and Persistence
Probe checks legacy machine ID or N900-compatible OF machine, rewrites static DAI/aux/codec components from DT phandles when present, allocates GPIO platform data, requests three GPIOs, and registers the card. Startup constrains channels to stereo and syncs DAPM pins. `hw_params` sets codec sysclk to 19.2 MHz. Mixer controls persist global speaker, DMIC, and jack mode state; `rx51_ext_control()` enables DAPM pins and toggles TV-out GPIO. Link init limits headphone volume, adds McBSP2 sidetone controls, creates AV jack reporting headset/videoout, and binds a jack GPIO.

## Dependencies and Integration
Depends on TLV320AIC3x codec instances, TPA6130A2 aux component, OMAP McBSP and sidetone helper, ASoC jack GPIO APIs, GPIO descriptors, and optional OF phandles `nokia,cpu-dai`, `nokia,audio-codec`, and `nokia,headphone-amplifier`.

## Risks and Test Signals
Risks include static global card/link/control state, mixed legacy/DT matching, GPIOs required even when some routes are unused, global mode variables without locking beyond control callbacks, and sidetone controls failing the whole link init. Test signals are N900 DT probe, aux codec/amplifier binding, speaker/DMIC/jack control DAPM effects, AV jack GPIO reports, TV-out GPIO switching, sidetone controls on McBSP2, and volume limit application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/rx51.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.c

## Purpose
Shared TI sDMA PCM registration helper for ASoC CPU DAIs. It supplies common PCM hardware constraints and adapts optional named DMA channels to `devm_snd_dmaengine_pcm_register()`.

## APIs, Types, and Functions
Defines `sdma_pcm_hardware`, `sdma_dmaengine_pcm_config`, and exported `sdma_pcm_platform_register(struct device *dev, char *txdmachan, char *rxdmachan)`. The hardware config supports mmap, pause/resume, no-period-wakeup, interleaved access, 32-byte minimum periods, 64 KiB maximum periods, 128 KiB buffers, and 2-255 periods.

## Control Flow, State, and Persistence
If both channel names are NULL, registration uses standard `tx`/`rx` DMA channel names and the static config. If one or both custom names are supplied, it allocates a per-device config, copies defaults, sets half-duplex when one direction is absent, normalizes the single direction into `chan_names[0]`, and registers DMAengine PCM. Persistent state is owned by devm and DMAengine PCM.

## Dependencies and Integration
Depends on ALSA DMAengine PCM helpers and is called by OMAP McBSP, McPDM, DMIC, and HDMI drivers. Channel names such as `tx`, `rx`, `dn_link`, `up_link`, and `audio_tx` are supplied by callers and DT DMA bindings.

## Risks and Test Signals
Risks include caller confusion over single-direction channel normalization, fixed 128 KiB preallocation limiting large buffers, and half-duplex flags when only capture/playback is requested. Test signals are full-duplex default registration, named duplex registration, named half-duplex registration, DMA channel lookup from DT, and buffer/period constraint visibility in ALSA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.h

## Purpose
Small public helper header for TI sDMA PCM platform registration.

## APIs, Types, and Functions
Declares `sdma_pcm_platform_register()` when `CONFIG_SND_SOC_TI_SDMA_PCM` is enabled. Otherwise provides a stub returning `-ENODEV`.

## Control Flow, State, and Persistence
The header has no runtime state. It controls compile-time integration: drivers can call the helper unconditionally and receive an explicit failure when the helper is not built.

## Dependencies and Integration
Used by TI OMAP audio CPU DAI/glue drivers that depend on sDMA. Its behavior affects whether those drivers can successfully probe when the sDMA PCM module is disabled.

## Risks and Test Signals
Risk is probe failure for callers that require sDMA but do not select the config, since the stub returns `-ENODEV`. Test signals are builds with helper enabled/disabled and probe behavior for McBSP, McPDM, DMIC, and HDMI callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.c

## Purpose
Shared TI UDMA PCM registration helper for newer TI ASoC drivers. It wraps DMAengine PCM registration with broad hardware limits suitable for UDMA.

## APIs, Types, and Functions
Defines `udma_pcm_hardware`, `udma_dmaengine_pcm_config`, and exported `udma_pcm_platform_register(struct device *dev)`. The hardware configuration supports mmap, pause/resume, no-period-wakeup, interleaved access, 32-byte minimum periods, 64 KiB maximum periods, `SIZE_MAX` buffer bytes, and `UINT_MAX` periods.

## Control Flow, State, and Persistence
The only runtime path is `udma_pcm_platform_register()`, which registers the static DMAengine PCM config with no special flags. Persistent data is managed by the devm PCM registration.

## Dependencies and Integration
Depends on ALSA DMAengine PCM helpers and is intended for TI drivers using UDMA channel bindings with standard DMAengine lookup.

## Risks and Test Signals
Risks include extremely large advertised buffer/period counts relying on lower layers to constrain allocations and no preallocated buffer size. Test signals are successful DMAengine PCM registration, ALSA constraint reporting, mmap playback/capture with UDMA, pause/resume, and large-buffer rejection or acceptance by the final DMA/memory stack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.h

## Purpose
Public helper header for TI UDMA PCM platform registration.

## APIs, Types, and Functions
Declares `udma_pcm_platform_register(struct device *dev)` when `CONFIG_SND_SOC_TI_UDMA_PCM` is enabled. Otherwise provides a stub returning success.

## Control Flow, State, and Persistence
No runtime state is held here. The disabled-config stub allows callers to continue probing without registering a UDMA PCM platform, unlike the sDMA helper stub.

## Dependencies and Integration
Used by TI ASoC drivers targeting UDMA-capable SoCs. The helper implementation depends on DMAengine PCM.

## Risks and Test Signals
Risk is silent success when the helper is disabled, which can hide missing PCM platform registration until stream creation fails elsewhere. Test signals are builds with the config enabled/disabled and probe/runtime behavior of UDMA-based DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/Kconfig

## Purpose
Kconfig menu for Socionext UniPhier ASoC support. It exposes the common AIO CPU DAI driver, LD11/LD20 and PXs2 device drivers, and the internal EVEA codec driver.

## APIs, Types, and Functions
Defines `SND_SOC_UNIPHIER_AIO`, `SND_SOC_UNIPHIER_LD11`, `SND_SOC_UNIPHIER_PXS2`, and `SND_SOC_UNIPHIER_EVEA_CODEC`. The menu depends on `ARCH_UNIPHIER || COMPILE_TEST`; AIO selects `REGMAP_MMIO` and `SND_SOC_COMPRESS`; SoC device drivers select the common AIO driver; EVEA selects `REGMAP_MMIO`.

## Control Flow, State, and Persistence
This file controls build-time availability only. Selecting LD11 or PXs2 pulls in the shared AIO CPU/compress/core objects; selecting EVEA builds the internal codec independently.

## Dependencies and Integration
Integrates with the kernel ASoC Kconfig hierarchy and corresponding Makefile object names. It enables compile-test coverage outside UniPhier architectures.

## Risks and Test Signals
Risks include missing dependencies for reset/clk/syscon/DMA symbols if not selected elsewhere and broad `SND_SOC_COMPRESS` selection whenever AIO is enabled. Test signals are `allyesconfig`, `COMPILE_TEST`, module builds for each option, and dependency resolution in minimal UniPhier configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/Makefile

## Purpose
Build recipe for UniPhier ASoC modules.

## APIs, Types, and Functions
Defines compound objects: `snd-soc-uniphier-aio-cpu-y` from `aio-core.o`, `aio-dma.o`, `aio-cpu.o`, and `aio-compress.o`; `snd-soc-uniphier-aio-ld11-y` from `aio-ld11.o`; `snd-soc-uniphier-aio-pxs2-y` from `aio-pxs2.o`; and `snd-soc-uniphier-evea-y` from `evea.o`. Kconfig options map to corresponding `obj-*` module entries.

## Control Flow, State, and Persistence
No runtime behavior exists. The object grouping determines link boundaries and which exported symbols from the common AIO CPU module are available to LD11/PXs2 glue.

## Dependencies and Integration
Depends on the Kconfig symbols in this directory and on the common kernel Kbuild system. The AIO CPU object must include core, DMA, CPU DAI, and compressed-audio support together.

## Risks and Test Signals
Risks include object list drift if headers reference functions in omitted files, and common code always linking compressed support when AIO is built. Test signals are module build/link checks for each config combination and unresolved-symbol scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-compress.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-compress.c

## Purpose
Compressed audio operations for UniPhier AIO, focused on IEC61937 S/PDIF pass-through. It allocates a coherent-enough software buffer, maps it for DMA, converts user IEC frames into hardware output format, manages ring-buffer pointers, and exposes ALSA compress callbacks.

## APIs, Types, and Functions
Exports `uniphier_aio_compress_ops`. Important helpers are `uniphier_aio_comprdma_new/free()`, `uniphier_aio_compr_open/free()`, `uniphier_aio_compr_set_params()`, `uniphier_aio_compr_prepare()`, `uniphier_aio_compr_trigger()`, `uniphier_aio_compr_pointer()`, `aio_compr_send_to_hw()`, `uniphier_aio_compr_copy()`, and capability callbacks.

## Control Flow, State, and Persistence
Open claims one compressed stream per direction, marks pass-through mode, disables mmap mode, allocates `AUD_RING_SIZE` memory, maps it with a 33-bit DMA mask, and calls `aio_init()`. `set_params` accepts only IEC61937 S/PDIF, initializes a default IEC type, stores params, resets port/SRC, and prepares hardware. Prepare sets DMA channel parameters, ring buffer, port settings, stream type, port enable, and DMA interface settings. Trigger starts/stops ring-buffer DMA under the substream spinlock. Copy transforms 32-bit IEC61937 words into doubled AIO output words for playback, dynamically updates stream type from Pc headers, or copies capture bytes to user space, synchronizing DMA ownership and software offsets.

## Dependencies and Integration
Depends on AIO core helpers, ALSA compressed API, DMA mapping APIs, user-copy helpers, IEC61937 constants, and per-substream state from `aio.h`. SPDIF DAI ops in `aio-cpu.c` hook `snd_soc_new_compress` to use these operations.

## Risks and Test Signals
Risks include leak paths when `aio_init()` fails after DMA allocation, unchecked `dma_unmap_single()` with zero/invalid address if open partially failed, user-copy size assumptions in doubled playback format, stream-type changes during copy, and ring threshold updates racing with IRQ/DMA. Test signals are open/free failure injection, IEC61937 AC3/MP3/DTS/AAC pass-through, pointer monotonicity, wraparound copy, DMA sync correctness, trigger start/stop, unsupported codec rejection, and capture if supported by hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-core.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-core.c

## Purpose
Common UniPhier AIO hardware programming library. It manages ring-buffer arithmetic, SoC glue IEC output, PLL programming, global chip initialization, per-substream mapping, port/SRC/DMA interface setup, digital volume, compressed stream type, DMA channel control, and hardware ring-buffer pointer synchronization.

## APIs, Types, and Functions
Exports many helpers consumed by `aio-cpu.c`, `aio-dma.c`, and `aio-compress.c`: `aio_rb_cnt()`, `aio_rb_space()`, `aio_iecout_set_enable()`, `aio_chip_set_pll()`, `aio_chip_init()`, `aio_init()`, `aio_port_reset()`, `aio_port_set_param()`, `aio_port_set_enable()`, `aio_port_get_volume()`, `aio_port_set_volume()`, `aio_if_set_param()`, `aio_oport_set_stream_type()`, `aio_src_reset()`, `aio_src_set_param()`, `aio_srcif_set_param()`, `aio_srcch_set_param()`, `aio_srcch_set_enable()`, `aiodma_ch_set_param()`, `aiodma_ch_set_enable()`, `aiodma_rb_set_threshold()`, `aiodma_rb_set_buffer()`, `aiodma_rb_sync()`, IRQ test/clear helpers, and internal pointer load/store routines.

## Control Flow, State, and Persistence
Chip init powers audio PLLs, configures external MCLK output, input source selectors, and address-extension mode. Per-substream init writes resource maps for ring buffer, DMA channel, input/output interfaces, ports, and converter paths based on `swm`. PCM port setup validates channels/rates/formats, chooses PLL/divider routing, configures pass-through or PCM validity, and enables port masks. SRC setup handles selected output rates. DMA setup configures channel address modes and ring-buffer start/end/thresholds; ring synchronization reads hardware pointers, updates software offsets, totals, and hardware producer/consumer pointers. Volume state is applied by fade slope/target registers.

## Dependencies and Integration
Depends heavily on `aio-reg.h` register definitions, regmap MMIO, `aio.h` topology/spec structures, ALSA PCM params, bitfield helpers, and IEC61937 type definitions. It is the shared implementation beneath CPU DAI, PCM DMA, and compressed paths.

## Risks and Test Signals
Risks include many `regmap_write/update_bits` return values ignored, ring-buffer arithmetic reserving eight bytes without documenting hardware constraints, pointer-load delay loops using repeated reads instead of timeouts, limited PLL frequencies, defaulting SRC rates to 48 kHz for unsupported rates, volume slope divide behavior at zero sample rate, and complex mapping tables from SoC specs. Test signals are PLL A/F 36.864/33.8688 MHz programming, 2/6/8 channel PCM, I2S/left/right-justified formats, pass-through SPDIF, SRC 32/44.1/48 kHz, volume fade, ring wraparound, IRQ threshold behavior, and LD11/PXs2 address-extension variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-cpu.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-cpu.c

## Purpose
UniPhier AIO ASoC CPU DAI/component driver. It binds SoC-specific DAI specs to common AIO hardware helpers, handles sysclk/PLL/format selection, PCM lifecycle, compressed DAI creation hooks, suspend/resume, mixer volume controls, and platform probe/remove.

## APIs, Types, and Functions
Exports DAI ops tables for LD11 and PXs2 I2S/SPDIF variants, with `*_ops2` enabling compressed streams. Exports `uniphier_aio_probe()` and `uniphier_aio_remove()` for SoC glue drivers. Important helpers are `is_valid_pll()`, `find_volume()`, `find_spec()`, `find_divider()`, `uniphier_aio_set_sysclk()`, `uniphier_aio_set_pll()`, `uniphier_aio_set_fmt()`, PCM startup/shutdown/hw_params/hw_free/prepare, DAI probe/remove and LD11/PXs2 PLL initialization, suspend/resume helpers, and volume get/put.

## Control Flow, State, and Persistence
Platform probe obtains chip spec from OF match data, optional syscon regmap, `aio` clock, shared reset, allocates AIO instances and PLL table copies, initializes per-substream locks and default I2S format, enables clock/reset, registers the component/DAIs, and registers the AIO DMA platform. DAI probe matches substreams to SoC specs by DAI name/group and direction, assigns switch-matrix data, initializes volumes, enables IEC output, initializes chip registers, and marks chip active. PCM startup stores the substream and initializes mapping. `hw_params` supports selected rates, auto-selects an audio PLL divider, stores params, sets volume, and resets port/SRC. Prepare programs port/SRC/interface and converter blocks. Suspend disables clock/reset when active DAIs are quiesced; resume restores chip/substream mapping and resets configured blocks.

## Dependencies and Integration
Depends on `aio.h` SoC specs, AIO core helpers, AIO DMA platform registration, regmap syscon, clk/reset frameworks, OF match data, ASoC component/DAI APIs, and ALSA controls. LD11/PXs2 device drivers provide DAI arrays and specs used here.

## Risks and Test Signals
Risks include `uniphier_aio_vol_put()` returning 0 even after changing volume, resume accumulating bitwise OR of negative return codes, limited `hw_params` rates despite core supporting more FS values, auto-PLL search depending on enabled PLL table, compressed support tied only to specific SPDIF ops tables, and clock/reset reference counting via `num_wup_aios`. Test signals are probe/remove with optional syscon absent/present, I2S and SPDIF DAIs on LD11/PXs2, PLL set_sysclk auto-selection, PCM startup/hw_params/prepare for 32/44.1/48 kHz families, compressed DAI creation, volume controls for all output ports, and suspend/resume with active and inactive DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-cpu.c -->
