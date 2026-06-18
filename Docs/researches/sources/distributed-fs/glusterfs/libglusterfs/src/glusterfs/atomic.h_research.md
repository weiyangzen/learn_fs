# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/atomic.h

## Purpose
`atomic.h` defines GlusterFS portable atomic integer wrappers. It supports compiler `__atomic` builtins, older `__sync` builtins, and a lock-based fallback for unsupported type sizes, especially 64-bit atomics on 32-bit platforms.

## Important APIs, Types, and Functions
- `gf_atomic_int8_t`, `gf_atomic_int16_t`, `gf_atomic_int32_t`, `gf_atomic_int64_t`, pointer-sized signed variants, unsigned variants, and `gf_atomic_t` aliasing int64.
- `GF_ATOMIC_INIT`, `GET`, `ADD`, `SUB`, `AND`, `OR`, `XOR`, `NAND`, `FETCH_*`, `SWAP`, `CMP_SWAP`, `INC`, `DEC`.
- `GF_ATOMIC_CHOOSE()`: selects builtin vs lock implementation based on `sizeof(_atomic) > sizeof(uint64_t)`.
- Lock fallback macros: initialize and operate under `gf_lock_t`.
- Builtin implementations: `__atomic_*` with acquire/release or `__sync_*`.

## Control Flow
Compile-time feature and word-size macros decide whether each type embeds a zero-size dummy lock field or a real `gf_lock_t`. At each operation, `GF_ATOMIC_CHOOSE()` compares structure size and dispatches to the lock or builtin macro. Builtin `__atomic` operations use acquire/release memory order; `__sync` operations rely on full barriers.

## State and Persistence
Atomic state is embedded in caller-owned structures. Lock fallback atomics also embed a mutex-like `gf_lock_t` that must be initialized by `GF_ATOMIC_INIT`.

## Dependencies and Integration Points
Depends on `locking.h`, integer types, bool, and configure-time macros (`HAVE_ATOMIC_BUILTINS`, `HAVE_SYNC_BUILTINS`, `SIZEOF_LONG`). It is used broadly for fd refs, client refs/counts, I/O counters, and other shared state.

## Risks and Edge Cases
- All atomic variables must be initialized before use, especially lock fallback variants.
- The lock/builtin selection assumes mutex-bearing structures are larger than `uint64_t`.
- Direct access to `.value` bypasses synchronization.
- `NAND` semantics differ historically across builtin families; callers should avoid relying on nuanced old-value behavior without tests.

## Test Signals
Build on 32-bit and 64-bit configurations, with and without atomic builtins where possible. Test every operation against expected returned values, compare-swap success/failure, concurrent increments, and struct sizes that drive lock fallback.
