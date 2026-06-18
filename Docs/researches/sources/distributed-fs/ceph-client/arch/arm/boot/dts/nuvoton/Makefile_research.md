# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nuvoton/Makefile

Purpose: Kbuild manifest for Nuvoton ARM BMC device trees. It covers NPCM7xx boards and the older WPCM450 board family.

Important APIs/types/functions: `dtb-$(CONFIG_ARCH_NPCM7XX) +=` lists five NPCM730/NPCM750 board DTBs: GSJ, GBS, Kudo, EVB, and RunBMC Olympus. `dtb-$(CONFIG_ARCH_WPCM450) +=` lists `nuvoton-wpcm450-supermicro-x9sci-ln4f.dtb`.

Control flow: Kbuild evaluates the two architecture config conditions and appends matching DTB targets.

State and persistence: no state. Compiled DTBs persist hardware descriptions for BMC firmware or kernel boot.

Dependencies and integration: depends on Nuvoton architecture Kconfig symbols, matching DTS files, the device tree compiler, and the ARM DTS build hierarchy.

Risks: BMC DTBs frequently describe board management hardware where missing GPIO, I2C, or LPC descriptions can disable platform control. This Makefile's direct risk is target omission or stale filenames. Test with `make ARCH=arm dtbs` for NPCM7xx/WPCM450 configs and targeted DTB builds after renames.
