<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.h

Purpose: AMS Delta board constants shared by board setup and FIQ code. It defines GPIO pin numbers for keyboard, modem, hook switch, NAND ready/busy, and other board signals.

Important APIs/types/functions: The file provides macros such as `AMS_DELTA_GPIO_PIN_KEYBRD_DATA`, `KEYBRD_CLK`, `MODEM_IRQ`, `HOOK_SWITCH`, and `NAND_RB`.

Control flow, state, and persistence: There is no runtime state; these constants align board platform data with low-level FIQ assembly masks.

Dependencies and integration points: The file provides macros such as `AMS_DELTA_GPIO_PIN_KEYBRD_DATA`, `KEYBRD_CLK`, `MODEM_IRQ`, `HOOK_SWITCH`, and `NAND_RB`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are off-by-one GPIO definitions causing wrong FIQ/IRQ behavior. Test by validating keyboard, modem IRQ, hook switch, and NAND ready GPIO routing on hardware.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 42 lines, 1786 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.h -->
