# sources/distributed-fs/ceph-client/drivers/uio/uio_pdrv_genirq.c

## Purpose
`uio_pdrv_genirq.c` is a generic platform-device UIO driver for memory-mapped devices whose interrupt can be disabled in the interrupt controller while userspace performs device-specific acknowledgement. It supports platform data and firmware-node-created devices.

## Important APIs, Types, And Functions
- `struct uio_pdrv_genirq_platdata` holds `uio_info`, a spinlock, an IRQ-disabled bit, and the platform device.
- `uio_pdrv_genirq_open()` and `release()` bridge UIO fd lifetime to runtime PM get/put.
- `uio_pdrv_genirq_handler()` disables the IRQ once with `disable_irq_nosync()`.
- `uio_pdrv_genirq_irqcontrol()` lets userspace enable or disable the IRQ without corrupting IRQ depth.
- `uio_pdrv_genirq_probe()` validates platform/fwnode metadata, discovers optional IRQ and memory resources, initializes UIO callbacks, enables runtime PM, and registers the UIO device.

## Control Flow
Probe either uses existing `struct uio_info` platform data or allocates one from a firmware node and assigns a name from `linux,uio-name` or the firmware node path. It rejects preconfigured handlers, irqcontrol callbacks, and shared IRQs because this driver owns generic IRQ masking. It obtains IRQ 0 if not supplied, maps platform memory resources into UIO physical maps, sets level-triggered IRQs to `IRQ_DISABLE_UNLAZY`, enables runtime PM, and registers the UIO device. Interrupt handling disables the IRQ and records `UIO_IRQ_DISABLED`; userspace writes to the UIO control path to re-enable after clearing the device cause.

## State And Persistence Behavior
The private flag bit tracks whether the IRQ is currently disabled, protecting IRQ depth across concurrent handler and userspace control paths. Runtime PM state is held while the UIO fd is open and released on close. Memory maps and UIO registration are devm-managed and last for the platform-device lifetime.

## Dependencies And Integration Points
The driver integrates platform devices, firmware node properties, Open Firmware matching through the `of_id` module parameter, IRQ core, runtime PM, and UIO core. Device-specific userspace must know how to map registers, acknowledge interrupts, and write UIO irqcontrol.

## Risks And Edge Cases
Interrupt sharing is intentionally unsupported. The firmware-node match table is populated by module parameter, so incorrect `of_id` can bind unintended hardware. `pm_runtime_get_sync()` return values are ignored, so wake failures are not propagated to userspace open. Platform data must not predefine handler/irqcontrol. Userspace failure to re-enable IRQ leaves the device quiet.

## Test Signals
Bind a simple platform MMIO device with one IRQ and confirm `/dev/uioX` appears with expected maps. Trigger an interrupt and verify it is disabled once, not repeatedly depth-disabled. Write irqcontrol values from multiple processes and verify enable/disable balance. Test level-triggered IRQs for immediate retrigger prevention. Validate runtime PM transitions on UIO open and close.
