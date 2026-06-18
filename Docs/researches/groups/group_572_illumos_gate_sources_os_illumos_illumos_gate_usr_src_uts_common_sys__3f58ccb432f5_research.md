# Group Research: group_572_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__3f58ccb432f5

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_pcbe.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_pcbe.h

## Role

Defines the kernel-facing Performance Counter Backend interface used by CPC to support CPU-specific hardware counters.

## Key Interfaces

- `PCBE_VER_1`: required backend ABI version.
- `pcbe_ops_t`: backend operation table covering counter count, implementation identity, event/attribute listing, event coverage, overflow reporting, configuration, programming, stopping, sampling, and freeing.
- `pcbe_ops`: global selected backend operations pointer.
- `PCBE_IMPL_NAME_P4HT`: named implementation string for Pentium 4 HyperThreading.

## Behavior Notes

- Backends expose CPU counter capabilities through `pcbe_caps`, including overflow interrupt and precise overflow support.
- `pcbe_configure()` creates opaque per-counter backend configuration and can walk grouped configurations via a token.
- `pcbe_program()` must collect all grouped configs and program/start hardware counters.
- `pcbe_sample()` updates CPC-visible counter deltas.
- If overflow precision is unavailable, `pcbe_overflow_bitmap()` must conservatively report all counters overflowed.

## Dependencies

Includes `sys/inttypes.h` and `sys/cpc_impl.h`, particularly for integer types and `kcpc_attr_t`.

## Research Relevance

Useful for understanding illumos kernel performance counter plumbing and how CPU-specific drivers integrate with common accounting/profiling paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_pcbe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpr.h

## Role

Defines common checkpoint/resume, suspend-to-disk, reusable statefile, CPR boot, and suspend-to-RAM constants and structures.

## Public/Common Configuration

- `CPR_VERSION`, `CPR_CONFIG`: CPR config version and config path.
- `CPR_CONFIG_MAGIC`, `CPR_DEFAULT_MAGIC`: file magic values.
- `cpr_prop_info`, `cpr_default_mini`, `cpr_default_info`: NVRAM/default CPR metadata.
- `struct cprconfig`: pmconfig-provided statefile and power-management configuration.
- `CFT_UFS`, `CFT_SPEC`, `CFT_ZVOL`: statefile placement types.

## Kernel Statefile Format

Under `_KERNEL`, the file defines the on-disk/on-statefile CPR format:

- `cpr_dump_desc`: dump header.
- `cpr_bitmap_desc`: physical memory bitmap descriptor.
- `cpr_storage_desc`: storage description for dirty/clean pages.
- `cpr_page_desc`: page record descriptor, including compression/checksum flags.
- `cpr_machdep_desc`: machine-dependent resume block descriptor.
- `cpr_terminator`: end marker with statefile size and timing data.
- Magic constants: `CPR_DUMP_MAGIC`, `CPR_BITMAP_MAGIC`, `CPR_PAGE_MAGIC`, `CPR_MACHDEP_MAGIC`, `CPR_TERM_MAGIC`.

## CPR Control Constants

- `AD_CPR_*`: uadmin subcommands for compression, reusable CPR, test modes, debug modes, printing stats, suspend-devices-only, and no-compress flows.
- `AD_LOOPBACK_SUSPEND_TO_RAM_*`, `AD_FORCE_SUSPEND_TO_RAM`, `AD_DEVICE_SUSPEND_TO_RAM`: suspend-to-RAM testing/development commands.
- `DEV_SUSPEND_TO_RAM`, `DEV_CHECK_SUSPEND_TO_RAM`: temporary non-ON application compatibility commands.
- `CPR_DEFAULT`, `CPR_STATE_FILE`: hardcoded cprboot-related paths.
- `CPR_SPEC_OFFSET`: offset used when CPR statefile I/O targets a block device.

## Kernel Runtime State

- `cpr_t`: central CPR state, including flags, substate, active vnode, bitmap descriptors, reserved mapping area, statistics, and allocation retry count.
- Global access macros: `CPR`, `STAT`, `C_VP`.
- Flags: `C_SUSPENDING`, `C_RESUMING`, `C_COMPRESSING`, `C_REUSABLE`, `C_ERROR`.
- Substates: from `C_ST_SUSPEND_BEGIN` through CPU offline, thread stopping, statefile allocation, device suspension, dump, reusable, nodump, and MP paused phases.
- `DCF_CPR_SUSPENDED`: device flag indicating CPR suspend occurred.
- `CPR_TORAM`, `CPR_TODISK`: suspend target differentiation.

## Function Surface

Declares many CPR kernel routines for:

- Statefile path construction and PROM path/property handling.
- Default CPR setup, validation, and file I/O.
- Dumping, reading dump headers, physical pages, terminators, and machine-dependent blocks.
- Device suspend/resume.
- CPU offline/online, CPU allocation/freeing, and CPU stop handling.
- User/kernel thread stop/start/signal handling.
- Bitmap allocation, cleanup, page counting, and page range display.
- Statistics collection, event timing, and reporting.
- Time-of-day save/restore/status.
- Error reporting via `cpr_err()`.

## Important Constraints

- Comments explicitly state CPR statefile structures must remain layout-compatible between ILP32 and LP64 kernels because `cprboot` supports both.
- Bitmap and page descriptors encode physical memory state; layout stability matters for resume correctness.
- `PROM_MAX_READ`, `CPR_MAX_BLOCK`, and `CPR_MAXCONTIG` constrain I/O chunking.

## Research Relevance

This is central to illumos suspend/resume and statefile handling. It intersects filesystem research through statefile placement on UFS, special devices, and ZVOLs, plus direct vnode/block-device I/O during kernel checkpoint.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_event.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_event.h

## Role

Defines kernel CPU idle event notification and per-CPU idle property APIs.

## Idle Callback Priorities

- Priority classes:
  - High static priorities.
  - Dynamic priorities.
  - Low static priorities.
- Constants include `CPU_IDLE_CB_PRIO_LOW_BASE`, `CPU_IDLE_CB_PRIO_DYN_BASE`, `CPU_IDLE_CB_PRIO_HIGH_BASE`, and reserved base.
- `CPU_IDLE_CB_PRIO_DYNAMIC` asks the framework to assign ordering.
- Fixed callback priorities exist for DTrace and, on x86, TLB flushing.

