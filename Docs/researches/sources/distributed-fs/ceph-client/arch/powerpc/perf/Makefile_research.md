
# sources/distributed-fs/ceph-client/arch/powerpc/perf/Makefile

## Purpose

This Makefile wires PowerPC perf support into the kernel build. It selects common callchain/perf register objects, Book3S PMU cores and model drivers, Freescale embedded PMUs, hypervisor PMUs, PowerNV/KVM/VPA PMUs, 8xx PMU support, and architecture-width-specific objects.

## Important Rules

- Always builds `callchain.o`, `callchain_$(BITS).o`, and `perf_regs.o`.
- Adds `callchain_32.o` under `CONFIG_COMPAT`.
- Adds `core-book3s.o` under `CONFIG_PPC_PERF_CTRS`.
- Adds 64-bit Book3S model drivers, ISA 2.07 helpers, `generic-compat-pmu.o`, Power10, and `bhrb.o` through `obj64-*`.
- Adds `mpc7450-pmu.o` for 32-bit Book3S through `obj32-*`.
- Adds `imc-pmu.o`, Freescale embedded core/model drivers, hypervisor counter drivers, VPA PMU, KVM HV PMU, and 8xx PMU based on their config symbols.
- Appends `$(obj64-y)` only for `CONFIG_PPC64` and `$(obj32-y)` only for `CONFIG_PPC32`.

## Control Flow

Kbuild evaluates config symbols and architecture width, expanding the appropriate object lists into `obj-y`. There is no runtime control flow, but build-time selection controls which PMU registration initcalls are linked into the kernel.

## State And Persistence

No runtime state. Its persistent effect is build composition: enabling or disabling symbols changes the linked perf implementation set.

## Dependencies And Integration Points

The file integrates with Kbuild, PowerPC config symbols, and source files in this directory. Ordering matters because multiple PMU initcalls may attempt registration, and the selected object set determines which registration paths are available.

## Risks And Edge Cases

Duplicate inclusion risk exists when compatibility or width-specific objects overlap; here `callchain_32.o` can be built both as native 32-bit and compat support intentionally depending on config. Missing an object from the correct `obj32`/`obj64` list can cause unresolved symbols only for specific architecture builds.

## Test Signals

Useful signals are allmodconfig/allyesconfig and targeted PPC32/PPC64 builds for `CONFIG_COMPAT`, `CONFIG_PPC_PERF_CTRS`, `CONFIG_FSL_EMB_PERF_EVENT`, `CONFIG_HV_PERF_CTRS`, `CONFIG_PPC_8xx`, and KVM/PowerNV combinations.
