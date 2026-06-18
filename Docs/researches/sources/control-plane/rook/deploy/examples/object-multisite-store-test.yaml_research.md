# sources/control-plane/rook/deploy/examples/object-multisite-store-test.yaml

Purpose: attaches a test object store gateway to the `test-zone` multisite topology.

Important APIs/types/functions: `CephObjectStore/test-store` with one gateway instance on port 80 and `spec.zone.name: test-zone`.

Control flow: after the realm/zone resources exist, Rook deploys an RGW gateway bound to that zone.

State and persistence: object data follows the referenced zone's pools; the CR persists gateway desired state.

Dependencies/integration: requires `object-multisite-realm-test.yaml` or equivalent `test-zone`.

Risks: applying this before the zone exists leaves reconciliation pending.

Test signals: store ready, RGW service created, and S3 operations routed to `test-zone`.
