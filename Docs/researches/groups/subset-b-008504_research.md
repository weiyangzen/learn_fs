# subset-b-008504 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/serialize.h -->
## sources/storage-engines/foundationdb/flow/include/flow/serialize.h

### Purpose
This header is Flow's core serialization interface. It defines the generic `serializer`, `save`, and `load` dispatch path, binary-serializable trait specializations, STL/container serialization overloads, protocol-version framing helpers, binary archive implementations, packet-buffer writing, and object-serializer integration. It is on the wire-format boundary for network messages, persistent encoded values, object serializer support, and tuple-style key serialization helpers.

### Important APIs, Types, and Functions
Key template APIs are `is_binary_serializable<T>`, `BINARY_SERIALIZABLE(T)`, `Serializer<Archive, T>`, `save`, `load`, `operator<<`, `operator>>`, and variadic `serializer`. `scalar_traits<ProtocolVersion>` stores a protocol version as its `versionWithFlags()` `uint64_t`. Container overloads cover `std::string`, `std::vector`, `std::deque`, `std::array`, `std::set`, `std::map`, `boost::container::flat_map`, `std::unordered_set` file identifiers, and `std::variant`. Version option types are `_IncludeVersion`, `_AssumeVersion`, and `_Unversioned`, with helpers `IncludeVersion`, `AssumeVersion`, and `Unversioned`.

Archive implementations include `BinaryWriter`, `OverWriter`, `_Reader<Impl>`, `ArenaReader`, and `BinaryReader`. Network output support is provided by `SplitBuffer`, `SendBuffer`, `PacketBuffer`, `PacketWriter`, `ISerializeSource`, `MakeSerializeSource`, and `SerializeSource<T>`. `PacketBuffer::markForWipe` and `PacketWriter::packetWriterMarkForWipe` integrate sensitive-data wiping when the relevant knob is enabled.

### Control Flow
Generic serialization resolves through `Serializer<Archive, T>::serialize`; by default it calls `t.serialize(ar)`, while binary and enum specializations use `serializeBinaryItem`. Variadic `serializer` saves or loads arguments in order and statically enforces "appears last" properties, notably for Arena-like trailing parameters. Versioned writers call `vo.write(*this)` in the constructor; readers call `vo.read(*this)` and then may initialize `ObjectReader`/`ArenaObjectReader` when the protocol version carries the object-serializer flag. Container loads read a length, clear existing state, reserve where possible, and deserialize each element in order. `PacketWriter` writes into the current `PacketBuffer` until it crosses the boundary, then allocates/chains another buffer via private boundary methods.

### State and Persistence Behavior
The file defines durable binary layout conventions: integer lengths are serialized as `int` or `int32_t`, variants store a `uint8_t` index, binary items are raw copied according to host ABI assumptions used by Flow, and protocol version inclusion determines how future readers interpret the stream. `BinaryWriter` stores bytes in an `Arena` and can materialize a `Standalone<StringRef>` or arena-owned `StringRef`. `BinaryReader` and `ArenaReader` maintain cursor state, optional checkpoint/rewind state, and an arena for copied reads. `PacketBuffer` is reference counted and can zero a contiguous sensitive range before freeing memory.

### Dependencies and Integration Points
The header depends on Flow's `Arena`, `Error`, `FastAlloc`, `FileIdentifier`, `ObjectSerializer`, `ProtocolVersion`, and `network` facilities. It integrates with `TraceEvent` for invalid/future protocol versions and Valgrind undefined-memory checks. `g_network` is used for packet enqueue timing. `ObjectWriter` and `ObjectReader` are the integration point for file-identifier-aware object serialization; `HasFileIdentifier<T>` controls whether that path is taken.

### Risks
Wire compatibility is the major risk. Changing trait specializations, container ordering, length widths, or protocol-version handling can break mixed-version clusters or persistent data. Binary serialization transmits host-layout bytes for approved scalar types, so adding non-packed structs to `BINARY_SERIALIZABLE` would risk padding and undefined bytes. Several loads trust serialized lengths enough to reserve memory; malformed input paths rely on archive assertions and surrounding validation. Variant indices are limited to `uint8_t`, and `loadVariant` asserts on invalid indexes. Packet buffer wiping merges ranges into a contiguous union, which is conservative for wiping but may wipe more than the exact sensitive spans.

