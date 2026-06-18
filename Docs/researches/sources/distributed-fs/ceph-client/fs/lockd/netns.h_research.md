# sources/distributed-fs/ceph-client/fs/lockd/netns.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/netns.h` defines lockd's per-network-namespace state container. The source was read as a complete 25-line header.

## Important APIs, Types, and Functions

The central type is `struct lockd_net`, with fields for service user count, next host-GC time, host count, grace time, TCP/UDP ports, delayed grace-period work, `struct lock_manager`, and the NSM handle list. It declares `extern unsigned int lockd_net_id`.

## Control Flow

There is no direct control flow. Other lockd files retrieve this state with `net_generic(net, lockd_net_id)` to coordinate service lifetime, host cache accounting, grace-period control, netlink/procfs settings, and NSM handle storage.

## State and Persistence Behavior

All fields are per-net in-memory state. They persist for the lifetime of the network namespace and are cleaned up by lockd net namespace operations outside this header.

## Dependencies and Integration Points

It integrates with `host.c` for `nrhosts` and `next_gc`, `mon.c` for `nsm_handles`, procfs/netlink control paths for grace/ports, and lock-manager grace handling through `lockd_manager`.

## Risks and Edge Cases

Per-net isolation depends on every call site using the correct namespace. Grace-period delayed work and host/NSM lists must be drained before net namespace teardown.

## Test Signals

Signals include network namespace create/destroy tests with lockd active, independent netlink/procfs port and grace settings per netns, NSM handle cleanup, and host count leak checks.
