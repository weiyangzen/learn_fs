# sources/distributed-fs/ceph-client/tools/perf/util/pstack.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/pstack.h` exposes the opaque pointer-stack API used by perf utility code.

## Important APIs, Types, and Functions

The header forward-declares `struct pstack` and declares `pstack__new`, `pstack__delete`, `pstack__empty`, `pstack__remove`, `pstack__push`, and `pstack__peek`.

## Control Flow

No runtime flow exists in the header. Callers create a stack with a fixed capacity, push pointer keys, optionally remove a specific key, peek the top entry, and delete the stack.

## State and Persistence Behavior

The stack object is opaque and in-memory only. Pointer payload ownership remains with callers.

## Dependencies and Integration Points

The only external include is `<stdbool.h>`. The API is intentionally generic and does not depend on perf-specific types in the header.

## Risks and Edge Cases

The capacity type is `unsigned short`, matching the implementation. There is no thread-safety contract and no ownership transfer for pushed pointers.

## Test Signals

Compile users against the opaque type, plus behavioral tests in `pstack.c`, are sufficient.
