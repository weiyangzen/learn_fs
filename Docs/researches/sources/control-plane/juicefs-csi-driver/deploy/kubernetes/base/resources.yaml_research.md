<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/resources.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/resources.yaml

## Purpose
Canonical base manifest for the JuiceFS CSI driver deployment. It defines the full set of deployable Kubernetes resources before release/webhook/CI overlays remove or specialize pieces.

## Important APIs, Types, and Resources
Contains 22 YAML documents: controller/node/dashboard ServiceAccounts, ClusterRoles and ClusterRoleBindings, `CSIDriver csi.juicefs.com`, driver ConfigMap, controller StatefulSet, node DaemonSet, mutating and validating webhook configurations, webhook Service/Secret, dashboard Deployment, and dashboard Service. It embeds CSI sidecars including provisioner, resizer, snapshotter, node-driver-registrar, and livenessprobe.

## Control Flow
Kustomize overlays consume this file as the root resource set. Applying the base directly creates both node and controller CSI components, admission webhook resources, and dashboard. The controller handles provisioning/resizing/snapshot control-plane calls while the DaemonSet handles node plugin registration and mount operations.

## State and Persistence
Persistent cluster state includes RBAC, ConfigMap settings, admission configurations, TLS Secret, Services, StatefulSet/DaemonSet/Deployment pod templates, hostPath-backed JuiceFS directories, CSI sockets, leader-election leases, and objects created later by the driver such as mount pods, jobs, and secrets.

## Dependencies and Integration Points
Depends on Kubernetes RBAC, admissionregistration.k8s.io/v1, storage.k8s.io/v1 CSIDriver, apps/v1 workloads, sig-storage sidecars, hostPath kubelet layout, and JuiceFS CSI driver flags. It integrates with all deployment overlays and generated top-level YAMLs.

## Risks
Major risks are broad privileged access, admission webhook availability blocking pod/serverless admission when enabled, secret mutation permissions, hostPath and mountPropagation sensitivity, and base changes breaking many overlays that assume exact resource/container names.

## Test Signals
Signals include building every overlay, server-side dry-run validation, CSI sanity/e2e suites, webhook admission tests, dashboard access tests, and RBAC review with least-privilege tooling.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/resources.yaml -->
