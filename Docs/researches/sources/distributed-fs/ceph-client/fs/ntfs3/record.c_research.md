# sources/distributed-fs/ceph-client/fs/ntfs3/record.c

## Purpose
`record.c` manages individual NTFS MFT records: reading, validating, enumerating attributes, finding attributes, writing dirty records, formatting new records, inserting/removing attributes, resizing resident attributes, and repacking nonresident runs.

## Important APIs and Functions
`mi_get()` allocates and reads a `mft_inode`; `mi_put()` frees it. `mi_init()` allocates record memory. `mi_read()` reads through `$MFT` runs, reloads missing runs, marks fixup-repaired records dirty, and validates record size. `mi_enum_attr()` validates and enumerates resident/nonresident attributes. `mi_find_attr()` filters by type/name/id. `mi_write()` flushes dirty record buffers and flags MFT mirror updates. `mi_format_new()` prepares reusable records with sequence handling. `mi_insert_attr()`, `mi_remove_attr()`, `mi_resize_attr()`, and `mi_pack_runs()` mutate record contents.

## Control Flow
Reads take the `$MFT` run lock when mounted. If the read misses a run, the code loads the needed run range and retries. Enumeration starts at `attr_off`, validates bounds and alignment, and stops at `ATTR_END`. Insertions preserve sorted attribute order using the upcase table, make room with `memmove()`, assign an id, and mark dirty.

## State and Persistence Behavior
`mft_inode::mrec` is the in-memory copy of persistent MFT bytes and `nb` holds buffer heads. Mutations update `rec->used`, attribute headers, hardlink counts for indexed name removal, and dirty flags. Formatting increments sequence numbers for stale handle detection.

## Dependencies and Integration Points
This file depends on `ntfs_read_bh()`, `ntfs_write_bh()`, `ntfs_get_bh()`, `attr_load_runs_vcn()`, `run_pack()`, `ntfs_cmp_names()`, and inode bad-state marking. Higher-level inode, attrlist, xattr, security, and directory code rely on it.

## Risks
This is a metadata corruption boundary. Off-by-one validation, overlapping moves, bad ordering, or wrong `rec->used` updates can damage the MFT. Fixup and run-retry handling must not mask real corruption.

## Test Signals
Use images with full records, many attributes, named streams, resident/nonresident transitions, fragmented `$MFT`, bad fixups, reused records, and mirrored records. Fuzz MFT attributes for clean errors.
