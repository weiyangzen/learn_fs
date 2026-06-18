# Research: subset-b-000884

Work item `subset-b-000884` covers x86 CPU helper code, resctrl architecture support, and SGX support files from the imported Ceph client kernel source tree. Each file section below is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/perfctr-watchdog.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/perfctr-watchdog.c

## Purpose

This file provides a small reservation layer for performance counter MSRs used by the local APIC NMI watchdog and other low-level users. It is not a full watchdog implementation; it coordinates ownership of counter and event-select MSR slots so independent kernel subsystems do not program the same hardware counter at the same time.

## Important APIs, Types, And Functions

The exported APIs are `reserve_perfctr_nmi()`, `release_perfctr_nmi()`, `reserve_evntsel_nmi()`, and `release_evntsel_nmi()`. The state is held in two static bitmaps, `perfctr_nmi_owner` and `evntsel_nmi_owner`, each sized by `NMI_MAX_COUNTER_BITS`. Translation helpers `nmi_perfctr_msr_to_bit()` and `nmi_evntsel_msr_to_bit()` convert vendor/family-specific MSR numbers into bitmap indices using `boot_cpu_data`, architectural perfmon feature bits, and legacy AMD, Intel P6/KNC/P4, Zhaoxin, and Centaur ranges.

## Control Flow

Reservation calls translate the MSR to a slot, treat unmanaged MSRs as available, and then use `test_and_set_bit()` to atomically claim the bit. Release calls translate the MSR and clear the corresponding bit. No locks are used; atomic bit operations are the synchronization mechanism.

## State, Dependencies, And Integration

The bitmap state is boot-lifetime only and not persistent. Consumers coordinate with the NMI watchdog/perf counter hardware through these exported symbols. Dependencies include x86 CPU vendor data, perf event MSR constants, APIC/NMI headers, bitops, and export support.

## Risks And Test Signals

The translation logic is hardware-specific. Incorrect offsets can alias unrelated counters or make a managed counter appear unmanaged. The boundary check uses `counter > NMI_MAX_COUNTER_BITS`; index equality with the bitmap size would be out of range if ever produced. Useful tests are booting on supported vendors, enabling the NMI watchdog alongside perf users, and verifying duplicate reservations fail while unrelated counters can still be acquired and released.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/perfctr-watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/powerflags.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/powerflags.c

## Purpose

This file is a data-only lookup table for x86 CPU power-management feature names. It intentionally contains no executable code and feeds human-readable power-management strings into `/proc/cpuinfo`.

## Important APIs, Types, And Functions

The single exported datum is `const char *const x86_power_flags[32]`. Entries map bit positions in `struct cpuinfo_x86::x86_power` to strings such as `ts`, `fid`, `vid`, `tm`, `hwpstate`, `cpb`, `eff_freq_ro`, `proc_feedback`, and `acc_power`. Empty entries suppress output for bits intentionally mapped elsewhere, such as invariant TSC.

## Control Flow

There is no control flow in this file. Consumers index the array while rendering CPU information and skip null or empty names according to their own rules.

## State, Dependencies, And Integration

The table is immutable static kernel data. It depends on `asm/cpufeature.h` for the associated feature definitions and integrates mainly with `proc.c` when printing `power management:` in `/proc/cpuinfo`.

## Risks And Test Signals

Risk is mostly ABI/user-visible naming drift. Adding, moving, or removing entries changes `/proc/cpuinfo` output and can affect scripts that parse power flags. Test by building x86 CPU code and comparing `/proc/cpuinfo` power-management output on CPUs with the relevant bits set.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/powerflags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/proc.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/proc.c

## Purpose

This file implements x86-specific `/proc/cpuinfo` rendering and optional per-thread x86 feature rendering for procfs. It converts `struct cpuinfo_x86`, topology data, feature bitmaps, bug bitmaps, power flags, and frequency data into the stable text interface consumed by userspace.

## Important APIs, Types, And Functions

The exported proc sequence operations are exposed through `const struct seq_operations cpuinfo_op`. Core functions are `show_cpuinfo()`, `show_cpuinfo_core()`, architecture-specific `show_cpuinfo_misc()`, iterator callbacks `c_start()`, `c_next()`, and `c_stop()`. When `CONFIG_X86_USER_SHADOW_STACK` is enabled, `arch_proc_pid_thread_features()` reports task thread feature and locked-feature masks with help from `dump_x86_features()`.

## Control Flow

The seq-file iterator walks `cpu_online_mask` and returns `cpu_data()` for each online CPU. `show_cpuinfo()` prints processor identity, model, stepping, microcode, frequency from `arch_freq_get_on_cpu()`, cache size, SMP topology, feature flags, optional VMX flags, bug strings, bogomips, TLB size, cache alignment, address widths, and power-management strings. Feature and bug output loops over the x86 capability arrays and only prints named bits.

## State, Dependencies, And Integration

The file does not persist data; it reads live CPU and task state. It depends on procfs/seq-file APIs, cpufreq, x86 feature-name arrays, topology helpers, shadow-stack prctl state, and `powerflags.c`. The output is a user-visible ABI, even though some values are informational.

## Risks And Test Signals

Changes can break parsers or expose inconsistent per-CPU data. Frequency may be unavailable, CPU hotplug can change iteration results, and feature-name arrays must remain aligned with capability bit numbering. Test signals include `cat /proc/cpuinfo`, CPU hotplug while reading, 32-bit versus 64-bit builds, VMX feature-name builds, and `/proc/<pid>/status`-style thread-feature output when shadow stack support is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/rdrand.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/rdrand.c

## Purpose

This file validates the CPU RDRAND instruction during CPU initialization and disables RDRAND/RDSEED capability bits if the instruction appears unreliable. The check protects kernel and userspace consumers from known classes of hardware or firmware failures that return repeated values or fail the instruction.

## Important APIs, Types, And Functions

The single API is `x86_init_rdrand(struct cpuinfo_x86 *c)`. It uses `rdrand_long()`, `cpu_has()`, `clear_cpu_cap()`, and `pr_emerg()`. The local sampling constants require eight samples and at least five observed changes.

## Control Flow

If the CPU lacks `X86_FEATURE_RDRAND`, the function exits. Otherwise it invokes RDRAND repeatedly, records whether each call succeeded, and counts sample-to-sample changes. Any failed invocation or too few changed samples marks the feature unreliable. On failure it clears both `X86_FEATURE_RDRAND` and `X86_FEATURE_RDSEED` from the CPU capability set and logs an emergency message.

