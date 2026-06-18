# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/SetReplication.java

Purpose: implements `-setrep`, recursively setting file replication and optionally waiting until block locations reflect the requested replication.

Important APIs and types: `processOptions()`, `processArguments()`, `processPath()`, and private `waitForReplication()`. State includes `newRep`, `waitList`, and `waitOpt`.

Control flow: parses `-R` for compatibility and `-w`, requires positive short replication, and always enables recursion. `processPath()` rejects symlinks, ignores directories directly, skips erasure-coded files, calls `fs.setReplication()`, prints status, and enqueues files when waiting. `waitForReplication()` polls `refreshStatus()` and `getFileBlockLocations()` every 10 seconds until every block's host count equals `newRep`.

State and persistence: mutates file replication metadata on supported filesystems. Wait state is in-memory list of files processed successfully.

Dependencies and integration: uses `BlockLocation`, `PathData`, and inherited recursive traversal.

Risks: waiting can run indefinitely if replication never converges. Host-count comparison may not capture all filesystem replication semantics. Interrupted sleeps are swallowed. EC files are intentionally skipped. Decreasing replication prints a warning only once per file.

Test signals: cover invalid replication, symlink rejection, EC skip, directory recursion, failed `setReplication()`, wait success, wait warning on decrease, and interruption behavior.
