# Research: subset-b-009052

Grouped research report for the testtools files listed in work item `subset-b-009052`. Each section is source-tree-aligned and bounded for deterministic reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testcase.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testcase.py

## Purpose

This module is the main behavioral contract suite for `testtools.testcase` and the testtools extensions exported through `testtools.__init__`. It validates placeholder test objects, error holders, `TestCase` identity/equality, assertion helpers, expectation handling, cleanup execution, expected failures, details propagation, unique-name factories, cloning, lifecycle correctness, skipping decorators, exception hooks, monkey patch cleanup, `Nullary`, attribute-tagged ids, and `DecorateTestCaseResult`.

The file is test code, but it acts as executable API documentation for the compatibility boundary between testtools and `unittest` result implementations.

## Important APIs, Types, And Functions

- `TestPlaceHolder` checks `PlaceHolder` id/description/repr/count/run/debug/call behavior, detail/timestamp emission, tag scoping, and hashability inherited from `unittest.TestCase`.
- `TestErrorHolder` checks the deprecated-but-supported `ErrorHolder`, including id/description/count/run/debug/call behavior and `addError` detail emission.
- `TestEquality` asserts that `TestCase` equality is identity based and handles objects lacking `__dict__`.
- `TestAssertions` covers assertion helpers including `assertRaises`, `assertRaisesRegex`, `assertIn`, `assertNotIn`, `assertIsInstance`, identity assertions, `assertThat`, `expectThat`, `force_failure`, pretty equality formatting, non-ASCII formatting, and preservation of preexisting traceback details.
- `TestAddCleanup` validates cleanup ordering and aggregation: cleanups run after `tearDown`, run even after `setUp` failure, execute in reverse registration order, continue after failures, aggregate multiple traceback details, and re-raise `KeyboardInterrupt`.
- `TestExpectedFailure` covers internal `_UnexpectedSuccess`, `expectFailure`, `unittest.expectedFailure`, and expected-failure details such as `reason` and `traceback`.
- `TestUniqueFactories` covers `getUniqueInteger`, `getUniqueString`, `unique_text_generator`, `_mods`, and `_unique_text`.
- `TestCloneTestWithNewId` verifies cloned tests have rewritten ids but do not share details dictionaries.
- `TestDetailsProvided` checks details for errors, failures, skips, success, unexpected success, mismatch details, duplicate detail names, and `addDetailUniqueName`.
- `TestSetupTearDown` detects test cases that call `setUp` or `tearDown` too many or too few times.
- `TestRunTwiceDeterminstic` and `TestRunTwiceNondeterministic` use sample-case scenarios to verify repeated runs either produce identical deterministic events or known nondeterministic event shapes.
- `TestSkipping` covers `skipTest`, custom `skipException`, old Python 2.6-style result fallback, method/class decorators from both testtools and unittest, and ensuring skipped decorators do not run `setUp`.
- `TestOnException` verifies `onException` and registered exception handlers.
- `TestPatchSupport` confirms `TestCase.patch` applies temporary attributes and restores or deletes them during cleanup.
- `TestTestCaseSuper` ensures `setUp`/`tearDown` cooperate with multiple inheritance via `super()`.
- `TestNullary` covers the small callable wrapper that stores arguments and exposes the wrapped function repr.
- `Attributes` plus `TestAttributes` cover `attr` and `WithAttributes`, proving tagged ids are sorted and stable.
- `TestDecorateTestCaseResult` verifies a wrapper test case that transforms the result before delegating and forwards attributes to the decorated case.

## Control Flow

Most tests synthesize inner `TestCase` subclasses, run them against `ExtendedTestResult`, `Python26TestResult`, `Python27TestResult`, `LoggingResult`, or `unittest.TestResult`, then assert event order and detail keys. This pattern exercises the full `TestCase.run` path: `startTest`, `setUp`, test method, `tearDown`, cleanups, outcome recording, `stopTest`, and tag restoration.

Cleanup tests intentionally raise exceptions from test bodies and cleanups to confirm that testtools converts multiple errors into one result event with multiple detail attachments. Skip tests branch through modern result objects and older result objects without skip support, proving fallback compatibility.

## State And Persistence Behavior

