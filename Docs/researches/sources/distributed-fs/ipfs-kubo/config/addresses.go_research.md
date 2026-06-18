# Research: sources/distributed-fs/ipfs-kubo/config/addresses.go

Purpose: Defines the address-related configuration schema for a Kubo node.

Important APIs/types/functions: `Addresses` has `Swarm`, `Announce`, `AppendAnnounce`, `NoAnnounce`, `API`, and `Gateway` fields. `API` and `Gateway` use the custom `Strings` type so JSON can hold a single string or an array.

Control flow, state, and persistence: No functions. Values are persisted in the repo config and consumed by libp2p host, identify, API listener, and gateway listener setup.

Dependencies and integration points: Integrated into top-level `Config`, defaults from `addressesConfig`, and profiles such as `server`, `test`, and `default-networking`.

Risks and test signals: Invalid multiaddrs are not validated here; downstream listener/routing setup must reject them. Tests are indirect via config reflection/default profile behavior.
