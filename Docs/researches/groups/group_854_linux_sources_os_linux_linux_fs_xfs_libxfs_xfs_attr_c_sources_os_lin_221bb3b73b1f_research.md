# Group Research: Linux XFS libxfs extended attributes and bit helpers

This group covers XFS extended attribute metadata management in libxfs: high-level get/set/remove orchestration, delayed-attribute state machines, shortform and leaf-block packing, attr Btree split/join behavior, remote value IO, on-disk format verification, and small bitmap utility helpers used by XFS code.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.c

## Purpose
Implements the main XFS extended attribute API and the delayed attribute operation state machine. It routes lookups, creates, replaces, and removals across shortform inode-local attributes, single leaf blocks, and multi-block node/Btree attr forks.

## Main Interfaces
- Attribute queries: `xfs_attr_get()`, `xfs_attr_get_ilocked()`, `xfs_inode_hasattr()`, `xfs_attr_is_leaf()`.
- Attribute mutations: `xfs_attr_set()`, `xfs_attr_set_iter()`, `xfs_attr_setname()`, `xfs_attr_removename()`, `xfs_attr_replacename()`.
- Format/space helpers: `xfs_attr_calc_size()`, `xfs_attr_set_resv()`, `xfs_attr_add_fork()`, `xfs_attr_sf_totsize()`.
- Hash/name validation: `xfs_attr_hashname()`, `xfs_attr_hashval()`, `xfs_attr_namecheck()`, `xfs_attr_check_namespace()`.
- Intent cache lifecycle: `xfs_attr_intent_init_cache()`, `xfs_attr_intent_destroy_cache()`.

## Control Flow
`xfs_attr_get()` initializes `xfs_da_args`, computes the namespace-aware hash, takes an attr-map shared lock, and calls `xfs_attr_get_ilocked()`. The locked getter loads attr-fork extents and chooses shortform, single-leaf, or node lookup based on fork format and `xfs_attr_is_leaf()`.

`xfs_attr_set()` calculates reservations for create/replace/upsert or remove, creates the attr fork if needed, allocates an inode transaction, checks extent-count growth, performs an initial lookup, and dispatches to set, replace, or remove helpers. Shortform operations can complete immediately in one transaction; larger operations are queued through deferred attr intents.

`xfs_attr_set_iter()` drives resumable delayed operations through `enum xfs_delattr_state`. It handles shortform add/remove, leaf add/remove, node add/remove setup, remote value space discovery/allocation, incomplete-flag flips for atomic replace, remote block invalidation/removal, leaf entry removal, node cleanup, and optional leaf-to-shortform shrinking.

## State And Transactions
The file relies on `struct xfs_attr_intent` to carry current DA state, saved DA lookup state, remote extent allocation progress, and operation flags across transaction rolls. Remote attribute replacement uses saved `blkno/index/rmtblk*` fields to distinguish old and new entries. `XFS_ATTR_INCOMPLETE` is used to hide partially created or replaced attributes from normal lookup until remote values are durable and flags are flipped or cleared.

## Integration Points
Calls shortform and leaf routines from `xfs_attr_leaf.c`, remote value routines from `xfs_attr_remote.c`, DA Btree helpers from `xfs_da_btree`, bmap attr-fork helpers, transaction reservation tables, deferred operation logging in `xfs_attr_item`, quota and inode transaction allocation, and parent-pointer hash/name validation through `xfs_parent`.

## Notable Behaviors
- Parent-pointer attributes use `xfs_parent_hashattr()` and have special replace handling that swaps canonical name/value fields after removal.
- Logged attribute replacement starts with removal for crash recovery consistency; unlogged replacement normally adds first and then atomically flips incomplete flags.
- Leaf and node remote values are allocated after the leaf entry exists to avoid oversized transactions and deadlocks.
- Recovery remove paths tolerate missing attributes as successful cleanup.
- Namespace validation enforces at most one on-disk namespace bit per attribute, while parent-pointer names delegate to parent-specific validation.

