# sources/distributed-fs/coda/coda-src/vice/coppend.h

## Purpose
`coppend.h` declares the pending-COP table interface shared by vice mutation code. It defines the entry and manager classes used to track which fids still need COP2 version-vector completion for a store ID.

## Important APIs, types, and functions
- `MAXFIDS` is the fixed maximum number of fids associated with one operation.
- `CPENTMAGIC` is the integrity marker checked by `cpent`.
- `class cpent` stores a store ID, fid array, entry timestamp, dequeue flag, and print helpers. Its internals are exposed to selected friends: table insertion, `InternalCOP2`, and `cpman`.
- `class cpman` owns the manager lock, LWP process ID, and object hash table. It exposes `add`, `remove`, `findanddeq`, and print helpers; construction/destruction and raw `find` are intentionally private/friend-mediated.
- `CopPendingMan`, `InitCopPendingTable`, `AddToCopPendingTable`, and `AddPairToCopPendingTable` are the global interface.

## Control flow
The header establishes a singleton style: server startup calls `InitCopPendingTable`, mutation paths add entries through the extern functions, and COP2 completion uses friend access from `InternalCOP2` to consume entries and inspect fids.

## State and persistence behavior
All state described by this header is in-memory and protected by a Coda `Lock`. The pending table records live coordination state, not durable state.

## Dependencies and integration points
The header includes C linkage dependencies for `stdio`, `lwp/lock.h`, `vice.h`, and `rpc2`, then includes `ohash.h` for the C++ hash table. It is consumed by `srv.cc`, `codaproc.cc`, `codaproc2.cc`, and `coppend.cc`.

## Risks
The fixed `MAXFIDS` bound is part of the ABI between operations and COP2. Adding operations that mutate more objects requires revisiting this structure. Friend-heavy encapsulation makes invariants implicit, and raw pointers are returned for entries managed by `cpman`.

## Test signals
Build coverage should catch include-order issues. Runtime COP tests should confirm all mutating operations add the right fids and COP2 consumes them exactly once.
