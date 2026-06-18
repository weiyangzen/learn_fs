# sources/distributed-fs/ceph-client/drivers/phy/realtek/Makefile

Purpose: Connects Realtek USB PHY Kconfig options to their object files.

Important APIs/types/functions: Builds `phy-rtk-usb2.o` for `CONFIG_PHY_RTK_RTD_USB2PHY` and `phy-rtk-usb3.o` for `CONFIG_PHY_RTK_RTD_USB3PHY`.

Control flow: No runtime logic. Kbuild object inclusion follows config selection.

State and persistence: No persistent state except generated build artifacts.

Dependencies and integration points: Integrates with `drivers/phy/realtek/Kconfig` and the parent PHY build.

Risks: Object/config mismatch would omit the driver or break the build. Both drivers use similar names and shared concepts, so incorrect object mapping would be easy to miss in review.

Test signals: Build each config as `m` and `y`, inspect generated modules, and verify platform aliases come from each driver's OF match table.
