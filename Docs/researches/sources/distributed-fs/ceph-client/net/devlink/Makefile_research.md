# sources/distributed-fs/ceph-client/net/devlink/Makefile

## Purpose

This Makefile defines the object set for the devlink subsystem.

## Important APIs, Types, and Functions

It links `core.o`, `netlink.o`, generated netlink ops, and feature modules for devices, ports, shared buffers, dpipe, resources, params, regions, health, traps, rates, linecards, and shared devlink support.

## Control Flow

Kbuild compiles the listed objects into the devlink directory object. The ordering ensures the core and netlink implementation are present together with all built-in devlink feature providers.

## State and Persistence Behavior

There is no runtime state in this file. Runtime state is in the C objects it selects.

## Dependencies and Integration Points

The object list reflects devlink's modular internal structure. `netlink_gen.o` supplies generated split operation tables consumed by `netlink.c`, while the other files implement handlers referenced by those tables.

## Risks

Any mismatch between generated netlink operations and linked handler objects can cause build failures. Omitting a feature object would silently remove handler implementations from the subsystem.

## Test Signals

Build tests should verify all devlink objects compile together after generated netlink changes and that no handler referenced by `netlink_gen.o` is missing.
