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
