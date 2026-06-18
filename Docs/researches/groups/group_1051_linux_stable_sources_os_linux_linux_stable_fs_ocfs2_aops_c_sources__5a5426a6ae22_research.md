# Group Research: group_1051_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_aops_c_sources__5a5426a6ae22

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/aops.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/aops.c

## Summary
Implements OCFS2 address-space operations for file data: block mapping, inline-data reads/writes, folio read/readahead/writeback, buffered write preparation/completion, mmap write preparation support, direct I/O mapping/completion, unwritten extent conversion, and exported `ocfs2_aops`.

## Main Responsibilities
- Translate logical file blocks/clusters to physical blocks through the extent map.
- Support special symlink mapping and inline-data file reads/writes.
- Coordinate page-cache reads, readahead, writepages, bmap, folio release, and migration hooks.
- Prepare buffered, mmap, and direct writes with cluster allocation, quota, journaling, COW, unwritten extent, and non-sparse-extension handling.
- Zero newly allocated or partially initialized regions to prevent stale data exposure.
- Track direct-I/O unwritten extents and finalize them after I/O completion.
- Maintain inode size, timestamps, block counts, dinode fields, and fsync transaction state after writes.

## Key Interfaces
- `ocfs2_get_block()` maps normal data and symlink data for buffer-head users.
- `ocfs2_read_inline_data()` and `ocfs2_size_fits_inline_data()` are shared inline-data helpers.
- `ocfs2_write_begin_nolock()` and `ocfs2_write_end_nolock()` are the reusable write core for buffered, mmap, and direct paths.
- `ocfs2_map_folio_blocks()` maps buffer heads within folios after extent decisions are already made.
- `ocfs2_direct_IO()` selects read/write get-block callbacks for `__blockdev_direct_IO()`.
- `ocfs2_aops` installs the address-space operation table.

## Important Behavior
`ocfs2_get_block()` never allocates. It maps existing extents, treats unwritten extents as holes for zeroing, marks buffers new only for writes past EOF, and rejects missing mappings on non-sparse files.

Buffered reads take the inode cluster lock and `ip_alloc_sem`, then choose inline-data reads or `block_read_full_folio()`. Readahead uses nonblocking inode locking and ignores difficult cases.

Writes allocate an `ocfs2_write_ctxt`, optionally keep data inline, zero sparse tails, expand non-sparse files, perform refcount COW, build per-cluster descriptors, lock allocators, start a journal transaction, grab all affected folios, allocate or mark extents written, map buffers, and later commit written ranges and inode metadata.

Direct writes use a custom `ocfs2_dio_write_ctxt`. Extending direct I/O may add the inode to the orphan directory before allocating blocks, then `ocfs2_dio_end_io_write()` converts unwritten extents, advances i_size, removes the orphan entry, and releases deferred metadata.

## State and Synchronization
The file relies on OCFS2 inode locks, rw locks held by higher file I/O paths, `ip_alloc_sem`, folio locks, buffer-head state, JBD2 handles, quota reservations, `ip_unwritten_list` under `ip_lock`, and cached deallocation contexts.

## Cross-File Interactions
It depends on extent mapping/allocation, inode locking, journaling, refcount COW, truncate-log freeing, orphan directory management, quota, and directory/sysfile helpers. `file.c`, mmap code, and other OCFS2 write paths call the nolock write helpers.

## Risks
The most sensitive areas are stale-data prevention during allocation failure, direct-I/O unwritten extent cleanup, orphan handling for extending DIO, inline-to-extent conversion, and lock ordering between page locks, journal locks, inode locks, and `ip_alloc_sem`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/aops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/aops.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/aops.h

## Summary
Declares the shared OCFS2 address-space helper API used by file, mmap, and direct-I/O paths, plus the small `kiocb->private` bit protocol used to release OCFS2 rw locks from direct-I/O completion.

