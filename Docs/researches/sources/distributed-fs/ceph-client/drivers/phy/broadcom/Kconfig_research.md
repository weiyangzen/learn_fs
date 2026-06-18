# sources/distributed-fs/ceph-client/drivers/phy/broadcom/Kconfig

Purpose: Defines Broadcom PHY driver build options for USB, PCIe, SATA, and STB platform PHY implementations.

Important APIs and types: The menu includes `PHY_BCM63XX_USBH`, `PHY_CYGNUS_PCIE`, `PHY_BCM_SR_USB`, `BCM_KONA_USB2_PHY`, `PHY_BCM_NS_USB2`, `PHY_BCM_NS_USB3`, `PHY_NS2_PCIE`, `PHY_NS2_USB_DRD`, `PHY_BRCM_SATA`, `PHY_BRCM_USB`, and `PHY_BCM_SR_PCIE`. Most select `GENERIC_PHY`; some additionally depend on `PHYLIB`, `EXTCON`, `MFD_SYSCON`, or `SOC_BRCMSTB`.

Control flow and integration: These symbols control which platform or MDIO drivers are built for Broadcom families such as Cygnus, Kona, Northstar, Northstar2, Stingray, BCM63xx, BRCMSTB, BCMBCA, and iProc.

State and persistence: This file has only build-time state. Defaults are tied to relevant architecture symbols where appropriate.

Dependencies: The dependency expressions encode required bus/framework support: OF, MDIO mux/PHYLIB, HAS_IOMEM, architecture families, and compile-test escape hatches.

Risks and test signals: Build matrices should cover every symbol as module and built-in, compile-test paths, and transitive dependency correctness. `PHY_BRCM_USB` is especially coupled to multiple object files and optional SoC support.
