# Research group: subset-b-006533

This grouped report covers Qualcomm LPASS and QDSP6 audio source files under `sources/distributed-fs/ceph-client/sound/soc/qcom`. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.h

## Purpose
`lpass-hdmi.h` defines the HDMI/DisplayPort-specific register constants, register address helpers, and regmap-field holder types used by the Qualcomm LPASS CPU/platform drivers. It is a hardware interface header, not an executable driver: its job is to centralize HDMI TX control, stream control, metadata, parity, vbit, channel status, and HDMI DMA field descriptions so SoC variant files can describe the register layout and common code can program it.

## Important APIs, types, and constants
The file exposes bit values such as `LPASS_HDMITX_LEGACY_ENABLE`, `LPASS_DP_AUDIO_BITWIDTH16`, `LPASS_DP_AUDIO_BITWIDTH24`, `LPASS_SSTREAM_ENABLE`, `LPASS_MUTE_ENABLE`, `HW_MODE`, `SW_MODE`, and masks for data format, word length, and frequency. Address helpers such as `LPASS_HDMI_TX_CTL_ADDR(v)`, `LPASS_HDMI_TX_CH_LSB_ADDR(v, port)`, and `LPASS_HDMI_TX_DMA_ADDR(v, port)` read offsets and strides from `struct lpass_variant`.

The key holder structs are `struct lpass_sstream_ctl`, `struct lpass_dp_metadata_ctl`, `struct lpass_hdmi_tx_ctl`, `struct lpass_hdmitx_dmactl`, and `struct lpass_vbit_ctrl`; each stores `struct regmap_field *` members allocated elsewhere. The header also declares `asoc_qcom_lpass_hdmi_dai_ops`, which integrates with SoC DAI driver tables in `lpass-sc7180.c` and `lpass-sc7280.c`.

## Control flow and integration
This header has no direct runtime control flow. Its definitions are consumed by LPASS HDMI DAI operations and by SoC variant tables that populate `struct lpass_variant` HDMI fields. `lpass-platform.c` indirectly depends on these definitions through `lpass.h` when it selects DP/HDMI DMA register maps, enables HDMI DMA fields, and handles HDMI-specific IRQ bits such as metadata done, preload request, and deep-audio disable.

## State and persistence behavior
No state is persisted in the header. The structs describe in-memory regmap-field handles stored in `struct lpass_data`; actual state lives in LPASS registers and in the regmap cache used by the platform driver during suspend/resume.

## Dependencies and integration points
The header depends on Linux `regmap` and on `struct lpass_variant` fields defined in `lpass.h`. It is part of the ASoC LPASS register programming path and integrates with HDMI/DP DAI ops, SC7180/SC7280 variant data, and LPASS platform interrupt/DMA handling.

## Risks and test signals
The main risk is register layout drift: wrong offsets, masks, or field ranges will silently program the wrong HDMI TX block fields. Useful tests include HDMI/DP playback on supported SoCs, suspend/resume playback, channel status validation for 16/24-bit audio, and IRQ traces confirming preload/metadone/deep-audio events are cleared correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-ipq806x.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-ipq806x.c

## Purpose
`lpass-ipq806x.c` is the IPQ806x-specific LPASS CPU DAI platform driver. It supplies the single MI2S DAI definition, IPQ806x register layout, clock bring-up/tear-down, and a simple DMA channel policy to the shared LPASS CPU/platform infrastructure.

## Important APIs, types, and functions
The file defines local enums for IPQ806x I2S ports and DMA channels, then declares `ipq806x_lpass_cpu_dai_driver` with playback-only capability for `IPQ806X_LPAIF_I2S_PORT_MI2S`. Playback supports S16/S24/S32, 8 kHz through 96 kHz selected rates, and 1 to 8 channels.

`ipq806x_lpass_init()` retrieves `ahbix-clk`, sets it to `LPASS_AHBIX_CLOCK_FREQUENCY`, and enables it. `ipq806x_lpass_exit()` disables that clock. `ipq806x_lpass_alloc_dma_channel()` returns the fixed MI2S RDMA channel for playback and rejects capture with `-EINVAL`; `ipq806x_lpass_free_dma_channel()` is a no-op because the allocation is static.

The `ipq806x_data` `struct lpass_variant` is the main integration object. It provides I2S, IRQ, RDMA, WRDMA base offsets/strides, `REG_FIELD_ID` definitions for I2SCTL/RDMA/WRDMA bitfields, DAI clock names, and callbacks consumed by `asoc_qcom_lpass_cpu_platform_probe()` and `asoc_qcom_lpass_platform_register()`.

## Control flow
The platform driver matches `qcom,lpass-cpu`, then delegates probe/remove to the common LPASS CPU platform helpers. During common probe, the variant `init` callback enables the bus clock, the DAI table is registered, and the shared platform component later programs DMA registers according to the variant fields. PCM open asks the variant for a DMA channel; IPQ806x always maps playback to `IPQ806X_LPAIF_RDMA_CHAN_MI2S`.

