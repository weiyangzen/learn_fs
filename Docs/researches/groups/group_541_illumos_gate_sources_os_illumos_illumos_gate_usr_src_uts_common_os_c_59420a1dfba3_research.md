# Group Research: group_541_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_c_59420a1dfba3

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu.c

## Role

`cpu.c` is the architecture-independent CPU control core for illumos. It manages CPU topology lists, online/offline transitions, CPU hotplug configuration, processor binding, weak migration barriers, CPU pause coordination, CPU state reporting, processor-set/zone visibility, and CPU kstats.

It is the shared policy and synchronization layer above machine-dependent hooks such as `mp_cpu_start()`, `mp_cpu_stop()`, `mp_cpu_poweron()`, `mp_cpu_poweroff()`, `mp_cpu_configure()`, and interrupt enable/disable helpers.

## Global State and Locking

The central lock is `cpu_lock`, which protects `ncpus`, `ncpus_online`, `cpu_flag`, `cpu_list`, `cpu_active`, `cpu_active_set`, `cpu_available`, `cpu_seqid_inuse`, `cpu_seq`, `max_cpu_seqid_ever`, dispatch queue reallocations, and CPU topology mutations.

Important global structures include:

- `cpu_list`: circular list of all configured CPUs.
- `clock_cpu_list`: CPU list cursor used by clock code.
- `cpu_active`: circular list of online active CPUs.
- `cpu_active_set`: cached active CPU bitmap.
- `cpu_available`: configured CPU bitmap.
- `cpu_seq`: sequential CPU-id lookup table.
- `cpu_inmotion`: CPU currently being offlined or moved.
- `weakbindingbarrier`: global suppression flag for weak CPU bindings.
- `safe_list[]` and `cpu_pause_info`: cross-CPU quiesce/pause coordination.

The file repeatedly emphasizes a key invariant: some code walks CPU lists without `cpu_lock`, so list modifications are made while other CPUs are paused, and unlocked walkers must use preemption discipline and revalidation.

## CPU Affinity and Migration

`thread_affinity_set()` and `thread_affinity_clear()` implement counted hard CPU affinity. They support `CPU_CURRENT`, `CPU_BEST`, and explicit CPU IDs, update `t_bound_cpu`, and force migration or dispatch-queue movement through `force_thread_migrate()` when needed.

`thread_nomigrate()` and `thread_allowmigrate()` implement weak CPU affinity for short regions that must not migrate but should not fully disable preemption unless necessary. This is used for “no migration” semantics that are less disruptive than `kpreempt_disable()`.

Weak binding has careful interaction with CPU offline:

- `cpu_inmotion` marks an offline target so new weak bindings avoid that CPU.
- `weakbinding_stop()` forces future weak bindings to be satisfied by preemption disabling.
- Existing weak bindings are expected to drain quickly because callers must not block while weak-bound.
- Dispatcher behavior favors `t_weakbound_cpu` over strong binding while the weak binding exists.

## Pausing CPUs

The CPU pause subsystem creates high-priority per-CPU pause threads:

- `cpu_pause_alloc()` creates and binds a pause thread for a CPU.
- `cpu_pause_start()` schedules pause threads on all eligible CPUs except the caller/target.
- `pause_cpus()` waits until all selected CPUs reach a safe pause point, then raises interrupt priority on the current CPU.
- `start_cpus()` releases paused CPUs and restores the caller state.
- `cpu_pause_free()` safely kills a pause thread during CPU deletion.

The paused region is intentionally restrictive: code run while CPUs are paused must not acquire adaptive or low-level spin locks and must not block. This mechanism is fundamental to safe mutation of CPU global lists and hotplug state.

## CPU State Predicates

The file provides kernel-facing state tests that operate on `cpu_flags` while `cpu_lock` is held:

- `cpu_is_online()`
- `cpu_is_offline()`
- `cpu_is_poweredoff()`
- `cpu_is_nointr()`
- `cpu_is_active()`

The corresponding flag helpers are:

- `cpu_flagged_online()`
- `cpu_flagged_offline()`
- `cpu_flagged_poweredoff()`
- `cpu_flagged_nointr()`
- `cpu_flagged_active()`

