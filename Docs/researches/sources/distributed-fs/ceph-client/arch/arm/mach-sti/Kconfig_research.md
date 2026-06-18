# sources/distributed-fs/ceph-client/arch/arm/mach-sti/Kconfig

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-sti/Kconfig` is the Kconfig menu for STMicroelectronics STi platform support. It exposes build-time symbols `ARCH_STI`, `SOC_STIH407` and records dependencies/selects that decide whether this platform code, SMP support, timers, PM hooks, and board files are compiled into an ARM kernel.

## Important APIs, Types, and Functions
Build API symbols are `ARCH_STI`, `SOC_STIH407`. Dependencies are `ARCH_MULTI_V7`; `select` edges are `ARM_GIC`, `ST_IRQCHIP`, `ARM_GLOBAL_TIMER`, `CLKSRC_ST_LPC`, `PINCTRL`, `PINCTRL_ST`, `MFD_SYSCON`, `ARCH_HAS_RESET_CONTROLLER`, `HAVE_ARM_SCU if SMP`, `GPIOLIB`, `ARM_ERRATA_754322`, `ARM_ERRATA_764369 if SMP`, `ARM_ERRATA_775420`, `PL310_ERRATA_753970 if CACHE_L2X0`, `PL310_ERRATA_769419 if CACHE_L2X0`, `RESET_CONTROLLER`, `STIH407_RESET`; `imply` edges are none. These symbols are consumed by top-level ARM Kconfig and Kbuild to include the matching platform objects.

## Control Flow
Control flow is build-time configuration resolution. `make *config` evaluates prompts, dependencies, and selects; the resulting `.config` symbols drive Kbuild object inclusion and preprocessor conditionals in the ARM tree.

## State and Persistence Behavior
There is no runtime state. Persistent behavior is the build contract: selected symbols and object lists determine which code is present in the kernel image, and those choices persist through generated `.config`, built objects, and linked images.

## Dependencies and Integration Points
Dependencies include no C includes because this is Kconfig/Makefile data plus platform integration with DT-only machine selection, GIC/irqchip setup, SMP secondary boot through syscfg boot registers, PSCI fallback expectations, and OF platform device population. Cross-reference scans for visible symbols/compatibles found no extra direct hits beyond this source set. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: missing syscfg phandles, wrong secondary-start address programming, stale compatible strings, and SMP boot regressions when firmware or DT changes the CPU bring-up method. Additional file-specific risks: dependency/select mistakes silently change whole-platform build coverage.

## Test Signals
ARCH_STI builds, DT boot on stih415/stih416/stih407 class boards, secondary CPU online/offline logs, and dtbs_check coverage for `st,syscfg` and CPU enable-method data. Run `make ARCH=arm allnoconfig`, relevant defconfigs, and `scripts/kconfig/conf --syncconfig` to catch dependency cycles or unmet selects.
