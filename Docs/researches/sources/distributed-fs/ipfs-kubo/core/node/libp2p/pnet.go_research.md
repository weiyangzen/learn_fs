# sources/distributed-fs/ipfs-kubo/core/node/libp2p/pnet.go

Purpose: configures private libp2p networks from a repo swarm key and warns when isolated. Important APIs are `PNetFingerprint`, `PNet`, `PNetChecker`, and `pnetFingerprint`.

Control flow: `PNet` reads `repo.SwarmKey`, decodes a V1 PSK, adds `libp2p.PrivateNetwork`, and returns a fingerprint. `PNetChecker` starts a ticker after node start and warns every 30 seconds after the first tick if the private-network host has no peers. `pnetFingerprint` runs Salsa20 over zero bytes with the PSK and then SHAKE-128 to produce a 16-byte non-reversible fingerprint.

State and persistence: reads swarm key from repo; no writes. Runtime checker uses a done channel.

Dependencies/integration: repo, libp2p pnet, host, fx, Salsa20, SHA3. Base libp2p provides and invokes this logic.

Risks: invalid swarm keys abort startup; private networks cannot use some transports, enforced elsewhere. No direct tests in this subset.
