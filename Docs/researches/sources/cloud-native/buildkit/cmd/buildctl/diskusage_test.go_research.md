# Research: sources/cloud-native/buildkit/cmd/buildctl/diskusage_test.go

Purpose: provides a minimal integration smoke test for the `buildctl du` command.

Important function and flow: `testDiskUsage` runs `sb.Cmd("du")` against an integration sandbox and asserts that the command exits without error.

State and dependencies: depends on the integration sandbox daemon and worker cache state. It does not create specific cache records or validate output.

Risks and test signals: the test confirms basic command-to-daemon wiring and avoids output regressions only at the level of fatal errors. It does not verify table columns, summary math, filtering, template output, or verbose formatting.
