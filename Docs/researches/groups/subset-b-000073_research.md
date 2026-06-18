# Research: subset-b-000073

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir_test.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir_test.go

Purpose: integration-style tests for the `bindir` image verifier backend. The test builds standalone Go verifier binaries, arranges temporary verifier directories with deterministic names, and exercises verifier ordering, pass/fail aggregation, I/O handling, timeout behavior, output truncation, missing/empty directories, max-verifier limits, and child process cleanup.

Important APIs/types/functions: `buildGoVerifiers` compiles every verifier source in a directory with `go build`; `exeIfWindows` normalizes executable suffix expectations; `newBinDir` copies selected test binaries into a temp directory as sorted `verifier-N` entries; `TestBinDirVerifyImage` contains all behavioral subtests. The test also renders `testdata/verifier_templates` with file paths used to assert argv and stdin contents.

Control flow: setup builds all static and rendered verifier binaries once, then each subtest constructs a `Config` with `BinDir`, `MaxVerifiers`, and `PerVerifierTimeout`, calls `VerifyImage`, and asserts `Judgement.OK`, `Judgement.Reason`, and side effects. Rejection short-circuits after the first nonzero exit. The slow child test validates context timeout and platform process cleanup paths.

State/persistence: all state is temporary test state: compiled binaries, copied verifier directories, captured args/stdin files, and child processes. No containerd metadata is persisted.

Dependencies/integration: depends on the local Go toolchain, `tomlext.Duration`, OpenContainers descriptors, containerd logging, and testify. It directly tests `bindir.NewImageVerifier` and platform-specific `startProcess` implementations through real executables.

Risks: tests can be sensitive to Go toolchain availability, process scheduling, timeout values, pipe buffering, and Windows executable suffixes. Infinite-loop child fixtures make cleanup correctness important; leaks may only show as hanging tests or stray processes.

Test signals: strong coverage for verifier command contract (`-name`, `-digest`, descriptor JSON on stdin, descriptor media type), sorted execution, max verifier truncation, stdout/stderr truncation, missing/empty bin directories, reject reason formatting, timeout errors, and child process termination.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_unix.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_unix.go

Purpose: Unix process-management shim for verifier binaries. It starts each verifier in a separate process group so context cancellation kills both the verifier and any subprocesses it created.

Important APIs/types/functions: `process` wraps `*exec.Cmd`; `startProcess(ctx, cmd)` sets `cmd.SysProcAttr = &unix.SysProcAttr{Setpgid: true}`, installs `cmd.Cancel` to send `SIGKILL` to `-cmd.Process.Pid`, starts the command, and returns the wrapper; `(*process).cleanup` is a no-op on Unix.

Control flow: before `cmd.Start`, the command is configured to become process-group leader. When `exec.CommandContext` observes context cancellation, Go calls `cmd.Cancel`, which targets the whole process group rather than only the immediate child.

State/persistence: no persistent state. Runtime state is only the OS process group and the process handle owned by `exec.Cmd`.

Dependencies/integration: used by `bindir.runVerifier` after pipes and context deadlines are configured. Depends on `golang.org/x/sys/unix` for `SysProcAttr` and `Kill`.

Risks: process-group kill assumes `cmd.Process` is initialized when `Cancel` runs. A verifier that changes process groups can escape cleanup. Sending `SIGKILL` prevents graceful teardown but is intentional for bounded verifier timeouts.

Test signals: exercised by `slow_child_process.go` through `bindir_test.go`, which verifies verifier timeouts do not leave a long-running child process alive.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_windows.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_windows.go

Purpose: Windows process-management shim for verifier binaries. It places each verifier in a Windows Job Object configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, so closing the job tears down the verifier process tree.

Important APIs/types/functions: `process` stores the `exec.Cmd`, job handle, and opened process handle. `startProcess` creates a job object, sets extended limit information, starts the command, opens the verifier process with query/quota/terminate rights, assigns it to the job, and returns the wrapper. `cleanup` closes both handles and logs close failures.

Control flow: job object creation precedes `cmd.Start`; after start, `OpenProcess` obtains a handle suitable for `AssignProcessToJobObject`. Any setup failure after job creation calls `cleanup` before returning an annotated error.

State/persistence: runtime-only Windows kernel handles. No filesystem or metadata persistence.

Dependencies/integration: used by `bindir.runVerifier` on Windows. Depends on `golang.org/x/sys/windows` and containerd log context. The implementation is the Windows counterpart to Unix process-group cleanup.

Risks: one failure path after `OpenProcess` failure returns without calling `cleanup`, so the already-started process/job handle path should be reviewed carefully. Job assignment can fail when nested job restrictions apply. Handle leaks or failed job closure can leave verifier descendants running.

Test signals: indirectly exercised by the bindir slow-child timeout test on Windows; coverage should assert no lingering child and no handle cleanup errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_a.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_a.go

Purpose: tiny acceptance verifier fixture. It prints a multi-line acceptance reason and exits successfully, letting tests verify reason trimming and aggregation.

Important APIs/types/functions: only `main`, which writes `Reason A line 1` and `Reason A line 2` to stdout with `fmt.Println`.

Control flow: linear print-and-exit path with implicit exit code 0.

State/persistence: no persistent state and no inputs read.

Dependencies/integration: compiled by `buildGoVerifiers` and copied by `newBinDir` into sorted verifier directories. Used by `TestBinDirVerifyImage` to check successful `Judgement` text.

Risks: minimal. Any change to exact stdout text breaks tests that assert reason formatting.

Test signals: validates that stdout from a successful verifier becomes the per-verifier reason and that embedded newlines are preserved after trimming outer whitespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_a.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_b.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_b.go

Purpose: second successful verifier fixture used to prove multiple accepting verifiers are executed and their reasons are ordered by directory entry sorting.

Important APIs/types/functions: `main` prints `Reason B` to stdout and returns normally.

Control flow: single stdout write followed by implicit zero exit.

State/persistence: no state.

Dependencies/integration: built into a standalone binary for `bindir_test.go`. It is commonly placed after `accept_reason_a` in temporary verifier directories.

Risks: exact output is part of test expectations. The fixture intentionally does not inspect argv or stdin, so it only validates aggregation behavior.

Test signals: confirms successful verifier reasons are appended after prior success reasons with the expected comma separator and verifier binary name prefix.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_b.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_c.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_c.go

Purpose: third successful verifier fixture for max-verifier and ordering tests.

Important APIs/types/functions: `main` prints `Reason C` and exits with status 0.

Control flow: linear stdout write.

State/persistence: none.

Dependencies/integration: used by `bindir_test.go` with other accept fixtures to verify that `MaxVerifiers` limits execution after the configured number of sorted entries.

Risks: low. Output text is an asserted test contract.

Test signals: helps detect regressions where `MaxVerifiers` is ignored, directory ordering changes, or skipped verifiers still influence the final reason.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_c.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr.go

Purpose: stress fixture for verifier stderr handling. It emits a large single write to stderr while returning success, so `bindir.runVerifier` must drain stderr without blocking or inflating the returned reason.

Important APIs/types/functions: `main` sets `n := 50000`, announces the intended write on stdout, writes `n` repeated `A` bytes to stderr, reports write errors to stdout, and prints the byte count written.

Control flow: one large stderr write through `fmt.Fprint(os.Stderr, strings.Repeat(...))`, then normal exit.

State/persistence: no persistent state.

Dependencies/integration: compiled and run by the `large output is truncated` subtest, alongside stdout variants.

Risks: pipe buffer behavior is platform-dependent; the fixture specifically guards against deadlocks when stderr exceeds `outputLimitBytes`.

Test signals: proves stderr is scanned/logged up to a bound, truncated remainder is discarded, and successful verification can complete even when stderr is much larger than the retained limit.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr_chunked.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr_chunked.go

Purpose: stderr stress fixture that writes many small chunks instead of one large buffer. It covers a different pipe-buffer and scanner interaction than `large_stderr.go`.

Important APIs/types/functions: `main` loops 500000 times, printing one `A` byte to stderr each iteration, tracking bytes written, and periodically reporting progress to stdout.

Control flow: repeated stderr writes with progress messages every 10000 iterations; write errors are reported to stdout and execution continues.

State/persistence: none.

Dependencies/integration: used by the bindir truncation test to ensure long-running chunked stderr output does not block verifier completion.

