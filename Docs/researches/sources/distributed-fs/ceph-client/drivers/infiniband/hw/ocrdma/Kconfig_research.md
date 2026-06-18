# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Kconfig

Purpose: declares the kernel configuration option for the Emulex OneConnect ocrdma RoCE driver.

Important APIs/types/functions: defines `CONFIG_INFINIBAND_OCRDMA` as a tristate option labeled "Emulex One Connect HCA support".

Control flow: Kconfig dependency resolution requires `ETHERNET`, `NETDEVICES`, `PCI`, and `INET`; selecting the option also selects `NET_VENDOR_EMULEX` and `BE2NET`.

State and persistence: build-time configuration state only. When enabled as built-in or module, the ocrdma objects listed by the Makefile become part of the kernel build.

Dependencies and integration: couples the RDMA driver to the Emulex be2net Ethernet/NIC driver because ocrdma shares OneConnect hardware support and headers.

Risks: missing `BE2NET` or networking dependencies prevents the driver from building. The help text says "InfiniBand over Ethernet", reflecting RoCE support rather than native InfiniBand link-layer behavior.

Test signals: Kconfig allmodconfig/allyesconfig coverage, module build with `CONFIG_INFINIBAND_OCRDMA=m`, and dependency checks when BE2NET is disabled.
