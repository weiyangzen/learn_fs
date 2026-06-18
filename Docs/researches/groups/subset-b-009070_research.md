# subset-b-009070 research

Grouped research report for WiredTiger packing tests, Python test harness utilities, readonly/salvage tests, timestamp simulator components, and Python suite helper mixins. Each file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/packing-test.c -->
# sources/storage-engines/wiredtiger/test/packing/packing-test.c

Purpose: small C smoke test for WiredTiger's internal struct packing helpers. It exercises valid and invalid packing format strings and prints the resulting byte sequences for human/debug visibility.

Important APIs and control flow: `check()` first calls `__wt_struct_sizev` to compute the packed length for a varargs format, validates that it fits a 200-byte local buffer, then calls `__wt_struct_packv` and prints bytes as hexadecimal. `main()` initializes test utility state with `testutil_set_progname()` and `__wt_library_init()`, then checks `iii`, `3i`, `iS`, `s`, and `.s` formats and asserts `>s`, `<s`, and `@s` return `EINVAL`.

State and persistence behavior: the program creates no WiredTiger home and writes no database state. State is limited to stack buffers, varargs traversal, and stdout output.

Dependencies and integration points: depends on `test_util.h`, internal `__wt_struct_sizev`/`__wt_struct_packv`, `WT_TRET`, `WT_RET`, and the library initialization path needed for internal data references. It is run by the packing smoke script.

Risks: it tests only a narrow set of formats and relies on internal WiredTiger functions, so ABI/config changes can break it outside public API compatibility. The varargs list must be restarted between size and pack calls, which the test handles explicitly.

Test signals: successful process exit validates valid formats and invalid-format rejection; printed hex output is useful for diagnosing packing layout drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/packing-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/smoke.sh -->
# sources/storage-engines/wiredtiger/test/packing/smoke.sh

Purpose: shell smoke driver for the packing test directory. It runs a small representative subset during check rather than every performance-oriented packing test.

Important APIs and control flow: `set -e` makes any failing command abort the script. The script invokes `$TEST_WRAPPER ./packing-test`, `$TEST_WRAPPER ./intpack-test3`, and `$TEST_WRAPPER ./int4bpack-test`.

State and persistence behavior: no persistent state is created by the script itself. It delegates all state to the executed test binaries.

Dependencies and integration points: depends on the build system producing the named executables and on `TEST_WRAPPER` being set by the test environment, commonly to inject sanitizer, timeout, or platform wrappers.

Risks: failures are coarse-grained because the script does not annotate which subtest failed beyond shell output. It intentionally excludes some directory tests, so broader packing regressions require dedicated test execution.

Test signals: a zero exit status from all three binaries is the check signal for packing smoke coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_install/testbase.py -->
# sources/storage-engines/wiredtiger/test/py_install/testbase.py

Purpose: installation sanity test for the Python `wiredtiger` package after `pip install wiredtiger`. It verifies that the extension imports, opens a home, performs basic table operations, and exposes version information.

Important APIs and control flow: imports `wiredtiger_open` and `wiredtiger_version`, recreates `WTPY_TEST`, opens a connection with `create`, creates `table:foo` with string keys and integer values, writes three records through a cursor mapping interface, verifies key `B` returns `200`, closes handles, prints the version, and reports success.

State and persistence behavior: deletes and recreates local directory `WTPY_TEST`, then persists a small WiredTiger table there. It does not clean up after success, leaving the home for inspection.

Dependencies and integration points: depends on the installed Python package and its native library resolution, not the local test path setup utilities. This is useful for packaging/installation validation.

Risks: uses a fixed relative directory name, so concurrent runs in one working directory can collide. It only checks a minimal cursor path and will not catch most optional-package issues.

Test signals: failure raises an exception on incorrect lookup; success prints `testbase success.` and the WiredTiger version tuple/string.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_install/testbase.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_install/testpack.py -->
# sources/storage-engines/wiredtiger/test/py_install/testpack.py

Purpose: installation sanity test for the Python packing-only API. It validates that `wiredtiger.packing.unpack` and `pack` are importable and produce expected binary/int conversions.

Important APIs and control flow: builds bytes from a fixed hexadecimal string, unpacks it with format `iiiiiiiiiiiiii`, compares the resulting integer list to a hard-coded expected sequence, packs four integers with format `iiii`, and compares the exact byte string to `b'\x81\x82\x83\x84'`.

State and persistence behavior: no database or filesystem state is used. All validation is in process memory.

Dependencies and integration points: depends on `wiredtiger.packing` from the installed Python package. It intentionally avoids `wiredtiger_open` and therefore isolates packing module installation from full database runtime setup.

Risks: hard-coded byte encodings are sensitive to packing format semantics; if the encoding changes intentionally, this test must be updated. It retains Python 2/3 compatibility style around byte construction although modern runs are likely Python 3.

Test signals: exceptions indicate exact pack/unpack mismatch; success prints `testpack success.`
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_install/testpack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/abstract_test_case.py -->
# sources/storage-engines/wiredtiger/test/py_utility/abstract_test_case.py

Purpose: shared base harness for WiredTiger Python tests independent of a specific suite. It centralizes result output, stdout/stderr capture, test directory setup, deterministic random seeds, test identity formatting, known-failure helpers, and debugger/TTY support.

Important APIs and control flow: `TeeFile` mirrors writes to a capture file and optionally the original stream. `CapturedFd` tracks expected offsets in captured stdout/stderr and provides validators such as `check`, `checkAdditional`, `checkAdditionalPattern`, and `checkCustomValidator`. `AbstractWiredTigerTestCase` extends `unittest.TestCase`; setup methods initialize test directories and line-buffered result files, while `fdSetUp`/`fdTearDown` replace Python streams with tee captures. `failed()` adapts to several `unittest` outcome internals across Python versions.

