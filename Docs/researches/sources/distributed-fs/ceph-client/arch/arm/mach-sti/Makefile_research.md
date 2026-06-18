# sources/distributed-fs/ceph-client/arch/arm/mach-sti/Makefile

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-sti/Makefile` is the Kbuild fragment for STMicroelectronics STi platform support. It maps configuration symbols to platform objects so the ARM build includes only the board, SMP, PM, reset, and helper code selected by Kconfig.

## Important APIs, Types, and Functions
Kbuild rules in this file are `obj-$(CONFIG_SMP) += platsmp.o`, `obj-$(CONFIG_ARCH_STI) += board-dt.o`. The important API is object membership: changing these lines changes which init, SMP, PM, hotplug, and assembly units are linked for a selected platform.

## Control Flow
Control flow is Kbuild evaluation. `obj-y` and `obj-$(CONFIG_...)` lines are expanded after Kconfig selection, then linked into `vmlinux` before the platform's runtime init functions can be called by the ARM boot path.

## State and Persistence Behavior
There is no runtime state. Persistent behavior is the build contract: selected symbols and object lists determine which code is present in the kernel image, and those choices persist through generated `.config`, built objects, and linked images.

## Dependencies and Integration Points
Dependencies include no C includes because this is Kconfig/Makefile data plus platform integration with DT-only machine selection, GIC/irqchip setup, SMP secondary boot through syscfg boot registers, PSCI fallback expectations, and OF platform device population. Cross-reference scans for visible symbols/compatibles found no extra direct hits beyond this source set. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: missing syscfg phandles, wrong secondary-start address programming, stale compatible strings, and SMP boot regressions when firmware or DT changes the CPU bring-up method. Additional file-specific risks: object-list mistakes compile cleanly for unrelated configs but drop platform hooks.

## Test Signals
ARCH_STI builds, DT boot on stih415/stih416/stih407 class boards, secondary CPU online/offline logs, and dtbs_check coverage for `st,syscfg` and CPU enable-method data. Build with the platform symbol enabled and disabled, then inspect `make V=1` or `nm vmlinux` for expected objects and entry symbols.
