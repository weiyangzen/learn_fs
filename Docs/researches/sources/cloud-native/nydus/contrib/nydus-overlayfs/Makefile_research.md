# sources/cloud-native/nydus/contrib/nydus-overlayfs/Makefile

## Purpose
This Makefile builds and tests the `nydus-overlayfs` Go mount helper.

## Important APIs, Types, and Functions
Variables include `GIT_COMMIT`, `BUILD_TIME`, `PACKAGES`, `GOARCH`, optional `GOPROXY`, and derived `PROXY`. Targets include `all`, `build`, `release`, `test`, and `clean`.

## Control Flow
`build` compiles `cmd/main.go` as a Linux static-ish CGO-disabled binary with version/build-time ldflags. `release` adds static external linker flags. `test` depends on build. `clean` removes the output directory.

## State, Persistence, and Dependencies
Build output is `bin/nydus-overlayfs`. It depends on Go tooling, git for commit hash, and environment architecture. The `PACKAGES` variable is prepared but not used in the visible `test` rule content.

## Integration Points
The Makefile supports release automation and local development of the containerd mount helper.

## Risks and Test Signals
`test: build` without an explicit `go test` command is weak if no omitted continuation exists; it may only build. Cross-compilation is limited to Linux output. Version injection depends on git availability.
