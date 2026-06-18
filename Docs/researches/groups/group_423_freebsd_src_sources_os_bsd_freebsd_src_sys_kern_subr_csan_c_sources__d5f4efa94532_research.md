# Group Research: group_423_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_subr_csan_c_sources__d5f4efa94532

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_csan.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_csan.c

## Purpose
Implements the FreeBSD kernel concurrency sanitizer runtime. It receives compiler-emitted ThreadSanitizer-style hooks, samples kernel memory accesses, detects overlapping racy accesses across CPUs, and reports them through `printf` or `panic` depending on configuration.

## Key Elements
- Per-CPU state: `kcsan_cpus[MAXCPU]`, `csan_cpu_t`, `csan_cell_t`.
- Runtime enablement: `kcsan_enable()` at `SI_SUB_SMP`.
- Main detector: `kcsan_access(addr, size, write, atomic, pc)`.
- Reporting: `kcsan_report()` with optional DDB symbol lookup and MD unwind.
- Compiler hooks: `__tsan_read*`, `__tsan_write*`, range hooks, init/function-entry no-ops.
- Instrumented libc-style helpers: `kcsan_memcpy`, `kcsan_memcmp`, `kcsan_memset`, `kcsan_memmove`, string helpers, and copyin/copyout wrappers.
- Atomic wrappers from `<sys/atomic_san.h>`.
- Bus-space wrappers from `<sys/bus_san.h>`.

## Behavior
`kcsan_access()` first exits if KCSAN is disabled, the machine-dependent layer rejects the address, or the kernel is panicked. It compares the new access with each CPU's sampled access cell, ignores non-overlaps, read/read pairs, and accesses where all writes are marked atomic, then reports the first conflict.

Sampling is deliberately sparse: every `KCSAN_NACCESSES` accesses, the current CPU publishes one access cell, delays for `KCSAN_DELAY`, then clears it. Interrupt state is managed by the MD layer while publishing the sample.

## Research Notes
This file is runtime glue for compiler and kernel wrappers. The race model is simple and sampling-based: it catches conflicting overlapping accesses only while another CPU has an active sampled cell. Atomic wrappers still record accesses, but conflicts between properly atomic writers/readers are suppressed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_csan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_devmap.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_devmap.c

## Purpose
Provides machine-independent helpers for statically and dynamically mapping device physical memory into kernel virtual address space.

## Key Elements
- Static devmap support under `__HAVE_STATIC_DEVMAP`.
- Static table registration: `devmap_register_table()`.
- Bootstrap mapping: `devmap_bootstrap()`.
- AKVA dynamic static-entry builder: `devmap_add_entry()`.
- Lookup helpers: `devmap_ptov()` and `devmap_vtop()`.
- Public mapping APIs: `pmap_mapdev()`, `pmap_mapdev_attr()`, `pmap_unmapdev()`.
- DDB command: `show devmap` when static devmap and DDB are enabled.

## Behavior
Static mappings are registered before bootstrap and installed with `pmap_preboot_map_attr()` as device memory. `devmap_lastaddr()` reports the lowest KVA consumed by static device mappings.

`pmap_mapdev_attr()` first reuses a static device mapping when possible. Otherwise it rounds the physical range to pages, allocates KVA, and enters mappings with `pmap_kenter()`. Some platforms use special early-boot allocation from the top of KVA, and aarch64 prefers aligned KVA for large mappings. `pmap_unmapdev()` skips static mappings, otherwise removes the device mapping and frees the KVA.

## Research Notes
The file distinguishes firmware/platform-provided static mappings from ad hoc KVA mappings. Static entries are always device-memory mappings; callers asking for a non-device memory attribute cannot use the static table.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_devmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_devstat.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_devstat.c

## Purpose
Implements kernel device I/O statistics used by storage devices and exposed to userland through `kern.devstat.*` sysctls and the `devstat` mmap device.

## Key Elements
- Global list: `device_statq`.
- Synchronization: `devstat_mutex`.
- Public lifecycle: `devstat_new_entry()`, `devstat_remove_entry()`.
- Transaction accounting: `devstat_start_transaction*()`, `devstat_end_transaction*()`.
- BIO integration: `devstat_start_transaction_bio*()`, `devstat_end_transaction_bio*()`.
- Sysctls: `kern.devstat.all`, `numdevs`, `generation`, `version`.
- mmap backing allocator: `struct statspage`, `devstat_alloc()`, `devstat_free()`.
- DTrace SDT probes: `io:start` and `io:done`.

