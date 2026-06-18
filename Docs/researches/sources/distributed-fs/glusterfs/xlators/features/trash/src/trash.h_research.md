# sources/distributed-fs/glusterfs/xlators/features/trash/src/trash.h

## Purpose
Declares trash translator data structures, constants, and helper macros used by `trash.c`.

## Important APIs, Types, and Functions
- `GF_BLOCK_READV_SIZE` defaults truncate-copy chunks to 128 KiB.
- `GF_DEFAULT_MAX_FILE_SIZE` defaults to 200 MiB if no configured maximum is present in `init()`.
- `trash_local_t` stores per-fop fd/loc/path/offset/PID/link-count state.
- `trash_elim_path` is a singly-linked list of path prefixes excluded from trashing.
- `trash_private_t` stores configured trash paths, brick path, eliminate list, size limit, enable/internal flags, and trash inode table.
- `TRASH_SET_PID()` and `TRASH_UNSET_PID()` temporarily mark internal trash-created fops with `GF_SERVER_PID_TRASH`.
- `TRASH_STACK_UNWIND()` unwinds and then wipes `trash_local_t`.

## Control Flow
Macros directly affect fop callback flow by switching PID identity around internal mkdir/create operations and ensuring local cleanup on unwind.

## State and Persistence
Defines in-memory private and per-call state. The private struct points at persistent filesystem concepts, including the trash inode and configured trash directory.

## Dependencies and Integration Points
Includes GlusterFS core headers, defaults, `inode.c`, `fnmatch.h`, and `libgen.h`. The inclusion of inode implementation exposes internal dentry helpers used by truncate.

## Risks
Macros assume valid `frame`, `frame->root`, and local state. `PATH_MAX` arrays are embedded in `trash_local_t`, so long paths require careful handling. Including `inode.c` can create brittle build/link coupling.

## Test Signals
Compile tests catch signature drift. Runtime trash unlink/truncate tests validate local cleanup, PID restoration, and path buffer behavior.