User-visible processor states are derived separately by `cpu_flags_to_state()`, `cpu_get_state()`, and `cpu_get_state_str()`. The file explicitly separates internal `cpu_flags` semantics from `processor_info(2)` / `p_online(2)` states.

## Online, Offline, Fault, Spare, and Power Transitions

`cpu_online()` starts a CPU with `mp_cpu_start()`, inserts it into processor groups and active CPU lists while CPUs are paused, clears quiesced/offline/frozen/spare/fault/disabled flags, creates statistics and interrupt kstats, notifies CPU setup callbacks, enables interrupts, updates cyclic and callout subsystems, and pokes the CPU.

`cpu_offline()` is the most complex lifecycle transition. It:

- Rejects disabling the last online CPU in a partition or last interrupt-capable CPU.
- Unbinds soft or forced-bound user threads through `cpu_unbind()`.
- Notifies CPU state callbacks.
- Removes the CPU from processor groups.
- Disables interrupt participation through `cpu_intr_disable()`.
- Sets `cpu_inmotion` to discourage bindings and scheduling to the target CPU.
- Waits for bound threads to drain.
- Offlines callouts and cyclics.
- Calls `mp_cpu_stop()`.
- Pauses CPUs, removes the target from active lists, rehomes lgroup-affine threads, updates `t_cpu` for affected threads, marks `CPU_OFFLINE` and possibly `CPU_QUIESCED`, decrements `ncpus_online`, and tears down kstats.
- Rolls back interrupts, cyclics, callouts, processor group membership, and notifications if a later step fails.

`cpu_faulted()` and `cpu_spare()` layer on top of `cpu_offline()` or directly mark already-offline CPUs. `cpu_poweron()` and `cpu_poweroff()` delegate to machine-dependent power hooks and update visible state.

## CPU List and Hotplug Management

`cpu_list_init()` initializes the boot CPU’s circular lists, active set, partition membership, sequential ID, kmem cache offset, and CPU partition linkage.

`cpu_seq_tbl_init()` creates the dynamic sequential-ID table once memory allocation is available.

`cpu_add_unit()` adds a configured CPU to the all-CPU list and availability bitmap, assigns the first free sequential ID, initializes per-CPU cache offset, creates a pause thread, creates CPU info kstats, initializes machine-state accounting, and updates pool modification timestamps.

`cpu_del_unit()` removes an unconfigured CPU: it tears down processor-group and physical-ID state, destroys kstats and mstate accounting, frees the pause thread, removes availability and sequence mappings, pauses CPUs to unlink from `cpu_list`, marks the deleted CPU by nulling list pointers, decrements `ncpus`, and notifies lgroup/pool state.

`cpu_add_active_internal()` and `cpu_remove_active()` maintain the online active CPU list, per-partition circular list, active bitmap, processor-group state, lgroup state, partition CPU counts, and load-average state.

`cpu_configure()` and `cpu_unconfigure()` wrap machine-dependent CPU creation/destruction and invoke registered CPU setup hooks with rollback semantics.

## CPU Setup Callbacks

The file maintains a fixed-size `cpu_setups[]` callback table for early-boot feasibility. Callers register with `register_cpu_setup_func()` and unregister with `unregister_cpu_setup_func()`.

`cpu_state_change_notify()` broadcasts state changes without rollback. `cpu_state_change_hooks()` invokes callbacks and runs undo callbacks in reverse order if one fails.

Callbacks are called with `cpu_lock` held and must not block.

## CPU Kstats

The file exports CPU information and statistics through kstats:

- `cpu_info_kstat_create()` creates `cpu_info` named kstats.
- `cpu_info_kstat_update()` fills processor state, type, FPU type, MHz, chip/core IDs, implementation string, brand, current/supported frequencies, PG ID, SPARC FRU/device fields, and x86 vendor/family/model/cache/socket/C-state fields.
- `cpu_stats_kstat_create()` creates `cpu:<id>:sys`, `cpu:<id>:vm`, and raw `cpu_stat` kstats.
- `cpu_sys_stats_ks_update()` exports system counters and CPU mstate nanoseconds/ticks.
- `cpu_vm_stats_ks_update()` exports VM counters.
- `cpu_stat_ks_update()` exports legacy raw `cpu_stat_t` data.

