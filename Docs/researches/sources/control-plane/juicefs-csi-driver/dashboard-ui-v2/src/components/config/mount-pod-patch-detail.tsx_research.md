<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-detail.tsx

## Purpose
`mount-pod-patch-detail.tsx` displays a read-only view of one mount pod patch, including PVC selector criteria, images, labels, annotations, mount options, environment, resources, host flags, cache directories, and matched PVCs.

## Important APIs, Types, and Functions
`MountPodPatchDetail` takes a `mountPodPatch` and optional `PVCWithPod[]`. Its local `kvDescribe` renders key/value arrays. It uses `ProCard`, `ProDescriptions`, Ant Design `Checkbox`, `FormattedMessage`, and `PVCWithSelector`.

## Control Flow, State, and Persistence
The component is pure rendering. It conditionally renders the selector card when `patch.pvcSelector` exists, always renders basic patch descriptions, maps arrays to inline code blocks, switches on cache directory `type`, and appends matched PVC information.

## Dependencies and Integration Points
It depends on config type definitions and is likely used by config detail pages to turn stored YAML into operator-readable UI. It shares selector/PVC presentation with config update confirmation.

## Risks and Test Signals
Risks include uncontrolled checkboxes in read-only contexts, falsy numeric rendering for `terminationGracePeriodSeconds` equal to 0, incomplete environment rendering for `valueFrom` refs, and cache-dir fallback strings that may obscure invalid data. Signals are render snapshots for all patch fields, empty array handling, cache dir variants, and matched PVC link rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-detail.tsx -->
