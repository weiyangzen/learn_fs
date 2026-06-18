<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/register.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/register.go

### Purpose
`register.go` wires JuiceFS admission handlers into a controller-runtime webhook server and defines their URL paths.

### Important APIs, Types, And Functions
Constants define `SidecarPath`, `ServerlessPath`, `SecretPath`, `PVPath`, and `EvictPodPath`. `Register(mgr, client)` registers mutating and optional validating webhook handlers.

### Control Flow
`Register` sets the controller-runtime logger, obtains the manager webhook server and scheme, always registers normal and serverless sidecar mutating handlers, and conditionally registers secret, PV, and eviction validators when `config.ValidatingWebhook` is true.

### State, Persistence, And Dependencies
The function mutates in-process manager/server registration state. Dependencies include controller-runtime manager/webhook packages, project config, k8s client, and handler constructors.

### Integration Points
The paths must match `juicefs-csi-webhook-install.sh` and deployment manifests. Admission requests for pod creation, secret validation, PV creation, and pod eviction reach `handler.go` through these registrations.

### Risks
Path drift between this file and generated installation manifests breaks webhooks. Validating handlers are gated by a process-global boolean, so deployment flags must align with installed `ValidatingWebhookConfiguration`. There is no idempotency guard if `Register` is called multiple times on the same server.

### Test Signals
Useful tests would assert registered paths and handler types under validating enabled/disabled modes and compare path constants against rendered webhook manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/register.go -->
