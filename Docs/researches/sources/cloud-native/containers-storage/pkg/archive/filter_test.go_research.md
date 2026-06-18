<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/filter_test.go

Purpose: tests external filter subprocess helper behavior.

Important APIs/types/functions: `TestTryProcFilter`.

Control flow: subtests verify three cases: a nonexistent command returns nil/false; `cat -` returns input unchanged; a shell command that writes stderr and exits 21 causes `io.ReadAll` to return an error containing stderr and exit status, and eventually calls the cleanup function.

State/persistence: no durable state; uses an atomic bool to observe cleanup.

Dependencies/integration: requires common Unix-like tools `cat` and `sh` in PATH for success/failure subtests.

Risks/test signal: protects error propagation and cleanup behavior. It does not test cached path invalidation, input read errors, or early reader closure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter_test.go -->
