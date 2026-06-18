# sources/distributed-fs/ceph-client/arch/mips/lantiq/Kconfig

Purpose: defines Lantiq MIPS SoC configuration choices, covering XWAY-family, Amazon SE, and Falcon targets plus optional built-in device tree and PCI support.

Important APIs/types/functions: Kconfig symbols include `SOC_TYPE_XWAY`, `SOC_AMAZON_SE`, `SOC_XWAY`, `SOC_FALCON`, `LANTIQ_DT_NONE`, `DT_EASY50712`, and `PCI_LANTIQ`. Selections pull in pinctrl, MFD syscon/core, PCI capability, and built-in DTB support.

Control flow: under `if LANTIQ`, the first choice selects one SoC family, and the second selects whether to embed a fallback DTB. `PCI_LANTIQ` is only available for XWAY with generic PCI enabled.

State and persistence: build-time configuration only; it persists as `.config` symbols and drives compilation.

Dependencies and integration: feeds `arch/mips/lantiq/Makefile`, board DTS inclusion, pinctrl drivers, and PCI support.

Risks: selecting a SoC without the matching device tree or required pinctrl/syscon support can produce an unbootable kernel. Built-in DTB is only a fallback when firmware does not pass one.

Test signals: Kconfig dependency checks, defconfig coverage for XWAY/Falcon, and boot tests with both firmware-supplied and built-in DTB paths.
