# Research: subset-b-009004

Grouped research for the vendored `python-subunit-1.4.4` packaging, protocol, filter, and focused test files used under WiredTiger's third-party test tree. Each source file has its own source-tree-preserving section for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/MANIFEST.in -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/MANIFEST.in

## Purpose

`MANIFEST.in` controls the source distribution payload for this vendored Python package. It is intentionally small and mostly prunes non-Python build-system leftovers from the upstream multi-language subunit project while explicitly including `NEWS`.

## Important APIs, Types, and Functions

This is declarative setuptools manifest syntax rather than executable Python. It uses `exclude` for files such as `.gitignore`, `aclocal.m4`, `configure*`, `Makefile*`, `INSTALL`, `install-sh`, `missing`, `py-compile`, `stamp-h1`, and libtool/autotools helper names; `prune` for directories such as `autom4te.cache`, `c`, `c++`, `compile`, `m4`, `perl`, and `shell`; and `include NEWS` to keep the changelog in the sdist.

## Control Flow

During `setuptools` sdist generation, manifest commands are applied in order to the file list. The file removes generated/autotools and non-Python implementation artifacts, then restores `NEWS` as package documentation. Runtime import and test execution never read this file.

## State and Persistence Behavior

The file persists package assembly policy only. It does not create runtime state, but it determines what can be reconstructed from a source archive. If a needed Python package file is excluded here, builds from sdist could be incomplete even when the working tree is healthy.

## Dependencies and Integration Points

It integrates with setuptools via `pyproject.toml` and `setup.py`. It also reflects upstream subunit's mixed-language layout: the vendored Python package only needs the Python tree, packaging metadata, license/readme/news, and generated egg-info files, not C/C++/Perl/shell sources.

## Risks and Test Signals

The main risk is accidental omission from source distributions, especially if new Python-side data files or console script assets are added without updating the manifest. A useful validation signal is `python3 -m build --sdist` followed by checking the tarball contains `python/subunit`, `setup.py`, `setup.cfg`, `pyproject.toml`, `PKG-INFO`, licenses, and `NEWS`, while excluding pruned upstream-language directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/pyproject.toml -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/pyproject.toml

## Purpose

`pyproject.toml` declares the PEP 517 build backend and local Ruff formatting/linting defaults for the vendored `python-subunit` package.

## Important APIs, Types, and Functions

The `[build-system]` table requires `setuptools>=43.0.0` and selects `setuptools.build_meta`, so modern build frontends can build wheels/sdists without invoking `setup.py` directly. The `[tool.ruff]` section sets `line-length = 120` and `target-version = "py37"`, documenting the intended Python syntax baseline for linting.

## Control Flow

Build tools read this file before isolation and dependency installation. The backend then delegates metadata and file selection to setuptools configuration and package files. Ruff reads its section only when linting this sub-tree.

## State and Persistence Behavior

The file persists build-environment requirements and style configuration. It carries no application state and has no runtime effect after the package is installed.

## Dependencies and Integration Points

It integrates with `setuptools`, the local `setup.py`/`setup.cfg` metadata, and any CI or developer lint task that runs Ruff. In the larger WiredTiger tree it is third-party metadata, so repository-wide tooling should avoid rewriting it unless intentionally updating the vendored package.

## Risks and Test Signals

The build backend is stable, but the low minimum setuptools version can interact poorly with newer packaging standards if metadata changes elsewhere. Test signals are successful isolated builds, successful editable or wheel installs, and Ruff invocations honoring Python 3.7-compatible syntax rather than assuming a newer language level.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/__init__.py

## Purpose

`subunit/__init__.py` is the central public API for the Python Subunit package. It implements the original line-oriented subunit v1 protocol, exposes v2 stream adapters imported from `subunit.v2`, provides TAP conversion and tag filtering helpers, and supplies `unittest` integration classes for remote, isolated, and executable tests.

## Important APIs, Types, and Functions

Public exports include `TestProtocolServer`, `TestProtocolClient`, `ProtocolTestCase`, `RemotedTestCase`, `ExecTestCase`, `IsolatedTestCase`, `IsolatedTestSuite`, `run_isolated`, `TAP2SubUnit`, `tag_stream`, `TestResultStats`, `read_test_list`, `make_stream_binary`, and constants `PROGRESS_SET`, `PROGRESS_CUR`, `PROGRESS_PUSH`, and `PROGRESS_POP`. `__version__` is `(1, 4, 4, 'final', 0)`.

`TestProtocolServer` parses v1 byte lines into a `testtools`-extended result API. Its private parser states (`_OutSideTest`, `_InTest`, `_Reading*Details`) track whether a `test:` directive is active and whether the parser is consuming simple or multipart details. `TestProtocolClient` performs the reverse serialization: `startTest` writes `test:`, outcome methods write `error:`, `failure:`, `successful:`, `skip:`, `xfail:`, or `uxsuccess:`, and `_write_details` emits multipart details with chunked bodies.

`ProtocolTestCase` adapts a subunit byte stream to the callable `unittest` case/suite protocol. `RemotedTestCase` is a placeholder object representing a test that ran elsewhere. `TestResultStats` counts total, failed, skipped, passed, and seen tags. `TAP2SubUnit` converts TAP text into v2 status packets through `StreamResultToBytes`. `tag_stream` reads v2 packets with `ByteStreamToStreamResult` and rewrites `test_tags`.

## Control Flow

For v1 input, `ProtocolTestCase.run` wraps the target result in `TestProtocolServer` and feeds lines until EOF, then calls `lostConnection`. `_ParserState.lineReceived` identifies directive keywords, while `_InTest._outcome` validates that the outcome matches the current test id, switches back outside the test, or enters a details-reading state. Detail state delegates to `subunit.details` parsers and then reports the outcome to the decorated result.

For output, a test suite calls `TestProtocolClient.startTest`, one outcome method, and `stopTest`. Outcomes with traceback tuples become simple bracketed traceback details; outcomes with `details` dicts become multipart details, where each content item is serialized as content type, name, chunked bytes, and final bracket marker.

`run_isolated` forks, redirects child stdout to a pipe, runs the original `unittest` class method with `TestProtocolClient`, and has the parent parse the pipe through `TestProtocolServer`. `ExecTestCase` executes the script path stored in a test method docstring and parses stdout as subunit.

## State and Persistence Behavior

Parser state is kept in `TestProtocolServer._state`, `current_test_description`, and `_current_test`; malformed or truncated streams can synthesize `RemoteError` events on lost connection. `TestProtocolClient` writes directly to its binary stream and flushes at test boundaries. `run_isolated` uses OS pipes and forks, but persists no files. `tag_stream` and TAP conversion are streaming transformations and do not retain complete input beyond current TAP log/test state.

## Dependencies and Integration Points

The module depends on `testtools`, `iso8601`, `subunit.chunked`, `subunit.details`, and `subunit.v2`. It integrates with Python `unittest`, command-line filters in `subunit/filter_scripts`, and external TAP producers. Binary stream handling is important: `make_stream_binary` unwraps text streams and sets Windows file descriptors to binary mode.

## Risks and Test Signals