The kstat update paths take care to avoid monotonic time counters moving backward by comparing current mstate values with previously exported values.

## Zone and Processor Set Visibility

When processor sets are enabled, CPU kstats are initially global-zone visible and then explicitly added to or removed from zones:

- `cpu_visibility_configure()`
- `cpu_visibility_online()`
- `cpu_visibility_add()`
- `cpu_visibility_offline()`
- `cpu_visibility_unconfigure()`
- `cpu_visibility_remove()`

These functions maintain `zone_ncpus`, `zone_ncpus_online`, and kstat zone visibility for `cpu_info`, `cpu_stat`, `cpu/sys`, `cpu/vm`, and `intrstat`.

## Processor Binding

`cpu_bind_thread()` implements per-thread processor binding semantics for `processor_bind(2)`-style operations. It supports query, query-type, soft/hard binding type changes, unbinding, explicit CPU binding, permission checks, partition checks, lgroup rehoming, dispatch queue movement, and `TP_CHANGEBIND` notification.

`cpu_unbind()` walks active processes under `pidlock` and unbinds threads bound to a target CPU, optionally skipping hard-bound threads unless forced.

`cpu_destroy_bound_threads()` removes remaining system-class bound threads for a CPU being destroyed, collecting them under `pidlock` and freeing them after dropping the lock.

## CPU Sets

The file implements allocation and operations for `cpuset_t`:

- Allocation/free: `cpuset_alloc()`, `cpuset_free()`.
- Initialization: `cpuset_all()`, `cpuset_all_but()`, `cpuset_only()`, `cpuset_zero()`.
- Membership: `cpu_in_set()`, `cpuset_add()`, `cpuset_del()`.
- Queries: `cpuset_isnull()`, `cpuset_isequal()`, `cpuset_find()`, `cpuset_bounds()`.
- Atomic mutation: `cpuset_atomic_add()`, `cpuset_atomic_del()`, `cpuset_atomic_xadd()`, `cpuset_atomic_xdel()`.
- Boolean operations: `cpuset_or()`, `cpuset_xor()`, `cpuset_and()`.

These are general kernel utilities but live here because CPU lifecycle state is a primary user.

## Frequency Reporting

`cpu_set_supp_freqs()` updates the string used by `cpu_info:supported_frequencies_Hz`. It allocates or replaces the per-CPU string and adjusts kstat data size under the kstat lock when the kstat already exists.

`cpu_set_curr_clock()` updates the current CPU frequency and fires the `cpu-change-speed` DTrace probe.

## Notable Dependencies

This file coordinates with many kernel subsystems:

- Dispatcher and thread migration.
- CPU partitions and processor sets.
- Locality groups.
- Processor groups and CMT topology.
- Cyclic subsystem and callouts.
- Interrupt routing.
- Kstats and zones.
- Power management through CPU state/frequency fields.
- Machine-dependent CPU bringup/offline/power hooks.

## Research Notes

This is a high-risk kernel coordination file. Changes must preserve lock ordering, pause-region restrictions, CPU lifecycle rollback, and dispatcher assumptions about active CPU lists. The CPU offline path is especially sensitive because it combines binding policy, interrupt routing, cyclic/callout state, lgroup rehoming, processor group state, and kstat visibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_event.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_event.c

## Role

`cpu_event.c` implements the illumos CPU idle event notification framework. It lets kernel clients register callbacks that run just before a CPU enters a hardware idle state and just after it exits that state.

The implementation is optimized for the idle hot path: callback dispatch and property reads avoid normal locks, while registration and removal use `pause_cpus()` / `start_cpus()` to safely replace shared callback arrays.

## Main Concepts

The file defines two related facilities:

- CPU idle callbacks: ordered `idle_enter` and `idle_exit` callback functions registered by priority.
- CPU idle properties: per-CPU cache-aligned property storage exposed to callbacks through handles.

Built-in properties include:

- idle state
- enter timestamp
- exit timestamp
- last idle time
- last busy time
- total idle time
- total busy time
- interrupt count

Built-in callbacks include:

- DTrace idle-state transition probes.
- x86 non-XPV TLB idle service hooks, where available.

## Locking Strategy

The header comment documents the concurrency model:

