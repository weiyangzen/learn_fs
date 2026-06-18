# sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Kconfig

Purpose: Adds the National Instruments Ethernet vendor menu and the NI XGE management Ethernet driver configuration option.

Important APIs/types/functions: `config NET_VENDOR_NI` controls visibility of NI Ethernet drivers and defaults to `y`. `config NI_XGE_MANAGEMENT_ENET` is a tristate depending on `HAS_IOMEM && HAS_DMA`, selecting `PHYLIB` and `OF_MDIO` when OF is enabled.

Control flow/state: Kconfig-only build selection. It does not create runtime state; it controls whether `nixge.o` can be built.

Dependencies/integration: Integrated under the kernel Ethernet vendor tree. The selected driver depends on MMIO, DMA, PHY library, and optionally Open Firmware MDIO.

Risks: Missing dependency selections would surface as link/runtime failures in `nixge.c`. Defaulting vendor menu to yes exposes the prompt but does not force the driver.

Test signals: Run Kconfig/menuconfig coverage for `NET_VENDOR_NI=y/n`, module and built-in builds for `NI_XGE_MANAGEMENT_ENET`, and OF/non-OF dependency resolution.
