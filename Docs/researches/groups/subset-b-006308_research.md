# subset-b-006308 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/irq/request.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/irq/request.rs

Purpose: provides Rust RAII wrappers for registering hard IRQ and threaded IRQ handlers against a bound kernel device. It translates Rust handler traits into `request_irq` / `request_threaded_irq` callbacks and ensures `free_irq` runs before the pinned registration storage can disappear.

Important APIs/types/functions: `IrqReturn`, `ThreadedIrqReturn`, `Handler`, `ThreadedHandler`, `IrqRequest<'a>`, `Registration<T>`, `ThreadedRegistration<T>`, `RegistrationInner`, `try_synchronize`, `synchronize`, `handle_irq_callback`, `handle_threaded_irq_callback`, and `thread_fn_callback`. `Handler` and `ThreadedHandler` are implemented for `Arc<T>` and `Box<T, A>` so shared or heap-owned handler state can be installed directly.

Control flow: an unsafe device-side producer creates `IrqRequest::new(dev, irq)`. `Registration::new` or `ThreadedRegistration::new` pin-initializes the handler first, then creates a `Devres<RegistrationInner>` whose initialization calls the relevant C registration function with a cookie pointing at the pinned Rust registration. C callbacks cast the cookie back, recover the bound device from `Devres`, and invoke the Rust trait method. Drop of `RegistrationInner` calls `free_irq`, which waits for active callbacks to finish.

State and persistence behavior: no durable state is persisted. Runtime state is the IRQ number, callback cookie, device-managed registration, and handler object. The critical invariant is address stability: `_pin: PhantomPinned` and pin-init keep the cookie pointer valid for the full registration lifetime. `Devres` also accounts for device unbind; `try_synchronize` may fail with `ENODEV` if the devres payload is inaccessible.

Dependencies and integration points: depends on `crate::device::{Bound, Device}`, `crate::devres::Devres`, IRQ `Flags`, `Arc`, allocator-aware `Box`, `CStr`, and generated `bindings`. It integrates with the Linux IRQ subsystem through `request_irq`, `request_threaded_irq`, `synchronize_irq`, and `free_irq`.

Risks: callbacks run in interrupt context for hard handlers, so handler implementations must avoid sleeping and must use interior synchronization appropriate for IRQ context. The callback cookie cast is only sound while pinned storage is alive; any change to initialization ordering or pinning would be high risk. `ThreadedHandler::handle` defaults to `WakeThread`, which is convenient but may create avoidable thread wakeups if a driver forgets to override it. Device access relies on the invariant that IRQ callbacks are removed before device unbind completes.

Test signals: compile-time type checking covers trait bounds and pin-init shape. Runtime confidence should come from driver KUnit or integration tests that register/unregister shared IRQs, trigger threaded wakeups, exercise device unbind while IRQs are quiesced, and call both synchronization methods. Edge tests should cover immediate callback execution during registration and devres invalidation paths returning `ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/irq/request.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/jump_label.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/jump_label.rs

Purpose: exposes Rust support for Linux static keys / jump labels. It lets Rust code branch on a C-defined static key using the architecture-generated static branch assembly when jump labels are enabled, or `static_key_count` otherwise.

Important APIs/types/functions: `static_branch_unlikely!`, hidden `arch_static_branch!`, and `bool_to_int`. `static_branch_unlikely!` accepts the key path, key type, and field name containing the `static_key_false`.

Control flow: the public macro takes an address of the static C key field, casts it to `static_key`, and either calls `bindings::static_key_count` when `CONFIG_JUMP_LABEL` is off or emits an inline assembly block from `generated_arch_static_branch_asm.rs` when enabled. The assembly label path breaks out of a Rust labeled block with `true`; fallthrough returns `false`.

State and persistence behavior: this file owns no state. It observes static key state managed by the C kernel. Generated assembly is included from `OBJTREE`, so build output must contain the expected generated Rust assembly fragment.

Dependencies and integration points: depends on `bindings::static_key_false`, `bindings::static_key`, `static_key_count`, the crate-level `asm!` wrapper, `offset_of!`, and generated architecture files. It is used by Rust features that need low-overhead rarely-enabled branches.

Risks: misuse with a non-static or wrong field type can produce invalid pointer casts or wrong assembly relocation data; the macro is documented as safety-sensitive. Generated assembly inclusion ties correctness to build-system generation. The fallback path mutably casts the static key for `static_key_count`, so the C API assumptions must remain valid.

Test signals: build coverage with and without `CONFIG_JUMP_LABEL` is important. Static-key behavior should be validated by callers toggling keys from C and observing Rust branch behavior. The const include assertion is a build-time signal that the generated assembly fragment evaluates to a string literal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/jump_label.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/kunit.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/kunit.rs

Purpose: maps Rust unit-test assertions and generated test suites into the kernel KUnit framework. It provides hidden macros/functions used by generated Rust tests plus a public `in_kunit_test` helper.

Important APIs/types/functions: `err`, `info`, `kunit_assert!`, `kunit_assert_eq!`, private `TestResult`, `is_test_result_ok`, `kunit_case`, `kunit_unsafe_test_suite!`, and `in_kunit_test`. The local `tests` module demonstrates `#[kunit_tests]` integration.

