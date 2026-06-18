# subset-b-009005 Research

Grouped research for six python-subunit 1.4.4 files vendored under WiredTiger tests. Each section preserves the original source path so the reconciliation lane can split the grouped report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol.py

## Purpose

This file is the broad regression suite for python-subunit's original text protocol and adjacent unittest integration helpers. It validates the public imports exposed by `subunit`, the line-oriented `TestProtocolServer` parser, the `TestProtocolClient` serializer, remoted test objects, child-process execution, and process isolation helpers. The tests exercise both old stdlib-like `TestResult` behavior and testtools extended result behavior, which is important because subunit sits between external test producers and many generations of Python result consumers.

## Important APIs, Types, and Test Fixtures

- `details_to_str(details)` uses `testtools.TestResult()._err_details_to_string` to normalize detail dictionaries into the string form expected by legacy error/failure tuples.
- `TestHelpers` covers `subunit._unwrap_text` for text files, `io.FileIO`, and `io.BytesIO`, ensuring binary stream access is preserved when possible.
- `TestTestImports` asserts the package-level API exports `DiscardStream`, `ExecTestCase`, `IsolatedTestCase`, `ProtocolTestCase`, `RemotedTestCase`, `RemoteError`, `TestProtocolClient`, and `TestProtocolServer`.
- `TestProtocolServerForward`, `TestTestProtocolServerPipe`, `TestTestProtocolServerStartTest`, `TestTestProtocolServerPassThrough`, and `TestTestProtocolServerLostConnection` drive `TestProtocolServer.lineReceived`, `readFrom`, and `lostConnection`.
- `TestInTestMultipart`, `TestTestProtocolServerAddError`, `TestTestProtocolServerAddFailure`, `TestTestProtocolServerAddxFail`, `TestTestProtocolServerAddunexpectedSuccess`, `TestTestProtocolServerAddSkip`, and `TestTestProtocolServerAddSuccess` cover outcome parsing, bracketed details, multipart details, quoted closing brackets, and compatibility shims for result methods that may not support extended details.
- `TestTestProtocolServerProgress`, `TestTestProtocolServerStreamTags`, and `TestTestProtocolServerStreamTime` cover stream metadata directives.
- `TestRemotedTestCase` and `TestRemoteError` validate identity, formatting, equality, and non-runnable remote error behavior.
- `TestExecTestCase`, `DoExecTestCase`, `TestIsolatedTestCase`, and `TestIsolatedTestSuite` cover subprocess and fork-isolated execution helpers.
- `TestTestProtocolClient` validates serialized text protocol output for start, success, failure, error, skip, expected failure, unexpected success, progress, time, tags, Unicode test IDs, and multipart `testtools.content.Content` details.

## Control Flow and State Behavior

The server tests model a text protocol state machine. A `test` or `testing` line creates a `RemotedTestCase` and emits `startTest`. Outcome lines such as `success`, `successful`, `failure`, `error`, `skip`, `xfail`, and `uxsuccess` terminate the current test with the appropriate result event and `stopTest`. When an outcome line opens a bracketed detail block, the server switches into detail-reading mode until a bare closing `]` is received; an escaped bracket is represented by a leading-space line such as ` ]`. Multipart detail mode delegates to `subunit.details.MultipartDetailsParser`.

The pass-through tests establish that lines not recognized in the current parser state are written to the configured stream, but that detail parsers retain control while inside a detail block. `lostConnection` tests verify terminal recovery: no started test means no event, a started but unfinished test becomes an `addError` with a remote lost-connection message, and an interrupted outcome/detail block reports that the connection was lost during that outcome's report.

The client tests cover the reverse flow: `TestProtocolClient` receives unittest/testtools result calls and writes text protocol lines to a byte stream. Simple outcomes produce one-line records; errors and failures with exceptions produce bracketed tracebacks; extended detail dictionaries produce multipart records. Progress, time, and tags emit stream-level directives immediately. `stopTest` intentionally emits no bytes because the v1 protocol treats outcome lines as test terminators.

State is mostly in-memory: `BytesIO` captures serialized streams, testtools result doubles capture `_events`, and class-level boolean flags in isolated test fixtures verify that child process mutations do not persist in the parent. Temporary files are used only to exercise `_unwrap_text` and are removed via cleanup hooks.