## State and persistence behavior
Runtime state is minimal and held in common `struct lpass_data`: the `ahbix_clk` pointer and shared DMA/substream arrays. There is no persistent storage. Hardware state is reset/managed through LPASS registers and clock enable state.

## Dependencies and integration points
This file depends on the common LPASS CPU and platform code declared in `lpass.h`, register macros from `lpass-lpaif-reg.h`, Linux clock APIs, platform driver matching, and ASoC DAI registration. It is the IPQ806x provider of `struct lpass_variant`.

## Risks and test signals
The capture path is intentionally unsupported despite WRDMA register fields being present; attempts should fail cleanly. Clock failures abort probe, so board DT clock names must match exactly. Test signals include successful probe with `ahbix-clk`, MI2S playback, expected `-EINVAL` on capture, and period IRQs from the fixed RDMA channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-ipq806x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-lpaif-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-lpaif-reg.h

## Purpose
`lpass-lpaif-reg.h` is the central register-address and bit-value macro header for LPASS Low Power Audio Interface register programming. It abstracts I2S control, IRQ registers, regular RDMA/WRDMA, HDMI RDMA, and CDC DMA register address selection across SoC variants.

## Important APIs and constants
The I2S section defines `LPAIF_I2SCTL_REG(v, port)` and values for loopback, speaker/mic enable, SD-line modes, mono/stereo, word-select source, and bit width. The IRQ section defines host-port IRQ registers and bit encodings: `LPAIF_IRQ_PER(chan)`, `LPAIF_IRQ_XRUN(chan)`, `LPAIF_IRQ_ERR(chan)`, `LPAIF_IRQ_ALL(chan)`, plus HDMI-specific preload/metadone/deep-audio bits.

The DMA section exposes address macros for HDMI RDMA, classic RDMA, WRDMA, and CDC DMA. The high-level macros `LPAIF_DMACTL_REG`, `LPAIF_DMABASE_REG`, `LPAIF_DMABUFF_REG`, `LPAIF_DMACURR_REG`, `LPAIF_DMAPER_REG`, and `LPAIF_DMAPERCNT_REG` choose the correct register family based on stream direction and `is_cdc_dma_port(dai_id)`. It also defines DMA control field values for burst, words-per-sample count, FIFO watermark, enable, and dynamic clock.

## Control flow and integration
The header has no executable flow, but it encodes a large amount of runtime branch behavior through macros. `lpass-platform.c` calls these macros while handling `hw_free`, `prepare`, `trigger`, `pointer`, and IRQ clear/enable paths. SoC variant files provide the base offsets, strides, and channel starts that these macros combine into final register addresses.

## State and persistence behavior
No state is stored here. The macros compute register offsets from immutable variant data and runtime PCM state such as channel, direction, and DAI ID. Persistent hardware state is in LPASS registers and may be cached by regmap during suspend.

## Dependencies and integration points
The macros assume `struct lpass_variant` fields from `lpass.h`, DAI IDs from Qualcomm sound DT bindings, and stream constants such as `SNDRV_PCM_STREAM_PLAYBACK`. They also depend on `is_cdc_dma_port()` and `is_rxtx_cdc_dma_port()` being visible via `lpass.h`.

## Risks and test signals
This header is high blast-radius because a bad macro affects all LPASS DMA paths. Risks include off-by-one channel-start handling for WRDMA/CDC WRDMA, incorrect CDC RXTX versus VA register family selection, and IRQ mask collisions if channel counts exceed the encoded bit stride. Tests should cover playback and capture on MI2S, HDMI/DP playback, CDC RX/TX/VA streams, pointer reporting, xrun/error IRQ handling, and suspend/resume regcache sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-lpaif-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-platform.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-platform.c

## Purpose
`lpass-platform.c` implements the shared ALSA SoC component/platform driver for Qualcomm LPASS PCM DMA. It manages PCM runtime constraints, allocates regmap fields for DMA controls, programs DMA base/buffer/period registers, enables/disables DMA and IRQs, handles LPASS DMA interrupts, preallocates codec-DMA low-power memory buffers, and registers the component for SoC-specific CPU DAI drivers.

## Important APIs, types, and functions
The component driver `lpass_component_driver` exposes standard ASoC component callbacks: `open`, `close`, `hw_params`, `hw_free`, `prepare`, `trigger`, `pointer`, `mmap`, `pcm_new`, `suspend`, `resume`, and `copy`. The exported entry point `asoc_qcom_lpass_platform_register()` wires IRQs, allocates regmap fields, and calls `devm_snd_soc_register_component()`.

The file defines three PCM hardware profiles: default MI2S/DP at 48 KiB, RXTX CDC DMA at 8 KiB, and VA CDC DMA at 12 KiB, all with two periods. Helper allocators create `struct lpaif_dmactl` field bundles for regular DMA, HDMI DMA, RXTX CDC DMA, and VA CDC DMA. Helper selectors `__lpass_get_dmactl_handle()`, `__lpass_get_id()`, and `__lpass_get_regmap_handle()` map a PCM substream's DAI ID and direction to the right regmap and field index.

