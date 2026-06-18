# Research: subset-b-000928

This grouped report covers the requested block-layer and partition-parser files under `sources/distributed-fs/ceph-client`. Each source file section is delimited for deterministic splitting into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/fops.c -->
# sources/distributed-fs/ceph-client/block/fops.c

## Purpose
`fops.c` implements the generic block-device `struct file_operations` and default address-space operations for block special files. It is the bridge between VFS reads/writes/mmap/fsync/fallocate/ioctl/io_uring and block-device primitives such as bios, page cache invalidation, cache writeback, flushes, zeroing, and open-mode conversion.

## Important APIs, Types, and Functions
- `def_blk_fops` wires block devices into VFS: `blkdev_open`, `blkdev_release`, `blkdev_read_iter`, `blkdev_write_iter`, `blkdev_llseek`, `blkdev_fsync`, `blkdev_fallocate`, `blkdev_mmap_prepare`, `blkdev_ioctl`, `compat_blkdev_ioctl`, and `blkdev_uring_cmd`.
- `def_blk_aops` is compiled in two variants. With `CONFIG_BUFFER_HEAD`, it uses buffer-head helpers (`block_read_full_folio`, `block_write_full_folio`, `mpage_readahead`). Without buffer heads, it uses iomap helpers (`iomap_bio_read_folio`, `iomap_writepages`).
- `struct blkdev_dio` stores direct-I/O state shared by bios: original `kiocb` or sync waiter, total size, reference count, flags, and an embedded first `bio` allocated from `blkdev_dio_pool`.
- Direct-I/O helpers include `blkdev_direct_IO`, `__blkdev_direct_IO_simple`, `__blkdev_direct_IO_async`, `__blkdev_direct_IO`, `blkdev_bio_end_io`, and `blkdev_bio_end_io_async`.
- `file_to_blk_mode()` converts file flags and modes into block open flags, including historical `O_RDWR | O_WRONLY` write-ioctl behavior.

## Control Flow
Open starts in `blkdev_open()`: file flags become `BLK_OPEN_*` flags, exclusive opens set `file->private_data`, permissions are checked via `bdev_permission()`, the bdev is looked up with `blkdev_get_no_open()`, metadata and atomic-write capabilities are reflected in `f_mode`, then `bdev_open()` owns the live reference. Release delegates to `bdev_release()`.

Reads in `blkdev_read_iter()` trim the iterator at device end, optionally do direct I/O after waiting for conflicting writeback, then fall back to `filemap_read()` under the block inode shared lock. Writes in `blkdev_write_iter()` reject read-only devices, swapfile writes, NOWAIT-buffered writes, writes beyond end, and invalid atomic writes. They trim to device size, update mtime/ctime, run direct I/O when requested, and can fall back to buffered iomap writes for short direct writes.

Direct I/O is selected by mapping size and metadata needs. Small, synchronous, single-bio I/O uses `submit_bio_wait()`. Async single-bio I/O can queue `REQ_POLLED`, `REQ_NOWAIT`, `REQ_ATOMIC`, integrity metadata, write streams, and ioprio. Multi-bio I/O uses `blkdev_dio` refcounts and completion coalescing.

## State and Persistence Behavior
The file persists no independent on-disk metadata, but it mutates durable media through writes, zeroing, flushes, and fallocate. It also changes in-memory page-cache state aggressively: direct writes invalidate before and after I/O, fallocate invalidates dirty cache for deallocation/zeroing, fsync writes cached data and issues a block flush, and read/write paths coordinate with block-size changes via inode locks.

## Dependencies and Integration Points
The file depends on VFS, iomap, buffer-head or non-buffer-head address-space operations, bio allocation/submission, integrity metadata mapping, task I/O accounting, suspend hibernation checks, and block-device open/close helpers from `blk.h`. It exports no symbols itself, but `def_blk_fops`, `def_blk_aops`, and `file_to_blk_mode()` are central block-layer integration surfaces.

## Risks and Edge Cases
Alignment is strict for direct I/O and fallocate: misaligned offsets/counts return `-EINVAL`. NOWAIT support is intentionally limited when multiple bios would be needed. Completion ordering and `ki_pos` updates are split between direct-I/O helper variants, so regressions can double-advance offsets or leak `iocb->private`. Buffered paths rely on inode locks to avoid races with `set_blocksize()`. Device-size truncation, atomic-write short writes, and metadata mapping failures are high-risk behavior.

## Test Signals
Useful tests include xfstests block-device direct/buffered read-write cases, O_DIRECT alignment failures, io_uring polled direct I/O, integrity metadata I/O, write stream validation, fsync flush behavior on devices without flush support, fallocate zero/punch/write-zeroes modes, read/write at end-of-device, and lockdep runs around block-size changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/genhd.c -->
# sources/distributed-fs/ceph-client/block/genhd.c

## Purpose
`genhd.c` owns generic disk (`struct gendisk`) lifecycle, capacity publication, major-number registration, disk/partition sysfs and procfs visibility, disk statistics, uevents, dynamic device-number allocation, and teardown for block devices.

## Important APIs, Types, and Functions
- Capacity and notification: `set_capacity()`, `set_capacity_and_notify()`, `invalidate_disk()`, `set_disk_ro()`, `inc_diskseq()`.
- Registration: `__register_blkdev()`, `unregister_blkdev()`, `blk_alloc_ext_minor()`, `blk_free_ext_minor()`, `device_add_disk()`, `add_disk_fwnode()`, `del_gendisk()`.
- Disk allocation: `__alloc_disk_node()`, `__blk_alloc_disk()`, `put_disk()`.
- Partition scan and event flow: `disk_scan_partitions()`, `add_disk_final()`, `disk_uevent()`, `blk_mark_disk_dead()`.
- User visibility: sysfs attribute show/store functions, `block_class`, `disk_type`, `/proc/partitions`, `/proc/diskstats`, and optional legacy autoload functions.

## Control Flow
Drivers allocate disks through `__blk_alloc_disk()` or `__alloc_disk_node()`, which initialize biosets, backing-dev info, `part0`, the xarray partition table, cgroup state, zone resources, queue ownership, class/type, diskseq, and queue kobject. `device_add_disk()` calls `add_disk_fwnode()`, which serializes against blk-mq hardware queue updates when needed, then calls `__add_disk()`.

`__add_disk()` validates queue/fops combinations, assigns explicit or extended dev_t numbers, suppresses uevents, adds the device, allocates disk events, creates deprecated `/sys/block` links, holder/slave directories, registers the queue, registers bdi and sysfs links for visible disks, and stores a dev_t for hidden disks. `add_disk_final()` creates `part0`, scans partitions for visible disks with capacity, enables uevents, emits `KOBJ_ADD`, applies bdi limits, starts disk events, and marks `GD_ADDED`.

