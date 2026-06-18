<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/webhook.yaml

## Purpose
Generated all-in-one manifest for deploying JuiceFS CSI controller/dashboard with admission webhooks and static TLS Secret material. It is kustomize output for the webhook overlay.

## Important APIs, Types, and Resources
Includes controller/dashboard service accounts, provisioner/snapshotter/dashboard RBAC, ConfigMap, static `juicefs-webhook-certs` Secret, webhook Service, dashboard Service/Deployment, controller StatefulSet with webhook flags, `CSIDriver`, two mutating webhook configurations, and one validating webhook configuration. It excludes node DaemonSet and node RBAC.

## Control Flow
Applying it creates static TLS material, starts the controller webhook server, and registers mutating/validating webhooks. kube-apiserver then routes matching admissions to `juicefs-admission-webhook` in `kube-system`.

## State and Persistence
Persistent cluster state includes the static Secret, webhook configurations and CA bundles, controller/dashboard workloads, RBAC, ConfigMap, and Services. Certificate rotation is not automatic unless the generated Secret is replaced.

## Dependencies and Integration Points
Depends on Kubernetes admissionregistration/v1, valid embedded webhook certificate data, sig-storage sidecars, and driver webhook behavior. Integrated into `scripts/juicefs-csi-webhook-install.sh` by `hack/update_install_script.sh`.

## Risks
Risks are stale/expired static certs, admission failure policy impact, generated-file drift, broad RBAC, and confusing controller-only scope if a full CSI node deployment is expected.

## Test Signals
Validate by dry-run apply, TLS Secret sanity checks, webhook call success, admission mutation/validation tests, and diffing against kustomize output.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook.yaml -->