State and persistence behavior: class-level state stores parent test directory, original streams, result file, random seeds, verbosity, preserved-file flags, and print-once markers. Per-test state stores capture file offsets and ignore regexes. It writes `results.txt`, `stdout.txt`, and `stderr.txt` under the configured test directory.

Dependencies and integration points: depends on `unittest`, file descriptors, `/dev/tty` for debug paths, and higher-level WiredTiger test cases that call `setupTestDir`, `setupIO`, `fdSetUp`, and `fdTearDown`. `suite_random` consumes the exported `getseed()`.

Risks: direct stream/file-descriptor manipulation is process-global and can be fragile under concurrent tests. `prout` writes through a duplicated stdout descriptor and expects it to remain valid. Captured output checks must keep ignore patterns current for expected verbose WiredTiger output.

Test signals: downstream tests rely on this harness to fail on unexpected stdout/stderr, preserve scenario names, emit PID-tagged logs, and report failure state correctly during teardown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/abstract_test_case.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/suite_random.py -->
# sources/storage-engines/wiredtiger/test/py_utility/suite_random.py

Purpose: deterministic pseudo-random generator for WiredTiger Python test scenarios without global random-module state.

Important APIs and control flow: `suite_random.__init__` accepts zero, one, or two seeds. With no explicit seed it pulls `seedw, seedz` from `abstract_test_case.getseed()`. `rand32()` implements Marsaglia multiply-with-carry updates for two 32-bit seeds and returns a combined 32-bit value. `rand_range(n, m)` bounds the value to `[n, m)`, and `rand_float()` maps the 32-bit integer to `[0, 1)`.

State and persistence behavior: state is only `self.seedw` and `self.seedz`. If either seed is zero, `rand32()` refreshes both from the global test seed source.

Dependencies and integration points: imported by `wtscenario.py` for probabilistic scenario pruning and by any tests needing reproducible randomness.

Risks: `rand32()` calculates updates from local `w`/`z` captured before zero-seed refresh, so a call that starts with a zero seed refreshes object fields but still computes the returned value from the old local values. The generator is deterministic, not suitable for security randomness.

Test signals: repeatable scenario selection under fixed `AbstractWiredTigerTestCase.setupRandom()` seeds is the main validation signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/suite_random.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/test_result.py -->
# sources/storage-engines/wiredtiger/test/py_utility/test_result.py

Purpose: custom `unittest` text result that prefixes verbose output and error lists with process IDs, including child process IDs conveyed through test tags.

Important APIs and control flow: `PidAwareTextTestResult` subclasses `unittest.TextTestResult`. The constructor initializes a thread-local prefix with the current PID. `tags()` detects new tags like `pid:<child>` and updates the prefix to `[pid:parent/child]: `. `startTest()` writes the prefix before delegating to the superclass. `getDescription()` returns `test.shortDescription()`, and `printErrorList()` writes separator lines plus PID-prefixed errors.

State and persistence behavior: state is per-result and per-thread through `threading.local()`. It writes only to the configured unittest stream.

Dependencies and integration points: integrates with test runners that emit tags, especially parallel/concurrent test execution where child PID attribution matters.

Risks: prefix state is thread-local but tag interpretation assumes `pid:` tags arrive before output that needs the child prefix. `shortDescription()` may be `None` for tests without descriptions, so stream rendering depends on `str(None)` behavior.

Test signals: verbose test output should show consistent PID prefixes, and failures/errors should be attributable to the correct child process.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/test_result.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/test_util.py -->
# sources/storage-engines/wiredtiger/test/py_utility/test_util.py

Purpose: bootstraps Python import/library paths for WiredTiger tests so they use the local build tree and bundled third-party test dependencies.

Important APIs and control flow: `get_dist_top_dir()` walks from this file to the distribution root. `find_build_dir()` prefers `WT_BUILDDIR`, then current directory, dist top, and dist top `build`, accepting directories that contain `wt` or `wt.exe`. `setup_wiredtiger_path()` inserts `<build>/lang/python` ahead of installed packages and appends `.libs` to `LD_LIBRARY_PATH` and `DYLD_LIBRARY_PATH` when present. `setup_3rdparty_paths()` scans `test/3rdparty` children for `lib`, `python`, or root package directories. `setup_paths()` runs both setup phases.

State and persistence behavior: mutates `sys.path` and process environment variables. It exits the process if no usable build directory is found.

Dependencies and integration points: imported early by Python test runners before importing `wiredtiger`, `wttest`, or bundled dependencies. It integrates with both in-tree and explicit build-dir workflows.

Risks: build-dir detection can pick the wrong build when multiple builds exist. Path separator logic uses `:`, which is POSIX-oriented. It does not validate ABI compatibility between the Python extension and libraries discovered via environment path.

Test signals: successful import of local `wiredtiger` and third-party modules after `setup_paths()` is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/test_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/wtscenario.py -->
# sources/storage-engines/wiredtiger/test/py_utility/wtscenario.py

Purpose: scenario-generation utilities for WiredTiger Python tests, including cross products, probabilistic pruning, long-run filtering, numbering, and page-size scenario generation.

Important APIs and control flow: `powerrange()` yields multiplicative ranges including the stop value. `make_scenarios()` multiplies scenario lists, applies optional include/prune/prunelong rules, and numbers them. `multiply_scenarios()` creates cross products, merges dictionaries, multiplies `P` probabilities when both sides provide them, and suppresses `long_only` combinations unless long runs are enabled. `prune_scenarios()` either filters by probability or chooses a bounded count using `suite_random`. `number_scenarios()` mutates dictionaries with `scenario_name` and `scenario_number`. `wtscenario.session_create_scenario()` generates combinations of page size/cache settings and exposes `shortName()`/`configString()`.

State and persistence behavior: module-level `_is_long_run` gates long-only scenarios. Scenario dictionaries are mutated in place during numbering and temporary pruning metadata insertion/removal.