## Risks And Review Focus
- State transitions in `xfs_attr_set_iter()` must remain aligned with `enum xfs_delattr_state`; several paths depend on sequential leaf/node state ordering.
- Atomic replace correctness depends on preserving old versus new entry locations through splits and transaction rolls.
- Remote value removal and incomplete-flag handling are crash-consistency sensitive.
- Shortcut shortform replacement must fall back cleanly when size changes force leaf conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.h

## Purpose
Declares the kernel-facing XFS extended attribute API, attr list context, delayed attr intent structure, update operation enum, and delayed attribute state-machine states.

## Main Interfaces
- Listing context: `struct xfs_attr_list_context`, `struct xfs_attrlist_cursor_kern`, `put_listent_func_t`.
- Delayed operation state: `enum xfs_delattr_state`, `struct xfs_attr_intent`, `xfs_attr_intent_op()`.
- Public attr operations: `xfs_attr_get()`, `xfs_attr_set()`, `xfs_attr_set_iter()`, `xfs_attr_remove_iter()`, `xfs_attr_list()`, `xfs_attr_inactive()`.
- Format helpers: `xfs_attr_is_shortform()`, `xfs_attr_init_add_state()`, `xfs_attr_init_remove_state()`, `xfs_attr_init_replace_state()`.
- Hashing and validation: `xfs_attr_hashname()`, `xfs_attr_hashval()`, `xfs_attr_sethash()`, `xfs_attr_namecheck()`.

## Main Contents
The header documents the delayed remove and set state machines with large diagrams. Remove operations progress from format detection through optional remote block invalidation/removal, leaf/node entry removal, tree shrink, and state cleanup. Set operations progress through fork creation, shortform add or conversion, leaf or node insertion, remote value allocation, replace flag flips, old remote block removal, and cleanup.

`enum xfs_delattr_state` encodes initial shortform/leaf/node add and remove states, leaf and node remote set/allocation states, replace states, old-entry removal states, remote removal states, final remove-entry states, and `XFS_DAS_DONE`.

## State And Data Model
`struct xfs_attr_intent` carries a deferred log list node, optional DA state, DA args, shared logged name/value buffer, current delayed state, operation flags, and remote allocation progress (`xattri_lblkno`, `xattri_blkcnt`, `xattri_map`). Inline helpers initialize the correct start state from the current attr fork format and replace/logged mode.

## Integration Points
Included by the attr implementation, remote attr implementation, deferred attr item code, xattr VFS-facing code, parent-pointer code, and attr leaf logic. The header also exposes the `xfs_attr_intent_cache` slab lifecycle and lower-level helpers such as `xfs_attr_add_fork()`, `xfs_attr_setname()`, `xfs_attr_removename()`, and `xfs_attr_replacename()`.

## Notable Behaviors
- `xfs_attr_is_shortform()` treats a zero-extent extents-format attr fork as shortform/nonexistent for upgrade decisions.
- Logged replacement starts from remove state so recovery always has enough log data to complete the operation.
- `xfs_attr_init_add_state()` returns done if a pure remove has already deleted the attr fork.
- The state string macro mirrors the enum for tracing/debugging.

## Risks And Review Focus
- Any insertion or reordering in `enum xfs_delattr_state` can break code that relies on sequential leaf/node state ranges.
- Public prototypes must stay synchronized with deferred attr logging and parent-pointer behavior.
- Cursor and list context fields are ABI-shape sensitive because they mirror user-level list cursor padding.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.c

## Purpose
Implements XFS shortform and leaf-block attribute formats, including on-disk verifiers, shortform packing, shortform-to-leaf and leaf-to-shortform conversion, leaf insertion/removal, leaf split/rebalance/join operations, lookup/value retrieval, and `XFS_ATTR_INCOMPLETE` flag manipulation.

