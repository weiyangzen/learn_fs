# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cg-api.ts

## Purpose
This file defines SWR and async hooks for CacheGroup listing, detail, worker metrics, worker membership, and CRUD operations.

## APIs, Control Flow, and State
`useCacheGroups`, `useCacheGroup`, `useWorkerCacheBytes`, `useCacheGroupWorkers`, and `useNodes` use SWR keys under `/api/v1/cachegroup(s)`. Mutating hooks wrap `apiFetch` with `useAsync`: `useRemoveWorker`, `useAddWorker`, `useCreateCacheGroup`, `useUpdateCacheGroup`, and `useDeleteCacheGroup`, sending JSON bodies or DELETE requests.

## Dependencies and Integration Points
The hooks support `cg-list`, `cg-detail`, worker tables, and YAML edit/create workflows. Types come from `CacheGroup`, Kubernetes `Pod`/`Node`, and pagination args.

## Risks and Test Signals
Hooks interpolate optional namespace/name into URLs even when undefined. Worker list query values may become `undefined`. Test create/update/delete error propagation, worker pagination filters, refresh intervals, and empty parameter cases.
