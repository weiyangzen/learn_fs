# sources/distributed-fs/openafs/src/vol/physio.c

## Purpose
Provides salvager physical I/O callbacks for OpenAFS directory objects. It reads and writes fixed `AFS_PAGESIZE` directory pages through inode handles and supplies small `DirHandle` identity/manipulation helpers.

## Important APIs, Types, And Functions
Functions include `ReallyRead`, `ReallyWrite`, `SetSalvageDirHandle`, `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, `FidCpy`, and `Die`. `ReallyRead` and `ReallyWrite` open `DirHandle.dirh_handle` with `IH_OPEN` and use `FDH_PREAD`/`FDH_PWRITE`; `SetSalvageDirHandle` initializes a salvage-only `DirHandle` and bumps a static cache-check counter.

## Control Flow
The directory package calls `ReallyRead` or `ReallyWrite` for a page number. Reads return `0` on a full page and `EIO` on physical or logical short-read failure, optionally reporting physical `errno` separately. Writes return `errno`/`EIO` and set `*volumeChanged` after a successful full-page write. Handle helpers release, zero, compare, copy, or panic.

## State And Persistence
Persistent effects are directory page writes to backing vnode files. Runtime state is the `DirHandle`, its referenced `IHandle_t`, the caller-owned `volumeChanged` flag, and the static `SalvageCacheCheck` counter used to force cache distinction across handles.

## Dependencies And Integration Points
This file integrates the salvager with `afs/dir.h`, `ihandle`, `salvage.h`, and volume internals. It is deliberately distinct from fileserver directory I/O because the salvager uses its own `DirHandle` definition.

## Risks And Test Signals
Risks include short reads being interpreted as logical corruption, stale handle references if `FidZap` is missed, and write failures after partial disk writes. Test signals include salvaging directories with good pages, short/truncated directory files, injected read/write errors, and verification that successful writes mark the volume changed.
