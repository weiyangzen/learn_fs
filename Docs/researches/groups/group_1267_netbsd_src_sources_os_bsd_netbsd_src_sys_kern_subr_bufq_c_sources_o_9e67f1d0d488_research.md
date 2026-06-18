# Group Research: group_1267_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_subr_bufq_c_sources_o_9e67f1d0d488

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_bufq.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_bufq.c

## Summary
Implements the machine-independent buffer queue strategy registry and wrapper API used by disk/block drivers to allocate, operate, inspect, drain, move, and destroy `struct bufq_state` queues.

## Main Responsibilities
- Maintains the global `bufq_strat_list` protected by `bufq_mutex`.
- Registers and unregisters `struct bufq_strat` implementations, tracking per-strategy references.
- Selects a queue strategy by exact name or highest priority and can autoload `bufq_<strategy>` modules.
- Provides generic wrappers for queue put/get/peek/cancel/drain/free/move.
- Exposes `kern.bufq.strategies` sysctl output listing registered strategies.

## Important Behavior
`bufq_alloc()` normalizes sort flags, refuses impossible sort modes, autoloads missing named strategies unless the module generation did not change, and falls back to the best priority strategy unless `BUFQ_EXACT` requires `ENOENT`.

`bufq_free()` asserts the queue is empty, calls the strategy finalizer, decrements the strategy refcount, and frees the state. `bufq_drain()` completes all queued buffers with `EIO`.

## Dependencies
Uses `sys/bufq_impl.h` strategy hooks, `struct buf`, module autoloading, `kmem`, `sysctl_createv`, and `copyout` for sysctl string construction.

## Risks
Strategy unload safety depends on `bs_refcnt` being updated only through `bufq_alloc()`/`bufq_free()`. Sysctl output walks the strategy list without taking `bufq_mutex`, so it assumes registration churn is externally benign for this diagnostic path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_bufq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_callback.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_callback.c

## Summary
Implements a small round-robin callback chain abstraction with registration, unregistration, and serialized run tracking.

## Main Responsibilities
- Initializes and destroys `struct callback_head` lock, condition variable, queue, and counters.
- Registers callback entries with function/object pairs.
- Unregisters callbacks after waiting for active runs to finish.
- Runs one round over the current entries, stopping when a callback returns something other than `CALLBACK_CHAIN_CONTINUE`.

## Important Behavior
`callback_run_roundrobin()` snapshots `ch_nentries` after marking the chain running, then invokes at most that many callbacks. `ch_next` preserves round-robin position between runs and is adjusted if an unregister removes the next entry.

## Dependencies
Uses `TAILQ`, mutexes, condition variables, and callback structures from `sys/callback.h`.

## Risks
Callbacks run without holding `ch_lock`; unregistration waits for `ch_running` to drop to zero. Callers must ensure callback entries remain valid until `callback_unregister()` returns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_callback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_copy.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_copy.c

## Summary
Provides generic `uio` transfer helpers, arbitrary-process/vmspace copy helpers, ioctl kernel/user copy selection, and generic user-space fetch/store/CAS wrappers.

## Main Responsibilities
- Implements `uiomove()`, `uiopeek()`, `uioskip()`, `ureadc()`, and `uiomove_frombuf()`.
- Copies data to/from arbitrary `vmspace` or `proc` objects through direct copy or `uvm_io()`.
- Supports `FKIOCTL` paths via `ioctl_copyin()`/`ioctl_copyout()`.
- Implements generic `_ucas_32()` and `_ucas_64()` when the port does not provide full user CAS.
- Exposes checked `ucas_*`, `ufetch_*`, and `ustore_*` entry points plus legacy aliases.

## Important Behavior
`uiomove()` mutates the caller's `uio` and iovecs while `uiopeek()` performs the same transfer without advancing the original `uio`. Both use `copyin_vmspace()`/`copyout_vmspace()` and call `preempt_point()` for user vmspaces.

Generic user CAS wires the target user page before entering the critical section. On MP platforms without native MP user CAS, it uses a CPU-wide IPI gate, `cpu_lock`, and `splhigh()` to keep other CPUs from racing the fetch/store pair.

## Dependencies
Uses UVM vmspace references, process lookup, `uvm_io()`, `uvm_vslock()`, IPI/cpu locking for generic MP CAS, and machine-provided low-level `_ufetch_*`/`_ustore_*` primitives.

