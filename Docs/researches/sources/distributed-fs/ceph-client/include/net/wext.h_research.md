# sources/distributed-fs/ceph-client/include/net/wext.h

## Purpose

`wext.h` declares the Wireless Extensions core entry points and config-dependent stubs for ioctl handling, proc registration, private ioctl dispatch, wireless statistics, and commit handling.

## Important APIs, types, and functions

Under `CONFIG_WEXT_CORE`, it declares `wext_handle_ioctl()`, `compat_wext_handle_ioctl()`, `get_wireless_stats()`, and `call_commit_handler()`. Under `CONFIG_WEXT_PROC`, it declares `wext_proc_init()` and `wext_proc_exit()`. Under `CONFIG_WEXT_PRIV`, it declares private ioctl helpers `ioctl_private_call()`, `compat_private_call()`, and `iw_handler_get_private()`. Disabled stubs return `-EINVAL`, zero, no-op, or NULL macros as appropriate.

## Control flow

Userspace wireless ioctl requests enter `wext_handle_ioctl()` or the compat path, locate driver `iw_handler` callbacks, optionally invoke private handlers, then call commit handlers for deferred configuration. Proc support initializes per-net WEXT proc views.

## State and persistence behavior

The header owns no state. Runtime state is in wireless handler tables, netdevice state, per-net proc entries, and driver-provided statistics.

## Dependencies and integration points

It depends on `net/iw_handler.h` and integrates with legacy wireless drivers, netdevice ioctl dispatch, compat ioctl handling, and procfs.

## Risks and test signals

Risks include assuming WEXT is present when config stubs reject ioctls, compat pointer translation bugs, private ioctl table mismatches, and commit handlers not being called after configuration changes. Tests should cover normal/compat ioctls, disabled-config return values, proc init/exit, private command dispatch, and stats retrieval from legacy drivers.
