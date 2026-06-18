# sources/distributed-fs/ceph-client/fs/cachefiles/internal.h

## Purpose
`internal.h` is the private contract for the CacheFiles implementation. It defines core structures, content/state enums, flags, inline helpers, conditional stubs, function prototypes, tracing hooks, credential override helpers, error macros, and debug/assertion macros.

## Important APIs, Types, and Functions
Key types are `enum cachefiles_content`, `struct cachefiles_volume`, `enum cachefiles_object_state`, `struct cachefiles_ondemand_info`, `struct cachefiles_object`, `struct cachefiles_cache`, `struct cachefiles_req`, and `enum cachefiles_has_space_for`. Important helpers include `cachefiles_in_ondemand_mode`, `cachefiles_cres_file`, `cachefiles_cres_object`, `cachefiles_state_changed`, error-injection inline helpers, on-demand state accessors, `cachefiles_begin_secure`, `cachefiles_end_secure`, `cachefiles_io_error`, and `cachefiles_io_error_obj`.

## Control Flow
The header itself is declarative, but its inlines participate in common flows: netfs cache resources recover the backing file/object through `cres`, daemon poll wakeups go through `cachefiles_state_changed`, VFS operations run under override creds through begin/end secure helpers, and fatal I/O errors mark a cache dead and flush on-demand requests. `CONFIG_CACHEFILES_ONDEMAND` and `CONFIG_CACHEFILES_ERROR_INJECTION` switch between real declarations and no-op/error stubs.

## State and Persistence Behavior
It defines all major runtime state: cache mount/dentries/credentials, volume fanout directories, object file/name/content/tmpfile state, request xarrays, culling thresholds and counters, released counters, write-block accounting, security ID, daemon flags, and on-demand object IDs. `enum cachefiles_content` values are persisted in object xattrs and must remain stable.

## Dependencies and Integration Points
The header integrates with FS-Cache, netfs cache resources, Linux credentials and security, xarray, tracepoints, and the `linux/cachefiles.h` userspace ABI. Every implementation file in `fs/cachefiles` depends on it.

## Risks and Edge Cases
Changing persisted enum values, struct fields used across files, flag bit positions, request semantics, or conditional stubs can break on-disk compatibility, non-optional builds, or daemon ABI behavior. Error macros have side effects beyond logging: they mark the cache dead and may flush requests.

## Test Signals
Build all Kconfig matrices, check on-disk xattr content values, run sparse/lockdep for helper use, test fatal I/O transitions to `CACHEFILES_DEAD`, and verify on-demand-off builds link with stubbed helpers.
