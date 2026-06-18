# sources/distributed-fs/ceph-client/drivers/base/Makefile

## Purpose
Specifies which driver-core objects are built into the kernel or conditionally included based on configuration symbols. It is the build manifest for `drivers/base`.

## Important APIs, Types, And Functions
Core built-in objects include `component.o`, `core.o`, `bus.o`, `dd.o`, `syscore.o`, `driver.o`, `class.o`, `platform.o`, `cpu.o`, `firmware.o`, `init.o`, `map.o`, `devres.o`, `attribute_container.o`, `transport_class.o`, `topology.o`, `container.o`, `property.o`, `cacheinfo.o`, `swnode.o`, and `faux.o`. Conditional objects include `auxiliary.o`, `auxiliary_sysfs.o`, `devtmpfs.o`, `module.o`, `node.o`, `memory.o`, `hypervisor.o`, `soc.o`, `devcoredump.o`, `platform-msi.o`, `arch_topology.o`, `arch_numa.o`, and tracing.

## Control Flow
Kbuild reads `obj-y` and `obj-$(CONFIG_...)` assignments to compile/link objects. Subdirectories `power/`, `firmware_loader/`, `regmap/`, `pinctrl/`, and `test/` are included according to unconditional or conditional entries. `ccflags-$(CONFIG_DEBUG_DRIVER)` adds `-DDEBUG`, and `CFLAGS_trace.o` adds an include path.

## State And Persistence
No runtime state is stored. The file shapes the built object graph based on `.config`.

## Dependencies And Integration Points
Directly consumes symbols from `drivers/base/Kconfig` and other subsystem Kconfigs. It ties `attribute_container.c`, `auxiliary.c`, `auxiliary_sysfs.c`, `arch_topology.c`, and `arch_numa.c` into the build when selected.

## Risks And Edge Cases
`auxiliary_sysfs.o` is built only when both sysfs is enabled and modules are supported, so IRQ sysfs helper availability depends on more than `CONFIG_AUXILIARY_BUS`. Missing include path for trace would break `define_trace.h` usage.

## Test Signals
Object inclusion under relevant configs, allmodconfig/allyesconfig builds, no unresolved symbols when `CONFIG_MODULES` or `CONFIG_SYSFS` are disabled, and debug-driver builds with `-DDEBUG` are key checks.
