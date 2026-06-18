# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Makefile

Purpose: Builds the IBM PowerPC 4xx on-chip EMAC driver and optional hardware-support objects.

Important build entries: `obj-$(CONFIG_IBM_EMAC) += ibm_emac.o` defines the composite driver. `ibm_emac-y := mal.o core.o phy.o` always includes MAL, core, and PHY support. Conditional additions include `zmii.o`, `rgmii.o`, and `tah.o` when `CONFIG_IBM_EMAC_ZMII`, `CONFIG_IBM_EMAC_RGMII`, or `CONFIG_IBM_EMAC_TAH` are selected.

Control flow: kbuild enters this Makefile when the parent directory includes `emac/`. The composite object includes optional bridge/accelerator files based on hidden Kconfig symbols selected by platform code.

State and persistence: No runtime state. Build artifacts persist only in the kernel build directory.

Dependencies and integration: Coupled to `ibm/emac/Kconfig` and to source files in the EMAC subdirectory. The base object set implies the EMAC driver always needs MAL DMA management, the core netdev implementation, and PHY handling.

Risks: Optional hardware files must be included when hardware requires them; otherwise the driver can compile but lack required register support. Conversely, unnecessary optional objects may introduce references unavailable on a given platform if Kconfig selects are wrong.

Test signals: Build `CONFIG_IBM_EMAC` with no optional bridges, with each optional bridge alone, and with combined ZMII/RGMII/TAH selections; module and built-in links; platform defconfig coverage.
