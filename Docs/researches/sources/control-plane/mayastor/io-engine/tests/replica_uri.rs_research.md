# sources/control-plane/mayastor/io-engine/tests/replica_uri.rs

Purpose: integration test ensuring replica share URIs carry a per-replica unique `uuid=` query parameter distinct from the volume UUID and usable in nexus children.

Important APIs/types/functions: `replica_uri` uses v0 Mayastor RPCs for pools, replicas, sharing, and nexus creation. Helpers `pool_name`, `get_bdev`, and `check_replica_uri` parse `Replica.uri` via `url::Url` and compare its `uuid` query value with the backing `Bdev.uuid`.

Control flow: two io-engine containers are started, pools are created, one replica is created shared over NVMe-oF and one local/loopback replica is created unshared then shared/unshared. Each URI is validated, then a nexus is created with both URIs.

State/persistence: transient pools, replicas, bdev UUIDs, and a nexus. The test asserts UUID identity state is exposed consistently through both replica and bdev listings.

Dependencies/integration: covers v0 gRPC API compatibility, replica URI formatting, bdev metadata, NVMe-oF sharing, and MOAC-style volume/nexus child addressing.

Risks: query parsing assumes `uuid=` exists and is the only query value used for the assertion. The fixed `VOLUME_UUID` is reused across two replicas, making the per-replica bdev UUID distinction critical.

Test signals: failure indicates URI generation no longer exposes unique replica identity or nexus child URI consumption regressed.
