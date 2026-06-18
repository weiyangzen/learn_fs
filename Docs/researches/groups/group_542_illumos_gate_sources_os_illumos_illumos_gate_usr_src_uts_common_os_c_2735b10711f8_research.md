# Group Research: group_542_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_c_2735b10711f8

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cyclic.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cyclic.c

## Purpose

`cyclic.c` implements the illumos cyclic subsystem: high-resolution, per-CPU interval timers that can fire at high, lock, or low interrupt level. It is the kernel’s low-level timer engine for recurring and reprogrammable callbacks, including CPU-bound, CPU-partition-bound, and omnipresent timers.

The file is unusually well documented. Its design centers on minimizing cross-CPU interference by keeping timer state in per-CPU `cyc_cpu_t` structures and using a heap ordered by absolute expiration time.

## Core Data Model

Each CPU owns:

- `cyp_cyclics`: an expandable array of `cyclic_t` slots.
- `cyp_heap`: an array heap of cyclic indexes, sorted by `cy_expire`.
- `cyp_softbuf[]`: producer/consumer buffers for lock-level and low-level cyclics.
- `cyp_state`: online/offline/suspended/expanding/removing state.
- backend state copied from the platform `cyc_backend_t`.

Cyclic IDs are represented by `cyc_id_t`, not opaque numeric handles. Regular IDs point to a single CPU/index pair. Omnipresent IDs keep a linked list of `cyc_omni_cpu_t` components, one per online CPU.

## Timer Firing

`cyclic_fire()` is the high-level interrupt entry point called by the platform backend. It:

- Reads the current high-resolution time.
- Checks the heap root.
- Expires root cyclics whose `cy_expire <= now`.
- Recomputes the next expiration from the previous expiration plus interval.
- Handles `CY_INFINITY` as a one-shot/reprogrammable timer pattern.
- Corrects very late expirations by jumping to the next interval boundary.
- Downheaps after each expiration.
- Reprograms the backend with the next root expiration.

`cyclic_expire()` either calls high-level handlers directly or enqueues lower-level handlers into the appropriate soft interrupt producer/consumer buffer and posts a backend soft interrupt.

## Soft Interrupt Handling

`cyclic_softint()` drains pending lock-level or low-level cyclics. Pending work is tracked with `cy_pend`, which counts how many handler invocations are owed. The softint path calls the handler before atomically decrementing `cy_pend`, preserving the one-to-one mapping between high-level expirations and low-level handler calls.

The implementation is mostly lock-free on the hot path. It handles three difficult races explicitly:

- New high-level expirations bumping `cy_pend` while softint drains it.
- Per-CPU array resize while a softint holds an old `cyp_cyclics` pointer.
- Cyclic removal while a softint is executing or about to execute the handler.

Removal with pending callbacks uses `cyp_rpend` and `cyclic_remove_pend()` so `cyclic_remove()` can preserve the guarantee that all owed handler calls complete before removal returns.

## Heap And Resizing

`cyclic_upheap()` and `cyclic_downheap()` maintain the per-CPU min-heap by expiration time. The heap stores indexes into `cyp_cyclics`, allowing compact arrays and cache-local heap operations.

`cyclic_expand()` doubles the per-CPU heap, cyclic array, and soft buffers. It cross-calls the target CPU through `cyclic_expand_xcall()`, switches heap/cyclic pointers at high interrupt level, zeroes old `cy_pend` values to force softint retry against the new array, flips hard producer buffers, then waits for both soft levels to observe the new buffers before freeing old storage.

## Add, Remove, And Reprogram

`cyclic_add()` creates a regular cyclic under `cpu_lock`, chooses a suitable CPU with `cyclic_pick_cpu()`, allocates a `cyc_id_t`, and inserts the cyclic on the target CPU via cross-call.

`cyclic_remove()` removes either a regular cyclic or all components of an omnipresent cyclic. Regular removal uses `cyclic_remove_here()` and `cyclic_remove_xcall()` to remove the cyclic from its CPU heap at high level, disable the backend if the CPU heap becomes empty, and wait for pending low-level callbacks if required.

`cyclic_reprogram()` can be called from a cyclic handler. It uses `cyi_lock` as a reader lock to prevent migration/removal while reprogramming. Local reprogramming calls `cyclic_reprogram_cyclic()` directly at high level; remote reprogramming cross-calls the owning CPU. A local handler racing with removal may get a failure return instead of a panic.

