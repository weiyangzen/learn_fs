# sources/distributed-fs/ceph-client/drivers/platform/mips/Makefile

## Purpose
Kbuild fragment mapping MIPS platform driver config symbols to object files.

## Important APIs, Types, And Targets
`obj-$(CONFIG_CPU_HWMON) += cpu_hwmon.o`, `obj-$(CONFIG_RS780E_ACPI) += rs780e-acpi.o`, and `obj-$(CONFIG_LS2K_RESET) += ls2k-reset.o` are the complete build rules.

## Control Flow
There is no runtime control flow. Kbuild includes each object when its corresponding Kconfig symbol resolves to `y` or `m`.

## State, Dependencies, Integration, Risks, Tests
State is build configuration only. The file depends on the symbols defined in the adjacent Kconfig and on matching source files in the same directory. Integration is the Linux Kbuild object-selection contract. Risks are stale symbol/object names, missing object sources, or Kconfig options that cannot be enabled in expected build matrices. Test signals are `make drivers/platform/mips/`, config toggles for each symbol, and allmodconfig/allyesconfig object inclusion.
