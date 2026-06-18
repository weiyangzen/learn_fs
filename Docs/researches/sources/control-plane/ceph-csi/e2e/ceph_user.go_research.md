# sources/control-plane/ceph-csi/e2e/ceph_user.go

Purpose: e2e helpers for creating/deleting Ceph auth users and building least-capability strings for RBD and CephFS test users.

Important APIs/types/functions: constants for RBD/CephFS user and Kubernetes Secret names; `rbdNodePluginCaps`, `rbdProvisionerCaps`, `cephFSNodePluginCaps`, `cephFSProvisionerCaps`, `createCephUser`, and `deleteCephUser`.

Control flow: tests build caps based on pool/namespace, run `ceph auth get-or-create-key client.<user> ...` in the toolbox pod, trim returned key text, and later delete with `ceph auth del`.

State and persistence behavior: creates and deletes real Ceph auth entities in the test cluster. Kubernetes Secrets are referenced by constants but managed elsewhere.

Dependencies and integration points: depends on toolbox exec helper, `rookNamespace`, Ceph auth CLI, and capability recommendations from Ceph-CSI docs.

Risks: command construction joins capability strings into shell command text; inputs should remain controlled test values. Failed cleanup leaves test users in the cluster.

Test signals: indirectly exercised by e2e setup/teardown that provisions with dedicated Ceph users.
