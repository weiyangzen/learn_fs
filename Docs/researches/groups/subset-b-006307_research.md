# Research Report: subset-b-006307

This grouped report covers Rust-for-Linux kernel support files from `sources/distributed-fs/ceph-client/rust/kernel`. Each source file has a separate source-tree-preserving section bounded by reconciliation markers so the guard can split the report into one per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/error.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/error.rs

## Purpose
`error.rs` is the Rust kernel error bridge. It models negative Linux `errno` values as a nonzero, range-checked `Error`, exposes common error constants through `error::code`, defines the crate-wide `Result` alias, and provides helpers for converting C integer returns, error pointers, and Rust `Result` values at FFI boundaries.

## Important APIs, Types, and Functions
The `code` module declares constants such as `EINVAL`, `ENOMEM`, `EIOCBQUEUED`, and NFS-specific errors by validating C binding errno values at compile time. `Error(NonZeroI32)` exposes `from_errno`, `to_errno`, `to_ptr`, `name`, and, under `CONFIG_BLOCK`, `to_blk_status`. `to_result()` maps negative C return codes to `Err(Error)`. `from_err_ptr()` handles `ERR_PTR`-encoded pointers while preserving `NULL` as success. `from_result()` lets `extern "C"` callbacks return integer status from Rust closures. `VTABLE_DEFAULT_ERROR` is a shared diagnostic string for generated default vtable methods.

## Control Flow
Error construction runs through `try_from_errno`; invalid values log a warning and become `EINVAL`. C-call wrappers use `to_result` immediately after an unsafe binding call, so normal `?` propagation works. Error-pointer handling calls `IS_ERR`, then `PTR_ERR`, and relies on kernel invariants that encoded pointer errors are in `MAX_ERRNO` range. `from_result` executes a closure, returns the successful value unchanged, or converts the error's errno into a narrow integer compatible with C callback ABIs.

## State and Persistence
There is no persistent state. `Error` is a copyable value. Error names are retrieved from static C kernel tables in non-test builds; `testlib` disables that dependency and always returns `None`.

## Dependencies and Integration Points
This file integrates with C errno bindings, kernel error-pointer macros, block status conversion, `errname`, allocator/layout/int/UTF-8/formatting errors, and the rest of the Rust kernel crate through the `Result` alias. Almost every higher-level wrapper in this subset depends on `Error`, `Result`, `to_result`, or `from_result`.

## Risks
The range invariant is central: unsafe construction with an out-of-range errno would break `ERR_PTR` and integer conversion assumptions. `from_result` assumes all kernel errno values fit in `i16`, matching `MAX_ERRNO`. `from_err_ptr` intentionally treats `NULL` as non-error; callers of APIs where `NULL` is failure must add their own check.

## Test Signals
Useful tests cover every conversion path: valid and invalid errno construction, debug output with and without names, `to_result` success and failure, `from_err_ptr` for `ERR_PTR`, `NULL`, and normal pointers, and `from_result` on successful and failing closures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/faux.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/faux.rs

## Purpose
`faux.rs` provides a Rust RAII wrapper for Linux faux devices, useful for kernel modules that need a device-core object without a physical bus device.

## Important APIs, Types, and Functions
`Registration` owns a non-null `struct faux_device`. `Registration::new(name, parent)` calls `faux_device_create`, optionally parenting the device under a `device::Device`. `AsRef<device::Device>` exposes the embedded `dev` field. `Drop` calls `faux_device_destroy`. `Send` and `Sync` are implemented because the device core handles synchronization and the Rust type prevents duplicate destruction.

## Control Flow
Creation passes a copied C string name, optional parent raw pointer, and null ops pointer to the C API. A null return maps to `ENODEV`; otherwise the pointer is stored as the type invariant. Use sites borrow the embedded `struct device` through `AsRef`. Drop unconditionally unregisters/destroys the faux device once.

## State and Persistence
The only durable state is the registered kernel device object. Its lifetime is exactly tied to the `Registration` value. Parent device references are handled by the C device core during registration.

## Dependencies and Integration Points
The file depends on `include/linux/device/faux.h`, `crate::device`, `CStr`, `NonNull`, and standard Rust drop semantics. It is an integration helper for drivers or tests that need a device for devres, firmware, sysfs, or other device-scoped APIs.

## Risks
The wrapper assumes `faux_device_create` returns only valid devices or null and that `faux_device_destroy` is the correct inverse. Exposing the device reference is safe only while `Registration` is alive. No custom faux operations are supported because ops are always null.

## Test Signals
Test creation with and without a parent, null/failure path propagation as `ENODEV`, use of `as_ref()` with device-scoped APIs, and drop/unregister ordering under normal module teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/faux.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/firmware.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/firmware.rs

## Purpose
`firmware.rs` wraps Linux firmware loading and module firmware metadata generation. It gives Rust drivers RAII access to requested firmware blobs and a const builder for `.modinfo` firmware entries.

## Important APIs, Types, and Functions
`FwFunc` stores one of the firmware request function pointers. `Firmware` owns a `struct firmware` pointer and provides `request`, `request_nowarn`, `size`, and `data`. `Drop` releases firmware. The exported `module_firmware!` macro emits a used static byte array in `.modinfo`. `ModInfoBuilder<N>` provides const `new`, `new_entry`, `push`, `build`, and `build_length`.

## Control Flow
`Firmware::request_internal` initializes a null firmware pointer, calls the selected C request function with the device and name, converts nonzero returns to `Error`, and stores a non-null pointer on success. Data access builds a byte slice from `firmware::data` and `firmware::size`. The metadata macro runs the builder twice: once with `N=0` to compute length and once with the computed length to build the final byte array.

## State and Persistence
Loaded firmware is kernel-managed memory held until `Firmware` drops. The byte slice is immutable for the wrapper lifetime. `.modinfo` entries are compile-time static metadata, not runtime mutable state.

## Dependencies and Integration Points
The runtime API depends on `request_firmware`, `firmware_request_nowarn`, and `release_firmware`, plus `Device` and `CStr`. The macro integrates with module metadata, `LocalModule`, `ModuleMetadata`, link sections, and compile-time string building. Drivers may use the macro when firmware names depend on module name or generated lists.

## Risks
The wrapper trusts successful C firmware requests to return a valid non-null pointer. `data()` assumes the firmware backing buffer remains valid and immutable until release. The builder has strict sequencing: `new_entry()` must precede `push()` for nonzero buffers, and `build_length()` and `build()` must agree exactly or trigger compile-time errors.

