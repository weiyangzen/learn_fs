# Group Research: group_809_linux_sources_os_linux_linux_fs_ocfs2_aops_c_sources_os_linux_linux__f7236e612068

Scope: `Docs/research_subset_a.md` / source tree `sources/os/linux/linux`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/aops.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/aops.c

OCFS2 address-space operations implementation. This file connects Linux VFS/page-cache operations to OCFS2 extent mapping, inline-data handling, journaling, quota accounting, direct I/O completion, and cluster-safe inode locking.

Key exported/global interfaces:
- `const struct address_space_operations ocfs2_aops`: installs OCFS2 handlers for read, readahead, writepages, buffered writes, bmap, direct I/O, invalidation, release, migration, and partial-uptodate checks.
- `ocfs2_get_block()`: maps logical file blocks to physical blocks through the OCFS2 extent map. It treats sparse holes and unwritten extents carefully and never allocates here.
- `ocfs2_read_inline_data()` and `ocfs2_size_fits_inline_data()`: helpers for inline-data files.
- `ocfs2_map_folio_blocks()`, `ocfs2_write_begin_nolock()`, `ocfs2_write_end_nolock()`, and `ocfs2_unlock_and_free_folios()`: shared write-path helpers used by buffered, mmap, and direct write paths.
- `walk_page_buffers()`: ext3-derived helper for iterating buffer_heads in a page range.

Major behavior:
- Symlink block mapping is special-cased through `ocfs2_symlink_get_block()`, including a buffer-cache-to-page-cache copy for newly created symlinks whose data may still be journaled.
- Read path takes the inode cluster lock and `ip_alloc_sem`; `read_folio` handles inline-data files and zeroes folios beyond updated `i_size` after remote truncation.
- Readahead uses nonblocking inode locking and skips inline data, remote truncation, and allocation semaphore contention.
- Writeback delegates to `mpage_writepages()` with `ocfs2_get_block()`, relying on preexisting block mappings for dirty pages.
- `bmap` refuses refcounted inodes because swap-style bypass I/O cannot safely interact with CoW/refcount semantics.
- Buffered writes allocate and populate an `ocfs2_write_ctxt`, possibly convert inline data to extents, zero sparse tails or expand nonsparse files, CoW refcounted extents, lock allocators, start transactions, prepare folios, allocate/write clusters, update inode size/timestamps, and commit journal state.
- Direct writes use `ocfs2_dio_wr_get_block()` to allocate/map one cluster-sized range at a time, may add growing writes to the orphan directory, and defer unwritten extent conversion plus `i_size` updates to `ocfs2_dio_end_io_write()`.
- Unwritten extent coordination uses inode-local `ip_unwritten_list` plus per-write/per-DIO lists to avoid double-zeroing and defer `OCFS2_EXT_UNWRITTEN` clearing until I/O completion.
- Inline writes are attempted for empty or already-inline files when the write fits and is not mmap-based; otherwise the inode is converted to extents.

Important invariants and locking:
- Extent lookups and modifications are serialized with `OCFS2_I(inode)->ip_alloc_sem`; normal buffered writes take it for write, reads take it for read.
- Metadata changes require inode cluster locks and journal access to the dinode buffer.
- Write context folios are unlocked before cached deallocs run to avoid journal transaction barrier deadlocks.
- Direct-I/O end completion expects the submitting iocb to retain an OCFS2 rw-lock bit in `iocb->private`; completion clears the bit and unlocks.
- Newly allocated or partially failed write ranges are zeroed and marked dirty/uptodate to avoid stale data exposure.
- Sparse holes in `ocfs2_get_block()` are treated as holes if sparse allocation is enabled; holes on nonsparse files are logged as corruption-like I/O errors.

Dependencies:
- Core OCFS2 modules: allocation, extent map, inode, journal, suballoc, super, refcount tree, directory/namei/sysfile helpers.
- Linux helpers: buffer_head, folios, mpage, direct I/O, quota, block device, page cache, JBD2 handles.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/aops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/aops.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/aops.h

Header for OCFS2 address-space operation helpers shared with other OCFS2 files.

