# sources/distributed-fs/ceph-client/drivers/dio/Makefile

Purpose: builds the legacy DIO bus support objects into the kernel.

Important APIs/types/functions: declares `obj-y := dio.o dio-driver.o dio-sysfs.o`.

Control flow: no runtime flow. The three objects are always linked when this directory participates in the architecture build.

State and persistence behavior: none beyond build output.

Dependencies and integration points: integrates bus enumeration (`dio.o`), driver-core registration (`dio-driver.o`), and sysfs attributes (`dio-sysfs.o`) into one built-in subsystem for HP300/m68k DIO support.

Risks and test signals: because this is `obj-y`, architecture Makefiles/Kconfig must gate directory inclusion. Test signal is successful HP300/m68k builds with all three object files present and no missing DIO symbols.
