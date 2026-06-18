# sources/distributed-fs/ceph-client/drivers/thermal/st/Kconfig

Purpose: Kconfig entries for STMicroelectronics thermal drivers.

Important symbols: `ST_THERMAL` enables the shared STi thermal core; `ST_THERMAL_MEMMAP` selects `ST_THERMAL` and builds memory-mapped STi sensor support; `STM32_THERMAL` builds the STM32 thermal framework driver and depends on `MACH_STM32MP157`, defaulting to yes for that machine.

Control flow and integration: symbols map to objects in `st/Makefile`. `ST_THERMAL_MEMMAP` uses the shared exported functions from `st_thermal.c`, while `STM32_THERMAL` is independent and implemented in `stm_thermal.c`.

State and persistence: build-time only.

Risks and test signals: `ST_THERMAL_MEMMAP` selects rather than depends on the shared core, which is correct for its exported helpers. Test all three symbols as modules and built-ins, especially the composite dependency between `st_thermal.o` and `st_thermal_memmap.o`.