### Test Signals
Relevant tests should round-trip all supported containers, enums, `ProtocolVersion`, object-serializer-flagged payloads, and versioned/unversioned archives. Compatibility tests should decode old serialized bytes with current readers and reject invalid/future protocol versions. Packet tests should exercise boundary-crossing writes, `SplitBuffer` overwrite paths, reference counting, and sensitive-data wipe behavior. Valgrind or sanitizer runs are useful for catching undefined data sent through `serializeBytes` and raw binary serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/serialize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/singleton.h -->
## sources/storage-engines/foundationdb/flow/include/flow/singleton.h

### Purpose
This header provides `crossbow::singleton`, a policy-based singleton holder originally from the Crossbow code used by FoundationDB. It abstracts allocation, lifetime, and locking policies so a type can be lazily constructed, optionally destroyed at process exit, and accessed through static `instance()` or pointer-like wrapper operators.

### Important APIs, Types, and Functions
Creation policies are `create_static<T>`, `create_using_new<T>`, `create_using_malloc<T>`, and `create_using<T, allocator>`. Lifetime policies are `default_lifetime<T>`, `phoenix_lifetime<T>`, and `infinite_lifetime<T>`, with `lifetime_traits` controlling whether recreation is supported. `no_locking` implements a mutex-like no-op policy. On Windows, `WinLockGuard` and `MUTEX_TYPE` wrap a Win32 `HANDLE`; elsewhere locking defaults to `std::mutex` and `std::lock_guard<Mutex>`. The main template is `singleton<Type, Create, LifetimePolicy, Mutex>`.

### Control Flow
`singleton::instance()` performs lazy double-checked initialization. If `instance_` is null, it acquires `mutex_`, checks again, handles dead-reference state, creates the object through `Create::create()`, and registers `destroy()` through the selected lifetime policy. `destroy()` calls `Create::destroy(instance_)`, nulls the pointer, and marks `destroyed_`. `destroy_instance()` explicitly destroys the object under lock and warns that it must not be called while multithreaded. Operator overloads call `instance()` on demand and return pointer/reference access to the stored object.

### State and Persistence Behavior
All state is process-local static template state: `destroyed_`, `instance_`, and `mutex_`. No persisted state is written. `default_lifetime` uses `std::atexit`, so destruction order relative to other global state matters. `phoenix_lifetime` permits recreation after destruction if the creation policy supports it; `infinite_lifetime` intentionally never schedules destruction.

### Dependencies and Integration Points
The header uses the C++ standard library for allocation, mutexes, assertions, and `std::atexit`. On Windows it depends on `Windows.h` and `std::system_error`. It is isolated under namespace `crossbow` and can be included by any component that wants a configurable singleton rather than function-local static construction.

### Risks
The double-checked locking pattern depends on correct static pointer visibility and may be less robust than C++11 function-local statics. Windows `WinLockGuard` creates a mutex in its constructor every time it is used and stores it through the reference, which is unusual and can leak handles. `destroy_instance()` is explicitly unsafe under concurrent use. `create_static` uses a custom union for alignment and should be revisited if used with over-aligned types. Dead-reference handling can throw under `default_lifetime`.

### Test Signals
Unit tests should cover one-time construction, explicit destruction, post-destruction access under each lifetime policy, custom allocator creation/destruction, and no-locking use in single-threaded contexts. Threaded tests should stress concurrent `instance()` calls and confirm only one object is constructed. Windows builds need coverage for the `WinLockGuard` branch.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/singleton.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/sse2neon.h -->
## sources/storage-engines/foundationdb/flow/include/flow/sse2neon.h

### Purpose
This vendored header is a translation layer from Intel SSE/SSE2/SSSE3/SSE4/AES-style intrinsics to Arm NEON intrinsics. It lets code written against `_mm_*`, `__m128`, and `__m128i` compile on Arm/AArch64 without rewriting call sites.

### Important APIs, Types, and Functions
The header defines `_MM_SHUFFLE`, `__constrange`, `__m64`, `__m128`, `__m128i`, `SIMDVec`, many `vreinterpretq_*` compatibility macros, and hundreds of `_mm_*` functions/macros. Covered families include prefetch, set/get, load/store, logic, shuffle/permute, shifts, masks, arithmetic, saturated arithmetic, horizontal operations, comparisons, conversions, packing/unpacking, extraction/insertion, carry-less multiply, AES round support, streaming fences, cache flush stubs, and aligned allocation (`_mm_malloc`, `_mm_free`).

