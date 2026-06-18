# Research: sources/distributed-fs/ipfs-kubo/config/internal_test.go

Purpose: Locks default and JSON behavior for internal diagnostic flags.

Important APIs/types/functions: `TestInternalCheckFlagsDefaultEnabled` and `TestInternalCheckFlagsJSON`.

Control flow, state, and persistence: Pure JSON/in-memory tests. They verify zero-value flags resolve to enabled defaults, unset flags are omitted from JSON, and explicit false disables checks.

Dependencies and integration points: Exercises `Flag.WithDefault`, `json.Marshal`, and `json.Unmarshal` for `Internal`.

Risks and test signals: Narrow coverage, but important for operator-facing diagnostics because omitted config should not disable CGNAT/dead-listener checks.
