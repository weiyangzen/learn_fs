# sources/distributed-fs/ipfs-kubo/core/node/libp2p/transport.go

Purpose: configures libp2p network transports and bandwidth metrics. Important APIs are `Transports` and `BandwidthCounter`.

Control flow: `Transports` checks whether a private network fingerprint exists, enables TCP with metrics, WebSocket with optional p2p-forge TLS config, shared TCP listener when TCP+WebSocket are enabled and allowed, and QUIC/WebTransport/WebRTC Direct unless disabled or private networking is active. Private networks explicitly error for transports that do not support pnet. `BandwidthCounter` creates and injects a metrics reporter.

State and persistence: runtime options only; no persistent state.

Dependencies/integration: Kubo transport config, p2p-forge cert manager, libp2p tcp/quic/websocket/webtransport/webrtc, metrics, fx. Wired by `LibP2P`.

Risks: pnet incompatibilities abort startup; `LIBP2P_TCP_MUX=false` changes listener sharing; AutoTLS requires WebSocket TLS config. No direct tests here.
