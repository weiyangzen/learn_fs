# sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir_test.go

Purpose: integration-style tests for the `bindir` image verifier backend. The test builds standalone Go verifier binaries, arranges temporary verifier directories with deterministic names, and exercises verifier ordering, pass/fail aggregation, I/O handling, timeout behavior, output truncation, missing/empty directories, max-verifier limits, and child process cleanup.

Important APIs/types/functions: `buildGoVerifiers` compiles every verifier source in a directory with `go build`; `exeIfWindows` normalizes executable suffix expectations; `newBinDir` copies selected test binaries into a temp directory as sorted `verifier-N` entries; `TestBinDirVerifyImage` contains all behavioral subtests. The test also renders `testdata/verifier_templates` with file paths used to assert argv and stdin contents.

Control flow: setup builds all static and rendered verifier binaries once, then each subtest constructs a `Config` with `BinDir`, `MaxVerifiers`, and `PerVerifierTimeout`, calls `VerifyImage`, and asserts `Judgement.OK`, `Judgement.Reason`, and side effects. Rejection short-circuits after the first nonzero exit. The slow child test validates context timeout and platform process cleanup paths.

State/persistence: all state is temporary test state: compiled binaries, copied verifier directories, captured args/stdin files, and child processes. No containerd metadata is persisted.

Dependencies/integration: depends on the local Go toolchain, `tomlext.Duration`, OpenContainers descriptors, containerd logging, and testify. It directly tests `bindir.NewImageVerifier` and platform-specific `startProcess` implementations through real executables.

Risks: tests can be sensitive to Go toolchain availability, process scheduling, timeout values, pipe buffering, and Windows executable suffixes. Infinite-loop child fixtures make cleanup correctness important; leaks may only show as hanging tests or stray processes.

Test signals: strong coverage for verifier command contract (`-name`, `-digest`, descriptor JSON on stdin, descriptor media type), sorted execution, max verifier truncation, stdout/stderr truncation, missing/empty bin directories, reject reason formatting, timeout errors, and child process termination.
