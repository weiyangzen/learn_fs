# sources/distributed-fs/ceph-client/fs/hfs/string_test.c

Purpose: KUnit coverage for classic HFS string comparison, dentry hashing, and dentry comparison.

Important APIs and control flow: `hfs_strcmp_test()` checks equality, inequality, length ordering, case-insensitive behavior, special filename strings, and one-character boundaries. `hfs_hash_dentry_test()` builds three `qstr` values, hashes them, expects case variants to hash equally, and expects a different name to hash differently. `hfs_compare_dentry_test()` checks exact, case-insensitive, different-name, different-length, empty-string, and `HFS_NAMELEN` boundary comparisons. The suite is registered as `hfs_string` and imports the KUnit export namespace.

State and persistence: no filesystem state is persisted. The tests exercise pure functions that affect dentry-cache lookup and catalog key comparison.

Dependencies and integration: depends on KUnit, `linux/dcache.h`, and exported symbols from `string.c` via `EXPORT_SYMBOL_IF_KUNIT`. Build integration depends on the corresponding kernel config/Makefile entries outside this file.

Risks and test signals: the tests are valuable smoke coverage but mostly ASCII-focused; they do not exhaust the Mac `caseorder` table, high-bit characters, or all punctuation ordering that the catalog tree relies on. Additional tests should assert hash/compare consistency for overlong names and Mac-encoded bytes above 0x7f.
