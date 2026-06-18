# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Makefile

Purpose: Connects NXP pinctrl Kconfig symbols to the objects built by kbuild.

Important APIs, types, and symbols: `obj-$(CONFIG_PINCTRL_S32CC) += pinctrl-s32cc.o` builds the common S32 pinctrl core, and `obj-$(CONFIG_PINCTRL_S32G2) += pinctrl-s32g2.o` builds the S32G2 SoC data and platform driver.

Control flow: There is no runtime control flow. Build-time control follows kbuild expansion of `obj-y` entries based on selected Kconfig symbols.

State and persistence: No runtime state. The selected `.config` controls whether these object files become part of the kernel image.

Dependencies and integration points: Integrates with `drivers/pinctrl/Makefile`, the local `Kconfig`, and the split between reusable S32CC core code and S32G2-specific data/driver registration.

Risks: Because `pinctrl-s32g2.c` calls `s32_pinctrl_probe()` from `pinctrl-s32cc.c`, selecting or building the SoC object without the common object would fail linking. The Kconfig currently prevents that by selecting `PINCTRL_S32CC`.

Test signals: Kernel build with `CONFIG_PINCTRL_S32G2=y` should compile and link both objects; build with only hidden common selected by another SoC should compile only `pinctrl-s32cc.o`.
