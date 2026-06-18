# Group Research: group_1425_openzfs_sources_cow_pools_openzfs_module_os_freebsd_zfs_zio_crypt_c_32ae8481f549

Scope: `Docs/research_subset_a.md`; all listed files are under `sources/cow-pools/openzfs`, which is included in subset A. I read every listed source file completely.

This group covers the FreeBSD OpenZFS ZIO encryption and zvol OS integration paths plus Linux SPL compatibility implementations for condition variables, credentials, errors, module initialization, kmem, kmem caches, kstats, math helpers, proc/sysctl plumbing, procfs list iteration, and shrinker registration.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zio_crypt.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zio_crypt.c

Read completely: 1813 lines.

This is the FreeBSD/OpenCrypto implementation of ZFS encryption parameter handling, authenticated encryption, wrapping/unwrapping dataset keys, block pointer salt/IV/MAC encoding, and authentication checksums for encrypted datasets.

Key responsibilities:
- Defines the supported encryption table for AES-CCM and AES-GCM key sizes, along with `inherit`, `on`, and `off` pseudo-values.
- Creates, unwraps, wraps, rotates, and destroys `zio_crypt_key_t` state, including master key data, HMAC key data, current HKDF-derived encryption key, salt, key GUID, and FreeBSD crypto sessions.
- Enforces salt rotation after `zfs_key_max_salt_uses` to bound IV/key reuse risk.
- Generates random IVs for normal encrypted writes and deterministic HMAC-derived salt/IV pairs for encrypted dedup.
- Encodes/decodes salt, IV, and MAC fields into block pointers and ZIL headers with explicit byte-swap handling.
- Computes HMACs for objset, dnode, indirect-block, and unencrypted authenticated metadata.
- Builds FreeBSD `zfs_uio_t`/`struct uio` layouts for normal data, ZIL blocks, and dnode blocks, then invokes `freebsd_crypt_uio()`.

Important implementation details:
- The top comment is essential design documentation for on-disk encryption: IV storage in DVA[2]/`blk_fill`, salt in DVA[2], MAC in the upper checksum words, object HMACs, ZIL plaintext/AAD exceptions, dnode bonus-buffer encryption, objset portable/local MACs, and dedup-derived IV/salt.
- `zio_crypt_key_init()` generates key GUID, master key, HMAC key, salt, derives `zk_current_keydata` through HKDF-SHA512, initializes `zk_current_key`, and opens an OpenCrypto session. The unwrap path rebuilds the same state from encrypted key material and generates a fresh salt.
- `zio_do_crypt_uio_opencrypto()` maps OpenCrypto errors to `EIO` on encryption and `ECKSUM` on decryption/authentication failure.
- FreeBSD OpenCrypto uses one in/out buffer, so key wrapping and data encryption copy plaintext/ciphertext into the target buffer and arrange AAD before encrypted iovecs.
- `zio_crypt_bp_zero_nonportable_blkprop()` defines which block pointer properties participate in portable MACs and preserves compatibility with version 0 crypt keys.
- ZIL handling encrypts sensitive record payloads but leaves the chain header and write/clone block pointers as AAD.
- Dnode handling leaves the core dnode and block pointers plaintext/AAD, encrypting only encrypted bonus buffers.
- `zio_do_crypt_data()` selects either the current cached key/session or a temporary HKDF-derived key when decrypting blocks with an older salt.

Dependencies and interactions:
- Depends on DMU, dnode, objset, ZIL, ABD, SHA2/HMAC, HKDF, FreeBSD OpenCrypto glue, and ZFS block pointer macros.
- Called by the ZIO encryption pipeline to transform ABDs and linear buffers.
- Objset/dnode authentication must match raw send/receive portability rules, so this file is tightly coupled to on-disk format compatibility.

Reliability/security notes:
- Cryptographic correctness depends on never reusing salt/IV pairs for non-dedup writes and on preserving exact AAD/MAC field normalization across byte orders.
- Several paths intentionally support legacy key version 0 for read-only import or rewrap scenarios.
- Error cleanup zeroes temporary key material and frees uio/auth buffers. The `zio_crypt_key_init()` HMAC `ck_data` assignment differs from the unwrap path and is worth verifying against the corresponding struct definition/upstream when auditing this copy.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zio_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zvol_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zvol_os.c

Read completely: 1647 lines.

