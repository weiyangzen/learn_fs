# sources/distributed-fs/ceph-client/fs/cachefiles/error_inject.c

## Purpose
`error_inject.c` provides a small sysctl-controlled error injection mechanism for CacheFiles test builds.

## Important APIs, Types, and Functions
It defines the global `cachefiles_error_injection_state`, the `cachefiles_sysctls` table with `error_injection`, and registration helpers `cachefiles_register_error_injection` and `cachefiles_unregister_error_injection`.

## Control Flow
Module init calls registration when `CONFIG_CACHEFILES_ERROR_INJECTION` is enabled. The sysctl is registered under `cachefiles/error_injection`; reads and writes go through `proc_douintvec`. Module exit unregisters the table.

## State and Persistence Behavior
The sysctl integer is runtime-only state. `internal.h` interprets bit 1 as write `-ENOSPC`, bit 2 as read/write/remove `-EIO`, and disabled builds compile the state to zero through stubs.

## Dependencies and Integration Points
This file integrates with `main.c` init/exit and the inline injection helpers in `internal.h`, which are called throughout daemon, cache, namei, io, interface, and xattr paths.

## Risks and Edge Cases
Registration failure aborts module init. Tests must reset the global after use because it affects broad paths. Unsupported combinations are handled by stubs, so call sites should not require this object when the Kconfig option is off.

## Test Signals
Confirm the sysctl exists only with the option enabled; inject read, write/ENOSPC, write/EIO, and remove/EIO failures; verify cleanup unregisters the sysctl; and run non-error-injection builds to catch missing stubs.
