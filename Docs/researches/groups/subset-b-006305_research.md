# Research: subset-b-006305

Work item `subset-b-006305` covers Rust-for-Linux kernel support code under `sources/distributed-fs/ceph-client/rust/kernel`. The notes below are intentionally source-tree-aligned and each section is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec.rs

## Purpose
This file implements the kernel Rust `Vec<T, A>` abstraction: a growable contiguous array whose backing storage is allocated by a kernel allocator implementing `Allocator`. It provides allocator-specific aliases `KVec<T>`, `VVec<T>`, and `KVVec<T>`, plus the exported `kvec!` macro for convenient construction with `GFP_KERNEL`.

## Important APIs, Types, and Functions
The central type is `Vec<T, A: Allocator>`, storing `ptr: NonNull<T>`, `layout: ArrayLayout<T>`, `len`, and allocator phantom state. Public APIs include `new`, `with_capacity`, `capacity`, `len`, `is_empty`, `as_slice`, `as_mut_slice`, raw pointer accessors, `spare_capacity_mut`, `reserve`, `push`, `push_within_capacity`, `insert_within_capacity`, `pop`, `remove`, `truncate`, `clear`, `drain_all`, `retain`, `into_raw_parts`, and unsafe `from_raw_parts`. Clone-oriented APIs include `extend_with`, `extend_from_slice`, `from_elem`, and `resize`. `Vec<T, KVmalloc>::shrink_to` is a temporary allocator-specific shrinking path. Trait integrations include `Drop`, `Default`, `Debug`, `Deref`, `DerefMut`, `Borrow`, `BorrowMut`, `Index`, `IndexMut`, slice equality implementations, reference iteration, owning `IntoIter`, and `AsPageIter` for `VVec<T>`.

## Control Flow and State
Growth flows through `reserve`: if spare capacity is insufficient, it doubles capacity or uses the requested minimum, validates via `ArrayLayout`, and calls `A::realloc`. Element insertion writes into spare `MaybeUninit<T>` and then uses unsafe `inc_len` only after initialization. Removal and truncation use `dec_len` to transfer ownership of initialized tail ranges before reading or dropping them. `IntoIter` takes raw parts, advances a cursor with each `next`, and frees the original buffer in `Drop`; its `collect` path can move remaining elements to the start of the buffer and attempt a shrink. `DrainAll` sets vector length to zero immediately, then owns the former elements until iteration or drop.

## State and Persistence Behavior
The vector owns initialized elements in `[0, len)` and uninitialized allocation in `[len, capacity)`. Non-ZST vectors persist heap allocation until `Drop`, explicit raw-part handoff, or `KVVec::shrink_to(0)` for an empty vector. ZST vectors use a dangling pointer and report `usize::MAX` capacity without allocation. Raw-part APIs deliberately allow allocation ownership to leave the type, so reconstruction must use the same allocator type and exact layout constraints.

## Dependencies and Integration Points
This code depends on `Allocator`, `Kmalloc`, `Vmalloc`, `KVmalloc`, `ArrayLayout`, `Flags`, `NumaNode`, kernel `Box`, page iteration helpers, and low-level pointer/slice primitives. It integrates with Rust-for-Linux allocation conventions rather than `std::vec::Vec`, and with vmalloc pages through `AsPageIter` for page-oriented kernel operations.

## Risks
Most risk is around unsafe invariants: length must increase only after initialization, raw parts must match allocator/layout, `ptr::copy` ranges must be valid under insert/remove/retain, and `IntoIter::collect` must not double-drop moved elements. `KVVec::shrink_to` is especially sensitive because it distinguishes kmalloc versus vmalloc storage with `is_vmalloc_addr`, frees pages only when beneficial, and manually copies live elements. Allocation failure paths must leave the original vector intact.

## Test Signals
The file includes KUnit tests for `retain` over all boolean predicates up to length nine, and for `KVVec::shrink_to` preserving data, shrinking empty vectors to zero capacity, no-op behavior when the minimum exceeds current capacity, and respecting minimum capacity. Doc examples cover core push, resize, raw-parts, iteration, and page-iteration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec/errors.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec/errors.rs

## Purpose
This file defines small error types used by the kernel `Vec` implementation for operations that intentionally do not allocate or that validate indices.

## Important APIs, Types, and Functions
`PushError<T>(pub T)` is returned by `Vec::push_within_capacity` when a value cannot be appended without reallocating. `RemoveError` is returned by `Vec::remove` on an out-of-bounds index. `InsertError<T>` distinguishes `IndexOutOfBounds(T)` from `OutOfCapacity(T)` for `Vec::insert_within_capacity`, preserving ownership of the rejected element in both cases.

## Control Flow and State
Each error implements `fmt::Debug` without formatting the contained value, avoiding additional trait bounds on `T`. All three convert into kernel `Error` as `EINVAL`. The choice is explicit for capacity errors: a full vector is a caller contract failure for no-allocation insertion, not system-wide `ENOMEM`.

## State and Persistence Behavior
The generic error variants carry rejected elements by value, so failed insertions and pushes do not drop caller-owned data unexpectedly. The error values have no persistent external state.

## Dependencies and Integration Points
The file depends on `kernel::fmt`, `kernel::prelude::*`, and the kernel `Error`/`EINVAL` error model. It is re-exported from `kvec.rs`.

