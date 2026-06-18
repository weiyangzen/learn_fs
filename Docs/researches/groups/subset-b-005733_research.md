# subset-b-005733 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/aops.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/aops.c

## Purpose
`aops.c` implements OCFS2 address-space operations for page-cache reads, readahead, writeback, buffered writes, mmap writes, direct I/O, inline data, block mapping, and folio buffer lifetime. It is the bridge between Linux VFS/page-cache APIs and OCFS2 clustered metadata, extent maps, journaling, quotas, refcount/COW, and inode DLM locks.

## Important APIs, types, and functions
The exported objects are `ocfs2_aops`, `ocfs2_get_block`, `ocfs2_map_folio_blocks`, `ocfs2_unlock_and_free_folios`, `walk_page_buffers`, `ocfs2_write_begin_nolock`, `ocfs2_write_end_nolock`, `ocfs2_read_inline_data`, and `ocfs2_size_fits_inline_data`. Internal write state is held in `struct ocfs2_write_ctxt`, `struct ocfs2_write_cluster_desc`, and `struct ocfs2_unwritten_extent`; direct-I/O completion state uses `struct ocfs2_dio_write_ctxt`. Major paths include `ocfs2_read_folio`, `ocfs2_readahead`, `ocfs2_write_begin`, `ocfs2_write_end`, `ocfs2_dio_wr_get_block`, `ocfs2_dio_end_io_write`, and `ocfs2_direct_IO`.

## Control flow
Reads take the inode lock and `ip_alloc_sem` read-side before resolving extents; inline inodes are copied from the dinode, while regular files use block helpers. Buffered writes take the inode lock exclusive, hold `ip_alloc_sem` write-side, allocate a write context, optionally use inline data, zero sparse tails or expand nonsparse files, COW refcounted extents, populate per-cluster descriptors, reserve allocators, start a journal transaction, grab folios, map/zero buffers, and finish in `ocfs2_write_end_nolock` by committing buffers, updating size/times, dirtying metadata, unlocking folios, committing, and running deferred deallocs. Direct writes use `ocfs2_dio_wr_get_block` as the block mapper, attach private completion context to the mapping buffer, add expanding writes to the orphan directory, and clear unwritten extents/update size/delete orphan in `ocfs2_dio_end_io_write`.

## State and persistence behavior
Persistent effects are extent allocation, unwritten-to-written conversion, inline-data conversion, dinode size/timestamp/block-count updates, orphan directory membership for extending direct I/O, quota allocation, and journaled metadata changes. Runtime state includes folio buffer flags, clustered extent cache results, `ip_unwritten_list`, allocation reservations, dealloc contexts, and `kiocb->private` bits used to communicate rw-lock ownership to direct-I/O completion.

## Dependencies and integration points
This file depends on the VFS address-space API, buffer-head helpers, mpage, direct I/O, quotas, jbd2 transactions, OCFS2 extent maps/allocation/refcount tree, inode locks, DLM rw locks, inline-data helpers, and tracing. `ocfs2_aops` is installed on OCFS2 inodes and is called from generic read/write/mmap/direct-I/O paths.

## Risks and test signals
Risks include lock-order deadlocks between folios, `ip_alloc_sem`, inode/DLM locks, and journal barriers; stale-data exposure during partial allocation failures; direct-I/O orphan cleanup failures; races with remote truncate; incorrect unwritten extent tracking; inline-to-extent conversion edge cases; and fallback behavior for unsupported append DIO. Test signals include buffered writes across cluster/page boundaries, sparse and nonsparse extension, inline data growth and conversion, mmap page faults, direct writes beyond EOF with crash recovery, refcounted COW writes, ENOSPC retry through truncate-log freeing, remote truncate during reads/readahead, and DIO completion with short or failed I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/aops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/aops.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/aops.h

## Purpose
`aops.h` declares the OCFS2 address-space helper API shared with file, mmap, direct-I/O, and inode code. It exposes the core write-begin/write-end primitives that assume higher-level locking has already been handled.

## Important APIs, types, and functions
It declares `ocfs2_map_folio_blocks`, `ocfs2_unlock_and_free_folios`, `walk_page_buffers`, `ocfs2_write_begin_nolock`, `ocfs2_write_end_nolock`, `ocfs2_read_inline_data`, `ocfs2_size_fits_inline_data`, and `ocfs2_get_block`. The `ocfs2_write_type_t` enum distinguishes buffered, direct, and mmap writes. Inline helpers and macros encode direct-I/O rw-lock state in `kiocb->private`, with `OCFS2_IOCB_RW_LOCK` and `OCFS2_IOCB_RW_LOCK_LEVEL`.

