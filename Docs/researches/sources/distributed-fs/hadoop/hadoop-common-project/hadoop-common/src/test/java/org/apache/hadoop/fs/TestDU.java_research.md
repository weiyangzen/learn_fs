## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDU.java

Purpose: validates `DU`, Hadoop's disk-usage monitor, especially cached/background refresh behavior, non-negative accounting, and honoring an initial used-space value.

Important APIs/types/functions: `DU`, `DU.init`, `DU.getUsed`, `DU.close`, `DU.incDfsUsed`, `CommonConfigurationKeys.FS_DU_INTERVAL_KEY`, `Shell.WINDOWS` assumptions, and local `RandomAccessFile` writes. `createFile` writes random bytes to avoid filesystem compression effects.

Control flow: setup skips Windows, clears and recreates a temp directory. `testDU` writes a 32 KiB file, waits for metadata, then checks three modes: background updater with interval, zero interval without a thread, and initialized object before close. `testDUGetUsedWillNotReturnNegative` applies a very large negative delta and asserts clamping at zero. `testDUSetInitialValue` starts with an explicit initial value, waits for a background refresh, then expects actual usage.

State and persistence: creates real files and syncs data to disk. Background refresh threads are initialized and closed in most paths; one branch intentionally checks a non-closed-before-read path and relies on test cleanup.

Dependencies/integration points: local filesystem block accounting, POSIX permissions/metadata timing, `Shell.WINDOWS`, and `FileUtil` cleanup. It protects callers that depend on `DU` not invoking external `du` on every `getUsed`.

Risks and test signals: sleeps make it timing-sensitive. Disk slack is allowed, but compression, delayed allocation, or unusual block sizes can affect reported values. Non-negative and initial-value assertions are strong regression signals for accounting state.
