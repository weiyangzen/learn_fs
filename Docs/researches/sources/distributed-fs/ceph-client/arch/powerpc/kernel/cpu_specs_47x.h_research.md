<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_47x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_47x.h

## Purpose
`cpu_specs_47x.h` defines CPU descriptors for 47x/476-class embedded PowerPC cores. It distinguishes key 476 variants and exposes the 47x MMU/cache model to the rest of the kernel.

## Important APIs, Types, And Functions
The header supplies `static struct cpu_spec cpu_specs[] __initdata`. Entries cover 476 DD2, 476fpe, 476 ISS, other 476 cores, and a generic 47x fallback. They use `CPU_FTRS_47X`, sometimes add `CPU_FTR_476_DD2`, expose BookE and FPU user features where applicable, set `MMU_FTR_TYPE_47x` with broadcast invalidation features, and use `machine_check_47x`.

## Control Flow
Selection is first-match PVR scanning. The DD2 exact `0xffffffff` match appears before broader 476 matches so the DD2 feature bit is preserved only for the known revision.

## State And Persistence
This is boot-time metadata copied into `cur_cpu_spec`; no direct runtime mutable state is kept in the table.

## Dependencies And Integration Points
The descriptors integrate with `cputable.c`, BookE MMU code, machine-check handling, user HWCAP generation, and TLB invalidation paths that depend on `MMU_FTR_USE_TLBIVAX_BCAST` and `MMU_FTR_LOCK_BCAST_INVAL`.

## Risks
The default generic 47x entry omits FPU and broadcast invalidation feature bits listed on specific entries, so unexpected PVRs may boot with conservative behavior. Mask mistakes can misclassify ISS or DD2 cores.

## Test Signals
Expected signals are correct CPU name on boot, FPU HWCAP on matching 476 variants, 128-byte D-cache line behavior, and stable SMP TLB invalidation on systems using broadcast invalidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_47x.h -->
