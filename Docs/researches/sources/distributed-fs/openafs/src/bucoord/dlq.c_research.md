# sources/distributed-fs/openafs/src/bucoord/dlq.c

## Purpose
Implements a minimal intrusive doubly linked queue used by backup coordinator status management. Queue heads are sentinel `dlqlinkT` records and entries embed the same link fields, allowing status nodes and other structures to be linked without wrapper allocation.

## Important APIs, Types, And Functions
The public queue operations are `dlqInit`, `dlqEmpty`, `dlqLinkf`, `dlqLinkb`, `dlqMoveb`, `dlqUnlinkb`, `dlqUnlinkf`, `dlqUnlink`, `dlqFront`, `dlqCount`, and `dlqTraverseQueue`. `DLQ_ASSERT_HEAD` validates sentinel nodes by checking `dlq_type == DLQ_HEAD`.

## Control Flow
Initialization points head `next` and `prev` at itself and marks it as `DLQ_HEAD`. Link operations splice entries at the front or back. `dlqMoveb` appends all entries from one queue to another and resets the source head to empty. Unlink operations remove first, last, or a specific entry and either self-link or null the removed entry’s pointers. Traversal walks from head to head, optionally calling one function on each entry’s `dlq_structPtr` and another on the link itself.

## State And Persistence
All state is in caller-owned memory; there is no persistence or allocation. The implementation mutates embedded link pointers directly and has no internal locking, so callers must provide synchronization.

## Dependencies And Integration Points
Depends on queue link definitions from `bc.h`/`afs/bubasics.h`. `status.c`, `bc_status.c`, and `commands.c` use it for the global status queue and temporary job listing queues.

## Risks And Test Signals
Invalid queue heads or attempts to unlink a head call `printf` and `exit(1)`, which is harsh for library-style code. Link functions do not verify whether an entry is already linked. There is no thread safety without external locks. Test signals include empty queue behavior, front/back insertion order, moving non-empty and empty queues, unlink first/last/specific nodes, traversal while freeing nodes, and misuse assertions in debug or fault-injection tests.