## Risks
The main semantic risk is callers assuming `OutOfCapacity` means memory pressure; conversion to `EINVAL` intentionally communicates that no allocation was attempted. Generic payload ownership must be preserved across all error handling.

## Test Signals
No direct tests live in this file. Usage is exercised through `kvec.rs` examples and tests for `push_within_capacity`, `insert_within_capacity`, and `remove`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/layout.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/layout.rs

## Purpose
This file provides `ArrayLayout<T>`, a small checked wrapper for array allocation layouts used by kernel allocator-backed containers.

## Important APIs, Types, and Functions
`LayoutError` marks invalid layout construction. `ArrayLayout<T>` stores an element count and enforces the invariant `len * size_of::<T>() <= isize::MAX`. It exposes `empty`, checked `new`, unsafe `new_unchecked`, `len`, `is_empty`, and `size`, and converts into `core::alloc::Layout`.

## Control Flow and State
`new` multiplies the requested length by element size with `checked_mul` and rejects overflow or sizes above `isize::MAX`. `new_unchecked` bypasses validation for callers that have already established the invariant. Conversion to `Layout` calls `Layout::array::<T>` and unwraps unchecked because `ArrayLayout`'s invariant should make failure impossible.

## State and Persistence Behavior
`ArrayLayout` is copyable and stores only the logical element count plus phantom type identity. It persists no allocation itself; it describes allocation size and alignment for other allocators and containers.

## Dependencies and Integration Points
The type depends only on `core::alloc::Layout` and `PhantomData`. It is used by `kvec.rs` to record vector capacity and to pass exact old/new layouts into allocator `realloc`/`free` calls.

## Risks
Incorrect use of `new_unchecked` can poison allocator calls with layouts exceeding pointer offset limits. Because `From<ArrayLayout<T>> for Layout` unwraps unchecked, invariant violations would become undefined behavior. ZST behavior requires care because `size()` is zero regardless of length.

