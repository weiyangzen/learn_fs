<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ObjectReferencer.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ObjectReferencer.h

**Purpose:** Provides a small template wrapper that stores an object reference, tracks a manual reference count, and optionally owns/deletes the referenced object when the wrapper is destroyed.

**Important APIs/types/functions:** `ObjectReferencer(T referencedObject, bool ownReferencedObject=true)`, destructor, `reference`, `release`, `getReferencedObject`, `getRefCount`, `setOwnReferencedObject`, and `getOwnReferencedObject`.

**Control flow:** `reference` increments `refCount` and returns the stored object. `release` decrements and returns the new count; when `DEBUG_REFCOUNT` is enabled it logs and avoids decrementing below zero if release is called at count zero. The destructor deletes `referencedObject` only when ownership is enabled.

**State and persistence behavior:** State is in-memory only: `refCount`, `ownReferencedObject`, and `referencedObject`. There is no mutex or atomic protection, so the counter is not thread-safe.

**Dependencies and integration points:** Uses `LogContext` only for debug underflow diagnostics. The type is intended for pointer-like `T` values because the destructor calls `delete referencedObject`.

**Risks:** Manual reference counting is easy to misuse and is not RAII-safe for borrowed references. Non-pointer `T` will not compile or will behave incorrectly due to `delete`. Unsynchronized increments/decrements can race. Disabling ownership after references exist changes destruction behavior globally.

**Test signals:** No direct tests in this subset. Useful tests would cover ownership on/off, debug underflow behavior, reference/release balance, and single-thread-only assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ObjectReferencer.h -->
