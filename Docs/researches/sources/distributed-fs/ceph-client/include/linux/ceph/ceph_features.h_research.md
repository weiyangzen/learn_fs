# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_features.h

## Purpose

`ceph_features.h` defines the 64-bit Ceph feature negotiation bitspace used by clients and servers. It handles feature bit reuse through incarnation marker bits so an old meaning and a new meaning for the same numeric bit are not mistaken for each other during connection negotiation.

## Important APIs, Types, and Functions

Key macros are `CEPH_FEATURE_INCARNATION_1/2/3`, `DEFINE_CEPH_FEATURE`, `DEFINE_CEPH_FEATURE_DEPRECATED`, `DEFINE_CEPH_FEATURE_RETIRED`, and `CEPH_HAVE_FEATURE`. The file enumerates supported named feature constants such as `CEPH_FEATURE_MSG_AUTH`, `CEPH_FEATURE_SERVER_LUMINOUS`, `CEPH_FEATURE_MSG_ADDR2`, and `CEPH_FEATURE_CEPHX_V2`, then aggregates the client-advertised mask in `CEPH_FEATURES_SUPPORTED_DEFAULT`; `CEPH_FEATURES_REQUIRED_DEFAULT` is zero.

## Control Flow

There is no runtime control flow. Compile-time macro expansion creates feature constants and masks, while callers use `CEPH_HAVE_FEATURE(x, name)` to require both the bit and the correct incarnation marker.

## State and Persistence Behavior

The file owns no mutable state. Its constants become persistent wire-compatibility contracts because feature masks are exchanged during monitor, OSD, and messenger handshakes.

## Dependencies and Integration Points

It depends on kernel integer types and `__maybe_unused` availability through includers. Integration is with `msgr.h`, messenger negotiation, monitor session setup, and any protocol path that gates behavior on peer feature masks.

## Risks and Edge Cases

Feature bit reuse is the central risk. Testing only `(mask & bit)` is unsafe for reused bits; callers must use the mask form. The spelling `LUNINOUS` in a retired macro argument is inert but illustrates that retired macro arguments are not type checked. Adding a feature to the wrong supported/default mask can create false compatibility.

## Test Signals

Useful signals are build coverage of feature consumers, connection tests against clusters with old and new release feature masks, assertions that `CEPH_HAVE_FEATURE` rejects reused bits lacking incarnation markers, and protocol downgrade tests for optional features.