## Behavior
Devices are inserted into a priority-sorted STAILQ, then assigned monotonically increasing device numbers and creation times. Transaction starts and completions update counters mostly locklessly, using `sequence0` and `sequence1` as consistency markers for mmap readers.

`devstat_end_transaction()` updates bytes, operation counts, tag counts, duration, busy time, and end counts. BIO wrappers derive read/write/free/no-data categories from `bio_cmd`, account residual bytes, and emit DTrace probes.

The `kern.devstat.all` sysctl emits a generation number followed by each `struct devstat`, retrying with `EBUSY` if the list changes during traversal. The mmap path exposes pages of allocated `struct devstat` entries read-only.

## Research Notes
The sequence fields are deliberately placed and updated to let lockless userland snapshots detect torn reads. Structural list changes are mutex-protected; per-device counters rely on ordered atomic sequence updates.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_devstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_disk.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_disk.c

## Purpose
Provides disk-related utility routines: formatted disk transfer error reporting and a BIO queue implementation with seek sorting and barrier semantics.

## Key Elements
- Debug sysctl: `debug.bioq_batchsize`.
- Error formatter: `disk_err()`.
- Queue lifecycle: `bioq_init()`.
- Queue operations: `bioq_insert_head()`, `bioq_insert_tail()`, `bioq_first()`, `bioq_takefirst()`, `bioq_remove()`, `bioq_flush()`.
- Sort helper: `bioq_disksort()`.

## Behavior
`disk_err()` prints device or disk name, BIO command, and filesystem block range. It handles unknown devices, single-block transfers, and a known completed block offset.

The BIO queue uses a TAILQ plus metadata:
- `last_offset` models current disk head position.
- `insert_point` acts as a barrier for later sorted inserts.
- `total` counts queued BIOs.
- `batched` limits long sorted batches.

`bioq_disksort()` only sorts read, write, and delete BIOs without `BIO_ORDERED`. Ordered or non-offset commands go to the tail and create ordering barriers. Sorting uses unsigned offset distance from `last_offset`, preserving elevator-style scan ordering.

## Research Notes
Direct queue operations intentionally alter future sorting behavior. `bioq_insert_tail()` creates a barrier, while `bioq_insert_head()` updates `last_offset` so later sorted requests stay behind the inserted head request.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_dummy_vdso_tc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_dummy_vdso_tc.c

## Purpose
Supplies dummy VDSO timecounter fill routines for platforms that do not provide CPU-specific VDSO timehands support.

## Key Elements
- `cpu_fill_vdso_timehands(struct vdso_timehands *, struct timecounter *)`.
- 32-bit compatibility variant under `COMPAT_FREEBSD32`: `cpu_fill_vdso_timehands32()`.

## Behavior
Both routines return `0` and do not populate their output structures. This indicates that no CPU-specific VDSO timecounter data is available from this implementation.

## Research Notes
This is a compatibility stub. Real architectures that support fast userspace timecounter reads replace these functions with machine-dependent implementations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_dummy_vdso_tc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_early.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_early.c

## Purpose
Provides early-boot wrappers for memory routines before the normal runtime environment is fully available.

## Key Elements
- `memset_early()`.
- `memcpy_early()`.
- `memmove_early()`.
- Optional machine-specific overrides: `MEMSET_EARLY_FUNC`, `MEMCPY_EARLY_FUNC`, `MEMMOVE_EARLY_FUNC`.

## Behavior
Each wrapper calls either the normal libc/kernel routine or a machine-provided early implementation selected by preprocessor macro. If no machine override exists, the wrapper maps directly to `memset`, `memcpy`, or `memmove`.

## Research Notes
The file is intentionally small and exists to provide stable MI names for early boot code while letting architectures swap in safe implementations for periods when normal code may not be usable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_early.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_efi_map.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_efi_map.c

## Purpose
Processes UEFI memory map descriptors for physical memory discovery, exclusion of runtime/reserved ranges, and diagnostic printing.

## Key Elements
- Iterator: `efi_map_foreach_entry()`.
- Physmem add pass: `efi_map_add_entries()`.
- Physmem exclusion pass: `efi_map_exclude_entries()`.
- Entry handler: `handle_efi_map_entry()`.
- Printer: `efi_map_print_entries()`.

