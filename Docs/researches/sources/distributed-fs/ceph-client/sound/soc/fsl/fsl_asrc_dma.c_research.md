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
