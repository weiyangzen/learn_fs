# sources/distributed-fs/ceph-client/drivers/thermal/renesas/Kconfig

Purpose: Kconfig menu entries for Renesas thermal drivers. It exposes separate tristate options for legacy R-Car, R-Car Gen3/Gen4 and RZ/G2, RZ/G2L, RZ/G3E, and RZ/G3S thermal sensor drivers.

Important symbols: `RCAR_THERMAL`, `RCAR_GEN3_THERMAL`, `RZG2L_THERMAL`, `RZG3E_THERMAL`, and `RZG3S_THERMAL`. Most depend on `ARCH_RENESAS || COMPILE_TEST`; the RZ/G3S option specifically depends on `ARCH_R9A08G045 || COMPILE_TEST` plus `OF`, `IIO`, and `RZG2L_ADC`.

Control flow and integration: these symbols select whether the corresponding objects in `renesas/Makefile` are built. The options assume thermal OF integration from the driver side but do not select the thermal framework themselves, relying on parent menu context and build dependencies.

State and persistence: no runtime state. It controls build-time inclusion only.

Dependencies and risks: missing `HAS_IOMEM` or `OF` dependencies would produce bad compile or probe surfaces for MMIO/DT-only drivers; `RZG3E_THERMAL` lacks explicit `HAS_IOMEM` and `OF` dependencies compared with neighboring options, so compile-test coverage is important. `RZG3S_THERMAL` is tied to IIO and the RZ/G2L ADC because its temperature samples come through an IIO channel.

Test signals: run Kconfig dependency checks under Renesas and COMPILE_TEST configs; ensure every enabled symbol builds the object named in `Makefile`; verify RZ/G3S cannot be enabled without the IIO ADC dependency.