## Main Interfaces
- Buffer format verification/read: `xfs_attr3_leaf_read()`, `xfs_attr3_leaf_header_check()`, `xfs_attr3_leaf_hdr_from_disk()`, `xfs_attr3_leaf_hdr_to_disk()`, `xfs_attr3_leaf_buf_ops`.
- Shortform operations: `xfs_attr_shortform_create()`, `xfs_attr_sf_findname()`, `xfs_attr_shortform_replace()`, `xfs_attr_shortform_add()`, `xfs_attr_sf_removename()`, `xfs_attr_shortform_getvalue()`, `xfs_attr_shortform_to_leaf()`, `xfs_attr_shortform_allfit()`, `xfs_attr_shortform_verify()`.
- Leaf/tree operations: `xfs_attr3_leaf_create()`, `xfs_attr3_leaf_init()`, `xfs_attr3_leaf_split()`, `xfs_attr3_leaf_add()`, `xfs_attr3_leaf_remove()`, `xfs_attr3_leaf_to_node()`, `xfs_attr3_leaf_to_shortform()`, `xfs_attr3_leaf_toosmall()`, `xfs_attr3_leaf_unbalance()`.
- Lookup/value/utility: `xfs_attr3_leaf_lookup_int()`, `xfs_attr3_leaf_getvalue()`, `xfs_attr_leaf_lasthash()`, `xfs_attr_leaf_order()`, `xfs_attr_leaf_newentsize()`.
- Crash-consistency flags: `xfs_attr3_leaf_clearflag()`, `xfs_attr3_leaf_setflag()`, `xfs_attr3_leaf_flipflags()`.

## On-Disk Verification
The verifier checks attr leaf magic, CRC metadata, owner, sorted hash order, entry array bounds, name/value region bounds, nonzero name lengths, remote value block presence for complete remote entries, `firstused` validity, freemap alignment, freemap bounds, integer overflow, and freemap overlap. Attr3 64 KiB block handling maps a disk `firstused` value of zero to the full block size for empty blocks because the on-disk field is only 16 bits.

## Shortform Flow
Shortform attributes live in the inode literal area. Creation initializes an `xfs_attr_sf_hdr`, additions append compact name/value entries and adjust `i_forkoff`, replacements update in place only when the stored size remains compatible, and removals memmove later entries over the deleted one. If the final entry disappears and no parent-pointer feature constraints require keeping the fork, the attr fork is removed. Shortform verification checks total size, entry bounds, nonzero names, valid flags, and namespace combinations.

## Leaf And Btree Flow
Leaf add first searches freemap entries for a first-fit region; if fragmented, it compacts the block and retries. Local values store name and value directly in the leaf; large values create a remote entry, mark it incomplete, and return remote block requirements to the higher-level state machine. Leaf removal updates freemaps, clears name/value storage, compacts the entry array, recomputes `firstused` when needed, and reports whether the block is below the join threshold.

Single leaf blocks convert to node format by allocating a new block, copying the old leaf there, and creating a root node pointing to the copied leaf. Splits allocate a new leaf, rebalance entries by byte usage, link sibling blocks, and track old/new entry locations for replacement operations. Shrink paths test if leaves can be joined with siblings, move entries into the retained leaf, and update last hash values for DA Btree fixup.

## Lookup And Values
`xfs_attr3_leaf_lookup_int()` binary-searches by hash, scans duplicate hash entries, and compares namespace, incomplete bit handling, name, and parent-pointer value when relevant. Local values are copied directly. Remote entries populate `rmtblkno`, `rmtblkcnt`, and `rmtvaluelen` before `xfs_attr_copy_value()` calls remote IO.

## Integration Points
Works with `xfs_attr.c` for high-level operation sequencing, `xfs_attr_remote.c` for remote values, `xfs_da_btree` for splits/joins/path shifts, inode literal-area helpers, bmap local-to-extents conversion, superblock attr2 feature logging, transaction buffer logging, CRC buffer ops, health marking, and parent-pointer matching semantics.

