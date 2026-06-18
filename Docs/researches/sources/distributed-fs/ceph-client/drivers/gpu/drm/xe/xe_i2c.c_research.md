# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.c

## Purpose
`xe_i2c.c` discovers and registers an MMIO-backed Synopsys DesignWare I2C host controller embedded in Xe devices, then creates an I2C client for the attached Add-In Management Controller. It also bridges Xe top-level interrupts to a Linux IRQ domain used by the I2C adapter.

## Important APIs, Types, And Functions
- `xe_i2c_probe()` is the public probe entry point.
- `xe_i2c_present()` validates the endpoint cookie and confirms controller availability.
- `xe_i2c_register_adapter()` creates a software fwnode and platform device named `i2c_designware`.
- `xe_i2c_notifier()` captures the DesignWare adapter once the platform device is added, then schedules `xe_i2c_client_work()` to instantiate the `"amc"` client.
- `xe_i2c_create_irq()`, `xe_i2c_irq_postinstall()`, `xe_i2c_irq_reset()`, and `xe_i2c_irq_handler()` create and operate the pseudo IRQ used by the adapter.
- `xe_i2c_pm_suspend()` and `xe_i2c_pm_resume()` directly manipulate the embedded PCI PM registers.
- `xe_i2c_read()` and `xe_i2c_write()` provide a regmap-backed MMIO access layer.

## Control Flow
Probe exits early when the platform lacks I2C, is an SR-IOV VF, or endpoint cookie validation fails. On success it allocates `struct xe_i2c`, stores it in `xe->i2c`, resumes the embedded device to D0, creates a regmap, registers an I2C bus notifier, optionally creates an IRQ domain/mapping, registers the DesignWare platform device, enables IRQ forwarding, and installs managed cleanup. Adapter creation deliberately avoids `platform_device_register_full()` so the notifier has a valid `pdev` handle early.

## State And Persistence
State persists in `xe->i2c`: endpoint data, platform device/fwnode, adapter pointer, I2C clients, notifier, work item, IRQ domain, adapter IRQ, DRM device, and MMIO pointer. Cleanup unregisters client devices, bus notifier, platform device, fwnode, and IRQ domain. The embedded controller's PM state is written directly by suspend/resume helpers.

## Dependencies And Integration Points
The file integrates with Linux I2C, platform devices, fwnodes, irqdomain, regmap, PCI PM definitions, Xe MMIO, Xe SR-IOV checks, and survivability mode. The global Xe IRQ handler calls `xe_i2c_irq_handler()`, `xe_i2c_irq_reset()`, and `xe_i2c_irq_postinstall()`.

## Risks
The notifier/workqueue sequence depends on adapter discovery ordering. The work item is scheduled when the adapter appears, but removal does not explicitly flush it, so lifetime assumptions rely on managed remove ordering and adapter/device teardown. IRQ forwarding deasserts/reasserts INTx bits after the nested handler; incorrect ordering could lose edge-like events. Survivability mode disables IRQ creation, so adapter behavior must remain correct without IRQs.

## Test Signals
Exercise endpoint absent/present paths, SR-IOV VF exclusion, adapter registration/unregistration, client instantiation, IRQ forwarding under repeated interrupts, D3hot/D0 transitions, and survivability boot mode. Dynamic debug around PMCSR and adapter events is useful.
