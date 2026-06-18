<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_44x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_44x.h

## Purpose
`cpu_specs_44x.h` defines the PVR match table for 44x-family BookE PowerPC cores. It maps 440/460/APM821xx revisions to kernel CPU features, user-visible HWCAPs, MMU type, cache line sizes, setup routines, machine-check handlers, and platform strings.

## Important APIs, Types, And Functions
The file contributes `static struct cpu_spec cpu_specs[] __initdata`. Entries cover 440GR, 440EP, 440GRX, 440EPX, 440GP, 440GX, 440SP, 440SPe, 460EX, 460GT, 460SX, APM821XX, and a generic 44x fallback. It references setup helpers such as `__setup_cpu_440ep`, `__setup_cpu_440gx`, `__setup_cpu_440spe`, `__setup_cpu_460ex`, `__setup_cpu_460gt`, `__setup_cpu_460sx`, and machine-check handlers including `machine_check_4xx` and `machine_check_440A`.

## Control Flow
`identify_cpu()` scans this array in declaration order and picks the first `(pvr & pvr_mask) == pvr_value` match. The table intentionally places exact or revision-specific masks before broader defaults, including logical PVR variants for 440EP/440EPx.

## State And Persistence
The array is init-only metadata. Its selected entry is copied into the persistent `the_cpu_spec` object by `cputable.c`, after which the table can be discarded.

## Dependencies And Integration Points
It depends on 44x CPU feature macros, MMU feature macros, machine-check implementations, and CPU setup assembly/C helpers. The user-visible flags feed `AT_HWCAP`, and cache sizes feed cache maintenance code.

## Risks
PVR mask ordering is fragile: a broad match before a revision-specific entry would select the wrong setup routine or omit FPU exposure. The default entry can hide unsupported silicon by booting as generic 44x. Incorrect machine-check selection risks poor fault diagnosis.

## Test Signals
Booting each supported SoC should report the right CPU name and platform, expose FPU HWCAP only where listed, use 32-byte I/D cache lines, and survive 44x machine-check and cache/TLB invalidation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_44x.h -->