## Notable Behaviors
- Normal lookup includes the incomplete bit in the match mask; recovery lookup ignores it so recovery can find entries needing cleanup.
- Parent-pointer matching requires both name and value equality and does not support remote values.
- Leaf-to-shortform conversion skips incomplete entries and only accepts local entries.
- Leaf compaction preserves disk header fields outside the incore header before repacking entries.
- Remote entry creation zeros `valueblk` and `valuelen` until the remote value is written and the incomplete flag is cleared.

## Risks And Review Focus
- Freemap updates are delicate: insertion and removal both adjust entry-array boundaries and must avoid overlapping or stale zero-length freemap entries.
- Split/rebalance code must maintain `args->index`, `blkno`, `index2`, and `blkno2` correctly for atomic replace.
- Verifier changes must preserve 64 KiB attr block first-used conversion behavior.
- Incomplete-entry semantics differ between normal operation and recovery; lookup mask changes can expose partial attributes or hide recoverable ones.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.h

## Purpose
Declares the incore attr leaf header representation and the shortform, leaf, Btree growth/shrink, verification, and utility functions implemented by `xfs_attr_leaf.c`.

## Main Interfaces
- Incore header: `struct xfs_attr3_icleaf_hdr`, including links, magic, count, used bytes, 32-bit `firstused`, holes, and freemap entries.
- Shortform routines: create, replace, add, get, convert to leaf, remove, find, allfit, bytesfit, verify, and fork removal.
- Leaf routines: convert to node, convert to shortform, clear/set/flip incomplete flags, split, lookup, get value, add, remove, list.
- Shrink/growth helpers: leaf init, toosmall, unbalance.
- Utilities: last hash, leaf order, new entry size, leaf read, header conversion, header check.

## Data Model
The incore `firstused` is intentionally 32-bit, unlike the 16-bit on-disk field, so the code can represent maximum 64 KiB filesystem block sizes without overflow. Conversion helpers in the C file handle the special on-disk zero encoding for 64 KiB empty leaf blocks.

## Integration Points
Used by high-level attr operations in `xfs_attr.c`, attr listing, DA Btree code, inode fork conversion paths, and recovery/verification code that must inspect attr leaf blocks.

## Risks And Review Focus
- Prototype and struct changes must preserve compatibility with the on-disk leaf formats in `xfs_da_format.h`.
- The 32-bit incore `firstused` field is a correctness guard for 64 KiB block filesystems and should not be narrowed.
- Flag manipulation helpers are part of the delayed attr crash-consistency protocol.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.c

## Purpose
Implements storage, verification, reading, writing, invalidation, allocation, and removal of remote XFS extended attribute values stored in attr-fork data blocks outside leaf entries.

## Main Interfaces
- Sizing: `xfs_attr3_rmt_buf_space()`, `xfs_attr3_rmt_blocks()`.
- Buffer verification: `xfs_attr3_rmt_buf_ops`, read/write/struct verifiers.
- Value IO: `xfs_attr_rmtval_get()`, `xfs_attr_rmtval_set_value()`.
- Allocation/removal state helpers: `xfs_attr_rmtval_find_space()`, `xfs_attr_rmtval_set_blk()`, `xfs_attr_rmtval_invalidate()`, `xfs_attr_rmtval_remove()`, `xfs_attr_rmt_find_hole()`.
- Cache stale marking: `xfs_attr_rmtval_stale()`.

## Remote Format
On CRC-enabled filesystems, every remote value block contains an `xfs_attr3_rmt_hdr`, so usable payload per block is `attr_blksize - sizeof(header)`. The number of blocks is therefore not a simple byte-to-FSB conversion for v5 filesystems. Remote attr buffers are written synchronously and deliberately avoid the logging system because maximum-sized values plus headers can exceed the maximum loggable buffer size.

