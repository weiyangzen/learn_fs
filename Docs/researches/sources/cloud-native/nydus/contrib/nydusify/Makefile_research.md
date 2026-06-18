# sources/cloud-native/nydus/contrib/nydusify/Makefile

## Purpose
This Makefile builds, tests, releases, and cleans the `nydusify` Go CLI.

## Important APIs, Types, and Functions
Variables include `GIT_COMMIT`, `BUILD_TIME`, `PACKAGES`, `GOARCH`, optional `GOPROXY`, and `PROXY`. Targets include `all`, `build`, `release`, `test`, and `clean`.

## Control Flow
`build` compiles `cmd/nydusify.go` into `bin/nydusify`, injects version/build time, disables CGO, and targets Linux. `release` builds with static linker flags. `test` depends on build; the visible content does not show a `go test` invocation. `clean` removes build output.

## State, Persistence, and Dependencies
The main persistent output is `bin/nydusify`. It depends on Go tooling and git. `GOPROXY` can be injected into build commands.

## Integration Points
The Makefile is the developer/release entrypoint for the CLI that orchestrates conversion, checking, copying, optimization, packing, chunkdict, and commit workflows.

## Risks and Test Signals
As with overlayfs, `test` appears weak if it only builds. The build hardcodes Linux output and relies on runtime architecture. Version strings are `main` package variables in the CLI.
