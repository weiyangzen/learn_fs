<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AtomicObjectReferencer.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/AtomicObjectReferencer.h

Purpose: Provides intrusive atomic reference counting for a raw object pointer.

Important APIs/types: `AtomicObjectReferencer<T>` stores `referencedObject`, `ownReferencedObject`, and atomic `refCount`. It exposes `reference`, `release`, `getRefCount`, and ownership flag accessors.

Control flow/state/persistence: `reference` increments and returns the raw pointer. `release` decrements; when the old count indicates the last reference and ownership is enabled, it deletes the object. Logging reports misuse when release is called with count 0.

Dependencies/integration: Uses `Atomics` and `LogContext`. It predates widespread `shared_ptr` usage.

Risks/test signals: Raw pointer lifetime and old-value semantics of `Atomic::decrease` are critical. Tests should cover last release deletion, non-owning mode, over-release logging, concurrent references, and object destruction ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AtomicObjectReferencer.h -->
