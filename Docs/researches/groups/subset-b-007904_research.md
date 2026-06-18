# Research Report: subset-b-007904

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_runner.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_runner.py

## Purpose
This Twisted Trial test module exercises Tahoe-LAFS command-line runner behavior around parsing, `bin/tahoe` subprocess execution, node creation, node runtime lifecycle, stdin-close handling, and pid-file locking. It is not an implementation module, but it is a high-value integration test for user-visible CLI contracts and process management.

## Important APIs, Types, And Functions
`get_root_from_file(src)` derives a project root from an installed module path, handling `site-packages` and source-layout cases. `run_bintahoe(extra_argv, python_options=None)` is the central subprocess helper: it runs `python -b -m allmydata.scripts.runner`, encodes argv through `unicode_to_argv`, captures stdout and stderr, decodes using the preferred locale, and returns `(out, err, returncode)`.

`ParseOrExitTests` validates non-ASCII parse errors through `run_cli_unicode`. `BinTahoe` validates direct runner invocation, Python interpreter option forwarding, and Eliot destination option parsing. `CreateNode` calls CLI creation commands via `run_cli` and `parse_cli` to verify node, client, and introducer directory creation. `RunNode` uses `CLINodeAPI`, `Expect`, and process stdout matching to exercise `tahoe run` for introducers and clients. `OnStdinCloseTests` targets `allmydata.scripts.tahoe_run.on_stdin_close` using `MemoryReactorClock`. `PidFileLocking` tests `allmydata.util.pid.check_pid_process`, `_pidfile_to_lockpath`, and `ProcessInTheWay`.

## Control Flow
The file mixes synchronous testtools matchers, `inlineCallbacks`, and Tahoe's Eliot-aware `inline_callbacks`. CLI creation tests build several command variants for each node kind: explicit `--basedir`, positional basedir, global `--node-directory`, unquiet output, duplicate-directory rejection, and usage-error paths. Runtime tests create nodes with `run_bintahoe`, mutate generated config when needed, spawn `tahoe run`, wait for startup text, poll for readiness files, stop the process, and restart to assert stable FURLs.

Bad-directory tests intentionally race two expected outputs: an error message and a possible normal startup line. A `DeferredList(..., fireOnOneCallback=True)` asserts the error arrives first and then waits for process completion to avoid dirty reactor state. Stdin-close tests simulate platform-specific reader shutdown: normal reactor readers on POSIX and explicit `writeConnectionLost`/`readConnectionLost` on Windows.

## State And Persistence Behavior
The tests create real filesystem node directories under `test_runner/...`. They assert persistent artifacts such as `tahoe.cfg`, `tahoe-client.tac`, `tahoe-introducer.tac`, `introducer.furl`, `storage.furl`, `twistd.pid`, and `node.url`. Important persistence contracts include storage being enabled for `create-node`, disabled for `create-client`, reserved space being written for storage nodes, stable introducer and storage FURLs across restarts, and pid-file removal after graceful POSIX shutdown.

`PidFileLocking` writes a small helper script and uses a child process to hold the lock corresponding to a pid file. This deliberately tests interprocess state rather than only same-process locking, because the lock library allows reentrant locking inside one process.

## Dependencies And Integration Points
The module depends on Twisted reactor/process APIs, `twisted.python.usage`, platform detection, `FilePath`, Tahoe CLI helpers (`run_cli`, `parse_cli`, `CLINodeAPI`), encoding utilities, file utilities, pid-file utilities, and Eliot logging. It also depends on real child-process invocation of the installed/source runner, so it verifies packaging and module-entry behavior beyond unit-level parser calls.

## Risks And Edge Cases
These tests are sensitive to platform behavior, especially Windows process termination and stdin simulation. They also rely on stdout text such as `client running` and `introducer running`, so changes in log wording can break tests without changing core behavior. Locale decoding in `run_bintahoe` can surface environment-dependent failures. Runtime tests may be slower and more fragile than pure unit tests because they spawn real processes and poll filesystem readiness.

## Test Signals
Passing tests indicate that non-ASCII CLI errors are preserved, global runner options are parsed correctly, Eliot destination validation rejects malformed inputs, node creation creates correct files and rejects invalid forms, `tahoe run` starts usable nodes and preserves FURLs across restarts, stdin close callbacks run and swallow callback exceptions, and pid-file locking detects another live process holding the lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_sftp.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_sftp.py

## Purpose
This module is a no-network integration test suite for Tahoe-LAFS SFTP frontend behavior, centered on `allmydata.frontends.sftpd.SFTPUserHandler` and the file-handle abstractions it exposes to Twisted Conch. It validates path parsing, directory listing, metadata, reading, writing, deletion, rename semantics, OpenSSH extensions, and shell/session behavior against an in-memory Tahoe grid.

