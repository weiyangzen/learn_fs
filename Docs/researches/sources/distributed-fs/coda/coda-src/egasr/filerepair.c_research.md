# sources/distributed-fs/coda/coda-src/egasr/filerepair.c

## Purpose
Simple file-conflict repair helper that replaces an inconsistent Coda file with the contents of another regular file.

## APIs, Types, and Functions
Defines `getfid()` using `pioctl(..., _VIOC_GETFID)` to read `ViceFid`, `ViceVersionVector`, and realm. `main()` validates arguments and the repair file with `stat()`, builds an `@Volume.Vnode.Unique@realm` repair path when possible, and calls `pioctl(..., _VIOC_REPAIR)`.

## Control Flow, State, and Persistence
The program ensures the second argument exists and is regular, resolves it to a Coda FID if possible, otherwise uses its pathname, submits that as repair input for the inconsistent first argument, tolerates `ETOOMANYREFS`, then stats the repaired object before exiting. Persistent state changes are performed by Venus/server repair logic.

## Dependencies and Integration
Depends on `pioctl()`, Coda ioctl numbers, Vice FID/version-vector structures, and Venus repair semantics. It is invoked by `xaskuser`.

## Risks and Test Signals
Risks include weak regular-file check using `statbuf.st_mode & S_IFREG`, no detailed conflict validation, fixed 2 KB ioctl buffers, and success ambiguity when `ETOOMANYREFS` is returned. Test signals are successful `_VIOC_REPAIR`, repaired object stat success, and `xfrepair` workflows using selected replicas or named files.
