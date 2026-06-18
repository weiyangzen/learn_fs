# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/TestSafeModeManager.java

Purpose: no-op safe mode manager for tests that do not want safe-mode behavior.

Important APIs/types/functions: implements `notifyPrimaryMasterStarted`, `notifyRpcServerStarted`, and `isInSafeMode`.

Control flow: notification methods do nothing and `isInSafeMode` always returns false.

State and persistence: stateless and non-persistent.

Dependencies/integration: installed by `MasterTestUtils.testMasterContext` so unit tests using the context are not blocked by safe mode.

Risks: hides safe-mode gating from tests. Code whose correctness depends on safe-mode transitions should use `DefaultSafeModeManager` instead.

Test signals: fixture behavior is trivial; consumers validate it by proceeding without safe-mode waits.
