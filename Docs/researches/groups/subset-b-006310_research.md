# subset-b-006310 research

Grouped research for Rust kernel helper files under `sources/distributed-fs/ceph-client/rust/kernel`. Each section is source-tree-aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/rbtree.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/rbtree.rs

Purpose: provides an owned Rust wrapper around Linux `rb_root`/`rb_node`, exposing map-like red-black-tree operations while preserving kernel allocation and pointer layout. It is generic over ordered keys and values and supports preallocation through `RBTreeNodeReservation` for contexts that cannot sleep while inserting.

Important APIs/types/functions: `RBTree<K,V>` owns the root and drops all nodes in postorder. `try_create_and_insert`, `insert`, `entry`, `find_mut`, `get`, `get_mut`, `remove_node`, `remove`, and lower-bound cursor constructors are the main map APIs. `Cursor` and `CursorMut` provide bidirectional traversal, peeking, and node removal. `Iter`, `IterMut`, and `IntoIterator` expose sorted iteration. `RBTreeNode` owns one boxed `Node`, and `RBTreeNodeReservation` stores uninitialized boxed node memory for later initialization.

Control flow: lookup and insertion walk raw child pointers by comparing keys. Vacant insertion links a node with `rb_link_node` and rebalances with `rb_insert_color`; duplicate insertion replaces with `rb_replace_node`. Removal calls `rb_erase` before converting the raw node back into a `KBox`. Cursor movement delegates to `rb_prev`/`rb_next`, and cursor removal selects the next neighbor first, then the previous one.

State/persistence: state is purely in-memory kernel heap plus embedded C rb links. Ownership of each allocation transfers between `RBTreeNode`, the live tree, and removed/replaced return values. No persistent storage or serialization exists.

Dependencies/integration: depends on `bindings` rbtree functions, `container_of!`, `KBox`, allocator `Flags`, `MaybeUninit`, `NonNull`, and Rust ordering traits. Integrates with locking externally; the tree itself has no internal synchronization.

Risks: all safety rests on rb link pointers always referring to `Node<K,V>::links`, and on no concurrent mutation during iteration/cursor use. Replacement requires equal keys but only call-site lookup enforces that. Iterator raw pointers become invalid if the tree is mutated outside the borrow model through unsafe aliases. `Drop` breaks invariants internally while freeing nodes, so postorder traversal must obtain next before dropping current.

Test signals: extensive doctests cover insertion, replacement, iteration, mutable access, removal, preallocation, reservations, cursors, lower-bound search, and cursor-adjacent removal. Additional stress should cover duplicate keys, drop order of key/value destructors, and lock-protected insertions in non-sleepable contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/rbtree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/regulator.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/regulator.rs

Purpose: wraps Linux regulator consumer APIs for Rust drivers, modeling regulator handles as typestates so enable-reference ownership is reflected by `Regulator<Enabled>` versus `Regulator<Disabled>`.

Important APIs/types/functions: `RegulatorState` is sealed and defines `DISABLE_ON_DROP`; `Enabled` owns an enable refcount, while `Disabled` owns only a regulator reference. `devm_enable` and `devm_enable_optional` provide device-managed one-shot enable helpers. `Regulator<T>` supports `set_voltage`, `get_voltage`, `get_internal`, and internal enable/disable calls. State transitions are `Regulator<Disabled>::try_into_enabled` and `Regulator<Enabled>::try_into_disabled`; failures return `Error<State>` with the original handle for retry. `Voltage` is a transparent microvolt wrapper.

Control flow: acquisition calls `regulator_get`; `Regulator<Enabled>::get` chains disabled acquisition and enable transition. Transitions wrap `self` in `ManuallyDrop` so the old handle is not prematurely dropped while the new typestate is constructed. `Drop` conditionally calls `regulator_disable` based on typestate, then always calls `regulator_put`.

State/persistence: state is a raw `struct regulator *` plus typestate marker. The backing regulator framework maintains global regulator state, enable counts, and voltage configuration; this wrapper persists no state beyond the handle lifetime.

Dependencies/integration: integrates with `Device`, `CStr`, `from_err_ptr`, `to_result`, and C `include/linux/regulator/consumer.h` bindings. Device-managed helpers integrate with devres-managed teardown.

