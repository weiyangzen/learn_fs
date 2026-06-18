<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-to-upgrade-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-to-upgrade-table.tsx

## Purpose
`pod-to-upgrade-table.tsx` previews mount pods whose current settings differ from the proposed config before a batch upgrade job is created.

## Important APIs, Types, and Functions
It defines `diffContent(podDiff)` using YAML and `ReactDiffViewer`, a `upgradeColumn` set for pod name and diff popover, and `PodToUpgradeTable` which calls `useConfigDiff(nodeName, uniqueId, pageSize, current)`.

## Control Flow, State, and Persistence
Pagination is local. When diff data changes, the table total is updated and `setDiffPods(diffPods?.pods || [])` informs the parent modal whether start should be enabled. Diff buttons show old/new setting YAML in a popover.

## Dependencies and Integration Points
It is used by `BatchUpgradeModal` and depends on backend config diff pagination. Links point to syspod details when namespace exists.

## Risks and Test Signals
Risks include large diff content inside a popover, no loading/error state, parent enablement based only on the current page of results, and non-null UID assertions. Signals are pagination tests, parent callback tests, diff rendering snapshots, and filters for node/PVC unique ID.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-to-upgrade-table.tsx -->