## Important APIs, Types, And Functions
`Handler` combines `GridTestMixin`, `ShouldFailMixin`, `ReallyEqualMixin`, and `unittest.TestCase`. If Twisted Conch is unavailable, the whole class is skipped. `shouldFailWithSFTPError(expected_code, which, callable, *args, **kwargs)` wraps a callable with `defer.maybeDeferred`, expects `sftp.SFTPError`, and checks the exact SFTP status code. `_set_up` creates a one-client no-network grid, a root dirnode, reloads SFTP module state, and constructs `SFTPUserHandler`. `_set_up_tree` builds the reusable fixture: mutable file, readonly view, immutable files including a non-ASCII name, LIT directories, an unknown future URI, and a self-referential loop directory with fixed metadata.

Helper comparators `_compareDirLists` and `_compareAttributes` validate Conch-style directory entries and attrs dictionaries. The tests exercise `SFTPUserHandler` methods including `gotVersion`, `_path_from_string`, `realPath`, `openDirectory`, `getAttrs`, `setAttrs`, `openFile`, `removeFile`, `removeDirectory`, `renameFile`, `makeDirectory`, `extendedRequest`, and session adapter methods from `conch_interfaces.ISession`.

## Control Flow
Most tests build a Deferred callback chain. Setup creates the grid and tree, then each operation appends either a success assertion or an expected SFTP error assertion. Read tests open handles, call `readChunk` at normal, zero-length, near-EOF, EOF, and after-EOF offsets, inspect handle and handler attrs, verify write operations are denied on read-only handles, and assert closed handles reject further operations.

Write tests cover SFTP flag combinations in depth: invalid empty paths, `TRUNC` without existing files, `EXCL` without `CREAT`, writes to directories or unknown nodes, immutable directory denial, readonly mutable caps, direct URI writes, create/truncate/append behavior, sparse writes with NUL filling, resize via `setAttrs`, write-only read denial, idempotent close, replacing immutable files, writing mutable files in place, and changing parent links to readonly. They also test read/write handles, renaming links while handles are open, and a deliberate open/rename race using a delayed Deferred.

Removal and rename tests distinguish file removal from directory removal, allow unknown link removal, preserve open read handles after unlink, prevent deleted heisenfiles from being committed on close, reject ordinary rename over existing targets, and validate OpenSSH POSIX rename replacement semantics through `extendedRequest(b"posix-rename@openssh.com", ...)`. Session tests adapt the handler to `ISession`, verify `df -P -k /`, unsupported commands, shell rejection, CRLF endings, and process termination reasons. Extended-request tests validate `statvfs@openssh.com`, unsupported requests, and malformed POSIX rename payloads.

## State And Persistence Behavior
All persistent application state is inside the no-network Tahoe grid: dirnodes, mutable file versions, readonly caps, immutable file shares, metadata, and links. The SFTP layer also maintains transient heisenfile state for open write handles, tracked through `sftpd.all_heisenfiles` and `handler._heisenfiles`; most tests assert both are empty at the end. This is a key cleanup signal because open-write placeholder state must not leak across operations or tests.

Write behavior persists only on close for some handle types, but created placeholder links may be visible earlier. Tests intentionally remove or rename open handles to validate final commit behavior. Mutable writes preserve storage identity when using writable caps, while chmod-like permission changes can diminish parent links to readonly without changing storage index. Grid destruction via `nuke_from_orbit` verifies read and close failure paths when shares disappear.

## Dependencies And Integration Points
The module integrates Twisted Deferreds, Twisted Conch SFTP constants and interfaces, Tahoe no-network grid machinery, mutable publish data, immutable upload data, `download_to_data`, `IDirectoryNode`, Tahoe-specific exceptions (`ExistingChildError`, `NoSuchChildError`, `NotWriteableError`), and process-end marker classes (`ProcessDone`, `ProcessTerminated`). It is tightly coupled to `allmydata.frontends.sftpd` internal behavior, including `_reload`, `_convert_error`, global heisenfile bookkeeping, and request-extension encodings.

## Risks And Edge Cases
The suite encodes many user-visible compatibility decisions: invalid UTF-8 maps to `FX_NO_SUCH_FILE`, ordinary rename-over-existing maps to `FX_PERMISSION_DENIED` for sshfs compatibility, unsupported links/shells map to explicit SFTP failures, and `WRITE | TRUNC` without `CREAT` is accepted for POSIX interoperability despite SFTP spec tension. It is sensitive to exact SFTP status codes, directory-list text formatting, timezone-dependent date rendering, Twisted Conch availability, and race handling around open files.

