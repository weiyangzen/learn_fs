# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/config_helpers.go

Purpose: supplies generic JSON-map mutation helpers for embedded migration converters.

Important APIs and control flow: includes dot-path getters/setters/deleters, move/copy/rename helpers, defaults, field transforms, section creation, safe map/slice casts, merging source maps into destination maps, slice append/replace helpers, string-map cloning, and empty-slice detection.

State and persistence: operates in memory on decoded config maps; changes are later persisted by `WriteConfig` through `BaseMigration`/`WithBackup`.

Dependencies and integration: used by the 16-to-17 migration to add AutoConf, rewrite bootstrap/DNS/routing/IPNS fields, and by 17-to-18 tests and helpers. Depends on Go `maps`, `slices`, `strings`, and `fmt`.

Risks and test signals: `SetField` replaces non-map intermediates with maps, which is convenient for repair but can discard malformed user data. Equality in `EnsureFieldIs` requires comparable values. Helpers are mostly covered indirectly by migration tests rather than direct unit tests.
