<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/pubsub.go

Purpose: small generic pubsub implementation for live build history events.

Important APIs and types: `pubsub[T]`, `channel[T]`, `Subscribe`, `Send`, `Close`, `channel.send`, and `channel.close`.

Control flow: subscribing creates a buffered channel and done channel, adds it to the subscriber map under lock, and returns it. Sending snapshots current subscribers under lock by launching a goroutine per subscriber send; each send either writes to the buffered channel or exits if closed. Close iterates current subscribers and closes each idempotently. Channel close removes itself from the parent map and closes `done` via `sync.Once`.

State and dependencies: in-memory subscriber map under mutex; each subscriber has a buffered `ch` of size 32. Depends only on `sync`.

Integration points: `history.Queue` uses it to broadcast STARTED, COMPLETE, DELETED, and graceful-close events to listeners.

Risks and test signals: send starts goroutines while holding the pubsub lock, which avoids blocking on full subscribers but can create many goroutines under high fanout. Tests cover send/receive, close, idempotent close, and concurrent send/receive.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub.go -->