## Verification And Copying
Read verification checks CRCs, magic, UUID, block address, payload byte count, total offset bounds, and nonzero owner for each attr block in the buffer. Copy-out then checks owner, offset, size, and block number against the expected attr value stream before copying payload into the caller buffer. Copy-in stamps headers, sets `NULLCOMMITLSN`, copies payload, and zeroes unused tail bytes in the final block.

## Control Flow
`xfs_attr_rmtval_get()` walks attr-fork mappings with `xfs_bmapi_read()`, reads each mapped disk buffer with remote attr buffer ops, copies out payload, and converts disk `-ENODATA` to `-EIO` to avoid confusion with xattr-not-found semantics.

`xfs_attr_rmtval_find_space()` finds an unused attr-fork logical range large enough for the value and seeds the delayed intent allocation fields. `xfs_attr_rmtval_set_blk()` allocates mapped blocks one transaction at a time with `xfs_bmapi_write()`. After all blocks are allocated, `xfs_attr_rmtval_set_value()` synchronously writes the value to those blocks.

Removal first invalidates any incore buffers for the mapped range, then `xfs_attr_rmtval_remove()` unmaps extents with `xfs_bunmapi()`, returning `-EAGAIN` until the unmap operation reports completion.

## Integration Points
Called by leaf value lookup and high-level delayed attr set/remove operations. Depends on attr fork bmap read/write/unmap helpers, XFS buffer cache, remote attr buffer ops, inode health marking, and transaction context supplied by the attr state machine.

## Notable Behaviors
- Remote attr headers use `NULLCOMMITLSN` so log recovery ignores meaningless LSNs for synchronously written, non-logged buffers.
- Incore stale marking rejects delayed or hole mappings as corruption and marks the attr fork sick.
- Remote value write durability precedes clearing `XFS_ATTR_INCOMPLETE` in the leaf entry.
- Removal progress does not need a separate sub-state; it is inferred from `xfs_bunmapi()` returning not-done.

## Risks And Review Focus
- Remote buffers must not acquire log items; accidentally logging them can exceed log buffer limits.
- Header owner/offset/length checks are critical to detecting stale or misdirected remote value blocks.
- The CRC versus non-CRC sizing split must stay consistent with leaf entry `rmtblkcnt` calculations.
- `-ENODATA` translation is important because xattr callers use that errno for a different meaning.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.h

## Purpose
Declares the remote extended attribute value helper API used by attr leaf and delayed attr operation code.

## Main Interfaces
- `xfs_attr3_rmt_blocks()` computes the number of attr-fork blocks required for a value.
- `xfs_attr3_max_rmt_blocks()` returns the block count for `XFS_XATTR_SIZE_MAX`.
- `xfs_attr_rmtval_get()` reads a remote value.
- `xfs_attr_rmtval_stale()` marks cached remote value buffers stale.
- `xfs_attr_rmtval_invalidate()` invalidates remote buffers before removal.
- `xfs_attr_rmtval_remove()` unmaps remote value blocks.
- `xfs_attr_rmt_find_hole()`, `xfs_attr_rmtval_find_space()`, `xfs_attr_rmtval_set_blk()`, and `xfs_attr_rmtval_set_value()` support delayed allocation and writing of remote values.

## Integration Points
Included by `xfs_attr.c`, `xfs_attr_leaf.c`, and `xfs_attr_remote.c`. The prototypes connect leaf entries that reference remote values to bmap allocation/removal and synchronous remote buffer IO.

