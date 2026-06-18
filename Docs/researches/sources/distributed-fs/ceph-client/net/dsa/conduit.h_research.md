# sources/distributed-fs/ceph-client/net/dsa/conduit.h

## Purpose
This private header declares the conduit management API used by DSA setup, user-port migration, and stubs.

## Important APIs, Types, And Functions
It forward-declares `struct dsa_port`, `struct net_device`, `struct netdev_lag_upper_info`, and `struct netlink_ext_ack`, then declares setup/teardown for normal conduit devices and LAG conduits plus `__dsa_conduit_hwtstamp_validate()`.

## Control Flow
No executable control flow exists here. The declarations are implemented in `conduit.c` and called from `dsa.c`, `user.c`, and the DSA stubs registration path.

## State And Persistence
No state is stored in the header.

## Dependencies And Integration Points
The header is the local interface between conduit handling and the rest of DSA core. The hwtstamp declaration is also exposed through `dsa_stubs` for core netdev code.

## Risks And Edge Cases
Because the header does not include all type definitions, users must include appropriate networking headers before using the declared types in code that needs their fields.

## Test Signals
Compile coverage confirms signature consistency. Runtime coverage comes from conduit setup and hwtstamp validation tests.