Risks: incorrect typestate conversion would leak or double-release enable counts; `ManuallyDrop` is central to avoiding this. `is_enabled` is implemented only for the sealed `IsEnabled` trait currently implemented for `Disabled`, matching the notion that disabled handles may query actual hardware state. Drop ignores `regulator_disable` errors, as destructors cannot report failure.

Test signals: no local KUnit tests. Doctests document acquisition, voltage set/get, state transitions, retry-on-error, and devm helpers. Runtime validation should use driver probe/remove tests checking enable counts, optional regulator absence, and voltage error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/regulator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/revocable.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/revocable.rs

Purpose: implements `Revocable<T>`, a pinned wrapper whose contents can be made inaccessible and dropped at runtime after RCU readers finish. It lets Rust objects model kernel resources that disappear while references may briefly be in flight.

Important APIs/types/functions: `Revocable::new` pin-initializes an `AtomicBool` availability flag and `Opaque<T>` data. `try_access` takes an RCU read lock and returns `RevocableGuard`; `try_access_with_guard` reuses an existing RCU guard and returns `&T`; `try_access_with` runs a closure under the short-lived guard. Unsafe `access` bypasses revocation checks. `revoke`, unsafe `revoke_nosync`, and `revoke_internal<SYNC>` revoke and drop contents. `RevocableGuard` dereferences to `T` while holding `rcu::Guard`.

Control flow: readers acquire RCU, check `is_available` with relaxed ordering, then dereference data. Revocation atomically swaps availability from true to false, optionally calls `synchronize_rcu`, then drops the object in place. Pinned drop only drops data if it has not already been revoked.

State/persistence: state is in-memory: availability flag plus pinned opaque data. Once revoked, data is dropped exactly once and never reinitialized.

Dependencies/integration: depends on Rust RCU wrappers, kernel `synchronize_rcu`, `Opaque`, pin-init, `PinnedDrop`, and `AtomicBool`. Integrates with subsystems that need revocable, RCU-protected shared objects.

Risks: readers must not sleep while holding `RevocableGuard`, because revocation may wait for RCU grace periods. Relaxed atomics rely on RCU for lifetime, not ordering of data initialization. Unsafe `revoke_nosync` and `access` require external proof that no concurrent users or revocation exist. Double-drop prevention hinges on only one successful `swap(true -> false)` path.

Test signals: doctests cover access before and after `revoke` and explicit RCU-guard access. Additional tests should exercise concurrent readers, repeated revocation returning false, and drop without prior revoke.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/revocable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/safety.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/safety.rs

Purpose: provides `unsafe_precondition_assert!`, a macro for documenting and optionally checking unsafe-function preconditions in debug Rust kernel builds.

Important APIs/types/functions: the exported macro accepts either a condition alone or a condition plus formatted message. Both forms route to an internal arm that calls `core::debug_assert!` with a standardized "unsafe precondition violated" prefix.

Control flow: the macro expands at call sites. With debug assertions enabled it evaluates the condition and panics on violation; otherwise it compiles to the normal `debug_assert!` no-op behavior.

State/persistence: no runtime state and no persistence. It only affects debug-time checks.

Dependencies/integration: uses the kernel prelude formatting macro for message construction and integrates with unsafe APIs as a lightweight guardrail in debug builds.

Risks: it is not a safety mechanism in production configurations where debug assertions are disabled. Callers must still uphold the unsafe contract. Format arguments should avoid side effects because they may not be evaluated in release-like builds.

Test signals: doctest demonstrates guarding an unchecked buffer write. Broader signal comes from compiling unsafe APIs under `CONFIG_RUST_DEBUG_ASSERTIONS` and inducing violations in KUnit or debug-only tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/safety.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/scatterlist.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/scatterlist.rs

Purpose: wraps kernel scatter-gather tables and entries for DMA, supporting borrowed externally managed `sg_table`s and owned Rust-created tables built from vmalloc-backed page iterators.

Important APIs/types/functions: `SGEntry` exposes `dma_address` and `dma_len`. `SGTable<Borrowed>` can be constructed from raw `sg_table *` with `from_raw` and iterated. `Owned<P>` stores a `Devres<DmaMappedSgt>`, `RawSGTable`, and backing pages, with drop order intentionally unmapping DMA before freeing the SG table and pages. `SGTable<Owned<P>>::new` constructs a pinned table from `Device<Bound>`, pages, DMA direction, and flags. `SGTableIter` yields DMA-mapped entries.