Key declarations:
- `ocfs2_map_folio_blocks()`, `ocfs2_unlock_and_free_folios()`, `walk_page_buffers()`.
- `ocfs2_write_begin_nolock()` / `ocfs2_write_end_nolock()` for nonstandard write flows such as mmap and direct I/O.
- `ocfs2_read_inline_data()`, `ocfs2_size_fits_inline_data()`, and `ocfs2_get_block()`.
- `ocfs2_write_type_t` distinguishes buffered, direct, and mmap write callers.

Direct-I/O lock state:
- Defines bit helpers storing OCFS2 rw-lock state in `kiocb->private`.
- `OCFS2_IOCB_RW_LOCK` tracks whether a lock is held.
- `OCFS2_IOCB_RW_LOCK_LEVEL` stores lock level.
- These helpers are paired with `ocfs2_dio_end_io()` in `aops.c` and file read/write paths.

Notable issue:
- The include guard closes with comment `OCFS2_FILE_H`, while the guard name is `OCFS2_AOPS_H`; cosmetic only.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/aops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/blockcheck.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/blockcheck.c

Implements metadata CRC32 and Hamming-code ECC for OCFS2 metadata blocks and buffer_head lists.

Core algorithms:
- `calc_code_bit()` maps 0-based data bit offsets into 1-based Hamming-code positions, skipping parity positions.
- `ocfs2_hamming_encode()` computes parity over one hunk and supports chained calls across multiple buffers.
- `ocfs2_hamming_fix()` flips the data bit identified by a parity mismatch, ignoring pure parity-bit errors and hunks not containing the bad bit.
- Block wrappers provide single-buffer convenience APIs.

Block check APIs:
- `ocfs2_block_check_compute()` zeroes the embedded `struct ocfs2_block_check`, computes CRC32 and ECC over on-disk-format data, and stores little-endian results.
- `ocfs2_block_check_validate()` verifies CRC first, then attempts one-bit ECC repair and rechecks CRC.
- `_bhs` variants compute and validate checks over multiple buffer_heads as one logical block stream.
- High-level `ocfs2_compute_meta_ecc*()` and `ocfs2_validate_meta_ecc*()` call the low-level routines only when the mounted filesystem advertises metadata ECC.

Debug/observability:
- Optional debugfs support exposes `blocks_checked`, `checksums_failed`, and `ecc_recoveries`.
- Stats increments are spinlock-protected and log wraparound.

Important invariants:
- Metadata passed in must already be in on-disk endian form.
- The check structure is expected to be inside the data or equivalent fields must already be zeroed by the caller.
- ECC is asserted to fit in 16 bits because OCFS2 ECC-covered metadata structures are no larger than 4 KiB.
- Failed ECC repair returns `-EIO` after restoring the original check fields.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/blockcheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/blockcheck.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/blockcheck.h

Public declarations for OCFS2 metadata checksum/ECC support.

Defines:
- `struct ocfs2_blockcheck_stats`: spinlock-protected counters for checked blocks, checksum failures, ECC recoveries, plus optional debugfs directory state.

Declares:
- High-level metadata ECC APIs gated by filesystem feature state.
- Low-level compute/validate APIs for single buffers and buffer_head arrays.
- Debugfs install/remove hooks.
- Hamming encode/fix helpers for single or multi-hunk buffers.

