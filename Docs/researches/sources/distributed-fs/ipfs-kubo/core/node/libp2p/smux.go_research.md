# sources/distributed-fs/ipfs-kubo/core/node/libp2p/smux.go

Purpose: configures stream multiplexing. Important APIs are `makeSmuxTransportOption` and `SmuxTransport`.

Control flow: rejects the legacy `LIBP2P_MUX_PREFS` environment variable, rejects disabled Yamux config, and returns the Yamux default muxer option. `SmuxTransport` wraps this into the grouped libp2p option provider.

State and persistence: reads environment only; no writes.

Dependencies/integration: Kubo transport config, libp2p muxer option, Yamux. Wired by `LibP2P`.

Risks: unsupported env/config aborts startup; currently Yamux is mandatory. No direct tests in this subset.
