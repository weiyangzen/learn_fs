# Research: subset-b-006505

Grouped research for Freescale/NXP ASoC source files under `sources/distributed-fs/ceph-client/sound/soc/fsl`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl-asoc-card.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl-asoc-card.c

## Purpose
`fsl-asoc-card.c` is the generic Freescale i.MX ASoC machine-card driver for boards that connect an SSI/ESAI/SAI/SPDIF CPU DAI to one or two codecs, optionally through an ASRC DPCM front-end/back-end path. It converts Device Tree board descriptions into `snd_soc_card`, `snd_soc_dai_link`, DAPM routes/widgets, jack detection, AUDMUX wiring, codec clock/PLL setup, and ASRC backend rate/format constraints.

## Important APIs, Types, and Functions
- `struct codec_priv` stores per-codec MCLK, free-running fallback frequency, MCLK/FLL/PLL IDs used with `snd_soc_dai_set_sysclk()` and `snd_soc_dai_set_pll()`.
- `struct cpu_priv` stores CPU DAI sysclk IDs, directions, static rates, sample-rate ratios, and optional TDM slot shape.
- `struct fsl_asoc_card_priv` is card state: three DAI links, jacks, CPU/codec private data, current stream mask, current sample rate/format, ASRC backend rate/format, DAI format, and generated card name.
- `fsl_asoc_card_hw_params()` records active stream parameters, sets CPU sysclk/TDM slots, and starts codec PLL/FLL paths when a codec profile declares PLL and FLL IDs.
- `fsl_asoc_card_hw_free()` clears the active stream bit and, when the last stream stops, switches codecs back to MCLK/free frequency and stops FLL/PLL.
- `be_hw_params_fixup()` forces ASRC backend DPCM parameters to the ASRC output rate and format parsed from the ASRC node.
- `fsl_asoc_card_audmux_init()` programs i.MX AUDMUX port routing based on CPU/codec clock-provider format or AC97 mode.
- `fsl_asoc_card_spdif_init()` handles new and legacy SPDIF bindings, including dummy codec fallback and playback/capture-only route pruning.
- `fsl_asoc_card_late_probe()` applies codec sysclk after card registration and handles an AC97 S/PDIF slot quirk.
- `fsl_asoc_card_probe()` is the main DT parser and card constructor.

## Control Flow
Probe allocates private state, resolves `audio-cpu` or legacy CPU phandles, looks up up to two codecs, optionally resolves `audio-asrc`, samples codec MCLK rates, and initializes three predeclared links: normal link, ASRC FE, and ASRC BE. It then selects a board-specific profile from the machine compatible string, filling codec DAI names, DAI format, PLL/FLL IDs, stream direction limits, TDM width, CPU sysclk direction/ratio, and DAPM route variants.

After profile selection, DT can override `mclk-id` and DAI clock provider/format. CPU-specific setup configures AUDMUX for SSI, reads ESAI `extal` clock and IDs, or sets SAI master clock IDs. The card is named from `model` or a fallback, routes/widgets are attached, ASRC-only route halves are dropped when no ASRC node exists, and `audio-routing` can replace/extend routing via standard ASoC parsing.

Normal link components are bound to CPU and codec nodes. AC97 uses `cell-index` to synthesize an `ac97-codec.N` component name. When ASRC is present, links 1 and 2 are enabled as FE/BE DPCM links, codec components are copied to the BE link, and ASRC fixed output rate/format are read from `fsl,asrc-rate` plus `fsl,asrc-format` or legacy `fsl,asrc-width`.

Runtime `hw_params` sets CPU and codec clocks per stream. Runtime `hw_free` tears down shared codec FLL/PLL only when no streams remain. Jack setup happens after `devm_snd_soc_register_card()` and registers notifiers to disable speaker on headphone insertion and DMIC on analog mic insertion.

## State and Persistence
All state is kernel runtime state owned by the platform device and ASoC card. `priv->streams` is a bitmask protecting shared PLL teardown while playback/capture overlap. `sample_rate` and `sample_format` are updated from the latest stream and used for PLL ratios. `asrc_rate` and `asrc_format` persist from DT and feed DPCM backend fixups. No disk persistence exists.

Device Tree is the persistent configuration source. The driver consumes both current and legacy properties: `audio-cpu`, `ssi-controller`, `spdif-controller`, `audio-codec`, `audio-asrc`, `mclk-id`, `model`, `audio-routing`, `mux-int-port`, `mux-ext-port`, old SPDIF booleans, and deprecated GPIO names.

## Dependencies and Integration Points
The driver integrates with ASoC core card/link/component APIs, simple-card jack helpers, codec-specific clock IDs from several codec headers, CPU DAI definitions from FSL ESAI/SAI, i.MX AUDMUX, AC97 support when enabled, and the ASRC DAI exposed by `fsl_asrc.c`. DPCM integration depends on the ASRC platform exposing FE CPU/platform DAIs and on `fsl_asrc_dma.c` providing the component DMA operations.

## Risks and Edge Cases
- The profile table hard-codes many board/codec assumptions; new compatibles must fill all clock, format, and route details correctly.
- `codec_dai_name[]` and `codec_dev_name[]` are profile-dependent and can be uninitialized if a branch fails to assign names for all active codec slots.
- The stream bitmask is not locked; ASoC serializes most runtime callbacks, but concurrent open/close behavior should still be considered when modifying clock teardown.
- PLL output ratios are fixed at 256x or 384x depending on S24_LE only, which may not match every codec or packed 24-bit variant.
- AUDMUX setup is sensitive to master/slave interpretation and legacy AC97 special casing.
- ASRC route pruning assumes ASRC routes remain in the second half of each route array.
- SPDIF old-binding dummy-codec handling intentionally suppresses DAPM routes; changes can break old device trees.

