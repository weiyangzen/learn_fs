## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-httproute.yaml

Purpose: renders Gateway API HTTPRoute resources for Ceph RGW object stores with route exposure enabled.

Important template behavior: iterates `.Values.cephObjectStores` and checks `route.enabled` via `dig`. For enabled stores, it creates `gateway.networking.k8s.io/v1` `HTTPRoute` in the release namespace, with optional annotations, hostname, parentRefs, one backendRef to `rook-ceph-rgw-<store-name>`, port from route override or gateway secure/plain port, and path match defaults.

Control flow: pure values range with optional output per object store.

State and persistence: creates HTTPRoute resources that route external or internal Gateway API traffic to RGW services. It does not configure RGW itself.

Dependencies and integration points: requires Gateway API CRDs and a compatible Gateway/controller. It depends on Rook operator-created RGW service naming. Risks: if route port defaults to a nil gateway port, rendered manifests may be invalid; parentRefs and hostnames must match cluster Gateway policy; securePort selection may need TLS backend alignment. Test signals should include Helm render with route enabled and Gateway API validation.
