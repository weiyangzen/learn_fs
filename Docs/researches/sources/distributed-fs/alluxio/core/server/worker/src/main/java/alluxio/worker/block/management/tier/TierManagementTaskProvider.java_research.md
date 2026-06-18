# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/TierManagementTaskProvider.java

Purpose: Chooses the next tier-management task to run: swap restore, alignment, promotion, or none.

Important APIs: Constructor wires services; static `setSwapRestoreRequired`; `getTask`; private `findNextTask`; enum `TierManagementTaskType`.

Control flow: Swap restore has first priority when enabled and flagged. Otherwise it builds a fresh evictor view, checks each adjacent tier pair for misalignment, then checks promotion eligibility based on high-tier used ratio and lower-tier evictable blocks.

State and persistence: Holds service references and a static boolean swap-restore flag. No persistence.

Dependencies and integration: Used by `ManagementTaskCoordinator`; creates `AlignTask`, `PromoteTask`, and `SwapRestoreTask`.

Risks and test signals: Static swap-restore flag is process-global and not synchronized. Provider decisions depend on current block iterator ordering and evictor view freshness. Tests should cover task priority, disabled feature flags, quota thresholds, no evictable lower blocks, and flag reset.
