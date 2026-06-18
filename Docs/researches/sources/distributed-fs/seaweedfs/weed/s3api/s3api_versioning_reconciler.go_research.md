<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler.go

Purpose: implements a background reconciler for versioned objects whose `.versions` directory latest pointer references a missing version file after a partial delete/update failure.

Important APIs/types/functions: `versioningHealLogPrefix` and logging helpers emit sanitized structured log lines. `sanitizeHealArgs`, `sanitizeHealArg`, and `needsHealQuote` prevent log injection. Queue constants define capacity, poll interval, retry count, and backoff bounds. `versionsHealCandidate` and `versionsHealQueue` store pending bucket/object repairs. Queue methods `Enqueue`, `popReady`, `requeue`, and `Len` manage bounded deduplicated work. Server methods `startVersioningReconciler`, `runVersioningReconciler`, `drainVersionsHealQueue`, and `healVersionsPointer` run and execute repairs.

Control flow: producers enqueue bucket/object candidates. The reconciler ticks every 5 seconds, pops candidates whose retry time has arrived, increments attempts, calls `healVersionsPointer`, and either logs drain success or requeues with exponential backoff capped at 30 seconds. After max retries it drops the candidate and relies on read-path heal. `healVersionsPointer` reads the `.versions` directory, treats missing directory/no pointer/consistent pointer as success, retries transient read/probe errors, and calls `healStaleLatestVersionPointer` when the latest-file pointer is missing.

State and persistence behavior: the queue is in-memory, bounded to 4096 entries, and deduplicated by `bucket/object`. Durable state lives in filer entries and extended metadata under `.versions`; the reconciler repairs that metadata by delegating to the read-path heal function. Queue state is lost on restart, but stranded state can still be healed by reads or future enqueue events.

Dependencies and integration: depends on S3 server bucket/path helpers, filer `getEntry`, versioning constants, gRPC status codes, and the existing `healStaleLatestVersionPointer` implementation. It is started by `NewS3ApiServerWithStore` and stopped by `Shutdown`.

Risks: bounded queue drops newest candidates under flood, so hot failure modes may rely on read-path heal. `versionsHealKey` concatenates bucket/object with `/`, which is adequate for a map key but can collide in pathological bucket/object combinations if bucket names and object names are not constrained. Healing after a transient listing/probe anomaly could rewrite to an older version if transient errors are misclassified, so non-NotFound probe errors are retried. Queue iteration order is map-random, so fairness is best-effort.

Test signals: reconciler tests cover deduplication, capacity cap, due-only popping, backoff requeue, give-up behavior, and retry helper semantics. Heal-log tests protect observability formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler.go -->
