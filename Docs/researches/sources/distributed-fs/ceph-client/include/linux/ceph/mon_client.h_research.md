# sources/distributed-fs/ceph-client/include/linux/ceph/mon_client.h

## Purpose

`mon_client.h` declares the monitor client that manages monitor maps, authentication, subscriptions, generic monitor requests, statfs/version queries, and monitor session hunting.

## Important APIs, Types, and Functions

Key types are `ceph_monmap`, `ceph_mon_request`, `ceph_mon_generic_request`, and `ceph_mon_client`. APIs include `ceph_monc_init()`, `ceph_monc_stop()`, `ceph_monc_reopen_session()`, map subscription helpers `ceph_monc_want_map()`, `ceph_monc_got_map()`, `ceph_monc_renew_subs()`, `ceph_monc_wait_osdmap()`, statfs/version/blocklist operations, `ceph_monc_open_session()`, and `ceph_monc_validate_auth()`.

## Control Flow

The monitor client opens a messenger connection to a selected monitor, hunts among monitor addresses on failures, authenticates, sends subscriptions for monmap/osdmap/fsmap/mdsmap, renews subscriptions, and tracks generic requests in an RB tree keyed by tid until replies complete.

## State and Persistence Behavior

Runtime state includes the current `ceph_monmap`, auth client and auth messages, pending auth flag, hunt state/backoff multiplier, current monitor index, subscription epochs, generic request tree, last tid, and per-client debugfs file. Persistent cluster identity comes from monitor maps and FSID validation.

## Dependencies and Integration Points

It includes `messenger.h` and works inside `ceph_client`. It drives OSD map freshness for `osd_client.h`, auth handshakes for messenger connections, and monitor wire structs from `ceph_fs.h`.

## Risks and Edge Cases

Hunt/backoff and subscription renewal can stall map progress if delayed work is mishandled. Generic request lifetime spans messages, completions, callbacks, and RB tree removal. Auth validation failures must wake waiters. Monitor maps with changing membership require safe reconnection.

## Test Signals

Exercise monitor failover, auth success/failure, subscription renewal, waiting for target OSD epochs, statfs/version synchronous and async requests, blocklist command construction, and request timeout/unwind behavior.