### Control Flow
Most intrinsics are `FORCE_INLINE` wrappers that reinterpret x86 vector types as NEON lane types, call one or more NEON intrinsics, then reinterpret the result back. Immediate-sensitive operations such as `_mm_shuffle_ps`, `_mm_shuffle_epi32`, shifts, alignment, extract, and insert are macros because compilers require literal lane/immediate values. Several implementations branch on `__clang__`, `__aarch64__`, `__GNUC__`, and `__ARM_FEATURE_CRYPTO` to choose compiler builtins, AArch64 lane operations, inline assembly, or fallback sequences. Crypto support chooses hardware polynomial/AES intrinsics when available and software NEON polyfills otherwise.

### State and Persistence Behavior
The header has no durable state. Runtime-visible state is limited to stack temporaries and static lookup tables in AES fallback code. It does affect ABI and code generation by defining x86 intrinsic type names as NEON vector types and by pushing/popping `FORCE_INLINE` and `ALIGN_STRUCT` macros around its contents.

### Dependencies and Integration Points
It depends on `<arm_neon.h>`, compiler vector extensions, `stdint.h`, `stdlib.h`, and POSIX `posix_memalign` for aligned allocation. It is an external project imported into the Flow include tree; FoundationDB Arm builds can include it in code paths that otherwise use Intel intrinsics.

### Risks
Semantic mismatches are the central risk. Floating-point rounding, reciprocal/square-root approximations, NaN comparisons, saturated arithmetic, immediate handling, endian assumptions, alignment behavior, and cache/fence semantics may differ from real SSE. Some comments call out approximation or limitations, such as Armv7 round-to-even limitations and `_mm_clflush` being a no-op. Macro implementations can evaluate arguments in expression contexts and depend on GNU statement expressions. Crypto fallbacks are performance- and correctness-sensitive. Because this file is vendored, local changes can diverge from upstream `sse2neon` behavior.

### Test Signals
Best tests compare outputs against native SSE on x86 for representative vectors, including edge cases for NaN, signed overflow, saturation, rounding, masks, shuffle immediates, AES/carry-less multiply, and unaligned loads. Build coverage should include Clang/GCC, Armv7 if supported, AArch64, with and without crypto extensions. Performance tests are appropriate for hot vector code that depends on approximate reciprocal/sqrt or crypto paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/sse2neon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift.h

### Purpose
This is a compact umbrella header for Flow's Swift interop surface. It pulls in Swift support annotations, Swift ABI task definitions, and Flow protocol-version context, then declares small C++ APIs Swift code can call to interact with the Flow network.

### Important APIs, Types, and Functions
The header includes `swift_support.h`, `swift/ABI/Task.h`, and `flow/ProtocolVersion.h`. It declares `_tid()` as an inline wrapper around `pthread_self()`, `flow_gNetwork_now()`, `flow_gNetwork_delay(double seconds, TaskPriority taskID)`, `JobDelay` as nanoseconds, and `ExecutorRef` with `Identity`, `Implementation`, and `ExecutorRef::generic()`.

### Control Flow
The only implemented control flow is `_tid()` returning the current pthread id and `ExecutorRef::generic()` constructing a null identity/zero implementation executor. The Flow network functions are declarations whose behavior is supplied by implementation files. Swift concurrency hook code later uses `ExecutorRef` when running Swift jobs on a generic executor.

### State and Persistence Behavior
No persistent state is stored. `ExecutorRef` is a by-value ABI carrier for Swift executor identity/implementation bits. `flow_gNetwork_*` declarations imply access to global Flow network state, but this header does not own it.

### Dependencies and Integration Points
This header is an integration point between Flow futures/networking, Swift ABI job structures, and Swift-generated code. It depends on pthreads transitively for `_tid`, Swift ABI declarations, and Flow `Future<Void>`/`TaskPriority` declarations from included headers.

### Risks
The header is ABI-facing: changing `ExecutorRef` layout or function signatures can break Swift/C++ interop. `TaskPriority` is forward-declared as an enum class and must match included Flow definitions in translation units. Because `Future<class Void>` appears in a declaration, include ordering must provide compatible Flow future declarations before use in implementation.