## Test Signals
Exercise successful and missing firmware requests, optional firmware no-warn behavior, zero-length and nonzero blobs, drop releasing firmware once, and compile-time `.modinfo` generation for single and multiple entries, including built-in versus loadable module prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/firmware.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fmt.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/fmt.rs

## Purpose
`fmt.rs` centralizes formatting traits for Rust kernel code. It re-exports core formatting types and defines an adapter/display pattern that allows kernel macros to format foreign types while avoiding direct orphan-rule conflicts.

## Important APIs, Types, and Functions
The file re-exports `Arguments`, `Debug`, `Error`, `Formatter`, `Result`, and `Write`. `Adapter<T>` is an internal wrapper used by formatting macros. `impl_fmt_adapter_forward!` forwards non-display formatting traits. The custom `Display` trait mirrors `core::fmt::Display`, and `impl_display_forward!` implements it for primitive types, `PanicInfo`, `Arguments`, `str`, and kernel smart pointers that already implement display.

## Control Flow
Formatting macros wrap values in `Adapter`; forwarded trait impls delegate to the underlying type. For display, kernel-local `Display` implementations can be added for foreign types, then `Adapter<&T>` implements real `core::fmt::Display` by delegating through the local trait.

## State and Persistence
No state is stored. The module is purely trait and type glue used at compile time and during formatting calls.

## Dependencies and Integration Points
The module is used by `prelude::fmt!` and kernel printing/logging infrastructure. It integrates with `Arc` and `UniqueArc` formatting and is consumed by other modules such as `error.rs` for debug rendering.

## Risks
The adapter is internal; direct use could confuse trait resolution. Missing custom `Display` implementations for foreign types will surface as compile errors in formatting macros. Any divergence from core formatting semantics would affect diagnostic output.

## Test Signals
Doctest formatting of primitives, `Arguments`, references to custom `Display` implementors, and adapter forwarding for debug/hex/binary/pointer traits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fmt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fs.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/fs.rs

## Purpose
`fs.rs` is the top-level Rust filesystem module. It wires the file and asynchronous I/O callback wrappers into the public `kernel::fs` namespace.

## Important APIs, Types, and Functions
It declares `pub mod file`, re-exports `File` and `LocalFile`, declares private `kiocb`, and re-exports `Kiocb`.

## Control Flow
There is no runtime control flow. The file controls module visibility: `file` remains public while `kiocb` implementation details stay in a private submodule but expose the `Kiocb` wrapper.

## State and Persistence
No state is defined in this module. State belongs to wrapped C objects in `file.rs` and `kiocb.rs`.

## Dependencies and Integration Points
The module is the import point for filesystem-related Rust abstractions used by drivers and filesystems. It maps to Linux `include/linux/fs.h` concepts.

## Risks
The only risk is API surface management: re-exporting a wrapper makes it part of the Rust kernel interface. Submodule changes can affect external users through this facade.

## Test Signals
Compile tests should verify `kernel::fs::{File, LocalFile, Kiocb}` imports work and that private implementation modules remain hidden except through intended re-exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fs/file.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/fs/file.rs

## Purpose
`fs/file.rs` provides Rust wrappers for open kernel files and file descriptor reservation. It models `struct file` reference ownership, distinguishes locally safe file references from thread-safe ones, exposes open flags, and provides RAII cleanup for reserved fd slots.

## Important APIs, Types, and Functions
`Offset` aliases `loff_t`. `flags` exports open and file mode constants. `File` is the thread-safe wrapper around `struct file`; `LocalFile` models a file that may have same-thread `fdget_pos` state. Both implement `AlwaysRefCounted` through `get_file`/`fput`. `LocalFile::fget`, `LocalFile::from_raw_file`, `LocalFile::assume_no_fdget_pos`, `cred`, and `flags` are the main accessors. `File::from_raw_file` creates a shared thread-safe reference. `FileDescriptorReservation` wraps `get_unused_fd_flags`, `fd_install`, and `put_unused_fd`. `BadFdError` maps only to `EBADF`.

## Control Flow
`fget` calls C `fget`, turns null into `BadFdError`, and transfers the acquired reference into `ARef<LocalFile>`. Callers that know no unsafe `fdget_pos` path is active can convert `ARef<LocalFile>` to `ARef<File>` with `assume_no_fdget_pos`. `File` derefs to `LocalFile` to share methods. Descriptor reservation first claims an unused fd, then either `fd_install` consumes both reservation and file reference via `forget`, or `Drop` releases the unused slot.

## State and Persistence
State is entirely kernel object state: file reference counts, flags, credentials, and fd table reservations. `FileDescriptorReservation` is task-local by `NotThreadSafe` because fd reservation must be committed or released on the same current task.

## Dependencies and Integration Points
The file integrates with VFS `fget`, `get_file`, `fput`, `get_unused_fd_flags`, `fd_install`, `put_unused_fd`, credentials, `ARef`, `Opaque`, and device/ioctl code that accepts file descriptors. It is foundational for Rust drivers exposing or consuming file-backed resources.

## Risks
The safety boundary around `fdget_pos` is subtle. Incorrectly converting `LocalFile` to `File` can allow data races on `f_pos`. Raw construction requires the caller to keep the C refcount positive. `flags()` uses volatile read as a READ_ONCE stand-in; future memory-ordering helpers may be needed.

## Test Signals
Test invalid fd returns `BadFdError`, valid fd refcount lifecycle, `cred()` stability, flag reads, reservation drop releasing unused fd, `fd_install` consuming the reservation, and compile-time non-`Send` behavior for `FileDescriptorReservation`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fs/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fs/kiocb.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/fs/kiocb.rs

## Purpose
`fs/kiocb.rs` wraps `struct kiocb` for Rust file operation callbacks. It currently exposes file-private data and the file position carried by the kernel I/O callback.

## Important APIs, Types, and Functions
`Kiocb<'a, T>` stores a non-null raw `kiocb` pointer and a lifetime marker for private data type `T`. `T` must implement `ForeignOwnable`. `from_raw` constructs the wrapper, `as_raw` returns the C pointer, `file()` borrows `ki_filp->private_data` as `T::Borrowed`, `ki_pos()` reads the current offset, and `ki_pos_mut()` exposes mutable access to the position.

