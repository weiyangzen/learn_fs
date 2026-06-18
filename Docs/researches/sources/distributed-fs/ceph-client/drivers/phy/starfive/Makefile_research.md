# sources/distributed-fs/ceph-client/drivers/phy/starfive/Makefile

Purpose: object mapping for StarFive JH7110 PHY drivers.

Important APIs, types, and functions: maps DPHY RX/TX, PCIe, and USB Kconfig symbols to `phy-jh7110-dphy-rx.o`, `phy-jh7110-dphy-tx.o`, `phy-jh7110-pcie.o`, and `phy-jh7110-usb.o`.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY build system.

Risks: low; direct mapping.

Test signals: module/object inclusion and DT modalias generation.
