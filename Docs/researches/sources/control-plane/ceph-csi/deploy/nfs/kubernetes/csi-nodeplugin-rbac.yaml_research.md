# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: minimal static ServiceAccount manifest for the NFS nodeplugin.

Important APIs/types/functions: creates `ServiceAccount` named `nfs-csi-nodeplugin`; no ClusterRole or binding appears in this file.

Control flow: the NFS node DaemonSet references this account, relying on limited or separately managed permissions.

State and persistence behavior: namespace-scoped identity object only.

Dependencies and integration points: consumed by `csi-nfsplugin.yaml`.

Risks: if nodeplugin later needs API access, this file alone is insufficient. Namespace is implicit, unlike many other static manifests.

Test signals: pod admission and any API authorization failures in nodeplugin logs.
