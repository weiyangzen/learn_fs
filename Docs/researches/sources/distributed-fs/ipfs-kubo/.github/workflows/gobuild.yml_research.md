# sources/distributed-fs/ipfs-kubo/.github/workflows/gobuild.yml

## Purpose
This CI workflow verifies that `./cmd/ipfs` cross-builds for every platform listed in `.github/build-platforms.yml`.

## Important APIs, Types, And Functions
The single `go-build` job uses `actions/checkout`, `actions/setup-go` with `go.mod`, and a shell loop that parses platform names into `GOOS` and `GOARCH`, then runs `go build -o /dev/null ./cmd/ipfs`.

## Control Flow
On master pushes, pull requests, or manual dispatch, the job runs only in `ipfs/kubo` unless manually dispatched. It uses self-hosted runners for canonical repo CI and `ubuntu-latest` elsewhere.

## State And Persistence Behavior
Only Go module/build caches and ephemeral compiled output are used. No artifacts are persisted.

## Dependencies And Integration Points
It integrates the platform manifest, Go module version, build tags/ldflags from normal Go build behavior, and environment flags used by Kubo's resource-manager checks.

## Risks And Test Signals
Risks include brittle `grep` parsing of YAML, unsupported platform names with extra hyphens, and platform-specific compile breakage. Success is every listed platform compiling `cmd/ipfs`.
