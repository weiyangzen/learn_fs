# sources/distributed-fs/eos/namespace/locking/RawPtr.hh

Purpose: supplies lightweight pointer helpers for lock templates or APIs that need pointer-like access without ownership.

Important APIs/types/functions: `no_delete` is a no-op deleter. `raw_ptr<T>` exposes `element_type`, `pointer`, `get`, `operator*`, `operator->`, bool conversion, and inequality comparison.

Control flow: trivial pointer forwarding; no allocation, deletion, or locking.

State and persistence: stores one raw pointer and never owns or persists it.

Dependencies and integration: lives in the EOS namespace and can satisfy template expectations similar to smart pointers, especially where object locks should operate on raw metadata objects without extending lifetime.

Risks: lifetime is entirely external. Dereferencing null or stale pointers is undefined. The inequality operator is non-const, limiting use with const `raw_ptr` values.

Test signals: covered only through consumers that instantiate lock/helper templates with raw metadata pointers.
