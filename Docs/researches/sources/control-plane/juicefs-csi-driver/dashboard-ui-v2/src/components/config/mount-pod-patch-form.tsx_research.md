<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-form.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-form.tsx

## Purpose
`mount-pod-patch-form.tsx` renders the editable form for a mount pod patch, covering selector fields and all supported patch knobs.

## Important APIs, Types, and Functions
`MountPodPatchForm` composes `PVCSelectorForm`, `ProDescriptions`, `ProForm.Item`, `ProFormList`, `ProFormText`, `ProFormSelect`, `ProFormCheckbox`, `ProFormDependency`, `Input`, and `InputNumber`. It supports image overrides, labels, annotations, mount options, env vars with value/configMap/secret/fieldRef sources, resource requests/limits, host networking/PID flags, termination grace period, and cache directories of type HostPath/PVC/EmptyDir.

## Control Flow, State, and Persistence
The component has no local state; form state is owned by an ancestor ProForm. Dynamic subfields are selected by `ProFormDependency` for env `valueType` and cache `type`. Creator records set defaults for env and cache list entries.

## Dependencies and Integration Points
Field names are the persistence contract back to YAML serialization of `mountPodPatch`. It must match `MountPodPatchDetail`, backend config schema, and Kubernetes environment/resource/volume models.

## Risks and Test Signals
Risks include nested `ProForm.Item` structures that may not bind as intended, UI-only `valueType` fields leaking into serialized config, missing validation on CPU/memory quantities and mount option strings, and incomplete EmptyDir HugePages semantics. Signals are form submit serialization tests, edit-existing patch initialization, env valueFrom variants, cache dir validation, and round trip through YAML config update.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-form.tsx -->