## State, Dependencies, And Integration

The persistent effect is in the in-memory CPU capability bitmap for the current CPU initialization path. The file depends on x86 processor feature handling, `asm/archrandom.h`, and printk. It integrates with CPU bring-up and affects later random-number instruction dispatch.

## Risks And Test Signals

The heuristic intentionally catches obvious bad outputs, not cryptographic quality. False positives disable hardware random instructions; false negatives leave bad hardware exposed. Test by booting with known-good and fault-injected RDRAND behavior, checking dmesg for the disable message, and verifying `/proc/cpuinfo` feature flags no longer show RDRAND/RDSEED after failure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/rdrand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/Makefile

## Purpose

This Makefile selects the x86 resctrl architecture objects built for Resource Director Technology support. It wires core resource detection, control, monitoring, optional Intel Application Energy Telemetry, and optional pseudo-locking into the kernel build.

## Important APIs, Types, And Functions

Build targets are `core.o`, `rdtgroup.o`, `monitor.o`, `ctrlmondata.o`, optional `intel_aet.o`, and optional `pseudo_lock.o`. `CFLAGS_pseudo_lock.o = -I$(src)` is required so `define_trace.h` can recursively include `pseudo_lock_trace.h` from the source directory.

## Control Flow

There is no runtime control flow. Kconfig symbols `CONFIG_X86_CPU_RESCTRL`, `CONFIG_X86_CPU_RESCTRL_INTEL_AET`, and `CONFIG_RESCTRL_FS_PSEUDO_LOCK` choose which objects are compiled and linked.

## State, Dependencies, And Integration

This file affects build-time composition only. It integrates the architecture-specific files with generic resctrl filesystem code and tracepoint generation.

## Risks And Test Signals

Missing objects create unresolved symbols or silently remove features. Missing include flags break pseudo-lock tracepoint builds. Test with all three configurations: base resctrl, Intel AET enabled, and pseudo-lock enabled, including incremental builds that regenerate trace headers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/core.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/core.c

## Purpose

This file is the x86 architecture backend for resctrl resource discovery, domain lifetime, CPU hotplug, default control programming, and boot-time option handling. It turns CPUID/MSR capabilities into `struct rdt_resource` instances for L3/L2 CAT, MBA/SMBA, L3 monitoring, and package telemetry, then registers them with the generic resctrl filesystem.

## Important APIs, Types, And Functions

Global state includes `rdt_resources_all[]`, `rdt_alloc_capable`, per-CPU `pqr_state`, `domain_list_lock`, and the CPU hotplug state `rdt_online`. Exported or cross-file functions include `resctrl_arch_get_resource()`, `resctrl_arch_system_num_rmid_idx()`, `resctrl_arch_get_num_closid()`, `rdt_ctrl_update()`, `resctrl_arch_pre_mount()`, `rdt_cpu_has()`, `resctrl_arch_is_evt_configurable()`, `resctrl_cpu_detect()`, and init/exit hooks. Hardware-specific helpers include CAT/MBA MSR writers, CPUID parsers, Haswell CAT probing, CDP setup, and Intel/AMD resource default initialization.

## Control Flow

`resctrl_arch_late_init()` initializes resource IDs, vendor defaults, quirks, allocation/monitoring resources, CPU hotplug callbacks, and generic `resctrl_init()`. `get_rdt_alloc_resources()` probes CAT/CDP/MBA/SMBA and configures MSR bases and CLOSID counts. `get_rdt_mon_resources()` enables monitoring events and calls `rdt_get_l3_mon_config()`. CPU hotplug callbacks add or remove control and monitor domains based on cache/node/package scopes, allocate per-domain control arrays and MBM state, update MSRs, and notify generic resctrl domain online/offline paths.

## State, Dependencies, And Integration

State is boot-lifetime kernel memory and per-domain dynamic allocations. Control-domain `ctrl_val[]` arrays mirror programmed CLOSID values. Monitor domains keep architecture-private MBM state. CPU hotplug mutations are protected by `domain_list_lock`, RCU list deletion, and cpus-read locking where required. Dependencies include CPUID, MSR accessors, topology/cacheinfo, CPU hotplug, Intel AET hooks, generic resctrl APIs, and x86 vendor/model quirks.

## Risks And Test Signals

Risk centers on incorrect resource enumeration, wrong MSR base/update callback, per-domain CPU mask handling, and hotplug lifetime. Haswell probing and Skylake/Broadwell MBM quirks are model-sensitive. CDP and AMD per-CPU config require updating the right CPU set. Test by booting on Intel and AMD systems with `rdt=` force-on/off options, mounting resctrl, verifying `info/` resource files, changing schemata, CPU hotplugging, enabling AET during mount, and checking that PQR_ASSOC resets on online/offline paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/ctrlmondata.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/ctrlmondata.c

## Purpose

This file implements architecture-specific control update helpers for resctrl schemata writes and AMD I/O allocation enablement. It bridges generic staged resctrl configurations to x86 QOS MSR writes.

## Important APIs, Types, And Functions

Important APIs are `resctrl_arch_update_one()`, `resctrl_arch_update_domains()`, `resctrl_arch_get_config()`, `resctrl_arch_get_io_alloc_enabled()`, and `resctrl_arch_io_alloc_enable()`. It uses `struct rdt_hw_ctrl_domain`, `struct rdt_hw_resource`, `struct msr_param`, and staged config arrays from the generic resctrl layer.

## Control Flow

`resctrl_arch_update_one()` validates that the caller is executing on a CPU in the target domain, updates the cached `ctrl_val` entry, and writes a single MSR range through the resource's `msr_update()` callback. `resctrl_arch_update_domains()` walks all control domains under the CPU hotplug read lock, collects changed staged CDP/non-CDP config entries for one CLOSID, updates cached values, and sends `rdt_ctrl_update()` to one CPU in each domain. AMD SDCIAE enablement writes or clears bit 1 of `MSR_IA32_L3_QOS_EXT_CFG` on all CPUs in all control domains.

## State, Dependencies, And Integration

The persistent runtime state is the per-domain `ctrl_val[]` cache plus `rdt_hw_resource::sdciae_enabled`. It depends on CPU mask IPIs, MSR helpers, generic resctrl staging, and `internal.h` conversion helpers. It integrates with resctrl filesystem schemata writes and I/O allocation toggles.