Control flow: print helpers route formatted Rust `fmt::Arguments` to `_printk` when `CONFIG_PRINTK` is enabled. `kunit_assert!` first checks the Rust condition, then obtains the current KUnit test. Without a current KUnit test it logs KUnit-like failure text. With a test pointer, it builds static `kunit_loc` and `kunit_unary_assert` records, calls `__kunit_do_failed_assertion`, then aborts the KUnit test via `__kunit_abort`. `kunit_unsafe_test_suite!` builds a static `kunit_suite` and places a pointer into `.kunit_test_suites`.

State and persistence behavior: state is static test metadata and per-current-task KUnit context retrieved from C. Assertion metadata is static to satisfy C lifetime requirements. No persistent state is written.

Dependencies and integration points: depends on KUnit C bindings, `_printk`, Rust formatting, generated `#[kunit_tests]` infrastructure, `CStr`, and link-section behavior. It is a bridge between Rust doc/unit tests and KUnit's C execution model.

Risks: failing assertions abort without running Rust destructors, and comments explicitly note the foreign-unwind/stack implications. The hidden macros must be used only from generated tests or valid KUnit context. Suite and test case arrays must be static and null-terminated; misuse of `kunit_unsafe_test_suite!` can hand invalid metadata to KUnit. The suite-name buffer has a 255-byte limit enforced at const time.

Test signals: the embedded tests cover basic assertion routing and `in_kunit_test`. Additional signals are build/link tests verifying `.kunit_test_suites`, tests with `CONFIG_PRINTK` disabled, generated doctests returning both `()` and `Result`, and tests that intentionally fail to confirm KUnit receives the failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/kunit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/lib.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/lib.rs

Purpose: defines the root Rust `kernel` crate, module exports, module initialization traits, panic handling, core macros, and small helpers shared by Rust kernel code.

Important APIs/types/functions: crate feature gates, module exports, `Module`, `InPlaceModule`, `ModuleMetadata`, `ThisModule`, `container_of!`, `assert_same_type`, `concat_literals!`, architecture-specific `asm!`, panic handler, and `file_from_location`. It also publicly re-exports `bindings`, `macros`, `uapi`, and `ffi`.

Control flow: module crates implement `Module::init`; `InPlaceModule` adapts that into pin-init by constructing `Self` then writing into the provided slot. `ThisModule` wraps the raw `THIS_MODULE` pointer. Panics print emerg and call `BUG()`. `container_of!` computes a field offset, subtracts it from a field pointer, then type-checks the field pointer. `asm!` normalizes kernel inline assembly syntax, adding AT&T syntax on x86. `file_from_location` selects the best available compiler API for C-string source filenames.

State and persistence behavior: root crate owns no durable runtime state. It controls compile-time API surface through `CONFIG_*` conditional modules and unstable feature gates. `ThisModule` is a raw module pointer with static use expectations.

Dependencies and integration points: this is the integration hub for nearly every Rust kernel abstraction. It depends on generated bindings, proc macros, pin-init, kernel configuration symbols, architecture assembly generation, and the kernel BUG/logging facilities.

Risks: any exported module or feature gate change affects all Rust kernel users. `container_of!` is unsafe at call sites and relies on same-allocation provenance. The panic handler intentionally terminates via `BUG()`. Conditional compilation must be correct; the crate emits a `compile_error!` when `CONFIG_RUST` is missing to avoid silent misbuilds.

Test signals: crate-level build coverage across representative kernel configs is the main signal. Macro doctests exercise `container_of!` and `file_from_location`. Architecture build tests should cover `asm!` on x86 and non-x86. Module initialization tests should ensure `Module` and `InPlaceModule` paths both run destructors correctly on later teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/list.rs