## Risks
The arbitrary-vmspace copy path depends on correct `uio_rw` direction conventions for `uvm_io()`. The generic CAS fallback is intentionally heavyweight and correctness depends on page wiring and the IPI gate memory-ordering protocol.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_copy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_cprng.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_cprng.c

## Summary
Implements NetBSD's per-CPU strong CPRNG instances backed by NIST Hash_DRBG and reseeded from the kernel entropy subsystem.

## Main Responsibilities
- Initializes `kern_cprng` and `user_cprng` with different maximum IPLs.
- Creates `kern.urandom` and `kern.arandom` sysctl nodes.
- Allocates per-CPU DRBG and reseed event counter state.
- Reseeds per-CPU DRBGs when the entropy epoch changes or generation requires reseed.
- Provides `cprng_strong()`, `cprng_strong32()`, and `cprng_strong64()`.

## Important Behavior
Per-CPU DRBG state is allocated separately from the `percpu` object because percpu storage may move without zeroing. `cprng_strong()` raises to the instance IPL and holds a percpu reference while generating, but drops both around `entropy_extract()` because entropy extraction may sleep.

`kern.arandom` clamps sysctl reads to 256 bytes and clears the temporary buffer after copying. `kern.urandom` similarly clears the stack integer after sysctl lookup.

## Dependencies
Uses `crypto/nist_hash_drbg`, `percpu`, `entropy_epoch()`/`entropy_extract()`, `evcnt`, sysctl, IPL control, and explicit memory clearing.

## Risks
Callers must obey the context constraints: not hard interrupt context, request length no more than `CPRNG_MAX_LEN`, and legacy `flags == 0`. Reseeding may race benignly across CPUs, intentionally trading extra reseeds for simpler synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_cprng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_cpu.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_cpu.c

## Summary
Provides shared CPU bookkeeping for MI and rump code, including CPU topology construction, CPU model storage, stable-current-CPU checks, and per-CPU counter aggregation.

## Main Responsibilities
- Initializes `cpu_lock`, attached/running CPU sets, and early fake topology.
- Stores and returns the global CPU model string.
- Determines whether code is in soft interrupt context or whether `curcpu()` is stable.
- Records package/core/SMT/NUMA IDs and relative slow/fast CPU classification.
- Builds circular sibling lists for core, package, and package-first relationships.
- Maintains per-CPU counters and synchronized global `cpu_counts`.

## Important Behavior
`cpu_topology_init()` validates topology uniqueness, falls back to fake topology on bogus duplicate package/core/SMT IDs, marks first SMT/core/package CPUs, and marks first-class CPUs either by fast/slow status or core-first status.

`cpu_count_sync()` sums per-CPU counters at `splvm()`, can poll only once per tick, and has a uniprocessor shortcut before MP is online.

## Dependencies
Uses `struct cpu_info`, scheduler flags, `CPU_INFO_FOREACH`, `kcpuset`, atomic tick polling, IPL control, and scheduler/preemption state.

## Risks
Topology building assumes every CPU has a coherent circular sibling list after fallback or MD-provided data. Counter synchronization is intentionally approximate when polling and is sensitive to `CPU_COUNT_MAX` layout assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_cpufreq.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_cpufreq.c

## Summary
Implements the generic CPU frequency backend registry, state validation, latency measurement, suspend/resume preservation, and cross-call based get/set operations.

## Main Responsibilities
- Initializes a singleton `struct cpufreq` backend protected by `cpufreq_lock`.
- Registers one backend after boot, validating callbacks and frequency states.
- Filters state entries to descending, valid values and measures transition latency.
- Sets all CPUs to the maximum registered frequency on registration.
- Provides backend/state/frequency query APIs and per-CPU/all-CPU setters.
- Saves minimum-frequency suspend transition and restores prior frequency on resume.

## Important Behavior
`cpufreq_register()` refuses registration while `cold`, rejects duplicate backends, drops invalid/duplicate/out-of-order states, and deregisters on validation or latency failure. All hardware callback invocations are made via `xc_unicast()` or `xc_broadcast()` and waited synchronously.

`cpufreq_get_state_raw()` performs a binary search over descending frequencies and returns the nearest state selected by the search even if the input frequency is not an exact state.