## Risks And Test Signals

Incorrect index calculation can program the wrong CLOSID or CDP half. The CPU-mask assertions matter because domain lists can change during hotplug. SDCIAE must be updated on every CPU when hardware state is per-CPU. Test by writing schemata for CAT/MBA/SMBA, toggling I/O allocation on AMD systems with SDCIAE, hotplugging CPUs, and reading back config through resctrl's info and schema paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/ctrlmondata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/intel_aet.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/intel_aet.c

## Purpose

This file adds Intel Application Energy Telemetry support as a package-scoped resctrl monitoring resource. It discovers PMT telemetry aggregators, validates their GUIDs and MMIO layouts, exposes selected per-RMID energy/activity/performance events through resctrl, and reads package-domain counters from MMIO.

## Important APIs, Types, And Functions

Key structures are `struct pmt_event` and `struct event_group`. Static event groups describe known XML GUIDs for energy and performance telemetry, including event IDs, counter indices, fixed-point fractional bits, expected RMID counts, and MMIO size. Public hooks are `intel_handle_aet_option()`, `intel_aet_get_events()`, `intel_aet_exit()`, `intel_aet_read_event()`, and `intel_aet_mon_domain_setup()`.

## Control Flow

Boot option parsing can force event groups on or off by PMT feature name and optional GUID. `intel_aet_get_events()` asks the Intel PMT driver for feature regions, validates package IDs and MMIO sizes, rejects groups with insufficient RMIDs unless forced on, enables resctrl monitor events, and adjusts the resource RMID count to the minimum supported. `intel_aet_read_event()` derives the containing event group from `arch_priv`, computes the per-RMID MMIO slot, sums valid data across matching package aggregators, and returns `-EINVAL` when no valid data exists.

## State, Dependencies, And Integration

Each enabled `event_group` retains a `pmt_feature_group` reference until `intel_aet_exit()`. Resctrl package monitor domains are allocated in `intel_aet_mon_domain_setup()`. Dependencies include the Intel PMT telemetry driver, topology package count, MMIO `readq()`, and generic resctrl monitor event registration.

## Risks And Test Signals

Risks include stale XML-derived sizes, bad package IDs from firmware, mismatched RMID counts, invalid MMIO index arithmetic, and duplicate event IDs already enabled by another source. Test on AET-capable Intel hardware by using `rdt=energy`, `rdt=!energy`, and GUID-qualified options, mounting resctrl, checking package monitor domains/events, reading counters for several RMIDs, and unloading/exiting to verify PMT references are released.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/intel_aet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/internal.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/internal.h

## Purpose

This header defines x86-private resctrl data structures, constants, CPUID layouts, ABMC encodings, and cross-file prototypes. It is the contract between `core.c`, control update code, monitoring code, pseudo-locking, and optional Intel AET support.

## Important APIs, Types, And Functions

Important types include `struct arch_mbm_state`, `struct rdt_hw_ctrl_domain`, `struct rdt_hw_l3_mon_domain`, `struct rdt_perf_pkg_mon_domain`, `struct msr_param`, `struct rdt_hw_resource`, CPUID unions for RDT allocation leaves, and `union l3_qos_abmc_cfg`. Inline conversion helpers map generic `struct rdt_resource`, `struct rdt_ctrl_domain`, and `struct rdt_l3_mon_domain` to architecture-private containers. Constants describe CDP MSR bits, MBM counter widths, RMID error bits, ABMC/SDCIAE bits, and event identifiers.

## Control Flow

The header itself has no runtime flow, but it enables common call paths: `rdt_ctrl_update()` receives `msr_param`, monitor reads use `arch_mbm_state`, ABMC configuration packs fields into `l3_qos_abmc_cfg`, and Intel AET functions compile either as real hooks or stubs depending on Kconfig.

## State, Dependencies, And Integration

The header exposes `rdt_resources_all[]` and architecture-private fields that persist for boot lifetime. It depends on generic `linux/resctrl.h` and is included by all x86 resctrl implementation files. It also shields non-AET builds with inline stubs.

## Risks And Test Signals

Layout changes can break container conversions or generic/architecture assumptions. Bitfield definitions must match hardware MSR encodings. Test signals are compile coverage across Intel, AMD, AET disabled/enabled, ABMC/SDCIAE paths, and runtime monitor reads that validate MBM overflow and ABMC counter behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/monitor.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/monitor.c

## Purpose

This file implements x86 resctrl monitoring: RMID reads, MBM overflow correction, Sub-NUMA Cluster RMID translation, L3 monitoring capability setup, Intel MBM correction quirks, and AMD bandwidth-monitor event/counter assignment support.

## Important APIs, Types, And Functions

Cross-file APIs include `resctrl_arch_rmid_read()`, `resctrl_arch_reset_rmid()`, `resctrl_arch_reset_rmid_all()`, `arch_mon_domain_online()`, `rdt_get_l3_mon_config()`, `intel_rdt_mbm_apply_quirk()`, `resctrl_arch_mbm_cntr_assign_set()`, `resctrl_arch_mbm_cntr_assign_enabled()`, `resctrl_arch_config_cntr()`, and `resctrl_arch_mbm_cntr_assign_set_one()`. Important helpers include `logical_rmid_to_physical_rmid()`, `__rmid_read_phys()`, `get_corrected_val()`, `__cntr_id_read()`, and the MBM correction-factor table.

## Control Flow

Monitor reads program `MSR_IA32_QM_EVTSEL`, read `MSR_IA32_QM_CTR`, reject error/unavailable bits, and convert raw values to bytes. MBM events use per-RMID `arch_mbm_state` to accumulate wraparound deltas and optional Intel correction factors. SNC mode changes L3 monitor scope to node and maps logical RMIDs into physical RMID partitions. AET package resources delegate reads to `intel_aet_read_event()`. ABMC support toggles `MSR_IA32_L3_QOS_EXT_CFG`, assigns counters through `MSR_IA32_L3_QOS_ABMC_CFG`, and reads counters through extended event IDs.

## State, Dependencies, And Integration

State includes global `rdt_mon_capable`, SNC node count, correction-factor threshold/value, per-resource monitor scale/width, per-domain MBM arrays, and ABMC enable state. Dependencies include CPUID, MSR access, CPU model matching, topology NUMA/package helpers, generic resctrl monitor event APIs, and Intel AET.

