# sources/distributed-fs/ceph-client/security/landlock/object.h

## Purpose

`object.h` defines the generic Landlock object wrapper used to attach rules to underlying kernel objects without depending on the underlying object's lifetime alone.

## Important APIs, Types, and Functions

`struct landlock_object_underops` defines a `release()` callback. `struct landlock_object` contains a `usage` refcount, `lock`, `underobj` pointer, and a union for RCU freeing or underops pointer. `landlock_create_object()`, `landlock_put_object()`, and inline `landlock_get_object()` are the public object lifetime APIs.

## Control Flow

Provider code creates objects for underlying resources. Rules pin them. Final put calls provider release before RCU freeing, allowing weak references from underlying resources to be cleared.

## State and Persistence Behavior

The object persists independently of the underlying object while rules reference it. `underobj` marks whether it is still tied to the underlying kernel structure.

## Dependencies and Integration Points

The header is consumed by ruleset and filesystem code. It relies on refcount, spinlock, and RCU primitives.

## Risks and Test Signals

Lock ordering is documented: inode lock nests inside object lock. Violating this can deadlock. Test with lockdep, unmount/rule races, and object reference leak detection.
