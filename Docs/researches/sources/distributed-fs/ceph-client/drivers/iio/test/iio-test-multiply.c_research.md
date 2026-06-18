# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-multiply.c

Purpose: KUnit suite for `iio_multiply_value()`, validating conversion of IIO encoded values multiplied by signed 64-bit multipliers into integer results.

Important APIs/types/functions: Helper test functions cover integer, fixed-point micro/nano, fractional, and fractional-log2 formats for positive, negative, and zero values. Uses `div_s64()` for expected fixed/fractional results.

Control flow: public KUnit cases call internal helpers twice, once with positive multiplier and once with negative multiplier. The suite registers as `iio-multiply`.

State and persistence: no persistent state.

Dependencies/integration: depends on KUnit, `linux/iio/consumer.h`, math64 helpers, and namespace `IIO_UNIT_TEST`. Built by `CONFIG_IIO_MULTIPLY_KUNIT_TEST`.

Risks: tests assert integer truncation behavior, so changes in rounding semantics will fail. Very large overflow boundaries are not deeply covered despite use of s64 multipliers.

Test signals: all four KUnit cases should pass for positive and negative multipliers across supported IIO value encodings.
