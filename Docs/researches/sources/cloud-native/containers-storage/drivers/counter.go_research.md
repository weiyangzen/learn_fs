# sources/cloud-native/containers-storage/drivers/counter.go

## Purpose
`counter.go` implements `RefCounter`, a concurrency-safe mount reference counter for graphdriver `Get`/`Put` flows.

## Important APIs, Types, And Functions
`minfo` stores whether a path has been checked and the current count. `RefCounter` stores counts, a mutex, and a `Checker`. `NewRefCounter`, `Increment`, `Decrement`, and `incdec` provide the public behavior.

## Control Flow
On first use of a path, `incdec` asks the checker whether it is already mounted and seeds the count accordingly. On later operations, if the checker reports the path is no longer mounted, the count is reset to zero before applying the increment/decrement. Entries are deleted when count drops to zero or below.

## State And Persistence
State is in-memory only and keyed by mount path. It is intentionally reconciled with external mount state because another process can unmount a path.

## Dependencies And Integration Points
AUFS and similar mount-backed drivers use it to prevent duplicate mounts and premature unmounts. It depends on the `Checker` abstraction implemented by platform driver files.

## Risks
Correctness depends on the checker accurately reporting mounted state. A decrement for an unknown path can produce a negative intermediate count before entry deletion. External unmounts reset the count, which is defensive but can surprise callers that still hold references.

## Test Signals
AUFS concurrent benchmark and mount tests indirectly exercise refcount behavior.
