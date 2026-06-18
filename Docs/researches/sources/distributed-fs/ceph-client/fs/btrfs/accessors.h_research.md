# sources/distributed-fs/ceph-client/fs/btrfs/accessors.h

## Purpose
Defines the typed accessor API for Btrfs on-disk metadata structures. It centralizes little-endian conversion, unaligned access, extent-buffer member reads/writes, stack-structure reads/writes, header access, key conversion, item pointer arithmetic, and field-specific helpers for a broad set of Btrfs tree items.

## Important APIs, Types, And Functions
The foundational macros are `read_eb_member()`, `write_eb_member()`, `DECLARE_BTRFS_SETGET_BITS()`, `BTRFS_SETGET_FUNCS()`, `BTRFS_SETGET_HEADER_FUNCS()`, and `BTRFS_SETGET_STACK_FUNCS()`. They generate type-checked helpers using `static_assert()` and `sizeof_field()`.

Generated or hand-written accessor families cover device items, chunks and stripes, block group items including v2/remap fields, free-space records, inode refs and inode items, timespecs, RAID stride records, device extents, extent refs and inline-ref sizing, node pointers, leaf items, directory/root refs, free-space headers, disk-key conversions, tree headers, root items/backups, balance items, superblock fields, file extents, qgroup status/info/limits, device replace state, fs-verity descriptor items, and remap items. `btrfs_item_ptr()` and `btrfs_item_ptr_offset()` convert leaf slots to item data offsets.

## Control Flow
Most helpers are inline field translations. Extent-buffer helpers pass an offset-like cast pointer plus a field offset into the out-of-line `btrfs_get_*()`/`btrfs_set_*()` functions implemented in `accessors.c`. Stack helpers operate on in-memory structs with unaligned little-endian loads/stores. Header helpers assume the tree header is in the first folio at `offset_in_page(eb->start)`. Key conversion helpers are optimized to `memcpy()` on little-endian builds and perform explicit `le64_to_cpu()`/`cpu_to_le64()` conversions on big-endian builds.

Special helpers add semantics beyond raw field access. `btrfs_set_device_total_bytes()` warns if the value is not sector-size aligned. `btrfs_extent_inline_ref_size()` maps inline-ref key types to their record sizes. Header flag helpers set, clear, and decode backref revision bits. Item helpers compute slot offsets and item data extents.

## State And Persistence
Header and extent-buffer setters mutate Btrfs metadata buffers; stack setters mutate temporary in-memory copies. Persistence is controlled by the surrounding transaction and extent-buffer writeback code, not by this header. The header also encodes invariants: field sizes must match expected integer widths at compile time, and all on-disk multi-byte fields are treated as little-endian.

## Dependencies And Integration Points
The header depends on UAPI Btrfs tree structure definitions, `struct extent_buffer` and folio layout from `extent_io.h`, filesystem state from `fs.h`, Linux unaligned access helpers, and endian macros. It is widely included across Btrfs tree manipulation, mount, transaction, scrub, qgroup, send, balance, device replace, and tree-checker code.

## Risks
This is a high-blast-radius header. A wrong field width, offset, endian conversion, or pointer calculation can corrupt filesystem metadata across many call sites. Header helpers assuming the first folio must remain consistent with extent-buffer allocation. The little-endian fast path relies on `struct btrfs_key` and `struct btrfs_disk_key` layout compatibility. Adding on-disk fields without accessor updates can lead to ad hoc access and missed validation.

## Test Signals
Signals include compiler `static_assert()` failures, sparse/endian warnings, Btrfs KUnit or module-load sanity tests over extent buffers and tree items, cross-endian build coverage, filesystem mount and scrub of metadata-heavy images, tree-checker validation, and tests that exercise leaf item pointer arithmetic, inline refs, qgroups, device replace, and superblock parsing.
