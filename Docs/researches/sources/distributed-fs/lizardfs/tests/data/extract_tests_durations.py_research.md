# sources/distributed-fs/lizardfs/tests/data/extract_tests_durations.py

## Purpose
`extract_tests_durations.py` parses Jenkins/GTest logs and emits averaged per-test duration hints for Sanity, Short, and Long LizardFS suites. These hints can feed scheduling or timeout estimates.

## Important APIs, Types, and Functions
`TestSuite` normalizes supported suite names. `create_test_suite_enum()` accepts aliases. `process_one_build()` parses a direct Sanity log or discovers concurrent subjob logs for Short/Long. `parse_logfile_for_tests()` extracts `Suite.test (milliseconds)` lines. `get_subjobs_from_mainjob_log()` and `convert_to_correct_subjob_path()` locate concurrent job logs. `print_result()` averages durations, converts to seconds, rounds down to a 10-second bucket, and floors zero to 5 seconds.

## Control Flow
`main()` validates arguments, normalizes the suite, processes every provided log path, aggregates durations by test name, and prints `name=duration` lines sorted by name. Missing subjob logs cause the whole build to be skipped rather than partially counted.

## State and Persistence Behavior
The script is read-only with respect to logs and writes results to stdout plus errors to stderr. No cache or output file is persisted.

## Dependencies and Integration Points
It depends on Python 3 standard library modules `os`, `re`, `sys`, `enum`, and `typing`. It is coupled to Jenkins log text and GTest output formatting.

## Risks and Edge Cases
Regexes assume word-character test names and a specific concurrent-job phrase. Rounding down can understate slow tests, and skipping whole builds on one missing subjob trades completeness for consistency. Unsupported suite aliases raise a generic exception.

## Test Signals
Fixture logs should cover direct Sanity parsing, Short/Long subjob discovery, missing subjob handling, multiple-build averaging, zero-duration flooring, unsupported suite names, and malformed/empty logs.
