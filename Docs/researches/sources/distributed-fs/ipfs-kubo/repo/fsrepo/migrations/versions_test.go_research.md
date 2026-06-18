# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/versions_test.go

Purpose: checks version-list fetching and latest-version selection against the local test distribution.

Important APIs and control flow: `TestDistVersions` fetches and sorts versions descending for `go-ipfs`, requiring a non-empty result. `TestLatestDistVersion` fetches the latest version, checks basic length, and validates semver after dropping the leading `v`.

State and persistence: no writes; uses the shared test server and test distribution created in `setup_test.go`.

Dependencies and integration: exercises `NewHttpFetcher`, `DistVersions`, `LatestDistVersion`, and semver parsing.

Risks and test signals: coverage is broad enough for normal version files, but does not test `stableOnly`, dev/rc filtering edge cases, invalid-line-only files, or fetcher errors.
