# sources/distributed-fs/ceph-client/tools/perf/tests/util.c

## Purpose
This perf utility test validates two unrelated utility surfaces: character replacement via `strreplace_chars()` and the in-tree BLAKE2s implementation used for build-id-sized hashing.

## Important APIs, Types, And Functions
Local helpers are `test_strreplace()` and `test_blake2s()`, with `test__util()` as the suite entry point. It uses `strreplace_chars()`, `free()`, `strcmp()`, `blake2s_init()`, `blake2s_update()`, `blake2s_final()`, `memcmp()`, and `TEST_ASSERT_VAL()`. Constants are `MAX_DATA_LEN` at 512 and `HASH_LEN` at 20 bytes, matching ELF build ID length.

## Control Flow
`test__util()` asserts replacement behavior for empty strings, no-match input, single replacement, repeated replacement, and replacement strings longer than the needle. It then delegates to `test_blake2s()`. The BLAKE2s test fills deterministic data bytes, hashes every prefix length from 0 through 512, verifies one-shot and two-part update consistency, feeds each digest into a parent BLAKE2s context, then compares the final hash-of-hashes to a Python-generated constant.

## State, Dependencies, And Integration
All state is local stack memory. The file depends on `util/blake2s.h`, `util/debug.h`, `string2.h`, and perf's test macros. It is registered as `DEFINE_SUITE("util", util)`.

## Risks And Test Signals
The string-replacement assertions catch allocation or expansion errors in common cases but do not test allocation failure. The hash test is deterministic and relatively broad across input lengths; failures indicate a regression in streaming, finalization, digest sizing, or endian/byte handling.