## Main Responsibilities
- Expose folio block mapping and folio cleanup helpers.
- Expose the nolock write begin/end core and its caller type enum.
- Expose inline-data read/size helpers and generic `ocfs2_get_block()`.
- Define helper macros for tracking whether a direct-I/O `kiocb` owns an OCFS2 rw lock and at which level.

## Key Interfaces
- `ocfs2_write_type_t` distinguishes buffered, direct, and mmap writes.
- `ocfs2_write_begin_nolock()` and `ocfs2_write_end_nolock()` are the core reusable write lifecycle.
- `ocfs2_iocb_set_rw_locked()`, `ocfs2_iocb_clear_rw_locked()`, and `ocfs2_iocb_rw_locked_level()` encode DIO lock ownership in `iocb->private`.

## Risks
The `kiocb->private` bit use is compact but fragile: all participants must treat the pointer storage as bit flags while DIO is in progress, and completion must clear and unlock exactly once.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/aops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.c

## Summary
Implements OCFS2 metadata block integrity checking with CRC32 plus Hamming-code ECC. It can compute and validate checks for contiguous blocks or multi-buffer metadata, attempt single-bit recovery after CRC failure, and publish optional debugfs counters.

## Main Responsibilities
- Encode Hamming parity over one buffer or multiple data hunks.
- Locate and flip a single bad data bit from stored-vs-computed parity.
- Compute `struct ocfs2_block_check` fields in little-endian disk format.
- Validate checks, restore check fields after validation, and attempt ECC recovery.
- Maintain checked, failed, and recovered counters with spinlock protection.
- Install/remove debugfs statistics files when debugfs is enabled.
- Gate high-level metadata ECC operations on the mounted filesystem feature flag.

## Key Interfaces
- `ocfs2_hamming_encode()`, `ocfs2_hamming_fix()`, and block wrappers are the low-level ECC API.
- `ocfs2_block_check_compute()` and `ocfs2_block_check_validate()` handle one memory block.
- `ocfs2_block_check_compute_bhs()` and `ocfs2_block_check_validate_bhs()` handle arrays of buffer heads.
- `ocfs2_compute_meta_ecc*()` and `ocfs2_validate_meta_ecc*()` are feature-aware filesystem entry points.
- `ocfs2_blockcheck_stats_debugfs_install()` and `_remove()` expose counters.

## Important Behavior
Validation temporarily zeroes the embedded check structure, computes CRC32, and succeeds immediately if CRC matches. On mismatch, it computes Hamming parity, applies the XOR difference as a possible single-bit fix, recomputes CRC, and returns `-EIO` if recovery still fails.

Multi-buffer ECC preserves a continuous bit numbering across buffers by passing each buffer’s bit offset into the Hamming encoder/fixer.

## Risks
ECC correction assumes the failure is within the repairable Hamming model. Multi-bit corruption may not recover and must remain an I/O error. Callers must pass on-disk little-endian data and ensure embedded check fields are correctly zeroed or pointed to by `bc`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.h

## Summary
Declares OCFS2 block integrity APIs and the statistics structure used by `blockcheck.c`.

## Main Responsibilities
- Define `struct ocfs2_blockcheck_stats` counters and optional debugfs parent.
- Declare high-level metadata ECC compute/validate helpers.
- Declare low-level block and buffer-head check helpers.
- Declare debugfs install/remove routines.
- Declare Hamming encode/fix primitives and block wrappers.

## Key Interfaces
- `ocfs2_blockcheck_stats` tracks checks, checksum failures, and ECC recoveries.
- `ocfs2_compute_meta_ecc()` and `ocfs2_validate_meta_ecc()` operate on one metadata block.
- `_bhs` variants operate on multi-buffer metadata.
- `ocfs2_hamming_encode()` and `ocfs2_hamming_fix()` support incremental hunks.

## Risks
The header exposes both low-level and high-level APIs; callers need to choose the feature-gated metadata wrappers unless they intentionally bypass mount feature checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/blockcheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.c

