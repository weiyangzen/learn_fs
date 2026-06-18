<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/mod.rs

Purpose: Nexus module facade, JSON-RPC registration entry point, shutdown orchestration, and runtime feature toggles for nexus behavior.

Important APIs/types: re-exports nexus creation (`nexus_create`, `nexus_create_v2`), `Nexus`, status/state/target/reservation types, child state/error types, iterators/lookups, persistence types (`NexusInfo`, `PersistentNexusInfo`, transactions), snapshot status/descriptor types, and internal channel/module/share/persistence helpers. `register_module(register_json)` registers the SPDK nexus module and optionally a JSON-RPC `nexus_share` method. `shutdown_nexuses()` collects mutable nexus iterators, destroys each nexus with persistence, and emits shutdown events. Static atomics toggle partial rebuild, nexus reset, channel debug, and all-thread nexus channel behavior.

Control flow: JSON-RPC share validates `protocol == "nvmf"`, looks up a bdev by name, shares it with ANA and controller ID range, and returns the share URI. Shutdown collects before iterating to avoid invalidation while SPDK destroys bdevs.

State and dependencies: mutates SPDK module registry, nexus lifecycle/persistence, event stream, bdev sharing state, and global atomic feature flags.

Risks and test signals: JSON-RPC comment notes it shares a bdev, not necessarily a nexus. Shutdown logs and emits events on errors rather than aborting the loop. Test registration, share RPC validation, clean shutdown persistence, and feature-flag-sensitive rebuild/reset behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/mod.rs -->
