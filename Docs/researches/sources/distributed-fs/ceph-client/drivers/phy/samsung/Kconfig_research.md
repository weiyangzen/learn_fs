# sources/distributed-fs/ceph-client/drivers/phy/samsung/Kconfig

Purpose: Defines Kconfig symbols for Samsung-family PHY drivers: Exynos DP video, MIPI video, PCIe, UFS, USB2, USB DRD, and Exynos5250 SATA PHY support. It also gates SoC-specific USB2 implementation objects behind the common Samsung USB2 driver.

Important APIs and functions: The relevant symbols are `PHY_EXYNOS_DP_VIDEO`, `PHY_EXYNOS_MIPI_VIDEO`, `PHY_EXYNOS_PCIE`, `PHY_SAMSUNG_UFS`, `PHY_SAMSUNG_USB2`, `PHY_EXYNOS4210_USB2`, `PHY_EXYNOS4X12_USB2`, `PHY_EXYNOS5250_USB2`, `PHY_S5PV210_USB2`, `PHY_EXYNOS5_USBDRD`, and `PHY_EXYNOS5250_SATA`.

Control flow: Build selection flows from SoC or compile-test symbols into driver compilation. Most user-visible drivers select `GENERIC_PHY`; UFS, USB2, USB DRD, and SATA also select or depend on syscon/I2C facilities as needed. The hidden USB2 SoC symbols default on for matching SoC families and cause extra object files to be included in the common USB2 module.

State and persistence: Kconfig has no runtime state, but it persists build-time policy. Defaults such as `default ARCH_EXYNOS` or `default y if ARCH_S5PV210 || ARCH_EXYNOS` determine whether PHY providers are available in platform kernels without explicit user selection.

Dependencies and integration points: Integrates with architecture symbols (`ARCH_EXYNOS`, `ARCH_S5PV210`, `SOC_EXYNOS*`, `CPU_EXYNOS4210`), USB controller symbols (`USB_EHCI_EXYNOS`, `USB_OHCI_EXYNOS`, `USB_DWC2`, `USB_DWC3_EXYNOS`), `OF`, `HAS_IOMEM`, `TYPEC || !TYPEC`, `MFD_SYSCON`, and I2C support for SATA.

Risks: Incorrect dependencies can produce link errors or nonfunctional platform boots. The USB DRD symbol depends on `USB_DWC3_EXYNOS`, so PHY-only compile coverage is constrained. Hidden USB2 SoC options rely on architecture defaults and can omit needed tables on unusual multiplatform or compile-test builds.

Test signals: Build matrix coverage for Exynos, S5PV210, and `COMPILE_TEST`; checking that selected symbols produce the intended objects; randconfig coverage around optional Type-C and USB controller symbols; and boot-time verification that expected PHY providers appear for enabled DT compatibles.
