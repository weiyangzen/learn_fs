# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/job-api.ts

## Purpose
This hook module encapsulates batch mount-pod upgrade job creation, listing, detail, deletion, and control actions.

## APIs, Control Flow, and State
`useCreateUpgradeJob` POSTs `/api/v1/batch/upgrade/jobs` with jobName, normalized nodeName, recreate=true, worker count, ignoreError, and uniqueId, returning the created job name. `useUpgradeJob` fetches one job. `useUpgradeJobs` builds paginated/sorted list query parameters. `useDeleteUpgradeJob` DELETEs one job. `useUpdateUpgradeJob` PUTs an action such as pause, resume, or stop.

## Dependencies and Integration Points
Used by batch job list, detail, creation modal, and `UpgradeBasic`. Types are `UpgradeJob`, `UpgradeJobWithDiff`, and list args.

## Risks and Test Signals
`All Nodes` is a UI sentinel converted to empty string. Query values are unencoded and status action strings are unchecked. Test create payload variants, pagination continue tokens, delete/update failures, and list sorting.
