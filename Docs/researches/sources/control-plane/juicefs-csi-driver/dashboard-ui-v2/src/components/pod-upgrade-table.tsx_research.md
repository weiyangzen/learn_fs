<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-upgrade-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-upgrade-table.tsx

## Purpose
`pod-upgrade-table.tsx` renders the per-mount-pod status and config diff for an existing batch upgrade job.

## Important APIs, Types, and Functions
`PodUpgradeTable` consumes `UpgradeJobWithDiff`, `diffStatus`, and `failReasons`. It builds a `podMap`, flattens `upgradeJob.config.batches` into `UpgradeType[]`, renders pod links, status badges, failure tooltips, and diff popovers. Helper `getPodUpgradeStatus` prefers log-derived status, then falls back to batch config status.

## Control Flow, State, and Persistence
Effects rebuild map/table state when upgrade job or status map changes and update pagination total from `upgradeJob.total`. Diffs are disabled once `diffStatus` is `success`; otherwise they show YAML old/new settings. State is local and derived from props.

## Dependencies and Integration Points
It integrates upgrade job detail data, websocket/log-derived status maps, Ant Design table UI, diff viewer, YAML serialization, router links, and `getUpgradeStatusBadge`.

## Risks and Test Signals
Risks include missing `failReasons` in effect dependencies only affecting render because map reads are direct, pagination total not matching flattened rows, disabled diffs after success hiding historical changes, and empty dependency on `failReasons` for row status details. Signals are batch flattening tests, status precedence tests, failure tooltip rendering, and diff enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-upgrade-table.tsx -->
