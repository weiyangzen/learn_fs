# sources/distributed-fs/ceph-client/fs/hfsplus/unicode_test.c

## Purpose
`unicode_test.c` provides KUnit coverage for the HFS+ Unicode string, conversion, hash, and dentry-compare helpers. It exercises the exported-for-KUnit functions in `unicode.c` with mocked HFS+ strings, superblock private state, NLS callbacks, and dentry/qstr objects.

## Important APIs, types, and functions
The test suite is registered as `hfsplus_unicode`. Helpers include `struct test_mock_string_env`, `setup_mock_str_env()`, `free_mock_str_env()`, `create_unistr()`, `corrupt_unistr()`, `struct test_mock_sb`, `setup_mock_sb()`, `free_mock_sb()`, `test_uni2char()`, `test_char2uni()`, `check_unistr_content()`, `setup_mock_dentry()`, and `create_qstr()`.

The suite lists 27 test cases covering `hfsplus_strcasecmp`, `hfsplus_strcmp`, Unicode edge/boundary behavior, `uni2asc`, `asc2uni`, dentry hashing, dentry comparison, casefold flags, decomposition flags, special-character handling, long strings, embedded NULs, and combined flags. It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace.

## Control flow
Most tests allocate a small mock environment, populate HFS+ big-endian Unicode strings from ASCII fixtures, call the target helper, assert return values and output state, and free allocations. Conversion tests install simple mock NLS callbacks: `test_uni2char()` passes ASCII and maps non-ASCII to `?`; `test_char2uni()` maps one input byte to the same Unicode code point.

The hash/compare tests create a static mock dentry with a mock superblock, then toggle `HFSPLUS_SB_CASEFOLD` and `HFSPLUS_SB_NODECOMPOSE` to verify case sensitivity, case-insensitive equality, colon/slash normalization, long-name behavior, and deterministic hash output. The suite registration at the end supplies all cases to KUnit.

## State and persistence behavior
The tests do not touch disk or persistent filesystem state. They emulate the runtime state that affects Unicode behavior: `s_fs_info`, NLS callbacks, and HFS+ superblock flags. Memory is dynamically allocated and freed per test helper usage, with some static dentry state reset before hash/compare tests.

## Dependencies and integration points
It depends on KUnit, Linux NLS and dcache/stringhash headers, `hfsplus_fs.h`, and the KUnit-visible exports in `unicode.c`. It is a direct unit-test signal for table-driven Unicode behavior but does not mount HFS+ images or exercise catalog/B-tree integration.

## Risks and test signals
The test file's strengths are broad coverage of ASCII-oriented behavior, boundary lengths, corrupted HFS+ length fields, slash/colon mapping, embedded NULs, and flag combinations. Gaps include real UTF-8/NLS behavior, actual non-ASCII decomposition/composition vectors, Hangul syllable decomposition/composition, xattr-specific conversion, KASAN-style bounds checking for table offsets, and integration with catalog key ordering. Risks in the tests themselves include the mock NLS simplifying non-ASCII to `?`, possible polarity confusion in comments around `NODECOMPOSE`, and reliance on a static dentry object.