### Test Signals
Swift-enabled builds should compile generated Swift module headers that include this file. Runtime smoke tests should call `flow_gNetwork_now`, await `flow_gNetwork_delay`, and run jobs with `ExecutorRef::generic()` through the hook layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/MetadataValues.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/MetadataValues.h

### Purpose
This vendored Swift ABI header defines target-independent metadata constants and flag wrappers needed by Flow's embedded Swift concurrency interop. It mirrors selected Swift runtime/compiler ABI structures without pulling in the full Swift runtime headers.

### Important APIs, Types, and Functions
It defines ABI size constants such as `NumWords_ValueBuffer`, `NumWords_AsyncTask`, `NumWords_TaskGroup`, and `NumBytes_UniqueHash`; forward declarations for `InProcess`, `TargetMetadata`, and `Metadata`; enums `JobKind`, `JobPriority`, `TaskOptionRecordKind`, and `ContinuationStatus`; helper `descendingPriorityOrder`; and flag wrapper classes `JobFlags` and `AccessibleFunctionFlags`. `JobFlags` exposes fields for job kind and priority plus task-specific flags such as child task, future, group child, and async-let task.

### Control Flow
The header has minimal runtime control flow. `descendingPriorityOrder` returns `0`, `-1`, or `1` to order higher priority values first. `JobFlags` operations are inherited from `FlagSet`: constructors set kind and priority, accessors read/write packed fields, and flag accessors manipulate individual bits.

### State and Persistence Behavior
No state is persisted. The important "state" is bit-level ABI layout: `JobFlags` uses a `uint32_t` with kind in bits 0-7, priority in bits 8-15, and task flags in bits 24-28. These values must stay aligned with the Swift runtime ABI expected by compiled Swift code.

### Dependencies and Integration Points
It depends on `flow/swift/Basic/FlagSet.h` plus standard integer headers. `flow/swift/ABI/Task.h` consumes `JobFlags`, `JobPriority`, and `JobKind`. Flow's Swift concurrency hooks inspect `swift::Job` priority/kind through these definitions.

### Risks
Any drift from the Swift ABI version used by the compiler/runtime can corrupt job scheduling behavior. The flag macros rely on valid field widths and values; debug `assert` catches out-of-range fields only when assertions are enabled. `JobPriority` numeric values are copied from Dispatch QoS and must be mapped carefully to Flow priorities.

### Test Signals
Swift-enabled ABI tests should validate `sizeof`, alignment, and field offsets against the Swift runtime version in use. Unit tests for `JobFlags` should verify opaque bit patterns for kind, priority, and task flags. Scheduling tests should confirm priority ordering and Flow priority conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/MetadataValues.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/Task.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/Task.h

### Purpose
This Swift ABI header defines the schedulable `swift::Job` layout used by Flow's Swift concurrency hooks. It supplies enough of the Swift runtime task object layout for C++ hook code to inspect and run jobs without including the entire Swift runtime object model.

### Important APIs, Types, and Functions
The header defines `NumWords_HeapObject = 2` and class `swift::Job`, aligned to `2 * alignof(void*)`. `Job` contains fake heap-object storage, `SchedulerPrivate[2]`, `JobFlags Flags`, `uint32_t Id`, `void* Voucher`, and `void* Reserved`. It exposes scheduler-private indexes such as `NextWaitingTaskIndex`, `DispatchLinkageIndex`, and `DispatchQueueIndex`, plus `isAsyncTask()` and `getPriority()`.

### Control Flow
There is no complex control flow. Methods delegate directly to `Flags.isAsyncTask()` and `Flags.getPriority()`. The enum constants compute dispatch-linkage indexes based on pointer and int sizes so layout matches Dispatch expectations on 32-bit and 64-bit targets.

### State and Persistence Behavior
`Job` represents runtime task state owned by Swift. The C++ structure must match the memory layout Swift uses for jobs. Fields are not persisted, but scheduler-private pointers and flags are live runtime coordination state between Swift's runtime, Dispatch, and Flow's network executor hooks.

### Dependencies and Integration Points
The file includes `MetadataValues.h` for `JobFlags` and `JobPriority`. It is consumed by `swift.h` and `swift_concurrency_hooks.h`, especially declarations for hook callbacks and `swift_job_run`.

