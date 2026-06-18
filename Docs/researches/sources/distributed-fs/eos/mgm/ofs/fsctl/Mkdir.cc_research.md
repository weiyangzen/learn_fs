<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Mkdir.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Mkdir.cc

Source read size: 104 lines, 4232 bytes.

## Purpose

Implements the FUSE fsctl mkdir operation. It creates a directory using MGM namespace APIs and returns a POSIX-style stat tuple for the created entry.

## Important APIs, Types, and Functions

The endpoint is `XrdMgmOfs::Mkdir(...)`. It reads `mode`, calls `_mkdir(path, mode, error, vid, 0)`, then `lstat(path, &buf, error, client, 0)` and formats `struct stat` fields into a `mkdir:` response.

## Control Flow

Write access, stall, redirect, and `Fuse-Mkdir` stats happen first. If `mode` is present, it creates the directory and stats it. Success returns `SFS_DATA` with device, inode, mode, ownership, size/block, and timestamp seconds/nanoseconds. Failure returns `mkdir: retc=<errno>`.

## State and Persistence Behavior

The durable side effect is namespace container creation through `_mkdir`. The stat response is transient.

## Dependencies and Integration Points

Integrates fsctl mkdir requests with the main `XrdMgmOfs::_mkdir` implementation, `lstat`, `MgmStats`, XRootD env parsing, and platform-specific stat timestamp fields.

## Risks and Edge Cases

`atoi` accepts malformed mode prefixes. The fixed 16 KiB stack buffer is much larger than the formatted response but still uses `sprintf`. If mkdir succeeds and stat fails, callers only receive the stat error code, not a rollback.

## Test Signals

Cover valid mode creation, missing/malformed mode, permission failure, redirect to master, mkdir success with lstat failure, and Linux/macOS timestamp formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Mkdir.cc -->
