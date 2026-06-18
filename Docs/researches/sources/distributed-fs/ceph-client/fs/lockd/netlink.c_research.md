# sources/distributed-fs/ceph-client/fs/lockd/netlink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/netlink.c` is generated generic-netlink family registration data for lockd's administrative netlink interface. It describes commands, attribute policies, permissions, and the `genl_family`. The source was read as a complete 45-line generated file.

## Important APIs, Types, and Functions

The main objects are `lockd_server_set_nl_policy`, `lockd_nl_ops`, and `struct genl_family lockd_nl_family`. The command handlers are declared in `netlink.h` and implemented elsewhere as `lockd_nl_server_set_doit` and `lockd_nl_server_get_doit`.

## Control Flow

Generic netlink dispatch uses `lockd_nl_ops`: `LOCKD_CMD_SERVER_SET` accepts gracetime, TCP port, and UDP port attributes under `GENL_ADMIN_PERM`; `LOCKD_CMD_SERVER_GET` returns current server configuration. `parallel_ops` allows concurrent generic-netlink operations.

## State and Persistence Behavior

This file owns no mutable runtime configuration. The family is `__ro_after_init`; actual lockd per-net configuration is stored in `struct lockd_net` and manipulated by the command handlers.

## Dependencies and Integration Points

It depends on generated UAPI `linux/lockd_netlink.h`, generic netlink core, and declarations in `netlink.h`. It is built into lockd via the Makefile and registered by lockd init code outside this file.

## Risks and Edge Cases

Generated file drift from `Documentation/netlink/specs/lockd.yaml` is the main risk. Attribute policy bounds must match UAPI enum values. Because operations can run in parallel and are netns-aware, handlers must provide their own synchronization.

## Test Signals

Signals include ynl/netlink selftests for server set/get, permission tests for admin-only set, per-net namespace behavior, build regeneration diff checks, and malformed attribute fuzzing.
