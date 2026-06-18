<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_text.c -->
# sources/distributed-fs/openafs/src/budb/db_text.c

## Purpose
Manages persistent text objects stored inside the budb database, such as dump schedules, volume sets, and tape hosts. It supports chunked reads and lock-protected chunked replacement.

## Important APIs, Types, And Functions
RPC wrappers audit `GetText`, `GetTextVersion`, and `SaveText`. `GetText` reads a byte range from the committed text chain. `SaveText` builds a replacement chain in `newTextAddr/newsize`, commits it when `BUDB_TEXT_COMPLETE` is set, increments the version, and frees old blocks. `freeOldBlockChain` releases obsolete text blocks. `saveTextToFile` is debug support.

## Control Flow
Readers validate text type, offset, and a syntactically valid lock handle, then skip blocks until the requested offset and copy up to `maxLength`. Writers require a valid lock handle. Offset zero discards any previous staged replacement and starts a new block chain; later calls must append exactly at `newsize`. Completion swaps new and old chains atomically within the transaction.

## State And Persistence
Text contents are linked `text_BLOCK` database blocks. `textBlock` header fields persist committed and staged chains, sizes, and versions. Each `SaveText` chunk is capped at one block data payload.

## Dependencies And Integration Points
Uses `db_alloc.c` block allocation, `database.c` I/O, `db_lock.c` handle validation, and RPC/audit infrastructure. Clients use the fields from `budb_client.h`.

## Risks And Test Signals
Handle validation does not check ownership. Interrupted replacement can leave `newTextAddr` staged until the next offset-zero save frees it. Signals are multi-chunk save/get, version increment, complete vs incomplete save, lock failure, empty text, and verifier text-chain checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_text.c -->