This is the FreeBSD zvol OS layer. It exposes ZFS volumes as either GEOM providers (`volmode=geom`) or character devices (`volmode=dev`) and bridges FreeBSD I/O, ioctl, open/close, kqueue, resize, rename, and destruction events to the common OpenZFS zvol core.

Key responsibilities:
- Defines FreeBSD-specific `zvol_state_os`, with a union for cdev state or GEOM provider state plus open/removal interlock flags.
- Registers the `zvol` character device switch and the `ZFS::ZVOL` GEOM class.
- Implements GEOM `open`, `close`, `access`, `BIO_GETATTR`, and bio strategy dispatch.
- Implements cdev open/close/read/write/ioctl/strategy/kqueue filtering.
- Performs zvol read/write/delete/flush by taking `zv_suspend_lock`, range locks, DMU transactions, ZIL logging, and optional `zil_commit()`.
- Creates, renames, resizes, removes, and frees FreeBSD device nodes/providers for zvol minors.

Important implementation details:
- `zpool_on_zvol` is a dangerous sysctl that controls whether zvols may be used recursively as pool vdevs. GEOM probing normally rejects zvols during ZFS vdev probe to avoid namespace-lock deadlocks.
- First open and last close carefully acquire `zv_suspend_lock` before `zv_state_lock`; retry paths drop locks and yield to avoid lock inversion with `spa_namespace_lock`.
- GEOM mode counts access deltas from `acr/acw/ace`, while cdev mode increments/decrements a single open count.
- `zvol_strategy_impl()` handles `BIO_READ`, `BIO_WRITE`, `BIO_FLUSH`, and `BIO_DELETE`. It chunks data by `zvol_maxphys`, maps checksum errors to `EIO`, updates dataset kstats, and commits the ZIL when synchronous semantics require it.
- Asynchronous GEOM/cdev bio handling hashes `(zv, curcpu, offset)` to a zvol taskq, while sync-capable contexts may execute inline.
- cdev ioctl supports sector/media size, flush, delete/unmap, stripe attributes, GEOM-style attributes, and `FIOSEEKHOLE`/`FIOSEEKDATA`.
- `zvol_ensure_zilog()` lazily opens the ZIL on first write and upgrades/downgrades the suspend lock to protect `zv_zilog`.
- `zvol_os_create_minor()` temporarily owns the objset read-only, reads volume metadata, allocates the OS device state, replays/destroys the ZIL if writable, prefetches beginning/end ranges, disowns the objset, then inserts the zvol globally.

Dependencies and interactions:
- Bridges common zvol code with FreeBSD GEOM, cdev, bio, kqueue, sysctl, DMU, ZIL, SPA namespace locking, dataset kstats, and range locks.
- Common zvol lifecycle functions such as `zvol_first_open()`, `zvol_last_close()`, `zvol_insert()`, `zvol_find_by_name_hash()`, and `zvol_fini_impl()` are assumed external.

Reliability/security notes:
- The most delicate code is lock ordering across GEOM topology, zvol state, suspend locks, and SPA namespace locks.
- Removal waits for in-progress opens (`zso_opening`) and clears provider/device backpointers before destroying OS-visible nodes.
- Write/open checks enforce readonly state and incompatible encryption version restrictions before allowing writable GEOM opens.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zvol_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-condvar.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-condvar.c

Read completely: 465 lines.

This implements Solaris-style condition variables for the Linux SPL using Linux wait queues, scheduler states, atomic waiter/reference counters, and high-resolution timeout support.

Key responsibilities:
- Initializes and destroys `kcondvar_t` objects.
- Implements uninterruptible, interruptible, I/O, idle, timed, and high-resolution condition waits.
- Implements signal and broadcast wakeups.
- Exposes the tunable `spl_schedule_hrtimeout_slack_us`, capped at 1000 microseconds.

Important implementation details:
- Each condvar tracks `cv_magic`, `cv_event`, `cv_destroy`, `cv_waiters`, `cv_refs`, and a debug `cv_mutex`.
- Wait paths increment references, assert all waiters use the same mutex, call `prepare_to_wait_exclusive()`, drop the mutex, schedule, finish the wait, decrement waiter/ref counts, and reacquire the mutex.
- Destruction marks `CV_DESTROY`, drops the initial ref, and waits until no refs, no waiters, and no active waitqueue entries remain.
- Timed jiffies waits return `1` for wake before timeout and `-1` for timeout; signal variants return `0` when a signal is pending.
- High-resolution waits use `schedule_hrtimeout_range()` with configured slack and support relative or absolute Illumos-style flags.
- Idle waits block all signals around interruptible sleep to emulate idle wait semantics.