## Risks And Review Focus
- Block-count helpers must remain in lockstep with CRC header sizing in `xfs_attr_remote.c`.
- Delayed operation helpers depend on `struct xfs_attr_intent` state fields declared in `xfs_attr.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_sf.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_sf.h

## Purpose
Defines shortform extended attribute helper types and inline entry navigation/size routines for attributes packed inside the inode literal area.

## Main Interfaces
- `xfs_attr_sf_sort_t` describes sortable shortform entries for hash-ordered listing.
- `XFS_ATTR_SF_ENTSIZE_MAX` defines the maximum one-byte name/value length representable in shortform entries.
- `xfs_attr_sf_entsize_byname()` computes entry size from name and value lengths.
- `xfs_attr_sf_entsize()` computes entry size from an entry.
- `xfs_attr_sf_firstentry()`, `xfs_attr_sf_nextentry()`, and `xfs_attr_sf_endptr()` navigate the packed shortform buffer.

## Data Model
Shortform entries contain one-byte name and value lengths, namespace flags, and contiguous `nameval` storage. The total shortform buffer size is stored in the header as big-endian `totsize`; the end pointer helper converts it before pointer arithmetic.

## Integration Points
Used heavily by `xfs_attr_leaf.c` shortform add/remove/find/verify/convert code and by `xfs_attr.c` when estimating whether a new attr fork can start in shortform.

## Risks And Review Focus
- Pointer arithmetic assumes verified packed-entry bounds; callers must validate raw buffers before walking untrusted disk contents.
- One-byte length limits force conversion to leaf format for large names or values.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_sf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.c

## Purpose
Implements small bitmap scanning helpers used by XFS non-realtime code.

## Main Interfaces
- `xfs_bitmap_empty()` returns whether all words in a bitmap are zero.
- `xfs_contig_bits()` counts contiguous set bits starting at a given bit.
- `xfs_next_bit()` finds the next set bit at or after a start bit, or returns `-1`.

## Control Flow
`xfs_bitmap_empty()` linearly scans each word for nonzero content. `xfs_contig_bits()` advances to the starting word, masks bits before the requested start as already set, scans full words equal to `~0U`, and uses `ffz()` to find the first clear bit. `xfs_next_bit()` similarly advances to the starting word, masks off bits before the requested start, scans for a nonzero word, and uses `ffs()` to return the next set bit.

## State And Assumptions
Bitmap sizes are expressed in machine words, not bytes. Bit offsets are converted using `BIT_TO_WORD_SHIFT` and `NBWORD`. `xfs_contig_bits()` asserts that `start_bit` is inside the bitmap, while `xfs_next_bit()` returns `-1` if the start is outside.

## Integration Points
Declared by `xfs_bit.h` and used by XFS code that needs compact bitmap scans without open-coding word and bit arithmetic.

## Risks And Review Focus
- Callers must pass word counts, not byte counts.
- `xfs_contig_bits()` relies on the start bit being in range; unlike `xfs_next_bit()`, it asserts instead of gracefully returning.
- The functions operate on `uint` words and therefore depend on the platform word constants used by XFS.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.h

## Purpose
Declares XFS bit manipulation helpers and provides inline mask and high/low-bit routines.

## Main Interfaces
- Masks: `xfs_mask64hi()`, `xfs_mask32lo()`, `xfs_mask64lo()`.
- High bit: `xfs_highbit32()`, `xfs_highbit64()`.
- Low bit: `xfs_lowbit32()`, `xfs_lowbit64()`.
- Bitmap scans: `xfs_bitmap_empty()`, `xfs_contig_bits()`, `xfs_next_bit()`.

## Main Contents
The high-bit helpers wrap `fls()` and `fls64()` and return `-1` when no bit is set. The low-bit helpers wrap `ffs()` behavior; `xfs_lowbit64()` explicitly checks the lower 32 bits first and then the upper 32 bits, adding 32 when the low set bit is in the high half.

## Integration Points
Included by `xfs_bit.c` and other XFS code needing common mask or bit-index helpers. It relies on kernel bit primitives such as `fls`, `fls64`, `ffs`, and constants such as `NBWORD`.

## Risks And Review Focus
- The mask helpers assume valid `n` ranges; shifting by the type width would be undefined, so callers must avoid invalid counts.
- Return values use XFS’s historical “bit index or `-1`” convention rather than kernel bitops’ one-based `ffs` convention.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.h -->