## Test Signals
- Probe succeeds for each compatible string with representative DTs, including one/two-codec SPDIF, AC97, SSI AUDMUX, ESAI, SAI, and ASRC/non-ASRC variants.
- `aplay`/`arecord` exercise `hw_params`, `trigger`, and `hw_free` for playback-only, capture-only, and duplex profiles without clock errors.
- ASRC DPCM playback/capture reports BE parameters fixed to `fsl,asrc-rate` and `fsl,asrc-format`.
- Jack GPIO insertion toggles DAPM pins `Ext Spk` and `DMIC` as expected.
- Runtime logs lack `failed to set sysclk`, `failed to start FLL`, `failed to init audmux`, and probe defer loops after dependencies bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl-asoc-card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.c

## Purpose
`fsl_asrc.c` is the core Freescale/NXP ASRC DAI driver. It owns ASRC register programming, pair allocation, sample-rate conversion configuration, clock-source selection, interrupt error accounting, runtime/system power management, SoC variant data, and the callback table used by the DMA and M2M frontends.

## Important APIs, Types, and Functions
- Supported rates are listed in `supported_asrc_rate[]` and exposed as an ALSA hardware constraint.
- Clock map tables translate public `enum asrc_inclk`/`enum asrc_outclk` values into hardware ASRCSR fields for i.MX35, i.MX53, i.MX8QM, i.MX8QXP, and i.MX952 variants.
- `fsl_asrc_request_pair()` and `fsl_asrc_release_pair()` allocate/free ASRC pairs and channel capacity under `asrc->lock`.
- `fsl_asrc_config_pair()` validates channels, formats, rates, ratio limits, clock divisibility, word widths, and writes the ASRC pair registers.
- `fsl_asrc_select_clk()` chooses internal-ratio clocks with exact divisors or falls back to ideal-ratio mode.
- `fsl_asrc_start_pair()` and `fsl_asrc_stop_pair()` enable/disable a pair and prime the input FIFO.
- DAI callbacks `startup`, `hw_params`, `hw_free`, `trigger`, and `probe` integrate conversion with ALSA PCM.
- Regmap callbacks describe readable, writable, and volatile registers plus defaults.
- `fsl_asrc_init()` writes recommended parameter registers, task FIFO base, and 76 kHz/56 kHz period registers from `ipg_clk`.
- `fsl_asrc_isr()` clears overload status and records per-pair task/FIFO errors.
- M2M helpers implement `m2m_prepare`, `m2m_start`, `m2m_stop`, output readiness, output-length calculation, maxburst selection, capabilities, and resume priming.
- `fsl_asrc_probe()` wires platform resources, clocks, regmap, IRQ, DT properties, SoC data, callbacks, runtime PM, ASoC DAI registration, and M2M registration.

## Control Flow
Probe maps MMIO, initializes regmap, requests IRQ, obtains `mem`, `ipg`, optional `spba`, and all sixteen `asrck_N` clocks, then reads SoC match data. It fills shared `struct fsl_asrc` callbacks for DMA and M2M users, picks the appropriate clock map from compatible string plus `fsl,asrc-clk-map` where required, reads default ASRC backend rate/format from DT, enables runtime PM, resumes the device to initialize registers, then registers the ASoC component/DAI and the compressed M2M card.

PCM startup constrains rates and older 3-bit-channel hardware to even channel counts. PCM `hw_params` requests a pair for the stream channel count, fills an `asrc_config` according to playback or capture direction, selects clocks, and programs the pair. Playback converts user input rate/format to fixed ASRC output rate/format; capture reverses that relationship. Trigger starts/stops the pair; `hw_free` releases the pair.

Pair configuration chooses word widths from ALSA formats, validates rates against the supported table and low-output-rate ratio range, maps clock IDs, checks dividers, writes channel count, ratio mode, clock sources, clock divisors, word width, buffer stall, FIFO watermarks, and optionally ideal ratio preprocessing/postprocessing plus fixed-point ratio registers.

Runtime resume enables clocks, temporarily disables all pairs, restores regmap cache, reapplies cached `REG_ASRCFG` fields, restarts previously enabled pairs, and waits for initialization status. Runtime suspend snapshots `REG_ASRCFG`, switches regmap to cache-only, and disables clocks. System suspend/resume wraps runtime PM and calls M2M suspend/resume helpers.

## State and Persistence
Persistent hardware state is represented in regmap cache across runtime suspend. `asrc_priv->regcache_cfg` keeps `REG_ASRCFG` fields that regcache alone does not safely restore. `asrc->pair[]`, `channel_avail`, and each `fsl_asrc_pair` contain live allocation and error state. `asrc->asrc_rate` and `asrc->asrc_format` are DT-derived defaults for ASoC BE conversion. No filesystem persistence is used.

`pair_priv->config` points to a stack `struct asrc_config` during `hw_params`/M2M prepare, so it must not be dereferenced after the configuration function returns. The current code confines use to synchronous configuration.

## Dependencies and Integration Points
This file depends on ALSA SoC DAI/component APIs, DMAengine PCM metadata, regmap MMIO, runtime PM, common ASRC structures from `fsl_asrc_common.h`, ASRC register definitions from `fsl_asrc.h`, and exported component/M2M functions in `fsl_asrc_dma.c` and `fsl_asrc_m2m.c`. It integrates with machine drivers through the DAI stream names `ASRC-Playback` and `ASRC-Capture` and with DT compatibles for SoC-specific behavior.

## Risks and Edge Cases
- `fsl_asrc_dai_hw_params()` requests a pair before full validation; if `fsl_asrc_config_pair()` fails, the function returns without releasing the pair, so error-path changes should be audited.
- Clock map entries can map many unsupported public clock IDs to fallback hardware values; invalid DT or future enum additions can silently choose undesirable clocks.
- Ideal ratio mode avoids exact divider requirements but changes conversion speed and uses `IDEAL_RATIO_RATE` for fast M2M conversions, which can overload hardware.
- Initialization timeouts are warnings, not hard failures, so conversion may continue with latent hardware readiness issues.
- Interrupt handling clears overload broadly and logs at debug level; test setups must inspect `pair->error` or debug logs to see quality issues.
- Runtime resume restarts pairs based on cached ASRCTR state; concurrent stream shutdown around suspend/resume should be treated carefully.
- `fsl_asrc_m2m_calc_out_len()` subtracts `ASRC_OUTPUT_LAST_SAMPLE`; small conversions can underflow if callers do not validate minimum input length.

