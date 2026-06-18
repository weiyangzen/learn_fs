# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Kconfig

## Purpose
This Kconfig fragment exposes StarFive JH7100 and JH7110 pinctrl/GPIO drivers and their shared feature dependencies.

## Important APIs, types, and functions
The visible symbols are `PINCTRL_STARFIVE_JH7100`, `PINCTRL_STARFIVE_JH7110_SYS`, and `PINCTRL_STARFIVE_JH7110_AON`. `PINCTRL_STARFIVE_JH7110` is an internal bool selected by both JH7110 instance drivers to build the common helper. All drivers select `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIOLIB_IRQCHIP`.

## Control flow
Kconfig dependency resolution controls which object files are built by the Makefile. JH7100 is a standalone tristate. The JH7110 SYS and AON drivers are separate tristates that each select the common bool, ensuring `pinctrl-starfive-jh7110.o` is built when either instance is enabled.

## State and persistence behavior
There is no runtime state. Build-time selections determine whether module or built-in platform drivers are present in the kernel image.

## Dependencies and integration points
All visible symbols depend on `SOC_STARFIVE || COMPILE_TEST` and `OF`, default to `SOC_STARFIVE`, and integrate with DT-based platform probing. The selected generic pinctrl and gpiolib symbols reflect the implementation's use of generic group/function registration, generic pinconf parsing, and GPIO IRQ chips.

## Risks
Because `PINCTRL_STARFIVE_JH7110` is bool, enabling either JH7110 instance as a module can still force the shared helper according to Kconfig's tristate/bool semantics; this should be checked against expected module linkage. The visible drivers have no explicit `HAS_IOMEM` dependency even though they ioremap MMIO resources, relying on the StarFive/compile-test context.

## Test signals
Build matrix should cover `JH7100=y/m`, `JH7110_SYS=y/m`, `JH7110_AON=y/m`, both JH7110 instances enabled together, and `COMPILE_TEST` on non-StarFive architectures. Module dependency checks should confirm the common JH7110 object is linked whenever SYS or AON is selected.
