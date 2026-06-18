# sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub_test.go

Purpose: validates the datastore-backed pubsub sequence-number store. Important test is `TestSeqnoStore`.

Control flow: tests create a synchronized in-memory datastore and a `seqnoStore`, decode two peers, then assert unknown peers return nil without error, seqnos store/retrieve as big-endian uint64, peer entries are isolated, updates replace older values, keys use `/pubsub/seqno/<peer>`, and data persists across store instances sharing the datastore.

State and persistence: uses in-memory datastore to model repo persistence.

Dependencies/integration: go-datastore, sync datastore wrapper, libp2p peer IDs, testify. The test directly protects the validator contract needed by `pubsub.NewBasicSeqnoValidator`.

Risks signaled: returning datastore-not-found as an error would reject first messages; peer key collision or non-persistence would weaken replay prevention.
