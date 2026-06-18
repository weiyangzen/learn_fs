# sources/distributed-fs/glusterfs/xlators/meta/src/logfile-link.c

## Purpose
Implements a meta symlink exposing the current log file path.

## Important APIs, Types, and Functions
- `logfile_link_fill()` writes `this->ctx->log.filename`.
- `logfile_link_ops` exposes `.link_fill`.
- `meta_logfile_link_hook()` attaches ops.

## Control Flow
Readlink invokes fill after hook attachment.

## State and Persistence
Reads logging filename from runtime context.

## Dependencies and Integration Points
Used by the meta logging directory. Depends on meta symlink support.

## Risks
Assumes log filename is non-null or strprintf tolerates it.

## Test Signals
Meta logging logfile symlink should resolve to the active log path.