Dependencies and integration points: depends on `suite_random` and is consumed by many Python test classes through a `scenarios` class variable. Generated config strings feed `session.create`.

Risks: duplicate names assert at runtime. In-place dictionary mutation can surprise callers sharing scenario dictionaries. `log2chr()` uses `/`, producing floats in Python 3 during repeated division, though comparisons and integer-like values still produce character offsets only if coerced safely by `chr` inputs.

Test signals: runners should list unique, numbered scenario names and execute deterministic subsets under fixed seeds and long-run settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/py_utility/wtscenario.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/readonly/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/readonly/CMakeLists.txt

Purpose: build and register the readonly C test.

Important APIs and control flow: `create_test_executable(test_readonly SOURCES readonly.c EXECUTABLE_NAME "t" ADDITIONAL_FILES smoke.sh)` builds `readonly.c` as executable `t` and stages the smoke script. `add_test` runs the script from the binary directory. `set_tests_properties` labels the test `check`.

State and persistence behavior: CMake writes build-system metadata and the test executable. Runtime state is created by `readonly.c` and `smoke.sh`.

Dependencies and integration points: depends on the repository's `create_test_executable` helper and CTest. The short executable name is matched by `smoke.sh`.

Risks: if the executable name changes, the smoke script must change too. The test is POSIX-heavy, so platform gating must happen outside this file if required.

Test signals: `ctest -L check` should run `test_readonly` via `smoke.sh`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/readonly/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/readonly/readonly.c -->
# sources/storage-engines/wiredtiger/test/readonly/readonly.c

Purpose: integration test for WiredTiger readonly connection semantics, lock-file behavior, read/write reopen restrictions, and data visibility from read-only homes.

Important APIs and control flow: parent mode creates a table `table:main`, inserts `MAX_KV` large values, copies the home into writable/no-lock and chmod-readonly variants, then opens four parent connections and invokes fresh child processes with `-R` or `-W`. Child mode calls `open_dbs()`, which runs `run_child()` against each directory with expected success or failure. `run_child()` opens with readonly or writable config, scans the table, and asserts exactly `MAX_KV` rows.

State and persistence behavior: creates `WT_RD`, `WT_RD.WRNOLOCK`, `WT_RD.RD`, and `WT_RD.RDNOLOCK`, copies database files, removes selected `WiredTiger.lock` files, changes permissions to read-only, and restores permissions for cleanup. WiredTiger state includes logs, statistics, statistics log output, and the table data.

Dependencies and integration points: depends on `test_util.h`, POSIX `system`, `chmod`, process exit status macros, file-copy helpers, and WiredTiger open/session/cursor APIs. `smoke.sh` wraps it and installs a chmod cleanup trap.

Risks: permission behavior is platform and filesystem dependent. Child execution uses `system()` and command string formatting, so paths with shell-sensitive characters would be risky. The test expects several WiredTiger error messages and must not treat them as failures.

Test signals: child process exit status validates each scenario; row-count scans validate read visibility; final output prints `Readonly test successful`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/readonly/readonly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/readonly/smoke.sh -->
# sources/storage-engines/wiredtiger/test/readonly/smoke.sh

Purpose: smoke runner for the readonly test executable.

Important APIs and control flow: installs a trap that restores user write permission on `WT_*` paths for normal exit and common signals, enables `set -e`, and runs `$TEST_WRAPPER ./t`.

State and persistence behavior: the script itself mutates permissions during cleanup only. Runtime database directories are created by `./t`.

Dependencies and integration points: depends on POSIX shell, `chmod`, the test executable named `t`, and the test harness-provided `TEST_WRAPPER`.

Risks: the broad `chmod -R u+w WT_*` pattern can affect unrelated matching directories in the working directory. It assumes a shell/glob environment compatible with the test layout.

Test signals: zero exit status from `./t` and cleanup trap execution are the expected smoke signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/readonly/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/salvage/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/salvage/CMakeLists.txt

Purpose: build and register the salvage C test with CTest.

Important APIs and control flow: `create_test_executable(test_salvage SOURCES salvage.c)` builds the executable. `add_test(NAME test_salvage COMMAND test_salvage)` registers it directly. `set_tests_properties(... LABELS "check")` includes it in check smoke runs.

State and persistence behavior: build metadata and executable are produced by CMake. Runtime creates and destroys `WT_TEST` files.

Dependencies and integration points: depends on the repository CMake test helper and CTest. It does not stage a wrapper script.

Risks: the direct command assumes the executable is discoverable in the CTest working context established by the helper macro.

Test signals: `ctest -R test_salvage` or `ctest -L check` should execute the compiled program successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/salvage/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/salvage/salvage.c -->
# sources/storage-engines/wiredtiger/test/salvage/salvage.c

Purpose: synthetic file-level salvage test for row-store and variable column-store pages. It builds controlled page fragments with chosen record ranges and write generations, runs WiredTiger salvage/verify/dump, and compares the dump to expected results.

Important APIs and control flow: `main()` parses `-r`, `-t var|row`, and `-v`, then runs `t()` for unique and non-unique values. `run()` contains 24 scenarios covering empty files, sequential pages, overlapping duplicate ranges, prefixes, suffixes, middle overlaps, and column-store missing ranges. `build()` creates a one-page `file:__slvg.load` with configured key/value formats and fixed page sizes. `copy()` appends the file description and modified page image to `__slvg.prep`, rewriting `WT_PAGE_HEADER.recno`, `write_gen`, and block checksum. `process()` copies prep to salvage file, runs `session->salvage`, `verify`, dumps through a `dump=print` cursor, and compares output with `__slvg.result`.

State and persistence behavior: recreates `WT_TEST` for every run and creates `__slvg.load`, `__slvg.prep`, `__slvg.slvg`, `__slvg.dump`, and `__slvg.result`. Logging is disabled because the test mutates WiredTiger files directly and must avoid recovery rewriting the synthetic state.

