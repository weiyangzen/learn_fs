# sources/distributed-fs/ceph-client/tools/perf/tests/unit_number__scnprintf.c

## Purpose
This is a focused unit test for `unit_number__scnprintf()`, verifying that byte counts are formatted into perf's compact binary units with expected suffixes.

## Important APIs, Types, And Functions
The only test function is `test__unit_number__scnprint()`, registered with `DEFINE_SUITE("unit_number__scnprintf", unit_number__scnprint)`. It uses `u64`, `PRIu64`, `unit_number__scnprintf()`, `strcmp()`, `pr_debug()`, and perf's `TEST_OK`/`TEST_FAIL` convention.

## Control Flow
The function walks a sentinel-terminated table of input values and expected strings: `1 -> 1B`, `10*1024 -> 10K`, `20*1024*1024 -> 20M`, `30*1024*1024*1024ULL -> 30G`, and `0 -> 0B`. For each case it formats into a fixed 100-byte buffer, emits debug output, and fails immediately on any string mismatch.

## State, Dependencies, And Integration
There is no persistent state. The test depends on `units.h` for the formatter and `tests.h` for suite registration. It runs as a normal perf C test and does not depend on host hardware.

## Risks And Test Signals
Coverage is intentionally narrow: it checks exact binary-unit thresholds for only whole-unit values and does not test truncation, fractional output, larger suffixes, or small buffers. A passing test strongly signals stable canonical formatting for common byte-unit cases.
