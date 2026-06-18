# sources/control-plane/rook/deploy/examples/object-multisite-pull-realm.yaml

Purpose: production-oriented example for pulling an RGW realm into a secondary Rook namespace.

Important APIs/types/functions: `Secret/realm-a-keys`, `CephObjectRealm/realm-a` with pull configuration, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-b` with replicated size 3 metadata/data pools, and `CephObjectStore/zone-b-multisite-store`.

Control flow: the secondary cluster imports realm metadata from the primary, creates a zone in that realm, and exposes it through a local RGW gateway.

State and persistence: realm/zone metadata and replicated pools persist in Ceph; pull credentials persist in Kubernetes Secret.

Dependencies/integration: needs primary realm endpoint, enough OSDs for replica size 3, and network connectivity between sites.

Risks: stale or leaked pull keys are sensitive; incorrect endpoints leave the realm pending.

Test signals: object realm status ready, RGW sync status healthy, and cross-site object replication.
