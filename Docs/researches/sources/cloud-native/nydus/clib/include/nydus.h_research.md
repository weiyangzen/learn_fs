# sources/cloud-native/nydus/clib/include/nydus.h

## Purpose
This generated C header exposes the public C ABI for the `nydus-clib` library. It defines opaque integer handles for Nydus filesystem and file objects and declares open/close entry points.

## Important APIs, Types, and Functions
The header defines `NYDUS_FILE_HANDLE_MAGIC`, `NYDUS_INVALID_FILE_HANDLE`, `NYDUS_FS_HANDLE_MAGIC`, and `NYDUS_INVALID_FS_HANDLE`. It typedefs `NydusFileHandle` and `NydusFsHandle` as `uintptr_t`. Public functions are `nydus_fopen`, `nydus_fclose`, `nydus_open_rafs`, `nydus_open_rafs_default`, and `nydus_close_rafs`.

## Control Flow
C callers open a RAFS filesystem with explicit config or default localfs config, optionally open file handles from the filesystem, close file handles, then close the filesystem. The comments state that file handles must be closed before closing the filesystem.

## State, Persistence, and Dependencies
The handles are raw pointer values managed by Rust allocation and deallocation. The header has no persistence but encodes the ABI contract. It includes standard C integer and boolean headers.

## Integration Points
It is generated from Rust source by cbindgen and must remain synchronized with `clib/src/file.rs` and `clib/src/fs.rs`. Consumers use it for linking C or C++ code against static/dynamic Rust artifacts.

## Risks and Test Signals
The ABI exposes raw integer handles, so invalid, stale, double-closed, or cross-thread handles can trigger Rust assertions or memory unsafety. The header comments warn about leak and panic risks but cannot enforce them. Tests in Rust exercise opening/closing RAFS; file operations remain skeletal.