## Test Signals
Passing tests signal that the SFTP frontend can safely expose Tahoe directories as SFTP paths, including Unicode names, cap-based `uri/` access, readonly and mutable capability boundaries, LIT directory handling, unknown-node protection, correct file-handle lifecycle, cleanup of transient write state, OpenSSH extension support, and robust conversion from Tahoe/Twisted failures into SFTP error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_sftp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_spans.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_spans.py

## Purpose
This module tests `allmydata.util.spans.Spans`, `overlap`, and `DataSpans`. These utilities model byte ranges and sparse byte data, so the tests focus on range algebra, containment, length accounting, chunk retrieval, mutation, copying, and randomized equivalence to simple reference implementations.

## Important APIs, Types, And Functions
`sha256(data)` returns deterministic hex bytes and is used as a pseudo-random generator. `SimpleSpans` is a deliberately inefficient oracle backed by a set of byte offsets; it implements `add`, `remove`, `each`, iteration as coalesced `(start, length)` ranges, `len`, boolean state, `+`, `-`, `+=`, `-=`, `&`, and containment of full spans. `ByteSpans` compares this oracle to the production `Spans`.

`extend` and `replace` are helper functions for the data-span oracle. `SimpleDataSpans` represents sparse data with a missing-mask string and a byte buffer; it implements `get_chunks`, `get_spans`, `get`, `pop`, `remove`, and `add`. `StringSpans` applies the same behavioral checks to the simple oracle and production `DataSpans`.

## Control Flow
`ByteSpans.test_basic` checks empty spans, construction from start/length and from another span set, mutation chaining, containment semantics, iteration, and length. `test_large` validates huge spans such as `2**65` without expanding them, proving the production representation is interval-based. `test_math` exercises subtraction, intersection, union, and in-place variants over overlapping, adjacent, and disjoint ranges.

`test_random` executes 1000 deterministic operations derived from SHA-256 bytes. It repeatedly resets, constructs, adds, removes, unions, subtracts, mutates in place, intersects, and then compares the oracle and production object on expanded offsets, total length, truthiness, coalesced spans, and sampled containment. `test_overlap` exhaustively checks small range pairs by comparing `overlap(a,b,c,d)` to set intersection.

For data spans, `do_basic` checks empty behavior, gap handling, copy independence, chunk totals, partial pop/removal, overlapping writes, and data replacement. `do_scan` builds a baseline with many gaps and then tests every added interval and many short removals, checking both retrieval correctness and absence/presence of bytes. `StringSpans.test_random` performs 1000 deterministic add/remove/pop operations and compares `DataSpans` to `SimpleDataSpans` over length, dump positions, and 100 sampled reads per step.

## State And Persistence Behavior
The tests are pure in-memory checks. `Spans` state is a set of covered byte ranges and must maintain canonical coalesced iteration while supporting very large lengths. `DataSpans` state is sparse byte content; adding data fills or overwrites ranges, removing creates holes, and popping returns data only for fully available requested ranges while removing it. Copy constructors must preserve data but not alias mutable state.

## Dependencies And Integration Points
The module depends on Twisted Trial and `allmydata.util.spans`. In Tahoe-LAFS, span utilities are typically used by transfer, encoding, repair, and download code that needs compact accounting for byte ranges or sparse data. These tests therefore provide low-level confidence for higher-level file-transfer correctness without using network or filesystem fixtures.

## Risks And Edge Cases
Important edge cases include huge non-expanded ranges, zero or empty states, adjacent range coalescing, partial overlap math, full-span containment semantics, sparse reads that cross holes, overlapping writes replacing old data, copy independence, and deterministic randomized operations that could hide gaps if the oracle shares the same bug. The reference implementations are intentionally simple and structurally different, reducing that risk.

## Test Signals
Passing tests signal that `Spans` correctly implements range algebra and accounting, `overlap` returns exact intersections or `None`, and `DataSpans` preserves sparse byte data semantics under add/remove/pop/copy operations. The randomized oracle comparisons are the strongest signal because they cover many operation sequences beyond handwritten examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_spans.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_statistics.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_statistics.py

## Purpose
This module tests probability and repair-cost helpers in `allmydata.util.statistics`. The covered functions model binomial probabilities, survival distributions, convolution, repair counts, repair costs, and threshold selection for erasure-coded file-loss risk.

