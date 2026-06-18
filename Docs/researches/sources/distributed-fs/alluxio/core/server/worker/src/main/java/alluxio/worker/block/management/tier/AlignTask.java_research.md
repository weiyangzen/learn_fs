# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/AlignTask.java

Purpose: Swaps blocks between adjacent tiers so hotter or higher-ranked blocks reside in upper tiers and colder blocks move down.

Important APIs: `run`; private `generateSwapTransferInfos`.

Control flow: For each tier intersection, it requests paired swap lists from `BlockIterator.getSwaps` using upper-tier natural order and lower-tier reverse order, filtered by evictability. It generates location-aware swap transfer infos, sorts both sides by location, and executes swaps. Resource exhaustion during swap marks `TierManagementTaskProvider` to run swap restoration.

State and persistence: Per-run transient lists only. Actual moves are executed through `LocalBlockStore`, affecting metadata and files.

Dependencies and integration: Uses `BlockMetadataManager`, `BlockMetadataEvictorView`, `BlockTransferExecutor`, `BlockOrder`, `BlockTransferInfo`, and `ResourceExhaustedRuntimeException`.

Risks and test signals: Sorting source and destination lists independently by location can pair blocks differently than the iterator returned. Tests should cover equal list sizes, filter behavior, resource-exhausted callback, generated swap locations, and partial transfer failures.
