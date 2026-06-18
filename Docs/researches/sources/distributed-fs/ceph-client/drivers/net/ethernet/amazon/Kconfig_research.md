# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Kconfig

Purpose: this Kconfig file exposes Amazon Ethernet device support and the ENA PCI Ethernet driver to kernel configuration.

Important APIs, types, and functions: `NET_VENDOR_AMAZON` is a vendor menu boolean defaulting to `y`. Inside that menu, `ENA_ETHERNET` is a tristate for Elastic Network Adapter support. The ENA symbol depends on `PCI_MSI`, excludes `CPU_BIG_ENDIAN`, depends on optional PTP clock support through `PTP_1588_CLOCK_OPTIONAL`, and selects `DIMLIB` and `NET_DEVLINK`.

Control flow: the file contributes build-time configuration only. If `NET_VENDOR_AMAZON` is disabled, the ENA question is hidden. If `ENA_ETHERNET` is `m` or `y`, the Amazon Makefile descends into the ENA driver and builds it as a module or built-in object.

State and persistence: persistent state is the kernel `.config` symbol values. There is no runtime state in this file.

Dependencies and integration points: `PCI_MSI` matches ENA's MSI-X interrupt model, `!CPU_BIG_ENDIAN` matches the driver's little-endian descriptor/register assumptions, `PTP_1588_CLOCK_OPTIONAL` supports PHC integration, `DIMLIB` supports adaptive interrupt moderation, and `NET_DEVLINK` supports the devlink companion file.

Risks: the help text contains an extra quote after `Elastic Network Adapter (ENA)`, which is cosmetic. The hard `!CPU_BIG_ENDIAN` dependency prevents unsupported endian builds but also hides the driver from any future big-endian platform work. Missing `PCI` dependency may be covered indirectly by `PCI_MSI`, but config dependency changes should be audited with ENA probe assumptions.

Test signals: configuration tests should verify the ENA option appears only when the vendor menu and dependencies permit it, `CONFIG_ENA_ETHERNET=m` builds `ena.ko`, `=y` links built-in, and disabling `NET_DEVLINK` or `DIMLIB` manually is not possible while ENA is selected.
