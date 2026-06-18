# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.h

## Purpose
Declares the read-ahead translator's private structures, helper prototypes, and lock wrappers shared by `read-ahead.c` and `page.c`.

## Important APIs, Types, And Functions
`ra_waitq` stores blocked frames. `ra_fill` stores one returned page fragment for user unwind. `ra_local` tracks a user read's range, wait count, error state, pending fault metadata, fd, fill list, and mutex. `ra_page` stores cached page data and invalidation flags. `ra_file` stores per-fd cache state and sequential-read counters. `ra_conf` stores translator options and all open files. Prototypes expose page lookup/create/fault/wakeup/error/purge, frame fill/return, and file destroy helpers. Inline lock helpers wrap pthread mutexes.

## Control Flow
The header itself has no control flow, but it defines the contracts used by read dispatch: pages are protected by `ra_file_lock`, frame-local wait counts by `ra_local_lock`, and the global file list by `ra_conf_lock`.

## State And Persistence
All structures are transient in-memory state. The shape of `ra_page` and `ra_file` determines cache lifetime, invalidation semantics, and statedump visibility.

## Dependencies And Integration Points
Includes Gluster logging, dict, xlator APIs, and read-ahead memory types. It is the internal ABI between the page-cache implementation and the xlator fop layer.

## Risks
The structures expose raw linked-list pointers and manual lock discipline; misuse can corrupt lists or race with callbacks. `ra_file.refcount` is declared but not visibly central in the current implementation, so lifetime is mainly governed by fd contexts and release.

## Test Signals
Compile-time tests should catch signature drift between `page.c` and `read-ahead.c`. Runtime lock, leak, and statedump diagnostics should validate that file/page/local objects are created and destroyed through these structures.
