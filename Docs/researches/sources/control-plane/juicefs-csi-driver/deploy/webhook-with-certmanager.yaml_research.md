<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook-with-certmanager.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/webhook-with-certmanager.yaml

## Purpose
Generated all-in-one manifest for deploying JuiceFS CSI controller/dashboard with admission webhooks and cert-manager-managed TLS. It is kustomize output for the webhook-with-certmanager overlay.

## Important APIs, Types, and Resources
Includes controller/dashboard service accounts, provisioner/snapshotter/dashboard RBAC, ConfigMap, webhook Service, dashboard Service/Deployment, controller StatefulSet, `Certificate juicefs-cert`, `Issuer juicefs-selfsigned`, `CSIDriver`, mutating webhook configurations for standard and serverless admission, and validating webhook configuration. It excludes the node DaemonSet and node RBAC.

## Control Flow
Applying it installs controller-only admission infrastructure. cert-manager reconciles TLS Secret and CA injection, the controller StatefulSet runs with webhook flags, and kube-apiserver calls the webhook Service during matching admissions.

## State and Persistence
Persistent state includes RBAC, webhook configurations, cert-manager CRDs/status, generated TLS Secret, dashboard and controller workloads, CSI driver object, and ConfigMap settings. There is no node-side DaemonSet state from this manifest.

## Dependencies and Integration Points
Depends on cert-manager, Kubernetes admissionregistration/v1, sig-storage sidecars, JuiceFS CSI webhook code, and the dashboard. Integrates with install script update tooling and webhook-with-certmanager kustomize overlay.

## Risks
Risks include admission outage if the controller or cert-manager is unavailable, broad controller RBAC, generated-file drift, and the absence of node DaemonSet resources if users expect a complete CSI node deployment from this manifest.

## Test Signals
Signals are `kustomize build` parity, server-side dry-run on a cert-manager cluster, Certificate Ready/CA injection checks, webhook admission e2e tests, and controller/dashboard readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook-with-certmanager.yaml -->
