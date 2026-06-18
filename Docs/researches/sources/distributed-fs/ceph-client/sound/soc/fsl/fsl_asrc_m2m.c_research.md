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
