# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.c

## Purpose
`xfs_exchmaps.c` implements the libxfs side of exchange-range / file mapping exchange. It estimates required work and reservations, creates deferred exchange intents, performs one resumable exchange step per transaction, updates quotas and inode sizes, handles reflink/large-extent-count state, and performs post-operation conversion back to shortform formats when possible.

## Important APIs, Types, and Functions
Public functions include `xfs_exchmaps_check_forks`, `xfs_exchmaps_finish_one`, `xfs_exchmaps_estimate_overhead`, `xfs_exchmaps_intent_init_cache`, `xfs_exchmaps_intent_destroy_cache`, `xfs_exchmaps_init_intent`, `xfs_exchmaps_estimate`, `xfs_exchmaps_ensure_reflink`, `xfs_exchmaps_upgrade_extent_counts`, and `xfs_exchange_mappings`. Internal structures include the global `xfs_exchmaps_intent_cache`, `struct xfs_exchmaps_adjacent` for estimate-time neighbor tracking, and `struct xfs_exchmaps_intent` from the header.

## Control Flow
Callers first validate fork eligibility with `xfs_exchmaps_check_forks`, which rejects missing or local-format forks. `xfs_exchmaps_estimate` creates a temporary intent, walks mappings with `xfs_exchmaps_find_mappings`, counts exchange steps, accounts moved data/rt blocks, simulates extent-count deltas with neighbor-aware merge logic, checks extent counter limits, and calls `xfs_exchmaps_estimate_overhead` to reserve bmbt/rmapbt growth. The estimator also honors `XFS_EXCHMAPS_INO1_WRITTEN`, which can skip holes/unwritten mappings from inode1, with special rules for realtime files with multi-FSB allocation units.

Actual scheduling occurs in `xfs_exchange_mappings`. It asserts both inodes are exclusively ILOCKed and the filesystem supports exchange range, creates an intent from the request, queues it with `xfs_exchmaps_defer_add`, sets reflink flags on the opposite inode when needed before rmap updates, and upgrades both inode extent counters if the filesystem supports large counts.

Deferred execution calls `xfs_exchmaps_finish_one`. If work remains, it finds the next pair of different mappings, unmaps both extents, swaps logical offsets, maps the opposite physical mapping into each inode, updates quota block counts, advances the intent cursor, and grows on-disk sizes before post-EOF mappings can exist. When the main range is complete, optional `XFS_EXCHMAPS_SET_SIZES` swaps final sizes. If only post-op work remains, it attempts to convert inode2's attr fork, directory data fork, or symlink target back to shortform and clears reflink flags that can be exchanged away. Returning `-EAGAIN` asks the deferred-op framework for another transaction; error injection can force `-EIO` through `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`.

## State and Persistence
Persistent mutations include bmbt mappings in two inodes, quota block counters, inode disk sizes, reflink flags, large extent-count flags, and possible fork format conversions for attr/dir/symlink data. Recovery state is carried by logged exchange-map intent/done items outside this file; `xfs_exchmaps_finish_one` advances the in-core intent so the deferred item can be relogged for remaining work. COW fork tags are refreshed after completion for data-fork exchanges.

## Dependencies and Integration Points
This file integrates with bmap read/map/unmap APIs, deferred operations and exchange-map log items, transaction and quota accounting, reflink/rmap behavior, inode fork management, directory and attr shortform conversion, remote symlink conversion, extent count limits, tracepoints, error injection, and health marking on corrupt same-physical-block state mismatches.

## Risks and Test Signals
Risks include exchanging delalloc or unexpected mappings, adding mappings past EOF before size logging, underestimating extent/rmap reservation, quota accounting drift, reflink flag inconsistency, and partial-operation recovery after crashes. Realtime unwritten extent skipping is especially subtle because swaps must respect allocation-unit boundaries. Tests should cover crash recovery of deferred exchange intents, reflink and non-reflink pairs, attr-fork exchanges, size-swapping, same-inode exchanges, realtime files, extent-count overflow injection, quota accounting, shortform post-op conversion, and `exchmaps_finish_one` error injection.
