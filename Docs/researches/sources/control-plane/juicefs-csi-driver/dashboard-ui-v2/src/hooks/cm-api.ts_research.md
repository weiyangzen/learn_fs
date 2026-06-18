# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cm-api.ts

## Purpose
This file provides hooks for the CSI dashboard configuration ConfigMap and related PVC impact analysis.

## APIs, Control Flow, and State
`useConfig` fetches `/api/v1/config`, `useConfigPVC` fetches PVC matches for config patches, `useConfigPVCSelector` posts a candidate ConfigMap to `/api/v1/config/pvcs/selector`, `useUpdateConfig` PUTs the ConfigMap, and `useConfigDiff` queries diff pods with node, uniqueId, pageSize, and current parameters.

## Dependencies and Integration Points
Config pages and update confirmation modals use these hooks to edit `config.yaml`, preview affected PVCs/pods, and decide whether batch upgrade should be offered.

## Risks and Test Signals
`useConfigDiff('', '')` produces empty query filters by design. Query strings are not URL-encoded. Test invalid YAML update errors, selector preview, All Nodes behavior, pagination defaults, and diff refresh after config saves.
