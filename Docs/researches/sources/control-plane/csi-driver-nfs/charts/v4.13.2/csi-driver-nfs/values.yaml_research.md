# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/values.yaml

## Purpose
This values file supplies the default runtime and rendering configuration for the v4.13.2 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It defines image defaults, service account names, RBAC names, driver settings, feature flags, kubelet directory, controller settings, node-driver-registrar health settings, node settings, external snapshotter settings, snapshot class defaults, image pull secrets, and storage class examples. Compared with v4.13.1, the only values change is `image.nfs.tag: v4.13.2`.

## Control Flow, State, and Persistence
Values drive Helm conditionals for RBAC, CRDs, snapshot controller deployment, volume snapshot class creation, storage classes, sidecar inclusion, mount option propagation, and scheduling. Defaults create the driver workloads and RBAC, enable the controller-side snapshotter, but do not deploy the external snapshot controller, CRDs, snapshot class, or storage class.

## Dependencies and Integration Points
The file integrates chart templates with CSI sidecar image versions, registry composition through `image.baseRepo`, Kubernetes priority classes, host kubelet paths, NFS snapshot behavior, and optional storage class parameters.

## Risks and Test Signals
Risks are sidecar/driver version skew, enabling snapshots without a cluster snapshot controller/CRDs, privileged host mount behavior, and registry mirroring mistakes with leading-slash repository values. Signals are `helm template` matrices, chart install/upgrade from v4.13.1, rendered image tag verification, PVC lifecycle, expansion, node registration, and optional snapshot tests.