## Risks And Test Signals

Wrong RMID width, scale, SNC translation, or MBM overflow handling yields misleading monitoring data. ABMC toggles are domain-wide and must reset state consistently. Intel correction factors are model/RMID-count dependent. Test by mounting resctrl, reading `mon_data` occupancy and MBM files under traffic, exercising SNC systems, toggling ABMC counter assignment, configuring BMEC event masks, and validating unavailable/error returns under invalid RMIDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock.c

## Purpose

This file provides x86-specific pseudo-locking primitives for resctrl. Pseudo-locking uses CAT to load a kernel buffer into a selected cache allocation region and keep later allocations from overlapping it, then exposes measurement helpers to evaluate latency and cache residency.

## Important APIs, Types, And Functions

Important APIs are `resctrl_arch_get_prefetch_disable_bits()`, `resctrl_arch_pseudo_lock_fn()`, `resctrl_arch_measure_cycles_lat_fn()`, `resctrl_arch_measure_l2_residency()`, and `resctrl_arch_measure_l3_residency()`. It uses `struct pseudo_lock_region`, per-CPU `pqr_state`, `MSR_MISC_FEATURE_CONTROL`, `MSR_IA32_PQR_ASSOC`, perf raw events, RDPMC, and tracepoints from `pseudo_lock_trace.h`.

## Control Flow

Platform detection returns the documented prefetch-disable bits for validated Intel Broadwell-X and Goldmont variants. The lock function flushes caches with `wbinvd()`, disables interrupts and hardware prefetchers, switches PQR_ASSOC to the pseudo-lock CLOSID, reads the buffer by page and cache-line stride, restores the previous CLOSID/RMID and prefetch MSR, then wakes the waiting control thread. Measurement paths either trace per-access TSC latency or create pinned perf counters for platform-specific hit/miss events, read the locked region, compute deltas, and emit L2/L3 tracepoints.

## State, Dependencies, And Integration

The only global state is `prefetch_disable_bits`. Runtime state lives in `pseudo_lock_region`, perf events, and trace buffers. Dependencies include resctrl pseudo-lock generic code, x86 perf raw event encoding, MSRs, interrupt/preemption rules, cache flushing, and tracepoint generation.

## Risks And Test Signals

The code is sensitive to platform event encodings, prefetch bits, interrupt state, speculative reads, and KASAN register pressure. Bad restore paths can leave prefetchers or PQR_ASSOC in the wrong state. Test on supported platforms by creating pseudo-locked regions, reading `tracefs` events for latency/L2/L3, validating low miss rates under load, and checking unsupported platforms reject pseudo-locking cleanly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock_trace.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock_trace.h

## Purpose

This header defines tracepoints used by resctrl pseudo-lock measurement code. It gives users and tests visibility into memory access latency and cache residency measurements.

## Important APIs, Types, And Functions

Trace events are `pseudo_lock_mem_latency`, `pseudo_lock_l2`, and `pseudo_lock_l3`. The first records a 32-bit latency sample. The L2 and L3 events record 64-bit hit/reference and miss counts. The header sets `TRACE_SYSTEM resctrl`, `TRACE_INCLUDE_PATH .`, and `TRACE_INCLUDE_FILE pseudo_lock_trace` for recursive trace generation.

## Control Flow

There is no ordinary control flow. `pseudo_lock.c` defines `CREATE_TRACE_POINTS` before including this header, causing tracepoint definitions to be emitted; other includes can use declarations.

## State, Dependencies, And Integration

Tracepoint state is managed by the kernel tracing subsystem. Dependencies include `linux/tracepoint.h` and the Makefile include-path setting. Integration is with tracefs/perf tracing and pseudo-lock measurement functions.

## Risks And Test Signals

Field or format changes affect tracing tools. Include-path mistakes break builds. Test by enabling `CONFIG_RESCTRL_FS_PSEUDO_LOCK`, building with tracing, creating measurements, and verifying events appear under `tracefs/events/resctrl/`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/rdtgroup.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/rdtgroup.c

## Purpose

This file contains x86 architecture hooks used by the generic resctrl group/filesystem layer. It synchronizes CLOSID/RMID state on CPUs, reads and writes configurable monitoring-event masks, toggles CDP, and resets all control MSRs for a resource.

## Important APIs, Types, And Functions

Exported hooks include `resctrl_arch_sync_cpu_closid_rmid()`, `resctrl_arch_mon_event_config_read()`, `resctrl_arch_mon_event_config_write()`, `rdt_domain_reconfigure_cdp()`, `resctrl_arch_set_cdp_enabled()`, `resctrl_arch_get_cdp_enabled()`, and `resctrl_arch_reset_all_ctrls()`. Static keys `rdt_enable_key`, `rdt_mon_enable_key`, and `rdt_alloc_enable_key` gate fast-path resctrl usage elsewhere.

## Control Flow

CPU sync updates per-CPU default CLOSID/RMID and calls `resctrl_arch_sched_in()` so the currently running task's effective state is applied safely. Monitor event configuration maps total/local MBM event IDs to `MSR_IA32_EVT_CFG_BASE` offsets. CDP toggling builds a CPU mask from control domains and writes L2/L3 QOS_CFG MSRs either once per domain or per CPU for AMD-style per-CPU config. Resetting controls fills each domain's cached values with defaults and programs the full CLOSID range.

## State, Dependencies, And Integration

State includes static keys, per-CPU `pqr_state`, `rdt_hw_resource::cdp_enabled`, cached domain control values, and hardware QOS MSRs. Dependencies are generic resctrl group logic, MSR writes, CPU masks, and hotplug read locking. It integrates directly with mount options, schemata resets, CDP enable/disable operations, and monitoring event configuration files.

## Risks And Test Signals

Risks include writing QOS_CFG on too few CPUs, races with CPU hotplug, invalid configurable event IDs, and stale cached control values after reset. Test CDP mount/remount flows, monitor event config writes, schemata reset, per-task scheduling changes, AMD per-CPU config hardware, and CPU hotplug while resctrl is mounted.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/rdtgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/scattered.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/scattered.c

## Purpose

This file discovers CPU feature bits that are scattered across CPUID leaves rather than grouped in the usual architectural feature words. It centralizes the mapping from leaf/subleaf/register/bit to `X86_FEATURE_*` capability flags.

## Important APIs, Types, And Functions

