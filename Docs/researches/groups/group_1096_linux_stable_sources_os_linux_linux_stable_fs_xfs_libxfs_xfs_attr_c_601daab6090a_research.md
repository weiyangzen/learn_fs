# Group Research: group_1096_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_attr_c_601daab6090a

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`. All listed files were read completely. Line/byte counts matched the work item manifest.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.c

## Purpose

`xfs_attr.c` is the main libxfs extended-attribute orchestration layer. It exposes inode attribute presence checks, get/set/remove entry points, attribute fork creation, namespace/name validation, hashing, and the deferred xattr state machine that spans shortform, leaf, node, and remote-value operations.

## Main APIs and Data Flow

- `xfs_attr_get` prepares `xfs_da_args` fields and calls `xfs_attr_get_ilocked`.
- `xfs_attr_get_ilocked` dispatches by format: shortform, leaf, or node.
- `xfs_attr_set` handles remove, upsert, create, and replace, including fork creation, reservations, lookup, and helper dispatch.
- `xfs_attr_set_iter` runs deferred attr intents across transaction rolls.

## Deferred State Machine

The state machine handles shortform, leaf, and node add/remove states, remote allocation/removal, replace flag flips, and cleanup. Replace operations depend on INCOMPLETE flag transitions so the new value becomes visible atomically before the old one is removed.

## Dependencies and Risks

This file integrates `xfs_attr_leaf.c`, `xfs_attr_remote.c`, da btree code, bmap, transactions, quota, attr intent logging, tracing, and parent-pointer support. Key risks are the inverted lookup convention (`-EEXIST` means found), old/new `blkno/index` tracking during replacement, and remote-value state preservation across transaction rolls.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.h

## Purpose

`xfs_attr.h` defines the shared extended-attribute interface: list context, delayed-operation states, attr intent structure, update operation enum, hashing helpers, state initialization helpers, and cross-file prototypes.

## Key Contents

- `struct xfs_attr_list_context` carries list cursor, output buffer, filters, and callback.
- `enum xfs_delattr_state` names all resumable attr states.
- `struct xfs_attr_intent` tracks delayed attr operation state, args, log name/value storage, da state, and remote allocation progress.
- `xfs_attr_init_add_state`, `xfs_attr_init_remove_state`, and `xfs_attr_init_replace_state` select initial deferred states from current fork format and logging mode.

## Invariants

State enum ordering matters because leaf and node sequences are intentionally aligned. Namespace validation allows at most one on-disk namespace bit. Replace helpers mutate operation flags, so callers must treat `xfs_da_args` as stateful.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.c

## Purpose

`xfs_attr_leaf.c` implements shortform attributes, attr leaf blocks, and leaf-level btree operations. It covers header conversion, verification, shortform create/add/remove/get, format conversion, leaf insertion/removal, split/rebalance/join support, lookup, value copy, freemap compaction, and INCOMPLETE flag handling.

## Main Behavior

The file supports legacy and CRC-enabled attr leaf blocks via in-core `xfs_attr3_icleaf_hdr` conversion helpers. Verifiers check da block headers, hash order, name/value bounds, remote entry validity, freemap bounds/alignment, and CRC owner metadata.

Shortform attrs are packed in the inode attr fork. The code can create, scan, replace, append, remove, verify, and convert shortform attrs to leaf blocks. Leaf blocks can shrink back to shortform when all entries are local and fit.

Leaf insertion uses a sorted hash entry array plus backward-growing name/value storage. If freemap space is fragmented, compaction rewrites entries into a packed layout. Remote values create an incomplete leaf entry first; value block allocation and writing happen later.

## Atomic Replace

`xfs_attr3_leaf_setflag`, `xfs_attr3_leaf_clearflag`, and `xfs_attr3_leaf_flipflags` manage INCOMPLETE flags. `flipflags` can update old and new entries in one transaction even when they are in different leaf blocks.

## Risks

Subtle areas include 64 KiB `firstused` conversion, freemap overlap handling, duplicate hash lookup, split-time old/new index tracking, and ensuring remote values are synchronously written before clearing INCOMPLETE.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.h

## Purpose

`xfs_attr_leaf.h` declares the in-core attr leaf header and the shortform/leaf helper APIs used by the high-level attr state machine and da btree code.

## Key Contents

`struct xfs_attr3_icleaf_hdr` normalizes legacy and CRC-enabled leaf headers, including sibling links, magic, count, used bytes, 32-bit `firstused`, hole flag, and freemap entries.

The header declares shortform operations, leaf/node conversion, INCOMPLETE flag helpers, split/lookup/add/remove/list functions, shrink helpers, and verifier/header conversion utilities.

## Invariants

Callers must provide populated `xfs_da_args` fields such as geometry, transaction, inode, owner, and fork. The widened in-core `firstused` must round-trip correctly through disk conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.c

## Purpose

`xfs_attr_remote.c` manages out-of-line extended attribute values stored in attr-fork blocks. It computes remote block needs, verifies/stamps CRC remote headers, reads and writes remote value buffers, finds holes, allocates remote extents for delayed ops, invalidates cached buffers, and removes remote extents.

## Main Behavior

Remote attr buffers are not logged. CRC-enabled remote blocks include per-block headers, and writes are synchronous so data reaches disk before the leaf entry is made complete. Headers include magic, offset, bytes, uuid, owner, physical block number, and `NULLCOMMITLSN`.

`xfs_attr_rmtval_get` maps and reads remote extents, validates buffers, and copies payload out. `xfs_attr_rmtval_set_value` writes already allocated extents synchronously. `xfs_attr_rmtval_set_blk` allocates one extent step for deferred operations, allowing transaction rolls.

## Removal

`xfs_attr_rmtval_invalidate` marks incore buffers stale before removal. `xfs_attr_rmtval_remove` unmaps extents and returns `-EAGAIN` until unmapping is complete.

## Risks

Correctness depends on remote buffers never entering the log, header fields matching physical storage and owner metadata, and leaf entries remaining INCOMPLETE until allocation plus synchronous writes finish.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.h

## Purpose

`xfs_attr_remote.h` declares helpers for remote extended attribute values.

## APIs

It exposes block-count calculation, max remote block calculation, remote value get/set, stale/invalidate/remove helpers, hole finding, and delayed allocation helpers.

## Integration Notes

Callers must preserve `xfs_da_args` remote fields across state-machine steps. The API is used by leaf insertion/removal and deferred attr intent processing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_sf.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_sf.h

## Purpose

`xfs_attr_sf.h` defines shortform extended attribute helpers for packed inode-resident attrs.

## Key Contents

`xfs_attr_sf_sort_t` supports listing entries in hash order. Inline helpers compute entry sizes, find the first entry, advance to the next entry, and find the end pointer from the shortform total size.

## Invariants

Traversal depends on verified `namelen`, `valuelen`, and `totsize`. One-byte length fields limit shortform name/value sizes; larger attrs must use leaf or remote formats.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_sf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.c

## Purpose

`xfs_bit.c` implements small bitmap scanning helpers.

## APIs

- `xfs_bitmap_empty` tests whether all bitmap words are zero.
- `xfs_contig_bits` counts contiguous set bits from a start bit.
- `xfs_next_bit` returns the next set bit at or after a start bit, or `-1`.

## Invariants

`size` is measured in words. `xfs_contig_bits` asserts the start bit is in range; `xfs_next_bit` returns `-1` for out-of-range starts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.h

## Purpose

`xfs_bit.h` declares and defines XFS bit manipulation helpers.

## Key Contents

It provides high/low mask helpers, highest/lowest set-bit helpers for 32-bit and 64-bit values, and declarations for bitmap scanning functions implemented in `xfs_bit.c`.

## Risks

Mask helpers rely on callers passing shift counts within the width of the target integer type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.h -->