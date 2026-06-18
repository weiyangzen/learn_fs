# sources/distributed-fs/ceph-client/drivers/phy/realtek/Kconfig

Purpose: Declares Realtek RTD USB2 and USB3 PHY driver configuration entries under an `ARCH_REALTEK || COMPILE_TEST` guard.

Important APIs/types/functions: Defines `PHY_RTK_RTD_USB2PHY` and `PHY_RTK_RTD_USB3PHY`. Both depend on `USB_SUPPORT` and select `GENERIC_PHY`, `USB_PHY`, and `USB_COMMON`.

Control flow: No runtime flow. Kconfig controls whether Realtek USB PHY objects are compiled.

State and persistence: No runtime state. Values persist in kernel configuration and affect Kbuild output.

Dependencies and integration points: Integrates with the Realtek PHY Makefile and the parent PHY Kconfig. The selected USB symbols ensure debug/USB helper APIs are available to the driver sources.

Risks: The outer architecture guard hides options outside Realtek unless compile testing. Missing dependencies for debugfs/nvmem/syscon are handled by source-level includes and broader kernel config, so compile-test coverage matters.

Test signals: Build both options as modules and built-in under `ARCH_REALTEK`, compile-test them on another architecture, and confirm Kconfig selects expected generic PHY and USB helper symbols.
