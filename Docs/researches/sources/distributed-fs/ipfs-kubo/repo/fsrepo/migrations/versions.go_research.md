# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions.go

Purpose: reads and sorts distribution version lists from migration distribution sites.

Important APIs and control flow: `DistVersions` fetches `<dist>/versions`, scans lines, parses semver after trimming a leading `v`, ignores invalid lines, sorts ascending or descending, and returns `v`-prefixed versions. `LatestDistVersion` calls `DistVersions`, scans from newest to oldest, skips `-dev` always and `-rc` when `stableOnly`, and returns the first acceptable version.

State and persistence: no local persistence; fetches version file bytes through a `Fetcher`.

Dependencies and integration: used by `fetchMigrations` and `FetchBinary` selection. Depends on `blang/semver`.

Risks and test signals: invalid lines are silently ignored, and `strings.TrimLeft` removes any run of `v` characters rather than a single prefix. Tests validate non-empty sorted version lists and semver parse of latest.