Dependencies and interactions:
- Used by SPL/ZFS code expecting Illumos `cv_*` semantics over Linux scheduler primitives.
- Exports all public condition variable entry points used by other OpenZFS modules.

Reliability notes:
- The `cv_mutex` tracking is intentionally best-effort and racy only for debug validation.
- The jiffies timed wait code explicitly notes it does not handle jiffies wrap properly.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-condvar.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-cred.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-cred.c

Read completely: 151 lines.

This is the Linux SPL credential compatibility layer. It maps Solaris/OpenZFS credential helpers onto Linux `cred`, `group_info`, kuid/kgid, and idmap/user-namespace primitives.

Key responsibilities:
- Reference count credentials with `crhold()` and `crfree()`.
- Return effective uid, real uid, effective gid, supplemental group count, and supplemental group array.
- Check supplemental group membership with a binary search over Linux group info.
- Return the initial idmap abstraction as either `nop_mnt_idmap` or `init_user_ns`, depending on kernel API availability.

Important implementation details:
- `cr_groups_search()` compares converted scalar gids and assumes the Linux group list ordering used by `GROUP_AT()`.
- `crgetgroups()` returns a direct pointer into `group_info`; callers must hold a credential reference for safe use.
- UID/GID accessors use conversion macros (`KUID_TO_SUID`, `KGID_TO_SGID`, `SGID_TO_KGID`) to handle Linux namespace-aware types.

Dependencies and interactions:
- Provides exported symbols consumed by ZFS permission, ACL, and vnode/znode paths.
- The idmap helper abstracts kernel changes around inode `create` idmap support.

Reliability notes:
- The functions are thin wrappers and assume non-null, valid `cred_t` inputs.
- Group membership correctness depends on the group array being sorted as expected by Linux credentials.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-cred.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-err.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-err.c

Read completely: 124 lines.

This implements Solaris-style SPL error reporting and panic helpers on Linux.

Key responsibilities:
- Provides `spl_dumpstack()`, `spl_panic()`, `vcmn_err()`, and `cmn_err()`.
- Exposes `spl_panic_halt`, which controls whether assertion/panic paths call Linux `panic()` or only log, dump stack, and park the thread.

Important implementation details:
- `spl_panic()` strips the source filename basename, formats the panic message, logs it at emergency priority, optionally calls `panic()`, dumps the stack, then sets the current task uninterruptible and schedules forever.
- `vcmn_err()` maps `CE_IGNORE`, `CE_CONT`, `CE_NOTE`, `CE_WARN`, and `CE_PANIC` to Linux printk levels and the same optional-halt behavior.
- `cmn_err()` is a varargs wrapper around `vcmn_err()`.

Dependencies and interactions:
- Used by SPL assertion/error macros and exported for other OpenZFS modules.
- Integrates with Linux printk, `dump_stack()`, scheduler state, and module parameter handling.

Reliability notes:
- When `spl_panic_halt=0`, panic paths intentionally immobilize only the current thread for debugging instead of crashing the node.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-err.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-generic.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-generic.c

Read completely: 622 lines.

This is the Linux SPL generic module implementation. It owns module-level initialization/finalization, hostid handling, pseudo-random byte generation, Solaris DDI conversion helpers, user/kernel copy wrappers, and block-device uevent signaling.

Key responsibilities:
- Defines/export `spl_hostid` and dummy process `p0`.
- Implements `random_get_pseudo_bytes()` using per-CPU xoshiro256++ state seeded from Linux `get_random_bytes()`.
- Implements `ddi_strtol`, `ddi_strtoll`, and `ddi_strtoull` through a macro-generated parser.
- Implements `ddi_copyin()` and `ddi_copyout()` with `FKIOCTL` kernel-buffer bypass.
- Signals `KOBJ_CHANGE` uevents for block devices.
- Reads `/etc/hostid` or the configured `spl_hostid_path`, preserving Linux hostid behavior.
- Initializes/finalizes SPL subsystems in dependency order.

Important implementation details:
- Per-CPU PRNG state avoids atomic operations; comments state it is not for cryptographic-quality callers and that callers needing stronger randomness should use `random_get_bytes()`.
- Random initialization jumps the PRNG sequence per CPU to avoid practical overlap and has a fallback if Linux returns an all-zero seed.
- Hostid reading uses only the first four bytes of the file, matching glibc/coreutils behavior.
- Initialization order is: random, kmem/vmem, TSD, proc, kstat, taskq, kmem cache, zlib, zone. Failure unwinds in reverse order.
- Module metadata registers SPL as GPL with OpenZFS version strings.