## Idle Properties

Property names include:

- `idle-state`
- `enter-ts`
- `exit-ts`
- `last-idle-time`
- `last-busy-time`
- `total-idle-time`
- `total-busy-time`
- `interupt-count` spelling as present in source

Property types are represented by `cpu_idle_prop_type_t`, and values use `cpu_idle_prop_value_t`.

## Callback API

- `cpu_idle_enter_cbfn_t`: called before hardware idle entry, in idle thread context, interrupts disabled.
- `cpu_idle_exit_cbfn_t`: called on idle exit, in idle thread or interrupt context, interrupts disabled.
- `cpu_idle_check_wakeup_t`: lets callbacks check and report already-pending wakeups.
- `cpu_idle_callback_t`: versioned callback pair.
- `cpu_idle_register_callback()` / `cpu_idle_unregister_callback()` manage callbacks.

## Idle State API

- `cpu_idle_enter()`: notifies entry; returns non-zero if hardware idle should be canceled.
- `cpu_idle_exit()`: notifies exit.
- `cpu_idle_get_context()`: returns current CPU context.
- `cpu_idle_get_cpu_state()`: fetches CPU idle state.

## Property API

Supports creating/destroying properties and handles, querying type/name, getting values in typed forms, setting a current-CPU value, and setting all CPUs.

## Lifecycle

- `cpu_event_init()`
- `cpu_event_init_cpu(cpu_t *)`
- `cpu_event_fini_cpu(cpu_t *)`

## Research Relevance

Important for CPU power, idle accounting, DTrace, and platform wakeup coordination. Filesystem relevance is indirect through scheduling, power transitions, and timing behavior during I/O idle periods.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_pm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_pm.h

## Role

Defines CPU power manager policies, domain state, governor state, utilization events, and platform hooks.

## Key Types

- `cpupm_policy_t`: `CPUPM_POLICY_ELASTIC`, `CPUPM_POLICY_DISABLED`.
- `cpupm_dtype_t`: active and idle power domains.
- `cpupm_state_name_t`: named low-power and max-performance states.
- `cpupm_gov_state_t`: transience governor states.
- `cpupm_util_event_t`: dispatcher utilization events.
- `cpupm_handle_t`: platform handle.
- `cpupm_state_t`: speed plus platform handle.
- `cpupm_domain_t`: domain id/type, state array/current state, named states, raise/lower timestamps, transient histories, governor state, and linked-list pointer.

## Interfaces

- Domain management:
  - `cpupm_domain_init()`
  - `cpupm_domain_id()`
  - `cpupm_change_state()`
  - `cpupm_redefine_max_activepwr_state()`
- Policy:
  - `cpupm_set_policy()`
  - `cpupm_get_policy()`
  - `cpupm_utilization_event()`
- Platform driver hooks:
  - `cpupm_plat_domain_id()`
  - `cpupm_plat_state_enumerate()`
  - `cpupm_plat_change_state()`

## Scope

Definitions are visible when `_KERNEL` or `_KMEMUSER` is defined.

## Research Relevance

Documents the higher-level CPU power manager model used by dispatcher/utilization signals and platform-specific state transitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_pm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_uarray.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_uarray.h

## Role

Defines an aligned per-CPU unsigned 64-bit array abstraction for scalable counters.

## Layout Model

- Each CPU’s counter block is aligned to `CUA_ALIGN` = 128 bytes.
- `CUA_CPU_STRIDE(nr_items)` rounds item count up to the 128-byte stride.
- `CUA_INDEX(nr_items, c, i)` maps CPU index and stat index to the flat array.
- `CPU_UARRAY_VAL(cua, cpu_index, stat_index)` accesses a specific value.

## Main Type

- `cpu_uarray_t`:
  - `cu_nr_items`: number of values per CPU.
  - padding to one alignment unit.
  - flexible `volatile uint64_t cu_vals[]`.

The struct itself is aligned to 128 bytes.

## Kernel API

- `cpu_uarray_zalloc(size_t, int)`
- `cpu_uarray_free(cpu_uarray_t *)`
- `cpu_uarray_sum(cpu_uarray_t *, size_t)`
- `cpu_uarray_sum_all(cpu_uarray_t *)`

Summation saturates at `UINT64_MAX`.

## Research Relevance

Useful for scalable per-CPU statistics and avoiding cacheline sharing in multi-socket systems. This pattern can affect filesystem and block-layer counters.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_uarray.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps.h

## Role

Defines the public kernel CPU caps interface for enforcing hard CPU usage limits at project or zone level.

## Key Constants and State

- `MAXCAP`: maximum cap value; specifying it disables the cap.
- `cpucaps_enabled`: fast global enable check.
- `CPUCAPS_ON()`, `CPUCAPS_OFF()`: guard macros.

## Framework Interfaces

- Initialization:
  - `cpucaps_init()`
- Project/zone lifecycle:
  - `cpucaps_project_add()`
  - `cpucaps_project_remove()`
  - `cpucaps_zone_remove()`
- Cap control:
  - `cpucaps_project_set()`
  - `cpucaps_zone_set()`
  - `cpucaps_project_get()`
  - `cpucaps_zone_get()`

## Scheduling Class Hooks

- `caps_sc_t`: per-thread scheduling-class CPU caps accounting, currently `csc_cputime`.
- `cpucaps_sc_init()`
- `cpucaps_charge()`: charges CPU time and optionally enforces.
- `CPUCAPS_CHARGE()` macro short-circuits when caps are off.
- `cpucaps_enforce()` / `CPUCAPS_ENFORCE()`: place capped threads on wait queues.
- `cpucaps_clock_callout`: hook into clock processing.

## Charge Modes

- `CPUCAPS_CHARGE_ENFORCE`
- `CPUCAPS_CHARGE_ONLY`

## Research Relevance

Important for resource controls, zones, projects, scheduling behavior, and CPU isolation effects on filesystem workloads.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps_impl.h

## Role

Defines private implementation state for CPU caps.

## Key Constants