Usage expectations:
- Callers pass disk-format data.
- Validation APIs may mutate the data buffer when ECC repair is attempted.
- Stats are optional; all increment helpers tolerate `NULL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/blockcheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/buffer_head_io.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/buffer_head_io.c

OCFS2 buffer_head read/write helper implementation. It layers OCFS2 clustered metadata-cache state and validation over Linux buffer_head I/O.

Key functions:
- `ocfs2_write_block()`: synchronous nonjournaled metadata write for system-file style buffers. It rejects hard-readonly mounts, marks the buffer uptodate, clears dirty state, submits write I/O, waits, and updates OCFS2’s metadata uptodate cache on success.
- `ocfs2_read_blocks_sync()`: simple synchronous read of a contiguous block range without clustered cache validation.
- `ocfs2_read_blocks()`: main cached metadata read routine. It honors `OCFS2_BH_IGNORE_CACHE`, `OCFS2_BH_READAHEAD`, JBD-owned buffers, dirty buffers, OCFS2 clustered uptodate state, and optional validation callbacks.
- `ocfs2_write_super_or_backup()`: writes the primary or backup superblock directly, computes metadata ECC first, and refuses emergency readonly state.

Internal state:
- Defines `BH_NeedsValidate` as an OCFS2-private buffer state bit after JBD private bits.
- `NeedsValidate` is set when a freshly submitted read must later run the caller’s validation callback.

Important behavior:
- Caller-provided `bhs[]` must contain either all `NULL` or all non-`NULL` entries; allocation and cleanup logic depends on that.
- On read failure, newly allocated buffer_heads are put and nulled; externally supplied uptodate buffers have uptodate cleared.
- Readahead does not wait for completion but still records buffers in the OCFS2 uptodate cache.
- Buffers owned by JBD are skipped because the journal controls their state.
- Superblock writes verify the block number is the primary or a known backup and do not use the metadata cache lock path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/buffer_head_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/buffer_head_io.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/buffer_head_io.h

Header for OCFS2 buffer_head I/O helpers.

Declares:
- `ocfs2_write_block()`.
- `ocfs2_read_blocks_sync()`.
- `ocfs2_read_blocks()` with optional validation callback.
- `ocfs2_write_super_or_backup()`.

Defines:
- `OCFS2_BH_IGNORE_CACHE`: force disk read instead of clustered metadata cache.
- `OCFS2_BH_READAHEAD`: submit best-effort metadata readahead.
- `ocfs2_read_block()` inline wrapper for a single-block cached read.

Contract:
- Validation callbacks are invoked only for freshly read buffers, not cache hits.
- Readahead callers still need to pass validation callbacks so the buffer can be marked for later validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/buffer_head_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/Makefile -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/Makefile

Build rules for the OCFS2 cluster/nodemanager module.

Behavior:
- Builds `ocfs2_nodemanager.o` when `CONFIG_OCFS2_FS` is enabled.
- Links object components: `heartbeat.o`, `masklog.o`, `sys.o`, `nodemanager.o`, `quorum.o`, `tcp.o`, and `netdebug.o`.

Significance:
- The cluster support is packaged as the nodemanager module but includes heartbeat, network transport, quorum, sysfs, and debug components.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.c

OCFS2 disk heartbeat implementation. It maintains heartbeat regions, writes this node’s heartbeat block, reads peer slots, generates node up/down callbacks, manages local/global heartbeat modes, and triggers self-fencing on write timeout/quorum failure.

Global state:
- Live-node state: `o2hb_live_slots[]`, `o2hb_live_node_bitmap`, node event queue, and callback semaphore.
- Global heartbeat region bitmaps: configured, live, quorum, and failed regions.
- Heartbeat mode: local or global; can only change before regions exist.
- Dependent users pin heartbeat regions to prevent configfs removal while DLM/user dependencies exist.

Region model:
- `struct o2hb_region` is a configfs item and owns one heartbeat thread, block-device file, slot pages, per-slot state, debugfs files, timeout work, negotiation work, live-node bitmap, and message handlers.
- `struct o2hb_disk_slot` tracks per-node raw slot data, last sequence/generation, live-list membership, and sample counters.

Heartbeat loop:
- `o2hb_thread()` depends the local node, repeatedly runs `o2hb_do_disk_heartbeat()`, sleeps so writes occur at the configured interval, and on clean stop writes generation zero as explicit down notification.
- `o2hb_do_disk_heartbeat()` reads configured/live peer slots, checks own slot integrity, prepares this node’s block, submits this node’s write, evaluates peer slots, waits for write completion, and arms timeout monitoring after steady state.
- Slot liveness requires `O2HB_LIVE_THRESHOLD` changed samples to become live and `o2hb_dead_threshold` equal samples or generation change to become dead.
- CRC protects each heartbeat block; bad CRC from a live node is treated as a transient miss.

Timeout and fencing:
- `o2hb_write_timeout()` logs heartbeat write timeout and calls `o2quo_disk_timeout()` unless global-heartbeat failed-region count is still below half of quorum regions.
- Negotiation work handles the case where all nodes may be stuck on a region; the lowest live node acts as master and can approve timeout extension/rearming.
- `o2hb_arm_timeout()` schedules write timeout and negotiation timeout only after steady state.

Configfs:
- The heartbeat group creates region items.
- Region attributes: `block_bytes`, `start_block`, `blocks`, `dev`, and read-only `pid`.
- Writing `dev` is the commit point: opens the block device, validates sector size and configured params, allocates slot pages, populates baseline data, starts the heartbeat thread, waits for steady state, and marks the region live in global mode.
- Heartbeat group attributes: `dead_threshold` and `mode`.
- Dropping a region stops its thread, clears global bitmaps, wakes pending start, and adjusts pinning.

Callbacks:
- `o2hb_setup_callback()`, `o2hb_register_callback()`, and `o2hb_unregister_callback()` provide priority-ordered node up/down callbacks.
- Callback execution is serialized by `o2hb_callback_sem`.
- `o2hb_fill_node_map()` gives callers a live-node snapshot serialized against callback changes.

Global/local heartbeat:
- Local mode pins only the region matching a domain/region UUID.
- Global mode assigns region numbers, tracks quorum regions, pins all active regions when dependent users exist and quorum-region count is small, and can unpin when enough quorum regions exist.

Debug:
- Optional debugfs directory `o2hb` exposes global live nodes, live regions, quorum regions, failed regions, plus per-region live nodes, region number, elapsed timeout time, and pinned state.

Exported interfaces:
- `o2hb_fill_node_map`, callback setup/register/unregister, heartbeat checks, stop-all-regions, get-all-regions, and global heartbeat mode query.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.h

Public cluster heartbeat header.

Defines:
- Heartbeat interval and thresholds: `O2HB_REGION_TIMEOUT_MS`, `O2HB_LIVE_THRESHOLD`, default/min dead threshold, and max write timeout expression.
- Region name length and callback magic.
- Callback types: node down and node up.
- `struct o2hb_callback_func` with list node, callback pointer, data, priority, type, and magic.

Declares:
- Heartbeat configfs group allocation/free.
- Callback setup/register/unregister APIs.
- Live-node map and node-heartbeating checks.
- Init/exit, stop-all-regions, get-all-regions, and global-heartbeat query.

Important dependency:
- Includes `ocfs2_heartbeat.h` for the on-disk heartbeat block layout.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/masklog.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/masklog.c

Runtime-configurable logging mask implementation for OCFS2/O2CB cluster code.

State:
- `mlog_and_bits`: masks explicitly allowed, initialized to errors and notices.
- `mlog_not_bits`: masks explicitly denied.
- Both are exported GPL symbols.

Logging:
- `__mlog_printk()` checks allow/deny masks, selects kernel log level, prefixes errors, and prints task name, pid, CPU, function, line, and formatted message.

Sysfs:
- Creates one attribute per mask bit under the O2CB logmask kset.
- Each attribute supports `allow`, `deny`, and `off`.
- `mlog_sys_init()` attaches the `logmask` kset under the O2CB kset.
- `mlog_sys_shutdown()` unregisters it.

Mask attributes:
- Covers TCP, MSG, SOCKET, HEARTBEAT, HB_BIO, DLMFS, DLM, DLM_DOMAIN, DLM_THREAD, DLM_MASTER, DLM_RECOVERY, DLM_GLUE, VOTE, CONN, QUORUM, BASTS, CLUSTER, ERROR, NOTICE, and KTHREAD.

Concurrency:
- Updates to global mask words are plain bit operations without explicit locking; this logging path favors low overhead.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/masklog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/masklog.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/masklog.h

OCFS2 cluster logging mask header.

Defines:
- 64-bit mask constants for cluster subsystems and high-priority error/notice/kthread messages.
- Initial allow mask: `ML_ERROR | ML_NOTICE`.
- Compile-time filtering via `CONFIG_OCFS2_DEBUG_MASKLOG`; without it, only error and notice masks survive the inline test.
- `struct mlog_bits` and architecture-specific helpers for 32-bit and 64-bit `unsigned long`.

Macros:
- `mlog(mask, fmt, ...)`: fast-path mask test, then calls `__mlog_printk()`.
- `mlog_ratelimited()`: local ratelimit wrapper around `mlog`.
- `mlog_errno(st)`: logs most unexpected negative statuses but suppresses common control-flow errors.
- `mlog_bug_on_msg()`: logs condition and message before `BUG()`.

Declares:
- Global allow/deny masks.
- `__mlog_printk()`.
- Sysfs init/shutdown functions.

Operational notes:
- New mask flags must be added to both this header and `masklog.c`.
- `MLOG_MASK_PREFIX` lets files assign a subsystem prefix before including this header.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/masklog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/netdebug.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/netdebug.c

Debugfs support for O2Net, compiled only with `CONFIG_DEBUG_FS`.

Debugfs files:
- `o2net/send_tracking`: active message-send tracking records.
- `o2net/sock_containers`: detailed socket container state.
- `o2net/stats`: compact CSV-like socket statistics for tooling.
- `o2net/connected_nodes`: bitmap-style list of connected node numbers.

Tracking lists:
- Maintains `sock_containers` and `send_tracking` under `o2net_debug_lock`.
- `o2net_debug_add_nst()` / `del_nst()` add and remove send tracking records.
- `o2net_debug_add_sc()` / `del_sc()` add and remove socket containers.

Seq-file implementation:
- Uses dummy tracking/container records inserted into the lists to support iteration while real objects may be added/removed.
- Show functions take the debug lock while reading object fields.
- Socket details include refs, IPv4 endpoints, remote node name, page offset, handshake state, timing fields, current message key/type.
- Stats output version is `O2NET_STATS_STR_VERSION == 1`.

Init/exit:
- `o2net_debugfs_init()` creates the directory and files.
- `o2net_debugfs_exit()` removes the subtree.

Dependency:
- Reads internals from `tcp_internal.h`, so this is tightly coupled to O2Net transport structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/netdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.c

OCFS2 cluster nodemanager module. It owns the O2CB configfs cluster hierarchy, singleton cluster registry, node definitions, local-node activation, heartbeat group attachment, sysfs initialization, and module lifecycle.

Global model:
- `o2nm_single_cluster` enforces one active cluster at a time.
- Cluster tracks node array, node bitmap, IPv4 address rb-tree, local-node state, O2Net timing settings, and fence method.

Lookup/exported helpers:
- `o2nm_get_node_by_num()` and `o2nm_get_node_by_ip()` return config-item-referenced nodes.
- `o2nm_configured_node_map()` copies the configured node bitmap.
- `o2nm_this_node()` returns the local node number or invalid node.
- `o2nm_node_get()` / `o2nm_node_put()` wrap config item refs.
- `o2nm_depend_item()` / `undepend_item()` and local-node depend helpers integrate with configfs dependency pinning.

Node configfs:
- Node attributes: `num`, `ipv4_port`, `ipv4_address`, `local`.
- Address and port must be set before node number.
- Setting node number inserts the node into `cl_nodes[]` and bitmap.
- IPv4 address store validates dotted-quad input and inserts into an rb-tree to prevent duplicates.
- Setting `local=1` requires address, port, and number, then starts O2Net listening. Clearing local stops listening for that node.
- Dropping a node disconnects O2Net, stops listening if it was local, erases rb-tree and bitmap entries, and releases the config item.

Cluster configfs:
- Cluster attributes: `idle_timeout_ms`, `keepalive_delay_ms`, `reconnect_delay_ms`, `fence_method`.
- Idle and keepalive timeouts cannot change after peers are connected and must maintain idle > keepalive.
- Fence method supports `reset` and `panic`.

Hierarchy:
- Top-level configfs subsystem name: `cluster`.
- Creating a cluster creates default `node` and `heartbeat` groups.
- Only one cluster can exist; creating a second returns `-ENOSPC`.
- Dropping the cluster removes default groups and clears the singleton pointer.

Module lifecycle:
- `init_o2nm()` initializes heartbeat, O2Net, heartbeat callbacks, configfs subsystem, and O2CB sysfs.
- Exit unregisters heartbeat callbacks, configfs subsystem, sysfs, O2Net, and heartbeat.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.h

Internal nodemanager header.

Defines:
- Fence methods: reset and panic.
- `struct o2nm_node`: configfs item, name, node number, one IPv4 address/port, rb-tree node, local flag, attribute-set bitmap, and lock.
- `struct o2nm_cluster`: configfs group, local-node state, node lock, node array, IP rb-tree, O2Net timeout settings, fence method, and configured-node bitmap.

Declares:
- Singleton cluster pointer.
- Local-node query, configured-node bitmap copy, node lookup by number/IP, node get/put.
- Configfs dependency helpers used by heartbeat to pin nodes/regions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_heartbeat.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_heartbeat.h

Userspace/kernel shared on-disk heartbeat structure header.

Defines:
- `struct o2hb_disk_heartbeat_block`:
  - `hb_seq`: heartbeat sequence timestamp.
  - `hb_node`: node number.
  - padding.
  - `hb_cksum`: CRC32 over the heartbeat block with checksum field zeroed.
  - `hb_generation`: nonzero generation distinguishing region starts/stops.
  - `hb_dead_ms`: advertised dead timeout in milliseconds.

Usage:
- Written and read by `heartbeat.c` in each node’s disk slot.
- Generation zero is used as clean down notification.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_heartbeat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_nodemanager.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_nodemanager.h

Userspace/kernel shared nodemanager constants.

Defines:
- `O2NM_API_VERSION` as 5.
- Maximum nodes: 255.
- Invalid node number: 255.
- Maximum node/host/group/cluster name length: 64.
- Maximum global heartbeat regions: 32, with compatibility warning.

Usage:
- Included by nodemanager and heartbeat headers.
- Exposed through sysfs interface revision in `sys.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/ocfs2_nodemanager.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/quorum.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/quorum.c

