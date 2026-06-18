# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-provisioner-rbac.yaml

Purpose: generated RBAC for the NFS provisioner.

Important APIs/types/functions: creates `nfs-csi-provisioner` ServiceAccount, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, volumeattachments/status, CSINodes, snapshot resources/classes/content/status, volumeattributesclasses, and namespace Role/RoleBinding for configmaps and leases.

Control flow: authorizes external sidecars to provision, attach, resize, snapshot, and lead-elect NFS CSI operations.

State and persistence behavior: RBAC objects only; authorized controllers mutate Kubernetes storage resources.

Dependencies and integration points: used by NFS provisioner Deployment and CSI sidecars.

Risks: generated and should be changed at source. The Role keeps legacy configmap create/delete support. Hardcoded default namespace must be adjusted.

Test signals: NFS provisioner sidecar authorization and storage e2e.
