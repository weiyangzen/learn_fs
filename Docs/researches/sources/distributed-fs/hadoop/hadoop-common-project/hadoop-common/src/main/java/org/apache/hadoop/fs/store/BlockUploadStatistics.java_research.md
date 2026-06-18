# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/BlockUploadStatistics.java

Purpose: small callback interface for tracking allocation and release of upload data blocks.

Important APIs, types, and functions: `blockAllocated()` and `blockReleased()`.

Control flow: `DataBlocks.DataBlock` subclasses call `blockAllocated()` during construction and `blockReleased()` during close/cleanup.

State and persistence: no state in the interface. Implementations usually update runtime counters or gauges.

Dependencies and integration points: used by `DataBlocks` factories and block implementations to integrate upload buffering with statistics.

Risks and test signals: missed release calls can leak active-block metrics. Tests should cover allocation/release balance for array, bytebuffer, and disk blocks, including close-before-upload and upload-close paths.
