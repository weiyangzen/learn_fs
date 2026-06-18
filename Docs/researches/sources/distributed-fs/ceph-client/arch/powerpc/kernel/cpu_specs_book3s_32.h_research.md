<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_32.h

## Purpose
`cpu_specs_book3s_32.h` is the 32-bit Book3S/classic PowerPC CPU descriptor table. It covers 603/604/G2/e300, 740/750, and G4-class 7400/7410/745x/744x variants, mapping PVR revisions to feature workarounds, PMU types, setup routines, HWCAPs, and MMU feature flags.

## Important APIs, Types, And Functions
The file defines `COMMON_USER` and `static struct cpu_spec cpu_specs[] __initdata`. It references setup routines such as `__setup_cpu_603`, `__setup_cpu_604`, `__setup_cpu_750`, `__setup_cpu_750cx`, `__setup_cpu_750fx`, `__setup_cpu_7400`, `__setup_cpu_7410`, and `__setup_cpu_745x`. It also selects `machine_check_generic` or `machine_check_83xx`, IBM/G4 PMC types, high-BAT features, HPTE table support, Altivec compatibility, and variant-specific CPU feature macros like `CPU_FTRS_750FX2` or `CPU_FTRS_7450_20`.

## Control Flow
The array is ordered from exact revision matches to broad family matches and finally a generic PPC default for the 604 section. `identify_cpu()` performs linear first-match PVR selection, so comments about specific revisions are part of the functional contract.

## State And Persistence
The table is `__initdata`; selected fields persist in `the_cpu_spec`. User feature fields become visible to userspace through aux vectors, while MMU/cache fields influence low-level memory behavior.

## Dependencies And Integration Points
It integrates with classic 32-bit Book3S boot, feature fixups, PMU/perf, machine-check paths, cache maintenance, and processor-specific setup files. `CONFIG_PPC_BOOK3S_603`, `CONFIG_PPC_BOOK3S_604`, and `CONFIG_PPC_83xx` gate table portions.

## Risks
Ordering mistakes are high risk because many entries share high PVR bits but require revision-specific feature masks, especially 750FX/7450/7455/7447 families. The default generic PPC entry can mask missing support. Incorrect HWCAP Altivec or FPU exposure changes userspace ABI behavior.

## Test Signals
Test signals include boot identification for old 32-bit systems, correct `/proc/cpuinfo` platform, HWCAP FPU/Altivec flags, PMU counter availability, and regression tests for feature fixups and machine-check handling on emulated or real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_32.h -->
