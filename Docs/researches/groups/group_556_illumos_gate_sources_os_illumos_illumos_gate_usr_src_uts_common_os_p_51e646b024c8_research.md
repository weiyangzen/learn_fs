# Group Research: group_556_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_p_51e646b024c8

Scope: `Docs/research_subset_a.md`
Source tree: `sources/os/illumos/illumos-gate`
Files researched: 10

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool.c

## Purpose

`pool.c` implements the common illumos resource pools layer: pool lifecycle, global pool state, pool locking, pool/resource association, pool property management, exacct packing for `/dev/pool`, process/project/task/zone pool binding, and asynchronous pool event callbacks.

Read completely: 1,797 lines.

## Main Responsibilities

- Initializes the default pool at boot and wires it to the default processor-set plugin.
- Provides long-duration, interruptible global pool locking with `pool_lock()`, `pool_lock_intr()`, `pool_unlock()`, and ownership checks through `pool_lock_held()`.
- Coordinates pool rebinding against fork, exec, exit, and LWP creation through the per-process pool barrier (`pool_barrier_enter()` / `pool_barrier_exit()`).
- Enables and disables the pools facility, including default system and pool properties, modification timestamps, and event dispatch.
- Creates/destroys pools and dispatches creation/destruction of pool resource components such as processor sets.
- Associates and disassociates pools with resource sets, currently processor sets via `pool_pset_assoc()`.
- Exposes pool configuration snapshots using exacct groups, including system, pool, and processor-set data.
- Validates and mutates system/pool/pset/CPU properties through typed `nvlist` property tables.
- Implements `pool_do_bind()`, the central atomic binding operation for PIDs, tasks, projects, pools, and zones.
- Provides async event callback registration and dispatch for pool enable/disable/change notifications.

## Important Data Structures And Globals

- `pool_default`: always-present default pool.
- `pool_count`, `pool_state`: current pool count and enabled/disabled state.
- `pool_buf` / `pool_bufsz`: saved pre-commit configuration snapshot used during pool commit transactions.
- `pool_sys_mod`, `pool_pool_mod`: system and pool modification timestamps reported in exacct output.
- `pool_sys_prop`: global pool-system property nvlist.
- `pool_ids`: ID allocator for non-default pools.
- `pool_list`: list of all `pool_t` objects.
- `pool_mutex`, `pool_busy_cv`, `pool_busy_thread`: implementation of the global pool lock.
- `pool_barrier_lock`, `pool_barrier_cv`, `pool_barrier_count`: synchronization with processes currently inside pool-sensitive barriers.
- `pool_event_cb_list`, `pool_event_cb_lock`, `pool_event_cb_taskq`: event callback registry and async delivery path.

## Control Flow And Algorithms

`pool_init()` allocates ID space, creates `pool_default`, initializes `pool_list`, initializes the processor-set plugin, assigns `p0` and the global zone to the default pool, and sets the default reference count.

`pool_status()` gates transitions. `POOL_ENABLED` initializes pset support and installs default system/pool properties; `POOL_DISABLED` refuses while more than one pool exists, disables pset support, and frees properties.

`pool_pool_create()` allocates a new `pool_t`, assigns an ID, attaches it to the default pset, initializes required properties, inserts it in `pool_list`, and increments `pool_count`. `pool_pool_destroy()` first rebinds all members to the default pool, updates zones that pointed at the destroyed pool, releases properties and ID allocation, updates pset pool counts, and frees the object.

`pool_pack_conf()` builds an exacct hierarchy by packing system metadata, pool records, and pset records. `pool_commit(1)` preserves a snapshot used by concurrent queries while a userspace commit is underway; `pool_commit(0)` releases that snapshot.

`pool_do_bind()` is the key atomic operation. It builds a target process list under `pidlock`, sets `PBWAIT`, waits for pool barriers to drain, rechecks exiting processes and newly forked children, performs pset preflight through `pset_bind_start()`, moves each process's threads to the target pset, optionally moves threads to a pool-specified scheduling class, updates `p_pool` references, wakes stopped processes, and finally handles project/zone cleanup. Failure before the binding phase wakes all stopped processes and leaves old bindings intact.

## Dependencies And Integration

- Calls into `pool_pset.c` for processor-set enable/disable/create/destroy/association/packing/property operations.
- Uses process, project, zone, scheduler, class, and FSS interfaces for binding semantics.
- Uses exacct and nvpair APIs for kernel-to-user configuration serialization.
- Integrates with `/dev/pool` ioctl paths and older pset/process binding callers through exported pool entry points.

## Locking And Concurrency

The file documents the lock order as `pool_lock() -> cpu_lock -> pidlock -> p_lock -> pool_barrier_lock`. The global pool lock is not a normal mutex because callers may sleep for long periods and may need signalable acquisition. Binding uses `PBWAIT` and `p_poolcnt` to stop relevant processes at stable points before rebinding their resource-set membership.

## Notable Risks And Invariants

- Callers must hold `pool_lock()` for almost all pool state mutation and snapshot operations.
- `pool_do_bind()` assumes resource-set-specific preflight and finish routines are kept in sync with operations that can make thread binding fail.
- Local zones cannot arbitrarily bind processes/tasks to pools; zone handling is deliberately constrained.
- Pool destruction requires every member to be rebound to the default pool and the destroyed pool reference count to drop to zero.
- Event callbacks are dispatched asynchronously and must not run while holding the pool lock.

## Research Relevance

This file is central to illumos workload/resource isolation. For filesystem and storage research it matters because pools influence scheduling, CPU placement, zones, project controls, and accounting context for kernel work and user processes that drive filesystem load.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool_pset.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool_pset.c

## Purpose

