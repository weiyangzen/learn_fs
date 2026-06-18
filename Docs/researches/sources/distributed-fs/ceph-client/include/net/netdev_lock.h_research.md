<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_lock.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_lock.h

## Purpose
`netdev_lock.h` provides helper wrappers around the per-netdevice instance lock, compatibility with RTNL-serialized operations, lockdep class setup, and ops-lock assertions.

## Important APIs, types, and functions
It defines `netdev_trylock`, assertion helpers, `netdev_need_ops_lock`, lock/unlock wrappers for ops and compatibility modes, lock transition helpers, `netdev_lock_cmp_fn`, `netdev_lockdep_set_classes`, `netdev_lock_dereference`, and `netdev_debug_event`.

## Control flow
Callers use per-device locking when queue management or net shaper ops require it; otherwise compatibility helpers fall back to RTNL. Lockdep classes and compare functions permit multiple device locks under RTNL while detecting unordered nesting elsewhere.

## State and persistence
State is the `net_device::lock`, request flags, queue management/net shaper ops presence, and lockdep metadata. The header itself does not store persistent data.

## Dependencies and integration points
It depends on lockdep, netdevice, rtnetlink, and optional net shaper support. It integrates new per-netdev operation locking with legacy RTNL code.

## Risks and test signals
Risks include missing locks for ops that require serialization, deadlocks when taking multiple device locks outside RTNL, stale assumptions about invisible/unregistered devices, and lockdep class setup omissions. Tests should cover queue/shaper ops with and without request_ops_lock, nested device removal, RCU protected dereferences, and CONFIG_DEBUG_NET_SMALL_RTNL builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_lock.h` completely for this pass (138 lines, 3370 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_lock.h -->
