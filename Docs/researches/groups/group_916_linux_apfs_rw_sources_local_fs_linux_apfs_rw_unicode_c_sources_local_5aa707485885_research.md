# Group Research: group_916_linux_apfs_rw_sources_local_fs_linux_apfs_rw_unicode_c_sources_local_5aa707485885

Scope confirmed from `Docs/research_subset_a.md`: `sources/local-fs/linux-apfs-rw` is included in subset A. All four listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/unicode.c -->
# File Research: sources/local-fs/linux-apfs-rw/unicode.c

This file implements APFS filename Unicode normalization and optional case folding for the Linux APFS read-write driver. It is used by catalog key comparison, filename hashing/key generation, and directory/name lookup paths that need APFS-style normalized Unicode semantics.

Public API:
- `apfs_init_unicursor(struct apfs_unicursor *cursor, const char *utf8str, unsigned int total_len)` initializes cursor state over a UTF-8 byte string.
- `apfs_normalize_next(struct apfs_unicursor *cursor, bool case_fold)` returns one normalized UTF-32 codepoint at a time, with optional case folding.

Core implementation:
- `apfs_trie_find()` is a shared lookup helper for three static Unicode data tries. For NFD and case-folding tries it returns a position and length into a value array; for canonical combining class lookup it returns the CCC value directly.
- `apfs_is_precomposed_hangul()` and `apfs_decompose_hangul()` implement algorithmic Hangul syllable decomposition using Unicode 9.0 constants.
- `apfs_normalize_char()` decomposes one UTF-32 codepoint into NFD form and then applies case folding if requested. Characters absent from the lookup tables normalize to themselves.
- `apfs_get_normalization_length()` scans forward from the current UTF-8 position until the next starter after a combining sequence, counting the number of normalized codepoints in that segment.
- `apfs_normalize_next()` emits normalized codepoints in canonical combining class order. For ASCII it has a fast path using `tolower()` when case folding is requested; for non-ASCII it computes a segment length, repeatedly scans the segment, and selects the next codepoint by CCC and position.

Static data:
- `apfs_nfd_trie` plus `apfs_nfd` encode Unicode 9.0 canonical decomposition data.
- `apfs_cf_trie` plus `apfs_cf` encode Unicode 9.0 case-fold mappings.
- `apfs_ccc_trie` encodes canonical combining class values.
- The data tables occupy most of the file and are generated/static Unicode reference data rather than driver control logic.

Integration points:
- `namei.c` uses the cursor to build normalized names for lookup.
- `key.c` uses it for APFS name comparison and key construction.
- The header contract is declared in `unicode.h`.

Important behavior and edge cases:
- Invalid UTF-8 makes normalization return `0`, which is also the end/invalid sentinel for callers.
- Normalization is segment-based: it reorders combining marks only within the substring ending before the next starter.
- The ASCII fast path checks `*utf8str` before checking `total_len`; current callers appear to provide real string storage, but this is a boundary assumption worth preserving if call sites change.
- Embedded NUL bytes terminate normalization because the scanner checks `!*utf8str`, even though a separate byte length is also tracked.

Testing signals:
- High-value tests would cover APFS name comparison for composed/decomposed Latin characters, Hangul syllables, combining mark reordering, invalid UTF-8, ASCII case-folding, and embedded NUL behavior.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/unicode.h -->
# File Research: sources/local-fs/linux-apfs-rw/unicode.h

This header declares the APFS Unicode normalization cursor interface used by filename/key handling code.

Exports:
- `struct apfs_unicursor` stores the current UTF-8 pointer, remaining total byte length, normalized segment length, last emitted normalized position, and last canonical combining class.
- `apfs_init_unicursor()` initializes the cursor over a UTF-8 string.
- `apfs_normalize_next()` advances the cursor and returns one normalized UTF-32 codepoint, optionally case folded.

Dependencies:
- Includes `<linux/nls.h>` for `unicode_t`.
- Consumed by `unicode.c`, with call sites in `namei.c` and `key.c`.

Design notes:
- The cursor exposes enough state for `unicode.c` to reorder combining marks without allocating a normalized string.
- Callers should treat return value `0` as end or invalid normalization, matching the implementation’s sentinel behavior.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/xattr.c -->
# File Research: sources/local-fs/linux-apfs-rw/xattr.c

This file implements APFS extended attribute support for the Linux VFS xattr interface and for APFS-internal compressed-resource data. APFS stores xattr records in the catalog tree, with values either embedded inline or referenced through a separate data stream.

Public/internal APIs:
- `____apfs_xattr_get()` reads a named xattr, optionally allowing partial reads for header-only compressed-file probing.
- `__apfs_xattr_get()` wraps the strict whole-value read form without locking.
- `apfs_xattr_get_compressed_data()` loads compressed data metadata/value for compression paths.
- `apfs_release_compressed_data()` releases storage allocated by compressed-data lookup.
- `apfs_compressed_data_read()` reads from inline compressed data or dstream-backed compressed data.
- `apfs_xattr_set()` creates, replaces, or deletes a named APFS xattr inside an active transaction.
- `apfs_delete_all_xattrs()` removes all xattrs for an inode while the caller holds `nx_big_sem` for writing.
- `apfs_listxattr()` implements VFS listxattr with the fake Linux namespace prefix.

