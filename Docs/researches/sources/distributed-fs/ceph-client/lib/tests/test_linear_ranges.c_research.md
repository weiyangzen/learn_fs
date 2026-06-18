<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_linear_ranges.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_linear_ranges.c

## Purpose
KUnit tests for `linear_range` helpers, using two simple selector-to-value ranges to verify value lookup, selector lookup, and total value counts.

## APIs, Types, and Functions
Defines two `struct linear_range` entries with `LINEAR_RANGE()`. Test cases call `linear_range_get_value_array()`, `linear_range_get_selector_high()`, `linear_range_values_in_range_array()`, and `linear_range_get_selector_low_array()`.

## Control Flow, State, and Persistence
Static arrays describe expected selectors and values for two ranges. Each test iterates expected entries and asserts exact return codes, selector/value mapping, and found flags. Boundary checks verify selectors outside the range and values below/above the range. State is static immutable test data only.

## Dependencies and Integration
Depends on KUnit and `linux/linear_range.h`. It registers as `linear-ranges-test` and targets helpers used by regulator, power, and driver tables.

## Risks and Test Signals
Risks include limited range complexity, no overlap or descending-range cases, and no large arithmetic overflow stress. Test signals cover both single-range and array-of-ranges lookup, below-minimum high selector behavior, above-maximum low selector behavior, and total count computation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_linear_ranges.c -->
