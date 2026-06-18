# sources/distributed-fs/ipfs-kubo/test/cli/harness/log.go

Purpose: buffered hierarchical logger for tests that only prints on failure or explicit enablement, keeping verbose `go test` output readable.

Important APIs/types/functions: `event`, sortable `events`, and `TestLogger`. `NewTestLogger` registers cleanup. `Log`, `Logf`, `Fatal`, `Fatalf`, `AddPrefix`, `EnableLogs`, and `flush` manage buffered log events.

Control flow: log methods timestamp and annotate entries with caller file/line plus prefixes, then append under a mutex. Child loggers register their own cleanup; because testing cleanup runs LIFO, children flush into parents before the root sorts and prints.

State and persistence: in-memory event buffers only. Output is printed to stdout during cleanup if the test failed or logging was enabled.

Dependencies/integration: depends on `testing.T`, runtime caller metadata, sorting, and synchronization. It is a harness utility rather than daemon log capture.

Risks: `EnableLogs` has confusing parent recursion and prints diagnostic “enabling children” text itself. Caller depth is fixed and may point at helper internals after wrapper changes. Test signals are failure-time logs and prefixed contextual events.