## Dependencies
Uses `sys/cpufreq.h` backend callbacks, `xcall`, `nanotime()`, `timespecsub()`, `kmem`, and a global mutex.

## Risks
Only one backend is supported. Latency sampling divides total successful time by the fixed sample count even if slow samples were skipped, so reported latency is a suitability heuristic, not a precise average.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_cpufreq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_csan.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_csan.c

## Summary
Implements NetBSD KCSAN runtime support: compiler instrumentation entry points, sampled race detection, reporting, and wrappers for memory, copy, atomic, and bus-space operations.

## Main Responsibilities
- Tracks one sampled memory access cell per CPU.
- Reports overlapping racy accesses with CPU, access type, address, size, PC, and symbol name.
- Provides `__tsan_read*`, `__tsan_write*`, range, init, and function entry/exit hooks.
- Wraps compiler-builtins for `memcpy`, `memcmp`, `memset`, `memmove`, `strcpy`, `strcmp`, and `strlen`.
- Wraps kernel copy routines to annotate kernel-side buffers.
- Generates KCSAN-aware atomic operation wrappers through macros.
- Generates KCSAN-aware bus-space multi/region read/write wrappers.

## Important Behavior
`kcsan_access()` ignores disabled or MD-unsupported addresses, compares the new access with all CPUs' sampled cells, and reports when ranges overlap and at least one non-atomic write participates. Sampling happens every `KCSAN_NACCESSES` accesses per CPU, with interrupts disabled around publishing the cell and a short MD delay.

Atomic wrappers mark accesses as atomic so atomic-vs-atomic conflicts are suppressed. Non-atomic memory and bus-space wrappers annotate the relevant source or destination buffer before invoking the underlying primitive.

## Dependencies
Uses MD hooks from `<machine/csan.h>`, `ksyms_getname()`, `pserialize`, CPU numbering, compiler TSAN ABI names, kernel atomic APIs, copy APIs, and bus-space APIs.

## Risks
Detection is probabilistic and intentionally samples, so absence of reports is not proof of race freedom. Reporting relies on lockless snapshots of other CPU cells and can report approximate PCs/ranges while prioritizing low runtime overhead.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_csan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_debug.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_debug.c

## Summary
Provides optional DEBUG-kernel allocation/free validation by tracking pointer membership in caller-supplied lists.

## Main Responsibilities
- Initializes the global freecheck lock and optional fixed pool of tracking items.
- `freecheck_out()` records that an address is checked out and panics if already present.
- `freecheck_in()` removes a checked-out address and panics or enters DDB if absent.

## Important Behavior
Tracking is enabled by setting `debug_freecheck`. The fixed pool is allocated from wired kernel memory during `debug_init()`. If the pool runs out, the code prints a one-time warning and disables effective tracking by changing `debug_freecheck`.

## Dependencies
Uses `uvm_km_alloc()`, CPU simple locks, `splvm()`, atomic swap, optional DDB, and DEBUG kernel configuration.

## Risks
The feature is deliberately expensive and not enabled by default. Once tracking slots are exhausted, further coverage is degraded.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_device.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_device.c

## Summary
Implements core `device_t` accessors, `devhandle_t` comparison/subclass/call lookup, generic device calls, and device property get/set helpers.

## Main Responsibilities
- Provides the global `root_device`.
- Implements `devhandle_is_valid()`, `devhandle_invalid()`, `devhandle_type()`, `devhandle_compare()`, and subclass helpers.
- Looks up device-call descriptors through handle implementations and system-default link sets.
- Exposes common `device_t` accessors for class, cfdata, cfdriver, cfattach, unit, xname, parent, activation, private data, properties, and handle.
- Implements generic device-call dispatch and child enumeration.
- Retrieves properties from the device property dictionary first, then platform device-call backends.
- Provides typed property length/type/encoding/data/string/bool/integer get APIs and typed set/delete APIs.

## Important Behavior
Property lookup treats `ENOENT` from the local dictionary as permission to ask the platform backend. Dictionary-backed properties are native-endian; platform-backed properties must report explicit little or big endian encoding.

String and data properties can be fetched into caller buffers or exact-sized allocated buffers. Integer helpers validate size and range; signed helpers sign-extend smaller two's-complement values before range checks.

