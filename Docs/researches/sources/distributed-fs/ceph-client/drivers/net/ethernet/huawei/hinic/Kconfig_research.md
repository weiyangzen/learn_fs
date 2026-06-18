# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/Kconfig

Defines `CONFIG_HINIC`, a tristate for the Huawei Intelligent PCIe Network Interface Card driver. It depends on `PCI_MSI` and `X86 || ARM64`, and selects `NET_DEVLINK`.

The setting persists in `.config` and drives the `hinic` Kbuild directory. `NET_DEVLINK` is required by the devlink firmware flash and health reporter code. Risks include architecture exclusion and build breakage if devlink is not selected. Test Kconfig dependency visibility and module/built-in builds.
