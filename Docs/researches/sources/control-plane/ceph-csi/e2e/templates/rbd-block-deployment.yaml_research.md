# sources/control-plane/ceph-csi/e2e/templates/rbd-block-deployment.yaml

Purpose: Kubernetes Deployment template for testing RBD raw block PVC use by multiple replicas. It runs three CentOS pods and exposes PVC `raw-block-pvc` as `/dev/xvda` through `volumeDevices`.

Important fields and flow: `metadata.name` and labels are `pod-block-rx-volume`; selector matches the pod template label; container sleeps forever to keep the block device attached. The `data` volume references the PVC with `readOnly: false`.

State, dependencies, and integration: creates an apps/v1 Deployment and resulting Pods that attach an existing block-mode RBD PVC. It is consumed by e2e helpers that validate deployment binding, multi-replica attach semantics, and block device availability.

Risks and test signals: requires a compatible block-mode PVC and access mode that permits the requested replica count. The `latest` CentOS image makes runtime behavior dependent on registry availability. Success is observed through Deployment readiness and pod-visible block device paths.
