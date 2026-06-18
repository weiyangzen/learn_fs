## sources/distributed-fs/beegfs/client_module/source/os/atomic64.h

**Purpose:** Declares the fallback `atomic64_t` type and operation prototypes/macros for kernels that lack native 64-bit atomics.

**Important APIs/types/functions:** Defines fallback `atomic64_t` with `counter` and `spinlock_t lock`, declares all atomic64 operations implemented in `atomic64.c`, defines convenience macros such as `atomic64_inc`, `atomic64_dec`, and `atomic64_inc_not_zero`, and provides `atomic_init`.

**Control flow:** On kernels with native `ATOMIC64_INIT`, the file contributes nothing. Otherwise, callers use the familiar atomic64 API and the fallback implementation handles locking.

**State and persistence behavior:** Each atomic object stores its own counter and lock. `atomic_init` initializes both, replacing disabled upstream `ATOMIC64_INIT`.

**Dependencies and integration points:** Depends on `asm/atomic.h` feature availability and kernel spinlocks. It provides compatibility for BeeGFS modules built on older or weaker architectures.

**Risks:** The fallback `atomic_init` name may collide conceptually with generic atomic initialization APIs on some kernels, though it is only compiled in the missing-atomic64 path. Static initialization via `ATOMIC64_INIT` is intentionally unavailable in this fallback, so all objects need runtime initialization.

**Test signals:** Compile fallback and native paths, validate macro semantics, and audit all atomic64 users for explicit initialization.
