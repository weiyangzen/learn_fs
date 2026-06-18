# Research Group subset-b-000554

Grouped research for BeeGFS metadata server PMQ, program bootstrap, session, locking, mirrored response state, and selected storage dentry files. Each section is source-tree aligned and bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq.cpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq.cpp

Purpose: implements the persistent message queue declared by `pmq.hpp`. It is a single-enqueuer/single-persister design with concurrent readers, using an in-memory slot ring for fresh messages, compacted fixed-size chunk buffers for older persisted messages, and three on-disk files under the queue directory: `wal.dat`, `chunks.dat`, and `state.dat`.

Important types and APIs: internal tagged sequence numbers `CSN`, `SSN`, and `MSN` use `SN<Tag>` from `pmq_common.hpp`. `PMQ_Slot` is a 128-byte ring slot with a leader flag, message-size field, and 112-byte payload. `PMQ_Chunk_Hdr` stores the first MSN, message count, and offset-table location inside a 64 KiB chunk. `In_Queue`, `Chunk_Queue`, `Chunk_Store`, `Persist_Cursors`, and `Commit_Record` are the core state structures. Public entry points are `pmq_create`, `pmq_destroy`, `pmq_enqueue_msg`, `pmq_sync`, `pmq_get_stats`, `pmq_get_persist_info`, reader creation/destruction, seek helpers, `pmq_read_msg`, `pmq_reader_find_old_msn`, and `pmq_reader_eof`.

Control flow: enqueue locks `enqueue_mutex`, computes the required slot count, calls `pmq_prepare_input_slots`, and serializes payload fragments into consecutive ring slots. If slots are exhausted, the enqueue path may take `persist_mutex` and force `pmq_persist`. Persistence compacts slot messages into chunk buffers (`pmq_compact`), writes finished chunks to `chunks.dat`, writes unchunked tail slots to `wal.dat`, fsyncs, and finally writes `Commit_Record` to `state.dat`. Reader flow refreshes published persistence cursors, seeks either in the chunk store by binary-searching chunk headers or in the slot region by scanning leader slots, then reads from either `chunks.dat` or the slot ring.

State and persistence behavior: `wal_ssn`/`wal_msn` describe the durable tail in `wal.dat`; `cks_csn`/`cks_msn`/`cks_ssn` describe the next chunk to write; `cks_discard_csn` is the oldest retained chunk. `pmq_commit` fsyncs the chunk file, writes and fsyncs `state.dat`, then publishes cursors. Chunk-store capacity is rounded to a power of two and must be at least 64 MiB. On load, `pmq_init_loadexisting` validates weak ordering and file sizes, reads `wal.dat` into the in-memory ring, opens `chunks.dat`, and reconstructs cursors. On create, `pmq_init_createnew` creates the directory and preallocates all backing files.

Dependencies and integration points: depends on `pmq_common.hpp` for RAII wrappers, slices, ring buffers, memory mapping, logging, and POSIX helpers. It integrates with BeeGFS logging indirectly through `pmq_logging.cpp`. Readers and enqueue/persist code rely on `Mutex_Protected` publication of cursor snapshots.

Risks: there is no checksum in the slot or chunk formats, so integrity checks catch structure violations but not arbitrary payload corruption. The slot-file is currently as large as the in-memory queue despite comments that only a tail is needed. Readers lock `enqueue_mutex` while reading slot-region messages, which can block writers for large messages. `pmq_read_msg_chunkstore` sets `out_size` but does not return `Buffer_Too_Small` when the caller buffer is undersized, unlike the slot-file path. Sequence number wraparound is intentionally theoretical and largely untested. Several validation comments note historical bugs around finalized chunk cursors and RAM loaded from disk being corruptible.

Test signals: useful tests include create/load round trips across `wal.dat` and `chunks.dat`, enqueue sizes spanning one and many slots, forced chunk rollover, buffer pressure causing enqueue-triggered persistence, recovery from incomplete/empty files, reader seeks to current/oldest/specific MSN, concurrent discard returning `Out_Of_Bounds`, and corruption cases for non-leader slots, invalid offset tables, and invalid commit cursor ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq.hpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq.hpp

Purpose: public C/C++ API for the PMQ persistent queue. It intentionally hides `PMQ` and `PMQ_Reader` internals and exposes enqueue, sync, persistence-status, stats, and sequential reader operations.

Important APIs and types: `PMQ_Init_Params` carries `basedir_path` and optional `create_size`; `PMQ_Stats` combines `PMQ_Enqueuer_Stats` and `PMQ_Persister_Stats`; `PMQ_Persist_Info` exposes the oldest chunk CSN and next MSNs for chunk store and WAL. `PMQ_Read_Result` provides explicit read outcomes: success, too-small buffer, EOF, out-of-bounds, I/O error, and integrity error. The C++ RAII aliases `PMQ_Handle` and `PMQ_Reader_Handle` wrap the raw handles with `pmq_destroy` and `pmq_reader_destroy`.

Control flow: callers create a queue with `pmq_create`, enqueue using `pmq_enqueue_msg`, make current messages durable using `pmq_sync`, and destroy with `pmq_destroy`, which flushes before cleanup. Readers are created from a queue, positioned with `pmq_reader_seek_to_current`, `pmq_reader_seek_to_oldest`, or `pmq_reader_seek_to_msg`, and advanced with `pmq_read_msg`.

State and persistence behavior: the header documents that a queue directory is either loaded if it exists or created if absent. `pmq_reader_find_old_msn` warns that the oldest persisted message may be discarded concurrently. `pmq_reader_eof` is a cheap synchronization-oriented check based on current persisted cursors, not a blocking wait.

Dependencies and integration points: depends only on fixed-size integer and size headers, keeping the C surface lightweight. The RAII wrapper requires C++ compilation and `std::swap` availability through transitive includes in current use.

Risks: `pmq_enqueue_msg` asserts nonzero size in the implementation, but the public header does not document the zero-size restriction. The returned `PMQ_Persist_Info` is a snapshot and can become stale immediately under concurrent enqueue/persist/discard. Reader positioning semantics require callers to handle `Out_Of_Bounds` and retry after concurrent discard.