## Behavior
`efi_map_foreach_entry()` computes the descriptor array offset after `struct efi_map_header`, validates descriptor size, and invokes a callback for every descriptor.

The memory map is handled in two passes. The add pass calls `physmem_hardware_region()` for usable loader, boot service, conventional, reclaim, runtime code, and runtime data ranges. The exclude pass removes ACPI reclaim, runtime code, and runtime data from allocation with `EXFLAG_NOALLOC`, while still allowing them to be represented in the direct map.

Printing decodes EFI memory type names, physical and virtual addresses, page counts, and memory attributes such as UC, WC, WB, XP, NV, RO, and RUNTIME.

## Research Notes
Runtime firmware memory is deliberately added first and excluded later so it can be mapped but not used for general allocation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_efi_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_epoch.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_epoch.c

## Purpose
Implements FreeBSD's epoch reclamation subsystem on top of Concurrency Kit epochs. It provides non-preemptible and preemptible epoch sections, grace-period waits, deferred callbacks, and callback draining.

## Key Elements
- Per-epoch structure: `struct epoch`.
- Per-CPU records: `struct epoch_record`.
- Global epochs: `global_epoch`, `global_epoch_preempt`.
- Lifecycle: `epoch_alloc()`, `epoch_free()`.
- Entry/exit: `epoch_enter()`, `epoch_exit()`, `_epoch_enter_preempt()`, `_epoch_exit_preempt()`.
- Grace waits: `epoch_wait()`, `epoch_wait_preempt()`.
- Deferred callbacks: `epoch_call()`, `epoch_call_task()`.
- Drain path: `epoch_drain_callbacks()`.
- Optional tracing under `EPOCH_TRACE`.
- Stats sysctls under `kern.epoch.stats`.

## Behavior
Initialization creates a per-CPU UMA zone, attaches per-CPU group tasks for callback processing, initializes counters, and allocates the global epochs. Each epoch owns per-CPU CK records and a drain lock pair.

Non-preemptible epoch sections enter a critical section and use the current CPU record. Preemptible epoch sections pin the thread, add an `epoch_tracker` to the CPU record's thread list, and call CK begin/end with a section object.

`epoch_wait_preempt()` may migrate to the CPU with blocking epoch participants, boost priorities, wait through turnstiles, or voluntarily switch to let blockers run. `epoch_call()` queues callbacks on the current CPU record and the per-CPU task polls all active epochs for deferred callbacks.

## Research Notes
The preemptible wait path is scheduler-aware and much more complex than the non-preemptible spin path. `epoch_free()` first drains callbacks, marks the epoch unused, then waits through `global_epoch` so callback tasks stop observing it before freeing per-CPU records.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_epoch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_eventhandler.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_eventhandler.c

## Purpose
Implements the kernel eventhandler registry: named lists of callback entries sorted by priority, with safe deregistration while lists are being invoked.

## Key Elements
- Global list of lists: `eventhandler_lists`.
- Global mutex: `eventhandler_mutex`.
- Per-list locks via `EHL_LOCK`.
- Registration: `eventhandler_register()`.
- VIMAGE registration: `vimage_eventhandler_register()` when enabled.
- Deregistration: `eventhandler_deregister()`, `eventhandler_deregister_nowait()`.
- Lookup/create: `eventhandler_find_list()`, `eventhandler_create_list()`.
- Cleanup: `eventhandler_prune_list()`.

## Behavior
The subsystem initializes at `SI_SUB_EVENTHANDLER`. Lists are created lazily by name, with a second lookup after allocation to avoid races. Handlers are inserted by increasing priority, preserving efficient tail insertion when priorities are equal.

If a handler or whole list is deregistered while the list is running, entries are not immediately freed. They are marked with `EHE_DEAD_PRIORITY` and counted in `el_deadcount`; pruning later removes and frees them. Blocking deregistration waits until dead entries are pruned, while the nowait variant returns after marking.

## Research Notes
This file manages list infrastructure only. Actual event invocation is macro-driven in eventhandler interfaces, which rely on the dead-entry/prune protocol implemented here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_eventhandler.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_fattime.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_fattime.c

## Purpose
Converts between POSIX `timespec` values and MS-DOS/FAT date, time, and hundredths-of-second timestamp fields.

## Key Elements
- Forward conversion: `timespec2fattime()`.
- Reverse conversion: `fattime2timespec()`.
- Four-year leap-cycle constants and month tables: `mtab`, `daytab`.
- Local/UTC behavior controlled by the `utc` argument.
- Optional standalone test driver under `TEST_DRIVER`.

