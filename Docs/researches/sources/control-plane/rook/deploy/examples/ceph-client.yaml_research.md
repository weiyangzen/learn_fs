
# sources/control-plane/rook/deploy/examples/ceph-client.yaml

Purpose: creates two sample `CephClient` users for OpenStack-style RBD consumers named `glance` and `cinder`.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephClient`, metadata namespace `rook-ceph`, and Ceph caps strings. `glance` receives `mon: profile rbd` and `osd: profile rbd pool=images`; `cinder` receives RBD access to `volumes` and `vms` plus read-only access to `images`.

Control flow: Rook reconciles each client CR by creating/updating a Ceph auth user and a Kubernetes secret containing the key. Consumers then use those credentials for RBD pool access.

State and persistence: client desired state persists in Kubernetes; Ceph auth entries and generated secrets persist until the CR is removed and finalization completes.

Dependencies/integration: depends on the CephCluster, target pools `images`, `volumes`, and `vms`, Rook CephClient CRDs, and applications that consume generated secrets.

Risks: caps are powerful for the named pools and should be narrowed for production tenants. Referencing missing pools causes application failures even if the client is created. Namespace mismatch changes where secrets are generated.

Test signals: apply after pools exist, inspect generated secrets, run `ceph auth get client.glance/client.cinder`, and verify RBD operations are allowed only for intended pools.