## Control flow
Callers that already hold OCFS2 inode and allocation locks can call the nolock write functions directly, passing a dinode buffer and receiving opaque `fsdata` write context. Direct-I/O submitters initialize and set rw-lock bits, while completion tests and clears those bits before unlocking.

## State and persistence behavior
The header itself has no storage, but it defines the `kiocb->private` bit contract. Misuse can leave direct-I/O completions unable to release the correct OCFS2 rw lock.

## Dependencies and integration points
It depends on Linux `fs.h`, folios, buffer heads, JBD handles, and OCFS2-specific definitions supplied by including C files. It integrates `aops.c` with write, mmap, direct-I/O, and inline-data users.

## Risks and test signals
Risks are ABI-like coupling through opaque `fsdata`, bit packing into `kiocb->private`, and callers invoking nolock helpers without required inode/alloc/journal context. Test signals include all three write types, direct-I/O completion after async submit, mmap write retry, and build coverage for all prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/aops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.c

## Purpose
`blockcheck.c` computes and validates OCFS2 metadata integrity fields: CRC32 plus a Hamming-code ECC capable of correcting a single bit error. It also exposes optional debugfs counters for checked blocks, checksum failures, and ECC recoveries.

## Important APIs, types, and functions
Low-level Hamming APIs are `ocfs2_hamming_encode`, `ocfs2_hamming_encode_block`, `ocfs2_hamming_fix`, and `ocfs2_hamming_fix_block`. Block APIs are `ocfs2_block_check_compute`, `ocfs2_block_check_validate`, `ocfs2_block_check_compute_bhs`, and `ocfs2_block_check_validate_bhs`. Superblock-gated wrappers are `ocfs2_compute_meta_ecc`, `ocfs2_validate_meta_ecc`, `ocfs2_compute_meta_ecc_bhs`, and `ocfs2_validate_meta_ecc_bhs`. Debugfs wrappers install/remove `blockcheck` statistic files.

## Control flow
Compute paths zero the embedded `struct ocfs2_block_check`, calculate CRC32 over disk-endian data, compute Hamming parity, then write little-endian check fields. Validate paths save stored CRC/ECC, zero the field, recalculate CRC, and return success if it matches. On mismatch they increment failure counters, compute current ECC, apply `stored_ecc ^ current_ecc` as the bit fix, then re-run CRC; success increments recovery, failure returns `-EIO`. Multi-buffer variants stream CRC/ECC across buffer heads with bit offsets.

## State and persistence behavior
Persistent state is the on-disk `ocfs2_block_check` embedded in metadata blocks. Runtime state consists of optional `ocfs2_blockcheck_stats` counters protected by a spinlock and debugfs dentries. Validation temporarily mutates the in-memory block while zeroing/restoring check fields and may correct the data buffer in place.

## Dependencies and integration points
It depends on Linux CRC32, bitops, buffer heads, debugfs, endian helpers, and OCFS2 superblock feature tests. Metadata readers/writers call the high-level wrappers so ECC is active only when `ocfs2_meta_ecc()` is enabled.

## Risks and test signals
Risks include corrupting buffers when an uncorrectable error is treated as correctable, wrong bit numbering across multi-buffer metadata, missing restoration of check fields, counter wrap, and callers passing host-endian instead of disk-endian data. Test signals include clean CRC fast path, single-bit correction, multi-bit failure, split buffer-head metadata, disabled meta-ECC feature, debugfs counter reads, and fuzzed block sizes up to the 4 KiB ECC assumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.h

## Purpose
`blockcheck.h` defines the public OCFS2 metadata checksum/ECC interface and the statistic structure used by debugfs.

## Important APIs, types, and functions
`struct ocfs2_blockcheck_stats` stores a spinlock, check/failure/recovery counters, and the debugfs parent dentry. The header declares high-level metadata ECC wrappers, lower-level raw block and buffer-head checksum functions, debugfs install/remove functions, and Hamming encode/fix helpers for whole buffers or offset hunks.

## Control flow
Metadata code includes this header to compute check fields before write and validate them after read. The high-level wrappers choose whether to execute based on the mounted filesystem’s meta-ECC feature; the lower-level functions assume the caller has already selected the correct policy.

## State and persistence behavior
The header contributes no state, but its declarations control both persistent `ocfs2_block_check` updates and in-memory statistics. Callers must initialize the stats spinlock and hold valid buffers while validation may repair data in place.