## CPU Mobility

The file integrates tightly with CPU management:

- `cyclic_juggle()` moves movable cyclics away from a CPU.
- `cyclic_offline()` juggles regular cyclics away and stops omnipresent components.
- `cyclic_online()` restarts omnipresent cyclics on the CPU.
- `cyclic_move_in()` and `cyclic_move_out()` handle CPU partition transitions.
- `cyclic_bind()` applies CPU and CPU-partition bindings.
- `cyclic_move_here()` best-effort migrates an unbound cyclic to the current CPU.

Migration removes the cyclic from the source CPU while preserving its expiration time, then re-adds it to the destination CPU. This relies on `gethrtime()` increasing consistently across CPUs.

## Suspend And Backend Integration

`cyclic_init()` installs the backend template, configures CPU 0, and onlines it. `cyclic_mp_init()` configures remaining CPUs and registers CPU setup hooks.

`cyclic_suspend()` cross-calls every CPU and disables active backends while preserving per-CPU state. `cyclic_resume()` resumes backends, reenables CPUs with cyclics, and reprograms each backend from its heap root.

The backend contract is abstracted through `cyb_configure`, `cyb_enable`, `cyb_disable`, `cyb_reprogram`, `cyb_softint`, `cyb_xcall`, `cyb_set_level`, `cyb_restore_level`, `cyb_suspend`, and `cyb_resume`.

## Dependencies

Key dependencies include:

- CPU lifecycle and partition state: `cpu_lock`, `cpu_t`, `cpupart_t`, CPU flags.
- High-resolution time: `gethrtime()`, `gethrtime_unscaled()`.
- Interrupt/cross-call backend APIs from `cyc_backend_t`.
- Synchronization primitives: semaphores, reader-writer locks, atomics, preemption disable.
- Kernel memory allocation and DTrace probes.

## Research Notes

This file is a concurrency-heavy kernel subsystem. Highest-risk areas are softint resize/removal races, `cy_pend` accounting, backend reprogramming after heap root changes, migration while preserving single-threaded handler semantics, and reprogramming from within handlers racing with removal or omnipresent CPU offline.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cyclic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf.c

## Purpose

`dacf.c` implements the core Device Autoconfiguration Framework. DACF is a lightweight policy engine that maps device descriptions and kernel lifecycle actions to configuration operations supplied by kernel modules.

The rule database maps:

`(device specifier, DACF operation) -> (module, opset, op args, options)`

Supported operations in this file are `post-attach` and `pre-detach`. Supported device specifiers are `minor-nodetype`, `driver-minorname`, and `device-path`.

## Initialization And Rule Storage

`dacf_init()` creates the rule hash matrix, module hash, and per-minor info hash. It registers the synthetic `__kernel` DACF module and reads `/etc/dacf.conf` through `read_dacf_binding_file(NULL)`.

Rules are stored in operation/specifier-specific hash tables selected through `dacf_rule_matrix`. Each hash uses the rule’s device spec string as key and a `dacf_rule_t` as value. Rule values own the key string, so the hash uses a null key destructor and `dacf_rule_val_dtor()` releases the rule.

`dacf_clear_rules()` clears all rule hashes, typically before rereading configuration.

## Rule Lifecycle

`dacf_rule_insert()` validates the requested operation/specifier pairing, constructs a rule with `dacf_rule_ctor()`, takes an initial reference, and inserts it into the proper hash. Duplicate rules are rejected.

`dacf_rule_ctor()` copies the device spec, module name, opset name, options, operation ID, and argument list. A null module name is normalized to `__kernel`.

Rules are reference-counted under `dacf_lock`:

- `dacf_rule_hold()` increments `r_refs`.
- `dacf_rule_rele()` decrements and destroys at zero.
- `dacf_rule_destroy()` frees copied strings and argument lists.

Arguments are maintained as linked `dacf_arg_t` entries with duplicate-name rejection in `dacf_arg_insert()` and full teardown in `dacf_arglist_delete()`.

## Reservations

Reservations defer matched operations until a lifecycle point. `dacf_rsrv_make()` attaches a rule and info handle to a `dacf_rsrvlist_t`, takes a rule reference, and links it into a caller-provided list.

`dacf_process_rsrvs()` walks a reservation list for a requested operation. Depending on flags, it invokes matching reservations with `dacf_op_invoke()` and/or releases them. `dacf_clr_rsrvs()` is a thin wrapper for releasing reservations for a device node and operation.

