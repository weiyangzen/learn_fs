# sources/distributed-fs/coda/coda-src/venus/persistent.h

## Purpose
This file is a template, intentionally disabled by `#error`, for RVM-backed persistent reference-counted objects. It documents a pattern later open-coded by classes such as `Realm`: separate recoverable reference counts from transient VM reference counts and destroy an object only when both reach zero inside a transaction.

## Important APIs, Types, and Functions
`PersistentObject` defines RVM allocation/deallocation operators, constructor initialization of `rec_refcount` and `refcount`, `ResetTransient()`, `Rec_GetRef()`, `Rec_PutRef()`, `GetRef()`, and `PutRef()`. The persistent methods use `RVMLIB_REC_OBJECT` and transaction annotations, while transient methods can run outside transactions.

## Control Flow
Creation allocates from recoverable memory and starts with one transient reference. Recovery calls `ResetTransient()` to drop transient references after restart and potentially delete objects that have no persistent references. Persistent reference changes are transaction-protected. Transient `PutRef()` can delete only when already inside an RVM transaction, otherwise destruction is deferred.

## State and Persistence Behavior
`rec_refcount` is recoverable and must be logged before mutation; `refcount` is transient. This is exactly the kind of split needed when persistent objects can be referenced from both RVM data structures and active in-memory users. The file is not meant to be compiled because RVM inheritance and virtual functions are called out as problematic.

## Dependencies and Integration Points
It depends on `rvmlib`, `venusrecov.h`, and Coda assertions. Its integration role is architectural guidance rather than direct inclusion.

## Risks and Test Signals
The visible risks are misspelled annotation macros (`REQUIRES_TRANSACION`) and the explicit `#error`, both reinforcing that it is not production code. Any class copied from this template should be tested for transaction correctness, restart-time `ResetTransient()` cleanup, and delayed deletion outside transactions.
