# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance_test.c

This file provides KUnit coverage for mean/variance and 128-bit helper arithmetic.

Test coverage:
- `mean_and_variance_basic_test()`:
  - verifies mean/variance over small repeated samples.
- `mean_and_variance_weighted_test()`:
  - checks weighted mean/variance for positive and negative sequences.
- `mean_and_variance_weighted_advanced_test()`:
  - checks longer positive and negative weighted sequences with weight 8.
- `do_mean_and_variance_test()`:
  - common harness comparing unweighted and weighted expected mean/stddev arrays.
- `mean_and_variance_test_1()`:
  - steady state, outlier, return to steady state.
- `mean_and_variance_test_2()`:
  - transition from one steady state to another.
- `mean_and_variance_fast_divpow2()`:
  - verifies signed power-of-two division behavior for positive and negative values.
- `mean_and_variance_u128_basic_test()`:
  - verifies 128-bit add, subtract, shift, square, and division.

KUnit registration:
- Test suite name: `"mean and variance tests"`.
- Module metadata describes bcachefs mean/variance unit tests.

Research notes:
- Expected values are hard-coded, making this a regression suite for integer rounding behavior.
- The tests cover negative weighted samples, which is important because signed right shift behavior is normalized through `fast_divpow2()`.
