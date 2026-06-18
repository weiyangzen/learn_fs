# sources/distributed-fs/coda/coda-src/librepair/path.cc

## Purpose
Path-processing helpers for the repair tool: detect leftmost conflicts, detect dangling conflict symlinks, and retrieve FID/version-vector metadata through pioctl.

## APIs, Types, and Functions
Exports `repair_isleftmost()`, `repair_getmnt()`, `repair_inconflict()`, and `repair_getfid()`. Internal helpers are `repair_abspath()` and `repair_getvid()`. Uses `pioctl(_VIOC_GETFID)`, `readlink()`, `stat()`, `chdir()`, `getcwd()`, `ViceFid`, and `ViceVersionVector`.

## Control Flow, State, and Persistence
`repair_isleftmost()` simulates pathname traversal component by component, following symlinks up to `CODA_MAXSYMLINK`, and rejects paths where an earlier component is already a conflict. `repair_inconflict()` identifies a conflict by failed `stat()` plus symlink target beginning with `@`, parsing FID and realm. `repair_getfid()` first asks Venus for metadata and falls back to conflict-symlink parsing with undefined version-vector markers. `repair_getmnt()` walks upward to find the last Coda volume mount, but its helper currently asserts. These functions change the current directory temporarily and restore it.

## Dependencies and Integration
Depends on `repcmds.h`, pioctl support, Coda conflict symlink encoding, and filesystem traversal. Used by `BeginRepair()` and volume-replica setup.

## Risks and Test Signals
Risks include process-wide `chdir()` side effects, fixed path buffers, symlink target concatenation overflow, `repair_getvid()` containing `CODA_ASSERT(0)` which makes `repair_getmnt()` unusable, and fragile parsing of `@fid@realm`. Test signals are correct leftmost-conflict rejection, FID retrieval for normal and conflict objects, cwd restoration, and symlink-loop handling.