Teardown flows through `del_gendisk()` and `__del_gendisk()`: prevent new opens, notify filesystems, mark dead, drop partitions, remove bdi links, unregister queues, delete holder/slave dirs, remove device/sysfs links, freeze/drain queues, cancel throttled bios/work, exit rq-qos and blk-mq queue state as appropriate.

## State and Persistence Behavior
The persistent device data is elsewhere; this file manages kernel-visible state. Important mutable state includes `disk->state` bits (`GD_ADDED`, `GD_DEAD`, `GD_OWNS_QUEUE`, `GD_READ_ONLY`), capacity in `part0`, dynamic dev_t allocation in `ext_devt_ida`, major-name hash tables, partition xarray references, diskseq, sysfs/procfs exported counters, and badblocks sysfs storage via `disk->bb`.

## Dependencies and Integration Points
It integrates with block queue registration, blk-mq, rq-qos, blk-cgroup, blk-throttle, disk events, bdi, device model, sysfs/procfs, uevents, badblocks, blktrace, partition scanning, md autodetect indirectly, and optional legacy module autoload. It exports core driver-facing APIs for adding/removing disks and changing capacity/read-only state.

## Risks and Edge Cases
Device teardown ordering is delicate: bdi unregister must precede dev_t reuse, queue drain/freezing must prevent new I/O, hidden disks need valid `bd_dev` without user-visible registration, and blk-mq tag-set locks avoid hardware-queue update races. Capacity changes suppress initial/empty uevent noise. Per-cpu stat aggregation can observe transient negative inflight counts and clamps them. Major allocation is legacy and name-limited.

## Test Signals
Signals include hotplug add/remove tests, udev event diskseq correlation, partition scan/rescan races, dynamic minor exhaustion, hidden disk behavior, blk-mq queue teardown under I/O, sysfs attribute correctness, `/proc/diskstats` format, read-only uevents, capacity resize notifications, badblocks sysfs operations, and lockdep around `open_mutex` and tag-set locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/genhd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/holder.c -->
# sources/distributed-fs/ceph-client/block/holder.c

## Purpose
`holder.c` implements deprecated sysfs relationship links between a block device that is claimed as a slave and a gendisk that holds it. It is used by legacy stacking drivers such as device mapper to expose `/sys/block/<holder>/slaves/<slave>` and `/sys/block/<slave>/holders/<holder>`.

## Important APIs, Types, and Functions
- `struct bd_holder_disk` tracks one holder relationship with a list node, referenced holder directory kobject, and refcount.
- `bd_link_disk_holder()` creates the two symlinks and records/refcounts the relationship.
- `bd_unlink_disk_holder()` removes symlinks and drops the holder directory kobject when the relationship refcount reaches zero.
- `blk_holder_mutex` serializes relationship list and symlink operations.

## Control Flow
`bd_link_disk_holder()` rejects missing holder/slave directories and self-links, takes `bdev->bd_disk->open_mutex` to verify the slave disk is still live, and takes a kobject reference to survive past gendisk deletion. Under `blk_holder_mutex`, it either bumps the existing relationship refcount or allocates a `bd_holder_disk`, creates the holder-to-slave symlink, creates the slave-to-holder symlink, and links the record into `disk->slave_bdevs`. Partial creation failures unwind symlinks and references.

`bd_unlink_disk_holder()` looks up the relationship, decrements the refcount, and on zero removes both symlinks, drops the saved holder directory reference, deletes the list node, and frees the holder object.

## State and Persistence Behavior
There is no persistent disk format state. Runtime state is sysfs topology plus refcounted `bd_holder_disk` records on `disk->slave_bdevs`. Kobject references deliberately outlive `del_gendisk()` dropping the initial holder-dir reference so cleanup can still remove links safely.

## Dependencies and Integration Points
The file depends on `CONFIG_BLOCK_HOLDER_DEPRECATED` users, gendisk `slave_dir`, bdev `bd_holder_dir`, kobjects/sysfs, and block-device claiming semantics managed elsewhere. Both public functions are exported GPL-only.

## Risks and Edge Cases
Callers must already hold a valid claim and lifetime references; this file only validates obvious live-state conditions. Missing unlink calls leave stale topology until teardown. Symlink creation is two-phase and must unwind correctly. The typo in the doc comment (`calimed`) is harmless but indicates the interface is maintenance-only.

## Test Signals
Exercise stacked block devices that still call these helpers, verify sysfs links appear/disappear across repeated claims, check refcount behavior under duplicate links, run hot-unplug/teardown tests with live holders, and use lockdep/KASAN for kobject lifetime mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/holder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioctl.c -->
# sources/distributed-fs/ceph-client/block/ioctl.c

## Purpose
`ioctl.c` implements generic block-device ioctl handling, compat ioctl handling, persistent reservation commands, geometry/size/read-only/block-size controls, discard/secure erase/zeroout operations, crypto/zone delegation, and an io_uring command path for discard.

## Important APIs, Types, and Functions
- Entry points: `blkdev_ioctl()`, `compat_blkdev_ioctl()`, `blkdev_compat_ptr_ioctl()`, and `blkdev_uring_cmd()`.
- Partition mutation: `blkpg_ioctl()`, `compat_blkpg_ioctl()`, `blkpg_do_ioctl()`.
- Data modification: `blk_ioctl_discard()`, `blk_ioctl_secure_erase()`, `blk_ioctl_zeroout()`, `blkdev_cmd_discard()`.
- Persistent reservation helpers wrap `struct pr_ops`: register, reserve, release, preempt, clear, read keys, and read reservation.
- Common dispatch is centralized in `blkdev_common_ioctl()`.

## Control Flow
Native and compat ioctl entry points handle structurally incompatible commands first, then call `blkdev_common_ioctl()`. Unknown commands fall back to driver `fops->ioctl` or `fops->compat_ioctl` when present. `BLKPG` requires `CAP_SYS_ADMIN`, whole-disk access, positive partition numbers, aligned byte ranges, overflow checks, and capacity checks before delegating to add/delete/resize partition helpers.

Discard and zeroing ioctls copy a two-u64 byte range from userspace, validate write access, read-only state, alignment, nonzero length, and end-of-device bounds. They lock the block inode and invalidate mapping pages before issuing discard/secure erase/zeroout bios. Secure erase checks secure-erase queue support and uses `blkdev_issue_secure_erase()`. Zeroout uses `BLKDEV_ZERO_NOUNMAP | BLKDEV_ZERO_KILLABLE`.

Persistent reservation commands gate partition use, capability/open-mode permissions, user copy, flag validity, and driver `pr_ops` presence. Read-key output allocates a variable-size kernel buffer, copies only the requested/available key count, and returns generation/count metadata.