## Control flow
PCM open allocates `struct lpass_pcm_data`, asks the SoC variant for a DMA channel when available, stores the substream in the relevant IRQ lookup array, resets regular/HDMI DMA control registers, selects hardware constraints, and attaches preallocated codec-DMA buffers where needed. Close clears the substream slot, returns the DMA channel to the variant allocator, and frees private data.

`hw_params` derives bit width and channels, programs burst enable, FIFO watermark, interface selection, and words-per-sample count. The HDMI path additionally programs burst8/burst16/dynburst fields. `prepare` writes DMA base address, buffer size, and period size registers, then enables DMA. `trigger` handles start/resume/pause-release by enabling DMA and IRQ bits, and stop/suspend/pause-push by disabling DMA and updating IRQ masks. `pointer` reads base/current hardware addresses and returns frame offset.

IRQ handlers read the appropriate IRQ status register for regular LPAIF, HDMI, RXTX, or VA. `lpass_dma_interrupt_handler()` clears period, xrun, error, and HDMI sideband bits. Period IRQs call `snd_pcm_period_elapsed()`, xruns call `snd_pcm_stop_xrun()`, and bus errors stop the stream as disconnected.

## State and persistence behavior
Per-stream state lives in `runtime->private_data` as `struct lpass_pcm_data`, while active substreams are indexed in `drvdata->substream`, `hdmi_substream`, `rxtx_substream`, and `va_substream`. DMA allocation state is owned by variant callbacks and bitmaps in `struct lpass_data`. The driver stores no disk state. Hardware state is programmed into LPASS registers. Suspend switches regmaps to cache-only and marks them dirty; resume disables cache-only and syncs the cached register state.

## Dependencies and integration points
The file depends on variant data from `struct lpass_variant`, register macros from `lpass-lpaif-reg.h`, DAI IDs from Qualcomm sound DT bindings, and shared driver state from `lpass.h`. It integrates with SoC-specific drivers such as IPQ806x, SC7180, and SC7280 via `asoc_qcom_lpass_platform_register()` and variant callbacks. It also uses ALSA PCM helpers, regmap/regmap-field APIs, Linux IRQ APIs, and low-power codec DMA memory configured in `struct lpass_data`.

## Risks and test signals
Important risks include channel-index mismatch between DAI IDs and variant channel starts, missing cleanup when `open` fails after allocating a DMA channel, incorrect IRQ mask values on stop for CDC DMA paths, and unchecked `memremap()` failure in codec-DMA preallocation. The switch in `hw_params` includes a suspicious range typo for VA (`LPASS_CDC_DMA_VA_TX0 ... LPASS_CDC_DMA_VA_TX0`) that only matches the first VA TX DAI in that case, though later paths handle the full range. Test signals include PCM playback/capture for each DAI family, xrun and bus-error IRQ injection, suspend/resume with active HDMI and regular streams, mmap/copy on CDC DMA buffers, and checking that DMA bitmaps are released on stream close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7180.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7180.c

## Purpose
`lpass-sc7180.c` provides the SC7180-specific LPASS CPU DAI driver and variant data. It describes the available Primary MI2S, Secondary MI2S, and HDMI/DP playback DAI interfaces, SC7180 register offsets/fields, clock list, PM callbacks, and DMA channel allocation policy.

## Important APIs, types, and functions
`sc7180_lpass_cpu_dai_driver[]` defines three DAIs: Primary MI2S with playback and capture, Secondary MI2S playback, and `LPASS_DP_RX` HDMI playback. The DAI ops are shared LPASS CPU ops or HDMI ops declared in `lpass.h`/`lpass-hdmi.h`.

`sc7180_lpass_alloc_dma_channel()` allocates from either `hdmi_dma_ch_bit_map` for DP playback or `dma_ch_bit_map` for regular RDMA/WRDMA, using `find_first_zero_bit()` for playback and `find_next_zero_bit()` from `wrdma_channel_start` for capture. `sc7180_lpass_free_dma_channel()` clears the corresponding bit. `sc7180_lpass_init()` bulk-gets and enables the variant clock list; `exit`, suspend, and resume disable or re-enable the bulk clocks.

The `sc7180_data` variant table provides register bases/strides, channel counts, I2S and DMA reg fields, HDMI/DP control field addresses, clock names, DAI clock names, and the callback pointers consumed by the common LPASS driver.

## Control flow
On platform match `qcom,sc7180-lpass-cpu`, common LPASS probe receives `sc7180_data`. Initialization allocates `drvdata->clks`, populates IDs from `clk_name`, then enables all clocks. Common PCM open calls the SC7180 allocator to reserve DMA channel bits. Common platform callbacks then use SC7180 register field metadata to program DMA and HDMI blocks. PM suspend/resume gates only the variant clock bulk; regmap cache handling is done in `lpass-platform.c`.