## Dependencies and integration points
It depends on OCFS2 on-disk `struct ocfs2_block_check`, Linux buffer heads, debugfs dentries, spinlocks, and integer types. It is used by metadata I/O paths such as superblock and inode/extent validation.

## Risks and test signals
Risks are incorrect use of lower-level APIs when the feature is disabled, uninitialized stats locks, and misuse of hunk offsets in Hamming helpers. Test signals include compile coverage with and without debugfs, meta-ECC enabled/disabled mounts, and callers validating both single-buffer and multi-buffer metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/buffer_head_io.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/buffer_head_io.c

## Purpose
`buffer_head_io.c` centralizes OCFS2 synchronous metadata buffer I/O. It reads metadata blocks through the clustered uptodate cache, supports forced reads and readahead, validates freshly-read buffers, writes non-journaled metadata blocks, and writes superblock/backup blocks with ECC.

## Important APIs, types, and functions
Public functions are `ocfs2_write_block`, `ocfs2_read_blocks_sync`, `ocfs2_read_blocks`, and `ocfs2_write_super_or_backup`. The file defines the private buffer state bit `BH_NeedsValidate` and generated helpers `set_buffer_needs_validate`, `clear_buffer_needs_validate`, and `buffer_needs_validate`. `ocfs2_check_super_or_backup` guards direct superblock writes.

## Control flow
`ocfs2_read_blocks` validates arguments, obtains/uses supplied buffer_heads, takes `ocfs2_metadata_cache_io_lock`, decides whether to trust `ocfs2_buffer_uptodate`, submit disk I/O, or skip JBD-owned buffers, optionally marks buffers for validation, waits unless readahead, runs the validate callback after successful disk reads, updates the clustered uptodate cache, and unwinds all buffers on failure. `ocfs2_read_blocks_sync` is a lower-level synchronous path without the clustered cache. `ocfs2_write_block` locks a metadata buffer, clears dirty, submits synchronous write, and marks it uptodate in the metadata cache. Super/backup writes verify block identity, compute metadata ECC, and bypass journal collaboration.

## State and persistence behavior
Persistent effects are raw writes to metadata, superblock, and backup superblocks. Runtime state includes buffer lock/dirty/uptodate/JBD bits, the OCFS2 clustered uptodate cache, and the transient `BH_NeedsValidate` bit that defers validation until the blocking caller waits.

## Dependencies and integration points
It depends on Linux buffer-head submission, OCFS2 metadata cache locking, hard/emergency read-only checks, blockcheck ECC, journal state bits, and metadata validators supplied by callers. It is used throughout OCFS2 metadata read/write code, especially inode, extent, directory, and superblock paths.

## Risks and test signals
Risks include races with JBD ownership, readahead validation being skipped or delayed incorrectly, buffer leaks when allocation fails mid-array, trusting stale clustered uptodate state, and raw superblock writes to wrong blocks. Test signals include cached versus forced reads, readahead followed by synchronous read with validation, dirty/JBD buffer encounters, multi-block read failure cleanup, hard read-only and emergency read-only writes, and ECC recomputation for primary and backup superblocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/buffer_head_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/buffer_head_io.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/buffer_head_io.h

## Purpose
`buffer_head_io.h` declares OCFS2 metadata buffer I/O helpers and read flags used by the filesystem’s metadata cache users.

## Important APIs, types, and functions
It declares `ocfs2_write_block`, `ocfs2_read_blocks_sync`, `ocfs2_read_blocks`, `ocfs2_write_super_or_backup`, and the inline single-block wrapper `ocfs2_read_block`. Flags are `OCFS2_BH_IGNORE_CACHE` for forced disk reads and `OCFS2_BH_READAHEAD` for asynchronous metadata prefetch.

## Control flow
Callers pass a caching object, block number, buffer array, flags, and optional validator. `ocfs2_read_block` checks for a null output pointer then delegates to `ocfs2_read_blocks` for one block.

## State and persistence behavior
The header has no state, but its flags govern whether callers consult or bypass the clustered metadata uptodate cache and whether validation is delayed to a later synchronous read.

## Dependencies and integration points
It depends on Linux buffer heads and OCFS2 `struct ocfs2_super`/`struct ocfs2_caching_info` definitions. It is included by metadata users that need consistent cache-aware I/O behavior.

## Risks and test signals
Risks are invalid flag combinations, null buffer arrays, and validators that assume they are called for cached buffers. Test signals include one-block and multi-block reads, forced reads, readahead plus later validation, and superblock backup writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/buffer_head_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/Makefile -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/Makefile

## Purpose
This Makefile builds the OCFS2 cluster/nodemanager support object when `CONFIG_OCFS2_FS` is enabled.