Control flow: owned construction collects `struct page *` values from a `VmallocPageIter`, allocates an sg table with `sg_alloc_table_from_pages_segment`, computes max segment from `dma_max_mapping_size`, then maps with `dma_map_sgtable`. Iteration starts at `sgl`, uses `nents`, and advances with `sg_next`. Drops call `dma_unmap_sgtable` and `sg_free_table`.

State/persistence: state is in-memory DMA mapping state associated with a bound device. The backing page owner `P` is held to keep pages alive. No persistent storage exists.

Dependencies/integration: integrates with `Device`, `Devres`, DMA direction/address types, vmalloc page iteration, `ARef<Device>`, allocation flags, and C scatterlist/DMA bindings.

Risks: borrowed `from_raw` requires no concurrent modification and external lifetime validity. Owned construction rejects empty page lists to avoid C-side null dereference. The iterator warns that entries can become unmapped on device unbind despite table borrowing. Drop order is safety-critical. DMA direction and device must match unmap parameters.

Test signals: doctest covers constructing an owned table from `VVec`. Runtime tests should validate empty-buffer rejection, nents iteration boundaries, unmap-on-drop, and device-unbind devres interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/scatterlist.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/security.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/security.rs

Purpose: exposes Rust wrappers for selected Linux Security Module hooks and a managed security-context string returned by secid translation.

Important APIs/types/functions: binder hook wrappers are `binder_set_context_mgr`, `binder_transaction`, `binder_transfer_binder`, and `binder_transfer_file`. `SecurityCtx` owns a `bindings::lsm_context` and provides `from_secid`, `is_empty`, `len`, and `as_bytes`.

Control flow: binder functions pass credential and file raw pointers into corresponding `security_binder_*` hooks and convert integer status with `to_result`. `SecurityCtx::from_secid` zero-initializes an `lsm_context`, calls `security_secid_to_secctx`, and on success stores it. `Drop` releases it with `security_release_secctx`.

State/persistence: `SecurityCtx` temporarily owns kernel-allocated LSM context bytes; release happens on drop. Binder wrappers persist no state.

Dependencies/integration: integrates with `Credential`, `File`, `to_result`, and C LSM bindings from `include/linux/security.h`.

Risks: lifetime correctness relies on `Credential` and `File` shared references guaranteeing live refcounts. `as_bytes` must handle null context pointers for empty contexts because `slice::from_raw_parts` cannot take null even for zero length. Drop must only run for contexts produced by successful `security_secid_to_secctx`.

Test signals: no local tests. Useful validation includes LSM-enabled binder paths, secid conversion success/failure, empty contexts, and ensuring release is called once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/security.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/seq_file.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/seq_file.rs

Purpose: provides a minimal Rust facade over `struct seq_file` for formatted output in procfs/debugfs-style sequential files.

Important APIs/types/functions: `SeqFile` is a transparent wrapper containing `Opaque<bindings::seq_file>` and `NotThreadSafe`. `unsafe from_raw` creates a borrowed wrapper from C. `call_printf` writes `fmt::Arguments` through `seq_printf("%pA")`. The exported `seq_print!` macro mirrors Rust formatting syntax.

Control flow: callers receive a raw seq-file pointer from a C callback, wrap it with `from_raw`, then invoke `seq_print!`, which passes `fmt!` arguments to `call_printf`.

State/persistence: state is the underlying C seq file buffer/cursor managed by the kernel seq-file subsystem. The Rust wrapper owns no buffer.

Dependencies/integration: depends on `bindings::seq_printf`, `fmt`, `CStrExt::as_char_ptr`, `Opaque`, and `NotThreadSafe`. It integrates with kernel virtual file emit paths.

Risks: `from_raw` is unsafe because the caller must guarantee exclusive thread access and valid lifetime. `call_printf` ignores `seq_printf` return behavior; consumers cannot observe truncation/error through this API. The `%pA` format assumes kernel formatting support for Rust `Arguments`.

Test signals: no direct tests. Compile-time macro use and seq-file callback integration tests should verify formatting, truncation behavior, and thread confinement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/seq_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sizes.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sizes.rs

Purpose: exposes common Linux `SZ_*` constants to Rust as `usize` module constants and as typed associated constants for device address-width calculations.