Key risks are protocol fidelity, byte/text boundary mistakes, and edge cases in v1 line parsing. `DiscardStream.write` has duplicated `pass` but no behavioral impact. `RemotedTestCase.run` calls `stopTest` twice, which looks suspicious and is worth preserving only because compatibility tests may depend on historic behavior. `run_isolated` assumes `os.fork`, so it is Unix-oriented. TAP parsing is regex based and handles common TAP constructs but not every TAP dialect.

The strongest test signals come from `test_subunit_filter.py`, `test_subunit_stats.py`, `test_subunit_tags.py`, `test_tap2subunit.py`, `test_run.py`, and the broader unlisted protocol tests in the same package. They exercise v1 parsing, v2 tag rewriting, TAP plan/missing-test behavior, stats accounting, and runner output decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_output.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_output.py

## Purpose

`_output.py` implements the `subunit-output` command helper. It generates subunit v2 `StreamResult` packets from CLI status options, tags, timestamps, and optional file attachments.

## Important APIs, Types, and Functions

`output_main()` parses command-line arguments, wraps stdout with `StreamResultToBytes`, and calls `generate_stream_results`. `parse_arguments()` creates option groups for status commands (`--exists`, `--fail`, `--skip`, `--success`, `--uxsuccess`, `--xfail`, `--inprogress`) and file options (`--attach-file`, `--file-name`, `--mimetype`, `--tag`). `set_status_cb()` enforces a single status command and extracts the following `TEST_ID`. `generate_stream_results()` emits `startTestRun`, one or more `status` calls, and `stopTestRun`. `_CHUNK_SIZE` is 3.5 MiB.

## Control Flow

Argument parsing validates that `--mimetype` and `--file-name` appear only with `--attach-file`. Attachments are opened in binary mode; `-` is converted to binary stdin and defaults `file_name` to `stdin`. Generation sends timestamp and tags on the first packet only. For final statuses, `test_status` is delayed until the last packet when attachments are chunked; for `inprogress`, status is emitted on the first packet. EOF is set when the next read is empty.

## State and Persistence Behavior

State is local to the parsed options and attachment reader. The command writes a binary subunit stream to stdout and opens but does not explicitly close attachment files in this module. No files are persisted except what callers redirect.

## Dependencies and Integration Points

It depends on `optparse`, `iso8601.UTC`, `subunit.make_stream_binary`, and `subunit.v2.StreamResultToBytes`. It is exposed by `filter_scripts/subunit_output.py` and likely by packaging entry points.

## Risks and Test Signals

Risks include option parser compatibility, binary stdin handling, and multi-packet attachment metadata duplication. `test_output_filter.py` is extensive: it verifies all status commands parse, required test ids, invalid option combinations, file chunking, binary and empty files, stdin attachments, single-use tags/timestamps/mimetypes, and final-status placement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_output.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_to_disk.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_to_disk.py

## Purpose

`_to_disk.py` exports a subunit v2 stream into a directory tree: one directory per test id, one `test.json` metadata file, and one file for each attachment/detail.

## Important APIs, Types, and Functions

`_allocate_path(root, sub)` normalizes a requested path under a root, prevents parent-directory escape by rewriting separators, and appends numeric suffixes for collisions. `_open_path(root, subpath)` creates parent directories and opens a binary file. `_json_time()` stringifies optional timestamps. `DiskExporter.export(test_dict)` writes metadata and detail files. `to_disk(argv=None, stdin=None, stdout=None)` is the CLI entry point.

## Control Flow

`to_disk` parses `--directory` and an optional input filename. It creates a `DiskExporter`, wraps `export` with `testtools.StreamToDict`, then calls `run_tests_from_stream` with `protocol_version=2`. `StreamToDict` accumulates per-test status data and calls `export` when complete. `DiskExporter.export` allocates a root for the test id, writes sorted metadata to `test.json`, then iterates each detail content's bytes to sibling files under that root.

## State and Persistence Behavior

This module is persistence-oriented. It creates directories and binary files under the configured export directory. Collision handling creates suffixes such as `foo-1`. Escape prevention compares `realpath` values and rewrites unsafe subpaths, reducing traversal risk from malicious test ids or attachment names.

## Dependencies and Integration Points

It depends on `testtools.StreamToDict`, `subunit.filters.run_tests_from_stream`, JSON, and the filesystem. The thin CLI wrapper is `filter_scripts/subunit2disk.py`.

## Risks and Test Signals

Path safety is the main risk. The prefix check uses `candidate.startswith(realroot)`, which can be vulnerable to sibling-prefix confusion if not followed by a path separator, although unsafe paths are later rooted through recursive rewriting only when the prefix check fails. Large attachments are streamed chunk by chunk but still materialized by `StreamToDict` semantics before export. `test_filter_to_disk.py` smoke-tests JSON metadata and attachment content for a successful tagged test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_to_disk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/chunked.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/chunked.py

## Purpose

`chunked.py` implements HTTP-style chunked byte encoding and decoding used by the subunit v1 multipart detail format.

## Important APIs, Types, and Functions

`Decoder(output, strict=True)` accepts encoded bytes via `write()` and writes decoded body bytes to `output`. It exposes `close()` to detect incomplete streams. Internal states are `_read_length`, `_read_body`, and `_finished`. `Encoder(output)` buffers small writes and serializes chunks through `write()`, `flush(extra_len=0)`, and `close()`.

## Control Flow

The decoder buffers writes, scans hex length lines until newline, validates CRLF in strict mode, then copies exactly `body_length` bytes to the output. A zero-length chunk switches to `_finished` and any bytes after the terminal chunk are returned as residue. The encoder buffers until a write would reach 65,536 bytes; it then flushes a hex length header, buffered bytes, and the large write body. `close()` writes the final `0\r\n`.

## State and Persistence Behavior

Both classes are in-memory stream adapters. `Decoder` keeps `buffered_bytes`, `body_length`, and state function references. `Encoder` keeps a byte list and `buffer_size`. Persistence occurs only through the caller's output stream.

## Dependencies and Integration Points

The only external helper is `testtools.compat._b` for byte literals. `subunit.details.MultipartDetailsParser` uses `Decoder`, and `TestProtocolClient._write_details` uses `Encoder`.

## Risks and Test Signals

Risks center on strict CRLF parsing, residual bytes after terminal chunks, incomplete stream detection, and memory behavior for many small writes. `test_chunked.py` validates empty, short, long, hex, combined, and oversized chunks; strict versus non-strict newline handling; residue after EOF; write-after-finish errors; and encoder buffering boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/chunked.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/details.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/details.py

## Purpose

`details.py` parses v1 subunit outcome details, either simple bracketed traceback/message blocks or multipart MIME-like detail blocks with chunked payloads.

## Important APIs, Types, and Functions

`DetailsParser` is an empty base marker. `SimpleDetailsParser(state)` accumulates lines until `]\n`, unescapes lines beginning ` ]`, and returns either a `traceback`, `reason`, or `message` `testtools.content.Content` object. `MultipartDetailsParser(state)` parses `Content-Type`, part name, chunked body, and returns a dict of named `Content` objects.

## Control Flow

Simple parsing appends lines to `_message` until the end marker asks the parent state to end details. Multipart parsing uses a three-function state machine: `_look_for_content`, `_get_name`, and `_feed_chunks`. Once a chunked parser returns residue, the body is stored as a `Content` object and the parser returns to looking for the next content header.

