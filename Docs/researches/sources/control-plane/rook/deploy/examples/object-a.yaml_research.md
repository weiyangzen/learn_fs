# sources/control-plane/rook/deploy/examples/object-a.yaml

Purpose: defines one RGW object store, `store-a`, using pre-created shared pools.

Important APIs/types/functions: `CephObjectStore/store-a` in `rook-ceph`, `spec.sharedPools`, `gateway.port: 80`, `gateway.instances: 1`, anti-affinity against other RGW pods, and `priorityClassName: system-cluster-critical`.

Control flow: Rook binds the store to shared object pools and deploys one RGW gateway pod/service.

State and persistence: object data and metadata live in the referenced shared pools; the CR stores gateway desired state.

Dependencies/integration: intended to pair with `object-shared-pools.yaml` and `storageclass-bucket-a.yaml`.

Risks: shared pools create coupling between stores; deleting or changing the shared pools affects all dependent stores.

Test signals: RGW service creation, store status ready, and bucket provisioning through the matching bucket storage class.
