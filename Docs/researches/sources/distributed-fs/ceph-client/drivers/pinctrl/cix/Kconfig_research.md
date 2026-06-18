# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Kconfig

Purpose: Kconfig entries for Cix Sky1 pinctrl support.

Important APIs/types/functions: hidden `PINCTRL_SKY1_BASE` selects generic pinctrl group/function/conf and regmap support; visible `PINCTRL_SKY1` depends on `ARCH_CIX || COMPILE_TEST` and `HAS_IOMEM`, and selects the base.

Control flow: enabling the Sky1 SoC driver pulls in the reusable base driver compiled from this subset and the SoC-specific `pinctrl-sky1.o`.

State and persistence: compile-time only.

Dependencies/integration: Kbuild consumes both symbols; base driver exports `sky1_base_pinctrl_probe()` for SoC-specific code.

Risks: base is tristate, so module linkage between base and SoC driver must be consistent. Missing `HAS_IOMEM` would break MMIO access, so the dependency is required.

Test signals: Kconfig resolution for ARCH_CIX and COMPILE_TEST, module build coverage, and confirmation that selecting `PINCTRL_SKY1` links both base and SoC object.
