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