No repository state is persisted by this file. Runtime state is held in in-memory lists (`log`, `events`, `calls`), result double `_events`, generated detail dictionaries, class attributes on synthetic cases, and per-case counters used by unique factories. Patch tests mutate attributes on `self` but require restoration through cleanup. External state is limited to temporary details attached to test cases and result objects.

## Dependencies

The module depends heavily on the local testtools package: `TestCase`, `PlaceHolder`, `ErrorHolder`, `DecorateTestCaseResult`, `MultipleExceptions`, skip decorators, `clone_test_with_new_id`, `content`, `testcase`, `TracebackContent`, `text_content`, many matchers, `Nullary`, `WithAttributes`, `attr`, `TestSkipped`, result doubles, helper matchers, and sample-case scenario factories. Standard library dependencies include `doctest`, `pprint`, `sys`, `_thread`, and `unittest`.

## Integration Points

This is a central integration test for `testtools.testcase`, `testtools.runtest`, result adapters, matcher details, content objects, and skip compatibility with `unittest`. Failures here usually indicate a public behavior change affecting external users writing testtools-based test cases or consuming testtools result objects.

## Risks And Edge Cases

Key risks covered include lost cleanup errors, cleanup ordering regressions, incorrect skip fallback on older result objects, duplicate detail-name collisions, non-ASCII failure formatting, lifecycle misuse detection, repeated-run nondeterminism, tag leakage, patch restoration leaks, and wrappers failing to forward attributes or result hooks. The tests also guard against swallowing `KeyboardInterrupt` and `SystemExit` incorrectly.

## Test Signals

Strong test signals are exact result event sequences, expected detail-key sets, doctest-style traceback fragments, unique string outputs, skip reason storage, and restored object attributes after run completion. The suite is sensitive to line/path formatting in some traceback assertions but generally uses ellipses to tolerate implementation-version differences.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testcase.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testresult.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testresult.py

## Purpose

This module is the main contract and regression suite for testtools result classes, result decorators, stream result conversion, routing, summaries, non-ASCII traceback rendering, per-test callback results, tagging, and timestamping. It defines reusable contract mixins for result behavior and applies them to many concrete result implementations.

## Important APIs, Types, And Functions

- Factory helpers create representative passing, failing, erroring, mismatching, and unexpectedly successful tests plus `make_exception_info`.
- `TestControlContract`, `Python26Contract`, `Python27Contract`, `TagsContract`, `DetailsContract`, `FallbackContract`, and `StartTestRunContract` describe expected behavior for result control, success/failure accounting, skip/xfail/uxsuccess, tag scope, details API, fallback policy, and run reset behavior.
- Concrete contract classes apply those contracts to `TestResult`, `MultiTestResult`, `TextTestResult`, `ThreadsafeForwardingResult`, `ExtendedTestResult`, Python 2.6/2.7 doubles, Twisted doubles, `ExtendedToOriginalDecorator`, `ExtendedToStreamDecorator`, `StreamToExtendedDecorator`, and `TestResultDecorator`.
- `TestStreamResultContract` exercises `StreamResult.status` across file and non-file parameter power sets; derived classes apply it to stream decorators and routers.
- `TestDoubleStreamResultEvents`, `TestCopyStreamResultCopies`, `TestStreamTagger`, `TestStreamToDict`, `TestExtendedToStreamDecorator`, `TestResourcedToStreamDecorator`, `TestStreamFailFast`, and `TestStreamSummary` validate stream-event semantics.
- `TestTestResult`, `TestMultiTestResult`, `TestTextTestResult`, and `TestThreadSafeForwardingResult` cover classic result behavior, fan-out, text output, and atomic forwarding under concurrency.
- `TestMergeTags`, `TestStreamResultRouter`, and `TestStreamToQueue` cover tag-delta merging, route-code/test-id routing, queue event serialization, and route prefix composition.
- `TestExtendedToOriginalResultDecoratorBase` plus outcome-specific subclasses validate conversion from extended details APIs to older result APIs.
- `TestNonAsciiResults` and `TestNonAsciiResultsWithUnittest` create temporary modules in varied encodings to verify traceback and exception text rendering.
- `TestDetailsToStr`, `TestByTestResultTests`, `TestTagger`, and `TestTimestampingStreamResult` cover detail stringification, one-callback-per-test summaries, per-test tag injection, and automatic timestamp insertion.

