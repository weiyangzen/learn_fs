<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.h

Purpose: Declares Cobalt IRQ entry points and diagnostics.

Important APIs/types: `cobalt_irq_handler()` is registered with `request_irq()`. `cobalt_irq_work_handler()` is used as the deferred workqueue callback. `cobalt_irq_log_status()` reports and resets IRQ counters.

Control flow: The top half queues the work handler for subdevice interrupt service; diagnostics are called from V4L2 log-status.

State/persistence: No header state; functions operate on `struct cobalt` and `struct cobalt_stream` internals.

Dependencies/integration: Includes Linux interrupt declarations and is consumed by PCI setup, V4L2 status, and workqueue initialization.

Risks: Function declarations depend on `struct cobalt` being visible to includers through `cobalt-driver.h` or prior declarations.

Test signals: Compile/link checks and successful `request_irq()` binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-irq.h -->
