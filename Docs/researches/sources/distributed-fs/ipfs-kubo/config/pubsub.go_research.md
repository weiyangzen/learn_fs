# Research: sources/distributed-fs/ipfs-kubo/config/pubsub.go

Purpose: Defines pubsub configuration and duplicate-message tracking strategy names.

Important APIs/types/functions: Strategy constants `last-seen`, `first-seen`, and default. `PubsubConfig` fields include router, signing, enabled flag, seen-message TTL, and seen-message strategy.

Control flow, state, and persistence: No functions. Values persist in config and are consumed by pubsub/namesys setup.

Dependencies and integration points: `Ipns.UsePubsub` and daemon flags interact with this config. Optional types allow defaults to be omitted.

Risks and test signals: Strategy string validation is not in this file, so typos must be handled downstream. Disabling signing changes message authenticity semantics. No direct tests in this subset.
