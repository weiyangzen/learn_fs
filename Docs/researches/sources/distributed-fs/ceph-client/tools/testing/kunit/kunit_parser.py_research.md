# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_parser.py

## Purpose

This module extracts KTAP/TAP from kernel output, parses KUnit results into a nested `Test` tree, tracks aggregate pass/fail/skip/crash/error counts, and prints human-readable summaries. It is the central result parser for `kunit.py`.

## Important APIs, Types, And Data

Core data types are `Test`, `TestStatus`, `TestCounts`, and `LineStream`. Regex constants recognize KTAP/TAP starts, kernel-output stops, executor errors, subtest headers, test plans, test result lines, skip directives, and diagnostic lines. Important functions include `extract_tap_lines()`, `check_version()`, `parse_ktap_header()`, `parse_test_header()`, `parse_test_plan()`, `parse_test_result()`, `parse_diagnostic()`, print/format helpers, `_summarize_failed_tests()`, `bubble_up_test_results()`, `parse_test()`, and `parse_run_tests()`.

## Control Flow

`parse_run_tests()` prints a divider, calls `extract_tap_lines()` to isolate TAP from mixed kernel logs, and either reports missing KTAP or calls recursive `parse_test()`. `parse_test()` handles three forms: a top-level KTAP/TAP header and plan, a nested subtest with optional KTAP and/or `# Subtest`, or a leaf `ok`/`not ok` result. It consumes diagnostics between structural lines, recurses through expected subtests, checks matching result numbers/names, bubbles child counts up, prints incremental results, and returns a populated root test.

## State And Persistence Behavior

The parser itself has no file persistence. It stores parse state in `LineStream`, `Test.log`, `Test.subtests`, `Test.counts`, and `Test.status`. Printing happens incrementally through a `Printer`, and `kunit.py` uses the returned tree for summary status and JSON output.

## Dependencies And Integration Points

It depends on Python regex, textwrap, enums, dataclasses, typing, and `kunit_printer.Printer`. It integrates with `kunit_kernel.run_kernel()` output, `kunit.py parse_tests()`, `kunit_json`, `--summary`, `--failed`, `--raw_output=kunit`, and KUnit executor output including KTAP version 1 and TAP versions 13/14.

## Risks And Edge Cases

Parsing is intentionally tolerant but complex. It must handle prefixed kernel lines, missing headers, zero-test plans, nested suites, missing subtest result lines, mismatched test numbers, skipped tests, crashes, executor errors before KTAP, and kernel termination markers. `check_version()` has a typo in an error string (`higer`) but behavior is clear. If a top-level stream contains non-KTAP output before a version line, it is ignored except executor errors; users need `--raw_output=all` for full debugging. Failure summarization suppresses very large failure lists.

## Test Signals

`kunit_tool_test.py` includes extensive parser fixtures. Key regression signals are successful parsing of nested KTAP, TAP 13/14, skip directives, missing KTAP, missing subtest results, zero tests, crash logs, line-number preservation, failed-only printing, and summary/count status precedence where crashes outrank failures and failures outrank skips.
