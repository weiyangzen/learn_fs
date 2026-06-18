# sources/distributed-fs/coda/coda-src/venus/spool.cc

## Purpose
This file ensures Venus checkpoint/spool directories exist with expected ownership and permissions, including per-user spool subdirectories.

## Important APIs, Types, and Functions
`ValidateDir()` checks whether a path exists and is a directory, removes non-directory entries, creates the directory if needed, and fixes owner/group/mode. `MakeUserSpoolDir()` validates the global `SpoolDir`, constructs `SpoolDir/<uid>` into the caller-provided buffer, and validates the per-user directory.

## Control Flow
Callers pass a writable path buffer and owner uid. The function first guarantees the parent spool directory is owned by Venus (`V_UID`) and group `V_GID` with mode `0755`, then creates/fixes the user's private directory with owner uid and mode `0700`.

## State and Persistence Behavior
This file mutates the host filesystem, not RVM. It creates directories, unlinks non-directory collisions, changes ownership, and changes modes. These directories are used for CML checkpoints/snapshots configured by `SpoolDir`.

## Dependencies and Integration Points
It depends on POSIX `stat`, `mkdir`, `unlink`, `chown`, `chmod`, Venus uid/gid constants, and the `SpoolDir` configuration exported from `venus.private.h`.

## Risks and Test Signals
Risks include unsafe `sprintf()` into the caller buffer, unlinking a non-directory path without additional safety checks, ignored errors from `chown/chmod/stat`, and behavior under privilege restrictions. Tests should cover missing parent, file collision, wrong owner/mode repair, long spool paths, and unprivileged failure modes.
