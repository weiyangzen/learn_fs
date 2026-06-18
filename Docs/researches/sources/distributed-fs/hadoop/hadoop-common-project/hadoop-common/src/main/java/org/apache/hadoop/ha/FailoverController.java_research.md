# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverController.java

Purpose: Coordinates manual or controller-driven failover between two HA service targets. It performs preflight checks, tries graceful standby transition of the old active, fences if needed, transitions the target to active, and optionally attempts failback when activation fails.

Important APIs and types: Public `FailoverController(Configuration, RequestSource)`, static timeout helpers `getGracefulFenceTimeout()` and `getRpcTimeoutToNewActive()`, package-visible `tryGracefulFence()`, and public `failover()`. Internal `preFailoverChecks()` validates target state, readiness, and health.

Control flow: `failover()` requires a fencer, checks the destination is standby and healthy unless forced, tries `transitionToStandby()` on the source with low-retry graceful fencing config, fences the source if graceful fencing failed or force-fence is requested, then calls `transitionToActive()` on the destination. If activation fails and the old active was not fenced, it recursively fails back with forced fencing/activation.

State and persistence: Holds configuration, a graceful-fence configuration copy with reduced IPC retries, request source, and timeout values. It does not persist state; persistent effects are service HA state transitions and external fencing side effects.

Dependencies and integration points: Uses `HAServiceTarget`, `HAServiceProtocol`, `HAServiceProtocolHelper`, `NodeFencer`, Hadoop IPC timeout keys, `RPC.stopProxy()`, and request source metadata. Called by CLI/admin code and ZKFC old-active fencing.

Risks: Fencing and activation ordering is safety-critical. Force-active can activate a target that reports not ready. Failback recursion is intentionally aggressive and can fence the failed target. Timeout tuning changes split-brain risk and recovery latency.

Test signals: `TestFailoverController` covers preflight failures, graceful fencing, forced fencing, activation failure, failback, and fencer invocation counts.