## Test Signals
Doc examples validate normal construction and two failure modes: multiplication overflow and byte sizes above `isize::MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/layout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/auxiliary.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/auxiliary.rs

## Purpose
This file implements Rust abstractions for Linux auxiliary bus drivers and auxiliary device registration.

## Important APIs, Types, and Functions
`Adapter<T: Driver>` bridges Rust driver implementations to `driver::RegistrationOps` and `DriverLayout`. `module_auxiliary_driver!` declares a module exposing one auxiliary driver. `DeviceId` wraps `bindings::auxiliary_device_id`, builds `modname.name` IDs, and implements raw ID-table traits. `auxiliary_device_table!` creates a typed `IdArray` plus module alias. The `Driver` trait defines `IdInfo`, `ID_TABLE`, `probe`, and optional `unbind`. `Device<Ctx>` wraps `struct auxiliary_device`, exposes `id` and `parent`, implements bus-device and refcount traits, and is `Send`/`Sync`. `Registration` owns a registered auxiliary device and exposes `Registration::new` as a `Devres<Self>` initializer.

## Control Flow and State
Driver registration initializes `struct auxiliary_driver` fields (`name`, `probe`, `remove`, and `id_table`) before calling `__auxiliary_driver_register`; unregister delegates to `auxiliary_driver_unregister`. Probe casts the C device and matched ID into Rust wrappers, looks up ID info by `driver_data` index, invokes `T::probe`, and stores pinned driver data in device drvdata. Remove borrows that data and calls `T::unbind`. Device registration allocates a zeroed auxiliary device, fills parent/name/id/release, calls `auxiliary_device_init`, leaks the allocation to C lifetime management, calls `__auxiliary_device_add`, and rolls back with `auxiliary_device_uninit` on add failure.

## State and Persistence Behavior
Registered devices persist until `Registration::drop`, which calls `auxiliary_device_delete` and `auxiliary_device_uninit`. The leaked `KBox` is reclaimed in the device release callback when the final device reference drops. Driver private data is persisted in drvdata after successful probe and remains available for remove/unbind.

## Dependencies and Integration Points
The module integrates with kernel driver registration, device IDs, `Devres`, `device::Device`, `AlwaysRefCounted`, `KBox`, `PinInit`, and C auxiliary bus bindings. Parent device lifetime is tied to devres when `Registration::new` returns `Devres<Self>`.

## Risks
Safety depends on correct transparent casts between C and Rust wrappers, exact field offsets, and correct C callback sequencing. `DeviceId::new` copies C strings into a fixed-size C array without explicit runtime length checks, so callers must respect kernel ID size assumptions. Remove assumes probe succeeded and drvdata was set. Device memory is intentionally leaked until release; missing release or mismatched init/uninit would leak or double-free.

## Test Signals
No local KUnit tests are present. Test signals are compile-time type checking, macro expansion for driver/device tables, and runtime probe/remove behavior through auxiliary bus users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/auxiliary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bitmap.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/bitmap.rs

## Purpose
This file wraps Linux C bitmap APIs in Rust, providing borrowed `Bitmap` views and owned `BitmapVec` storage with inline or allocated representation.

## Important APIs, Types, and Functions
`Bitmap` is an unsized wrapper over a bit-length metadata slice and exposes unsafe `from_raw`, `from_raw_mut`, `as_ptr`, `as_mut_ptr`, and `len`. `BitmapVec` owns either a single inline `usize` bitmap or a `bitmap_zalloc` allocation via `BitmapRepr`, with constants `MAX_LEN` and `MAX_INLINE_LEN`. Bitmap operations include non-atomic `set_bit`/`clear_bit`, relaxed atomic `set_bit_atomic`/`clear_bit_atomic`, `copy_and_extend`, `last_bit`, `next_bit`, and `next_zero_bit`. `BitmapVec::new_inline`, `new`, and optional benchmark-only `fill_random` manage owned storage.

## Control Flow and State
`BitmapVec::new` selects inline zeroed storage for lengths up to one machine word, rejects sizes above `i32::MAX`, otherwise allocates zeroed C bitmap memory. Deref/DerefMut choose the correct pointer and build a borrowed `Bitmap` with bit-length metadata. Out-of-bounds mutating operations either panic under `CONFIG_RUST_BITMAP_HARDENED` or log and return under non-hardened builds. Search operations call C `_find_*` helpers and translate indexes at or beyond `len` into `None`.

## State and Persistence Behavior
Inline state lives directly in `BitmapVec::repr.bitmap`. Larger state persists in a C allocation freed by `Drop` through `bitmap_free`. Borrowed `Bitmap` references do not own memory and require the caller or owning `BitmapVec` to keep the backing storage alive.

## Dependencies and Integration Points
This module depends on `crate::bindings` for bitmap helpers, `AllocError`, allocation `Flags`, optional `pr_err!`, and kernel config gates. It is intended to interoperate with C APIs expecting `unsigned long *` bitmap storage.

## Risks
Atomic and non-atomic operations must not be mixed unsafely by callers. The unsized `Bitmap` cast relies on careful metadata interpretation: length is in bits while the backing memory is `usize` words. Non-hardened out-of-bounds behavior silently ignores writes after logging, which can hide caller bugs. Allocation length conversion to `u32` assumes prior `MAX_LEN` validation.

## Test Signals
KUnit tests cover borrowing raw arrays/words, allocation at several sizes, rejection of too-large lengths, set/clear/find semantics, non-hardened out-of-bounds behavior, and `copy_and_extend` clearing old destination bits. Hardened panic tests are noted but blocked by KUnit cfg/should-panic support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bitmap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bits.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/bits.rs

## Purpose
This file provides Rust equivalents of common Linux bit macros for fixed unsigned integer types.

## Important APIs, Types, and Functions
The `impl_bit_fn!` macro generates `checked_bit_u64/u32/u16/u8` and const `bit_u64/u32/u16/u8`. The `impl_genmask_fn!` macro generates runtime-checked `genmask_checked_*` and const-build-asserted `genmask_*` functions for the same integer types.

## Control Flow and State
Checked bit functions call `checked_shl` and return `None` on out-of-range shifts. Const bit functions use `build_assert!(n < <$ty>::BITS)` and then shift. Checked genmask functions reject reversed ranges, compute high and low bits through checked helpers, and build `(high | (high - 1)) & !(low - 1)`. Const genmask functions assert `start <= end` and rely on const bit helpers for range validation.

## State and Persistence Behavior
The module is stateless. It computes integer masks from inputs and emits no persistent data.

## Dependencies and Integration Points
It uses `crate::prelude::*` for `build_assert!`, `core::ops::RangeInclusive`, and the `macros::paste` helper. It mirrors `include/linux/bits.h` behavior for Rust kernel code that needs masks without invoking C macros.

## Risks
The const APIs require compile-time provability; misuse with non-constant or invalid values leads to build failures. Runtime APIs return `None` for invalid ranges, so callers must not unwrap unchecked values from untrusted inputs. The mask formula depends on valid high/low bit values and would underflow if range checks were removed.

## Test Signals
Doc examples cover edge single-bit masks, full-width masks, middle ranges, out-of-range endpoints, and reversed ranges for all supported integer widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block.rs

## Purpose
This small file is the root Rust block-layer module and re-exports the blk-mq submodule.

## Important APIs, Types, and Functions
It declares `pub mod mq` and exposes sector-related constants: `SECTOR_MASK`, `SECTOR_SHIFT`, `SECTOR_SIZE`, and `PAGE_SECTORS_SHIFT`, all sourced from generated kernel bindings.

## Control Flow and State
There is no runtime control flow. The file is a namespace and constant bridge.

## State and Persistence Behavior
The constants are compile-time values reflecting the target kernel configuration and architecture. No mutable state is owned here.

## Dependencies and Integration Points
The file depends on `bindings` and integrates Rust block drivers with the `block::mq` API in child modules. The constants provide shared units for code converting pages, bytes, and sectors.

## Risks
Risks are mainly configuration drift: Rust constants must match C kernel bindings. Incorrect use of sector units by callers can still cause block size/capacity bugs.

## Test Signals
No local tests are present; build-time binding generation and downstream block driver compilation are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq.rs

## Purpose
This module documents and assembles the Rust blk-mq abstraction layer for implementing block device drivers.

## Important APIs, Types, and Functions
It exposes `gen_disk`, private `operations`, private `request`, private `tag_set`, and publicly re-exports `Operations`, `Request`, and `TagSet`. The module-level documentation describes the required sequence: implement `Operations`, create a `TagSet<T>`, build a `GenDisk<T>` through `GenDiskBuilder`, and ensure requests are ended.

## Control Flow and State
There is no executable control flow in this file. It defines the public composition of the blk-mq API and the conceptual request lifecycle: blk-mq queues a `Request`, Rust driver code receives `ARef<Request<T>>`, and driver completion must call `Request::end_ok` or equivalent completion flow.

## State and Persistence Behavior
The documentation highlights that Rust drivers hold refcounts on in-flight C requests, and that `TagSet` maintains tag-to-request mapping and blk-mq queue resources. Actual state is implemented in sibling modules.

## Dependencies and Integration Points
It integrates the Rust block module with C blk-mq concepts: `struct blk_mq_tag_set`, `struct gendisk`, `struct request`, queue depth, queue maps, and request completion. The example uses `Arc<TagSet<_>>`, `GenDiskBuilder`, and `ARef<Request<_>>`.

## Risks
The main risk described here is liveness: drivers must end every request, and the Rust reference-count model must align with blk-mq ownership. Holding requests too long, ending with extra references, or losing the tag-set/disk lifetime ordering can deadlock or timeout I/O.

## Test Signals
No local tests are present. The embedded example is a compile-time/API smoke signal for creating a tag set, disk, and request callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/gen_disk.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/gen_disk.rs

## Purpose
This file wraps C `struct gendisk` creation and teardown for Rust blk-mq drivers.

## Important APIs, Types, and Functions
`GenDiskBuilder` carries `rotational`, `logical_block_size`, `physical_block_size`, and `capacity_sectors`. It provides `new`, `rotational`, `validate_block_size`, `logical_block_size`, `physical_block_size`, `capacity_sectors`, and `build`. `GenDisk<T: Operations>` owns a raw `gendisk` pointer and an `Arc<TagSet<T>>` to preserve tag-set lifetime.

## Control Flow and State
`build` converts driver queue data into a foreign pointer, guards it with `ScopeGuard`, fills `queue_limits`, allocates the disk with `__blk_mq_alloc_disk`, installs a mostly empty `block_device_operations` table, writes a NUL-terminated disk name, sets capacity, and calls `device_add_disk`. On success it dismisses the recovery guard so queue data is owned by the disk queue; on failure the guard reconstructs and drops queue data.

## State and Persistence Behavior
After successful build, the gendisk is registered in VFS/block core and owns queue data in `queue.queuedata`. `GenDisk::drop` fetches that queue data, calls `del_gendisk`, then reconstructs and drops the `ForeignOwnable` queue data. The `Arc<TagSet<T>>` field keeps the tag set alive until disk teardown.

## Dependencies and Integration Points
The file depends on blk-mq bindings, `TagSet`, `Operations`, kernel formatting, `NullTerminatedFormatter`, `ForeignOwnable`, `ScopeGuard`, and static lock-class helpers. It integrates with C block-device operations, queue limits, capacity management, and disk registration.

## Risks
`build` must handle ownership transfer exactly once. If `device_add_disk` fails after queue data is installed, the guard must recover it. Disk names must fit the C fixed buffer. The operations table currently has `owner: null_mut()` with a TODO, so module ownership protection may be incomplete. Block size validation constrains sizes to powers of two in `[512, PAGE_SIZE]`; misuse by callers can return `EINVAL`.

## Test Signals
No local tests exist. The module-level blk-mq example exercises the builder path. Runtime validation would require creating a test block driver and checking registration/teardown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/gen_disk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/operations.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/operations.rs

## Purpose
This file defines the Rust trait and generated C vtable used by blk-mq to call into Rust block drivers.

## Important APIs, Types, and Functions
`Operations` requires an associated `QueueData: ForeignOwnable` and callbacks `queue_rq`, `commit_rqs`, and `complete`, with optional `poll`. `OperationsVTable<T>` builds a `bindings::blk_mq_ops` with callbacks for queueing, commits, completion, polling, hardware-context init/exit, and request init/exit.

## Control Flow and State
`queue_rq_callback` receives `blk_mq_queue_data`, casts the request to `Request<T>`, sets the Rust request refcount to `2` for one `ARef` plus in-flight ownership, creates `ARef`, borrows queue data from `queue.queuedata`, starts the request with `blk_mq_start_request`, and calls `T::queue_rq`. Errors convert to blk status. `commit_rqs_callback` borrows queue data and calls `T::commit_rqs`. `complete_callback` reconstructs the `ARef` leaked by `Request::complete` and calls `T::complete`. `init_request_callback` initializes per-request `RequestDataWrapper.refcount`; `exit_request_callback` drops it.

## State and Persistence Behavior
Per-request Rust state lives in the blk-mq private PDU area sized by `TagSet`. Queue data is a foreign-owned pointer installed by `GenDiskBuilder` and borrowed during callbacks. The static vtable persists for the driver type.

## Dependencies and Integration Points
This file integrates directly with C `blk_mq_ops`, `blk_mq_hw_ctx`, request PDU storage, `ARef`, `Refcount`, `ForeignOwnable`, and kernel error conversion. It is consumed by `TagSet::new`.

## Risks
The callback contracts are strict: C pointers must be valid, request private data must be initialized, and queue data must outlive callbacks. The refcount transition in `queue_rq_callback` is the root of later request-ending safety. Returning success without eventually ending the request can stall I/O; ending with extra refs fails in `Request`. Optional callbacks are installed only when vtable metadata says they exist.

## Test Signals
No local tests exist. Useful signals are compile-time vtable generation, a minimal block driver example, and runtime tests that queue, complete, poll, and tear down requests without refcount panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/operations.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/request.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/request.rs

## Purpose
This file wraps blk-mq `struct request` and implements Rust-side reference accounting for in-flight block requests.

## Important APIs, Types, and Functions
`Request<T>` is a transparent wrapper over `bindings::request` plus type marker. Key methods are unsafe `aref_from_raw`, unsafe `start_unchecked`, private `try_set_end`, public `end_ok`, `complete`, unsafe `wrapper_ptr`, and `wrapper_ref`. `RequestDataWrapper` stores a `Refcount` in the request PDU and exposes `refcount` and unsafe `refcount_ptr`. `Request<T>` implements `Send`, `Sync`, and `AlwaysRefCounted`.

## Control Flow and State
When blk-mq queues a request, `operations.rs` sets refcount to `2`. `start_unchecked` calls `blk_mq_start_request` once Rust has exclusive request ownership. `end_ok` consumes an `ARef`, uses `try_set_end` to atomically change refcount from `2` to `0`, forgets the `ARef`, and calls `blk_mq_end_request`. If extra `ARef`s exist, it returns the request in `Err`. `complete` transfers an `ARef` raw pointer into blk-mq remote completion; if the C helper does not schedule remote completion, it reconstructs the `ARef` and calls the Rust complete callback immediately.

## State and Persistence Behavior
Refcount states encode ownership: `0` C-owned, `1` Rust-owned with no `ARef`, `2` Rust-owned with one `ARef`, and `>2` shared Rust references. The PDU wrapper persists for each request from `init_request` to `exit_request`. `AlwaysRefCounted::dec_ref` decrements the refcount and can panic under `CONFIG_DEBUG_MISC` if a Rust reference reaches zero unexpectedly.

## Dependencies and Integration Points
The module depends on blk-mq bindings, `ARef`, `AlwaysRefCounted`, `Refcount`, atomic `Relaxed`, and the `Operations` trait. It is called by operation callbacks and driver code that completes requests.

## Risks
The core risk is mismatched ownership between Rust references and C request lifetime. Ending requires exactly one live `ARef`; cloned references must be dropped first. `complete` deliberately leaks/reclaims raw references around C scheduling. Any driver that forgets to complete a request, holds a reference forever, or calls end twice can cause timeouts or refcount corruption.

## Test Signals
No direct tests are present. Runtime signals should include successful request completion, failure when ending with extra references, no debug refcount panic, and correct remote/local completion callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/request.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/tag_set.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/tag_set.rs

## Purpose
This file wraps C `struct blk_mq_tag_set`, which owns blk-mq tag allocation and request private-data sizing for a Rust block driver.

## Important APIs, Types, and Functions
`TagSet<T: Operations>` is a pinned transparent wrapper over `Opaque<bindings::blk_mq_tag_set>`. `TagSet::new(nr_hw_queues, num_tags, num_maps)` returns a `PinInit<Self>`. `raw_tag_set` exposes the C pointer for disk allocation. Pinned `Drop` calls `blk_mq_free_tag_set`.

## Control Flow and State
Construction zeroes a C tag set, computes `cmd_size` from `RequestDataWrapper`, fills operations pointer from `OperationsVTable::<T>::build`, queue counts, default timeout, NUMA node, depth, flags, driver data, and map count, then calls `blk_mq_alloc_tag_set` in a pin chain. Drop frees the allocated tag-set resources.

## State and Persistence Behavior
The tag set persists pinned because the C struct includes linked-list state and is registered with blk-mq. It carries the request private-data size used by request init callbacks and the static operations vtable pointer. `GenDisk` holds an `Arc<TagSet<T>>` to keep it alive while queues use it.

## Dependencies and Integration Points
The file depends on blk-mq bindings, `OperationsVTable`, `RequestDataWrapper`, `PinInit`, `try_pin_init`, and `Opaque`. It integrates with `GenDiskBuilder::build` through `raw_tag_set`.

## Risks
Incorrect `cmd_size` would break `Request::wrapper_ptr`. Queue/depth/map parameters are passed through without higher-level policy validation. `blk_mq_free_tag_set` must run only after queues and disks no longer use the tag set, so user code should preserve the `Arc` lifetime pattern.

## Test Signals
No local tests. Useful coverage would allocate/drop tag sets with varied queue parameters and exercise request PDU init/exit through a minimal blk-mq driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/tag_set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bug.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/bug.rs

## Purpose
This file provides Rust support for kernel WARN/BUG metadata emission and a public `warn_on!` macro.

## Important APIs, Types, and Functions
Multiple cfg-specific `warn_flags!` macro definitions implement architecture/config-dependent warning emission. `bugflag_taint` shifts taint values into BUG flag position. `warn_on!` evaluates a condition, emits warning metadata when true, and returns the condition result.

## Control Flow and State
For normal `CONFIG_BUG` non-UML/non-LoongArch/non-ARM builds, `warn_flags!` emits inline assembly that includes generated architecture warn and reachable assembly snippets, optionally including verbose file metadata. UML calls `warn_slowpath_fmt`; LoongArch/ARM call `WARN_ON(true)`; builds without `CONFIG_BUG` emit nothing. `warn_on!` builds a file or detailed condition string depending on `CONFIG_DEBUG_BUGVERBOSE_DETAILED`.

## State and Persistence Behavior
The module stores no runtime state. Its effect is compile-time/static metadata emission and runtime warning reporting through architecture or C kernel helpers.

## Dependencies and Integration Points
It depends on generated `OBJTREE` assembly includes, `bindings::BUGFLAG_WARNING`, `TAINT_WARN`, `bug_entry`, `WARN_ON`, and `warn_slowpath_fmt`. It is a low-level macro facility for other Rust kernel code.

## Risks
Architecture cfg coverage must match kernel support. Inline assembly includes must exist and have the expected operands. Because `warn_on!` returns the condition, callers may rely on single evaluation; the macro stores `cond` first to preserve that. Builds without `CONFIG_BUG` suppress warning side effects.

## Test Signals
No local tests. Validation is primarily build coverage across configurations and architecture smoke tests that warning metadata appears or C warning helpers are called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bug.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/build_assert.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/build_assert.rs

## Purpose
This file defines build-time assertion macros for Rust kernel code, mirroring and extending C `static_assert` and `BUILD_BUG_ON` patterns.

## Important APIs, Types, and Functions
It re-exports `static_assert!`, `const_assert!`, `build_error!`, and `build_assert!`, plus the hidden `build_error::build_error` function. `static_assert!` emits a const `assert!`; `const_assert!` emits a const block assertion; `build_error!` calls the external build-error mechanism; `build_assert!` calls `build_error!` when the condition is not optimized/proven true.

## Control Flow and State
`static_assert!` is evaluated as an item-level constant and cannot depend on generics or runtime values. `const_assert!` works in statement positions and can depend on generics. `build_assert!` uses an `if !$cond` branch that must be eliminated by constant evaluation or optimization; otherwise linking/build fails through `build_error`.

## State and Persistence Behavior
The module has no runtime state. It intentionally fails compilation or linking for invalid code paths.

## Dependencies and Integration Points
It depends on the `build_error` crate/mechanism and is used by other modules such as `bits.rs` and `cpufreq.rs`. The macros are exported at crate root for general kernel Rust use.

## Risks
`build_assert!` can produce less friendly linker/undefined-symbol style failures when the optimizer cannot prove the branch unreachable. Functions using runtime-like values should be `#[inline(always)]` when the caller provides constants. Misusing the stronger macros where simpler `static_assert!` suffices can defer errors.

