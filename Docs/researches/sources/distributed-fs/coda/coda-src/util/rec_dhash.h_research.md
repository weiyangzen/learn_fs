# sources/distributed-fs/coda/coda-src/util/rec_dhash.h

## Purpose
Declares the recoverable doubly-linked hash table.

## Important APIs, Types, And Functions
`RHFN`, `rec_dhashtab`, and `rec_dhashtab_iterator` mirror `dhashtab` with `rec_dlink` entries, `rec_dlist` buckets, recoverable allocation, and transaction annotations.

## Control Flow
Persistent callers initialize with power-of-two bucket count and callbacks, mutate inside transactions, and iterate by key or whole table.

## State And Persistence
Bucket topology and counts are intended to persist in RVM. Callback addresses are process state.

## Dependencies And Integration Points
Includes `dhash.h`, `rec_dlist.h`, and `rvmlib.h`.

## Risks
Requires strict transaction discipline and stable key hashing. No resizing or synchronization exists.

## Test Signals
Compile RVM users, test power-of-two validation, and verify committed bucket changes survive recovery.
