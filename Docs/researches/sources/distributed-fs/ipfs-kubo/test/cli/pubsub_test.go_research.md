# sources/distributed-fs/ipfs-kubo/test/cli/pubsub_test.go

Purpose: tests Kubo pubsub CLI behavior and the persistent per-peer seqno validator state used for replay protection.

Important APIs and helpers: `waitForSubscription` polls `pubsub ls` for a topic, `waitForMessagePropagation` sleeps to allow propagation and datastore persistence, and `publishMessages` sends repeated messages with short spacing. `TestPubsub` uses `Pubsub.Enabled=true` and `Routing.Type=none` to simplify node setup.

Control flow: basic delivery starts a subscriber command in a goroutine, waits for the topic, publishes one message, and attempts to parse JSON data from `pubsub sub --enc=json`. Seqno persistence tests subscribe one node to messages from another, stop daemons, and inspect `/pubsub/seqno/` through `diag datastore`. Update tests compare datastore values across daemon restarts and additional messages. Reset tests run `pubsub reset` globally and with `--peer`, then verify datastore keys are deleted selectively. Restart survival tests confirm seqno count remains stable across daemon restart.

State and persistence: the core state is `/pubsub/seqno/<peerid>` in the repo datastore, storing an eight-byte max seqno per publisher peer. `pubsub reset` mutates this state while the daemon is running; datastore inspection generally requires stopped daemons.

Dependencies and integration points: integrates libp2p pubsub, CLI subscriptions, JSON output, datastore diagnostic commands, peer IDs, daemon stop/start, and persistent BasicSeqnoValidator behavior.

Risks and test signals: the tests acknowledge that message delivery may be timing-sensitive and sometimes log instead of failing when a specific seqno key is absent. Stronger assertions cover datastore counts and reset behavior. Failures indicate pubsub subscriptions not registering, seqno state not persisted, reset not deleting keys, or state lost across restart.
