# sources/distributed-fs/ceph-client/arch/arm/mach-ux500/Makefile

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-ux500/Makefile` is the Kbuild fragment for ST-Ericsson Ux500/DB8500 platform support. It maps configuration symbols to platform objects so the ARM build includes only the board, SMP, PM, reset, and helper code selected by Kconfig.

## Important APIs, Types, and Functions
Kbuild rules in this file are `obj-y := pm.o`, `obj-$(CONFIG_UX500_SOC_DB8500) += cpu-db8500.o`, `obj-$(CONFIG_SMP) += platsmp.o`. The important API is object membership: changing these lines changes which init, SMP, PM, hotplug, and assembly units are linked for a selected platform.

## Control Flow
Control flow is Kbuild evaluation. `obj-y` and `obj-$(CONFIG_...)` lines are expanded after Kconfig selection, then linked into `vmlinux` before the platform's runtime init functions can be called by the ARM boot path.

## State and Persistence Behavior
There is no runtime state. Persistent behavior is the build contract: selected symbols and object lists determine which code is present in the kernel image, and those choices persist through generated `.config`, built objects, and linked images.

## Dependencies and Integration Points
Dependencies include no C includes because this is Kconfig/Makefile data plus platform integration with DB8500 DT machine setup, PRCMU-driven SMP boot, SCU/TWD local timer handling, cpuidle registration, PM domain creation, and OF platform population with legacy auxdata. Cross-reference scans for visible symbols/compatibles found no extra direct hits beyond this source set. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: PRCMU wakeup mailbox changes, incorrect SCU base discovery, stale auxdata names, cpuidle registration without required firmware services, and hotplug races around secondary boot flags. Additional file-specific risks: object-list mistakes compile cleanly for unrelated configs but drop platform hooks.

## Test Signals
Ux500 multiplatform builds, DB8500 DT boot, CPU1 bring-up, cpuidle visibility, platform device probe logs, and PM-domain attachment checks. Build with the platform symbol enabled and disabled, then inspect `make V=1` or `nm vmlinux` for expected objects and entry symbols.
