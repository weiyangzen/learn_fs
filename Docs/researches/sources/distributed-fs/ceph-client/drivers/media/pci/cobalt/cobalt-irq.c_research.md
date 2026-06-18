<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.c

Purpose: Handles Cobalt MSI interrupts for DMA completions, ADV subdevice events, FIFO/data-loss conditions, and deferred subdevice interrupt servicing.

Important APIs/functions: `cobalt_irq_handler()` is the top-half IRQ handler. It reads/clears DMA interrupt status and system edge status, temporarily masks edge sources, completes DMA buffers per stream, sets ADV IRQ flags, updates counters, queues `cobalt_irq_work_handler()`, and returns handled. `cobalt_dma_stream_queue_handler()` removes the completed buffer, handles unstable capture lock/freewheel/CVI state, timestamps/sequences it, and returns it to vb2. `cobalt_irq_work_handler()` calls subdevice `interrupt_service_routine` and unmasks ADV IRQs. `cobalt_irq_log_status()` logs and resets counters and re-enables lost-data masks.

Control flow: DMA completion removes the oldest queued buffer because descriptor chaining guarantees the interrupt occurs only when DMA can continue. For video capture, initial frames are marked error while measurement, clock-loss, CVI lock, and freewheel state converge; lock loss restarts the freewheel recovery sequence. ADV interrupts are deferred to a single-thread workqueue to avoid doing I2C-heavy subdevice work in hard IRQ context.

State/persistence: Uses per-stream `bufs`, `irqlock`, `flags`, `unstable_frame`, `enable_cvi`, `enable_freewheel`, `skip_first_frames`, and sequence counters. Card-wide IRQ counters persist until log-status resets them.

Dependencies/integration: Works with Cobalt V4L2/vb2 queues, generated FPGA register maps, Omnitek DMA, ADV7604-style subdevice IRQ callbacks, and system status masks from `cobalt-driver.h`.

Risks: The handler assumes a buffer exists on DMA interrupt; empty list logs an error and drops handling. Buffer list manipulation is split before stability checks, so hardware state checks happen outside the lock. FIFO/data-loss masking depends on edge/mask ordering. Stability logic is tied to exact FPGA status semantics and may mark multiple startup frames as errors.

Test signals: Streaming DMA interrupt cadence, buffer DONE/ERROR states during stable and unstable video, cable unplug/replug recovery, ADV source-change event delivery, FIFO-full logs, counter reset in log-status, and interrupt storm/no-interrupt cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.c -->
