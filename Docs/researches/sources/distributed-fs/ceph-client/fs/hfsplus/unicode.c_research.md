# sources/distributed-fs/ceph-client/fs/hfsplus/unicode.c

## Purpose
`unicode.c` implements HFS+ Unicode string comparison, case folding, filename conversion between HFS+ UTF-16-ish names and Linux/NLS byte strings, HFS+/Linux special-character compatibility mapping, decomposition/composition, dentry hashing, and dentry comparison. It is the main enforcement point for HFS+ and HFSX filename semantics.

## Important APIs, types, and functions
Public functions are `hfsplus_strcasecmp()`, `hfsplus_strcmp()`, `hfsplus_uni2asc_str()`, `hfsplus_uni2asc_xattr_str()`, `hfsplus_asc2uni()`, `hfsplus_hash_dentry()`, and `hfsplus_compare_dentry()`. Many are exported with `EXPORT_SYMBOL_IF_KUNIT` for unit testing.

Important internal helpers are `case_fold()`, `hfsplus_compose_lookup()`, `hfsplus_mac2linux_compatibility_check()`, `hfsplus_uni2asc()`, `hfsplus_linux2mac_compatibility_check()`, `asc2unichar()`, `hfsplus_decompose_nonhangul()`, `hfsplus_try_decompose_hangul()`, and `decompose_unichar()`.

## Control flow
Case-insensitive comparison clamps invalid lengths to `HFSPLUS_MAX_STRLEN`, folds each 16-bit character through `hfsplus_case_fold_table`, skips folded-zero ignorables, and compares folded values. Case-sensitive comparison clamps lengths and lexicographically compares raw big-endian 16-bit values.

HFS+ to Linux conversion (`hfsplus_uni2asc`) reads HFS+ Unicode characters, optionally composes decomposed sequences unless `HFSPLUS_SB_NODECOMPOSE` is set, handles Hangul algorithmic composition, maps HFS+ NUL to U+2400 and slash to colon for regular filenames, skips that compatibility mapping for xattr names, and emits bytes through the mounted NLS table. NLS conversion failures become `?` except `-ENAMETOOLONG`, which stops with an error and reports consumed length.

Linux to HFS+ conversion (`hfsplus_asc2uni`) repeatedly calls `char2uni`, maps U+2400 back to NUL and colon to slash for regular filenames, optionally decomposes non-Hangul characters through the table and Hangul syllables algorithmically, writes big-endian 16-bit output, and returns `-ENAMETOOLONG` if input remains after the maximum HFS+ name length is filled.

Dentry hashing and comparison both convert incoming byte names through NLS, optionally decompose, optionally case-fold, skip ignorable folded characters, and use Linux stringhash or lexicographic comparison over the resulting HFS+ semantic code units.

## State and persistence behavior
The file does not persist metadata directly, but it determines persistent namespace keys and lookup behavior. Superblock flags `HFSPLUS_SB_CASEFOLD` and `HFSPLUS_SB_NODECOMPOSE` alter hash, compare, and conversion semantics. The mounted NLS table affects byte encoding. Special-character mapping preserves HFS+ names containing slash or NUL while exposing Linux-compatible names.

## Dependencies and integration points
It depends on NLS tables, HFS+ Unicode mapping arrays from `tables.c`, superblock flags, Linux dentry stringhash helpers, catalog key creation/comparison through the declared API, and KUnit visibility exports. `inode.c` installs these functions into `hfsplus_dentry_operations`.

## Risks and test signals
Risks include casefold table bounds assumptions, invalid length correction reading padded or uninitialized entries, mismatched hash and compare normalization, NLS conversion lossy fallback causing name collisions, xattr names intentionally bypassing slash/NUL compatibility conversion, Hangul edge-case mistakes, and polarity confusion around `NODECOMPOSE`. Test signals include KUnit vectors, real HFS+/HFSX images with casefolded and decomposed names, slash/colon and NUL/U+2400 round trips, xattr name conversion, ENAMETOOLONG boundaries, non-ASCII NLS behavior, ignorable characters, and hash/compare equivalence checks.