OCFS2 quorum and self-fencing logic. It decides whether this node must fence itself when heartbeat and network connectivity disagree.

State:
- `o2quo_state` tracks heartbeating nodes, connected nodes, nodes holding quorum decisions, pending decision state, and a work item.
- Protected by `qs_lock`.

Fencing:
- `o2quo_fence_self()` stops all heartbeat regions, then either panics or emergency-restarts depending on cluster fence method.
- `o2quo_disk_timeout()` fences immediately after heartbeat disk write timeout.

Decision logic:
- `o2quo_make_decision()` runs asynchronously when holds drain.
- If this node is not heartbeating or is the only heartbeating node, no fence occurs.
- Odd-sized heartbeat set: this node must be connected to majority.
- Even-sized heartbeat set: this node must be connected to at least half, and if exactly half, its connected partition must include the lowest-numbered active node.
- Failure logs an error and fences.

Hold protocol:
- Holds delay quorum decisions during transitions where heartbeat/network state has not converged.
- `o2quo_hb_up()` adds a heartbeating node and holds if not connected.
- `o2quo_hb_down()` removes heartbeat state and clears holds.
- `o2quo_conn_up()` adds network connectivity and holds if heartbeat is not yet seen.
- `o2quo_conn_err()` removes connectivity and holds if the peer still heartbeats.
- `o2quo_hb_still_up()` marks a pending decision and clears a connection-error hold.

