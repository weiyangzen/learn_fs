# sources/distributed-fs/ipfs-kubo/test/cli/testutils/json.go

Purpose: tiny helper for constructing JSON strings in tests.

Important APIs: `JSONObj` is a `map[string]any` alias, and `ToJSONStr(m JSONObj) string` marshals it with `encoding/json`.

Control flow: `ToJSONStr` panics on marshal error and returns the JSON string otherwise.

State and persistence: no state.

Dependencies and integration points: used by tests that need compact inline JSON config or request bodies without repetitive marshal boilerplate.

Risks and test signals: map iteration order in JSON output may not be stable for string comparison. Panic behavior is acceptable for test setup but callers should avoid passing non-marshalable values.
