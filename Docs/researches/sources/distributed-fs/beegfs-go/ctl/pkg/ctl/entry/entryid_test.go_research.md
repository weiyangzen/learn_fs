# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid_test.go

Purpose: unit tests for compact entry ID parsing and bounded entry ID map behavior.

Important APIs/types/functions: `TestNewPackedEntryID`; `TestParseHexToUint32`; `TestPackedEntryMap`; `TestPackedEntryMapCapZero`.

Control flow: tests validate expected packed values for real-looking IDs, reject special/oversized IDs, verify hex parser behavior, exercise map add/contains/duplicate semantics, inspect FIFO eviction ring/index state, and confirm zero capacity behaves as one.

State and persistence: no persistence; tests inspect in-memory state directly because package-private internals are in the same package.

Dependencies and integration points: uses `testing` and testify `assert`.

Risks: subtests use `t.Run(t.Name(), ...)`, so names may not distinguish cases as intended. Direct internal-state assertions are precise but can make refactors noisy even if behavior remains equivalent.

Test signals: strong coverage for this small data structure. Additional race tests could validate concurrent Add/Contains under `go test -race`.
