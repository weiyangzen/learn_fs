# sources/control-plane/rook/deploy/examples/object-openshift.yaml

Purpose: adapts the standard object-store example for OpenShift by using RGW port 8080 and an OpenShift `Route`.

Important APIs/types/functions: `CephObjectStore/my-store` with replicated metadata/data pools, `preservePoolsOnDelete: true`, gateway port 8080, anti-affinity, health check, and `Route/rook-ceph-rgw-my-store`.

Control flow: Rook creates pools and RGW gateway; OpenShift routes external HTTP traffic to the RGW service.

State and persistence: pools are preserved on object store deletion; route state persists as an OpenShift object.

Dependencies/integration: requires OpenShift route API and a Rook Ceph cluster in `rook-ceph`.

Risks: OpenShift-specific `Route` is not portable to vanilla Kubernetes; preserving pools requires manual lifecycle cleanup.

Test signals: route admitted, RGW service endpoint ready, and S3 access through the route host.
