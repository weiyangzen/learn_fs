
# sources/distributed-fs/ceph-client/lib/tests/base64_kunit.c

## Purpose
`base64_kunit.c` validates kernel Base64 encoding and decoding for standard, URL-safe, and IMAP variants, with and without padding. It also includes a small timing benchmark for the standard variant.

## Important APIs, types, and functions
The suite calls `base64_encode()`, `base64_decode()`, `get_random_bytes()`, `ktime_get_ns()`, `div64_u64()`, `kmalloc()`, `kfree()`, and KUnit assertions. Helpers `expect_encode_ok()`, `expect_decode_ok()`, and `expect_decode_err()` wrap output length, string, memory, and error checks. `run_perf_and_check()` allocates buffers, does a random round trip, then reports average encode/decode nanoseconds with `kunit_info()`.

## Control flow
`base64_test_cases` registers four tests: performance, standard encode vectors, standard decode vectors, and variant checks. The encode/decode tests walk RFC-style examples (`f`, `fo`, `foo`, `foobar`) plus longer alphabet and punctuation strings. Decode tests cover invalid characters, malformed padding, too-short padded input, excess padding, embedded NUL, and mismatched padding policy. Variant tests derive expected URL-safe and IMAP output by rewriting standard `+`, `/` characters and verify decoding back to the sample bytes.

## State and persistence
All state is stack- or heap-local to each test. Random benchmark input is transient and not used as a golden vector. No global mutable state or persistent output is kept beyond KUnit logs.

## Dependencies and integration points
The file depends on `<linux/base64.h>` and KUnit. It is built through `CONFIG_BASE64_KUNIT` in the tests Makefile.

## Risks and edge cases
The benchmark test is not a strict performance gate; it can add noise to test logs and runtime. Fixed 128-byte helper buffers are adequate for listed vectors but would need resizing for larger new cases. Error behavior assumes `base64_decode()` returns `-1` for invalid input.

## Test signals
Pass signals are KUnit equality, string, and memory assertions. Performance emits informational timing lines for 64B and 1KB standard-variant round trips.
