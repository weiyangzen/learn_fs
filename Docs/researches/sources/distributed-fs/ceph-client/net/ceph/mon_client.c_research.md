# Research: sources/distributed-fs/ceph-client/net/ceph/mon_client.c

## Purpose

`mon_client.c` implements the kernel Ceph monitor client. It maintains a session with one monitor, hunts for a replacement monitor on fault, authenticates the client, subscribes to cluster maps, handles map updates, provides synchronous/asynchronous monitor requests such as `statfs`, `mon_get_version`, monitor command, and blocklist add, and supplies monitor-specific connection operations to the generic messenger.

The monitor client is the bootstrap and control-plane path for libceph. It discovers and refreshes the monmap, receives OSD maps, manages authentication state, and wakes waiters that need map epochs or auth completion.

## Important APIs, Types, and Functions

Public monitor-client APIs:

- `ceph_monc_init()` and `ceph_monc_stop()` allocate/free monitor client state, auth state, preallocated messages, connection, delayed work, and monmap.
- `ceph_monc_open_session()` starts a monitor session and requests monmap and OSD map subscriptions.
- `ceph_monc_reopen_session()` forces hunting for a new monitor.
- `ceph_monc_want_map()`, `ceph_monc_got_map()`, and `ceph_monc_renew_subs()` manage map subscription intent and progress.
- `ceph_monc_wait_osdmap()` waits for an OSD map epoch.
- `ceph_monc_do_statfs()`, `ceph_monc_get_version()`, `ceph_monc_get_version_async()`, and `ceph_monc_blocklist_add()` issue generic monitor requests.
- `ceph_monc_validate_auth()` requests auth renewal when needed.

Monmap and session helpers:

- `ceph_monmap_decode()` decodes monitor maps, including v6 `mon_info_t` entries with address vectors.
- `build_initial_monmap()` builds a temporary monmap from mount options.
- `pick_new_mon()`, `__open_session()`, `__close_session()`, `reopen_session()`, `finish_hunting()`, and `delayed_work()` implement hunting, reconnect, backoff, keepalive, and subscription renewal.

Generic request helpers:

- `alloc_generic_request()`, `register_generic_request()`, `send_generic_request()`, `finish_generic_request()`, `wait_generic_request()`, and `get_generic_reply()` maintain an rb-tree of outstanding requests keyed by TID.
- Reply handlers include `handle_statfs_reply()`, `handle_get_version_reply()`, and `handle_command_ack()`.

Connection operations:

- `mon_alloc_msg()` preallocates or dynamically allocates incoming messages.
- `mon_dispatch()` routes monitor messages to auth, subscribe ack, statfs, version, command, monmap, OSD map, or extra dispatch handlers.
- `mon_fault()` hunts for a new monitor when the messenger reports a fault.
- msgr2 auth callbacks `mon_get_auth_request()`, `mon_handle_auth_reply_more()`, `mon_handle_auth_done()`, and `mon_handle_auth_bad_method()` bridge v2 frames to the Ceph auth subsystem.

## Control Flow

Initialization builds an initial monmap from configured monitor addresses, creates the auth client with desired key types, allocates reusable auth and subscription messages, initializes the embedded messenger connection with `mon_con_ops`, and sets initial hunting/backoff state.

Opening a session records interest in monmap and OSD map, calls `__open_session()`, and schedules delayed work. `__open_session()` randomly chooses a monitor, sets `hunting`, increases hunting backoff after previous connections, expires subscription renewal, opens the messenger connection, and queues a keepalive. For msgr1, it immediately builds and sends an auth hello message. For msgr2, auth is initiated through messenger v2 auth callbacks.

Authentication replies are handled either as normal `CEPH_MSG_AUTH_REPLY` messages in msgr1 or as msgr2 auth frames through callbacks. `finish_auth()` clears pending auth, records auth errors, sets the messenger entity name from the authenticated global id on first success, sends subscriptions, resends outstanding generic requests, and logs session establishment. `finish_hunting()` marks the monitor as found, reduces backoff, and reschedules delayed work.

Subscriptions are encoded by `__send_subscribe()` from `monc->subs[]`, always including monmap. Continuous subscriptions advance their start epoch after maps arrive; one-time subscriptions clear their want flag. Legacy monitor subscription acks determine `sub_renew_after` for periodic renewal if the peer lacks `CEPH_FEATURE_MON_STATEFUL_SUB`.

Generic requests allocate request and reply messages, register a TID in `generic_request_tree`, fill the request body, send it, and either wait for completion or return for async callback. Replies look up by TID, copy/decode results, remove the request from the tree, revoke request/reply messages from the connection, and complete the waiter or callback. On monitor reconnect, `__resend_generic_request()` revokes in-flight request/reply messages and resends all pending request messages.

Delayed work runs periodically. While hunting it reopens sessions. Otherwise it checks keepalive expiry, reopens on timeout, sends keepalive, validates auth, reduces hunting backoff, and renews subscriptions for old monitors when needed.

## State and Persistence Behavior

The monitor client keeps live state in `struct ceph_mon_client`: current monmap, current monitor index, hunting flags, hunt multiplier, subscription table, subscription renewal timestamps, auth state, reusable messages, generic request rb-tree, last TID, fs cluster id, embedded connection, and delayed work. There is no durable persistence; monmap and auth/session state are memory-only and rebuilt or reacquired after init/reconnect.

Generic requests are reference counted with `kref`. The rb-tree holds a reference while a request is active. Waiters or async users hold their own reference until completion. Request cancellation on interrupted waits removes the request if still active.

## Dependencies and Integration Points

This file is tightly integrated with the generic messenger, msgr1/msgr2 auth callbacks, Ceph auth subsystem, libceph options, OSD client map handling, debugfs state, and monitor protocol structs. It uses Linux delayed work, completions, wait queues, rbtrees, random monitor selection, and memory allocation helpers. `mon_dispatch()` passes `CEPH_MSG_OSD_MAP` directly to `ceph_osdc_handle_map()` and unknown extra messages to `client->extra_mon_dispatch`.

## Risks and Edge Cases

Monitor hunting and request resend must avoid losing control-plane requests during reconnect. `__close_session()` revokes reusable auth/subscription messages and resets auth; `__resend_generic_request()` handles outstanding generic requests after new auth. The monitor address in the initial monmap may have a bogus monitor entity number until a real monmap is decoded. `ceph_monmap_decode()` must handle modern and older monmap structures, skip unknown feature sections, and choose address type according to msgr mode. Subscription renewal has compatibility logic for monitors without stateful subscriptions.

Generic reply matching has a special workaround for old OSDs/monitors that omit `tid` in `MON_GET_VERSION_REPLY`, allocating a fresh message when tid is zero. Monitor command formatting uses a fixed 256-byte request message and `vsprintf()`, so command strings are expected to fit the preallocated buffer. `ceph_monc_blocklist_add()` retries the old `"blacklist"` command name if the modern `"blocklist"` command returns `-EINVAL`.

## Test Signals

Useful tests include initial monmap construction for msgr1 and msgr2 address types, monmap decode for v3/v6 maps and malformed buffers, random monitor repick avoiding the current monitor, msgr1 auth reply loop, msgr2 auth callbacks, auth failure wakeups, subscription encode/ack/renew behavior, OSD map wait timeout and interrupt, statfs/version/command request completion and cancellation, async version callback, monitor fault while hunting versus established, delayed keepalive timeout reopen, request resend after reconnect, blocklist fallback command, and teardown with pending work flushed and no rb-tree leaks.
