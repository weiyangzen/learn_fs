# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/macio.h

Purpose: declares the Apple MacIO pseudo-bus, MacIO device representation, resource/IRQ accessors, and driver registration API.

Important APIs/types/functions: `struct macio_bus` links a MacIO chip to an optional PCI host device. `struct macio_dev` wraps a platform device, media-bay relation, DMA parameters, resources, and interrupts. Helpers include `to_macio_device`, `of_to_macio_device`, `macio_dev_get/put`, resource and IRQ accessors, `macio_enable_devres`, resource request/release functions, drvdata and OF-node helpers, `macio_get_pci_dev`, `struct macio_driver`, `to_macio_driver`, and driver register/unregister functions.

Control flow: MacIO bus enumeration creates `macio_dev` objects from Open Firmware nodes. Drivers register `struct macio_driver`, probe matching devices, request resources/IRQs, and receive suspend/resume/shutdown/media-bay callbacks.

State and persistence: each `macio_dev` persists as a platform device with resource arrays and driver data. Bus/chip pointers persist for device lifetime.

Dependencies and integration points: depends on OF, platform devices, optional PCI, and optional PMAC media bay support. It integrates old PowerMac onboard devices with Linux driver model.

Risks: resource and IRQ accessors do not bounds-check indexes. Non-PCI machines can have `pdev == NULL`. Media-bay devices require callback coordination during hot-swap.

Test signals: boot PowerMac systems with MacIO devices, verify OF matching, resource request/release, IRQ delivery, suspend/resume, PCI-backed and non-PCI MacIO paths, and media-bay events.
