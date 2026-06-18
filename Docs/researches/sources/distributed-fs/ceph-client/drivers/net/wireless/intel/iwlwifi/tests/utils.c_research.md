# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/utils.c

## Purpose
This KUnit suite tests `iwl_average_neg_dbm()`, a utility that averages encoded negative dBm samples where `0xff` marks unused entries.

## Important APIs, Types, and Functions
- `struct average_neg_db_case` stores a description, a 22-byte sample array, and the expected signed dBm result.
- Cases cover all-minimum, all-maximum, partially filled arrays, and rounding boundaries between -79 and -80 dBm.
- `test_average_neg_db()` checks the function on the original order and reversed order.
- Suite name is `iwl-average-db`.

## Control Flow
KUnit parameterization feeds each sample set to the test. The function under test is expected to ignore `0xff` padding and return a rounded negative signed value. Reversing input checks that order does not affect aggregation.

## State and Persistence Behavior
The test owns only stack/local arrays. No persistent driver state is touched.

## Dependencies and Integration Points
It includes `../iwl-utils.h`, imports namespace `IWLWIFI`, and depends on KUnit parameterized test support.

## Risks and Edge Cases
Coverage is specific to the selected sentinel, extremes, partial fills, and rounding thresholds. It does not explicitly test empty/all-`0xff` input unless that behavior is represented elsewhere.

## Test Signals
Passing results indicate the average helper handles sentinel filtering, sign conversion, rounding, and input-order independence for representative arrays.
