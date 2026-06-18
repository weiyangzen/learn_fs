# sources/distributed-fs/ceph-client/drivers/phy/ralink/Kconfig

Purpose: Declares build-time configuration entries for Ralink/MediaTek MT7621 PCIe PHY and Ralink USB PHY drivers.

Important APIs/types/functions: Defines `PHY_MT7621_PCI` and `PHY_RALINK_USB`. Both select `GENERIC_PHY`; the PCI option also selects `REGMAP_MMIO`, and the USB option selects `MFD_SYSCON` and depends on `HAS_IOMEM`.

Control flow: No runtime control flow. Kconfig dependency resolution decides whether the corresponding objects are built as modules, built-in, or omitted.

State and persistence: No runtime state. The selected config values persist in the kernel `.config` and drive Makefile object inclusion.

Dependencies and integration points: Integrates with the top-level PHY Kconfig hierarchy and the ralink Makefile. `PHY_MT7621_PCI` is available for `RALINK && OF` or `COMPILE_TEST`; `PHY_RALINK_USB` is available for `RALINK` or compile testing.

Risks: Missing dependencies can produce compile failures under `COMPILE_TEST`; overly strict dependencies can hide drivers for valid platforms. The MT7621 help text ends with a comma, which is cosmetic but unpolished.

Test signals: Run `make olddefconfig`/`menuconfig`, build each option as `y` and `m` where allowed, and compile-test non-Ralink architectures.
