# sources/distributed-fs/ceph-client/drivers/phy/spacemit/Kconfig

Purpose: Kconfig entries for SpacemiT K1 PCIe/USB3 combo PHY and USB2 PHY drivers.

Important APIs, types, and functions: `PHY_SPACEMIT_K1_PCIE` depends on SpacemiT or compile-test, common clock, MMIO, and OF; selects `GENERIC_PHY`; defaults on `ARCH_SPACEMIT`. `PHY_SPACEMIT_K1_USB2` depends on SpacemiT/compile-test with OF, common clock, and USB common support; selects `GENERIC_PHY`.

Control flow: build-time selection for the two K1 PHY objects.

State and persistence: no runtime state.

Dependencies and integration points: the PCIe symbol covers one combo PCIe/USB3 PHY plus two PCIe-only PHYs; USB2 symbol supports K1 USB device/EHCI/OTG/xHCI consumers.

Risks: PCIe driver has cross-device calibration ordering, so build inclusion alone is not enough; DT must instantiate the combo PHY first or handle probe deferral. USB2 depends on USB_COMMON for `.disconnect` semantics.

Test signals: compile-test, module load ordering with port A calibration, and K1 board boot with PCIe-only and USB3 combo use cases.
