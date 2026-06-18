# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcResults.py

## Purpose
Provides result data structures and formatting helpers for tc-testing. It models per-test results, aggregates suites, and emits TAP or xUnit-like XML.

## Important APIs, Types, And Functions
Defines `ResultState` enum values `noresult`, `skip`, `success`, and `fail`; class `TestResult` with result, error, failure, and executed-step fields; and `TestSuiteReport` with add/update/count/find methods plus `format_tap()` and `format_xunit()`.

## Control Flow
Test code creates `TestResult`, sets result and messages, adds executed steps, and inserts it into `TestSuiteReport`. Formatters iterate results to produce a TAP plan with `ok`/`not ok` lines or XML with testcase, failure, error, and skipped elements.

## State And Persistence
Suite state is an in-memory list `_testsuite`. No files are written directly by this module.

## Dependencies And Integration Points
Used by `valgrindPlugin.py` to record memory-check subresults and likely by the main runner. XML formatting depends on `xml.sax.saxutils.escape`.

## Risks
`TestResult.add_steps()` has a bug in the string path: it appends undefined variable `step` instead of `newstep`. TAP skip formatting treats `noresult` as skipped. XML attribute escaping is applied to id/name, but the XML format lacks a failures count and may not match strict xUnit consumers.

## Test Signals
Correct suite counts, TAP plans matching result count, fail entries including executed commands and fail messages, skip entries carrying error text, and no TypeError except on invalid result/steps types.
