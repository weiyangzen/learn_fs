<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.h -->
# sources/distributed-fs/orangefs/src/apps/ucache/ucached.h

## Purpose
Defines constants, includes, and shared settings for the ucache daemon and command helper.

## Important APIs, Types, And Functions
The header exports no functions. It defines daemon file paths (`UCACHED_LOG_FILE`, `UCACHED_INFO_FILE`, `UCACHED_STARTED`), gossip masks, FIFO names and buffer sizes, shared-memory key inputs (`KEY_FILE`, `SHM_ID1`, `SHM_ID2`), permissions (`FILE_MODE`, `SVSHM_MODE`), and control defaults (`CREATE_AT_START`, `DEST_AT_EXIT`, `FIFO_TIMEOUT`, `BLOCK_LOCK_TIMEOUT`).

## Control Flow
Compile-time `#ifndef` guards allow build or compiler flags to override most defaults. Both `ucached.c` and `ucached_cmd.c` consume the same constants so daemon and client agree on IPC paths.

## State And Persistence
The header defines the persistent namespace for the daemon: `/tmp` files/FIFOs and SYSV keys derived from `/etc/fstab`. It does not own runtime state itself.

## Dependencies And Integration Points
Pulls in POSIX, SYSV IPC, poll, and `ucache.h` declarations needed by daemon code. It bridges application commands to user-cache shared-memory structures.

## Risks And Test Signals
Risks are hard-coded globally shared IPC paths, permissive `0666` FIFO/shared-memory permissions, and build-time overrides that can desynchronize daemon and command binaries. Test signals include compiling both binaries with default and overridden paths, permission checks, and successful command exchange against the same FIFO names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.h -->
