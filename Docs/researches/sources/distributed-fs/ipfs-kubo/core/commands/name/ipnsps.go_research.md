# sources/distributed-fs/ipfs-kubo/core/commands/name/ipnsps.go

## Purpose

`name/ipnsps.go` implements experimental `ipfs name pubsub` management commands. It reports whether the IPNS pubsub resolver is enabled, lists current IPNS pubsub subscriptions, and cancels a subscription.

## Important APIs, Types, and Functions

`IpnsPubsubCmd` registers `state`, `subs`, and `cancel`. Output types are `ipnsPubsubState`, `ipnsPubsubCancel`, and `stringList`. `stringListEncoder` prints one string per line. The command uses `n.PSRouter`, `GetSubscriptions`, and `Cancel`.

## Control Flow

`state` obtains the node and emits whether `PSRouter` is non-nil. `subs` gets the requested IPNS key encoder, requires an enabled pubsub router, iterates subscription keys, splits each record key, filters to the `ipns` namespace, decodes the raw key bytes into a peer ID, formats it in the requested IPNS base, and emits `/ipns/<name>` paths. `cancel` requires an enabled router, trims an optional `/ipns/` prefix, decodes the user-supplied peer ID, calls `PSRouter.Cancel("/ipns/" + string(pid))`, and emits whether a subscription was canceled.

## State and Persistence Behavior

The command operates on live in-memory IPNS pubsub subscriptions. It does not mutate repo config. `cancel` affects active resolver subscriptions; `state` and `subs` are read-only.

## Dependencies and Integration Points

Dependencies include Kubo node access through `cmdenv`, key encoding helpers, libp2p record key parsing, and peer ID decoding. It integrates with the IPNS resolver's pubsub router and with user-facing key-base formatting.

## Risks and Test Signals

Risks include invalid subscription key data, disabled router errors, and the subtle internal path used for cancellation (`/ipns/` plus raw peer ID bytes). Tests should cover enabled/disabled state, non-IPNS subscription filtering, invalid peer IDs being logged/skipped in `subs`, cancel with bare and prefixed names, no-subscription output, key base formatting, and router errors.
