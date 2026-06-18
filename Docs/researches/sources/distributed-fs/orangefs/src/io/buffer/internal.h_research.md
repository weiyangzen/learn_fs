# sources/distributed-fs/orangefs/src/io/buffer/internal.h

## Purpose
Defines the NCAC internal data model, global device state, status/error constants, list helpers, and function prototypes shared by the buffer-cache implementation.

## Important APIs, Types, And Functions
Key types are `NCAC_info_t`, `NCAC_dev_t`, `NCAC_req_t`, `struct cache_stack`, `struct inode`, and `struct extent`. It defines request optype/status/error constants, `MAX_INODE_NUM`, `MAX_DELT_REQ_NUM`, `INVAL_IOREQ`, global `NCAC_dev`, `inode_arr`, cache initialization, request-build/progress/done APIs, one-piece read/write prototypes, and inline helpers for aiovec and LRU-list manipulation.

## Control Flow
The header supports the pipeline where public cache descriptors become `NCAC_req_t`, requests acquire extents under inode/cache locks, move through prepare/buffer-complete/complete lists, and eventually release extents and return to the free request pool.

## State And Persistence
Defines all primary in-memory NCAC state: cache memory, extent pool, request pool, inode radix trees and dirty/clean lists, active/inactive/free LRU lists, counters, pending Trove ids, and per-request communication arrays. There is no persistence beyond the process.

## Dependencies And Integration Points
Includes `ncac-interface.h`, `ncac-list.h`, `radix.h`, `aiovec.h`, `flags.h`, and `ncac-locks.h`. It exposes internals broadly to all NCAC compilation units.

## Risks And Test Signals
Risks include tight coupling among modules, globally mutable singleton state, mismatched status names with interface comments, no clear ownership/free path for inodes, and counters spread across inode/cache/extent objects. Tests should validate struct initialization, cache counters, request list transitions, and build coverage for all modules using the header.
