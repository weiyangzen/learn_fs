# Research: sources/distributed-fs/ipfs-kubo/config/provide_test.go

Purpose: Tests provide strategy parsing, config validation, and selection logic.

Important APIs/types/functions: Tests cover `ParseProvideStrategy`, `MustParseProvideStrategy`, `ValidateProvideConfig` strategy/interval/Bloom/worker cases, and `ShouldProvideForStrategy`.

Control flow, state, and persistence: Pure in-memory tests. Table cases verify valid combinations, typo rejection, delimiter errors, `all` combination rejection, unique/entities constraints, interval zero migration guard, interval upper bound, Bloom minimum, positive workers, and OR behavior for combined strategies.

Dependencies and integration points: Uses `testify/assert` and `require`. Protects behavior consumed by provider setup and `ipfs add` fast-provide logic.

Risks and test signals: Strong for parser and basic validation. It does not exercise actual DHT providing, Bloom implementation, or persisted sweep resume behavior.
