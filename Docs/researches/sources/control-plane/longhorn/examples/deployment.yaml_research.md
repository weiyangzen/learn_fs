<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/deployment.yaml -->
# sources/control-plane/longhorn/examples/deployment.yaml

Purpose: MySQL Deployment example using a Longhorn RWO PVC.

Important APIs/types/functions: headless-style Service `mysql` with `clusterIP: None`, PVC `mysql-pvc`, and Deployment `mysql` with Recreate strategy, `mysql:5.6`, root password env var, port 3306, and liveness probe on `/var/lib/mysql/lost+found`.

Control flow: CSI provisions the PVC, Deployment creates one MySQL pod, kubelet mounts the volume, and the liveness probe checks filesystem mount availability.

State and persistence: MySQL data persists in the Longhorn PVC.

Dependencies/integration points: depends on Longhorn StorageClass, MySQL image behavior, RWO scheduling, and Kubernetes Service discovery.

Risks/test signals: password is hard-coded, MySQL 5.6 is obsolete, and liveness probe tests only mount presence. Test signals are PVC bound, MySQL readiness/application checks, data persistence across pod recreation, and backup/snapshot coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/deployment.yaml -->
