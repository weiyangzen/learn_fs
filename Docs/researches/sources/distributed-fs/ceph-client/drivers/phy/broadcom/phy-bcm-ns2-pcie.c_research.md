# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-pcie.c

Purpose: Provides a small MDIO-backed Northstar2 PCIe PHY initializer for the 100 MHz AFE block.

Important APIs and types: The driver stores the `mdio_device` directly as PHY driver data. `ns2_pci_phy_init()` selects MDIO block `PLL_AFE1_100MHZ_BLK` and writes `PLL_CLK_AMP_2P05V` to the clock amplitude register.

Control flow: MDIO probe creates one generic PHY attached to the MDIO OF node, stores the MDIO device as driver data, and registers a simple provider from the PHY device. Init performs the two MDIO writes and logs the failing return code if either fails.

State and persistence: No software state beyond the MDIO pointer. Hardware retains the selected block/amplitude programming.

Dependencies and integration: It depends on OF MDIO, MDIO device access, generic PHY, and compatible `brcm,ns2-pcie-phy`. PCIe host drivers consume the PHY before link setup.

Risks and test signals: Because block select is global to the MDIO PHY page, other users must not race register-page selection. Test MDIO write errors, provider registration, PCIe link stability at 100 MHz reference, and repeated init calls.
