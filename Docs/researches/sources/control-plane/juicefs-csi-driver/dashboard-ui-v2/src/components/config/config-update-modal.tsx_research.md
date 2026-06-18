<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/config-update-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/config-update-modal.tsx

## Purpose
`config-update-modal.tsx` confirms edits to the dashboard config ConfigMap by showing mount-pod patch diffs and the PVCs affected by each changed selector before saving.

## Important APIs, Types, and Functions
`ConfigUpdateConfirmModal` uses `useUpdateConfig`, `useConfigPVCSelector`, `YAML.parse/stringify`, `ReactDiffViewer`, `Collapse`, `PVCWithSelector`, and `PvcPop`. The internal `configDiff` compares `OriginConfig.mountPodPatch` entries and builds collapsible diff panels with matched PVC tables.

## Control Flow, State, and Persistence
When opened, the modal parses old and new YAML, asks the backend which PVCs match the proposed config, and stores old/new config plus PVC groups. Saving reparses YAML, executes an update ConfigMap request with `data['config.yaml']`, clears edit/update flags, and closes. Parse/API errors are sent to `setError`.

## Dependencies and Integration Points
It bridges the config editor page, ConfigMap update API, selector evaluation API, YAML config schema, diff viewer, and PVC display components. The positional relationship between `mountPodPatch[i]` and `pvcs[i]` is critical.

## Risks and Test Signals
Risks include index-based diffing that misses inserted/deleted/reordered patches, promise chaining where `.then()` runs after a caught update error, missing loading/error UI for selector fetch, and YAML parse errors typed narrowly. Signals are YAML parse tests, changed patch diff snapshots, backend selector alignment checks, and save error-path tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/config-update-modal.tsx -->
