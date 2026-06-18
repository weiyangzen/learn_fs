# sources/distributed-fs/ipfs-kubo/bin/test-go-fmt

## Purpose
This script checks Go formatting across the repository.

## Important APIs, Types, And Functions
It uses `find` to select `*.go` files while pruning `test/sharness` and `plugin/loader/preload.go`, runs `gofmt -s -l`, and reports any paths listed.

## Control Flow
It writes gofmt output to a temp file, prints a formatted failure message if non-empty, cleans up, and exits nonzero.

## State And Persistence Behavior
It creates and removes a temporary file; it does not rewrite source files.

## Dependencies And Integration Points
It supports Make/CI format checks and relies on Go's `gofmt`.

## Risks And Test Signals
Risks include skipped paths hiding formatting issues and temp-file cleanup on interruption. Signal is empty gofmt output.
