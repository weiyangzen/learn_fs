# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs_test.go

## Purpose
This file tests MFS remote pinning error paths and policy handling.

## Important APIs, Types, And Functions
Test doubles include `testPinMFSContext` and `testPinMFSNode`. Helpers include `isErrorSimilar`, `testPinMFSServiceWithError`, and `readLogLine`. Tests cover config errors, root node errors, disabled services, invalid intervals, unnamed pins, and named pins.

## Control Flow
Tests create short-lived contexts, start `pinMFSOnChange` in a goroutine, read structured log lines from `logging.NewPipeReader`, and assert error level plus message content.

## State And Persistence Behavior
No real remote pinning service is used; failed client calls produce expected log errors. Logging pipe state is the primary observable.

## Dependencies And Integration Points
It integrates the MFS pinning polling loop, config structs, logging pipeline, and merkledag raw node test double.

## Risks And Test Signals
Risks include tests depending on log timing and exact message substrings. Signals are expected logged errors for config read failure, root node failure, invalid interval, and empty remote service response.
