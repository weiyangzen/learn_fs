# sources/distributed-fs/ipfs-kubo/core/node/libp2p/sec.go

Purpose: configures libp2p security transports. Important API is `Security`.

Control flow: if encryption is disabled, it logs a prominent error and appends `libp2p.NoSecurity`. Otherwise it chains TLS and Noise security options using the shared priority mechanism, with default priorities TLS=100 and Noise=200 and config overrides from `Swarm.Transports.Security`.

State and persistence: no persistence.

Dependencies/integration: Kubo transport config, libp2p security options, Noise, TLS. Wired by `LibP2P` based on `BuildCfg.DisableEncryptedConnections`.

Risks: disabling encryption prevents connections to encrypted nodes and is operator-dangerous; priority changes alter protocol negotiation preference. Priority behavior is covered by `libp2p_test.go`.
