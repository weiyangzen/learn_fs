<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-basic.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-basic.tsx

## Purpose
`pod-basic.tsx` renders basic pod metadata and top-level pod actions such as diagnosis download, smooth pod upgrade, and YAML viewing.

## Important APIs, Types, and Functions
`PodBasic` uses `useMountPodImage`, `useVersion`, `useDownloadPodDebugInfos`, `YamlModal`, `UpgradeModal`, YAML serialization, and pod utility functions `isMountPod`, `isSysPod`, `omitPod`, `podStatus`, `getPodStatusBadge`, and `supportPodSmoothUpgrade`.

## Control Flow, State, and Persistence
It tracks only YAML modal open state. For mount pods it shows a diagnosis gather/download button. Smooth upgrade is shown when grace upgrade is enabled and both original and resolved mount images support pod smooth upgrade. YAML content is desensitized through `omitPod` unless the utility treats the pod as a system pod.

## Dependencies and Integration Points
It appears in pod detail pages and integrates with debug-info download, mount pod image lookup, version configuration, smooth upgrade action, and YAML modal display.

## Risks and Test Signals
Risks include capturing the initial image in state so prop changes do not update it, assuming the first container image is the mount image, rendering invalid dates if creation timestamp is missing, and YAML modal placement inside a tooltip. Signals are mount/non-mount pod render tests, desensitization checks, upgrade gating tests, and debug download error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-basic.tsx -->
