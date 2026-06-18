<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.c

Purpose: provides low-level MDIO/PHY helper operations for Atlantic copper PHY discovery and PTP-disable workarounds.

Important APIs/functions: `aq_mdio_busy_wait`, `aq_mdio_read_word`, `aq_mdio_write_word`, `aq_phy_read_reg`, `aq_phy_write_reg`, `aq_phy_init_phy_id`, `aq_phy_init`, and `aq_phy_disable_ptp`.

Control flow: raw MDIO read/write first programs address registers, issues address/read/write commands, and waits for the MDIO busy bit. Higher-level PHY accesses acquire the firmware MDIO semaphore with polling, perform the MDIO transaction, then release the semaphore. PHY init scans possible PHY IDs until identifier registers respond, then reads the full PMA/PMD ID. PTP disable loops over vendor registers and clears the PTP enable bit.

State and persistence: mutates `aq_hw->phy_id` and writes PHY registers. Register changes persist in device hardware/PHY state until reset or firmware reprovisioning, but no host filesystem persistence exists.

Dependencies and integration: uses Linux MDIO constants, `hw_atl_llh` register accessors, `aq_hw_utils`, and `aq_hw`. Called from `aq_nic_init` for Atlantic TP devices and from B0 PTP external timestamp GPIO support.

Risks: timeout returns are coarse (`0xffff` for failed reads), semaphore misuse can race firmware, and the PTP-disable workaround only runs when quirks and detected PHY ID allow it. Test signals include PHY ID detection, MDIO timeout injection, bad-PTP quirk devices, and external timestamp GPIO register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.c -->
