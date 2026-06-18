<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cg-workers-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cg-workers-table.tsx

## Purpose
`cg-workers-table.tsx` renders and manages cache group worker pods, including listing, filtering, adding workers to nodes, removing workers, viewing cache bytes, and starting warmup.

## Important APIs, Types, and Functions
`CgWorkersTable` uses `useCacheGroupWorkers`, `useAddWorker`, `useRemoveWorker`, and `useNodes`. It manages table pagination/filter, refresh interval, existing worker nodes, and an add-worker `ModalForm`. Columns link to syspods, show node/status/cache bytes/start time, and provide a remove-worker `Popconfirm`.

## Control Flow, State, and Persistence
Initial refresh interval is 0 unless `autoRefresh` is true. API data updates pagination totals and existing node names. Adding or removing a worker executes the corresponding hook, shows a success message, and enables 1 second refresh. Table search values are flattened into `filter`, including nested metadata values.

## Dependencies and Integration Points
It integrates cache group worker backend endpoints, node inventory, pod status utility functions, `WorkerCacheBytes`, and `WarmupModal`. Worker status is affected by annotations such as `juicefs.io/waiting-delete-worker` and `juicefs.io/backup-worker`.

## Risks and Test Signals
Risks include duplicate disabled-node logic based only on current page data, success messages without error handling, nonlocalized Chinese success text, unsafe non-null assertions on pod specs/status, and repeated row polling. Signals are add/remove API tests, pagination/filter behavior, annotation status rendering, and ensuring warmup uses a valid container status.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cg-workers-table.tsx -->