## Test Signals
Documentation examples describe allowed and disallowed contexts. Practical signals are compile-fail tests or builds that instantiate generic functions and validate assertion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/build_assert.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/clk.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/clk.rs

## Purpose
This file provides Rust abstractions for clock rates and, when `CONFIG_COMMON_CLK` is enabled, reference-counted clock handles.

## Important APIs, Types, and Functions
`Hertz(c_ulong)` represents a frequency and exposes `from_khz`, `from_mhz`, `from_ghz`, `as_hz`, `as_khz`, `as_mhz`, and `as_ghz`, plus `From<Hertz> for c_ulong`. Under `CONFIG_COMMON_CLK`, `Clk` wraps `*mut bindings::clk` and exposes `get`, `as_raw`, `enable`, `disable`, `prepare`, `unprepare`, `prepare_enable`, `disable_unprepare`, `rate`, and `set_rate`. `OptionalClk` wraps optional clocks from `clk_get_optional` and derefs to `Clk`.

## Control Flow and State
Clock acquisition calls `clk_get` or `clk_get_optional` with a device and optional connection ID. Clock operations directly call the corresponding C API and convert integer errors through `to_result`/`from_err_ptr`. `Drop for Clk` calls `clk_put`, so both `Clk` and `OptionalClk` release their C references through RAII.

