# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-pci.c

Purpose: PCI front end for Red Hat/QEMU pvpanic devices.

Important APIs and functions: `pvpanic_pci_probe()` enables the PCI device with `pcim_enable_device()`, maps BAR0 with `pcim_iomap()`, and delegates to `devm_pvpanic_probe()`. The ID table matches vendor `PCI_VENDOR_ID_REDHAT` and device `0x0011`. The `pci_driver` exposes `pvpanic_dev_groups`.

Control flow: managed PCI helpers keep teardown simple; no explicit remove hook is needed because devm and pcim resources unwind automatically.

State and persistence: only BAR mapping is transport-local; core pvpanic instance state is maintained by `pvpanic.c`.

Dependencies and integration points: depends on PCI and the shared pvpanic header/core. Provides the same sysfs event/capability controls as MMIO.

Risks and test signals: test BAR0 absent or unmappable, PCI enable failure, sysfs group creation, and event delivery under panic/shutdown in a QEMU guest exposing the PCI pvpanic device.
