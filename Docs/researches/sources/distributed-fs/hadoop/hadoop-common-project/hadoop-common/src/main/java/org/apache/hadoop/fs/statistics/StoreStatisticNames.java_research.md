# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StoreStatisticNames.java

Purpose: public constant catalog for object-store and filesystem operation statistics.

Important APIs, types, and functions: declares string constants for filesystem operations (`OP_OPEN`, `OP_CREATE`, `OP_DELETE`, etc.), store IO events, object requests, multipart uploads, HTTP responses, duration suffixes (`.min`, `.max`, `.mean`, `.failures`), and conditional create metrics.

Control flow: no executable flow beyond private constructor. Other classes compose names from these constants, especially duration tracker suffix handling in `IOStatisticsStoreImpl` and `StatisticDurationTracker`.

State and persistence: no runtime state. The string values are persistent compatibility contracts for logs, metrics, and downstream monitoring.

Dependencies and integration points: depends only on Hadoop classification annotations. Integrated across S3A/object-store code, storage statistics publication, audit operation names, and common metrics consumers.

Risks and test signals: renaming or reusing constants breaks metric compatibility. Tests should verify uniqueness, expected literal names, suffix composition, and consumers that aggregate duration metrics by shared prefixes.
