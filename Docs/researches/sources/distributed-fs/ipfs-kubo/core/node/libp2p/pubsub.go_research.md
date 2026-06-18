# sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub.go

Purpose: creates FloodSub/GossipSub services and a datastore-backed seqno validator to reduce replay/cycle risk. Important APIs are `FloodSub`, `GossipSub`, `newSeqnoValidator`, `SeqnoStorePrefix`, and `seqnoStore.Get/Put`.

Control flow: both pubsub constructors use a lifecycle context, host, topic discovery, and default validator. GossipSub additionally enables flood publishing for local publications to improve IPNS delivery. `newSeqnoValidator` wraps `seqnoStore` in libp2p pubsub's basic seqno validator. `seqnoStore.Get` maps datastore-not-found to `(nil, nil)` so first messages from unknown peers are accepted; `Put` stores bytes under `/pubsub/seqno/<peer>`.

State and persistence: seqno metadata persists in the repo datastore, allowing validator state to survive restarts. Pubsub service itself is runtime.

Dependencies/integration: libp2p pubsub/discovery/host/peer, repo datastore, Kubo helpers. Wired when `pubsub` or `ipnsps` build options are enabled.

Risks: persistent seqno state can reject old messages after restart by design; datastore errors bubble to validation. Tests cover `seqnoStore`.
