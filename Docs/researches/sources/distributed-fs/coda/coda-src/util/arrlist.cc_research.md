# sources/distributed-fs/coda/coda-src/util/arrlist.cc

## Purpose
Implements `arrlist`, a simple growable array of unowned `void *` pointers, and `arrlist_iterator`, a sequential iterator over the populated prefix.

## Important APIs, Types, And Functions
Constructors call `init()` with either an explicit size or default 32. `Grow()` doubles capacity or adds a requested increase. `add()` appends one pointer. `arrlist_iterator::operator()()` returns the next stored pointer until `NULL`.

## Control Flow
Initialization allocates and zero-fills the pointer array. `add()` grows when `cursize >= maxsize`, stores the pointer at `list[cursize]`, and increments `cursize`. Iteration tracks a previous index and reads from `list[0..cursize)`.

## State And Persistence
State is process-local: `list`, `maxsize`, and `cursize`. The container owns only the array storage, not the pointed-to objects. No RVM or disk persistence is involved.

## Dependencies And Integration Points
Depends on `malloc/free`, `CODA_ASSERT`, and `arrlist.h`. It is a generic helper for older Coda code that wants a minimal pointer vector without templates.

## Risks
No copy constructor or assignment protection is defined, so accidental copying would shallow-copy ownership and double-free. Iterators are invalidated by mutation and explicitly do not support deleting current entries. Allocation failures assert rather than returning errors.

## Test Signals
Construct with zero, default, and custom sizes; append past capacity; verify preserved entries and zero-filled new slots; iterate exactly `cursize` elements; destroy empty and populated lists under leak checking.
