# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/SessionCleaner.java

Purpose: `SessionCleaner` periodically removes timed-out worker sessions and asks registered components to clean their per-session state.

Important APIs are constructor, `run`, and `close`. Control flow tracks `lastCheckMs`, sleeps until `WORKER_BLOCK_HEARTBEAT_INTERVAL_MS` has elapsed, warns if cleanup took longer than the interval, obtains timed-out sessions from `Sessions`, removes each session, and calls `cleanupSession` on each `SessionCleanable`. `close` flips a volatile running flag so the loop exits after wakeup.

State and persistence include the `Sessions` object, a list of cleanable callbacks, check interval, and running flag. Dependencies are Alluxio `Sessions`, configuration, sleep utilities, and `SessionCleanable`. Integration points include block lock cleanup and other worker components with session-scoped resources. Risks include close not interrupting sleep by itself, cleanup callback exceptions escaping the loop, and interval coupling to block heartbeat configuration. No direct tests are in this subset.