- `NOCAP`: alias for `MAXCAP`; disables caps.
- `MAX_USAGE`: maximum usage value, based on `LONG_MAX` for LP64 or explicit 64-bit max for non-LP64.

## Main Structure

- `cpucap_t` stores per-project or per-zone cap state:
  - list linkage.
  - associated project or zone.
  - wait queue for capped threads.
  - kstat pointer.
  - generation for zone caps.
  - scaled cap value and current usage.
  - usage lock.
  - statistics: max usage, below-cap ticks, above-cap ticks.

## Macros

- `CAP_ENABLED()`, `CAP_DISABLED()`
- `PROJECT_IS_CAPPED()`
- `ZONE_IS_CAPPED()`

## Dependencies

Includes kstats, list handling, time, wait queues, and the public `cpucaps.h`.

## Research Relevance

Shows how caps are represented internally and enforced through wait queues, useful when tracing scheduling throttling or resource-control side effects.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpudrv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpudrv.h

## Role

Defines private CPU power-management driver state, speed-level data, monitoring thresholds, and driver/machine hooks.

## Speed State

- `cpudrv_pm_spd_t`:
  - platform-dependent `speed`.
  - monitoring quantum count.
  - up/down speed links.
  - idle and user high/low watermarks.
  - counters for hysteresis.
  - power framework level.

The comment notes speed means divisor on SPARC and frequency on x86.

## PM State

- `cpudrv_pm_t`:
  - speed list head/current speed and count.
  - last microstate accounting snapshot.
  - PM busy count.
  - taskq, timeout id/count/lock/cv.
  - x86-only governor thread and effective top speed.
  - `pm_started`.

## Thresholds and Timing

- x86 and non-x86 idle thresholds differ.
- `CPUDRV_USER_HWM`, `CPUDRV_IDLE_BUF_ZONE`.
- `CPUDRV_QUANT_CNT_NORMAL` is 1 second on x86, 5 seconds elsewhere.
- `CPUDRV_QUANT_CNT_OTHR` is 1 second.
- Taskq dimensions are fixed to one worker and small queue bounds.

## Driver State

- `cpudrv_devstate_t`: devinfo handle, CPU pointer/id, PM data, and lock.
- Globals:
  - `cpudrv_state`
  - `cpudrv_enabled`

## Debugging

Under `DEBUG`, defines debug categories and `DPRINTF()` backed by `prom_printf`.

## Function Surface

Declares speed change, CPU id lookup, governor-thread detection, machine init/fini, readiness/enabled checks, supported-frequency setup, and CPU lookup helpers.

## Research Relevance

Useful for understanding CPU frequency/power transitions and their interaction with dispatcher microstate accounting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpudrv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuid_drv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuid_drv.h

## Role

Defines names, minor values, ioctls, and data structures for the `/dev/cpu/.../cpuid` driver interface.

## Device Names

- Driver: `cpuid`
- Self node: `self`
- Directory names:
  - `cpu`
  - `self`
  - `cpuid`
- `CPUID_SELF_NAME`: `cpu/self/cpuid`

## Minor and Ioctls

- `CPUID_SELF_CPUID_MINOR`: special minor for current CPU at invocation time.
- `CPUID_IOC`: ioctl base.
- `CPUID_GET_HWCAP`
- `CPUID_RDMSR`

The file notes ioctl numbers are not exported interfaces.

## Data Structures

- `struct cpuid_get_hwcap`:
  - architecture name pointer.
  - three hardware capability words.
- `struct cpuid_rdmsr`:
  - MSR number.
  - MSR value.
- `_SYSCALL32_IMPL` variant:
  - `struct cpuid_get_hwcap32`.

## Research Relevance

Small but useful for user/kernel CPU identification and MSR access plumbing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuid_drv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupart.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupart.h

## Role

Defines CPU partition structures and APIs used by processor sets, dispatching, load averages, lgroups, and CMT processor groups.

## Key Types

- `cpupartid_t`: integer partition id.
- `CP_DEFAULT`: default partition id.
- `CP_ALL`, `CP_NONEMPTY`: `cpupart_list()` filters.
- `cpupart_t`: partition state:
  - partition-wide kernel preemption queue.
  - id, CPU count, partition list links.
  - CPU list and kstat.
  - runnable/running counts.
  - cumulative load statistics.
  - load average data.
  - lgroup set/load table, generation, hint.
  - attributes.
  - CMT PG bitset.
  - halted CPU bitset.
- `cpupart_kstat_t`: named kstat fields for updates, runnable/waiting totals, CPU count, and load averages.

## Scheduling Macros

- `CP_MAXRUNPRI(cp)`: maximum run priority for a partition global queue.
- `DISP_MUST_SURRENDER(t)`: checks whether a thread must yield to higher-priority runnable work on local or partition queues.

## Globals

- `cp_default`
- `cp_list_head`
- `cp_numparts`
- `cp_numparts_nonempty`
- `cp_haltset_fanout`

## APIs

Includes initialization, lookup, create/destroy, CPU attach/query/list, thread binding, kernel preempt queue allocation, load averages, partition listing, and attribute get/set.

## Research Relevance

Important for scheduling topology, processor sets, CPU partition load accounting, and how zones/projects can be isolated at CPU level.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupart.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupm.h

## Role

Small CPU power-management public header that bridges common CPU state and machine-specific CPU PM support.

## Interface

- Includes:
  - `sys/types.h`
  - `sys/cpuvar.h`
  - `sys/cpupm_mach.h`
- Declares:
  - `cpupm_set_supp_freqs(cpu_t *, int *, uint_t)`

## Research Relevance

A narrow helper interface for recording supported CPU frequencies. It connects platform-specific PM code to common CPU structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuvar.h

## Role

Defines the central `cpu_t` per-CPU kernel structure, CPU state flags, CPU-set manipulation APIs, CPU lifecycle APIs, and per-CPU statistics macros.

## Core Per-CPU Structures

