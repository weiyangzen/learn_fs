<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-selector-form.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-selector-form.tsx

## Purpose
`pvc-selector-form.tsx` provides the editable selector subsection for mount pod patch rules.

## Important APIs, Types, and Functions
`PVCSelectorForm` accepts an optional `mountPodPatch`, renders a `ProCard` and `ProDescriptions`, and binds ProForm fields under `pvcSelector.matchName`, `pvcSelector.matchStorageClassName`, and `pvcSelector.matchLabels[]` entries with `key` and `value`.

## Control Flow, State, and Persistence
The component is stateless and relies on parent form context. It renders three selector categories: PVC name, storage class name, and label matches. Label matches are dynamically repeatable through `ProFormList`.

## Dependencies and Integration Points
It is embedded by `MountPodPatchForm` and must match backend config selector semantics used by `useConfigPVCSelector` and config diffing.

## Risks and Test Signals
Risks include no validation for mutually broad selectors, empty selector fields serializing as empty objects, and labels with empty key/value pairs. Signals are form serialization tests, selector evaluation against PVC fixtures, and UI checks for adding/removing label rows.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-selector-form.tsx -->
