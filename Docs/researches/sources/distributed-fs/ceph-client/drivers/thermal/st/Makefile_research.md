# sources/distributed-fs/ceph-client/drivers/thermal/st/Makefile

Purpose: Kbuild mapping for ST thermal drivers.

Important entries: `CONFIG_ST_THERMAL` builds `st_thermal.o`, `CONFIG_ST_THERMAL_MEMMAP` adds `st_thermal_memmap.o`, and `CONFIG_STM32_THERMAL` builds `stm_thermal.o`.

Control flow and integration: the shared STi core is built as its own object and exports registration/PM helpers for the memory-mapped variant. STM32 is separate.

State, risks, and test signals: no runtime state. Risks are limited to Kconfig/object drift and module dependency between memmap and core. Compile with `ST_THERMAL_MEMMAP=m` and ensure exported symbols resolve.