## Control Flow
Callback glue calls unsafe `from_raw` once the kernel passes a valid `kiocb`. Methods then directly read the embedded `ki_filp` and `ki_pos` fields. Private data borrowing is delegated to the `ForeignOwnable` contract so wrappers can recover Rust driver/filesystem state stored in C.

## State and Persistence
The wrapper owns no state. It borrows the callback-local `kiocb`, whose position and file pointer are owned by VFS. Mutating `ki_pos` updates the live callback object.

## Dependencies and Integration Points
It integrates with VFS async/sync file operation callbacks and Rust-owned private data stored as C `void *`. It depends on `kernel::types::ForeignOwnable`.

## Risks
`from_raw` is unsafe because a null or wrong-type `kiocb` would make later field access invalid. `file()` assumes private data has type `T`; a mismatch can violate aliasing or lifetime invariants. `ki_pos_mut()` requires exclusive wrapper access to avoid concurrent offset mutation.

## Test Signals
File operation tests should verify correct private-data recovery, read/write callback position updates, invalid private-data assumptions caught by review, and offset behavior across repeated operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/fs/kiocb.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/generated_arch_reachable_asm.rs.S -->
# sources/distributed-fs/ceph-client/rust/kernel/generated_arch_reachable_asm.rs.S

## Purpose
This generated assembly-template source emits the architecture-specific Rust literal for reachable warning sites. It is part of the build glue that extracts C macro expansions into Rust-accessible constants.

## Important APIs, Types, and Functions
The file includes `<linux/bug.h>` and invokes `::kernel::concat_literals!(ARCH_WARN_REACHABLE)` after the marker comment. There are no Rust functions or runtime types.

## Control Flow
Build tooling preprocesses this `.S` file so `ARCH_WARN_REACHABLE` is expanded by the C preprocessor and concatenated into Rust literal output. Runtime code never executes this file directly.

## State and Persistence
There is no runtime state. The persistent artifact is generated build output used by Rust-side architecture warning helpers.

## Dependencies and Integration Points
It depends on the C architecture implementation of `ARCH_WARN_REACHABLE` and the Rust `concat_literals!` macro. It integrates with generated Rust kernel assembly support.

## Risks
Architecture macro signature or include changes can break preprocessing. Because this is generated glue, formatting or marker changes may break the extraction pipeline.

## Test Signals
Build tests on supported architectures should confirm preprocessing succeeds and the generated Rust literal matches the architecture's expected warning sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/generated_arch_reachable_asm.rs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/generated_arch_static_branch_asm.rs.S -->
# sources/distributed-fs/ceph-client/rust/kernel/generated_arch_static_branch_asm.rs.S

## Purpose
This generated template extracts the architecture-specific static branch assembly macro into Rust literal form for jump-label support.

## Important APIs, Types, and Functions
The file includes `<linux/jump_label.h>` and calls `::kernel::concat_literals!(ARCH_STATIC_BRANCH_ASM("{symb} + {off} + {branch}", "{l_yes}"))`. It has no runtime functions.

## Control Flow
During build, the C preprocessor expands `ARCH_STATIC_BRANCH_ASM` with placeholder operands. The Rust macro concatenates emitted string fragments so generated Rust code can embed the resulting assembly template.

## State and Persistence
No runtime state exists. The preprocessed generated literal is a build artifact consumed by Rust static branch support.

## Dependencies and Integration Points
It depends on architecture jump-label macro definitions and Rust build tooling that recognizes the marker and macro output.

## Risks
Placeholder argument changes, architecture macro changes, or include ordering can invalidate generated output. Cross-architecture differences must remain compatible with Rust-side consumers.

## Test Signals
Compile on architectures with static branch support and compare generated strings against C expectations for symbol, offset, branch, and label substitutions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/generated_arch_static_branch_asm.rs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/generated_arch_warn_asm.rs.S -->
# sources/distributed-fs/ceph-client/rust/kernel/generated_arch_warn_asm.rs.S

## Purpose
This generated template extracts architecture-specific warning assembly into Rust-accessible literal form.

## Important APIs, Types, and Functions
The file includes `<linux/bug.h>` and calls `::kernel::concat_literals!(ARCH_WARN_ASM("{file}", "{line}", "{flags}", "{size}"))`. It defines no runtime functions.

## Control Flow
The build preprocesses the file, expands `ARCH_WARN_ASM` with placeholder file, line, flags, and size arguments, and converts the expansion into concatenated Rust literals.

## State and Persistence
There is no runtime state. Generated assembly strings persist as build output.

## Dependencies and Integration Points
The file is tied to C `ARCH_WARN_ASM` macro definitions and Rust-side generated warning support.

## Risks
The macro's argument shape must stay synchronized with the template. Any architecture-specific syntax not representable in the concatenation path can break Rust warning generation.

## Test Signals
Architecture build coverage should verify successful preprocessing and correct generated warning assembly for normal Rust warning sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/generated_arch_warn_asm.rs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/gpu.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/gpu.rs

## Purpose
`gpu.rs` is the top-level GPU subsystem module for Rust kernel abstractions.

## Important APIs, Types, and Functions
It conditionally exposes `pub mod buddy` when `CONFIG_GPU_BUDDY = "y"`.

## Control Flow
There is no runtime control flow. Module availability follows kernel configuration.

## State and Persistence
No state is defined. GPU allocator state is in `gpu/buddy.rs` when compiled in.

## Dependencies and Integration Points
The file integrates the Rust GPU buddy allocator wrapper into the public `kernel::gpu` namespace and respects Kconfig gating.

## Risks
Users must guard imports or feature use by configuration. Missing `CONFIG_GPU_BUDDY` means `kernel::gpu::buddy` is unavailable.

