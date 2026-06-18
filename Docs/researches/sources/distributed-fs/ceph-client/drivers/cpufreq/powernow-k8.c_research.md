<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.c

## Purpose

Implements legacy AMD K8 Athlon64/Opteron PowerNow support for processors without hardware P-state support, using ACPI `_PSS` where possible and deprecated BIOS PSB tables as a uniprocessor fallback.

## APIs, Types, And Functions

The cpufreq driver `cpufreq_amd64_driver` provides async-notified target, get, init, exit, and ACPI BIOS limits. Per-policy/per-core state is `struct powernow_k8_data`. Core transition helpers are `core_voltage_pre_transition()`, `core_frequency_transition()`, `core_voltage_post_transition()`, and `transition_frequency_fidvid()`. Firmware table loaders are `powernow_k8_cpu_init_acpi()`, `find_psb_table()`, `fill_powernow_table()`, and `fill_powernow_table_fidvid()`.

## Control Flow

Late init rejects non-K8 CPUs and CPUs with `X86_FEATURE_HW_PSTATE`, requesting `acpi-cpufreq` instead. CPU init validates support on the target CPU, allocates state, loads ACPI or single-CPU PSB tables, computes transition latency, initializes the FID/VID MSR on the target CPU, sets the policy cpumask to the topology core mask, and stores the same data pointer for all CPUs in the policy. Targeting runs on the policy CPU with `work_on_cpu()`, checks the pending bit, refreshes current FID/VID, serializes with `fidvid_mutex`, decodes ACPI transition parameters for the selected state, and executes the three-phase transition.

## State And Persistence

Per-CPU `powernow_data` points at shared policy state containing current FID/VID, ACPI performance data, transition timing parameters, and the cpufreq table. Hardware state persists in `MSR_FIDVID_CTL` and `MSR_FIDVID_STATUS`. Exit unregisters ACPI performance data, frees the table and state, and clears per-CPU pointers for related CPUs.

## Dependencies And Integration Points

Depends on x86 CPUID, MSR access, topology core masks, ACPI processor performance, optional BIOS physical memory scanning, and cpufreq target execution on a specific CPU. It defers newer hardware to `acpi-cpufreq`.

## Risks And Test Signals

Transition correctness depends on pending-bit polling, voltage step limits, max VID/RVO validation, VCO FID stepping, and ACPI/PSB table sanity. Failures return `-EIO` or log detailed FID/VID mismatches. Test signals include "Found ... powernow-k8" init logs, ACPI `_PSS` decoding, PSB validation, `get` frequency from current FID, and stress transitions across low/high FID boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.c -->
