# sources/distributed-fs/ipfs-kubo/core/node/builder.go

## Purpose
Defines node build configuration defaults and Fx option provisioning for Kubo node construction.

## Important APIs, Types, and Functions
Defines `BuildCfg`, methods `getOpt`, `fillDefaults`, `options`, and helper `defaultRepo`.

## Control Flow and State
`fillDefaults` supplies an in-memory mock repo, DHT routing option, and default host option when omitted. `options` installs repo, host, routing, and metrics context providers into Fx, registers repo close on lifecycle stop, and reads the repo config. `defaultRepo` generates an RSA identity, peer ID, base64 private key, fallback bootstrap list, default swarm addresses, and returns a mock repo over the provided datastore.

## Dependencies and Integration Points
Depends on datastore, Kubo config/repo, autoconf bootstrap peers, libp2p routing/host option types, crypto identity generation, peer IDs, shutdown helpers, and Uber Fx. Used by `core.NewNode`.

## Risks and Test Signals
Risks include default repo identity generation cost, mock repo use when callers expected persistent state, repo close lifecycle errors, shutdown timeout behavior handled elsewhere, and default swarm addresses in tests. Tests should cover nil/default build configs, injected repo/host/routing, config read failures, and lifecycle stop.