## Behavior
FAT date fields encode year since 1980, month, and day. FAT time fields encode hour, minute, and two-second units. The optional hundredths byte stores second parity and hundredths.

`timespec2fattime()` optionally adjusts by `utc_offset()`, emits hundredths, packs time fields, clamps pre-1980 dates to 1980-01-01, handles leap-year cycles, and corrects the non-leap year 2100. `fattime2timespec()` unpacks fields, reconstructs day count using `daytab`, applies the 2100 correction in reverse, adds the 1970-to-1980 offset, and optionally applies local timezone offset.

## Research Notes
The implementation avoids per-year loops by using four-year cycle tables, but FAT's range through 2107 requires special handling because 2100 breaks the simple every-four-years rule.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_fattime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_filter.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_filter.c

## Purpose
Implements rolling time-window min/max filters for 64-bit values and smaller 32-bit variants.

## Key Elements
- Setup/reset: `setup_time_filter()`, `setup_time_filter_small()`, `reset_time()`, `reset_time_small()`.
- Apply functions: `apply_filter_min()`, `apply_filter_max()`, and `_small` variants.
- Maintenance helpers: `check_update_times*()`, `tick_filter_clock*()`, `forward_filter_clock*()`.
- Manual adjustment: `filter_reduce_by*()`, `filter_increase_by*()`.

## Behavior
A filter maintains `NUM_FILTER_ENTRIES` value/time slots. Setup validates min/max type and time length, then initializes entries to either the maximum sentinel for min filters or zero for max filters.

Applying a new min or max updates all slots if the new value is better than the current best, updates a suffix of slots if it is better than later entries, and then ages entries using fractional time limits across the window. Clock ticking ages entries without a new measurement, but preserves the oldest worst value rather than replacing it with a synthetic zero. Manual increase/reduce helpers rewrite all slots to the adjusted current value and timestamp.

## Research Notes
The filter does not own a clock source. Callers provide `now` in arbitrary units, making this a reusable network/timing primitive rather than a wall-clock API.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_filter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_firmware.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_firmware.c

## Purpose
Implements the kernel firmware image registry, firmware lookup/autoloading, direct binary firmware file loading, reference counting, and unload handling.

## Key Elements
- Internal wrapper: `struct priv_fw`.
- Public registry APIs: `firmware_register()`, `firmware_unregister()`, `firmware_get()`, `firmware_get_flags()`, `firmware_put()`.
- Global table: `firmware_table`.
- Synchronization: `firmware_mtx`.
- Taskqueue: `firmware_tq`.
- Autoload task: `loadimage()`.
- Unload task: `unloadentry()`.
- Direct file loader: `try_binary_file()`.
- Loader-preloaded firmware import: `firmware_binary_files()`.
- Module glue: `firmware_modevent()`.

## Behavior
Firmware images are registered by name with data pointer, size, version, and optional parent image. Children hold references on parent images when used. Lookup is case-insensitive and can match absolute firmware paths by trailing component.

If `firmware_get_flags()` cannot find an image, privileged callers at securelevel 0 may trigger module autoload on the firmware taskqueue. If module loading fails, it tries `/boot/firmware/<imagename>` subject to `debug.firmware_max_size`. Successful direct file loads are registered with `FW_BINARY`.

`firmware_put()` decrements references and, when requested with `FIRMWARE_UNLOAD`, schedules unload work for autoloaded images. Binary firmware is freed directly; kld-backed firmware is released through the linker and expected to unregister on module unload.

## Research Notes
Loading is bounced to a taskqueue because linker and vnode I/O need a safe thread context and directory state. The mountroot event sets up taskqueue directory context once root is mounted.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_firmware.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_gtaskqueue.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_gtaskqueue.c

## Purpose
Implements group taskqueues and taskqgroups, used for CPU-distributed deferred work such as softirq-style processing.

