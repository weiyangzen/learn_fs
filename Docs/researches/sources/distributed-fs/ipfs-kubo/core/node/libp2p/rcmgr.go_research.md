# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr.go

Purpose: constructs and exposes libp2p resource manager limits, runtime usage views, and safety checks. Important APIs include `ResourceManager`, `LimitConfig`, `ResourceLimitsAndUsage`, `LimitsConfigAndUsage`, `MergeLimitsAndStatsIntoLimitsConfigAndUsage`, `LimitConfigsToInfo`, and `ensureConnMgrMakeSenseVsResourceMgr`.

Control flow: `ResourceManager` honors config and `LIBP2P_RCMGR`, computes limits plus user overrides, logs defaults, checks connection-manager compatibility, sets trace reporters, subnet limits, allowlisted multiaddrs, optional debug trace file, wraps the manager in `loggingResourceManager`, injects it into libp2p, and closes it on stop. If disabled, it injects `NullResourceManager`. Merge helpers combine concrete limits with runtime stats and render filtered resource info entries.

State and persistence: optional trace file `rcmgr.json.gz` is written in the repo when `LIBP2P_DEBUG_RCMGR` is set. Runtime error counts live in the logging wrapper. No datastore state.

Dependencies/integration: Kubo config/repo/helpers/shutdown, libp2p network/resource-manager, multiaddr, fx. Used by `LibP2P` and swarm resource commands.

Risks: conflicting resource limits vs connection manager high-water abort startup; invalid allowlist entries are skipped with logs; disabling manager removes protection. Tests cover logging wrapper; default calculations are in `rcmgr_defaults.go`.
