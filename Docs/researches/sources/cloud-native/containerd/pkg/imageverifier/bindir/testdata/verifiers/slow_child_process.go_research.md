# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/slow_child_process.go

Purpose: timeout and descendant-process cleanup fixture. It re-executes itself as a child that loops forever, then waits on that child, forcing the verifier runner to kill process descendants on timeout.

Important APIs/types/functions: `main` has two modes. With `-sleep-forever`, it prints a message and spins forever. Without the flag, it starts `os.Args[0] -sleep-forever`, captures combined output, prints it, and panics if the child exits with an error.

Control flow: parent blocks on `cmd.CombinedOutput`; child never exits. Only external cancellation should terminate the process tree.

State/persistence: transient processes only.

Dependencies/integration: used by `bindir_test.go` to exercise Unix process-group killing and Windows job-object cleanup.

Risks: a broken cleanup implementation can leave an infinite child consuming CPU. The child loop is intentionally busy rather than sleeping, so timeout bounds must be short and cleanup reliable.

Test signals: strongest signal for process tree cleanup and command context cancellation semantics in `processes_unix.go` and `processes_windows.go`.
