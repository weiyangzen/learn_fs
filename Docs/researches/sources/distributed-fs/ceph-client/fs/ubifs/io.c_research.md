# sources/distributed-fs/ceph-client/fs/ubifs/io.c

## Purpose

`io.c` is the UBIFS low-level I/O and write-buffer subsystem. It wraps UBI read/write/change/map/unmap operations, validates node headers and CRCs, prepares nodes for flash by filling common headers, sequence numbers, padding, CRCs, and optional HMACs, and implements journal write buffers that batch small writes while respecting minimum and maximum flash write sizes.

## Important APIs, Types, And Functions

The UBI wrappers are `ubifs_leb_read()`, `ubifs_leb_write()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`, `ubifs_leb_map()`, and `ubifs_is_mapped()`. Validation and node-preparation helpers include `ubifs_check_node()`, `ubifs_pad()`, `ubifs_init_node()`, `ubifs_crc_node()`, `ubifs_prepare_node_hmac()`, `ubifs_prepare_node()`, and `ubifs_prep_grp_node()`. Write-buffer APIs include `ubifs_wbuf_sync_nolock()`, `ubifs_wbuf_seek_nolock()`, `ubifs_bg_wbufs_sync()`, `ubifs_wbuf_write_nolock()`, `ubifs_read_node_wbuf()`, `ubifs_wbuf_init()`, `ubifs_wbuf_add_ino_nolock()`, and `ubifs_sync_wbufs_by_inode()`.

The central type is `struct ubifs_wbuf`, with `buf`, `inodes`, `lnum`, `offs`, `size`, `avail`, `used`, `io_mutex`, `lock`, timer state, optional `sync_callback`, and journal-head identity. `struct ubifs_ch` is the common node header validated by reads and populated by writes.

## Control Flow

Raw write-like wrappers assert the filesystem is not mounted read-only and not on read-only media, return `-EROFS` after a prior write error, optionally route through debug recovery hooks, and call `ubifs_ro_mode()` on write/map/unmap failures. Reads report errors but do not make the filesystem read-only. `ubifs_check_node()` validates magic, node type, length range from `c->ranges`, and CRC. It may skip data-node CRC checks only when allowed by mount state and `must_chk_crc`.

Write-buffer writes first check that the aligned node fits in the current LEB. If the node fits in available buffer space, it is copied into RAM and either left pending with a timer or flushed if it exactly fills the buffer. Larger writes flush any partial buffer, write full maximum-write-size chunks directly, and keep only the tail in the buffer. `ubifs_wbuf_sync_nolock()` writes only the used portion rounded to `min_io_size`, pads the remainder, advances offsets, recalculates the temporary buffer size needed to regain `max_write_size` alignment, clears inode tracking, and invokes `sync_callback`.

Reads can overlap a pending write buffer. `ubifs_read_node_wbuf()` copies the overlapping suffix from RAM and reads any prefix from flash before validating the reconstructed node. Background synchronization is timer-driven: timer expiry marks a buffer and wakes the background thread, `ubifs_bg_wbufs_sync()` skips locked buffers, syncs marked buffers, and cancels all timers after an error to avoid repeated failures.

## State And Persistence Behavior

The file owns UBIFS's transition to read-only error mode. `ubifs_ro_mode()` sets `c->ro_error`, clears data-CRC skipping, sets `SB_RDONLY`, logs the reason, and dumps a stack once. Sequence numbers are assigned by `next_sqnum()` under `c->cnt_lock`; near or actual overflow logs warnings or forces read-only. Padding nodes and padding bytes make scanned media unambiguous at minimum-I/O boundaries, while 8-byte alignment preserves UBIFS node layout.

Write buffers intentionally allow recently written nodes to live temporarily in RAM. Callers that require durability call sync paths directly, rely on timer/background sync, or call inode-targeted synchronization. The `inodes` side array records inode numbers represented in a pending buffer so `ubifs_sync_wbufs_by_inode()` can flush the right journal heads for fsync-style operations, excluding the GC head because those nodes are copies of existing media nodes.

## Dependencies And Integration Points

`io.c` integrates directly with UBI, Linux timers and locks, CRC32, UBIFS authentication/HMAC helpers, debugging/recovery hooks, dump helpers, journal heads, and lprops callbacks. Higher layers depend on it for all physical persistence: journal writes use `ubifs_wbuf_write_nolock()`, log writes use `ubifs_write_node()`, GC uses seek/sync/write-buffer functions, scanning and TNC reads use node validation, and error paths rely on `ubifs_ro_mode()`.

## Risks And Edge Cases

The alignment logic is subtle: `wbuf->offs`, `wbuf->size`, `wbuf->avail`, and `wbuf->used` must stay consistent across partial syncs, direct large writes, and end-of-LEB writes. CRC skipping must never apply during mount/recovery or forced checks. `ubifs_read_node_wbuf()` must reconstruct overlap without racing buffer mutation, so it uses `wbuf->lock` only around state/copy and then validates outside. Sequence number exhaustion, buffer allocation failure, stale inode tracking, and sync-callback failures are significant risk points.

## Test Signals

Test signals include UBI error injection for write/change/unmap/map, CRC and bad-magic images, no-data-CRC mounts versus recovery-time checks, writes that cross min/max write-size boundaries, end-of-LEB writes, overlapping reads from a pending write buffer, timer-triggered background sync, inode-specific fsync, authenticated node HMAC preparation, and assertion-enabled runs that exercise alignment invariants.
