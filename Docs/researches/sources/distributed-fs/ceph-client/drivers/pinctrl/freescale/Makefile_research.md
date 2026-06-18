# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Makefile

Purpose: Maps Freescale/NXP pinctrl Kconfig symbols to the object files built under `drivers/pinctrl/freescale`.

Important APIs and symbols: Uses `obj-$(CONFIG_...) += ...` for common objects (`pinctrl-imx.o`, `pinctrl-scu.o`, `pinctrl-imx-scmi.o`, `pinctrl-imx1-core.o`, `pinctrl-mxs.o`) and SoC-specific data/probe files such as `pinctrl-imx1.o`, `pinctrl-imx23.o`, `pinctrl-imx25.o`, `pinctrl-imx27.o`, `pinctrl-imx28.o`, and `pinctrl-imx35.o`.

Control flow: Build system inclusion is controlled entirely by Kconfig. Shared cores are linked when selected by SoC symbols, and SoC files provide the platform/SCMI driver registration and pin tables.

State and persistence: No runtime state. It determines which probe functions, module aliases, and exported common symbols are available in the built kernel.

Dependencies and integration points: Must stay synchronized with `Kconfig` symbol names and source filenames. It also determines whether shared helper exports satisfy SoC object references.

Risks: Omitting a common object selected by a SoC symbol produces link errors; adding a SoC file without a matching Kconfig line leaves it unreachable. Duplicate object inclusion under different symbols can create duplicate registration if not designed for it.

Test signals: Incremental builds for each `CONFIG_PINCTRL_*` symbol, clean `make drivers/pinctrl/freescale/`, and defconfig builds for i.MX/MXS platforms.