## Test Signals
- Probe on each compatible verifies all clocks and `fsl,asrc-clk-map` variants bind.
- PCM playback/capture with all supported rates and S8/S16/S24 formats validates constraints, pair allocation, dividers, and DMA integration.
- Runtime suspend/resume during active conversion checks regcache restore and pair restart.
- M2M compressed tasks with varied rates/formats validate ideal-ratio configuration, DMA completion, final FIFO drain, and output-size reporting.
- Error injection or overload stress should update `pair->error` without interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.h

## Purpose
`fsl_asrc.h` is the hardware-specific ASRC register and private-data header. It defines FIFO thresholds, buffer constants, register offsets, bitfield macros, input/output clock enums, word-width encodings, configuration structures, error flags, DMA block metadata, SoC data, and private ASRC driver state consumed primarily by `fsl_asrc.c`.

## Important APIs, Types, and Definitions
- FIFO and buffer constants include `ASRC_M2M_INPUTFIFO_WML`, `ASRC_M2M_OUTPUTFIFO_WML`, `ASRC_INPUTFIFO_THRESHOLD`, `ASRC_FIFO_THRESHOLD_MIN/MAX`, `ASRC_DMA_BUFFER_SIZE`, `ASRC_MAX_BUFFER_SIZE`, and `ASRC_OUTPUT_LAST_SAMPLE`.
- Register offsets cover control, interrupt, channel-count, config, clock-source, divider, status, ratio, FIFO data, ideal-ratio, 76K/56K, machine-control, FIFO-status, and word-format registers.
- Macros such as `ASRCTR_ASRCE(i)`, `ASRCNCR_ANCi()`, `ASRCFG_PREMOD()`, `ASRCSR_AICS()`, `ASRCDRi_AICP()`, `ASRSTR_AIDU()`, `ASRMCRi_INFIFO_THRESHOLD()`, and `ASRFSTi_OUTPUT_FIFO_FILL()` encode/decode hardware fields.
- `enum asrc_inclk` and `enum asrc_outclk` expose logical clock selections for legacy and i.MX8-era clocks.
- `struct asrc_config` is the pair configuration passed into the core configurator.
- `struct fsl_asrc_soc_data` communicates SoC quirks: eDMA usage, channel-count bit width, and ASRC-before-DMA start ordering.
- `struct fsl_asrc_pair_priv` currently stores a pointer to the active configuration.
- `struct fsl_asrc_priv` stores the ASRCK clock array, SoC data, input/output clock maps, and the cached `REG_ASRCFG` value.

## Control Flow and Usage
The header itself has no control flow; it shapes the code generated in `fsl_asrc.c`. The driver builds register addresses with index macros such as `REG_ASRDI(i)`, `REG_ASRDO(i)`, `REG_ASRIDRH(i)`, and `REG_ASRMCR(i)` so pair A/B/C programming can share code. Public clock enums are translated through per-SoC `clk_map` arrays before being written to `ASRCSR`.

## State and Persistence
The persistent state represented by this header is hardware register state plus runtime private structures. `struct fsl_asrc_priv` is allocated once per platform device and keeps clock-map and regcache metadata across operations. `struct asrc_config` is a transient programming description, not a durable copy unless a caller owns its lifetime.

## Dependencies and Integration Points
It includes `fsl_asrc_common.h` for common pair and device structures. It relies on ALSA PCM format types and kernel DMA address types being available through includers. Its macros must match the ASRC reference manual and are consumed by `fsl_asrc.c` and indirectly by M2M/DMA callbacks.

## Risks and Edge Cases
- Many macros do not fully mask input values before shifting, so callers must pass already valid field-width values.
- `ASRCFG_INIRQi` and similar macros use an `i` identifier in the expansion form; incorrect usage can produce compile errors or misleading code.
- Public clock enums have sparse values up to `ASRC_CLK_MAP_LEN`; out-of-range enum values would index clock maps unsafely if validation is not added by callers.
- Buffer-size constants are shared assumptions between core and M2M; changing them requires auditing DMA buffer allocation, output-length calculations, and FIFO draining.

