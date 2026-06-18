# sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.cc

## Purpose
`QuotaRecomputer.cc` implements recalculation of quota accounting for a QuarkDB namespace quota node by traversing namespace contents and rebuilding a `QuotaNodeCore`.

## Important APIs, Types, and Functions
`QuotaRecomputer::QuotaRecomputer(qclient::QClient*, folly::Executor*)` stores the QuarkDB client and executor. Internal `QuotaNodeFilter` implements `ExpansionDecider` and permits traversal through the root quota container and non-quota descendants, but stops descent into nested quota nodes. `QuotaRecomputer::recompute()` resets the output core, validates the root container ID, creates a `NamespaceExplorer`, and accounts every file.

## Control Flow
`recompute()` clears `qnc`, rejects `cont_id == 0`, configures `ExplorationOptions` with depth limit 2048 and the quota filter, starts exploration at `cont_uri`, and loops over `explorer.fetch(item)`. File items contribute logical size from `item.fileMd.size()` and physical size as `size * LayoutId::GetSizeFactor(layout_id)`, keyed by UID and GID. Directory items are used only for traversal. On completion it returns an OK `MDStatus`.

## State and Persistence Behavior
The function does not write QuarkDB. It reconstructs accounting into the caller-supplied `QuotaNodeCore`, replacing any previous contents. The result depends on current namespace metadata, file layout IDs, and the explorer's handling of corrupt or missing metadata.

## Dependencies and Integration Points
It depends on `NamespaceExplorer`, `ExpansionDecider`, `QuotaNodeCore`, QuarkDB client access, Folly executor scheduling, namespace constants, and common layout size-factor logic. It integrates with quota repair or validation flows that need to recalculate quota nodes from source metadata.

## Risks and Edge Cases
Nested quota nodes are deliberately skipped, so recomputation is scoped to one quota subtree and relies on correct `QUOTA_NODE_FLAG` state. The hard-coded depth limit can exclude extremely deep namespace trees. Physical size is estimated from layout factor rather than confirmed replica state. If `NamespaceExplorer` throws on corruption, recomputation can fail mid-run after clearing the output core.

## Test Signals
Direct tests are not present in this file. Indirect signals include namespace explorer traversal tests and `QuotaNodeCore` accounting tests in `VariousTests.cc`. Dedicated tests should build nested quota-node trees and verify skipped subtrees and physical-size calculations.