## Dependencies and Integration Points

The suite depends on `unittest`, `testtools`, `iso8601`, and the vendored `subunit` package. It imports testtools compatibility helpers (`_b`, `_u`), content types, matchers, and result doubles for Python 2.6/2.7 style compatibility even though this vendored copy targets Python 3. The subprocess execution tests rely on sibling sample scripts in the `subunit.tests` package and on POSIX for fork-based isolation tests. The suite integrates directly with public subunit APIs and with internal constants from `subunit.tests` that normalize remote exception representations across testtools versions.

## Risks and Maintenance Signals

- The tests encode precise textual protocol bytes, including whitespace and bracket escaping; parser or serializer refactors can break compatibility with existing subunit consumers.
- Several assertions allow alternate traceback representations because testtools changed traceback formatting. Future dependency changes may require similar compatibility branches.
- Outcome compatibility differs by result implementation: old Python-style results may map `xfail` to success or `uxsuccess` to failure, while extended testtools results preserve richer events and details.
- Isolation tests are skipped outside POSIX, so regressions in fork-based behavior may not be detected on Windows.
- `TestTestProtocolServerPipe.test_non_test_characters_forwarded_immediately` and some debug/count tests are placeholders, indicating incomplete coverage for immediate forwarding and child-process count behavior.

## Test Signals

This file is itself the test signal for the v1 subunit protocol. Strong signals include full start/outcome/stop event order assertions, passthrough byte assertions, lost-connection recovery assertions, Unicode serialization, multipart detail serialization, progress/time/tag directives, and process-isolation checks. It should be run with the rest of python-subunit's test suite whenever protocol parsing, result adaptation, or packaging of sample scripts changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol2.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol2.py

## Purpose

This file tests python-subunit's v2 binary protocol adapters. It verifies that `StreamResultToBytes` conforms to the testtools `StreamResult` contract and emits stable binary packets, and that `ByteStreamToStreamResult` parses those packets back into `StreamResult.status` events while safely handling non-subunit bytes, malformed packets, bad checksums, invalid UTF-8, and optional property-based fuzzing.

## Important APIs, Types, and Constants

- `CONSTANT_ENUM`, `CONSTANT_INPROGRESS`, `CONSTANT_SUCCESS`, `CONSTANT_UXSUCCESS`, `CONSTANT_SKIP`, `CONSTANT_FAIL`, `CONSTANT_XFAIL`, `CONSTANT_EOF`, `CONSTANT_FILE_CONTENT`, `CONSTANT_MIME`, `CONSTANT_TIMESTAMP`, `CONSTANT_ROUTE_CODE`, `CONSTANT_RUNNABLE`, and `CONSTANT_TAGS` are golden binary packets for deterministic wire compatibility checks.
- `TestStreamResultToBytesContract` mixes in `TestStreamResultContract` and returns `subunit.StreamResultToBytes(BytesIO())`.
- `TestStreamResultToBytes` checks varint number encoding boundaries, volatile packet-length boundaries, known status encodings, route codes, runnable flags, tags, timestamps, file content, MIME type, EOF, and unknown status rejection.
- `TestByteStreamToStreamResult` checks conversion of raw bytes to file-content events, parsing of valid v2 packets, parser-error status events for corrupt packets, route+file combined packets, and an optional Hypothesis binary fuzz test when `hypothesis` is importable.
- Helper methods `check_events`, `check_event`, and `_event` build expected `StreamResult` event tuples for compact parser assertions.

## Control Flow and State Behavior

The encoder tests call `StreamResultToBytes.status(...)` with one or more status fields and inspect the resulting `BytesIO` bytes. Numeric encoding is tested at every variable-length boundary: 1-byte values up to 63, 2-byte values up to 16383, 3-byte values up to 4194303, and 4-byte values up to 1073741823. Packet length tests focus on boundaries where the packet length field itself changes size, preventing off-by-one regressions.

The decoder tests feed `BytesIO` streams to `ByteStreamToStreamResult(...).run(result)`. When `non_subunit_name` is set, bytes outside v2 packets become `status(file_name=<name>, file_bytes=<byte>)` or aggregated file-content events. A signature-like byte sequence inside a multibyte UTF-8 character must not be misread as a subunit packet start. When `non_subunit_name` is omitted, the first non-subunit byte raises an exception and leaves the unread remainder in the source stream.