## Summary
Implements OCFS2 metadata buffer-head I/O helpers. It handles synchronous metadata reads/writes, clustered metadata-cache uptodate state, optional validation of freshly read buffers, readahead handling, and non-journaled superblock/backup writes with ECC computation.

## Main Responsibilities
- Write a metadata buffer outside JBD2 while updating OCFS2’s metadata cache state.
- Read one or more blocks synchronously, allocating buffer heads when needed.
- Read through the clustered metadata cache with `IGNORE_CACHE` and `READAHEAD` modes.
- Mark freshly read buffers for validation and call a provided validator after I/O completion.
- Keep JBD-managed buffers from being read or written incorrectly.
- Write the main superblock or backup superblocks with metadata ECC.

## Key Interfaces
- `ocfs2_write_block()` writes one non-journaled metadata block.
- `ocfs2_read_blocks_sync()` performs direct synchronous multi-block reads.
- `ocfs2_read_blocks()` is the cache-aware read helper used broadly by metadata code.
- `ocfs2_write_super_or_backup()` validates target block identity and writes superblock data.

## Important Behavior
`ocfs2_read_blocks()` uses an OCFS2-specific `BH_NeedsValidate` buffer state bit. Validation is only run for buffers freshly read from disk, but readahead can set the flag so a later synchronous caller validates the completed buffer.

Read error cleanup is careful about ownership: if this helper allocated the buffer heads it drops and nulls them, while caller-supplied buffers have uptodate state cleared.

## State and Synchronization
Uses OCFS2 metadata cache I/O locks, buffer locks, local buffer uptodate/dirty state, clustered uptodate tracking from `uptodate.c`, and JBD2 buffer ownership checks.

## Risks
Correctness depends on not racing JBD2 ownership, preserving caller ownership of buffer-head arrays, and validating all disk-fresh metadata before trusting it. Superblock writes bypass journaling and therefore must only target the primary or known backup superblocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.h

## Summary
Declares OCFS2 buffer-head I/O helpers and read flags.

## Main Responsibilities
- Expose metadata block read/write helpers.
- Define `OCFS2_BH_IGNORE_CACHE` and `OCFS2_BH_READAHEAD`.
- Provide a single-block inline wrapper around `ocfs2_read_blocks()`.
- Document validator behavior for fresh disk reads.

## Key Interfaces
- `ocfs2_read_blocks()` accepts an optional validator invoked only for fresh disk I/O.
- `ocfs2_read_block()` is the common one-block helper.
- `ocfs2_write_super_or_backup()` is the specialized non-journaled superblock writer.

## Risks
Callers using validators must pass them for readahead too when later validation is required, because the helper uses a buffer state bit to remember validation need.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/Makefile

## Summary
Builds the OCFS2 cluster support module object when `CONFIG_OCFS2_FS` is enabled.

## Main Responsibilities
- Add `ocfs2_nodemanager.o` to the OCFS2 build.
- Compose that object from heartbeat, masklog, sysfs, nodemanager, quorum, tcp, and netdebug sources.

## Key Interfaces
- `obj-$(CONFIG_OCFS2_FS) += ocfs2_nodemanager.o`
- `ocfs2_nodemanager-objs := heartbeat.o masklog.o sys.o nodemanager.o quorum.o tcp.o netdebug.o`

## Risks
This file defines module composition boundaries. Missing an object here would silently remove cluster subsystem behavior from the OCFS2 module.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.c

## Summary
Implements O2CB disk heartbeat. It manages heartbeat configfs regions, per-region heartbeat kthreads, bio-based slot reads/writes, CRC-protected on-disk heartbeat blocks, live-node detection, node up/down callbacks, global heartbeat region/quorum tracking, write timeout fencing, timeout negotiation messages, debugfs reporting, and callback registration.

