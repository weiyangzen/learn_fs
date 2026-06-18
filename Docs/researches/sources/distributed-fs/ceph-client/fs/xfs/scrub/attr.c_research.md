# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.c

## Purpose
This file scrubs extended attribute metadata for an inode. It validates shortform and leaf/block attr structures, checks name/value placement with byte bitmaps, verifies hashes and namespaces, retrieves every attribute by name/hash, and validates parent pointer values.

## Important APIs, types, and functions
`xchk_setup_xattr` prepares repair state when available, optionally preallocates maximum buffers for retry, and sets up inode-content scrub. `xchk_setup_xattr_buf` manages `struct xchk_xattr_buf`, including used/free maps, salvage name buffer, and value buffer. `xchk_xattr_set_map` marks byte ranges and detects overlaps/out-of-bounds usage. `xchk_xattr_actor` is called by attr walking to validate names, parent values, lookupability, and value length. `xchk_xattr_block`, `xchk_xattr_entry`, and `xchk_xattr_rec` validate attr leaf internals. `xchk_xattr_check_sf` validates shortform attr layout. `xchk_xattr` is the main entry point.

## Control flow and state
Scrub allocates reusable buffers, validates physical structure first, then does semantic lookup of every xattr if no corruption was found. Shortform validation walks entries inside the inode fork and marks each header/name/value byte range. Leaf validation clears used/free maps per block, validates padding, header bounds, entry array placement, sorted hashes, local versus remote entry sizes, freemap entries, and `usedbytes`. Record validation recalculates the attr hash from local value bytes or remote value length and checks namespace flags. The actor path fetches values with `xfs_attr_get_ilocked` to ensure dabtree lookup and remote value retrieval work.

## Persistence and integration
This file is validation-only, except for scrub result flags and preen markers for incomplete attrs, leaf holes, and harmless freemap anomalies. It integrates with dabtree scrub, listxattr walking, parent pointer validation, attr repair buffers, and inode locking established by setup.

## Risks and test signals
Risks center on byte map bounds, remote value lookup, parent pointer validation, and avoiding deadlocks by returning `-EDEADLOCK` when larger buffers are needed. Tests should cover malformed shortform sizes, overlapping attr entries, bad freemap/usedmap intersections, unsorted hashes, wrong namespace flags, invalid parent pointer values, missing remote value blocks, lookup returning `-ENODATA`, incomplete attrs being preened, and retry with `XCHK_TRY_HARDER`.
