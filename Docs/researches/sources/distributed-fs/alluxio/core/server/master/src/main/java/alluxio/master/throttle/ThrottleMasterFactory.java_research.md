# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ThrottleMasterFactory.java

Purpose: factory for optional `DefaultThrottleMaster` creation.

Important APIs/types/functions: implements raw `MasterFactory`; `isEnabled` reads `MASTER_THROTTLE_ENABLED`; `getName` returns `Constants.THROTTLE_MASTER_NAME`; `create` returns null if disabled or constructs `DefaultThrottleMaster`.

Control flow: master startup asks the factory whether it is enabled, then `create` double-checks the config. When enabled it logs creation and lets `DefaultThrottleMaster` register itself with the registry during construction.

State and persistence: factory is stateless and thread-safe. Created master is `NoopJournaled`.

Dependencies/integration: integrates with Alluxio master factory discovery and throttle master optional configuration.

Risks: raw `MasterFactory` omits a generic type parameter. Returning null from `create` when disabled assumes caller tolerates null even though many factory flows call `isEnabled` first.

Test signals: enabled/disabled config behavior, factory name, created type, and registry registration side effect.