The io_uring path currently supports `BLOCK_URING_CMD_DISCARD`: it validates SQE padding, persists start/len in the command private data across reissue, supports nonblocking invalidation/allocation with `-EAGAIN`, chains discard bios, and completes through task work.

## State and Persistence Behavior
The file can persistently alter media via discard, secure erase, zeroout, partition table mutation, read-only flags, block-size changes, persistent reservations, crypto key preparation/import/generation, and zone management. It mutates page cache and bdev metadata to keep kernel state coherent with destructive media operations. It also updates BDI readahead pages and returns diskseq for user-space event correlation.

## Dependencies and Integration Points
It integrates with VFS file mode conversion from `file_to_blk_mode()`, partition core helpers, zone management, blktrace, blk-crypto, persistent reservation driver callbacks, block queue limits, page cache invalidation, io_uring command infrastructure, and compat userspace ABI translation.

## Risks and Edge Cases
The ioctl ABI is broad and compatibility-sensitive. Misaligned or overflowing ranges must be rejected before destructive operations. `BLKFLSBUF` has holder sync behavior under `bd_holder_lock`; incorrect locking could deadlock or skip stacked-device sync. Compat command numbers differ for selected commands. io_uring discard cannot safely report partial multi-bio failures in NOWAIT mode, so it forces retry. `blkdev_bszset()` must reopen exclusively when the original file is not exclusive.

## Test Signals
Run block ioctl ABI tests for native and compat userspace, BLKPG add/delete/resize races, discard/zeroout/secure erase boundary tests, read-only permission tests, persistent reservation passthrough tests with capable and unprivileged callers, blk-crypto ioctl tests, zone ioctl tests, io_uring discard NOWAIT/blocking tests, and syzkaller-style user pointer/fuzz tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioprio.c -->
# sources/distributed-fs/ceph-client/block/ioprio.c

## Purpose
`ioprio.c` implements the `ioprio_set` and `ioprio_get` system calls and capability validation for process, process-group, and user scoped I/O priorities.

## Important APIs, Types, and Functions
- `ioprio_check_cap()` validates encoded I/O priority class and level and enforces `CAP_SYS_ADMIN` or `CAP_SYS_NICE` for real-time I/O priority.
- `SYSCALL_DEFINE3(ioprio_set, which, who, ioprio)` applies priority to a process, process group, or user’s tasks through `set_task_ioprio()`.
- `SYSCALL_DEFINE2(ioprio_get, which, who)` returns raw process priority or the best effective priority across group/user scopes.
- `get_task_ioprio()` and `get_task_raw_ioprio()` wrap LSM checks and task locking.

## Control Flow
`ioprio_set()` first validates the requested priority. Under RCU, it resolves `which`: current or target pid, current or target pgrp, or current/target uid. Process-group iteration uses `tasklist_lock`; user iteration walks every process/thread and filters by uid and visible pid. Each selected task is updated until an error aborts the operation.

`ioprio_get()` similarly resolves scope. For a single process it returns the raw userspace-set value so callers can distinguish default/unset from an explicit class. For pgrp/user scopes it obtains effective task priorities, skips tasks that fail per-task security checks, and returns the numerically best priority via `min()`.

## State and Persistence Behavior
I/O priority is task/io-context runtime state, not durable storage. The syscalls can allocate or update task `io_context` state through lower-level helpers. User references from `find_user()` are released after iteration.

## Dependencies and Integration Points
The file depends on scheduler task iteration, pid namespaces, credentials/user namespaces, Linux Security Module hooks (`security_task_getioprio` and checks inside setters), capabilities, and block I/O scheduler interpretation of encoded `IOPRIO_*` values. Schedulers such as mq-deadline use request ioprio to select priority classes.

## Risks and Edge Cases
RT priority permission checks intentionally check `CAP_SYS_ADMIN` before `CAP_SYS_NICE` for historical SELinux behavior. `IOPRIO_CLASS_NONE` is valid only with level zero. User namespace uid conversion can fail. Group/user scans under RCU and tasklist locking must avoid use-after-free while still tolerating tasks disappearing. `ioprio_best()` uses numeric minimum, matching encoded-priority ordering assumptions.

## Test Signals
Use syscall tests for all `which` scopes, invalid class/level encodings, RT priority with and without capabilities, uid namespace behavior, raw default priority reads, LSM denial paths, pgrp/user aggregation, and scheduler-visible behavior under mq-deadline or BFQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/kyber-iosched.c -->
# sources/distributed-fs/ceph-client/block/kyber-iosched.c

## Purpose
`kyber-iosched.c` implements the Kyber blk-mq I/O scheduler. Kyber controls latency by classifying requests into scheduling domains, limiting each domain with device-wide tokens, batching dispatch per hardware queue, and dynamically resizing token depths from latency histograms.

## Important APIs, Types, and Functions
- Domain constants: `KYBER_READ`, `KYBER_WRITE`, `KYBER_DISCARD`, `KYBER_OTHER`.
- Queue state: `struct kyber_queue_data` stores domain token `sbitmap_queue`s, per-cpu latency histograms, timer, latency targets, and p99 state.
- Hardware context state: `struct kyber_hctx_data` stores per-domain flushed request lists, current domain, batching counter, per-software-context queues, busy bitmaps, and wait entries.
- Elevator callbacks: init/exit, hctx init/exit, depth limiting, bio merge, request prepare/insert/finish/requeue/completed, dispatch, has-work, depth-updated.
- Tunables: sysfs `read_lat_nsec` and `write_lat_nsec`; debugfs token/list/wait/current-domain/batching views.

## Control Flow
Initialization enables block stats, clears single-queue scheduling, computes async depth as 75% of queue requests, allocates per-domain token pools and per-cpu latency buckets, and initializes per-hctx queues and wait entries. Inserts classify each request by operation, append it to the matching per-context domain list, and set a busy bit so dispatch can flush it later.

Dispatch holds the hctx scheduler lock. It continues the current domain batch until the batch size is consumed or the domain cannot supply a request/token. It then rotates domains and attempts dispatch. `kyber_dispatch_cur_domain()` either dispatches from already flushed domain lists or obtains a token and flushes busy per-context queues. If no token is available, it registers a wait entry in the token sbitmap so token release reruns the hardware queue.

Completion records total and device I/O latency for read/write/discard requests in per-cpu histograms and schedules a timer. The timer aggregates histograms, computes p90 I/O congestion and p99 total latency, and resizes domain token depths: congested devices throttle domains with good latency and ease throttling for domains with bad latency.

## State and Persistence Behavior
Kyber state is runtime-only: token depths, wait queues, current batching domain, per-context pending lists, latency histograms, target latency sysfs values, and trace/debugfs observations. It does not persist policy across reboot. Request `elv.priv[0]` stores the allocated domain token index until finish/requeue clears it.

