# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dmaengine.c

## Purpose
This file adapts the generic IIO DMA buffer queue to Linux DMAengine channels, providing a reusable hardware IIO buffer for devices with DMAengine-connected converter ports.

## Important APIs, Types, And Functions
`struct dmaengine_buffer` wraps an `iio_dma_buffer_queue`, DMA channel, active block list, transfer alignment, and max segment size. `iio_dmaengine_buffer_submit_block()` prepares either a `dma_vec` transfer for scatter-gather dma-bufs or a slave single transfer for coherent file I/O blocks. `iio_dmaengine_buffer_block_done()` removes active blocks, subtracts residue, and completes the generic block. Exported setup APIs include `iio_dmaengine_buffer_setup_ext()`, `devm_iio_dmaengine_buffer_setup_ext()`, `devm_iio_dmaengine_buffer_setup_with_handle()`, and `iio_dmaengine_buffer_teardown()`.

## Control Flow
Setup requests or accepts a DMA channel, allocates a DMAengine buffer, marks the IIO device as hardware-buffer capable, sets the buffer direction, and attaches it. On queue submission, the code chooses device-to-memory or memory-to-device direction, prepares a descriptor, installs a completion callback, submits the descriptor, records the block on the active list, and issues pending DMA. Disable calls `dmaengine_terminate_sync()` and aborts active blocks.

## State And Persistence
State is volatile: active DMA blocks, channel pointer, alignment, max size, and generic queue state. The `length_align_bytes` sysfs attribute exposes minimum transfer alignment inferred from DMA slave capabilities.

## Dependencies And Integration Points
It depends on DMAengine, scatterlist DMA addresses, IIO DMA buffer namespace, IIO buffer core, and optional devm cleanup. It imports the `IIO_DMA_BUFFER` namespace and exports `IIO_DMAENGINE_BUFFER` symbols.

## Risks
Alignment and max segment handling are central: zero or overlarge `bytes_used` is rejected for fileio. SG paths allocate `dma_vec` with `GFP_ATOMIC`; memory pressure can fail submissions. The code assumes SG entries are already DMA-mapped by the dma-buf attachment path. Active-list manipulation must pair with completion and abort to avoid list corruption.

## Test Signals
Exercise DMA slave capability variations, both input and output directions, residue accounting, abort paths, devm setup teardown, external channel handles, SG dma-buf enqueue, and `length_align_bytes` ABI.
