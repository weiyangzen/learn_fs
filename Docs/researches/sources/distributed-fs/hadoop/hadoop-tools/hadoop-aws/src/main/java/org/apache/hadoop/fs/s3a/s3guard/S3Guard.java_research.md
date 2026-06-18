<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java

Purpose: compatibility utility for a now-removed/unsupported S3Guard feature set while retaining authoritative-path helper logic.

Important APIs/types/functions: private constructor prevents instantiation. `checkNoS3Guard(URI,Configuration)` rejects configured metadata stores other than the null metadata store. `getAuthoritativePaths(URI,Configuration)` reads authoritative path config. `allowAuthoritative(Path,S3AFileSystem,Set<Path>)` decides whether a path is covered by authoritative configuration.

Control flow: filesystem startup/tooling can call `checkNoS3Guard()` to fail fast if legacy metadata store config is present. Authoritative-path checks normalize configured paths and compare requested paths against the bucket filesystem.

State/persistence: stateless utility. Reads configuration only.

Dependencies/integration: uses S3A constants, Hadoop `Path`, `Configuration`, `PathIOException`, and `S3AFileSystem`.

Risks/test signals: legacy config must produce clear failures instead of silently enabling removed behavior. Tests should cover null/default metadata store allowance, non-null metadata store rejection, bucket-qualified authoritative paths, and path matching edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java -->