Dependencies and integration points: depends on internal page header/block structures, checksum helpers, `__wt_page_type_string`, endian swaps, and public salvage/verify/cursor APIs. The output comparison uses `cmp`.

Risks: highly coupled to WiredTiger on-disk page layout, block header checksum rules, and page size assumptions. Direct file manipulation can fail if layout or allocation behavior changes. Some scenarios are meaningful only for column store.

Test signals: for each scenario, salvage plus verify must succeed and `cmp __slvg.dump __slvg.result` must pass for both unique and non-unique values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/salvage/salvage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/simulator/CMakeLists.txt

Purpose: top-level CMake entry for simulator tests.

Important APIs and control flow: contains a single `add_subdirectory(timestamp)` call that delegates all simulator build work to the timestamp subtree.

State and persistence behavior: no runtime state. It contributes CMake graph structure only.

Dependencies and integration points: integrated by the parent test CMake tree and depends on the `timestamp` directory existing.

Risks: currently only timestamp simulator is represented; adding more simulator domains requires explicit subdirectories here.

Test signals: configure should descend into `test/simulator/timestamp` and create its library/executable targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/CMakeLists.txt

Purpose: builds the shared timestamp simulator library and delegates front-end executable targets.

Important APIs and control flow: `add_library(timestamp_simulator SHARED ...)` compiles `connection_simulator.cpp`, `session_simulator.cpp`, and `timestamp_manager.cpp`. It exposes `src/include`, compiles as C++17, applies diagnostic flags, then adds `call_log_manager` and `simulator_interface` subdirectories.

State and persistence behavior: produces a shared library artifact; no runtime state is handled in CMake.

Dependencies and integration points: downstream executables link to `timestamp_simulator`. The target depends on repository diagnostic flag variables and compiler support for C++17.

Risks: simulator headers are public to consumers, so include path and ABI changes affect both frontends. A shared library is produced even though the tools are test utilities, which can matter for runtime library lookup.

Test signals: successful build of `timestamp_simulator`, `call_log_manager`, and `simulator_interface` validates the CMake integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/CMakeLists.txt

Purpose: builds the call-log replay frontend for the timestamp simulator.

Important APIs and control flow: `add_executable(call_log_manager call_log_manager.cpp)` creates the tool. Include directories expose the local directory and `test/3rdparty` for `nlohmann/json.hpp`. The executable links to `timestamp_simulator`, optionally links `wt::voidstar` when `ENABLE_ANTITHESIS` is set, and applies C++ diagnostic flags.

State and persistence behavior: produces an executable artifact. Runtime reads an external call-log file but CMake manages no state.

Dependencies and integration points: depends on the simulator library and bundled JSON library. Optional Antithesis integration is through `wt::voidstar`.

Risks: missing third-party JSON include path or shared-library runtime path will break the executable. Optional linking must stay aligned with Antithesis build configuration.

Test signals: the target should compile and link; a valid call log should replay through the built executable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.cpp -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.cpp

Purpose: command-line replay tool that consumes a WiredTiger API call log in JSON-entry form and drives the in-memory timestamp simulator, asserting simulated return values and queried timestamps match logged expectations.

Important APIs and control flow: the constructor reads the file, strips trailing newlines/commas, wraps entries in `[...]`, parses JSON, obtains the connection singleton, and initializes `_api_map`. Each `call_log_*` method extracts fields from a log entry, normalizes `"(null)"` configs, dispatches to `connection_simulator` or `session_simulator`, asserts the simulator return equals `return.return_val`, and throws on non-zero returns. `process_call_log_entry()` switches on `method_name` for begin/commit/prepare/rollback, session open/close, set/query timestamp, and `timestamp_transaction_uint`.

State and persistence behavior: maintains `_session_map` from logged session IDs to simulator session pointers and mutates the singleton connection/session timestamp state. It reads but does not write files.

Dependencies and integration points: depends on `nlohmann::json`, `call_log_manager.h`, `connection_simulator`, and exact call-log schema keys such as `method_name`, `class_name`, `session_id`, `input`, `output`, and `return`.

Risks: several thrown expressions are string concatenations from string literals and may not be caught by `catch (std::string&)` as intended. `assert` checks disappear in release builds, reducing mismatch detection. Unknown `method_name` uses `_api_map.at` and can throw outside the switch-specific handling.

Test signals: successful replay with no assertion failure validates simulator agreement with the call log; query timestamp entries additionally compare returned hex timestamps when supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.h -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.h

Purpose: declares the call-log replay manager and its mapping from logged WiredTiger API method names to simulator method handlers.

Important APIs and control flow: `enum class api_method` enumerates supported call-log methods. `call_log_manager` exposes a constructor taking a call-log file path and `process_call_log()`. Private helpers set up `_api_map`, retrieve sessions by logged ID, and implement one handler per supported method.

State and persistence behavior: owns a raw pointer to the connection singleton, parsed JSON call log, method-name map, and session-ID-to-session-pointer map. Session lifetime is controlled by forwarding open/close operations to `connection_simulator`.

Dependencies and integration points: includes `connection_simulator.h` and `nlohmann/json.hpp`. It is consumed only by the call-log executable.

Risks: raw session pointers require `_session_map` to stay synchronized with connection lifetime. The header uses `using json = nlohmann::json` globally, which leaks an alias to includers.

Test signals: compile-time coverage of all declared handlers and replay coverage for each enum value show schema/API alignment.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/CMakeLists.txt

Purpose: builds the interactive timestamp simulator CLI frontend.

Important APIs and control flow: `add_executable(simulator_interface simulator_interface.cpp)` creates the tool, includes the local source directory, links `timestamp_simulator`, optionally links `wt::voidstar` under `ENABLE_ANTITHESIS`, and applies diagnostic flags.

