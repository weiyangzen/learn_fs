# sources/distributed-fs/ceph/src/osd/ClassHandler.h

## Purpose
`ClassHandler.h` declares the OSD object-class registry and loader interface. It models object classes, methods, and filters, and provides synchronized lookup/open APIs for OSD code.

## Important APIs, Types, and Control Flow
`ClassHandler` owns a `CephContext`, a map of class metadata, and a mutex. `ClassData` tracks load status (`CLASS_UNKNOWN`, `CLASS_MISSING`, `CLASS_MISSING_DEPS`, `CLASS_INITIALIZING`, `CLASS_OPEN`), class name, handler, dlopen handle, default allowed flag, method/filter maps, dependencies, and missing dependencies. It provides method/filter registration and lookup helpers. `ClassMethod` stores method name, a C or C++ callback variant, flags, and backpointer, with `exec()`, `unregister()`, and synchronized `get_flags()`. `ClassFilter` stores filter factory metadata.

## State and Persistence Behavior
All state is in-memory and protected by the handler mutex for lookup and flag reads. Object classes themselves are loaded from shared libraries by the `.cc` implementation; this header only declares the metadata and lifecycle.

## Dependencies and Integration Points
It depends on Ceph common types, `CephContext`, `ceph::mutex`, and object-class ABI declarations. It integrates with OSD operation execution paths that resolve a class method/filter by name and then call `exec()` or create filters.

## Risks and Test Signals
Risks include returning raw pointers into maps that may be invalidated by unload, insufficient locking during class initialization callbacks, duplicate registration behavior hidden by `try_emplace`, and methods with zero flags. Tests should compile-check ABI variants, verify method lookup and flags, simulate unregister behavior, and exercise concurrent open/lookup under the mutex.
