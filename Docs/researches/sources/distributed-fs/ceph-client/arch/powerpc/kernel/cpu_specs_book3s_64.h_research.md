<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_64.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_64.h

## Purpose
`cpu_specs_book3s_64.h` defines the 64-bit Book3S PVR table for PPC970, POWER5 through POWER11, Cell, and PA6T processors. It is the static fallback and compatibility-mode CPU description path used when CPU features are not built dynamically from device tree.

## Important APIs, Types, And Functions
The file defines common user feature macro groups for PPC64 and POWER generations, then supplies `static struct cpu_spec cpu_specs[] __initdata`. Important callbacks include PPC970 setup/restore, POWER7/8/9/10 setup and restore, PA6T setup/restore, and early machine-check handlers for POWER7-10. Entries set MMU feature groups, cache line sizes, PMC counts/types, platform strings, user `PPC_FEATURE*` and `PPC_FEATURE2*` flags, and POWER9 DD revision workaround feature sets.

## Control Flow
`identify_cpu()` scans in order. Exact architected compatibility PVR entries, raw PVR entries, and DD-specific POWER9 entries rely on specific-before-generic ordering. PPC970MP DD1.0 is matched exactly before the broader PPC970MP entry to avoid deep-nap setup.

## State And Persistence
The init-only table is copied into `the_cpu_spec`. The selected fields persist as the authoritative CPU feature, MMU feature, PMU, machine-check, setup, and restore contract for the booted kernel.

## Dependencies And Integration Points
This table integrates with `cpu_setup_ppc970.S`, POWER setup routines, machine-check real-mode handlers, MMU selection, perf, feature fixups, and user HWCAP export. It also preserves compatibility-mode PMU information when logical PVR values override real PVR values in `cputable.c`.

## Risks
Incorrect PVR matching can expose unsupported ISA facilities to userspace or miss processor errata bits. POWER9 revision masks are especially sensitive. Adding POWER generation support requires keeping user feature macros, setup/restore hooks, PMU state, and machine-check handlers consistent.

## Test Signals
Signals include booting under raw and architected PVR modes, correct platform strings for POWER generations, accurate HWCAP2 ISA bits, PMU availability, machine-check handler selection, and PPC970 HV-mode behavior through the referenced setup routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_64.h -->