## Test Signals
Build matrix coverage should include configurations with and without `CONFIG_GPU_BUDDY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/gpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/gpu/buddy.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/gpu/buddy.rs

## Purpose
`gpu/buddy.rs` provides a Rust RAII and locking wrapper around the C GPU buddy allocator. It manages a contiguous GPU address space with power-of-two blocks, supports range/top-down/simple allocation modes, and automatically frees allocated block lists.

## Important APIs, Types, and Functions
`GpuBuddyAllocMode` selects simple, range-constrained, or top-down allocation. `GpuBuddyAllocFlags` and `GpuBuddyAllocFlag` are generated by `impl_flags!` for contiguous, clear, and trim-disable modifiers. `GpuBuddyParams` carries base offset, total size, and chunk alignment. `GpuBuddy` wraps `Arc<GpuBuddyInner>` and exposes `new`, `base_offset`, `chunk_size`, `size`, `avail`, and `alloc_blocks`. `AllocatedBlocks` owns a C list of `gpu_buddy_block`s and exposes `is_empty` and `iter`. `AllocatedBlock` reports absolute offset, order, and byte size.

## Control Flow
`GpuBuddy::new` pin-initializes `GpuBuddyInner`, calls `gpu_buddy_init`, initializes a mutex, and caches parameters. Allocation clones the inner `Arc`, initializes a `CListHead`, validates non-empty ranges, locks the allocator, and calls `gpu_buddy_alloc_blocks`. Iteration uses `clist_create!` to view the C intrusive list as `Block` wrappers. Dropping `AllocatedBlocks` locks the allocator and calls `gpu_buddy_free_list`; dropping the final buddy inner calls `gpu_buddy_fini`.

## State and Persistence
Allocator state lives in the C `gpu_buddy` object behind `Opaque`. The mutex serializes all allocation, free, avail, and fini operations. Allocated block lists persist until their `AllocatedBlocks` owner drops. The `Arc` keeps the allocator alive for outstanding allocations.

## Dependencies and Integration Points
The module depends on C `include/linux/gpu_buddy.h`, `Arc`, `Mutex`, pin-init, `Alignment`, `CListHead`, and the interop list iterator. It is the Rust-facing allocator for GPU memory managers that still use the C buddy implementation.

## Risks
Correctness depends on all C allocator operations being under the wrapper mutex. `AllocatedBlocks::iter` assumes the list is not concurrently modified while borrowed. `AllocatedBlock::size` shifts chunk size by block order; invalid C block metadata would overflow or misrepresent size. Range allocation rejects empty ranges but otherwise relies on the C allocator for size/alignment constraints.

## Test Signals
Tests should cover simple, top-down, range, fragmented, contiguous-failure, clear/trim flags, empty-range error, `avail` accounting before and after drop, iterator block offsets/sizes, and concurrent allocation/free stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/gpu/buddy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/i2c.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/i2c.rs

## Purpose
`i2c.rs` implements Rust abstractions for I2C drivers, device IDs, adapters, clients, board info, and manual client registration. It connects Rust driver traits to the C I2C driver model.

## Important APIs, Types, and Functions
`DeviceId` wraps `i2c_device_id` and implements raw ID traits. `i2c_device_table!` emits an ID array and module alias. `Adapter<T>` implements `driver::DriverLayout`, `RegistrationOps`, and `driver::Adapter` for any Rust `Driver`. `module_i2c_driver!` declares a module driver. The `Driver` trait defines ID tables, `probe`, optional `shutdown`, and optional `unbind`. `I2cAdapter`, `I2cBoardInfo`, `I2cClient`, and `Registration` wrap C adapter, board-info, client, and manually registered client lifetimes.

## Control Flow
Driver registration statically requires at least one ACPI, OF, or legacy I2C ID table, fills `struct i2c_driver` callbacks and match tables, then calls `i2c_register_driver`. Probe casts the C client to `I2cClient<CoreInternal>`, obtains ID info from I2C or generic ACPI/OF matching, calls `T::probe`, and stores pinned driver data as device drvdata. Remove and shutdown borrow that drvdata and dispatch to `T::unbind` or `T::shutdown`. Manual client registration uses `i2c_new_client_device`, converts error pointers and null, and unregisters in `Drop`.

## State and Persistence
Registered drivers persist until unregistered by the driver core. Per-client Rust driver state is pinned in drvdata after successful probe. `I2cAdapter` and `I2cClient` are reference-counted through C device/I2C references. `Registration` owns one created client device and unregisters it on drop.

## Dependencies and Integration Points
This file integrates with the generic Rust driver framework, device context system, ACPI and OF ID tables, `module_device_table!`, `Devres`, `ARef`, device drvdata storage, and C I2C core APIs including `i2c_register_driver`, `i2c_match_id`, `i2c_get_adapter`, `i2c_verify_client`, and `i2c_new_client_device`.

## Risks
Callback casts rely on I2C core passing valid `struct i2c_client` pointers. Drvdata borrow in remove/shutdown assumes probe completed and stored the expected type. Compile-time ID string limits are 20 bytes including NUL. `I2cAdapter::get` must balance references through `AlwaysRefCounted`. Manual registration must handle both error pointers and null returns.

## Test Signals
Test driver registration with each ID table type, missing-table compile failure, probe/remove/shutdown callback order, ID info lookup priority, adapter get/put lifecycle, `Device` to `I2cClient` conversion success/failure, manual client devres cleanup, and ID string length assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/i2c.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/id_pool.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/id_pool.rs

## Purpose
`id_pool.rs` implements a dynamic bitmap-backed ID allocator. It lets callers find, acquire, release, grow, and shrink numeric IDs while separating allocation of replacement bitmaps from mutation of the pool.

## Important APIs, Types, and Functions
`IdPool` owns a `BitmapVec`. `ReallocRequest` records a target capacity, and `PoolResizer` owns a preallocated replacement bitmap. `IdPool::new`, `with_capacity`, `capacity`, `find_unused_id`, `release_id`, `grow_request`, `grow`, `shrink_request`, and `shrink` form the API. `UnusedId` represents a discovered free bit and exposes `as_usize`, `as_u32`, and consuming `acquire`.

## Control Flow
Clients call `find_unused_id(offset)`, inspect the result if needed, and must call `acquire` to set the bit. If no free bit exists, clients can request a grow, drop locks, allocate a `PoolResizer`, reacquire locks, and call `grow`; `grow` rechecks whether the new bitmap is still larger. Shrink follows a similar request/realloc/apply pattern and rechecks that the last set bit still permits shrinking.

## State and Persistence
The bitmap records allocated IDs in memory only. Capacity starts inline or at requested size, doubles on grow requests, and shrinks by half or to inline size when usage is in the first quarter or empty. The API itself is not synchronized; callers provide locking for shared pools.

## Dependencies and Integration Points
The module depends on `BitmapVec` and allocation flags. It is intended for kernel subsystems needing compact integer handles while allowing allocation outside spinlocks.

## Risks
`UnusedId` does not reserve the bit until `acquire`; callers must not drop it without understanding the ID remains available. `release_id` does not validate ownership and can clear an already-free or out-of-range bit if misused. Grow/shrink are robust to races only if callers serialize actual pool mutation.

## Test Signals
Exercise full allocation to capacity, release/reuse, offset search, grow under contention with stale resizers, shrink when empty and when high bits remain set, max-capacity refusal, and `as_u32` bounds assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/id_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/impl_flags.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/impl_flags.rs

## Purpose
`impl_flags.rs` provides a macro for declaring compact bitflag and individual flag types with standard bitwise operators and containment helpers.

## Important APIs, Types, and Functions
The exported `impl_flags!` macro consumes a tuple-struct bitmask declaration and an enum of individual flags. It generates `#[repr(transparent)]` flag set struct, `#[repr($ty)]` flag enum, conversions to/from the storage type, `BitOr`, `BitAnd`, `BitXor`, `Not`, assignment operators for both set and single-flag operands, `empty`, `all_bits`, `contains`, `contains_any`, and `contains_all`.