- `ftrace_data_t`: per-CPU fast event tracing state.
- `cpu_t`: large per-CPU state structure containing:
  - CPU ids and flags.
  - self pointer and current/idle/pause threads.
  - LWP/FPU owner state.
  - CPU partition, lgroup load, CPU PG membership.
  - CPU list links across global, online, partition, lgroup, and load partitions.
  - dispatch queue and scheduler/preemption state.
  - interrupt stack/thread/activity/base SPL state.
  - per-CPU statistics and CPU info kstat.
  - profiling PCs and PIL.
  - ftrace state.
  - deadman counters.
  - CPC performance counter context and lock.
  - `processor_info` data and CPU state start time.
  - CPR flags.
  - cyclic subsystem data.
  - networking squeue set.
  - pool properties.
  - DTrace fasttrap/probe accounting.
  - microstate accounting and load average.
  - debug id/brand strings.
  - interrupt weight, VM data, physical IDs.
  - current/supported frequencies.
  - CPC profiling PCs.
  - interrupt load tracking.
  - per-CPU pseudo-random rotor.
  - capacity/utilization info.
  - CPU generation for online/offline changes.
  - architecture-specific `machcpu` tail under `_MACHDEP`.

The file warns that adding members can affect CTF uniquification; new members must be added before `cpu_m_pad`.

- `cpu_core_t`: context-safe per-CPU state for DTrace flags, DCPC interrupt state, illegal value, and pid provider lock, padded to avoid false sharing.

## Interrupt and Random Macros

- `CPU_ON_INTR(cpup)`
- `INTR_ACTIVE(cpup, level)`
- `CPU_PSEUDO_RANDOM()`
- `INTR_STACK_SIZE`

## CPU Flags

Defines core CPU lifecycle/state flags:

- `CPU_RUNNING`
- `CPU_READY`
- `CPU_QUIESCED`
- `CPU_EXISTS`
- `CPU_ENABLE`
- `CPU_OFFLINE`
- `CPU_POWEROFF`
- `CPU_FROZEN`
- `CPU_SPARE`
- `CPU_FAULTED`
- `CPU_DISABLED`

Also defines `CPU_ACTIVE()` and `CPU_FORCED`.

## DTrace and Dispatcher Flags

- DTrace flags cover no-fault, drop, bad address/alignment, divide by zero, illegal op, no scratch, privilege faults, tuple overflow, entry/bad stack, and SPARC fake restore.
- Aggregate masks:
  - `CPU_DTRACE_FAULT`
  - `CPU_DTRACE_ERROR`
- Dispatcher flags:
  - `CPU_DISP_DONTSTEAL`
  - `CPU_DISP_HALTED`

## CPU Sets

- `cpuset_t`: opaque or concrete bitmap depending on `_MACHDEP`.
- APIs for allocation/free, all/all-but/only, add/delete, atomic add/delete, exclusive atomic add/delete, or/xor/and/zero, equality/null tests, find, bounds, membership.
- `_MACHDEP` compatibility macros wrap these APIs.

## CPU Globals

Includes arrays/lists and counters:

- `cpu[]`, `cpu_seq`, `cpu_list`, `cpu_active`, `cpu_active_set`
- `ncpus`, `ncpus_online`, `ncpus_intr_enabled`
- boot/max CPU counters and max ids
- `cpu_inmotion`, `clock_cpu_list`, `max_cpu_seqid_ever`
- `CPU` macro maps to `curcpup()` on x86 and `curthread->t_cpu` elsewhere.

## CPU Statistics

- `CPU_STATS_ENTER_K()`, `CPU_STATS_EXIT_K()`
- `CPU_STATS_ADD_K()`
- `CPU_STATS_ADDQ()`: emits DTrace probe then increments stat.
- `CPU_STATS()`
- `CPU_NEW_GENERATION()`: increments online/offline generation.

## CPR CPU Flags

- `CPU_CPR_OFFLINE`, `CPU_CPR_ONLINE`
- `CPU_CPR_IS_OFFLINE()`, `CPU_CPR_IS_ONLINE()`, `CPU_SET_CPR_FLAGS()`

## CPU Lifecycle and Scheduling APIs

Declares routines for CPU list management, active list management, kstats, visibility by zone, interrupt stats, cross-call mailbox init, poking CPUs, pausing/restarting CPUs, online/offline/spare/faulted/power state transitions, interrupt routing enable/disable/count, state checks, processor_info state strings, CPU clock/frequency strings, configure/unconfigure, bound thread destruction, CPU binding/unbinding, thread affinity, migration control, weak binding, and interrupt participation.

## CPU Setup Events

- `cpu_setup_t`: `CPU_INIT`, `CPU_CONFIG`, `CPU_UNCONFIG`, `CPU_ON`, `CPU_OFF`, `CPU_CPUPART_IN`, `CPU_CPUPART_OUT`, `CPU_SETUP`, `CPU_INTR_ON`.
- `cpu_setup_func_t`
- Registration/notification APIs:
  - `register_cpu_setup_func()`
  - `unregister_cpu_setup_func()`
  - `cpu_state_change_notify()`

## Research Relevance

One of the most important kernel headers in this batch. It anchors CPU scheduling, CPU hotplug, interrupt routing, DTrace state, power/current frequency accounting, zones visibility, processor sets, and per-CPU statistics that filesystem and block-layer performance work often depends on.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crc32.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crc32.h

## Role

Defines CRC32 theory notes, table-generation/computation macros, the standard Solaris CRC32 polynomial, and the kernel precomputed table declaration.

## Main Macros

- `CRC32_INIT(table, poly)`: fills a 256-entry `uint32_t` lookup table for a polynomial.
- `CRC32(crc, buf, size, start, table)`: computes CRC over a byte buffer.
- `CRC32_STRING(crc, len, str, start, table)`: computes CRC over a NUL-terminated string and records length.
- `CRC32_POLY`: `0xEDB88320U`.
- `CRC32_TABLE`: full precomputed 256-entry table for `CRC32_POLY`.

## Kernel Interface

- `extern const uint32_t crc32_table[256];`

## Behavior Notes

- Documentation explains initial value choice, polynomial constraints, bitwise algorithm, bytewise algorithm, and lookup-table optimization.
- Macros use local variable names prefixed with `X` to reduce caller collision risk, but they are still statement-like macro blocks.

## Research Relevance

CRC32 is common in storage, networking, and metadata checks. This header supplies illumos’s common table/macro implementation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred.h

## Role

Defines the opaque credential type and kernel accessor/manipulation API.

## Main Type

