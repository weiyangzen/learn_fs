# sources/distributed-fs/coda/coda-src/venus/refcounted.h

## Purpose
This header defines a lightweight transient reference-counted base class for VM-only objects that should delete themselves when the last reference is released.

## Important APIs, Types, and Functions
`RefCountedObject` stores protected `refcount`, initializes it to one, asserts the destructor is reached only with `refcount <= 1`, and exposes `GetRef()`, `PutRef()`, and `PrintRef()`. `PutRef()` asserts a positive count, decrements, and `delete`s `this` at zero. A `TESTING` block defines a simple `RefObj` exerciser.

## Control Flow
Objects start with an implicit reference. Callers increment before sharing and call `PutRef()` when done. Deletion is synchronous on the final put.

## State and Persistence Behavior
The class is entirely transient and not thread-safe by itself. It should not be used for RVM-persistent objects because deletion and refcount changes are not transaction logged.

## Dependencies and Integration Points
It depends only on C stdio/assert headers. `mgrpent` privately inherits it, and other VM-only Venus objects can use the same pattern.

## Risks and Test Signals
Risks include non-atomic refcounting, deletion through base pointer expectations, accidental direct `delete` while references exist, and cyclic references. Unit tests should verify final-put deletion and assert behavior for over-release in debug builds.