## Control Flow
Expansion-time code builds all operators around the underlying integer. XOR and NOT mask with `all_bits()` so inverted/toggled values cannot set bits outside the declared flag set. Individual enum values can be directly combined, producing the bitmask struct.

## State and Persistence
Generated flag values are plain copyable integer wrappers with no runtime global state.

## Dependencies and Integration Points
The macro is used by wrappers such as `gpu/buddy.rs` to expose C flag constants with Rust operator ergonomics. It depends only on core conversion and operator traits.

## Risks
The macro assumes declared enum values are valid, non-conflicting bit masks. `all_bits()` ORs every declared value; multi-bit flags are allowed but can make containment semantics surprising. It does not generate debug formatting unless the caller derives it.

## Test Signals
Macro tests should cover combining individual flags, assignment operators, contains/all/any behavior, XOR and NOT masking, empty masks, conversion to raw storage, and multi-flag use sites such as GPU buddy allocation flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/impl_flags.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/init.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/init.rs

## Purpose
`init.rs` extends the `pin-init` crate for kernel allocation and initialization patterns. It provides smart-pointer in-place initialization traits and kernel-default fallible initializer macros.

## Important APIs, Types, and Functions
`InPlaceInit<T>` abstracts smart pointers that can allocate and initialize `T` in place. It defines `try_pin_init`, `pin_init`, `try_init`, and `init`, with `PinnedSelf` for pointer-specific pinning behavior. The exported `try_init!` and `try_pin_init!` macros wrap `pin_init` macros with default error type `crate::error::Error`.

## Control Flow
`pin_init` and `init` convert initializer error types into kernel `Error` by wrapping user initializers in unsafe closures that delegate to `__pinned_init`. Smart pointer implementations perform allocation with `Flags` and either run pin or non-pin initialization. The macros pass through to the underlying crate with a default error attribute.

## State and Persistence
The file defines initialization mechanics only. Any persistent state is created in the target object and smart pointer chosen by callers.

## Dependencies and Integration Points
It depends on `pin_init::{Init, PinInit}`, kernel allocation flags, `AllocError`, and `Error`. Many wrappers in this subset use the macros for safe construction of pinned C-backed structs, including GPU buddy lists and devres-managed mappings.

## Risks
Unsafe initializer closures must maintain pin-init rules: no references to uninitialized fields, correct cleanup on failure, and full initialization before success. Incorrect smart pointer implementations can cause moves of pinned data or leaks after partial initialization.

## Test Signals
Compile and runtime tests should cover fallible initialization success, allocation failure, conversion of custom errors to `Error`, pinned non-`Unpin` types, and partial initialization cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/init.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/interop.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/interop.rs

## Purpose
`interop.rs` is the namespace for low-level Rust-to-C kernel interoperability helpers.

## Important APIs, Types, and Functions
It declares `pub mod list`, exposing C intrusive list helpers.

## Control Flow
No runtime logic exists in this facade. It intentionally keeps interop utilities separate from ordinary Rust data structures.

## State and Persistence
No state is held here.

## Dependencies and Integration Points
The module is used by wrappers that must interact with C-owned structures, such as the GPU buddy allocator's list of allocated blocks.

## Risks
The module comment warns that these helpers are not general-purpose Rust collections. Misuse can bypass safer Rust ownership models.

## Test Signals
Build tests should verify `kernel::interop::list` remains available for intended low-level modules and that higher-level code uses safer native collections where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/interop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/interop/list.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/interop/list.rs

## Purpose
`interop/list.rs` provides Rust read/iteration wrappers for C `struct list_head` intrusive circular lists. It is intended for direct C interop, not as a native Rust list.

## Important APIs, Types, and Functions
`CListHead` wraps a `list_head` sentinel or node, with `from_raw`, `as_raw`, `next`, `is_linked`, and `new`. `CList<T, OFFSET>` views a sentinel as a typed list. `CListIter` yields `&T` by subtracting the embedded list offset. The exported `clist_create!` macro verifies the field path has type `list_head`, computes `offset_of!`, and calls `CList::from_raw`.

## Control Flow
Creation either initializes a standalone empty `list_head` with `INIT_LIST_HEAD` or casts an existing raw sentinel. Iteration starts from `head.next()`, stops when it returns to the sentinel, and converts each node to its containing item using the constant offset.

## State and Persistence
The wrapper does not own list items. It borrows a C-managed list for the lifetime of the returned reference. `CListHead::new` owns only a sentinel head used by other C APIs.

## Dependencies and Integration Points
The module depends on C `list_head`, `INIT_LIST_HEAD`, `Opaque`, pin-init, and `offset_of!`. `gpu/buddy.rs` uses it to iterate C `gpu_buddy_block` lists.

## Risks
Safety depends on the list not being concurrently modified during iteration and on `OFFSET` matching the real embedded field. `is_linked` treats an empty sentinel as not linked, which is correct for sentinel emptiness but not a full membership proof for arbitrary nodes. Wrong transparent wrapper layout can produce invalid references.

## Test Signals
Doctests and integration tests should cover empty and non-empty lists, field-offset validation, iteration order, fused iterator behavior, initialized sentinel creation, and C-owned item wrapper layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/interop/list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/io.rs

## Purpose
`io.rs` is the core Rust memory-mapped I/O abstraction. It defines raw and typed MMIO regions, generic I/O capability traits, typed register-location support, checked read/write/update helpers, and relaxed accessor views.

