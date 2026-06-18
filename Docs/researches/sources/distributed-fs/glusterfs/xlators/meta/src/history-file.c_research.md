# sources/distributed-fs/glusterfs/xlators/meta/src/history-file.c

## Purpose
Implements a meta virtual file exposing the GlusterFS log history buffer.

## Important APIs, Types, and Functions
- `history_file_fill()` writes `this->ctx->log.history`.
- `history_file_ops` exposes `.file_fill`.
- `meta_history_file_hook()` attaches ops.

## Control Flow
File read invokes fill, which prints history when present and returns `strfd->size`.

## State and Persistence
Reads in-memory logging history; no state mutation.

## Dependencies and Integration Points
Depends on logging context and strfd. Listed in meta build sources and hook tables elsewhere.

## Risks
Assumes history is a printable string. Large history output can grow strfd.

## Test Signals
Meta history file should reflect recent log history when logging history is enabled.