### Risks
Layout drift is the main risk. Adding, removing, or reordering fields would make Flow call into Swift jobs with incorrect offsets. The fake heap-object storage intentionally avoids pulling in full Swift `HeapObject`; that keeps dependencies small but requires ABI vigilance. Voucher handling is stubbed for non-Darwin platforms.

### Test Signals
Swift interop tests should verify `sizeof(swift::Job)`, alignment, field offsets, and priority extraction against the active Swift runtime. Runtime tests should enqueue jobs through Flow hooks and confirm `swift_job_run` receives a valid job and executor.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/Task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift/Basic/FlagSet.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift/Basic/FlagSet.h

### Purpose
This vendored Swift helper defines `swift::FlagSet<IntType>`, a base class for strongly typed wrappers around packed integer bitfields. Flow uses it for Swift ABI flag types such as `JobFlags` and `AccessibleFunctionFlags`.

### Important APIs, Types, and Functions
`FlagSet` stores an integral `Bits` value and provides protected helpers `lowMaskFor`, `maskFor`, `getFlag`, `setFlag`, `getField`, and `setField`. It defines macros `FLAGSET_DEFINE_FLAG_ACCESSORS`, `FLAGSET_DEFINE_FIELD_ACCESSORS`, and `FLAGSET_DEFINE_EQUALITY` for subclasses to expose typed accessors while preventing arbitrary cross-type comparisons. Public `getOpaqueValue()` returns the raw integer.

### Control Flow
Flag reads mask and test bits. Flag writes set or clear a single-bit mask. Field reads shift and mask a range. Field writes assert the value fits, clear the target range, and OR in the shifted value. The macro-generated accessors forward to these template helpers.

### State and Persistence Behavior
The only state is the in-memory integer bitset. There is no persistence, but consumers may treat `getOpaqueValue()` as ABI-significant data. Because the helper uses bit positions directly, subclass definitions determine durable ABI layout.

### Dependencies and Integration Points
It depends on `<type_traits>` and `<assert.h>`. `MetadataValues.h` derives Swift ABI flag wrappers from it. Any new Swift ABI-compatible flag type can reuse the macros.

### Risks
`lowMaskFor` uses `IntType((1 << BitWidth) - 1)`, so very wide fields can overflow the intermediate `int` before conversion. Current users use small widths, but this is a constraint for future use. Range validation is only an `assert`, so release builds can silently truncate or overlap if callers pass invalid values. The macros are intentionally defined inside the class body but become preprocessor globals after inclusion.

### Test Signals
Tests should instantiate representative flag subclasses, verify raw bit patterns, equality macro behavior, field overwrite semantics, and out-of-range assertions in debug builds. Static analysis should watch for future `BitWidth` values that approach or exceed native `int` width.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift/Basic/FlagSet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_concurrency_hooks.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift_concurrency_hooks.h

### Purpose
This header exposes the C/C++ declarations and inline installers that let Flow take over Swift global executor enqueueing. It bridges Swift runtime hook variables to Net2 or simulator scheduling so Swift async jobs can be run on Flow's event loop.

### Important APIs, Types, and Functions
The file defines Swift compiler/visibility/calling-convention macros such as `SWIFT_READONLY`, `SWIFT_RUNTIME_EXPORT`, `SWIFT_EXPORT_FROM`, `SWIFT_CC(swift)`, `SWIFT_CONTEXT`, and related attributes. It declares Swift runtime hook function-pointer variables: `swift_task_enqueueGlobal_hook`, `swift_task_enqueueGlobalWithDelay_hook`, `swift_task_enqueueGlobalWithDeadline_hook`, and `swift_task_enqueueMainExecutor_hook`, plus `swift_job_run`. Flow-specific hook implementations are declared as `net2_enqueueGlobal_hook_impl` and `sim2_enqueueGlobal_hook_impl`. Inline helpers are `installSwiftConcurrencyHooks`, `newNet2ThenInstallSwiftConcurrencyHooks`, and `globalNetworkRun`.

