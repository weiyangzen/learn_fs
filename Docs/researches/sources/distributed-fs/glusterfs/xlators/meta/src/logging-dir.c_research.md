# sources/distributed-fs/glusterfs/xlators/meta/src/logging-dir.c

## Purpose
Implements the meta logging directory.

## Important APIs, Types, and Functions
- `logging_dir_dirents` defines `logfile` symlink, `loglevel` file, and `history` file.
- `logging_dir_ops` exposes fixed dirents.
- `meta_logging_dir_hook()` attaches ops.

## Control Flow
Directory hook sets fixed entries; readdir exposes logging introspection nodes.

## State and Persistence
No owned state; child entries read logging runtime state.

## Dependencies and Integration Points
Depends on hooks for logfile, loglevel, and history files. Integrated by meta root/view directories.

## Risks
Static directory must stay synchronized with hook implementations and build source list.

## Test Signals
Listing meta logging directory should show `logfile`, `loglevel`, and `history`.
