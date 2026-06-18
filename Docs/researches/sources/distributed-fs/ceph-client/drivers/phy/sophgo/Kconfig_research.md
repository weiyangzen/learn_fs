# sources/distributed-fs/ceph-client/drivers/phy/sophgo/Kconfig

Purpose: Kconfig gate for Sophgo CV18XX/SG200X USB2 PHY support.

Important APIs, types, and functions: `PHY_SOPHGO_CV1800_USB2` is visible when `ARCH_SOPHGO || COMPILE_TEST`, depends on `MFD_SYSCON` and `USB_SUPPORT`, and selects `GENERIC_PHY`.

Control flow: not executable; controls compilation of `phy-cv1800-usb2.o`.

State and persistence: build-time only.

Dependencies and integration points: enables a generic PHY used with the DWC2 USB controller on Sophgo CV18XX/SG200X SoCs.

Risks: no explicit `COMMON_CLK` dependency despite the driver using clocks; transitive platform configs may cover this, but compile-test coverage should verify it.

Test signals: compile-test for module and built-in forms, dependency checks, and DWC2 consumer DT boots on CV1800B/SG200x boards.
