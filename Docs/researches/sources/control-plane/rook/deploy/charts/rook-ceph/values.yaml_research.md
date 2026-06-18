
# sources/control-plane/rook/deploy/charts/rook-ceph/values.yaml

Purpose: defines default Helm values for the Rook Ceph operator chart, including images, CRD/RBAC toggles, operator scheduling and security, CSI operator/sidecar images, discovery settings, OBC controls, and monitoring.

Important APIs/types/functions: Helm values consumed by templates and subcharts. Key fields include `image`, `crds.enabled`, `resources`, `currentNamespaceOnly`, `reconcileConcurrentClusters`, `rbacEnable`, `containerSecurityContext`, `allowLoopDevices`, `monRunAsRoot`, `ceph-csi-operator`, `csi.*` sidecar image tags, `enableDiscoveryDaemon`, `useOperatorHostNetwork`, `hostpathRequiresPrivileged`, `enforceHostNetwork`, `imagePullSecrets`, `enableOBCWatchOperatorNamespace`, `obcAllowAdditionalConfigFields`, and `monitoring.enabled`.

Control flow: Helm templates read these values to decide which resources render and what environment, image, RBAC, ServiceMonitor, SCC, discovery, and CSI settings are applied. The `ceph-csi-operator` block configures the subchart when `csi.installCsiOperator` is true.

State and persistence: values do not persist directly until rendered into Kubernetes objects. CRD enablement is persistent and hazardous because deleting CRDs can destroy or orphan Rook-managed custom resources.

Dependencies/integration: integrates with all rook-ceph chart templates, the ceph-csi-operator subchart, Prometheus Operator, OpenShift SCCs, OBC provisioning, private registries, and Kubernetes scheduling/security APIs.

Risks: `image.tag: master` is a moving default; disabling CRD management after install can be destructive if CRDs are removed externally. Host networking, privileged hostPath mode, loop devices, and OBC additional config allowlists are security-sensitive. CSI image tag skew can break driver behavior.

Test signals: run `helm template` with default, production-pinned images, RBAC disabled, CRDs disabled, host-network enabled, monitoring enabled, and private registry secrets. Validate rendered manifests against the target Kubernetes/OpenShift API set.
