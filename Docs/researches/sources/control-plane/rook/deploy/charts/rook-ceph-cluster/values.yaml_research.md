## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values.yaml

Purpose: default values for installing one locally managed Rook Ceph cluster and common storage resources.

Important configuration: operator namespace, cluster name, optional config override, toolbox settings, monitoring and PrometheusRule overrides, Ceph image (`quay.io/ceph/ceph:v20.2.1` by default), and a large `cephClusterSpec`. Defaults create a converged cluster with `/var/lib/rook`, 3 mons, 2 mgrs, dashboard enabled with SSL, network encryption/compression disabled, crash and log collectors, host cleanup disabled unless explicitly confirmed, default daemon resources, disruption management, health checks, and storage discovery using all nodes and all devices. Defaults also create RBD, CephFS, and RGW object store definitions and StorageClasses; snapshot classes are disabled; EC pools are commented out; dashboard/objectstore ingress and routes are disabled by default.

Control flow: values are consumed by many templates using raw `toYaml`, ranges, and conditionals. Comments document CRD equivalents and production warnings.

State and persistence: these defaults can create real Ceph storage, host data directories, StorageClasses, pools, filesystems, object stores, and optional external exposure/alerting resources. `cleanupPolicy.confirmation` is the destructive cleanup gate.

Dependencies and integration points: depends on Rook operator, CRDs, Ceph image support, CSI driver naming, Prometheus/Gateway/Ingress/Snapshot APIs when enabled. Risks: `useAllNodes` and `useAllDevices` are dangerous in real clusters without careful node/device constraints; default StorageClass settings affect cluster-wide PVCs; image tag policy warns against floating major tags in production; cleanup and preserve/delete settings affect data retention. Tests should render default, external, monitoring, snapshot, and exposure scenarios.
