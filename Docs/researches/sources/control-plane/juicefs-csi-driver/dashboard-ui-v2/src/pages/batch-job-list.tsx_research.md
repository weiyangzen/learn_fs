# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-job-list.tsx

## Purpose
`UpgradeJobList` lists batch upgrade jobs and opens the creation modal.

## APIs, Control Flow, and State
It reads `modalOpen` from search params, tracks pagination, filter, continue token, and modal visibility, fetches jobs with `useUpgradeJobs`, and fetches version data to disable graceful upgrade creation. Columns show job name, status badge, and creation time. Successful creation closes the modal and mutates the job list.

## Dependencies and Integration Points
It integrates with `BatchUpgradeModal`, `useVersion`, `useUpgradeJobs`, route `/jobs/:namespace/:name`, and localized text.

## Risks and Test Signals
The create button is initially enabled until version data says otherwise. Continue-token paging coexists with current/pageSize. Test disabled graceful-upgrade mode, `?modalOpen=true`, list mutation after create, and status display for empty config status.