`struct cpuid_bit` describes a feature, CPUID register, bit number, leaf, and subleaf. `cpuid_bits[]` includes features for APERF/MPERF, EPB, PPIN, APX, speculation controls, RDT monitoring/allocation, SGX subfeatures, AMD RAS/power/workload/topology features, ABMC, SDCIAE, and others. The single function is `init_scattered_cpuid_features(struct cpuinfo_x86 *c)`.

## Control Flow

The function walks the sorted table, checks that each CPUID leaf is valid by comparing against the maximum supported level for that CPUID namespace, calls `cpuid_count()`, and sets the target CPU capability when the requested register bit is present.

## State, Dependencies, And Integration

State changes are limited to the `cpuinfo_x86` capability bitmap. Dependencies include CPUID helpers, feature definitions, and CPU initialization. Later code such as resctrl and SGX relies on these features being set before capability-based initialization runs.

## Risks And Test Signals

Table ordering and leaf validity checks matter. A wrong register/bit maps hardware incorrectly, and duplicate feature entries for Intel/AMD leaves must remain intentional. Test by comparing `/proc/cpuinfo` flags and kernel capability-dependent behavior on CPUs with RDT, SGX, AMD extended features, and older CPUs that lack the leaves.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/scattered.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/Makefile

## Purpose

This Makefile selects x86 SGX support objects. It builds the native SGX device driver, enclave backing/fault logic, ioctl handlers, EPC page-cache core, and optional KVM virtual EPC support.

## Important APIs, Types, And Functions

Always-built objects are `driver.o`, `encl.o`, `ioctl.o`, and `main.o`. `virt.o` is included when `CONFIG_X86_SGX_KVM` is enabled.

## Control Flow

There is no runtime control flow. Kconfig determines whether the KVM-facing `/dev/sgx_vepc` and exported virtualization ENCLS helpers are included.

## State, Dependencies, And Integration

This file controls link composition for SGX and KVM integration. It depends on the kernel build system and SGX Kconfig options.

## Risks And Test Signals

Missing objects produce unresolved symbols or absent devices. Test base SGX builds and SGX+KVM builds, then verify `/dev/sgx_enclave`, `/dev/sgx_provision`, and optional `/dev/sgx_vepc` registration behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.c

## Purpose

This file implements the native `/dev/sgx_enclave` misc device. It allocates per-file enclave objects, validates mmap permissions, dispatches ioctls, and registers the enclave device after SGX launch-control and SGX1 capabilities are confirmed.

## Important APIs, Types, And Functions

Global masks `sgx_attributes_reserved_mask`, `sgx_xfrm_reserved_mask`, and `sgx_misc_reserved_mask` constrain enclave attributes. Core functions are `sgx_open()`, `sgx_release()`, `sgx_mmap()`, `sgx_get_unmapped_area()`, optional `sgx_compat_ioctl()`, and `sgx_drv_init()`. The file defines `sgx_encl_fops` and miscdevice `sgx_dev_enclave`.

## Control Flow

Open increments SGX usage, allocates and initializes `struct sgx_encl`, xarray, mutexes, VA/MM lists, spinlock, and SRCU. Release drains remaining mm-notifier records, unregisters notifiers, and drops enclave references. mmap validates requested VMA permissions with `sgx_encl_may_map()`, adds the mm to the enclave, and installs SGX VM ops with PFNMAP/IO/DONTDUMP flags. Init queries SGX CPUID leaves for supported attributes/misc/xfrm bits and registers the device only if launch control and SGX1 are available.

## State, Dependencies, And Integration

State persists per open file in `file->private_data`. Device registration is boot-lifetime. Dependencies include miscdevice, mmu notifiers, mmap flags, CPU SGX CPUID data, LSM/security attribute handling through ioctl paths, and SGX core usage accounting.

## Risks And Test Signals

Release ordering must avoid mm-notifier and SRCU lifetime races. Attribute masks must match CPUID or invalid enclaves may be accepted. mmap permissions are security-sensitive. Test by opening/closing devices, mmap/fork/exit races, invalid MAP_PRIVATE use, attribute-mask validation, and running SGX SDK enclave create/add/init flows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.h

## Purpose

This header declares the native SGX driver interface shared by the SGX misc-device, ioctl, and core files.

## Important APIs, Types, And Functions

It defines EINIT retry constants `SGX_EINIT_SPIN_COUNT`, `SGX_EINIT_SLEEP_COUNT`, and `SGX_EINIT_SLEEP_TIME`. It declares reserved masks for SGX attributes, XFRM, and miscselect; `sgx_provision_fops`; `sgx_ioctl()`; and `sgx_drv_init()`.

## Control Flow

The header itself has no flow. The constants drive retry/sleep behavior in EINIT ioctl handling, and prototypes connect file operations to ioctl implementation.

## State, Dependencies, And Integration

It depends on kref, mmu_notifier, scheduler/workqueue headers, SGX UAPI definitions, and `sgx.h`. It integrates the native driver with provisioning and enclave ioctl code.

## Risks And Test Signals

Changing retry constants changes EINIT latency and interrupt responsiveness. Prototype or include drift breaks SGX builds. Test through SGX native driver builds and EINIT behavior under signals/interrupts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.c

## Purpose

This file manages SGX enclave runtime objects below the ioctl layer: EPC page reload from backing storage, page faults, SGX2 dynamic page addition, VMA permission enforcement, debug access, mmu-notifier tracking, backing shmem pages, VA slots, PTE zapping, and enclave teardown.

## Important APIs, Types, And Functions

Public APIs include `sgx_encl_may_map()`, `sgx_encl_release()`, `sgx_encl_mm_add()`, `sgx_encl_cpumask()`, `sgx_encl_alloc_backing()`, `sgx_encl_put_backing()`, `sgx_encl_test_and_clear_young()`, `sgx_encl_page_alloc()`, `sgx_zap_enclave_ptes()`, `sgx_alloc_va_page()`, VA slot helpers, `sgx_encl_free_epc_page()`, and `sgx_encl_load_page()`. VM operations are `sgx_vm_ops`.

## Control Flow

Faults load existing enclave pages through ELDU or, on SGX2, dynamically allocate a new REG page with EAUG. ELDU pins shmem contents and PCMD pages, loads the EPC page, clears PCMD metadata, truncates no-longer-needed backing pages, and restores VA slots. VMA checks ensure requested mappings stay within declared page permissions and reject READ_IMPLIES_EXEC tasks. Debug access uses EDBGRD/EDBGWR only for debug enclaves. MMU notifier registration tracks all mms mapping the enclave so reclaimer and SGX2 operations can zap PTEs and compute CPU masks after ETRACK.