## State and persistence behavior
Runtime state consists of clock handles and DMA channel bitmaps in `struct lpass_data`. No persistent storage is used. The SoC table is static const data. Hardware register state is held by LPASS blocks and regmap caches.

## Dependencies and integration points
The file depends on SC7180 sound DT bindings, common LPASS CPU/platform helpers, HDMI DAI ops, Linux PM macros, bulk clock APIs, and `lpass-lpaif-reg.h` register macros. It is tightly integrated with `lpass-platform.c`, which expects `hdmi_port_enable` and `hdmiif_map` setup from the common CPU probe path when a DP DAI is present.

## Risks and test signals
Risks include mismatched DT clock names, incomplete HDMI field definitions, and DMA bitmap leaks if open/close error paths in shared code mis-handle SC7180 channels. Useful tests include Primary MI2S playback/capture, Secondary playback, DP playback, concurrent stream channel exhaustion returning `-EBUSY`, and system sleep/resume with audio clocks restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7280.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7280.c

## Purpose
`lpass-sc7280.c` is the SC7280 LPASS CPU DAI variant driver. It extends the SC7180-style MI2S/DP support with codec DMA RX, codec DMA TX, and voice-assist DMA capture DAIs, and supplies the register field layout and channel allocation policy needed by the shared LPASS platform component.

## Important APIs, types, and functions
`sc7280_lpass_cpu_dai_driver[]` defines Primary and Secondary MI2S, DP playback, CDC DMA RX playback, CDC DMA TX capture, and CDC DMA VA capture DAIs. CDC DMA DAIs use `asoc_qcom_lpass_cdc_dma_dai_ops`; MI2S and HDMI use the common LPASS CPU/HDMI ops.

`sc7280_lpass_alloc_dma_channel()` dispatches by DAI family: regular MI2S uses `dma_ch_bit_map`, DP uses `hdmi_dma_ch_bit_map`, RXTX CDC uses `rxtx_dma_ch_bit_map`, and VA CDC uses `va_dma_ch_bit_map`. Playback searches from zero for RDMA channels; capture searches from the family-specific WRDMA start. `sc7280_lpass_free_dma_channel()` clears the matching bitmap. Clock initialization and PM mirror SC7180 but with a one-clock `clk_name` array.

The `sc7280_data` variant table defines regular, HDMI, RXTX, and VA IRQ/DMA bases, channel starts/counts, regmap fields for regular and CDC DMA control and codec-interface registers, HDMI metadata/control fields, DAI clock names, and callback pointers.

## Control flow
The platform driver matches `qcom,sc7280-lpass-cpu` and delegates probe/remove/shutdown to common LPASS CPU helpers. During stream open, the shared platform code calls the SC7280 allocator, stores substreams in the right IRQ array, and chooses the correct hardware constraints. During prepare/trigger/IRQ, `lpass-platform.c` uses SC7280's variant fields to program regular, HDMI, RXTX, or VA regmaps.

## State and persistence behavior
SC7280-specific state is held in `struct lpass_data`: clock handles, DMA bitmaps, low-power codec DMA buffer physical addresses, regmaps, and active substream arrays. No disk state is written. PM callbacks gate the variant clocks; component suspend/resume handles regmap cache state.

## Dependencies and integration points
The file depends on SC7180 LPASS DT binding constants for shared IDs, common LPASS infrastructure, codec DMA DAI ops, HDMI DAI ops, and Linux bulk clock/PM APIs. It integrates with `lpass-platform.c` more deeply than SC7180 because codec DMA paths require `rxtx_lpaif_map`, `va_lpaif_map`, codec DMA memory buffers, and CDC DMA IRQ handlers.

## Risks and test signals
One visible risk is that RX CDC DMA allocation finds a free bit but does not call `set_bit()` in the RX case, while free clears the RXTX bitmap for both RX and TX. That can permit duplicate RX channel allocation if multiple RX CDC streams are opened. Other risks include shared register bases between regular and RXTX fields, channel-start arithmetic for WRDMA families, and missing DT memory resources for codec DMA. Tests should include simultaneous CDC RX streams to detect duplicate allocation, WCD playback/capture, DMIC VA capture, DP playback, PM suspend/resume, and IRQ delivery on RXTX/VA maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass.h

## Purpose
`lpass.h` is the shared private header for Qualcomm LPASS ASoC CPU/platform drivers. It defines constants, helper predicates, core state structures, the SoC variant contract, PCM private data, and declarations for the common probe/remove/shutdown, CPU DAI ops, CDC DMA DAI ops, and platform registration entry point.

## Important APIs, types, and functions
`is_cdc_dma_port()` and `is_rxtx_cdc_dma_port()` classify DAI IDs into codec-DMA families. `struct lpaif_i2sctl` and `struct lpaif_dmactl` hold regmap-field pointers for I2S and DMA control registers.