## Control Flow

The file begins with reusable behavior contracts and then instantiates them for each result implementation. Many tests call `startTestRun`, mutate tags or time, run synthetic tests, emit outcome methods, and assert the resulting state or event logs. Stream tests call `status` directly with combinations of `test_id`, `test_status`, `test_tags`, `runnable`, `file_name`, `file_bytes`, `eof`, `mime_type`, `route_code`, and `timestamp`.

Adapter tests branch on target capability: Python 2.6-style results receive fewer calls and map unsupported outcomes to success or failure; Python 2.7-style results receive skip/expected-failure support; extended results preserve detail dictionaries. The non-ASCII tests create temporary modules, import them, run generated cases through `TextTestResult` or `unittest.TextTestRunner`, and inspect the output stream.

## State And Persistence Behavior

Runtime state is held in result object fields such as `shouldStop`, `failfast`, `testsRun`, `current_tags`, skip reason maps, stream event lists, queues, timestamp fields, and summary lists. Temporary files and importable modules are created under `tempfile.mkdtemp` in `TestNonAsciiResults` and removed through cleanups; `sys.path` and `sys.modules` are also restored through cleanups. `TestTestResult.test_now_datetime_now` temporarily patches `testresult.real.datetime` and restores it.

## Dependencies

The module uses many testtools exports: result classes/decorators, stream classes, `PlaceHolder`, `TestCase`, `TestControl`, `TestByTestResult`, content helpers, compatibility helpers, matchers, result doubles, and `_details_to_str`, `_merge_tags`, and `utc` from `testtools.testresult.real`. Standard dependencies include `codecs`, `datetime`, `doctest`, `io`, `itertools`, `os`, `platform`, `queue`, `re`, `shutil`, `sys`, `tempfile`, `threading`, and `unittest.TestSuite`. Optional `testresources` is imported with `try_import` and gates resource-stream tests.

## Integration Points

This file validates the contract among classic unittest-style results, extended testtools results, stream results, subunit-like event flows, routing, and queue transport. It is a key guard for users that bridge testtools into old unittest consumers, Twisted/subunit style result consumers, or concurrent runners requiring atomic per-test event forwarding.

## Risks And Edge Cases

Major risks include incompatible fallback mappings, tag leakage between tests, failure to reset result state at `startTestRun`, incorrect failfast behavior, empty attachments being dropped or misreported, malformed MIME handling, in-progress stream tests not failing at run end, route-code prefix consumption mistakes, queue route composition errors, Unicode/encoding regressions in tracebacks, temporary import pollution, and broken timestamp injection.

## Test Signals

Signals include exact `_events` tuples, `wasSuccessful()` state, `shouldStop`, skip reason maps, stream summaries, queue dictionaries, rendered text output fragments, detail stringification output, per-test callback dictionaries, and timestamp type/value assertions. The encoding tests are especially valuable for platform compatibility but are intentionally tolerant around implementation-specific syntax-error formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testresult.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testsuite.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testsuite.py

## Purpose

This module tests `ConcurrentTestSuite`, `ConcurrentStreamTestSuite`, `FixtureSuite`, and `sorted_tests`. It verifies parallel-suite glue, stream event routing, setup-class skip compatibility, fixture wrapping, and deterministic sorting with duplicate-id detection.

## Important APIs, Types, And Functions

- `Sample` is a simple `TestCase` with two methods and identity hashing for suite tests.
- `TestConcurrentTestSuiteRun` checks broken runners, trivial execution, and the `wrap_result` hook for per-thread results.
- `TestConcurrentStreamTestSuiteRun` checks stream-based concurrent execution, broken runner traceback streaming, and class-level `setUpClass` skip/upcall behavior through normal `unittest.TestSuite`.
- `TestFixtureSuite` uses optional `fixtures.FunctionFixture` to assert setup/test/teardown ordering and duplicate sorting failure.
- `TestSortedTests` validates custom suite sorting, custom suites without `sort_tests`, simple sorting, duplicate detection, and multi-duplicate error messages.
- `test_suite()` exposes standard `TestLoader` discovery.

## Control Flow