### Control Flow
Preprocessor flow selects attributes for Mach-O/WASI, ELF, Cygwin, or PE/COFF and checks which Swift libraries are being exported. At runtime, `installSwiftConcurrencyHooks` assigns Swift's global enqueue hook to simulator or Net2 implementation when `WITH_SWIFT` is enabled; otherwise it asserts. `newNet2ThenInstallSwiftConcurrencyHooks` creates `TLSConfig`, initializes `g_network` through `_swift_newNet2`, and installs Net2 hooks. `globalNetworkRun` blocks in `g_network->run()`.

### State and Persistence Behavior
The header mutates process-global Swift runtime hook variables and Flow's global `g_network` pointer. There is no persisted data. Hook installation is process-wide and should be treated as singleton runtime state; installing the wrong hook changes how every Swift async task in the process is scheduled.

### Dependencies and Integration Points
It depends on `swift.h`, `swift/ABI/Task.h`, `flow/AsioReactor.h`, and `flow/TLSConfig.h`. It must match Swift runtime exported symbol names and calling conventions. It integrates Flow's Net2 reactor, simulator scheduling, and Swift `swift_job_run` with an `ExecutorRef`.

### Risks
ABI/calling-convention mismatch can crash immediately because hook functions use Swift calling conventions. Visibility macros must be right for each platform or runtime hook symbols may fail to link. Hook globals are nullable/non-null annotated but not protected by synchronization here. `newNet2ThenInstallSwiftConcurrencyHooks` allocates `TLSConfig` and initializes global network state inline, so repeated calls or calls after another network is installed are risky. Non-Swift builds assert if installation is attempted.

### Test Signals
Swift-enabled integration tests should install hooks in simulator and Net2 modes, enqueue immediate, delayed, deadline, and main-executor jobs, and verify they run on the Flow network. Link tests should cover ELF, Mach-O, and Windows visibility branches. Non-Swift builds should compile and assert on accidental installation attempts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_concurrency_hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_future_support.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift_future_support.h

### Purpose
This header supplies Swift-friendly aliases for Flow `Promise`, `Future`, `Callback`, `PromiseStream`, and `FutureStream` template instantiations. It is part of the bridge that lets Swift code work with concrete Flow future types despite limited direct template interop.

### Important APIs, Types, and Functions
Aliases include `PromiseCInt`, `FutureCInt`, `CallbackInt`, `PromiseVoid`, `FutureVoid`, `CallbackVoid`, `PromiseStreamCInt`, `FutureStreamCInt`, `PromiseStreamVoid`, `FutureStreamVoid`, `PromiseStreamFutureVoid`, and `FutureStreamFutureVoid`. It also aliases `FlowCallbackForSwiftContinuationCInt` and `FlowCallbackForSwiftContinuationVoid` to `FlowCallbackForSwiftContinuation<int>` and `FlowCallbackForSwiftContinuation<Void>`.

### Control Flow
The large `FlowCallbackForSwiftContinuation` implementation is commented out, documenting the intended bridge: validate Swift did not copy the callback object, reinterpret a Swift checked-continuation handle passed through `void*`, register with a `Future`, then resume or throw from `fire`/`error`. Active control flow is limited to type alias exposure.

### State and Persistence Behavior
The header itself stores no state. The intended callback bridge would own a Swift continuation wrapper and mutate Flow callback links, but that implementation is not active in this file. The exposed aliases represent runtime future/promise state owned by Flow objects.

### Dependencies and Integration Points
It includes `swift.h`, `flow.h`, `swift_stream_support.h`, `unsafe_swift_compat.h`, `SwiftModules/Flow_CheckedContinuation.h`, pthreads, and integer headers. It depends on `FlowCallbackForSwiftContinuation` being defined elsewhere or generated so the aliases compile.

### Risks
The file is sensitive to Swift/C++ template interop limitations and generated module availability. If `FlowCallbackForSwiftContinuation` is not visible before these aliases are used, builds will fail. The commented bridge shows unsafe `void*` reinterpretation and lifetime assumptions that can cause use-after-free or continuation misuse if revived incorrectly.

### Test Signals
Swift build tests should import the aliases and await `Future<int>`/`Future<Void>` through the intended bridge. Runtime tests should cover successful values, thrown `Error`, cancellation/unwait behavior once implemented, and callback object lifetime across Swift/C++ boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_future_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_stream_support.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift_stream_support.h

### Purpose
This header bridges Flow `FutureStream<T>` callbacks to Swift checked continuations, with concrete support for `int` streams. It exists because Flow streams use `SingleCallback` rather than regular multi-callback futures.

