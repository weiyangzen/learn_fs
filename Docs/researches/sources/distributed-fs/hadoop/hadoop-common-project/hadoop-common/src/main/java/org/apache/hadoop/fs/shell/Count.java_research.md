# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Count.java

Purpose: implements `-count`, reporting directory/file/byte counts, quotas, storage-type quota usage, erasure coding policy, and snapshot counts for paths.

Important APIs and types: `processOptions()`, `getAndCheckStorageTypes()`, `processPath()`, and package-private test accessors. Flags include `-q`, `-h`, `-v`, `-t`, `-u`, `-x`, `-e`, and `-s`.

Control flow: options are parsed first and default path `.` is added when no path remains. Quota modes parse optional storage types and disable snapshot exclusion. Optional header output is assembled from `ContentSummary` or `QuotaUsage` static header helpers plus EC/snapshot columns. `processPath()` calls either `fs.getQuotaUsage()` or `fs.getContentSummary()` and appends optional EC and snapshot strings before the path.

State and persistence: command state is per-run booleans and storage-type list only. No filesystem mutation occurs.

Dependencies and integration: extends `FsCommand`; uses `ContentSummary`, `QuotaUsage`, `StorageType`, Hadoop and commons `StringUtils`, and the `FsShell` deprecated constructor path for compatibility.

Risks: multiple optional columns can trigger repeated `getContentSummary()` calls per path. `-t` is ignored unless quota output is enabled. Snapshot exclusion is intentionally ignored under quota modes with a printed notice. Invalid storage-type strings propagate parse failures.

Test signals: cover default path, headers for every mode, human-readable formatting, type-list parsing including `all`/empty, `-x` interaction with quota modes, EC/snapshot appended columns, and invalid storage type errors.
