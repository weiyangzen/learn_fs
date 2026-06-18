# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/Makefile

## Purpose
This Makefile maps the Cadence Kconfig choices to kernel objects. It builds the main `macb` object from `macb_main.o`, conditionally links `macb_ptp.o` into that same object when hardware timestamping is enabled, and builds `macb_pci.o` as the PCI wrapper module.

## Important build rules
- `macb-y := macb_main.o` makes `macb_main.c` the always-present implementation of `CONFIG_MACB`.
- `macb-y += macb_ptp.o` is conditional on `CONFIG_MACB_USE_HWSTAMP=y`.
- `obj-$(CONFIG_MACB) += macb.o` emits the platform driver according to the tristate.
- `obj-$(CONFIG_MACB_PCI) += macb_pci.o` emits the PCI wrapper separately.

## Integration, risks, and tests
The important integration point is object composition: `macb_ptp.c` is part of `macb.o`, while the PCI wrapper remains separate and depends on the platform driver name. The main risk is link drift between the PTP declarations in `macb.h` and conditional inclusion here. Test by building with timestamping on/off and with `macb` and `macb_pci` as built-ins and modules.