## Module Registration

`dacf_module_register()` registers a DACF module’s exported `struct dacfsw`. It validates the module revision, counts exported opsets, rejects empty non-kernel modules, and stores a copied opset table in `dacf_module_hash`.

The module object has a reader-writer lock:

- Registration and unregistration take writer access.
- Invocation takes reader access to keep the opset table stable while calling into a module operation.

`dacf_module_unregister()` marks a module unloaded and destroys copied opsets, unless module autounloading is blocked or the module lock cannot be acquired. The synthetic `__kernel` module is not allowed to unregister.

`dacf_destroy_opsets()` frees copied opset names and operation arrays. `dacf_opset_copy()` deep-copies the opset descriptor and terminates the copied operation list with `DACF_OPID_END`.

## Operation Invocation

`dacf_op_invoke()` is the core dispatcher. Given a rule and per-minor info handle, it:

- Finds or loads the target DACF module.
- Takes the module lock as reader.
- Locates the requested opset by name.
- Locates the operation matching the rule’s `r_opid`.
- Marks the devinfo node as invoking DACF to prevent recursive matching deadlocks.
- Drops `dacf_lock` before calling the operation function.
- Reacquires `dacf_lock`, clears the invoking marker, releases the module lock, and normalizes the return code.

It may call `modload("dacf", rule->r_module)` repeatedly until the module registers or loading fails. The `dacf_modload_laps` counter is diagnostic.

## Public DACF Helpers

The lower portion exposes helpers intended for DACF modules:

- Device/minor inspection: `dacf_minor_name`, `dacf_minor_number`, `dacf_get_dev`, `dacf_driver_name`, `dacf_devinfo_node`.
- Argument lookup: `dacf_get_arg`.
- Per-minor opaque data: `dacf_store_info`, `dacf_retrieve_info`.
- Vnode creation for a minor: `dacf_makevp`.

It also provides string-to-enum and enum-to-string helpers for device specifiers, operations, and options.

## Dependencies

The file depends on:

- `mod_hash` for rule, module, and info tables.
- Kernel module loading through `modload`.
- DDI minor data and devinfo internals.
- `dacf_impl.h` structures and flags.
- `kmod_dacfsw`, defined by `dacf_clnt.c`.

## Research Notes

Important invariants are that rule and module metadata are protected by `dacf_lock`, module opsets are protected by `dm_lock`, and DACF drops `dacf_lock` before invoking module callbacks. The main audit hotspots are recursive DACF invocation handling, module load/unload races, reservation reference counts, and opaque per-minor data lifetime because `dacf_info_hash` deliberately has no destructor.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf_clnt.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf_clnt.c

## Purpose

`dacf_clnt.c` implements the kernel-side clients of DACF. It connects device-minor creation and devinfo attach/detach lifecycle events to the core rule engine in `dacf.c`.

It also defines the synthetic `__kernel` DACF module descriptor `kmod_dacfsw`, which is mostly empty outside DEBUG builds.

## Minor Creation Matching

`dacfc_match_create_minor()` is called during minor-node creation. It checks whether a newly created minor node matches any DACF rule and, if so, creates deferred reservations on the devinfo node.

The function filters early:

- Clone devices are ignored unless they are network minor nodes.
- Minor nodes created outside attach are ignored because current DACF hooks only cover post-attach and pre-detach processing.

It builds match keys:

- Full device path from `ddi_pathname()`.
- `driver:minor` name when a minor name exists.
- Minor node type.

Rule matching is performed from most specific to least specific:

1. `device-path`
2. `driver-minorname`
3. `minor-nodetype`

It repeats that ordering separately for `post-attach` and `pre-detach`. Matches allocate `dacf_rsrvlist_t` entries and link them into `DEVI(dip)->devi_dacf_tasks`.

## Recursion Avoidance

Before matching, `dacfc_match_create_minor()` checks `DEVI_IS_INVOKING_DACF(dip)` under `devi_lock`. If a DACF operation is currently being invoked for the same devinfo node, matching is aborted with a warning. This prevents a configuration operation from recursively creating a minor node and deadlocking on the same devinfo task machinery.

## Post-Attach Handling

`dacfc_postattach()` invokes all post-attach reservations for the devinfo node with `dacf_process_rsrvs(..., DACF_PROC_INVOKE)`. It then scans the reservation list for failed post-attach operations.

