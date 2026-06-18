# sources/distributed-fs/openafs/src/rx/rx_queue.h

## Purpose
Provides the legacy RX intrusive doubly linked queue macro package.

## Important APIs, Types, And Functions
The header defines `struct rx_queue`, internal macros `_RXQ`, `_RXQA`, `_RXQS`, `_RXQSP`, `_RXQMV`, `_RXQR`, and public macros `queue_Init`, `queue_NodeInit`, `queue_Prepend`, `queue_Append`, insertion, splice, split, replace, move, remove, first/last/next/prev, empty/on-queue/end checks, forward/backward scans, and `queue_Count`.

## Control Flow
All operations are macro-expanded pointer rewrites on intrusive `prev`/`next` links. Scan macros generate `for` loop clauses and require caller-provided current/next variables so removing the current item is safe.

## State And Persistence
Queue state is embedded in caller-owned structs. A queue head points to itself when empty; removed nodes have `next` cleared by `queue_Remove`. There is no persistence beyond memory.

## Dependencies And Integration Points
This header predates the newer `opr_queue` used by many current RX files. It remains included by older RX code and test makefiles. Its API assumes the queue link can be coerced to the containing structure pointer, so layout discipline is critical.

## Risks And Test Signals
Risks include side effects in macro arguments, type confusion from casts, the apparent `queue_IsFirst` use of a nonexistent `first` member, double removal, and misuse with structures where the queue link is not at the expected offset. Compile coverage and focused queue-manipulation unit tests are the main signals.
