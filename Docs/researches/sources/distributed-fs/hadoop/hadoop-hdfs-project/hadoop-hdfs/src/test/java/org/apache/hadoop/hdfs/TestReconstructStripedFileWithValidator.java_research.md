# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithValidator.java

Purpose: extends striped-file reconstruction tests with EC reconstruction validation enabled, specifically proving that polluted decoder outputs are rejected once and then correctly reconstructed by a later task.

Important APIs and types: `TestReconstructStripedFile` inheritance, `DataNodeFaultInjector.badDecoding`, `DataNodeMetrics.getECInvalidReconstructionTasks`, `ByteBuffer`, `AtomicBoolean`, and overridden `isValidationEnabled` and `getPendingTimeout`.

Control flow: constructor logs validator mode. `testValidatorWithBadDecoding` checks all DataNode invalid reconstruction counters start at zero, installs a fault injector that mutates decoder output buffers once, calls inherited `assertFileBlocksReconstruction` for all parity-unit data losses, then sums `ECInvalidReconstructionTasks` and expects exactly one invalid task. The injector is restored in `finally`.

State and persistence behavior: enables `DFS_DN_EC_RECONSTRUCTION_VALIDATION_KEY` through parent setup and shortens pending timeout to 10 seconds so failed reconstruction is rescheduled promptly. It mutates transient decoder buffers, DataNode metrics, and reconstruction task state.

Dependencies and integration points: integrates DataNode EC validation, metrics accounting, fault injection, and parent replica-content assertions. It depends on parent setup reading `isValidationEnabled` and `getPendingTimeout` polymorphically.

Risks and edge cases: the injector modifies output buffer contents in-place and must reset buffer marks correctly. The expected metric sum of one assumes only the first poisoned decode fails and later retry succeeds. A failure could indicate validation is disabled, metric accounting broke, or corrupted data was accepted.

Test signals: inherited reconstruction content checks pass, and cluster-wide `ECInvalidReconstructionTasks` metric sum is exactly one.
