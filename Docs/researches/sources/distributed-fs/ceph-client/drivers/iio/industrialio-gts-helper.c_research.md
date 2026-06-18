# sources/distributed-fs/ceph-client/drivers/iio/industrialio-gts-helper.c

## Purpose
`industrialio-gts-helper.c` provides gain-time-scale conversion helpers, mainly for IIO light sensors whose scale is a function of hardware gain and integration time. It initializes a descriptor from gain/time selector tables, precomputes available scale/time lists for `read_avail`, converts between total gain and scale, finds selectors for requested scales, and computes gain compensation when integration time changes.

## Important APIs, types, and functions
- `struct iio_gts` is populated with max linear scale, hardware gain table, integration-time table, generated per-time scale tables, all-scale table, and available-time table.
- `devm_iio_init_iio_gts()` initializes the descriptor, validates inputs, builds availability tables, and registers devm cleanup.
- `iio_gts_total_gain_to_scale()`, `iio_gts_get_total_gain()`, and `iio_gts_get_scale()` convert between gain/time combinations and IIO scale values.
- `iio_gts_all_avail_scales()`, `iio_gts_avail_scales_for_time()`, and `iio_gts_avail_times()` return `read_avail`-compatible arrays and types.
- `iio_gts_find_sel_by_gain()`, `iio_gts_find_gain_by_sel()`, `iio_gts_get_min_gain()`, and `iio_find_closest_gain_low()` query gain tables.
- `iio_gts_find_gain_sel_for_scale_using_time()` and `iio_gts_find_gain_time_sel_for_scale()` resolve requested scale values to selectors.
- `iio_gts_find_new_gain_sel_by_old_gain_time()`, `iio_gts_find_new_gain_by_old_gain_time()`, and `iio_gts_find_new_gain_by_gain_time_min()` compute gain changes to preserve or approximate scale across integration-time changes.

## Control flow
Initialization linearizes the maximum scale into a nanounit-based integer, records gain and integration-time tables, checks that gains/selectors/time multipliers are nonnegative and nonzero where required, and validates that gain multiplied by integration-time multiplier does not overflow `int`. It then allocates per-time scale tables, computes total gains for every time/gain combination, sorts gain-derived scales, creates one combined unique sorted all-scale table, and builds a sorted integration-time table formatted as `IIO_VAL_INT_PLUS_MICRO`.

Lookup helpers linearize requested scale values, derive total gain as `max_scale / scale`, divide by known time multiplier or gain, require exact divisibility for exact-match helpers, and validate the resulting gain against the hardware table. Compensation helpers compute the old scale from old gain/time and then solve for a new gain under the new time. The `_min` variant falls back to closest lower supported gain and then minimum gain to avoid saturation.

## State and persistence behavior
The helper stores only generated lookup tables in memory. `devm_iio_init_iio_gts()` binds those allocations to the caller device lifetime through `devm_add_action_or_reset()`. It does not touch hardware; drivers use returned selectors to update their own device registers.

## Dependencies and integration points
The file depends on Linux integer overflow helpers, sorting, slab allocation, unit constants, IIO value types, and the public `iio-gts-helper.h` API. It is exported in namespace `IIO_GTS_HELPER`, so users must import that namespace.

## Risks
- Exact-match helpers require total gain to divide cleanly by known gain/time. Users expecting nearest-match behavior must call the explicit closest/lower helper path.
- Scale linearization divides nanoseconds by the selected scaler; unsupported scaler values return errors and fractional precision can be lost.
- `iio_gts_get_min_gain()` uses a local variable named `min`; it relies on macro expansion context and should be watched when refactoring.
- Availability table generation assumes sorted/preferred integration-time semantics for search order but also sorts displayed values; driver documentation should make policy clear.
- Large gain/time tables can fail allocation or overflow computed table sizes.

## Test signals
- Unit-style tests should cover initialization rejection for empty tables, negative selectors, zero gain/time multiplier, and multiplication overflow.
- Conversion tests should cover gain-to-scale, scale-to-gain selector, exact and non-exact scale requests, duplicate integration times, duplicate scales across time/gain pairs, and all exported availability helpers.
- Compensation tests should verify exact preservation, in-range lower fallback, out-of-range minimum fallback, and selector-versus-time variants.
- Build tests should verify namespace imports for module users.
