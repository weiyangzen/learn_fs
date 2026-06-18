<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/influxdb.yaml -->
# sources/control-plane/longhorn/dev/upgrade-responder/manifests/influxdb.yaml

Purpose: development InfluxDB 1.8 deployment and service for upgrade responder telemetry.

Important APIs/types/functions: creates `influxdb-creds` Secret with base64 root credentials, a 2Gi Longhorn PVC, an `apps/v1` Deployment using `docker.io/influxdb:1.8.10`, and a ClusterIP Service on 8086.

Control flow: Kubernetes mounts the PVC at `/var/lib/influxdb`, injects credentials from the Secret, starts one InfluxDB replica, and exposes it internally as `influxdb.default.svc.cluster.local:8086`.

State and persistence: InfluxDB data persists in the Longhorn PVC; credentials persist in the Kubernetes Secret.

Dependencies/integration points: depends on Longhorn StorageClass, InfluxDB 1.x behavior, the upgrade responder values pointing at this service, and namespace `default`.

Risks/test signals: root/root credentials are demo-grade, no resource limits are set, and InfluxDB 1.8 is legacy. Test signals are PVC binding, pod readiness, service DNS, credential login, and upgrade responder writes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/influxdb.yaml -->
