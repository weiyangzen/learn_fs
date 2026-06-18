# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-if.c

## Purpose
`isp1760-if.c` is bus glue for the ISP1760 common driver. It supports OpenFirmware/platform devices and, under `CONFIG_USB_PCI`, the PLX PCI evaluation-card path for ISP1761.

## Important APIs, Types, And Functions
PCI-specific functions are `isp1761_pci_init()`, `isp1761_pci_probe()`, `isp1761_pci_remove()`, and `isp1761_pci_shutdown()`, with `isp1761_pci_driver` matching a PLX bridge. Platform functions are `isp1760_plat_probe()` and `isp1760_plat_remove()` with OF matches for `nxp,usb-isp1760`, `nxp,usb-isp1761`, and `nxp,usb-isp1763`. Module entry/exit are `isp1760_init()` and `isp1760_exit()`.

## Control Flow
Module init creates HCD kmem caches, registers the platform driver, and optionally registers the PCI driver; if neither registration succeeds it destroys caches and returns `-ENODEV`. Platform probe obtains MMIO and IRQ resources, reads IRQ trigger type, parses OF compatibility and properties into devflags (`bus-width`, `dr_mode`, `analog-oc`, DACK/DREQ polarity), then calls `isp1760_register()`. PCI probe enables the device, runs PLX setup, sets bus mastering, and calls `isp1760_register()` on resource 3 and the PCI IRQ.

PCI init probes scratch access through resource 3, adjusts PCI latency, configures PLX interrupt pass-through via resource 0, and releases temporary mappings/regions before common registration.

## State And Persistence
Bus glue itself keeps no long-lived state beyond registered platform/PCI drivers. Device state is owned by `isp1760_register()` and stored as driver data on the device. PCI enablement and PLX interrupt bits are hardware state lasting until remove/shutdown.

## Dependencies And Integration Points
The file depends on platform devices, OF helpers, USB OTG/dr-mode parsing, IRQ trigger helpers, PCI APIs when enabled, MMIO mapping, and the common ISP1760 registration API. It is the bridge from device tree or PCI IDs to `devflags`.

## Risks
Platform probe rejects non-OF devices with `-ENXIO`, so board-file platform data is not supported. PCI error paths call `pci_disable_device()` but common registration failures rely on the common layer for partial cleanup. `isp1761_pci_shutdown()` only logs and does not stop hardware. PCI temporary resource names and scratch-test assumptions are evaluation-card specific. `isp1760_init()` ignores the return from `isp1760_init_kmem_once()`, so cache allocation failure can surface later.

## Test Signals
Test OF probe for each compatible and bus-width value, missing IRQ/resource failures, peripheral dr_mode flagging, analog overcurrent rejection on ISP1763, and remove/unregister. PCI tests should validate scratch mismatch, resource request failures, PLX interrupt enabling, and disable paths. Build with and without `CONFIG_USB_PCI`.