Important APIs/types/functions: the `define_sizes!` macro emits constants from `bindings::SZ_*`, the `SizeConstants` trait, and implementations for `u32`, `u64`, and `usize`. Constants range from `SZ_1K` through `SZ_2G`.

Control flow: all behavior is compile-time macro expansion and constant evaluation. Implementations assert each value fits in the target integer type before casting.

State/persistence: no runtime state.

Dependencies/integration: depends on generated C bindings for `include/linux/sizes.h`. Used by drivers for page arithmetic, MMIO windows, heaps, and hardware address-space sizing.

Risks: constants are only as correct as the C bindings. The typed constants intentionally cover only values fitting in `u32`; adding larger sizes would require revisiting the `u32` implementation. Trait constants require type qualification, which may surprise callers expecting module constants.

Test signals: doctests show module-level `usize` use and typed `u64`/`u32` use. Compile-time assertions are the main safety signal for lossless casts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sizes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/soc.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/soc.rs

Purpose: wraps Linux SoC device registration so Rust drivers can publish SoC identity attributes under `/sys/devices/socX` and keep the backing strings alive for the registration lifetime.

Important APIs/types/functions: `Attributes` contains optional `CString` fields for `machine`, `family`, `revision`, `serial_number`, and `soc_id`. `BuiltAttributes` owns the backing attributes and an opaque `soc_device_attribute` populated with C string pointers. `Registration` is a pinned drop handle whose `new` registers with `soc_device_register` and whose drop unregisters.

Control flow: `Attributes::build` converts optional CStrings to nullable C pointers and stores the owned strings alongside the C attribute struct. `Registration::new` pin-initializes built attributes, passes their mutable pointer to `soc_device_register`, wraps the returned non-null `soc_device`, and unregisters on pinned drop.

State/persistence: state is in-memory registration plus sysfs-visible SoC attributes managed by the kernel. `Registration` lifetime controls visibility.

Dependencies/integration: uses `CString`, `Opaque`, `NonNull`, pin-init, `from_err_ptr`, and C `include/linux/sys_soc.h` bindings.

Risks: pointers inside `soc_device_attribute` must always point into still-owned `CString` buffers. Pinning matters because external kernel code may retain the attribute pointer. Registration returns are both error-pointer checked and null-checked. Dropping unregisters; leaking the handle leaves the SoC device registered.

Test signals: no local tests. Useful tests register sample attributes, inspect sysfs fields, and verify unregister on drop with optional fields omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/soc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/std_vendor.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/std_vendor.rs

Purpose: vendors and adapts standard Rust `dbg!` behavior for the kernel, printing through `pr_info!` instead of standard error.

Important APIs/types/functions: the exported `dbg!` macro supports no-argument location printing, one expression returning the expression value, and multiple expressions returning a tuple. It uses `file!`, `line!`, `column!`, `stringify!`, and `Debug` formatting.

Control flow: single-expression expansion evaluates via `match` to control temporary lifetimes, logs the source location, expression text, and pretty debug value, then returns the moved value. Multi-expression form recursively calls `dbg!` for each expression.

State/persistence: no state except kernel log output.

Dependencies/integration: depends on `pr_info!` and Rust formatting. It is intended for temporary development diagnostics, not committed production logging.

Risks: it moves non-`Copy` inputs just like standard `dbg!`, can leak sensitive data into kernel logs, and always runs in release builds. Output format is not stable.

Test signals: documentation examples describe expression, no-arg, method-call, recursive, and tuple behavior. Practical validation is macro expansion/compile coverage and controlled log output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/std_vendor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/str.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/str.rs

Purpose: provides byte-string, C-string extension, formatting-buffer, boolean-parsing, and owned C string utilities for Rust kernel code.

Important APIs/types/functions: `BStr` is a transparent unsized byte-string wrapper with `len`, `is_empty`, `from_bytes`, `strip_prefix`, display/debug escaping, indexing, and `b_str!`. `CStrExt` adds `from_char_ptr`, mutable unchecked construction, `as_char_ptr`, allocation into `CString`, and ASCII case conversion. `c_str!` builds static `CStr`s. `RawFormatter`, `Formatter`, and `NullTerminatedFormatter` support bounded raw formatting. `kstrtobool` and `kstrtobool_bytes` wrap kernel boolean parsing. `CString` owns a nul-terminated, interior-nul-free `KVec<u8>`.