State and persistence behavior: CMake produces the executable; runtime state is in the simulator library and process stdin/stdout.

Dependencies and integration points: depends on the timestamp simulator shared library and optional Antithesis target.

Risks: because this is an interactive executable, automated test coverage may only compile it unless explicit scripted input is provided.

Test signals: successful compile/link and manual or scripted CLI interactions that exercise timestamp rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.cpp -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.cpp

Purpose: interactive console frontend for the timestamp simulator. It lets a user create/use sessions, set/query connection timestamps, begin/commit/prepare/rollback transactions, set transaction timestamps, query session timestamps, and print rule summaries.

Important APIs and control flow: helper functions print colored bordered messages, list numbered options, parse numeric choices from stdin, collect free-form input, and retrieve sessions from a map. `interface_session_management()` lists sessions, switches active session, or opens a new one. Connection-level functions build `set_timestamp` and `query_timestamp` configs. Session-level functions incrementally build config strings then execute simulator methods. `main()` creates a connection singleton, opens `Session1`, maintains `session_map` and `session_in_use`, and loops over the main menu until exit.

State and persistence behavior: process state includes the simulator singleton, session map, active session name, and in-progress config strings. No files or databases are written.

Dependencies and integration points: includes `simulator_interface.h` and uses `connection_simulator`/`session_simulator`. Output uses ANSI color constants declared in the header.

Risks: input validation only bounds parsed integers; nonnumeric input can reuse an uninitialized `choice` value if extraction fails. Config string assembly appends commas after each selected option, relying on the parser to ignore empty tokens. Session close is not exposed, so created sessions live until process exit.

Test signals: manual runs should show expected success/error messages for timestamp rule examples and query paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.h -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.h

Purpose: declaration header for the interactive timestamp simulator CLI.

Important APIs and control flow: declares ANSI color macros, generic CLI helpers (`choose_num`, `print_border_msg`, `print_options`, `get_input`, `get_session`), session-management entry point, connection-level timestamp operations, session-level transaction operations, and `print_rules()`.

State and persistence behavior: the header stores no state. Declared functions operate on `connection_simulator*`, `session_simulator*`, and a caller-owned session map.

Dependencies and integration points: includes STL containers/strings and `connection_simulator.h`; consumed by `simulator_interface.cpp`.

Risks: color macros are global preprocessor definitions and can collide with other code if reused more widely. Function declarations expose raw session pointers consistent with the simulator library.

Test signals: compile coverage ensures the frontend and simulator library APIs remain aligned.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/connection_simulator.cpp -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/connection_simulator.cpp

Purpose: implements the connection-level timestamp simulator singleton, global timestamp state, session ownership, and connection `set_timestamp`/`query_timestamp` semantics.

Important APIs and control flow: `get_connection()` returns a static singleton. `open_session()` allocates a new `session_simulator` and stores it in `_session_list`; `close_session()` finds, erases, and deletes it. `query_timestamp()` parses `get=...`, supports `all_durable`, `oldest`, and `stable`, returns success-but-unsupported for several WiredTiger query types, and computes `all_durable` by considering global durable timestamp plus active session commit/durable timestamps. `set_timestamp()` parses `oldest_timestamp`, `stable_timestamp`, `durable_timestamp`, and `force`, validates through `timestamp_manager`, then updates global fields.

State and persistence behavior: process-local singleton state includes `_session_list`, `_oldest_ts`, `_stable_ts`, and `_durable_ts`. There is no durable storage; destructor deletes remaining sessions.

Dependencies and integration points: depends on `session_simulator`, `timestamp_manager`, `error_simulator` macros, STL maps/vectors, and simulator frontends.

Risks: raw owning pointers require correct close/destructor paths. `all_durable` decrements a durable timestamp before comparison, so zero values must be avoided. The simulator intentionally supports only a subset of WiredTiger timestamp query/config options.

Test signals: call-log replay and CLI queries should match expected hex timestamps and validation failures for supported connection-level operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/connection_simulator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/connection_simulator.h -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/connection_simulator.h

Purpose: declares the singleton connection simulator API and global timestamp/session state.

Important APIs and control flow: public methods expose `get_connection`, session open/close, `set_timestamp`, global durable setter/getters, oldest/stable presence checks, latest active read timestamp, and `query_timestamp`. Private `decode_timestamp_config_map()` extracts parsed set-timestamp fields. Copy and assignment are deleted.

State and persistence behavior: private members are a vector of owned `session_simulator*` plus oldest, stable, and durable timestamps. State is process-local and reset only by process restart.

Dependencies and integration points: includes `session_simulator.h` and is included by frontends and session/timestamp validation code.

Risks: singleton design makes tests order-dependent if multiple replay/interface operations run in one process. Raw pointer ownership is visible through the API and requires clients not to delete sessions directly.

Test signals: compile and replay coverage of all getters/setters and session lifecycle calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/connection_simulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/error_simulator.h -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/error_simulator.h

Purpose: small error/return macro header for the timestamp simulator, mirroring common WiredTiger-style early-return patterns.

Important APIs and control flow: `WT_SIM_RET` and `WT_SIM_RET_MSG` evaluate an expression and return nonzero errors, optionally printing a message. `WT_TXN_SIM_RET` and `WT_TXN_SIM_RET_MSG` additionally set `_txn_error = true` before returning, intended for methods inside `session_simulator`. The header defines `EINVAL` as 22.

State and persistence behavior: macros do not own state, but transaction variants mutate the caller's `_txn_error` member.

Dependencies and integration points: assumes `std::cerr` is available where message macros are used and that transaction macros are expanded in a class scope with `_txn_error`.

Risks: macro hygiene is limited; transaction macros are not safe outside `session_simulator`. Defining `EINVAL` can conflict with system errno headers if included together.

Test signals: validation failures should return 22 and, for transaction timestamp errors, cause later commit to roll back.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/error_simulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/session_simulator.h -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/session_simulator.h