## State and Persistence Behavior
`Hertz` is a copyable value. `Clk` persists a C clock reference until drop. `OptionalClk` may contain a null underlying pointer per common-clk optional semantics, but it still exposes the same operations through `Deref`.

## Dependencies and Integration Points
The file depends on `ffi::c_ulong`, and conditionally on `Device`, `CStr`, error helpers, C clock bindings, and `Deref`. It is used by cpufreq policy setup through `Policy::set_clk`.

## Risks
Rate unit conversion truncates toward lower units and multiplication constructors do not check overflow. `Policy::set_clk` callers must keep the returned `Clk` alive while C uses the raw pointer. Optional clocks require C helpers to tolerate null handles for later operations.

## Test Signals
Doc examples cover frequency conversion and common clock configuration. No local KUnit tests are present; runtime testing requires a device with real or mock common clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/clk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/configfs.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/configfs.rs

## Purpose
This file implements Rust abstractions for configfs, allowing kernel modules to expose userspace-created configuration hierarchies and attributes.

## Important APIs, Types, and Functions
`Subsystem<Data>` registers a top-level configfs subsystem and stores pinned user data. `Group<Data>` represents dynamically created subgroups. Unsafe trait `HasGroup<Data>` provides offset/container conversions for types embedding `config_group`. `GroupOperations` defines `make_group` and optional `drop_item`. `Attribute<ID, O, Data>` wraps a `configfs_attribute`; `AttributeOperations<ID>` defines `show` and optional `store`. `AttributeList<N, Data>` stores the null-terminated C pointer array. `ItemType<Container, Data>` wraps `config_item_type`. The exported `configfs_attrs!` macro generates static attributes, attribute lists, and item types.