Control flow: `CString::try_from_fmt` first formats into a counting `RawFormatter`, allocates exact capacity, formats again with bounds checking, increments vector length, then scans for interior nul with `memchr`. Boolean parsing passes either a C string pointer or a small stack nul-terminated byte array to `kstrtobool`.

State/persistence: owned state appears only in `CString`'s vector. Formatters track pointer positions or remaining buffer slices. No persistent storage.

Dependencies/integration: integrates with kernel allocation, `fmt`, C string literals, `bindings::kstrtobool`, `memchr`, and prelude `CStr`.

Risks: unchecked mutable CStr construction and `to_bytes_mut` rely on layout assumptions and caller-maintained nul invariants. `RawFormatter` can advance beyond the buffer by design, so callers must use `Formatter` when overflow is an error. `kstrtobool_bytes` intentionally considers only two input bytes. Formatting arbitrary bytes escapes non-printable/non-ASCII values rather than validating UTF-8.

Test signals: KUnit tests cover CStr UTF-8 conversion failure/success, CStr/BStr display/debug escaping for byte ranges, boolean parsing examples, and formatter behavior through `CString::try_from_fmt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/str.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/str/parse_int.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/str/parse_int.rs

Purpose: implements kernel-style integer parsing for `BStr`, including optional signs and radix prefixes compatible with `kstrtol`/`kstrtoul` conventions.

Important APIs/types/functions: sealed private `FromStrRadix` abstracts per-integer parsing and negation. `strip_radix` detects `0x`, `0o`, `0b`, and leading-zero octal. Public `ParseInt` exposes `from_str`. `impl_parse_int!` implements the trait for signed/unsigned 8-, 16-, 32-, 64-bit and pointer-sized integer types.

Control flow: `from_str` handles a leading `-` by stripping radix from the rest, parsing digits as `u64`, then calling `from_u64_negated`. Non-negative paths strip radix and use the target type's `from_str_radix` after UTF-8 validation. Negation handles signed minimum exactly using two's-complement wrapping.

State/persistence: no state.

Dependencies/integration: uses `BStr`, `core::str::from_utf8`, Rust integer `from_str_radix`, `TryFrom`, and kernel `EINVAL`.

Risks: parsing requires UTF-8 digit bytes; invalid bytes map to `EINVAL`. Leading `0` means octal, so strings like `09` fail. Negative values for unsigned types fail except the implementation's `ABS_MIN == 0` edge maps `-0` to zero. `u64` is chosen because 128-bit integers are not universally available.

Test signals: doctests cover zero, hex, octal, binary, signed negatives, overflow boundaries, and unsigned overflow. Additional tests should include `+` handling, invalid prefixes, and `-0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/str/parse_int.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync.rs

Purpose: is the top-level Rust synchronization module, re-exporting synchronization primitives and defining lockdep class-key utilities for locks.

Important APIs/types/functions: it declares submodules for `arc`, `aref`, `atomic`, `barrier`, `completion`, `condvar`, `lock`, `poll`, `rcu`, `refcount`, and `set_once`. Re-exports include `Arc`, `UniqueArc`, `ARef` indirectly through submodule, `Completion`, mutex/spinlock APIs, global locks, `LockedBy`, `Refcount`, and `SetOnce`. `LockClassKey` wraps `struct lock_class_key`; `static_lock_class!` creates static keys; `optional_name!` supplies explicit or file-line lock names.

Control flow: dynamic lock class keys register through `lockdep_register_key` during pin initialization and unregister in pinned drop. Static keys are initialized in static storage and returned as pinned static references.

State/persistence: lock class keys are kernel lockdep state. Static keys persist for the module/kernel lifetime; dynamic keys persist until dropped.

Dependencies/integration: depends on `Opaque`, pin-init, lockdep C bindings, and all synchronization submodules. Lock constructors consume these keys to participate in lockdep checking.

Risks: dynamic keys must remain pinned while registered. Static keys must never run destructors. Misusing foreign-owned dynamic keys in examples can unregister while a lock still references the key.

Test signals: doctests show dynamic and static key usage with `SpinLock`. Broader validation comes from lockdep runtime checks and compilation of re-exported primitives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/arc.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/arc.rs

Purpose: implements kernel-style `Arc`, `ArcBorrow`, and `UniqueArc`, backed by kernel `Refcount`, without weak references, and with implicitly pinned shared data.

