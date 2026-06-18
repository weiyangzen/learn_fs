# sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p.go

Purpose: defines common libp2p option providers and option prioritization. Important APIs are `Libp2pOpts`, `ConnectionManager`, `PstoreAddSelfKeys`, `UserAgent`, `simpleOpt`, `priorityOption`, `prioritizeOptions`, and `ForceReachability`.

Control flow: provider functions append libp2p options into the fx group `libp2p`. `ConnectionManager` builds a basic connection manager with watermarks, grace, and silence period. `PstoreAddSelfKeys` stores local public/private keys. `prioritizeOptions` filters disabled priority settings, sorts ascending by priority, and chains resulting options. `ForceReachability` maps config strings to libp2p public/private reachability options.

State and persistence: peer keys are stored in the in-memory peerstore. No datastore writes.

Dependencies/integration: Kubo version/config, libp2p options, crypto/peerstore, connmgr, fx. Used widely by `groups.go` transport/security/resource setup.

Risks: lower priority numbers win, so config mistakes can reorder security/transports; unrecognized forced reachability aborts startup. Tests cover priority ordering.
