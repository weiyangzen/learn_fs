<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm6368.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm6368.c

Purpose: Broadcom BCM6368 MDIO mux controller for selecting internal versus external PHY buses.

Important APIs/types/functions: `struct bcm6368_mdiomux_desc` stores mux handle, base, device, parent mii_bus, and `ext_phy` selection. Core functions are `bcm6368_mdiomux_read`, `bcm6368_mdiomux_write`, `bcm6368_mdiomux_switch_fn`, probe, and remove.

Control flow: probe maps the integrated register region, allocates/registers a parent mii_bus, masks PHYs from parent auto-scan, then calls `mdio_mux_init` to create child buses. The switch function updates `ext_phy`; subsequent reads/writes include or omit `MDIOC_EXT_MASK`, write command registers, delay 50 us, and read/write data.

State and persistence: runtime state is the `ext_phy` flag, mux child state in mdio-mux core, MMIO registers, and bus objects. No persistent storage exists.

Dependencies/integration: depends on OF MDIO, BMIPS/compile-test config, mdio-mux core, platform bus, and phylib. Compatible string is `brcm,bcm6368-mdio-mux`.

Risks and test signals: risks include no busy/status polling, raw MMIO ordering, child `reg` values treated directly as boolean external selection, and parent phy mask assumptions. Tests should cover internal/external child reads/writes, mux init failure cleanup, and timing on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm6368.c -->