Concurrent suite tests wrap a standard `unittest.TestSuite`, split it with `iterate_tests`, and run it against either `LoggingResult`, `TestByTestResult`, or `LoggingStream`. Broken runner tests intentionally define objects with invalid `run` signatures so suite code must synthesize a failed "broken-runner" event. Fixture tests run two sample test methods inside a fixture and assert fixture setup before tests and teardown after them.

## State And Persistence Behavior

The file has no persistent state. Test state is stored in local `log`, `wrap_log`, `result_log`, and stream `_events` lists. Optional fixture setup mutates the in-memory log only. Sorting mutates suite internals in custom subclasses when `sort_tests` is called.

## Dependencies

It depends on `doctest`, `pprint.pformat`, `unittest`, testtools suite/result APIs, matchers, `try_import`, and optional `fixtures.FunctionFixture`. It also uses `LoggingResult` from local test helpers and `StreamResult` doubles.

## Integration Points

The suite connects testtools suite implementations with result doubles, stream results, fixture integration, and standard `unittest` class-level setup semantics. It is an important guard for concurrent runners and users relying on deterministic test ordering.

## Risks And Edge Cases

Risks covered include invalid test runner objects, loss of traceback attachments in stream mode, route-code omission in concurrent stream output, wrapper hooks receiving the wrong result/thread number, duplicate ids silently sorting, and fixture teardown not running after all tests.

## Test Signals

Primary signals are exact event tuples, route codes, traceback doctest fragments, setup-class skip event names, fixture log order, sorted `iterate_tests` output, and duplicate-id error text.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testsuite.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_with_with.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_with_with.py

## Purpose

This module tests the `ExpectedException` context manager exported by testtools. It validates exception-type matching, optional message regex matching, matcher-based validation, custom annotation text, and correct pass-through of unexpected exceptions.

## Important APIs, Types, And Functions

- `TestExpectedException` is the single test class.
- `test_pass_on_raise` and `test_pass_on_raise_matcher` prove the context manager suppresses matching exceptions.
- Mismatch tests prove regex mismatches and matcher mismatches become `AssertionError` with useful messages.
- `test_raise_on_error_mismatch` proves unexpected exception types are re-raised rather than converted.
- `test_raise_if_no_exception` proves missing exceptions fail with "`TypeError not raised.`".
- Annotation tests verify `msg` is appended to failure messages.
- `test_suite()` exposes standard loader integration.

## Control Flow

Each test enters `with ExpectedException(...)`; the context manager observes the exception exiting the block. If the type and optional message/matcher match, execution proceeds. If no exception or the wrong message occurs, the test catches `AssertionError` and compares its text. If a different exception type occurs, the original exception is expected outside the context.

## State And Persistence Behavior

No persistent state exists. Temporary local exception objects and matcher instances are created only for the assertion under test.

## Dependencies

The module uses `sys.exc_info`, `ExpectedException`, `TestCase`, and matchers `AfterPreprocessing`, `Equals`, and `EndsWith`.

## Integration Points

This tests the context-manager API used by external test authors who prefer `with` blocks to `assertRaises` calls. It also validates matcher integration for exception values.

## Risks And Edge Cases

Risks include swallowing unexpected exceptions, producing misleading messages for regex or matcher mismatches, failing to report missing exceptions, and losing caller-supplied annotation text.

## Test Signals

Signals are successful context exit for matched exceptions and exact `AssertionError` text for mismatch/no-exception cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_with_with.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/__init__.py

## Purpose

This package initializer provides the aggregate test suite for `testtools.tests.twistedsupport`. It groups the Twisted support test modules into a single `unittest.TestSuite`.

## Important APIs, Types, And Functions

- Imports `TestSuite` from `unittest`.
- `test_suite()` imports `test_deferred`, `test_matchers`, `test_runtest`, and `test_spinner`, calls each module's `test_suite()`, and wraps the resulting suites in a parent `TestSuite`.

## Control Flow

Imports of submodules are delayed until `test_suite()` is called. The function builds a module list, maps each module to its suite, and returns a `TestSuite` containing those child suites.

## State And Persistence Behavior

No persistent state exists. The only state is the local module list and the suite object returned to the caller.

## Dependencies

Depends on the local Twisted support test modules and standard `unittest.TestSuite`.

## Integration Points

This function is used by test discovery or explicit suite loading to run the Twisted-related test subset together. It preserves the package-level contract used by older test loaders that call `test_suite()`.

