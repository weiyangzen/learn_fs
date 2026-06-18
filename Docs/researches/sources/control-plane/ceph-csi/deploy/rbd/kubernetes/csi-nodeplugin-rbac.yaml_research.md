# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: static RBAC for the RBD nodeplugin.

Important APIs/types/functions: creates `rbd-csi-nodeplugin` ServiceAccount in default namespace, ClusterRole for node read, secret get/list/watch, configmap get, serviceaccount get, PV get, volumeattachment list/get, and token creation; binds it with ClusterRoleBinding.

Control flow: authorizes nodeplugin API calls for topology, config, KMS/secret access, PV/attachment lookup, and service account token projection.

State and persistence behavior: Kubernetes RBAC state only.

Dependencies and integration points: referenced by RBD DaemonSet and KMS/encryption flows.

Risks: broad secret access and hardcoded default namespace. Namespace comments rely on manual replacement.

Test signals: RBD node stage/publish, encryption, and authorization logs.
