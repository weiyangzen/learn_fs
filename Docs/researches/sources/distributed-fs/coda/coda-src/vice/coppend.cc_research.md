# sources/distributed-fs/coda/coda-src/vice/coppend.cc

## Purpose
`coppend.cc` implements the in-memory pending-COP table used between COP1 and COP2. Mutating operations add affected fids under a `ViceStoreId`; later COP2 processing dequeues the entry to update version vectors. A background LWP expires old entries.

## Important APIs, types, and functions
- `InitCopPendingTable` creates the global `CopPendingMan`.
- `AddToCopPendingTable` inserts a full `MAXFIDS` fid array for a store ID.
- `AddPairToCopPendingTable` appends one fid to an existing store ID entry or creates a new entry.
- `cpent` stores the `ViceStoreId`, up to `MAXFIDS` mutated fids, creation time, dequeue-in-progress flag, and a magic value checked by the destructor.
- `coppendhashfn` hashes store IDs by host plus uniquifier.
- `cpman` owns the hash table, lock, and manager LWP. Its public methods add, remove, find-and-dequeue, and print entries.

## Control flow
Initialization constructs `cpman`, which starts `cpman_func` as an LWP. Mutations call `add` or `AddPairToCopPendingTable`; both serialize with the manager lock. `InternalCOP2` calls `findanddeq`, which marks an entry `deqing` while COP2 owns it, then later calls `remove` and deletes it. The manager loop wakes every `CPINTERVAL` seconds, removes the first expired non-dequeuing entry after `CPTIMEOUT`, optionally prints debug state, and sleeps again.

## State and persistence behavior
The pending table is process memory only. It is not recoverable across server restart, so it is a transient coordination structure for live COP completion. The authoritative persistent outcome is the vnode/volume version-vector state updated by COP2. Expired entries are dropped after 900 seconds, which can leave a late COP2 returning `ENOENT`.

## Dependencies and integration points
This file depends on LWP process creation/sleep, Coda locks, `ohashtab`, `ViceStoreId`, `ViceFid`, `NullFid`, logging, and `SrvDebugLevel`. It is used by repair and reintegration code in `codaproc.cc` and `codaproc2.cc`.

## Risks
`AddPairToCopPendingTable` assumes no operation exceeds `MAXFIDS`; overflow is a hard assertion. `find` returns a pointer after releasing the read lock, so callers that mutate the entry depend on table lifetime assumptions. The expiration daemon removes only the first entry returned by `objects.first()` per interval, so a large backlog can linger. Since the table is volatile, crashes between COP1 and COP2 require higher-level repair/resolution to reconcile state.

## Test signals
Exercise multi-fid operations, duplicate fids, COP2 dequeue/removal, late COP2 after expiration, concurrent add/findanddeq, and debug print paths. Useful signals include `ENOENT` from `InternalCOP2`, expired BusyQueue log messages, and assertions around `MAXFIDS` or `CPENTMAGIC`.