Malformed packet tests assert that parse failures are reported as two synthetic `subunit.parser` events: one attaches the packet bytes as `application/octet-stream`, and one reports `test_status='fail'` with a text parser error. This keeps parser corruption visible in the result stream rather than crashing successful decoding of surrounding content. The optional Hypothesis test feeds arbitrary binary data through the decoder to assert complete stream consumption without requiring all bytes to be valid subunit.

## Dependencies and Integration Points

The tests use `BytesIO`, `datetime`, `iso8601.UTC`, `testtools.TestCase`, `testtools.matchers.Contains` and `HasLength`, `StreamResult` doubles, and `TestStreamResultContract`. Hypothesis is optional; when unavailable, the property test is not defined. The subject APIs are exposed through `subunit.StreamResultToBytes` and `subunit.ByteStreamToStreamResult`, which are implemented in `python/subunit/v2.py` and integrated with testtools `StreamResult` consumers.

## Risks and Maintenance Signals

- Golden binary constants make wire-format changes explicit, but they also mean benign ordering changes, especially tag set order, must be handled deliberately. The tag test accepts either ordering.
- Packet length and varint boundaries are high-risk because length includes signature, flags, encoded length, body, and CRC. The tests directly protect boundary calculations.
- Parser error reporting is part of observable behavior; changing exceptions into raised errors would break downstream tooling that expects parser failures as status events.
- Hypothesis coverage is conditional, so environments without the optional test dependency lose fuzz-style assurance over arbitrary binary streams.
- The tests validate selected malformed packet cases, not every invalid flag combination or truncation path.

## Test Signals

This file is the focused regression suite for subunit v2 byte compatibility. The strongest signals are golden packet equality, round-trip parser event equality, error-event emission for CRC and structural failures, UTF-8 edge cases, and the testtools `StreamResult` contract mixin.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_results.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_results.py

## Purpose

This file tests result decorators and reporting adapters in `subunit.test_results`. These helpers sit between raw unittest/testtools events and subunit output formats, adding hooks, timestamps, tag/time collapsing, per-test callback aggregation, and CSV reporting. The suite validates event ordering and data preservation rather than wire-format bytes.

## Important APIs, Types, and Test Fixtures

- `LoggingDecorator` subclasses `HookedTestResultDecorator` and increments `_calls` in `_before_event`.
- `AssertBeforeTestResult` asserts that an earlier decorator ran before forwarding reaches this decorator, proving hook order through a decorator chain.
- `TimeCapturingResult` is a minimal `unittest.TestResult` with a `time()` method and `failfast` state used by auto-timing tests.
- `TestHookedTestResultDecorator` exercises forwarding and hook invocation for run lifecycle, test lifecycle, all major outcomes, progress, `wasSuccessful`, `shouldStop`, `stop`, and `time`.
- `TestAutoTimingTestResultDecorator` verifies automatic time emission on real result events, suppression for progress and `shouldStop`, explicit `time()` behavior, `time(None)` re-enabling auto timing, and failfast property propagation.
- `TestTagCollapsingDecorator` verifies that adjacent tag events are collapsed outside and inside tests and flushed before outcome events where ordering matters.
- `TestTimeCollapsingDecorator` verifies that repeated adjacent time events collapse to first and last distinct timestamps before a non-time event.
- `TestByTestResultTests` validates `TestByTestResult`, which converts start/outcome/stop event sequences into one callback per completed test.
- `TestCsvResult` validates CSV output headers and one-row-per-test reporting.

## Control Flow and State Behavior

The decorator tests build chains of result objects and then call result methods through the outer decorator. `HookedTestResultDecorator` is expected to run `_before_event` before forwarding to the decorated result for every observable event-like operation. The ordering fixture proves the outer hook increments its counter before the inner assertion hook runs.

`AutoTimingTestResultDecorator` keeps state about whether explicit time events have been observed. If no explicit time has been sent, it emits a current timestamp before test events. `progress` and `shouldStop` do not trigger automatic timestamps. Calling `time(a_datetime)` forwards that timestamp and suppresses automatic timestamps until `time(None)` is called, which passes `None` through and then allows automatic timing again.

