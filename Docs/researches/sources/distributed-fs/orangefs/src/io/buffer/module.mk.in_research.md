# sources/distributed-fs/orangefs/src/io/buffer/module.mk.in

## Purpose
Adds NCAC buffer-cache implementation files to OrangeFS server builds.

## Important APIs, Types, And Functions
Appends `ncac-interface.c`, `ncac-trove.c`, `ncac-job.c`, `ncac-buf-job.c`, `ncac-init.c`, `internal.c`, `cache.c`, `ncac-lru.c`, `state.c`, and `radix.c` to `SERVERSRC`.

## Control Flow
No runtime control flow. The fragment controls compilation membership for the server-side cache.

## State And Persistence
No runtime state exists. Persistent effect is build inclusion.

## Dependencies And Integration Points
Integrates NCAC only into `SERVERSRC`, not client `LIBSRC`, matching a server-side cache role.

## Risks And Test Signals
Risks are stale source membership if files are renamed or if client-side cache use is later expected. Server build success is the main signal.
