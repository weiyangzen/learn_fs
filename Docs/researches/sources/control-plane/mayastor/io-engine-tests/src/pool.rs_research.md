<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/pool.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/pool.rs

Purpose: Pool builder utilities for both remote v1 gRPC pools and local in-process LVS pools.

Important APIs/types: `PoolBuilderOpts` stores name, UUID, bdev URI, and cluster size. `PoolBuilderRpc` wraps opts plus `SharedRpcHandle`; `PoolBuilderLocal` wraps local opts. `PoolOps` abstracts pool operations over local and remote variants. RPC builders create/grow/destroy pools, list replicas, and create replicas through generated gRPC clients. Local builders use `io_engine::lvs::Lvs::create_or_import`, create lvols directly, and clean up in `Drop` through `Reactor::block_on`.

Control flow: fluent builder methods require name/uuid/bdev before operations. `with_malloc*` convenience methods synthesize malloc bdev URIs.

State and dependencies: mutates remote pool service state or local SPDK/LVS state. Local `PoolLocal` owns optional cleanup behavior.

Risks and test signals: local and RPC implementations are not perfectly symmetric; local `get_replicas` is unimplemented. `Drop` cleanup can hide destroy errors with `.ok()`. Test by listing pools after create/grow/destroy and by `validate_pools_used_space` for replicated expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/pool.rs -->