## Risks And Edge Cases

Because imports occur inside `test_suite()`, missing optional Twisted dependencies are handled by individual test modules rather than preventing package import. A risk is that adding a new Twisted support test module requires updating this list.

## Test Signals

The primary signal is that the returned suite contains the four expected child suites in the declared order.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/_helpers.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/_helpers.py

## Purpose

This helper module provides a Twisted-aware base test class for the Twisted support test suite. It centralizes optional dependency skipping.

## Important APIs, Types, And Functions

- `__all__ = ['NeedsTwistedTestCase']` declares the exported helper.
- `defer = try_import('twisted.internet.defer')` records whether Twisted is importable.
- `NeedsTwistedTestCase(TestCase)` overrides `setUp`; after calling `super().setUp()`, it calls `skipTest("Need Twisted to run")` when Twisted is unavailable.

## Control Flow

Each Twisted test class inherits from `NeedsTwistedTestCase`. During setup, tests are skipped before Twisted-specific behavior runs if `try_import` failed.

## State And Persistence Behavior

State is module-level and immutable after import for normal use: `defer` is either the Twisted defer module or `None`. There is no persistent state.

## Dependencies

Depends on `testtools.helpers.try_import` and `testtools.TestCase`. Optionally depends on `twisted.internet.defer`.

## Integration Points

This helper gates all Twisted support tests in the same way, allowing the broader testtools test suite to run in environments where Twisted is not installed.

## Risks And Edge Cases

If Twisted is partially installed such that `defer` imports but later Twisted modules fail, this helper will not skip those later failures. It only validates the base `twisted.internet.defer` import.

## Test Signals

The signal is skip behavior at setup time when `defer is None`; otherwise subclasses proceed normally.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/_helpers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_deferred.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_deferred.py

## Purpose

This module tests `testtools.twistedsupport._deferred.extract_result` and `DeferredNotFired`, the small helper that synchronously inspects an already-fired Twisted `Deferred`.

## Important APIs, Types, And Functions

- `DeferredNotFired` and `extract_result` are imported with `try_import`.
- `defer` and `Failure` are optional Twisted imports.
- `TestExtractResult` inherits from `NeedsTwistedTestCase`.
- `test_not_fired` expects `extract_result(defer.Deferred())` to raise `DeferredNotFired`.
- `test_success` expects a succeeded deferred to return its callback value.
- `test_failure` expects a failed deferred to re-raise the underlying exception.
- `test_suite()` exposes standard loader integration.

## Control Flow

The tests build three deferred states: pending, succeeded, and failed. `extract_result` is called directly and the result or raised exception is matched through testtools matchers.

## State And Persistence Behavior

No persistent state exists. Deferred objects are local to tests. The failure case captures a `Failure` from the current exception and wraps it with `defer.fail`.

## Dependencies

Depends on `try_import`, matchers `Equals`, `MatchesException`, and `Raises`, `NeedsTwistedTestCase`, and optional Twisted `defer` and `Failure`.

## Integration Points

`extract_result` is a support primitive for Twisted deferred matchers and synchronous/asynchronous runner code that needs to inspect deferred completion without spinning the reactor.

## Risks And Edge Cases

Risks include treating pending deferreds as successful, returning `Failure` objects instead of raising their exceptions, or losing the original failure type.

## Test Signals

Signals are exact exception type for pending/failing deferreds and object identity/equality for successful results.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_deferred.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_matchers.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_matchers.py

## Purpose

This module tests Twisted `Deferred` matchers exported by `testtools.twistedsupport`: `has_no_result`, `succeeded`, and `failed`.

## Important APIs, Types, And Functions

- `mismatches(description, details=None)` builds a matcher for mismatch objects by preprocessing `describe()` and `get_details()`.
- `make_failure(exc_value)` raises an exception and captures it as a Twisted `Failure`.
- `NoResultTests` verifies `has_no_result()` matches pending deferreds, mismatches succeeded/failed deferreds, and does not consume later callback or errback behavior.
- `SuccessResultTests` verifies `succeeded(matcher)` matches successful deferred values, forwards inner matcher mismatches, and produces clear mismatches for pending or failed deferreds with traceback details for failures.
- `FailureResultTests` verifies `failed(matcher)` matches failure objects, forwards inner matcher mismatches, and mismatches success or pending deferreds.
- `test_suite()` exposes standard loader integration.

