# sources/distributed-fs/coda/coda-src/venus/binding.h

## Purpose
This header defines the generic `binding` class used to represent a two-sided association with list handles and explicit refcount management.

## Important APIs, Types, and Functions
`binding` contains `binder_handle`, `binder`, `bindee_handle`, `bindee`, and `referenceCount`. `IncrRefCount()` and `DecrRefCount()` manage references, with an assertion preventing underflow. Copy construction and assignment abort. `print` overloads write debug state.

## Control Flow
The class is a passive container. External owners manipulate handles and endpoint pointers, then call refcount methods as ownership changes.

## State and Persistence Behavior
Binding state is transient and not recoverable on its own. Persistent or recoverable semantics belong to the structures connected by the binding.

## Dependencies and Integration Points
It depends on `dlist.h` and Coda assertions. `fsobj` declares methods to attach/detach `binding` instances for hoard database and modification log relationships.

## Risks and Test Signals
Risks include unscoped public fields and manual lifecycle requirements. Tests should cover underflow assertions, copy prevention, print output, and subsystem-level cleanup before destruction.