## Main Responsibilities
- Maintain global live-node, live-region, quorum-region, and failed-region bitmaps.
- Create and destroy heartbeat regions under the cluster configfs hierarchy.
- Open heartbeat block devices, map slot pages, seed slot state, and start/stop heartbeat kthreads.
- Periodically read configured node slots, write the local node slot, verify CRCs, and detect membership changes.
- Queue serialized node up/down callbacks for DLM, networking, and other cluster users.
- Detect stalled heartbeat writes and trigger quorum fencing when necessary.
- Support local and global heartbeat modes, including region pinning for dependent users.
- Expose heartbeat state through debugfs.

## Key Interfaces
- `o2hb_alloc_hb_set()` / `o2hb_free_hb_set()` provide the configfs heartbeat group.
- `o2hb_setup_callback()`, `o2hb_register_callback()`, and `o2hb_unregister_callback()` manage ordered callbacks.
- `o2hb_fill_node_map()` returns currently heartbeating nodes.
- `o2hb_check_node_heartbeating_*()` test node liveness in normal or callback contexts.
- `o2hb_stop_all_regions()`, `o2hb_get_all_regions()`, and `o2hb_global_heartbeat_active()` support cluster management.
- `o2hb_init()` / `o2hb_exit()` initialize global structures and debugfs.

## Important Behavior
A region becomes active when userspace writes a block-device fd to its `dev` configfs attribute after setting block size, start block, and slot count. The region opens the block device, maps one heartbeat slot per node, starts an `o2hb-*` thread, and waits until the thread reaches a steady state.

Each heartbeat pass reads configured slots, verifies the local slot still matches the previous write, prepares a new local slot with sequence time, node number, generation, dead timeout, and CRC, writes it synchronously, checks every slot for live/dead transitions, and rearms write-timeout work only after a good own-slot check.

A dead node becomes live after `O2HB_LIVE_THRESHOLD` changed samples. A live node becomes dead after `o2hb_dead_threshold` equal samples or generation change. First live region entry for a node emits an up callback; last region exit emits a down callback.

Global heartbeat promotes a region to quorum only after it sees all globally live nodes. Failed quorum regions can trigger fencing when enough write timeouts occur.

## State and Synchronization
Uses `o2hb_live_lock`, `o2hb_callback_sem`, configfs item references, kthreads, delayed work, per-region handler lists, bio completions, bitmaps, and node references from nodemanager.

## Cross-File Interactions
Calls nodemanager for configured/local nodes and configfs dependencies, tcp for timeout negotiation messages, quorum for disk timeout fencing, and masklog/debugfs for observability.

## Risks
Heartbeat is safety-critical. Bugs in slot ownership checks, CRC handling, steady-state waits, timeout arming, generation changes, global quorum accounting, or callback serialization can cause false node death, missed fencing, or unsafe concurrent filesystem access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.h

## Summary
Declares the O2CB heartbeat API, callback types, callback registration structure, and heartbeat timing constants.

## Main Responsibilities
- Define region timeout, live/dead thresholds, max region name length, and callback magic.
- Define node up/down callback event types.
- Define `struct o2hb_callback_func`.
- Expose heartbeat configfs group allocation, lifecycle, callback, liveness, and region utility APIs.

## Key Interfaces
- `o2hb_register_callback()` and `o2hb_unregister_callback()` connect cluster subsystems to node events.
- `o2hb_fill_node_map()` gives a serialized live-node bitmap.
- `o2hb_stop_all_regions()` is used before fencing or emergency shutdown paths.
- `o2hb_global_heartbeat_active()` reports the configured heartbeat mode.

## Risks
Callback users must initialize with `o2hb_setup_callback()` and respect callback-context locking expectations, especially when using `_from_callback()` helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.c

## Summary
Implements OCFS2/O2CB runtime log-mask control. It maintains global allow/deny masks, prints formatted masked log messages, and exposes per-mask sysfs attributes under the O2CB kset.

## Main Responsibilities
- Store global `mlog_and_bits` and `mlog_not_bits`.
- Convert each mask bit between `allow`, `deny`, and `off`.
- Print enabled messages with task, pid, CPU, function, line, severity, and formatted payload.
- Define sysfs attributes for every supported mask bit.
- Register/unregister the `logmask` kset.