## Important APIs, Types, and Functions
It exposes submodules `mem`, `poll`, `register`, and `resource`, re-exports the `register!` macro and `Resource`, and defines `PhysAddr` and `ResourceSize`. `MmioRaw<SIZE>` stores base address and maximum size. `Mmio<SIZE>` is the checked accessor wrapper. `IoCapable<T>` supplies backend reads/writes. `IoLoc<T>` maps offsets or register locations to an offset and storage type. `Io` provides `try_read*`, `try_write*`, `try_read`, `try_write`, `try_write_reg`, `try_update`, compile-time checked `read*`/`write*`, `write_reg`, and `update`. `IoKnownSize` enables compile-time bounds via `MIN_SIZE`. `RelaxedMmio` uses relaxed MMIO functions.

## Control Flow
Bus-specific code creates an `MmioRaw` after mapping a region, then exposes it as `Mmio` via unsafe `from_raw`. Runtime-checked operations call `io_addr`, validating alignment, size, and overflow, then invoke `IoCapable`. Compile-time checked operations require `IoKnownSize` and use `build_assert!` in `io_addr_assert`. `relaxed()` transmutes an `Mmio` reference into `RelaxedMmio` to change the underlying read/write functions without changing bounds behavior.

## State and Persistence
`MmioRaw` stores only base virtual address and mapped size. The actual hardware state is external MMIO device state. No synchronization is provided; callers must serialize read-modify-write updates when required.

## Dependencies and Integration Points
The file integrates with architecture MMIO bindings (`readb`, `writeb`, `readl_relaxed`, etc.), `io::register` generated types, bus mapping wrappers in `io::mem`, and drivers needing typed hardware register access.

## Risks
Unsafe construction must only wrap valid mapped I/O memory. Compile-time checked methods rely on constant offsets so `build_assert!` can enforce bounds. `try_update`/`update` are not atomic with respect to hardware or other CPUs. Relaxed accessors do not provide ordering with DMA or memory accesses.

## Test Signals
Test runtime rejection of out-of-bounds, overflow, and misaligned offsets; compile-time checked access for fixed-size regions; u8/u16/u32 and cfg-gated u64 access; typed register reads/writes; relaxed accessor selection; and update closure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/mem.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/io/mem.rs

## Purpose
`io/mem.rs` maps device resources into MMIO accessors and optionally reserves exclusive resource regions. It provides devres-managed `IoMem` and `ExclusiveIoMem` initializers for bus drivers.

## Important APIs, Types, and Functions
`IoRequest<'a>` pairs a bound device with a `Resource`. It exposes `iomap_sized`, `iomap_exclusive_sized`, `iomap`, and `iomap_exclusive`. `IoMem<SIZE>` owns an `MmioRaw<SIZE>` and derefs to `Mmio<SIZE>`. `ExclusiveIoMem<SIZE>` owns an `IoMem` plus a `Region` reservation and derefs to `Mmio`.

## Control Flow
Subsystem code creates an `IoRequest` after validating a resource belongs to a device. Mapping converts resource size to `usize`, rejects zero length, chooses `ioremap_np` when `IORESOURCE_MEM_NONPOSTED` is set and `ioremap` otherwise, and wraps the returned address in `MmioRaw`. Exclusive mapping first calls `request_region` on the resource, then maps. Both constructors return `Devres` pin initializers so cleanup occurs during device unbind. `IoMem::drop` calls `iounmap`; `Region::drop` releases exclusivity.

## State and Persistence
The mapped virtual address persists for the `IoMem` lifetime. `ExclusiveIoMem` also holds a busy resource reservation. Device-managed resources persist until the bound device releases devres or the object is otherwise dropped.

## Dependencies and Integration Points
This file depends on `Device<Bound>`, `Devres`, `Resource`, `Region`, `MmioRaw`, `ioremap`, `ioremap_np`, and `iounmap`. Platform and other bus abstractions can return `IoRequest` values to drivers.

## Risks
`IoRequest::new` is unsafe because callers must prove the resource remains valid for the device. Size conversion can fail on platforms where resource size exceeds CPU addressable mapping type. Exclusive mapping currently requests the whole resource range. Mapping a wrong or already busy resource can fail or cause undefined device behavior.