## Dependencies
Uses autoconf device internals, device-call link sets, proplib dictionaries/objects, `kmem`, and byte-order constants.

## Risks
`device_set_private()` asserts private data is set exactly once and non-NULL. Property allocation loops can retry if backend property size changes between length query and fetch; backends must set `propsize` correctly, especially on `EFBIG`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_device.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_devsw.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_devsw.c

## Summary
Implements block and character device switch registration, lookup, name/major conversion, dynamic table expansion, detach synchronization, and wrapper methods for driver operations.

## Main Responsibilities
- Initializes `device_lock` and detach condition variable.
- Attaches block/character driver switch entries by name and major number.
- Dynamically expands `bdevsw`, `cdevsw`, and conversion tables up to `MAXDEVSW`.
- Detaches devsw entries after preventing new references and draining local references.
- Converts between names, block majors, char majors, block `dev_t`, and char `dev_t`.
- Wraps block operations: open, cancel, close, strategy, ioctl, dump, flags/type, size, discard, detached.
- Wraps character operations: open, cancel, close, read, write, ioctl, stop, tty, poll, mmap, kqfilter, discard, flags/type, detached.
- Emits SDT probes for device operation entry/return and open acquire/release events.

## Important Behavior
Dynamic attach allocates reference tables and expanded switch arrays only once, publishing them with atomic stores so readers can safely use either old or new arrays. `*_lookup_acquire()` uses pserialize and optional `localcount` references so detach can wait for in-flight opens.

`devsw_detach_locked()` verifies no autoconf device instances remain for associated drivers, clears switch entries, uses `xc_barrier()` to wait for lockless lookups to observe the removal, and drains localcounts before freeing them.

Open wrappers acquire a referenced autoconf device instance when `d_devtounit` is provided, stabilizing `device_lookup()` during driver `d_open`. Non-MPSAFE drivers are serialized with the kernel lock.

## Dependencies
Uses generated static `bdevsw0`/`cdevsw0`/`devsw_conv0` tables, `localcount`, `pserialize`, `xc_barrier`, autoconf `device_lookup_acquire()`, `config_detach_commit()`, SDT probes, and kernel locking.

## Risks
Detach safety depends on callers ensuring no open instances remain and future opens fail. Many non-open wrappers still use simple lookup without acquired localcount, matching the file's own note that opened vnode references should eventually make those checks unnecessary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_devsw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk.c

## Summary
Implements common disk support: error formatting, disk lifecycle, I/O statistics, bounds checks, disklabel conversion, disk ioctls, and disk geometry/property publication.

## Main Responsibilities
- Formats transfer errors with partition, block range, and optional CHS detail.
- Finds disks through iostat names.
- Initializes, attaches, detaches, destroys, renames, and begin-detaches `struct disk`.
- Maintains disk I/O statistics through iostat helpers.
- Bounds-checks raw media and labeled partition transfers.
- Reads sectors through a driver strategy routine.
- Converts legacy labels to ensure a usable raw partition exists.
- Handles generic disk ioctls for disk info, geometry, partition info, wedges, sector alignment, and labels.
- Canonicalizes disk geometry and exports `disk-info` property dictionaries.

## Important Behavior
`bounds_check_with_label()` rejects negative offsets, protects the on-disk label from writes unless `wlabel` is set, truncates transfers at partition end, reports EOF at exact end, and computes `b_cylinder` for queue sorting.

`disk_ioctl()` passes unknown commands through with `EPASSTHROUGH`, enforces write permission for wedge mutating operations, and returns raw partition size from disk geometry rather than disklabel partitions.

`disk_set_info()` fills missing sector size and derived sector count/cylinder fields, stores geometry in a proplib dictionary, and mirrors it into the device properties when a device is supplied.

## Dependencies
Uses `struct disk`, `disklabel`, `buf`, iostat, wedge management, proplib, disk ioctls, and kernel logging.

## Risks
Label and geometry paths retain compatibility behavior for old disklabel assumptions. Some partition block-size logic is explicitly called out as buffer-cache legacy behavior and mainly reliable for BSD FFS metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk_4bsd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk_4bsd.c

## Summary
Implements simple 4BSD-style `readdisklabel()` and `writedisklabel()` routines for ports using the basic scheme.

