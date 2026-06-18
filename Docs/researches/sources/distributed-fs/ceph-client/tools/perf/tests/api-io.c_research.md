# sources/distributed-fs/ceph-client/tools/perf/tests/api-io.c

Purpose: `api-io.c` tests perf's buffered `api/io.h` helpers for character, hexadecimal, decimal, and line reads.

Important APIs and state: helpers create temporary files, initialize `struct io`, and clean up buffers, descriptors, and paths. Macros `EXPECT_EQUAL` and `EXPECT_EQUAL64` mark failures while continuing within a case. The suite entry is `test__api_io`, registered as `"Test api io"`.

Control flow: `make_test_file` writes exact test contents to `/tmp/perf-test-XXXXXX`. `setup_test` opens it and initializes a caller-provided buffer size. Character tests iterate through multiple buffer powers to verify refill and EOF. Hex and decimal tests exercise delimiters, invalid leading characters, `0x`-style handling, oversized values, and EOF flags. Line testing verifies a line longer than the internal buffer and a final unterminated line.

State and persistence: temporary files are created and unlinked per case; heap buffers are freed. No durable state remains on success.

Dependencies, integration, risks, and tests: this is a direct perf test suite for `io__get_char`, `io__get_hex`, `io__get_dec`, and `io__getline`. Risks are mostly environment cleanup on early setup failures and assumptions about `/tmp`. Test signals are exact return values, parsed values, EOF flags, line lengths, and no leaked files.
