# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-format.c

Purpose: KUnit suite for `iio_format_value()` string formatting across IIO value encodings.

Important APIs/types/functions: `IIO_TEST_FORMAT_EXPECT_EQ()` checks return length and output string. Test cases cover `IIO_VAL_INT`, `IIO_VAL_INT_PLUS_MICRO`, `IIO_VAL_INT_PLUS_MICRO_DB`, `IIO_VAL_INT_PLUS_NANO`, `IIO_VAL_FRACTIONAL`, `IIO_VAL_FRACTIONAL_LOG2`, `IIO_VAL_INT_MULTIPLE`, and `IIO_VAL_INT_64`.

Control flow: each test allocates a PAGE_SIZE buffer with KUnit allocation, sets sample values, calls `iio_format_value()`, and asserts exact strings. `kunit_test_suite()` registers the `iio-format` suite.

State and persistence: no persistent state; allocations are KUnit-managed per test.

Dependencies/integration: depends on KUnit and IIO core formatting. Built by `CONFIG_IIO_FORMAT_KUNIT_TEST`.

Risks: exact string tests are intentionally brittle for ABI regressions; any intended formatting change must update many expected strings. Large integer edge coverage protects sign handling, but buffer-size behavior is not directly stress-tested.

Test signals: KUnit suite `iio-format` should pass all six cases and catch formatting regressions for sysfs ABI text.
