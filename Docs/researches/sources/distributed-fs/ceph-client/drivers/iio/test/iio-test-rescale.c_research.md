# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-rescale.c

Purpose: KUnit suite for IIO analog-front-end rescale conversion helpers, covering scale and offset calculations across IIO value encodings and difficult numeric cases.

Important APIs/types/functions: `struct rescale_tc_data` defines parameterized cases. `scale_cases` and `offset_cases` cover typical, small fractional, negative, decimal-overflow, and 32-bit-overflow scenarios. Helpers include `case_to_desc()`, `iio_str_to_nano()`, `iio_test_relative_error_ppm()`, `iio_rescale_test_scale()`, and `iio_rescale_test_offset()`.

Control flow: KUnit array parameters feed scale and offset tests. The scale test calls `rescale_process_scale()`, formats the result with `iio_format_value()`, parses expected and actual strings into nano units, and requires zero ppm relative error. The offset test calls `rescale_process_offset()` and compares trimmed formatted output to expected integer strings.

State and persistence: no persistent state; each test allocates buffers and local `struct rescale`.

Dependencies/integration: depends on `linux/iio/afe/rescale.h`, IIO formatting/parsing helpers, gcd/overflow utilities, KUnit, and namespace `IIO_RESCALE`. Built by `CONFIG_IIO_RESCALE_KUNIT_TEST`.

Risks: string parsing with nano precision can lose precision for very long decimal expected values, but the cases are selected to match helper outputs. The suite is large and exact, so intentional arithmetic changes need synchronized expected updates.

Test signals: KUnit suite `iio-rescale` should pass all parameterized scale and offset cases and is the primary regression signal for rescale arithmetic.
