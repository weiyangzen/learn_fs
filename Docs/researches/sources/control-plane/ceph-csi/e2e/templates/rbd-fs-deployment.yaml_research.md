# sources/control-plane/ceph-csi/e2e/templates/rbd-fs-deployment.yaml

Purpose: Kubernetes Deployment template for testing filesystem RBD PVC use across three nginx replicas.

Important fields and flow: Deployment `pod-fs-rx-volume` selects matching labels, runs `nginx:latest`, and mounts PVC `rbd-pvc` at `/var/lib/www/html`. The template keeps `readOnly: false` for write-capable filesystem validation.

State, dependencies, and integration: creates a Deployment and pods that depend on an existing filesystem-mode RBD PVC. E2E helpers load and optionally adjust replica counts to test binding and controller behavior.

Risks and test signals: multi-replica RBD filesystem use requires access-mode compatibility. The `latest` image tag and external registry can affect reproducibility. Readiness confirms Kubernetes attach/mount and application container startup.