## State and Persistence Behavior

The parsers keep accumulated bytes in memory. `MultipartDetailsParser` stores part bodies in `BytesIO` before creating content lambdas that return the captured bytes. There is no filesystem persistence.

## Dependencies and Integration Points

The module depends on `testtools.content`, `testtools.content_type`, and `subunit.chunked`. It is called by `_ReadingDetails` states in `subunit.__init__.py`.

## Risks and Test Signals

Multipart parsing has intentionally minimal error handling: malformed `Content-Type` raises `ValueError`, but the TODO notes broader error handling is absent. Large attachments are fully buffered. `test_details.py` verifies simple message accumulation, escaped bracket handling, content type/name mapping for traceback/skip/success, and multipart chunk body reconstruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/details.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/__init__.py

## Purpose

`filter_scripts/__init__.py` marks the command modules directory as a Python package. It contains no executable code, imports, or package-level state.

## Important APIs, Types, and Functions

There are no APIs in this file. The important contract is package importability for modules such as `subunit.filter_scripts.subunit_filter`, `subunit.filter_scripts.subunit2csv`, and `subunit.filter_scripts.tap2subunit`.

## Control Flow

Importing `subunit.filter_scripts` executes no behavior. Individual command modules define their own `main()` functions and `if __name__ == '__main__'` blocks.

## State and Persistence Behavior

No state is created or persisted.

## Dependencies and Integration Points

It integrates with Python's import system and packaging entry points. Without this file, older Python/package layouts could fail to resolve the command modules as package children.

## Risks and Test Signals

The file is intentionally empty. The main risk is accidental removal in environments that still require explicit package markers. Test signals are successful `python -m subunit.filter_scripts.<name>` invocations and import coverage from the command tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2csv.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2csv.py

## Purpose

`subunit2csv.py` converts a subunit stream into CSV rows using the package's `CsvResult`.

## Important APIs, Types, and Functions

`main()` calls `run_filter_script(lambda stream: StreamToExtendedDecorator(CsvResult(stream)), __doc__)`. `CsvResult` writes `test,status,start_time,stop_time` rows as tests complete.

## Control Flow

The shared filter runner parses common passthrough/output options, opens the input stream, constructs the result factory, runs the input through the v1 protocol path by default, and exits with 0 or 1 based on result success. `StreamToExtendedDecorator` adapts stream-style events to the extended result API consumed by `CsvResult`.

## State and Persistence Behavior

The script writes CSV to stdout or the shared `--output-to` path. It does not retain persistent state beyond output rows.

## Dependencies and Integration Points

It depends on `testtools.StreamToExtendedDecorator`, `subunit.filters.run_filter_script`, and `subunit.test_results.CsvResult`. It is a CLI integration point for CI tooling that wants flat test result rows.

## Risks and Test Signals

The CSV writer expects a text stream; binary stdout wrappers can cause type mismatches if the surrounding runner changes stream mode. Coverage is indirect through `CsvResult` behavior and shared filter tests rather than a dedicated command test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2csv.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2disk.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2disk.py

## Purpose

`subunit2disk.py` is the command shim for exporting a subunit v2 stream to filesystem artifacts.

## Important APIs, Types, and Functions

`main()` simply returns `to_disk()` from `subunit._to_disk`. The module imports `sys` only to call `sys.exit(main())` in its executable block.

## Control Flow

All parsing, stream decoding, and file writing are delegated to `_to_disk.to_disk`. This module exists to provide a stable module/entry-point name.

## State and Persistence Behavior

State and persistence are owned by `_to_disk`. This wrapper creates no additional state.

## Dependencies and Integration Points

It integrates packaging console entry points and `python -m subunit.filter_scripts.subunit2disk` with the actual exporter implementation.

## Risks and Test Signals

Risks are minimal in the wrapper. `test_filter_to_disk.py` validates the underlying command path by calling `_to_disk.to_disk`; packaging tests should also confirm the console script points here.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2disk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2gtk.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2gtk.py

## Purpose

`subunit2gtk.py` displays a subunit stream in a GTK progress window. It is a graphical consumer of v2 subunit events.

## Important APIs, Types, and Functions

`GTKTestResult` is a `unittest.TestResult`-like receiver that tracks `tests`, `failures`, `errors`, `skips`, `xfails`, `uxsuccesses`, `progress`, and `last_time`. It builds GTK widgets including a window, progress bar, labels, and scrolling details text. Outcome methods update counters and append test ids. `progress()` applies subunit progress constants to a `ProgressModel`. `main()` starts a reader thread that runs `ByteStreamToStreamResult(sys.stdin).run(StreamToExtendedDecorator(result))`, enters `Gtk.main()`, and exits nonzero if failures occurred.

## Control Flow

The GTK main thread owns the UI. The worker thread parses stdin and calls result methods as events arrive. UI mutations are scheduled with `GObject.idle_add` to avoid direct GTK calls from the reader thread. `stopTestRun` schedules `Gtk.main_quit`. The progress bar displays `pos/width` when width is known, otherwise it uses pulse mode.

## State and Persistence Behavior

All state is in-memory UI/result state. No files are written. The script persists only the process exit status based on `wasSuccessful`.

## Dependencies and Integration Points

It depends on PyGObject (`gi`, `Gtk`, `GObject`), `testtools.StreamToExtendedDecorator`, `subunit.ByteStreamToStreamResult`, and `subunit.progress_model.ProgressModel`. It is optional and environment-sensitive compared with the non-GUI filters.

## Risks and Test Signals

GUI availability is the main risk: missing GI bindings or headless environments will fail at import/runtime. Threaded event handling depends on `GObject.threads_init`, which is old GTK-era API. There are no direct tests in this subset, so validation should be manual or an integration smoke test with a small v2 stream in a GTK-capable environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2gtk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2junitxml.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2junitxml.py

## Purpose

`subunit2junitxml.py` converts subunit input to JUnit XML using `junitxml.JUnitXmlResult` when that optional dependency is installed.

## Important APIs, Types, and Functions

`main()` imports `junitxml.JUnitXmlResult`, wraps it with `StreamToExtendedDecorator`, and passes it to `run_filter_script`. If `junitxml` is unavailable, it prints an installation hint to stderr and exits 1.

## Control Flow

The command defers import of `junitxml` until `main`. On success, shared filter plumbing parses input and forwards events into the JUnit XML result. The filter runner handles passthrough and exit status.

## State and Persistence Behavior

The script writes XML to stdout or an output file selected by shared filter options. No other state is persisted.

## Dependencies and Integration Points

It depends on optional `junitxml`, `testtools.StreamToExtendedDecorator`, and `subunit.filters.run_filter_script`. It integrates subunit streams with CI systems that understand JUnit XML.

## Risks and Test Signals

The optional dependency path is the largest risk, and XML fidelity depends on the external `junitxml` package's interpretation of extended result events. There is no direct test in this subset; validation should include command execution with and without `junitxml` installed and comparison against expected JUnit XML for pass/fail/skip cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2junitxml.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2pyunit.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2pyunit.py

## Purpose

`subunit2pyunit.py` replays a subunit v2 stream through Python's `unittest.TextTestRunner`, making subunit input visible as ordinary pyunit-style output.

## Important APIs, Types, and Functions