## Dependencies and Integration Points
The scheduler integrates with blk-mq elevator registration, request queues, `sbitmap_queue`, blk statistics, block tracepoints, Kyber tracepoints, debugfs, and request ioprio indirectly through operation classification. It is registered as elevator `kyber` via module init.

## Risks and Edge Cases
Correct token release is critical; leaks throttle domains permanently. Wait-queue insertion/removal has races with token wakeups and is carefully protected. Per-context list flushing trades merge opportunities against dispatch latency. Only read/write latency targets are exposed even though discard has an internal default. Latency feedback depends on sample windows and may overreact or underreact on sparse workloads.

## Test Signals
Run fio latency tests across read/write/discard mixes, token-depth resizing tracepoint checks, scheduler switch/load/unload tests, blk-mq debugfs inspection, NOWAIT/sync-vs-async queue-depth checks, merge tests, CPU hotplug/per-cpu bucket aggregation, and lockdep under high parallel dispatch/completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/kyber-iosched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/mq-deadline.c -->
# sources/distributed-fs/ceph-client/block/mq-deadline.c

## Purpose
`mq-deadline.c` implements the mq-deadline blk-mq scheduler. It adapts the classic deadline algorithm to blk-mq by sorting requests by sector while also enforcing read/write expiration, batching, write-starvation limits, and I/O priority ordering.

## Important APIs, Types, and Functions
- `struct deadline_data` stores global scheduler state: dispatch list, per-priority queues, last direction, batching, starved counter, tunables, and spinlock.
- `struct dd_per_prio` stores per-priority red-black sort lists and FIFO lists for reads and writes plus latest positions and stats.
- Priority mapping maps I/O classes NONE/RT/BE/IDLE to deadline priorities RT/BE/IDLE.
- Core algorithms: `__dd_dispatch_request()`, `dd_dispatch_prio_aged_requests()`, `dd_dispatch_request()`, `dd_insert_request()`, `dd_request_merge()`, `dd_bio_merge()`, and request merge/finish callbacks.
- Tunables: `read_expire`, `write_expire`, `writes_starved`, `front_merges`, `fifo_batch`, and `prio_aging_expire`.

## Control Flow
Initialization allocates `deadline_data`, initializes all per-priority FIFO and RB trees, sets defaults, marks the queue as `QUEUE_FLAG_SQ_SCHED` because scheduling is queue-wide, and sets async depth. Insertion maps request ioprio to a scheduler priority, records the per-prio pointer in `rq->elv.priv[0]`, attempts insert merge, then either appends to the dispatch head list or adds the request to both the sector-sorted RB tree and expiry FIFO list.

Dispatch first drains explicit dispatch-head requests. It then checks priority aging so old lower-priority requests can run despite higher-priority traffic. Otherwise it scans priorities from RT to IDLE and dispatches from the first priority that has work. Within a priority, `__dd_dispatch_request()` continues a batch in the same direction when possible, prefers reads over writes unless writes have been starved too often, switches to FIFO order when deadlines expire or sector order wraps, and rejects requests whose start time is newer than the aging threshold.

Merging can do front merges by RB lookup on `bio_end_sector()` when enabled, repositions RB nodes after front merge, preserves earliest FIFO expiry when two requests merge, and removes merged requests from queue state.

## State and Persistence Behavior
State is runtime scheduler metadata only. Requests live simultaneously in RB trees/FIFO lists or the dispatch list until dispatched. Statistics count inserted, merged, dispatched, and completed requests per priority; they can overflow but are sized for outstanding-request tracking. Sysfs tunables persist only until changed or scheduler teardown.

## Dependencies and Integration Points
The scheduler integrates with blk-mq elevator callbacks, request hashes/RB-tree helpers, bio merge helpers, ioprio encoding, sbitmap depth limiting, tracepoints, and optional blk-mq debugfs. It registers as elevator `mq-deadline` with alias `deadline` and module alias `mq-deadline-iosched`.

## Risks and Edge Cases
The scheduler uses queue-wide state even when dispatch is called for a specific hardware queue, so returned requests may target another hctx. Correct lock coverage around RB/list state is essential. Stats warnings in exit catch missed completions or bypassed paths. Priority aging must prevent starvation without undermining RT priority. Front merges require RB repositioning to preserve sector order.

## Test Signals
Use fio workloads for read-vs-write latency, sequential batching, starvation limits, RT/BE/IDLE priority behavior, priority aging, front merge on/off, scheduler switch/unload under I/O, debugfs queue stats, blk-mq queue-depth updates, and lockdep/KASAN under concurrent merges and dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/mq-deadline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/opal_proto.h -->
# sources/distributed-fs/ceph-client/block/opal_proto.h

## Purpose
`opal_proto.h` defines constants, token IDs, UIDs, method IDs, packet headers, and Discovery 0 feature descriptor structs for TCG Opal self-encrypting drive support. It is a protocol description header consumed by the Opal implementation, primarily `sed-opal.c`.

## Important APIs, Types, and Functions
There are no functions. Important definitions include:
- Security protocol IDs `TCG_SECP_00..02`, generic session numbers, discovery COMID, and TPer/locking feature masks.
- Atom encoding masks and token bytes for tiny/short/medium/long/empty atoms.
- `enum opal_uid`, `enum opal_method`, `enum opal_token`, `enum opal_lockingstate`, `enum opal_parameter`, and `enum opal_revertlsp`.
- Packet structures: `opal_compacket`, `opal_packet`, `opal_data_subpacket`, `opal_header`, `opal_stack_reset`, and `opal_stack_reset_response`.
- Discovery feature descriptors: `d0_header`, `d0_tper_features`, `d0_locking_features`, `d0_geometry_features`, `d0_enterprise_ssc`, `d0_opal_v100`, `d0_single_user_mode`, `d0_datastore_table`, `d0_opal_v200`, and `d0_features`.

## Control Flow
This header does not execute code. Its layout controls how the Opal command layer builds and parses SECURITY PROTOCOL IN/OUT payloads, indexes static UID/method arrays, interprets method status and token streams, and walks variable-length Discovery 0 feature descriptors.

## State and Persistence Behavior
The header itself has no mutable state. The protocol entities it describes affect persistent drive security state such as locking ranges, MBR shadowing, user/admin PINs, generated keys, revert behavior, and datastore tables. Endianness annotations (`__be*`) are part of the state contract for on-wire parsing.

## Dependencies and Integration Points
It depends on `<linux/types.h>` and Linux endian integer typedefs. The main integration is with TCG Opal SED management and block crypto/security ioctl flows that eventually send Opal commands to storage devices.

