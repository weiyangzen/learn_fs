# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: static RBAC for CephFS nodeplugin.

Important APIs/types/functions: creates `cephfs-csi-nodeplugin` ServiceAccount in default namespace, ClusterRole with node read, secret get/list/watch, configmap get, serviceaccount get, and serviceaccounts/token create, plus ClusterRoleBinding.

Control flow: authorizes nodeplugin pods to read runtime config/secrets and create tokens for KMS flows.

State and persistence behavior: Kubernetes RBAC state only.

Dependencies and integration points: referenced by the CephFS DaemonSet serviceAccountName.

Risks: broad secret access and hardcoded default namespace require operator review. Static sample comments instruct namespace replacement but do not enforce it.

Test signals: nodeplugin authorization and mount/encryption e2e.