`main()` parses `--no-passthrough` and `--progress`, creates a `ByteStreamToStreamResult` from stdin or a named file, decorates its result with `StreamToExtendedDecorator`, optionally routes global attachments to `CatFiles(sys.stdout)`, and runs it through either `unittest.TextTestRunner` or Bazaar's `bzrlib` progress runner.

## Control Flow

`DecorateTestCaseResult` wraps the stream-backed test case so `startTestRun` and `stopTestRun` are called around the run. The wrapper function controls whether non-test global file packets are printed to stdout. Exit code is 0 when the runner result is successful, otherwise 1.

## State and Persistence Behavior

State is limited to runner/result state. The command reads stdin or a file, writes human-readable test output to stdout/stderr, and persists no files.

## Dependencies and Integration Points

It depends on `unittest`, `testtools.DecorateTestCaseResult`, `StreamResultRouter`, `StreamToExtendedDecorator`, `subunit.ByteStreamToStreamResult`, `subunit.filters.find_stream`, and `CatFiles`. The optional `--progress` path depends on `bzrlib`.

## Risks and Test Signals

The optional Bazaar runner is likely unavailable in modern environments. Passthrough routing must not corrupt normal test output. Validation should feed v2 streams with pass, fail, skip, and global stdout packets, checking TextTestRunner output and exit status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2pyunit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_1to2.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_1to2.py

## Purpose

`subunit_1to2.py` converts a subunit v1 stream into a subunit v2 byte stream.

## Important APIs, Types, and Functions

`make_options()` returns a basic `OptionParser`. `main()` opens stdin or the named input file with `find_stream`, wraps stdout in `StreamResultToBytes`, adapts it with `ExtendedToStreamDecorator`, and passes the v1 input through `run_tests_from_stream`.

## Control Flow

The conversion relies on the v1 parser in `ProtocolTestCase`/`TestProtocolServer`, which emits extended result events. `ExtendedToStreamDecorator` maps those events into v2 `status` calls, and `StreamResultToBytes` serializes them.

## State and Persistence Behavior

This is a pure streaming transformation from input to stdout. It persists no state and exits 0 after conversion.

## Dependencies and Integration Points

It depends on `testtools.ExtendedToStreamDecorator`, `subunit.StreamResultToBytes`, and shared filter helpers. It is paired with `subunit_2to1.py` for protocol migration.

## Risks and Test Signals

Fidelity risks include v1 features that do not map perfectly to v2 stream status packets. Regression tests should round-trip representative v1 streams with details, tags, time, progress, and passthrough text.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_1to2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_2to1.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_2to1.py

## Purpose

`subunit_2to1.py` converts subunit v2 input into the older v1 textual protocol.

## Important APIs, Types, and Functions

`main()` constructs `ByteStreamToStreamResult` for input, `TestProtocolClient(sys.stdout)` for v1 output, wraps it with `StreamToExtendedDecorator`, and uses `StreamResultRouter` to send global non-test file packets to `CatFiles(sys.stdout)`.

## Control Flow

The v2 parser emits stream events. `StreamToExtendedDecorator` translates test events to extended result calls, which `TestProtocolClient` serializes as v1 directives. Router rules divert events with `test_id=None` to `CatFiles` so global attachments become raw stdout content.

## State and Persistence Behavior

This is a streaming stdout transformation and persists no files. The output is byte-oriented even though it is passed through `sys.stdout`.

## Dependencies and Integration Points

It depends on `testtools.StreamResultRouter`, `StreamToExtendedDecorator`, `subunit.ByteStreamToStreamResult`, `TestProtocolClient`, shared `find_stream`, and `CatFiles`.

## Risks and Test Signals

The v2 protocol can represent global attachments and richer stream status than v1; conversion may lose metadata. A practical test is converting v2 streams with successful, failing, skipped, tagged, and global stdout events and reparsing the result with `ProtocolTestCase`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_2to1.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_filter.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_filter.py

## Purpose

`subunit_filter.py` filters subunit v2 streams by outcome, tags, regular expressions, expected-failure lists, and optional test id renaming.

## Important APIs, Types, and Functions

`make_options()` defines filtering flags: include/exclude errors, failures, successes, skips, xfails, passthrough behavior, tag filters, `--with`/`--without` regex filters, `--fixup-expected-failures`, `--only-genuine-failures`, and `--rename`. `_make_regexp_filter()` builds a predicate over test id, outcome, error, and details. `_compile_rename()` returns chained `re.sub` renaming. `_make_result()` creates a `TestResultFilter` wrapped through extended/stream decorators to emit v2. `main()` combines regexp and tag predicates and calls `filter_by_result`.

## Control Flow

The command parses options, builds predicate functions, reads expected-failure ids with `read_test_list`, and streams input through the v2 filter path. `TestResultFilter` decides per-test whether buffered start/tags/outcome/stop calls should be forwarded. Passthrough defaults to forwarding non-subunit input as v2 stdout packets unless disabled.

## State and Persistence Behavior

State is in filter predicates, expected-failure sets, and `TestResultFilter` buffering for the current test. No persistent files are written unless stdout is redirected by the caller.

## Dependencies and Integration Points

It depends on `re`, `optparse`, `testtools` stream decorators, `subunit.StreamResultToBytes`, shared `filter_by_result` and `find_stream`, and `subunit.test_results` filter helpers. It is the CLI front-end for the result filtering classes.

## Risks and Test Signals

Regex filters concatenate stringified test, outcome, error, and details, so filtering can match implementation-specific detail text. `--rename` mutates test objects by replacing their `id` method. `test_subunit_filter.py` covers default success stripping, tag filtering, no-passthrough, passthrough, expected-failure fixups, renames, preserved time ordering, and command execution through `python -m`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_filter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_ls.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_ls.py

## Purpose

`subunit_ls.py` lists test ids from a subunit v2 stream, optionally showing timing data and `exists` declarations.

## Important APIs, Types, and Functions

`main()` parses `--times` and `--exists`, constructs a `TestIdPrintingResult`, routes global attachment packets to `CatFiles(sys.stdout)`, and runs `ByteStreamToStreamResult` over stdin or a named input file. It also uses `StreamSummary` to compute the exit status from stream outcomes.

## Control Flow

`CopyStreamResult` sends events to both the printing result and summary result. `StreamResultRouter` routes `test_id=None` packets to `CatFiles` and all other packets to the copy result. After parsing, `result.stopTestRun()` flushes active tests and `summary.wasSuccessful()` determines exit status.

## State and Persistence Behavior

State is in `TestIdPrintingResult` active tests/durations and `StreamSummary` counters. Output is textual test ids on stdout. No files are persisted.

## Dependencies and Integration Points

It depends on `testtools.CopyStreamResult`, `StreamResultRouter`, `StreamSummary`, `subunit.ByteStreamToStreamResult`, `find_stream`, `CatFiles`, and `TestIdPrintingResult`.

## Risks and Test Signals

Timing depends on timestamp packets; missing timestamps can yield zero or `None`-derived durations depending on path. The command should be validated with `exists`, `inprogress`/final status pairs, failed status exit codes, and global stdout packets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_ls.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_notify.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_notify.py

## Purpose

`subunit_notify.py` sends a desktop notification summarizing a subunit run.

## Important APIs, Types, and Functions

