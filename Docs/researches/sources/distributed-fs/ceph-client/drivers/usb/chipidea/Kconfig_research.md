# sources/distributed-fs/ceph-client/drivers/usb/chipidea/Kconfig

Purpose: defines the build-time configuration surface for the ChipIdea Highspeed Dual Role Controller core, optional host/device roles, and platform glue drivers.

Important APIs/types/functions: declares `USB_CHIPIDEA`, `USB_CHIPIDEA_UDC`, `USB_CHIPIDEA_HOST`, and glue options for PCI, MSM, NPCM, i.MX, generic USB2, and Tegra. The core selects dependencies such as `EXTCON`, `RESET_CONTROLLER`, `USB_ULPI_BUS`, and `USB_ROLE_SWITCH`.

Control flow: Kconfig selections control which objects `Makefile` compiles and which inline stubs are active in headers such as `host.h` and `otg_fsm.h`.

State and persistence: no runtime state. Configuration persists in the kernel `.config` and determines available roles and glue modules.

Dependencies and integration: requires DMA and either EHCI host or USB gadget support. Host role depends on `USB_EHCI_HCD`; gadget role depends on `USB_GADGET`; several glue options depend on OF or PCI.

Risks: selecting dual-role core without matching role options can still build a core that rejects unsupported runtime modes. Defaults tie glue drivers to `USB_CHIPIDEA`, which can broaden build coverage unexpectedly for expert configurations.

Test signals: randconfig/allmodconfig builds and explicit host-only, gadget-only, OTG, PCI, OF, and Tegra/i.MX configurations.