Risks: slow on loaded systems because it performs many small formatted writes. Output sizes and progress messages are part of a stress profile rather than exact assertions.

Test signals: catches regressions where stderr draining only works for one large write but deadlocks or times out when the verifier writes incrementally.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr_chunked.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout.go

Purpose: stdout stress fixture for returned verifier reason truncation. It emits more stdout than `outputLimitBytes`, forcing the caller to retain a bounded reason and discard the rest safely.

Important APIs/types/functions: `main` writes an informational line to stderr, prints 50000 repeated `A` bytes to stdout in one call, reports stdout write errors to stderr, and logs the written count.

Control flow: single large stdout write followed by normal exit.

State/persistence: none.

Dependencies/integration: used by `bindir_test.go` in the large-output suite. `runVerifier` reads stdout with a limited reader, marks truncation, then drains the remainder.

Risks: pipe buffering can expose deadlocks if the parent stops reading after the limit without discarding. Exact length is chosen to exceed the 32 KiB limiter.

Test signals: validates bounded `Judgement.Reason` size and confirms large stdout does not prevent process completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout_chunked.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout_chunked.go

Purpose: chunked stdout stress fixture. It verifies that many small stdout writes are truncated and drained without hanging the verifier.

Important APIs/types/functions: `main` loops 500000 times, writes `A` to stdout, tracks total bytes, and logs progress and final count to stderr.

Control flow: repeated stdout writes; every 10000 iterations a progress line is written to stderr. Write errors are logged but do not stop the loop.

State/persistence: no persistent state.

Dependencies/integration: runs under `bindir.runVerifier` where stdout is read to a limit and then drained to avoid broken pipes.

Risks: high iteration count can make the test sensitive to slow CI. It intentionally exercises a worst-case path for scanner/pipe scheduling.

Test signals: catches regressions in stdout draining, truncation marker logic, and timeout handling for verbose verifier programs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout_chunked.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/reject_reason_d.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/reject_reason_d.go

Purpose: rejection verifier fixture. It emits a reason and exits nonzero so `VerifyImage` can convert verifier failure into `Judgement.OK=false` rather than a Go error.

Important APIs/types/functions: `main` prints `Reason D` to stdout and calls `os.Exit(1)`.

Control flow: stdout reason write, then explicit exit code 1.

State/persistence: none.

Dependencies/integration: used by bindir tests to verify rejection short-circuiting and reason formatting.

Risks: output and exit code are test contracts. If changed, rejection semantics assertions lose signal.

Test signals: confirms `cmd.Wait` `ExitError` is treated as verifier judgement data, not infrastructure failure, and that subsequent verifiers are not executed after rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/reject_reason_d.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/slow_child_process.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/slow_child_process.go

Purpose: timeout and descendant-process cleanup fixture. It re-executes itself as a child that loops forever, then waits on that child, forcing the verifier runner to kill process descendants on timeout.

Important APIs/types/functions: `main` has two modes. With `-sleep-forever`, it prints a message and spins forever. Without the flag, it starts `os.Args[0] -sleep-forever`, captures combined output, prints it, and panics if the child exits with an error.

Control flow: parent blocks on `cmd.CombinedOutput`; child never exits. Only external cancellation should terminate the process tree.

State/persistence: transient processes only.

Dependencies/integration: used by `bindir_test.go` to exercise Unix process-group killing and Windows job-object cleanup.

Risks: a broken cleanup implementation can leave an infinite child consuming CPU. The child loop is intentionally busy rather than sleeping, so timeout bounds must be short and cleanup reliable.