## Control Flow and State
`Subsystem::new` zero-initializes C subsystem state, calls `config_group_init_type_name`, initializes `su_mutex`, pins user data, then registers via `configfs_register_subsystem`. Drop unregisters and destroys the mutex. `GroupOperationsVTable::make_group` resolves parent data, calls Rust `make_group`, allocates `Arc<Group<Child>>`, leaks it to C via raw pointer, and returns the embedded C group. `drop_item` optionally calls Rust `drop_item`, then drops a C config item reference. Group release reconstructs the `Arc` and drops it. Attribute `show`/`store` map C item pointers back to `Data`, call Rust trait methods, and translate `Result` into byte counts or negative errno.

## State and Persistence Behavior
Subsystem and group data are pinned and embedded beside C configfs structures. Dynamic groups persist as `Arc<Group<Child>>` leaked into configfs until release. Attribute definitions and item types are static. Attribute values themselves live in user `Data`; configfs callbacks provide page buffers but this module does not persist attribute payloads.

## Dependencies and Integration Points
The module integrates with C `configfs_subsystem`, `config_group`, `config_item`, `configfs_attribute`, `config_item_type`, mutex initialization/destruction, `Arc`, `ArcBorrow`, `CString`, `PAGE_SIZE`, `PinInit`, vtable macros, and `container_of!`.