- `cpu_idle_prop_busy` and `cpu_idle_prop_free` are protected by `cpu_idle_prop_lock`.
- `cpu_idle_cb_busy` is protected by `cpu_idle_cb_lock`.
- Per-CPU `cpu_idle_cb_state` does not need global locking.
- `cpu_idle_cb_array`, `cpu_idle_cb_curr`, and `cpu_idle_cb_max` are protected for writers by pausing other CPUs.
- The idle enter/exit hot path reads callback arrays without taking locks.

This design makes callback registration relatively expensive but idle transitions cheap.

## Initialization

`cpu_event_init()` initializes callback and property locks, creates internal properties, allocates cache-aligned per-CPU callback state for `max_ncpus`, caches property-value pointers in each per-CPU state record, and registers built-in callbacks.

`cpu_event_init_cpu()` enables per-CPU callback state when a CPU starts. `cpu_event_fini_cpu()` disables and clears per-CPU idle callback state when a CPU stops.

A notable implementation detail: the per-CPU state has an `intr_cnt` pointer field, but the initialization macro assigns the interrupt-count property to `last_idle` a second time. The file otherwise retrieves interrupt counts through property handles and update callbacks, so this cached field appears unused in the current implementation.

## Callback Registration

`cpu_idle_register_callback()` validates call context and parameters, rejects duplicate non-dynamic priorities, allocates a `cpu_idle_cb_impl_t`, inserts it into the busy list, and calls `cpu_idle_insert_callback()`.

`cpu_idle_insert_callback()` may allocate a larger callback array, then acquires `cpu_lock` if needed, pauses other CPUs if not already paused, swaps/copies the callback array, inserts the new callback item in priority order, resumes CPUs, and frees the old array.

`cpu_idle_unregister_callback()` validates that it is not called from an active callback, removes the implementation from the busy list, calls `cpu_idle_remove_callback()`, and frees the implementation.

`cpu_idle_remove_callback()` pauses CPUs, compacts the callback array, decrements the current count, and clears per-CPU property readiness when the last callback is removed.

## Idle Enter and Exit Flow

`cpu_idle_enter()` is called before entering hardware idle state. It:

- Resolves the current CPU callback context from `cpu_seqid`.
- Handles disabled per-CPU state.
- On x86, disables interrupts before callback dispatch.
- Updates idle state, enter timestamp, last busy time, and total busy time.
- Skips callbacks the first time a CPU’s idle state becomes ready.
- Calls registered `idle_enter` callbacks in priority order.
- Tracks `sp->v.index` so that `idle_exit` can unwind callbacks in reverse order.
- Detects interrupts or early exits during an enter callback by observing index changes and returns `EBUSY`.

`cpu_idle_exit()` is called after leaving hardware idle state. It:

- Updates idle state back to normal, exit timestamp, last idle time, and total idle time.
- Calls registered `idle_exit` callbacks in reverse order for only the callbacks whose enter side ran.
- Clears `sp->v.index`.
- Handles SPARC and x86 interrupt-state differences separately.

On x86, `cpu_idle_exit()` supports calls from either idle thread or interrupt handler. Interrupt-handler calls assume interrupts are already disabled; idle-thread calls disable and restore interrupts around exit processing.

## Idle Properties

`cpu_idle_prop_allocate_impl()` allocates property implementation records in groups sized to cache-line property groups and allocates cache-aligned per-CPU value storage.

Property APIs include:

- `cpu_idle_prop_create_property()`
- `cpu_idle_prop_destroy_property()`
- `cpu_idle_prop_create_handle()`
- `cpu_idle_prop_destroy_handle()`
- `cpu_idle_prop_get_type()`
- `cpu_idle_prop_get_name()`
- `cpu_idle_prop_get_value()`
- typed getters for `uint32`, `uint64`, `intptr`, and `hrtime`
- `cpu_idle_prop_set_value()`
- `cpu_idle_prop_set_all()`

Properties are reference-counted. Destroy succeeds only when the property has a single reference. Allocated backing value buffers are intentionally not freed individually.

`cpu_idle_prop_update_intr_cnt()` computes current interrupt count by summing per-PIL interrupt statistics on the current CPU.

## CPU State and x86 Poweroff Intercept

