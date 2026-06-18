
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa-pci.c

Purpose: this built-in PCI glue driver exposes Intel CE4100 PCI I2C controllers as three platform devices consumed by the main PXA I2C platform driver. CE4100 hardware is similar enough to PXA I2C to reuse `i2c-pxa.c`, but each PCI BAR represents a separate controller and target/slave mode is unsupported.

Important APIs, types, and functions: `struct ce4100_devices` stores the three created platform devices. `add_i2c_device()` builds a `struct i2c_pxa_platform_data`, two resources (MMIO and IRQ), locates the matching child DT node for the BAR, reads optional `fast-mode`, allocates a `platform_device` named `ce4100-i2c`, attaches resources and platform data, and registers it. `ce4100_i2c_probe()` enables the PCI function with `pcim_enable_device()`, requires a device tree node, allocates state, and creates devices for all three BARs.

Control flow: PCI probe performs managed PCI enable, validates OF presence, allocates `ce4100_devices`, then loops over BARs 0..2. Each BAR is matched against child OF `reg` resources by start, end, and flags. If any platform-device registration fails, previously created devices are unregistered and the state object is freed. Successful probe stores state with `pci_set_drvdata()`. There is no remove callback because the driver is built in via `builtin_pci_driver()`.

State and persistence: state is limited to the allocated list of platform-device pointers and a static incrementing `devnum` used for platform IDs. The generated platform devices hold the resource and pdata copies for the PXA driver lifetime.

Dependencies and integration points: it depends on PCI ID `8086:2e68`, OF child address translation, platform-device registration, and `linux/platform_data/i2c-pxa.h`. It integrates with `i2c-pxa.c` through the platform device name `ce4100-i2c` and `REGS_CE4100` platform ID entry.

Risks: probe fails without a DT node or if any BAR cannot be matched to a child node. All child controllers share the same PCI IRQ. There is no hot-unplug/remove cleanup path, acceptable only for built-in/non-hotpluggable assumptions. The static `devnum` is global and monotonically increasing.

Test signals: CE4100 boot should create three `ce4100-i2c` platform devices, match each BAR to a DT child, propagate `fast-mode`, share IRQ resources correctly, and unwind all earlier devices if one BAR setup fails.