A failure sets `DACF_FAILURE`; optional debug logging reports the affected device path. The function does not release reservations after invocation, leaving them available for later cleanup or pre-detach flow.

## Pre-Detach Handling

`dacfc_predetach()` invokes all pre-detach reservations and checks whether any failed. If a pre-detach operation fails, it makes one attempt to re-run post-attach operations through `dacfc_postattach()` to restore a sane configuration state.

Debug logging can report both the failed unconfiguration and whether re-autoconfiguration succeeded.

## Kernel DACF Module

The file defines `kmod_dacfsw`, registered by `dacf_init()` as the special `__kernel` DACF module. In DEBUG builds it exposes a test post-attach operation under the `kmod_test` opset. In non-DEBUG builds the kernel module has no opsets but is still registered so kernel-supplied DACF operations can exist without loadable modules.

## Dependencies

`dacf_clnt.c` depends on the core DACF APIs:

- `dacf_match`
- `dacf_rsrv_make`
- `dacf_process_rsrvs`
- `dacf_get_arg`

It also uses DDI/devinfo internals, minor data, driver names, device paths, and DACF debug flags.

## Research Notes

This file is the bridge between rule matching and actual device lifecycle events. The key semantic detail is reservation: matching occurs during minor creation, but operation invocation happens later at attach/detach boundaries. The highest-risk areas are the recursion guard, exact match priority, clone-device filtering, and recovery behavior when pre-detach fails.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf_clnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/damap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/damap.c

## Purpose

`damap.c` implements device address maps. A DAM tracks provider-reported string addresses, waits for reports to stabilize, activates newly stable addresses, deactivates addresses that disappear, and lets class drivers look up active address IDs.

It supports two reporting modes:

- `DAMAP_REPORT_PERADDR`: providers report individual address additions and deletions.
- `DAMAP_REPORT_FULLSET`: providers report a complete address set between begin/end calls.

## Map Creation And Allocation

`damap_create()` allocates a lightly backed map, records callbacks, initializes locks, condition variables, bitsets, options, stabilization timing, and returns a `damap_t`.

Major backing resources are allocated lazily by `dam_map_alloc()` on first report. It creates:

- Soft-state storage for `dam_da_t` address records.
- A string-to-ID table through `ddi_strid`.
- Per-map kstats.
- Bitsets for active, stable, and report sets.

The map grows in `DAM_SIZE_BUMP` chunks when IDs exceed the current bitset capacity.

`damap_destroy()` marks the map destroy-pending, synchronizes pending activity, cancels timers, deactivates stable addresses, releases unstable entries directly, destroys string IDs/soft state/kstats/bitsets, and frees the map.

## Stabilization And Synchronization

`damap_sync()` waits until no full-set update, stabilization pass, report-set entries, or scheduled timeout remains. With a nonzero timeout it can return 0 on timeout. After apparent quiescence, it waits one stabilization interval and checks again to avoid racing with late report activity.

Stabilization is timer-driven. Per-address reports use `dam_addr_stable_cb()`. Full-set reports use `dam_addrset_stable_cb()`. Both eventually dispatch `dam_stabilize_map()` on `system_taskq`.

`dam_stabilize_map()` compares the current active set and computed stable set, derives activation and deactivation bitsets, drops the map lock while invoking callbacks, then updates stable-cycle counters and active kstats.

## Per-Address Reporting

`damap_addr_add()` reports an address addition. It validates mode, allocates backing resources, gets or creates an address ID, clears any existing pending report as jitter, stores provider-private data and optional nvlist, then calls `dam_addr_report(..., RPT_ADDR_ADD)`.

`damap_addr_del()` reports removal. Missing addresses are treated as success. Existing pending reports are released as jitter, then a delete report is queued through `dam_addr_report(..., RPT_ADDR_DEL)`.

`dam_addr_report()` timestamps the report, sets a deadline based on `ddi_get_lbolt64() + dam_stable_ticks`, records add/delete intent with `DA_RELE`, adds the ID to the report set, and schedules the stabilization timeout.

`dam_addr_report_release()` cancels a pending report, optionally calls the provider deactivation callback for unstable private data, clears provider-private data, and frees the report nvlist.

## Full-Set Reporting

`damap_addrset_begin()` starts a full-set report and sets `DAM_SETADD`. It flushes any already pending full-set activity first.

`damap_addrset_add()` adds addresses to the pending report set while `DAM_SETADD` is active. It creates IDs as needed, handles jitter by releasing previous pending report data, stores provider-private data and optional nvlist, and returns the address ID.