`cpu_idle_get_cpu_state()` returns the cached idle state for a CPU through the internal idle-state property.

On x86, `cpu_idle_intercept_cpu()` sets a bit in `cpu_idle_intercept_set`, pokes the target CPU, and waits until the target clears its bit inside `cpu_idle_enter()` with interrupts disabled. The target CPU then spins forever at a safe point before poweroff.

## DTrace Integration

The built-in DTrace callback emits `idle-state-transition` probes on idle enter and exit. Enter reports the requested idle state; exit reports the normal state.

## Research Notes

This file is a low-latency event framework tightly coupled to CPU idle paths. The critical invariants are no sleeping or unsafe locking on idle enter/exit, safe callback-array replacement using paused CPUs, correct reverse-order unwinding, and correct interrupt-state handling across architectures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_intr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_intr.c

## Role

`cpu_intr.c` provides the architecture-independent CPU interrupt participation helpers. It determines whether CPUs are accepting I/O interrupts, finds alternate interrupt-capable CPUs, counts interrupt-capable CPUs, and wraps machine-dependent interrupt enable/disable operations.

## Functions

`cpu_intr_on()` returns whether a CPU has `CPU_ENABLE` set. It requires `cpu_lock`.

`cpu_intr_next()` walks the online CPU list from a given CPU and returns the next online CPU that accepts interrupts, or `NULL` if none is found.

`cpu_intr_count()` counts CPUs in the all-CPU circular list that currently accept I/O interrupts.

`cpu_intr_enable()` calls the machine-dependent `cpu_enable_intr()` if interrupts are currently disabled for the CPU, then updates user-visible CPU state through `cpu_set_state()`.

`cpu_intr_disable()` prevents taking the last interrupt-capable CPU out of service. If another interrupt-capable CPU exists, it first tries to juggle cyclics away from the target CPU with `cyclic_juggle()`, then calls machine-dependent `cpu_disable_intr()`. On success it updates CPU state.

## Integration

This file is used by CPU online/offline and `p_online(2)` state transitions. `cpu_offline()` depends on `cpu_intr_disable()` to move a CPU out of interrupt participation before quiescing or offlining it.

## Research Notes

The file is intentionally small, but it enforces an important system invariant: the kernel should not gracefully disable I/O interrupt participation on the last interrupt-capable CPU. Platform-specific interrupt routing remains in machine-dependent helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_intr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_pm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_pm.c

## Role

`cpu_pm.c` implements platform-independent event-based CPU power management. It manages active power domains, power-management policy, domain state enumeration, state transitions, and an elastic utilization governor that reacts to dispatcher-reported domain utilization changes.

It is the policy layer between CMT/processor-group utilization tracking and platform-specific CPU power-state operations.

## Policy Model

The global `cpupm_policy` starts as `CPUPM_POLICY_DISABLED`. Supported policy behavior includes:

- `CPUPM_POLICY_DISABLED`: disables active power-aware dispatch support and forces active power domains to maximum performance.
- `CPUPM_POLICY_ELASTIC`: enables active power-aware dispatch support and allows domains to shift between max performance and low power based on utilization.

`cpupm_get_policy()` returns the active policy. `cpupm_set_policy()` changes policy under `cpu_lock`, pausing CPUs while changing the global policy so other CPUs cannot race with CPUPM state transitions.

## Domains and States

Power domains are represented by `cpupm_domain_t` records linked from `cpupm_domains`.

`cpupm_domain_find()` searches for an existing domain by ID and type. `cpupm_domain_create()` allocates and links a new domain.

`cpupm_domain_state_enum()` asks the platform layer how many states exist for a domain, allocates state storage, and asks the platform layer to fill it.

`cpupm_domain_init()` creates or finds the domain for a CPU and domain type. For active domains, it names the first enumerated state as `CPUPM_STATE_MAX_PERF` and the last as `CPUPM_STATE_LOW_POWER`, then assumes the domain begins at max performance.

`cpupm_domain_id()` delegates domain-ID discovery to `cpupm_plat_domain_id()`.

`cpupm_change_state()` delegates to `cpupm_plat_change_state()`, fires a `cpupm-change-state` DTrace probe, and updates the domain’s current state on success.

