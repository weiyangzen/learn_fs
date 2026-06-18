## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/SpecificMasterBlockSyncTest.java

**Purpose:** Tests `SpecificMasterBlockSync`, the per-master heartbeat/registration coordinator for a block worker.

**Important APIs:** Exercises `heartbeat`, `isRegistered`, block master `register`, `registerWithStream`, `heartbeat`, `acquireRegisterLeaseWithBackoff`, and `BlockHeartbeatReporter.generateReportAndClear`.

**Control flow:** The single test configures heartbeat report threshold, uses a custom reporter that adds one removed block per report generation, and a custom block master client with toggles for flaky registration, register commands, and heartbeat failures. It verifies initial registration, register-command reset for both streaming and non-streaming modes, retry behavior on heartbeat failure, and later re-registration.

**State and persistence:** Runtime state includes registration flag, heartbeat call count, reporter accumulated removals, and client booleans indicating which registration path ran. No durable state.

**Dependencies and integration:** Uses `BlockWorker` mock returning store meta, report, address, and worker ID. Integrates heartbeat report sizing, registration lease hooks, master commands, and stream-registration configuration.

**Risks:** Incorrect registration state transitions can leave workers unregistered or repeatedly re-registering. Report clearing on failures must avoid losing block changes while still preventing unbounded reports.

**Test signals:** Covers flaky registration recovery, master-driven re-registration, threshold-limited heartbeat retries, and both legacy and stream registration paths.
