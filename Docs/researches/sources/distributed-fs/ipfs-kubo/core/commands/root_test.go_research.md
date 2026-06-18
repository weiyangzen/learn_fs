# sources/distributed-fs/ipfs-kubo/core/commands/root_test.go

Purpose: validates the entire registered command tree rooted at `Root`.

Important APIs/types/functions: `TestCommandTree` invokes `Root.DebugValidate()` and prints any returned errors grouped by command path.

Control flow: the test treats a nil error map as success; otherwise it records each command and validation error with `t.Errorf`.

State and persistence behavior: no durable state. It only inspects in-memory command definitions.

Dependencies and integration points: depends on `root.go` initialization and every subcommand attached to `Root`. It is a broad schema/sanity test rather than behavioral coverage.

Risks: validation catches structural command issues but not runtime command behavior, repo mutation, network behavior, or text/JSON output correctness beyond command metadata.

Test signals: a failure here usually points to malformed command declarations, incompatible encoders/types, or invalid argument/option definitions introduced anywhere in the root command tree.