## Key Elements
- Queue object: `struct gtaskqueue`.
- Active task tracking: `struct gtaskqueue_busy`.
- Defined group: `TASKQGROUP_DEFINE(softirq, mp_ncpus, 1)`.
- Enqueue/cancel/drain: `grouptaskqueue_enqueue()`, `gtaskqueue_cancel()`, `gtaskqueue_drain()`, `gtaskqueue_drain_all()`.
- Blocking: `grouptask_block()`, `grouptask_unblock()`, `gtaskqueue_block()`, `gtaskqueue_unblock()`.
- Worker loop: `gtaskqueue_thread_loop()`, `gtaskqueue_run_locked()`.
- Taskqgroup APIs: `taskqgroup_create()`, `taskqgroup_attach()`, `taskqgroup_attach_cpu()`, `taskqgroup_detach()`, `taskqgroup_bind()`, `taskqgroup_drain_all()`.

## Behavior
A `gtaskqueue` holds pending tasks in an STAILQ and running tasks in an active list. Enqueue refuses already queued tasks or `TASK_NOENQUEUE` tasks. Workers pull tasks, clear `TASK_ENQUEUED`, record active sequence numbers, run callbacks, and wake drainers.

Drain-all uses a high-priority barrier task to wait until currently queued tasks have started, then waits for active tasks with sequence numbers from before the drain. Network tasks are run inside `NET_EPOCH` while consecutive net tasks continue.

Taskqgroups create one fast queue per selected CPU. Attach chooses the least-loaded queue, preferring one without the same uniqueness token, and optionally binds device interrupts to the queue CPU.

## Research Notes
The group placement logic balances work while avoiding multiple queues for the same uniqueness key when possible. The queue worker can switch in and out of net epoch mode based on task flags.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_gtaskqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_hash.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_hash.c

## Purpose
Provides generic hash table allocation and teardown helpers for multiple queue-head types and optional per-bucket lock types.

## Key Elements
- Core allocator: `hashalloc()`.
- Core free path: `hashfree()`.
- Compatibility helpers: `hashinit_flags()`, `hashinit()`, `hashdestroy()`.
- Prime-size helpers: `phashinit_flags()`, `phashinit()`.
- Shape calculator: `hashalloc_sizes()`.
- Static padding assertions for queue-head plus lock layouts.

## Behavior
`hashalloc()` chooses either a power-of-two bucket count or a prime count from a fixed table. It computes each bucket header size from requested queue head and lock type, honors caller-provided `hdrsize`, allocates the table, initializes each queue head, initializes requested locks, and optionally runs a caller constructor per bucket.

Supported heads include LIST, CK_LIST, SLIST, CK_SLIST, STAILQ, CK_STAILQ, and TAILQ. Supported locks include none, mutex, rwlock, sx, rmlock, and rmslock.

`hashfree()` optionally runs destructors, asserts buckets are empty under `INVARIANTS`, destroys per-bucket locks, and frees the backing memory. Legacy helpers build `struct hashalloc_args` for common power-of-two or prime hash tables.

## Research Notes
The file is infrastructure for many kernel hash tables. The `_Static_assert` checks are important because callers may rely on predictable head-plus-lock packing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_hints.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_hints.c

## Purpose
Implements kernel resource hint lookup, merging static hints into the dynamic environment and exposing typed query helpers for device configuration hints.

## Key Elements
- Static hint merge: `static_hints_to_env()`.
- Environment search backend: `res_find()`.
- High-level search: `resource_find()`.
- Typed accessors: `resource_int_value()`, `resource_long_value()`, `resource_string_value()`.
- Iterators: `resource_find_match()`, `resource_find_dev()`.
- Helpers: `resource_disabled()`, `resource_unset_value()`.

## Behavior
At `SI_SUB_KMEM + 1`, static hints are copied into the dynamic kernel environment unless an overriding value already exists. Before that merge, lookup falls back through machine-dependent environment, static environment, then `static_hints`; after the merge, dynamic environment is authoritative.

Hints must match the format `hint.<name>.<unit>.<resname>=<value>`. `resource_find()` first searches exact units, then wildcard unit `-1`. It can filter by device name, unit, resource name, and value, and can return non-null-terminated name/resource spans or value pointers. Invalid hint strings are reported and mutated from `hint.` to `Hint.` to avoid repeated parsing.

Typed accessors parse integer or long values with `strtoul`, return strings by pointer, and report `EFTYPE` on malformed values.

## Research Notes
The static buffer in `resource_string_copy()` makes iterator results convenient but not generally reentrant. Dynamic environment traversal is protected by `kenv_lock`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_hints.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_intr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_intr.c

## Purpose
Implements FreeBSD's new-style interrupt framework: interrupt controller registration, interrupt source registration, resource-to-source mapping, activation/setup/teardown, MSI/MSI-X support, counters, CPU binding, IPI support, and DDB inspection.