- `typedef struct cred cred_t;`

The implementation is private in `sys/cred_impl.h`.

## Kernel Macros and Globals

- `CRED()`: current thread credential.
- `ngroups_max`: supplemental group limit.
- `kcred`: all-privileges kernel credential.

## Credential Lifecycle

- `cred_init()`
- `crhold()`, `crfree()`
- `cralloc()`, `cralloc_ksid()`
- `crget()`
- `crcopy()`, `crcopy_to()`
- `crdup()`, `crdup_to()`
- `crgetcred()`
- `crset()`
- `zone_kcred()`

## Identity and Permission APIs

- Group checks:
  - `groupmember()`
  - `supgroupmember()`
- Process permission checks:
  - `hasprocperm()`
  - `prochasprocperm()`
- Credential comparison:
  - `crcmp()`
- Accessors:
  - UIDs/GIDs: effective, real, saved.
  - zone id and project id.
  - audit info and modifiable audit info.
  - refcount.
  - group list and group count.
  - mapped credential.

## Mutation APIs

- UID/GID setting:
  - `crsetresuid()`
  - `crsetresgid()`
  - `crsetugid()`
- Supplemental groups:
  - `crsetgroups()`
  - `crgrpcopyin()`
  - `crgrprele()`
  - `crsetcredgrp()`
- Zone/project:
  - `crsetzone()`, `crgetzone()`
  - `crsetprojid()`
- NFS:
  - `crnetadjust()`
- procfs:
  - `cred2prcred()`
- Trusted Solaris/Rampart:
  - `crgetlabel()`
  - `crisremote()`
- Ephemeral IDs:
  - `VALID_UID()`, `VALID_GID()`
  - `valid_ephemeral_uid()`, `valid_ephemeral_gid()`
  - `eph_uid_alloc()`, `eph_gid_alloc()`
- SIDs and privileges:
  - `crsetsid()`, `crsetsidlist()`
  - `crgetsid()`, `crgetsidlist()`
  - `crsetpriv()`
- KLPD:
  - `crgetcrklpd()`
  - `crsetcrklpd()`

## Research Relevance

Credentials are central to VFS permission checks, zones, projects, NFS identity handling, auditing, and privilege enforcement.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred_impl.h

## Role

Defines the private credential implementation layout for kernel and kmem consumers.

## Main Structures

- `credgrp_t`:
  - reference count.
  - number of groups.
  - flexible-style group array with one declared element.

- `struct cred`:
  - reference count.
  - effective, real, and saved UID/GID.
  - privilege state.
  - project id.
  - zone pointer.
  - effective label pointer.
  - KLPD pointer.
  - SID pointer.
  - supplemental groups pointer.
  - dynamic audit info follows when audit is enabled.

## Macros

- `CR_PRIVS(c)`: address of credential privilege state.
- `CR_PRIVSETS(c)`: privilege set array.

## Important Notes

The file explicitly states:

- It is not public.
- Credentials are shared and read-only after finalization except for `cr_ref`.
- Kernel modules should use accessors in `cred.h`.
- Credential size depends on `ngroups_max`; callers cannot safely declare one directly.
- Correctly sized credentials come from allocation/copy routines.

## Research Relevance

Critical when tracing low-level credential lifetime, memory layout, privilege checks, and VFS authorization behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crtctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crtctl.h

## Role

Defines legacy cursor/CRT control command byte constants and video attribute values.

## Command Constants

Includes cursor movement and screen editing commands:

- `ESC`
- `CUP`, `CDN`, `CRI`, `CLE`
- `NL`, `HOME`, `VHOME`, `LCA`, `CRTN`
- Blink, clear, erase, delete, insert, keyboard lock/unlock, tabs, scrolling, segment/protect controls.
- Variable-screen controls: `SVSCN`, `UVSCN`, `DVSCN`.
- Video controls: `SVID`, `CVID`, `DVID`.

## Video Attributes

- `VID_NORM`
- `VID_UL`
- `VID_BLNK`
- `VID_REV`
- `VID_DIM`
- `VID_BOLD`
- `VID_OFF`

## Other Constants

- `BRK`: transmit break.
- `HIQ`: place remainder of write on high-priority queue.

## Research Relevance

A small legacy terminal/control header. Filesystem relevance is minimal, but it may appear in historical TTY/console code paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crtctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cryptmod.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cryptmod.h

## Role

Defines a Sun-private STREAMS crypto module interface, including ioctls, method identifiers, setup structures, and kernel module state.

## Ioctls

Base:

- `CRYPTIOC`

Commands:

- `CRYPTIOCSETUP`
- `CRYPTIOCSTOP`
- `CRYPTIOCSTARTENC`
- `CRYPTIOCSTARTDEC`
- `CRYPTPASSTHRU`

## Methods

- `CRYPT_METHOD_NONE`
- DES CFB/CBC variants.
- 3DES CBC SHA1.
- ARCFOUR HMAC MD5 and export variant.
- AES128/AES256.

Validation/helper macros:

- `CR_METHOD_OK()`
- `IS_RC4_METHOD()`
- `IS_AES_METHOD()`

## Direction and IV Usage

- Directions:
  - `CRYPT_ENCRYPT`
  - `CRYPT_DECRYPT`
  - `CR_DIRECTION_OK()`
- IV usage:
  - `IVEC_NEVER`
  - `IVEC_REUSE`
  - `IVEC_ONETIME`
  - `CR_IVUSAGE_OK()`

## Sizes and Options

Defines SHA1, DES3, ARCFOUR, AES key/hash/block sizes, truncated AES HMAC length, and max key/IV lengths.

Options:

- `CRYPTOPT_NONE`
- `CRYPTOPT_RCMD_MODE_V1`
- `CRYPTOPT_RCMD_MODE_V2`
- `ANY_RCMD_MODE()`
- `RCMD_LEN_SZ`
- `CR_OPTIONS_OK()`

## User Setup Structure

- `struct cr_info_t`:
  - key and IV buffers.
  - key/IV lengths.
  - IV usage.
  - direction mask.
  - crypto method.
  - option mask.

## Kernel State

Under `_KERNEL`:

