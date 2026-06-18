# sources/distributed-fs/ceph-client/include/net/bareudp.h

## Purpose

`bareudp.h` exposes a single helper for identifying Bare UDP tunnel netdevices by rtnl link kind.

## Important APIs, Types, and Functions

`netif_is_bareudp()` checks that `dev->rtnl_link_ops` exists and that its `kind` string equals `"bareudp"`.

## Control Flow

Callers use the helper in packet, offload, or configuration paths that need Bare UDP-specific behavior. The helper performs no locking itself; callers must hold or otherwise rely on valid netdevice lifetime.

## State and Persistence Behavior

No state is defined. It reads netdevice metadata registered by the Bare UDP rtnl link implementation.

## Dependencies and Integration Points

The header depends on `netdevice.h`, basic types, and rtnetlink link operations. It integrates with Bare UDP tunnel devices and generic networking code that branches by netdevice kind.

## Risks and Edge Cases

String-based kind checks are simple but depend on stable rtnl link naming. `rtnl_link_ops` can be `NULL` for ordinary devices; the helper handles that. Lifetime and locking are external to the helper.

## Test Signals

Check true results for Bare UDP devices, false results for ordinary devices and devices with `NULL` link ops, behavior during device unregister paths, and callers that need RTNL or RCU protection.
