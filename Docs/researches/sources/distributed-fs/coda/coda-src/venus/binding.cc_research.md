# sources/distributed-fs/coda/coda-src/venus/binding.cc

## Purpose
This file implements the small `binding` object used as a generic association between a binder and bindee, with dlist handles for both sides and explicit reference counting.

## Important APIs, Types, and Functions
The constructor initializes `binder`, `bindee`, and `referenceCount` to zero and increments debug allocation counters. The destructor increments debug deallocation counters, logs a warning if the reference count is nonzero, and treats non-null endpoints as fatal. `print(int)` writes endpoint pointers and refcount to a file descriptor.

## Control Flow
Bindings are allocated empty, then other subsystems attach them to lists and set endpoints. Before deletion, owners must detach both handles, clear endpoints, and decrement references to zero.

## State and Persistence Behavior
State is in-memory only. Bindings connect runtime structures such as hoard database entries, modification log entries, and fsobjs.

## Dependencies and Integration Points
It includes `binding.h` and `venus.private.h` for logging and fatal error handling. `fso.h` uses `binding` in hoard and MLE linkage.

## Risks and Test Signals
Risks are dangling list links, double deletes, reference leaks, and fatal destructor checks during shutdown. Tests should attach/detach bindings through representative fsobj/hdb/mle paths and assert debug alloc/dealloc balance.
