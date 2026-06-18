<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-csi-driver-config.example.yaml -->
# sources/control-plane/juicefs-csi-driver/juicefs-csi-driver-config.example.yaml

## Purpose
Example ConfigMap documenting the JuiceFS CSI driver runtime configuration schema and common `mountPodPatch` use cases.

## Important APIs, Types, and Resources
Defines `v1` ConfigMap `juicefs-csi-driver-config` in `kube-system` with embedded `config.yaml`. Important settings include `enableNodeSelector`, `enableNativeSidecar`, `enableSetQuota`, `enableControllerSetQuota`, `enableAutoRemoveRequestResources`, `enableAutoAbortStuckMountPod`, `enableKubeletListMountPod`, and a list-based `mountPodPatch` with PVC/node selectors, mountOptions, labels, resources, images, probes, annotations, env, volumes, initContainers, and DNS settings.

## Control Flow
The CSI driver reads `/etc/config/config.yaml` at startup. It applies global booleans to scheduling, quota, cleanup, stuck-mount handling, and kubelet list behavior, then recursively merges matching mountPodPatch entries into generated mount pod specs based on selectors.

## State and Persistence
The ConfigMap persists cluster-level driver configuration. Effective behavior persists through mounted config in controller/node pods and through generated mount pod specs derived from it.

## Dependencies and Integration Points
Depends on Kubernetes ConfigMap projection, driver config parsing/merge code, PVC and node label selectors, and template variables such as `${MOUNT_POINT}`, `${SUB_PATH}`, and `${VOLUME_ID}`. Integrates with deployment manifests mounting `/etc/config`.

## Risks
Risks include malformed YAML embedded in ConfigMap, selector patches applying too broadly, resource/image/probe changes destabilizing mount pods, and comments drifting from actual config defaults.

## Test Signals
Validate by applying a config, restarting driver pods, inspecting generated mount pods, and running config parser unit tests plus selected PVC/node selector e2e cases.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-csi-driver-config.example.yaml -->
