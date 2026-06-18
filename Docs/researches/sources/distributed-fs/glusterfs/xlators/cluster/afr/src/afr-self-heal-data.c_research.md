# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-data.c

## Purpose

`afr-self-heal-data.c` implements AFR data self-heal for regular files. It selects an authoritative source, truncates sinks to the source size, copies data blocks from source to sinks, avoids unnecessary writes through checksum and sparse-file checks, fsyncs if durability is required, restores timestamps, and clears data pending xattrs.

The file owns byte-range content repair. It relies on common self-heal logic for locks, direction calculation, pending-xattr cleanup, and split-brain policies.

## Important APIs, Types, and Functions

`afr_selfheal_data()` is the public entry point. It takes a self-heal domain inode lock, then delegates to `__afr_selfheal_data()`.

`__afr_selfheal_data_prepare()` discovers locked replies, calls `afr_selfheal_find_direction()` for `AFR_DATA_TRANSACTION`, initializes `healed_sinks`, and finalizes the source through `__afr_selfheal_data_finalize_source()`.

`__afr_selfheal_data_finalize_source()` handles split brain, CLI/favorite-child selection, source witness tie breakers, size mismatches, largest-file policy, newest-file tie breaking, arbiter empty-file behavior, and final source selection via `afr_choose_source_by_policy()`.

`afr_selfheal_data_do()` performs the copy loop. It chooses full or diff heal, sizes the block window, copies with a reusable iter frame, and fsyncs healed sinks if enabled.

`afr_selfheal_data_block()` locks a byte range, optionally skips a diff block by comparing checksums, and calls `__afr_selfheal_data_read_write()`.

`__afr_selfheal_data_read_write()` reads from the source with `syncop_readv()` and writes the buffer to each healed sink with `syncop_writev()`, unmarking any sink whose write fails.

`__afr_can_skip_data_block_heal()` issues `rchecksum` on source and sinks and skips matching blocks, with special handling for zero-filled sparse regions.

`__afr_selfheal_truncate_sinks()` performs up-front `ftruncate` on healed sinks. Arbiter sinks are also included so changelog/geo-rep state can capture data transactions.

`afr_selfheal_data_open()` opens an inode on up children and binds the fd if at least one open succeeds.

## Control Flow

The entry point first locks the file in `priv->sh_domain` with `afr_selfheal_tie_breaker_inodelk()`. If every child cannot be locked, it returns `-ENOTCONN`. Under that outer lock, `__afr_selfheal_data()` takes the xlator-domain file lock, discovers replies, computes sources/sinks, and decides whether there is real work.

If a source is selected and at least one sink is marked, the code rejects non-empty arbiter sources. It truncates healed sinks to the source size and drops the xlator-domain lock before copying file data. If the only sink is an arbiter or the file is empty on all children, it skips data copy and proceeds to timestamp restoration and pending cleanup.

The copy loop uses `block = 128 KiB * data_self_heal_window_size`, reduced to `128 KiB` for files with holes. Dynamic heal mode chooses diff heal when any participant has non-zero size, otherwise full heal. Each block is separately range-locked before read/write.

For diff blocks, checksums are requested from source and sinks. A matching checksum can skip the write. Sparse files get extra handling to avoid filling holes with zero writes, except where the final block is needed to establish file size.

After data copy, the code restores source atime/mtime/ctime to healed sinks, reacquires the xlator-domain lock when needed, and calls `afr_selfheal_undo_pending()` for `AFR_DATA_TRANSACTION`.

## State and Persistence Behavior

Persistent effects are writes, truncates, fsyncs, timestamps, and AFR pending xattrs on bricks. The function treats `healed_sinks[]` as mutable success state: a sink starts as a target but is cleared if truncate, write, fsync, or metadata update fails.

`locked_replies` preserve source and sink stat/xattr state from the locked discovery. Source size and sparse status drive block iteration and skip decisions.

Arbiter state is special. The arbiter is temporarily removed from data copy targets, can remain a sink for metadata/changelog purposes, and is never accepted as the source for non-empty data.

`ensure_durability` controls whether successful sink writes must be followed by `fsync`; fsync failures turn those sinks back into unhealed sinks before pending xattrs are cleared.

## Dependencies and Integration Points

This file depends on common helpers from `afr-self-heal-common.c` for locks, source/sink direction, split-brain handling, xattr undo, timestamp restoration, logging, and reply management. It also uses Gluster syncops for `readv`, `writev`, `ftruncate`, `fsync`, and `open`.

It integrates with AFR configuration fields such as `data_self_heal_algorithm`, `data_self_heal_window_size`, `ensure_durability`, `arbiter_count`, `local[]`, and `pending_key[]`.

It shares checksum semantics with lower translators through `rchecksum` xdata keys `check-zero-filled`, `buf-has-zeroes`, and `fips-mode-rchecksum`.

## Risks and Edge Cases

Sparse-file handling is deliberately conservative and comments note that proper FIEMAP/discard support is missing. Incorrect zero-skip logic can alter disk usage or fail to preserve holes.

The source-selection tie breakers combine xattr witnesses, size, ctime, favorite-child policy, and arbiter rules. Small changes can convert a no-heal or split-brain condition into data overwrite.

The function clears pending xattrs only for sinks still marked healed. Any path that forgets to clear a failed sink before post-op can lose pending state.

Range locks around each block reduce concurrency risk but increase exposure to lock loss and reconnect behavior during long heals.

Checksum skip depends on comparable checksum algorithms. FIPS-mode SHA256 and default MD5 lengths are tracked per reply; mismatches here can cause false equality or unnecessary copying.

## Test Signals

Tests should cover full and diff algorithms, dynamic mode selection, sparse source with zero blocks, non-sparse zero-filled blocks, failed sink write/truncate/fsync, durability enabled and disabled, arbiter-only sink, arbiter source rejection, empty-file heal, size-mismatch source selection, witness tie breaking, range-lock failures, and pending xattr cleanup after partial success.

Runtime signals include `performing data selfheal`, block debug logs with GFID/offset/size, `afr_log_selfheal()` source/sink output, split-brain events from common helpers, and changes in AFR index counts after pending xattrs are cleared.
