# Research: sources/distributed-fs/ceph-client/include/linux/pci-pwrctrl.h

Purpose: `pci-pwrctrl.h` declares a framework for PCI devices that need external resources such as regulators, GPIOs, or clocks enabled before the PCI device can be discovered.

Important APIs/types/functions: `struct pci_pwrctrl` contains the power-control device, `power_on`/`power_off` callbacks, and private notifier, device link, and work fields. APIs initialize a power-control context, mark/unmark a device ready, provide a devm ready helper, and create/destroy/power on/off power-control devices under a parent when `CONFIG_PCI_PWRCTRL` is enabled.

Control flow and state: platform devices created from firmware nodes power resources, mark themselves ready, trigger PCI bus rescan, and create a device link so PCI PM/reset ordering respects the power controller. State persists in the context and device link until unset or managed cleanup.

Dependencies and integration points: depends on notifier and workqueue APIs, device links, platform/OF population, PCI bus rescans, and power resource providers.

Risks and test signals: risks include rescanning before resources are stable, failing to remove links, power-off races with PCI devices, and disabled-config stubs masking missing framework support. Tests should cover deferred probe, ready/unready cycles, device-link PM ordering, devm cleanup, parent create/destroy, and PCI remove/rescan.
