# sources/control-plane/ceph-csi/e2e/resize.go

Purpose: provides reusable PVC expansion helpers for filesystem and raw-block e2e cases.

Important APIs and flow: `expandPVCSize` fetches the latest PVC, updates `Spec.Resources.Requests[storage]`, then polls until resize conditions clear and `Status.Capacity` equals the requested size. `resizePVCAndValidateSize` accepts either a PVC YAML path or a prebuilt PVC, creates the PVC plus app pod, validates the initial mounted size, expands to `10Gi`, waits for the pod, revalidates the mounted size, and deletes both objects. `checkDirSize`, `checkDeviceSize`, `getDirSizeCheckCmd`, `getDeviceSizeCheckCmd`, and `checkAppMntSize` wrap pod-exec size probes.

State and persistence: mutates PVC spec/status in the Kubernetes API and validates filesystem or block-device state from inside an app pod. It creates and deletes one PVC and one pod in the test namespace when using `resizePVCAndValidateSize`.

Dependencies and integration: uses client-go PVC updates, Kubernetes wait polling, e2e pod exec helpers, `resource.Quantity`, and `helpers.RoundUpToGiB`. It is reused by RBD, CephFS, NFS, static PV, controller recovery, and upgrade tests.

Risks and test signals: `expandPVCSize` assumes any first condition of `Resizing` or `FileSystemResizePending` means it should keep waiting; additional conditions are only logged. Block size validation parses `blockdev --getsize64` output as a Kubernetes quantity and rounds to GiB. Filesystem validation shells through `df -h|grep`, which can be sensitive to mount path matching and human-readable units. Passing tests prove the controller expansion and node expansion paths converged and are visible in the workload.
