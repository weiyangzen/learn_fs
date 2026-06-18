# sources/distributed-fs/ipfs-kubo/core/commands/repo_verify_test.go

Purpose: Go 1.25-only unit coverage for `ipfs repo verify` worker healing timeout behavior. It isolates `verifyWorkerRun` with mocked blockstore and CoreAPI block access so timeout logic can be tested with `testing/synctest` virtual time instead of real sleeps.

Important APIs/types/functions: `TestVerifyWorkerHealTimeout` contains subtests for successful heal before deadline, timeout failure, zero timeout meaning no deadline, concurrent multiple-block healing, and valid-block no-op behavior. `mockBlockstore`, `mockBlockAPI`, and `mockCoreAPI` implement the minimum interfaces needed by the worker: block reads, delete/put stubs, `Block().Get`, and CoreAPI method stubs.

Control flow: each corruption case sends one or more CIDs through `keys`, starts `verifyWorkerRun` in goroutines with a `sync.WaitGroup`, advances virtual time, waits, closes `results`, and asserts the resulting state/message. Mock `BlockAPI.Get` waits on `time.After(getDelay)` or returns `ctx.Err()` when the worker's heal context expires.

State and persistence behavior: no durable state is written. The mocked blockstore simulates corrupt or valid local blocks and the mocked block API simulates remote healing data. The test verifies in-memory result states such as `verifyStateCorruptHealed`, `verifyStateCorruptHealFailed`, and `verifyStateValid`.

Dependencies and integration points: depends on the production `verifyWorkerRun`, `verifyResult`, and verify state constants defined elsewhere in the commands package; uses `boxo/path`, Kubo `coreiface`, and `coreiface/options` only to satisfy interfaces.

Risks: build-tagged `go1.25`, so coverage is absent on older Go versions. The mocks cover timeout outcomes but not full CLI flags, repo traversal, block replacement durability, or network behavior. The concurrent subtest uses identical fast mock behavior for both blocks, so it does not actually exercise mixed success/failure outcomes despite the name.

Test signals: directly tests heal timeout semantics and explicitly points end-to-end coverage to `test/cli/repo_verify_test.go`. Failures here would indicate worker context/deadline regressions.