## Risks and Edge Cases
Struct layout and endian annotations are ABI-critical for device interoperability. Optional fields and bit-packed descriptors require exact offsets. Enum indices must match companion UID/method arrays; inserting values can break lookups. Atom masks and response token IDs are protocol-sensitive and difficult to test without real or emulated Opal devices.

## Test Signals
Useful checks include compile-time layout assertions in consumers, Opal discovery parsing tests against captured device payloads, security protocol command tests on real SEDs, endianness tests on big-endian builds, and regression tests for UID/method array index consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/opal_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Kconfig -->
# sources/distributed-fs/ceph-client/block/partitions/Kconfig

## Purpose
`partitions/Kconfig` declares build-time configuration options for partition table parsers. It lets kernels include common MSDOS/GPT support by default and optional foreign/legacy formats when `PARTITION_ADVANCED` or architecture defaults request them.

## Important APIs, Types, and Functions
This is Kconfig data, not C code. Key symbols include `PARTITION_ADVANCED`, `ACORN_PARTITION` and its subformats, `AIX_PARTITION`, `OSF_PARTITION`, `AMIGA_PARTITION`, `ATARI_PARTITION`, `IBM_PARTITION`, `MAC_PARTITION`, `MSDOS_PARTITION`, BSD/Minix/Solaris/Unixware subpartition options, `LDM_PARTITION`, `LDM_DEBUG`, `SGI_PARTITION`, `ULTRIX_PARTITION`, `SUN_PARTITION`, `KARMA_PARTITION`, `EFI_PARTITION`, `SYSV68_PARTITION`, `CMDLINE_PARTITION`, and `OF_PARTITION`.

## Control Flow
The file controls which parser objects appear in `partitions/Makefile` and therefore which entries are compiled into the `check_part[]` probe order in `core.c`. Several options default to `y` on matching architectures, while `EFI_PARTITION` and `MSDOS_PARTITION` default to `y` generally. `EFI_PARTITION` selects `CRC32`; `OF_PARTITION` depends on `OF`; MSDOS subpartition features depend on `MSDOS_PARTITION`.

## State and Persistence Behavior
Kconfig choices persist in the kernel build configuration, not at runtime. They determine the kernel’s ability to recognize partition formats and can affect bootability or device enumeration on systems using uncommon labels.

## Dependencies and Integration Points
This file integrates Kconfig with parser C files and the top-level block configuration. It must stay consistent with Makefile object names and `core.c` conditional parser declarations. Help text references relevant admin documentation for LDM and command-line partitioning.

## Risks and Edge Cases
Disabling default parsers can make disks invisible at boot. Enabling too many legacy probes can increase false-positive risk, which is mitigated by parser order in `core.c`. Subpartition options require parent parser support. Architecture defaults need care when architectures are removed or renamed.

## Test Signals
Build matrices with `PARTITION_ADVANCED` on/off, architecture default configs, `EFI_PARTITION=n`, `MSDOS_PARTITION=n`, and dependency checks via `make olddefconfig` or Kconfig warnings are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Makefile -->
# sources/distributed-fs/ceph-client/block/partitions/Makefile

## Purpose
`partitions/Makefile` maps partition parser Kconfig symbols to object files in the kernel build.

## Important APIs, Types, and Functions
There are no functions. The key entries build `core.o` whenever `CONFIG_BLOCK` is enabled and conditionally include parser objects such as `acorn.o`, `amiga.o`, `atari.o`, `aix.o`, `cmdline.o`, `mac.o`, `ldm.o`, `msdos.o`, `of.o`, `osf.o`, `sgi.o`, `sun.o`, `ultrix.o`, `ibm.o`, `efi.o`, `karma.o`, and `sysv68.o`.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` entries into built-in objects for enabled symbols. The resulting compiled objects must define the parser functions referenced under matching `#ifdef`s in `core.c`.

## State and Persistence Behavior
The file has no runtime state. It controls static kernel contents and therefore the set of partition formats recognized by the built kernel.

## Dependencies and Integration Points
It depends on symbol names from `Kconfig` and source filenames in the same directory. It also depends on `core.o` always being present for partition management when block support is compiled.

## Risks and Edge Cases
Kconfig/Makefile/core mismatches produce link errors or dead code. Removing an object without updating parser declarations can break builds for specific configs. Parser order is not defined here, so adding an object also requires updating `core.c` if it participates in probing.

## Test Signals
Build all partition-related config combinations, especially individual parser enablement, `CONFIG_BLOCK=n`, and allmodconfig/allyesconfig link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/acorn.c -->
# sources/distributed-fs/ceph-client/block/partitions/acorn.c

## Purpose
`acorn.c` implements partition detection for multiple Acorn/RISC OS disk-label variants: Cumana, native ADFS, ICS, PowerTec, EESOX, and optional RISCiX/Linux subformats. It reflects the lack of a single Acorn partition standard.

## Important APIs, Types, and Functions
- Shared helpers: `adfs_partition()`, `linux_partition()`, optional `riscix_partition()`.
- Parser entry points: `adfspart_check_CUMANA()`, `adfspart_check_ADFS()`, `adfspart_check_ICS()`, `adfspart_check_POWERTEC()`, and `adfspart_check_EESOX()`.
- On-disk structs: `riscix_record`, `riscix_part`, `linux_part`, `ics_part`, `ptec_part`, and `eesox_part`.
- Validation helpers: `valid_ics_sector()`, `valid_ptec_sector()`, and `adfspart_check_ICSLinux()`.

## Control Flow
Each parser reads fixed sectors with `read_part_sector()`, validates magic/checksum/ADFS boot block data, emits parser tags to `pp_buf`, and calls `put_partition()` for discovered ranges. ADFS and Cumana use sector 6 boot-block data and may delegate non-ADFS regions to RISCiX or Linux parsers. ICS reads sector 0, validates a checksum seeded with `0x50617274`, interprets signed sizes, and can hide a Linux marker sector by advancing start/size. PowerTec reads sector 0, rejects PC MBR signatures, validates a checksum, and scans twelve entries. EESOX reads sector 7, XOR-decodes a 256-byte table with a fixed name key, derives partition sizes from successive starts, and makes the final partition extend to disk capacity.

## State and Persistence Behavior
There is no runtime state beyond `parsed_partitions`. The parser translates vendor-specific on-disk metadata into kernel partition records and informational printk text. It does not write disk metadata.

## Dependencies and Integration Points
It depends on ADFS filesystem disk-record helpers, `check.h`, partition core probe ordering, and Kconfig suboptions. It must run before more generic parsers when stale PC tables may coexist with Acorn metadata.