Purpose: declares the session-level transaction timestamp simulator API and per-transaction state.

Important APIs and control flow: public API methods mirror WiredTiger session operations: `begin_transaction`, `rollback_transaction`, `prepare_transaction`, `commit_transaction`, `timestamp_transaction`, `timestamp_transaction_uint`, and `query_timestamp`. Accessors expose commit, durable, first commit, prepare, and read timestamps plus flags for prepared/running/rounding states. Private setters and config decoding enforce validation through `timestamp_manager`.

State and persistence behavior: per-session state tracks whether a transaction is running/prepared, whether commit/durable/read timestamps are set, rounding flags, transaction error flag, and timestamp values. `reset_txn_level_var()` resets all transaction-level state.

Dependencies and integration points: used by `connection_simulator`, `timestamp_manager`, and both frontends. Copy and assignment are deleted so sessions are owned by connection.

Risks: all state is single-threaded and mutable; concurrent use would need synchronization. The boolean/timestamp split must remain consistent for query and validation behavior.

Test signals: replayed call logs should validate begin/prepare/commit/rollback sequencing and timestamp query values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/session_simulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/timestamp_manager.h -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/timestamp_manager.h

Purpose: declares the timestamp validation singleton used by connection and session simulators.

Important APIs and control flow: public helpers parse config strings into maps, convert between hex strings and decimal timestamps, validate hex strings, validate oldest/stable and connection durable timestamps, and validate read/commit/prepare/session durable timestamps. Private `trim()` supports config parsing. Copy and assignment are deleted.

State and persistence behavior: the manager itself stores no timestamp state; it reads state from `connection_simulator` and `session_simulator` during validation.

Dependencies and integration points: included by simulator source files and depends on `session_simulator.h`.

Risks: singleton is mostly stateless but creates tight coupling to the connection singleton during validation. Config parsing supports only simple comma-separated `key=value` tokens and not full WiredTiger nested config grammar.

Test signals: validation error paths should return `EINVAL` and print descriptive messages through simulator macros.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/timestamp_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/session_simulator.cpp -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/session_simulator.cpp

Purpose: implements session transaction lifecycle and transaction timestamp semantics for the in-memory simulator.

Important APIs and control flow: `begin_transaction()` rejects already-running transactions, resets state, parses read timestamp and rounding config, sets read timestamp, then marks the transaction running. `timestamp_transaction()` and `timestamp_transaction_uint()` set commit/durable/prepare/read timestamps after validation. `prepare_transaction()` requires a running transaction, a prepare timestamp, no prior commit timestamp, and marks the transaction prepared. `commit_transaction()` parses optional commit/durable timestamps, rolls back on earlier transaction errors, enforces prepared versus non-prepared requirements, updates global durable timestamp, and ends the transaction. `rollback_transaction()` clears running state. Query returns selected session timestamp as hex.

State and persistence behavior: all state is in session fields. Commit and durable setters maintain first commit timestamp, default durable-to-commit behavior, durable-set flag, and rounding behavior around prepare/read timestamps.

Dependencies and integration points: depends on `connection_simulator` for global timestamp state, `timestamp_manager` for validation and parsing, and `error_simulator` for return/error macros.

Risks: failed timestamp operations set `_txn_error`, causing the next commit to roll back; callers must understand this deferred behavior. Some unsupported WiredTiger config keys are silently ignored by being listed as unsupported. Prepared/non-prepared durable timestamp rules are simplified to simulator needs.

Test signals: call-log replay should match WiredTiger return codes for transaction timestamp operations and query timestamps for commit, first_commit, prepare, and read.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/session_simulator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/timestamp_manager.cpp -->
# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/timestamp_manager.cpp

Purpose: implements config parsing, timestamp conversion, and timestamp rule validation for the simulator.

Important APIs and control flow: `parse_config()` splits comma-separated tokens into a map, drops explicitly unsupported keys, and rejects keys not listed as supported. `validate_hex_value()` rejects strings longer than 16 hex digits, non-hex characters, and zero. `validate_oldest_and_stable_timestamp()` enforces monotonic oldest/stable movement and oldest <= stable. Session validators enforce read-before-prepare and single-read rules, commit monotonicity and oldest/stable/latest-read constraints, prepare ordering and stable/latest-read constraints, and durable requirements for prepared transactions.

State and persistence behavior: no internal persistent state. Validation reads current global state from `connection_simulator` and transaction state from passed sessions.

Dependencies and integration points: central rule engine for `connection_simulator::set_timestamp` and all session timestamp setters.

Risks: parser is intentionally simpler than WiredTiger config parsing and may mishandle nested configs beyond current use. `trim()` assumes nonempty strings with at least one non-space character. Stable timestamp validation requires new stable to be strictly greater than current stable, which should match intended simulator behavior.

Test signals: successful and failing call-log replay entries validate rule parity; manual CLI `print_rules()` text should stay synchronized with this implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/simulator/timestamp/src/timestamp_manager.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/checkpoint_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/checkpoint_util.py

Purpose: mixin/base class with checkpoint-specific helpers for Python suite tests.

Important APIs and control flow: `checkpoint_util` extends `wttest.WiredTigerTestCase`. `wait_for_checkpoint_start()` opens a `statistics:` cursor, polls `stat.conn.checkpoint_state`, and waits until it becomes nonzero, sleeping between attempts and asserting before a timeout expires.

State and persistence behavior: no persistent state beyond polling statistics. Uses the provided session or `self.session`.

Dependencies and integration points: depends on `wttest.open_cursor`, WiredTiger statistics cursors, and `wiredtiger.stat.conn.checkpoint_state`. Used by tests that need to coordinate with a running checkpoint.

Risks: polling interval and timeout balance flake detection against slow environments. If statistics are disabled or checkpoint state semantics change, the helper can false-fail.