Purpose: implements a generic intrusive circular doubly-linked list for Rust kernel code. Elements are reference-counted through `ListArc`, and each list owns the unique `ListArc` permission to mutate an element's link fields.

Important APIs/types/functions: `List<T, ID>`, unsafe trait `ListItem<ID>`, `ListLinks<ID>`, `ListLinksSelfPtr<T, ID>`, `Iter`, `Cursor`, `CursorPeek`, `IntoIter`, and re-exported helper macros/types from `list/arc.rs`, `list/arc_field.rs`, and `list/impl_list_item_mod.rs`. Public operations include `new`, `is_empty`, `push_back`, `push_front`, `pop_back`, `pop_front`, unsafe `remove`, `push_all_back`, `cursor_front`, `cursor_back`, and `iter`.

Control flow: insertion consumes a `ListArc`, converts it to a raw pointer, calls `T::prepare_to_insert` to obtain exclusive link-field access, and links the node into the circular list. Removal updates neighboring links, nulls the removed node's links, calls `T::post_remove`, and reconstructs the `ListArc`. Iteration walks from `first` until it reaches the stop pointer again. Cursors hold a mutable borrow of the list and represent the gap before `next`; peek wrappers permit removal or temporary borrowing of adjacent elements.

State and persistence behavior: list state is an in-memory raw pointer to the first link node; empty lists use null. Each element's link fields are null when not in a list and cyclic when inserted. Drop drains the list by popping the front, thereby dropping owned `ListArc`s. No persistent storage exists.

Dependencies and integration points: depends on `ArcBorrow`, `ListArc`, `Opaque`, pin-init, raw pointer manipulation, and `container_of!` via implementations. It is intended as a building block for kernel subsystems that need intrusive lists without allocating wrapper nodes.

Risks: the unsafe `ListItem` contract is central. Incorrect `view_links`, `view_value`, `prepare_to_insert`, or `post_remove` can create aliasing, dangling pointers, or duplicate link ownership. `remove` is unsafe because the caller must ensure the item is not in another same-ID list. Trait-object support through `ListLinksSelfPtr` stores a self pointer and must preserve validity until removal. Pointer provenance comments indicate sensitivity to pointer-reference-pointer roundtrips.

Test signals: doctests cover basic list use, trait-object list items, cursor removal/insertion, merging, and owned iteration. Additional tests should stress remove of absent items, single/two/many-element edge cases, `push_all_back` from empty and non-empty lists, drop draining, `DoubleEndedIterator`, and multiple `ID` link sets on the same value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list/arc.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/list/arc.rs

Purpose: defines `ListArc`, a special `Arc` wrapper that is unique per element and list-link ID, giving its owner exclusive permission to mutate intrusive list fields while still allowing ordinary shared `Arc` references.

Important APIs/types/functions: `ListArcSafe<ID>`, unsafe `TryNewListArc<ID>`, `impl_list_arc_safe!`, `ListArc<T, ID>`, `AtomicTracker<ID>`, constructors `new`, `pin_init`, `init`, conversions from `UniqueArc`, `pair_from_unique`, `try_from_arc`, `try_from_arc_borrow`, `try_from_arc_or_drop`, raw conversions, `into_arc`, `clone_arc`, `as_arc`, `as_arc_borrow`, and `ptr_eq`.

Control flow: creating a `ListArc` from a `UniqueArc` pins or owns the unique allocation, calls `on_create_list_arc_from_unique`, converts to `Arc`, then rewraps without changing representation. Attempted creation from a shared `Arc` delegates to `TryNewListArc::try_new_list_arc`, typically an atomic compare-exchange. Dropping or converting into a regular `Arc` calls `on_drop_list_arc` so tracking no longer claims a live list permission. Raw conversions intentionally preserve the tracking state so list insertion/removal can round-trip ownership.

State and persistence behavior: no persistent state. Per-object list-permission state lives inside the target type via `ListArcSafe`, commonly through `AtomicTracker` storing an `AtomicFlag`. The invariant allows false positives in tracking but forbids false negatives, avoiding duplicate `ListArc` creation.

Dependencies and integration points: depends on kernel `Arc`, `ArcBorrow`, `UniqueArc`, atomic ordering, pinning, `AllocError`, and `build_assert!`. It is tightly coupled to `List` ownership transfer and to macros that implement tracking for user structs.

