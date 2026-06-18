## sources/cloud-native/moby/daemon/internal/filters/example_test.go

Purpose: Documents `Args.MatchKVList` behavior as an executable Go example.

Important test: `ExampleArgs_MatchKVList` builds label filters for `image=foo` and `state=running`, then prints results for a missing filter key, nil sources, matching sources, and mismatching values.

Control flow and state: The example uses `NewArgs` and `Arg`, then calls `MatchKVList` with different source maps. The `// Output:` block verifies the user-facing semantics.

Dependencies and integration: Runs as a Go example test and documents package behavior for generated docs.

Risks covered: Confirms the "no values for key means no filtering" behavior and the "filter set with no sources fails" behavior. It does not cover key-only labels, multiple fields, or malformed values.

Persistence: None.