## Control Flow

Each class has a small `match` helper that calls the relevant matcher's `match` method. Tests create pending, succeeded, or failed deferreds, then assert either `None` for match success or a structured mismatch with expected description and details.

## State And Persistence Behavior

No persistent state exists. Failed deferred tests add errbacks where needed to suppress unhandled Twisted errors after inspection. Deferred callback/errback lists are intentionally checked to ensure matchers do not consume or fire deferreds.

## Dependencies

Depends on `TracebackContent`, matchers `AfterPreprocessing`, `Equals`, `Is`, and `MatchesDict`, `NeedsTwistedTestCase`, Twisted `defer`, Twisted `Failure`, and the three Twisted support matchers.

## Integration Points

These matchers let test authors assert deferred state and result values using the same matcher protocol as the rest of testtools. They integrate with detail reporting by attaching traceback content for failed deferreds when a success was expected.

## Risks And Edge Cases

Risks include matchers mutating deferred state, not suppressing or exposing failures correctly, losing inner matcher details, or producing ambiguous mismatch text for pending versus failed states.

## Test Signals

Signals are `None` on match success, exact mismatch descriptions, exact mismatch detail dictionaries, and preservation of callback/errback results after a no-result assertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_matchers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_runtest.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_runtest.py

## Purpose

This module tests Twisted-aware single-test execution logic in `testtools.twistedsupport`, including synchronous and asynchronous deferred runners, error/log capture, reactor cleanup, debug mode, helper assertion `assert_fails_with`, and Twisted log observer fixtures.

## Important APIs, Types, And Functions

- Optional imports include `DebugTwisted`, `assert_fails_with`, `AsynchronousDeferredRunTest`, `flush_logged_errors`, `SynchronousDeferredRunTest`, Twisted `defer`, `failure`, `log`, `DelayedCall`, and `_get_global_publisher_and_observers`.
- Nested class `X` defines sample test cases for integration testing normal `RunTest`, `SynchronousDeferredRunTest`, and `AsynchronousDeferredRunTest` against errors in setup/test/teardown/cleanup, failures, expected matcher failures, and `SystemExit`.
- `make_integration_tests()` clones a base integration test for every runner/sample-case pair and adds those tests through `load_tests`.
- `TestSynchronousDeferredRunTest` verifies returned deferred success/failure and deferred-returning `setUp` sequencing in the synchronous runner.
- `TestAsynchronousDeferredRunTest` covers asynchronous `setUp`/test/`tearDown` sequencing, async cleanups, dirty reactor detection, exposing `self.reactor`, unhandled deferred errors, SIGINT stop behavior, timeouts, factory construction, deferred errors, one `addError` despite multiple errors, Twisted log handling, observer restoration, and debug flag restoration.
- `TestAssertFailsWith` verifies deferred failure assertions for success, wrong exception type, expected exception type, multiple expected types, and custom failure exception.
- `TestRunWithLogObservers`, `TestNoTwistedLogObservers`, `TestTwistedLogObservers`, `TestErrorObserver`, and `TestCaptureTwistedLogs` cover lower-level Twisted log observer fixtures and capture behavior.

## Control Flow

The asynchronous tests use the real Twisted reactor, schedule deferred callbacks with `callLater` or `callWhenRunning`, and run testtools runners with small timeouts. Runner flow is expected to be `startTest`, asynchronous `setUp`, test method, asynchronous `tearDown`, cleanups, reactor cleanup/log flushing, single outcome event, and `stopTest`. Error tests deliberately create combinations of direct exceptions, cleanup exceptions, dirty reactor ports, logged errors, and unhandled deferred failures to verify aggregation into details.

`load_tests` appends cloned integration tests generated by `make_integration_tests`, so discovery receives both the module's normal tests and the generated runner matrix.

## State And Persistence Behavior

No durable state is written. Runtime state includes reactor delayed calls, listening ports, Twisted global log observers, debug flags on `defer.Deferred` and `DelayedCall`, result `_events`, test details, and local call logs. Tests explicitly require observer restoration after normal completion and timeout, debug flag restoration, reactor cleanup, and no leaked local Twisted observers. Some POSIX-only tests send `SIGINT` to the current process.

