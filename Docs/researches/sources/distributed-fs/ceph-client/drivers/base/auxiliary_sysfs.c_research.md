# sources/distributed-fs/ceph-client/drivers/base/auxiliary_sysfs.c

## Purpose
Adds auxiliary-device sysfs support for exposing IRQ numbers under an `irqs/` attribute group. It lets auxiliary-device users publish per-IRQ sysfs files after acquiring interrupts and remove them when interrupts are released.

## Important APIs, Types, And Functions
- `struct auxiliary_irq_info` stores a `device_attribute` and fixed-size decimal IRQ name.
- `auxiliary_irq_dir_prepare()` lazily creates the `irqs` group, initializes the xarray, and marks the directory present under a per-device mutex.
- Exported APIs: `auxiliary_device_sysfs_irq_add()` and `auxiliary_device_sysfs_irq_remove()`.

## Control Flow
Adding an IRQ first ensures the `irqs` group exists. It allocates an info record, initializes the sysfs attribute, formats the IRQ as the file name, inserts it into the auxiliary device xarray to reserve uniqueness, adds the file to the group, then stores ownership in the xarray. Removal loads the info by IRQ, removes the sysfs file, erases the xarray entry, and frees through cleanup attributes.

## State And Persistence
Per auxiliary device, state lives in `auxdev->sysfs.lock`, `irq_dir_exists`, and `sysfs.irqs` xarray. Each IRQ entry persists until explicitly removed or device-managed group cleanup occurs with the device.

## Dependencies And Integration Points
Depends on `linux/auxiliary_bus.h`, sysfs, devm device groups, xarray fields inside `struct auxiliary_device`, and compiler cleanup helpers.

## Risks And Edge Cases
The name buffer allows up to 10 digits plus terminator; unusually formatted or negative IRQs rely on `snprintf()` truncation behavior. Duplicate adds fail through `xa_insert()`. Remove logs an error for missing IRQs. Add/remove concurrency is only partially serialized: directory creation is locked, while unique IRQ discipline is required from callers as documented.

## Test Signals
First IRQ creating `irqs/`, duplicate add failure, sysfs file visibility/removal, missing IRQ removal error, concurrent unique adds, sysfs add failure rollback, and device teardown with devm group cleanup validate behavior.
