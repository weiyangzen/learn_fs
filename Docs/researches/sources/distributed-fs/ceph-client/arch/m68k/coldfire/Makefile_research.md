# sources/distributed-fs/ceph-client/arch/m68k/coldfire/Makefile

Purpose: ColdFire CPU, timer, board, PCI, GPIO, and startup object selection.

The file sets optional debug assembler flags, builds common ColdFire objects (`cache.o`, `clk.o`, `device.o`, `entry.o`, `vectors.o`) for `CONFIG_COLDFIRE`, and chooses CPU-family-specific setup, interrupt controller, and reset objects based on symbols such as `CONFIG_M520x`, `CONFIG_M527x`, `CONFIG_M53xx`, and `CONFIG_M5441x`. It also selects PIT/timer variants, board files such as `amcore.o`, `firebee.o`, and `stmark2.o`, optional PCI, plus always-built `gpio.o` and `head.o`.

Control flow is Kbuild-only. The build graph enforces that each selected ColdFire SOC gets a compatible interrupt controller and reset path.

State/persistence: no runtime state in the Makefile; linked object selection determines available platform devices and low-level CPU code.

Dependencies include ColdFire Kconfig symbols and the corresponding source files. Integration is through top-level `arch/m68k/Kbuild` when `CONFIG_COLDFIRE` is enabled.

Risks and test signals: wrong pairing of SOC file and interrupt controller can compile but fail at boot. Validate representative ColdFire defconfigs, especially combinations for timer choice, PCI, and board files such as AMCORE.
