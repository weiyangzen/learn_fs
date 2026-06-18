# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-thunderx-pcidrv.c

Purpose: binds Cavium ThunderX/OcteonTX TWSI I2C controllers exposed as PCI devices and adapts the shared Octeon I2C core to PCI resources, interrupts, clocks, SMBus alert, and adapter registration.

Important APIs/types/functions: this file uses `struct octeon_i2c` from `i2c-octeon-core.h`. It provides interrupt enable/disable callbacks for core and high-level controller interrupt bits, `thunderx_i2c_functionality()`, the `thunderx_i2c_algo` using `octeon_i2c_xfer`, clock setup helpers, SMBus alert setup/removal, and PCI probe/remove.

Control flow: PCI probe allocates Octeon core state, fills ThunderX register offsets, enables the PCI device, requests BARs, maps BAR0, obtains system clock from DT clock or ACPI properties with defaults, reads `clock-frequency`, initializes the wait queue and interrupt callback hooks, allocates one MSI-X vector, requests `octeon_i2c_isr`, initializes low-level hardware, applies OcteonTX2 reference-clock adjustment for low-speed modes, programs the TWSI clock, configures adapter metadata/recovery, registers it, and optionally creates an SMBus alert responder from OF IRQ data. Remove unregisters alert, disables the clock, and removes the adapter.

State and persistence: persistent controller state is held in the shared `octeon_i2c` object: mapped register base, offsets, clock frequencies, callback hooks, adapter, alert client, and wait queue. Transfer state is managed by the Octeon core rather than this wrapper.

Dependencies and integration: depends on PCI, MSI-X, the shared Octeon I2C core, OF/ACPI firmware properties, Linux clocks, SMBus alert helpers, and I2C bus recovery info from the core. It matches Cavium PCI device ID `0xa012` and advertises I2C plus SMBus emulation except quick, SMBus read block data, and block process call.

Risks: `thunder_i2c_smbus_remove()` unconditionally unregisters `i2c->ara`; if alert setup never created a client, this path depends on unregister handling of a null pointer and should be checked. ACPI SMBus alert is explicitly unsupported. Clock defaults hide missing firmware clock data. Probe error paths disable clocks but rely on devm/pcim for most cleanup.

Test signals: PCI probe/remove, DT and ACPI clock property paths, OcteonTX2 low-speed reference clock selection, MSI-X IRQ delivery, shared-core transfer/recovery paths, SMBus alert present/absent cases, and probe failures after clock enable or IRQ allocation.
