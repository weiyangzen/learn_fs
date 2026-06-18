## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/externalrules.yaml

Purpose: Prometheus alert rules for external Ceph cluster mode, where Rook provisions Kubernetes consumers for a Ceph cluster not fully managed locally.

Important content: defines `persistent-volume-alert.rules` with `PersistentVolumeUsageNearFull` and `PersistentVolumeUsageCritical`. Both alerts calculate PVC used/capacity ratios by joining kubelet volume stats with PVC and StorageClass metadata, restricted to provisioners matching RBD or CephFS CSI drivers.

Control flow: selected by `templates/prometheusrules.yaml` when `.Values.cephClusterSpec.external.enable` is true. The PrometheusRule template can merge overrides or disable rules by alert name through `monitoring.prometheusRuleOverrides`.

State and persistence: renders into a `PrometheusRule` CR when monitoring rule creation is enabled. It does not mutate Ceph state but drives alerting state in Prometheus/Alertmanager.

Dependencies and integration points: requires kubelet volume metrics, kube-state-metrics PVC/storageclass metrics, and Prometheus Operator CRDs. Risks: label joins assume `cluster`, `namespace`, `persistentvolumeclaim`, and `storageclass` labels are available; external clusters get only PVC capacity alerts here, not full Ceph health coverage. Test signals should include YAML parse/render and PromQL validation where available.