Important APIs/types/functions: `Arc<T>` owns a non-null `ArcInner<T>` pointer containing `Refcount` and data. `Arc::new`, `into_raw`, `from_raw`, `as_ptr`, `as_arc_borrow`, `ptr_eq`, and `into_unique_or_drop` are core APIs. `ForeignOwnable` allows C ownership transfer. `ArcBorrow` is a non-owning borrowed refcounted pointer that can be upgraded to `Arc`. `UniqueArc<T>` represents refcount-one ownership, supports mutable access, uninitialized allocation, init/pin-init flows, and conversion to `Arc`.

Control flow: clone increments the saturated refcount; drop decrements and frees the leaked `KBox` when zero. `into_unique_or_drop` manually decrements; if zero, it restores the count to one and returns a pinned `UniqueArc`, otherwise it drops only this reference. Raw conversions reconstruct `ArcInner` from the data pointer via layout offset calculation.

State/persistence: state is heap allocation and refcount. No weak state exists. `UniqueArc` guarantees mutable access only while refcount remains one.

Dependencies/integration: depends on `KBox`, `Refcount`, `ForeignOwnable`, pin-init traits, `Layout`, `NonNull`, and vendored `Any` downcast support.

Risks: raw pointer APIs require exact one-for-one ownership recovery. Saturating refcounts avoid zero overflow but can leak on pathological overflow. Pinned data means no `get_mut` for shared `Arc`; moving out would violate invariants. `ArcBorrow::from_raw` requires the refcount not reach zero and no `UniqueArc` coexist.

Test signals: doctests cover clone/drop, receiver forms, trait-object coercion, uniqueness conversion, uninitialized initialization, pin conversion, borrow traits, and display/debug forwarding. Additional stress should exercise raw/foreign ownership and concurrent clone/drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/arc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/arc/std_vendor.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/arc/std_vendor.rs

Purpose: vendors the standard-library-style `Arc<dyn Any + Send + Sync>::downcast` operation for this kernel `Arc` implementation.

Important APIs/types/functions: `downcast<T>` checks `Any::is::<T>()` on the trait object and, on success, casts the internal `ArcInner<dyn Any + Send + Sync>` pointer to `ArcInner<T>`, forgets the original `Arc`, and returns `Arc<T>`. On mismatch it returns the original trait-object `Arc` in `Err`.

Control flow: type check first, pointer cast second. The refcount ownership is preserved by forgetting `self` before constructing the new typed `Arc` from the same inner pointer.

State/persistence: no new state; it retypes an existing refcounted allocation.

Dependencies/integration: depends on private `ArcInner`, public `Arc`, and `core::any::Any`. Integrates with trait-object storage using the kernel Arc.

Risks: soundness depends on `Any::is::<T>()` matching the actual data allocation and on `ArcInner<T>` having compatible metadata handling after downcast. Forgetting `self` is required to avoid decrementing the refcount during successful conversion.

Test signals: no local tests. Standard downcast success/failure cases should be compiled for sized concrete types and should verify pointer identity/refcount preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/arc/std_vendor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/aref.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/aref.rs

Purpose: provides `ARef<T>`, an owned Rust pointer for C-style objects that already contain their own reference count, avoiding a second Rust `Arc` allocation.

Important APIs/types/functions: unsafe trait `AlwaysRefCounted` defines `inc_ref` and unsafe `dec_ref`. `ARef<T>` stores `NonNull<T>` and owns one reference count increment. APIs include unsafe `from_raw`, `into_raw`, `Clone`, `Deref`, `From<&T>`, `Drop`, `Unpin`, and equality impls.

Control flow: `From<&T>` and `Clone` increment the object's internal refcount before constructing an owned `ARef`. `Drop` calls `T::dec_ref` for the owned increment. `into_raw` suppresses drop with `ManuallyDrop` and transfers refcount responsibility to the caller.

State/persistence: the state lives in the referenced object, not in `ARef`. `ARef` persists only a non-null pointer and ownership of one reference.

Dependencies/integration: integrates with wrappers around kernel C structs that implement get/put patterns. It uses `NonNull`, `ManuallyDrop`, and Rust trait bounds for thread-safety forwarding.

Risks: `AlwaysRefCounted` is unsafe because implementers must guarantee every instance is refcounted and increments keep memory alive. `from_raw` requires the caller to relinquish an existing increment. After `dec_ref`, the object may be freed and must not be used unless another increment is held.

