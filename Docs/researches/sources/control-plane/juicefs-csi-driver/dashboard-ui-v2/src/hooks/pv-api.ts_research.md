# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/pv-api.ts

## Purpose
This module defines storage-resource hooks for StorageClasses, PVs, PVCs, PVC unique IDs, basic PVC info, and storage events.

## APIs, Control Flow, and State
List hooks build SWR URLs with sort, filter, page, and Kubernetes continue parameters: `/api/v1/storageclasses`, `/api/v1/pvs`, and `/api/v1/pvcs`. Detail hooks fetch `/api/v1/storageclass/:name/`, `/api/v1/pv/:name/`, `/api/v1/pvc/:namespace/:name/`, and related PVs/events. Unique-ID helpers resolve PVCs by namespaced name or unique ID.

## Dependencies and Integration Points
Storage list/detail pages, `PVsTable`, upgrade job basic info, and config/job workflows depend on these hooks.

## Risks and Test Signals
Some hooks emit URLs with undefined path segments; `usePVC` guards with an empty SWR key only when name is missing. `usePVCEvents` names its argument `pvName`. Test empty params, continue pagination, storage class filtering, unique-ID split edge cases, and event fetching.
