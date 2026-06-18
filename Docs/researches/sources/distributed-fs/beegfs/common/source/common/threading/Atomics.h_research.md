<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Atomics.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Atomics.h

Purpose: Wraps GCC legacy atomic builtins for simple atomic scalar values.

Important APIs/types: `Atomic<T>` and aliases for size, ssize, uint32, uint64, int16, and int64 expose `set`, `setZero`, `increase`, `decrease`, `compareAndSet`, and `read`.

Control flow/state/persistence: State is a single volatile-ish scalar updated with `__sync_*` full-barrier builtins. `read` uses fetch-add-zero for atomic read behavior.

Dependencies/integration: Used by threading and counters, notably `PThread` self-termination fast path. It avoids `<atomic>` and reflects older BeeGFS portability choices.

Risks/test signals: `increase`/`decrease` return the old value because `__sync_fetch_and_add/sub` is used. Tests should document return semantics, compare-and-set ordering, concurrent increments, and type width assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Atomics.h -->
