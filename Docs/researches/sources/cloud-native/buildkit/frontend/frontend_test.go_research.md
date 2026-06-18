# sources/cloud-native/buildkit/frontend/frontend_test.go

## Purpose

This integration test file validates basic frontend gateway behavior against BuildKit workers: returning nil or empty results, reading files, reading directories, statting files, and evaluating refs.

## Important APIs, Types, And Functions

- `init` selects Docker, OCI, and containerd workers for integration coverage.
- `TestFrontendIntegration` registers test functions with the shared integration runner.
- `testReturnNil` verifies frontends can return nil or an empty result without failing the build.
- `testRefReadFile` checks full and ranged `Reference.ReadFile` behavior.
- `testRefReadDir` checks `Reference.ReadDir` with root/subdirectory and glob include patterns.
- `testRefStatFile` verifies `Reference.StatFile`.
- `testRefEvaluate` verifies lazy result evaluation succeeds for valid LLB and fails for invalid LLB.

## Control Flow

Each test creates a BuildKit client, prepares an optional local filesystem, defines a gateway frontend callback, then calls `client.Build`. Inside callbacks, local or scratch LLB is solved through the gateway client, refs are extracted, and gateway reference operations are asserted.

## State And Persistence Behavior

Tests create temporary directories via integration helpers and close BuildKit clients. They clear `ModTime` in directory listing expectations to avoid nondeterministic filesystem timestamps. No repository state is modified.

## Dependencies And Integration Points

The tests integrate the external client package, `llb`, gateway client frontend callbacks, integration sandbox utilities, worker initialization helpers, `fsutil`, and `fstest`.

## Risks And Edge Cases

The integration suite depends on worker availability and can be skipped or vary by worker backend configuration. Directory stat comparison normalizes only fields expected to vary, but other platform-specific fs metadata could still cause test differences. `testRefEvaluate` specifically catches the risk that refs stay lazy and errors surface late.

## Test Signals

These tests are primary signals for gateway reference filesystem APIs. They cover ranged reads including overruns, directory include patterns, stat equivalence, and evaluate error surfacing.
