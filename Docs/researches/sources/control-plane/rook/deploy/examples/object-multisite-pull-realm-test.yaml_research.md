# sources/control-plane/rook/deploy/examples/object-multisite-pull-realm-test.yaml

Purpose: test-sized secondary-cluster multisite configuration that pulls a realm from a primary object store.

Important APIs/types/functions: `Secret/realm-a-keys`, `CephObjectRealm/realm-a` with `spec.pull`, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-b` using one-replica pools, and `CephObjectStore/zone-b-multisite-store`.

Control flow: Rook uses the realm pull endpoint and keys to import realm metadata, creates a secondary zone, then starts an RGW for that zone.

State and persistence: pulled realm metadata and zone pools persist in the secondary Ceph cluster; credentials persist in the secret.

Dependencies/integration: requires a reachable primary zone endpoint and valid access/secret keys.

Risks: placeholder secret data must be replaced; one-replica pools are test only.

Test signals: realm pull succeeds, secondary zone appears in `radosgw-admin zone list`, and sync status advances.
