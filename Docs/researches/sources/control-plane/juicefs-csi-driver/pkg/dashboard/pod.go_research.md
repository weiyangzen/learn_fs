# sources/control-plane/juicefs-csi-driver/pkg/dashboard/pod.go

## Purpose
`pod.go` implements pod-focused dashboard HTTP handlers: listing app/system/CSI pods, fetching pod details, logs/events/node relations, mount/app-pod relationships, debug bundle downloads, websocket terminal operations, and smooth single-pod upgrade.

## Important APIs, Types, And Functions
Key handlers include `listAppPod`, `listSysPod`, `listCSINodePod`, `getPodMiddileware`, `getPodHandler`, `getPodLatestImage`, `getPodEvents`, `getPodNode`, `getPodLogs`, `listMountPodsOfAppPod`, `listAppPodsOfMountPod`, websocket wrappers for pod service methods, `downloadDebugFile`, `downloadDebugInfo`, and `smoothUpgrade`.

## Control Flow
Middleware fetches the requested pod from the cache and admits app pods, system pods, or PVC-using app pods. Pod detail desensitizes non-system pods. Log handlers validate container names and either return raw logs or delegate websocket streaming. Relationship handlers call `PodService` methods. `downloadDebugInfo` builds a temporary `/tmp/<namespace>/<pod>/info` directory, downloads CSI node and mount-pod logs/YAML, PV/PVC/global config YAML when available, zips the directory, and returns it. `smoothUpgrade` opens a websocket, checks upgrade is enabled, finds the mount pod and its CSI node, then execs `juicefs-csi-driver upgrade <mountpod>` in the CSI node plugin container.

## State And Persistence
Most operations are read-only. Debug bundle generation writes temporary files under `/tmp` and removes the info directory afterward. Smooth upgrade mutates cluster runtime state indirectly through an exec command in a CSI node pod.

## Dependencies And Integration Points
It depends on `PodService`, `EventService`, PV service lookup, `resource.DownloadPodLog`, `resource.ExecInPod`, `config.GenSettingAttrWithMountPod`, global config loading, and dashboard utility functions for pod classification and safe path names.

## Risks
`getCSINode` returns `&pods[0]` without checking length, so callers can panic if no CSI node pod is found; some callers wrap it indirectly but not all. `downloadDebugInfo` appears to call `GetPersistentVolume` when it intends to fetch a PVC after finding a PV, which may prevent PVC YAML capture. Exec/log/debug endpoints are privileged and need external auth controls. Temporary directory permissions use broad mode `0777`.

## Test Signals
No direct tests are present. Useful coverage should include middleware admission, desensitization, missing CSI node handling, debug bundle file composition, and smooth-upgrade command generation.
