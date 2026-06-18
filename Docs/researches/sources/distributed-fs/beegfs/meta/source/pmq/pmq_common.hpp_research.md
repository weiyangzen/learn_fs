## sources/distributed-fs/beegfs/meta/source/pmq/pmq_common.hpp

Purpose: shared PMQ runtime support: owning allocation wrappers, POSIX descriptor/mapping guards, mutex-protected values, string holders, tagged sequence numbers, wraparound comparisons, and typed ring buffers.

Important APIs and types: `Alloc_Slice<T>` owns a fixed array allocated once. `Posix_FD`, `Libc_DIR`, and `MMap_Region` close or unmap in destructors. `Mutex_Protected<T>` serializes `load`/`store` through a profiled mutex. `PMQ_String` and `PMQ_Owned_String` provide a simple immutable string holder. `SN<Tag>` implements typed sequence numbers with only distance addition/subtraction. `_sn64_*`, `sn64_*`, and `sn64_inrange` implement wraparound-aware comparisons. `Ringbuffer<Tag,V>` maps sequence numbers to power-of-two slots.

Control flow: PMQ initialization allocates ring-slot and chunk-buffer memory through these wrappers, publishes cursor snapshots through `Mutex_Protected`, and maps sequence numbers to slots through `Ringbuffer::get_slot_for`. Destructors handle cleanup on failed initialization and queue destruction.

State and persistence behavior: these types own in-memory state only, but `Posix_FD` lifetimes govern open handles for persisted PMQ files, and `MMap_Region` backs volatile queue/chunk buffers. `SN<Tag>` arithmetic defines all persistent cursor ordering.

Dependencies and integration points: includes PMQ logging, POSIX I/O, profiling macros, mmap/fcntl/stat/dirent, and standard allocation. The file intentionally avoids STL containers for PMQ hot-path primitives.

Risks: `Alloc_Slice` has no copy/move protection, so accidental copying would double-delete; current use keeps it as embedded non-copied state. `Ringbuffer(V *ptr, uint64_t size)` calls `reset(ptr, size)` even though only `reset(Slice<V>)` is defined in this source snapshot, so that constructor is either unused or depends on a missing overload. Wraparound ordering is not transitive by design and must only be used within bounded windows. `PMQ_Owned_String::set` throws `std::bad_alloc`, while much of PMQ otherwise returns bool/null on errors.

Test signals: unit tests should cover descriptor close/reset behavior, failed mmap cleanup, fixed-capacity allocation, sequence-number comparison near `UINT64_MAX`, ring-buffer slot wraparound, and published cursor snapshots under concurrent load/store.
