# sources/distributed-fs/orangefs/src/io/buffer/ncac-job.h

## Purpose
Declares NCAC job worker functions and the default discard request count.

## Important APIs, Types, And Functions
Defines `DELT_DISCARD_NUM` as 5 and declares workers for read, write, buffered read, buffered write, query, demote, and sync jobs.

## Control Flow
`internal.c` dispatches `NCAC_req_t` objects to these workers based on `optype`.

## State And Persistence
The header has no state; workers operate on `struct NCAC_req`.

## Dependencies And Integration Points
Included by `internal.c`, `ncac-job.c`, and `ncac-buf-job.c`. Its declarations must match worker implementations.

## Risks And Test Signals
Risks are that the header advertises more functionality than is implemented. Build coverage and worker-status tests should catch mismatches.