## Main Responsibilities
- Initializes minimal default disklabel geometry and raw partition fields before reading.
- Reads `LABELSECTOR` and scans for a valid `DISKMAGIC`/checksum disklabel.
- Writes an updated disklabel back over an existing valid on-disk label.

## Important Behavior
Read setup makes the raw partition cover `d_secperunit`, sets partition `a` to the whole raw partition as `FS_BSDFFS`, and scans the first sector at `sizeof(long)` alignment for a valid label.

Write chooses the requested partition unless that partition has nonzero offset, in which case it falls back to partition `a` if possible. It only overwrites an existing valid label and returns `ESRCH` if none is found.

## Dependencies
Uses `geteblk()`, driver strategy callbacks, `biowait()`, `brelse()`, disklabel checksum helpers, and disk partition macros.

## Risks
The writer does not create a new label if no valid label is already present. The implementation assumes the simple 4BSD sector placement model.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk_4bsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk_mbr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk_mbr.c

## Summary
Implements MBR-aware disklabel discovery and writing, including NetBSD partition labels, DOS partition import, extended partitions, protective MBR rejection, ISO/UDF fallback, and optional bad-sector table loading.

## Main Responsibilities
- Reads sectors through common disk sector helper into a reusable buffer.
- Scans primary and extended MBR partition tables.
- Detects and skips protective GPT MBRs and Ontrack DM6 DDO redirection.
- Finds NetBSD labels inside NetBSD or compatible 386BSD partitions.
- Imports MBR partitions into disklabel slots when no NetBSD label is found.
- Scans ISO/UDF Volume Recognition Sequences when neither label nor MBR data yields a label.
- Validates labels across a three-sector scan window and optionally handles endian-swapped labels.
- Writes or updates labels in NetBSD MBR partitions and/or the disk start.

## Important Behavior
`scan_mbr()` tracks extended partition bases, verifies partitions do not exceed `d_secperunit`, records whether a valid MBR exists, and stops on scan errors or found labels. Main MBR partitions are installed into `e` through `h`; extended partitions start at later slots and duplicate entries are avoided.

`validate_label()` scans for disklabel magic and checksum, converts endian-swapped labels when configured, calls `convertdisklabel()` on reads, and writes at the architecture default location if asked to create a missing label.

`scan_iso_vrs()` checks MMC sessions when available, otherwise the start of disk, and marks partition `a` as `FS_ISO9660` when ISO media is detected.

## Dependencies
Uses MBR structures, disklabel helpers, CD/MMC ioctls, UDF/ECMA identifiers, endian helpers, `geteblk()`, buffer I/O, and optional compatibility/config macros.

## Risks
MBR sector addresses are limited to 32-bit fields. Writing labels on disks with multiple NetBSD MBR partitions intentionally updates all matching partitions. The file notes possible MAXPARTITIONS compatibility issues when writing labels to disks with older eight-partition layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk_mbr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk_open.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk_open.c

## Summary
Provides helpers to open a disk device through a temporary vnode and query its size or wedge/partition identity.

## Main Responsibilities
- Maps a disk `device_t` to its block major and raw-partition `dev_t`.
- Opens a temporary block-device vnode for read-only disk inspection.
- Retrieves disk size with wedge information preferred over disklabel partition info.
- Builds `dkwedge_info` from either native wedge ioctl or partition info fallback.

## Important Behavior
`opendisk()` ignores expected open failures for missing devices, missing media, and busy devices, but logs unexpected errors. It treats `dk` wedge devices differently by using the unit directly rather than `MAKEDISKDEV(..., RAW_PART)`.

`getdisksize()` prefers `DIOCGWEDGEINFO` so large wedge sizes are not constrained by disklabel limits. It validates sector size as nonzero, power of two, not above `MAXBSIZE`, and requires nonzero sector count.

## Dependencies
Uses devsw name-to-block-major conversion, specfs `bdevvp()`, `VOP_OPEN()`, disk and wedge ioctls, `disk_find()`, and partition type naming.

## Risks
Temporary vnode opening depends on the block devsw and driver open path being usable during probing. Fallback disklabel sizes may be too small for large media, which is why wedges are queried first.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disk_open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disklabel.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disklabel.c