## Test Signals
- Compile coverage is the main test for macro shape.
- Register dumps during known-rate conversions should show expected bitfields from the macros.
- Static analysis should verify all clock enum values used by DT/bindings remain below `ASRC_CLK_MAP_LEN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_common.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_common.h

## Purpose
`fsl_asrc_common.h` defines common ASRC structures and function declarations shared by the ASRC core, PCM DMA component, and compressed memory-to-memory driver. It is the cross-file contract that lets `fsl_asrc.c` provide hardware callbacks while `fsl_asrc_dma.c` and `fsl_asrc_m2m.c` implement ALSA data movement frontends.

## Important APIs, Types, and Definitions
- Direction constants `IN` and `OUT` index all two-element arrays for input/output resources.
- `enum asrc_pair_index` identifies ASRC pair contexts A through D, with this hardware using A/B/C and `PAIR_CTX_NUM` allowing four slots.
- `struct fsl_asrc_m2m_cap` reports supported compressed-M2M input/output formats, channel range, and rate arrays.
- `struct fsl_asrc_pair` stores per-conversion context: parent ASRC pointer, error flags, pair index, channel count, DMA descriptors/channels, imx DMA metadata, PCM pointer position, private extension memory, completions, M2M formats/rates/buffer lengths, DMA buffers, first-convert flag, and optional ratio modifier state.
- `struct fsl_asrc` stores shared device state: DMAengine DAI metadata, platform device, regmap, physical base, clocks, M2M ALSA card, pair table, channel availability, fixed ASRC BE rate/format, SoC flags, callback table, pair private size, and hardware-private pointer.
- Export declarations cover `fsl_asrc_component` and M2M init/exit/suspend/resume.

## Control Flow and Usage
The ASRC core initializes `struct fsl_asrc` and populates callbacks. The DMA component allocates `struct fsl_asrc_pair` instances during PCM open/new, asks the core to request/release pair slots, and uses callbacks for FIFO addresses and DMA channel selection. The M2M driver allocates pairs per compressed stream, uses the same callbacks for pair configuration/start/stop, and owns DMA-buffer export and task execution.

## State and Persistence
All structures are volatile kernel runtime state. The central stateful fields are `asrc->pair[]` and `channel_avail`, protected by the core spinlock during allocation/release, plus per-pair DMA descriptors, completions, and error flags. No state persists beyond driver lifetime except what is represented by hardware registers and regmap cache in the core.

## Dependencies and Integration Points
The header depends on ALSA DMAengine structures, compressed/M2M users, DMAengine descriptors/channels, imx DMA data, completions, regmap, clocks, and platform devices supplied by included kernel headers in the C files. It is included by all ASRC implementation files and forms the ABI between the ASRC component and the M2M driver inside the kernel tree.

## Risks and Edge Cases
- The common structures expose many fields directly, so ownership rules must be respected by all users; for example, DMA channels may be reused or released depending on `req_dma_chan`.
- `PAIR_CTX_NUM` includes D while core allocation iterates only up to `ASRC_PAIR_MAX_NUM` from `fsl_asrc.h`; cross-header changes can desynchronize capacity.
- Callback pointers are optional in places; M2M code checks some but not all callbacks before use.
- Direction indexes are plain integers, so IN/OUT inversion mistakes compile cleanly and can swap DMA/FIFO semantics.

## Test Signals
- Build all three ASRC objects together to catch signature drift.
- Run PCM DPCM and compressed M2M paths in one boot to verify common pair allocation and release remain coherent.
- Suspend/resume with M2M pairs verifies shared pair table iteration and callback expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_dma.c

## Purpose
`fsl_asrc_dma.c` is the ASoC PCM component for ASRC DPCM streams. It allocates per-stream ASRC pair context, refines PCM hardware constraints, configures a front-end DMA channel between memory and ASRC FIFO, configures a back-end DMA channel between ASRC FIFO and the real audio peripheral, submits cyclic transfers, reports PCM pointer progress, and exports `fsl_asrc_component` for registration by the ASRC core.

## Important APIs, Types, and Functions
- `snd_imx_hardware` declares ASRC DMA PCM capabilities: mmap/interleaved/block transfer, 256 KiB buffer, period constraints, and SDMA-limited period maximum.
- `filter()` selects general-purpose imx DMA channels and attaches `imx_dma_data`.
- `fsl_asrc_dma_complete()` updates `pair->pos` by one period and calls `snd_pcm_period_elapsed()`.
- `fsl_asrc_dma_prepare_and_submit()` builds cyclic descriptors for FE memory transfer and BE device-to-device transfer.
- `fsl_asrc_dma_trigger()` prepares/issues DMA on start-like triggers and terminates both channels on stop-like triggers.
- `fsl_asrc_dma_hw_params()` discovers the BE DAI/DMA data from DPCM, requests/configures FE and BE DMA channels, handles SDMA vs eDMA differences, sets bus widths, and programs device-to-device addresses.
- `fsl_asrc_dma_startup()` allocates pair private state, temporarily requests a pair and DMA channel to refine runtime hardware, and sets runtime private data.
- `fsl_asrc_dma_shutdown()`, `fsl_asrc_dma_hw_free()`, and `fsl_asrc_dma_pcm_new()` release channels/context and preallocate fixed buffers.

## Control Flow
On PCM open, a `struct fsl_asrc_pair` plus core-private extension is allocated. A dummy one-channel pair and DMA channel are requested only to learn DMA constraints, then released before returning with runtime hardware set. On `hw_params`, the real channel count has already been requested by the ASRC DAI `hw_params`; this component configures DMA resources for the selected pair.

The FE channel direction is opposite the user stream direction because playback writes memory to ASRC input FIFO and capture reads ASRC output FIFO to memory. The BE channel direction follows the hardware peripheral side and is configured as `DMA_DEV_TO_DEV`. For SDMA, the code extracts DMA request numbers from a temporary BE channel and a temporary ASRC-side channel, then requests a general-purpose channel through `__dma_request_channel()`. For eDMA, it directly uses or requests the BE channel because fixed event routing makes a separate request pair unnecessary.

Trigger start prepares both descriptors, issues input and output channels, and relies on the ASRC DAI trigger to start/stop the pair. Trigger stop terminates both DMA channels asynchronously. Pointer reporting is software-maintained by the FE cyclic callback rather than reading hardware position.

## State and Persistence
Per-stream state lives in `runtime->private_data` as `struct fsl_asrc_pair`. It stores DMA channels, descriptors, software position, channel-release ownership, and core private data. `pair->req_dma_chan` records whether the BE/dev-to-dev channel must be released. No persistent storage exists.

## Dependencies and Integration Points
The component is exported as `fsl_asrc_component` and registered by `fsl_asrc.c`. It depends on DPCM relationships from the machine card, CPU/codec DAI `dma_data`, ASRC core callbacks (`get_dma_channel`, `get_fifo_addr`, pair allocation), imx SDMA metadata, DMAengine cyclic/device-to-device support, and ALSA component PCM operations.

## Risks and Edge Cases
- Several error paths after channel requests return without releasing earlier channels; changes should audit cleanup symmetry.
- The BE cyclic descriptor uses dummy address/size values (`0xffff`, `64`) for device-to-device preparation; this relies on slave configuration and DMA controller behavior.
- Reusing a BE channel from an existing DMAengine PCM component depends on component lookup and stream slot state.
- FE software pointer advances only on callbacks; no-period-wakeup or DMA callback suppression can affect pointer accuracy.
- `startup()` manually clears `asrc->pair[pair->index]` later in shutdown if still matching, after a dummy release; this area is sensitive to pair allocation lifecycle changes.
- SDMA-specific private-data extraction assumes requested channels expose `struct imx_dma_data`.

## Test Signals
- DPCM playback/capture through ASRC with SDMA and eDMA SoCs verifies both DMA setup branches.
- `aplay`/`arecord` with multiple period sizes validates cyclic callbacks and pointer wrapping.
- Stop/pause/resume loops should not leak DMA channels or leave ASRC pair slots allocated.
- Audio graph card backend with dummy CPU DAI should still resolve the real hardware DAI for DMA data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_m2m.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_m2m.c

## Purpose
`fsl_asrc_m2m.c` exposes the ASRC as an ALSA compressed offload memory-to-memory PCM sample-rate converter. It allocates DMA buffers, exports them as dma-bufs for task IO, validates PCM conversion parameters, configures ASRC pair/DMA channels per task, runs input/output DMA transfers, drains the final ASRC FIFO samples, and registers a standalone compressed card named `ASRC-M2M`.

## Important APIs, Types, and Functions
- `ASRC_M2M_BUFFER_SIZE` and `ASRC_M2M_PERIOD_SIZE` define maximum task buffer and scatter-gather segment sizes.
- `asrc_input_dma_callback()` and `asrc_output_dma_callback()` complete per-direction DMA completions.
- `asrc_read_last_fifo()` drains residual output FIFO samples into the output DMA buffer after DMA completion.
- `asrc_dmaconfig()` configures one DMA channel, builds a temporary scatterlist over the DMA buffer, prepares an interrupting slave-SG descriptor, and attaches the direction callback.
- `asrc_m2m_device_run()` is the main conversion routine invoked by compressed task start.
- Compressed operations implement open, free, set_params, get_caps, get_codec_caps, task_create, task_start, task_stop, and task_free.
- dma-buf ops implement mmap, map, unmap, and release wrappers over ALSA DMA buffers.
- `fsl_asrc_m2m_suspend()` and `fsl_asrc_m2m_resume()` handle active task completions and pair resume priming.
- `fsl_asrc_m2m_init()` and `fsl_asrc_m2m_exit()` create/free the compressed sound card.

## Control Flow
Open allocates a pair context, initializes completions, allocates input and output DMA pages, and runtime-resumes the ASRC device. `set_params` validates input/output PCM formats against ASRC core capabilities, checks input/output rates against supported tables, requires equal input/output channels within range, and stores formats, rates, channel count, and fragment sizes in the pair.

Task creation exports both DMA buffers as dma-bufs, requests an ASRC pair with the chosen channel count, calls the core M2M prepare callback, then requests input and output ASRC DMA channels. Task start calls `asrc_m2m_device_run()`: optionally applies ratio modifier, validates input size, configures IN DMA from memory to ASRC input FIFO, computes output DMA length from input length and rates, configures OUT DMA from ASRC output FIFO to memory, starts ASRC before or after DMA depending on SoC data, waits up to 10 seconds for DMA completions, drains final FIFO data, and reports `task->output_size`.

Task free stops/unprepares the ASRC pair, releases the pair and DMA channels. Stream release drops runtime PM, frees DMA pages, and frees pair memory. Suspend terminates incomplete DMA operations, manually completes waiters, and calls optional pair suspend. Resume calls optional pair resume on all live pairs.

## State and Persistence
Per compressed stream state lives in `runtime->private_data`. Per task state includes exported dma-bufs referencing `pair->dma_buffer[IN/OUT]`, pair allocation, DMA channels, descriptors, completions, rates, formats, and `first_convert`. No data is persisted beyond stream lifetime; userspace-visible buffers are DMA allocations exported for the stream.

## Dependencies and Integration Points
The M2M layer depends on ASRC core callbacks for capabilities, pair management, configuration, start/stop, FIFO address/size, maxburst, output readiness, output length, and resume behavior. It uses ALSA compressed offload task APIs, DMAengine slave-SG APIs, dma-buf export/attachment APIs, ALSA DMA-buffer mmap helpers, runtime PM, and SoC-specific start ordering from `fsl_asrc.c`.

## Risks and Edge Cases
- If output dma-buf export fails after input export, the input dma-buf is not explicitly released in that error path.
- `asrc_m2m_device_run()` does not terminate DMA descriptors on timeout before returning, relying on later task free/suspend cleanup.
- `asrc_read_last_fifo()` pointer arithmetic uses `void *` extension semantics and must match kernel compiler assumptions.
- Output length calculation occurs in the core and subtracts last-sample compensation; small buffers and extreme ratios need validation.
- `fsl_asrc_m2m_get_caps()` reports fixed 4096 fragment size while buffers are much larger; userspace must follow task sizing semantics.
- `fsl_asrc_m2m_map_dma_buf()` should avoid leaking partially initialized sg tables on `dma_get_sgtable()`/`dma_map_sgtable()` failures.

## Test Signals
- Compressed M2M conversion tasks at each supported rate pair and S16/S24/S8/S24_3LE format combination validate param checks and output sizes.
- Timeout tests should show clean task teardown and no DMA channel leaks.
- dma-buf mmap/map/unmap from userspace or an attaching device verifies exported buffer semantics.
- Suspend/resume during a running task should complete waiters, stop DMA, and allow later tasks after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_m2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.c

## Purpose
`fsl_aud2htx.c` is the NXP AUD2HTX ASoC CPU DAI driver for routing audio data into HDMI transmit hardware. It provides a playback-only DAI, configures FIFO watermarks and DMA parameters, controls enable/DMA-enable bits on trigger, manages regmap cache and bus clock runtime PM, and registers a DMAengine PCM platform.

## Important APIs, Types, and Functions
- `fsl_aud2htx_trigger()` enables/disables the AUD2HTX block and DMA request generation on PCM trigger commands.
- `fsl_aud2htx_dai_probe()` configures DMA request threshold, masks interrupts, sets low/high watermarks, and attaches TX/RX DMA data to the DAI.
- `fsl_aud2htx_dai` exposes playback stream `CPU-Playback`, 1-8 channels, common HDMI audio rates from 32 kHz through 192 kHz, and formats from `FSL_AUD2HTX_FORMATS`.
- Regmap callbacks define readable, writable, volatile registers and defaults.
- `fsl_aud2htx_probe()` maps registers, initializes regmap, requests IRQ, obtains `bus` clock, sets TX DMA address/name/maxburst, enables runtime PM, registers DMAengine PCM, and registers the component/DAI.
- Runtime suspend/resume toggles regcache cache-only and the bus clock.

## Control Flow
Probe allocates private state, maps MMIO, initializes a MAPLE regmap, registers a placeholder IRQ handler, obtains the bus clock, initializes TX DMA parameters pointing at `AUD2HTX_WR`, sets drvdata, enables runtime PM, puts regmap into cache-only mode, and registers the platform and DAI. DAI probe then writes hardware defaults through regmap when the DAI is instantiated. Trigger start sets `AUD2HTX_CTRL_EN` and `AUD2HTX_CTRE_DE`; stop clears DMA enable then block enable.

Runtime resume enables the bus clock and syncs regmap cache to hardware; runtime suspend switches regmap cache-only and disables the clock. System sleep delegates to runtime PM force helpers.

## State and Persistence
Driver state is `struct fsl_aud2htx` with platform device, regmap, bus clock, and DMAengine DAI metadata. Register values persist logically through regmap cache across runtime suspend. There is no on-disk persistence.

## Dependencies and Integration Points
The driver depends on ASoC DAI/component APIs, DMAengine PCM registration, runtime PM, regmap MMIO, a DT compatible `fsl,imx8mp-aud2htx`, a `bus` clock, an IRQ resource, and a DMA channel named `tx`. Machine cards or graph cards connect its `CPU-Playback` stream to downstream HDMI/audio paths.

## Risks and Edge Cases
- The IRQ handler always returns handled and does not inspect or clear interrupt status; interrupts are masked by default, so enabling them later requires real handling.
- `dma_params_rx` is initialized into the DAI despite the DAI being playback-only and RX fields not being populated.
- Register writes in DAI probe depend on runtime PM/regcache behavior; if the device is not resumed by ASoC around probe, writes may remain cached until resume.
- Error paths disable runtime PM but do not need explicit regmap cleanup due to devm resources.

## Test Signals
- Probe and runtime resume should show no clock/regmap errors.
- Playback through HDMI should trigger enable bits, generate DMA requests below the low watermark, and stop cleanly.
- Runtime suspend/resume followed by playback validates regcache restore of watermark and mask configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.h

## Purpose
`fsl_aud2htx.h` defines the AUD2HTX register map, bitfields, FIFO/DMA constants, supported audio formats, and private driver state used by `fsl_aud2htx.c`.

## Important APIs, Types, and Definitions
- `FSL_AUD2HTX_FORMATS` allows S24_LE, S32_LE, and IEC958 subframe little-endian playback.
- Register offsets cover control, extended control, write FIFO register, status, nonmasked IRQ flags, masked IRQ flags, and IRQ masks.
- Bit macros define block enable, DMA enable, DMA threshold selector, low/high watermark fields, and interrupt mask bits.
- FIFO constants set depth and both watermarks to 0x10, with DMA maxburst 0x10.
- `struct fsl_aud2htx` contains platform device, regmap, bus clock, and DMAengine DAI metadata.

## Control Flow and Usage
The header has no direct control flow. The C file uses register and field macros to initialize regmap, configure watermarks/interrupt masks, toggle trigger enable bits, and fill DMA parameters for writes to `AUD2HTX_WR`.

## State and Persistence
State is represented by hardware registers and the private structure. Regmap cache in the C file preserves register settings across runtime suspend.

## Dependencies and Integration Points
It assumes includers provide ASoC/DMAengine, regmap, clk, and platform-device type definitions. The format mask and DMA constants are part of the driver contract exposed through the DAI and DMAengine PCM registration.

## Risks and Edge Cases
- Field macros use raw shifts and masks; callers must pass values within hardware width.
- Watermark constants equal half FIFO depth; changing them affects DMA request behavior and underrun/overrun margin.
- The private struct contains RX DMA metadata although current DAI support is playback-only.

## Test Signals
- Compile-time use catches missing type includes from C files.
- Register write traces should show expected low/high watermark fields and IRQ mask bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_audmix.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_audmix.c

## Purpose
`fsl_audmix.c` is the NXP AUDMIX ASoC DAI driver. It exposes two playback TDM inputs and one capture mixed output, provides mixer/attenuation ALSA controls, enforces safe output-source and mix-clock state transitions based on started TDM streams, configures DSP_A DAI format polarity, tracks active TDM playback DAIs, manages regmap/cache/runtime PM, and optionally spawns an `imx-audmix` card device for legacy-style DTs.

## Important APIs, Types, and Functions
- Enum tables define user controls for TDM selection, output source mode, output width, enable/disable, attenuation direction, and error masks.
- `struct fsl_audmix_state` and the `prms[4][4]` matrix encode allowed state transitions and required active TDMs/clock changes.
- `fsl_audmix_state_trans()` checks active TDM requirements and prepares control-register updates.
- `fsl_audmix_put_mix_clk_src()` validates that both the current and requested clock sources are backed by started TDMs before changing clock source.
- `fsl_audmix_put_out_src()` validates output-source transitions and updates `FSL_AUDMIX_CTR`.
- `fsl_audmix_snd_controls[]` exposes mixer routing, output width, error masks, sync mode, and per-TDM attenuation controls.
- `fsl_audmix_dai_set_fmt()` accepts DSP_A plus provider/consumer combinations and maps clock inversion to output clock polarity.
- `fsl_audmix_dai_trigger()` tracks active playback TDM DAIs in `priv->tdms`.
- The DAI array exposes `audmix-0`, `audmix-1` playback inputs and `audmix-2` capture output, all fixed at 8 channels.

## Control Flow
Probe maps AUDMIX registers, creates a flat regmap with defaults, obtains the `ipg` clock, initializes the lock, enables runtime PM, and registers the component with three DAIs. If the DT node has a `dais` property, it also registers an `imx-audmix` platform device; otherwise an audio graph card is expected to connect the DAIs.

At runtime, playback trigger start sets the bit for the DAI ID in `priv->tdms`; stop clears it. Capture triggers are ignored because the active-source constraints are tied to playback inputs. Userspace control writes for output source and clock source read the current control register, check active TDM bits, optionally adjust mix clock, and then update the hardware register. DAI format configuration validates DSP_A and clock-provider flags and writes output clock polarity.

Runtime resume enables `ipg_clk`, switches regmap out of cache-only mode, marks cache dirty, and syncs registers. Runtime suspend switches regmap cache-only and disables the clock. System sleep uses runtime PM force helpers.

## State and Persistence
`priv->tdms` is the key runtime state tracking which playback TDMs are active; it is protected by `priv->lock` in trigger paths but read by control paths without taking that lock. Register state persists through regmap cache during runtime suspend. Optional child platform device state persists until remove.

## Dependencies and Integration Points
The driver depends on ASoC component/DAI/control APIs, regmap MMIO, runtime PM, `ipg` clock, DT compatibles `fsl,imx8qm-audmix` and `fsl,imx952-audmix`, and either audio graph card wiring or the spawned `imx-audmix` card driver. ALSA controls are the primary userspace integration surface for mixer routing and attenuation.

## Risks and Edge Cases
- Control callbacks read `priv->tdms` locklessly while triggers update it under spinlock, creating a small race in concurrent control/trigger operations.
- Transition constraints rely on the hard-coded `prms` matrix; new modes or semantics require careful matrix updates.
- DAI IDs are used as bit positions; adding/reordering DAIs can break `tdms` semantics.
- The driver accepts both `BC_FC` and `BP_FP` clock-provider cases but rejects other valid-looking combinations; graph card format settings must match.
- Optional child platform registration must be removed exactly once; current remove handles `priv->pdev`.

## Test Signals
- ALSA control changes for output source and clock source should fail when required TDM streams are not running and succeed when they are.
- Start/stop both playback TDMs and capture mixed output while toggling controls to validate transition matrix behavior.
- Runtime suspend/resume should preserve control settings through regcache.
- DTs with and without `dais` property validate both child-card and audio-graph integration modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_audmix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_audmix.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_audmix.h

## Purpose
`fsl_audmix.h` defines AUDMIX-supported formats, register offsets, control/status/attenuation bitfields, maximum DAI count, and the private `struct fsl_audmix` used by the AUDMIX DAI driver.

## Important APIs, Types, and Definitions
- `FSL_AUDMIX_FORMATS` supports S16_LE, S24_LE, and S32_LE.
- Register offsets cover the main control/status registers and two full sets of attenuation control/value/step registers.
- Control macros encode mix clock source, output source, output width, output clock polarity, rate/clock diff error masks, sync mode, and sync source.
- Status macros expose rate diff, clock diff, and mix state fields.
- Attenuation macros define enable, direction, step divider, initial value, step-up/down factors, target, current value, and step count masks.
- `struct fsl_audmix` stores optional child platform device, regmap, IPG clock, spinlock, and active TDM bitmask.

## Control Flow and Usage
The header has no executable flow. `fsl_audmix.c` uses the macros to create ALSA controls, implement control writes, set DAI format polarity, initialize regmap defaults, and manage active TDM state.

## State and Persistence
The active `tdms` bitmask is volatile driver state. Register values are cached and restored by the C file's regmap runtime-PM handling. Hardware attenuation state is represented through the defined registers.

## Dependencies and Integration Points
It assumes includers provide platform device, regmap, clk, and spinlock types. The register constants and format mask are the shared contract between the driver, ALSA controls, and the AUDMIX hardware reference.

## Risks and Edge Cases
- `FSL_AUDMIX_MAX_DAIS` is 2 while the C file registers three DAIs; because the macro is not used there, this mismatch is currently harmless but can mislead future code.
- Some masks use fixed widths and raw shifts; caller range validation is required.
- `FSL_AUDMIX_STR_MIXSTAT(i)` macro masks before shifting in a way that expects `i` to already be a register value.

## Test Signals
- Compile all AUDMIX control definitions after macro changes.
- Register dumps from control writes should match expected `FSL_AUDMIX_CTR_*` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_audmix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.c

## Purpose
`fsl_dma.c` is the legacy Freescale Elo DMA ASoC PCM component for MPC/Freescale SSI audio. It implements fixed-buffer PCM DMA using the platform's CCSR DMA channel registers, two reusable link descriptors in chaining mode, SSI FIFO-aware bandwidth programming, interrupt-driven period completion, and DT discovery from SSI nodes that reference DMA channel nodes.

## Important APIs, Types, and Functions
- `struct dma_object` is per-platform-channel state containing the component driver, SSI STX/SRX physical addresses, SSI FIFO depth, mapped DMA channel registers, IRQ, and assignment flag.
- `struct fsl_dma_private` is per-open-substream state with two link descriptors, channel registers, IRQ, substream, SSI data register address, link-descriptor buffer physical address, current link index, DMA buffer addresses, period size, and period count.
- `fsl_dma_hardware` describes PCM capabilities, broad format support, mmap/interleaved/joint-duplex/pause flags, period limits, and 128 KiB fixed buffer.
- `fsl_dma_isr()` handles DMA status bits, stops on transmit/programming errors, reports period elapsed on end-of-segment, updates link descriptors, and clears handled bits.
- `fsl_dma_update_pointers()` rotates one of the two link descriptors to the next period when the number of ALSA periods exceeds the descriptor count.
- `fsl_dma_new()` sets a 36-bit coherent DMA mask and allocates fixed PCM buffers.
- `fsl_dma_open()` allocates coherent private/link memory, requests IRQ, initializes ringed link descriptor `next` pointers, sets mode register for external master start/pause, interrupts, and source/destination hold.
- `fsl_dma_hw_params()` programs sample-size-dependent SSI register offsets, transfer size, bandwidth count, period descriptors, and snoop attributes.
- `fsl_dma_pointer()` reads SAR/DAR to compute the ALSA hardware pointer and detects out-of-range positions.
- `find_ssi_node()` scans compatible SSI nodes to find one whose playback/capture DMA phandle points at this DMA node.
- `fsl_soc_dma_probe()` builds and registers the component driver for compatible `fsl,ssi-dma-channel`.

## Control Flow
Probe finds the SSI node that references the DMA channel, reads SSI MMIO resource and FIFO depth, allocates `dma_object`, fills component callbacks, computes SSI STX0/SRX0 physical addresses, registers the component, maps DMA channel registers, parses IRQ, and stores drvdata.

PCM new coerces the card DMA mask to 36 bits and allocates the fixed DMA buffer. PCM open rejects non-integer periods, enforces one stream per DMA channel with `assigned`, allocates coherent `fsl_dma_private` and descriptors, requests IRQ, links the two descriptors in a ring, writes current link descriptor address registers, clears BCR, and programs DMA mode for external SSI master control plus interrupts. Playback holds destination address; capture holds source address.

`hw_params` computes sample width and period layout, adjusts SSI register address for big-endian sub-word writes, rejects unsupported packed widths, sets DMA transfer sizes, computes bandwidth count from FIFO depth and sample bytes, and initializes each descriptor for either memory-to-SSI playback or SSI-to-memory capture with appropriate snoop attributes. ISR period completions call ALSA and rotate descriptors for buffers with more periods than links. `hw_free` aborts/reset registers; close frees IRQ and coherent private memory.

## State and Persistence
Per-device state persists in `dma_object` while the platform device is bound. Per-stream state is coherent DMA memory so the hardware can read link descriptors. Hardware register state is explicitly programmed/reset on open/hw_params/hw_free. No regmap or runtime PM is used, and no disk persistence exists.

## Dependencies and Integration Points
The driver integrates with ALSA SoC component PCM callbacks, Freescale SSI register offsets from `fsl_ssi.h`, CCSR DMA register definitions from `fsl_dma.h`, OF address/IRQ/phandle helpers, big-endian MMIO accessors, DMA coherent allocation, and SSI DT properties `fsl,playback-dma`, `fsl,capture-dma`, and `fsl,fifo-depth`.

## Risks and Edge Cases
- The driver scans all `fsl,mpc8610-ssi` nodes because DT lacks a reverse DMA-to-SSI link; this is fragile for unusual DT topologies.
- `assigned` is not protected by a lock; concurrent opens on the same channel depend on higher-level serialization.
- Packed 24-bit formats are advertised in `FSLDMA_PCM_FORMATS`, but `hw_params` only accepts 8/16/32 physical widths; packed 24-bit support can fail at runtime.
- Big-endian SSI register offset logic is hardware-specific and easy to break when changing formats.
- `CCSR_DMA_MR_BWC()` uses `ilog2(x)`; invalid or zero FIFO-derived values would be problematic.
- Probe maps registers and IRQ after component registration; failures after registration are not explicitly handled.

## Test Signals
- Playback/capture on MPC SSI should produce regular EOS interrupts and period elapsed callbacks.
- Runtime `hw_params` for 8/16/32-bit samples validates SSI register offset and transfer-size programming; packed 24-bit should be checked for expected rejection.
- Error injection for DMA transmit/programming errors should stop the stream with XRUN.
- Pointer readings must stay within the fixed buffer and wrap at buffer end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.h

## Purpose
`fsl_dma.h` defines the CCSR/Elo DMA register layout, mode/status/attribute bitfields, address helper macros, and packed/aligned list and link descriptor formats used by the Freescale SSI DMA PCM driver.

## Important APIs, Types, and Definitions
- `struct ccsr_dma` and nested `struct ccsr_dma_channel` model the memory-mapped DMA controller and per-channel registers.
- Mode register macros define bandwidth count, external master pause/start, transfer sizes, address hold enable, snoop/read-write flags, interrupt enables, channel abort, chaining mode, and start bits.
- Status register macros define transmit error, channel halt, programming error, end-of-link/list, channel busy, and end-of-segment conditions.
- `CCSR_DMA_ECLNDAR_ADDR()` and `CCSR_DMA_CLNDAR_ADDR()` split link descriptor addresses for current/extended registers.
- Attribute macros define platform/bus attributes, no-snoop/snoop encodings, and extended source/destination address bits.
- `struct fsl_dma_list_descriptor` and `struct fsl_dma_link_descriptor` describe 32-byte aligned hardware descriptors for chaining.

## Control Flow and Usage
The header has no executable flow. `fsl_dma.c` uses the register layout with big-endian MMIO accessors, writes mode/status/address registers, and fills link descriptors in coherent memory. Helper macros convert physical addresses and field values to the hardware's expected register fields.

## State and Persistence
State represented here is hardware register state and coherent descriptor memory. Descriptor structures are owned by the PCM runtime and consumed by the DMA controller until stream close/hw_free.

## Dependencies and Integration Points
The header depends on kernel integer and endian types. It is tightly coupled to the CCSR DMA controller manual and the `fsl_dma.c` PCM implementation. Descriptor alignment/packing is part of the hardware ABI.

## Risks and Edge Cases
- Field macros assume valid inputs; for example `CCSR_DMA_MR_BWC(x)` calls `ilog2(x)` and expects a positive bandwidth count.
- Descriptor structures must remain exactly aligned and packed; compiler or manual layout changes would break DMA hardware reads.
- 36-bit address support depends on upper bits being written consistently in register and descriptor attributes.
- Status and mode constants are raw bit values with no type safety.

## Test Signals
- Build and sparse/endian checks should validate big-endian field usage.
- Hardware descriptor dumps during playback/capture should show correct ring pointers, counts, snoop attributes, and extended address bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.h -->
