<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_hash.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_hash.c

## Purpose
KUnit coverage for integer and string hashing helpers in `linux/hash.h` and `linux/stringhash.h`, checking equivalence between generic and architecture-specific implementations and sufficient bit coverage.

## APIs, Types, and Functions
Helper functions `xorshift()`, `mod255()`, and `fill_buf()` generate deterministic nonzero strings. `test_int_hash()` exercises `__hash_32()`, `hash_32()`, and `hash_64()` for output widths 1 through 32, optionally comparing to `__hash_32_generic()` and `hash_64_generic()` under architecture feature macros. `test_string_or()` checks `full_name_hash()` coverage. `test_hash_or()` compares `hashlen_string()` length/hash results to `full_name_hash()` across substrings and feeds hash outputs into integer hash tests.

## Control Flow, State, and Persistence
The test fills a 256-byte buffer with deterministic nonzero bytes, then loops over every substring endpoint. For each substring it temporarily NUL-terminates at `j`, computes hashes from `buf+i`, updates OR accumulators, and asserts lengths and bounded k-bit outputs. Final assertions require OR coverage of all expected result bits. State is local to each KUnit case.

## Dependencies and Integration
Depends on KUnit, kernel hash/stringhash headers, compiler attributes, and architecture feature macros such as `HAVE_ARCH__HASH_32` and `HAVE_ARCH_HASH_64`. It integrates as the `hash` KUnit suite.

## Risks and Test Signals
Risks include cubic runtime sensitivity to `SIZE`, probabilistic coverage assumptions, and conditional paths that only run on some architectures. Test signals are exhaustive substring comparisons, generic-vs-arch equality where required, k-bit upper-bound checks, and final OR masks covering all bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_hash.c -->
