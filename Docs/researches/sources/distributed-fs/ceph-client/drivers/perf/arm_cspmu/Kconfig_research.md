# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Kconfig

Purpose: Defines build configuration options for the generic ARM CoreSight Architecture PMU driver and its NVIDIA and Ampere vendor/implementer backends.

Important APIs and types: Provides tristate symbols `ARM_CORESIGHT_PMU_ARCH_SYSTEM_PMU`, `NVIDIA_CORESIGHT_PMU_ARCH_SYSTEM_PMU`, and `AMPERE_CORESIGHT_PMU_ARCH_SYSTEM_PMU`. The generic driver depends on `ARM64 || COMPILE_TEST`; vendor options depend on the generic symbol.

Control flow: Kconfig selection controls whether `arm_cspmu_module.o`, `nvidia_cspmu.o`, and `ampere_cspmu.o` are compiled as built-in, module, or omitted. Vendor backend symbols cannot be enabled unless the generic CoreSight PMU architecture driver is enabled.

State and persistence: No runtime state. The file persists build-time feature availability and module dependency relationships.

Dependencies and integration points: Consumed by the perf drivers Makefile and kernel configuration system. Help text clarifies this is the CoreSight PMU architecture, not CoreSight self-hosted tracing, and notes Ampere's initial MCU PMU focus.

Risks: Vendor backend dependencies must match the runtime registration model in `arm_cspmu.c`; if a backend can be built without the generic driver, symbols such as `arm_cspmu_impl_register()` would fail. The Ampere stanza has whitespace inconsistency but no behavioral impact.

Test signals: `make menuconfig` visibility, all three tristate combinations, module dependency/modprobe behavior, and compile-test builds on non-ARM64 validate this file.