## Important APIs, types, and functions
It emits `ocfs2_nodemanager.o` from `heartbeat.o`, `masklog.o`, `sys.o`, `nodemanager.o`, `quorum.o`, `tcp.o`, and `netdebug.o`.

## Control flow
Kbuild includes the aggregate object under `obj-$(CONFIG_OCFS2_FS)`, so the cluster stack is compiled into the OCFS2 module/build only when the filesystem is selected.

## State and persistence behavior
The file has no runtime state. Its object list controls which cluster subsystems exist at runtime, including configfs, sysfs log masks, heartbeat, quorum, TCP messaging, and debugfs.

## Dependencies and integration points
It integrates the cluster directory with Linux Kbuild and the OCFS2 filesystem Kconfig option. The aggregate object order matters for linked symbols but module init remains driven by `nodemanager.c`.

## Risks and test signals
Risks are missing objects causing unresolved symbols or disabled diagnostics. Test signals include `CONFIG_OCFS2_FS=y/m` builds, `CONFIG_DEBUG_FS` builds for `netdebug.o`, and link verification for heartbeat/quorum/tcp cross-calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.c

## Purpose
`heartbeat.c` implements O2CB disk heartbeat. It exposes heartbeat regions through configfs, starts one kernel thread per region, writes this node’s slot to a shared block device, reads peer slots, derives live-node membership, fires ordered callbacks, tracks global-heartbeat quorum regions, and fences via quorum on heartbeat write timeouts.

## Important APIs, types, and functions
Main structures are `struct o2hb_region`, `struct o2hb_disk_slot`, `struct o2hb_node_event`, `struct o2hb_callback_func`, and `struct o2hb_bio_wait_ctxt`. Public APIs include `o2hb_init`, `o2hb_exit`, `o2hb_alloc_hb_set`, `o2hb_free_hb_set`, `o2hb_setup_callback`, `o2hb_register_callback`, `o2hb_unregister_callback`, `o2hb_fill_node_map`, `o2hb_check_node_heartbeating_no_sem`, `o2hb_check_node_heartbeating_from_callback`, `o2hb_stop_all_regions`, `o2hb_get_all_regions`, and `o2hb_global_heartbeat_active`.

## Control flow
Userspace creates a heartbeat configfs item, sets `block_bytes`, `start_block`, and `blocks`, then writes a block-device fd to `dev`. That commit path opens the block device, verifies sector size, allocates slot pages, reads baseline slot data, registers timeout work, starts `o2hb_thread`, and waits for steady iterations. Each heartbeat loop reads configured/live slots, validates peer CRCs, checks this node’s previous slot for overwrite/generation mismatch, prepares and writes this node’s slot, updates membership through `o2hb_check_slot`, and arms write/negotiation timeouts after steady state. Drop-item stops the thread, clears global-region bitmaps, wakes startup waiters, and releases the config item.

## State and persistence behavior
Persistent state lives on shared disk in `struct o2hb_disk_heartbeat_block` slots: sequence time, node number, CRC, generation, and dead timeout. Runtime global state includes live-node lists/bitmap, all-region list, live/quorum/failed region bitmaps, callback lists, debugfs buffers, heartbeat mode, dead threshold, and dependent-user pin counts. Region state includes block device file, task pointer, slot buffers, generation, timeout work, negotiation bitmap/key, and debugfs entries.

## Dependencies and integration points
It depends on configfs, block bio I/O, kthreads, delayed work, debugfs, CRC32, random generation values, O2CB networking for timeout negotiation messages, nodemanager for node identity/config dependencies, and quorum for self-fencing. O2NET and DLM register callbacks for node up/down events.

## Risks and test signals
Risks include false fencing on slow I/O, missed node transitions due to CRC/generation edge cases, configfs lifetime races while startup waits, mismatched dead thresholds across nodes, global-heartbeat region pin leaks, bio allocation under GFP_ATOMIC, and unsafe unclean stops. Test signals include local and global heartbeat modes, region creation/removal during startup, slow or failed heartbeat writes, all-nodes-hung negotiation, duplicate node slot detection, generation rollover/restart, callback priority ordering, debugfs bitmap reads, dependent-user pin/unpin, and quorum-region cut-off behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.h

## Purpose
`heartbeat.h` defines the in-kernel O2CB heartbeat interface, constants, callback contract, and public region/node query APIs.

