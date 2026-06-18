# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/index.ts

## Purpose
This file defines shared route parameter and pagination/filter argument types for dashboard list hooks and route dispatchers.

## APIs, Control Flow, and State
`Params` enumerates supported resource route keys. `DetailParams` adds namespace and name. Paging interfaces define optional pageSize/current, filters, sort maps, and Kubernetes continue tokens for app pods, system pods, StorageClasses, PVs, PVCs, CacheGroup workers, and upgrade jobs.

## Dependencies and Integration Points
Route dispatch components and hook modules use these types to keep URL params and query-building inputs consistent.

## Risks and Test Signals
Route keys must stay aligned with router declarations, `ResourcesList`, `ResourcesDetail`, and `getBasePath`. Test TypeScript compilation after adding resources and verify sort keys accepted by backend.