## Risks and Edge Cases
Several formats have uncertain or historically incomplete semantics. Cumana code explicitly notes untested behavior and unclear next-partition sizing. EESOX stores starts but not sizes, making derived sizes fragile. Signed ICS sizes are overloaded as ignore markers. All parsers must avoid sector leaks on early breaks; this file has complex `put_dev_sector()` paths.

## Test Signals
Use disk images for each Acorn variant, malformed checksum/magic cases, negative ICS sizes with Linux marker sectors, EESOX final-size behavior, partition-limit truncation, stale MBR coexistence, and memory/folio leak checks around early exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/acorn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/aix.c -->
# sources/distributed-fs/ceph-client/block/partitions/aix.c

## Purpose
`aix.c` recognizes a simple AIX LVM layout and exposes contiguous logical volumes as Linux partitions. It supports only the simple case where logical volumes occupy contiguous physical partitions.

## Important APIs, Types, and Functions
- Parser entry point: `aix_partition()`.
- Disk-reading helpers: `read_lba()`, `alloc_pvd()`, and `alloc_lvn()`.
- On-disk structs: `lvm_rec`, `vgda`, `lvd`, `lvname`, `ppe`, and `pvd`.
- Internal `lv_info` tracks expected physical partitions per logical volume, discovered count, and contiguity.

## Control Flow
The parser reads sector 7 and checks the LVM record version. Version 1 yields physical-partition size, VGDA length, and VGDA sector. It reads VGDA metadata to discover logical-volume count, reads logical-volume descriptors and names, then reads a physical-volume descriptor. It scans physical partition entries, tracking contiguous logical partition indices for each LV. When the final expected LP for an LV is seen in order, it publishes one partition covering the contiguous extent and prints the LV name. Non-contiguous LVs are warned and skipped.

## State and Persistence Behavior
The parser creates transient allocations for LV names, PVD, and `lv_info`; it writes only `parsed_partitions`. It does not mutate AIX metadata. The resulting partition numbers are LV index plus one, bounded by `state->limit`.

## Dependencies and Integration Points
It depends on `check.h`, big-endian field conversion, generic sector reads, and partition core probing. It is enabled by `CONFIG_AIX_PARTITION`.

## Risks and Edge Cases
Only LVM version 1 is supported; other versions produce informational output and no partitions. Large shifts from `pp_size` need sane on-disk data. The parser assumes VGDA/PVD offsets used by supported simple layouts. Non-contiguous logical volumes are intentionally not exposed, avoiding misleading block-device ranges.

## Test Signals
Test with simple contiguous AIX LVM images, non-contiguous LV images, unsupported LVM version, truncated VGDA/PVD/name tables, large physical partition sizes, and allocation-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/aix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/amiga.c -->
# sources/distributed-fs/ceph-client/block/partitions/amiga.c

## Purpose
`amiga.c` detects Amiga Rigid Disk Block partition tables and maps valid `PartitionBlock` entries to Linux partitions.

## Important APIs, Types, and Functions
- Entry point: `amiga_partition()`.
- Helper: `checksum_block()` sums big-endian words and expects zero for valid blocks.
- Uses Amiga AFFS hardblock structures `RigidDiskBlock` and `PartitionBlock`.

## Control Flow
The parser scans sectors from zero to `RDB_ALLOCATION_LIMIT` looking for an `IDNAME_RIGIDDISK` block with a valid checksum. It retries checksum validation after zeroing a known Windows-corrupted word range. Once an RDB is found, it derives the logical block-size multiplier and follows the RDB partition-list chain. For each partition block it validates ID and checksum, calculates cylinder blocks from heads and sectors, normalizes by RDB block size, derives start and size from low/high cylinders, checks overflow, then calls `put_partition()`. It prints DOS type and selected environment parameters for mounting diagnostics.

## State and Persistence Behavior
The parser only reads Amiga RDB metadata and writes transient parsed partition records. It emits warnings for invalid checksums, overflow, and 64-bit needs but does not repair metadata.

## Dependencies and Integration Points
It depends on AFFS hardblock definitions, overflow helpers, `check.h`, generic sector reads, and `CONFIG_AMIGA_PARTITION`. It is called from the partition core after several more common parser types.

## Risks and Edge Cases
RDB permits very large 32-bit fields whose products can overflow, so checked arithmetic is central. Logical block sizes other than 512 bytes require normalization. Partition-list block numbers are in the RDB block-size domain and are converted to 512-byte sectors in-place. Bad metadata can create long or invalid chains; the loop bounds partition count to 16.

## Test Signals
Use valid RDB images, corrupted checksum images including the Windows word workaround, oversized arithmetic cases, non-512 RDB block sizes, invalid partition IDs, zero-length partitions, and KASAN/folio leak testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/amiga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.c -->
# sources/distributed-fs/ceph-client/block/partitions/atari.c

## Purpose
`atari.c` detects Atari AHDI partition tables, XGM extended chains, and ICD/Supra extra partition entries.

## Important APIs, Types, and Functions
- Entry point: `atari_partition()`.
- Validation macros/helpers: `VALID_PARTITION()` and `OK_id()`.
- On-disk structures are defined in `atari.h`: `rootsector` and `partition_info`.

## Control Flow
The parser first requires a 512-byte logical block size because the Atari format assumes 512-byte LBAs. It reads sector 0 and accepts the table only if at least one primary partition entry is active, alphanumeric, and within disk size. It emits `AHDI`, iterates four primary entries, publishes ordinary active entries, and follows `XGM` extended chains by reading rootsectors at linked offsets and publishing their first partition. If no XGM format was found, it optionally scans ICD/Supra entries 5 through 12 and publishes entries with accepted IDs (`GEM`, `BGM`, `RAW`, `LNX`, `SWP`).

## State and Persistence Behavior
State is limited to `parsed_partitions` and printk/seq output. The parser does not persist or modify Atari rootsector data.

## Dependencies and Integration Points
It depends on `check.h`, `atari.h`, `ctype`, big-endian conversion, and `CONFIG_ATARI_PARTITION`. It is invoked after Amiga in the generic probe list.

## Risks and Edge Cases
The format has no reliable magic, so false positives are mitigated by entry validation. XGM chains can be malformed: missing active first subpartition, wrong second-entry ID, read failure, and partition-limit exhaustion are handled with messages and breaks. Non-512 logical sectors are rejected early to prevent bad arithmetic.

## Test Signals
Test valid AHDI, XGM extended, ICD/Supra, malformed chains, non-512 logical block devices, invalid active entries, out-of-range sizes, and partition-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.h -->
# sources/distributed-fs/ceph-client/block/partitions/atari.h

## Purpose
`atari.h` defines the packed on-disk Atari rootsector and partition-entry layout consumed by `atari.c`.

## Important APIs, Types, and Functions
There are no functions. `struct partition_info` stores flags, a three-byte ID, big-endian start sector, and big-endian size. `struct rootsector` contains boot-code padding, eight ICD partition slots, disk size, four primary entries, bad-sector-list fields, and checksum.