## Important APIs, types, and functions
Constants define heartbeat timing (`O2HB_REGION_TIMEOUT_MS`, `O2HB_DEFAULT_DEAD_THRESHOLD`, `O2HB_MAX_WRITE_TIMEOUT_MS`), live/dead thresholds, region name length, and callback magic. `enum o2hb_callback_type` defines node-down and node-up callbacks. `struct o2hb_callback_func` stores callback function, data, priority, type, list node, and magic. Declarations cover callback setup/register/unregister, node-map fills, heartbeat init/exit, region stop/listing, node heartbeat checks, and global heartbeat mode query.

## Control flow
Subsystems initialize a callback with `o2hb_setup_callback`, register it optionally against a region UUID, receive serialized node up/down calls from heartbeat threads, then unregister before teardown. Region configfs groups are allocated by nodemanager through `o2hb_alloc_hb_set`.

## State and persistence behavior
The header exposes `o2hb_dead_threshold`, whose value influences on-disk `hb_dead_ms` and write-timeout fencing. It has no direct storage beyond declarations but defines the callback ABI used to pin heartbeat regions while dependent users exist.

## Dependencies and integration points
It includes `ocfs2_heartbeat.h` for on-disk slot layout and forward-declares nodemanager nodes/configfs groups. It is consumed by nodemanager, quorum, TCP networking, DLM, and filesystem code that checks cluster membership.

## Risks and test signals
Risks include callback users registering with wrong priority/type, stale region UUID assumptions in local heartbeat mode, and timeout macros changing as `o2hb_dead_threshold` changes. Test signals include callback registration order, unregister during active callbacks, local versus global region UUID behavior, and builds across configfs users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.c

## Purpose
`masklog.c` implements runtime-controllable OCFS2/O2CB logging masks. It stores allow/deny bitsets, formats log messages through `printk`, and exposes each mask bit under `/sys/fs/o2cb/logmask`.

## Important APIs, types, and functions
Global exported state is `mlog_and_bits` and `mlog_not_bits`. Public functions are `__mlog_printk`, `mlog_sys_init`, and `mlog_sys_shutdown`. Internal helpers parse/format mask state (`mlog_mask_show`, `mlog_mask_store`) and sysfs attributes (`mlog_show`, `mlog_store`).

## Control flow
Initialization populates the default attribute list from `mlog_attrs`, attaches a `logmask` kset under the supplied O2CB kset, and registers sysfs files. Reads return `allow`, `deny`, or `off`; writes accept those strings to update the global bitsets. The `mlog` macro in the header filters constant masks before calling `__mlog_printk`, which chooses severity and prefixes process, pid, CPU, function, and line.

## State and persistence behavior
All log masks are runtime-only global bitsets. Defaults allow errors and notices. Changes through sysfs do not persist across module unload/reboot unless userspace reapplies them.

## Dependencies and integration points
It depends on sysfs/kset APIs, kernel printk formatting, task identity, and `masklog.h` macros. Nearly all OCFS2 cluster code uses `mlog` for diagnostics, and `sys.c` owns the parent O2CB sysfs kset.

## Risks and test signals
Risks include unsynchronized global bit updates, mask table mismatch when adding bits, noisy console output if broad masks are enabled, and string parsing accepting prefixes. Test signals include sysfs allow/deny/off writes for every declared mask, debug-mask builds, default error/notice logging, and module shutdown unregistering the kset cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.h

## Purpose
`masklog.h` defines OCFS2/O2CB logging mask bits, compile-time filtering, bitset helpers, logging macros, and sysfs initialization declarations.

## Important APIs, types, and functions
It defines mask constants such as `ML_TCP`, `ML_HEARTBEAT`, `ML_DLM`, `ML_QUORUM`, `ML_ERROR`, `ML_NOTICE`, and `ML_KTHREAD`; `struct mlog_bits`; architecture-specific `__mlog_test_u64`, set, clear, and initializer macros; and user macros `mlog`, `mlog_ratelimited`, `mlog_errno`, and `mlog_bug_on_msg`. It declares `__mlog_printk`, `mlog_sys_init`, and `mlog_sys_shutdown`.

## Control flow
Call sites pass mask bits to `mlog`. The macro adds `MLOG_MASK_PREFIX`, applies `ML_ALLOWED_BITS`, then calls `__mlog_printk` only when runtime masks permit. `mlog_errno` suppresses common expected errors, and `mlog_bug_on_msg` logs before `BUG()`.

## State and persistence behavior
The header declares global allow/deny bitsets but stores no state itself. Mask choices affect runtime diagnostics only and are not persistent.