### Important APIs, Types, and Functions
Aliases `PromiseStreamCInt` and `FutureStreamCInt` expose concrete stream types. Template `FlowSingleCallbackForSwiftContinuation<T>` derives from `SingleCallback<T>` and stores a `flow_swift::FlowCheckedContinuation<T>`. Concrete alias `FlowSingleCallbackForSwiftContinuation_CInt` binds it to `int`. `SwiftContinuationSingleCallbackCInt` is annotated `UNSAFE_SWIFT_CXX_IMMORTAL_REF`, derives from `SingleCallback<int>`, and exposes `make`, `addCallbackAndClearTo`, `fire`, `error`, and `unwait`.

### Control Flow
`FlowSingleCallbackForSwiftContinuation<T>::set` checks `this == thisPointer`, reconstructs a Swift continuation wrapper from an opaque pointer-sized value, stores it, and registers the callback with a `FutureStream<T>`. `fire` removes the callback, clears `next`, and resumes the continuation with either a const value or a copied rvalue. `error` removes and resumes throwing. The concrete `SwiftContinuationSingleCallbackCInt` stores raw Swift callback function pointers; its `fire` methods invoke `resumeWithValue`, and `error` logs the error then invokes `resumeWithError`.

### State and Persistence Behavior
State is callback-local and heap-local. `SwiftContinuationSingleCallbackCInt::make` allocates with `new` and the unsafe Swift immortal annotation means Swift will not retain/release in a normal ownership pattern. There is no persistence; lifetime correctness depends on Flow callback removal and external ownership expectations.

### Dependencies and Integration Points
It includes `swift.h`, `flow.h`, `unsafe_swift_compat.h`, `SwiftModules/Flow_CheckedContinuation.h`, pthreads, and integer headers. It integrates Flow `FutureStream`/`SingleCallback` with Swift continuations and generated Swift module glue.

### Risks
This is explicitly unsafe interop. The immortal reference annotation can leak or mask use-after-free. The raw `void*` continuation box and function pointers must remain valid until callback fire/error. `unwait()` is not implemented. `error()` prints to stdout using `printf` rather than Flow tracing and has special logging for end-of-stream. Private inheritance from `SingleCallback<T>` in the template may constrain how Swift/C++ sees the type.

### Test Signals
Tests should cover stream value delivery, end-of-stream error delivery, non-end errors, rvalue fire, callback removal, and object lifetime after `make`. Swift async tests should ensure continuations resume exactly once and that cancellation/unwait gaps are tracked.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_stream_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_support.h -->
## sources/storage-engines/foundationdb/flow/include/flow/swift_support.h

### Purpose
This header centralizes Swift interop annotations and small declarations for Flow C++ types. It lets the same C++ headers compile in Swift-enabled and non-Swift builds by defining Swift attributes under `WITH_SWIFT` and no-op fallbacks otherwise.

### Important APIs, Types, and Functions
Swift-enabled macros include `SWIFT_CXX_IMMORTAL_SINGLETON_TYPE`, `SWIFT_CXX_REF`, `SWIFT_CXX_IMPORT_UNSAFE`, `SWIFT_CXX_IMPORT_OWNED`, `SWIFT_SENDABLE`, `SWIFT_STRINGIFY`, `CONCAT2`, `CONCAT3`, nullability annotation helpers, and `_Nullable`/`_Nonnull` fallbacks when needed. It declares `TaskPriority swift_priority_to_net2(swift::JobPriority p)`. Non-Swift builds define annotation macros as empty and preserve compatibility macros.

### Control Flow
All behavior is preprocessor-controlled. Under `WITH_SWIFT`, the header includes Swift ABI task definitions and Flow task priority definitions, then defines Clang `swift_attr` annotations. It also detects compiler nullability support and either emits `clang assume_nonnull` pragmas or erases nullability markers. Without Swift, the macros collapse to no-ops.

### State and Persistence Behavior
No runtime state is stored. The important effect is compile-time import metadata consumed by Swift's C++ interop importer. Annotations influence ownership, Sendable conformance, reference importing, and unsafe projection behavior.

### Dependencies and Integration Points
Swift-enabled builds depend on `flow/swift/ABI/Task.h` and `flow/TaskPriority.h`. This file is included by `swift.h` and many C++ types that want to expose Swift import behavior without hard requiring Swift support.