Dependencies and interactions:
- Coordinates many SPL subsystems: kmem, vmem, TSD, proc, kstat, taskq, kmem cache, zlib, and zones.
- Exported helpers are used broadly by OpenZFS Linux code.

Reliability notes:
- `ddi_strtox` overflow detection is simple and based on wraparound of the accumulating value.
- `spl_signal_kobj_evt()` has compile-time failure if the kernel no longer exposes a supported way to obtain the block-device kobject.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-generic.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem-cache.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem-cache.c

Read completely: 1444 lines.

This implements the Linux SPL `kmem_cache_*` compatibility layer. It chooses between Linux slab-backed caches for smaller objects and a custom SPL virtual-memory slab implementation with per-CPU magazines for larger or explicitly kvmem-backed objects.

Key responsibilities:
- Provides cache creation, destruction, allocation, free, reaping, and introspection helpers.
- Maintains a global cache list protected by `spl_kmem_cache_sem`.
- Implements custom slabs with `spl_kmem_slab_t`, `spl_kmem_obj_t`, partial/full lists, per-CPU magazines, and emergency allocations.
- Uses Linux `kmem_cache_create_usercopy()` for caches selected as `KMC_SLAB`.
- Uses a taskq to grow custom slab caches asynchronously.

Important implementation details:
- Tunables control magazine size, target objects per slab, maximum slab size, small-object Linux slab cutoff, and number of cache worker threads.
- Custom slabs allocate a page-aligned virtual region containing slab metadata, object storage, and per-object metadata.
- Per-CPU magazines avoid taking the cache spinlock on most allocations/frees. Refill drains objects from partial slabs; free returns objects to the local CPU magazine and flushes when full.
- Empty slabs move to the tail of the partial list and are reclaimed outside the cache spinlock.
- `KM_NOSLEEP` growth can allocate emergency objects from pages, tracked in an rb-tree because they do not belong to a normal virtual slab.
- If asynchronous slab growth appears deadlocked, the cache sets `KMC_BIT_DEADLOCKED` and uses emergency objects until the grow task completes.
- Linux slab-backed caches rely on the kernel allocator and track active objects through a percpu counter for debug/proc reporting.
- Cache destruction removes the cache from the global list, cancels pending grow tasks, waits for active references, destroys magazines/slabs or Linux cache, and asserts all object/slab counters are zero.
- `spl_kmem_reap()` reaps all registered custom caches.

Dependencies and interactions:
- Depends on SPL kmem/vmem, taskq, Linux slab/page APIs, percpu counters, wait queues, rb-trees, and memory reclaim accounting.
- Statistics are consumed by `spl-proc.c` slab proc output.
- Exported symbols back Solaris `kmem_cache_create`, alloc/free, reap, and cache inspection APIs.

Reliability notes:
- Correctness depends on local IRQ disabling around magazine access, spinlock protection for slab lists/counters, and careful avoidance of freeing virtual memory while holding the cache spinlock.
- Constructors run after allocation and destructors before free; the custom slab reclaim path currently asserts object metadata but does not call per-object destructors there because destructors are run when objects are freed to the cache.
- Emergency allocation exists to preserve forward progress under memory pressure but is intentionally rare and more expensive.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem.c

Read completely: 630 lines.

This implements general SPL `kmem_*` allocation wrappers on Linux, including formatted string allocation, contiguous-vs-virtual allocation policy, optional debug accounting, and optional allocation tracking.

Key responsibilities:
- Exposes `spl_kmem_alloc_warn` and `spl_kmem_alloc_max` tunables.
- Provides `kmem_asprintf()`, `kmem_vasprintf()`, `kmem_strdup()`, and `kmem_strfree()`.
- Implements `spl_kvmalloc()` with kmalloc-first and vmalloc fallback behavior.
- Implements `spl_kmem_alloc_impl()` and `spl_kmem_free_impl()` behind public `spl_kmem_alloc()`, `spl_kmem_zalloc()`, and `spl_kmem_free()`.
- Supports optional `DEBUG_KMEM` byte accounting and `DEBUG_KMEM_TRACKING` per-allocation leak tracking.