## Dependencies and integration points
It depends on scheduler/task state, kobject/sysfs declarations, ratelimit helpers, and compile-time options such as `CONFIG_OCFS2_DEBUG_MASKLOG`. Cluster modules can define `MLOG_MASK_PREFIX` before including it to prefix subsystem masks.

## Risks and test signals
Risks include forgetting to update `masklog.c` when adding a bit, architecture-specific bitset bugs, and assuming disabled debug logs have side effects. Test signals include 32-bit and 64-bit builds, ratelimited error paths, prefixed TCP/quorum logging, and sysfs table consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/netdebug.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/netdebug.c

## Purpose
`netdebug.c` provides debugfs diagnostics for O2CB TCP networking when `CONFIG_DEBUG_FS` is enabled. It exposes current socket containers, send-tracking entries, per-socket stats, and connected-node bitmap.

## Important APIs, types, and functions
Public hooks are `o2net_debug_add_nst`, `o2net_debug_del_nst`, `o2net_debug_add_sc`, `o2net_debug_del_sc`, `o2net_debugfs_init`, and `o2net_debugfs_exit`. Internal seq-file operations walk `send_tracking` and `sock_containers` lists under `o2net_debug_lock`; files are `send_tracking`, `sock_containers`, `stats`, and `connected_nodes`.

## Control flow
Networking code adds/removes live tracking and socket objects to debug lists. Opening a debugfs seq file allocates a dummy cursor object and inserts it into the same list to iterate safely. Show functions locate the next real object, format task/message timing for sends, socket endpoint and callback timing for sockets, CSV-like stats for tooling, or a simple connected-node bitmap.

## State and persistence behavior
State is runtime-only debugfs state: global lists, dummy per-open cursors, and formatted snapshots. It does not affect network behavior or persist across unload. With `CONFIG_OCFS2_FS_STATS` disabled, stats fields report zero.

## Dependencies and integration points
It depends on debugfs, seq_file, spinlocks with bottom halves disabled, O2NET internal structures from `tcp_internal.h`, nodemanager node names/numbers, socket internals, and optional stats instrumentation.

## Risks and test signals
Risks include list iteration races, dereferencing partially destroyed socket/send objects, holding the debug spinlock while formatting larger records, and tooling depending on the stats string version. Test signals include concurrent connection churn while reading debugfs files, send timeout diagnostics, stats reads with and without `CONFIG_OCFS2_FS_STATS`, connected-node bitmap correctness, and debugfs init/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/netdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.c

## Purpose
`nodemanager.c` implements the O2CB configfs cluster model and module lifecycle. It lets userspace create one cluster, define nodes with number/IP/port/local status, tune network timeouts and fence method, attach the heartbeat default group, and initialize/shutdown heartbeat, TCP, quorum callbacks, configfs, and sysfs.

## Important APIs, types, and functions
Exports include `o2nm_single_cluster`, `o2nm_get_node_by_num`, `o2nm_get_node_by_ip`, `o2nm_configured_node_map`, `o2nm_node_get`, `o2nm_node_put`, `o2nm_this_node`, `o2nm_depend_item`, `o2nm_undepend_item`, `o2nm_depend_this_node`, and `o2nm_undepend_this_node`. Configfs handlers manage node attributes (`num`, `ipv4_port`, `ipv4_address`, `local`) and cluster attributes (`idle_timeout_ms`, `keepalive_delay_ms`, `reconnect_delay_ms`, `fence_method`). Module init/exit are `init_o2nm` and `exit_o2nm`.

## Control flow
Module init initializes heartbeat, O2NET, heartbeat callbacks, configfs subsystem `cluster`, and `/sys/fs/o2cb`. Creating a cluster allocates cluster, node group, and heartbeat group; only one cluster is allowed. Creating a node allocates a config item; userspace must set address and port before node number, then can mark one node local, which starts listening. Dropping nodes disconnects network state, stops local listening if applicable, removes IP tree and bitmap entries, and releases the item. Dropping the cluster removes default groups and clears `o2nm_single_cluster`.

## State and persistence behavior
State is runtime configfs state: the single cluster pointer, node array, configured-node bitmap, IP rbtree, local-node flag, network timeout values, reconnect delay, and fence method. None is persisted by the kernel; userspace cluster tooling must recreate it after boot.

## Dependencies and integration points
It depends on configfs, rbtree, O2NET TCP helpers, heartbeat configfs allocation, O2CB sysfs, and masklog. Heartbeat and networking use nodemanager lookups and configfs dependency pins to keep local nodes/regions alive while active.

