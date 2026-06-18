# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-metadata.c

## Purpose

`afr-self-heal-metadata.c` implements AFR metadata self-heal. It repairs uid, gid, mode, and user xattrs from a selected source to healed sinks, handles metadata split brain, supports directory time-only split-brain resolution, restores source timestamps, and clears metadata pending xattrs.

This file is the metadata-specific counterpart to data and entry heal, using the common direction and locking logic while owning attribute and xattr copy semantics.

## Important APIs, Types, and Functions

`afr_selfheal_metadata()` is the main entry point. It takes a tie-breaker inode lock at offset `LLONG_MAX - 1`, prepares source/sink state, copies metadata, restores times, and undoes pending xattrs.

`__afr_selfheal_metadata_prepare()` discovers locked replies, computes direction for `AFR_METADATA_TRANSACTION`, gives preference to source witnesses, and calls `__afr_selfheal_metadata_finalize_source()`.

`__afr_selfheal_metadata_finalize_source()` handles split brain, favorite-child/CLI resolution, directory time-only split brain, forced metadata split-brain heal, source pruning for stat/xattr mismatch, and optional marking of pending xattrs when all bricks were initially sources but mismatches are found.

`__afr_selfheal_metadata_do()` copies metadata. It gets xattrs from the source, removes ignorable keys, sets uid/gid/mode on each healed sink, removes old sink xattrs, and sets the source xattr set.

`afr_dirtime_splitbrain_source()` detects the special case where only directory atime/mtime/ctime differ while GFID, type, mode, uid, gid, and non-ignorable xattrs match; it selects the newest mtime source.

`afr_selfheal_metadata_by_stbuf()` builds an inode from a supplied stat buffer and runs metadata heal, useful for callers that already have authoritative iatt state.

## Control Flow

Metadata heal starts with an inode lock in the xlator domain at a high offset to avoid conflicting with normal data ranges. The prepare step does a locked discover and interprets metadata changelogs. If any source has witness counts, it is selected and other sources are converted to healed sinks.

Finalize handles hard cases. If every locked child is a sink or no source exists, it first tries common split-brain source selection. If that fails, it checks for directory time-only split brain and selects the most recent directory time. If forced metadata split-brain heal is enabled, it arbitrarily picks a locked sink as source; otherwise it emits a split-brain event and returns `-EIO`.

When a source is selected, other sources are compared against the source's type, uid, gid, mode, and xattrs. Mismatching sources are downgraded to sinks. If all children were initially sources and mismatches are found, the code marks metadata pending xattrs on sources and refreshes replies before the actual heal.

The copy phase fetches source xattrs once, removes ignorable AFR/internal keys, applies uid/gid/mode through `setattr`, removes old sink xattrs by passing the old dict to `removexattr`, and writes the source xattrs to each sink. Sink failures clear `healed_sinks[i]`.

After copy, the code restores timestamps and uses `afr_selfheal_undo_pending()` to clear metadata pending state only for successfully healed sinks.

## State and Persistence Behavior

Persistent state includes inode ownership, mode, xattrs, timestamps, and AFR metadata changelog xattrs. The macro `AFR_HEAL_ATTR` limits attribute copy to uid, gid, and mode; timestamps are restored separately.

Ignorable xattrs are filtered both from the source xattr set and old sink xattrs before removal. This prevents AFR/internal or otherwise ignored keys from being copied or deleted as user metadata.

`metadata_splitbrain_forced_heal` changes persistence behavior significantly by allowing an arbitrary locked sink to become source when no policy/source can resolve split brain.

The directory time-only path treats mtime/ctime divergence as a repairable artifact of platform-specific directory timestamp behavior after entry changes.

## Dependencies and Integration Points

This file depends on common AFR self-heal helpers for lock, direction, split-brain policy, pending cleanup, timestamp restoration, xattr equality, and logging. It uses syncops for `getxattr`, `setattr`, `removexattr`, and `setxattr`.

It integrates with AFR configuration for arbiter xattr comparisons, favorite-child policy, and forced metadata split-brain healing. It also uses Gluster event logging for unresolved metadata split brain.

## Risks and Edge Cases

Removing old sink xattrs with a dictionary is powerful and risky. If ignorable filtering is incomplete, internal or externally managed xattrs may be removed incorrectly.

Forced metadata split-brain heal can overwrite metadata arbitrarily and must remain an explicit configuration choice.

The all-sources-but-mismatching path marks pending xattrs before healing. Failures between marking and completion must leave enough pending state for a later heal.

Directory time-only detection must compare all non-time fields and xattrs. If it misses a meaningful difference, it can silently choose the newest timestamp as source and overwrite real divergence.

## Test Signals

Tests should cover uid/gid/mode repair, user xattr copy and old xattr removal, ignorable xattr preservation, sink failure during setattr/removexattr/setxattr, directory time-only split brain, forced and non-forced metadata split brain, source witness selection, all-sources mismatch marking, favorite-child policy rejection for metadata heal-op modes, and timestamp restoration.

Runtime signals include `performing metadata selfheal`, `clear time split brain`, metadata split-brain events, debug logs for iatt/xattr mismatch, and final `afr_log_selfheal()` status.
