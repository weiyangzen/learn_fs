## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TestSpecificMasterBlockSync.java

### Purpose
`TestSpecificMasterBlockSync` is a visible-for-testing subclass of `SpecificMasterBlockSync` that exposes controllable heartbeat failures and a registration success counter for tests.

### Important APIs and Types
- `failHeartbeat()` and `restoreHeartbeat()` toggle a volatile failure flag.
- `getRegistrationSuccessCount()` returns an `AtomicInteger` count.
- Overrides `registerWithMasterInternal()` to increment the count after successful super registration.
- Overrides `beforeHeartbeat()` to throw `UnavailableRuntimeException` when failure is enabled.

### Control Flow
Tests can force normal heartbeat attempts to fail before the helper heartbeat RPC. Registration still uses the production path, and successful registration increments the test counter.

### State and Persistence
Only test-only in-memory state: failure flag and registration counter. No additional persistence beyond superclass behavior.

### Dependencies and Integration Points
Constructed by `BlockSyncMasterGroup` when `TEST_MODE` is true and directly by tests.

### Risks
- It lives under main sources, so production classpath includes test hooks gated only by test-mode construction.
- It changes timing/behavior only through `beforeHeartbeat`; registration failures still require mock/master setup.

### Test Signals
Used by all-master registration and specific master sync tests to assert re-registration and retry paths.