## Test Signals
Tests should cover sized versus dynamic maps, zero-size rejection, nonposted resource choosing `ioremap_np`, exclusive reservation conflicts, devres cleanup order, and read/write through returned `Mmio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/mem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/poll.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/io/poll.rs

## Purpose
`io/poll.rs` provides Rust equivalents of common kernel read-poll-timeout helpers for waiting on hardware state in sleepable and atomic contexts.

## Important APIs, Types, and Functions
`read_poll_timeout` repeatedly runs a fallible operation until a condition succeeds or a monotonic timeout expires, sleeping with `fsleep`. `read_poll_timeout_atomic` repeats a fixed number of attempts, delaying with `udelay` and never sleeping.

## Control Flow
The sleepable function records `Instant::now`, calls `might_sleep`, then loops: run `op`, return on `cond`, return `ETIMEDOUT` if elapsed time exceeds timeout, optionally `fsleep`, and `cpu_relax`. The atomic variant loops `retry` times with the same op/condition check, optional busy delay, and CPU relax, then returns `ETIMEDOUT`.

## State and Persistence
No persistent state exists. The only state is loop-local timing, retry count, and the last operation result.

## Dependencies and Integration Points
It depends on `Delta`, `Instant<Monotonic>`, `fsleep`, `udelay`, `cpu_relax`, `might_sleep`, and `ETIMEDOUT`. Drivers use it with `Io::try_read*` closures for hardware readiness polling.

## Risks
The sleepable version unconditionally calls `might_sleep`, so it must not be used in atomic context. Timeout is checked after an operation, so a slow `op` can exceed timeout before the error is returned. The atomic version uses retry count rather than wall-clock timeout.

## Test Signals
Tests should cover immediate success, success after several attempts, operation error propagation, timeout behavior, zero sleep/delay values, retry count zero, and context checking for sleepable use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/poll.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/register.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/io/register.rs

## Purpose
`io/register.rs` implements the `register!` macro and supporting traits for type-safe hardware register definitions. It lets drivers model fixed, relative, array, and relative-array registers with generated bitfield accessors and integration with `Io`.

## Important APIs, Types, and Functions
Core traits include `Register`, `FixedRegister`, `RegisterBase`, `WithBase`, `RelativeRegister`, `RegisterArray`, `Array`, `RelativeRegisterArray`, and `LocatedRegister`. Location types include `FixedRegisterLoc`, `RelativeRegisterLoc`, `RegisterArrayLoc`, and `RelativeRegisterArrayLoc`. The `register!` macro generates transparent register value structs, raw conversions, `Zeroable`, `IoLoc` implementations, array metadata, field masks/ranges/shifts, getters, setters, `try_with_*`, const setters, and `Debug`.

## Control Flow
Macro input is dispatched by declaration shape: fixed address, alias, relative base plus offset, fixed array, relative array, and aliases into arrays. Generated location builders compute offsets by fixed offset, base plus offset, or index times stride; compile-time builders use `build_assert`, while `try_at` returns `None` for runtime out-of-range indexes. Field getters use bounded shifts; setters clear the field mask and OR shifted bounded values.

## State and Persistence
Generated register values are plain copyable snapshots of raw storage. Locations are zero-sized or index-carrying values. Hardware state is read/written by `Io`, not stored in this module.

## Dependencies and Integration Points
The module integrates tightly with `IoLoc` and `Io::read/write/update`, `kernel::num::Bounded`, `TryIntoBounded`, `pin_init::Zeroable`, `build_assert`, and macro paste support. It is a key driver ergonomics layer for MMIO register maps.

## Risks
Bit ranges must fit the storage type and not overlap unintentionally; the macro does not enforce all semantic register constraints. Compile-time index validation requires constant inputs. Aliases share offsets but can expose different fields, so incorrect aliasing can make code write incompatible layouts. `Debug` reads generated field getters and may include fallible conversion results.

## Test Signals
Macro tests should cover all declaration forms, aliases, stride validation, fixed and relative arrays, runtime and compile-time index checks, field get/set for full-width and sub-width fields, fallible conversion accessors, debug output, and integration with `Io` read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/register.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/resource.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/io/resource.rs

## Purpose
`io/resource.rs` wraps Linux `struct resource` and requested resource regions. It exposes resource metadata and RAII release for busy I/O or memory ranges.

## Important APIs, Types, and Functions
`Region` owns a non-null resource returned by `__request_region` and the `CString` name passed to C. It derefs to `Resource` and releases in `Drop`. `Resource` wraps `bindings::resource` and provides `from_raw`, `request_region`, `size`, `start`, `name`, and `flags`. `Flags` wraps resource flag bits with `contains`, bitwise operators, and constants `IORESOURCE_IO`, `IORESOURCE_MUXED`, `IORESOURCE_MEM`, and `IORESOURCE_MEM_NONPOSTED`.

## Control Flow
`request_region` calls `__request_region` with start, size, name pointer, and flags. A null return means the region was unavailable. `Region::drop` inspects flags to call `release_mem_region` for memory ranges or `release_region` otherwise. Resource accessors directly read C fields or call `resource_size`.

## State and Persistence
`Resource` is a borrowed view of C resource state. `Region` owns an active busy reservation until dropped and keeps the name allocation alive because C stores its pointer.

## Dependencies and Integration Points
This module is used by `io::mem` exclusive mapping and bus resource wrappers. It depends on C ioport resource APIs and kernel `CString`.

## Risks
`Resource::from_raw` is unsafe and requires the pointer to remain valid and exclusively accessed through the returned reference. Dropping `Region` chooses release function based on current flags; inconsistent flags could release through the wrong API. Callers must pass correct start/size subranges.

## Test Signals
Tests should cover successful and conflicting reservations, memory versus I/O release paths, null resource names, nonposted flag detection, flag operators, and name lifetime through drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/io/resource.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/ioctl.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/ioctl.rs

## Purpose
`ioctl.rs` provides Rust const helpers for constructing and decoding Linux ioctl command numbers using the asm-generic bit layout.

## Important APIs, Types, and Functions
Internal `_IOC` builds a command from direction, type, number, and size with `build_assert` bounds checks. Public constructors `_IO`, `_IOR<T>`, `_IOW<T>`, and `_IOWR<T>` encode no-arg, read, write, and read-write commands. Public decoders `_IOC_DIR`, `_IOC_TYPE`, `_IOC_NR`, and `_IOC_SIZE` extract fields.

## Control Flow
All operations are const arithmetic. Constructors validate each field against UAPI masks, shift into the correct positions, and OR the result. Typed constructors use `size_of::<T>()`.

## State and Persistence
No state is stored. The output is a `u32` ioctl number.

## Dependencies and Integration Points
The module depends on generated `uapi` ioctl constants and `build_assert`. Rust drivers can use it to define ioctl command constants matching C macros.

## Risks
The size field uses the Rust type layout; command ABIs must use `#[repr(C)]` or otherwise ABI-stable types. Direction names follow ioctl convention from the user pointer perspective, which can be confusing. Oversized types fail at compile time.

## Test Signals
Compare generated constants against C `_IO*` values for representative types, test field decoders, and verify compile-time rejection of out-of-range type/number/size values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/ioctl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/iommu/mod.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/iommu/mod.rs

## Purpose
`iommu/mod.rs` is the Rust IOMMU support namespace.

## Important APIs, Types, and Functions
It exposes `pub mod pgtable`.

## Control Flow
There is no runtime control flow.

## State and Persistence
No state is defined here; page table state is owned by `iommu/pgtable.rs`.

## Dependencies and Integration Points
The module makes Rust IOMMU page table wrappers available under `kernel::iommu::pgtable`.

## Risks
Only page-table support is exposed. Broader IOMMU domain/device APIs are not represented in this facade.

## Test Signals
Build tests should verify `kernel::iommu::pgtable` imports and configuration coverage for users that depend on it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/iommu/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/iommu/pgtable.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/iommu/pgtable.rs

## Purpose
`iommu/pgtable.rs` wraps Linux `io_pgtable_ops` for Rust users. It supports allocating typed IOMMU page tables, mapping and unmapping pages, and accessing ARM64 LPAE S1 configuration values.

## Important APIs, Types, and Functions
`prot` exports IOMMU protection flags. `Config` carries quirks, page-size bitmap, IAS/OAS, and coherent-walk settings. `IoPageTable<F>` owns an `io_pgtable_ops` pointer parameterized by an `IoPageTableFmt`. `IoPageTableFmt` provides the C format enum. `IoPageTable::new`, unsafe `new_raw`, `raw_ops`, `raw_pgtable`, `raw_cfg`, unsafe `map_pages`, and unsafe `unmap_pages` form the main API. `NOOP_FLUSH_OPS` supplies no-op TLB callbacks. `ARM64LPAES1` implements the format and exposes unsafe `ttbr` plus `mair`.

