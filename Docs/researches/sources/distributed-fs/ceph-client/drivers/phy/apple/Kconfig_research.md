# sources/distributed-fs/ceph-client/drivers/phy/apple/Kconfig

Purpose: Adds the Kconfig entry for the Apple Type-C PHY driver.

Important APIs and types: Defines `CONFIG_PHY_APPLE_ATC` as a tristate named "Apple Type-C PHY". It depends on Apple ARM64 platforms or compatible compile-test conditions, and on `TYPEC`. It selects `GENERIC_PHY` and `APPLE_TUNABLE`.

Control flow and integration: Enabling this symbol allows the `phy-apple-atc` module to be built and provides support for Apple Silicon Type-C PHY hardware used for USB2, USB3, USB4, Thunderbolt, and DisplayPort.

State and persistence: Kconfig carries build-time state only. It does not encode runtime policy.

Dependencies: The dependency set captures the driver use of Type-C switch/mux APIs, generic PHY APIs, and firmware-provided Apple tunables. The compile-test clause excludes `GENERIC_ATOMIC64`, matching broader ARM64/atomic constraints in kernel build coverage.

Risks and test signals: Build coverage should include built-in, module, disabled, ARCH_APPLE, and COMPILE_TEST configurations. Because the implementation also registers reset-controller and Type-C mux/switch devices, config tests should verify transitive dependencies are sufficient for both module and built-in builds.