`TagCollapsingDecorator` accumulates pending tag additions/removals. Outside tests, repeated tag events collapse and flush at the next test start or run end. Inside a test, repeated tag updates collapse and flush before the outcome event, preserving protocol semantics where tag placement relative to outcomes matters. Add/remove conflicts are resolved so the final event represents net tag state.

`TimeCollapsingDecorator` buffers consecutive time events. The first time is always forwarded; if multiple distinct times occur before another event, the last distinct time is forwarded just before that next event. Duplicate times collapse to one event. The decorator does not synthesize new times for ordinary test events.

`TestByTestResult` tracks per-test start time, stop time, tags, details, and status. On `stopTest`, it calls the user callback with one dictionary. Exceptions passed as `exc_info` are converted to `TracebackContent`; detail dictionaries are preserved. Unexpected success maps to `status='success'` with supplied details, and skip reason strings are wrapped as text content. `CsvResult` builds on this style to write a header at `startTestRun` and rows for completed tests.

State is in-memory except for CSV writes to a provided text stream. Tests override `_now` with deterministic iterators to make start/stop times predictable.

## Dependencies and Integration Points

The file depends on `csv`, `datetime`, `sys`, `unittest`, `StringIO`, `testtools`, `testtools.content.TracebackContent`, `text_content`, and `ExtendedTestResult`. It imports `subunit`, `iso8601`, and `subunit.test_results`. These decorators integrate with both stdlib `unittest.TestResult` and testtools extended APIs, so they are important adapters between raw result event producers and subunit stream writers.

## Risks and Maintenance Signals

- Decorator forwarding must preserve subtle property behavior such as `failfast` and `shouldStop`, not just method calls.
- Tag ordering is protocol-sensitive; tags must be emitted before outcomes when they apply to a test.
- Automatic time insertion can create noisy or misleading streams if it triggers on non-event probes such as `shouldStop`; the tests guard against this.
- `TestByTestResult` assumes a well-formed start/outcome/stop lifecycle. Out-of-order or missing events are not deeply tested here.
- CSV tests validate minimal output only; quoting, newline handling, and unusual test IDs depend on Python's `csv` module but are not exhaustively covered.

## Test Signals

The suite provides strong event-order assertions using `ExtendedTestResult._events`, deterministic timing via `_now`, callback payload equality for each outcome, and CSV reader checks for output shape. It is the main local signal for changes to `subunit.test_results` decorators and summary/reporting adapters.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/v2.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/v2.py

## Purpose

This module implements python-subunit's v2 binary stream protocol bridge. `StreamResultToBytes` converts testtools `StreamResult.status` calls into framed bytes, while `ByteStreamToStreamResult` parses framed bytes back into `StreamResult.status` events. The module also supports wrapping mixed non-subunit output as file-content status events and reports parser failures as structured status events.

## Important APIs, Types, Constants, and Functions

- `__all__ = ['ByteStreamToStreamResult', 'StreamResultToBytes']` defines the public exports.
- `SIGNATURE = b'\xb3'` marks packet starts.
- Format constants (`FMT_8`, `FMT_16`, `FMT_24`, `FMT_32`, `FMT_TIMESTAMP`) centralize big-endian `struct` packing and unpacking.
- Flag constants (`FLAG_TEST_ID`, `FLAG_ROUTE_CODE`, `FLAG_TIMESTAMP`, `FLAG_RUNNABLE`, `FLAG_TAGS`, `FLAG_MIME_TYPE`, `FLAG_EOF`, `FLAG_FILE_CONTENT`) describe optional packet fields.
- `EPOCH` anchors timestamp encoding to Unix epoch in `iso8601.UTC`.
- `read_exactly(stream, size)` repeatedly reads until exactly `size` bytes are returned or raises `ParseError` for short reads.
- `ParseError` is the module-local exception used to turn parser failures into result events.
- `StreamResultToBytes.status(...)` is the public encoder entry point. It delegates to `_write_packet`.
- `StreamResultToBytes._encode_number(value)` and `_write_number` encode unsigned varints in 1, 2, 3, or 4 bytes with top bits denoting width.
- `StreamResultToBytes._write_packet(...)` builds the packet body, calculates flags and length, appends CRC-32, writes all bytes to the binary output stream, and flushes.
- `ByteStreamToStreamResult.run(result)` is the public parser loop and is also aliased as `__call__`.
- `ByteStreamToStreamResult._parse_packet`, `_parse`, `_parse_varint`, and `_read_utf8` implement framed packet parsing, validation, and event emission.