Test signals: API-level tests should exercise RAII destruction, failure from invalid/create-size paths, all `PMQ_Read_Result` values, reader EOF behavior before and after sync, and documented stale-snapshot behavior around persistence info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_base.hpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq_base.hpp

Purpose: foundational PMQ utilities for attributes, assertions, alignment, byte slices, typed slices, and pointer wrappers. It keeps low-level helper code small and avoids heavier STL abstractions in hot PMQ headers.

Important APIs and types: `__pmq_cache_aligned`, `__pmq_profiled`, `__pmq_artificial_method`, `__pmq_artificial_func`, and `__pmq_formatter` centralize compiler attributes. `pmq_assert` wraps assertions and sleeps before failing in debug builds. `Untyped_Slice` and `Slice<T>` carry non-owning memory ranges with offset/sub-slice helpers. `copy_slice`, `copy_to_slice`, `copy_from_slice`, and `zero_out_slice` implement bounded memory copies. `Pointer<T>` wraps a non-null single-object pointer and intentionally does not expose array indexing.

Control flow: the file is header-only. Call sites construct slices around stack buffers, mmap regions, ring slots, chunk buffers, and serialized records, then use the helper functions to copy or zero exact ranges. Alignment helpers assert runtime alignment and feed `__builtin_assume_aligned` to the compiler.

State and persistence behavior: no persistent state is stored here, but these types are heavily used for PMQ persistence I/O. Incorrect slice sizes or alignment assumptions can directly affect `wal.dat`, `chunks.dat`, and `state.dat` writes.

Dependencies and integration points: uses libc, POSIX `sleep`, GCC attributes, and `__assert_fail`. The format diagnostic pragma makes PMQ format warnings hard errors for the translation units including this header.

Risks: compiler attributes and `#pragma GCC diagnostic error "-Wformat"` are GCC-oriented and may reduce portability. `Pointer<T>` asserts non-null but still has pointer semantics. Slice helpers rely on assertions for bounds, so release builds may not catch misuse before memory corruption.

Test signals: compile tests with and without `NDEBUG`/`PMQ_WITH_PROFILING`, format-string warning tests, alignment tests on mapped buffers, and fuzz-style slice subrange tests would protect this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_base.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_common.hpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq_common.hpp

Purpose: shared PMQ runtime support: owning allocation wrappers, POSIX descriptor/mapping guards, mutex-protected values, string holders, tagged sequence numbers, wraparound comparisons, and typed ring buffers.

Important APIs and types: `Alloc_Slice<T>` owns a fixed array allocated once. `Posix_FD`, `Libc_DIR`, and `MMap_Region` close or unmap in destructors. `Mutex_Protected<T>` serializes `load`/`store` through a profiled mutex. `PMQ_String` and `PMQ_Owned_String` provide a simple immutable string holder. `SN<Tag>` implements typed sequence numbers with only distance addition/subtraction. `_sn64_*`, `sn64_*`, and `sn64_inrange` implement wraparound-aware comparisons. `Ringbuffer<Tag,V>` maps sequence numbers to power-of-two slots.

Control flow: PMQ initialization allocates ring-slot and chunk-buffer memory through these wrappers, publishes cursor snapshots through `Mutex_Protected`, and maps sequence numbers to slots through `Ringbuffer::get_slot_for`. Destructors handle cleanup on failed initialization and queue destruction.

State and persistence behavior: these types own in-memory state only, but `Posix_FD` lifetimes govern open handles for persisted PMQ files, and `MMap_Region` backs volatile queue/chunk buffers. `SN<Tag>` arithmetic defines all persistent cursor ordering.

Dependencies and integration points: includes PMQ logging, POSIX I/O, profiling macros, mmap/fcntl/stat/dirent, and standard allocation. The file intentionally avoids STL containers for PMQ hot-path primitives.

Risks: `Alloc_Slice` has no copy/move protection, so accidental copying would double-delete; current use keeps it as embedded non-copied state. `Ringbuffer(V *ptr, uint64_t size)` calls `reset(ptr, size)` even though only `reset(Slice<V>)` is defined in this source snapshot, so that constructor is either unused or depends on a missing overload. Wraparound ordering is not transitive by design and must only be used within bounded windows. `PMQ_Owned_String::set` throws `std::bad_alloc`, while much of PMQ otherwise returns bool/null on errors.

Test signals: unit tests should cover descriptor close/reset behavior, failed mmap cleanup, fixed-capacity allocation, sequence-number comparison near `UINT64_MAX`, ring-buffer slot wraparound, and published cursor snapshots under concurrent load/store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_common.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.cpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.cpp

Purpose: implements PMQ logging. In normal BeeGFS metadata-server builds it forwards messages to the BeeGFS `Logger`; in `PMQ_TEST` builds it buffers formatted messages in a local blocking ring for tests or standalone consumers.

Important APIs and types: `Log_Buffer` owns a 1024-message circular buffer, mutex, and two condition variables. `pmq_write_log_message`, `pmq_read_log_message`, `pmq_try_read_log_message`, and timeout read functions expose low-level message transport. `log_msg_printfv`, `log_msg_printf`, `pmq_msg_ofv`, and `pmq_msg_of` format severity, message body, optional errno text, and source location.

Control flow: callers use macros from `pmq_logging.hpp` to create `PMQ_Msg_Options`; `pmq_msg_ofv` formats a `Log_Message`. In integrated mode, it maps PMQ debug/info/warn/error to BeeGFS log priorities and calls `Logger::log`. In test mode, it applies `PMQ_LOG_LEVEL`, prefixes severity text, appends newline, and writes into `global_log_buffer`.

State and persistence behavior: logging state is process-local. `global_log_buffer` persists only for the process lifetime and can block writers when full in test mode.

Dependencies and integration points: depends on `pmq_common.hpp` for allocation and profiled mutex/condition macros, and on BeeGFS `Logger` outside test builds. Errno text uses `strerror_r` with GNU/XSI branches.

Risks: test-mode logging can block indefinitely if no reader drains the fixed ring. Integrated mode does not perform the same local log-level early return as test mode. `log_msg_printfv` clamps `msg->size` after `vsnprintf`, which avoids overflow but truncates silently.