`struct lpass_data` is the central runtime state for the LPASS device: clocks, MI2S SD-line modes, HDMI/codec-DMA enable flags, MMIO bases, regmaps, IRQ numbers, variant pointer, DMA allocation bitmaps, active substream arrays, regmap-field bundles, HDMI field bundles, and codec-DMA low-power memory addresses. `struct lpass_variant` is the SoC-specific contract containing register bases/strides/counts, every reg field used by common code, channel-start offsets, callbacks, DAI tables, and clock lists. `struct lpass_pcm_data` stores per-substream DMA channel and I2S port.

## Control flow and integration
The header does not execute code except inline DAI classifiers. It defines the data contract between SoC files (`lpass-ipq806x.c`, `lpass-sc7180.c`, `lpass-sc7280.c`), common CPU code (not in this work item), common HDMI/CDC DAI ops, and `lpass-platform.c`. SoC probes provide a `struct lpass_variant`; common code fills `struct lpass_data`; platform callbacks consume both.

## State and persistence behavior
All LPASS runtime state is in `struct lpass_data` and per-stream `struct lpass_pcm_data`. The fields are kernel-memory state only and are destroyed with the platform device. Register persistence across PM uses regmap cache behavior in the platform component, not storage declared here.

## Dependencies and integration points
The header includes Linux clock/platform/regmap APIs, Qualcomm sound DT bindings, Q6AFE binding IDs, `common.h`, and HDMI definitions. It is included by most LPASS source files and is therefore sensitive to type changes.

## Risks and test signals
Risks include ABI-like coupling: adding or changing `struct lpass_variant` fields requires all variants and common code to stay aligned. The DMA substream array sizes also need to match channel counts used by variants. Tests should cover all variant probes, all DAI ID classifiers, regular/HDMI/CDC stream open/close, and build coverage for all enabled LPASS SoC drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/Makefile

## Purpose
The QDSP6 `Makefile` declares how Qualcomm DSP audio support objects are built under Kconfig control. It groups common DSP helpers and AudioReach APM support into composite modules and maps each QDSP6 feature config symbol to the corresponding object.

## Important build APIs and objects
`snd-q6dsp-common-y` links `q6dsp-common.o`, `q6dsp-lpass-ports.o`, and `q6dsp-lpass-clocks.o`. `snd-q6apm-y` links `q6apm.o`, `audioreach.o`, and `topology.o`. Individual `obj-$(CONFIG_...)` lines include Q6 core, AFE, AFE DAI, AFE clocks, ADM, routing, ASM, ASM DAI, APM, APM DAI, APM LPASS DAI, PRM, PRM LPASS clocks, and USB support.

## Control flow and integration
There is no runtime flow, but build-time dependency flow matters. Enabling `CONFIG_SND_SOC_QDSP6_APM` pulls in `audioreach.o` through `snd-q6apm.o`. Enabling `CONFIG_SND_SOC_QDSP6_AFE_DAI` builds `q6afe-dai.o`; enabling `CONFIG_SND_SOC_QDSP6_AFE_CLOCKS` builds `q6afe-clocks.o`; enabling `CONFIG_SND_SOC_QDSP6_ADM` builds `q6adm.o`.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the kernel build graph selected by Kconfig.

## Dependencies and integration points
The Makefile integrates with Linux kbuild and the QDSP6 Kconfig symbols. It defines whether the source files researched in this item are compiled into the kernel for a given configuration.

## Risks and test signals
Risks are missing object dependencies or incorrect composite grouping, which would surface as unresolved symbols or absent drivers at runtime. Test signals include allmodconfig or targeted QDSP6 build coverage, module load availability for AFE/ADM/APM paths, and checking that AudioReach symbols resolve when `CONFIG_SND_SOC_QDSP6_APM` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.c

## Purpose
`audioreach.c` implements helper routines for Qualcomm AudioReach/APM graph and module control over GPR. It allocates packets, builds graph-open payloads from topology data, sends synchronous commands, programs module media formats, configures shared-memory endpoints, sets gain/volume and module enable parameters, and sends EOS for shared-memory playback.

## Important APIs, types, and functions
Packet allocation helpers include `audioreach_alloc_pkt()`, `audioreach_alloc_apm_pkt()`, `audioreach_alloc_cmd_pkt()`, and `audioreach_alloc_apm_cmd_pkt()`, all backed by `__audioreach_alloc_pkt()`. `audioreach_alloc_graph_pkt()` constructs an `APM_CMD_GRAPH_OPEN` payload containing subgraph config, container config, module list, module properties, and module connections.

Synchronous command APIs are `audioreach_send_cmd_sync()` and `audioreach_graph_send_cmd_sync()`. Module/media-format APIs include `audioreach_set_media_format()`, `audioreach_compr_set_param()`, `audioreach_send_u32_param()`, `audioreach_gain_set_vol_ctrl()`, `audioreach_shared_memory_send_eos()`, and `audioreach_graph_free_buf()`. Static helpers handle I2S, DisplayPort, codec DMA, shared memory, PCM/MFC, compressed formats, data logging, SAL, gapless, gain, and speaker-protection modules.