## Key Interfaces
- `__mlog_printk()` is called by the `mlog()` macro after compile/runtime mask checks.
- `mlog_sys_init()` installs the sysfs logmask kset.
- `mlog_sys_shutdown()` unregisters it.

## Important Behavior
`ML_ERROR` maps to `KERN_ERR` with an `ERROR:` prefix, `ML_NOTICE` maps to `KERN_NOTICE`, and other enabled masks use `KERN_INFO`. A message is suppressed if its mask is not allowed or is explicitly denied.

## Risks
The sysfs mask table must stay aligned with mask definitions in `masklog.h`; adding a new bit requires updating both files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.h

## Summary
Defines OCFS2/O2CB masked logging categories, bit operations, and logging macros.

## Main Responsibilities
- Define log categories for TCP, messages, heartbeat, DLM, quorum, cluster, errors, notices, and kthreads.
- Define initial masks and debug/non-debug compile-time allowed bits.
- Provide efficient 32-bit and 64-bit `u64` mask operations.
- Declare global allow/deny masks and the print backend.
- Provide `mlog()`, `mlog_ratelimited()`, `mlog_errno()`, and `mlog_bug_on_msg()` macros.
- Declare sysfs logmask lifecycle functions.

## Key Interfaces
- `mlog(mask, fmt, ...)` is the primary cluster logging macro.
- `mlog_errno()` suppresses common non-error control returns such as restart, interrupt, ENOSPC, and EDQUOT.
- `mlog_bug_on_msg()` logs context before `BUG()`.

