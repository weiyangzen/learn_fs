# sources/control-plane/mayastor/io-engine/tests/persistence.rs

Purpose: validates nexus persistent-store behavior in etcd: clean shutdown tracking, child health persistence after I/O failure, add/rebuild/remove child persistence, connection outage behavior, and transaction API behavior.

Important APIs/types/functions: v0 nexus/bdev RPCs, `NexusInfo`, `ChildInfo`, `PersistentStore`, `PersistentStoreBuilder`, `Client`, `MayastorTest`, `Url`, `start_infrastructure`, `create_nexus`, `publish_nexus`, `create_and_share_bdevs`, `child_info`, `no_child_info`, and `uuid`.

Control flow: infrastructure starts etcd plus four io-engine containers with `-p`. Clean/unexpected restart tests create two children and a nexus, read etcd JSON directly, and check `clean_shutdown` and child health before/after restart or destroy. `persist_io_failure` publishes a nexus, unshares one child, pauses etcd to force save retries, runs FIO, verifies runtime and persisted states, adds a third child, waits for rebuild, then removes it and confirms persistence updates. `persistent_store_connection` pauses etcd during create and expects timeout, then thawed etcd eventually completes creation. `pstor_txn_api` checks compare-and-set transaction success.

State and persistence behavior: direct etcd values are the main subject. The tests deserialize `NexusInfo` and inspect `clean_shutdown`, child UUID health, and child removal.

Dependencies and integration points: etcd binary/container, persistent-store client, libnvme/FIO, v0 gRPC, and transaction API.

Risks: fixed port/endpoints can collide; timed-out create intentionally may complete later.

Test signals: persisted booleans/child health, runtime degraded/faulted states, rebuild completion, removed child absence, create timeout then later visibility, and transaction success.
