## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/Makefile

Purpose: selects the Alchemy development board support objects for the MIPS build. It always builds the shared CPLD, platform, and board-family setup files, and conditionally includes suspend support when `CONFIG_PM` is enabled.

Important build entries: `obj-y += bcsr.o platform.o db1000.o db1200.o db1300.o db1550.o db1xxx.o` ensures the board detection and device registration code is linked into the platform. `obj-$(CONFIG_PM) += pm.o` gates the DB1x suspend userspace interface.

Control flow: as a makefile, it has no runtime flow. Its ordering ensures `db1xxx.o` and the per-board implementations are linked together so `board_setup()`, `arch_initcall()`, and `device_initcall()` hooks from those objects are present.

State and persistence: none directly. It controls which object code contributes runtime global state.

Dependencies and integration: depends on Kbuild, the parent Alchemy machine selection, and `CONFIG_PM`. The listed objects integrate with arch setup, platform devices, PCI setup, PM, and CPLD helpers.

Risks: adding board files without updating this list would leave init functions unlinked. Removing `pm.o` from the PM gate would expose suspend sysfs without PM support, while missing `bcsr.o` would break almost all board files.

Test signals: a configured Alchemy devboard kernel should contain the expected init symbols and boot to board-specific device registration. PM builds should create the `/sys/power/db1x` interface from `pm.c`.
