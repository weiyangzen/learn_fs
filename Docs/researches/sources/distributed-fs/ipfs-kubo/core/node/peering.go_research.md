# sources/distributed-fs/ipfs-kubo/core/node/peering.go

Purpose: constructs and configures the peering service. Important APIs are `Peering` and `PeerWith`.

Control flow: `Peering` creates a boxo `PeeringService`, starts it on fx start, and stops it on fx stop through `shutdown.CloseWithCtx`. `PeerWith` returns an invoke option that adds configured peers to the service.

State and persistence: runtime peering state only; configured peers come from config and are not written here.

Dependencies/integration: boxo peering, libp2p host/peer, fx, shutdown helper. Wired by `Online` in `groups.go` and feeds trusted peers into AutoRelay elsewhere.

Risks: stop is bounded but `PeeringService.Stop` itself has no context; startup failure from `Start` propagates. No direct tests in this subset.