## Risks
Pointer provenance and offset logic are central: root groups map to `Subsystem<Data>`, child groups map to `Group<Data>`. Incorrect `HasGroup` implementation would corrupt callback data access. `Attribute::show` casts the page pointer to `[u8; PAGE_SIZE]` and assumes C supplied a full page. `store` trusts the supplied byte count. The macro uses static mutable-through-`UnsafeCell` initialization patterns that must remain single-threaded during expansion/init. Unsupported configfs features include item-only children, symlinks, disconnect notification, and default groups.

## Test Signals
No local tests are present. The long sample in module docs exercises subsystem creation, attributes, mutex-backed state, `show`, and `store`. Runtime test signals should include mount-visible directories/files, mkdir/rmdir callback ordering, correct `Arc` release, and errno propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/configfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpu.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cpu.rs

## Purpose
This file provides basic Rust CPU identifier wrappers and access to CPU devices.

## Important APIs, Types, and Functions
`nr_cpu_ids()` returns the configured maximum possible CPU count, using either `bindings::NR_CPUS` or the runtime `bindings::nr_cpu_ids` global depending on config. `CpuId(u32)` enforces IDs in `[0, nr_cpu_ids())` through checked `from_i32`/`from_u32` and unsafe unchecked constructors. It exposes `as_u32`, `current`, and conversions into `u32`/`i32`. Unsafe `from_cpu` returns the `Device` for a CPU.

## Control Flow and State
Checked constructors reject negative or too-large IDs. Unchecked constructors debug-assert validity and rely on caller safety. `CpuId::current` calls `raw_smp_processor_id` and wraps it unchecked. `from_cpu` calls `get_cpu_device`, returns `ENODEV` on null, and casts the C device pointer into a Rust `Device`.

## State and Persistence Behavior
`CpuId` is a copyable validated value. `from_cpu` returns a `'static` device reference because C does not free CPU device memory on hot-unplug, but the docs warn that unregister can make use invalid from a logical lifetime perspective.

## Dependencies and Integration Points
The file depends on CPU bindings, `device::Device`, kernel `Result`, and `ENODEV`. It is used by cpufreq and cpumask abstractions.

## Risks
`CpuId::current` can become stale under preemption or migration. `from_cpu` is unsafe because CPU hotplug can unregister the device while memory remains allocated; callers need hotplug notification or another lifetime discipline. Unchecked constructors must not be used with arbitrary C integers.

## Test Signals
No local tests. Doc examples cover checked and unchecked construction. Runtime validation should include boundary IDs and CPU hotplug-aware device use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpufreq.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cpufreq.rs

## Purpose
This file implements Rust abstractions for the Linux cpufreq subsystem, including frequency tables, policies, driver callback traits, and registration.

## Important APIs, Types, and Functions
It defines driver flags, `DEFAULT_TRANSITION_LATENCY_NS`, `Relation`, `PolicyData`, `TableIndex`, `Table`, `TableBox`, `TableBuilder`, `Policy`, internal `PolicyCpu`, trait `Driver`, and `Registration<T>`. `TableBuilder` builds pinned C frequency tables terminated by a sentinel. `Policy` wraps `struct cpufreq_policy` and exposes CPU, min/max/current/suspend frequencies, generic helpers, cpumask, optional common-clock attachment, DVFS/fast-switch flags, transition/cpuinfo fields, frequency table getter/setter, and private driver data get/set/clear. `Driver` mirrors many cpufreq callbacks. `Registration<T>` builds a mutable C `cpufreq_driver` vtable and registers/unregisters it.

## Control Flow and State
`Relation::new` decodes C relation flags and efficient-bit markers. `TableBuilder::to_table` appends a sentinel entry with `c_ulong::MAX` before pinning entries. `Registration::new` copies the static vtable into `KBox<UnsafeCell<_>>` because cpufreq mutates driver fields, then calls `cpufreq_register_driver`. Mandatory callbacks include `init` and `verify`; optional callbacks are installed based on vtable macro `HAS_*` constants. `init_callback` wraps the policy, calls `T::init`, and stores returned `PData` as foreign-owned driver data. `exit_callback` clears that data and passes ownership to `T::exit`. Other callbacks map C pointers/integers into `Policy`, `PolicyData`, `Relation`, `TableIndex`, or `PolicyCpu` and convert Rust `Result` back into C integers.