Test signals: examples demonstrate a minimal implementation and raw round trip. Real tests should use concrete refcounted kernel wrappers to verify get/put balance and clone/drop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/aref.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic.rs

Purpose: exposes Linux Kernel Memory Model-compatible atomics to Rust, intentionally mapping to kernel C atomic/READ_ONCE/WRITE_ONCE semantics rather than Rust's standard atomic memory model.

Important APIs/types/functions: `Atomic<T>` is transparent over `AtomicRepr<T::Repr>`. Unsafe `AtomicType` defines representation compatibility; unsafe `AtomicAdd` defines valid wrapping arithmetic. Methods include `new`, unsafe `from_ptr`, `as_ptr`, `get_mut`, `load`, `store`, `xchg`, `cmpxchg`, `fetch_add`, `fetch_sub`, and `add`. `AtomicFlag` wraps an architecture-appropriate `Flag` for efficient boolean RMW. Raw helpers `atomic_load`, `atomic_store`, `xchg`, and `cmpxchg` work directly on C-side fields.

Control flow: values transmute to representation with `into_repr`, call selected C primitive based on ordering marker type, then transmute back. Load accepts acquire/relaxed; store accepts release/relaxed; exchange and cmpxchg accept all four marker orderings; arithmetic is available for representation types that implement arithmetic ops.

State/persistence: atomic memory is the wrapped value or a borrowed C field. No persistence beyond memory.

Dependencies/integration: depends on `internal` generated atomic traits, `ordering` marker types, predefined implementations, `build_error!`, C bindings, and LKMM.

Risks: `AtomicType` safety is subtle: same size/alignment and round-trip transmutability are required, padding-containing types are excluded, and pointer transfer safety is justified only because dereference remains unsafe. `from_ptr` requires LKMM-race-free concurrent access. Mixed C/Rust atomic use must match ordering expectations.

Test signals: KUnit tests in `predefine.rs` cover loads/stores, acquire-release, xchg, cmpxchg, arithmetic, bool, pointers, and `AtomicFlag`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/internal.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/internal.rs

Purpose: provides the sealed low-level implementation layer that maps Rust atomic representations onto concrete kernel C atomic helper functions.

Important APIs/types/functions: `AtomicImpl` marks supported representation types (`i8`, `i16`, `*const c_void`, `i32`, `i64`) and their arithmetic `Delta`. `AtomicRepr<T>` wraps `UnsafeCell<T>`. Macro families declare and implement `AtomicBasicOps`, `AtomicExchangeOps`, and `AtomicArithmeticOps` for the relevant representation-to-C-helper mappings.

Control flow: `declare_and_impl_atomic_methods!` expands a type map into trait declarations and implementations. Generated methods cast `AtomicRepr::as_ptr()` to the C helper's expected pointer type, then call helpers like `atomic_read`, `atomic64_xchg`, `atomic_i8_read_acquire`, or `atomic_ptr_try_cmpxchg_relaxed`.

State/persistence: state is the underlying `UnsafeCell` memory. The module owns no global state.

Dependencies/integration: depends on generated bindings, paste macros, `UnsafeCell`, `c_void`, and architecture config. It includes a static assertion that current i8/i16/pointer helpers require `CONFIG_ARCH_SUPPORTS_ATOMIC_RMW`.

Risks: macro-generated safety comments are generic, so invocation-site requirements must remain accurate. Byte/halfword/pointer atomicity currently assumes native atomic RMW support. Arithmetic ops are intentionally limited to `i32` and `i64` representations.

Test signals: indirect KUnit coverage through public atomic tests. Build coverage across architectures is especially important because helper availability and config assertions are architecture-sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/internal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/ordering.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/ordering.rs

Purpose: defines marker types and sealed traits for LKMM memory-order annotations used by the Rust atomic wrapper.

Important APIs/types/functions: marker structs are `Relaxed`, `Acquire`, `Release`, and `Full`. `OrderingType` is the internal enum used by dispatch code. Sealed trait `Ordering` exposes `TYPE`; `AcquireOrRelaxed` and `ReleaseOrRelaxed` restrict operation-specific valid orderings.

Control flow: methods in `atomic.rs` accept marker values as zero-sized type arguments and dispatch on `Ordering::TYPE`. Invalid combinations are excluded by trait bounds or produce compile-time `build_error!` in unreachable match arms.