Test signals: strongest signal for process tree cleanup and command context cancellation semantics in `processes_unix.go` and `processes_windows.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/slow_child_process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/image_verifier.go -->
# sources/cloud-native/containerd/pkg/imageverifier/image_verifier.go

Purpose: defines the minimal image-verification contract used by containerd components and implementations such as `bindir`.

Important APIs/types/functions: `ImageVerifier` is an interface with `VerifyImage(ctx, name, desc) (*Judgement, error)`. `Judgement` contains `OK bool` and `Reason string`.

Control flow: none directly. Implementations decide how to inspect the image name and OCI descriptor, whether to accept or reject, and whether failures are infrastructure errors or negative judgements.

State/persistence: no state. `Judgement` is a transient result object suitable for callers to log or surface.

Dependencies/integration: imports `context` and OpenContainers image-spec descriptors. `pkg/imageverifier/bindir` implements this interface and uses `Judgement` to aggregate external verifier decisions.

Risks: the interface intentionally does not distinguish policy rejection from infrastructure failure except through `Judgement.OK` vs returned error; callers must preserve that distinction. `Reason` is unstructured text and may include external verifier output.

Test signals: implementation tests should assert accept, reject, and error paths all map to the expected interface semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/image_verifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/read_closer.go -->
# sources/cloud-native/containerd/pkg/ioutil/read_closer.go

Purpose: adapts an `io.Reader` into an `io.ReadCloser` whose `Close` can interrupt reads and whose background copy closes pipe ends when input drains.

Important APIs/types/functions: `wrapReadCloser` stores an `io.PipeReader` and `io.PipeWriter`; `NewWrapReadCloser(r)` starts a goroutine that copies `r` into the pipe writer, then closes both pipe ends; `Read` delegates to the pipe reader and maps `io.ErrClosedPipe` to `io.EOF`; `Close` closes both pipe ends and returns nil.

Control flow: construction immediately starts an asynchronous `io.Copy`. Consumers read from the pipe. Close interrupts future reads and unblocks the copy path through closed pipe errors.

State/persistence: in-memory pipe state and one goroutine per wrapper. No persistence.

Dependencies/integration: general helper for code expecting an `io.ReadCloser` around a plain reader.

Risks: caller must eventually close or drain the wrapper to avoid goroutine leakage, as documented. Errors from `io.Copy` and pipe closes are discarded. Closing both ends can hide the original underlying reader error.

Test signals: `read_closer_test.go` verifies sequential byte reads and EOF behavior after explicit close.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/read_closer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/read_closer_test.go -->
# sources/cloud-native/containerd/pkg/ioutil/read_closer_test.go

Purpose: unit test for `NewWrapReadCloser` read and close behavior.

Important APIs/types/functions: `TestWrapReadCloser` wraps a `bytes.Buffer` containing `abc`, reads one byte at a time, then calls `Close` and checks that a subsequent read returns `(0, io.EOF)` without modifying the destination buffer.

Control flow: create wrapper, read first byte, read second byte, close early before consuming `c`, then assert EOF.

State/persistence: only in-memory buffer and pipe state.

Dependencies/integration: uses Go `bytes`, `io`, `testing`, and testify assertions. Tests the implementation in the same package.

Risks: does not assert behavior when the underlying reader blocks, returns errors, or is larger than pipe buffering. It also does not assert goroutine exit explicitly.

Test signals: verifies the core adapter contract that explicit close maps closed-pipe reads to EOF and that partial reads preserve byte order.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/read_closer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/write_closer.go -->
# sources/cloud-native/containerd/pkg/ioutil/write_closer.go

Purpose: small write closer utilities: close notification, no-op close wrapping, and serialized concurrent writes.

Important APIs/types/functions: `NewWriteCloseInformer` wraps an `io.WriteCloser` and returns both the wrapper and a close channel that closes after `Close`. `NewNopWriteCloser` adapts an `io.Writer` to `io.WriteCloser` with no-op close. `NewSerialWriteCloser` wraps a write closer with a mutex around both `Write` and `Close`.

Control flow: wrappers delegate writes to the underlying writer. `writeCloseInformer.Close` calls the underlying close then closes the notification channel. `serialWriteCloser` serializes every write and close call, preventing interleaved concurrent writes for pipes and older kernel/file behavior.

State/persistence: in-memory wrapper state and one mutex/channel. Persistence depends on the underlying writer.

Dependencies/integration: generic package helper used where containerd needs close observation or atomic write groups.

Risks: `writeCloseInformer.Close` will panic if called twice because it closes the channel unguarded. `serialWriteCloser` cannot make partial writes atomic if the underlying writer itself returns short writes. Close waits behind active writes.

Test signals: `write_closer_test.go` validates close notification and non-interleaving under concurrent file writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/write_closer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/write_closer_test.go -->
# sources/cloud-native/containerd/pkg/ioutil/write_closer_test.go

Purpose: tests close notification and serialization guarantees in `write_closer.go`.

Important APIs/types/functions: `TestWriteCloseInformer` wraps a pipe writer, starts a goroutine waiting on the close channel, writes data, closes, and verifies the channel signal. `TestSerialWriteCloser` creates a temp file, wraps it in `NewSerialWriteCloser`, launches multiple goroutines writing repeated digit lines, and checks each line remains intact. `repeatNumber` builds expected lines.

Control flow: close-informer test coordinates through channels. Serial-write test repeats concurrent writes across several iterations, then sorts resulting lines before comparing expected payloads.

State/persistence: temporary files only, removed by test cleanup.

Dependencies/integration: uses `os`, `sync`, `sort`, `strconv`, `strings`, and testify.

Risks: concurrency tests are probabilistic; without serialization, interleaving may not reproduce on every platform. Test does not cover double close or underlying write errors.

Test signals: protects the key requirement that a logical write payload is not interleaved with another goroutine's payload when the serial wrapper is used.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/write_closer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/writer_group.go -->
# sources/cloud-native/containerd/pkg/ioutil/writer_group.go

Purpose: fan-out writer registry keyed by string. It lets callers add, retrieve, remove, write to all, and close all registered `io.WriteCloser`s safely under a mutex.

Important APIs/types/functions: `WriterGroup` stores `writers map[string]io.WriteCloser` and `closed bool`. `NewWriterGroup` initializes the map. `Add` replaces an existing writer and closes the replaced one, or immediately closes the new writer if the group is already closed. `Get` returns the current writer. `Remove` deletes and closes a writer. `Write` writes to every registered writer, accumulating the first error and returning the input length on success. `Close` closes all writers and marks the group closed.

Control flow: all public methods take the mutex. Writes are sequential across registered writers while holding the lock, so add/remove/close cannot race with fan-out writes.

State/persistence: in-memory registry; persistence is owned by underlying writers.

Dependencies/integration: generic I/O helper for broadcasting output streams.

Risks: holding the mutex during slow or blocking writes can block management operations. `Close` ignores close errors. `Write` returns after attempting all writers but only preserves the first error.

Test signals: `writer_group_test.go` covers empty, closed, add/get/remove, replacement, write fan-out, and close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/writer_group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/writer_group_test.go -->
# sources/cloud-native/containerd/pkg/ioutil/writer_group_test.go

Purpose: unit tests for `WriterGroup` registry and fan-out semantics.

Important APIs/types/functions: local `writeCloser` records written bytes and close state. `TestEmptyWriterGroup` checks writes to an empty group. `TestClosedWriterGroup` verifies add-after-close immediately closes the writer. `TestAddGetRemoveWriter` exercises add, retrieval, write, removal, and close. `TestReplaceWriter` ensures replacing an existing key closes the old writer and directs subsequent writes to the new one.

Control flow: tests create a group, mutate writer membership, call `Write` or `Close`, and assert writer content and close flags.

State/persistence: in-memory buffers only.

Dependencies/integration: same-package tests with Go `testing` and simple fake write closers.

Risks: does not cover underlying writer errors or concurrent method calls. Close error swallowing is not asserted.

Test signals: confirms the intended ownership rule: once a writer is removed, replaced, or added after group closure, the group closes it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ioutil/writer_group_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/kernelversion/kernel_linux.go -->
# sources/cloud-native/containerd/pkg/kernelversion/kernel_linux.go

Purpose: Linux kernel version parser and comparator used by features that need minimum kernel gates.

Important APIs/types/functions: `KernelVersion` stores `Kernel` and `Major` integers and formats as `kernel.major`. Package variable `kernelVersion` caches detected host version. `getKernelVersion` calls `unix.Uname`, converts `Utsname.Release` through `unix.ByteSliceToString`, parses it, and caches the result. `parseRelease` scans two dot-separated integers using `fmt.Fscanf`. `GreaterEqualThan(minVersion)` compares current kernel major/minor against a minimum.

Control flow: first comparison loads and caches the host kernel. Parsing accepts release strings with extra suffix after the second number because scanning stops after the major component.

State/persistence: process-global in-memory cache only. No disk persistence.

Dependencies/integration: depends on `golang.org/x/sys/unix`. Copied/customized from Moby seccomp kernel version handling.

Risks: cache never refreshes during process lifetime. Parser ignores patch level and distribution suffix semantics. The name `Major` represents the second component, which can be confused with semantic-version major naming.

Test signals: `kernel_linux_test.go` covers host detection, accepted release formats, parse errors, and comparison outcomes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/kernelversion/kernel_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/kernelversion/kernel_linux_test.go -->
# sources/cloud-native/containerd/pkg/kernelversion/kernel_linux_test.go

Purpose: tests Linux kernel parsing and minimum-version comparison.

Important APIs/types/functions: `TestGetKernelVersion` validates nonnil host version with nonzero kernel component. `TestParseRelease` table-tests valid release formats such as `3.8.0-19-generic`, distro suffixes, short `3.8`, and invalid strings. `TestGreaterEqualThan` overwrites the package `kernelVersion` cache with synthetic versions and checks boundary comparisons.

Control flow: table tests parse input and compare either exact `KernelVersion` or expected error string. Comparator tests set cached state directly to avoid host dependency.

State/persistence: mutates package-global `kernelVersion` during tests; no external persistence.

Dependencies/integration: Linux-only package tests with Go `testing` and `fmt`.

Risks: direct global mutation can leak between tests if future tests assume actual host state. Error string comparisons are brittle if parser wording changes.

Test signals: ensures parser tolerates common uname suffixes and that `GreaterEqualThan` handles equal, lower, and higher second components.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/kernelversion/kernel_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/labels/labels.go -->
# sources/cloud-native/containerd/pkg/labels/labels.go

Purpose: central constants for well-known containerd labels used across content, namespace, and distribution metadata.

Important APIs/types/functions: `LabelUncompressed` marks compressed layer contents with the uncompressed digest. `LabelSharedNamespace` marks namespaces whose contents may be shared. `LabelDistributionSource` records content origin, for example distribution registry and repository source.

Control flow: none; constants only.

State/persistence: labels are persisted as metadata keys wherever containerd stores content or namespace records. This file only defines keys.

Dependencies/integration: imported by content management, namespace sharing, and distribution pull/push paths that need stable label names.

Risks: changing constant values breaks existing metadata compatibility and external tooling. The constants do not validate label values or ownership of subkeys such as distribution source suffixes.

Test signals: no direct tests here; validation tests cover size limits in `validate.go`. Integration tests should assert these labels are emitted and read consistently by content and namespace flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/labels/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/labels/validate.go -->
# sources/cloud-native/containerd/pkg/labels/validate.go

Purpose: enforces the containerd label size limit for key plus value.

Important APIs/types/functions: constants `maxSize = 4096` and `keyMaxLen = 64`; `Validate(k, v)` computes byte length of key and value, returns nil when at or below the limit, and returns an `errdefs.ErrInvalidArgument`-wrapping error when above the limit. Long keys are truncated to 64 bytes in the error message.

Control flow: one size check. If invalid, optionally shorten the key used in the diagnostic, then format a descriptive error with wrapped invalid-argument sentinel.

State/persistence: no state. It protects persisted label metadata by rejecting oversized inputs before storage.

Dependencies/integration: depends on `github.com/containerd/errdefs` so callers can classify validation failure through `errdefs.IsInvalidArgument` or `errors.Is`.

Risks: uses `len` byte counts, not rune counts, which is correct for storage but can surprise callers with multibyte labels. It validates only total size, not key syntax or reserved prefixes.

Test signals: `validate_test.go` covers valid boundaries, oversized labels, error classification, and long-key diagnostic truncation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/labels/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/labels/validate_test.go -->
# sources/cloud-native/containerd/pkg/labels/validate_test.go

Purpose: boundary tests for label key/value size validation.

Important APIs/types/functions: `TestValidLabels` checks ordinary values and a total size just below `maxSize`. `TestInvalidLabels` checks an oversized key/value pair and verifies invalid-argument classification. `TestLongKey` validates long-key truncation and exact-size boundaries.

Control flow: tests build strings with `strings.Repeat`, call `Validate`, and compare nil, nonnil, or sentinel error classification through `errdefs`.

State/persistence: no external state.

Dependencies/integration: uses `testing`, `strings`, `errdefs`, and testify `assert`.

Risks: tests focus on ASCII strings, so they do not document multibyte byte-count behavior. The equality assertion style for nil errors is less idiomatic but still effective.

Test signals: protects the 4096-byte total limit, the allowed exact-boundary behavior, and preservation of `errdefs.ErrInvalidArgument` wrapping for API callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/labels/validate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/context.go -->
# sources/cloud-native/containerd/pkg/namespaces/context.go

Purpose: carries containerd namespace identity through contexts, environment defaults, and RPC metadata.

Important APIs/types/functions: constants `NamespaceEnvVar = "CONTAINERD_NAMESPACE"` and `Default = "default"`; private `namespaceKey`; `WithNamespace` stores the namespace in context and also attaches gRPC and ttrpc outgoing metadata; `NamespaceFromEnv` uses the env var or default; `Namespace` reads from context value, then incoming gRPC metadata, then ttrpc metadata; `NamespaceRequired` requires a nonempty namespace and validates it with `identifiers.Validate`.

Control flow: namespace lookup prefers local context value over RPC metadata. Required lookup wraps missing namespace as `errdefs.ErrFailedPrecondition` and invalid names with validation context.

State/persistence: context-only transient state; environment read is process state.

Dependencies/integration: used by clients, services, and spec options such as namespaced cgroups. Bridges gRPC and ttrpc header helpers.

Risks: `Namespace` may return an unvalidated value; only `NamespaceRequired` validates. Environment fallback can make behavior implicit.

Test signals: `context_test.go` validates set/get, required errors, invalid namespace handling, and env default behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/context_test.go -->
# sources/cloud-native/containerd/pkg/namespaces/context_test.go

Purpose: tests namespace context propagation and environment fallback.

Important APIs/types/functions: `TestContext` verifies missing namespace, `NamespaceRequired` errors, `WithNamespace` storage, valid required lookup, and invalid namespace failure. `TestNamespaceFromEnv` uses `t.Setenv` to test default namespace and explicit `CONTAINERD_NAMESPACE`.

Control flow: each test creates a background context, applies namespace helpers, and asserts lookup results.

State/persistence: mutates process environment only through test-scoped `t.Setenv`.

Dependencies/integration: same-package tests with `context`, `testing`, and errdefs/identifier behavior through production functions.

Risks: does not directly test gRPC/ttrpc metadata fallback; those are covered by separate metadata tests. Validation expectations depend on `identifiers.Validate`.

Test signals: protects the missing namespace precondition contract, default namespace name, environment variable name, and invalid-namespace rejection path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/context_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/grpc.go -->
# sources/cloud-native/containerd/pkg/namespaces/grpc.go

Purpose: gRPC metadata carrier for containerd namespace propagation.

Important APIs/types/functions: `GRPCHeader = "containerd-namespace"`; `withGRPCNamespaceHeader(ctx, namespace)` creates metadata pair and joins it ahead of existing outgoing metadata; `fromGRPCHeader(ctx)` reads the first namespace value from incoming metadata.

Control flow: outgoing writes preserve existing metadata while placing the latest namespace first. Incoming reads do not inspect outgoing metadata and return false when metadata or values are absent.

State/persistence: context metadata only.

Dependencies/integration: used by `WithNamespace` and `Namespace`. Depends on `google.golang.org/grpc/metadata`.

Risks: multiple namespace values can exist; readers take index 0. Outgoing context is not checked on reads, so client-side contexts without incoming metadata rely on the direct context value.

Test signals: no direct gRPC-specific test in this subset, but namespace context tests plus RPC integration should verify header propagation between clients and servers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/store.go -->
# sources/cloud-native/containerd/pkg/namespaces/store.go

Purpose: defines the metadata-store interface for namespace records.

Important APIs/types/functions: `Store` exposes `Get`, `List`, `Create`, `Update`, `Delete`, `SetLabel`, and `Labels`. `DeleteInfo` carries a `Synchronous` flag. `DeleteOpts` mutates `DeleteInfo` during delete operations.

Control flow: interface-only file. Implementations decide persistence, filtering, update semantics, and asynchronous vs synchronous deletion.

State/persistence: the interface represents persisted namespace metadata and labels. This file stores nothing directly.

Dependencies/integration: imports API `types.Namespace` and `filters`. Containerd metadata backends implement this interface; higher-level services use it to manage namespace lifecycle and labels.

Risks: label validation, delete synchronization, and filter semantics are delegated to implementations. Callers must not assume delete completion unless a synchronous option is supported and requested.

Test signals: implementation tests should cover create/update/delete semantics, filtering, labels, and deletion modes. This file is compile-time contract surface.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/ttrpc.go -->
# sources/cloud-native/containerd/pkg/namespaces/ttrpc.go

Purpose: ttrpc metadata carrier for containerd namespace propagation.

Important APIs/types/functions: `TTRPCHeader = "containerd-namespace"`; `withTTRPCNamespaceHeader(ctx, namespace)` clones existing metadata or creates a new map, sets the namespace, and returns a context with metadata. `fromTTRPCHeader(ctx)` extracts the first namespace value.

Control flow: metadata is cloned before mutation to avoid aliasing callers' maps. Lookup returns false on absent metadata or absent header values.

State/persistence: context metadata only.

Dependencies/integration: used by `WithNamespace` and `Namespace`. Depends on `github.com/containerd/ttrpc`.

Risks: only the first value is used when multiple values exist. Header key must remain aligned with gRPC and service expectations.

Test signals: `ttrpc_test.go` verifies metadata clone independence and namespace header round trip.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/ttrpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/ttrpc_test.go -->
# sources/cloud-native/containerd/pkg/namespaces/ttrpc_test.go

Purpose: tests ttrpc metadata behavior used by namespace propagation.

Important APIs/types/functions: `TestCopyTTRPCMetadata` confirms `ttrpc.MD.Clone` deep-copies value slices by mutating the original after clone. `TestTTRPCNamespaceHeader` verifies `withTTRPCNamespaceHeader` and `fromTTRPCHeader` round-trip a namespace string.

Control flow: create metadata/context, mutate or extract values, compare with `reflect.DeepEqual` or direct string checks.

State/persistence: context metadata only.

Dependencies/integration: uses `github.com/containerd/ttrpc`.

Risks: tests do not cover multiple namespace header values or interaction with direct context values. The clone test partly tests upstream ttrpc behavior, not only this package.

Test signals: protects against metadata aliasing bugs and ensures ttrpc clients receive the same namespace header key as gRPC clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/namespaces/ttrpc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/netns/netns_linux.go -->
# sources/cloud-native/containerd/pkg/netns/netns_linux.go

Purpose: Linux network namespace lifecycle helper for sandbox/container networking.

Important APIs/types/functions: `newNS(baseDir, pid)` creates a bind-mounted namespace file under `baseDir`, either from a new namespace (`unshare(CLONE_NEWNET)`) or an existing pid namespace. `unmountNS` detaches and removes the path. `getCurrentThreadNetNSPath` uses `/proc/<pid>/task/<tid>/ns/net`. `NetNS` exposes `NewNetNS`, `NewNetNSFromPID`, `LoadNetNS`, `Remove`, `Closed`, `GetPath`, and `Do`.

Control flow: new namespace creation locks an OS thread, records the original netns, unshares, bind-mounts the thread netns path to a temp file, restores the original namespace, and returns the bind path. `Closed` treats missing or non-namespace paths as closed and cleans up stale files.

State/persistence: persists namespace references as bind mounts/files under `baseDir`; removal unmounts and deletes them.

Dependencies/integration: uses CNI `ns`, containerd mount helpers, `golang.org/x/sys/unix`, and `/proc`. Sandbox code can pass `GetPath` to runtimes or call `Do` to execute in the namespace.

Risks: requires privileges for unshare, setns, bind mount, and unmount. Thread locking and restoration are critical; failure can affect the running thread's namespace. Cleanup must handle stale paths.

Test signals: no direct tests in subset; integration should cover create/load/remove, pid-based namespace, closed detection, and `Do` execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/netns/netns_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/netns/netns_other.go -->
# sources/cloud-native/containerd/pkg/netns/netns_other.go

Purpose: non-Linux, non-Windows stub for network namespace APIs.

Important APIs/types/functions: `errNotImplementedOnUnix`; `NetNS` stores `path`; `NewNetNS`, `NewNetNSFromPID`, `Remove`, and `Closed` return not implemented; `LoadNetNS` returns a path wrapper; `GetPath` returns the stored path.

Control flow: all operational methods are immediate stubs. Load/get path remain available so callers can carry opaque namespace identifiers where supported elsewhere.

State/persistence: no namespace creation or cleanup. Only in-memory path storage.

Dependencies/integration: selected by build tag `!windows && !linux`, preserving package API shape across Unix-like platforms without Linux netns support.

Risks: callers must handle not-implemented errors. `LoadNetNS` returning a value does not imply the namespace can be removed or entered on these platforms.

Test signals: compile-time API compatibility is the main signal; platform tests should assert not-implemented behavior where relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/netns/netns_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/netns/netns_windows.go -->
# sources/cloud-native/containerd/pkg/netns/netns_windows.go

Purpose: Windows network namespace implementation backed by HCN namespaces.

Important APIs/types/functions: `NewNetNS` creates an `hcn.HostComputeNamespace` and stores its ID as `path`; `NewNetNSFromPID` is not implemented; `LoadNetNS` wraps an existing ID; `Remove` gets the namespace by ID and deletes it, treating not-found as success; `Closed` returns true when HCN reports not found; `GetPath` returns the ID.

Control flow: create, get, delete, and not-found classification are delegated to hcsshim HCN APIs. Remove is idempotent.

State/persistence: namespace state lives in Windows HCN. `NetNS.path` is an HCN namespace ID rather than a filesystem path.

Dependencies/integration: imports `github.com/Microsoft/hcsshim/hcn`. Windows sandbox networking can use the returned ID.

Risks: pid-based loading and `Do` are unsupported. HCN errors other than not-found propagate. Naming the ID as `path` preserves API shape but can confuse callers expecting a filesystem path.

Test signals: Windows integration tests should cover create/delete/idempotent remove, closed detection, and HCN not-found handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/netns/netns_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/client.go -->
# sources/cloud-native/containerd/pkg/oci/client.go

Purpose: defines the small client/image interfaces that OCI spec generation options need, avoiding direct dependency on the full containerd client type.

Important APIs/types/functions: `Client` exposes `ImageService`, `ContentStore`, `SnapshotService(name)`, and `EventsService`. `Image` exposes `Name`, `Target`, `Labels`, `Unpack`, `RootFS`, `Size`, `Usage`, `Config`, `IsUnpacked`, `ContentStore`, and `Platform`.

Control flow: interface-only file. Spec options call these methods to fetch image config blobs, snapshot mounts, platform information, and optional mount manager extensions.

State/persistence: no state directly. Methods represent access to persisted content, snapshots, images, and event services.

Dependencies/integration: imports containerd core services, snapshotters, image metadata, containers, and OCI descriptors. Used heavily by `spec.go` and `spec_opts.go`.

Risks: interface drift can break alternate client implementations and tests. Some spec options assume `Container.Snapshotter` and `SnapshotKey` are set when rootfs lookup is needed.

Test signals: fake images and clients in `spec_opts_test.go` validate enough of this interface for image config and rootfs user lookup paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/mounts.go -->
# sources/cloud-native/containerd/pkg/oci/mounts.go

Purpose: default OCI mounts for general Unix/Linux-style containers, plus a no-op OS mount hook for non-FreeBSD builds.

Important APIs/types/functions: `defaultMounts()` returns `proc`, `tmpfs` mounts for `/dev`, `/dev/shm`, `/dev/pts`, `/run`, `sysfs`, and cgroup. Each mount includes standard options such as `nosuid`, `noexec`, `nodev`, `mode=755`, `ptmxmode=0666`, and `size=65536k`. `appendOSMounts` is a no-op in this file.

Control flow: default spec generation calls `defaultMounts` when populating Unix specs. Image config handling may call `appendOSMounts`, which only changes behavior on FreeBSD.

State/persistence: no persistence; mount entries become part of the generated OCI spec.

Dependencies/integration: uses OpenContainers runtime-spec `specs.Mount`. Integrated by `populateDefaultUnixSpec` and spec options such as `WithDevShmSize` and `WithoutMounts`.

Risks: defaults are security-sensitive. Changing mount options can affect container isolation, device behavior, or compatibility. Cgroup mount defaults may not match all cgroup v2 environments.

Test signals: spec and spec options tests validate default spec shape, `/dev/shm` sizing, and mount removal behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/mounts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/mounts_freebsd.go -->
# sources/cloud-native/containerd/pkg/oci/mounts_freebsd.go

Purpose: FreeBSD-specific OCI mount defaults and OS-dependent image mount hook.

Important APIs/types/functions: `defaultMounts()` returns FreeBSD mount entries for `/dev`, `/dev/fd`, `/dev/fuse`, `/dev/null`, `/dev/random`, `/dev/urandom`, `/dev/zero`, `/proc`, and `/tmp`. `appendOSMounts(s, os)` appends additional defaults when the image OS is `linux` or `freebsd`.

Control flow: default spec population gets FreeBSD defaults. Image config processing can append Linux/FreeBSD compatibility mounts based on image OS.

State/persistence: generated OCI spec mount list only.

Dependencies/integration: build-selected on FreeBSD. Uses runtime-spec mount definitions.

Risks: device and procfs mount behavior is platform-specific and security-sensitive. Appending mounts based on image OS can duplicate or conflict with caller-supplied mounts if not managed carefully.

Test signals: FreeBSD build/integration tests should validate generated spec mounts and image OS handling. General mount tests do not fully cover this platform-specific file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/mounts_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec.go -->
# sources/cloud-native/containerd/pkg/oci/spec.go

Purpose: core OCI runtime spec generation, default population, spec file reading, and descriptor conversion helpers.

Important APIs/types/functions: `Spec` aliases `specs.Spec`; `ConfigFilename = "config.json"`; `ReadSpec` loads JSON from a bundle path; `GenerateSpec` and `GenerateSpecWithPlatform` create default specs then apply `SpecOpts`; `ApplyOpts` runs options sequentially. Default helpers populate Unix, Windows, and Darwin specs with process, root, namespaces, mounts, capabilities, seccomp, masked/readonly paths, and Windows layer folders. `DescriptorFromProto` and `DescriptorToProto` convert between containerd protobuf and OCI descriptors.

Control flow: `GenerateSpecWithPlatform` seeds an empty spec, calls `generateDefaultSpecWithPlatform`, then applies options in order. Platform selection uses parsed OS strings, with Unix/Linux defaults, Windows defaults, and Darwin defaults.

State/persistence: reads existing `config.json` via `ReadSpec`; otherwise returns in-memory specs that are later persisted by runtime/bundle code.

Dependencies/integration: depends on containerd API types, platforms, runtime-spec, and image-spec. Spec options in `spec_opts.go` compose on this base.

Risks: default security settings are high impact. Option order is significant and can overwrite defaults. Platform mismatch can create invalid specs.

Test signals: `spec_test.go` validates generation, platform selection, TTY, namespaces, capabilities, privileged behavior, descriptor conversion, and user file symlink handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts.go

Purpose: main library of `SpecOpts`, the composable functions that mutate generated OCI specs for process args/env, image config, users/groups, namespaces, mounts, security, devices, and resources.

Important APIs/types/functions: `SpecOpts` and `Compose`; initialization helpers `setProcess`, `setRoot`, `setLinux`, `setResources`, `setCPU`, and `setCapabilities`; defaults (`WithDefaultSpec`, `WithDefaultSpecForPlatform`); config loaders (`WithSpecFromBytes`, `WithSpecFromFile`, `WithImageConfigArgs`); process/env opts; namespace/cgroup opts; user/group lookup helpers (`WithUser`, `WithUserID`, `WithUsername`, `WithAdditionalGIDs`, `WithAppendAdditionalGroups`, `UserFromFS`, `GIDFromFS`); capability opts; security opts; resource opts; device opts; Windows opts; `openUserFile`.

Control flow: options are closures applied in caller order. Many options lazily initialize missing spec sections, then mutate only relevant Linux or Windows branches. Image config reads the image config descriptor/blob, unmarshals OCI image JSON, applies env/args/cwd/user, and handles Windows `ArgsEscaped`.

State/persistence: no direct persistence. Some options read image content, snapshot mounts, rootfs files, env files, or spec JSON; output is an in-memory OCI spec.

Dependencies/integration: integrates with snapshot services, mount/fsview helpers, user parsing, namespaces, runtime-spec, image-spec, errdefs, and platform-specific files.

Risks: option order can silently override prior fields. Rootfs user/group lookup relies on safe fs access and read-only mounts. Resource options are no-ops on wrong platform, which can hide caller mistakes. Windows command-line escaping is subtle.

Test signals: broad tests in `spec_opts*_test.go` cover env merging, image config args, users/groups, capabilities, mounts, `/dev/shm`, resources, devices, Windows command lines, and path env defaults.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_linux.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_linux.go

Purpose: Linux-specific spec options for host devices, arbitrary devices, Linux capabilities, and command argument escaping placeholder.

Important APIs/types/functions: `WithHostDevices` appends all devices from `HostDevices` into `s.Linux.Devices`. `WithDevices(devicePath, containerPath, permissions)` recursively discovers devices from a host path, appends them to the spec, and adds matching cgroup allow rules. `WithAllCurrentCapabilities` reads the current process capabilities and applies them; `WithAllKnownCapabilities` applies all known capabilities. Linux `escapeAndCombineArgs` panics because Windows-only code should call the escaping implementation.

Control flow: device options call `setLinux` and `setResources`, then append devices and cgroup rules. Capability options delegate to `cap.Current` or `cap.Known` and then `WithCapabilities`.

State/persistence: generated spec only; reads `/dev` or device paths.

Dependencies/integration: uses `golang.org/x/sys/unix`-backed device helpers in `utils_unix.go` and `kernel.org/pub/linux/libs/security/libcap/cap`.

Risks: host-device passthrough and cgroup rules are privilege-sensitive. Recursive device discovery must avoid symlink and non-device surprises. Current capabilities depend on caller process state.

Test signals: `spec_opts_linux_test.go` covers capability set/add/drop and device discovery/follow symlink behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_linux_test.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_linux_test.go

Purpose: Linux-specific tests for capabilities and device helpers.

Important APIs/types/functions: `TestSetCaps`, `TestAddCaps`, and `TestDropCaps` validate bounding/effective/permitted/inheritable behavior. `TestGetDevices` creates temporary character device nodes and validates recursive discovery and container paths. `TestWithLinuxDeviceFollowSymlinks` verifies symlink resolution behavior for device specs.

Control flow: tests construct specs, apply options, and compare capability lists or device entries. Device tests require mknod-capable environments and skip where unsupported.

State/persistence: temporary filesystem nodes only.

Dependencies/integration: uses Linux device syscalls, runtime-spec types, and package helpers.

Risks: device tests may be skipped or fail in restricted CI without privileges. Capability ordering and host cap availability can vary.

Test signals: protects cgroup device rule generation, recursive device path handling, symlink-following option semantics, and capability mutation invariants.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_nonlinux.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_nonlinux.go

Purpose: non-Linux stubs for Linux capability propagation options.

Important APIs/types/functions: `WithAllCurrentCapabilities` and `WithAllKnownCapabilities` both delegate to `WithCapabilities(defaultUnixCaps())`.

Control flow: no host capability inspection occurs; the default Unix capability list is applied to the spec.

State/persistence: generated spec only.

Dependencies/integration: selected on non-Linux platforms to preserve `SpecOpts` API compatibility without libcap/Linux syscalls.

Risks: semantics differ from Linux because current process capabilities are not inspected. Callers that expect host cap reflection should account for platform behavior.

Test signals: compile-time coverage and general capability tests on non-Linux should confirm defaults are applied without platform syscalls.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows.go

Purpose: non-Windows default PATH option for OCI process specs.

Important APIs/types/functions: `WithDefaultPathEnv` sets or replaces `PATH` with `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` through `WithEnv`.

Control flow: option delegates to env merge logic, so an existing `PATH` entry is replaced while other environment variables are preserved.

State/persistence: generated spec process environment only.

Dependencies/integration: selected on all non-Windows platforms. Used by callers that want Docker-like default Unix PATH behavior.

Risks: hardcoded Unix path may be inappropriate for unusual images or minimal rootfs layouts. It only mutates the spec and does not verify path existence.

Test signals: `spec_opts_nonwindows_test.go` verifies exact PATH value and replacement behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows_test.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows_test.go

Purpose: tests non-Windows default PATH injection.

Important APIs/types/functions: `TestWithDefaultPathEnv` applies `WithDefaultPathEnv` to a spec and asserts the expected Unix PATH appears in `s.Process.Env`.

Control flow: create spec, apply option, inspect env.

State/persistence: none.

Dependencies/integration: same-package test for the build-tagged non-Windows implementation.

Risks: narrow coverage; it does not test replacement of a preexisting PATH or interaction with other env vars in this file, though shared env tests cover merge behavior.

Test signals: guards the exact default PATH string used by non-Windows containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_nonwindows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_test.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_test.go

Purpose: broad platform-neutral tests for the main `SpecOpts` library.

Important APIs/types/functions: defines fake content/image helpers, then tests env replacement, default spec platform selection, process cwd, env appending, mounts, spec-from-file, memory/swap/pids/blockio/cpu options, TTY size, user namespace mappings, image config args, `/dev/shm` size, mount removal, parent cgroup devices, Windows device/resource options, and helper equality checks.

Control flow: tests construct minimal specs or fake images, apply one or more options, and inspect targeted fields. Image config tests serialize OCI image configs into fake content blobs so production `WithImageConfigArgs` paths run.

State/persistence: temporary files for spec JSON and in-memory fake content store.

Dependencies/integration: runtime-spec, image-spec, content store interfaces, and testify/Go testing.

Risks: many tests validate field mutation but not runtime execution. Some Linux-specific effects are skipped or no-op depending on spec platform fields.

Test signals: strongest regression suite for option order, env merging, resource initialization, image command semantics, `/dev/shm` option replacement, and cross-platform no-op behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_unix.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_unix.go

Purpose: Unix non-Linux device and argument helper implementation.

Important APIs/types/functions: `WithHostDevices` appends devices returned by `HostDevices` to `s.Linux.Devices`. `WithDevices(devicePath, containerPath, permissions)` appends devices found by `getDevices` but does not add Linux cgroup device rules in this Unix non-Linux variant. `escapeAndCombineArgs(args)` joins arguments with spaces.

Control flow: options initialize the Linux section and append discovered devices. `escapeAndCombineArgs` is simple concatenation for non-Windows builds that need a compile-time symbol.

State/persistence: generated spec only; reads host device metadata.

Dependencies/integration: selected by Unix non-Linux build constraints and depends on `utils_unix.go` device helpers.

Risks: adding Linux section on non-Linux Unix platforms may be an API compatibility compromise. The simple argument combiner is not shell-safe and should not be used as Windows escaping.

Test signals: `spec_opts_unix_test.go` covers image config without env and umask behavior on Unix specs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_unix_test.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_unix_test.go

Purpose: Unix-specific tests for image config defaults and umask option.

Important APIs/types/functions: `TestWithImageConfigNoEnv` verifies default Unix environment is applied when image config has no env. `TestWithUmask_SetsUmaskOnEmptySpec` and `TestWithUmask_WithDefaultSpec` assert `WithUmask` initializes process state and stores a pointer to the requested umask value.

Control flow: create fake image/spec, apply options, inspect process env and user umask fields.

State/persistence: in-memory fake image content only.

Dependencies/integration: uses shared fake image helpers from `spec_opts_test.go`.

Risks: does not cover invalid umask ranges because the option stores raw uint32 without validation.

Test signals: guards default Unix env fallback in image config and confirms `WithUmask` works both before and after default spec population.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_user_test.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_user_test.go

Purpose: detailed tests for OCI user, group, and supplemental group resolution from container rootfs files.

Important APIs/types/functions: tests cover `WithUser`, `WithUserID`, `WithUsername`, `WithAdditionalGIDs`, `WithAppendAdditionalGroups`, and missing `/etc/group` behavior. Cases include numeric uid/gid, username/groupname, mixed forms, out-of-range IDs, missing passwd/group files, rootfs absolute-path requirements, and additional group append by name or gid.

Control flow: tests create temporary rootfs layouts with synthetic `etc/passwd` and `etc/group`, configure unmanaged root paths, apply user-related options, and assert `s.Process.User` fields or errors.

State/persistence: temporary rootfs files only.

Dependencies/integration: production user parsing and `openUserFile` paths are exercised through real filesystem reads.

Risks: rootfs parsing behavior can vary if Go or `moby/sys/user` changes. Tests focus on unmanaged rootfs paths rather than snapshotter-mounted rootfs.

Test signals: protects Docker/OCI-compatible `USER` parsing, fallback gid behavior, supplemental group lookup, error classification for missing groups, and additional-gid preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_user_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_windows.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_windows.go

Purpose: Windows-specific spec option helpers and stubs for Linux-only device behavior.

Important APIs/types/functions: `escapeAndCombineArgs` uses `windows.EscapeArg` for command-line construction. `WithProcessCommandLine` sets `s.Process.CommandLine` and clears args. `WithHostDevices` is a no-op, `DeviceFromPath` returns not implemented, and `WithDevices` is a no-op. `WithDefaultPathEnv` sets Windows PATH to `c:\Windows\System32;c:\Windows`.

Control flow: Windows command-line option initializes process state before mutation. Default PATH delegates to shared env merge logic. Linux device APIs remain callable but intentionally do nothing or return not implemented.

State/persistence: generated spec only.

Dependencies/integration: selected on Windows; uses `github.com/Microsoft/go-winio/pkg/guid` for not-implemented error construction and `golang.org/x/sys/windows` escaping.

Risks: Windows command-line escaping must match HCS/runtime expectations. No-op host devices can hide caller assumptions from cross-platform code.

Test signals: `spec_opts_windows_test.go` exercises command-line/image arg escaping and Windows resource/default PATH options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_windows_test.go -->
# sources/cloud-native/containerd/pkg/oci/spec_opts_windows_test.go

Purpose: Windows-specific tests for resources, networking flags, command-line generation, image config args, and default PATH.

Important APIs/types/functions: tests cover `WithWindowsCPUCount`, `WithWindowsIgnoreFlushesDuringBoot`, `WithWindowNetworksAllowUnqualifiedDNSQuery`, combinations of process args and image config entrypoint/cmd with Docker `ArgsEscaped`, `WithImageConfigArgsWindows`, `WithImageConfigArgsEscapedWindows`, and `WithDefaultPathEnv`.

Control flow: fake image configs are applied to Windows specs with or without user args, then assertions check whether `Process.Args` or `Process.CommandLine` is populated and escaped correctly.

State/persistence: in-memory fake image content only.

Dependencies/integration: Windows runtime-spec fields and shared fake image helpers.

Risks: escaping expectations are subtle and tightly coupled to Docker image config semantics. Tests are platform/build-tag specific.

Test signals: strong regression coverage for Windows command activation rules, especially interaction between image `Entrypoint`, `Cmd`, user args, and deprecated `ArgsEscaped`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_opts_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_test.go -->
# sources/cloud-native/containerd/pkg/oci/spec_test.go

Purpose: tests core spec generation, defaults, selected options, descriptor conversions, and safe user-file opening through absolute symlinks.

Important APIs/types/functions: `TestGenerateSpec`, `TestGenerateSpecWithPlatform`, `TestSpecWithTTY`, `TestWithLinuxNamespace`, capability tests, default Windows/Unix population tests, `TestWithPrivileged`, `TestOpenUserFile_AbsoluteSymlink`, and `TestGroupLookup_AbsoluteSymlink`. `readLinkFS` is a test filesystem implementing `ReadLink`.

Control flow: tests build specs through generation helpers or direct options, then inspect fields. Symlink tests simulate NixOS-style absolute symlinks and ensure `openUserFile` reanchors them inside the root fs.

State/persistence: temporary or in-memory filesystem state.

Dependencies/integration: runtime-spec defaults, platform parsing, user/group parsing, and descriptor API types.

Risks: generated default specs are broad and can change for valid runtime reasons, making tests sensitive to default policy changes. Symlink behavior depends on filesystem interface support.

Test signals: protects top-level generation behavior, platform-specific defaults, security option behavior, and the rootfs symlink compatibility path added for stricter Go fs validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/utils_unix.go -->
# sources/cloud-native/containerd/pkg/oci/utils_unix.go

Purpose: Unix device discovery and conversion helpers used by OCI device-related spec options.

Important APIs/types/functions: `ErrNotADevice`; package-level `osReadDir` and `deviceFromPath` variables for test injection; `HostDevices` discovers host devices under `/dev`; `getDevices(path, containerPath)` recursively walks a device path, preserving container-relative path mapping; `DeviceFromPath(path)` stats a node and returns an OCI `LinuxDevice` with type, path, major/minor, file mode, uid, and gid.

Control flow: `getDevices` stats the path; non-directory device nodes are converted directly, directories are read and recursed. `DeviceFromPath` rejects non-device modes and maps char, block, fifo, and regular device-ish modes to OCI types where supported.

State/persistence: reads host filesystem metadata only; outputs spec device entries.

Dependencies/integration: uses `os`, `path/filepath`, `syscall`, and runtime-spec. Linux options add returned devices to specs and cgroup rules.

Risks: traversing `/dev` can hit permissions, broken entries, or namespace-specific views. Device major/minor extraction is platform-specific. Test injection globals must be restored.

Test signals: `utils_unix_test.go` covers read-dir failures, user namespace behavior, conversion failures, and all-valid discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/utils_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/utils_unix_test.go -->
# sources/cloud-native/containerd/pkg/oci/utils_unix_test.go

Purpose: tests Unix host-device discovery error handling and success behavior with injectable filesystem/device helpers.

Important APIs/types/functions: `cleanupTest` restores package-level `osReadDir` and `deviceFromPath`. Tests cover `HostDevices` read-dir failure, read-dir failure in user namespace, `DeviceFromPath` failure, failure in user namespace, and all-valid device discovery.

Control flow: tests monkey-patch helper variables to return synthetic directory entries/devices or errors, call `HostDevices`, and assert returned devices or error behavior.

State/persistence: mutates package-level function variables during tests and restores them.

Dependencies/integration: uses Linux user namespace detection paths and OCI device structs.

Risks: package-level monkey-patching makes tests order-sensitive if run in parallel. User namespace behavior depends on environment and may use different expected error tolerance.

Test signals: protects error propagation/ignore policy for host device discovery and confirms valid devices are returned when all injected helpers succeed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oci/utils_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oom/oom.go -->
# sources/cloud-native/containerd/pkg/oom/oom.go

Purpose: Linux OOM watcher interface shared by cgroup v1 and v2 implementations.

Important APIs/types/functions: `Watcher` requires `Close() error`, `Run(ctx context.Context)`, and `Add(id string, cg any) error`.

Control flow: interface-only. Implementations add cgroups to be watched, run an event loop, publish task OOM events, and close resources.

State/persistence: no state directly. Implementations hold kernel event fds, channels, or cgroup references.

Dependencies/integration: build-tagged Linux. Used by runtime/task services that need a common abstraction over cgroup versions.

Risks: `Add` accepts `any`, so type errors are runtime errors in implementations. Consumers must run the watcher loop and close it on shutdown.

Test signals: implementation tests should assert type checking, event publication, cancellation, and cleanup for both cgroup versions. This file provides compile-time contract only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oom/oom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oom/v1/v1.go -->
# sources/cloud-native/containerd/pkg/oom/v1/v1.go

Purpose: cgroup v1 OOM watcher using epoll on cgroup OOM event fds.

Important APIs/types/functions: `New(publisher)` creates an epoll fd and returns an `epoller`; `epoller` holds mutex, epoll fd, publisher, and fd-to-item map; `Add(id, cgx)` type-checks `cgroup1.Cgroup`, obtains `OOMEventFD`, registers it with epoll, and stores metadata; `Run(ctx)` waits for epoll events and calls `process`; `process` flushes the fd, removes deleted cgroups, and publishes `TaskOOM`; `flush` reads 8 bytes.

Control flow: event loop blocks in `EpollWait` until context cancellation or events. Each event is mapped back to a container ID, deleted cgroups are cleaned up, and active cgroups emit runtime OOM events.

State/persistence: in-memory fd map plus kernel event fds. No persistence.

Dependencies/integration: depends on containerd events/runtime topics, cgroups v1, sys EINTR helper, unix epoll, and logging.

Risks: fd lifecycle is delicate; missed deletion cleanup leaks fds. Publish errors are logged only. `flush` errors are ignored by `process`.

Test signals: should cover wrong cgroup type, epoll registration, deletion cleanup, context cancellation, and event publication.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oom/v1/v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oom/v2/v2.go -->
# sources/cloud-native/containerd/pkg/oom/v2/v2.go

Purpose: cgroup v2 OOM watcher built on `cgroup2.Manager.EventChan`.

Important APIs/types/functions: `New(publisher)` returns a `watcher` with `itemCh`. `Run(ctx)` tracks last `OOMKill` count per container ID and publishes `TaskOOM` only when the count increases. `Add(id, cgx)` type-checks `*cgroupsv2.Manager`, gets event and error channels, and starts a goroutine forwarding events/errors into `itemCh`. `Close` is currently a no-op.

Control flow: `Add` creates one forwarding goroutine per cgroup. `Run` selects on context or forwarded items, drops state on errors, publishes on increasing `OOMKill`, and updates last-seen counters.

State/persistence: in-memory last OOM count map and goroutines. Cgroup state comes from kernel cgroup v2 files through the manager.

Dependencies/integration: containerd event publisher/runtime topic, cgroups v2 manager, and logging.

Risks: comment notes manager event goroutine cannot currently be explicitly closed; it exits mainly on cgroup deletion/error. If `Run` is not active, forwarding goroutines can block on `itemCh`. Publish errors are logged only.

Test signals: should cover type mismatch, OOMKill counter increase/de-duplication, error-state cleanup, and context cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/oom/v2/v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_linux.go -->
# sources/cloud-native/containerd/pkg/os/mount_linux.go

Purpose: Linux `RealOS` mount operations.

Important APIs/types/functions: `RealOS.Mount` calls `mount.Mount`; `RealOS.Unmount` calls `mount.Unmount`; `RealOS.LookupMount` calls `mount.Lookup`.

Control flow: thin delegation from the OS abstraction to containerd's mount package.

State/persistence: affects host mount table when called. Lookup reads mount state.

Dependencies/integration: selected on Linux; implements the mount methods of `pkg/os.OS`. Used by code that wants an injectable OS interface for filesystem and mount operations.

Risks: mount/unmount require privileges and can affect host state. Errors are returned without wrapping, so callers need context.

Test signals: fake OS tests outside this list can validate call recording; integration tests should cover mount behavior on Linux with appropriate privileges.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_other.go -->
# sources/cloud-native/containerd/pkg/os/mount_other.go

Purpose: non-Linux, non-FreeBSD, non-Windows lookup-mount stub.

Important APIs/types/functions: `RealOS.LookupMount(path)` returns an empty `mount.Info` and `errdefs.ErrNotImplemented`.

Control flow: immediate stub return.

State/persistence: none.

Dependencies/integration: build tag `!windows && !linux && !freebsd`; preserves `OS` interface compilation on platforms where mount lookup is unsupported.

Risks: callers must handle `ErrNotImplemented`. The zero `mount.Info` must not be used after an error.

Test signals: platform compile checks and any non-supported-platform tests should verify not-implemented classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_unix.go -->
# sources/cloud-native/containerd/pkg/os/mount_unix.go

Purpose: Unix non-Linux mount and unmount implementation for `RealOS`.

Important APIs/types/functions: `RealOS.Mount` delegates to `mount.Mount`; `RealOS.Unmount` delegates to `mount.Unmount`.

Control flow: direct delegation.

State/persistence: changes host mount state when called.

Dependencies/integration: build tag `!windows && !linux`; combined with platform-specific lookup implementation. Implements `OS` interface on Unix-like systems.

Risks: mount semantics and required privileges vary by platform. Errors are not wrapped with operation context.

Test signals: platform integration tests should cover successful mount/unmount and error propagation; fake OS can be used by higher-level code to avoid real mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_windows.go -->
# sources/cloud-native/containerd/pkg/os/mount_windows.go

Purpose: Windows stubs for mount operations in the `RealOS` abstraction.

Important APIs/types/functions: `RealOS.Mount`, `RealOS.Unmount`, and `RealOS.LookupMount` return `errdefs.ErrNotImplemented` with zero values where needed.

Control flow: immediate stub returns.

State/persistence: none; Windows mount-like operations are not implemented through this interface.

Dependencies/integration: selected on Windows. Keeps the cross-platform `OS` interface satisfied.

Risks: callers must not assume mount support on Windows. Higher-level code should branch on `errdefs.ErrNotImplemented` where mount operations are optional.

Test signals: Windows compile checks and behavior tests should validate not-implemented errors rather than nil success.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/mount_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os.go -->
# sources/cloud-native/containerd/pkg/os/os.go

Purpose: injectable filesystem/OS abstraction plus real implementation for common operations.

Important APIs/types/functions: `OS` interface includes directory creation/removal, stat, symlink resolution, scoped symlink following, file copy/write, mount/unmount/lookup, and hostname. `RealOS` implements common methods: `MkdirAll`, `RemoveAll`, `Stat`, `FollowSymlinkInScope`, `CopyFile`, `WriteFile`, and `Hostname`.

Control flow: methods delegate to standard library or containerd helpers. `CopyFile` opens source and destination with requested permissions, copies contents, and closes files. `FollowSymlinkInScope` delegates to `fs.RootPath`.

State/persistence: performs real filesystem writes/removes/copies and host lookups.

Dependencies/integration: used by code that benefits from fakeable OS operations. Depends on `github.com/containerd/continuity/fs` and platform-specific files for symlink/mount behavior.

Risks: `CopyFile` can partially write destination if copy fails. File permissions and symlink scope behavior are security-sensitive. RealOS methods return raw errors with limited context in some cases.

Test signals: fake implementation under `pkg/os/testing` supports higher-level tests; platform-specific tests cover symlink resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_unix.go -->
# sources/cloud-native/containerd/pkg/os/os_unix.go

Purpose: Unix symlink resolution implementation for `RealOS`.

Important APIs/types/functions: `RealOS.ResolveSymbolicLink(path)` calls `os.Lstat`, returns the path unchanged when it is not a symlink, and otherwise returns `filepath.EvalSymlinks(path)`.

Control flow: lstat first avoids resolving non-symlink paths unnecessarily. Symlink paths are fully evaluated through the standard library.

State/persistence: reads filesystem metadata only.

Dependencies/integration: build tag `!windows`; satisfies `OS.ResolveSymbolicLink` for Unix-like systems.

Risks: `EvalSymlinks` resolves the full path and may fail on missing intermediate components or permission issues. It is not scoped; callers needing scope containment should use `FollowSymlinkInScope`.

Test signals: platform tests should cover symlink and non-symlink paths, missing paths, and permission errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_windows.go -->
# sources/cloud-native/containerd/pkg/os/os_windows.go

Purpose: Windows path and symlink resolution for `RealOS`, using Win32 handle APIs to resolve files, directories, volume GUID paths, mount points, and UNC paths.

Important APIs/types/functions: `openPath` opens file or directory handles via `windows.CreateFile` with backup semantics. Constants define `GetFinalPathNameByHandle` flags. `getFinalPathNameByHandle` manages a pooled UTF-16 buffer and retries when larger buffers are needed. `resolvePath` opens a handle, prefers volume GUID final paths, falls back to DOS/UNC handling, and normalizes `\\?\UNC\` to `\\server\share`. `RealOS.ResolveSymbolicLink` evaluates symlinks with Windows-specific handling.

Control flow: resolution is handle-based to avoid fragile manual path parsing. UNC paths get fallback behavior when GUID lookup returns `ERROR_PATH_NOT_FOUND`.

State/persistence: reads filesystem and volume metadata; no writes.

Dependencies/integration: selected on Windows; uses `golang.org/x/sys/windows`. Supports higher-level code needing stable resolved paths, including volume mount points.

Risks: Windows path syntax is complex; extended-length, trailing-dot, mount point, and UNC edge cases can still differ from Go path functions. Handles must always be closed.

Test signals: `os_windows_test.go` outside this work item covers symlinks, VHD volume mount paths, and resolved path behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_windows.go -->
