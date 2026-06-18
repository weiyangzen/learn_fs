<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs.h

## Purpose
`cpu_specs.h` is the compile-time selector for PowerPC CPU specification tables. It includes exactly the CPU descriptor header(s) needed by the configured kernel family so `cputable.c` can expose a single `cpu_specs[]` array to early CPU identification.

## Important APIs, Types, And Functions
The file declares no functions or types. Its important contract is conditional inclusion of `cpu_specs_47x.h`, `cpu_specs_44x.h`, `cpu_specs_8xx.h`, `cpu_specs_e500mc.h`, `cpu_specs_85xx.h`, `cpu_specs_book3s_32.h`, and `cpu_specs_book3s_64.h` based on `CONFIG_*` symbols.

## Control Flow
Control flow is preprocessor-only. Build configuration chooses mutually exclusive or additive CPU families; for example 47x wins over 44x, e500mc wins over 85xx, and Book3S 32/64 tables are included for their respective builds.

## State And Persistence
No runtime state exists here. The included file contributes `static struct cpu_spec cpu_specs[] __initdata`, which is consumed during boot and later discarded with other init data.

## Dependencies And Integration Points
It is included directly by `cputable.c`. The correctness of `identify_cpu()` depends on this include graph producing a non-empty `cpu_specs` array with a default or exact PVR match appropriate for the target architecture.

## Risks
Configuration overlap can produce duplicate `cpu_specs` definitions if new include branches are added carelessly. Missing a configured CPU family causes `BUILD_BUG_ON(!ARRAY_SIZE(cpu_specs))` or a boot-time `BUG()` if no PVR match exists.

## Test Signals
Build coverage across PowerPC subarchitectures is the main signal. Runtime boot logs should identify the expected CPU name/platform and avoid falling into a generic default unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs.h -->
