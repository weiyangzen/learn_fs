# File Research: sources/cow-pools/bcachefs-tools/fs/util/mean_and_variance_test.c

Purpose: KUnit tests for the streaming median/MAD estimator.

Key test coverage:
- Basic exact mean/count behavior and MAD decay after many constant samples.
- Weighted constant-stream convergence toward the constant value.
- Weighted step response moving monotonically toward a new value.
- Bounded response to a single large outlier.

Integration:
- Uses `kunit_test_suite()` with four test cases.
- Includes only `mean_and_variance.h`.

Risks and gaps:
- Tests assert convergence-shaped properties, not exact estimator values.
- No explicit overflow or extreme signed-value tests are present.
