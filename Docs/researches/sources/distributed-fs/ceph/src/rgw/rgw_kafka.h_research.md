# sources/distributed-fs/ceph/src/rgw/rgw_kafka.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares RGW's Kafka notification API: `reply_callback_t`, `connection_id_t`, manager `init()`/`shutdown()`, endpoint `connect()`, `publish()`, `publish_with_confirm()`, status conversion, and counter/limit accessors. It carries no persistent state itself; manager state lives in the implementation. It integrates with RGW notification endpoint code. Risks are secret-bearing connection ids, `-ESRCH` when uninitialized/stopped, and `-EBUSY` on queue pressure. Tests should cover connection-id equality, lifecycle, publish modes, callbacks, and counters before/after shutdown.
