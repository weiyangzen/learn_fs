# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationCheckerTest.java

Purpose: tests consistency-check report generation across registered master/worker/server configuration records.

Important APIs/types/functions: uses `ConfigurationChecker`, `ConfigurationStore`, dynamic `PropertyKey` builders with `ConsistencyCheckLevel.ENFORCE` or `WARN`, gRPC `ConfigProperty`, `Scope`, `ConfigStatus`, `Address`, and wire `ConfigCheckReport`.

Control flow: setup creates two independent stores and a checker. `checkConf` defines master-enforce, worker-warn, and server-enforce keys, builds matching properties, and registers two node addresses. It first verifies identical records pass. Then it changes the WARN-scoped worker property on one record and expects one warning with status `WARN`. Then it changes the ENFORCE-scoped master property and expects one error plus one warning with status `FAILED`. Finally it introduces a mismatched server-enforce property and expects failure with one error and no warnings.

State and persistence behavior: all state is in-memory `ConfigurationStore` records keyed by node address. Reports are regenerated explicitly before inspection.

Dependencies and integration points: validates the master-side configuration consistency check that classifies mismatches by property consistency level and scope.

Risks: uses dynamically built test keys, so it avoids some real property metadata interactions. It checks counts/status but not exact report contents or grouping.

Test signals: clear regression signal for PASS/WARN/FAILED status transitions and warn-vs-error classification.