## Control Flow
The header has no executable flow. Its field offsets determine how `atari_partition()` interprets sector zero and optional ICD entries.

## State and Persistence Behavior
The structs model persistent Atari disk metadata. The Linux parser reads them but does not update them.

## Dependencies and Integration Points
It includes `<linux/compiler.h>` for `__packed` and uses Linux integer/endian types. It is tightly coupled to `atari.c`; changes must preserve binary layout.

## Risks and Edge Cases
Any padding/layout change would corrupt parsing. The checksum field exists but is not used by the current parser. Comments document ID semantics but validation policy lives in `atari.c`.

## Test Signals
Compile layout checks, parsing known Atari images, big-endian field conversion tests, and structure size/offset assertions are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/check.h -->
# sources/distributed-fs/ceph-client/block/partitions/check.h

## Purpose
`check.h` declares the shared partition-parser interface and `struct parsed_partitions`, the intermediate container used by all partition table parsers before the core creates block-device partition objects.

## Important APIs, Types, and Functions
- `struct parsed_partitions` contains the disk, printable name, per-slot parsed range/flags/meta-info array, next/limit fields, beyond-end flag, and `seq_buf` for diagnostic output.
- `Sector` wraps a folio reference returned by `read_part_sector()`.
- `put_dev_sector()` releases the folio.
- `put_partition()` records a partition slot and appends a printable partition name.
- Parser prototypes cover Acorn, AIX, Amiga, Atari, cmdline, EFI, IBM, Karma, LDM, Mac, MSDOS, OF, OSF, SGI, Sun, SYSV68, and Ultrix.

## Control Flow
Parser implementations call `read_part_sector()` to map sector data, inspect on-disk structures, call `put_partition()` for discovered ranges, optionally fill `state->parts[n].info`, and return `1` for recognized, `0` for not recognized, or negative for read errors.

## State and Persistence Behavior
The header describes transient state. `state->access_beyond_eod` informs `core.c` whether native capacity unlock/retry may be needed. Per-partition metadata can become persistent kernel-visible sysfs/uevent state after `add_partition()` duplicates it into `bd_meta_info`.

## Dependencies and Integration Points
It depends on block device, page cache, seq_buf, and internal block definitions. It is the contract between parser files and `partitions/core.c`.

## Risks and Edge Cases
`put_partition()` silently ignores slots beyond `state->limit`, so parsers must still avoid overrunning their own local counters. Parsers must always call `put_dev_sector()` for successful reads. `state->name` is modified by `core.c` to include `p` suffix rules for disk names ending in digits.

## Test Signals
Compile all parser combinations, sector read error injection, partition-limit tests, metadata propagation tests, and folio reference leak checks validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/cmdline.c -->
# sources/distributed-fs/ceph-client/block/partitions/cmdline.c

## Purpose
`cmdline.c` implements partition definitions supplied through the kernel command line `blkdevparts=` parameter, primarily for embedded fixed block devices without on-disk partition tables.

## Important APIs, Types, and Functions
- Runtime structs: `cmdline_subpart` for one named range and `cmdline_parts` for one block device’s partition list.
- Parser helpers: `parse_subpart()`, `parse_parts()`, `cmdline_parts_parse()`, `cmdline_parts_find()`.
- Runtime application: `cmdline_partition()`, `cmdline_parts_set()`, `add_part()`, `cmdline_parts_verifier()`.
- Boot parameter hook: `__setup("blkdevparts=", cmdline_parts_setup)`.

## Control Flow
The setup hook stores the raw command line. On first `cmdline_partition()` call, the raw string is parsed into a linked list of device definitions separated by `;`, with subpartitions separated by `,`. Each subpartition can specify size, optional start after `@`, optional name in parentheses, and flags `ro` and `lk`. The parser finds the matching `state->disk->disk_name`, fills missing starts sequentially, clamps oversize partitions to disk end, adds partitions by byte-to-sector conversion, stores names in `partition_meta_info`, and warns about overlaps.

## State and Persistence Behavior
`cmdline` is a one-shot pointer to boot argument text. Parsed `bdev_parts` is global runtime state retained for later device scans and freed/replaced if a new raw string is parsed. Published partition metadata becomes kernel-visible state; no on-disk metadata is written.

## Dependencies and Integration Points
It depends on `memparse()`, boot `__setup`, generic parser core, partition metadata, block device names, and `CONFIG_CMDLINE_PARTITION`. It has higher probe priority than OF partitioning in `core.c`.

## Risks and Edge Cases
The parser mutates `subpart->from` and `subpart->size` while applying to a disk, so repeated rescans use adjusted values. `PF_POWERUP_LOCK` is parsed but not applied in `add_part()`. Overlapping partitions are allowed but warned. Invalid size below `PAGE_SIZE` rejects a subpartition. `-` size means consume remainder.

## Test Signals
Boot tests with multiple devices, named/unnamed partitions, explicit and implicit starts, remainder sizes, read-only flags, overlaps, invalid syntax, no matching device, repeated rescans, and byte-sector conversion boundary cases are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/core.c -->
# sources/distributed-fs/ceph-client/block/partitions/core.c

## Purpose
`core.c` orchestrates partition table probing, partition block-device creation/removal/resizing, partition sysfs/uevent attributes, rescan behavior, and sector reads for parser implementations.

## Important APIs, Types, and Functions
- Probe list: `check_part[]` orders enabled parser functions.
- Parser lifecycle: `allocate_partitions()`, `free_partitions()`, `check_partition()`, `read_part_sector()`.
- Partition device lifecycle: `add_partition()`, `drop_partition()`, `bdev_add_partition()`, `bdev_del_partition()`, `bdev_resize_partition()`.
- Rescan flow: `blk_add_partitions()`, `blk_add_partition()`, `bdev_disk_changed()`.
- Sysfs/device model: `part_type`, partition attributes (`partition`, `start`, `size`, `ro`, alignment/discard alignment, stats, inflight), and uevent variables `PARTN`, `PARTNAME`, `PARTUUID`.

## Control Flow
`check_partition()` allocates a `parsed_partitions`, initializes a one-page diagnostic buffer, and walks `check_part[]` in order. Before each parser attempt it clears the parts array. Negative parser results are saved as read errors but do not stop probing. A positive parser returns the filled state; no parser plus beyond-end access can become `-ENOSPC`.

`blk_add_partitions()` checks scan eligibility, invokes `check_partition()`, handles native-capacity retry for beyond-EOD reads, rejects host-managed zoned bdev partitioning, emits a disk change uevent, then creates each nonzero parsed partition. `blk_add_partition()` validates partition start/size against capacity, optionally unlocks native capacity and retries, clamps broken overlong partitions to disk end, calls `add_partition()`, and triggers MD autodetect for RAID-flagged partitions.

