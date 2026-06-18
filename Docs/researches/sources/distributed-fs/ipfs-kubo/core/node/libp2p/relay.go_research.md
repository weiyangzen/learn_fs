# sources/distributed-fs/ipfs-kubo/core/node/libp2p/relay.go

Purpose: configures circuit relay transport, relay service, AutoRelay client, and hole punching. Important APIs are `RelayTransport`, `RelayService`, `MaybeAutoRelay`, and `HolePunching`.

Control flow: relay transport enables or disables circuit relay. Relay service applies user overrides onto libp2p default relay resources. `MaybeAutoRelay` either configures static relays or creates a peer source fed by trusted peering peers, DHT closest peers, and currently connected swarm peers through `autoRelayFeeder`. `HolePunching` enables hole punching only when the relay client is active; explicit incompatible enablement is fatal.

State and persistence: runtime channels and goroutines only. Relay reservations are libp2p runtime state.

Dependencies/integration: Kubo relay/peering config, libp2p autorelay and circuitv2 relay, fx. `groups.go` validates relay dependency flags before wiring these options.

Risks: peer source goroutine must respect shutdown; static relay strings must parse; disabling relay client disables hole punching. Tests are indirect through networking integration.
