# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-table-page.tsx

## Purpose
`ConfigTablePage` presents `config.yaml` mount-pod patches as structured forms or read-only detail panels.

## APIs, Control Flow, and State
It parses `configData` into `OriginConfig`, converts it to UI `Config` via `ToConfig`, stores it, and pushes form values into a ProForm ref. In edit mode, `ProFormList` renders collapsible `MountPodPatchForm` entries and converts all values back to YAML with `ToOriginConfig` on every change. In read-only mode it maps patches to `MountPodPatchDetail`. `PvcPop` shows a popover of PVCs matched by each patch.

## Dependencies and Integration Points
It depends on config conversion types, YAML, Ant Design Pro forms, patch form/detail components, and matched PVC data from `useConfigPVC`.

## Risks and Test Signals
Parsing happens whenever `configData` or `edit` changes; invalid YAML only reports via `setError`. Form changes rewrite YAML order/shape. Test round-trip conversion, adding/removing patches, PVC popovers, invalid config text, and read-only rendering.
