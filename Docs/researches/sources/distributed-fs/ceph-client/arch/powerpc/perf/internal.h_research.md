# sources/distributed-fs/ceph-client/arch/powerpc/perf/internal.h

Purpose: declares the architecture PMU initialization entry points used inside the PowerPC perf implementation for processor-specific PMU registration.

Important APIs/types/functions: `init_ppc970_pmu`, `init_power5_pmu`, `init_power5p_pmu`, `init_power6_pmu`, `init_power7_pmu`, `init_power8_pmu`, `init_power9_pmu`, `init_power10_pmu`, `init_power11_pmu`, and `init_generic_compat_pmu`, all returning `int` and marked `__init`.

Control flow and state: this header has no direct control flow. It provides prototypes so common setup code can attempt each CPU-family init routine and so family files can include common declarations without duplicating prototypes.

State and persistence behavior: no state is stored. The declarations describe boot-time registration functions whose implementations register global perf PMU descriptors.

Dependencies and integration points: included by several `arch/powerpc/perf/*` files, notably processor-specific PMU implementations and `isa207-common.h`. It depends on the kernel `__init` annotation being available through surrounding includes.

Risks: prototype drift would cause build failures or wrong init linkage. Missing a newly added family init would prevent central initialization code from seeing the implementation.

Test signals: PowerPC allmodconfig/defconfig builds, plus boot logs showing the correct CPU-family PMU is registered on supported hardware.
