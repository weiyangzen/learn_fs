# Research: sources/cloud-native/buildkit/cmd/buildctl/prune_test.go

Purpose: provides a minimal integration smoke test for the `buildctl prune` command.

Important function and flow: `testPrune` runs `sb.Cmd("prune")` against the sandbox and asserts no error. It does not seed specific cache entries or validate output.

State and dependencies: mutates sandbox cache state by asking the daemon to prune. It depends on the integration test harness and `stretchr/testify/require`.

Risks and test signals: this confirms basic command and RPC wiring but does not protect nuanced behavior such as keep-duration, storage limits, all/internal pruning, template mode, verbose mode, or reclaimed-byte summary.
