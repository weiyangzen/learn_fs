# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/yaml-modal.tsx

## Purpose
`YamlModal` is a reusable Monaco-backed YAML viewer/editor used across resource detail, config, and CacheGroup flows.

## APIs, Control Flow, and State
Props include `isOpen`, `onClose`, `content`, optional `editable`, `onSave`, and `saveButtonText`. It stores edited data in local state, renders an Ant Design modal, and when editable adds a primary save button that passes the current editor data to `onSave`.

## Dependencies and Integration Points
It depends on Monaco and Ant Design. Callers stringify Kubernetes resources or YAML templates and optionally parse/update them on save.

## Risks and Test Signals
The editor value is bound to `content`, not local `data`, so external content changes dominate display while `onChange` only affects saved data. Local state is initialized once and not reset on `content` changes. Test editable saves, reopening with different content, and read-only rendering.