## Important APIs, Types, And Functions
The `Statistics` test case defines small assertion helpers: `should_assert` expects an `AssertionError`, `failUnlessListEqual` compares exact lists element by element, and `failUnlessListAlmostEqual` compares floating-point lists. Tested production APIs include `binomial_coeff`, `binomial_distribution_pmf`, `print_pmf`, `survival_pmf`, `survival_pmf_via_conv`, `survival_pmf_via_bd`, `valid_pmf`, `repair_count_pmf`, `bandwidth_cost_function`, `mean_repair_cost`, `eternal_repair_cost`, `convolve`, `find_k`, `pr_file_loss`, and `pr_backup_file_loss`.

## Control Flow
Each test focuses on one mathematical contract. Binomial coefficient checks base cases, symmetry, and invalid `n < k`. Binomial PMF tests known values for `n=2, p=.1`, total probability near one, input assertions, and text output from `print_pmf`. Survival PMF cross-checks two independent implementations, convolution and binomial-distribution grouping, over a mixed reliability vector.

Repair tests build a survival PMF from five servers at `.9`, transform it with `repair_count_pmf(k=3)`, and verify the exact mapping of lost/surviving-share counts to repair counts. Cost tests feed the same PMF into mean and eternal repair-cost functions with different upload/download ratios and discount rates. Convolution tests algebraic properties: commutativity, associativity, distributivity, and scalar-multiplication associativity. The final tests verify `find_k` selects a threshold under a target loss probability and that file-loss helpers return known values for homogeneous reliabilities.

## State And Persistence Behavior
There is no persistent state. All tested functions operate on numeric inputs and return numbers or lists. The only side effect is `print_pmf`, which writes formatted lines to a provided `StringIO` object. Floating-point state is validated with approximate equality where appropriate.

## Dependencies And Integration Points
The module depends on Twisted Trial, `io.StringIO`, and `allmydata.util.statistics`. These helpers feed Tahoe-LAFS reasoning around share survival, file loss probability, and expected repair bandwidth, so correctness matters for capacity planning and reliability modeling rather than direct protocol behavior.

## Risks And Edge Cases
The tests cover invalid probabilities outside `[0, 1]`, invalid sample counts, coefficient symmetry, PMF normalization, and cross-implementation agreement. Some expected cost values are acknowledged in comments as not manually checked beyond a point, so they act as regression fixtures more than independently derived proofs. Floating-point tolerance must remain stable if algorithms are refactored.

## Test Signals
Passing tests signal that probability distributions remain normalized and consistent, convolution behaves algebraically, repair-count and cost helpers preserve historical outputs, and `find_k` can choose an erasure-coding threshold that keeps modeled file-loss probability below a target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_statistics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_stats.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_stats.py

## Purpose
This module tests `allmydata.stats.CPUUsageMonitor`, specifically that it starts as a Twisted service, collects enough samples, trims its history, and begins exposing expected CPU usage metrics.

## Important APIs, Types, And Functions
`FasterMonitor` subclasses `CPUUsageMonitor` and lowers `POLL_INTERVAL` to `0.01` seconds for test speed. `CPUUsage` combines Twisted Trial, `pollmixin.PollMixin`, and `StallMixin`. `setUp` starts a `service.MultiService`, `tearDown` stops it, and `test_monitor` drives the monitor lifecycle.

## Control Flow
The test first calls `get_stats()` before the monitor has a service parent and verifies the rolling average key is absent. It then attaches the monitor with `setServiceParent(self.s)`, polls until `len(m.samples) == m.HISTORY_LENGTH + 1`, stalls for two more fast polling intervals to exercise history trimming, and finally checks that `get_stats()` includes `cpu_monitor.1min_avg`, `cpu_monitor.5min_avg`, `cpu_monitor.15min_avg`, and `cpu_monitor.total`.

## State And Persistence Behavior
The monitor keeps in-memory CPU samples while running as a Twisted service. The test intentionally waits for one more sample than `HISTORY_LENGTH` and then stalls again so trimming code is covered. No filesystem or external persistent state is used.

## Dependencies And Integration Points
The module depends on Twisted Trial, `twisted.application.service.MultiService`, Tahoe's `CPUUsageMonitor`, `pollmixin`, and `StallMixin`. It verifies that the stats monitor integrates with Twisted's service-parent lifecycle and exposes keys expected by Tahoe's stats collection/reporting layer.

## Risks And Edge Cases
The test is timing-sensitive because it depends on periodic polling. `FasterMonitor` reduces runtime but still relies on reactor scheduling and CPU sampling availability. It checks key presence rather than numeric values, so it catches lifecycle and publication regressions but not detailed CPU calculation errors.

## Test Signals
Passing tests signal that CPU monitoring is quiet before startup, begins collecting after service attachment, maintains/trims sample history, and publishes the expected rolling and total CPU stat keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_stats.py -->