## State, Dependencies, And Integration

The enclave state is `struct sgx_encl`: xarray page map, SECS page, backing file, VA page list, mm list, SRCU, mm-list version, reference count, attributes, and flags. Backing storage is private shmem laid out as encrypted pages, SECS, and PCMD pages. Dependencies include ENCLS wrappers, shmem, mmu notifiers, SRCU/RCU, xarray, memcg charging, page-table walking, and SGX EPC allocation/reclaim.

## Risks And Test Signals

The highest risks are lifetime races with reclaim, mmu notifier teardown, PCMD truncation while reclaim writes, PTE zapping across forked mms, and correct lock ordering around `encl->lock` versus mmap locks. Test with SGX SDK workloads, EPC pressure/reclaim, fork/exit/mmap/mprotect races, SGX2 EAUG faults, debug enclave ptrace-like access, and teardown after partially built or heavily reclaimed enclaves.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.h

## Purpose

This header defines software data structures and function contracts for native SGX enclaves. It is the central model for enclave pages, enclave-wide state, mm tracking, VA pages, and backing storage.

## Important APIs, Types, And Functions

Important types are `struct sgx_encl_page`, `enum sgx_encl_flags`, `struct sgx_encl_mm`, `struct sgx_encl`, `struct sgx_va_page`, and `struct sgx_backing`. Important constants are `SGX_ENCL_PAGE_VA_OFFSET_MASK`, `SGX_ENCL_PAGE_BEING_RECLAIMED`, and `SGX_VA_SLOT_COUNT`. It declares `sgx_vm_ops`, lookup helper `sgx_encl_find()`, permission checks, backing helpers, page load/allocation helpers, VA page helpers, PTE zapping, and enclave grow/shrink functions.

## Control Flow

The header has only inline lookup flow: `sgx_encl_find()` checks whether an address belongs to a VMA using `sgx_vm_ops`. Other control is implemented in `encl.c`, `ioctl.c`, and `main.c`.

## State, Dependencies, And Integration

`struct sgx_encl` persists per open enclave device and owns the xarray of pages, SECS, backing file, VA pages, mm-list/SRCU, and refcount. The header depends on mm, mmu-notifier, list, mutex, xarray, and `sgx.h`. It integrates native driver, ioctl, fault, and reclaim code.

## Risks And Test Signals

Bit overlap between VA offset and `BEING_RECLAIMED` is intentional and requires careful checks. Structure fields are shared across locking domains. Test by compiling all SGX configurations and exercising page reclaim, VA slot allocation, mm notifier release, and SGX2 dynamic operations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encls.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encls.h

## Purpose

This header wraps privileged SGX ENCLS instructions in C inline functions with Linux exception-table handling. It provides the low-level instruction interface used by native SGX, EPC reclaim, SGX2 operations, and KVM SGX virtualization.

## Important APIs, Types, And Functions

Helpers `encls_faulted()`, `encls_failed()`, `ENCLS_TRAPNR()`, and `ENCLS_WARN()` classify ENCLS return values. Assembly macros `__encls_ret_N()` and `__encls_N()` encode leaves that return error codes or fault-only status. Inline wrappers include `__ecreate()`, `__eextend()`, `__eadd()`, `__einit()`, `__eremove()`, `__edbgwr()`, `__edbgrd()`, `__etrack()`, `__eldu()`, `__eblock()`, `__epa()`, `__ewb()`, `__emodpr()`, `__emodt()`, `__eaug()`, and `__eupdatesvn()`.

## Control Flow

Each wrapper loads the ENCLS leaf number and operands into required registers, executes `encls`, and uses `_ASM_EXTABLE_TYPE(..., EX_TYPE_FAULT_SGX)` so faults are converted into encoded return values. Callers then decide whether a page fault is expected/retryable or whether to warn and fail.

## State, Dependencies, And Integration

The header does not own state; it changes SGX hardware state through ENCLS. Dependencies include x86 assembly helpers, exception tables, trap numbers, and SGX architectural structures. It is integrated across every SGX source file.

## Risks And Test Signals

Register constraints and fault classification are critical. A wrong wrapper can corrupt inputs or misreport hardware failures. Test with enclave create/add/init/remove, EPC reclaim/load, SGX2 page modification, debug read/write, KVM virtual ECREATE/EINIT, and injected invalid operands that should fault predictably.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/ioctl.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/ioctl.c

## Purpose

This file implements the `/dev/sgx_enclave` ioctl API for enclave lifecycle and SGX2 dynamic management: create, add pages, initialize, authorize provisioning, restrict permissions, modify page types, and remove accepted trimmed pages.

## Important APIs, Types, And Functions

The public dispatcher is `sgx_ioctl()`. Key helpers are `sgx_encl_grow()`, `sgx_encl_shrink()`, `sgx_encl_create()`, `sgx_ioc_enclave_create()`, `sgx_validate_secinfo()`, `sgx_encl_add_page()`, `sgx_ioc_enclave_add_pages()`, `sgx_encl_init()`, `sgx_ioc_enclave_init()`, `sgx_ioc_enclave_provision()`, `sgx_enclave_etrack()`, and SGX2 ioctl handlers for permission/type/remove flows.

## Control Flow

`sgx_ioctl()` serializes ioctl execution with `SGX_ENCL_IOCTL`. Create copies SECS, allocates backing/SECS/VA resources, runs ECREATE, and records base, size, attributes, and debug flag. Add-pages validates source/offset/length/SECINFO, allocates enclave/EPC/VA pages, inserts xarray entries before irreversible EADD/EEXTEND, and reports partial progress. Init validates attributes and SIGSTRUCT masks, computes MRSIGNER, updates launch-control MSRs, retries EINIT around unmasked events, and marks the enclave initialized. SGX2 operations require initialized SGX2 enclaves, load pages, run EMODPR/EMODT/ETRACK, zap PTEs when needed, and remove pages only after enclave-side EACCEPT of TRIM.

## State, Dependencies, And Integration

The file mutates `struct sgx_encl` flags, page count, page xarray, VA pages, backing file, SECS child count, attributes mask, and page metadata. Dependencies include UAPI ioctl structs, ENCLS wrappers, shmem-backed storage, mmap locks, user-copy helpers, SHA-256 for MRSIGNER, provisioning file descriptors, and core EPC allocation/reclaim.

