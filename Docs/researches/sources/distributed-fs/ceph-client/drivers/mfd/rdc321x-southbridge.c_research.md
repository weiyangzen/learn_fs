# sources/distributed-fs/ceph-client/drivers/mfd/rdc321x-southbridge.c

## Purpose
`rdc321x-southbridge.c` is a small PCI MFD parent for RDC R-321x/R6030 southbridge functions. It enables the PCI device and exposes watchdog and GPIO logical children with I/O resource windows and shared southbridge platform data.

## Important APIs, Types, And Functions
`rdc321x_wdt_resource[]` and `rdc321x_gpio_resources[]` describe I/O register ranges. `rdc321x_wdt_pdata` and `rdc321x_gpio_pdata` carry the parent PCI device pointer, with GPIO also carrying `max_gpios`. `rdc321x_sb_cells[]` defines child devices `rdc321x-wdt` and `rdc321x-gpio`. `rdc321x_sb_probe()` performs setup.

## Control Flow
PCI probe calls `pci_enable_device()`, stores the parent `pci_dev` in both child platform-data structures, and calls `devm_mfd_add_devices()` to register the watchdog and GPIO children. The `module_pci_driver()` macro handles driver registration/removal.

## State And Persistence
State is static platform data plus devm-managed child devices. Hardware state is not modified beyond enabling the PCI device; watchdog/GPIO registers are left to child drivers.

## Dependencies And Integration Points
It depends on PCI vendor/device IDs `PCI_VENDOR_ID_RDC` and `PCI_DEVICE_ID_RDC_R6030`, MFD core, `linux/mfd/rdc321x.h`, and child drivers consuming I/O resources relative to the southbridge.

## Risks
The child platform-data structures are static globals, so multiple matching PCI devices would overwrite `sb_pdev`. There is no explicit `pci_disable_device()` callback in this file. Resource ranges are hard-coded and must match the child drivers' expectations.

## Test Signals
Probe on RDC hardware or emulation, child resource visibility, watchdog and GPIO child operation, repeated bind/unbind, and any multi-device scenario are the primary signals.