Risks: representation-preserving transmutes and raw pointer conversions are sound only if tracking invariants are exact. The `untracked` macro strategy intentionally prevents creation from shared `Arc`; using it where shared recreation is needed can cause functional failures, while incorrect tracked implementations can cause memory unsafety. `pair_from_pin_unique` relies on distinct const IDs enforced by `build_assert!`.

Test signals: tests should cover tracked and untracked strategies, `try_from_arc` contention, drop/recreate ordering with `AtomicTracker`, `into_arc` clearing tracking, pair creation with distinct IDs, and list insertion/removal round trips. Concurrency tests around `AtomicTracker::cmpxchg` would be valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list/arc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list/arc_field.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/list/arc_field.rs

Purpose: provides `ListArcField`, a field wrapper whose contents are accessible only through ownership of the corresponding `ListArc`. This supports per-list-permission interior mutability without exposing general shared mutation.

Important APIs/types/functions: `ListArcField<T, ID>`, `new`, `get_mut`, unsafe `assert_ref`, unsafe `assert_mut`, and `define_list_arc_field_getter!`.

Control flow: `ListArcField` stores `T` in `UnsafeCell`. Code with exclusive construction access can call `get_mut`. Code that has a shared or mutable `ListArc<Self, ID>` uses generated getters; the macro obtains the field from `self`, then calls `assert_ref` or `assert_mut` under the safety argument that `ListArc` ownership grants access to that field.

State and persistence behavior: state is the wrapped in-memory value. There is no persistence or independent synchronization. The type's `Send` and `Sync` implementations require `T: Send + Sync` because access may cross threads through a `ListArc`.

Dependencies and integration points: depends on `UnsafeCell` and `ListArc`. It integrates with list item structs that need a field owned by the unique list reference, often to pair intrusive-list membership with mutable metadata.

Risks: `assert_mut` returns `&mut T` from `&self`; soundness relies entirely on the caller really having mutable access to the unique `ListArc`. Manually calling the unsafe methods without the required `ListArc` access would violate aliasing. The macro is safer than hand calls but still assumes the field belongs to the same `Self` and `ID`.

Test signals: tests should verify generated shared and mutable getters, interaction with `UniqueArc` construction through `get_mut`, and compile-time rejection of mismatched field types/IDs. Miri-style aliasing checks would be useful if available for a user-space model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list/arc_field.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list/impl_list_item_mod.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/list/impl_list_item_mod.rs

Purpose: contains helper traits and macros that implement unsafe `ListItem` plumbing from declared link fields, reducing the amount of hand-written unsafe code needed by intrusive list users.

Important APIs/types/functions: unsafe `HasListLinks<ID>`, `impl_has_list_links!`, unsafe marker `HasSelfPtr<T, ID>`, `impl_has_list_links_self_ptr!`, and `impl_list_item!` for both `ListLinks` and `ListLinksSelfPtr` storage strategies.

Control flow: `impl_has_list_links!` uses `offset_of!` and `addr_of_mut!` to produce a raw pointer to a link field without dereferencing intermediate pointers. The `ListLinks` variant of `impl_list_item!` implements `view_links` as field access and `view_value`/`post_remove` via `container_of!`. The `ListLinksSelfPtr` variant writes the full self pointer into the `ListLinksSelfPtr` container during insertion and reads it back for trait-object-compatible value recovery.

State and persistence behavior: no module-owned persistent state. The macros define how per-object link state is accessed and, for self-pointer lists, where the object pointer is cached during list membership.

Dependencies and integration points: depends on `ListItem`, `ListLinks`, `ListLinksSelfPtr`, `Opaque`, and `container_of!`. It is the recommended integration path for user structs implementing intrusive list support.

Risks: macro-generated implementations are only as sound as the field declaration. The `ListLinksSelfPtr` variant has TODO safety comments and writes/reads raw self pointers, so misuse could invalidate trait object recovery. Nested field paths must not traverse pointers; the macro includes a static `offset_of!` check to catch that. Manual `HasListLinks` implementations bypass this protection.

Test signals: doctests cover simple and nested field implementations for both link storage styles. Additional compile-fail tests should cover wrong field types, pointer-traversing field paths, duplicate `ListItem` IDs, and mismatched trait-object self pointer types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/list/impl_list_item_mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/maple_tree.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/maple_tree.rs

Purpose: wraps Linux maple trees for Rust-owned values implementing `ForeignOwnable`, supporting non-overlapping range insertion, erasure, allocation-range insertion, locked lookup, and iteration through `ma_state`.

