## sources/distributed-fs/eos/namespace/MDLocking.cc

Purpose: Implements factory functions for namespace metadata RAII locks.

Important APIs and functions: `MDLocking::readLock/writeLock` overloads create `std::unique_ptr` wrappers for file and container read/write locks.

Control flow: each function simply constructs the corresponding `NSObjectMDLock` alias around a raw metadata pointer and returns it to the caller.

State and persistence: no durable state; returned lock objects own mutex acquisition/release lifetime.

Dependencies and integration: includes `MDLocking.hh`, `NSObjectLocker.hh`, and file/container interfaces. Used anywhere namespace metadata needs lock-order-aware read/write locking.

Risks: callers must pass valid metadata pointers and respect higher-level lock ordering. The wrappers do not encode cross-object order by themselves.

Test signals: compile tests for overload resolution, lock acquisition/release under read/write contention, and use with both file and container raw pointers.
