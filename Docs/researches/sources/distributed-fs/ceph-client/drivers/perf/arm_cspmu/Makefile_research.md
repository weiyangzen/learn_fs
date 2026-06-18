# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Makefile

Purpose: Connects the CoreSight PMU Kconfig symbols to object files built by Kbuild.

Important APIs and types: Builds `arm_cspmu_module.o` when `CONFIG_ARM_CORESIGHT_PMU_ARCH_SYSTEM_PMU` is set, with `arm_cspmu_module-y := arm_cspmu.o`. Builds `nvidia_cspmu.o` and `ampere_cspmu.o` under their respective vendor Kconfig symbols.

Control flow: Kbuild includes the listed objects as built-ins or modules according to each config symbol. The generic object is wrapped in a module name distinct from the source file, while vendor backends build as direct module objects.

State and persistence: No runtime state. It persists build linkage and module object naming.

Dependencies and integration points: Integrates with `drivers/perf` Kbuild and the Kconfig symbols in the same directory. Runtime vendor backend loading in `arm_cspmu.c` expects module names `nvidia_cspmu` and `ampere_cspmu`, matching this Makefile.

Risks: Renaming vendor objects without updating `module_name` in `arm_cspmu.c` would break request-module/deferred-probe behavior. Adding source files to the generic module requires extending `arm_cspmu_module-y`.

Test signals: Build the generic driver as built-in and module, build each vendor backend as module, and verify `modprobe nvidia_cspmu`/`modprobe ampere_cspmu` satisfies generic deferred probes.
