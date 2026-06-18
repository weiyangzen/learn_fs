# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/main.c

## Purpose
`main.c` implements the firmware loader public API: synchronous, direct, platform, into-buffer, partial, asynchronous, cache, compressed, and release paths. It coordinates built-in firmware, filesystem lookup, decompression, platform fallback, sysfs fallback, request batching, suspend caching, and shutdown cleanup.

## Important APIs, Types, And Functions
Public APIs include `request_firmware()`, `firmware_request_nowarn()`, `request_firmware_direct()`, `firmware_request_platform()`, `firmware_request_cache()`, `request_firmware_into_buf()`, `request_partial_firmware_into_buf()`, `release_firmware()`, `request_firmware_nowait()`, and `firmware_request_nowait_nowarn()`. Important internals are `struct firmware_cache`, `struct fw_cache_entry`, `alloc_lookup_fw_priv()`, `fw_get_filesystem_firmware()`, decompression helpers, `_request_firmware_prepare()`, `_request_firmware()`, `assign_fw()`, paged-buffer helpers, cache PM callbacks, and module init/exit.

## Control Flow, State, And Persistence
Requests validate firmware name and reject `..` path components, try built-in firmware, batch with an existing `fw_priv` unless no-cache/partial, then read from configured firmware paths in the init mount namespace under kernel credentials. Full reads may try `.zst`, `.xz`, platform fallback, and sysfs fallback after raw lookup failure; partial reads stay direct. Success marks state done and assigns data at the last moment. Batched requesters wait on the same completion. Release either frees direct vmalloc data or drops the shared `fw_priv` ref.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include initramfs, kernel file reading, LSM firmware hooks, vmalloc/vmap, XZ/ZSTD, async work, PM/reboot notifiers, syscore suspend, devres, fallback/sysfs, and builtin firmware linker tables. Risks include request batching with failed loads, no-cache buffer ownership, decompression size validation, path handling, suspend-cache deadlocks, fallback abort semantics, and firmware data lifetime across async callbacks. Test signals include all public APIs, batched concurrent same-name requests, invalid path rejection, search path priority, compressed fallback, platform fallback, sysfs fallback, partial offset reads, suspend/resume cache, shutdown abort, and release of built-in vs allocated firmware.
