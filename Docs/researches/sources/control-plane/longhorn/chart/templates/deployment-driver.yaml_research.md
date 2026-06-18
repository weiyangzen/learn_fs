# sources/control-plane/longhorn/chart/templates/deployment-driver.yaml

Purpose: deploys the single-replica `longhorn-driver-deployer` Deployment that waits for Longhorn Manager and then runs `longhorn-manager deploy-driver` to create or update CSI sidecars and driver components.

Important APIs/types/functions: Kubernetes `Deployment`, init container, manager image command `longhorn-manager -d deploy-driver`, Helm image registry coalescing, env vars `POD_NAMESPACE`, `NODE_NAME`, `SERVICE_ACCOUNT`, `KUBELET_ROOT_DIR`, CSI sidecar image variables, CSI replica-count variables, `GOCOVERDIR`, priority class, tolerations, node selectors, image pull secrets, and `longhorn.timezoneEnv`.

Control flow: an init container loops on `http://longhorn-backend:9500/v1` until it receives HTTP 200. The main container then starts the manager binary in deploy-driver mode, passes the manager image and internal manager URL, and conditionally exports CSI image, kubelet root, anti-affinity, replica-count, and coverage settings. Scheduling fields merge global, Longhorn-driver-specific, and Rancher Windows node placement settings.

State and persistence: the Deployment itself is persistent desired state. The deployer mutates cluster state by creating system-managed CSI objects outside this template. Optional coverage mode writes to host path `/go-cover-dir/`, and the driver deployment depends on service account and RBAC permissions from sibling templates.

Dependencies/integration: depends on the `longhorn-backend` service, manager image, CSI image values from `values.yaml`, `longhorn-service-account`, Role/RoleBinding permissions, private registry/image pull secret handling, and Longhorn Manager deploy-driver implementation. It also interacts with default settings such as `manager-url` and CSI storage capacity/topology settings.

Risks: the init wait loop has no explicit deadline, so a missing backend service can leave pods stuck indefinitely. Any registry, tag, or private-secret mismatch blocks driver deployment. A manager URL that resolves to an auth-protected external endpoint can cause internal JSON clients to receive HTML redirects. Node selector/toleration merges can accidentally unschedule the deployer, and coverage hostPath should not be enabled in production.

Test signals: template with default and custom registries, all CSI image overrides, Rancher Windows cluster placement, private registry strings and lists, coverage enabled, and custom kubelet root. In-cluster smoke tests should confirm the deployer reaches the backend, creates CSI components, and fails visibly on unavailable manager service or bad manager URL.
