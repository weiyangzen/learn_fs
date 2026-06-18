# sources/control-plane/rook/deploy/examples/object-multisite-realm-test.yaml

Purpose: creates only the realm, zone group, and zone pieces of a test multisite object topology.

Important APIs/types/functions: `CephObjectRealm/test-realm`, `CephObjectZoneGroup/test-zonegroup`, and `CephObjectZone/test-zone` with one-replica metadata/data pools and `sharedPools` support.

Control flow: Rook reconciles the realm hierarchy before any object store gateway is attached.

State and persistence: RGW realm/zone metadata and zone pools persist in Ceph; CRs persist desired topology.

Dependencies/integration: intended to pair with `object-multisite-store-test.yaml`.

Risks: without a store, this creates backend topology but no client endpoint; one-replica pools are unsafe for production.

Test signals: realm, zonegroup, and zone statuses ready before creating the store.
