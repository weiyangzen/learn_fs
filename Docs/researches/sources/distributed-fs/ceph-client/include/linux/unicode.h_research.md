<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unicode.h -->
# sources/distributed-fs/ceph-client/include/linux/unicode.h

Purpose: declares the kernel Unicode/UTF-8 normalization and casefolding interface used by filesystems and dcache name handling.

Important APIs and types: Unicode versions are encoded with `UNICODE_AGE()` and decoded by `unicode_major/minor/rev()`, with `UTF8_LATEST` set to 12.1.0. `enum utf8_normalization` supports `UTF8_NFDI` and `UTF8_NFDICF`. `struct unicode_map` stores the selected version, normalization tables, and table metadata. APIs validate, compare, case-insensitively compare, normalize, casefold, hash folded names, load/unload maps, and parse version strings.

Control flow: filesystems load a Unicode map for a version, validate and normalize/casefold `qstr` names on lookup/create/hash paths, and unload the map at teardown. Case-insensitive lookup can compare raw names or a pre-folded form.

State and persistence: `struct unicode_map` is an in-memory reference to Unicode tables. Normalized/casefolded names may influence persistent directory entries or lookup hashes in filesystems, but the header itself stores no persistent data.

Dependencies and integration points: depends on dcache `qstr`, init annotations, and generated UTF-8 data tables. It integrates with ext4/f2fs casefolding and any VFS-facing filesystem that needs Unicode normalization.

Risks and test signals: risks include version mismatch for persisted casefold policy, invalid UTF-8 acceptance, hash/compare inconsistency, buffer truncation in normalize/casefold, and default-ignorable handling changes. Test with Unicode conformance vectors, invalid sequences, casefold collisions, filesystem lookup/create/rename, and mount options selecting Unicode versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unicode.h -->