## Risks and test signals
Risks include singleton cluster assumptions, attribute ordering surprises, races between node deletion and heartbeat/network users, inability to change network timeouts after peers connect, duplicate IP/node numbers, local-node transitions, and fence-method misconfiguration. Test signals include configfs create/drop cycles, invalid attribute values, duplicate nodes/IPs, local listener start/stop, connected peer timeout-change rejection, module init unwind failures, and configfs dependency behavior under active heartbeat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.h

## Purpose
`nodemanager.h` defines the in-kernel O2CB node and cluster structures plus lookup/dependency APIs used by heartbeat, networking, and quorum.

## Important APIs, types, and functions
`enum o2nm_fence_method` selects reset or panic self-fencing. `struct o2nm_node` stores configfs identity, name, node number, IPv4 address/port, IP tree node, local flag, and set-attribute bitmap. `struct o2nm_cluster` stores the config group, local-node state, node array, node bitmap, IP rbtree, network timeout tuning, and fence method. It declares lookup, reference, configured-map, current-node, and configfs dependency helpers.

## Control flow
Cluster subsystems call lookup helpers to convert node numbers/IPs into refcounted config items and call dependency helpers to pin configfs items while active operations depend on them.

## State and persistence behavior
The header defines runtime-only configfs-backed state. The node bitmap is used by heartbeat to decide which disk slots to read, and the fence method controls quorum self-fencing behavior.

## Dependencies and integration points
It includes the userspace ABI limits from `ocfs2_nodemanager.h`, configfs, and rbtree. It is included by heartbeat, quorum, TCP networking, and nodemanager implementation.

## Risks and test signals
Risks are direct structure coupling across cluster modules, singleton cluster assumptions via `o2nm_single_cluster`, and stale configfs references. Test signals include node lookup by number/IP, dependency pin/unpin under deletion, and fence-method use by quorum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_heartbeat.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_heartbeat.h

## Purpose
`ocfs2_heartbeat.h` defines the on-disk heartbeat slot layout shared between kernel heartbeat code and tooling.

## Important APIs, types, and functions
`struct o2hb_disk_heartbeat_block` contains `hb_seq`, `hb_node`, padding, `hb_cksum`, `hb_generation`, and `hb_dead_ms`. Fields are little-endian where multibyte values are persisted.

## Control flow
Heartbeat threads read and write one block per node in a heartbeat region. They zero/compute `hb_cksum`, compare `hb_seq` movement and `hb_generation`, and use `hb_dead_ms` to detect threshold mismatches.

## State and persistence behavior
This structure is persistent shared-disk state. A nonzero generation identifies a running node instance; writing generation zero on clean shutdown signals departure.

## Dependencies and integration points
It depends only on kernel integer/endian types supplied by includers. `heartbeat.h` includes it for in-kernel APIs, and userspace-compatible consumers rely on this exact layout.

## Risks and test signals
Risks include layout changes breaking disk compatibility, endian mistakes, and stale slots after unclean shutdown. Test signals include CRC validation, clean generation-zero shutdown writes, cross-node dead-threshold mismatch detection, and compatibility with existing heartbeat regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_heartbeat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_nodemanager.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_nodemanager.h

## Purpose
`ocfs2_nodemanager.h` defines userspace-visible O2CB nodemanager constants and limits.

## Important APIs, types, and functions
It defines `O2NM_API_VERSION` as 5, `O2NM_MAX_NODES` and `O2NM_INVALID_NODE_NUM` as 255, `O2NM_MAX_NAME_LEN` as 64, and `O2NM_MAX_REGIONS` as 32.

## Control flow
The constants constrain configfs validation, heartbeat bitmaps/slot counts, sysfs interface revision reporting, and global heartbeat region allocation.

## State and persistence behavior
The header has no state. Changing these values affects runtime ABI and, for max regions, DLM compatibility.

## Dependencies and integration points
It is included by nodemanager and heartbeat headers and by sysfs revision code. Userspace cluster tools depend on the API version and limits.

## Risks and test signals
Risks are ABI breakage from changing constants, off-by-one treatment of node 255 as invalid, and exceeding DLM-compatible region limits. Test signals include configfs boundary values for node numbers, node names, and region count; sysfs `interface_revision`; and bitmap sizing builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/ocfs2_nodemanager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.c

## Purpose
`quorum.c` implements O2CB self-fencing decisions when heartbeat and network connectivity disagree. It prevents split-brain by fencing this node if it cannot communicate with a sufficient quorum of nodes that are still heartbeating.

