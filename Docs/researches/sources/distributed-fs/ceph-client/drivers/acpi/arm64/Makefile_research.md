# sources/distributed-fs/ceph-client/drivers/acpi/arm64/Makefile

## Purpose
Maps ARM64 ACPI Kconfig symbols to object files and always builds common DMA, init, and thermal CPU frequency hooks.

## Important APIs, Types, And Functions
Build entries include `agdi.o`, `apmt.o`, `ffh.o`, `gtdt.o`, `iort.o`, `mpam.o`, `cpuidle.o`, `amba.o`, plus unconditional `dma.o`, `init.o`, and `thermal_cpufreq.o`.

## Control Flow
Kbuild includes objects based on `obj-$(CONFIG_...)` or `obj-y`.

## State And Persistence
No runtime state; affects build products.

## Dependencies And Integration Points
Ties this directory to ARM64 ACPI, AMBA, processor idle, FFH, IORT, GTDT, APMT, AGDI, and MPAM feature symbols.

## Risks
Missing object mappings silently disable platform support even if symbols are selected. Unconditional objects must not depend on optional code without guards.

## Test Signals
Use build matrix coverage for each config symbol and verify unresolved symbols do not appear when optional objects are disabled.
