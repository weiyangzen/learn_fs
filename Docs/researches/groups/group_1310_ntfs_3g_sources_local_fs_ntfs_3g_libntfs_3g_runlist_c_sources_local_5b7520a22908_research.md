# Group Research: group_1310_ntfs_3g_sources_local_fs_ntfs_3g_libntfs_3g_runlist_c_sources_local_5b7520a22908

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/ntfs-3g` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/runlist.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/runlist.c

## Scope

Implements NTFS runlist handling for libntfs-3g: in-memory runlist allocation, extension, merge/splice operations, mapping-pair decompression and rebuilding, VCN-to-LCN translation, runlist-backed scatter/gather I/O, truncation, sparse detection, and compressed-size accounting.

## API And Behavior

- Low-level helpers move/copy runlist elements and grow storage in 4 KiB allocation units.
- `ntfs_runlists_merge()` handles inserting newly mapped/allocation runs into holes, not-mapped regions, or runlist ends while preserving sentinel terminators.
- `ntfs_mapping_pairs_decompress()` converts on-disk non-resident mapping pairs into runlists and validates malformed bounds, VCNs, sparse runs, and extent completeness.
- `ntfs_rl_pread()` and `ntfs_rl_pwrite()` implement runlist-backed gather/scatter I/O, zero-fill or skip sparse holes, retry `EINTR`, and return partial counts when appropriate.
- Mapping-pair build helpers encode signed run lengths and LCN deltas, omit NTFS 3.x sparse LCN fields, and report `ENOSPC` with continuation position.
- Truncation/sparse/compressed-size helpers support attribute shrink and compressed file accounting.
- `NTFS_TEST` includes standalone merge/decompression tests.

## Risks And Invariants

Runlists must remain VCN-sorted, logically adjacent, and correctly terminated by `LCN_ENOENT` or `LCN_RL_NOT_MAPPED`. Mapping-pair builders require fully mapped runlists. Some late terminator-repair allocation failures are treated as unrecoverable. Sparse writes intentionally discard caller bytes for holes.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/runlist.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/security.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/security.c

## Scope

Implements NTFS security descriptor support: SID/GUID formatting, `$Secure` storage/index maintenance, security-id reuse/allocation, descriptor retrieval/update/upgrade, POSIX ACL and Unix ownership mapping, permission checks, NTFS attribute xattrs, and offline Win32-like security APIs.

## API And Behavior

- Converts GUIDs/SIDs to strings, generates GUIDs, and hashes security descriptors for `$SDH`.
- Maintains `$Secure:$SDS`, `$SII`, and `$SDH`; descriptors are written twice 256 KiB apart and indexed by security ID/hash.
- Reuses existing descriptors on hash/full-descriptor match or allocates new IDs through `$Secure`.
- Updates legacy NTFS 1.x per-file security attributes or NTFS 3.x `STANDARD_INFORMATION.security_id`.
- Retrieves descriptors from `$Secure` or inode attributes, synthesizing a minimal admin descriptor when missing.
- Caches security-ID to owner/group/mode/POSIX ACL and reverse uid/gid/mode to security-ID lookups.
- Implements POSIX ACL inheritance/access paths when compiled with `POSIXACLS`, with plain mode-bit fallback otherwise.
- Exposes chmod/chown/ACL mutation, owner checks, create/access checks, SID mapping setup, NTFS file attributes, `$Secure` open/close, and `SECURITY_API` helpers.

## Risks And Invariants

`$Secure` writes are not transactional; comments document tolerated partial failure states. Calls are expected to be serialized, with only a reentry guard. Cache pointers must not be retained across later cache updates. NTFS ACL to POSIX permission mapping is approximate. `ntfs_guid_is_zero()` is documented like a zero check but returns raw `memcmp()` behavior.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/security.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/unistr.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/unistr.c

## Scope

Implements NTFS UTF-16LE string handling: comparisons, collation, case folding, UTF-16LE/UTF-8 and locale conversion, `$UpCase`/lowercase table construction, filename validation, DOS/Win32 reserved-name checks, encoding selection, and optional macOS normalization.

## API And Behavior

- Compares NTFS names case-sensitively or case-insensitively using upcase tables.
- `ntfs_names_full_collate()` matches NTFS directory collation semantics, including original-case tie-breaking.
- Converts between UTF-16LE and UTF-8 by default, with locale multibyte fallback when configured.
- Handles surrogate pairs and optionally tolerates broken Unicode via `ALLOW_BROKEN_UNICODE`.
- Builds default 65,536-entry NTFS upcase tables from Windows mappings and derives lowercase tables.
- Converts host strings to NTFS filenames with the 255-character limit and preserves `AT_UNNAMED`.
- Rejects forbidden Win32 characters, trailing dot/space in strict mode, and reserved DOS device names.
- macOS builds can normalize UTF-8 to NFC/NFD through CoreFoundation.

## Risks And Invariants

All NTFS strings are assumed little-endian. Encoding mode is process-global. `ALLOW_BROKEN_UNICODE` defaults to permissive behavior, improving compatibility but weakening strict validation. `ntfs_upcase_table_build()` assumes a sufficiently large buffer. macOS normalization may replace allocated buffers or copy into caller buffers.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/unistr.c -->