Test signals: tests using the helper should fail quickly with a clear timeout if checkpoints never start.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/checkpoint_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/compact_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/compact_util.py

Purpose: shared base class for background and file compaction Python tests.

Important APIs and control flow: methods delete ranges, populate tables, truncate bounded cursor ranges, read compaction-related connection/data-source statistics, compute file sizes through statistics, count compacted files, and turn background compaction on/off while polling `background_compact_running`.

State and persistence behavior: mutates test tables through inserts/removes/truncate and mutates connection background compaction state via `session.compact(None, 'background=...')`. Reads statistics through short-lived cursors.

Dependencies and integration points: extends `wttest.WiredTigerTestCase`, imports `wiredtiger.stat`, and expects tests to create compatible URIs/key formats. It integrates with WiredTiger background compaction statistics.

Risks: polling loops lack explicit timeout in `turn_on_bg_compact`/`turn_off_bg_compact`, so a stuck state can hang until the outer test timeout. `populate()` loops `range(start_key, num_keys)`, treating `num_keys` as an exclusive stop rather than a count.

Test signals: stats such as bytes recovered, pages rewritten, files skipped, and background running/success counters drive assertions in compaction tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/compact_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/error_info_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/error_info_util.py

Purpose: tiny assertion helper for tests of WiredTiger's last-error reporting.

Important APIs and control flow: `error_info_util` extends `wttest.WiredTigerTestCase`. `assert_error_equal()` calls `self.session.get_last_error()` and compares the top-level error, sub-level error, and message to expected values.

State and persistence behavior: reads per-session last-error state only; no filesystem/database mutation.

Dependencies and integration points: depends on the Python WiredTiger session binding exposing `get_last_error()`. Used by `test_error_info` style tests.

Risks: exact error message comparison is brittle across wording changes and localization-like edits. It assumes the session object is the one that observed the relevant error.

Test signals: all three returned fields must match expected values exactly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/error_info_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/eviction_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/eviction_util.py

Purpose: shared helper class for Python eviction tests, especially tests needing page eviction and time-window cleanup.

Important APIs and control flow: `evict_cursor_tw_cleanup()` opens a debug session with `release_evict_page=true`, begins an `ignore_prepare=true` transaction, scans keys with periodic cursor resets to trigger page release/eviction, then rolls back and closes. `get_stat()` reads a statistics cursor. `populate()` writes timestamped values in individual transactions, committing at `timestamp_str(k + 1)`.

State and persistence behavior: writes records to target URIs and uses debug session settings to influence eviction behavior. Reads connection/data-source statistics.

Dependencies and integration points: extends `wttest.WiredTigerTestCase`, uses WiredTiger debug cursor/session config, statistics cursors, and timestamp helpers from the test base.

Risks: debug eviction behavior is internal and may change. The helper assumes integer keys from `0` to `nrows - 1` and that the URI supports those keys.

Test signals: expected eviction/stat counters and absence/presence of time-window cleanup effects after forced eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/eviction_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/helper.py

Purpose: general Python suite helper functions for file/table comparison, URI existence checks, WiredTiger home copying, crash-restart simulation, statistics URI construction, and cursor context management.

Important APIs and control flow: `compare_files()` performs byte-for-byte size and buffer comparison. `compare_tables()` opens multiple cursors and checks value equality while scanning in lockstep. `confirm_does_not_exist`, `confirm_empty`, and `confirm_nonempty` assert URI visibility and backing-file patterns. `copy_wiredtiger_home()` copies a home while skipping lock/temp log files and can use unaligned `dd`. `simulate_crash_restart()` copies an open home, closes the old connection, and reopens on the copy. `WiredTigerCursor` implements `with` support around `session.open_cursor`.

State and persistence behavior: can create/copy/remove directories, copy WiredTiger files, run `dd`, close and reopen test connections, and leave copied homes for inspection.

Dependencies and integration points: depends on `wiredtiger`, `shutil`, `subprocess`, filesystem globbing, and `wttest`-style testcase methods. Many suite tests import these helpers directly.

Risks: `compare_tables()` compares cursor values rather than keys and can miss key divergence if values match. Unaligned copy uses `dd` and is unavailable on Windows. Copying a live home is a crash simulation, not a true power-loss test.

Test signals: helper assertions make absence/emptiness/comparison failures explicit in downstream tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper_disagg.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/helper_disagg.py

Purpose: helper library for disaggregated-storage Python tests. It provides scenario generation, connection/extension config, leader/follower checkpoint manipulation, oplog-style workload generation/checking, and palite page-log corruption utilities.

Important APIs and control flow: top-level helpers generate disaggregated scenarios from test variables, ignore expected RTS output, and compute palite shard IDs. `disagg_test_class` decorates test classes to mix in `DisaggConfigMixin`, create follower/kv_home directories, load page-log extensions, and add `disaggregated=(page_log=...)` config. `DisaggConfigMixin` builds configs, loads extensions, gets complete checkpoint metadata, advances follower checkpoints, switches leader/follower roles, reopens/restarts without local files, and saves old files. `Oplog` generates timestamped inserts/updates/removes, applies them to sessions, and checks point reads plus scans. `DisaggCorruptionMixin` uses built `sqlite3` to inspect/mutate palite `pages_NN.db` rows.

State and persistence behavior: creates `follower`, `kv_home`, `SAVE.N` directories, symlinks, page-log SQLite files, and WiredTiger data files. It mutates connection roles and checkpoint metadata. Corruption helpers directly update/delete palite page rows while the WT connection is closed.

Dependencies and integration points: depends on `wttest`, `wiredtiger`, `run.wt_builddir`, page-log extension APIs (`get_page_log`, `pl_get_complete_checkpoint`), subprocess `sqlite3`, and palite schema/flag constants.

Risks: tightly coupled to palite internals, SQLite file layout, shard count 17, and `WT_PAGE_LOG_DISCARDED`. Role switching and corruption require careful open/closed connection ordering. Decorator-generated classes preserve names but can obscure MRO and setup behavior.

