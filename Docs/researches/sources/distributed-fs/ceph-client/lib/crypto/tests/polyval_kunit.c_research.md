# sources/distributed-fs/ceph-client/lib/crypto/tests/polyval_kunit.c

## Purpose
This file adapts keyed POLYVAL to the shared hash template and adds POLYVAL-specific checks for RFC 8452 compatibility, all-one-bits arithmetic stress, key preparation safety, prepared-key alignment, interrupt-context key preparation, and optional benchmarking.

## Important APIs, Types, and Functions
- `static struct polyval_key test_key` is the fixed suite key used by template wrappers.
- `polyval_init_withtestkey()` and `polyval_withtestkey()` wrap `polyval_init()` and `polyval()`.
- The template macros bind POLYVAL functions and context types to `hash-test-template.h`.
- `test_polyval_rfc8452_testvec()` verifies a concrete AES-GCM-SIV/POLYVAL example from RFC 8452.
- `test_polyval_allones_key_and_message()` mirrors the GHASH all-one-bits stress path with POLYVAL functions and compares to `polyval_allones_hashofhashes`.
- `check_key_consistency()` verifies byte-identical prepared keys and equal hashes over random lengths.
- `test_polyval_with_guarded_key()` catches overreads of raw key or prepared-key output near the guard page.
- `test_polyval_with_minimally_aligned_key()` verifies only `__alignof__(struct polyval_key)` is required.
- `test_polyval_preparekey_in_irqs()` checks `polyval_preparekey()` consistency in task/softirq/hardirq-like contexts.
- `polyval_suite_init()` prepares the deterministic suite key and allocates the shared guarded buffer.

## Control Flow
Suite init prepares the key from deterministic random bytes and delegates buffer setup to the template. Generated template cases run first, followed by RFC compatibility, all-one-bits, guarded-key, alignment, IRQ key-preparation, and benchmark cases. Suite exit calls `hash_suite_exit()`.

## State and Persistence Behavior
Suite state consists of `test_key` plus the template's guarded buffer and PRNG state. Test-specific keys, contexts, and hashes are stack locals. There is no persistence.

## Dependencies and Integration Points
The file depends on `<crypto/gf128hash.h>`, `polyval-testvecs.h`, `hash-test-template.h`, KUnit, guarded vmalloc behavior through the template, and `kunit_run_irq_test()` through the template. It registers KUnit suite name `polyval`.

## Risks and Edge Cases
The RFC vector is a high-value compatibility check because POLYVAL endianness mistakes can still produce internally consistent template results if fixtures were wrong. The prepared-key equality assumption requires canonical key layout across implementations. Guard and minimal-alignment tests cover specific placements, not every possible unaligned address or vector backend.

## Test Signals
Signals include shared hash-template behavior, generated POLYVAL vector oracles, RFC 8452 compatibility, all-one-bits overflow stress, key overread detection, key alignment validation, interrupt-context preparekey consistency, and optional throughput.
