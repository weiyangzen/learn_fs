# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/amd.c

## Purpose
Contains x86 AMD/Hygon helper logic for decoding hardware P-states, boost state counts, and AMD pstate performance/frequency data for cpupower reports.

## Important APIs, Types, and Functions
Important elements are `union core_pstate`, `get_did`, `get_cof`, `decode_pstates`, `amd_pci_get_num_boost_states`, `amd_pstate_boost_init`, and `amd_pstate_show_perf_and_freq`. It reads MSRs `MSR_AMD_PSTATE_LIMIT`/`MSR_AMD_PSTATE*`, PCI D18F4 boost registers, cpufreq sysfs AMD pstate files, and ACPI CPPC values.

## Control Flow, State, and Persistence
`decode_pstates` checks AMD hardware pstate capability, reads the pstate limit, folds in boost states, reads each pstate MSR, skips disabled entries, and computes MHz based on family-specific FID/DID formats. AMD pstate boost support compares highest and nominal performance, then active state compares cpufreq max with AMD pstate max. The file keeps no persistent state.

## Dependencies and Integration Points
Depends on x86-only CPUID capabilities in `cpupower_cpu_info`, `read_msr`, libpci helpers, cpufreq sysfs access, and `acpi_cppc.h`. It feeds `frequency-info --boost` and AMD pstate performance output.

## Risks and Test Signals
Family-specific bitfield decoding is brittle for new CPU families. PCI access assumes domain/bus/slot/function layout used by older AMD platforms. Missing MSR or sysfs access causes feature output to disappear. Validate on pre-family-17h, family 17h+, family 1Ah+, AMD pstate enabled systems, Hygon systems, and non-x86 builds where the file is excluded.
