## sources/cloud-native/moby/daemon/internal/filters/parse.go

Purpose: Provides the daemon filter argument model: a map from filter keys to set-like string values, with JSON serialization, matching helpers, validation, and cloning.

Important APIs/types: `Args` owns `fields map[string]map[string]bool`. `KeyValuePair`, `Arg`, and `NewArgs` construct filters. Serialization APIs are `MarshalJSON`, `ToJSON`, `FromJSON`, and `UnmarshalJSON`. Query/mutation APIs include `Keys`, `Get`, `Add`, `Del`, `Len`, `Contains`, `Clone`, `Validate`, and `WalkValues`. Matching APIs are `MatchKVList`, `Match`, `ExactMatch`, `UniqueExactMatch`, `FuzzyMatch`, and `GetBoolOrDefault`.

Control flow: `FromJSON` first unmarshals the current map-of-map format, then falls back to legacy map-of-slice format and converts with `deprecatedArgs`; invalid input returns `invalidFilter`. Empty filter sets serialize to `{}` at JSON level and to an empty string through `ToJSON`. Matching semantics generally treat missing/empty filter values as "do not filter." `Match` first checks exact match and then regex matches each value, ignoring invalid regex patterns. Boolean parsing accepts only `0`, `1`, `false`, and `true`; missing values return the provided default.

State and persistence: State is in the `Args.fields` map. JSON is the persistence/interchange representation. `Clone` deep-copies nested maps to avoid shared mutation.

Dependencies and integration: Used throughout daemon APIs that accept filter query parameters. Depends on `encoding/json`, `regexp`, `strings`, and Go `maps.Copy`.

Risks: Map iteration order is nondeterministic for `Keys`, `Get`, `WalkValues`, and error value display. Regex matching treats filter values as regexes, so user-provided expressions can be expensive or surprising. `UnmarshalJSON` on a zero `Args` value requires valid map allocation from JSON; direct mutation on an uninitialized `Args{}` via `Add` would panic, so callers should use `NewArgs`.

Test signals: `parse_test.go` covers JSON formats, matching variants, add/delete, validation, walking, clone independence, and boolean parsing.