`damap_addrset_end()` either resets pending report state when `DAMAP_END_RESET` is requested or schedules full-set stabilization using `dam_addrset_stable_cb()`.

`damap_addrset_flush()` cancels a pending full-set report and releases pending address report data.

In full-set stabilization, the report set becomes the new stable set, then active/stable deltas drive activation and deactivation.

## Lookup And Reference Management

Active addresses can be queried through:

- `damap_lookup()`: returns and references a stable active ID by address string.
- `damap_lookup_all()`: returns a bitset list of all active IDs and references each.
- `damap_id_next()`: iterates an ID list.
- `damap_id_list_rele()`: releases all IDs in a list.
- `damap_id_rele()`: releases one referenced ID.
- `damap_id_ref()`: returns the current reference count.
- `damap_id2addr()` and `damap_id2nvlist()`: map IDs to address strings and active nvlists.
- `damap_id_priv_set()` and `damap_id_priv_get()`: manage class-driver private data per address.

`dam_addr_release()` frees an address ID only when no outstanding references remain and no report is pending.

## Activation And Deactivation

`dam_addr_activate()` marks an address active, moves the reported nvlist into the stable nvlist slot, calls the provider activation callback if present, then invokes the class configuration callback. If configuration fails, it marks `DA_FAILED_CONFIG` and immediately deactivates with reason `DAMAP_DEACT_RSN_CFG_FAIL`.

`dam_addr_deactivate()` invokes the class unconfiguration callback and then calls `dam_deact_cleanup()`.

`dam_deact_cleanup()` invokes the provider deactivation callback if present, clears active state and stored nvlists/private data, then releases the address.

`dam_addrset_activate()` and `dam_addrset_deactivate()` can run serially or create temporary taskqs for multithreaded configuration when `DAMAP_MTCONFIG` is set.

## Timers And Taskq Behavior

`dam_sched_timeout()` manages a single map timeout. It cancels with `untimeout()` when requested and schedules a timeout only if none is active.

`dam_addr_stable_cb()` scans pending per-address reports, computes which deadlines have passed, dispatches `dam_stabilize_map()` only when handoff succeeds, and reschedules for the next nearest deadline or short retry delay after taskq dispatch failure.

`dam_addrset_stable_cb()` handles full-set stabilization. If a stabilization pass is already active or taskq dispatch fails, it counts overrun and retries after `damap_taskq_dispatch_retry_usec`.

## Kstats

`dam_kstat_create()` creates per-map kstats under module `dam`, class `damap`, with counters:

- `cycles`
- `overrun`
- `jitter`
- `active`

Macros update these counters when the kstat exists.

## Dependencies

The file depends on:

- `ddi_strid` for string-to-ID mapping.
- DDI soft state for per-address records.
- `bitset_t` for active/stable/report sets.
- `timeout`, `untimeout`, `system_taskq`, and optional temporary taskqs.
- DTrace probes, kstats, nvlists, and DDI timing helpers.

## Research Notes

The core invariant is that provider report churn is not immediately exposed. Reports first enter `dam_report_set`, then stabilize into a computed stable set, then activate/deactivate callbacks are invoked outside `dam_lock`. Audit hotspots include report jitter handling, reference counts during deactivation, full-set flush/reset semantics, timeout cancellation while callbacks race, and taskq dispatch failure recovery.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/damap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi.c

## Purpose

`ddi.c` implements kernel functions required by the UNIX Device Driver Interface and STREAMS compatibility interfaces. Many routines are function equivalents of macros or legacy DDI/SVR4 APIs, made available as callable kernel symbols for drivers.

The file covers device number manipulation, driver parameters, buffer headers, time conversions, STREAMS queue/perimeter helpers, queue callback wrappers, device association, and kernel virtual address translation.

## Device Number Helpers

The file provides major/minor extraction and construction:

- `getmajor`, `getemajor`
- `getminor`, `geteminor`
- `etoimajor`, `itoemajor`
- `makedevice`
- `cmpdev`, `expdev`

The implementation handles `_LP64` and non-`_LP64` layouts with `NBITSMINOR64`/`MAXMIN64` versus `NBITSMINOR`/`MAXMIN`. illumos has a direct internal/external major mapping, so `itoemajor()` mostly validates and returns the same major.

## Basic DDI Utilities