### Risks
Wrong annotations can create memory-management bugs in Swift, especially immortal or reference-retained types. The no-op branch can hide Swift-only assumptions until a Swift build is run. `SWIFT_NAME` is only defined in the non-Swift branch here; if users expect it under `WITH_SWIFT`, they must get it from generated Swift headers or another include. Priority conversion must stay aligned with `swift::JobPriority` values.

### Test Signals
Both Swift and non-Swift builds should compile headers that use these macros. Swift import tests should verify annotated C++ types appear with expected ownership and Sendable behavior. Scheduling tests should validate `swift_priority_to_net2` for every `swift::JobPriority`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/swift_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/unactorcompiler.h -->
## sources/storage-engines/foundationdb/flow/include/flow/unactorcompiler.h

### Purpose
This small cleanup header undefines actor compiler macros after actor-generated or actor-aware code has been processed. It prevents Flow actor keywords/macros from leaking into ordinary C++ code.

### Important APIs, Types, and Functions
There are no functions or types. The header conditionally undefines `ACTOR`, `SWIFT_ACTOR`, `state`, `UNCANCELLABLE`, `choose`, and `when` when `NO_INTELLISENSE` is not defined, and always undefines `THIS` and `THIS_ADDR` inside the `!POST_ACTOR_COMPILER` branch. A comment notes that `loop` remains defined.

### Control Flow
All behavior is preprocessor control flow. If `POST_ACTOR_COMPILER` is not defined, the cleanup runs. If `NO_INTELLISENSE` is defined, it preserves some actor macros for IDE parsing while still undefining `THIS` and `THIS_ADDR`.

### State and Persistence Behavior
No runtime state exists. The header mutates preprocessor state for the rest of the translation unit, which is its entire purpose.

### Dependencies and Integration Points
It integrates with FoundationDB's actor compiler and headers that temporarily define actor-language macros. It is usually paired with actor compiler include boundaries to restore normal C++ macro space.

### Risks
Include ordering is the only real risk. Including it too early can remove actor macros before they are needed; including it too late can let macros corrupt unrelated code. Leaving `loop` defined is intentional but still a possible macro collision. IntelliSense-specific branching can differ from real compiler behavior.

### Test Signals
Actor-compiled and non-actor translation units should compile with this header at expected boundaries. Preprocessor tests can verify macros are present before and absent after inclusion, with separate coverage for `NO_INTELLISENSE` and `POST_ACTOR_COMPILER`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/unactorcompiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/unsafe_swift_compat.h -->
## sources/storage-engines/foundationdb/flow/include/flow/unsafe_swift_compat.h

### Purpose
This header defines a single unsafe Swift C++ interop annotation for importing C++ types as immortal Swift reference types. It is used where regular ownership cannot yet be represented safely across the Swift/C++ boundary.

### Important APIs, Types, and Functions
The only public API is `UNSAFE_SWIFT_CXX_IMMORTAL_REF`, which expands to Swift attributes `import_reference`, `retain:immortal`, and `release:immortal`. There are no functions or runtime types.

### Control Flow
There is no runtime control flow. The preprocessor guard defines the macro once, and Swift's importer consumes the attributes when compiling with a compiler that understands `swift_attr`.

### State and Persistence Behavior
No state is stored. The macro changes compile-time ownership semantics: Swift treats annotated C++ objects as references that are never retained or released.

### Dependencies and Integration Points
The macro is used by Swift bridge types such as `SwiftContinuationSingleCallbackCInt` in `swift_stream_support.h`. It complements the safer annotation set in `swift_support.h` but is intentionally separated and named unsafe.

### Risks
The file's own warning is the central risk: incorrect use can cause use-after-free or memory leaks. Because Swift will not manage lifetime, the C++ side must guarantee the object outlives all Swift references or intentionally leak it. There is no non-Swift fallback branch, so compilers that do not accept `swift_attr` must still tolerate the attribute syntax.

### Test Signals
Swift import tests should confirm annotated types appear as references with immortal retain/release behavior. Runtime tests for each annotated type should prove the C++ object outlives Swift use and document any intentional leaks. Static review should be required for every new use of the macro.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/unsafe_swift_compat.h -->
