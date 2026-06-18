# sources/distributed-fs/ipfs-kubo/.github/workflows/test-migrations.yml

## Purpose
This workflow validates repository migration and update behavior across Linux, Windows, and macOS.

## Important APIs, Types, And Functions
It builds Kubo with `make build`, adds `cmd/ipfs` to `PATH`, runs `go test ./repo/fsrepo/migrations/...`, `go test ./test/cli/migrations/...`, and `go test -run "TestUpdate" ./test/cli/...`.

## Control Flow
It runs on manual dispatch and on changes to migration, repo, update, CLI migration, or workflow files. A matrix covers `ubuntu-latest`, `windows-latest`, and `macos-latest`; macOS runs a DNS reconfiguration step before update tests to mitigate resolver flakiness.

## State And Persistence Behavior
It creates built binaries, temporary IPFS repos under runner temp, logs, and uploaded failure/success artifacts containing test logs and temp repo contents.

## Dependencies And Integration Points
It integrates fsrepo migration code, CLI migration tests, update command tests that may use GitHub APIs, OS-specific shell behavior, and runner DNS configuration.

## Risks And Test Signals
Risks include path/PATH differences on Windows, real-network update tests, and broad artifact uploads exposing temp state. Signals are successful migration package tests, CLI migration tests, and `TestUpdate` on all OSes.
