# sources/distributed-fs/ceph-client/security/apparmor/policy_unpack_test.c

Purpose: KUnit coverage for the low-level AppArmor binary unpack primitives exported under `EXPORTED_FOR_KUNIT_TESTING`.

Important APIs, types, and functions: defines `struct policy_unpack_fixture`, `build_aa_ext_struct()`, `policy_unpack_test_init()`, and KUnit cases for `aa_inbounds()`, `aa_unpack_array()`, `aa_unpack_blob()`, `aa_unpack_str()`, `aa_unpack_strdup()`, `aa_unpack_nameX()`, `aa_unpack_u16_chunk()`, `aa_unpack_u32()`, `aa_unpack_u64()`, and `aa_unpack_X()`. Test data is built with typed tags, named elements, little-endian integer encodings, and offsets derived from string sizes.

Control flow: each test starts from a fixture buffer with serialized AppArmor elements, adjusts `e->pos` and sometimes `e->end`, invokes one unpack helper, and asserts returned data plus cursor position. Negative tests verify that helpers fail cleanly and reset `e->pos` when a name/code/bounds check fails.

State and persistence: no persistent state; all allocations are KUnit-managed except strings returned by `aa_unpack_strdup()`, which tests free explicitly. Some tests intentionally extend `e->end` beyond allocated data only for pointer arithmetic comparisons.

Dependencies and integration: included by KUnit when AppArmor policy unpack testing is enabled; imports the KUnit export namespace and validates functions in `policy_unpack.c`.

Risks and test signals: coverage is strong for primitive cursor behavior but does not exercise full profile unpacking, DFA parsing, tag verification, or compatibility mapping. Important signals are preserving cursor rollback, rejecting out-of-bounds reads, ensuring duplicated strings are outside the source buffer, and matching little-endian integer values.