## Elastic Utilization Governor

`cpupm_utilization_event()` is the main event-driven policy function. It consumes dispatcher/CMT events for active power domains:

- `CPUPM_DOM_REMAIN_BUSY`
- `CPUPM_DOM_BUSY_FROM_IDLE`
- `CPUPM_DOM_IDLE_FROM_BUSY`

The simple target policy is “race to idle”:

- Busy domains should run at max performance.
- Idle domains should run at low power.

The governor prevents rapid state thrashing from transient work or transient idle periods. It tracks:

- `cpupm_ti_predict_interval`: transient idle threshold.
- `cpupm_tw_predict_interval`: transient work threshold.
- `cpupm_mispredict_thresh`: count needed to engage a governor.
- `cpupm_mispredict_gov_thresh`: count needed to remove a governor.
- Per-domain transient counters `cpd_ti` and `cpd_tw`.
- Per-domain governor mode: disengaged, transient-work governed, or transient-idle governed.

Transient work can suppress raising power; transient idle can suppress lowering power. Non-transient periods eventually remove the relevant governor.

## Global State Changes

`cpupm_state_change_global()` iterates all hardware power groups of the requested type and applies a named state to every CPU in each domain. Currently only active power domains are supported.

When policy is disabled, `cpupm_set_policy()` disables active PAD support and globally returns active power domains to max performance.

## Dynamic Max Performance Redefinition

`cpupm_redefine_max_activepwr_state()` lets platform code redefine which enumerated state is considered `CPUPM_STATE_MAX_PERF`. If the domain is currently at the old max-performance state, it immediately changes to the new max-performance state. Out-of-range indices are clamped to the lowest supported speed when multiple states exist.

## Governor Initialization

`cpupm_governor_initialize()` converts nanosecond tuning intervals into unscaled hrtime units, matching the timestamps passed to `cpupm_utilization_event()`.

Default transient idle and transient work governor intervals are both 400 microseconds.

## Dependencies

This file depends on:

- CMT power-aware dispatch: `cmt_pad_enable()` and `cmt_pad_disable()`.
- Processor-group hardware sets: `pghw_set_lookup()`, group iteration, `PG_CPU_ITR`.
- Platform CPUPM hooks: `cpupm_plat_domain_id()`, `cpupm_plat_state_enumerate()`, `cpupm_plat_change_state()`.
- Global CPU synchronization: `cpu_lock`, `pause_cpus()`, `start_cpus()`.
- DTrace probes for state changes and governor decisions.

## Research Notes

The key risk in this file is policy/state transition synchronization. Domain state can be changed by dispatcher-driven utilization events, global policy changes, and platform max-performance redefinition, so callers must respect the documented CPU-locking and pause semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_pm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_uarray.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_uarray.c

## Role

`cpu_uarray.c` implements a small per-CPU unsigned 64-bit array helper. It allocates storage for `nr_items` counters per CPU, aligned to `CUA_ALIGN`, and provides summation helpers.

## Functions

`cpu_uarray_size()` computes the allocation size as:

- rounded-up per-CPU item storage for `nr_items` `uint64_t` values,
- multiplied by `NCPU`,
- plus the `cpu_uarray_t` header.

`cpu_uarray_zalloc()` zero-allocates the computed structure, verifies the value array alignment, and records the item count.

`cpu_uarray_free()` frees a previously allocated structure using the recorded item count.

`cpu_uarray_sum()` sums one item index across CPUs from `0` to `ncpus - 1`, using `UINT64_OVERFLOW_ADD()` to preserve overflow behavior.

`cpu_uarray_sum_all()` sums every item for every CPU, also using overflow-aware addition.

## Research Notes

This is a utility file for per-CPU counters. It allocates for `NCPU` capacity but sums over current `ncpus`, so users should understand whether deleted or sparse CPU IDs matter for their accounting model. Index validation is done with `VERIFY3U(index, <, cua->cu_nr_items)`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_uarray.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpupm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpupm.c

## Role

`cpupm.c` contains a compatibility/helper routine for formatting supported CPU frequencies for the `cpu_info` kstat field `supported_frequencies_Hz`.

It is distinct from `cpu_pm.c`: this file only prepares a colon-separated frequency string and passes it to `cpu_set_supp_freqs()`.

