# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTestUtils.java

Purpose: assertion helpers for block master tests.

Important APIs/types/functions: `verifyBlockOnWorkers`, `verifyBlockNotExisting`, and `findWorkerInfo`.

Control flow: `verifyBlockOnWorkers` fetches block info, checks length and location count, constructs expected `BlockLocation` objects from worker IDs/addresses with MEM medium/tier, and compares as sets. `verifyBlockNotExisting` asserts `getBlockInfo` throws `BlockInfoException`. `findWorkerInfo` searches a list by worker id or throws assertion error.

State and persistence: no state or persistence.

Dependencies/integration: used by block master test suites to reduce repeated location assertions. Assumes MEM medium/tier for expected locations.

Risks: helper is specialized to MEM locations and will be wrong for tests involving other media unless extended. Set comparison ignores ordering by design.

Test signals: supports clear assertions for block existence, non-existence, and worker lookup in block master tests.
