# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/main.c

## Purpose
`builtin/main.c` implements lookup for firmware blobs linked into the kernel image through `CONFIG_EXTRA_FIRMWARE`.

## Important APIs, Types, And Functions
`struct builtin_fw` mirrors linker metadata. Linker symbols `__start_builtin_fw` and `__end_builtin_fw` delimit the table. Public/internal functions are `firmware_request_builtin()`, `firmware_request_builtin_buf()`, and `firmware_is_builtin()`, with helper `fw_copy_to_prealloc_buf()`.

## Control Flow, State, And Persistence
`firmware_request_builtin()` scans the linker table by name and, on match, points the caller's `struct firmware` directly at read-only built-in data with its size. `firmware_request_builtin_buf()` first performs that lookup and then optionally copies into a caller-provided preallocated buffer if it fits. `firmware_is_builtin()` identifies release paths that must not free built-in data.

## Dependencies, Integration Points, Risks, And Test Signals
The file is active only when `CONFIG_FW_LOADER` is built in. It integrates with `_request_firmware_prepare()` before filesystem lookup and with `release_firmware()`. Risks include table/name mismatch from generated assembly, buffer-too-small failure after a successful lookup, and callers incorrectly releasing stack-owned firmware from early boot APIs. Test signals include built-in hit/miss, preallocated buffer fit/fail, release of built-in firmware, early boot microcode-style lookup, and no allocator involvement for plain builtin requests.
