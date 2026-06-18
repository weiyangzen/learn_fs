# sources/distributed-fs/ipfs-kubo/cmd/ipfs/runmain_test.go

## Purpose
This coverage-only test file lets `go test -tags testrunmain` execute the real CLI startup path from a test binary.

## Important APIs, Types, And Functions
`TestRunMain` rebuilds `os.Args` from `flag.Args`, calls `kubo.Start(kubo.BuildDefaultEnv)`, writes the return code to `$IPFS_COVER_RET_FILE` if set, and redirects stdout/stderr to `/dev/null`.

## Control Flow
It is included only under the `testrunmain` build tag, matching the Make coverage binary target.

## State And Persistence Behavior
It mutates global `os.Args`, may write a return-code file, and replaces process stdout/stderr file handles.

## Dependencies And Integration Points
It integrates `cmd/ipfs/Rules.mk` coverage target with normal CLI startup.

## Risks And Test Signals
Risks include global output mutation and comments acknowledging unconventional test abuse. Signal is a coverage binary capable of driving real command execution and reporting exit status.
