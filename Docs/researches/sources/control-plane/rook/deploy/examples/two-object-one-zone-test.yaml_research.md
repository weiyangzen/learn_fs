# sources/control-plane/rook/deploy/examples/two-object-one-zone-test.yaml

Purpose: tests two RGW object stores attached to a single zone.

Important APIs/types/functions: `CephObjectRealm/two-object-one-zone`, `CephObjectZoneGroup/two-object-one-zone`, `CephObjectZone/object-separate-pools`, and object stores `two-object-one-zone-alpha` and `two-object-one-zone-beta`.

Control flow: Rook creates the realm and zone, then deploys two separate RGW gateway services that reference the same zone.

State and persistence: both stores share zone metadata and pools; gateway desired state is separate per CR.

Dependencies/integration: requires a pre-existing or default pool topology for the zone.

Risks: shared zone means metadata coupling between both gateway instances.

Test signals: both stores ready and objects/buckets behave consistently through either endpoint according to zone semantics.
