# sources/control-plane/rook/deploy/examples/object-multi-instance-test.yaml

Purpose: creates a test realm/zone topology with three object-store gateways sharing one zone but exposing different protocol combinations.

Important APIs/types/functions: `CephObjectRealm`, `CephObjectZoneGroup`, `CephObjectZone`, object stores `store-admin`, `store-s3`, `store-swift`, and `CephObjectStoreUser/multi-instance-user`.

Control flow: Rook creates the realm, zone group, zone pools, then reconciles three RGW instances against the same zone with protocol-specific settings before creating the user.

State and persistence: realm/zone metadata and bucket data live in Ceph RGW pools; CRs persist the topology.

Dependencies/integration: requires object multisite CRDs and a test cluster accepting one-replica pools.

Risks: multiple gateways sharing one zone can conflict if protocol or admin settings are misconfigured.

Test signals: all three object stores ready and user credentials usable against the intended protocol endpoints.