Important APIs/types/functions: `MapleTree<T>`, `MapleTreeAlloc<T>`, `to_maple_range`, `insert`, `insert_range`, `erase`, `lock`, `MapleGuard`, `MaState`, `find`, `alloc_range`, `InsertError<T>`, `InsertErrorKind`, `AllocError<T>`, and `AllocErrorKind`.

Control flow: constructors initialize a C `maple_tree` with normal or `MT_FLAGS_ALLOC_RANGE` flags. Insert operations convert Rust ownership to a foreign pointer, call C insertion APIs, and reclaim the value on error with a specific Rust error cause. `erase` removes the range containing an index and converts the returned pointer back into `T`. `lock` takes the tree spinlock and returns `MapleGuard`; lookups and `MaState` iteration borrow values while the guard/state proves access. Drop frees Rust entries if needed, then destroys the tree.

State and persistence behavior: state is in-memory C maple tree nodes containing foreign-owned Rust values. The invariant is that each stored range owns one `T`. Destruction may free all entries without first removing them because the tree is about to become unobservable. No durable persistence exists.

Dependencies and integration points: depends on `bindings` maple-tree APIs, `ForeignOwnable`, `Opaque`, RCU guard during raw destruction iteration, spinlocks, allocation flags, and kernel error conversion. It is useful for address/range maps in memory-management or driver code.

Risks: callers must not observe the tree during `free_all_entries`, which intentionally leaves C tree structure stale while freeing values. Borrowed results from `load` and `find` are only valid under the lock/state lifetime. Range conversion must reject empty or overflowing ranges; edge cases around `usize::MAX` are important. Error mapping treats unexpected non-ENOMEM/non-EEXIST returns as invalid requests.

Test signals: doctests cover point insertion, range insertion overlap, erasure by contained index, locked load with refcounted values, allocation tree placement, and iteration. Further tests should cover unbounded ranges, excluded bound overflow/underflow, drop of values with destructors, allocation-tree busy conditions, and lock-held mutation patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/maple_tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/miscdevice.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/miscdevice.rs

Purpose: provides Rust registration and file-operations adapters for Linux misc devices. A Rust type implementing `MiscDevice` supplies open/release/read/write/mmap/ioctl/fdinfo behavior, while the wrapper builds a `file_operations` table and manages registration lifetime.

Important APIs/types/functions: `MiscDeviceOptions`, `MiscDeviceRegistration<T>`, trait `MiscDevice`, `MiscdeviceVTable<T>`, and callback adapters `open`, `release`, `read_iter`, `write_iter`, `mmap`, `ioctl`, `compat_ioctl`, and `show_fdinfo`.

Control flow: `MiscDeviceRegistration::register` writes a raw `miscdevice` into pinned storage and calls `misc_register`; drop calls `misc_deregister`. The C `open` adapter first calls `generic_file_open`, receives the `miscdevice` pointer in `file.private_data`, casts it to the registration, calls `T::open`, and replaces `private_data` with `T::Ptr::into_foreign()`. Later file operations borrow or own that private data according to their lifecycle; `release` converts it back with `from_foreign` and calls `T::release`.

State and persistence behavior: registered miscdevice state lives in pinned `bindings::miscdevice` storage. Per-open-file state lives in `file.private_data` as a `ForeignOwnable` pointer from `T::Ptr`. No persistent storage is written.

Dependencies and integration points: depends on file abstractions (`File`, `Kiocb`), iov iterators, `VmaNew`, `SeqFile`, `ForeignOwnable`, C miscdevice APIs, and vtable macro support. It integrates with VFS file operations and optional compat ioctl support.

Risks: `private_data` changes type after open; every callback must agree on the lifecycle and pointer type. `MiscDeviceOptions::into_raw` sets dynamic minor and static name/fops; name lifetime must be static. Missing trait methods use `VTABLE_DEFAULT_ERROR` and are omitted from the C vtable based on generated `HAS_*` flags. `show_fdinfo` comments mention release ownership even though it borrows, indicating an area to read carefully during maintenance.

Test signals: useful tests include registration/deregistration, open failure preserving private data rules, release dropping exactly once, read/write iterator errno translation, mmap flag configuration through `VmaNew`, ioctl/compat behavior, and fdinfo output. Compile-time tests should ensure vtable omission for unimplemented methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/miscdevice.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/mm.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/mm.rs