## Risks
Compile-time filtering depends on `ML_ALLOWED_BITS`; non-error masks compile away unless `CONFIG_OCFS2_DEBUG_MASKLOG` is enabled. Developers adding new categories must update `masklog.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/masklog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/netdebug.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/netdebug.c

## Summary
Implements debugfs reporting for O2NET socket containers, active send tracking, connection statistics, and connected-node bitmaps when `CONFIG_DEBUG_FS` is enabled.

## Main Responsibilities
- Maintain debug-only lists of active `o2net_send_tracking` and `o2net_sock_container` objects.
- Provide seq_file iteration over active sends and sockets using dummy cursor objects.
- Report send wait timings, task identity, node, message id/type/key, and socket container pointers.
- Report socket connection details, krefs, endpoints, remote node, message handling state, and timing fields.
- Report compact CSV-style stats when `CONFIG_OCFS2_FS_STATS` is enabled.
- Expose connected-node bitmap through a simple debugfs file.
- Create/remove the `o2net` debugfs directory and files.

## Key Interfaces
- `o2net_debug_add_nst()` / `_del_nst()` track in-flight sends.
- `o2net_debug_add_sc()` / `_del_sc()` track socket containers.
- `o2net_debugfs_init()` creates `send_tracking`, `sock_containers`, `stats`, and `connected_nodes`.
- `o2net_debugfs_exit()` removes the tree.

## State and Synchronization
Uses `o2net_debug_lock` with bottom halves disabled around debug lists and seq iteration. Snapshot buffers for connected nodes are allocated at file open.

## Risks
This is diagnostic-only but reads live network structures under a debug spinlock. Output formats are consumed by tools such as `debugfs.ocfs2`, so field order and stats string version matter.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/netdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.c

## Summary
Implements the O2CB nodemanager module and configfs cluster hierarchy. It manages the single active cluster, node configuration, local node activation, IP lookup, network timing attributes, fence method selection, heartbeat group attachment, subsystem dependencies, and module init/exit ordering.

## Main Responsibilities
- Maintain `o2nm_single_cluster` and enforce one active cluster.
- Provide node lookup by node number and IPv4 address with config item references.
- Maintain configured-node bitmap and IP rbtree.
- Create configfs cluster, node, and default heartbeat groups.
- Validate and store node number, IPv4 port, IPv4 address, and local-node flag.
- Start/stop O2NET listening when the local node is enabled/disabled.
- Expose cluster network timing and fencing attributes.
- Pin/unpin configfs items for heartbeat-dependent users.
- Initialize heartbeat, networking, configfs, and O2CB sysfs in module init.

## Key Interfaces
- `o2nm_get_node_by_num()`, `o2nm_get_node_by_ip()`, `o2nm_node_get()`, and `o2nm_node_put()`.
- `o2nm_this_node()` returns the configured local node or invalid node number.
- `o2nm_configured_node_map()` returns the cluster node bitmap.
- `o2nm_depend_item()`, `o2nm_undepend_item()`, `o2nm_depend_this_node()`, and `_undepend_this_node()` wrap configfs dependencies.
- Module init/exit: `init_o2nm()` and `exit_o2nm()`.

## Important Behavior
A node cannot publish its node number until address and port are set, because network code can immediately resolve it. Address insertion rejects duplicates through the rbtree. Setting `local=1` requires all other node attributes and starts the network listener; clearing it stops listening.

Cluster timeout values cannot be changed after peers are connected if they would break negotiated timing. Keepalive must remain below idle timeout. Fence method accepts `reset` or `panic`.

Dropping a node disconnects it, stops local listening if applicable, removes its IP tree entry and node bitmap entry, and releases the config item.

## State and Synchronization
Uses the configfs subsystem mutex for structural changes and `cl_nodes_lock` for node arrays, bitmaps, and IP tree. Node config items provide lifetime references.

## Cross-File Interactions
Creates the heartbeat configfs group from `heartbeat.c`, starts O2NET listeners from `tcp.c`, exposes sysfs through `sys.c`, and uses masklog for cluster diagnostics.

## Risks
The single-cluster global simplifies lookup but means all users assume `o2nm_single_cluster` stability. Node attribute ordering, local-node transitions, configfs dependency lifetimes, and network listener start/stop are the main correctness boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.h

## Summary
Defines internal O2CB nodemanager structures and exported lookup/dependency APIs.

## Main Responsibilities
- Define fencing method enum.
- Define `struct o2nm_node` with configfs item, name, node number, IPv4 address/port, rbtree node, local flag, and attribute bitmap.
- Define `struct o2nm_cluster` with configfs group, local-node state, node lock, node table, IP tree, timeouts, fence method, and node bitmap.
- Declare the single active cluster pointer and public nodemanager helpers.

## Key Interfaces
- `o2nm_this_node()` reports local identity.
- Node lookup and ref helpers are used by heartbeat and network code.
- Configfs dependency helpers protect node/region items from removal while active.

## Risks
The structs are shared across cluster code, so lock discipline around `cl_nodes_lock` and configfs item references is essential.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_heartbeat.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_heartbeat.h

## Summary
Defines the on-disk heartbeat block layout shared by kernel heartbeat code and userspace-facing OCFS2 cluster tooling.

## Main Responsibilities
- Define `struct o2hb_disk_heartbeat_block`.
- Store heartbeat sequence, node number, CRC checksum, generation, and dead timeout in disk-endian fields.

## Key Interfaces
- `hb_seq` is the changing heartbeat value.
- `hb_node` records the node slot owner.
- `hb_cksum` protects the block.
- `hb_generation` distinguishes node restart/rejoin cycles.
- `hb_dead_ms` advertises the node’s dead timeout expectation.

## Risks
This is an on-disk ABI. Field layout or size changes would affect compatibility with existing heartbeat regions and tooling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_heartbeat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_nodemanager.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_nodemanager.h

## Summary
Defines userspace/kernel constants for the OCFS2 nodemanager interface.

## Main Responsibilities
- Publish nodemanager API version.
- Define maximum node count and invalid node number.
- Define maximum cluster/node/host name length.
- Define maximum global heartbeat regions.

## Key Interfaces
- `O2NM_API_VERSION` is exposed through `/sys/fs/o2cb/interface_revision`.
- `O2NM_MAX_NODES` and `O2NM_INVALID_NODE_NUM` are both 255.
- `O2NM_MAX_REGIONS` is 32 and documented as DLM compatibility-sensitive.

## Risks
These constants form ABI and protocol limits. Changing max regions or node numbering can break DLM and userspace compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_nodemanager.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.c

## Summary
Implements O2CB quorum/fencing decisions based on heartbeat and network connectivity state. It fences the local node when it cannot reach a sufficient set of nodes that are still heartbeating.

## Main Responsibilities
- Track heartbeating nodes, connected nodes, and nodes in transitional hold states.
- Delay quorum decisions while heartbeat and connection state is racing.
- Decide whether the local node must fence itself after connection loss.
- Fence by stopping all heartbeat regions and either panicking or emergency restarting.
- React immediately to heartbeat disk write timeout.

## Key Interfaces
- `o2quo_hb_up()`, `o2quo_hb_down()`, and `o2quo_hb_still_up()` are called from heartbeat/network recovery logic.
- `o2quo_conn_up()` and `o2quo_conn_err()` track network connectivity.
- `o2quo_disk_timeout()` fences on local heartbeat write timeout.
- `o2quo_init()` and `o2quo_exit()` initialize/flush quorum work.

## Important Behavior
For odd-sized heartbeating sets, the node fences if it cannot connect to a majority. For even-sized sets, a half-quorum is only allowed if it includes the lowest-numbered live node; otherwise the node fences to break split brain.

Holds defer decisions while a node has started heartbeating but is not connected, or while a connection failed but heartbeat has not yet resolved whether the peer is really gone.

## State and Synchronization
Uses a single static `o2quo_state`, `spin_lock_bh()`, bitmaps for heartbeat/connection/hold state, a pending flag, and a work item for decisions outside event paths.

## Risks
This is intentionally heavy-handed and safety-critical. Incorrect hold accounting or bitmap transitions can cause premature self-fencing or failure to fence during split brain.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.h

## Summary
Declares the O2CB quorum lifecycle and event API.

## Main Responsibilities
- Expose init/exit functions.
- Expose heartbeat up/down/still-up event hooks.
- Expose connection up/error event hooks.
- Expose disk timeout fencing hook.

## Key Interfaces
- Heartbeat code calls the heartbeat-related hooks.
- Network code calls connection-related hooks.
- Heartbeat write timeout calls `o2quo_disk_timeout()`.

## Risks
Callers must deliver paired state transitions accurately; quorum correctness depends on event ordering and hold release.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.c

## Summary
Implements the O2CB sysfs root under `fs_kobj`, exposing the nodemanager interface revision and installing the logmask sysfs tree.

## Main Responsibilities
- Create `/sys/fs/o2cb`.
- Expose `interface_revision` from `O2NM_API_VERSION`.
- Create the default O2CB attribute group.
- Initialize and shut down masklog sysfs support.
- Unregister the O2CB kset on shutdown or init failure.

## Key Interfaces
- `o2cb_sys_init()` creates sysfs state and calls `mlog_sys_init()`.
- `o2cb_sys_shutdown()` shuts down masklog and unregisters the kset.

## Risks
Init error handling unregisters the kset but does not separately remove a partially created attribute group. Shutdown ordering matters because masklog is parented under the O2CB kset.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.h

## Summary
Declares the O2CB sysfs lifecycle API.

## Main Responsibilities
- Provide include guard for cluster sysfs declarations.
- Declare `o2cb_sys_init()` and `o2cb_sys_shutdown()`.

## Key Interfaces
- Nodemanager module init calls `o2cb_sys_init()`.
- Nodemanager module exit calls `o2cb_sys_shutdown()`.

## Risks
Small lifecycle header; correctness depends on callers preserving init/exit ordering with masklog and configfs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.h -->