## Control Flow and State Behavior

`StreamResultToBytes` converts each `status` call independently. `_write_packet` starts with the signature and placeholders for flags and length, sets the v2 version flag (`0x2000`), and appends optional fields in a fixed order: timestamp, test ID, tags, MIME type, file content, EOF flag, and route code. The low status bits are selected from `status_mask`, so invalid status strings raise before bytes are emitted. Packet length includes the signature, flags, encoded length, payload, and CRC. The code chooses a 1-, 2-, or 3-byte length field and rejects packets beyond the policy limit rather than emitting a 4-byte length. It computes CRC-32 over packet content before the CRC, appends the stored CRC, writes through a `memoryview` loop to tolerate partial writes, and flushes the output stream.

`ByteStreamToStreamResult.run` reads one byte at a time until EOF. If a byte is the signature and the parser is not in the middle of a UTF-8 character, it parses a packet. Otherwise, it either raises `Exception("Non subunit content", content)` or wraps non-subunit content in `result.status(file_name=non_subunit_name, file_bytes=...)`. The non-subunit wrapper tries to aggregate nearby bytes up to 1 MiB or a short select timeout, with Windows and non-file-descriptor fallbacks to one-byte behavior. An incremental UTF-8 decoder prevents the parser from mistaking the middle byte of a multibyte UTF-8 character for a packet signature.

`_parse_packet` catches `ParseError` and emits two structured status events under `test_id="subunit.parser"`: the raw packet bytes as `application/octet-stream`, then a failing parser error as UTF-8 text. `_parse` reads flags and length, validates CRC, decodes the optional fields in the same order used by the encoder, checks file-content length, resolves runnable/eof booleans and status lookup, and calls `result.status(...)`. `_read_utf8` validates declared length, rejects NUL bytes, requires full UTF-8 decoding, and returns the decoded string with the next position.

The module has no persistent storage. State is confined to the output stream, source stream, and the parser's incremental UTF-8 decoder.

## Dependencies and Integration Points

The module uses only Python standard library modules plus `iso8601` and `subunit`: `builtins`, `codecs`, `datetime`, `select`, `struct`, `sys`, and `zlib`. It uses `subunit.make_stream_binary` to normalize input/output streams and integrates with testtools by implementing the `StreamResult`-style `status` API. It is consumed by package-level imports in `subunit` and by filter scripts that convert between subunit v1/v2 streams and other outputs.

## Risks and Maintenance Signals

- Packet compatibility is a public wire contract. Field ordering, flag values, varint widths, CRC calculation, and length calculation must remain stable unless the protocol version changes.
- `_write_packet` assumes `file_bytes` is not `None` whenever `file_name` is provided; callers violating that contract will fail when `len(file_bytes)` is evaluated.
- Large file attachments are rejected once packet length exceeds the 3-byte length policy; the TODO notes future chunking but does not implement it.
- Parser failure is intentionally non-throwing after a signature byte: errors become status events. Tooling may rely on that behavior.
- Non-subunit aggregation depends on `select` and platform/file-descriptor behavior, so packetization of wrapped stdout can differ across platforms while preserving byte content.
- Timestamp encoding stores microseconds as nanoseconds but decodes back through `datetime.timedelta(microseconds=nanoseconds/1000)`, preserving Python datetime precision rather than true nanosecond precision.

## Test Signals

`test_test_protocol2.py` provides the main regression coverage: golden packet constants, varint boundary checks, packet-length boundary checks, CRC and malformed packet tests, UTF-8 validation tests, non-subunit wrapping behavior, and optional Hypothesis fuzzing. Any edit here should be validated against that suite and downstream filter script behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/v2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.cfg -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.cfg

## Purpose

This packaging configuration file customizes setuptools egg metadata generation for the vendored `python-subunit` package. It keeps generated egg-info version tags stable by disabling build and date suffixes.

## Important Configuration

- `[egg_info]` selects setuptools' egg-info command configuration.
- `tag_build =` is blank, so development/build tags are not appended to the package version.
- `tag_date = 0` disables adding the current date to generated version metadata.

## Control Flow, State, and Persistence