Test signals: tests should cover severity mapping, errno formatting under GNU and XSI `strerror_r`, blocking/try/timeout reads, truncation to `Log_Message` capacity, and compile behavior for `PMQ_TEST` without `PMQ_LOG_LEVEL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.hpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.hpp

Purpose: declares PMQ log options, formatting entry points, convenience macros, and the small low-level `Log_Message` transport used by test builds.

Important APIs and types: log flags encode errno inclusion and severity in `PMQ_Msg_Options`. `PMQ_Source_Loc` captures file and line. Macros such as `pmq_msg_f`, `pmq_warn_f`, `pmq_perr_ef`, and `pmq_debug_ef` build options with source location. `Log_Message` is a fixed 256-byte record minus the `size_t` field.

Control flow: PMQ code calls macros rather than constructing options manually. All macros funnel into `pmq_msg_of`, which uses `pmq_msg_ofv` from the `.cpp` implementation.

State and persistence behavior: no persistent state. The source-location data is included in options and may be used by the BeeGFS logger.

Dependencies and integration points: includes `pmq_base.hpp` for the printf-format attribute. The low-level reader/writer declarations match the test-mode global log buffer.

Risks: `PMQ_MSG_OPTIONS((lvl), 0)` relies on aggregate initialization and variadic macro behavior that is compiler-sensitive. The 256-byte low-level message limit means high-detail PMQ errors can be truncated.

Test signals: compile-time format checking, macro expansion tests, and log truncation tests are the highest-value coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_posix_io.hpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq_posix_io.hpp

Purpose: header-only POSIX I/O helpers for PMQ file opening and full-length read/write loops. It centralizes error logging and regular-file checks around low-level syscalls.

Important APIs: `pmq_open_dir` opens directories with `O_RDONLY | O_DIRECTORY`. `pmq_check_regular_file` validates `fstat` and `S_ISREG`. `pmq_openat_regular_existing` opens an existing regular file without creation flags. `pmq_openat_regular_create` creates with `O_CREAT | O_EXCL`. `assert_sane_size` guards syscall sizes against `ssize_t` overflow. `pmq_write_all`, `pmq_pwrite_all`, `pmq_read_all`, and `pmq_pread_all` loop until the full slice is transferred.

Control flow: PMQ init and persistence use these helpers for `state.dat`, `wal.dat`, and `chunks.dat`. On syscall failure they log with PMQ errno-aware logging and preserve `errno` for callers where needed.

State and persistence behavior: this file performs no high-level persistence decisions but directly writes and reads PMQ serialized state and chunk/slot data. Full-transfer loops are critical for avoiding partial durable records.

Dependencies and integration points: depends on POSIX open/fstat/read/write/pread/pwrite and `pmq_logging.hpp`. It consumes `Untyped_Slice` from `pmq_base.hpp` through included logging/base headers.

Risks: read helpers do not treat zero-byte reads as errors inside a non-empty request, so an unexpected EOF can spin because the slice does not advance. Write helpers similarly do not explicitly handle zero-byte writes. Creation helper relies on `O_EXCL` instead of validating regular-file type afterward.

Test signals: short read/write injection, EOF during fixed-size read, symlink/directory open attempts, errno preservation, and files larger than `SSIZE_MAX` should be covered with fakes or controlled temp files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_posix_io.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_profiling.hpp -->
## sources/distributed-fs/beegfs/meta/source/pmq/pmq_profiling.hpp

Purpose: provides build-time profiling abstraction macros for PMQ scopes, functions, mutexes, condition variables, and locks, optionally integrating with Tracy.

Important APIs: when `PMQ_WITH_PROFILING` is enabled, `PMQ_PROFILING_CTX`, `PMQ_PROFILED_SCOPE`, `PMQ_PROFILED_FUNCTION`, `PMQ_PROFILED_MUTEX`, `PMQ_PROFILED_CONDVAR`, `PMQ_PROFILED_LOCK`, and `PMQ_PROFILED_UNIQUE_LOCK` expand to Tracy-aware constructs. Otherwise they expand to standard `std::mutex`, `std::condition_variable`, `std::lock_guard`, and `std::unique_lock` wrappers.

Control flow: PMQ code writes profiling-neutral lock and scope declarations. The macros choose whether instrumentation exists at compile time.

State and persistence behavior: no persistence. The selected mutex/condition types affect synchronization behavior and type compatibility across PMQ implementation files.

Dependencies and integration points: includes `<mutex>` and `<condition_variable>` always, and `<Tracy.hpp>` only under profiling. Comments identify a BeeGFS/flex-docs build setup requirement for Tracy headers.

Risks: profiling mode uses `std::condition_variable_any` and Tracy lock wrappers, which can differ in overhead and behavior from the non-profiling build. The macro-generated temporary names require careful use to avoid collisions.

Test signals: compile both profiling and non-profiling variants, run lock/condition wait tests in both modes, and check that PMQ hot paths still build when Tracy headers are absent and profiling is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/pmq/pmq_profiling.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/program/Main.cpp -->
## sources/distributed-fs/beegfs/meta/source/program/Main.cpp

Purpose: process entry point for the BeeGFS metadata server binary. It delegates all startup and shutdown behavior to `Program::main`.

Important APIs/functions: the only function is `int main(int argc, char** argv)`, returning `Program::main(argc, argv)`.

Control flow: no local initialization occurs before delegation, so all runtime checks and `App` lifecycle work are in `Program.cpp`.

State and persistence behavior: no state or persistence is touched in this file.

Dependencies and integration points: includes `Program.h`, making `Program` the bootstrap facade for the executable.

Risks: minimal. Any crash or failure behavior is controlled by `Program::main` and `App`.

Test signals: a smoke/link test should ensure the metadata-server target links exactly one `main` and returns the `Program::main` result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/program/Main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/program/Program.cpp -->
## sources/distributed-fs/beegfs/meta/source/program/Program.cpp

Purpose: implements static program startup. It performs build/runtime checks, constructs the metadata `App`, runs it in the current thread, captures the application result, and deletes the app.

Important APIs/functions: `App* Program::app` is the global app pointer. `Program::main` calls `BuildTypeTk::checkDebugBuildTypes`, `AbstractApp::runTimeInitsAndChecks`, `new App(argc, argv)`, `App::startInCurrentThread`, `App::getAppResult`, and `delete app`.

Control flow: initialization checks happen before `App` construction. The app runs synchronously in the caller thread; after it stops, the result code is read before deletion and returned to `main`.

State and persistence behavior: owns the process-global `Program::app` pointer for the app lifetime. This pointer is the integration point used throughout metadata server code, including session cleanup, lock notifications, PMQ logging, and dentry storage.

Dependencies and integration points: depends on `BuildTypeTk`, `AbstractApp`, and `App`. `Program::getApp` from the header exposes the static pointer to subsystems.

Risks: `app` is not reset to `NULL` after deletion, so late static/destructor code calling `Program::getApp()` would see a dangling pointer. `new App` is not checked for allocation failure.

Test signals: startup tests should validate runtime checks happen before app construction, app result propagation, and no subsystem uses `Program::getApp()` after app teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/program/Program.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/program/Program.h -->
## sources/distributed-fs/beegfs/meta/source/program/Program.h

Purpose: declares the static `Program` facade for the metadata server process and exposes the current `App` singleton-like pointer.

Important APIs/types: `Program::main(int argc, char** argv)` is the bootstrap entry. `Program::getApp()` returns the static `App*`. The constructor is private to prevent instances.

Control flow: external code does not instantiate `Program`; it calls static methods only. Many subsystems use `Program::getApp()` to access `Config`, `MetaStore`, work queues, sessions, and disposal directories.

State and persistence behavior: no persistence, but `Program::app` is global process state and effectively a service locator.

Dependencies and integration points: includes `<app/App.h>`. This creates broad coupling from storage/session code back to application-level services.

Risks: raw global pointer makes lifetime assumptions implicit. Tests using code that calls `Program::getApp()` need a real or mocked `App` installed.

Test signals: compile and dependency tests should watch for unintended inclusion bloat and initialization-order issues around `Program::app`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/program/Program.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/EntryLock.h -->
## sources/distributed-fs/beegfs/meta/source/session/EntryLock.h

Purpose: RAII wrappers around `EntryLockStore` locks for file IDs, parent/name pairs, and hash-directory fragments. These wrappers make mirrored-message and metadata operation locking exception/return-path safe.

Important APIs/types: `UniqueEntryLockBase<LockDataT>` owns an `EntryLockStore*` and a lock descriptor pointer and unlocks in its destructor. It is move-only and supports `swap`. `FileIDLock`, `ParentNameLock`, and `HashDirLock` specialize the base for `FileIDLockData`, `ParentNameLockData`, and `HashDirLockData`.

Control flow: constructors call `entryLockStore->lock(...)` and retain the returned descriptor. Destruction calls `entryLockStore->unlock(lockData)` if a descriptor is held. Move construction/assignment transfers ownership by swapping pointers.

State and persistence behavior: state is in-memory locking only. No session or metadata state is serialized here.

Dependencies and integration points: includes `EntryLockStore.h`. Message handlers in `net/message/...` return these types from `lock(EntryLockStore&)` methods to synchronize mirrored operations and local metadata mutation.

Risks: the base assumes `entryLockStore` remains alive longer than all wrappers. The inheritance is private for concrete classes, which is fine for RAII use but means callers only interact through construction/destruction. Default-constructed locks are empty and safe.

Test signals: tests should cover move construction/assignment, destructor unlock exactly once, empty lock destruction, and lock ordering in message handlers that return tuples of these lock types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/EntryLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.cpp -->
## sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.cpp

Purpose: implements typed lock acquisition and release for metadata entries. It maps high-level lock requests to `Mutex` or `RWLock` primitives held in `ValueLockStore` buckets.

Important functions: `lock(parentID,name)` gets a parent/name mutex descriptor and locks it. `lock(fileID, writeLock)` gets an `RWLock` descriptor and takes a read or write lock. `lock(hashDir)` gets and locks a hash-directory mutex. The three `unlock` overloads unlock the primitive and then return the descriptor to its store.

Control flow: each lock method first obtains a reference-counted descriptor from the appropriate `ValueLockStore`, then locks the underlying primitive before returning. Unlock reverses the order: release primitive first, decrement descriptor reference second.

State and persistence behavior: lock descriptors are transient in-memory state. Reference counts and per-bucket buffers live in `EntryLockStore`.

Dependencies and integration points: used by `EntryLock.h` RAII wrappers and metadata mirrored message lock methods. Depends on `Mutex` and `RWLock` from BeeGFS common threading.

Risks: callers must use the matching `unlock` overload for the descriptor type; RAII wrappers help enforce this. If a thread blocks while taking the primitive after descriptor acquisition, the descriptor stays referenced and cannot be recycled.

Test signals: concurrent acquisition/release by same and different keys, read/write exclusion for file IDs, descriptor reuse after buffer return, and hash collision behavior should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.h -->
## sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.h

Purpose: defines key-to-lock storage for metadata entry locking. It avoids unbounded allocation churn by using fixed hash buckets and small per-bucket buffers of reusable lock descriptors.

Important APIs/types: `ValueLockHash<Value>` specializations hash strings, parent/name pairs, and hash-dir pairs. `ValueLockStore<Value, Lock, HashSize, BufferSize>` manages `ValueLock` descriptors containing a lock primitive, key value, bucket pointer, list iterator, and reference count. Type aliases define `ParentNameLockStore`, `FileIDLockStore`, `HashDirLockStore`, and their descriptor types. `EntryLockStore` exposes typed lock/unlock functions.

Control flow: `getLockFor` hashes the key, locks the bucket mutex, searches active descriptors, either reuses a buffered descriptor or allocates a new one, increments references, and returns it. `putLock` decrements references and moves unused descriptors into the bucket buffer or deletes them when the buffer is full.

State and persistence behavior: all state is volatile. The active list and buffer list per bucket determine descriptor lifetime and allocation patterns.

Dependencies and integration points: integrates with BeeGFS `Mutex`, `RWLock`, `LogContext`, and the RAII wrappers in `EntryLock.h`. Hash choices are tuned for metadata entry IDs and inode/dentry hash-dir fragments.

Risks: active descriptor lookup is linear within a bucket, so pathological hash concentration can increase lock acquisition time. The parent/name hash specialization signature accepts `std::pair<const std::string&, const std::string&>` while the specialization type is `std::pair<std::string, std::string>`, relying on compatible invocation patterns. `ValueLock` objects are manually allocated and deleted.

Test signals: bucket buffer saturation, repeated same-key acquisition reference counts, pair-hash consistency, concurrent `getLockFor`/`putLock`, and no descriptor reuse while references remain are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.cpp -->
## sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.cpp

Purpose: enqueues asynchronous notification work for clients/processes waiting on file entry locks or byte-range locks.

Important functions: `notifyWaitersEntryLock` creates `LockEntryNotificationWork`; `notifyWaitersRangeLock` creates `LockRangeNotificationWork`. Both accept ownership of their notification lists through move semantics and submit work to the communication slave queue.

Control flow: each method fetches `Program::getApp()->getCommSlaveQueue()`, allocates a `Work` object, and calls `addDirectWork`.

State and persistence behavior: no persistent state. Notification lists are transferred into work packages and processed asynchronously by worker infrastructure.

Dependencies and integration points: depends on `Program`, `MultiWorkQueue`, `Work`, `LockEntryNotificationWork`, and `LockRangeNotificationWork`. It is part of the lock-grant path in storage/session locking.

Risks: raw `new` assumes `addDirectWork` assumes ownership. `Program::getApp()` and `getCommSlaveQueue()` must be valid. If allocation fails, no notification is sent.

Test signals: tests should verify ownership transfer of notify lists, correct work type and fields, and queue submission for both entry and range locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.h -->
## sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.h

Purpose: declares a static utility for scheduling lock notification work when file locks become available.

Important APIs/types: `notifyWaitersEntryLock` takes lock type, parent entry ID, entry ID, buddy-mirror flag, and `LockEntryNotifyList`. `notifyWaitersRangeLock` takes parent entry ID, entry ID, buddy-mirror flag, and `LockRangeNotifyList`.

Control flow: callers do not instantiate `LockingNotifier`; the constructor is private and functions are static.

State and persistence behavior: no state or persistence.

Dependencies and integration points: includes storage locking definitions and worker work-package headers. The declarations document that notifier takes ownership of notify lists.

Risks: the ownership contract is important because lists are moved into asynchronous work in the implementation.

Test signals: compile tests around move-only/owned notification lists and call sites that should not reuse lists after notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/MirrorMessageResponseState.cpp -->
## sources/distributed-fs/beegfs/meta/source/session/MirrorMessageResponseState.cpp

Purpose: serializes and deserializes response-state objects for mirrored metadata messages. These states let the server remember and replay responses for exactly-once or retry handling around mirror buddy processing.

Important functions: `MirroredMessageResponseState::serialize` writes a serializer tag and delegates to virtual `serializeContents`. `deserialize` reads the tag, maps it to a concrete message extension `ResponseState`, and constructs that state from the deserializer.

Control flow: deserialization uses a `HANDLE_TAG` macro in a `switch` over `NETMSGTYPE_*` constants. Known tags instantiate response states from many message families: opening/closing/truncation, creating/removing, moving/rename, xattrs/attrs, lookup, locking, ack notification, bump file version, and stripe-pattern update. Unknown tags log an error, mark the deserializer bad, and return null.

State and persistence behavior: serialized response states are stored inside `Session::mirrorProcessState`. A bad tag invalidates deserialization, preventing silent use of unknown persisted mirror state.

Dependencies and integration points: includes all message extension headers whose `ResponseState` types can be persisted. Uses `boost::make_unique` and BeeGFS logging.

Risks: every mirrored message with persistent response state must be represented in the switch; missing tags break replay/deserialization. The macro assumes each message extension exposes a nested `ResponseState` with a `Deserializer&` constructor. There is a spelling inconsistency in `AckNotifiyMsgEx` include/type that is presumably matched elsewhere.

Test signals: serialization/deserialization round trips for each handled tag, unknown-tag failure, partial-buffer failure, and compatibility tests when adding new mirrored message types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/MirrorMessageResponseState.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/MirrorMessageResponseState.h -->
## sources/distributed-fs/beegfs/meta/source/session/MirrorMessageResponseState.h

Purpose: declares the polymorphic base and common response-state templates used by mirrored message processing.

Important APIs/types: `MirroredMessageResponseState` requires `sendResponse`, `changesObservableState`, `serializerTag`, and `serializeContents`. `ErrorCodeResponseState<RespMsgT, SerializerTag>` stores an `FhgfsOpsErr` and sends either a generic indirect communication error or `RespMsgT(result)`. `ErrorAndEntryResponseState<RespMsgT, SerializerTag>` additionally stores `EntryInfo` and sends `RespMsgT(result, &info)`.

Control flow: concrete message response states either derive directly from the base or use these templates. Common templates deserialize by reading result and optional `EntryInfo`, serialize the same fields, and report observable changes only on `FhgfsOpsErr_SUCCESS`.

State and persistence behavior: response state is serialized into session mirror state slots. This is process and restart relevant because sessions can be saved and loaded.

Dependencies and integration points: depends on `GenericResponseMsg`, `EntryInfo`, `Serializer`, `Deserializer`, and net-message response contexts. Used by many `*MsgEx` mirrored message classes.

Risks: `changesObservableState` equates success with observable mutation, which may be too coarse for messages that succeed without mutation or fail after partial mutation unless they provide custom response states. Communication errors are normalized to a generic response instead of the specific response message type.

Test signals: test result serialization, communication-error response mapping, success/failure observable-state semantics, and derived custom response states with the deserializer factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/MirrorMessageResponseState.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/Session.cpp -->
## sources/distributed-fs/beegfs/meta/source/session/Session.cpp

Purpose: implements small `Session` operations not defined inline in the header.

Important functions: `mergeSessionFiles` merges another session's open-file sessions into this session. `operator==` compares session ID and contained `SessionFileStore`.

Control flow: merge delegates to `SessionFileStore::mergeSessionFiles`; equality delegates to `SessionFileStore::operator==`.

State and persistence behavior: merge affects in-memory session file maps and is used during deserialization when a loaded session already exists locally. Equality supports tests and state comparison.

Dependencies and integration points: includes `Session.h`; actual persistence behavior is in header serialization and `SessionStore`.

Risks: merge ownership semantics are subtle because `SessionFileStore::mergeSessionFiles` moves or deletes referencers from the source store. Callers must not continue using the source session as if it still owns its files.

Test signals: merge duplicate and non-duplicate file-session IDs, equality after serialize/deserialize, and source-session cleanup after merge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/Session.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/Session.h -->
## sources/distributed-fs/beegfs/meta/source/session/Session.h

Purpose: represents a client session, including open file sessions and mirrored-message response state slots keyed by sequence number.

Important APIs/types: `MirrorStateSlot` serializes a bool plus optional `MirroredMessageResponseState`. `Session` stores `NumNodeID sessionID`, `SessionFileStore files`, and `mirrorProcessState`. Public methods expose file store access, inode relinking, mirror-state slot acquisition/freeing, sequence-number base calculation, merge, serialization, and equality.

Control flow: serialization writes `sessionID`, `files`, and `mirrorProcessState`, then calls `dropEmptyStateSlots(ctx)`. The serializer overload is a no-op, while the deserializer overload removes empty mirror slots after loading. `acquireMirrorStateSlot` erases all states up to `endSeqno` and inserts/returns the slot for `thisSeqno`. `acquireMirrorStateSlotSelective` erases one finished sequence and inserts the current one. Shared pointers keep slots alive for threads even if the map entry is erased.

State and persistence behavior: session files and mirror process state are persisted by `SessionStore`. Empty mirror slots are deliberately discarded on load to avoid retry requests waiting forever after a shutdown while a message was still processing.

Dependencies and integration points: depends on `SessionFileStore`, `MirrorMessageResponseState`, `MetaStore`, BeeGFS serialization, and `Mutex`. It is used by normal and mirrored session stores in `App`.

Risks: `getFiles()` exposes mutable internal store. Mirror state cleanup assumes client sequence-number behavior; comments explicitly handle misbehaving clients by keeping shared slot lifetimes independent of map membership. Equality ignores mirror process state, which is likely intentional for tests focused on files but should be understood.

Test signals: serialize/deserialize with filled and empty mirror slots, sequence cleanup behavior, duplicate sequence acquisition returning inserted=false, concurrent slot acquisition/free, and relink failures removing bad session files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/Session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFile.cpp -->
## sources/distributed-fs/beegfs/meta/source/session/SessionFile.cpp

Purpose: implements equality and recovery relinking for a single open file session.

Important functions: `operator==` compares access flags, session ID, entry info, and async cleanup marker. `relinkInode` reopens the file through `MetaStore::openFile` with access-check bypass and stores the resulting `MetaFileHandle`.

Control flow: during session recovery, `SessionFileStore::relinkInodes` calls `SessionFile::relinkInode`. On success the in-memory handle is restored; on failure an error is logged and the session file can be removed by the caller.

State and persistence behavior: serialized `SessionFile` state omits the live `MetaFileHandle`; recovery reconstructs it from `EntryInfo` and access flags. `useAsyncCleanup` persists as a marker.

Dependencies and integration points: depends on `Program`, `MetaStore`, and storage file handle types. It integrates session persistence with metadata inode stores.

Risks: bypassing access checks is intentional for recovery, especially files in disposal directories, but it means recovery relies on stored session state being trusted. Equality does not compare the live inode handle.

Test signals: relink success/failure, disposal-directory locked file recovery, equality before/after serialization, and behavior when `EntryInfo` points to missing metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFile.h -->
## sources/distributed-fs/beegfs/meta/source/session/SessionFile.h

Purpose: defines the persisted and live state for one open file within a client session.

Important APIs/types: constructor stores a `MetaFileHandle`, access flags, and `EntryInfo`. Serialization covers `accessFlags`, `sessionID`, `entryInfo`, and `useAsyncCleanup`, but not the live inode handle. Methods expose access flags, session ID, inode handle access/release, async-cleanup marking, entry info, parent-entry update, equality, and `relinkInode`.

Control flow: normal open paths create `SessionFile` with a live inode. Close/removal paths may release the inode and perform cleanup. Recovery creates default `SessionFile`, deserializes fields, then relinks the inode.

State and persistence behavior: `sessionID` is the file-handle ID within a client session. `useAsyncCleanup` marks that a close/removal happened while the file was referenced and cleanup must run after the final release. The inode pointer is process-local and must be rebuilt.

Dependencies and integration points: uses `Path`, `EntryInfo`, `DirInode`, `FileInode`, `MetaFileHandle`, and `MetaStore`.

Risks: `getUseAsyncCleanup`/`setUseAsyncCleanup` are intentionally unsynchronized because the flag only transitions false-to-true; callers must preserve that invariant. `releaseInode` moves the handle out and leaves the object without a valid inode.

Test signals: serialization round trip, async cleanup transition, parent ID updates after rename, move/release of inode handles, and recovery relinking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFileStore.cpp -->
## sources/distributed-fs/beegfs/meta/source/session/SessionFileStore.cpp

Purpose: manages open file sessions within a client session. It assigns file-handle IDs, reference-counts `SessionFile` objects, supports recovery insertion, async cleanup, removal, merge, and equality.

Important functions: `addSession` assigns or accepts a session-file ID. `addAndReferenceRecoverySession` inserts a pre-ID session and immediately references it. `referenceSession`/`releaseSession` manage references. `removeSession` deletes unreferenced sessions or marks referenced ones for async cleanup. `removeAllSessions`, `deleteAllSessions`, `mergeSessionFiles`, `performAsyncCleanup`, `generateNewSessionID`, and `operator==` complete lifecycle support.

Control flow: all map mutations and reference-count changes are protected by `mutex`. `releaseSession` detects the final release of an async-cleanup-marked session, moves cleanup data out while locked, erases/deletes the referencer, then calls `performAsyncCleanup` outside the lock. Cleanup closes the file in `MetaStore` but intentionally does not close storage-server files or unlink disposable files.

State and persistence behavior: the store owns a map from `uint32_t` file-handle ID to `ObjectReferencer<SessionFile*>`. `lastSessionID` is randomized on construction to reduce collisions after metadata-server restart. Serialization/deserialization are in the header; this implementation handles runtime lifecycle.

Dependencies and integration points: uses `Program::getApp()->getMetaStore()` for cleanup, BeeGFS `Logger`, `StringTk`, `Random`, `ObjectReferencer`, and `SessionFile`.

Risks: manual ownership is complex. `mergeSessionFiles` transfers referencer pointers from the source map but does not clear the source map, so source destruction behavior must be known. `removeSession` returns false when async cleanup is deferred, which callers must treat as expected for referenced files. `releaseSession` silently does nothing if the session ID is absent.

Test signals: ID generation avoiding collisions, reference/release counts, remove while referenced causing async cleanup on final release, recovery insertion conflict, remove-all with referenced list, merge duplicate handling, and equality after serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFileStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFileStore.h -->
## sources/distributed-fs/beegfs/meta/source/session/SessionFileStore.h

Purpose: declares the per-session open-file store, its ownership model, serialization format, and recovery helpers.

Important APIs/types: `SessionFileReferencer` is `ObjectReferencer<SessionFile*>`; `SessionFileMap` maps file-handle IDs to referencers. Public APIs include add, recovery add-and-reference, reference, release, remove, remove-all, delete-all, merge, size, relink, serialize/deserialize, and equality.

Control flow: header serialization writes `lastSessionID`, map size, each key, and each `SessionFile`. Deserialization reads those fields, allocates `SessionFile` objects, inserts referencers, and cleans up the current object on per-element failure. `relinkInodes` iterates session files and erases those whose `SessionFile::relinkInode` fails.

State and persistence behavior: `lastSessionID` and all `SessionFile` records are persisted as part of `Session`. Live reference counts are not serialized. Constructor randomizes `lastSessionID`.

Dependencies and integration points: friends `SessionStore` so session-store serialization can inspect nested maps for lock-state persistence. Depends on `MetaStore` through relink declarations, `Random`, `Mutex`, and `ObjectReferencer`.

Risks: `getSessionMap` exposes the internal map to friend/merge code. Deserialization inserts without duplicate checks inside the same serialized stream. Relink erases bad files but leaves the overall result false for caller logging/removal decisions.

Test signals: malformed deserialization cleanup, duplicate serialized keys, relink erasure, `lastSessionID` preservation, and serialization ordering stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionFileStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionStore.cpp -->
## sources/distributed-fs/beegfs/meta/source/session/SessionStore.cpp

Purpose: manages all client sessions for a metadata server, including persistence to disk, recovery, mirror/session synchronization, open-file cleanup, and file-inode lock-state save/restore.

Important functions: `referenceSession`, `releaseSession`, `syncSessions`, `getAllSessionIDs`, `serialize`, `deserialize`, `deserializeLockStates`, `deserializeFromBuf`, `loadFromFile`, `serializeToBuf`, `saveToFile`, `clear`, `removeSessionUnlocked`, and `operator==`. The file format starts with `SESSION_FORMAT_HEADER` and `SESSION_FORMAT_VERSION`.

Control flow: `referenceSession` optionally creates a session and returns a referenced object. `syncSessions` compares sorted current sessions with a sorted master node list, removing sessions not present and reporting referenced unremovable sessions. Serialization writes sessions first, then a placeholder count and deduplicated file-inode lock states collected from all open session files. `serializeToBuf` does a sizing pass and a writing pass. Loading reads the file into memory under the store mutex, deserializes sessions, relinks open inodes, then restores inode lock states.

State and persistence behavior: session maps are persisted to a session file, including each session's files and mirror process state. Live object references are not persisted. File inode lock state is separately serialized once per unique inode. Recovery relinks inodes through `MetaStore` before applying lock states. `clear` removes sessions and closes open files but intentionally avoids unlinking disposed files or storage-server chunks during mirror resync secondary cleanup.

Dependencies and integration points: uses `Program::getApp()` for `MetaStore`, POSIX file I/O, BeeGFS serialization, `ObjectReferencer`, `NodeHandle` master lists, and `EntryLockStore`.

Risks: `loadFromFile` returns false on empty file without closing the opened fd because it returns before `err_stat`; this is a descriptor leak in that branch. `clear` logs a referenced-session error using `sessionIt->first` after the iterator was post-incremented, which can report the wrong ID or risk end-iterator use. `deserializeLockStates` dereferences `inode` after `metaStore.referenceFile(&info)` without checking `referenceRes`/null, so corrupt or stale lock-state entries can crash. `saveToFile` truncates the target before serialization succeeds, so allocation/serialization failure can destroy the previous session file.

Test signals: round-trip session persistence with lock states, malformed header/version, empty session file descriptor behavior, missing inode in lock-state restore, duplicate inode lock-state deduplication, syncSessions with referenced/unreferenced sessions, and save failure after truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionStore.h -->
## sources/distributed-fs/beegfs/meta/source/session/SessionStore.h

Purpose: declares the top-level client session store and embeds the `EntryLockStore` used to serialize mirrored metadata operations.

Important APIs/types: `SessionReferencer` is `ObjectReferencer<Session*>`; `SessionMap` maps `NumNodeID` to referencers. Public APIs handle session reference/release, synchronization with management node lists, listing IDs, size, serialization/deserialization, file load/save, clear, entry-lock-store access, and equality.

Control flow: callers reference sessions by client node ID and must release them. `getEntryLockStore` exposes the embedded lock store to mirrored message handlers. Private helpers add/remove sessions and relink inodes after deserialization.

State and persistence behavior: `sessions` is process-local but serializable through `SessionStore.cpp`. `entryLockStore` is not persisted; it is runtime synchronization state only. `relinkInodes` removes sessions that become empty after failed file relinks.

Dependencies and integration points: depends on `Node`, `ObjectReferencer`, `Mutex`, `EntryLockStore`, and `Session`. `App` owns normal and mirrored instances of this class.

Risks: raw `Session*` returned from `referenceSession` requires strict release discipline. `relinkInodes` erases map entries without deleting referencers in the shown code path, which should be reviewed in context for ownership leaks if relink failure occurs.

Test signals: reference/release discipline, relink failure removal, entry-lock-store access by mirrored messages, equality, and load/save behavior through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/session/SessionStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DentryStoreData.h -->
## sources/distributed-fs/beegfs/meta/source/storage/DentryStoreData.h

Purpose: defines the compact data fields stored on disk for a directory entry and the feature flags that describe dentry/inode encoding.

Important APIs/types: feature flags include `DENTRY_FEATURE_INODE_INLINE`, `DENTRY_FEATURE_IS_FILEINODE`, deprecated `DENTRY_FEATURE_MIRRORED`, `DENTRY_FEATURE_BUDDYMIRRORED`, and `DENTRY_FEATURE_32BITIDS`. `DentryStoreData` stores `entryID`, `entryType`, `ownerNodeID`, and `dentryFeatureFlags`, with protected setters/getters used by friend classes.

Control flow: `DirEntry`, `DiskMetaData`, and `FileInode` mutate and serialize this data. Constructors initialize invalid/zero defaults or full entry metadata.

State and persistence behavior: this is persistent metadata. Comments warn that adding flags requires updating `DiskMetaData::getSupportedDentryFeatureFlags()`.

Dependencies and integration points: depends on storage definitions for `DirEntryType` and `NumNodeID`. It is embedded in `DirEntry` and used by `DiskMetaData` versioned serialization.

Risks: `setDentryFeatureFlags(unsigned)` truncates to `uint16_t`, so new flags must stay within 16 bits. Friend-heavy access means invariants are maintained by surrounding classes rather than this data holder.

Test signals: feature-flag serialization compatibility, 32-bit/modern node ID handling, buddy-mirror flag propagation, and unsupported flag rejection in `DiskMetaData`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DentryStoreData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntry.cpp -->
## sources/distributed-fs/beegfs/meta/source/storage/DirEntry.cpp

Purpose: implements dentry persistence, update, removal, loading, type probing, inode extraction, and initial storage for BeeGFS metadata directory entries.

Important functions: `storeInitialDirEntryID`, `storeInitialDirEntryName`, `storeUpdatedDirEntryBuf*`, `storeUpdatedDirEntry`, `storeUpdatedInode`, `removeDirEntryFile`, `removeDirEntryName`, `removeDirEntryID`, `removeBusyFile`, `loadFromFileName`, `loadFromID`, `loadFromFile*`, `loadEntryTypeFromFile*`, `createFromFile`, `createInodeByID`, and `storeInitialDirEntry`.

Control flow: initial storage first creates an entry-by-ID file containing serialized dentry metadata, then hard-links it to the user-visible entry-by-name. For directories or non-inlined inodes, the ID file is unlinked after the name link is created. Updates serialize through `DiskMetaData` and write either to xattr `META_XATTR_NAME` or file contents based on config. Loads mirror that choice. Removal deletes name and/or ID paths; busy inlined-file removal moves the ID file into the inode hash directory, links it into disposal, and deletes the visible dentry as requested.

State and persistence behavior: dentry metadata can live either in extended attributes or file contents. Inlined file inode data is embedded in the dentry metadata; non-inlined inodes are represented by separate inode files. Buddy-mirrored dentries record changes in the current `BuddyResyncer` changeset as dentry or inode modifications/deletions. Empty dentry files can be self-healed by removal if configured.

Dependencies and integration points: depends on `Program` for config and app paths, `MetaStorageTk` path builders, `DiskMetaData` serialization, `FileInode`, `BuddyResyncer`, POSIX link/unlink/rename/xattr I/O, and disposal directories from `App`.

Risks: `storeUpdatedDirEntry` writes to `dirEntryPath + "/" + name` despite comments warning never to update through entry-name paths except fsck; this should be reconciled with call-site expectations. Initial storage is not rename-atomic and compensates manually on failures. `storeUpdatedDirEntryBufAsContents` uses in-place writes and truncation, so a crash during update can leave partial metadata. Type probing reads a single byte without full validation. Busy-file removal ignores errors from disposal linking. Xattr and file-content paths have separate error behavior and self-healing logic.

Test signals: create/link rollback on `EEXIST` and write failure, xattr and contents modes, empty-file self-heal, busy inlined inode unlink, buddy-resync changeset entries, load invalid/corrupt serialized dentries, type probing, and crash/partial-write recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntry.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntry.h -->
## sources/distributed-fs/beegfs/meta/source/storage/DirEntry.h

Purpose: declares the `DirEntry` class, which represents a directory entry copy containing user-visible name, on-disk dentry metadata, and optional inlined file-inode data.

Important APIs/types: constants define unlink modes for ID, filename, or both. Constructors create initialized entries or name-only load targets. Static APIs load/create entries from files and remove file/dir dentries. Mutators include `setOwnerNodeID`, `setFileInodeData`, buddy-mirror flag setters, dentry feature flag mutation, and `unsetInodeInlined`. Accessors expose entry ID, name, type, owner, feature flags, `EntryInfo`, and `FileInodeStoreData`. Serialization delegates to `DiskMetaData`.

Control flow: callers generally load a `DirEntry` copy, mutate it, and store it back; instances are not shared and have no internal mutex. `removeFileDentry` deletes by name first and only removes the ID file after successful name unlink to avoid racing with rename. `removeDirDentry` removes only the name path.

State and persistence behavior: persistent data is in `DentryStoreData` and optional `FileInodeStoreData`. `getEntryInfo` maps dentry flags to `ENTRYINFO_FEATURE_INLINED` and `ENTRYINFO_FEATURE_BUDDYMIRRORED`. Owner-node updates are disallowed for inlined inodes because ownership is stored in inode data instead.

Dependencies and integration points: friends `MetaStore`, `DirEntryStore`, `DirInode`, `FileInode`, debug and recreate message handlers. Depends on `StorageTkEx`, `DiskMetaData`, `MetadataEx`, and `FileInodeStoreData`.

Risks: no synchronization because dentries are copied per caller; correctness relies on external directory/inode locks. Friend classes can bypass encapsulation. Feature flags must remain consistent with serialized inode data; mismatches can break recovery or fsck.

Test signals: `EntryInfo` flag propagation, owner update rejection for inlined inode, unlink flag combinations, serialize/deserialize through `DiskMetaData`, hardlink/non-inlined conversion, and buddy-mirror flag inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntry.h -->
