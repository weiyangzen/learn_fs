# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlwaysPrimaryPrimarySelector.java

Purpose: test `PrimarySelector` implementation that permanently reports primary state.

Important APIs/types/functions: `start`, `stop`, `getState`, `getStateUnsafe`, `onStateChange`, and `waitForState`.

Control flow: lifecycle methods do nothing; state getters return `NodeState.PRIMARY`; listener registration returns a no-op scoped handle; waiting for PRIMARY returns immediately while waiting for STANDBY sleeps indefinitely.

State and persistence: stateless and non-persistent.

Dependencies/integration: used by `MasterTestUtils` and block/master tests requiring a primary master context without real leader election.

Risks: waiting for standby intentionally blocks forever, so tests must not call it except when verifying blocking behavior. It never emits state-change callbacks.

Test signals: useful as a fixture; behavior is simple enough to be validated by consumers that require primary startup.