## Function

`cpupm_set_supp_freqs()` accepts a CPU, an array of speed percentages or platform speed values, and a count.

If `speeds` is `NULL`, it calls `cpu_set_supp_freqs(cp, NULL)`, causing the CPU layer to report only the current clock.

If speeds are provided, it:

- Allocates a `uint64_t` array of frequencies.
- Converts input speeds to Hz with `CPUPM_SPEED_HZ(cp->cpu_type_info.pi_clock, speeds[j])`.
- Reverses the input order into the Hz array.
- Builds a colon-separated string of unsigned 64-bit frequency values.
- Calls `cpu_set_supp_freqs()` to update the CPU kstat backing string.
- Frees temporary arrays.

## Research Notes

This file is a narrow bridge between CPU power-management speed data and the generic CPU kstat export path in `cpu.c`. The fixed maximum decimal width is based on the maximum `uint64_t` string length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpupm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cred.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cred.c

## Role

`cred.c` implements illumos kernel credential management. It owns allocation, reference counting, copying, mutation, user/group membership checks, process permission checks, privilege manipulation, audit-label export, zone-aware credentials, kernel credential setup, and ephemeral ID/SID support.

This file is security-sensitive: credentials flow into process identity, vnode permission checks, privilege policy, auditing, labeled security, remote peer identity, NFS behavior, and zone isolation.

## Initialization

`cred_init()` initializes privilege infrastructure, determines whether C2 audit support is loaded, sizes the credential allocation including optional audit storage, creates `cred_cache`, initializes `dummycr`, and creates `kcred`.

`kcred` is the all-powerful kernel credential template. It is associated with `zone0`, has a full limit set, basic inheritable/effective/permitted sets, adjustments for `rstchown` and `rstlink`, and `NET_MAC_AWARE`.

The function also assigns `kcred` to process 0 and the current thread, initializes `ucredsize`, and creates zone-specific storage for ephemeral identity state.

## Allocation and Reference Management

Core allocation and lifecycle functions include:

- `cralloc_flags()` and `cralloc()`: allocate nearly uninitialized credentials.
- `cralloc_ksid()`: allocate with SID storage when ephemeral IDs have been used.
- `crget()`: allocate an initialized credential from the current zone’s kernel credential.
- `crhold()`: increment `cr_ref`.
- `crfree()`: decrement `cr_ref` and release labels, klpd, zone holds, SID data, group data, and cache storage when it reaches zero.
- `crcopy()` and `crcopy_to()`: copy and replace a credential, dropping the old reference and returning a two-reference credential for process/thread use.
- `crdup()`, `crdup_flags()`, and `crdup_to()`: duplicate credentials without freeing the source.

Shared subobjects are held or released explicitly: zones, labels, SID records, kernel privilege daemons, and supplemental groups.

## Process and Thread Credential Updates

`crset()` broadcasts a new credential to a process. It directly updates the current thread’s `t_cred` and marks other LWPs in the same process with `t_pre_sys` so they adopt the process credential at their next syscall/trap boundary. This avoids changing another thread’s credential in the middle of a system call.

`crgetcred()` returns a held copy of the current process credential under `p_crlock`.

## Group and Permission Checks

`groupmember()` checks effective group first and then supplemental groups. `supgroupmember()` uses linear search for small group lists and binary search for larger sorted lists.

`hasprocperm()` implements process-credential permission checks for signal-like operations:

- same credential succeeds,
- cross-zone access requires global-zone/zone privilege,
- matching real/effective/saved user IDs succeeds,
- `PRIV_PROC_OWNER` succeeds.

`prochasprocperm()` is the preferred wrapper when process pointers are available. It succeeds for the same process, enforces session/basic process policy, safely obtains the target credential, and calls `hasprocperm()`.

`crcmp()` compares credentials for same-user equivalence, including IDs, zone, supplemental groups, and effective/permitted privilege equivalence.

`suser()` is the compatibility superuser check using `PRIV_SYS_SUSER_COMPAT`.

## Accessors and Mutators

The file provides many simple accessors:

