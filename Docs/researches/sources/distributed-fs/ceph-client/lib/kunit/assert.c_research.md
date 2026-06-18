# sources/distributed-fs/ceph-client/lib/kunit/assert.c

Purpose: serializes KUnit expectation/assertion failures into `string_stream` output, including scalar, pointer, string, and memory comparison diagnostics.

Important APIs: `kunit_assert_prologue`, `kunit_fail_assert_format`, `kunit_unary_assert_format`, `kunit_ptr_not_err_assert_format`, `kunit_binary_assert_format`, `kunit_binary_ptr_assert_format`, `kunit_binary_str_assert_format`, `kunit_assert_hexdump`, and `kunit_mem_assert_format`. KUnit-visible helpers `is_literal`, `is_str_literal`, and `kunit_assert_print_msg` support concise output and tests.

Control flow: formatters downcast the base `struct kunit_assert` to a specific assertion type, emit a standardized message, optionally suppress redundant value lines when operands are literals, and append custom va_format messages. Memory assertions validate NULL sides first, then print two hexdumps marking differing bytes with angle brackets.

State and persistence: no persistent state; output accumulates in the caller-provided `string_stream`.

Dependencies and integration: depends on KUnit assert/test headers, visibility annotations, and `string-stream`. The KUnit macro layer calls these formatters for failed checks.

Risks: formatting must avoid misleading output when operand text is a literal; `is_literal()` allocates temporarily and can suppress output incorrectly only if string conversion matches exactly; hexdump size comes from the assertion and must be trustworthy.

Test signals: `assert_test.c` directly validates literals, prologue output, message appending, pointer/string/memory formatting, and hexdump markers.
