<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-object.yaml -->
# sources/control-plane/rook/tests/manifests/test-object.yaml

Purpose: small test `CephObjectStore` manifest for a single-OSD environment. It provides a minimal RGW object store named `my-store`.

Important structure: defines metadata and data pools with replicated size 1, `preservePoolsOnDelete: false`, gateway port 80, and one gateway instance. The comment indicates it is applied as an object test manifest.

State, persistence, and integration: creates RGW pools, deployment, and service state in the `rook-ceph` namespace. Dependencies include Rook object store CRDs and a functioning Ceph cluster. Risks include single-replica data loss assumptions, non-preserved pools on delete, and no secure port by default. Test signals are RGW pod readiness, service availability, and successful object API operations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-object.yaml -->