- UID/GID: `crgetuid()`, `crgetruid()`, `crgetsuid()`, `crgetgid()`, `crgetrgid()`, `crgetsgid()`.
- Audit: `crgetauinfo()`, `crgetauinfo_modifiable()`.
- Zone/project: `crgetzoneid()`, `crgetprojid()`, `crgetzone()`.
- Label: `crgetlabel()`.
- Remote marker: `crisremote()`.
- Groups: `crgetgroups()`, `crgetngroups()`.
- Refcount: `crgetref()`.

Mutation helpers include:

- `crsetresuid()`
- `crsetresgid()`
- `crsetugid()`
- `crsetgroups()`
- `crsetprojid()`
- `crsetzone()`

Mutators assert the credential has at most the expected mutable references and validate IDs against the credential’s zone.

Supplemental groups are stored in `credgrp_t`, sorted on set/copyin, reference-counted with `crgrphold()` and `crgrprele()`, and can be installed with `crsetcredgrp()`.

## User Credential Export

`cred2prcred()` converts kernel credentials into `/proc` `prcred_t`.

`cred2ucaud()` exports audit information if the receiver has audit-getattr policy rights.

`cred2uclabel()` copies the credential label.

`cred2ucred()` builds a user-visible `ucred_s`:

- Records size, PID, project ID, and zone ID.
- For remote peer credentials, exports only the label when available.
- For normal credentials, includes `prcred`, privilege data, optional audit data, and optional label data.
- Supports caller-provided aligned buffers.

`ucredminsize()` computes the minimal required allocation, avoiding unused supplemental group slots and handling remote/labeled credentials.

`pgetucred()` obtains a held process credential and exports it as a `ucred_s`.

## Audit and Label Support

Audit storage is conditionally embedded after `cred_t` depending on `get_c2audit_load()`, which checks whether `c2audit` is excluded.

Trusted Extensions label helpers include:

- `newcred_from_bslabel()`
- `copycred_from_tslabel()`
- `copycred_from_bslabel()`

`crgetlabel()` returns a credential label when present or falls back to the zone label.

## Zone Kernel Credentials

`zone_kcred()` returns the kernel credential equivalent for the current zone when available, otherwise global `kcred`.

`crsetzone()` updates a credential’s zone pointer by holding the new zone before releasing the old zone, which is safe when old and new are identical.

## NFS Credential Adjustment

`crnetadjust()` supports an NFS retry case: if the effective UID is root but the real UID is non-root, it duplicates the credential and changes effective UID to the real UID so network access can be retried without root identity.

## Ephemeral IDs and SID Mapping

The file maintains per-zone ephemeral identity state in `ephemeral_zsd_t`, created lazily by `get_ephemeral_zsd()` and freed through the zone-specific-data destructor.

Per-zone state tracks:

- minimum and last ephemeral UID
- minimum and last ephemeral GID
- lock
- an `eph_nobody` credential used when SID-containing credentials must map to nobody

Functions include:

- `valid_ephemeral_uid()`
- `valid_ephemeral_gid()`
- `eph_uid_alloc()`
- `eph_gid_alloc()`
- `get_ephemeral_data()`
- `set_ephemeral_data()`

Allocation detects unsigned wraparound, supports state reset/corruption flags, sets global `hasephids`, and returns ranges.

`crgetmapped()` maps credentials with user or group SIDs above `MAXUID` to the zone’s `eph_nobody` credential. It also tolerates `NULL` credentials passed incorrectly to vnode operations.

SID manipulation APIs include:

- `crsetsid()`
- `crsetsidlist()`
- `crgetsid()`
- `crgetsidlist()`

## Privilege and KLPD Helpers

`crsetpriv()` is a kernel-server helper that resets privilege sets and adds named privileges to permitted/effective sets without performing security checks.

`crset_zone_privall()` expands a credential to all privileges allowed by its zone privilege set.

`crgetcrklpd()` and `crsetcrklpd()` get and set the credential’s kernel privilege daemon state with reference release on replacement.

## Research Notes

This file is central to illumos security semantics. The most important invariants are credential immutability while shared, correct reference handling for all embedded objects, zone-aware ID validation, sorted supplemental groups for binary search, safe process/thread credential replacement timing, and careful separation between local, remote-peer, labeled, audited, and SID-bearing credentials.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cred.c -->