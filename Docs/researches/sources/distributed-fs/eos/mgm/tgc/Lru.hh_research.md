# sources/distributed-fs/eos/mgm/tgc/Lru.hh

## Purpose
`Lru.hh` declares the tape-GC file-ID LRU queue abstraction. It maintains the most recently used file at the front and the least recently used file at the back.

## Important APIs, Types, And Functions
The header defines `FidQueue`, exceptions `MaxQueueSizeIsZero` and `QueueIsEmpty`, constructor `Lru(size_type maxQueueSize = 10000000)`, event methods `fileAccessed()` and `fileDeletedFromNamespace()`, query methods `empty()`, `size()`, `maxQueueSizeExceeded()`, pop method `getAndPopFidOfLeastUsedFile()`, JSON method `toJson()`, and private queue update helpers.

## Control Flow
The public contract is event-driven: file open/convert/populate events call `fileAccessed()`, namespace deletion calls `fileDeletedFromNamespace()`, and GC workers pop the least-used fid for eviction attempts.

## State And Persistence
The class stores a max size, overflow latch, list of fids, and map from fid to list iterator. It has no persistence or built-in locks.

## Dependencies And Integration Points
It depends on namespace file IDs, EOS hash helpers, hopscotch map, and standard containers. `TapeGcStats` exposes queue size, and JSON diagnostics are surfaced through FSCTL `tgc`.

## Risks And Edge Cases
Because iterators are stored in a map, every list erase/reinsert must keep the map synchronized. The default max of ten million entries can consume significant memory. Lack of internal locking means misuse from multiple threads can corrupt the list/map pair.

## Test Signals
Compile and runtime tests should cover queue ordering, duplicate access promotion, deletion, overflow behavior, empty pop, JSON max length, and performance/memory at large sizes.
