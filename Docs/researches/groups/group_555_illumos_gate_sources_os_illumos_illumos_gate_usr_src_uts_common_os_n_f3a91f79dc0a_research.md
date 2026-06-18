# Group Research: group_555_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_n_f3a91f79dc0a

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/os/illumos/illumos-gate`  
Files researched: 9

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/netstack.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/netstack.c

## Purpose

`netstack.c` is the illumos kernel framework for per-zone networking stack instances. It creates, reference-counts, shuts down, and destroys `netstack_t` objects, and lets networking modules register per-stack lifecycle callbacks.

Read completely: 1,456 lines.

## Main Responsibilities

- Registers with the zones framework through `zone_key_create()` so netstacks are created, shut down, and destroyed with zones.
- Maintains the global list of active and closing `netstack_t` objects.
- Supports shared global-stack zones and exclusive-IP zones.
- Provides module registration and unregistration through `netstack_register()` and `netstack_unregister()`.
- Runs module create callbacks in module-ID order and shutdown/destroy callbacks in reverse order.
- Provides lookup and hold/release entry points for current, credential, zone ID, and stack ID callers.
- Defers final netstack destruction to `system_taskq` to avoid teardown reentrancy.
- Keeps shared-stack kstats visible in every zone that uses the global/shared stack.

## Key State

- `netstack_g_lock` protects `ns_reg` and the `netstack_head` linked list.
- `ns_reg[NS_MAX]` stores module create, shutdown, destroy callbacks and module registration flags.
- `netstack_head` is the global list of netstacks, including closing objects that may still have references.
- `netstack_shared_lock` protects `netstack_shared_zones` and `netstack_shared_kstats`.
- `netstack_reap_limiter` caps outstanding deferred reaps; `netstack_outstanding_reaps` defaults to 1024.

Each `netstack_t` also has `netstack_lock`, `netstack_cv`, `netstack_refcnt`, `netstack_numzones`, `netstack_flags`, per-module `nm_state_t` flags, and module-private pointers.

## Lifecycle

`netstack_init()` initializes locks, the reap limiter, marks the subsystem initialized, and registers zone callbacks.

`netstack_zone_create()` maps a zone to either an exclusive stack ID or `GLOBAL_NETSTACKID`, reuses the global stack for shared zones, or allocates a new `netstack_t`. For new stacks it initializes per-module condition variables, marks needed create callbacks, runs `apply_all_modules(..., netstack_apply_create)`, then clears `NSF_UNINIT` and `NSF_ZONE_CREATE`.

`netstack_zone_shutdown()` only runs module shutdown callbacks when the last zone using a stack is shutting down. Shared-stack zones that are not the last user return without shutdown.

`netstack_zone_destroy()` decrements `netstack_numzones`. When the last zone is gone, it marks `NSF_CLOSING` so future lookups skip the stack and releases the zone-owned reference.

`netstack_rele()` decrements `netstack_refcnt` and dispatches `netstack_reap()` once both references and zone users reach zero. `netstack_reap()` calls `netstack_stack_inactive()`, unlinks the stack from `netstack_head`, destroys per-module CVs and stack locks, frees memory, and releases the reap limiter.

## Module Callback State Machine

Per-module state uses flags such as `NSS_CREATE_NEEDED`, `NSS_CREATE_INPROGRESS`, `NSS_CREATE_COMPLETED`, plus corresponding shutdown and destroy states.

`netstack_register()` installs callbacks under `netstack_g_lock`, marks create-needed on existing non-closing stacks, then calls `apply_all_netstacks()` to create module state everywhere.

`netstack_unregister()` marks shutdown and destroy needed for already-created module instances, sets `NRF_DYING` to prevent new creates, applies shutdown and destroy, then clears callback pointers and completed state.

`netstack_apply_create()`, `netstack_apply_shutdown()`, and `netstack_apply_destroy()` all wait for in-progress work on the same stack/module, set an in-progress flag, drop the outer lock while invoking callbacks, then record completion and broadcast the module CV.

## Ordering and Concurrency

The design is careful about concurrent zone creation, module loading, and module unloading:

- `wait_for_zone_creator()` makes `netstack_register()` and `netstack_unregister()` wait for a zone-created stack to finish create callbacks, preserving module-ID order.
- `wait_for_nms_inprogress()` serializes create, shutdown, and destroy work per stack/module.
- `apply_all_netstacks()` restarts from `netstack_head` whenever the callback drops `netstack_g_lock`, avoiding stale traversal after arbitrary list changes.
- Shutdown and destroy are applied in reverse module-ID order because module teardown may depend on create order.

## Lookup and Iteration

`netstack_get_current()` returns a held active stack from `curproc->p_zone->zone_netstack`. `netstack_find_by_cred()`, `netstack_find_by_zoneid()`, `netstack_find_by_zoneid_nolock()`, and `netstack_find_by_stackid()` locate a stack and hold it only if it is neither `NSF_UNINIT` nor `NSF_CLOSING`.

`netstack_next_init()`, `netstack_next()`, and `netstack_next_fini()` implement a simple held-object iterator over active stacks, skipping uninitialized and closing entries.

## Kstats and Shared Zones

`kstat_create_netstack()` creates zone-scoped kstats. For `GLOBAL_NETSTACKID`, it creates the kstat in the global zone and records it in `netstack_shared_kstats` so `kstat_zone_add()` can expose it to all shared-stack zones.

`netstack_shared_zone_add()` and `netstack_shared_zone_remove()` maintain the list of zones using the global stack and add or remove all shared-stack kstats from those zones. `zoneid_to_netstackid()` maps shared-stack zone IDs back to `GLOBAL_ZONEID`.

## Notable Invariants

- Exclusive-IP netstacks are not reused across zone reboot; the code relies on zones receiving new zone IDs.
- `netstack_find*()` callers must release returned stacks with `netstack_rele()`.
- Module create callbacks must return non-NULL module state.
- Final freeing is asynchronous because module data may have reentrant reference patterns.
- Shared-stack zone/kstat lists are maintained separately from the netstack list.

## Research Relevance

For filesystem and storage research, this file is mostly ambient OS infrastructure. It matters for zone-aware kernel services, kstat visibility, and networking-related storage protocols because it defines how per-zone network state outlives zones while references drain.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/netstack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/nvpair_alloc_system.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/nvpair_alloc_system.c

## Purpose

`nvpair_alloc_system.c` defines the default kernel memory allocators used by the nvpair/nvlist subsystem.

Read completely: 62 lines.

## Main Responsibilities

- Implements `nv_alloc_sys()` as a thin wrapper around `kmem_alloc()`.
- Implements `nv_free_sys()` as a thin wrapper around `kmem_free()`.
- Defines `system_ops`, an `nv_alloc_ops_t` table using those allocation functions.
- Exports `nv_alloc_sleep` and `nv_alloc_nosleep` defaults backed by `KM_SLEEP` and `KM_NOSLEEP`.

## Key Interfaces

`nv_alloc_sleep_def` stores `KM_SLEEP` in `nva_arg`; `nv_alloc_sys()` casts that argument back to the allocation flag passed to `kmem_alloc()`.

`nv_alloc_nosleep_def` does the same for `KM_NOSLEEP`.

The public pointers `nv_alloc_sleep` and `nv_alloc_nosleep` point at those defaults for kernel nvlist users.

## Notable Invariants

- The allocator operation table has no init, fini, or reset hooks.
- The free routine ignores `nva` and relies on the caller-provided size.
- Allocation behavior is entirely controlled by the `nva_arg` flag.

## Research Relevance

This file is small but important for fault-management and configuration paths that use nvlists in the kernel. In this group, `pcifm.c` uses nvlist-backed ereports; this allocator is the default backing mechanism for such structured kernel data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/nvpair_alloc_system.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/panic.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/panic.c

## Purpose

`panic.c` implements the architecture-independent panic path. It records panic state, stops other CPUs, prints diagnostic information, optionally enters the debugger, switches storage I/O to polled mode, takes a crash dump, and reboots or halts.

Read completely: 415 lines.

## Panic Model

The opening design comment describes irreversible panic phases: calm, quiesce, sync, and dump. The implementation in this file centers on the quiesce and dump triggers:

- `panic_quiesce`: transition from normal execution into panic quiesce.
- `panic_dump`: transition into dump generation.

The low-level `vpanic()` assembly wrapper records machine registers, switches to `panic_stack` for the first panicking thread, and calls `panicsys()`.

## Key Global State

The first panicking thread records:

- `panic_stack`, reserved for the first panic path.
- `panic_thread`, `panic_cpu`, `panic_regs`, `panic_pcb`, and `panic_reg`.
- `panicstr` and `panicargs`.
- time snapshots: `panic_lbolt`, `panic_lbolt64`, `panic_hrtime`, `panic_hrestime`.
- thread state snapshots: IPL, scheduling flags, bound CPU, preemption count.
- `panic_dip`, used for `dev_err(..., CE_PANIC, ...)`.

Runtime controls include `panic_bootstr`, `panic_bootfcn`, `halt_on_panic`, `nopanicdebug`, `in_sync`, `do_polled_io`, and `panic_forced`.

## `panicsys()` Flow

`panicsys()` raises IPL with `spl8()`, marks the current thread `T_PANIC`, prevents swapping, binds it to the current CPU, increments preemption, and invokes `panic_enter_hw()`.

If the thread is on an interrupt stack and an interrupt thread is available, it preserves the active interrupt stack by swapping in an interrupt-thread stack.

On the first panic-stack entry, it initializes `panicbuf`, records a dump UUID, saves trap or register state, formats the panic message, stops other CPUs with `panic_stopcpus()`, and only then sets `panicstr`. This ordering preserves remote CPU lock-spin state before panic-aware lock bypassing begins.

It then records all one-time panic globals, lowers IPL to clock level, runs hardware quiesce, stops ftrace, executes panic callbacks, flushes kernel log queues, prints the fault-management banner, prints the panic message and optional device prefix, shows trap/register data, and may enter the debugger.

For reentrant panic callers after the first panic, it prints the additional panic message if dump or `panicstr` is already set; otherwise it spins.

## Dump and Reboot

When `panic_trigger(&panic_dump)` succeeds, the code runs `panic_dump_hw()`, lowers IPL to clock level, drains error queues with `errorq_panic()`, sets `do_polled_io = 1`, and calls `dumpsys()`.

If dump was already triggered, it either enters the debugger again or warns that the dump was aborted.

Finally it calls `mdboot()` to halt or reboot according to `halt_on_panic`, `panic_bootfcn`, and `panic_bootstr`. Threads that cannot proceed spin forever with IPL capped at clock level so debugger entry remains possible.

## Platform Dependencies

The file expects machine-dependent support for:

- `panic_savetrap()`
- `panic_saveregs()`
- `panic_stopcpus()`
- `panic_quiesce_hw()`
- `panic_showtrap()`
- `panic_dump_hw()`
- `panic_enter_hw()`

## Notable Invariants

- `panicstr` is intentionally set only after other CPUs are stopped.
- Panic code must be reentrant because debugger sync callbacks and watchdog timeouts can call panic again.
- The first panicking thread owns the reserved panic stack and panic buffer.
- Dump I/O is forced into polled mode before `dumpsys()`.

## Research Relevance

This file is directly relevant to filesystem research because panic handling decides whether the kernel attempts filesystem sync and crash dumps, and because storage drivers must tolerate the polled-I/O panic environment.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/panic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pcifm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pcifm.c

## Purpose

`pcifm.c` implements PCI and PCI-X fault-management support for non-PCIe systems. It gathers PCI error registers, posts ereports, dispatches error callbacks, clears error status, and asynchronously maps target physical addresses back to affected device nodes.

Read completely: 1,506 lines.

## Main Responsibilities

- Defines PCI, PCI bridge, PCI-X, and PCI-X secondary error-class tables.
- Sets up and tears down per-device `pci_erpt_t` state in the device fault-management handle.
- Reads standard PCI status/command, bridge status/control, PCI-X status, and PCI-X ECC registers.
- Converts register bits into fault-management ereports with severity tracking.
- Handles expected, unexpected, and poke error paths.
- Dispatches child fault handlers below PCI bridges.
- Queues target-device ereports from captured physical addresses.
- Provides panic-safe device tree walking and ereport posting.

## Register Gathering and Clearing

`pci_config_check()` checks access-handle fault state after config-space reads, optionally posts a nonrecoverable ereport, and clears access errors.

`pci_regs_gather()` reads generic PCI status and command registers, and for bridges reads secondary status and bridge control. If the device has PCI-X capability, it delegates to `pcix_regs_gather()`.

`pcix_regs_gather()` handles leaf versus bridge PCI-X layouts. PCI-X bridge ECC state may have two ECC register banks; leaf devices have one. `pcix_ecc_regs_gather()` reads ECC status, first address, second address, and attributes.

`pci_regs_clear()` and `pcix_regs_clear()` write saved status values back to clear error bits and reset validity flags.

## Setup and Teardown

`pci_ereport_setup()` validates that the device supports ereports or error callbacks, allocates `pci_erpt_t`, sets up PCI config access, detects bridge headers, records BDF from the `reg` property, detects PCI-X capability, gathers and clears any preexisting errors, then stores the result in `devi_fmhdl->fh_bus_specific`.

`pcix_ereport_setup()` allocates PCI-X leaf or bridge register structures and optional ECC register storage based on PCI-X version.

`pci_ereport_teardown()` frees PCI-X structures, tears down config access, frees bridge register state, and clears `fh_bus_specific`.

## Error Classification

`pci_error_report()` posts generic PCI errors for unexpected faults, delegates PCI-X handling, delegates bridge handling, and uses bus-specific address or BDF data to locate affected access or DMA handles.

`pci_bdg_error_report()` posts bridge secondary-status errors, handles discard timer status, treats cautious get/put and poke cases specially, and dispatches errors to children through `ndi_fm_handler_dispatch()`.

`pcix_error_report()` and `pcix_bdg_error_report()` post PCI-X status and secondary-status ereports.

`pcix_ecc_error_report()` classifies ECC phase and correctability, posts ECC address/attribute/data and secondary CE/UE ereports, and uses `pcix_check_addr()` to populate fault-management bus-specific address or BDF data.

Severity is tracked with local `fatal`, `nonfatal`, `unknown`, and `ok` counters via `PCI_FM_SEV_INC()`.

## Public Posting Path

`pci_ereport_post()` is the main entry point. It is a no-op on PCIe systems because PCIe fault handling is delegated to the PCIe misc module. Otherwise it normalizes older `ddi_fm_error_t` formats, creates a PCI bus-specific payload when needed, ensures an ENA exists, gathers registers, reports errors, clears registers, and updates the caller's status and ENA.

## Target Error Queue

`pci_targetq_init()` creates `pci_target_queue`, a vital error queue drained by `pci_target_drain()`.

`pci_target_enqueue()` packages ENA, class, bridge type, and physical address into `pci_target_err_t` and dispatches it asynchronously.

`pci_target_drain()` walks from the root to find a top-level PCI/PCIe nexus whose `ranges` property contains the physical address, translates it to PCI address space, then walks children to find a matching `reg` or `assigned-addresses` entry and posts a target-device ereport.

`pci_fm_walk_devs()` is a private panic-safe device-tree walker that avoids normal sleeping and locking. `pci_fm_ereport_post()` uses errorq nvlist storage in panic context and normal nvlist posting otherwise.

## Address Mapping Helpers

`pci_check_ranges()` handles top-level PCI nexus `ranges` translation, including config-space bus-range checks and a SPARC `pci_fix_ranges()` compatibility adjustment for psycho-class host bridges.

`pci_check_regs()` matches translated PCI addresses against child `reg` and `assigned-addresses` properties, recording the target `dev_info_t`.

## Notable Invariants

- PCIe systems are skipped based on bus private data.
- Register validity flags prevent clearing or reporting stale/unreadable state.
- Panic paths avoid sleeping locks and use reserved errorq storage.
- Target address mapping assumes PCI-PCI bridges are transparent.
- PCI-X ECC handling has separate bridge and leaf layouts.

## Research Relevance

This file is relevant to storage and filesystem reliability because PCI fault handling underlies HBA, NVMe, NIC, and storage controller error diagnosis. It also shows how illumos maps bus-level faults back to device-tree nodes and driver-owned handles.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pcifm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pg.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pg.c

## Purpose

`pg.c` implements the generic processor group framework. Processor groups model logical or physical relationships among CPUs and provide class-specific hooks for scheduler topology, CPU lifecycle, CPU partition movement, and dispatcher thread-switch events.

Read completely: 828 lines.

## Main Responsibilities

- Registers processor group classes.
- Allocates and destroys generic `pg_t` objects with sequential PG IDs.
- Maintains CPU membership in PGs and PG membership in per-CPU `cpu_pg_t` data.
- Initializes and tears down per-CPU processor group state.
- Broadcasts CPU active/inactive and CPU partition callbacks to all classes.
- Provides default allocation, free, and callback operations.
- Invokes per-PG dispatcher callbacks on thread switch and thread remain events.

## Class Model

`pg_class_register()` appends a `pg_class_t` to the global class array under `cpu_lock`. Each class has a name, ID, operations table, and relation type such as `PGR_LOGICAL` or physical relations used by CMT.

Default operations are `pg_alloc_default()`, `pg_free_default()`, and null event callbacks. Class-specific callbacks may override allocation, CPU init/fini, active/inactive, CPU partition in/out/move, membership testing, and policy naming.

`pg_init()` registers the default class, initializes the CMT class through `pg_cmt_class_init()`, initializes CPU0, and starts CMT CPU startup for the boot CPU.

## PG Creation and Membership

`pg_create()` allocates a PG through the class allocator, assigns class and relation fields, finds the next free sequential PG ID using `pg_id_set`, creates the PG CPU group, and installs default event callbacks.

`pg_destroy()` destroys the CPU group, releases the PG ID, updates `pg_id_next`, and frees the PG through the class free operation.

`pg_cpu_add()` adds a CPU to the PG's CPU group and adds the PG to the CPU's pending `cpu_pg_t` group. `pg_cpu_delete()` removes both links. Both require `cpu_lock` and assert that the CPU is still using bootstrap PG data because the routines may block.

`pg_cpu_find_pg()`, `pg_cpu_next()`, and `pg_cpu_find()` provide class membership and iteration helpers.

## Per-CPU PG Data

`pg_cpu_data_alloc()` creates `cpu_pg_t` and initializes `pgs` and `cmt_pgs` groups. `pg_cpu_data_free()` destroys those groups and frees the object.

`pg_cpu_init()` allocates CPU PG data and calls every class `cpu_init` callback. Unless deferred, it installs the new data into `cp->cpu_pg`.

`pg_cpu_fini()` switches the CPU back to bootstrap data if needed, calls every class `cpu_fini`, and frees the old data.

`pg_cpu_bootstrap()` points a CPU at the static `bootstrap_pg_data`; `pg_cpu_is_bootstrapped()` tests that state. This protects code that may see a partially initialized CPU.

## CPU and Partition Events

All event entry points require `cpu_lock`:

- `pg_cpu_active()` and `pg_cpu_inactive()` notify classes when CPUs come online or go offline. They may not block because they are called from paused CPU context.
- `pg_cpupart_in()` and `pg_cpupart_out()` notify classes before CPU partition entry or exit and may block.
- `pg_cpupart_move()` notifies classes during a CPU partition move and may not block.
- `pg_cpu0_reinit()` tears down and rebuilds CPU0 PG data after topology changes.

## Dispatcher Event Callbacks

`pg_ev_thread_swtch()` iterates all PGs for the CPU and calls each PG's `thread_swtch` callback with timestamp, old thread, and new thread.

`pg_ev_thread_remain()` calls each PG's `thread_remain` callback when a thread switches to itself after a timeslice artifact.

## Notable Invariants

- Most structural mutations require `cpu_lock`.
- Active/inactive and partition move callbacks must not block.
- CPU PG data construction uses bootstrap indirection to survive blocking allocations and dispatcher entry.
- PG class-specific views are expected to embed `pg_t` first.

## Research Relevance

This file matters for scheduler and CPU-topology context around filesystem workloads. It does not implement filesystem behavior, but it defines the CPU grouping callbacks used by load balancing, CMT locality, and hardware-sharing policy.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pghw.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pghw.c

## Purpose

`pghw.c` implements the hardware-sharing layer for processor groups. It extends generic `pg_t` objects into `pghw_t` objects that represent shared hardware resources such as sockets, caches, integer pipelines, FPUs, memory links, and CPU power domains.

Read completely: 749 lines.

## Main Responsibilities

- Organizes hardware PGs into per-hardware-type sets.
- Initializes and finalizes `pghw_t` metadata and power-management handles.
- Finds hardware PGs by CPU, hardware type, or platform instance ID.
- Manages per-CPU physical ID cache memory.
- Exports processor group topology and capacity/utilization data through kstats.
- Maintains CPU-list strings and generation counters for kstat snapshots.

## Hardware Set Model

`pg_hw` is a top-level `group_t` indexed by `pghw_type_t`. Each slot points to a hardware set containing all `pghw_t` instances of that sharing type.

`pghw_set_create()` creates `pg_hw` on first use, expands it to `PGHW_NUM_COMPONENTS`, creates a new type-specific group, and inserts it at the hardware type index.

`pghw_set_lookup()` returns the group for a hardware type, while `pghw_set_add()` and `pghw_set_remove()` maintain PG membership in that set.

## PG Initialization and Lookup

`pghw_init()` creates the hardware set if needed, adds the PG to it, records the hardware type, generation, and platform instance ID from `pg_plat_hw_instance_id()`, creates kstats, and initializes CPU power-management domains for active or idle power PGs.

`pghw_fini()` tears down CMT-specific PG state, removes the PG from its hardware set, invalidates instance and hardware type fields, and deletes the generic hardware kstat.

`pghw_cmt_fini()` frees the cached CPU-list string and deletes the capacity/utilization kstat.

Lookup helpers include `pghw_place_cpu()`, `pghw_find_pg()`, and `pghw_find_by_instance()`.

## Physical ID Cache

`pghw_physid_create()` allocates `cpu_physid_t` for a CPU and initializes every ID field to the CPU ID. Platform code can later overwrite relationship-specific IDs.

`pghw_physid_destroy()` frees the cache.

## Kstats

`pghw_kstat_create()` creates two virtual kstats:

- `pg:<pg_id>:pg`, exposing PG ID, class, CPU count, instance ID, hardware relationship string, and policy string.
- `pg_hw_perf:<pg_id>:<relationship>`, exposing parent PG ID, CPU list, generation, hardware relationship, utilization counters, running/stopped time, current rate, and maximum rate.

`pghw_kstat_update()` fills the basic topology fields and rejects writes with `EACCES`.

`pghw_cu_kstat_update()` checks `secpolicy_cpc_cpu()` before exposing utilization data, updates CPU-list strings and hardware utilization under a nonblocking `mutex_tryenter(&cpu_lock)`, and zeroes utilization data for callers lacking CPC privilege.

`pghw_cpulist_alloc()` allocates or invalidates the cached CPU-list string based on CPU count and `pghw_generation`.

`pghw_parent_id()` returns the parent CMT PG ID when the PG belongs to the `cmt` class, otherwise -1.

## Hardware Type Names

`pghw_type_string()` maps hardware types to user-readable names such as `Integer Pipeline`, `Cache`, `Floating Point Unit`, `Socket`, `Memory`, and CPU power-domain names.

## Notable Invariants

- `pghw_t` embeds `pg_t` as its first field so generic PG pointers can be cast safely.
- Hardware sets are created dynamically but not destroyed.
- CU kstat update must not block on `cpu_lock` because kstat deletion can occur while `cpu_lock` is held.
- Hardware utilization visibility is privilege-gated by `PRIV_CPC_CPU`.

## Research Relevance

This file provides CPU topology observability that can explain filesystem and storage benchmark behavior on NUMA or CMT systems. It is also an example of privilege-gated kernel kstats.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pghw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pgrp.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pgrp.c

## Purpose

`pgrp.c` implements process group membership, process-group signaling, and orphaned process group detection for job control.

Read completely: 258 lines.

## Main Responsibilities

- Adds and removes processes from process group lists.
- Sends signals to all members of a process group.
- Tracks whether a process group is orphaned.
- Detects when exiting parents orphan child process groups.
- Sends SIGHUP and SIGCONT to stopped orphaned groups as required by job-control semantics.
- Tests whether a process group has members other than its leader.

## Process Group Lists

Each process group is represented by a `struct pid` whose `pid_pglink` points to the head process and `pid_pgtail` to the tail. Each process uses `p_pglink` and `p_ppglink` for next and previous links, plus `p_pgidp` for the group ID object.

All structural operations assert or acquire `pidlock`.

## Membership and Orphan Tracking

`pglinked()` returns true when a process has a parent in the same session but outside the process group. Such a parent prevents the group from being orphaned.

`pgjoin()` inserts linked processes at the head and unlinked processes at the tail. On first membership it holds the process-group PID object with `PID_HOLD()` and initializes `pid_pgorphaned`. If an orphaned group gains a linked process, it clears the orphaned flag.

`pgexit()` unlinks a process from its group, releases the PID object when the group becomes empty, and recomputes orphaned state if a formerly non-orphaned group may have lost its last external parent link.

`pgdetach()` handles a parent process exiting. It walks children, checks whether each child's group becomes orphaned, and if the group is stopped sends SIGHUP followed by SIGCONT.

## Signaling Helpers

`pgsignal()` acquires `pidlock` and calls `sigtoproc()` for every group member under each process lock.

`sigtopg()` performs the same loop but requires the caller to already hold `pidlock`.

`pgmembers()` returns true if a process group contains a process whose PID differs from the group ID, meaning the group has members beyond its leader.

## Notable Invariants

- `pidlock` protects process group list structure.
- Process locks are acquired while walking group membership to deliver signals.
- Nonempty process groups hold their `struct pid`; empty groups release it.
- Orphan transitions can produce SIGHUP/SIGCONT only when stopped members are present.

## Research Relevance

This file is general process-control infrastructure. It is relevant to filesystem research primarily through signal and session semantics that affect shell-driven jobs, daemons, and processes blocked in filesystem operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pid.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pid.c

## Purpose

`pid.c` implements PID allocation, PID hash lookup, `/proc` slot management, persistent process locks, process lookup with zone visibility, `/proc` synchronization locks, driver process references, process signaling, and per-UID per-zone process counts.

Read completely: 826 lines.

## Main Responsibilities

- Initializes global PID and `/proc` directory state.
- Allocates and frees `struct pid` objects and `/proc` slots.
- Maintains `pidlock`, `pidlinklock`, `pr_pidlock`, per-process persistent locks, and per-slot condition variables.
- Finds processes and process groups subject to zone restrictions.
- Coordinates `/proc` users with process lifetime through `P_PR_LOCK`.
- Provides DDI process references for drivers.
- Maintains process counts by UID and zone.

## PID and `/proc` State

`pid0` is the static PID object for sched/proc0. `pidhash` stores active PID objects, with `pid_hashsz` sized from `v.v_proc / pid_hashlen`.

`procdir` is an array of `union procent` entries used as `/proc` slots. Free entries link through `procentfree`; allocated entries point at `proc_t`.

`proc_lock` is a persistent array of process locks. `pid_getlockslot()` maps proc slots to lock slots with a stride intended to reduce cache-line false sharing while preserving one-to-one slot mapping.

## Allocation and Exit

`pid_init()` allocates hash buckets, `procdir`, per-slot CVs, and persistent process locks; initializes sched as process 0; builds the free `/proc` slot list; inserts `pid0`; and initializes UID process count hashing.

`pid_setmin()` sets PID allocation lower bounds, honoring `jump_pid`.

`pid_allocate()` allocates a `struct pid`, optionally reserves a `/proc` slot, either installs an explicit early PID or loops through `mpid` to find a free PID, hashes the PID object, and wires `p_pidp` and `p_lockp` into the process when `PID_ALLOC_PROC` is requested.

`proc_entry_free()` marks a PID inactive for `/proc` and returns the slot to `procentfree`.

`pid_exit()` removes a process from its process group, releases its session, frees its `/proc` slot, removes it from the active process list, releases the PID, destroys credential lock state, frees the process cache object, decrements global process count, and decrements task/project/zone process counts.

`pid_rele()` unlinks a non-`pid0` PID from the hash table and frees it.

## Lookup and Zone Semantics

`prfind_zone()` finds a live process by PID under `pidlock`, returning it only if the target zone is visible or `ALL_ZONES` is requested.

`prfind()` applies global-zone versus current-zone visibility automatically.

`pgfind_zone()` and `pgfind()` do the same for process-group heads via `pid_pglink`.

`pid_entry()` returns a process for a `/proc` slot when the slot is active and the process is not still `SIDL`.

## `/proc` Synchronization

`sprtrylock_proc()` sets `P_PR_LOCK` on a fully created, non-system, non-exiting process. It returns invalid-state, already-locked, or success status.

`sprlock_zone()` repeatedly looks up a process, takes its `p_lock`, and sets `P_PR_LOCK`, waiting on the per-slot CV if another `/proc` user owns it. In panic context, it returns with just `p_lock`.

`sprwaitlock_proc()` waits for `P_PR_LOCK` to clear and returns with the lock dropped because the process pointer may no longer be valid.

`sprlock_proc()` applies the same lock protocol to an already locked process.

`sprunlock()` clears `P_PR_LOCK`, signals waiters, and drops `p_lock`. If the process received SIGKILL while locked, it restarts stopped LWPs with `TS_XSTART | TS_PSTART` so SIGKILL can be observed.

## Signaling and Driver References

`signal()` sends a signal to every process in a process group.

`prsignal()` sends to the process referenced by a `struct pid` if the `/proc` slot is still active.

`proc_ref()` holds the current process PID for driver use. `proc_unref()` releases it. `proc_signal()` sends a signal through a held PID reference and reports whether the process has gone inactive.

## UID/Zone Process Counts

`upcount_init()` sizes a hash table based on physical memory.

`upcount_inc()` increments the process count for a `(uid, zoneid)` pair, allocating a new entry if necessary. It may drop and reacquire `pidlock` for sleeping allocation, then restarts the lookup.

`upcount_dec()` decrements and frees zero-count entries, panicking if the pair is missing.

`upcount_get()` returns the current count or zero.

## Notable Invariants

- `pidlock` is the global process lock for process list and process lookup callers.
- `pidlinklock` protects PID hash and `/proc` free-slot state.
- PID objects can outlive processes via references, but `pid_prinactive` marks the `/proc` slot inactive.
- Persistent locks avoid dereferencing freed process memory after waits.
- Zone-aware lookup prevents non-global zones from seeing other zones' processes.

## Research Relevance

This file is important for any filesystem code that walks processes, signals owners, uses `/proc`, dumps process state, or coordinates with zones. It also shows panic-sensitive locking behavior used by `dumpsys()`-adjacent walkers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/policy.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/policy.c

## Purpose

`policy.c` contains the main illumos kernel privilege and security-policy checks. It maps kernel operations to privileges, handles auditing and privilege-debug reporting, supports external policy overrides, and implements policy wrappers for filesystems, vnodes, IPC, processes, devices, networking, zones, contracts, and storage-adjacent subsystems.

Read completely: 2,671 lines.

## Main Responsibilities

- Implements bottom-level privilege checks through `priv_policy*()` helpers.
- Emits audit records and privilege-debug messages for failed or successful privileged operations.
- Supports external policy through KLPD and PFEXEC privilege override paths.
- Encodes special root and zone escalation rules.
- Defines filesystem mount, unmount, quota, vnode access, setattr, setid, chown, and extended-attribute policies.
- Defines policy checks for IPC, auditing, process control, resource control, device access, module control, networking, contracts, graphics, ZFS, SMB, vscan, xVM, and PPP.

## Privilege Core

The file defines helper macros over credential privilege sets:

- `HAS_ALLPRIVS()`
- `ZONEPRIVS()`
- `HAS_ALLZONEPRIVS()`
- `HAS_PRIVILEGE()`
- `FAST_BASIC_CHECK()`

The comments distinguish three policy patterns: requiring one privilege, requiring one privilege plus all zone privileges, and requiring all privileges globally.

`priv_policy_ap()` is the core check. It grants access if the credential has the requested privilege and required zone privileges, or if external policy approves. On success it may mark accounting `ASU` and audit success. On failure it audits and reports missing privilege information when appropriate.

`priv_policy()`, `priv_policy_va()`, `priv_policy_choice()`, and `priv_policy_only()` provide error-returning, varargs, boolean/auditing, and boolean/non-auditing variants.

`secpolicy_require_set()` checks an arbitrary privilege set, handles PFEXEC/KLPD overrides, audits missing sets, and reports either the single missing privilege or `PRIV_MULTIPLE`.

`priv_policy_global()` requires global-zone execution regardless of privilege.

## Debugging, Auditing, and Overrides

`priv_policy_errmsg()` records missing privilege details in `lwp_badpriv` and optional `t_pdmsg`, and can log kernel notes under `priv_debug`. It tries to identify the first useful caller outside common policy wrappers.

`priv_policy_override()` calls KLPD for a single requested privilege or zone/all-privilege set when `PRIV_XPOLICY` is set.

`priv_policy_override_set()` supports PFEXEC checks with `check_user_privs()` and KLPD set checks.

`priv_policy_err()` emits audit failure and DTrace probes, then optionally calls `priv_policy_errmsg()`.

## Filesystem Mount Policy

`secpolicy_fs_common()` is the central mount ownership check. It handles pure privilege checks, zone restrictions for existing mounts, overlay-mount escalation checks, mount-point ownership and write access, and the all-zone privilege requirement for sensitive cases.

`secpolicy_fs_mount()` handles remount mount-point selection and invokes `secpolicy_fs_mount_clearopts()` when mount options must be restricted.

`secpolicy_fs_mount_clearopts()` enforces `nosuid`, `nodevices`, and `restrict` behavior depending on zone and privilege state.

`secpolicy_fs_allowed_mount()` lets non-global zones mount only filesystem types marked `VSW_ZMOUNT` or listed in `zone_fs_allowed`.

`secpolicy_fs_unmount()`, `secpolicy_fs_quota()`, `secpolicy_fs_minfree()`, and `secpolicy_fs_config()` reuse mount ownership policy.

`secpolicy_fs_linkdir()` blocks directory hard-link/unlink by default unless `priv_allow_linkdir` is set.

## Vnode and Attribute Policy

`secpolicy_vnode_access()` and `secpolicy_vnode_access2()` map denied read, write, execute, and directory search access to DAC and basic file privileges. Writes to root-owned objects can require all zone privileges.

`secpolicy_vnode_any_access()` is a ZFS-oriented non-auditing probe that checks whether any effective privilege would allow file access.

Setid and ownership helpers include `secpolicy_vnode_setid_modify()`, `secpolicy_vnode_setid_retain()`, `secpolicy_vnode_setids_setgids()`, `secpolicy_vnode_chown()`, `secpolicy_vnode_create_gid()`, `secpolicy_vnode_setdac()`, `secpolicy_vnode_setdac3()`, `secpolicy_vnode_stky_modify()`, `secpolicy_vnode_remove()`, `secpolicy_vnode_owner()`, `secpolicy_setid_clear()`, and `secpolicy_setid_setsticky_clear()`.

`secpolicy_xvattr()` checks optional attributes. DOS-style bits require ownership; immutable, nounlink, append-only, nodump, antivirus quarantine/modified/scanfstamp require file flag privileges or all privileges for clearing; opaque is rejected; some AV attributes are valid only on regular files.

`secpolicy_vnode_setattr()` is the main setattr policy helper. It handles size changes, mode changes, setid/sticky clearing, chown/chgrp rules, timestamp updates, ACL-check skipping, owner implicit rights, and extended attributes.

`secpolicy_pcfs_modify_bootpartition()` requires all privileges to modify a pcfs boot partition.

## IPC, Audit, and Process Policy

System V IPC policy includes `secpolicy_ipc_owner()`, `secpolicy_ipc_config()`, `secpolicy_ipc_access()`, and `secpolicy_rsm_access()`, with root-owned IPC write cases requiring all zone privileges.

Audit policy includes `secpolicy_audit_config()`, `secpolicy_audit_modify()`, and `secpolicy_audit_getattr()`.

Process and resource policy includes `secpolicy_lock_memory()`, `secpolicy_acct()`, `secpolicy_allow_setid()`, `secpolicy_proc_owner()`, `secpolicy_proc_access()`, `secpolicy_proc_excl_open()`, `secpolicy_proc_zone()`, `secpolicy_kmdb()`, `secpolicy_error_inject()`, `secpolicy_psecflags()`, `secpolicy_chroot()`, `secpolicy_tasksys()`, `secpolicy_meminfo()`, and basic exec/fork/session/procinfo/link/network/file read/write checks.

CPU and resource controls include `secpolicy_pset()`, `secpolicy_pbind()`, `secpolicy_ponline()`, `secpolicy_pool()`, `secpolicy_blacklist()`, `secpolicy_sys_config()`, `secpolicy_zone_admin()`, `secpolicy_zone_config()`, `secpolicy_rctlsys()`, `secpolicy_resource()`, `secpolicy_resource_anon_mem()`, and `secpolicy_newproc()`.

## Device, Module, and Hardware Policy

`drv_priv()`, `secpolicy_sys_devices()`, `secpolicy_excl_open()`, `secpolicy_console()`, and `secpolicy_power_mgmt()` map device operations to `PRIV_SYS_DEVICES`.

`secpolicy_spec_open()` enforces device policy privilege sets cached in snodes. It refreshes stale device policy generations, selects read or write privilege sets, and treats `PRIV_SYS_NET_CONFIG` as a superset of `PRIV_SYS_IP_CONFIG` for device-policy checks.

`secpolicy_modctl()` allows informational module commands unprivileged, requires all privileges for module loading and device policy setting, and otherwise falls back to system configuration privilege.

High-risk hardware paths include `secpolicy_sti()`, `secpolicy_cpc_cpu()`, `secpolicy_gart_access()`, `secpolicy_gart_map()`, `secpolicy_hwmanip()`, `secpolicy_zinject()`, and `secpolicy_ucode_update()`.

## Networking Policy

Networking checks include privileged port binding, MLP/MAC policies, raw access, observability, ICMP access, net/IP/datatalink/tunnel configuration, NFS, rpcmod, SAD admin device access, and PPP configuration.

`secpolicy_net_privaddr()` special-cases SMB/NBT ports for `PRIV_SYS_SMB` or `PRIV_NET_PRIVADDR`, NFS ports for `PRIV_SYS_NFS`, and all other privileged ports for `PRIV_NET_PRIVADDR`.

`secpolicy_ip_config()`, `secpolicy_dl_config()`, `secpolicy_iptun_config()`, and `secpolicy_ppp_config()` encode privilege supersets so broader network privileges satisfy narrower subsystem configuration checks.

`secpolicy_ip()` and `secpolicy_net()` map pseudo privileges such as `OP_CONFIG`, `OP_RAW`, and `OP_PRIVPORT` to concrete privileges.

## Storage and Filesystem Adjacent Policies

`secpolicy_zfs()` maps ZFS dataset manipulation to `PRIV_SYS_MOUNT`.

`secpolicy_zinject()` requires the full privilege set for ZFS fault injection.

`secpolicy_swapctl()` uses `PRIV_SYS_CONFIG`.

`secpolicy_smb()` protects SMB server driver access with `PRIV_SYS_SMB`.

`secpolicy_vscan()` requires DAC search, DAC read, and file flag setting for virus scanning.

`secpolicy_smbfs_login()` permits a user to manage their own SMBFS login and requires process-owner privilege for others.

## Contracts and Miscellaneous

Contract checks include `secpolicy_contract_identity()`, `secpolicy_contract_observer()`, `secpolicy_contract_observer_choice()`, `secpolicy_contract_event()`, and `secpolicy_contract_event_choice()`.

Other targeted checks include `secpolicy_idmap()`, `secpolicy_pfexec_register()`, `secpolicy_net_reply_equal()`, and `secpolicy_xvm_control()`.

## Notable Invariants

- Policy functions must not assume any particular lock state.
- Credentials are treated as read-only.
- Root-owned files and root identity transitions often require more than a single narrow privilege to prevent escalation.
- Zone operations that can expand available privileges require all privileges available in the zone or all privileges in the global zone.
- Many check-only variants return `0` for allowed and `EPERM` or boolean inverse forms for denied, so callers must observe each function's convention.

## Research Relevance

This is a core filesystem-security file. It defines mount restrictions, vnode permission overrides, setuid/setgid preservation, extended attributes, device policy, ZFS permissions, swap control, SMB/vscan policy, and zone privilege boundaries. Filesystem code in illumos commonly delegates authorization decisions here rather than open-coding privilege checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/policy.c -->