## State and Persistence Behavior
Registered driver state persists in a heap-owned `cpufreq_driver` until `Registration::drop`, which unregisters. Per-policy private data is stored in `policy.driver_data` as a `ForeignOwnable` pointer and must be cleared exactly once on exit. `TableBox` pins frequency-table memory so raw C pointers remain stable while the table is installed. `PolicyCpu` acquires policy references with `cpufreq_cpu_get` and releases with `cpufreq_cpu_put`.

## Dependencies and Integration Points
The module depends on `Hertz`, `CpuId`, `Cpumask`, `Device`, `devres`, kernel errors, `ForeignOwnable`, `Opaque`, optional `Clk`, `KVec`, and cpufreq C bindings. It integrates with platform/device drivers through `Registration::new_foreign_owned`.

## Risks
Lifetime hazards dominate: `Policy::set_freq_table` and `set_clk` store raw pointers and rely on callers to keep `TableBox`/`Clk` alive. Callback pointer validity is guaranteed only by cpufreq C infrastructure. Frequency conversion uses kHz fields and can truncate or overflow when casting. `copy_name` relies on compile-time `build_assert!` for name length. `init_callback` can fail with `EBUSY` if driver data was already set. Callback default methods deliberately build-error if installed unexpectedly.

## Test Signals
No local tests. Doc examples cover table construction, policy mutation, and registration from a platform driver. Runtime test signals should include registering/unregistering a sample driver, policy init/exit data ownership, verify/target callbacks, frequency-table lifetime, and suspend/get generic helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpufreq.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpumask.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cpumask.rs

## Purpose
This file wraps Linux `struct cpumask` and `cpumask_var_t` for Rust code.

## Important APIs, Types, and Functions
`Cpumask` is a transparent wrapper exposing unsafe `from_raw_mut`, unsafe `from_raw`, `as_raw`, non-atomic `set` and `clear`, `test`, `setall`, `empty`, `full`, `weight`, and `copy`. `CpumaskVar` owns either an offstack allocated cpumask or an inline `Cpumask`, depending on `CONFIG_CPUMASK_OFFSTACK`, and provides `new_zero`, unsafe uninitialized `new`, unsafe raw borrow constructors, `try_clone`, `Deref`, `DerefMut`, and `Drop`.

## Control Flow and State
Owned construction calls `zalloc_cpumask_var` or `alloc_cpumask_var` when offstack, or initializes inline `Opaque` storage otherwise. `try_clone` allocates a new mask and copies from the source. Methods delegate directly to C cpumask helpers with validated `CpuId` inputs.

## State and Persistence Behavior
`Cpumask` borrows existing C storage. `CpumaskVar` owns storage and frees it in `Drop` only for offstack configurations. Inline configurations store the C cpumask directly in the Rust object. `new` may return uninitialized storage, so callers must initialize before use.

## Dependencies and Integration Points
The module depends on `AllocError`, `Flags`, `CpuId`, `Opaque`, cpumask bindings, and Rust deref traits. It is used by cpufreq policies and other CPU-affinity code.

## Risks
`set`/`clear` are non-atomic despite C naming conventions, so concurrent cpumask mutation requires external synchronization or atomic C APIs not exposed here. Unsafe raw constructors rely on caller-managed lifetimes. Offstack allocation failures return `AllocError`. Using uninitialized masks from `new` before population is unsafe.

## Test Signals
No local tests. Doc examples demonstrate setting, testing, counting, and cloning masks. Useful runtime tests should cover both offstack and inline configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpumask.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cred.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cred.rs

## Purpose
This file wraps kernel credentials (`struct cred`) for Rust code.

## Important APIs, Types, and Functions
`Credential` is a transparent wrapper over `Opaque<bindings::cred>`. It exposes unsafe `from_ptr`, `as_ptr`, `get_secid`, and `euid`. It implements `Send`, `Sync`, and `AlwaysRefCounted`.

## Control Flow and State
`from_ptr` casts a valid C credential pointer into a borrowed Rust reference. `get_secid` initializes a local `secid`, calls `security_cred_getsecid`, and returns the resulting security ID. `euid` reads the immutable effective UID field and wraps it as `Kuid`. Refcount methods call `get_cred` and `put_cred`.

## State and Persistence Behavior
Credentials are reference-counted C objects. The wrapper does not mutate credential fields and relies on the kernel model where credentials are mostly immutable after initialization and changes happen by replacing credential pointers. `ARef<Credential>`-style ownership is enabled through `AlwaysRefCounted`.

## Dependencies and Integration Points
The module depends on `bindings`, `AlwaysRefCounted`, `task::Kuid`, and `Opaque`. It integrates with security hooks and task/file credential users that need stable references.

## Risks
`from_ptr` is unsafe because validity and lifetime are caller-provided. `get_secid` depends on security subsystem behavior. `Send`/`Sync` rely on credential immutability and C-side synchronization; adding mutable accessors would need new analysis. Refcount underflow/double-put would be a serious lifetime bug.

## Test Signals
No local tests. Runtime signals should include correct UID/security ID reads and balanced get/put behavior under `ARef` use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cred.rs -->