Important implementation details:
- Large non-`KM_VMEM` allocations above `spl_kmem_alloc_warn` log a warning and stack trace.
- Non-vmem allocations above `spl_kmem_alloc_max` fail quickly; vmem allocations may use `spl_vmalloc()`.
- `KM_SLEEP` allocations loop until success unless the allocator is allowed to fail after retry flags and scheduling.
- `spl_kvmalloc()` avoids vmalloc fallback for non-reclaim allocations because the fallback can sleep.
- Debug tracking stores allocation address, size, caller function, and line in a hash/list structure, then reports leaks on module unload.

Dependencies and interactions:
- Used by almost every Linux SPL/OpenZFS subsystem that expects Illumos `kmem_alloc` semantics.
- Depends on Linux kmalloc/kvmalloc/vfree, SPL vmem, converted GFP flags, and optional debug build macros.

Reliability notes:
- The file deliberately discourages large contiguous `kmem_alloc()` usage because of Linux fragmentation and latency.
- Leak tracking is powerful but explicitly high overhead and intended for debug builds only.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-kstat.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-kstat.c

Read completely: 769 lines.

This implements Solaris-style kstats on Linux procfs under `/proc/spl/kstat`. It creates kstat objects, formats their data through `seq_file`, manages module/submodule directories, and installs/removes proc entries.

Key responsibilities:
- Defines global kstat module list and monotonically increasing kstat IDs.
- Supports raw, named, interrupt, I/O, and timer kstat types.
- Provides seq_file show/start/next/stop operations for kstat reads.
- Provides write support by invoking the kstat update callback with `KSTAT_WRITE`.
- Creates/deletes nested proc directories for kstat module paths.
- Detects some namespace collisions between file names and module directory names.
- Exports kstat create/install/delete and raw operation setup APIs.

Important implementation details:
- Raw kstats allocate a temporary buffer at read start and resize it up to `KSTAT_RAW_MAX` if raw callbacks return `ENOMEM`.
- `kstat_seq_start()` locks the kstat, refreshes it through `ks_update(KSTAT_READ)`, sets snapshot time, optionally prints headers, and then returns the record for the current position.
- `kstat_create_module()` walks slash-separated module names, creating proc directories and parent-child bookkeeping.
- Installing an entry with an existing name in the same module removes the older proc entry from visibility while leaving the older kstat object alive.
- The `dbufs` kstat is installed mode `0600`; others default to `0644`.
- Finalization asserts all kstat modules have been removed.

Dependencies and interactions:
- Depends on procfs root `proc_spl_kstat` created by `spl-proc.c`.
- Procfs-list helpers install non-kstat list files through the same `kstat_proc_entry_install()` namespace.
- Used broadly for OpenZFS observability.

Reliability notes:
- Lifetime is guarded by `kstat_module_lock` for namespace structures and per-kstat locks for data snapshots.
- The collision detection only covers particular parent/file conflicts; consumers still need consistent module/name choices.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-kstat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-math-compat.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-math-compat.c

Read completely: 275 lines.

This provides compiler/runtime 64-bit division and modulo helper symbols for 32-bit Linux platforms.

Key responsibilities:
- Implements unsigned and signed 64-bit divide/modulo helpers when `BITS_PER_LONG == 32`.
- Exports `__udivdi3`, `__divdi3`, `__umoddi3`, `__moddi3`, `__udivmoddi4`, and `__divmoddi4`.
- Provides ARM EABI wrappers `__aeabi_uldivmod` and `__aeabi_ldivmod` on 32-bit ARM.

Important implementation details:
- The unsigned division algorithm is based on Hacker's Delight double-word division and avoids Linux `div64_u64()` because older kernels could return incorrect results.
- 32-bit divisor cases use `do_div()` directly or a grade-school two-half quotient path.
- 64-bit divisor cases normalize the divisor, estimate the quotient, and correct it if needed.
- Signed helpers operate by dividing absolute values and restoring quotient/remainder signs.
- ARM EABI helpers marshal quotient and remainder into `r0-r3` as required by the ABI.

Dependencies and interactions:
- Only compiled on 32-bit long platforms.
- Satisfies compiler-emitted helper references from other OpenZFS/SPL code using 64-bit arithmetic.

Reliability notes:
- This is low-level arithmetic infrastructure; divide-by-zero behavior is not explicitly guarded and follows helper/CPU expectations.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-math-compat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-proc.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-proc.c

Read completely: 532 lines.

