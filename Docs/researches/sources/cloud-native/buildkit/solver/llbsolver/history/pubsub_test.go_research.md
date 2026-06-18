<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/pubsub_test.go

Purpose: verifies pubsub delivery, closure, idempotency, and basic concurrency.

Important APIs and types: `TestPubsubSendReceive`, `TestPubsubClose`, `TestPubsubCloseIdempotent`, and `TestPubsubConcurrent`.

Control flow: tests subscribe one or more channels, send values, assert delivery, close one subscriber and verify it no longer receives, close all subscribers, and use a wait group to send/receive 100 messages across 10 subscribers.

State and dependencies: test-only in-memory pubsub. Depends on `sync`, `testing`, and testify.

Integration points: protects live history event delivery used by `Queue.Listen`.

Risks and test signals: concurrency test assumes all subscriber buffers/readers keep up. It does not test slow subscribers filling buffers or `pubsub.Close` during active sends.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub_test.go -->
