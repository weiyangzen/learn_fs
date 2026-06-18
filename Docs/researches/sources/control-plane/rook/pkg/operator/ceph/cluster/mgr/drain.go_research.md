# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain.go

Purpose: manages the mgr PodDisruptionBudget so clusters with multiple mgrs can tolerate voluntary disruptions while preserving at least one available mgr.

Important APIs and functions: `mgrPDBName` is `rook-ceph-mgr-pdb`. `reconcileMgrPDB` creates or updates a `policy/v1` PDB with selector `app=rook-ceph-mgr` and `maxUnavailable=1`. `deleteMgrPDB` removes the PDB when not needed.

Control flow: `mgr.go` calls `reconcileMgrPDB` when desired mgr count is greater than one and `deleteMgrPDB` otherwise. The reconcile helper uses controller-runtime `CreateOrUpdate` with a mutate function that replaces the PDB spec. Delete first GETs the PDB and ignores not-found errors, logging other get/delete errors.

State and persistence behavior: creates, updates, or deletes one namespaced PDB. It does not inspect cluster disruption-management settings directly in this file; caller policy determines whether and when it is invoked.

Dependencies and integration points: uses controller-runtime client, Kubernetes policy/v1 PDB, `k8sutil.AppAttr`, API errors, and the mgr cluster's namespace/context.

Risks: selector is broad for all mgr pods by app label and assumes all mgr pods in the namespace belong to the cluster. The mutate function overwrites the PDB spec, which is correct for reconciliation but will remove out-of-band edits. Delete logs errors without returning, so failure to delete does not fail mgr reconcile.

Test signals: `drain_test.go` covers create/update idempotence and deletion with fake clients.