This implements SPL procfs and sysctl setup on Linux. It creates `/proc/spl`, `/proc/spl/kmem/slab`, `/proc/spl/kstat`, and `/proc/sys/kernel/spl` sysctl entries for hostid, git revision, and kmem/slab statistics.

Key responsibilities:
- Registers sysctl tables, with compatibility for old `register_sysctl_table()` and newer `register_sysctl_sz()` APIs.
- Creates proc directories and the slab seq_file.
- Implements proc handlers for debug kmem usage, aggregated slab statistics, and hostid reads/writes.
- Provides slab cache reporting by iterating `spl_kmem_cache_list`.
- Cleans up proc and sysctl entries on failure or module unload.

Important implementation details:
- `proc_doslab()` sums selected cache fields across caches matching `KMC_KVMEM` and total/alloc/max masks.
- `proc_dohostid()` prints hostid as hex without a `0x` prefix and parses writes the same way to preserve existing behavior.
- The slab seq_file prints a header and then one line per cache. Linux slab-backed caches report active-object accounting only; custom kvmem slabs report slab/object/emergency/deadlock statistics.
- The Linux 6.6/6.11 sysctl sentinel compatibility block keeps sentinel-terminated arrays for older kernels but registers size-minus-one when `register_sysctl_sz()` is available.
- `spl_proc_cleanup()` removes proc entries and unregisters sysctl tables, and is reused for partial init failure cleanup.

Dependencies and interactions:
- Depends on `spl-kmem-cache.c` global cache list/stat fields and on `spl-generic.c` hostid state.
- Creates `proc_spl_kstat`, which `spl-kstat.c` uses as the kstat namespace root.

Reliability notes:
- Proc/sysctl init has multiple failure points and central cleanup; teardown assumes entries may or may not have been created.
- Some proc handlers ignore writes by consuming the write length without changing read-only aggregate values.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-proc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-procfs-list.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-procfs-list.c

Read completely: 285 lines.

This implements `procfs_list_t`, a scalable wrapper for exposing SPL linked lists through procfs `seq_file` entries under the kstat namespace.

Key responsibilities:
- Provides per-open cursors to avoid quadratic `seq_list_start()` rescans on large lists.
- Supports optional header, row show, and clear callbacks.
- Installs/uninstalls proc entries through the kstat proc namespace.
- Initializes, destroys, and appends nodes to wrapped lists.

Important implementation details:
- Each list node embeds a `procfs_list_node_t` at a caller-provided offset; the helper stores a monotonically increasing node ID there.
- The per-open cursor caches the last node and position. Reads can resume from the cached node or advance to the next node without walking from the head.
- If entries have been dropped from the head and the cached node is stale, `start()` returns `-EIO` to prevent reading removed entries.
- Position `0` is reserved for `SEQ_START_TOKEN`, so `pl_next_id` starts at 1.
- Writes call the optional clear callback and otherwise just return the write length.

Dependencies and interactions:
- Uses SPL lists/mutexes and Linux procfs/seq_file.
- Uses `kstat_proc_entry_install()` and `kstat_proc_entry_delete()` from `spl-kstat.c`.

Reliability notes:
- The design assumes callers add only through `procfs_list_add()` and remove only from the head if they manipulate the underlying list directly.
- Callers must hold `pl_lock` when adding nodes.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-procfs-list.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-shrinker.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-shrinker.c

Read completely: 78 lines.

This is a compatibility wrapper for registering and unregistering Linux shrinkers from SPL/OpenZFS code.

Key responsibilities:
- Allocates or receives a shrinker object depending on kernel API availability.
- Assigns count and scan callbacks plus seek cost.
- Registers the shrinker with the correct kernel API variant.
- Unregisters/frees the shrinker with the matching API.

Important implementation details:
- For kernels with `HAVE_SHRINKER_REGISTER`, `shrinker_alloc()` allocates the object and `shrinker_free()` unregisters/frees it.
- For older kernels, SPL allocates a `struct shrinker` with `kmem_zalloc()`, calls either `register_shrinker(shrinker, name)` or `register_shrinker(shrinker)`, then unregisters and `kmem_free()`s it.

Dependencies and interactions:
- Used by OpenZFS components that need memory reclaim callbacks while hiding Linux shrinker API churn.
- Depends on SPL kmem allocation and kernel feature macros.

Reliability notes:
- The wrapper returns `NULL` if allocation fails; callers must handle missing shrinker registration.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-shrinker.c -->