## Control flow
Graph-open construction first counts subgraphs, containers, modules, and connections, computes aligned payload sizes, allocates an APM command packet, lays out each parameter block in sequence, and calls `audioreach_populate_graph()` to fill module/connection objects from topology lists. Command sending serializes through a mutex, clears the result state, sends via either a GPR device or GPR port, waits up to five seconds for the expected opcode or response opcode, and maps timeout/DSP errors to Linux errors.

`audioreach_set_media_format()` dispatches on `module->module_id`. Hardware endpoints receive HW media format plus interface/frame-size/power config. PCM-like modules receive PCM output format configs. Shared-memory endpoints receive `PARAM_ID_MEDIA_FORMAT` or compressed media format packets. Some modules require sequencing, such as enabling data logging after config, enabling SAL limiter after output config, or enabling speaker-protection modules after mode configuration.

## State and persistence behavior
Most state is transient packet memory allocated with `kzalloc()` and freed through `__free(kfree)` cleanup or explicit `kfree()`. Command completion state is stored in `graph->result`, `graph->lock`, and `graph->cmd_wait`, or in caller-provided result/lock/wait structures. `audioreach_graph_free_buf()` persists stream buffer state changes by clearing `rx_data` and `tx_data` buffer pointers and period counts under the graph lock. No disk state is written.

## Dependencies and integration points
The file depends on GPR/APR packet definitions, `q6apm` graph and port APIs, AudioReach ABI constants/types from `audioreach.h`, ALSA codec and PCM params, and topology-provided `audioreach_graph_info` lists. It is built into `snd-q6apm` and is used by APM DAI/topology paths to translate ALSA/topology parameters into DSP commands.

## Risks and test signals
Risks include payload size miscalculation for variable-length channel maps, incomplete channel mapping for more than four channels in helper defaults, timeout handling if callbacks race or return a different opcode, and inconsistent ownership because most packet paths use cleanup attributes but speaker-protection VI manually frees. Compressed format setup uses a base payload size that may not include codec-specific payload lengths, so codec validation is important. Tests should include graph open for multi-container topologies, media-format setup for PCM/I2S/DP/codec-DMA/shared-memory/compressed paths, timeout/error injection, EOS delivery, and KASAN/KMSAN coverage for variable-size payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.h

## Purpose
`audioreach.h` defines the AudioReach/APM ABI constants, packed command payload structures, topology graph structs, module configuration structs, and function prototypes used by `audioreach.c` and other QDSP6 APM code. It is the contract layer between Linux ASoC topology/DAI code and Qualcomm DSP graph commands.

## Important APIs, types, and constants
The header lists AudioReach module IDs for shared memory, gain, PCM enc/dec/cnv, I2S, SAL, MFC, logging, codec DMA, MP3/AAC/FLAC/OPUS, DisplayPort, and speaker protection. It defines APM graph commands, shared-memory map/unmap commands, data buffer commands, EOS commands, media-format IDs, data formats, channel/PCM constants, and many `PARAM_ID_*` values.

Packed structs cover shared memory map/unmap, buffer done responses, PCM/compressed media formats, APM command headers, module parameter blocks, subgraph/container/module graph config, I2S/DP/HW endpoint configs, logging, speaker protection, SAL, MFC, codec DMA, clock config, volume, and placeholder real-module IDs. Runtime topology structs include `audioreach_graph_info`, `audioreach_sub_graph`, `audioreach_container`, `audioreach_module`, and `audioreach_module_config`.

Public functions include packet allocators, `audioreach_alloc_graph_pkt()`, `audioreach_tplg_init()`, command send helpers, `audioreach_set_media_format()`, EOS, gain/volume, u32 param setting, compressed parameter setup, and graph buffer freeing.

## Control flow and integration
The header itself has no flow. Its types are consumed by topology parsing, graph open construction, APM DAI configuration, and GPR command submission. The list-based graph structs establish the traversal model used in `audioreach_alloc_graph_pkt()`: graph info owns subgraphs, subgraphs own containers, and containers own modules.

## State and persistence behavior
The ABI structs are packed to match DSP wire format and should not gain implicit padding. Runtime graph structs use kernel lists and pointers to connect parsed topology state to ALSA widgets and module private data. No persistent storage exists, but structure layout is effectively persistent as a DSP ABI.

## Dependencies and integration points
The header depends on Linux types, APR/GPR types, ALSA SoC and codec UAPI types, and `snd_ar_tokens.h`. It is integrated with `q6apm`, topology parsing, APM DAI paths, and DSP firmware command handling.

## Risks and test signals
Risks include duplicate or inconsistent defines, ABI packing mistakes, flexible-array size errors, and parameter ID drift against DSP firmware. Test signals include successful topology parsing, graph open on real firmware, media-format programming for every supported module ID, compressed codec playback, and build checks for packed structure layout warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.c

