# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/k8s.ts

## Purpose
This file extends Kubernetes TypeScript models with dashboard-specific JuiceFS relationships and configuration/job types.

## APIs, Control Flow, and State
It defines enriched `Pod`, `PV`, `PVC`, unique-ID PVC types, `accessModeMap`, batch upgrade config/status models, config diff models, original config and mount patch shapes, cache directory/cache volume settings, CacheGroup templates and status, and upgrade job wrappers.

## Dependencies and Integration Points
Components, hooks, config conversion, batch upgrade pages, CacheGroup pages, and pod/storage tables all import these contracts. It depends on `kubernetes-types` API models.

## Risks and Test Signals
Several fields use backend-specific casing such as `PVC`, `PV`, `UniqueId`, `HostnameKey`, and `InitContainers`; these must match API JSON exactly. Test API contract decoding, optional field handling, and TypeScript strictness when backend models evolve.