`pool_pset.c` is the processor-set plugin for the resource pools subsystem. It maps pool resource-component operations onto CPU partitions, processor-set visibility, pset/CPU properties, pset packing, and per-zone CPU visibility behavior.

Read completely: 978 lines.

## Main Responsibilities

- Initializes and maintains the global list of pool-managed processor sets.
- Enables/disables pset support when pools are enabled/disabled.
- Creates and destroys pool processor sets on top of `cpupart_create()` / `cpupart_destroy()`.
- Associates pools with psets and atomically rebinds affected processes through `pool_do_bind()`.
- Transfers named CPU IDs between psets.
- Binds all threads of a process to a target pset after preflight checks.
- Maintains CPU and pset kstat visibility for zones.
- Exposes dynamic and static pset/CPU properties to the common pool layer.
- Packs processor-set and CPU state into exacct groups for pool configuration queries.

## Important Data Structures And Globals

- `pool_pset_list`: list of all `pool_pset_t` objects.
- `pool_pset_default`: the default pset wrapper with ID `PS_NONE`.
- `pool_pset_mod`, `pool_cpu_mod`: modification timestamps for psets and CPU properties.
- `pool_pset_props`: property schema for pset properties such as `pset.name`, `pset.min`, `pset.max`, `pset.load`, and `pset.size`.
- `pool_cpu_props`: property schema for CPU properties such as `cpu.comment`, `cpu.status`, and `cpu.pinned`.

## Research Relevance

Processor-set pools shape CPU availability and scheduler behavior for zones and projects. This file explains how illumos ties pool configuration to real CPU topology and how zone visibility of CPU resources is enforced.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool_pset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/port_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/port_subr.c

## Purpose

`port_subr.c` provides shared kernel support for event ports and event sources. It manages event allocation, queue submission/removal, poll wakeups, fd-source cleanup, and kernel event-source association with port file descriptors.

Read completely: 797 lines.

## Research Relevance

Event ports are a scalable notification primitive used by files, pollable objects, timers, and user-level event loops. This file is relevant to filesystem research because file descriptors and vnode-backed objects can register event associations whose lifetime must remain coherent with close, poll, and event retrieval.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/port_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/printf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/printf.c

## Purpose

`printf.c` implements core kernel formatted output and logging wrappers: `printf`, `uprintf`, `cmn_err`, `dev_err`, STREAMS `strlog`, assertion failure reporting, zone-aware output, syslog delivery, console delivery, interrupt-safe logging, and optional panic-buffer logging.

Read completely: 367 lines.

## Research Relevance

This file defines how kernel diagnostics from filesystem, STREAMS, drivers, and resource-control paths reach console and logs. Understanding its context restrictions is important when interpreting logging behavior from low-level storage paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/printf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/priv.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/priv.c

## Purpose

`priv.c` implements the kernel privilege-set abstraction: privilege initialization, `/proc` privilege export/import support, runtime privilege name allocation, opaque set operations, process credential permission checks, and privilege-aware credential flag transitions.

Read completely: 745 lines.

## Research Relevance

Kernel privilege checks gate many filesystem and storage operations, including mount, device, process-control, scheduling, and resource-management actions. This file defines the low-level set algebra and credential dominance rules those checks rely on.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/priv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/privs.awk -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/privs.awk

## Purpose

`privs.awk` is the generator for illumos privilege metadata. From a privilege definition input, it emits private kernel constants, public privilege-name constants, the C privilege name/metadata table, and `/etc/security/priv_names` explanatory text.

Read completely: 404 lines.

## Research Relevance

This script defines the generated privilege universe that kernel access checks use. It is relevant when tracing a named privilege from public headers into numeric kernel privilege-set operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/privs.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/proc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/proc.c

## Purpose

`proc.c` provides small process-core helpers for process context callback lists and process security flags.

Read completely: 173 lines.

## Research Relevance

Although small, this file is part of process lifecycle infrastructure used by kernel subsystems that attach state to processes, including mechanisms that can affect filesystem or device behavior across fork/exec/exit.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/procset.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/procset.c

## Purpose

`procset.c` implements `procset_t` selection logic for processes and LWPs. It validates procset operands, resolves `P_MYID`, scans process/LWP sets, evaluates set operations, and provides callbacks over matching processes or threads.

Read completely: 941 lines.

## Research Relevance

Procsets are a common selection language for process, scheduling, signal, and pool operations. This file is relevant when tracing how a filesystem-related workload or administrative command selects affected processes by project, zone, pool, UID, or task.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/procset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/project.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/project.c

## Purpose

`project.c` implements kernel project tracking and project-level resource controls. Projects group tasks/processes within zones, maintain usage counters, register resource controls, expose project kstats, and integrate with CPU caps, FSS, IPC, event ports, contracts, locked memory, crypto memory, and privilege daemon state.

Read completely: 1,162 lines.

## Research Relevance

Projects are a major illumos workload accounting and limit boundary. Filesystem/storage behavior can be affected by project rctls for process count, locked memory, IPC resources, CPU shares/caps, and event-port IDs, so this file is important for workload isolation research.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/project.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/putnext.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/putnext.c

## Purpose

`putnext.c` implements the C versions of STREAMS `putnext()` and `put()`. These functions deliver messages to downstream queue put procedures while respecting syncq/perimeter concurrency, queued message ordering, fast put locks, writer exclusion, and stack-depth protection.

Read completely: 679 lines.

## Research Relevance

STREAMS is used by illumos networking, terminal, and some device/file-descriptor paths. This file is relevant to filesystem-adjacent event and I/O research because it defines how STREAMS messages are delivered safely under high concurrency and deep module stacks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/putnext.c -->