## Purpose
`q6adm.c` implements the Qualcomm QDSP6 Audio Device Manager driver over APR. It opens and closes COPP objects for AFE ports, reuses matching COPPs through refcounts, maps ASM sessions to COPPs through ADM matrix routing, handles APR responses, and populates child devices under the ADM node.

## Important APIs, types, and functions
Internal state is represented by `struct q6adm` and `struct q6copp`. `q6adm` stores the APR device, service info, per-AFE-port COPP bitmaps, the active COPP list, locking, and matrix-map wait state. `q6copp` stores AFE port, COPP index, DSP COPP ID, topology/mode/rate/bit-width/channel/app metadata, response state, wait queue, kref, and list node.

Exported APIs are `q6adm_open()`, `q6adm_get_copp_id()`, `q6adm_matrix_map()`, and `q6adm_close()`. Important internal functions include `q6adm_alloc_copp()`, `q6adm_find_copp()`, `q6adm_find_matching_copp()`, `q6adm_device_open()`, `q6adm_device_close()`, `q6adm_apr_send_copp_pkt()`, `q6adm_callback()`, and `q6adm_free_copp()`.

## Control flow
Probe allocates `struct q6adm`, records service info, initializes locks/waits/list state, and populates child platform devices. `q6adm_open()` validates the port, searches for an existing matching COPP, or allocates a new COPP index under the list spinlock. It initializes metadata and sends `ADM_CMD_DEVICE_OPEN_V5`; the APR callback records the returned COPP ID and wakes the per-COPP wait queue.

`q6adm_matrix_map()` builds an `ADM_CMD_MATRIX_MAP_ROUTINGS_V5` packet containing one session node and the DSP COPP IDs found from the route payload. It sends the packet under `adm->lock` and waits for `ADM_CMD_MATRIX_MAP_ROUTINGS_V5` completion on `matrix_map_wait`. `q6adm_close()` drops the kref; final release sends device close, clears the COPP bitmap, removes the list node, and frees memory.

## State and persistence behavior
State is in kernel memory only: COPP bitmaps, active list, krefs, response fields, and wait queues. A COPP persists while references exist and is closed on final kref release. DSP-side state persists until ADM close succeeds or the DSP resets. No disk state is used.

## Dependencies and integration points
The driver depends on APR, Q6 core service info, Q6AFE port ID translation, Q6DSP channel mapping, Q6DSP errno values, and ASoC/QDSP6 routing/ASM layers that call ADM APIs. It registers as an APR driver matching `qcom,q6adm` and populates OF children for consumers.

## Risks and test signals
Risks include list traversal in callbacks without taking `copps_list_lock`, possible duplicate matching COPP selection if multiple compatible COPPs exist, and returning `0` from `q6adm_matrix_map()` on an invalid path after logging but without failing immediately. Error paths rely on kref release to close and free partially opened COPPs. Test signals include open/close refcount reuse, invalid port rejection, route mapping for playback and live record, APR timeout/error injection, concurrent opens/closes, and DSP reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.h

## Purpose
`q6adm.h` is the public internal header for the QDSP6 Audio Device Manager API. It provides path/topology constants, route payload shape, the opaque `struct q6copp` declaration, and prototypes for ADM open, close, COPP ID lookup, and matrix mapping.

## Important APIs and types
Constants include `ADM_PATH_PLAYBACK`, `ADM_PATH_LIVE_REC`, `MAX_COPPS_PER_PORT`, and `NULL_COPP_TOPOLOGY`. `struct route_payload` carries one session ID, the number of COPPs, and parallel arrays of COPP indexes and AFE port IDs. Function prototypes mirror the exported symbols in `q6adm.c`: `q6adm_open()`, `q6adm_close()`, `q6adm_get_copp_id()`, and `q6adm_matrix_map()`.

## Control flow and integration
The header has no control flow. It is included by QDSP6 routing/ASM code that needs to open ADM COPPs and map sessions. The opaque COPP pointer enforces that consumers use ADM APIs rather than directly mutating COPP internals.

## State and persistence behavior
State is represented indirectly through `struct q6copp *` handles returned by `q6adm_open()`. Callers are responsible for balancing `q6adm_close()` calls so the kref in `q6adm.c` can close DSP resources.

## Dependencies and integration points
The header relies on Linux device types and `uint16_t` availability through including C files. It is part of the QDSP6 audio control-plane API and integrates with APR-based ADM implementation.

## Risks and test signals
Risks include callers overfilling `route_payload` beyond `MAX_COPPS_PER_PORT`, not balancing open/close, or using a COPP index after close. Test signals include route payload validation in callers, build coverage for all consumers, and runtime route setup/teardown during PCM start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-clocks.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-clocks.c

## Purpose
`q6afe-clocks.c` exposes Q6AFE LPASS clocks and core hardware votes as Linux clocks through the common Q6DSP clock provider. It translates clock framework operations into Q6AFE DSP clock set/vote/unvote commands.

