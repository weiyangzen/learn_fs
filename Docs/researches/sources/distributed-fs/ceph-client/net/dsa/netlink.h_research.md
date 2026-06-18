# sources/distributed-fs/ceph-client/net/dsa/netlink.h

## Purpose
This private header exposes the DSA rtnetlink link-ops object to module initialization.

## Important APIs, Types, And Functions
It declares `extern struct rtnl_link_ops dsa_link_ops __read_mostly`.

## Control Flow
No executable logic exists. `dsa.c` registers and unregisters `dsa_link_ops`; `netlink.c` defines it.

## State And Persistence
The declared object is read-mostly global rtnetlink operation metadata.

## Dependencies And Integration Points
It connects DSA module init/exit with the rtnetlink implementation without exposing internals elsewhere.

## Risks And Edge Cases
Signature or storage changes must stay synchronized with `netlink.c`.

## Test Signals
Compile and module init tests cover the declaration.
