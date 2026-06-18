# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb_pci.c

## Purpose
`macb_pci.c` is a thin PCI wrapper for the Cadence MACB/GEM platform driver. It binds Cadence PCI device ID `0xe007`, enables the PCI function, constructs platform resources and fixed clocks, and registers a child platform device named `macb` so `macb_main.c` can handle the hardware.

## Important APIs and control flow
`macb_probe()` enables the PCI device, sets bus mastering, translates BAR0 and IRQ vector 0 into platform resources, creates fixed-rate `pclk` and `hclk` clocks at 50 MHz, fills `struct macb_platform_data`, and calls `platform_device_register_full()`. `macb_remove()` unregisters the child platform device, then unregisters the fixed clocks. The PCI ID table matches `PCI_VDEVICE(CDNS, PCI_DEVICE_ID_CDNS_MACB)`.

## State, dependencies, risks, and tests
Runtime state is the child `platform_device` stored as PCI drvdata plus the two fixed clocks copied through platform data. There is no persistent storage. The wrapper depends on PCI, platform-device registration, fixed-rate clocks, and `macb.h`. Risks include invalid BAR0/IRQ assumptions, incorrect fixed clock rates, and cleanup ordering. Tests are module load/unload, child platform probe success, correct BAR/IRQ resources, no clock leaks on failure, and successful network traffic through PCI-instantiated hardware.
