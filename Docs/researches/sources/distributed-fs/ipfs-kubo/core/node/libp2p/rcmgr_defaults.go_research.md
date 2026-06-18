# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_defaults.go

Purpose: computes default libp2p resource-manager limits from memory, file descriptors, and connection-manager settings. Important API is `createDefaultLimitConfig`.

Control flow: it defaults max memory to half total memory and max FDs to half the detected descriptor limit. It builds partial limits for system, transient, allowlisted, service/protocol/conn/stream, and per-peer scopes. It scales libp2p defaults, sets service limits, then increases inbound connection and stream limits to be at least twice ConnMgr high-water and a configured minimum when applicable. It returns a concrete config and startup message.

State and persistence: no writes; reads process/system memory and FD limits.

Dependencies/integration: `pbnjay/memory`, Kubo config, fd helper, go-libp2p resource-manager defaults. Called by `LimitConfig` before user overrides are applied.

Risks: memory and FD detection errors directly affect resource limits; comments note memory accounting gaps in libp2p, so inbound connection limits are a defensive proxy. Test coverage is indirect through resource-manager startup and command behavior.
