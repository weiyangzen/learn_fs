# Research: sources/distributed-fs/ipfs-kubo/config/swarm.go

Purpose: Defines libp2p swarm, relay, transport, connection manager, and resource manager configuration.

Important APIs/types/functions: `SwarmConfig`, `RelayClient`, `RelayService`, `Transports`, `ConnMgr`, `ResourceMgr`, and resource scope prefix constants.

Control flow, state, and persistence: No functions. The schema stores address filters, bandwidth/NAT settings, relay client/service settings, hole punching, transport enablement and priorities, connection manager watermarks/durations, and resource manager memory/fd/allowlist options. Values persist in config and are consumed by node/libp2p construction.

Dependencies and integration points: Profiles modify `Swarm.AddrFilters`, NAT port mapping, relay service, and connection manager fields. Removed `ResourceMgr.Limits` is guarded by a sentinel in `types.go`.

Risks and test signals: Misconfigured filters can block listeners or peer dials. Transport/security priority values can disable essential transports. Resource manager settings affect process stability. No direct tests here; `internal.go` defaults and profile behavior are indirect signals.