The file has no executable control flow. It is read by setuptools when `setup.py` invokes packaging commands that generate or update egg metadata. Its effects are persisted only in generated packaging artifacts such as egg-info metadata, not in runtime subunit behavior.

## Dependencies and Integration Points

The only integration point is setuptools/distutils configuration discovery. In this vendored tree it complements `setup.py`, which supplies the package metadata, dependencies, package list, and console entry points.

## Risks and Maintenance Signals

- Because the file suppresses dynamic build/date tags, downstream packaging expects `setup.py` or source metadata to provide the authoritative version.
- The blank `tag_build` value is meaningful; formatting cleanup that removes it could change generated egg-info behavior.
- This file does not constrain wheel metadata directly beyond the setuptools command behavior.

## Test Signals

There is no direct unit test for this file. Packaging smoke tests such as `python setup.py egg_info` or modern build invocations would reveal whether generated metadata remains stable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.py

## Purpose

This script defines setuptools packaging metadata for the Python implementation of the subunit test streaming protocol. In the WiredTiger source tree it packages the vendored `python-subunit` 1.4.4 test dependency, including its Python modules, runtime dependencies, test extras, and console conversion/filter tools.

## Important APIs, Functions, and Metadata

- `_get_version_from_file(filename, start_of_line, split_marker)` scans a file for lines starting with a marker, takes the last match, splits it on a marker, and returns the stripped right-hand value. It returns `None` for missing files or missing matches.
- `VERSION` is resolved from `PKG-INFO` `Version:` first, then from `Makefile` `VERSION=`, then falls back to `"0.0"`.
- `relpath = os.path.dirname(__file__)`; if non-empty, the script changes the working directory to the script directory so relative metadata files such as `README.rst` resolve correctly.
- `setup(...)` declares:
  - package name `python-subunit` and computed version;
  - README-based long description;
  - supported Python versions 3.7 through 3.12;
  - package list `subunit`, `subunit.tests`, and `subunit.filter_scripts`;
  - `package_dir={'subunit': 'python/subunit'}`;
  - `python_requires=">=3.7"`;
  - runtime dependencies `iso8601` and `testtools>=0.9.34`;
  - console scripts for v1/v2 conversion, filtering, listing, notification, output, stats, tags, CSV, disk export, GTK, JUnit XML, pyunit, and TAP conversion;
  - test/doc extras for `fixtures`, `testscenarios`, `hypothesis`, and `docutils`.

## Control Flow and State Behavior

At import/execution time the script computes `VERSION` by reading local metadata files. It changes process working directory to the setup script directory when invoked from another directory, then calls `setuptools.setup`. Packaging state is created by setuptools commands outside the script, such as build directories, egg-info, installed scripts, or metadata files. The script itself does not store runtime application state.

The version lookup intentionally prefers distribution metadata (`PKG-INFO`) over development checkout metadata (`Makefile`). The helper's list comprehension reads all matching lines and selects the last one, which allows later matching lines to override earlier ones but also means malformed duplicate metadata can affect the version.

## Dependencies and Integration Points

The script imports `os.path` and `setuptools.setup`. It reads `README.rst`, `PKG-INFO`, and `Makefile` relative to the package root. It exposes console entry points that target modules under `subunit.filter_scripts`, so packaging must include those modules and runtime imports must resolve the vendored `subunit` package. Runtime dependencies on `iso8601` and `testtools` match the modules used by `subunit.v2`, protocol tests, and result adapters.

## Risks and Maintenance Signals

- The helper uses `open(filename)` without an explicit encoding or context manager. That is acceptable for small local metadata files but can be brittle under unusual default encodings or static-analysis standards.
- If both `PKG-INFO` and `Makefile` are missing or malformed, the package version silently becomes `"0.0"`, which can confuse downstream packaging.
- The package list is explicit. Adding new import packages under `python/subunit` requires updating `setup.py` or they will not be installed.
- Console script entry points are a public CLI surface; renaming filter modules or `main` functions breaks installed tools.
- `tests_require` is legacy setuptools metadata; `extras_require['test']` is the more relevant modern dependency hook.

## Test Signals

Packaging signals are indirect: building the package, running `egg_info`, installing in a clean environment, invoking console scripts, and running the python-subunit test suite. The protocol and result test files in this work item also validate that declared runtime dependencies (`iso8601`, `testtools`) are sufficient for core behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.py -->
