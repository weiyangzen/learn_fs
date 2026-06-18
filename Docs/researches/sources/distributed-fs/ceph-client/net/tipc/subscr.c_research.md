# sources/distributed-fs/ceph-client/net/tipc/subscr.c

## Purpose
Implements topology service subscriptions: creating subscription objects from user/kernel requests, matching name-table publications against subscribed ranges and filters, emitting events, handling subscription timeout, and unsubscribing.

## Important APIs, Types, And Functions
`tipc_sub_subscribe` validates and allocates `struct tipc_subscription`, normalizes endian-sensitive request fields, registers with the name table, and arms an optional timer. `tipc_sub_report_overlap` is called by name-table publication changes to filter by service range, scope, and `TIPC_SUB_PORTS`/`TIPC_SUB_SERVICE`, then queue events. `tipc_sub_unsubscribe` removes the subscription from the name table, cancels the timer, unlinks it from the subscriber connection, and drops its reference. `tipc_sub_get`/`tipc_sub_put` wrap the `kref`.

## Control Flow And State
Subscription creation copies both the raw user-format request into `evt.s` and a host-endian version into `s`. The event template is reused for found/withdrawn/timeout notifications, preserving user-endian output with `tipc_evt_write`. Timeout acquires `sub->lock`, emits a `TIPC_SUBSCR_TIMEOUT` event without a publication, and marks the subscription inactive so later publication events do not send duplicates. Overlap reporting also holds `sub->lock`, serializing publication events with timeout state.

## Dependencies And Integration Points
Depends on TIPC core allocation/logging, `name_table.h` publication subscription hooks, and `tipc_topsrv_queue_evt` for delivery to userspace or kernel subscribers. The name table owns the service-list membership while topology server connections own the subscriber-list membership.

## Risks And Test Signals
Risks include endian compatibility with old subscribers, racing timeout with publication events, reference lifetime across name-table and connection lists, and enforcing mutually exclusive `TIPC_SUB_PORTS`/`TIPC_SUB_SERVICE` semantics. Test signals include subscription create/cancel, service-range overlap edges, node-vs-cluster scope filters, timeout delivery, cancellation before timeout, and max subscription pressure through `topsrv.c`.
