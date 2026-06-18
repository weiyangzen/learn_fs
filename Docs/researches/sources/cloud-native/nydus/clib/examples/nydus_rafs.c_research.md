# sources/cloud-native/nydus/clib/examples/nydus_rafs.c

## Purpose
This C example demonstrates the minimum FFI flow for opening and closing a RAFS filesystem through the Nydus C wrapper.

## Important APIs, Types, and Functions
It includes `nydus.h`, uses `NydusFsHandle`, calls `nydus_open_rafs`, checks against `NYDUS_INVALID_FS_HANDLE`, prints success or failure, and calls `nydus_close_rafs`.

## Control Flow
`main` builds hard-coded bootstrap and TOML config strings pointing at repeatable test fixtures. It opens RAFS, exits with `-1` on invalid handle, prints a success line otherwise, closes the RAFS handle, and returns zero.

## State, Persistence, and Dependencies
The example has no persistent state. It depends on fixture paths relative to the example directory and on the C ABI library being linked correctly. The config chooses a localfs backend and dummy cache.

## Integration Points
This file is an integration smoke example for the generated header and Rust exported symbols. It is useful for consumers learning handle lifetime and expected invalid-handle checks.

## Risks and Test Signals
The hard-coded relative paths make the example sensitive to the current working directory. It only tests open/close, not file operations. It does not inspect `errno`, so detailed FFI failures are opaque from the example.