## Important APIs, types, and functions
The `Q6AFE_CLK(id)` macro creates `struct q6dsp_clk_init` entries with Linux-facing clock IDs, Q6AFE DSP clock IDs, names, and a default 19.2 MHz rate. `q6afe_clks[]` enumerates MI2S, PCM, TDM, MCLK, codec core, WSA, VA, TX, RX, and vote clocks. `q6dsp_clk_q6afe` binds the table to `q6afe_set_lpass_clock()`, `q6afe_vote_lpass_core_hw()`, and `q6afe_unvote_lpass_core_hw()`.

## Control flow
The platform driver matches `qcom,q6afe-clocks` and calls the shared `q6dsp_clock_dev_probe()` with the descriptor from OF match data. From then on, clock framework consumers interact with clocks registered by the common provider, which calls back into Q6AFE helpers for DSP-side clock control.

## State and persistence behavior
This file has static const clock descriptors only. Runtime clock state is managed by the common Q6DSP clock provider and DSP firmware. No disk state is used.

## Dependencies and integration points
The driver depends on Q6AFE clock IDs from DT bindings, `q6dsp-lpass-clocks.h`, and Q6AFE clock/vote functions from `q6afe.h`. It integrates with device-tree clock providers and consumers such as QDSP6 AFE DAI or machine drivers that request LPASS clocks.

## Risks and test signals
Risks include missing clock IDs, incorrect default rates, or wrong vote block IDs, causing audio interfaces to fail only when a specific bus/codec clock is needed. Test signals include DT clock lookup, enable/disable traces for MI2S/TDM/codec clocks, vote/unvote balance, and allmodconfig build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-clocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-dai.c

## Purpose
`q6afe-dai.c` implements the ASoC DAI component for QDSP6 Audio Front End ports. It exposes HDMI/DP, Slimbus, MI2S, TDM, codec DMA, and USB AFE ports as DAIs, translates ALSA hw_params and DAI ops into `q6afe_port_config`, starts/stops DSP AFE ports, registers DAPM widgets/routes, and parses OF per-port configuration.

## Important APIs, types, and functions
`struct q6afe_dai_data` stores one `q6afe_port *`, one `q6afe_port_config`, a started flag, and private config for each AFE port ID. `struct q6afe_dai_priv_data` stores MI2S/TDM-specific DT settings such as SD-line mask, sync mode/source, data output, invert sync, data delay, and data alignment.

Parameter functions include `q6slim_hw_params()`, `q6hdmi_hw_params()`, `q6afe_usb_hw_params()`, `q6i2s_hw_params()`, `q6tdm_hw_params()`, and `q6dma_hw_params()`. Configuration ops include `q6i2s_set_fmt()`, `q6tdm_set_tdm_slot()`, `q6tdm_set_channel_map()`, `q6dma_set_channel_map()`, `q6slim_set_channel_map()`, and `q6afe_mi2s_set_sysclk()`. Runtime control is handled by `msm_dai_q6_dai_probe()`, `msm_dai_q6_dai_remove()`, `q6afe_dai_prepare()`, and `q6afe_dai_shutdown()`.

## Control flow
Probe allocates `q6afe_dai_data`, parses child OF nodes for per-port MI2S/TDM properties, builds DAI drivers through `q6dsp_audio_ports_set_config()`, and registers the ASoC component with DAPM widgets/routes. Each DAI probe obtains a `q6afe_port` by ID. ALSA `hw_params` fills the appropriate union member in `port_config`. DAI-specific ops fill channel maps, TDM slot masks, sysclk settings, or I2S format.

On `prepare`, if the port is already started it is first stopped so new config can be applied. The function then dispatches by DAI ID to HDMI, Slimbus, I2S, TDM, codec DMA, or USB prepare helpers and starts the port with `q6afe_port_start()`. Shutdown stops an active port and clears the started flag.

## State and persistence behavior
Runtime state is per platform device in `q6afe_dai_data`. `is_port_started[]` prevents redundant stops and allows reprepare with changed config. Port handles are acquired on DAI probe and released on DAI remove. OF-derived private settings persist for the lifetime of the device. No disk state is written; DSP AFE state persists until stop or DSP reset.

## Dependencies and integration points
The file depends on Q6AFE port APIs, common Q6DSP audio-port DAI generation, channel allocation helpers, Qualcomm Q6AFE DT bindings, ALSA ASoC component/DAI/DAPM APIs, and OF child node parsing. It integrates with machine drivers through DAPM routes and with DSP firmware through `q6afe_port_prepare/start/stop`.

## Risks and test signals
Risks include array indexing by raw DAI ID up to `AFE_PORT_MAX`, incomplete validation for unsupported formats, OF child-node ref leaks in `for_each_child_of_node()` error paths, and not stopping ports when prepare partially succeeds then start fails. TDM and codec DMA channel maps need careful validation because masks and slot arrays differ by direction. Tests should cover each DAI family, repeated prepare with changed params, shutdown without prepare, invalid TDM slot widths/slot counts, channel-map bounds, sysclk IDs, OF parsing for MI2S/TDM properties, and DAPM route visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe-dai.c -->
