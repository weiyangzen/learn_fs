# Research: sources/distributed-fs/ipfs-kubo/config/discovery.go

Purpose: Defines local discovery configuration.

Important APIs/types/functions: `Discovery` contains `MDNS`; `MDNS` has `Enabled bool`.

Control flow, state, and persistence: No functions. The boolean is persisted in config and consumed by node discovery setup.

Dependencies and integration points: Defaults are set in `InitWithIdentity`; profiles `server`, `local-discovery`, `test`, and `default-networking` mutate it.

Risks and test signals: There is no tri-state here, so explicit false and zero default are indistinguishable once omitted. Profile tests indirectly cover MDNS changes.
