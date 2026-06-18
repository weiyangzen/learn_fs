# sources/distributed-fs/ceph-client/io_uring/fs.h

## Purpose
This header declares io_uring filesystem namespace operation handlers.

## Important APIs, Types, And Functions
- Rename, unlink, mkdir, symlink, and link prep/issue handlers.
- Cleanup hooks for operations that retain delayed filenames.

## Control Flow
No runtime flow is implemented here.

## State And Persistence
No state is defined here; declarations operate on per-request command storage in `fs.c`.

## Dependencies And Integration Points
Used by io_uring opcode definitions and cleanup dispatch.

## Risks And Edge Cases
Missing cleanup declarations would leak delayed filenames on canceled or failed requests. Prototype drift breaks opcode wiring.

## Test Signals
Build and filesystem operation tests validate handler declarations and cleanup hooks.
