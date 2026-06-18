# sources/distributed-fs/ceph-client/lib/kunit/assert_test.c

Purpose: KUnit self-test suite for assertion formatting helpers in `assert.c`.

Important APIs/tests: tests cover `is_literal`, `is_str_literal`, `kunit_assert_prologue`, `kunit_assert_print_msg`, unary, not-err pointer, binary integer, binary pointer, binary string, hexdump, and memory assertion formatting. Helpers include `get_str_from_stream()`, `verify_assert_print_msg()`, and `validate_assert()`.

Control flow: each test allocates a managed `string_stream`, invokes a formatter with synthetic assertion structures, extracts the stream text, and checks for expected substrings or absence of hexdump markers. Pointer tests render expected addresses with `%px` to remain architecture-length independent.

State and persistence: managed allocations are tied to the test context using KUnit actions and allocators. Static test buffers provide deterministic hexdump comparisons.

Dependencies and integration: depends on KUnit core, assertion internals exposed to KUnit, and `string-stream`. Registered as suite `kunit-assert`.

Risks: substring-based checks can miss ordering or exact formatting regressions; `%px` output may depend on pointer hashing settings, though both expected and actual use the same formatter style.

Test signals: the file itself is the test signal for assertion diagnostics; it runs when `CONFIG_KUNIT_TEST` is built-in according to the Makefile.
