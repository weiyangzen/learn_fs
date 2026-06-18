# sources/distributed-fs/coda/coda-src/egasr/removeinc.c

## Purpose
Helper for removing an inconsistent file by first repairing it with an empty temporary file and then unlinking it.

## APIs, Types, and Functions
`IsObjInc()` detects conflict state through `stat()`, dangling symlink parsing of `@vol.vnode.unique@realm`, and `_VIOC_GETFID` output. `main()` validates inconsistency, rejects non-local directories with `ISDIR()` and `FID_IsLocalDir()`, creates a temporary file with `mkstemp()`, calls `_VIOC_REPAIR`, unlinks the temp file, then unlinks the target.

## Control Flow, State, and Persistence
If the target is already a dangling repair symlink, the FID is parsed from the symlink. Otherwise Venus supplies FID/version-vector information; an undefined StoreId or directory/file mismatch marks the object inconsistent. The persistent effects are Venus repair state and final filesystem unlink.

## Dependencies and Integration
Depends on `pioctl()`, `codadir.h` FID macros/helpers, Coda ioctl numbers, and local filesystem temp files. It is called by `xfrepair` when the user chooses removal.

## Risks and Test Signals
Risks include `/tmp` temporary-file exposure window, fixed ioctl buffers, broad success exit when the object is not inconsistent, directory conflict limitations, and symlink parsing assumptions. Test signals are detection of repair symlinks, rejection of directories requiring manual removal, successful empty repair, and target unlink.