## Summary
Provides a generic `setdisklabel()` implementation for ports without their own implementation or for rump kernels.

## Main Responsibilities
- Validates sector size, sectors per cylinder, disklabel magic, partition count, and checksum.
- Allows invalidation with magic `0xffffffff`.
- Prevents unsafe changes to open partitions.
- Preserves internally set partition information when a new label marks an open partition as unused.
- Recomputes and installs the label checksum before replacing the old label.

## Important Behavior
For every open partition, the new label must still contain that partition, must not change its offset, and must not shrink its size. This guards mounted/open users from having their backing range moved out from under them.

## Dependencies
Uses disklabel structures, `dkcksum()`, partition open masks, and optional DEBUG diagnostics.

## Risks
The function mutates `nlp` while preserving open partition metadata and recomputing checksum, so callers should not expect the input label object to remain byte-for-byte unchanged.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_disklabel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_emul.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_emul.c

## Summary
Implements helpers for executable emulation roots and interpreter lookup.

## Main Responsibilities
- Finds and stores the emulation root vnode for an exec package.
- Resolves dynamic interpreter paths using the emulation root when available.
- Replaces any prior saved interpreter vnode on the exec package.

## Important Behavior
`emul_find_root()` is idempotent and silently leaves `ep_emul_root` unset if the emulation has no path or the path does not exist.

`emul_find_interp()` uses `TRYEMULROOT | EMULROOTSET` when an emulation root is present, and stores the resolved interpreter vnode in `ep_interp` for later loading.

## Dependencies
Uses exec package/emulation structures, pathbuf, `namei_simple_kernel()`, `namei()`, vnode references, and compat emulation root flags.

## Risks
Missing emulation roots are not memoized, so repeated lookups can retry. The interpreter lookup deliberately uses the new program's emulation root rather than the current process root context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_emul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_evcnt.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_evcnt.c

## Summary
Implements kernel event counter registration, detachment, sysctl export, and legacy interrupt counter bridging.

## Main Responsibilities
- Maintains the global `allevents` tail queue protected by `evcnt_lock`.
- Attaches static counters from the `evcnts` link set during `evcnt_init()`.
- Attaches dynamic counters with or without zeroing.
- Detaches counters and increments a generation number.
- Exports counters through `kern.evcnt` sysctl with type and nonzero filters.
- Optionally mirrors legacy `intrcnt`/`intrnames` arrays into dynamic event counters.

## Important Behavior
Sysctl export builds variable-length `evcnt_sysctl` records containing fixed fields plus group/name strings, rounded to 64-bit units. It copies out without holding `evcnt_lock`; if the generation changes during copyout, it retries up to 100 times before returning `EAGAIN`.

Kernel addresses in sysctl output are conditionally exposed through `get_expose_address(curproc)`.

## Dependencies
Uses link sets, `TAILQ`, `kmem`, sysctl, `copyout`, event counter ABI structures, and optional legacy interrupt counter symbols.

## Risks
Counters are exported as statistics only; concurrent attach/detach can force retries and eventually `EAGAIN`. Dynamic event callers must ensure the pointed-to group and name strings remain valid while attached.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_evcnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_exec_fd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_exec_fd.c

## Summary
Implements exec-time file descriptor tracing and standard-descriptor repair for privileged execs.

## Main Responsibilities
- Emits ktrace records for every open file descriptor during exec.
- Ensures descriptors 0, 1, and 2 are open by attaching `/dev/null` where needed.
- Logs a warning when setuid/setgid execution inherited closed standard descriptors.

## Important Behavior
`fd_ktrexecfd()` walks the current process descriptor table with atomic loads and records descriptor number plus file type.

`fd_checkstd()` allocates descriptors for closed stdin/stdout/stderr, opens `/dev/null` read-write, attaches vnode file operations, and asserts allocated descriptors are below 3. It logs parent uid/pid/command context for the unsafe invocation.

## Dependencies
Uses file descriptor tables, atomic descriptor table loads, `ktr_execfd()`, `fd_allocfile()`, `vn_open()`, vnode file operations, `/dev/null`, process locks, and kauth credentials.

## Risks
The repair path assumes `fd_allocfile()` returns the lowest available descriptor and asserts it is one of 0..2. Errors opening `/dev/null` abort the partially allocated file descriptor.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_exec_fd.c -->