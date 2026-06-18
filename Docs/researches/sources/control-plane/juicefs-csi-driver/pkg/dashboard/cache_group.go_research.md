# sources/control-plane/juicefs-csi-driver/pkg/dashboard/cache_group.go

## Purpose
This file exposes CRUD and worker-management endpoints for JuiceFS CacheGroup custom resources and their worker pods.

## Important APIs, Types, And Functions
Key handlers are `listCacheGroups`, `createCacheGroup`, `deleteCacheGroup`, `updateCacheGroup`, `getCacheGroup`, `listCacheGroupWorkers`, `addWorker`, `removeWorker`, and `getCacheWorkerBytes`. `validateCg` enforces the required secret reference and worker node selector.

## Control Flow
CRUD handlers read route params or JSON bodies, validate referenced secrets and worker selector fields, then use the manager client to create/update/delete CacheGroup resources. Worker listing fetches the CacheGroup, selects pods with cache-group worker labels, sorts by creation time, applies name/node filters while paginating, and returns items plus total. `addWorker` and `removeWorker` mutate node labels according to the CacheGroup worker selector; cache-byte lookup calls the operator utility against a worker pod.

## State And Persistence
Persistent state is CacheGroup CRs, Node labels used to schedule workers, and worker pod state created by the cache-group operator. Handler-local state is only request filtering and pagination data.

## Dependencies And Integration Points
It depends on `juicefs-cache-group-operator` API/common/utils packages, controller-runtime clients, Kubernetes pods/nodes/secrets, and Gin. It is an extension integration point between the CSI dashboard and the cache-group operator.

## Risks
`updateCacheGroup` validates the existing object rather than the submitted body, so invalid updates can bypass part of validation. Node label mutation directly changes cluster scheduling signals and can remove labels that other workloads may share. Worker pagination applies filters after start offset while total reports unfiltered worker count, which can surprise UI pagination.

## Test Signals
No tests are present. Useful tests would cover validation, update-body validation, node label add/remove idempotency, and worker list pagination/filter totals.
