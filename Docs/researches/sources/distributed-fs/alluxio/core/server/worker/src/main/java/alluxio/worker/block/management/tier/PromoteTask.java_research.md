# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/PromoteTask.java

Purpose: Moves highly ranked blocks from lower tiers to adjacent upper tiers until configured range or quota limits are reached.

Important APIs: `run`; private `getTransferInfos`.

Control flow: For each tier intersection, it iterates lower-tier blocks in reverse order, computes the upper tier projected used ratio, stops at `WORKER_MANAGEMENT_TIER_PROMOTE_QUOTA_PERCENT`, and creates move transfer infos up to `WORKER_MANAGEMENT_TIER_PROMOTE_RANGE`.

State and persistence: Per-run transfer list and byte projection only. Moves mutate block store through the transfer executor.

Dependencies and integration: Uses block iterator ordering, metadata tier capacity, evictor view block metadata, `BlockTransferExecutor`, and management configuration.

Risks and test signals: The projection adds selected block sizes after checking quota, so a selected block can push usage above quota. Tests should cover quota boundaries, missing metadata, empty lower tiers, promote range limits, and transfer result aggregation.
