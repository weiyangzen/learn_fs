# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/helpers.h

## Purpose
Central utility header for cpupower internationalization, global process state, CPU capability declarations, x86-only MSR/PCI/AMD helper declarations, non-x86 stubs, and common CPU-state output helpers.

## Important APIs, Types, and Functions
Key definitions include `_`/`N_` gettext macros, global `run_as_root`, `base_cpu`, `cpus_chosen`, `online_cpus`, `offline_cpus`, `enum cpupower_cpu_vendor`, `CPUPOWER_CAP_*` flags, `CPUPOWER_AMD_CPBDIS`, `MAX_HW_PSTATES`, `struct cpupower_cpu_info`, and prototypes for CPU info, boost, MSR, PCI, AMD pstate, CPUID, CPU state, and `print_speed`.

## Control Flow, State, and Persistence
This file has compile-time control flow through x86 vs non-x86 sections. On non-x86, hardware-specific functions are inline stubs returning failure or zero so generic code can compile while features degrade gracefully. It declares process-wide state owned by `cpupower.c`.

## Dependencies and Integration Points
Included by nearly every cpupower utility source and monitor. It bridges libcpupower headers, libpci, gettext, and platform-specific helper implementations.

## Risks and Test Signals
Global state makes commands non-reentrant and hard to test in isolation. The unconditional `extern int be_verbose` appears even outside DEBUG after a static inline dprint definition, which can confuse strict builds. Test x86 and non-x86 compilation, DEBUG/NLS combinations, and command behavior when hardware helper stubs are active.
