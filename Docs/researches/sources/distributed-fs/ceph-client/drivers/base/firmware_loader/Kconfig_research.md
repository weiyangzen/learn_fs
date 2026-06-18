# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Kconfig

## Purpose
`Kconfig` defines the firmware loader feature matrix: core firmware loading, debug hashing, Rust abstractions, built-in firmware, sysfs fallback, compressed firmware, suspend caching, and sysfs-based firmware upload.

## Important APIs, Types, And Functions
Important symbols are `FW_LOADER`, `FW_LOADER_DEBUG`, `RUST_FW_LOADER_ABSTRACTIONS`, `FW_LOADER_PAGED_BUF`, `FW_LOADER_SYSFS`, `EXTRA_FIRMWARE`, `EXTRA_FIRMWARE_DIR`, `FW_LOADER_USER_HELPER`, `FW_LOADER_USER_HELPER_FALLBACK`, `FW_LOADER_COMPRESS`, `FW_LOADER_COMPRESS_XZ`, `FW_LOADER_COMPRESS_ZSTD`, `FW_CACHE`, and `FW_UPLOAD`.

## Control Flow, State, And Persistence
The config defaults `FW_LOADER` to enabled and pulls crypto SHA-256 only for debug checksums. Built-in firmware depends on a configured name list and directory. User-helper fallback selects sysfs and paged buffers; forced fallback is a compatibility option also mirrored by sysctl. Compression enables optional XZ and ZSTD paths. Firmware upload selects sysfs and paged buffers because userspace writes data into a loader device before driver-specific flashing.

## Dependencies, Integration Points, Risks, And Test Signals
This file controls which C files build and which paths are compiled inside firmware loader headers. Risks include enabling legacy sysfs fallback without userspace support, GPL/distribution concerns for non-GPL `EXTRA_FIRMWARE`, unsupported compression for built-in firmware, and suspend-cache uevents on platforms where they block sleep. Test signals are build matrix coverage for built-in, modular, fallback, compression, cache, upload, Rust abstraction selection, and sysctl availability.