## Risks And Test Signals

This is a security boundary. Risks include accepting invalid permissions, mishandling partial progress, losing xarray/backing consistency after irreversible EADD/EEXTEND, lock-order bugs around PTE zapping, and failure to serialize ETRACK-dependent operations. Test native SGX SDK lifecycle, invalid SECINFO/SIGSTRUCT/misc/xfrm inputs, signal interruption during add/init, provisioning authorization, SGX2 permission/type/remove workflows, and concurrent ioctl attempts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/main.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/main.c

## Purpose

This file is the SGX EPC page-cache core. It discovers EPC sections, maps them, manages NUMA free lists and poisoned pages, runs the `ksgxd` reclaimer/sanitizer, handles EPC memory failures, registers provisioning support, updates launch-key hash MSRs, tracks active SGX users for EUPDATESVN, and initializes native/KVM SGX devices.

## Important APIs, Types, And Functions

Important globals are `sgx_epc_sections[]`, `sgx_epc_address_space`, `sgx_active_page_list`, `sgx_nr_free_pages`, `sgx_numa_mask`, `sgx_numa_nodes`, and `sgx_dirty_page_list`. Public APIs include `__sgx_alloc_epc_page()`, `sgx_alloc_epc_page()`, `sgx_free_epc_page()`, `sgx_reclaim_direct()`, `sgx_mark_page_reclaimable()`, `sgx_unmark_page_reclaimable()`, `current_is_ksgxd()`, `arch_is_platform_page()`, `arch_memory_failure()`, `sgx_update_lepubkeyhash()`, `sgx_set_attribute()`, `sgx_inc_usage_count()`, and `sgx_dec_usage_count()`.

## Control Flow

`sgx_init()` checks SGX, enumerates EPC CPUID sections, maps EPC with `memremap()`, allocates `sgx_epc_page` arrays, sanitizes dirty pages through EREMOVE, starts `ksgxd`, registers `/dev/sgx_provision`, and tries both native and vEPC drivers. Allocation prefers the caller's NUMA node, can reclaim when allowed, and wakes `ksgxd` below watermarks. Reclaim ages pages via PTE accessed bits, allocates shmem backing, marks pages being reclaimed, EBLOCKs/zaps PTEs, EWB-writes EPC contents/PCMD, and frees EPC pages. Memory failure maps physical EPC addresses back to `sgx_epc_page` and quarantines poison.

## State, Dependencies, And Integration

State is boot-lifetime EPC section metadata and runtime lists protected by per-node locks and `sgx_reclaimer_lock`. Dependencies include CPUID SGX EPC leaves, ENCLS, NUMA, xarray, miscdevice, kthreads/freezer, shmem/highmem, memory-failure, RDRAND retry constants for EUPDATESVN, and KVM export symbols. It integrates with `encl.c` and `virt.c` through EPC allocation, reclaimability, and launch-control MSR updates.

## Risks And Test Signals

Risks include reclaim races, poisoned EPC handling, SECS/child ordering, deadlocks if direct reclaim is called with mm/enclave locks held, failure cleanup after partially mapped sections, and usage-count mistakes around EUPDATESVN. Test EPC discovery on NUMA systems, kexec sanitization, EPC pressure reclaim, memory failure injection for EPC pages, provisioning fd validation, native and KVM device registration, and EUPDATESVN retry/error paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/sgx.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/sgx.h

## Purpose

This header defines SGX EPC core structures, constants, and cross-file APIs shared by native SGX, enclave management, reclaim, and KVM virtual EPC support.

## Important APIs, Types, And Functions

Important constants include EPC section limits, EEXTEND block size, reclaim scan/watermark values, and EPC page flags. Types include `struct sgx_epc_page`, `struct sgx_numa_node`, and `struct sgx_epc_section`. Inline helpers `sgx_get_epc_phys_addr()` and `sgx_get_epc_virt_addr()` map an EPC page descriptor to physical/virtual addresses. Prototypes cover EPC allocation/free, reclaim tracking, IPI callback, vEPC init, usage counting, and launch public-key hash updates.

## Control Flow

The header only contains address-computation helpers. They locate the owning section, compute the page-array index, and derive the physical or remapped virtual EPC address.

## State, Dependencies, And Integration

It exposes `sgx_epc_sections[]` and core APIs implemented in `main.c`. Dependencies include SGX architectural definitions, bitops, I/O, and x86 assembly headers. It integrates every SGX implementation file and provides stubs for non-KVM builds.

## Risks And Test Signals

Address computations rely on page descriptors belonging to the correct section arrays. Flag definitions coordinate allocator and reclaimer ownership. Test by exercising native enclave allocation/free, reclaim, poisoned pages, and KVM vEPC with `CONFIG_X86_SGX_KVM` both enabled and disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/sgx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/virt.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/virt.c

## Purpose

This file implements SGX virtualization support for KVM: `/dev/sgx_vepc`, virtual EPC mmap/fault allocation, cleanup of guest-owned EPC pages, a remove-all ioctl, and exported helpers for KVM to run ECREATE/EINIT on guest-provided pages.

## Important APIs, Types, And Functions

The private `struct sgx_vepc` owns an xarray of EPC pages and a mutex. Device functions include `sgx_vepc_open()`, `sgx_vepc_release()`, `sgx_vepc_mmap()`, `sgx_vepc_fault()`, and `sgx_vepc_ioctl()`. Cleanup helpers are `sgx_vepc_remove_page()`, `sgx_vepc_free_page()`, and `sgx_vepc_remove_all()`. Exported KVM APIs are `sgx_virt_ecreate()` and `sgx_virt_einit()`.

## Control Flow

vEPC faults allocate an EPC page owned by the vEPC file, store it by mmap page offset, and insert the EPC PFN into userspace. Release EREMOVE's all pages, handles SECS pages that still have children by retrying after child removal, and keeps cross-instance SECS pages on a protected zombie list until later releases can remove them. `SGX_IOC_VEPC_REMOVE_ALL` lets userspace attempt explicit removal and reports remaining SECS failures. KVM ECREATE/EINIT helpers validate user pointers, temporarily enable user access, execute ENCLS, return guest trap numbers for faults, and update launch-key hash MSRs when launch control is available.

## State, Dependencies, And Integration

