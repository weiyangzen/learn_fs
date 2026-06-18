# sources/control-plane/rook/deploy/examples/monitoring/localrules.yaml

Purpose: defines the local-cluster `PrometheusRule` set for Rook/Ceph monitoring in namespace `rook-ceph`, labeled for the `rook-prometheus` Prometheus instance. It is the alert policy bundle for Ceph health, mons, OSDs, MDS, mgr, placement groups, nodes, pools, health checks, hardware, Prometheus itself, RADOS, RBD mirroring, NVMe-oF, and cert-manager signals.

Important APIs/types/functions: Kubernetes `monitoring.coreos.com/v1` `PrometheusRule`; alerting groups include `cluster health`, `mon`, `osd`, `mds`, `mgr`, `pgs`, `nodes`, `pools`, `healthchecks`, `hardware`, `PrometheusServer`, `rados`, `generic`, `rbdmirror`, `nvmeof`, and `certmgr`. Representative alerts include `CephHealthError`, `CephMonDown`, `CephOSDDown`, `CephOSDFull`, `CephFilesystemDamaged`, `CephMgrIsAbsent`, `CephPGsInactive`, `CephPoolQuotaBytesCriticallyExhausted`, `CephDaemonSlowOps`, `PrometheusJobMissing`, `CephRBDMirrorImageSyncing`, and `CephNVMeoFGatewayDown`.

Control flow: the Prometheus Operator selects this object by labels and installs each rule group into Prometheus. Expressions query Ceph exporter and mgr metrics over windows, apply `for` durations to suppress short transients, and emit labels such as severity and annotations with runbook-oriented messages.

State and persistence: no application state is stored here. Rules are persisted as Kubernetes objects and Prometheus evaluates them against time-series data retained in the Prometheus store.

Dependencies/integration: depends on Prometheus Operator CRDs, Rook Ceph mgr/exporter metrics, kube-state or node metrics for some node checks, and matching `Prometheus.spec.ruleSelector` in `prometheus.yaml`.

Risks: alert expressions are tightly coupled to metric names and labels exported by Ceph versions. Local thresholds may be noisy for small test clusters, especially one-node pools, near-full OSDs, or intentionally absent daemons.

Test signals: `kubectl apply --server-side --dry-run`, `promtool check rules` after rendering YAML, and end-to-end Prometheus rule discovery with the `prometheus=rook-prometheus` selector.
