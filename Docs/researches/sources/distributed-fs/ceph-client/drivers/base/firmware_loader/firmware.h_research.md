# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/firmware.h

## Purpose
`firmware.h` defines the shared internal firmware-loader state machine, request option flags, private firmware buffer object, and cross-file interfaces.

## Important APIs, Types, And Functions
Important enums are `fw_opt` and `fw_status`. Core structures are `struct fw_state` and `struct fw_priv`, with optional paged-buffer and user-helper fields. It declares `fw_lock`, `fw_cache`, `fw_load_abort_all`, `alloc_lookup_fw_priv()`, `assign_fw()`, `free_fw_priv()`, `fw_state_init()`, built-in firmware helpers, and paged-buffer helpers. Inline state functions cover wait, set, start, done, aborted, and status checks.

## Control Flow, State, And Persistence
`fw_priv` is the refcounted shared object for one firmware load, including data pointer, size, allocated size, offset, options, firmware name, cache owner, completion, and optional pages. State transitions move from unknown to loading to done or aborted; done/abort completes all waiters and removes pending fallback entries. `__fw_state_wait_common()` maps abort to `-ENOENT`, timeout to `-ETIMEDOUT`, and signal interruption through the wait helper.

## Dependencies, Integration Points, Risks, And Test Signals
The header ties together main lookup, builtin lookup, fallback, sysfs, upload, cache, and compression paths. Risks include global lock coupling, completion status races, list deletion only when fallback fields exist, and option flag interactions such as partial reads requiring preallocated buffers. Test signals include batched request completion, abort wakeups, timeout behavior, paged-buffer builds off/on, user-helper builds off/on, and builtin helper stubs for modular cases.