`notify_of_result(result)` initializes `Notify`, chooses a success or failure summary from `result.wasSuccessful()`, formats stats with `result.formatStats()`, and shows a notification. `main()` runs the shared filter script using `StreamToExtendedDecorator(TestResultStats(stream))` and the notification hook.

## Control Flow

Input is parsed through shared filter plumbing. `TestResultStats` collects totals and tags. After the run, `run_filter_script` calls `notify_of_result`, then exits based on test success.

## State and Persistence Behavior

State is in memory and in the desktop notification service. The stats text is also written to the configured stream by `TestResultStats.formatStats`.

## Dependencies and Integration Points

It depends on PyGObject `gi.repository.Notify`, `testtools.StreamToExtendedDecorator`, `subunit.TestResultStats`, and `run_filter_script`. It integrates subunit results with desktop notification daemons.

## Risks and Test Signals

Importing `gi`/`Notify` can fail in headless or minimal environments. Notification display is side-effectful and not directly tested in this subset. Smoke validation should use a small passing and failing stream on a desktop session and check exit codes when notification services are unavailable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_notify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_output.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_output.py

## Purpose

`subunit_output.py` is the console/module wrapper for `_output.output_main`.

## Important APIs, Types, and Functions

`main()` returns `output_main()`. The executable block exits with that return code.

## Control Flow

All argument parsing and stream generation are delegated to `subunit._output`.

## State and Persistence Behavior

This wrapper creates no state. `_output` writes the generated v2 stream to stdout.

## Dependencies and Integration Points

It integrates packaging entry points and `python -m subunit.filter_scripts.subunit_output` with the implementation in `_output.py`.

## Risks and Test Signals

Wrapper risk is minimal. `test_output_filter.py` validates the delegated implementation; packaging validation should confirm the console script resolves to this wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_output.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_stats.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_stats.py

## Purpose

`subunit_stats.py` prints aggregate statistics for a subunit stream.

## Important APIs, Types, and Functions

`main()` calls `run_filter_script` with `StreamToExtendedDecorator(TestResultStats(stream))` and a `print_stats` post-run hook that calls `result.decorated.formatStats()`.

## Control Flow

The shared filter runner parses the stream, updates `TestResultStats`, invokes `print_stats`, unwraps to a result with `wasSuccessful` if needed, and exits 0 for no failures or 1 for failures.

## State and Persistence Behavior

`TestResultStats` keeps counters and a set of seen tags in memory. Output is a short text summary; no files are persisted unless redirected.

## Dependencies and Integration Points

It depends on `testtools.StreamToExtendedDecorator`, `subunit.TestResultStats`, and `run_filter_script`.

## Risks and Test Signals

The post-run hook assumes the result has a `.decorated` layer because of the stream adapter. `test_subunit_stats.py` validates empty streams, mixed pass/fail/error/skip/xfail streams, tag accounting, and exact formatted output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_tags.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_tags.py

## Purpose

`subunit_tags.py` applies tag additions or removals to every test event in a subunit v2 stream.

## Important APIs, Types, and Functions

`main()` calls `subunit.tag_stream(sys.stdin, sys.stdout, sys.argv[1:])`. Tags are expressed as `TAG` to add or `-TAG` to remove.

## Control Flow

The command delegates all parsing and rewriting to `tag_stream`, which reads v2 packets and rewrites `test_tags` before serializing them to stdout.

## State and Persistence Behavior

State is limited to the tag set transformation in `tag_stream`. It writes a transformed stream to stdout and persists no files.

## Dependencies and Integration Points

It depends on the public `subunit.tag_stream` helper. It is useful in pipelines where CI wants to annotate or strip tags without re-running tests.

## Risks and Test Signals

Risk is mostly stream mode: stdin/stdout must be binary-safe through `tag_stream`. `test_subunit_tags.py` validates both adding and removing tags while preserving the rest of the v2 stream.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_tags.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/tap2subunit.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/tap2subunit.py

## Purpose

`tap2subunit.py` is the command wrapper that converts TAP text from stdin into subunit output.

## Important APIs, Types, and Functions

`main()` calls `TAP2SubUnit(sys.stdin, sys.stdout)`. The executable block exits with that return code.

## Control Flow

All TAP parsing and subunit generation happen in `subunit.TAP2SubUnit`. This wrapper only wires standard streams to the converter.

## State and Persistence Behavior

No wrapper state is persisted. The converter writes subunit v2 bytes to stdout.

## Dependencies and Integration Points

It depends on the public `TAP2SubUnit` helper. It integrates TAP-emitting test programs with subunit pipelines.

## Risks and Test Signals

The wrapper assumes stdout is suitable for byte output even though it passes `sys.stdout`. `test_tap2subunit.py` heavily validates the converter's behavior for TAP plans, skip/TODO directives, comments, bailouts, missing tests, trailing plans, and unnamed tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/tap2subunit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filters.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filters.py

## Purpose

`filters.py` contains shared plumbing for command-line subunit filters: common options, input stream selection, protocol-version dispatch, passthrough routing, and result-based filtering.

## Important APIs, Types, and Functions

`make_options(description)` defines `--no-passthrough`, `--output-to`, and `--forward`. `run_tests_from_stream()` consumes v1 or v2 input and drives a result object. `filter_by_result()` wires input, passthrough, forwarding, output selection, and a result factory. `run_filter_script()` implements the standard CLI lifecycle and exit-code policy. `find_stream(stdin, argv)` returns stdin or opens exactly one binary file.

## Control Flow

For protocol v1, `run_tests_from_stream` constructs `ProtocolTestCase` with passthrough and forward streams. For protocol v2, it builds a `ByteStreamToStreamResult`, optionally wraps output forwarding with `StreamResultToBytes`, `CopyStreamResult`, or `StreamResultRouter`, and optionally routes non-test packets through `CatFiles` or a v2 serializer. All paths call `result.startTestRun()`, run the test case, and call `result.stopTestRun()`.

`filter_by_result` chooses passthrough behavior from boolean flags and protocol version, opens output if requested, runs the stream, and closes the output file. `run_filter_script` parses common options and exits 0 if the final result is successful.

## State and Persistence Behavior

The module is mostly stateless. It opens input/output files and writes transformed streams or reports. It may drop, unwrap, or forward non-subunit input depending on flags.

## Dependencies and Integration Points

It depends on `testtools.CopyStreamResult`, `StreamResult`, `StreamResultRouter`, public subunit v1/v2 adapters, `DiscardStream`, and `CatFiles`. Nearly every `filter_scripts` module uses this shared layer.

## Risks and Test Signals

Forwarding subunit while also transforming can double-report if used incorrectly; the docstring warns not to set `forward_stream` when transforming. v1 and v2 passthrough semantics differ. `test_filters.py` validates `read_test_list` interaction and `find_stream`; `test_subunit_filter.py` validates command passthrough behavior over v2 streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filters.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/progress_model.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/progress_model.py

## Purpose

`progress_model.py` models nested progress directives from subunit streams and provides an aggregate position/width suitable for UIs.

## Important APIs, Types, and Functions

`ProgressModel` exposes `adjust_width(offset)`, `advance()`, `push()`, `pop()`, `set_width(width)`, `pos()`, and `width()`. Internal `_tasks` entries are mutable lists containing current position, width, and the overall position/width at push time.