- Usage constants for rcmd, ARCFOUR, AES.
- Default block sizes and ARCFOUR export salt.
- `struct cipher_data_t`: key/block/IV/saveblock buffers, mechanism type, crypto keys/templates/context, byte counts, lengths, IV usage, method, options.
- `struct rcmd_state_t`: plaintext/cipher lengths, received count, next length, mblk accumulator.
- Ready masks: `CRYPT_WRITE_READY`, `CRYPT_READ_READY`.
- `struct tmodinfo`: encryption/decryption cipher data, rcmd state, ready mask.

## Research Relevance

Documents legacy STREAMS encryption behavior and how it bridges to the kernel crypto API. Relevant for historical secure r-command paths and STREAMS data transformation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cryptmod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/api.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/api.h

## Role

Defines the kernel consumer API for the illumos Kernel Cryptographic Framework.

## Common Handles and Request State

- `crypto_req_id_t`
- `crypto_bc_t`
- `crypto_context_t`
- `crypto_ctx_template_t`
- `crypto_call_flag_t`
- Flags:
  - `CRYPTO_ALWAYS_QUEUE`
  - `CRYPTO_NOTIFY_OPDONE`
  - `CRYPTO_SKIP_REQID`
- `crypto_call_req_t`: callback, callback argument, flags, and request id.

## Mechanism and Context Templates

- `CRYPTO_MECH_INVALID`
- `crypto_mech2id()`
- `crypto_create_ctx_template()`
- `crypto_destroy_ctx_template()`

## Operation Families

The header declares single-part, init/update/final multipart, and provider-specific variants for:

- Digest.
- MAC and MAC verify.
- Sign, sign recover.
- Verify, verify recover.
- Encryption.
- Decryption.
- Encrypt/MAC dual operation.
- MAC/decrypt and MAC-verify/decrypt dual operations.

Most families include both provider-neutral and `_prov` variants that accept `crypto_provider_t` and session ids.

## Session, Object, and Key Management

Session APIs:

- `crypto_session_open()`
- `crypto_session_close()`
- `crypto_session_login()`
- `crypto_session_logout()`

Object APIs:

- copy, create, destroy, get/set attribute value, get size, find init/find/final.

Key APIs:

- derive, generate, generate pair, unwrap, wrap, key check by provider or framework.

## Async Cancellation

- `crypto_cancel_req()`
- `crypto_cancel_ctx()`

## Mechanism Lists and Provider Info

- `crypto_get_mech_list()`
- `crypto_free_mech_list()`
- `crypto_get_provider()`
- `crypto_get_provinfo()`
- `crypto_release_provider()`

## Event Notification

Events:

- `CRYPTO_EVENT_MECHS_CHANGED`
- `CRYPTO_EVENT_PROVIDER_REGISTERED`
- `CRYPTO_EVENT_PROVIDER_UNREGISTERED`

Types:

- `crypto_event_change_t`
- `crypto_notify_event_change_t`
- `crypto_notify_handle_t`
- `crypto_notify_callback_t`

APIs:

- `crypto_notify_events()`
- `crypto_unnotify_events()`

## Buffer Callback API

- `crypto_bufcall_alloc()`
- `crypto_bufcall_free()`
- `crypto_bufcall()`
- `crypto_unbufcall()`

## Mechanism Information

- Usage flags:
  - encrypt
  - decrypt
  - MAC
- `crypto_mechanism_info_t`
- 32-bit syscall variant.
- `crypto_get_all_mech_info()`
- `crypto_free_all_mech_info()`

## Research Relevance

This is the main kernel-facing crypto consumer surface. It is relevant to encrypted storage, checksums/MACs, IPsec, module verification, ZFS crypto-adjacent paths, and device/provider selection.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/api.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/common.h

## Role

Defines common data structures, mechanism names, key/data representations, provider metadata, command types, and error codes for the Kernel Cryptographic Framework.

## Mechanisms

- `CRYPTO_MAX_MECH_NAME`
- `crypto_mech_name_t`
- `crypto_mech_type_t`
- `crypto_mechanism_t`
- `crypto_mechanism32_t` for 32-bit syscall compatibility.

Parameter structures include AES CTR, CCM, GCM, GMAC, and ECDH1 derive parameters, with 32-bit variants under kernel syscall compatibility.

## Mechanism Flags and Names

- Key size units:
  - `CRYPTO_KEYSIZE_UNIT_IN_BITS`
  - `CRYPTO_KEYSIZE_UNIT_IN_BYTES`
- `CRYPTO_CAN_SHARE_OPSTATE`

Mechanism name constants include MD4/MD5/SHA1/SHA2, HMAC variants, DES/3DES, Blowfish, AES CBC/CMAC/ECB/CTR/CCM/GCM/GMAC/CFB128, RC4, RSA, EC, ECDH, and ECDSA names.

## Shared Operation Context

- `arcfour_state_t`: shared RC4 operation state with architecture-specific layout.

## Data Representation

- `crypto_data_format_t`: raw, `uio`, or `mblk`.
- `crypto_data_t`: format, offset, length, misc data, and union for raw iovec, uio, or mblk.
- `crypto_dual_data_t`: adds second offset/length for dual operations.

## Key Representation

- `crypto_key_format_t`: raw, reference, or attribute list.
- `crypto_attr_type_t`
- PKCS#11-like attribute constants for RSA, DH/DSA, EC, generic secret, AES, DES.
- `crypto_object_attribute_t`
- `crypto_key_t`
- 32-bit attribute/key variants.
- Convenience macros for key union fields.
- `CRYPTO_BITS2BYTES()` and `CRYPTO_BYTES2BITS()`.

## Providers and Sessions

- Provider types: hardware, software, logical.
- `crypto_provider_id_t`, `KCF_PROVID_INVALID`.
- Provider and device list entries.
- User types: security officer and user.
- `crypto_version_t`
- Opaque session/provider handles.
- Provider extended info limits and `crypto_provider_ext_info_t`.
- `crypto_session_id_t`

## Data Command Types

- Copy from data.
- Copy to data.
- Compare to data.
- MD5/SHA1/SHA2 digest data.
- GHASH data.

Operation flags include update/final, MD5/SHA1/SHA2, sign, verify.

## Status and Error Codes