## Control Flow
Construction fills `io_pgtable_cfg`, points TLB ops at no-op flush callbacks, sets the device pointer, and calls `alloc_io_pgtable_ops`. Mapping obtains the non-null `map_pages` function, passes IOVA, physical address, page size/count, protection flags, allocation flags, and a mapped-byte out parameter, then returns both mapped length and `Result`. Unmapping calls `unmap_pages` and returns the unmapped byte count. Drop frees the ops.

## State and Persistence
The page table and its configuration live in kernel memory allocated by io-pgtable code and persist until `IoPageTable` drops. The devres constructor ties lifetime to device unbind; unsafe `new_raw` requires callers to drop before device unbind. Mappings persist until unmapped or table destruction.

## Dependencies and Integration Points
It integrates with Linux `io-pgtable.h`, device devres, allocation flags, physical addresses, IOMMU protection flags, and GPU firmware users that manage their own IOTLB invalidation using ranges.

## Risks
Mapping/unmapping are unsafe because callers must serialize access to the affected IOVA range and avoid overlaps. No-op flush ops are correct only for users that handle invalidation elsewhere. `ttbr` is unsafe because users must stop device use before dropping the table. Partial map/unmap results require caller cleanup logic.

## Test Signals
Tests should cover allocation failure, raw/devres lifetime, map success and partial failure cleanup, unmap counts, ARM64 `ttbr`/`mair` reads, page-size/protection combinations, and external TLB invalidation integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/iommu/pgtable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/iov.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/iov.rs

## Purpose
`iov.rs` provides Rust wrappers for Linux `struct iov_iter` sources and destinations. It separates readable and writable iterator directions at the type level and exposes safe copying helpers for kernel buffers and vectors.

## Important APIs, Types, and Functions
`IovIterSource<'data>` wraps an iterator with `data_source == ITER_SOURCE`; `IovIterDest<'data>` wraps `ITER_DEST`. Both provide unsafe `from_raw`, `as_raw`, `len`, `is_empty`, `advance`, and unsafe `revert`. Source adds `copy_from_iter`, `copy_from_iter_vec`, and `copy_from_iter_raw`. Destination adds `copy_to_iter` and `simple_read_from_buffer`.

## Control Flow
`from_raw` asserts the C iterator direction matches the wrapper type before casting. Copy-from operations reserve vector capacity when needed, call `_copy_from_iter`, and set initialized length only for bytes C reports as written. Copy-to calls `_copy_to_iter`. `simple_read_from_buffer` validates nonnegative position, handles EOF, copies from the current offset, and advances `ppos` by bytes written.

## State and Persistence
The wrapper mutates the underlying C iterator's count and position as copy/advance/revert operations occur. It does not own the backing user/kernel memory. The types are intentionally not `Send` because data can be thread-locally mapped.

## Dependencies and Integration Points
It depends on C iov iterator helpers, allocation `Vec` and `Allocator`, `MaybeUninit`, `Opaque`, and VFS read/write iterator callbacks. `simple_read_from_buffer` is useful for pseudo-files exposing static content.

## Risks
`from_raw` is unsafe and direction assertions can panic if C passes the wrong iterator kind. `len()` may overestimate available bytes because user memory faults can terminate copying early. `revert` can underflow logical iterator position if caller passes too many bytes. Destination and source wrappers must not be confused.

## Test Signals
Test source and destination direction assertions, partial copies, vector append initialization, EOF and negative offset handling in `simple_read_from_buffer`, advance/revert bounds, and user-memory fault behavior through integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/iov.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/irq.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/irq.rs

## Purpose
`irq.rs` is the top-level Rust IRQ abstraction module. It exposes interrupt registration flags and request/handler types.

## Important APIs, Types, and Functions
It declares private `flags` and `request` modules, re-exports `flags::Flags`, and re-exports `Handler`, `IrqRequest`, `IrqReturn`, `Registration`, `ThreadedHandler`, `ThreadedIrqReturn`, and `ThreadedRegistration` from `request`.

## Control Flow
No runtime control flow is defined here. It controls the public namespace for IRQ helpers.

## State and Persistence
No state is stored in this facade. IRQ registration state is owned by the request submodule and C IRQ core.

## Dependencies and Integration Points
The module maps to Linux interrupt handling APIs and is used by drivers registering hard IRQ or threaded IRQ handlers.

## Risks
The visible API depends on `request.rs`, which is not part of this work item. Users importing from this facade must respect handler lifetime and context rules defined there.

## Test Signals
Build tests should verify the re-exported IRQ names remain stable and can be imported from `kernel::irq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/irq.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/irq/flags.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/irq/flags.rs

## Purpose
`irq/flags.rs` wraps Linux IRQ registration flags in a Rust bitmask type with documented constants and bitwise operators.

## Important APIs, Types, and Functions
`Flags(c_ulong)` exposes constants for trigger modes, sharing, timer, per-CPU, balancing, polling, oneshot, suspend/resume, threading, auto-enable, and debug behavior. `into_inner` returns the raw `c_ulong` for request code. `BitOr`, `BitAnd`, and `Not` combine and manipulate masks. `new` compile-time checks that C `u32` constants fit in `c_ulong`.

## Control Flow
Callers combine constants with bitwise operators and pass the raw value to IRQ registration internals. Lower C IRQ layers validate invalid combinations, sharing mismatches, and trigger conflicts.

## State and Persistence
`Flags` values are plain copyable masks. Actual IRQ registration state persists in the C IRQ subsystem after request code consumes the flags.

## Dependencies and Integration Points
The module depends on C `IRQF_*` bindings and `build_assert`. It is re-exported by `irq.rs` and used by IRQ request wrappers.

## Risks
`Not` inverts all bits of `c_ulong`, not only known IRQ flags, so callers should use it carefully, usually in masks rather than direct registration. Semantic validity is not enforced by the Rust type.

## Test Signals
Tests should cover raw value conversion, OR/AND composition, representative trigger/shared/oneshot combinations, compile-time constant fit, and integration with IRQ registration failure paths for invalid combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/irq/flags.rs -->
