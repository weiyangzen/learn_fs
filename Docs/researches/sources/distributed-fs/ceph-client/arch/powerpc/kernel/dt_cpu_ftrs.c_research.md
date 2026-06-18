<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dt_cpu_ftrs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dt_cpu_ftrs.c

## Purpose
`dt_cpu_ftrs.c` builds a PowerPC CPU specification dynamically from device-tree CPU feature nodes. It is the firmware-described alternative to static PVR tables for modern POWER systems, enabling hardware facilities, MMU modes, PMU setup, machine-check handlers, user HWCAPs, and processor errata bits.

## Important APIs, Types, And Functions
Core types are `struct dt_cpu_feature` and `struct dt_cpu_feature_match`. Important globals include `hv_mode`, `system_registers`, `init_pmu_registers`, `dt_cpu_name`, `base_cpu_spec`, `using_dt_cpu_ftrs`, `enable_unknown`, `nr_dt_cpu_features`, and `dt_cpu_features`. Public functions are `dt_cpu_ftrs_in_use()`, `dt_cpu_ftrs_init()`, and `dt_cpu_ftrs_scan()`. Major helpers include `cpufeatures_setup_cpu()`, `feat_enable*()` variants, `cpufeatures_process_feature()`, `cpufeatures_cpu_quirks()`, `process_cpufeatures_node()`, and `cpufeatures_deps_enable()`.

## Control Flow
Early init verifies the FDT, finds an `ibm,powerpc-cpu-features` node with `isa`, honors `dt_cpu_ftrs=off`, initializes `base_cpu_spec`, and marks the feature path active. The scan callback allocates a memblock array for subnodes, sets ISA baseline bits, parses each feature's privilege/support/FSCR/HFSCR/HWCAP properties, immediately enables independent features, then recursively enables dependency-gated features. Known names dispatch through `dt_cpu_feature_match_table`; unknown features can be enabled by generic FSCR/HFSCR/HWCAP recipes unless `dt_cpu_ftrs=known` was specified. Finish applies PVR-specific quirks, captures LPCR/HFSCR/FSCR/PCR for CPU restore, sets display name, logs final features, and frees the memblock array.

## State And Persistence
The dynamic CPU spec persists through `cur_cpu_spec`. `system_registers` stores restore-time SPR values, and `init_pmu_registers` persists a callback for secondary CPU restore. The temporary parsed feature array is freed after scanning.

## Dependencies And Integration Points
It depends on libfdt/flat DT scanning, memblock, CPU/MMU feature macros, machine-check handlers, PMU SPRs, HFSCR/FSCR/PCR/LPCR programming, command-line parsing, and `set_cur_cpu_spec()`.

## Risks
Firmware property validation is strict but recursive dependencies can silently disable dependent features. Unknown feature enablement can expose HWCAPs based on firmware recipes without kernel-specific code. SPR programming differs between HV and guest modes. PVR quirks for POWER9 errata must remain synchronized with static tables.

## Test Signals
Test by booting POWER8-POWER11 systems with DT CPU features, toggling `dt_cpu_ftrs=off` and `dt_cpu_ftrs=known`, checking final feature logs and HWCAPs, validating radix/hash MMU selection, PMU operation, secondary CPU restore, machine-check handler selection, and POWER9 errata flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dt_cpu_ftrs.c -->