`drv_getparm()` returns selected kernel parameters such as current process, process group, lbolt, time, PID, session ID, and credentials. It uses process locks where needed.

`drv_setparm()` increments CPU system statistics for receive, transmit, modem, raw character, canonical character, and output character counters.

`getrbuf()` allocates and initializes a `struct buf`; `freerbuf()` finalizes and frees it.

`btop()`, `btopr()`, and `ptob()` convert between byte counts and page counts.

`drv_hztousec()` and `drv_usectohz()` convert between ticks and microseconds, clamping tick-to-usec overflow to `LONG_MAX`.

`time_to_wait()` computes an absolute lbolt timeout target for timed condition-variable waits.

## STREAMS Macro Wrappers

The file exposes function versions of STREAMS helpers:

- `datamsg()`
- `OTHERQ()`
- `RD()`
- `WR()`
- `SAMESTR()`

`bcanputnext()` and `canputnext()` check downstream flow control. `canputnext()` uses stream reference locking, detects a full downstream service queue, sets `QWANTW` when blocked, and handles the common non-full path cheaply.

## Queue Lifecycle

`qprocson()` inserts a driver/module queue into the stream so put and service routines can run. It avoids reinsertion on reopen unless `_QINSERTING` is set.

`qprocsoff()` disables service/put processing, removes the queue, and is idempotent for `QWCLOSE`.

`freezestr()` freezes an entire stream by blocking entry and taking queue locks across the stream. `unfreezestr()` releases queue locks, unblocks the stream, and releases the stream reference. This is explicitly special because it acquires multiple queue locks.

## STREAMS Waiting And Perimeters

`qwait_sig()` and `qwait()` are used by open/close procedures to sleep while temporarily lowering perimeter exclusion. They:

- Exit the outer perimeter if present.
- Drop inner exclusive state and syncq count under lock.
- Broadcast waiters when needed.
- Drain queued syncq work when possible.
- Otherwise wait on `sq_exitwait`.
- Re-enter the syncq before returning.

`qwait_sig()` returns whether a signal interrupted the wait. `qwait()` waits uninterruptibly.

`qwait_rw()` is a consolidation-private variant for synchronous read/write entry points. It drops exclusive put access, waits for exit activity, then re-enters as `SQ_PUT`, returning whether a signal was seen.

`qwriter()` dispatches asynchronous upgrade to exclusive access at either the inner or outer perimeter through `qwriter_inner()` or `qwriter_outer()`.

## Queue Callbacks

`qtimeout()` and `qbufcall()` schedule callbacks that enter the queue’s inner perimeter via `qcallbwrapper`. They allocate `callbparams_t` under the syncq lock, store cancel metadata, schedule `timeout()` or `bufcall()`, and record the callback ID.

`quntimeout()` and `qunbufcall()` cancel those callbacks. They serialize cancellation through `sq_callbflags`, set the cancel ID/type, wake blocked callback wrappers, perform the underlying cancel operation, free callback parameters as appropriate, clear cancellation state, and wake waiters.

## Queue Device Association

`qassociate()` associates a stream with a specific hardware instance. Passing `-1` clears association. Otherwise it gets the stream vnode’s major number, holds the devinfo for the requested instance without attaching it, associates the queue with that devinfo, and releases the hold.

The comments explain the contract: `qassociate()` cannot drive blocking attach from a STREAMS put context, so callers must handle failure if the requested instance is detached or inaccessible.

## Address Translation

`kvtoppid()` returns the physical page frame number for a kernel virtual address through `hat_getpfnum(kas.a_hat, addr)`. It is the SVR4MP-style replacement for older platform-specific `hat_getkpfnum()` interfaces.

## Dependencies

This file depends heavily on:

- Device number layout macros.
- Process/session/credential state.
- CPU statistics.
- Buffer cache initialization.
- STREAMS internals: queues, streams, syncqs, perimeters, callback parameter lists.
- Timeout and bufcall machinery.
- Devinfo association helpers and vnode device numbers.
- HAT/kernel address-space APIs.

## Research Notes

`ddi.c` is glue code, but much of it sits on sensitive STREAMS synchronization boundaries. Important audit areas are `canputnext()` stream reference handling, `freezestr()` multi-lock ordering, `qwait*()` perimeter exit/reentry semantics, callback cancellation races in `quntimeout()`/`qunbufcall()`, and `qassociate()` failure handling in drivers that call it from nonblocking contexts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi.c -->