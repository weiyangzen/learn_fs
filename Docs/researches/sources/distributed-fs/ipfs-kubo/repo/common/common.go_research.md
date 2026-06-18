# sources/distributed-fs/ipfs-kubo/repo/common/common.go

Purpose: provides map utilities used by repo config code to manipulate JSON-like `map[string]any` structures without losing user-specified keys.

Important APIs and control flow: `MapGetKV` traverses dot-separated keys and returns detailed errors for missing or non-map intermediate nodes. `MapSetKV` creates missing intermediate maps and writes the final value. `MapMergeDeep` clones the left map and recursively overlays right-side map values when both sides are maps; otherwise the right value replaces.

State and persistence: functions are in-memory only, but they directly affect persisted repo config because `fsrepo.SetConfig` and `SetConfigKey` read config JSON into maps, mutate or merge, and write back.

Dependencies and integration: depends on Go `maps`, `strings`, and `fmt`; used by `repo/fsrepo` to preserve unknown config fields and protect private key values during partial updates.

Risks and test signals: dot-path keys cannot address literal dots in key names. `MapSetKV` replaces nil intermediates but errors on non-map intermediates. Tests focus on deep merge copy/override semantics; get/set edge cases rely on integration coverage.
