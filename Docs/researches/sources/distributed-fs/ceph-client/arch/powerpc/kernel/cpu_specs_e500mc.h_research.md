<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_e500mc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_e500mc.h

## Purpose
`cpu_specs_e500mc.h` describes e500mc, e5500, and e6500 BookE CPUs. It is the newer FSL embedded CPU table used instead of the classic 85xx e500 table when `CONFIG_PPC_E500MC` is enabled.

## Important APIs, Types, And Functions
It defines `COMMON_USER_BOOKE` differently for PPC32 and PPC64, then contributes `static struct cpu_spec cpu_specs[] __initdata`. Entries reference `__setup_cpu_e500mc`, `__setup_cpu_e5500`, `__setup_cpu_e6500`, 64-bit restore callbacks for e5500/e6500, `machine_check_e500mc`, and CPU-down flush hooks.

## Control Flow
PVR high-16-bit matches select e500mc, e5500, or e6500. The e500mc entry is present only for PPC32 builds, while e5500/e6500 support both 32-bit and 64-bit configurations with restore callbacks excluded on PPC32.

## State And Persistence
As with other CPU spec tables, this is init-only metadata copied into `cur_cpu_spec`. The selected descriptor controls persistent runtime feature checks, cache line sizing, PMU count, and CPU hotplug flush behavior.

## Dependencies And Integration Points
It integrates with FSL BookE MMU features including `MMU_FTR_BIG_PHYS` and `MMU_FTR_USE_TLBILX`, user HWCAPs for FPU/Altivec/ISEL, machine-check handling, and platform strings `ppce500mc`, `ppce5500`, and `ppce6500`.

## Risks
The file has no generic default, so unsupported PVRs fail identification. Conditional PPC32/PPC64 fields must stay aligned with available assembly helpers. Incorrect user features could mislead applications about FPU, Altivec, 64-bit, or BookE support.

## Test Signals
Boot tests should identify exact CPU names, expose ISEL and FPU/Altivec flags as appropriate, use 64-byte I/D cache lines, initialize four or six PMCs, and exercise CPU restore/down-flush paths on SMP or hotplug-capable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_e500mc.h -->
