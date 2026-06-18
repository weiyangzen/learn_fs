# sources/cloud-native/stargz-snapshotter/Makefile

## Purpose
The Makefile provides build, install, lint, test, integration, generation, vendor validation, and benchmark entry points for stargz-snapshotter.

## Important APIs, Types, and Functions
Variables compute `PREFIX`, package path, `VERSION`, `REVISION`, linker flags, command names, and command output paths. Binary targets build `containerd-stargz-grpc`, `ctr-remote`, `stargz-store`, `stargz-store-helper`, and `stargz-fuse-manager`. Other targets include `check`, `install`, `uninstall`, `clean`, `generate`, `validate-generated`, `vendor`, `test`, `test-root`, `test-all`, integration/runtime test targets, `validate-vendor`, and benchmark-related targets.

## Control Flow, State, and Persistence
Build targets run `go build` in module subdirectories with link-time version injection. Test targets run `go test -race` across root, estargz, cmd, and ipfs modules. Integration targets delegate to scripts. Install/uninstall mutate `CMD_DESTDIR`; clean removes built binaries; vendor validation copies the repo to a temp dir, runs `make vendor`, diffs, and deletes the temp dir.

## Dependencies and Integration Points
The Makefile integrates with Dockerfile stages and GitHub workflows. It depends on git metadata, Go toolchain, golangci-lint, shell scripts, and module layout.

## Risks and Test Signals
`VERSION` and `REVISION` depend on git commands and dirty state, affecting reproducibility. `GO111MODULE=auto` is legacy. `validate-vendor` copies the full repo and can be expensive. CI uses these targets as authoritative behavior gates.
