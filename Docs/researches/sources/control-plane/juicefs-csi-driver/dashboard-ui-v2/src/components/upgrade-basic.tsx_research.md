# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-basic.tsx

## Purpose
`UpgradeBasic` displays and controls a batch mount-pod upgrade job.

## APIs, Control Flow, and State
It receives an `UpgradeJob` plus `freshJob`. It fetches the targeted PVC via `usePVCWithUniqueId(upgradeJob.config.uniqueId)`, keeps a local status mirror, and conditionally renders pause, resume, stop, and delete actions. Actions call `useUpdateUpgradeJob` with `pause`, `resume`, or `stop`; delete calls `useDeleteUpgradeJob` and redirects to `/jobs`. Descriptions show node, worker parallelism, ignore-error flag, PVC link, and status badge.

## Dependencies and Integration Points
It uses job hooks, PV hook, icon components, `getUpgradeStatusBadge`, router links, and localized labels. `BatchUpgradeJobDetail` embeds it and refreshes job state after mutations.

## Risks and Test Signals
Redirect uses `window.location.href`, bypassing router navigation. Delete does not await before redirect. Test each status transition, API errors, empty `config.status`, and missing PVC resolution.
