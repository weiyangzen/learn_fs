# sources/distributed-fs/ceph-client/net/dcb/Makefile

## Purpose

The DCB Makefile defines the objects that make up the Data Center Bridging networking support directory.

## Important APIs, Types, and Functions

It builds `dcbnl.o` and `dcbevent.o` into the directory object through `obj-y`.

## Control Flow

At build time, Kbuild compiles and links the DCB rtnetlink implementation and event notifier implementation whenever the enclosing DCB directory is included by configuration.

## State and Persistence Behavior

There is no runtime state. The file influences build artifact composition only.

## Dependencies and Integration Points

`dcbnl.o` provides rtnetlink command handling and exported DCB app helpers. `dcbevent.o` provides the notifier chain used by DCB app change notifications. Both integrate with the broader networking build.

## Risks

Adding new DCB source files without updating this Makefile would omit runtime functionality. Removing one of these objects would break either user-facing netlink configuration or internal DCB event delivery.

## Test Signals

Build with DCB enabled and verify both `dcbnl_init()` and the dcbevent exported symbols are present.
