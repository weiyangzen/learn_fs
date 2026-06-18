# sources/distributed-fs/openafs/src/viced/physio.c

## Purpose

`physio.c` supplies the low-level physical page I/O hooks used by the directory buffer package in the fileserver. It translates a `DirHandle` into an `IHandle_t` file descriptor, reads or writes fixed 2048-byte directory pages, and maintains helper routines for copying, clearing, releasing, and comparing directory handles.

## Important APIs, Types, And Functions

- `ReallyRead(DirHandle *file, int block, char *data, int *physerr)` opens `file->dirh_handle`, performs `FDH_PREAD` of `PAGESIZE` bytes at `block * PAGESIZE`, returns `0` on success or `EIO` on short/failed read, and distinguishes logical short reads from physical errno via optional `physerr`.
- `ReallyWrite(DirHandle *file, int block, char *data)` opens the handle and writes one page with `FDH_PWRITE`; it logs errors and stores failure evidence in globals `lpErrno` and `lpCount`.
- `SetDirHandle(DirHandle *dir, Vnode *vnode)` copies vnode identity, volume cache generation, and ihandle into a buffer-package-compatible `DirHandle`.
- `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, and `FidCpy` manage `DirHandle` lifetime and identity comparison.
- `PAGESIZE` is forced to `2048`, matching the directory page size expected by this layer rather than the platform VM page size.

## Control Flow

The read/write path is intentionally narrow: open the inode handle, perform a positional full-page read or write, close or really-close the fd handle, and log on failure with device, inode, volume id, and errno context. `ReallyRead` has clearer error propagation than `ReallyWrite`: it returns `EIO` for both physical and short-read errors and can return physical errno through `physerr`. `ReallyWrite` always returns `0`, including failure cases, so callers must rely on historical global side effects if they need details.

Handle helpers are simple state transitions. `SetDirHandle` increments/copies the vnode ihandle reference with `IH_COPY`; `FidZap` releases the stored handle and clears the structure; `FidCpy` copies the structure and then takes another ihandle reference.

## State And Persistence Behavior

This file performs persistent directory object I/O through OpenAFS inode-handle abstractions. It does not own higher-level transaction state. The durable data unit is a 2048-byte directory page at a deterministic file offset. `DirHandle` includes copied device, inode, volume id, vnode id, uniquifier, and `cacheCheck` fields so cached directory pages can be invalidated when a vnode/volume identity changes even if the underlying handle object is reused.

## Dependencies And Integration Points

It depends on `afs/ihandle.h`, vnode/volume definitions, `viced.h` for `DirHandle`, and `viced_prototypes.h`. It is an integration layer between the directory buffer package and the fileserver's inode-handle package. Logging goes through `ViceLog`, and inode formatting uses `PrintInode`/`afs_printable_VolumeId_lu`.

## Risks And Edge Cases

- `ReallyWrite` returns success even when open or write fails; this is a legacy API trap and makes callers easy to misread.
- Short reads are converted to logical `EIO` with `physerr = 0`, so diagnostics must preserve both `code` and `physerr`.
- `FidZap` assumes `dirh_handle` is valid enough for `IH_RELEASE`; callers should not double-zap a copied/zeroed handle.
- The fixed 2048-byte page size must stay consistent with the directory package.

## Test Signals

Useful tests are fault-injection around `IH_OPEN`, short `FDH_PREAD`, short/failed `FDH_PWRITE`, and reference-count/lifetime checks for `SetDirHandle`, `FidCpy`, and `FidZap`. Integration tests should verify directory cache invalidation when vnode uniquifier or volume `cacheCheck` changes.