## Dependencies

Depends on `os`, `signal`, testtools `skipIf`, `TestCase`, `TestResult`, `RunTest`, `ExtendedTestResult`, local helper matchers, `NeedsTwistedTestCase`, and many testtools matchers. Twisted dependencies are optional at import time but required at setup through `NeedsTwistedTestCase`.

## Integration Points

This is the main integration suite for testtools' Twisted support. It connects `TestCase.run_tests_with`, deferred-returning test phases, real reactor spinning, result detail emission, Twisted logging, global observer fixtures, and testtools cleanup semantics.

## Risks And Edge Cases

Key risks include advancing to the test method before asynchronous `setUp` fires, running `tearDown` before deferred test completion, async cleanups running out of order, dirty reactor handles leaking between tests, unhandled deferred failures being missed, adding multiple outcome events for one test, not stopping on SIGINT, timeouts leaving observers/debug flags changed, Twisted logs leaking to global observers when suppressed, and `assert_fails_with` reporting unclear errors.

## Test Signals

Signals include exact result event heads, exact call-log order, expected detail keys such as `traceback`, `traceback-1`, `twisted-log`, `logged-error`, and `unhandled-error-in-deferred`, `result.shouldStop`, restored observer lists, debug flag values, and matcher checks against logged Twisted messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_runtest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_spinner.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_spinner.py

## Purpose

This module tests the low-level Twisted reactor spinner in `testtools.twistedsupport._spinner`. The spinner runs callables inside the reactor, waits for deferred completion, prevents re-entry, traps unhandled deferred errors, handles timeouts/SIGINT, and detects leftover reactor state.

## Important APIs, Types, And Functions

- `_spinner` is imported with `try_import`; Twisted `defer` and `Failure` are optional imports.
- `TestNotReentrant` verifies the `not_reentrant` decorator raises `_spinner.ReentryError` on direct and mutual recursion.
- `TestTrapUnhandledErrors` verifies `trap_unhandled_errors` returns normal function results and captures unhandled deferred failures.
- `TestRunInReactor` exercises `Spinner.run`, `_clean`, `get_junk`, and `clear_junk`.
- `make_reactor`, `make_spinner`, and `make_timeout` centralize access to the real reactor and short timeouts.
- `test_suite()` exposes standard loader integration.

## Control Flow

`Spinner.run(timeout, function, *args, **kwargs)` is tested for direct return values, exceptions, keyword forwarding, deferred success, reentry errors, timeout errors, signal behavior, and cleanup behavior. Reactor cleanup tests create delayed calls, canceled calls, TCP listening ports, and reactor threadpool work, then assert whether `_clean` cancels/removes or records leftover junk. Signal tests schedule `os.kill(os.getpid(), SIGINT)` while the reactor is running and expect `_spinner.NoResultError`.

## State And Persistence Behavior

No durable state is written. Runtime state includes Twisted reactor delayed calls, listening ports/selectables, threadpool threads, signal handlers, a spinner's internal junk list, and local call logs. Tests restore signal handlers with cleanups and require spinner cleanup to leave thread enumeration unchanged after running reactor thread work.

## Dependencies

Depends on `os`, `signal`, `testtools.skipIf`, `try_import`, matchers `Equals`, `Is`, `MatchesException`, and `Raises`, `NeedsTwistedTestCase`, and optional Twisted reactor/defer/failure/protocol modules.

## Integration Points

The spinner is a support primitive for `AsynchronousDeferredRunTest`. Its behavior determines whether Twisted tests can run inside normal testtools runs without leaking reactor state or hanging indefinitely.

## Risks And Edge Cases

Risks include nested reactor spins, unhandled deferred errors being lost, signal handlers being overwritten, timed-out deferreds affecting later runs, stale junk being ignored, listening ports remaining registered, delayed calls not being canceled, and threadpool work leaking threads. POSIX-only SIGINT tests protect interrupt handling.

## Test Signals

Signals are raised `_spinner` exception types, exact return object identity, call logs, restored signal handlers, `_clean` results, `get_junk` contents, canceled delayed-call state, unchanged thread enumeration, and successful second spinner run after a previously timed-out deferred later fires.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_spinner.py -->