## Control Flow

Construction pushes an initial task with unknown width. Top-level `advance` and width adjustments update the current task directly. `push` creates a nested subtask preserving overall progress. `pos()` and `width()` scale the saved outer progress by the nested width when nested tasks exist; if current nested width is zero, scaling uses one to preserve overall progress.

## State and Persistence Behavior

All state is in `_tasks`. There is no persistence or external I/O. `pop()` removes the current task without underflow checks.

## Dependencies and Integration Points

The module has no imports. `subunit2gtk.py` uses it to turn protocol progress events into a GTK progress bar.

## Risks and Test Signals

Risks are arithmetic edge cases around zero widths, nested scaling, and popping too far. `test_progress_model.py` covers initial `0/0`, advancing unknown totals, setting and adjusting widths, push/pop behavior, and nested scaling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/progress_model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/run.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/run.py

## Purpose

`run.py` implements `python -m subunit.run`, a `unittest`/`testtools` runner that reports test enumeration and execution as subunit v2.

## Important APIs, Types, and Functions

`SubunitTestRunner` accepts runner options and writes to `stream` or `stdout`. `run(test)` lists tests, emits `exists` statuses, wraps the stream result with `ExtendedToStreamDecorator` and `AutoTimingTestResultDecorator`, then runs the test. `list(test, loader=None)` emits test ids and import errors. `_list(test)` uses `testtools.run.list_test` and `StreamResultToBytes`. `SubunitTestProgram` customizes usage text. `main(argv=None, stdout=None)` wires `TestProgram` to `SubunitTestRunner`.

## Control Flow

`main` optionally reopens stdout unbuffered for CLI use, then constructs a `TestProgram` with `exit=False` so normal test failures do not raise `SystemExit`. The runner enumerates test ids before execution, giving downstream consumers an `exists` inventory, then runs the suite with timing decoration. Loader/listing errors are emitted as unrunnable file status packets and exit 2.

## State and Persistence Behavior

State is held in the stream result and runner options. The module writes binary subunit packets to stdout/stream and persists no files.

## Dependencies and Integration Points

It depends on `testtools.run`, `testtools.ExtendedToStreamDecorator`, `subunit.StreamResultToBytes`, and `AutoTimingTestResultDecorator`. It is the main Python test execution integration point for subunit.

## Risks and Test Signals

Stream handling is subtle: `_list` reopens file descriptors in binary unbuffered mode when possible, and `main` rewrites `sys.stdout`. `test_run.py` verifies timing output, pre-run `exists` statuses, loader errors, non-exit behavior for failing tests, and `SystemExit` behavior for execution errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/test_results.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/test_results.py

## Purpose

`test_results.py` provides reusable `TestResult` and `StreamResult` helpers for timing, tag collapsing, filtering, listing, per-test callbacks, CSV output, and attachment passthrough.

## Important APIs, Types, and Functions

`TestResultDecorator` forwards extended result calls while degrading through `testtools.ExtendedToOriginalDecorator`. `HookedTestResultDecorator` adds `_before_event` hooks. `AutoTimingTestResultDecorator` injects timestamps unless explicit time events are seen. `TagsMixin`, `TagCollapsingDecorator`, and `TimeCollapsingDecorator` coalesce tag/time events.

`make_tag_filter()` and `and_predicates()` build predicates. `_PredicateFilter` buffers current-test events until it knows whether a test passes the predicate. `TestResultFilter` builds outcome predicates, expected-failure fixups, and optional id renaming. `TestIdPrintingResult` prints test ids and optional durations from result or stream events. `TestByTestResult` calls an `on_test` callback with status, times, tags, and details at stop. `CsvResult` writes rows from that callback. `CatFiles` is a `StreamResult` that writes file attachment bytes to a stream.

## Control Flow

Decorators forward most calls directly. Hooked decorators call `_before_event` before non-time/progress events. `_PredicateFilter.startTest` begins buffering; outcome calls either buffer or mark the test filtered; `stopTest` replays buffered calls to a decorated result only if the test was not filtered. `TestResultFilter` first applies renames and expected-failure transformations, then delegates to `_PredicateFilter`.

`TestIdPrintingResult.status` supports v2 stream events: `exists` can be printed when requested, `inprogress` starts duration tracking, and final statuses print the id and duration. `TestByTestResult` stores outcome details and calls the callback when `stopTest` arrives.

## State and Persistence Behavior

All state is per-result in memory: tags, buffered calls, active tests, durations, counters, start/stop timestamps, and details. Output classes write text rows or raw bytes to supplied streams. No files are opened here.

## Dependencies and Integration Points

It depends on `csv`, `datetime`, `iso8601`, `testtools`, `TracebackContent`, `text_content`, and public `subunit.make_stream_binary`. It is used by filter scripts, `subunit.run`, stats/listing commands, and passthrough routing.

## Risks and Test Signals

Important risks include preserving event ordering when filtering, not leaking per-test tags globally, handling explicit versus automatic time, mutating `test.id` during renames, and byte/text stream mismatches in `CsvResult` or `CatFiles`. There are small suspicious duplications, such as `TestIdPrintingResult.addError` incrementing `failed_tests` twice. Tests in this subset cover filters, stats, tags, CSV indirectly, listing indirectly, and time ordering through `test_subunit_filter.py`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/test_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/__init__.py

## Purpose

`subunit/tests/__init__.py` assembles the package's test suite from individual test modules.

## Important APIs, Types, and Functions

`test_suite()` creates a `unittest.TestLoader`, loads tests from a fixed tuple of imported modules, and passes the resulting suite through `testscenarios.generate_scenarios`.

## Control Flow

Importing the package imports many test modules up front. Calling `test_suite` loads all tests from those modules and expands scenario-based tests before returning the suite.

## State and Persistence Behavior

No files or persistent state are created. The function returns an in-memory suite object.

## Dependencies and Integration Points

It depends on `unittest.TestLoader`, `testscenarios.generate_scenarios`, and all listed `subunit.tests.test_*` modules, including protocol tests outside this worker subset. `subunit.__init__.py:test_suite()` delegates here.

## Risks and Test Signals

Eager imports mean optional or platform-sensitive test dependencies can fail before selection. A useful validation signal is running `python -m testtools.run subunit.tests.test_suite` or the package's configured test runner after installing test dependencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-script.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-script.py

## Purpose

`sample-script.py` is a tiny executable fixture used by protocol/exec tests to emit deterministic subunit v1-style output.

## Important APIs, Types, and Functions

The script imports `sys` and writes fixed lines to `sys.stdout`: one successful test, one failing test with bracketed details, and one error test with bracketed details.

## Control Flow

Execution is linear. It emits `test`, `success`, `failure [`, detail lines, `]`, then another `test` and `error [` block. There are no functions or CLI arguments.

## State and Persistence Behavior

The script writes only stdout and maintains no state.

## Dependencies and Integration Points

It integrates with `ExecTestCase` and parser tests that need an external command producing subunit. Because it writes strings, callers must account for text-to-byte conversion depending on Python runtime.

## Risks and Test Signals

The fixture is intentionally static. The main risk is execution permissions or stdout text mode in tests expecting bytes. Validation is that parser tests consume its output and produce the expected success, failure, and error events.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-script.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-two-script.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-two-script.py

