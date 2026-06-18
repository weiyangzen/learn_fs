# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/config.ts

## Purpose
This file defines UI-friendly configuration types and conversion functions between the dashboard form model and the backend/original `config.yaml` model.

## APIs, Control Flow, and State
Types include `Config`, `mountPodPatch`, `pvcSelector`, `MountPatch`, resource and key/value helpers. `ToConfig` converts maps to arrays, mount options to key/value rows, env vars to rows with `valueType`, PVC selectors to form shape, and resources to cpu/memory strings. `ToOriginConfig` performs the reverse, omitting empty structures and removing env `value` or `valueFrom` based on `valueType`.

## Dependencies and Integration Points
`ConfigTablePage`, patch form/detail components, and config update flows rely on these conversions. Types import Kubernetes probes, lifecycle, volumes, env vars, quantities, and selector requirements.

## Risks and Test Signals
Round-trip conversion can drop empty values and reorder maps. `convertPVCSelector` uses a mutable `noMatch` flag that can be overwritten by later empty fields. Test map/list/env/resource round trips, selector combinations, empty patches, and cacheDirs handling.