State/persistence: no runtime state.

Dependencies/integration: integrated directly by `Atomic<T>` method signatures and maps to LKMM documentation semantics.

Risks: names resemble Rust standard atomics but semantics are LKMM-specific; developers must not assume C++/Rust memory-model details. `Full` represents fully ordered operations with full-barrier strength, not just acquire+release.

Test signals: compile-time trait bounds are the main signal. Public atomic KUnit tests exercise ordering-specific API paths for load/store/xchg/cmpxchg/arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/ordering.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/predefine.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/predefine.rs

Purpose: supplies built-in `AtomicType` and `AtomicAdd` implementations for primitive bool, integer, pointer, and pointer-sized types, plus KUnit coverage for the public atomic API.

Important APIs/types/functions: implementations cover `bool`, `i8`, `i16`, raw pointers, `i32`, `i64`, `isize`, `usize`, `u32`, and `u64`. `isize_atomic_repr` selects `i32` or `i64` based on kernel/test pointer width. `static_assert!` checks size/alignment compatibility. KUnit tests use `for_each_type!` to exercise many primitive widths.

Control flow: unsigned and pointer-sized types map onto signed atomic representations with casts for arithmetic deltas. Pointer types map to `*const c_void`. Tests construct atomics, call operations, and assert results.

State/persistence: no production state; test module creates stack-local atomics.

Dependencies/integration: depends on `AtomicType`, `AtomicAdd`, `Atomic`, ordering markers, `static_assert!`, `c_void`, and KUnit macro support.

Risks: transmutability assumptions for unsigned-to-signed representations are core to correctness. Pointer atomic support is for pointer values only; dereferencing remains the caller's unsafe responsibility. `bool` is represented as `i8`, while `AtomicFlag` may use a wider representation elsewhere for RMW efficiency.

Test signals: KUnit tests cover basic, acquire/release, xchg, cmpxchg, arithmetic, bool, pointer, and flag behavior, providing the strongest test coverage in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/predefine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/barrier.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/barrier.rs

Purpose: exposes compiler and SMP memory barriers matching Linux Kernel Memory Model semantics.

Important APIs/types/functions: private `barrier()` emits an empty inline asm block as a compiler barrier. Public `smp_mb`, `smp_wmb`, and `smp_rmb` call the matching C bindings on SMP builds or fall back to the compiler barrier on non-SMP builds.

Control flow: each public function checks `cfg!(CONFIG_SMP)` at compile time and chooses the C barrier or compiler-only fallback.

State/persistence: no state.

Dependencies/integration: depends on `core::arch::asm!` and barrier C bindings. Used by synchronization code that needs explicit LKMM barriers outside typed atomics.

Risks: barriers are low-level and do not provide mutual exclusion or lifetime management. Incorrect placement can leave races even when barriers are present. The empty asm relies on Rust inline-asm memory effects being conservative enough for compiler reordering prevention.

Test signals: no local tests. Validation comes from architecture build coverage and LKMM/litmus reasoning in users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/barrier.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/completion.rs -->
## sources/distributed-fs/ceph-client/rust/kernel/sync/completion.rs

Purpose: wraps Linux completions as a Rust synchronization primitive for one task or work item to signal that work has completed.

Important APIs/types/functions: `Completion` contains pinned `Opaque<bindings::completion>`. `Completion::new` initializes with `init_completion`. `complete_all` wakes all current and future waiters, and `wait_for_completion` blocks uninterruptibly until completion.

Control flow: initialization occurs through `Opaque::ffi_init`. Waiters call `wait_for_completion` on the raw pointer. Producers call `complete_all`, permanently setting the completion done state.

State/persistence: state is the underlying C `struct completion`, including wait queues and done count. It is in-memory and usually embedded in a pinned owner.

Dependencies/integration: depends on pin-init, `Opaque`, and C completion bindings. Commonly integrates with workqueues and `Arc`-owned task objects.

Risks: `wait_for_completion` is uninterruptible and has no timeout, so misuse can deadlock. `complete_all` is permanent for the current completion state; this wrapper does not expose reinitialization. Object lifetime must outlive waiters and signalers.

Test signals: doctest shows a workqueue task completing and a waiter blocking until `complete_all`. Runtime tests should cover multiple waiters, already-completed waits, and teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/sync/completion.rs -->
