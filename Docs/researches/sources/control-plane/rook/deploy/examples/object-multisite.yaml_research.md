# sources/control-plane/rook/deploy/examples/object-multisite.yaml

Purpose: production-style single-site piece of an RGW multisite setup.

Important APIs/types/functions: `CephObjectRealm/realm-a`, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-a` with size 3 replicated metadata/data pools and `bulk` data parameter, plus `CephObjectStore/multisite-store`.

Control flow: Rook configures RGW realm metadata, zone group, zone pools, and a gateway for the zone.

State and persistence: RGW metadata and objects persist in the configured replicated pools.

Dependencies/integration: needs sufficient OSDs and may later pair with a secondary pull-realm manifest.

Risks: topology changes after buckets exist can disrupt multisite sync; one gateway instance is not highly available.

Test signals: realm/zone/store ready, `radosgw-admin period get` valid, and S3 operations succeed.
