# sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.h

## Purpose
Declares the opaque fileinfo cache API used by pNFS data-server code.

## Important APIs, Types, And Functions
Declares `liz_fileinfo_cache_t`, `liz_fileinfo_entry_t`, create/reset/destroy, acquire/release/erase, pop expired, entry free, fileinfo extract, and fileinfo attach functions.

## Control Flow
Callers acquire an entry for an inode, open and attach a `liz_fileinfo_t` if extraction returns `NULL`, release the entry when a DS handle is done, and periodically pop expired entries to release associated LizardFS file handles and free entries.

## State And Persistence Behavior
The header documents cache ownership boundaries: entries are cache-owned until popped/erased, while attached fileinfo must be released by the caller after expiry.

## Dependencies And Integration Points
Includes the LizardFS C API for `liz_fileinfo_t` and `liz_inode_t`; C++ callers use the `extern "C"` block.

## Risks And Edge Cases
The comments say acquire may return NULL if full, but implementation does not enforce a hard cap. API users must pair acquire with release or erase and must not free active entries.

## Test Signals
The unit test exercises this interface directly.
