# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: RBAC for NVMe-oF nodeplugin.

Important APIs/types/functions: creates `ceph-nvmeof-nodeplugin` ServiceAccount, ClusterRole for node read, secret get, configmap get, serviceaccount get, PV get, volumeattachment list/get, and serviceaccounts/token create, plus ClusterRoleBinding.

Control flow: authorizes nodeplugin access to configuration, credentials/tokens, and storage object metadata during node operations.

State and persistence behavior: Kubernetes RBAC state only.

Dependencies and integration points: referenced by NVMe-oF DaemonSet and SCC.

Risks: namespace defaults to `default`; secret access is narrower than RBD/CephFS but still sensitive. Binding name and service account must match DaemonSet.

Test signals: NVMe-oF node staging/publish and KMS/token authorization behavior.
