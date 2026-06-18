# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.c

## Role

Implements the main bcachefs recovery and new-filesystem initialization pipeline.

## Major Responsibilities

- Marks btrees as having lost data and schedules the required repair passes.
- Supports allocator reconstruction and journal-rewind error silencing.
- Transitions recovery into early read-write mode.
- Replays journal keys into btrees, with accounting keys replayed first.
- Performs early replay of root, usage, blacklist, and clock journal entries.
- Reads btree roots, reconstructing fake roots where needed.
- Drives mount recovery from clean superblock or journal scan through startup recovery passes.
- Handles journal rewind, recent-journal scrub, blacklisting of unsafe post-replay sequences, fsck verification, quota loading, superblock cleanup, and background cleanup triggers.
- Initializes a new filesystem, including fake roots, journal allocation/start, root inode, `lost+found`, first journal flush, and initialized superblock state.

## Key Recovery Flow

`__bch2_fs_recovery()` reads the clean section for clean shutdowns or scans journal entries for unclean/recovery-info/rewind/scrub modes. It establishes journal start positions, runs early replay, resizes on mount, applies read-only restrictions for special image layouts, reconstructs alloc info if required, handles rewind setup, blacklists skipped sequence ranges, starts the journal, sorts journal keys, reads roots, starts the btree runtime, applies option hooks/upgrades, optionally scrubs recent journal entries, then runs startup recovery passes.

After pass execution it ensures `BCH_FS_may_go_rw`, clears fsck state, flushes rewrites, persists fixed-error metadata, optionally performs a second debug fsck, reads quotas, updates upgrade/compat bits, garbage-collects blacklist entries, starts dead-snapshot deletion, and runs replicas cleanup.

## Journal Replay

`bch2_journal_replay()` requires the journal key buffer to be stable, replays accounting deltas first, then tries sorted replay for locality. Keys that cannot be replayed in the fast path are sorted by journal sequence and replayed in journal order while dropping replay pins. Repair-generated allocated keys force immediate flush.

## Notable Details

- After unclean shutdown, recovery advances `cur_seq` by 64 before blacklisting skipped sequences.
- If encryption is enabled and shutdown was unclean, key version is advanced by `1 << 16` to avoid nonce reuse.
- Missing btree roots can be tolerated for reconstructible btrees and fake roots are allocated for missing standard roots.
- `bch2_fs_recovery()` wraps the internal recovery path and forces emergency read-only on recovery failure.
