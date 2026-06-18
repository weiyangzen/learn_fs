# sources/distributed-fs/ceph-client/drivers/net/wireless/Kconfig

Purpose: Defines the top-level Linux Wireless LAN driver Kconfig menu and includes vendor-specific wireless driver Kconfig files.

Important APIs and definitions: `menuconfig WLAN` is a bool menu enabled by default, depends on `!S390` and `NET`, and selects `WIRELESS`. Inside `if WLAN`, it sources vendor Kconfig files for ADMtek, Atheros, Atmel, Broadcom, Intel, Intersil, Marvell, MediaTek, Microchip, pureLiFi, Ralink, Realtek, RSI, Silicon Labs, ST, TI, Zydas, Quantenna, and virtual wireless drivers.

Control flow: Kconfig evaluation exposes the WLAN menu only when dependencies are satisfied. Vendor submenus and virtual drivers are included only when `WLAN` is enabled.

State and persistence: Build-time configuration only; no runtime state.

Dependencies and integration points: Integrates with the kernel Kconfig system and `drivers/net/wireless/Makefile` object selection. Vendor files define concrete driver symbols such as `ADM8211`.

Risks: Missing or reordered `source` lines hide entire vendor driver families. `default y` makes WLAN options broadly visible, increasing config surface. Dependency changes can affect many wireless drivers.

Test signals: `make menuconfig`/`oldconfig` visibility, all sourced vendor Kconfig paths existing, and build matrix with `CONFIG_WLAN=y/n`.
