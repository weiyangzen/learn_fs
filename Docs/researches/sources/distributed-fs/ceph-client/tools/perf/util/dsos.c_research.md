# sources/distributed-fs/ceph-client/tools/perf/util/dsos.c

## Purpose
This file manages a thread-safe collection of `struct dso *` objects. It stores DSOs in a dynamically sized array optimized for iteration and sorted binary lookup by long name, DSO id, and short name; it also supports module lookup/creation, build-id scanning, hit marking, and kernel DSO discovery.

## Important APIs, Types, And Functions
Public APIs are `dsos__init()`, `dsos__exit()`, `__dsos__add()`, `dsos__add()`, `dsos__find()`, `dsos__findnew_id()`, `dsos__read_build_ids()`, `dsos__fprintf_buildid()`, `dsos__fprintf()`, `dsos__hit_all()`, `dsos__findnew_module_dso()`, `dsos__find_kernel_dso()`, and `dsos__for_each_dso()`. Important internals include `__dsos__find_by_longname_id()`, `__dsos__find_id()`, `__dsos__addnew_id()`, `dso__set_basename()`, comparison helpers, and callback wrappers.

## Control Flow
Initialization sets an empty sorted array with an rwsem. Adds grow the array and either insert in sorted order or append if sorting is already invalid. Long-name lookups use bsearch, sorting under write lock if required; short-name lookups scan linearly. `findnew` holds the write lock, returns an existing DSO while improving its id if new metadata is available, or creates/inserts a new DSO. Module creation looks up by short module name, initializes module metadata, long name, kernel space, and inserts under lock.

## State, Dependencies, And Integration
`struct dsos` owns references to each DSO and clears `dso->dsos` during purge. It integrates with namespace-aware build-id reading, vdso hit exceptions, basename/JIT naming from perf map filenames, module parsing from `dso.c`, machine host/guest state, and kernel module classification. Read/write semaphores protect the array and sorted flag, but callbacks run under the read lock.

## Risks And Test Signals
Risks include callback code performing operations that need the write lock, stale sorted flags after DSO renames, incomplete identity causing false matches because empty IDs compare equal, memory leaks if `strdup(filename)` fails in module creation, and races if external users mutate DSO names outside provided setters. Tests should cover add/find ordering, findnew id improvement, short-name JIT basename generation, build-id reads with namespace fallback, module DSO creation for host/guest compressed modules, purge refcount behavior, and kernel DSO selection excluding modules.