## Purpose

`sample-two-script.py` is a second minimal external fixture for tests that need a separate subunit-emitting script.

## Important APIs, Types, and Functions

The script imports `sys` and writes a single successful subunit v1 test named `sample two`.

## Control Flow

Execution writes `test sample two` followed by `success sample two` to stdout. There are no functions or arguments.

## State and Persistence Behavior

No state is retained and no files are written.

## Dependencies and Integration Points

It is an integration fixture for external script execution paths, especially `ExecTestCase`-style tests.

## Risks and Test Signals

Risk is limited to executable discovery and stdout encoding. A passing integration test should observe exactly one successful remoted test from this script.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/sample-two-script.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_chunked.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_chunked.py

## Purpose

`test_chunked.py` verifies the HTTP-style chunked encoder/decoder used for multipart subunit details.

## Important APIs, Types, and Functions

`TestDecode` sets up a `BytesIO` output and `subunit.chunked.Decoder`. It tests close behavior, short/incomplete data, empty streams, combined writes, residue after terminal chunk, hex lengths, long 65,536-byte ranges, strict and non-strict newline handling, and malformed headers. `TestEncode` sets up `Encoder` and tests empty output, short buffering, hex length serialization, and large-write boundaries.

## Control Flow

Each test writes specific byte fragments and asserts either decoded output, returned residue, or `ValueError`. Encoder tests write bytes, close the encoder, and compare the exact serialized byte stream.

## State and Persistence Behavior

State is isolated per test in `BytesIO`. No filesystem state is used.

## Dependencies and Integration Points

It depends on `unittest`, `io.BytesIO`, `testtools.compat._b`, and `subunit.chunked`. It protects the detail parsing/serialization path used by `details.py` and `TestProtocolClient`.

## Risks and Test Signals

This file is the primary regression signal for chunk framing. It is especially useful for preventing Windows newline regressions, EOF handling mistakes, and accidental changes to the 65,536-byte flush threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_chunked.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_details.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_details.py

## Purpose

`test_details.py` validates simple and multipart detail parsers for subunit v1 outcomes.

## Important APIs, Types, and Functions

`TestSimpleDetails` covers line accumulation, escaped closing bracket handling, empty message retrieval, default traceback content creation, skip reason content, and success message content. `TestMultipartDetails` checks that multipart messages have no simple message, start with empty details, and parse a content type/name/chunk body into a named `Content` object.

## Control Flow

Tests instantiate parsers directly, feed byte lines, then compare content keys, content types, and joined bytes from `iter_bytes()`.

## State and Persistence Behavior

All parser state is in memory. No persistent files are involved.

## Dependencies and Integration Points

It depends on `unittest`, `testtools.compat._b`, and public `subunit.content`, `content_type`, and `details`. It guards the parser behavior invoked by `_ReadingDetails` states.

## Risks and Test Signals

The tests confirm expected content naming and escaping but do not cover malformed multipart headers beyond what implementation raises. They are strong smoke signals for preserving compatibility with v1 detail serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_details.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_filter_to_disk.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_filter_to_disk.py

## Purpose

`test_filter_to_disk.py` smoke-tests exporting a subunit v2 stream to disk.

## Important APIs, Types, and Functions

`SmokeTest.test_smoke` creates a temporary output directory, builds an in-memory v2 stream with `StreamResultToBytes`, writes a successful tagged test with attachment `fred`, runs `_to_disk.to_disk(['-d', output], stdin=stdin, stdout=stdout)`, and asserts file contents.

## Control Flow

The test constructs input, rewinds it, invokes the exporter, then checks `foo/test.json` and `foo/fred`.

## State and Persistence Behavior

It creates temporary filesystem state through `fixtures.TempDir`. The expected output is a JSON metadata file and an attachment file.

## Dependencies and Integration Points

It depends on `fixtures.TempDir`, `testtools.TestCase`, `FileContains`, `subunit._to_disk`, and `subunit.v2.StreamResultToBytes`. It validates `_to_disk` and the `subunit2disk` command's core implementation.

## Risks and Test Signals

The test covers the happy path only. It does not exercise path traversal, duplicate ids, multiple attachments, timestamps, or malformed input. Still, it is a direct signal that the exporter can consume v2 and write the documented disk layout.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_filter_to_disk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_filters.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_filters.py

## Purpose

`test_filters.py` tests small shared helpers used by filter commands.

## Important APIs, Types, and Functions

`TestReadTestList.test_read_list` verifies `read_test_list` strips full-line and trailing comments while preserving test ids. `TestFindStream` verifies `find_stream` returns stdin when no filename is supplied and opens a named binary file when one is supplied.

## Control Flow

Tests use `NamedTemporaryFile` for temporary input data, call the helper, and compare returned data or stream contents.

## State and Persistence Behavior

Only temporary files are used. No persistent state remains.

## Dependencies and Integration Points

It depends on `testtools.TestCase`, `tempfile.NamedTemporaryFile`, `subunit.read_test_list`, and `subunit.filters.find_stream`. These helpers support `subunit_filter`, conversion scripts, and other CLI filters.

## Risks and Test Signals

The tests do not cover too many filenames, missing files, or whitespace-only comments, but they cover the standard helper contracts used by command-line parsing paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_filters.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_output_filter.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_output_filter.py

## Purpose

`test_output_filter.py` extensively tests `_output.py`, the generator for synthetic subunit v2 status and attachment packets.

## Important APIs, Types, and Functions

`SafeOptionParser` prevents parser exits during tests. `safe_parse_arguments` wraps `_output.parse_arguments`. `TestStatusArgParserTests` runs as scenarios over every action in `_ALL_ACTIONS`. `ArgParserTests` covers invalid option combinations and tag parsing. `StatusStreamResultTests` checks generated status events for commands with and without attachments. `FileDataTests` covers attachment-only packets. `MatchesStatusCall` is a custom matcher for `StreamResult` double event tuples.

## Control Flow

Tests parse CLI-like argument lists, run `generate_stream_results` into `testtools.testresult.doubles.StreamResult`, and match the resulting `_events`. Several tests patch `_o.create_timestamp`, `_o._CHUNK_SIZE`, and `_o.sys.stdin` to make output deterministic and exercise chunking/stdin paths.

## State and Persistence Behavior

State is in temporary files, in-memory byte streams, and patched module variables. No persistent files are written.

## Dependencies and Integration Points

It depends on `iso8601.UTC`, `testtools` matchers, `NamedTemporaryFile`, `BytesIO`, `TextIOWrapper`, and `_output` internals. It is the main test signal for `filter_scripts/subunit_output.py`.

## Risks and Test Signals

This file strongly protects CLI parsing and stream generation. It verifies one-status-only enforcement, status ids, tags, timestamps, binary attachments, empty files, stdin filenames, chunk-size behavior, metadata only on first packet, and final statuses only on the last attachment packet. It is less focused on actual byte serialization because it uses a stream-result double rather than `StreamResultToBytes`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_output_filter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_progress_model.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_progress_model.py

## Purpose

`test_progress_model.py` validates the nested arithmetic of `ProgressModel`.

## Important APIs, Types, and Functions

`TestProgressModel.assertProgressSummary` checks `pos()` and `width()`. Individual tests cover initial unknown progress, advancing with unknown width, setting and adjusting width, preserving position, push/pop behavior, and nested subtask scaling.

