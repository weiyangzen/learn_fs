# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Kconfig

## Purpose
This Kconfig file declares Broadcom pinctrl driver configuration symbols and their build-time dependencies. It controls which Broadcom pinctrl, pinmux, pinconf, GPIO-integrated, and STB-related drivers are available for a kernel build.

## Important APIs, types, and functions
The file defines symbols including `PINCTRL_BCM281XX`, `PINCTRL_BCM2835`, `PINCTRL_BCM4908`, the shared `PINCTRL_BCM63XX`, several BCM63xx variants, `PINCTRL_BRCMSTB`, `PINCTRL_IPROC_GPIO`, `PINCTRL_CYGNUS_MUX`, `PINCTRL_NS`, `PINCTRL_NSP_GPIO`, `PINCTRL_NS2_MUX`, and `PINCTRL_NSP_MUX`. It selects framework symbols such as `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `REGMAP_MMIO`, `GPIOLIB`, `GPIOLIB_IRQCHIP`, `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `REGMAP`, and `GPIO_REGMAP`. It also sources `drivers/pinctrl/bcm/Kconfig.stb`.

## Control flow
Kconfig evaluation exposes prompts when architecture or `COMPILE_TEST` dependencies are met. Selected symbols cause corresponding object rules in the BCM Makefile to compile drivers. Default expressions enable drivers automatically for matching Broadcom architectures. The shared `PINCTRL_BCM63XX` symbol is selected by the individual BCM63xx SoC entries rather than prompted directly.

## State and persistence behavior
The file contributes persistent build configuration state through the kernel `.config`. It has no runtime state. Choices here determine which driver code is built in or available as a module and which framework dependencies are force-enabled.

## Dependencies and integration points
It integrates with the top-level pinctrl Kconfig tree, architecture symbols such as `ARCH_BCM_MOBILE`, `ARCH_BCM2835`, `ARCH_BRCMSTB`, `ARCH_BCMBCA`, `BMIPS_GENERIC`, `ARCH_BCM_IPROC`, `ARCH_BCM_CYGNUS`, `ARCH_BCM_5301X`, and `ARCH_BCM_NSP`, and the local Makefile. The help text documents driver scope and GPIO separation or integration.

## Risks
Incorrect dependencies can hide a driver for valid platforms or expose it where required infrastructure is missing. Incorrect `select` usage can force framework code without all needed prerequisites. Defaults that are too broad increase kernel footprint, while defaults that are too narrow break expected platform support. The STB source line means local Kconfig validity also depends on `Kconfig.stb`.

## Test signals
Run Kconfig configuration tests for the supported Broadcom architectures and for `COMPILE_TEST`. Confirm `make olddefconfig`, `make allnoconfig`, and relevant defconfigs select expected symbols. Build tests should verify every enabled symbol maps to an object rule and has all framework dependencies available.
