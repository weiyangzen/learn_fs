# Research: sources/distributed-fs/ipfs-kubo/config/version.go

Purpose: Defines version/user-agent related configuration and swarm update-check thresholds.

Important APIs/types/functions: `DefaultSwarmCheckPercentThreshold`; `Version` with `AgentSuffix`, `SwarmCheckEnabled`, and `SwarmCheckPercentThreshold`.

Control flow, state, and persistence: No functions. Values persist in config and are consumed by identify/version-check code outside this subset.

Dependencies and integration points: Uses optional string, flag, and optional integer helper types. `autoconf_client.go` uses Kubo version code for user-agent separately.

Risks and test signals: Agent suffix changes externally visible libp2p identify data. Update-check thresholds can affect warning noise. No direct tests in this subset.