Defines `CRYPTO_SUCCESS` through `CRYPTO_FIPS140_ERROR`, with `CRYPTO_LAST_ERROR` currently matching `0x53`.

Errors cover memory, arguments, device, encrypted data, keys, mechanisms, sessions, signatures, templates, wrapping/unwrapping, users/PINs, random number generation, provider/version/busy states, permissions, weak keys, and FIPS errors.

Special values:

- `CRYPTO_UNAVAILABLE_INFO`
- `CRYPTO_EFFECTIVELY_INFINITE`

## Research Relevance

Foundational KCF ABI/types header. Any kernel crypto consumer, provider, encrypted I/O path, or crypto-adjacent filesystem integration depends on these definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/dca.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/dca.h

## Role

Private header for the Deimos cryptographic accelerator driver based on Broadcom 582x hardware.

## Scope

The file explicitly states everything is private to the DCA device driver.

## Driver Identity and Tunables

- Driver name: `dca`
- Manufacturer id: `SUNWdca`
- Work/request watermarks for MCR1 and MCR2.
- Limits:
  - two MCRs.
  - max requests per MCR.
  - max fragments.
  - preallocated work structures.
  - max packet size differs on x86 due to rootnex behavior.

## Algorithm Constants

Includes sizes and ranges for DES, 3DES, DSA, SHA1, MD5-HMAC, SHA1-HMAC, RSA, IVs, and key sizes.

## Mechanism/Operation Types

- RSA modes: encrypt, decrypt, sign, verify, sign recover, verify recover.
- DSA modes: sign, verify.
- DCA mechanism enum for DES CBC, 3DES CBC, DSA, RSA X.509, RSA PKCS.
- Defines `SUN_CKM_DSA`.

## FMA

- `dca_fma_eclass_t`: hardware device, timeout, none.

## Core Structures

- `dca_device`: PCI vendor/device/model identity.
- `dca_chain`: DMA data buffer chain entry with descriptor/buffer kernel addresses, DMA handles, and physical addresses.
- `dca_listnode`: double linkage plus second linkage pair.
- `dca_rng` and `union dca_parameters`.
- `dca_ctx_t`: crypto context with mechanism, mode, atomic flag, RSA/DSA modulus data, DES/3DES IV/key/residual data, and duplicate input data.
- `dca_request_t`: full request/job descriptor, including KCF request handle, input/output data, context, DMA context/input/output buffers, programmed MCR fields, callback, flags, algorithm parameters, stats, pre-mapped chains, dynamic user-buffer chains, context-page offset, and destroy flag.
- `dca_work_t`: MCR work item with DMA mapping and request slots.
- `dca_worklist_t`: per-MCR queue state, locks, condition variable, freelists, wait/run queues, scheduling timeout, flow-control settings, drain flag, and kstats.
- `dca_stat_t`: kstat layout.
- `dca_cookie_t`: ioctl blocking state.
- `dca_t`: per-device instance with devinfo, registers, interrupt locks, worklists, model/id, kstats, RNG buffers/state, FMA capabilities, and context list.

## Request and Device Flags

Request flags include in-place, scatter, gather, no-cache, encrypt/decrypt, triple-DES, and atomic.

Device flags include failed, power management, and RNG-SHA1 support.

## Hardware Register Definitions

Defines PCI config offsets/bit fields, command/status registers, DMA control/status bits, MCR offsets/sizes/flags, data-buffer descriptor offsets, and hardware context offsets for 3DES, IPsec, RSA, and DSA operations.

## Access Macros

- `PUTMCR*`, `GETMCR*`
- `PUTDESC*`
- `PUTCTX*`
- `CTXBCOPY`
- `GETCSR`, `PUTCSR`, `SETBIT`, `CLRBIT`
- alignment and word extraction helpers.
- hardening check `CHECK_REGS()`.
- queue and worklist helpers.

## Debug and PKCS#11 Constants

Under `DEBUG`, defines debug categories and `DBG`.

The file locally defines PKCS#11 object/key attribute constants needed by the driver.

## Function Surface

Declares driver routines for:

- Debug/error reporting.
- 3DES context/init/update/final/atomic/free.
- RSA init/start/atomic/free.
- DSA sign/verify/init/atomic/free.
- RNG and random buffer management.
- Kstat initialization.
- Request allocation/free/destruction, queue manipulation, DMA chain binding/unbinding, starting jobs, completion, data length/gather/scatter/residual handling, duplicate crypto data, I/O validation, scatter/gather checks, key attribute lookup, buffer address extraction, coalescing, bignum helpers, DMA handle checking, and context freeing.

## Research Relevance

Important for hardware crypto provider internals and KCF provider implementation. It shows DMA, scatter/gather, request scheduling, device hardening, FMA, and asymmetric/symmetric operation integration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/dca.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/elfsign.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/elfsign.h

## Role

Defines private structures and status codes for ELF/file signature metadata exchanged among elfsign, libpkcs11, kcfd, and KCF.

## Status

- `ELFsign_status_t`:
  - unknown
  - success
  - failed
  - not signed
  - invalid cert path
  - invalid ELF object
  - unavailable

## Constants

- `SIG_MAX_LENGTH`: 1024.
- `ELF_SIGNATURE_SECTION`: `.SUNW_signature`.
- `filesig_vers_t`: 32-bit signature version type.

## Signature Layout

- `struct filesignatures`:
  - signature count.
  - padding.
  - union containing raw data, one `filesig`, or alignment field.
- `struct filesig`:
  - total signature size.
  - version.
  - version-specific payload:
    - version 1: DN size, signature size, OID size, data.
    - version 3: timestamp plus DN/signature/OID sizes and data.

Macros alias nested union fields for easier access.

## Traversal and Alignment

- `filesig_ALIGN(s)`: 64-bit alignment.
- `filesig_next(ptr)`: advances to the next signature record.

## Versions

- `FILESIG_UNKNOWN`
- `FILESIG_VERSION1`: all but signature section.
- `FILESIG_VERSION2`: version 1 format, SHF_ALLOC only.
- `FILESIG_VERSION3`: all but signature section.
- `FILESIG_VERSION4`: version 3 format, SHF_ALLOC only.

## Research Relevance

