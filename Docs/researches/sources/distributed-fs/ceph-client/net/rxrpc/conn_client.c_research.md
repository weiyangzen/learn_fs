# sources/distributed-fs/ceph-client/net/rxrpc/conn_client.c

## Purpose
`conn_client.c` implements client-side connection caching and channel assignment. It groups compatible client calls into bundles, allocates client connections and connection IDs, multiplexes calls onto four channels per connection, handles service upgrade probing, idles/reaps reusable connections, and cleans up local client connection state.

## Important APIs and functions
- `rxrpc_look_up_bundle()` finds or creates a bundle keyed by peer, key, security level, and upgrade flag.
- `rxrpc_connect_client_calls()` moves new calls into bundle waiting queues and activates channels.
- `rxrpc_expose_client_call()` marks a call ID as visible on the wire and links error delivery.
- `rxrpc_disconnect_client_call()` releases a channel, schedules final ACK retransmission, passes the channel to a waiting call, or idles the connection.
- `rxrpc_discard_expired_client_conns()` reaps idle client connections.
- `rxrpc_clean_up_local_conns()` kills all idle client connections during local endpoint teardown.

## Control flow
`call_object.c` queues new client calls on `local->new_client_calls`. The I/O thread invokes `rxrpc_connect_client_calls()`, which appends calls to their bundle and ensures capacity. Bundles allocate up to four connections, each with four channels, and an available-channel bitmask. `rxrpc_activate_one_channel()` assigns cid, call ID, connection reference, service ID, congestion state, starts the call timer, changes state to client send request, and wakes waiters.

## State and persistence behavior
Bundles are refcounted and have an active count for tree membership. Client connections get IDs from `local->conn_ids`, are listed for proc visibility, and may be cached idle after all channels drain. `DONT_REUSE` prevents reuse after exclusive calls, call counter exhaustion, epoch mismatch, invalid state, or sparse ID distance. Final ACKs are delayed briefly so a subsequent DATA packet can implicitly ACK the previous call.

## Dependencies and integration points
This file integrates with local endpoint IDR state, peer/key refs, connection allocation/destruction, call state/timers, congestion thresholds stored on peers, output final ACK retransmission, and the I/O thread client-call queue.

## Risks
Channel accounting is delicate: `avail_chans`, `act_chans`, bundle slots, and `conn->channels[]` must agree. Delayed final ACK state must be forced before unbundling. Reuse policy must avoid call ID wrap and stale epochs. Idle list refs must be balanced with reap/unbundle puts.

## Test signals
Cover parallel client calls, channel reuse, exclusive calls, service upgrade probing, call counter high-water behavior, idle reaping thresholds, final ACK deferral/subsumption, local teardown, and IDR leak assertions.
