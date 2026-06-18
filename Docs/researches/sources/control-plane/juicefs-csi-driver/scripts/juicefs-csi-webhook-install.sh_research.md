<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/juicefs-csi-webhook-install.sh -->
## sources/control-plane/juicefs-csi-driver/scripts/juicefs-csi-webhook-install.sh

### Purpose
`juicefs-csi-webhook-install.sh` prints or installs JuiceFS CSI manifests for webhook mode. It can generate self-signed TLS assets inline or use cert-manager resources for webhook serving certificates.

### Important APIs, Types, And Functions
Main commands are `install`, `print`, and `help`, with `-c/--with-certmanager`. `gen_webhook_manifests` creates OpenSSL CA/server keys and embeds base64 TLS data and CA bundles into generated YAML. `gen_webhook_manifests_with_cert_manager` emits cert-manager `Certificate`/`Issuer` resources and webhook annotations. `need_cmd`, `check_cmd`, `ensure`, and `main` support command validation and dispatch.

### Control Flow
The non-cert-manager path checks for `mktemp`, `openssl`, and `curl`, creates a temporary directory, generates CA and server cert/key for `juicefs-admission-webhook.kube-system.svc`, base64-encodes them, writes a large manifest, and substitutes TLS placeholders. The cert-manager path emits a similar manifest but relies on cert-manager CA injection and sets a placeholder CA bundle. `main` either pipes generated YAML to `kubectl apply -f -` or prints it.

### State, Persistence, And Dependencies
The script creates temporary local certificate files and, on install, persists Kubernetes RBAC, ServiceAccounts, controller/dashboard resources, Services, Secrets or cert-manager resources, CSIDriver, MutatingWebhookConfigurations, and ValidatingWebhookConfiguration. Dependencies include bash, OpenSSL, curl, kubectl, and optionally cert-manager in the target cluster.

### Integration Points
Generated webhook paths must match `register.go`: `/juicefs/inject-v1-pod`, `/juicefs/serverless/inject-v1-pod`, `/juicefs/validate-secret`, `/juicefs/validate-pv`, and `/juicefs/validate-evict-pod`. Namespace selectors opt pods into normal or serverless injection, and object selectors opt Secrets into validation.

### Risks
The manifest is embedded static YAML, so it can drift from kustomize/Helm sources and Go path constants. The self-signed cert lifetime and generated private key are managed outside cert rotation. `curl` is required even though the shown generation path primarily uses OpenSSL. `err` is referenced by `need_cmd`/`ensure` but not defined in the visible helper block, so missing command handling may fail unexpectedly. Generated resources are hard-coded to `kube-system` and `juicefs-admission-webhook`.

### Test Signals
Useful checks include shell syntax validation, `print` output applying through `kubectl --dry-run=server`, path constant parity with `register.go`, certificate SAN correctness, cert-manager output containing injection annotations, validating webhook failure policies, namespace/object selectors, and install behavior when required commands are missing.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/juicefs-csi-webhook-install.sh -->
