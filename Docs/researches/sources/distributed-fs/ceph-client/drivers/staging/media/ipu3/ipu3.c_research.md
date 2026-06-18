# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.c

## Purpose

This is the IPU3 ImgU PCI driver core. It probes the PCI device, powers and initializes CSS/MMU/DMA/V4L2 layers, handles interrupts, feeds and drains firmware CSS queues, manages dummy buffers for optional nodes, and implements runtime/system power transitions.

## Important APIs, Types, and Functions

Exported internal functions are `imgu_node_to_queue()`, `imgu_map_node()`, `imgu_queue_buffers()`, and `imgu_s_stream()`. Probe/remove flow is `imgu_pci_probe()` and `imgu_pci_remove()`. Interrupt flow uses `imgu_isr()` and `imgu_isr_threaded()`. Dummy buffer helpers include preallocate/init/get/check/cleanup functions. Power helpers are `imgu_powerup()` and `imgu_powerdown()`. PM callbacks are `imgu_suspend()`, `imgu_resume()`, and runtime dummy callbacks.

## Control Flow

Probe enables PCI/MMIO/MSI, sets a 39-bit DMA mask, initializes locks and drain waitqueue, powers CSS enough to initialize MMU/DMA/CSS, registers V4L2 nodes, requests a threaded IRQ, and enables runtime PM. Streaming-on resumes runtime PM, powers up CSS at 200 or 450 MHz depending on enabled pipe input size, starts CSS streaming, initializes per-pipe dummy buffers, and queues initial buffer sets. `imgu_queue_buffers()` only feeds CSS when the input master queue has a real buffer; other enabled queues can use user buffers or dummy buffers. The threaded IRQ dequeues finished CSS buffers, timestamps/sequences output-side buffers, completes user buffers, wakes drain waiters when CSS is empty, and queues more work unless `qbuf_barrier` is set.

## State and Persistence Behavior

`struct imgu_device` persists PCI/MMIO, V4L2/media devices, MMU, IOVA domain, CSS state, per-pipe node state, locks, streaming flags, suspend flag, qbuf barrier, and drain waitqueue. Per-pipe dummy DMA maps persist across node lifetime and are resized at stream start to match active formats. CSS buffer state distinguishes new, queued, done, and error states.

## Dependencies and Integration Points

The file integrates Linux PCI, MSI IRQs, runtime PM, `ipu3-css`, `ipu3-css-fw`, `ipu3-dmamap`, `ipu3-mmu`, and the V4L2 layer in `ipu3-v4l2.c`. Firmware requirements are declared through `MODULE_FIRMWARE()`.

## Risks and Edge Cases

Dummy buffers avoid requiring userspace to queue every optional output, but the master input queue never uses dummies. Queueing failure after streaming can complete all unqueued user buffers with error. Suspend sets `qbuf_barrier`, synchronizes the IRQ, waits up to one second for CSS queue drain, then stops and powers down. Error unwinding in probe must unwind CSS, DMA, MMU, power, and locks in strict reverse order.

## Test Signals

Signals include PCI probe/remove with firmware present and missing, IRQ dequeue under continuous streaming, stream-on with optional VF/stat nodes disabled, stream-on with params metadata, high-resolution input forcing 450 MHz, system suspend/resume while streaming, runtime PM transitions, and error injection in CSS queueing/dummy buffer allocation.