State lives per vEPC file and in global zombie SECS list protected by `zombie_secs_pages_lock`. Dependencies include SGX EPC allocation/free, ENCLS wrappers, miscdevice, mmap PFN insertion, xarray, KVM export macros, and VMX feature detection. It integrates with KVM's SGX support and the global SGX usage count.

## Risks And Test Signals

Guest-owned EPC pages may be in arbitrary states, so cleanup must tolerate `SGX_CHILD_PRESENT` while warning on unexpected failures. Concurrent removal while vCPUs run can return busy. User-pointer handling in KVM ENCLS helpers is security-sensitive. Test KVM SGX guests, mmap/fault/unmap cycles, `SGX_IOC_VEPC_REMOVE_ALL` retries, cross-vEPC SECS-child ordering, and trapped guest ECREATE/EINIT success and fault injection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/virt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.c

## Purpose

This file maintains early x86 CPU/APIC topology registration, CPU-number allocation, topology-domain bitmaps, logical ID queries, CPU hotplug APIC handling, and possible/present CPU mask initialization. It provides a unified topology view across package, die, tile, module, core, and SMT domains.

## Important APIs, Types, And Functions

Important globals are early per-CPU `x86_cpu_to_apicid`, `x86_cpu_to_acpiid`, `phys_cpu_present_map`, `cpuid_to_apicid[]`, domain `apic_maps[]`, and `topo_info`. Public APIs include `arch_match_cpu_phys_id()`, `topology_register_apic()`, `topology_register_boot_apic()`, `topology_get_logical_id()`, `topology_unit_count()`, `topology_get_primary_thread()`, ACPI hotplug helpers, `topology_apply_cmdline_limits_early()`, `topology_init_possible_cpus()`, and `topology_reset_possible_cpus_up()`.

## Control Flow

Firmware or guest enumeration registers APIC IDs early. The boot APIC reserves CPU0; later APICs receive stable CPU numbers unless limits reject them. Domain bitmaps store normalized APIC IDs at each topology level. BSP sanity checks detect crash-kernel scenarios and broken firmware enumeration to avoid INITing the real BSP. Possible CPU initialization computes maximum packages/nodes/dies/threads, applies command-line limits, assigns disabled hotplug CPUs, and populates present/possible masks.

## State, Dependencies, And Integration

State is mostly `__ro_after_init` or early per-CPU mappings, with hotplug updates for present APICs. Dependencies include APIC, ACPI/MPTABLE enumeration, Xen PV handling, NUMA, SMP masks, MSRs, and x86 topology parser output. It integrates with scheduler topology, CPU hotplug, perf/uncore topology users, and `/proc/cpuinfo`.

## Risks And Test Signals

Risks include APIC ID overflow, duplicate or out-of-order BSP enumeration, CPU-number exhaustion, disabled APIC handling, and incorrect domain shift assumptions. Test with maxcpus/nosmp/nolapic/possible_cpus options, Xen PV guests, ACPI CPU hotplug, kdump kernels, large APIC IDs, multi-die systems, and logical ID/unit count consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.h

## Purpose

This header defines the internal x86 topology scan state and helper functions used by generic and vendor-specific topology parsers.

## Important APIs, Types, And Functions

`struct topo_scan` holds the current `cpuinfo_x86`, per-domain shifts and CPU counts, legacy CPUID[1] logical-processor shift, and AMD node metadata. Prototypes cover topology initialization/parsing, domain updates, extended topology parsing, AMD parsing, and AMD fixups. Inline helpers are `topo_shift_apicid()`, `topo_relative_domain_id()`, `topo_domain_mask()`, and `topology_update_dom()`. `topology_unit_count()` is declared when local APIC support is enabled and stubbed otherwise.

## Control Flow

The inline helpers shift or mask APIC IDs according to `x86_topo_system.dom_shifts` and `dom_size`. `topology_update_dom()` updates one scan domain without propagating changes to higher domains, which is useful for vendor fixups.

## State, Dependencies, And Integration

The header does not own global state but depends on `x86_topo_system` and topology domain enums from broader x86 CPU headers. It integrates `topology.c`, AMD topology parsing, and generic extended topology parsing.

## Risks And Test Signals

Domain shifts and masks must remain consistent with parser-populated topology. Incorrect relative IDs affect package/core/thread IDs and downstream sched/perf users. Test by comparing parsed topology on Intel, AMD, Hygon, no-APIC, and sparse-domain systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_amd.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_amd.c

## Purpose

This file implements AMD and Hygon-specific topology parsing and fixups. It extracts SMT/core/package/node information from extended CPUID leaves and legacy MSRs, works around disabled topology extensions, sets LLC IDs, and adjusts core IDs on multi-node legacy systems.

## Important APIs, Types, And Functions

Primary public functions are `cpu_parse_topology_amd()` and `cpu_topology_fixup_amd()`. Helpers include `parse_8000_0008()`, `store_node()`, `parse_8000_001e()`, `parse_fam10h_node_id()`, `legacy_set_llc()`, `topoext_fixup()`, and `parse_topology_amd()`.

## Control Flow

Parsing first initializes AMD nodes-per-package to one, attempts to re-enable disabled Topology Extensions for affected Family 15h systems, then prefers modern extended topology leaves through `cpu_parse_topology_ext()`. If unavailable, it parses CPUID `0x80000008` for core-domain width and `0x8000001e` for extended APIC ID, SMT thread count, node ID, and nodes per socket. Legacy systems fall back to `MSR_FAM10H_NODE_ID`. Hygon receives a package-shift workaround for certain non-hypervisor models. Final fixup sets AMD DCM capability for multi-node packages and adjusts legacy core IDs relative to node.

## State, Dependencies, And Integration

State is written into `topo_scan`, `cpuinfo_x86::topo`, and CPU capability bits. Dependencies include CPUID/MSR helpers, cacheinfo AMD/Hygon LLC ID setup, x86 vendor/family/model data, and generic topology parser helpers. It integrates with CPU initialization and later topology registration.

## Risks And Test Signals

AMD topology leaves vary by family, and BIOS-disabled Topology Extensions or Hygon quirks can produce wrong package/core IDs if mishandled. Node ID is not always representable in APIC bits. Test on Family 10h/15h/17h+ AMD systems, Hygon systems, hypervisor guests, systems with multiple nodes per package, and CPUs with leaf `0x80000026`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_amd.c -->
