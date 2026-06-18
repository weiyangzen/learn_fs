# sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-pcm-dma.h

Purpose: shared Spreadtrum PCM/compress header. It defines the PCM DMA parameter contract that CPU DAIs provide to the platform driver, and the DSP compressed-offload callback/operation contract consumed by `sprd-pcm-compress.c`.

Important APIs and types: `SPRD_PCM_CHANNEL_MAX` caps PCM DMA at two hardware channels. `struct sprd_pcm_dma_params` supplies per-channel device FIFO physical addresses, data widths, fragment lengths, and dmaengine channel names. `struct sprd_compr_playinfo` is the DSP-visible progress block with total/current time, data length, and current data offset. `struct sprd_compr_params` packages direction, bit/sample rate, channels, format, period layout, and DSP info-buffer location. `struct sprd_compr_callback` carries a drain notification hook. `struct sprd_compr_ops` abstracts firmware-side stream lifecycle and parameter operations. `struct sprd_compr_data` groups ops and DMA params as DAI driver data.

Control flow and integration: PCM code retrieves `sprd_pcm_dma_params` with `snd_soc_dai_get_dma_data()`. Compressed code retrieves `sprd_compr_data` with `snd_soc_dai_get_drvdata()`, then uses `ops` for DSP lifecycle and `dma_params` for two-stage DMA routing. The external symbol `sprd_platform_compress_ops` is attached to the Spreadtrum component driver.

State and persistence: this header does not own state directly, but it defines state copied between AP, DMA engine, and DSP firmware. `sprd_compr_playinfo` is shared through DMA/IRAM memory and therefore must remain layout-stable for firmware.

Dependencies: Linux DMA address types and ALSA compressed ops declarations are expected through includers. The contract assumes Spreadtrum DMA can address the supplied physical FIFOs and memory blocks.

Risks: no versioning or size negotiation exists for the DSP-facing structures. `info_phys` is `u32`, so systems with physical addresses above 4 GiB need constraints or truncation protection. `fragment_len` and `datawidth` are trusted by the platform driver; invalid DAI data can misprogram DMA bursts. The compressed ops use `int str_id`, with current users passing stream direction as the ID, which couples firmware stream numbering to ALSA constants.

Test signals: compile both PCM and compress objects with this header, inspect structure sizes against firmware ABI expectations, test >32-bit DMA address configurations, and validate each DAI supplies two channel names/addresses before compressed playback is opened.
