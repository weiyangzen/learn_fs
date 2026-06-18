# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-dma.c

## Purpose
`industrialio-buffer-dma.c` is the generic DMA-backed IIO buffer queue implementation. It manages DMA blocks, file I/O double-buffering, imported dma-bufs, buffer enable/disable, polling wakeups, and block lifetime.

## Important APIs, Types, And Functions
The file operates on `struct iio_dma_buffer_queue` and `struct iio_dma_buffer_block` from public IIO DMA headers. Exported APIs include `iio_dma_buffer_block_done()`, `iio_dma_buffer_block_list_abort()`, `iio_dma_buffer_request_update()`, `iio_dma_buffer_enable()`, `iio_dma_buffer_disable()`, file read/write callbacks, dma-buf attach/detach/enqueue, queue lock/unlock helpers, datum/length setters, `iio_dma_buffer_init()`, `iio_dma_buffer_exit()`, and `iio_dma_buffer_release()`.

## Control Flow
File I/O mode allocates two page-aligned coherent blocks sized to half the configured buffer length. Input blocks start on the incoming queue and are submitted on enable; completed blocks become readable and then are re-enqueued. Output blocks are filled from userspace before submission. Imported dma-bufs disable file I/O mode, attach an external buffer, and enqueue it under the queue mutex with an optional fence and scatterlist. Hardware-specific drivers provide `submit()` and optional `abort()` callbacks.

## State And Persistence
Block state transitions through queued, active, done, and dead. Blocks are kref-counted; file I/O blocks own coherent DMA memory, while dma-buf blocks increment `num_dmabufs`. Completion from atomic context uses a global dead-block list and workqueue because coherent free can sleep. Queue state includes active flag, incoming list, fileio block array, active fileio block, position, mutex, and spinlock.

## Dependencies And Integration Points
The code integrates with IIO buffer core, DMA mapping, dma-buf, dma-fence, poll wait queues, workqueues, mutexes, spinlocks, and hardware-specific DMA buffer drivers such as DMAengine.

## Risks
Drivers must call `iio_dma_buffer_block_done()` for every submitted block, including aborted/no-transfer blocks, or blocks leak and userspace stalls. Missing `abort()` can leave active blocks unavailable across disable. Correct lock ordering between queue mutex and list spinlock is critical. File I/O and dma-buf modes are mutually exclusive, and incorrect state checks can expose use-after-free or stuck queues. `submit()` failure is only recoverable by disable/re-enable.

## Test Signals
Tests should cover input/output file I/O, short reads/writes rounded to datum size, length clamping to at least two, enable/disable abort, submit failure, dma-buf attach while fileio is enabled, fence signaling success/error, dead block cleanup from atomic completion, and poll wakeups.
