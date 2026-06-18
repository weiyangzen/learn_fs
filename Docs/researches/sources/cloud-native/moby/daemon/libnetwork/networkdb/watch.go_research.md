## sources/cloud-native/moby/daemon/libnetwork/networkdb/watch.go

Purpose: watch API for NetworkDB table changes. It exposes filtered event streams to consumers and synthesizes initial create events for existing remote entries so watchers start with a coherent view.

Important APIs/types/functions: `WatchEvent` carries table, network ID, key, current value, and previous value; methods `IsCreate`, `IsUpdate`, `IsDelete`, and `String` classify events; `NodeTable` and `NodeAddr` represent node join/leave table notifications; `(*NetworkDB).Watch` creates an `events.Channel` plus cancellation function.

Control flow: `Watch` optionally builds an `events.Matcher` for table/network filters, wraps an events queue in a filter, locks NetworkDB, walks either `byNetwork` or `byTable` radix indexes to emit synthetic create events for non-deleting entries not owned by this node, registers the sink with `nDB.broadcaster`, and returns a cleanup closure that removes and closes the sink/channel.

State and persistence behavior: no durable state is introduced, but watch registration adds an event sink to the NetworkDB broadcaster. Initial state is read under `RLock` to avoid racing table mutation while synthetic events are generated. Local entries are excluded from initial watch state.

Dependencies and integration points: uses `github.com/docker/go-events`, `net`, string path parsing, and NetworkDB indexes keyed by table/network. It is consumed by libnetwork code that needs to react to remote distributed table changes.

Risks: synthetic event generation depends on index path formats and `strings.SplitN` tuple lengths. The channel is unbuffered at creation but wrapped in a queue; slow consumers can still create backpressure or queue growth depending on go-events behavior. Correct cancellation is required to avoid leaked broadcaster sinks.

Test signals: `TestNetworkDBWatch`, `TestWatch_out_of_order`, and `TestWatch_filters` validate create/update/delete classification, synthetic initial state, filter combinations, local-entry exclusion, and out-of-order event behavior.