Purpose: wraps `struct mm_struct` and related read-lock guards so Rust code can model address-space lifetime through `mmgrab`, `mmget`, mmap read locks, and per-VMA read locks.

Important APIs/types/functions: `Mm`, `MmWithUser`, `AlwaysRefCounted` impls, `Mm::from_raw`, `Mm::mmget_not_zero`, `MmWithUser::from_raw`, `lock_vma_under_rcu`, `mmap_read_lock`, `mmap_read_trylock`, `MmapReadGuard`, `VmaReadGuard`, and `VmaRef` integration from `virt`.

Control flow: `ARef<Mm>` increments/decrements `mm_count` via `mmgrab`/`mmdrop`. `ARef<MmWithUser>` increments/decrements `mm_users` via `mmget`/`mmput`. `mmget_not_zero` attempts to upgrade an `Mm` to an `MmWithUser`. With nonzero users, callers may take mmap read locks or try per-VMA RCU locks. Guards unlock in `Drop` and are marked `NotThreadSafe` so lock/unlock happen on the same thread.

State and persistence behavior: wraps live process address-space state owned by the kernel. Reference counts are kernel state; guard objects model temporary lock ownership. No new persistent data is introduced.

Dependencies and integration points: depends on `bindings` MM APIs, `ARef`, `AlwaysRefCounted`, `NotThreadSafe`, `Opaque`, and `virt::VmaRef`. It is the foundation for VMA lookup and miscdevice mmap handling.

Risks: using `Mm` methods that require nonzero `mm_users` without `MmWithUser` would be unsafe, so the type split must be preserved. `mmdrop`/`mmput` may sleep, influencing where `ARef` destructors can run. Per-VMA lock support is config-dependent and returns `None` when disabled. Raw constructors require callers to prove lifetime and user-count invariants.

Test signals: tests should cover `mmget_not_zero` success/failure, mmap read lock lookup, trylock failure handling, per-VMA-lock disabled builds, and guard drop on the same thread. Static analysis should check no `VmaRef` outlives its guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/mm.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/mm/mmput_async.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/mm/mmput_async.rs

Purpose: provides an `MmWithUser` reference-count wrapper whose `ARef` destructor uses `mmput_async`, making it suitable for contexts where synchronous `mmput` could sleep.

Important APIs/types/functions: `MmWithUserAsync`, its `AlwaysRefCounted` implementation, `Deref<Target = MmWithUser>`, and `MmWithUser::into_mmput_async`.

Control flow: `inc_ref` still uses `mmget`, preserving `mm_users`. `dec_ref` calls `mmput_async`. `into_mmput_async` consumes an `ARef<MmWithUser>`, reinterprets the raw pointer as `MmWithUserAsync`, and returns an `ARef` with the alternate drop behavior.

State and persistence behavior: no independent state; it shares the same `mm_struct` and reference count as `MmWithUser`. The only behavioral difference is asynchronous release.

Dependencies and integration points: compiled only with `CONFIG_MMU`. Depends on `bindings::mmput_async`, `ARef`, `AlwaysRefCounted`, and `MmWithUser`. It is re-exported from `mm.rs` under `CONFIG_MMU`.

Risks: layout compatibility with `MmWithUser` is essential for the raw cast. Callers must choose this wrapper when destruction context matters; using regular `MmWithUser` in atomic context can be invalid because `mmput` may sleep. Conversely, async release may defer cleanup timing.

Test signals: build tests under `CONFIG_MMU`, refcount lifecycle tests converting from `MmWithUser`, and context tests dropping `ARef<MmWithUserAsync>` from atomic-like paths are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/mm/mmput_async.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/mm/virt.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/mm/virt.rs

Purpose: models access capabilities for `struct vm_area_struct`: read access (`VmaRef`), read access with `VM_MIXEDMAP` (`VmaMixedMap`), and mmap-initialization access (`VmaNew`). It also exports VMA flag constants.

Important APIs/types/functions: `VmaRef`, `VmaMixedMap`, `VmaNew`, `vm_flags_t`, `flags`, `VmaRef::mm`, `flags`, `start`, `end`, `zap_vma_range`, `as_mixedmap_vma`, `VmaMixedMap::vm_insert_page`, and VMA setup methods such as `set_mixedmap`, `set_io`, `set_dontexpand`, `set_dontcopy`, `set_dontdump`, `try_clear_mayread`, `try_clear_maywrite`, and `try_clear_mayexec`.

