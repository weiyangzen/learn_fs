<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cputable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cputable.c

## Purpose
`cputable.c` owns PowerPC CPU identification from static PVR tables. It selects a `cpu_spec`, copies it into permanent storage, invokes processor setup when required, records the base platform string, and initializes static keys for CPU/MMU feature checks.

## Important APIs, Types, And Functions
Important globals are `the_cpu_spec`, exported `cur_cpu_spec`, and `powerpc_base_platform`. Key functions are `set_cur_cpu_spec()`, `setup_cpu_spec()`, `identify_cpu()`, `identify_cpu_name()`, `cpu_feature_keys_init()`, and `mmu_feature_keys_init()`. The file includes `cpu_specs.h`, which supplies the active `cpu_specs[]` table.

## Control Flow
`identify_cpu()` relocates the table pointer, linearly scans PVR masks, and calls `setup_cpu_spec()` for the first match. Setup copies the descriptor using `memcpy`, preserves PMU fields and PMAO bug bits when logical PVR overrides a real PVR-derived spec, enables 32-bit KUAP by default when configured, records the platform string on first call, and invokes `cpu_setup` for PPC64/BookE. Static-key init disables jump labels for features absent from `cur_cpu_spec`.

## State And Persistence
The selected CPU descriptor is copied into `the_cpu_spec` marked `__ro_after_init`; `cur_cpu_spec` points to it. `powerpc_base_platform` persists the platform string of the real PVR. Static key arrays persist for optimized feature tests.

## Dependencies And Integration Points
It depends on early relocation macros, `struct cpu_spec`, feature bit definitions, CPU setup callbacks, OF/platform setup, and jump label support. It is used by early boot, dynamic device-tree CPU features for naming, and runtime `cpu_has_feature()`/`mmu_has_feature()` fast paths.

## Risks
No matching PVR calls `BUG()`, so table omissions are fatal. Copying and relocation happen very early; KASAN and relocation comments explain why simple struct assignment is avoided. Static keys must be initialized after `cur_cpu_spec` is final or feature checks can be wrong.

## Test Signals
Boot logs should show correct CPU name/platform, feature fixups should match selected bits, jump-label feature checks should agree with `cur_cpu_spec`, and compatibility logical PVR boots should retain real PMU information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cputable.c -->
