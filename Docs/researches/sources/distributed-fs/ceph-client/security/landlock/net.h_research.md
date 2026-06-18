# sources/distributed-fs/ceph-client/security/landlock/net.h

## Purpose

`net.h` declares Landlock network hook registration and network rule insertion, with stubs for non-INET builds.

## Important APIs, Types, and Functions

When `CONFIG_INET` is enabled, it declares `landlock_add_net_hooks()` and `landlock_append_net_rule()`. Otherwise `landlock_add_net_hooks()` is an empty inline and `landlock_append_net_rule()` returns `-EAFNOSUPPORT`.

## Control Flow

Setup calls hook registration unconditionally through this header. Syscall code can attempt to add network rules and receive a clear unsupported-family error when INET support is absent.

## State and Persistence Behavior

No state is stored in the header.

## Dependencies and Integration Points

It depends on common Landlock declarations, rulesets, and setup state. The real implementation is in `net.c`.

## Risks and Test Signals

Stub behavior must match syscall error expectations. Build and selftest both INET and non-INET configurations.