Control flow: raw constructors create references only under externally-proven lock or mmap-setup conditions. Read methods access fields under the read-lock invariant. `zap_vma_range` validates the requested range lies within the VMA and returns early on overflow/out-of-bounds. `VmaNew` mutates flags during mmap setup through `update_flags`; specific setters encode valid transitions and `try_clear_may*` rejects clearing a permission while it is actively enabled.

State and persistence behavior: state is the live VMA fields in kernel memory. `VmaNew` mutates the VMA before it is fully published. Page insertion and zap operations affect process mappings but do not persist outside kernel memory/page tables.

Dependencies and integration points: depends on `MmWithUser`, `Page`, MM bindings, kernel error codes, and miscdevice mmap callbacks. It integrates with the mmap path and page-table manipulation helpers.

Risks: capability separation is the safety boundary. Constructing `VmaRef` without the required lock or `VmaNew` outside mmap setup would allow races. `update_flags` must not create invalid flag combinations; currently `set_mixedmap` notes no `VM_PFNMAP` setter exists, limiting one invalid combination. `zap_vma_range` silently returns on invalid ranges pending a future warning.

Test signals: tests should verify flag setters/clearers, permission-clear failure when active, `set_mixedmap` enabling `vm_insert_page`, `as_mixedmap_vma` behavior, range validation in `zap_vma_range`, and integration from miscdevice `mmap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/mm/virt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/module_param.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/module_param.rs

Purpose: supports Rust module parameters by defining parse traits, storage access, and generated `kernel_param_ops` for integer parameter types.

Important APIs/types/functions: `KernelParam`, `ModuleParam`, unsafe extern `set_param<T>`, `impl_int_module_param!`, `ModuleParamAccess<T>`, `make_param_ops!`, and statics `PARAM_OPS_*` for integer types.

Control flow: C module-parameter code calls `set_param` with a string and `kernel_param`. The adapter validates `val`, converts it to `CStr`/`BStr`, parses `T`, casts the kernel param argument to `SetOnce<T>`, and populates it. `ModuleParamAccess::value` returns the populated value or the default. Generated ops expose only `set`; `get` and `free` are `None`.

State and persistence behavior: parameter state is in a `SetOnce<T>` plus default value created by the module macro. Parameters are currently write-once, read-only from Rust, and not readable through sysfs per comments.

Dependencies and integration points: depends on `bindings::kernel_param`, `kernel_param_ops`, `SetOnce`, string integer parsing, and the Rust `module!` macro that initializes parameter storage and C metadata.

Risks: `ModuleParam` is constrained to `Copy` because destructors during teardown could be unsound. A null `val` is rejected; future valueless arguments would need revised handling. Casting `param.arg` to `SetOnce<T>` relies on module macro layout. Re-population returns `EEXIST`, so repeated sysfs/module-load writes are not supported by this storage model.

Test signals: tests should parse every supported integer type, reject invalid strings and duplicate sets, verify default fallback, and verify generated `kernel_param_ops` call the right typed setter. Integration testing should cover built-in and loadable module parameter initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/module_param.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/net.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/net.rs

Purpose: top-level networking module gate for Rust kernel networking abstractions.

Important APIs/types/functions: conditionally exports `pub mod phy` when `CONFIG_RUST_PHYLIB_ABSTRACTIONS` is enabled.

Control flow: there is no runtime control flow. The file is purely a compile-time module declaration controlled by kernel configuration.

State and persistence behavior: none.

Dependencies and integration points: depends on `CONFIG_NET` at the parent `lib.rs` export level and `CONFIG_RUST_PHYLIB_ABSTRACTIONS` for PHY support. It is the namespace through which callers reach `kernel::net::phy`.

Risks: missing or incorrect cfg flags can hide PHY abstractions from users or build them when dependencies are unavailable. Because this file is small, most behavioral risk lives in `net/phy.rs`.

Test signals: build matrix coverage with networking on/off and PHY Rust abstractions on/off is sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/net.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/net/phy.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/net/phy.rs

Purpose: wraps Linux PHYLIB for Rust PHY drivers. It exposes a typed `Device`, driver trait/vtable generation, registration RAII, PHY IDs, and a `module_phy_driver!` macro.

Important APIs/types/functions: `DeviceState`, `DuplexMode`, `Device`, `flags`, `Adapter<T>`, `DriverVTable`, `create_phy_driver<T>`, `Driver`, `Registration`, `DeviceId`, `DeviceMask`, and `module_phy_driver!`. Device methods cover PHY ID/state/link/autoneg, speed/duplex mutation, register read/write, paged reads, generic PHY reset/init/aneg/suspend/resume/status helpers, and link/ability helpers.

Control flow: PHYLIB invokes C callbacks in `DriverVTable`; each callback casts `phy_device` into `Device` under PHYLIB locking/exclusivity assumptions and calls the corresponding Rust `Driver` method, converting `Result` into errno. `create_phy_driver` builds a C `phy_driver` with function pointers only for trait methods implemented according to `#[vtable]` `HAS_*` constants. `Registration::register` registers a pinned static slice of vtables; drop unregisters it. `module_phy_driver!` generates a module wrapper, static driver array, registration in `Module::init`, and MDIO device table.