Test signals: follower checkpoint advancement, leader/follower switch tests, oplog consistency checks at timestamps, and expected failures after injected corruption validate this helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper_disagg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper_layered_fast_truncate.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/helper_layered_fast_truncate.py

Purpose: shared helper mixin for layered fast truncate tests on disaggregated/layered tables.

Important APIs and control flow: utility functions concatenate iterables and create inclusive ranges. `LayeredFastTruncateConfigMixin` builds table create config, opens auto-closing cursors, populates keys in one transaction, sets up leader and follower roles, truncates bounded or whole URI ranges in transactions, scans visible keys forward/backward, searches keys or `search_near`, performs leader checkpoints with stable/oldest timestamps, steps up a follower, opens an additional follower connection, searches at a read timestamp, evicts key ranges, and reads statistics.

State and persistence behavior: creates layered/disaggregated tables, writes rows, checkpoints, reopens/switches disaggregated connections, truncates ranges, evicts pages, and opens follower homes.

Dependencies and integration points: assumes the test class provides `self.uri`, `self.session`, transaction context manager, disaggregated helper methods, timestamp formatting, and extension config. Uses `wiredtiger.WT_NOTFOUND`.

Risks: tightly bound to layered table/disaggregated test infrastructure. `open_follower()` uses fixed home name `follower`, which can collide if tests share working directories. Eviction uses debug cursor config and fixed read timestamp 10.

Test signals: visible key lists, `key_exists`, `search_near_key`, timestamped reads, follower advancement, and statistics reads support assertions around fast truncate correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper_layered_fast_truncate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper_tiered.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/helper_tiered.py

Purpose: helper module for tiered storage test scenarios and connection/extension configuration.

Important APIs and control flow: top-level functions supply storage-source auth tokens, bucket names, connection config strings, shared-tiered config strings, row-check helper `get_check`, and scenario lists from `gen_tiered_storage_sources()`. `TieredConfigMixin` detects tiered/shared scenarios, builds `conn_config`, creates local bucket directories, appends `tiered_storage=(...)` config, loads storage source extensions with optional config, and marks extensions skip-if-missing for nonlocal or Windows environments.

State and persistence behavior: creates bucket directories under the test home for local `dir_store` scenarios. Connection configs enable tiered storage and statistics. The placeholder `download_objects()` does nothing by default.

Dependencies and integration points: depends on `wiredtiger`, `os`, test extension-list API, and scenario attributes such as `ss_name`, `bucket`, `bucket_prefix`, and `auth_token`.

Risks: only `dir_store` is configured in the scenario list. Some config-builder helpers return strings with open parentheses/trailing comma fragments intended to be composed by callers, so misuse can produce malformed config. Windows skips extension loading.

Test signals: tiered tests verify object movement/visibility using generated scenarios, bucket setup, and extension loading.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/helper_tiered.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/metadata_helper.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/metadata_helper.py

Purpose: helper functions for reading WiredTiger metadata table IDs from Python tests.

Important APIs and control flow: `extract_id()` uses a regular expression to extract `,id=<digits>` from a metadata configuration string. `get_table_id()` opens a `metadata:` cursor through `WiredTigerCursor`, searches for a URI, raises `KeyError` if absent, and returns the parsed integer ID.

State and persistence behavior: reads metadata only; no persistent mutation.

Dependencies and integration points: depends on `re` and `helper.WiredTigerCursor`. Used by tests that need a numeric table/file ID, including lower-level storage or disaggregated helpers.

Risks: regex assumes the metadata config contains `,id=` with decimal digits. If the metadata format changes or `id` appears at the beginning without a leading comma, parsing fails.

Test signals: callers can assert nonmissing IDs and use them to locate related storage artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/metadata_helper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/modify_utils.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/modify_utils.py

Purpose: utility functions for generating randomized old values, modify vectors, and expected new values for WiredTiger modify-operation tests.

Important APIs and control flow: `OpType` enumerates add/remove/replace operations. `create_value()` builds repeated random string or bytes patterns depending on value format `S` or `u`. `create_mods()` chooses sorted offsets, lengths, and operation types, synthesizes a new value from the old value, then calls `wiredtiger.wiredtiger_calc_modify()` to compute modify entries, retrying with a larger size budget if repeated data causes an error.

State and persistence behavior: no filesystem or database state. It consumes randomness from a caller-provided random object and returns `(oldv, mods, newv)`.

Dependencies and integration points: depends on Python `string`, `Enum`, and the WiredTiger Python binding's `wiredtiger_calc_modify`.

Risks: offset/length generation can skip modifications when offsets are too close, so requested `nmod` is an upper bound on intended edits. `rand.sample(range(maxdiff), nmod + 1)` requires `maxdiff >= nmod + 1`. Byte generation uses random choices from encoded ASCII.

Test signals: downstream tests apply returned modify vectors and compare stored values with `newv`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/modify_utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/prepare_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/prepare_util.py

Purpose: minimal base class for tests that need preserve-prepared and precise-checkpoint connection settings.

Important APIs and control flow: declares `test_prepare_preserve_prepare_base`, a `wttest.WiredTigerTestCase` subclass with class attribute `conn_config = 'precise_checkpoint=true,preserve_prepared=true,statistics=(all)'`.

State and persistence behavior: no methods or runtime state are added. The class-level config changes connection behavior for subclasses.

Dependencies and integration points: imported by prepare/checkpoint tests that subclass it to share a common connection configuration.

Risks: despite the class name starting with `test_`, it is a base class and could be collected accidentally by generic test discovery if not handled by the suite conventions. Config is fixed and may need extension by subclasses through inheritance patterns.

Test signals: subclasses should open connections with precise checkpointing, prepared update preservation, and statistics enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/prepare_util.py -->
