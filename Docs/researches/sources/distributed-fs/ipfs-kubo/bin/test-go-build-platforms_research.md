# sources/distributed-fs/ipfs-kubo/bin/test-go-build-platforms

## Purpose
This script locally reproduces the cross-platform Go build check for Kubo.

## Important APIs, Types, And Functions
It reads `.github/build-platforms.yml`, extracts lines beginning with `  - `, splits each into `GOOS` and `GOARCH`, and runs `go build -o /dev/null ./cmd/ipfs`.

## Control Flow
The script validates the platform manifest exists, loops over non-empty platform entries, builds each target, and prints completion.

## State And Persistence Behavior
Only Go build cache is affected; output is discarded.

## Dependencies And Integration Points
It integrates the platform manifest, Go compiler, and `cmd/ipfs` package.

## Risks And Test Signals
Risks include simplistic YAML parsing and hyphenated platform format assumptions. Signal is all platform builds completing successfully.