State and persistence behavior: PHY device state is kernel-owned `phy_device` memory. Driver vtables and device tables are static module data. `Registration` owns the fact that the driver slice is registered and unregisters on drop. No durable persistence is written.

Dependencies and integration points: depends on PHYLIB bindings, `RawDeviceId`, `Device` wrappers, register abstractions in `net/phy/reg.rs`, module macros, and kernel device ID table generation. It is the Rust entry point for MDIO/PHY drivers.

Risks: `Device::from_raw` is private and unsafe because method safety depends on PHYLIB callback context and locking. Bitfield offsets for link/autoneg are manually hard-coded pending bindgen support. Callback coverage must match `Driver` optional method flags exactly. `module_phy_driver!` uses `static mut DRIVERS`; safety relies on anonymous-constant encapsulation and C-only use after pinning.

Test signals: build tests for a sample PHY driver using `module_phy_driver!`, callback invocation tests for implemented and omitted vtable entries, registration failure for empty slices, ID/mask generation tests, and integration tests reading/writing both C22/C45 registers through `Device`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/net/phy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/net/phy/reg.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/net/phy/reg.rs

Purpose: provides sealed typed access to MDIO clause 22 and clause 45 PHY registers and a unified `Register` trait consumed by `Device`.

Important APIs/types/functions: sealed `Register`, `C22`, `Mmd`, `C45`, C22 standard register constants, `C22::vendor_specific`, MMD constants, `C45::new`, and `read_status` implementations for C22 and C45.

Control flow: `Device::read`/`write` call the selected register object's trait methods. C22 reads/writes open-code `phy_read`/`phy_write` through `mdiobus_read`/`mdiobus_write` using the PHY's bus and address. C45 reads/writes call `phy_read_mmd` and `phy_write_mmd`. `read_status` dispatches to `genphy_read_status` or `genphy_c45_read_status`.

State and persistence behavior: no module-owned state. Reads/writes affect hardware registers and PHYLIB-maintained status as the C helpers do.

Dependencies and integration points: depends on `super::Device`, kernel error conversion, `uapi` MDIO constants, and `build_assert!`. The sealed trait prevents external register namespace implementations that might violate assumptions.

Risks: C22 vendor-specific addresses are const-checked to 16..31; incorrect constants would target wrong hardware registers. Hardware I/O errors are converted through `to_result`. Clause 45 MMD device addresses are represented as `u8`, matching valid 5-bit values from constants.

Test signals: compile-time tests for valid/invalid vendor-specific addresses, unit tests for MMD constants, and hardware/mock integration tests verifying C22/C45 read/write errno handling and status helper dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/net/phy/reg.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/num.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/num.rs

Purpose: defines shared numeric marker traits and re-exports bounded-number helpers for the Rust kernel crate.

Important APIs/types/functions: `pub mod bounded`, `pub use bounded::*`, marker enums `Unsigned` and `Signed`, trait `Integer`, and macro `impl_integer!` implementing the trait for Rust primitive integer types.

Control flow: there is no runtime control flow. The macro expands trait implementations that associate each primitive integer with signedness and expose `BITS`.

State and persistence behavior: none. This is compile-time type metadata.

Dependencies and integration points: depends on `core::ops` arithmetic/bitwise traits. It is intended for generic numeric code, especially bounded integer abstractions that need primitive integer capabilities and signedness information.

Risks: the `Integer` trait bundles many operator traits; adding/removing bounds affects all generic users. It does not encode overflow semantics, so generic code must still choose checked/wrapping/saturating behavior explicitly. Signedness marker enums are type-level only and have no values.

Test signals: compile tests should verify every primitive implements `Integer`, associated `BITS` matches primitive constants, signedness is correct, and bounded-number users compile for signed and unsigned types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/num.rs -->