Lifecycle:
- `o2quo_init()` initializes lock and work.
- `o2quo_exit()` flushes pending work.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/quorum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/quorum.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/quorum.h

Header for OCFS2 quorum logic.

Declares:
- Lifecycle: `o2quo_init()`, `o2quo_exit()`.
- Heartbeat events: `o2quo_hb_up()`, `o2quo_hb_down()`, `o2quo_hb_still_up()`.
- Network events: `o2quo_conn_up()`, `o2quo_conn_err()`.
- Disk timeout fencing entry: `o2quo_disk_timeout()`.

Role:
- Used by heartbeat and network transport code to coordinate self-fencing decisions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/quorum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/sys.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/sys.c

O2CB sysfs interface setup.

Behavior:
- Creates kset `o2cb` under `fs_kobj`.
- Adds attribute group containing `interface_revision`, which reports `O2NM_API_VERSION`.
- Initializes masklog sysfs under the O2CB kset with `mlog_sys_init()`.

Lifecycle:
- `o2cb_sys_init()` creates kset, sysfs group, and logmask interface; rolls back on failure.
- `o2cb_sys_shutdown()` shuts down masklog sysfs and unregisters the kset.

Dependency:
- Uses `ocfs2_nodemanager.h` for API version and `masklog.h` for logging sysfs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/sys.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/sys.h

Small header declaring O2CB sysfs lifecycle hooks.

Declares:
- `o2cb_sys_shutdown()`.
- `o2cb_sys_init()`.

Used by:
- `nodemanager.c` during module init/exit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/sys.h -->