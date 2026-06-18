## sources/cloud-native/moby/daemon/internal/filters/parse_test.go

Purpose: Provides broad behavioral coverage for the filters package.

Important tests: JSON tests cover current map-of-map format, empty filters, `ToJSON`, invalid JSON, legacy map-of-slice compatibility, and wrapped invalid filter errors. Matching tests cover `MatchKVList`, regex matching through `Match`, exact and unique exact matching, prefix fuzzy matching, and contains. Mutation tests cover `Add`, `Del`, `Len`, `Clone`, and `WalkValues`. `TestValidate` checks unknown keys. `TestGetBoolOrDefault` covers truthy/falsy values, invalid values, conflicts, sorting of expected value slices, and wrapped errors.

Control flow and state: Tests frequently instantiate `Args` with map literals to exercise internal states directly, in addition to using `NewArgs`.

Dependencies and integration: Uses `gotest.tools/v3/assert` and cmp helpers. It tests unexported `invalidFilter` by staying in package.

Risks covered: Legacy compatibility, nil/empty behavior, invalid regex handling, exact matching semantics, and value conflicts. Gaps include randomized map order, very large regex patterns, and concurrent access; `Args` is not synchronized.

Persistence: Tests JSON as the external persistence/interchange form.
