## sources/distributed-fs/ceph-client/drivers/staging/vme_user/Kconfig

Purpose: this Kconfig file defines staging support for the VME bus framework, bridge drivers, and a userspace VME access driver.

Important definitions: `menuconfig VME_BUS` is a bool depending on PCI and describes the bridge framework. Inside `if VME_BUS`, `VME_TSI148` is a DMA-dependent tristate for Tundra TSI148 PCI/X bridges, `VME_FAKE` is a virtual bridge for development, and `VME_USER` is a userspace access driver compatible with older vmelinux-style interfaces.

Control flow and state: selection controls which VME framework and device driver objects are built. Enabling `VME_BUS` alone builds framework support but not necessarily a hardware bridge or userspace device driver.

Dependencies and integration points: paired with `vme_user/Makefile`, which builds `vme.o`, `vme_user.o`, `vme_tsi148.o`, and `vme_fake.o` according to these symbols. The help text warns users that a specific bridge driver is needed for actual hardware.

Risks: `VME_BUS` depends only on PCI, while fake bridge may not need PCI in principle; this keeps the whole framework PCI-gated. `VME_USER` has no extra dependency beyond `VME_BUS`, so users can enable it without a real bridge. Staging status suggests ABI and cleanup concerns.

Test signals: Kconfig builds with each symbol as built-in/module where applicable, dependency resolution when `HAS_DMA` is absent, menu visibility, and allmodconfig coverage for VME components.
