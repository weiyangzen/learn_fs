# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/volumeMounts-table.tsx

## Purpose
`VolumeMountsTable` correlates an application pod's volume mounts with PVCs, PVs, and JuiceFS mount pods.

## APIs, Control Flow, and State
It fetches mount pods, PVCs, and PVs for the given pod with `usePods`, `usePVCsOfPod`, and `usePVsOfPod`. `dataSource()` builds maps by volume mount name, PVC name, PV claimRef name, and mount pod `volume-id`, then walks `pod.spec.volumes` to create rows containing PVC, PV, volume mount, and mount pod. Rows show PVC status/link, container path, subPath, and mount pod status/link.

## Dependencies and Integration Points
It integrates with pod detail pages, hook endpoints under `/api/v1/pod/:ns/:name/*`, Kubernetes volume types, and badge/status utilities.

## Risks and Test Signals
`rowKey` uses `volumeMount?.name`, which may be empty or duplicated across containers. The PV map ignores namespace and assumes claim names are unique in the pod context. Test multi-container same volume names, CSI volumeHandle matching, storage-class fallback matching, and pods with no PVC volumes.