## Important APIs, types, and functions
The global `o2quo_state` tracks heartbeating count/bitmap, connected count/bitmap, transition hold count/bitmap, pending decisions, and a work item. Public functions are `o2quo_init`, `o2quo_exit`, `o2quo_hb_up`, `o2quo_hb_down`, `o2quo_hb_still_up`, `o2quo_conn_up`, `o2quo_conn_err`, and `o2quo_disk_timeout`. `o2quo_fence_self` stops heartbeat regions and either panics or emergency-restarts according to nodemanager fence method.

## Control flow
Heartbeat up/down and network connection up/error events update bitmaps under a spinlock. Transition holds delay quorum decisions while a node is newly seen or connection fate is unresolved. When holds drain and a decision is pending, workqueue context runs `o2quo_make_decision`: odd-sized partitions require majority connectivity; even-sized half partitions require connectivity to the side containing the lowest active node. Disk heartbeat timeout fences immediately.

## State and persistence behavior
State is volatile in-memory cluster membership/connectivity. The only persistent side effect is indirect: fencing stops local writes by rebooting or panicking the machine. No state survives reboot.

## Dependencies and integration points
It depends on heartbeat callbacks, O2NET connection events, nodemanager fence configuration, workqueues, reboot/panic APIs, and masklog. Heartbeat write-timeout handling calls `o2quo_disk_timeout`.

## Risks and test signals
Risks include over-fencing during transient network races, stale hold counts blocking decisions, incorrect even-split lowest-node tie-breaks, null cluster state during fence, and heavy-handed local restart/panic. Test signals include two-node split, three-node majority/minority partitions, even half split with/without lowest active node, heartbeat-up before connection-up, connection-error while heartbeat remains up, hold drain scheduling, and disk timeout fencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.h

## Purpose
`quorum.h` declares the O2CB quorum interface used by heartbeat and networking.

## Important APIs, types, and functions
It declares lifecycle functions `o2quo_init` and `o2quo_exit`, heartbeat event functions `o2quo_hb_up`, `o2quo_hb_down`, `o2quo_hb_still_up`, network event functions `o2quo_conn_up`, `o2quo_conn_err`, and direct disk-timeout fencing `o2quo_disk_timeout`.

## Control flow
Heartbeat and TCP code notify quorum of membership/connectivity transitions. Quorum internally delays or schedules self-fence decisions based on those notifications.

## State and persistence behavior
The header has no state and exposes no structures. Implemented state is runtime-only and may lead to local panic/restart.

## Dependencies and integration points
It depends on node numbers (`u8`) and is included by heartbeat and networking modules.

## Risks and test signals
Risks are callers omitting paired up/down or conn_up/conn_err events and making quorum state inconsistent. Test signals include balanced event sequences, duplicate event BUG paths, and disk-timeout call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.c

## Purpose
`sys.c` creates the O2CB sysfs root under `/sys/fs/o2cb`, exposes the nodemanager interface revision, and attaches the logmask sysfs group.

## Important APIs, types, and functions
Public functions are `o2cb_sys_init` and `o2cb_sys_shutdown`. The `interface_revision` attribute is implemented by `version_show` and reports `O2NM_API_VERSION`.

## Control flow
Initialization creates the `o2cb` kset under `fs_kobj`, adds the interface revision group, then initializes masklog sysfs under the same kset. Shutdown unregisters masklog and the kset.

## State and persistence behavior
Runtime state is the `o2cb_kset` pointer and registered sysfs attributes. It is not persistent; userspace observes it while the module is loaded.

## Dependencies and integration points
It depends on kobject/sysfs APIs, `fs_kobj`, nodemanager ABI constants, and masklog sysfs initialization. `nodemanager.c` calls it during module init/exit.

## Risks and test signals
Risks include init unwind leaving partial sysfs state, shutdown ordering with masklog, and userspace depending on revision format. Test signals include module load/unload, sysfs read of `interface_revision`, masklog file presence, and simulated `sysfs_create_group`/`mlog_sys_init` failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.h

## Purpose
`sys.h` declares the O2CB sysfs lifecycle functions.

## Important APIs, types, and functions
It declares `o2cb_sys_init` and `o2cb_sys_shutdown`.

## Control flow
Nodemanager module initialization calls `o2cb_sys_init` after configfs registration; module exit calls `o2cb_sys_shutdown` before lower-level heartbeat/network teardown.

## State and persistence behavior
The header has no state. The implementation owns runtime sysfs kset state only.

## Dependencies and integration points
It is included by nodemanager and implemented by `sys.c`, binding module lifecycle to O2CB sysfs presence.

## Risks and test signals
Risks are limited to missing lifecycle calls or wrong init/exit ordering. Test signals include load/unload cycles and failure unwind coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.h -->