`bdev_disk_changed()` runs under `disk->open_mutex`, rejects live partitions, syncs and invalidates `part0`, drops existing partitions, optionally zeros capacity for media invalidation, and rescans if capacity remains. Manual add/delete/resize helpers enforce live disk state, no partition support flags, no overlaps, and no openers for deletion.

## State and Persistence Behavior
The file manages in-memory partition devices in `disk->part_tbl`, `block_device` fields (`bd_start_sect`, sector count, read-only flag, meta info), sysfs devices, uevents, inode hash visibility, and access-beyond-EOD state. It does not write partition tables; it reflects parser results into kernel block-device state.

## Dependencies and Integration Points
It integrates with every parser, gendisk/device model, xarray partition table, bdev allocation/hash/invalidation, sysfs, blk trace attributes, MD autodetect, native capacity unlock driver callback, zoned block restrictions, and generic page-cache sector reads.

## Risks and Edge Cases
Parser order is security and compatibility sensitive because false positives stop probing. `add_partition()` has several lifetime steps: get disk device reference, allocate bdev, assign devt, copy metadata, suppress uevent until holder dir exists, insert xarray, and bdev hash. Errors must unwind devt, kobjects, devices, and references. Rescan rejects open partitions; failure to do so would invalidate live devices. Beyond-EOD handling may unlock native capacity and retry.

## Test Signals
Run partition parser image tests, hot rescan while partitions are open, BLKPG add/delete/resize tests, overlap checks, host-managed zoned disk scans, native-capacity unlock scenarios, sysfs/uevent metadata tests, MD RAID flag autodetect, fault-injection for allocation/device_add failures, and folio leak tests for `read_part_sector()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.c -->
# sources/distributed-fs/ceph-client/block/partitions/efi.c

## Purpose
`efi.c` implements GUID Partition Table detection and parsing. It validates protective or hybrid MBRs, primary and alternate GPT headers, partition-entry CRCs, and emits Linux partition records with PARTUUID/PARTNAME metadata.

## Important APIs, Types, and Functions
- Entry point: `efi_partition()`.
- Validation helpers: `efi_crc32()`, `is_pmbr_valid()`, `pmbr_part_valid()`, `is_gpt_valid()`, `is_pte_valid()`, `compare_gpts()`, and `find_valid_gpt()`.
- Reading helpers: `last_lba()`, `read_lba()`, `alloc_read_gpt_header()`, `alloc_read_gpt_entries()`.
- Metadata conversion: `utf16_le_to_7bit()`.
- Boot override: `__setup("gpt", force_gpt_fn)` sets `force_gpt`.

## Control Flow
`efi_partition()` calls `find_valid_gpt()`. Unless `force_gpt` is set, `find_valid_gpt()` first reads LBA 0, validates MBR signature and a protective 0xEE record at LBA 1, and distinguishes hybrid MBRs. It validates the primary GPT at LBA 1 and, if good, validates the alternate GPT at the primary header’s `alternate_lba`. With `force_gpt`, it can also try the last LBA or driver-provided `alternative_gpt_sector()`.

`is_gpt_valid()` reads a logical-block-sized header, checks signature, header size range, header CRC with the CRC field zeroed, `my_lba`, usable-LBA bounds, entry size, table allocation size, reads the entry array, and verifies entry-array CRC. `compare_gpts()` warns on mismatches between primary and alternate headers.

After a valid GPT is selected, `efi_partition()` iterates entries up to the kernel partition limit. Non-null type GUIDs with in-range start/end LBAs become partitions after scaling logical blocks to 512-byte sectors. Linux RAID type GUID sets `ADDPART_FLAG_RAID`; unique partition GUID becomes `info.uuid`; UTF-16LE partition name is converted to printable 7-bit `info.volname`.

## State and Persistence Behavior
No on-disk GPT metadata is changed. Runtime state includes the global `force_gpt` flag and allocated header/entry buffers. Parsed metadata becomes partition device ranges, RAID flags, PARTUUID, and PARTNAME.

## Dependencies and Integration Points
It depends on CRC32, EFI GUID helpers, logical block size from the request queue, generic sector reads, optional driver `alternative_gpt_sector`, MD autodetect via RAID flag in core, and Kconfig `EFI_PARTITION` selecting `CRC32`.

## Risks and Edge Cases
GPT validation is intentionally strict for header CRC, entry CRC, entry size, and usable LBA bounds. Protective MBR size mismatches are only debug warnings to support cloned images. `read_lba()` reads in 512-byte sectors after multiplying by logical-block sectors, so logical block size handling must be correct. `force_gpt` bypasses PMBR protection and can expose stale or unintended GPTs.

## Test Signals
Use GPT images with valid primary/alternate headers, corrupt primary fallback to alternate, corrupt CRCs, hybrid MBRs, missing PMBR with and without `gpt`, non-512 logical block devices, RAID GUID entries, long/nonprintable UTF-16 names, oversized entry arrays, alternate GPT sector callbacks, and fuzzed GPT headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.h -->
# sources/distributed-fs/ceph-client/block/partitions/efi.h

## Purpose
`efi.h` defines GPT/PMBR constants, well-known partition type GUIDs, and packed on-disk structure layouts used by `efi.c`.

## Important APIs, Types, and Functions
There are no functions. Constants cover MBR signature, EFI protective MBR OS types, GPT primary LBA, GPT signature/revision, and common GUIDs for EFI system, legacy MBR, Microsoft reserved/basic data, Linux RAID, swap, and LVM. Types include `gpt_header`, `gpt_entry_attributes`, `gpt_entry`, `gpt_mbr_record`, and `legacy_mbr`.

## Control Flow
The header has no executable flow. `efi.c` uses these definitions to validate disk bytes and to populate partition metadata.

## State and Persistence Behavior
The structs model persistent GPT and PMBR on-disk state. Packed layout and little-endian fields are part of the disk-format contract.

## Dependencies and Integration Points
It depends on Linux EFI GUID types, endian integer typedefs, filesystem/kernel headers, and compiler packing. It is tightly coupled to the parser and any code comparing well-known partition type GUIDs.

## Risks and Edge Cases
Changing field order, packing, bitfield widths, or GUID constants would break GPT parsing. `gpt_entry_attributes` uses bitfields inside a packed type, so compiler expectations matter. The header intentionally omits variable reserved tail bytes from `gpt_header`; parser size checks handle full logical-block headers.

## Test Signals
Compile-time structure size/offset checks, GPT parser tests on known images, GUID comparison tests for RAID/swap/LVM/basic data, and cross-architecture endian/packing builds are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.h -->
