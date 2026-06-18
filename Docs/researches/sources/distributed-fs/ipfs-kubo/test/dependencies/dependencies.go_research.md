## sources/distributed-fs/ipfs-kubo/test/dependencies/dependencies.go

Purpose: Go tools tracking file that pins test-only command dependencies in `go.mod` without linking them into production binaries.

Important APIs and control flow: the file is guarded by `//go:build tools`, declares package `tools`, and imports tool packages only for side effects. There is no runtime control flow or persistence.

Dependencies and integration points: imported tools include `gocovmerge`, `golangci-lint`, `cid-fmt`, `random-data`, `random-files`, `hang-fds`, `multihash`, and `gotestsum`. These binaries are used by sharness, CI, linting, coverage, and helper command targets under `test/bin`.

Risks: removing or renaming blank imports can silently drop tool versions from the module graph and break test harness builds. Because the build tag excludes it from normal builds, test signal is indirect: `go install` or make rules for test dependencies continue to resolve exact tool modules.
