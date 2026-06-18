<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_85xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_85xx.h

## Purpose
`cpu_specs_85xx.h` describes classic Freescale e500/e500v2 85xx CPUs for BookE kernels that are not using the newer e500mc table. It maps PVRs to SPE/EFP capabilities, FSL embedded MMU features, setup routines, and machine-check behavior.

## Important APIs, Types, And Functions
It defines `COMMON_USER_BOOKE` and `static struct cpu_spec cpu_specs[] __initdata`. Entries include e500, e500v2, and a generic E500 fallback. Specific entries reference `__setup_cpu_e500v1`, `__setup_cpu_e500v2`, `machine_check_e500`, `cpu_down_flush_e500v2`, and set PMC counts.

## Control Flow
`identify_cpu()` scans exact high-16-bit PVR matches before the zero-mask default. e500v2 adds double-precision EFP compatibility, big physical address support, and a CPU-down flush hook relative to e500.

## State And Persistence
The table itself is discarded after init. The chosen feature and callback fields persist in `the_cpu_spec` and guide MMU, machine-check, perf, and CPU hotplug behavior.

## Dependencies And Integration Points
It integrates with FSL BookE MMU support, SPE/EFP user ABI exposure, e500 CPU setup assembly, and platform strings such as `ppc8540`/`ppc8548`.

## Risks
The generic fallback can boot unrecognized 85xx CPUs with incomplete setup callbacks or feature exposure. Incorrect user feature flags would affect userspace ABI detection for SPE/EFP code.

## Test Signals
Boot on e500/e500v2 should identify the exact name, expose the expected `PPC_FEATURE_HAS_SPE_COMP` and EFP flags, initialize four PMCs on matched entries, and survive CPU offline flush and machine-check tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_85xx.h -->