Relevant to module/file signature verification and KCF/daemon coordination around signed ELF objects.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/elfsign.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/impl.h

## Role

Defines private Kernel Cryptographic Framework implementation structures, provider tables, policy state, mechanism tables, provider operation wrappers, and internal exported functions.

## Kstats and Per-CPU Provider State

- `kcf_prov_stats_t`: provider total/passed/failed/busy statistics.
- `kcf_stats_t`: framework thread pool, queue, and taskq stats.
- `CPU_SEQID`: current CPU sequential id.
- `kcf_lock_withpad_t`: padded mutex.
- `kcf_prov_cpu_t`: per-CPU provider counters and hold/job counts, padded for cacheline isolation.
- `KCF_PROV_LOAD(pd)`: approximate provider load using refcount or taskq allocation count if busy.

## Provider State

- Provider states:
  - allocated
  - unverified
  - unverified FIPS140
  - verification failed
  - ready
  - busy
  - failed
  - disabled
  - unregistering
  - unregistered
- Macros:
  - `KCF_IS_PROV_UNVERIFIED()`
  - `KCF_IS_PROV_USABLE()`
  - `KCF_IS_PROV_REMOVED()`
- Internal flag:
  - `KCF_LPROV_MEMBER`

## Provider Descriptor

- `kcf_provider_desc_t` contains:
  - provider type and session id.
  - taskq.
  - per-CPU bins.
  - state lock/cv and state.
  - logical provider membership list.
  - provider handle and ops vector.
  - mechanism index table and mechanism list.
  - name, instance, module id, modctl.
  - description and flags.
  - hash/HMAC limits.
  - KCF-private handle and provider id.
  - kstat pointer and stats data.

Reference/job/stat macros manage per-CPU refcounts, job counts, completion signaling, and dispatch/failure/busy accounting.

## Mechanism Tables

- `crypto_mech_info_list_t`: valid second mechanisms for dual operations.
- `kcf_prov_mech_desc_t`: provider mechanism descriptor chain entry.
- `kcf_mech_entry_t`: mechanism table entry with name, id, hardware provider chain, software provider, hardware provider count, software generation, hardware threshold, parameter copyin function, and padding.
- Mechanism table limits:
  - digests, ciphers, MACs, sign/verify, key operations, misc.
- Global tables:
  - `kcf_digest_mechs_tab`
  - `kcf_cipher_mechs_tab`
  - `kcf_mac_mechs_tab`
  - `kcf_sign_mechs_tab`
  - `kcf_keyops_mechs_tab`
  - `kcf_misc_mechs_tab`
- Operation classes:
  - digest, cipher, MAC, sign, keyops, misc.
- ID helpers:
  - `KCF_MECHID()`
  - `KCF_MECH2CLASS()`
  - `KCF_MECH2INDEX()`
  - provider mechanism lookup macros.

## Policy and Software Configuration

- `kcf_policy_desc_t`: disabled-mechanism policy per provider/module, with refcount and mutex-protected disabled mechanism list.
- Policy refhold/refrele macros free descriptors on last release.
- `kcf_soft_conf_entry_t`: software module name plus mechanisms used as module autoload hints.
- Globals:
  - `soft_config_mutex`
  - `soft_config_list`

## Sessions and Minor State

- `crypto_provider_session_t`: links provider sessions to KCF provider descriptors.
- `crypto_session_data_t`: session lock/cv/flags, pre-approved amount, active contexts for digest/encrypt/decrypt/MAC/sign/verify/recover operations, provider, find cookie, provider session.
- Session flags:
  - in use
  - busy
  - closed
- `KCF_MAX_PIN_LEN`: 1024.
- `crypto_minor_t`: `/dev/crypto` minor state with refcount, lock/cv, session table, provider array, and provider sessions.
- `rc_project_crypto_mem`: project crypto memory resource-control handle.

## Internal Return Codes and RNG

- Internal status codes for mechanism lookup/table failure.
- `SUN_RANDOM`
- `CRYPTO_FG_RANDOM`: internal function group for random generation providers.

## Provider Ops Wrappers

The file defines extensive macros that call provider ops when present or return `CRYPTO_NOT_SUPPORTED` otherwise. Families include:

- Control/status.
- Context template creation/free.
- Mechanism copyin/copyout/free.
- Digest.
- Cipher encrypt/decrypt.
- MAC.
- Sign and sign recover.
- Verify and verify recover.
- Legacy dual operations.
- Dual cipher/MAC operations.
- Random seed/generate.
- Session open/close/login/logout.
- Object create/copy/destroy/get size/get/set attributes/find.
- Key generate/generate pair/wrap/unwrap/derive/check.
- Provider management: ext info, token init, PIN init/set.
- No-store key operations.

## Private KCF Entry Points

Exports internal routines from KCF to crypto/cryptoadmin modules, including:

- Single-operation digest/MAC/encrypt/decrypt/sign/verify variants.
- Digest-key provider operation.
- Dual update operations.
- Random seeding/generation.
- Provider info, mechanisms, token/PIN management.
- Administrative device/software provider list and disabled-mechanism configuration.
- Door loading, soft module unloading/loading.
- Mechanism number/function list/provider permitted mechanism building.
- Mechanism table init/add/remove/lookup.
- Provider descriptor allocation/free and registration undo/redo.
- RNG initialization and byte retrieval.
- Entropy insertion and poll support.
- Data movement helpers for `uio`, `mblk`, raw output/input, compare, digest data, block update across iov/uio/mblk.
- Key copy and attribute lookup.
- Parameter copyin helpers for AES CCM/GCM/GMAC and ECDH1.

## Provider and Policy Table Access

Provider table routines include init, add/remove, lookup by name/device/id, hardware provider table retrieval, slot list retrieval, provider table freeing, software provider lookup, and refcount query.

Policy routines include disabled-mechanism checks, policy table init, descriptor free, policy removal by name/device, lookup by name/device, loading disabled software/device policy, and removing soft config.

## Research Relevance

This is the central private KCF implementation header. It is essential for understanding provider registration, dispatch, mechanism lookup, policy enforcement, `/dev/crypto` session state, random provider plumbing, provider lifecycle, and how consumers are mapped to software/hardware crypto providers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/impl.h -->