# sources/distributed-fs/ceph-client/drivers/pmdomain/Kconfig

Purpose: top-level Kconfig menu for Linux PM domain drivers in this source tree.

Important APIs/types/functions: declares the `"PM Domains"` menu and sources subdirectory Kconfig files for Actions, Amlogic, Apple, ARM, Broadcom, i.MX, Marvell, MediaTek, Qualcomm, Renesas, Rockchip, Samsung, ST, StarFive, Sunxi, Tegra, T-Head, TI, and Xilinx.

Control flow: no runtime control flow. During kernel configuration it exposes child PM-domain driver symbols and their dependency logic.

State and persistence: configuration choices persist in `.config` and determine which PM-domain providers are built.

Dependencies/integration: pairs with `drivers/pmdomain/Makefile`, which descends into the same subdirectories and builds `core.o`/`governor.o`.

Risks: missing a subdirectory source hides all drivers below it. The ordering is mostly organizational, but bad paths break menuconfig and randconfig.

Test signals: `make olddefconfig`, menuconfig navigation under PM Domains, and randconfig coverage of every sourced subdirectory.