## Key Elements
- Root controller slots: `intr_irq_roots`.
- Controller registry: `struct intr_pic`, `pic_list`.
- Interrupt sources: global `irq_sources`, `intr_isrc_register()`, `intr_isrc_deregister()`.
- Dispatch: `intr_irq_handler()`, `intr_isrc_dispatch()`, `intr_child_irq_handler()`.
- Resource operations: `intr_activate_irq()`, `intr_deactivate_irq()`, `intr_setup_irq()`, `intr_teardown_irq()`, `intr_describe_irq()`.
- CPU binding: `intr_bind_irq()`, `intr_irq_next_cpu()`, SMP shuffle.
- MSI/MSI-X: `intr_msi_register()`, `intr_alloc_msi()`, `intr_release_msi()`, `intr_alloc_msix()`, `intr_release_msix()`, `intr_map_msi()`.
- Mapping table: `intr_map_irq()`, `intr_unmap_irq()`, `intr_map_clone_irq()`.
- SMP IPI support: `intr_ipi_pic_register()`, `intr_ipi_setup()`, `intr_ipi_send()`, `intr_ipi_dispatch()`.
- DDB command: `show irqs`.

## Behavior
Initialization allocates interrupt counters/names, a bitmap for counter allocation, and the IRQ source table. Non-IPI interrupt sources get two counters: handled and stray. Dispatch increments the handled counter, invokes either a solo filter or MI `intr_event`, and increments the stray counter on failure.

PICs and MSI controllers are registered in a shared controller list with type flags. Root PICs claim a root slot with a low-level filter. Interrupt resources are mapped through `intr_map_irq()`, resolved through the PIC or MSI map data, activated by `PIC_ACTIVATE_INTR`, and then set up with event handlers and PIC enable/setup calls.

MSI allocation asks the MSI controller for interrupt sources, attaches optional IOMMU domains, creates MSI map data, and returns framework IRQ resource IDs. Mapping MSI vectors calls `MSI_MAP_MSI()` and translates MSI addresses through IOMMU when present.

## Research Notes
There are two tables with different meanings: `irq_sources` maps framework IRQ source numbers to `intr_irqsrc`, while `irq_map` maps bus resource IDs to PIC/MSI map data and active sources. The map table is fixed at `2 * intr_nirq` and currently panics rather than expanding.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_intr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_kdb.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_kdb.c

## Purpose
Implements the machine-independent kernel debugger interface: backend selection, sysctl triggers, break-sequence handling, debugger entry/trap routing, backtraces, and thread enumeration helpers.

## Key Elements
- Global state: `kdb_active`, `kdb_dbbe`, `kdb_thread`, `kdb_frame`, `kdb_why`.
- Backend linker set: `kdb_dbbe_set`.
- Null backend: `KDB_BACKEND(null, ...)`.
- Sysctls under `debug.kdb`: available/current/enter/panic/panic_str/trap/trap_code/stack_overflow and break toggles.
- Entry points: `kdb_enter()`, `kdb_trap()`, `kdb_init()`.
- Break handling: `kdb_break()`, `kdb_alt_break()`, `kdb_alt_break_gdb()`.
- Backtraces: `kdb_backtrace()`, `kdb_backtrace_thread()`.
- Backend selection: `kdb_dbbe_select()`.
- Thread helpers: `kdb_thr_first()`, `kdb_thr_next()`, `kdb_thr_lookup()`, `kdb_thr_select()`, `kdb_thr_ctx()`.

## Behavior
`kdb_init()` initializes every backend, selects the highest-priority active backend, and reports available/current backends. Sysctls allow backend selection, debugger entry, deliberate panic, deliberate data/code faults, and stack overflow testing.

Break handling supports direct break-to-debugger and an alternate console sequence: carriage return, tilde, then control-B for debugger, control-P for panic, or control-R for reboot. The dcons-specific variant can force the gdb backend.

`kdb_trap()` disables interrupts, stops other CPUs when needed, marks the scheduler stopped, captures trapframe and PCB context, selects the current thread, grabs the console, invokes the selected backend trap method, supports backend switching, then restores CPUs and interrupt state.

## Research Notes
Debugger entry is gated by securelevel and MAC policy in `kdb_backend_permitted()`. Reentry uses a saved jump buffer so nested debugger faults can recover through `kdb_reenter()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_kdb.c -->