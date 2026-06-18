# sources/control-plane/rook/deploy/examples/object-multisite-test.yaml

Purpose: provides a compact test multisite configuration with one realm, one zone group, one zone, and one store.

Important APIs/types/functions: `CephObjectRealm/realm-a`, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-a` with one-replica pools and compression disabled for data, and `CephObjectStore/multisite-store`.

Control flow: Rook creates the topology in dependency order and starts one RGW gateway in `zone-a`.

State and persistence: test pools hold object and metadata state; CRs hold desired realm and gateway state.

Dependencies/integration: requires Rook object controllers and a small test Ceph cluster.

Risks: replica size 1 and `requireSafeReplicaSize: false` are test-only.

Test signals: all CRs ready and basic S3 object lifecycle against `multisite-store`.
