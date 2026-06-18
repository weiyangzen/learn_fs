# sources/control-plane/rook/deploy/examples/operator-openshift.yaml

Purpose: deploys the Rook Ceph operator on OpenShift with SecurityContextConstraints and OpenShift-specific privileged hostpath behavior.

Important APIs/types/functions: `SecurityContextConstraints/rook-ceph` and `rook-ceph-csi`, `ConfigMap/rook-ceph-operator-config`, CSI operator image set ConfigMap, `OperatorConfig`, RBD and CephFS CSI `Driver` CRs, and `Deployment/rook-ceph-operator`.

Control flow: OpenShift SCCs permit required privileged/host operations, ConfigMaps feed operator settings, CSI CRs configure drivers, and the deployment runs `docker.io/rook/ceph:master` with args `ceph operator`.

State and persistence: operator desired settings persist in ConfigMaps and CRs; the operator maintains cluster state through watched Ceph CRs.

Dependencies/integration: requires namespace `rook-ceph`, Rook RBAC/common manifests, OpenShift SCC API, and CSI operator CRDs.

Risks: privileged SCCs and host access are powerful; image tag `master` is mutable; `ROOK_HOSTPATH_REQUIRES_PRIVILEGED=true` differs from vanilla Kubernetes.

Test signals: SCC binding accepted, operator deployment ready, CSI driver CRs reconciled, and logs show successful startup.