Core control flow:
- `apfs_xattr_from_query()` converts a successful catalog-tree query into an in-memory `struct apfs_xattr`, validating name length, NUL termination, value length, and dstream flag consistency.
- Inline reads copy directly from catalog record value bytes.
- Dstream reads allocate a temporary `apfs_dstream_info`, populate it from xattr metadata, and call `apfs_nonsparse_dstream_read()`.
- Set operations build a catalog key/value pair, choose inline versus dstream storage based on `APFS_XATTR_MAX_EMBEDDED_SIZE`, insert or replace the btree record, then truncate any old dstream after the record has been replaced.
- Delete operations remove inline xattrs directly; dstream xattrs remove the catalog record first and then truncate the associated dstream.
- VFS `.get` and `.set` handlers intentionally strip the fake `XATTR_MAC_OSX_PREFIX`; on disk APFS xattrs have no Linux namespace prefix.

Kernel compatibility:
- `apfs_xattr_osx_set()` has signature variants for kernels before 5.12, kernels before 6.3 excluding newer RHEL 9.6 handling, and newer kernels using `struct mnt_idmap`.

Integration points:
- `apfs_xattr_handlers` is used by the inode operations.
- `apfs_listxattr()` is wired in `namei.c`, `file.c`, and `symlink.c`.
- Compression code calls `____apfs_xattr_get()` and `apfs_xattr_get_compressed_data()`.
- Symlink creation uses `apfs_xattr_set()` for `APFS_XATTR_NAME_SYMLINK`.

Error handling and safety:
- Corrupt on-disk records return `-EFSCORRUPTED` after consistency checks.
- Oversized dstream-backed xattrs return `-E2BIG` if the 64-bit APFS size cannot fit Linux `int` handling.
- VFS whole-read semantics return `-ERANGE` if the user buffer is too small.
- Allocation failures return `-ENOMEM`; btree and transaction failures propagate.
- `apfs_xattr_get()` serializes reads with `nx_big_sem`; transaction-starting VFS set wraps `apfs_xattr_set()` with commit/abort.

Risks and watchpoints:
- Dstream creation writes blocks before the catalog xattr record exists; failure cleanup frees the temporary dstream object but relies on transaction semantics for on-disk rollback.
- `apfs_create_xattr_dstream()` uses pointer arithmetic on `const void *value`, which is accepted as a compiler extension but is not strictly standard C.
- Several size paths narrow APFS 64-bit sizes to `int`; the file has an explicit TODO for huge compressed files.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/xfield.c -->
# File Research: sources/local-fs/linux-apfs-rw/xfield.c

This file implements helpers for APFS extended fields stored inside inode and dentry records. Extended fields are represented as an `apfs_xf_blob` header, followed by fixed-size metadata entries, followed by padded value data.

Exports:
- `apfs_find_xfield(u8 *xfields, int len, u8 xtype, char **xval)` locates the value for one xfield type and returns its padded length, or `0` if absent/corrupt.
- `apfs_init_xfields(u8 *buffer, int buflen)` initializes an empty xfield collection.
- `apfs_insert_xfield(u8 *buffer, int buflen, const struct apfs_x_field *xkey, const void *xval)` inserts or replaces an xfield in an in-memory buffer and returns the new collection length.

Core behavior:
- `apfs_find_xfield()` validates the blob header and metadata array fit inside the supplied length, walks each xfield entry, rounds each value length up to 8 bytes, and returns a pointer into the value area for the matching type.
- `apfs_init_xfields()` writes zero count and used-data fields.
- `apfs_insert_xfield()` supports both replacement and insertion. Replacement updates metadata, resizes the padded value, shifts trailing value bytes with `memmove()`, and updates used-data. Insertion creates a new metadata entry, shifts existing payload to make room, writes value bytes, zero-fills padding, and updates blob counters.

Integration points:
- Directory code uses these helpers for dentry sibling IDs and related APFS directory metadata.
- Inode code uses them for name, device number, sparse-byte count, and other inode extended fields.
- Prototypes live in `apfs.h`.

Error and corruption handling:
- The helpers return `0` for missing fields, invalid/corrupt layouts, or insufficient buffer capacity, so callers must distinguish “not found” from “bad collection” by context.
- Value sizes are always padded to 8 bytes, matching APFS xfield layout expectations.
- Callers must validate expected structure sizes before casting `*xval`, as noted in the function comment.

Risks and watchpoints:
- `apfs_insert_xfield()` mutates the buffer before all final capacity checks complete in some paths; current callers appear to operate on prepared in-memory construction buffers, but failed insertions should not be assumed to leave the buffer untouched.
- The API returns padded value length, not logical `x_size`, which is correct for traversal but important for typed consumers.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/xfield.c -->