## Control Flow

Each test creates a fresh model, performs a short sequence of progress operations, and asserts the resulting aggregate position and total.

## State and Persistence Behavior

All state is in the `ProgressModel` instance. There is no I/O.

## Dependencies and Integration Points

It depends on `unittest` and `subunit.progress_model.ProgressModel`. It indirectly protects GTK progress display behavior.

## Risks and Test Signals

The test suite captures the intended semantics for zero-width tasks and nested progress scaling. It does not cover invalid `pop()` underflow or negative widths beyond adjustment back to zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_progress_model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_run.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_run.py

## Purpose

`test_run.py` tests the `subunit.run` test runner integration.

## Important APIs, Types, and Functions

`TestSubunitTestRunner` verifies `SubunitTestRunner.run`, `.list`, and `run.main`. It defines nested `FailingTest` and `ExitingTest` fixtures for CLI behavior. Tests use `PlaceHolder`, `StreamResult`, and `ByteStreamToStreamResult` to inspect emitted v2 packets.

## Control Flow

Runner tests execute placeholder suites into `BytesIO`, decode the output stream, and assert timestamp and `exists` events. Listing error tests patch `run.list_test` or provide a loader with errors and assert `SystemExit(2)`. CLI tests call `run.main` with specific argv and stdout wrappers.

## State and Persistence Behavior

State is in in-memory streams and patched functions. No files are written.

## Dependencies and Integration Points

It depends on `testtools`, `unittest`, public `subunit.ByteStreamToStreamResult`, and `subunit.run`. It validates integration between testtools listing, stream result serialization, auto timing, and CLI exit policy.

## Risks and Test Signals

The tests assert that normal test failures do not cause `run.main` to exit, while execution errors can. They also check the v2 stream magic prefix. They do not cover buffering flags or `tb_locals`, but they exercise the runner's most important behavioral contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_filter.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_filter.py

## Purpose

`test_subunit_filter.py` validates both the `TestResultFilter` class and the `subunit.filter_scripts.subunit_filter` command.

## Important APIs, Types, and Functions

`TestTestResultFilter` uses a sample v1 subunit stream containing global/local tags, pass, fail, error with details, skip, and xfail. It tests default success filtering, tag filters, per-test tag scope, excluding each outcome type, expected-failure fixups, unexpected success fixup, custom predicates with old and new signatures, time ordering, skip preservation, and id renaming. `TestFilterCommand` executes `python -m subunit.filter_scripts.subunit_filter` as a subprocess and decodes v2 output.

## Control Flow

Class-level helper `run_tests` feeds bytes through `ProtocolTestCase` into a result filter. Command tests build v2 streams with `StreamResultToBytes`, run the module subprocess with stdin/stdout pipes, and decode output with `ByteStreamToStreamResult`.

## State and Persistence Behavior

State is in in-memory streams and subprocess execution. No persistent files are used.

## Dependencies and Integration Points

It depends on `subprocess`, `sys.executable`, `unittest`, `iso8601`, `testtools` doubles, public subunit stream adapters, and `TestResultFilter`/`make_tag_filter`. It directly covers the CLI filter and shared result filtering logic.

## Risks and Test Signals

This is a high-value regression suite for preserving filtered stream semantics. It specifically protects time passthrough for filtered tests, tag scoping, passthrough encoding of non-subunit input, and command default behavior. The subprocess tests also validate module importability and packaging layout.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_filter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_stats.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_stats.py

## Purpose

`test_subunit_stats.py` tests `TestResultStats`, the result object used by stats and notification commands.

## Important APIs, Types, and Functions

`TestTestResultStats` sets up `StringIO` output, a `TestResultStats`, a `BytesIO` input stream, and `ProtocolTestCase`. It tests empty streams, mixed outcome streams, tag accumulation, and exact `formatStats()` output.

## Control Flow

`setUpUsedStream` writes a v1 subunit stream with global and local tags plus passed, failed, errored, skipped, and xfail tests, rewinds it, and runs through `ProtocolTestCase`.

## State and Persistence Behavior

All state is in memory: streams and result counters. No files are persisted.

## Dependencies and Integration Points

It depends on `unittest`, `BytesIO`, `StringIO`, `testtools.compat._b`, and public `subunit`. It validates `TestResultStats` for `subunit_stats.py` and `subunit_notify.py`.

## Risks and Test Signals

The tests confirm xfail counts as passed for stats purposes because only errors/failures increment failed and skips increment skipped. They also confirm seen tags are accumulated from tag events. Exact formatting checks protect command output stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_tags.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_tags.py

## Purpose

`test_subunit_tags.py` verifies `subunit.tag_stream`, which adds or removes tags from v2 status packets.

## Important APIs, Types, and Functions

`TestSubUnitTags` creates `BytesIO` original and filtered streams. `test_add_tag` writes inprogress and success packets with tags, applies `["quux"]`, and compares against several acceptable byte encodings because tag set order can vary. `test_remove_tag` writes tags including `bar`, applies `["-bar"]`, and compares against a reference stream without `bar`.

## Control Flow

Tests serialize v2 packets with `StreamResultToBytes`, rewind input, invoke `tag_stream`, and compare resulting bytes.

## State and Persistence Behavior

Only in-memory streams are used. No files are persisted.

## Dependencies and Integration Points

It depends on `testtools`, `Contains` matcher, public `subunit`, and `subunit.test_results` importability. It covers the implementation used by `filter_scripts/subunit_tags.py`.

## Risks and Test Signals

The add-tag test accounts for non-deterministic set ordering in serialized bytes. These tests strongly protect binary stream fidelity for tag transformations but do not cover global non-test attachments or empty tag sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_subunit_tags.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_tap2subunit.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_tap2subunit.py

## Purpose

`test_tap2subunit.py` validates TAP-to-subunit conversion for many TAP plan, outcome, directive, comment, and missing-test cases.

## Important APIs, Types, and Functions

`TestTAP2SubUnit` uses `StringIO` TAP input and `BytesIO` subunit output. Each test writes TAP text, calls `subunit.TAP2SubUnit`, and checks decoded v2 events through `ByteStreamToStreamResult`. `UTF8_TEXT` documents the expected text attachment MIME type.

## Control Flow

The tests cover whole-file skip plans (`1..0`), unnamed and numbered `ok` tests, descriptions, `SKIP`/`skip` directives with comments, `TODO` directives mapped to xfail, bailouts mapped to fail, missing tests from plans or skipped numbers, trailing plans, no-plan streams, leading/trailing comments attached as `tap comment`, and mixed TODO/SKIP behavior.

## State and Persistence Behavior

State is in in-memory streams. No persistent files are used.

## Dependencies and Integration Points

It depends on `testtools.TestCase`, `testtools.compat._u`, `StreamResult` double, and public `subunit.TAP2SubUnit`. It directly protects `filter_scripts/tap2subunit.py`.

## Risks and Test Signals

This is the main compatibility signal for TAP conversion. It verifies exact event tuples including test ids, statuses, runnable flags, attachment names, bytes, EOF, MIME type, and timestamp absence. It does not cover all TAP dialect extensions, but it covers the package's supported grammar well.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_tap2subunit.py -->
