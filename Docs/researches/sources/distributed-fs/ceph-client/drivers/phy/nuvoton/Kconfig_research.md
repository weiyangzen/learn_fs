# sources/distributed-fs/ceph-client/drivers/phy/nuvoton/Kconfig

Purpose: This Kconfig fragment exposes the Nuvoton MA35 USB2.0 PHY driver.

Important APIs/types/functions: It defines tristate symbol `PHY_MA35_USB`, depends on `ARCH_MA35 || COMPILE_TEST`, depends on `OF`, and selects `GENERIC_PHY`.

Control flow: Kconfig enables the source driver only for MA35 platforms or compile-test builds with OF support. The matching Makefile compiles `phy-ma35d1-usb2.o`.

State and persistence: No runtime state exists here. Persistent configuration is held in the kernel `.config`.

Dependencies and integration points: The symbol mirrors the driver's OF/syscon/clock/generic-PHY requirements and integrates into the broader `drivers/phy` menu.

Risks: If the source driver gains new required subsystems such as reset controls or regulators, this file must gain matching dependencies or selects. The current dependency allows compile testing outside MA35, which helps catch generic build regressions.

Test signals: Build with `CONFIG_PHY_MA35_USB=m/y` under MA35 and `COMPILE_TEST`; runtime binding uses compatible `nuvoton,ma35d1-usb2-phy`.
