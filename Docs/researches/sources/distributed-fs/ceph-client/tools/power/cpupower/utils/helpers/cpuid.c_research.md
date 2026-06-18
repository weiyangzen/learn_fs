# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/cpuid.c

## Purpose
Extracts CPU vendor/family/model/stepping and cpupower capability bits from `/proc/cpuinfo` and CPUID.

## Important APIs, Types, and Functions
Exports CPUID register helpers `cpuid_eax`, `cpuid_ebx`, `cpuid_ecx`, `cpuid_edx` on x86 and `get_cpu_info` on all builds. It sets capability bits including invariant TSC, APERF/MPERF, AMD CPB, Intel perf bias, turbo ratio support, Sandy/Ivy Bridge classification, AMD RDPRU, AMD hardware pstate, AMD pstate definition, CPB MSR, and AMD pstate driver active.

## Control Flow, State, and Persistence
`get_cpu_info` initializes fields to unknown, reads `/proc/cpuinfo` until it reaches global `base_cpu`, fills identity fields, then augments capabilities with CPUID leaves. AMD pstate active state masks out older AMD boost/pstate capability paths so later code prefers amd-pstate sysfs/CPPC behavior. No persistent state is written; the caller stores results in global `cpupower_cpu_info`.

## Dependencies and Integration Points
Depends on `/proc/cpuinfo`, GCC `<cpuid.h>` on x86, global `base_cpu`, and helper `cpupower_amd_pstate_enabled`. Its output drives frequency info, boost control, monitor registration, and MSR/PCI logic.

## Risks and Test Signals
Parsing is x86 `/proc/cpuinfo` format specific and has no CPUID-only fallback if procfs is missing. New Intel models may not get turbo ratio classification until tables are updated. Test Intel, AMD, Hygon, non-x86, missing `/proc/cpuinfo`, AMD pstate enabled/disabled, and offline base CPU scenarios.
