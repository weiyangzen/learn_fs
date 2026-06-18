# sources/distributed-fs/ipfs-kubo/core/commands/stat_dht.go

Purpose: implements `ipfs stats dht`, returning routing table statistics for WAN/LAN DHT server/client tables and accelerated DHT clients.

Important APIs/types/functions: output structs `dhtPeerInfo`, `dhtStat`, and `dhtBucket`. `statDhtCmd` accepts DHT names (`wanserver`, `lanserver`, `wan`, `lan`) and emits one `dhtStat` per requested table.

Control flow: the command requires online mode and an initialized DHT. It defaults to `wan` and `lan`. For separate active accelerated DHT client (`DHTClient != DHT`), `wan` is reported from `fullrt.FullRT.Stat` and `lan` errors. Otherwise it selects the dual DHT WAN/LAN table, groups peers by common-prefix length against local identity, copies agent version, useful/query timestamps, connectedness, and bucket last-refresh timestamps, then emits stats.

State and persistence behavior: read-only. It inspects routing tables, peerstore metadata, and network connectedness.

Dependencies and integration points: integrates with Kubo `IpfsNode.HasActiveDHTClient`, libp2p-kad-dht dual/fullrt tables, kbucket prefix metrics, peerstore `AgentVersion`, and libp2p network connectedness.

Risks: accelerated client support assumes `*fullrt.FullRT`; other active DHT client types error. The text encoder checks `p.LastUsefulAt != ""` before parsing `LastQueriedAt`, so a peer with only `LastQueriedAt` set is printed as never queried; this looks like a formatting bug. Peerstore `AgentVersion` type assertions are defensive but unexpected errors are only logged.

Test signals: no direct tests here. `core_test.go` covers `HasActiveDHTClient`, which protects this command from typed-nil DHT clients.
