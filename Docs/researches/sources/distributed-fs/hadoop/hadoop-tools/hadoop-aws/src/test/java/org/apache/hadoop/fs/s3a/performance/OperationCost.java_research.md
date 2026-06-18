# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCost.java

Purpose: immutable value type and catalog of expected S3A HEAD/LIST request costs used by performance integration tests.

Important APIs/types/functions: `OperationCost` stores `head` and `list` counts, exposes package-private `head()`/`list()`, `plus(OperationCost)`, and `toString()`. Constants model individual probes (`HEAD_OPERATION`, `LIST_OPERATION`, `FILE_STATUS_FILE_PROBE`, `FILE_STATUS_DIR_PROBE`) and aggregate operations such as `GET_FILE_STATUS_ON_FILE`, `GET_FILE_STATUS_ON_DIR`, `GET_FILE_STATUS_FNFE`, `COPY_OP`, `RENAME_SINGLE_FILE_DIFFERENT_DIR`, `RENAME_SINGLE_FILE_SAME_DIR`, `CREATE_FILE_OVERWRITE`, and `CREATE_FILE_NO_OVERWRITE`.

Control flow: no runtime side effects; aggregate constants are composed at class initialization with `plus()`.

State and persistence: immutable in-memory counts only; no external persistence.

Dependencies/integration: consumed by `OperationCostValidator` and `AbstractS3ACostTest` callers to turn semantic operations into metric probes for `OBJECT_METADATA_REQUESTS` and `OBJECT_LIST_REQUEST`.

Risks: constants are tightly coupled to S3A implementation probe order; when S3A optimizes or changes marker/status logic, tests using these constants must be updated.

Test signals: this file is not itself a test, but all cost tests indirectly validate its constants by asserting live metric diffs.
