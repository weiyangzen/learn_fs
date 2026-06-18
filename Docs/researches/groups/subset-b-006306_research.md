# Research Group: subset-b-006306

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/debugfs.rs

## Purpose
`debugfs.rs` is the top-level Rust abstraction for Linux debugfs. It gives drivers an owning `Dir`, `File<T>`, and `Scope<T>` API for creating debugfs directories and files whose backing data lifetimes are tied to Rust ownership instead of open-coded `debugfs_create_*` calls. When `CONFIG_DEBUG_FS` is disabled, the API compiles to inert handles so callers do not need conditional code.

## Important APIs, Types, and Functions
The main public types are `Dir`, `File<T>`, `Scope<T>`, and `ScopedDir<'data, 'dir>`. `Dir::new`, `Dir::subdir`, `Dir::read_only_file`, `Dir::read_binary_file`, `Dir::read_callback_file`, `Dir::read_write_file`, `Dir::read_write_binary_file`, `Dir::read_write_callback_file`, `Dir::write_only_file`, `Dir::write_binary_file`, `Dir::write_callback_file`, and `Dir::scope` cover owned debugfs entries. `Scope::dir` creates a root scoped tree. `ScopedDir` mirrors the file creation methods for borrowed data whose lifetime is proven by the enclosing `Scope`.

## Control Flow
Directory creation routes through private `Dir::create`, which either stores an `Arc<Entry<'static>>` to keep parent dentries alive or records `None` when allocation fails. File creation routes through `Dir::create_file`, which builds a pinned `Scope<T>` and then creates the debugfs `Entry` only after `data` is initialized. Scoped trees create a `ScopedDir`, run the caller's initializer to populate files, and finally move the underlying `Entry` into the owning `Scope`.

## State and Persistence
State is entirely in-memory and debugfs-backed. `Dir` keeps an optional refcounted `Entry`, `Scope<T>` stores the backing data and the tree entry, and `File<T>` wraps a scope. Drop order is load-bearing: the debugfs entry is removed before the backing data is dropped. `PhantomPinned` prevents moving backing data after file private pointers are published.

## Dependencies and Integration Points
This file integrates the local `entry`, `file_ops`, `traits`, and `callback_adapters` modules with kernel `PinInit`, `Arc`, `CStr`, `fmt`, and `UserSliceReader` infrastructure. It is the driver-facing entry point for exporting formatted or binary diagnostic state through debugfs.

## Risks
The main risks are lifetime and drop-order mistakes around file private data, especially because C debugfs stores raw pointers. Callback adapters require non-capturing, zero-sized closures. The private `scoped_dir` and `ScopedDir::new` APIs are intentionally not public because extracting entries incorrectly can leak directories. Disabled-debugfs behavior silently drops entries, so tests must cover both config paths.

## Test Signals
Useful signals include Rust doctests/build tests for each constructor, runtime creation and removal of nested debugfs trees, reads and writes through trait-backed and callback-backed files, module unload while files are open, allocation-failure paths that produce `Dir(None)`, and builds with `CONFIG_DEBUG_FS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/callback_adapters.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/debugfs/callback_adapters.rs

## Purpose
`callback_adapters.rs` lets debugfs files use function items or non-capturing closures for read and write behavior without requiring the backing data type itself to implement `Writer` or `Reader`. It does this with transparent wrapper types that have the same representation as the wrapped data.

## Important APIs, Types, and Functions
The unsafe `Adapter` trait exposes the original `Inner` type for transmuting `FileOps<AdapterType>` back to `FileOps<Inner>`. `WritableAdapter<D, W>` implements `Reader` with a callback `W` while delegating `Writer` to `D`. `FormatAdapter<D, F>` implements `Writer` with a formatting callback `F` and dereferences to `D`. `NoWriter<D>` is a transparent passthrough used for write-only callback files. `materialize_zst<F>()` creates a static reference to an inhabited zero-sized function item/closure.

## Control Flow
The top-level debugfs constructors instantiate `FileOps` for an adapter stack, then call `.adapt()` one or more times to expose the operations as if they were for the original data type. At read or write time, the adapter implementation materializes the zero-sized callback type and invokes it against the underlying data reference.

## State and Persistence
The adapters contain only the wrapped data plus `PhantomData` for the callback type. They do not persist callback values; the callback type itself is the value, which is why only zero-sized function items and non-capturing closures are valid.

## Dependencies and Integration Points
This module depends on `debugfs::traits::{Reader, Writer}`, `fmt`, `UserSliceReader`, `Deref`, and the debugfs `FileOps::adapt` path. It is used by both owned `Dir` files and borrowed `ScopedDir` files for callback-based debugfs exports.

## Risks
The unsafe contract is narrow but important: the transparent adapter must be layout-compatible with the inner type, and `materialize_zst` assumes the callback type is inhabited and zero-sized. Accidentally accepting capturing closures would break this model. Adapter stacking also makes it easy to pick the wrong operation mode if the `.adapt()` chain is changed incorrectly.

## Test Signals
Compile-time tests should reject capturing closures, non-`Send`/`Sync` callbacks, and callbacks with wrong signatures. Runtime tests should exercise read-only, write-only, and read-write callback files and confirm the underlying data address is preserved through adapter casts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/callback_adapters.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/entry.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/debugfs/entry.rs

## Purpose
`entry.rs` is the raw debugfs dentry owner for the Rust debugfs abstraction. It wraps C `struct dentry *` values returned by debugfs creation functions and removes them on drop, while encoding parent and borrowed-data lifetimes.

## Important APIs, Types, and Functions
`Entry<'a>` stores the raw dentry pointer, an optional owning parent `Arc<Entry<'static>>`, and a lifetime marker. `Entry::dynamic_dir` and unsafe `Entry::dynamic_file` create entries whose parent is refcounted. `Entry::dir` and `Entry::file` create entries tied to borrowed parent/data lifetimes for scoped trees. `Entry::empty` creates a null placeholder, `Entry::as_ptr` exposes the raw pointer, and `Drop` calls `debugfs_remove`.

## Control Flow
Owned directory creation passes a parent pointer or null into `debugfs_create_dir`. Owned file creation calls `debugfs_create_file_full` with the file mode, parent dentry, backing data pointer, and Rust-generated file operations. Scoped creation follows the same pattern but uses borrowed lifetimes instead of `Arc`. Empty entries are used as placeholders during pinned initialization and for disabled/failed debugfs paths.

## State and Persistence
The only persistent state is the debugfs dentry pointer plus an optional parent keepalive. The pointer invariant allows null and error pointers because `debugfs_remove` accepts them. Parent `Arc` ownership prevents a child dentry from outliving a dynamically owned parent.

## Dependencies and Integration Points
This module is private to `debugfs.rs` and uses kernel bindings for `debugfs_create_dir`, `debugfs_create_file_full`, and `debugfs_remove`. It also depends on `CStr`, `Arc`, and `FileOps<T>` to pass valid names, parents, backing data, and C vtables into debugfs.

## Risks
Safety depends on the caller ensuring backing data outlives any created file entry. The `Entry::dynamic_file` function is unsafe for that reason, and `Scope` is the higher-level mechanism that satisfies it. Another risk is forgetting a scoped `Entry` deliberately; that is correct only because the enclosing root `Entry` recursively removes the subtree.

## Test Signals
Test nested directory removal, parent-drop-before-child ordering, null/error pointer cleanup, files backed by scoped and owned data, and module unload with open debugfs files. KASAN and lockdep should stay quiet during create/remove churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/entry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/file_ops.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/debugfs/file_ops.rs

## Purpose
`file_ops.rs` maps Rust debugfs traits to C `file_operations`. It provides operation tables for formatted reads through `seq_file`, text writes from user slices, binary reads and writes with offsets, and read-write combinations.

## Important APIs, Types, and Functions
`FileOps<T>` stores the C `file_operations`, Unix mode bits, and the invariant that inode private data points to a valid `T`. Traits `ReadFile`, `ReadWriteFile`, `WriteFile`, `BinaryReadFile`, `BinaryWriteFile`, and `BinaryReadWriteFile` provide const operation tables. Important callbacks include `writer_open`, `writer_act`, `write`, `write_only_open`, `write_only_write`, `blob_read`, and `blob_write`.

## Control Flow
Formatted files use `single_open` to create a `seq_file`; `writer_act` pulls the `T` pointer from `seq.private` and prints through `Writer`. Read-write text files add a `write` callback that retrieves the same private data from the `seq_file` and calls `Reader`. Write-only text files store the inode private pointer directly in `file.private_data`. Binary files use `simple_open`, then `blob_read` or `blob_write` calls the `BinaryWriter` or `BinaryReader` implementation with the user buffer and file offset.

## State and Persistence
The operation tables are static constants. Per-open state is managed by the kernel file and seq_file structures. No durable state exists; writes mutate the backing `T` through the trait implementation, usually via interior mutability.

## Dependencies and Integration Points
This file depends on `debugfs::traits`, `callback_adapters::Adapter`, `SeqFile`, `seq_print!`, `UserSlice`, `UserPtr`, and Linux file operation bindings. It is consumed by `Dir` and `ScopedDir` constructors to select file mode and callbacks.

## Risks
The main risks are raw-pointer type mismatches and offset handling. `FileOps::adapt` uses transmute, so adapter layout contracts must hold. Text writes ignore `ppos` and return the full input count on success. Binary operations must convert sizes to `isize` safely and report negative offsets or conversion failures correctly through errno.

## Test Signals
Read formatted files, write text files with valid and invalid inputs, exercise binary partial reads/writes at offsets, seek with `default_llseek`, and test all permission modes. Fault injection for invalid user buffers and large offsets should return errno without corrupting backing data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/file_ops.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/traits.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/debugfs/traits.rs

## Purpose
`traits.rs` defines the data-side contracts for Rust debugfs files. It lets values render formatted text, accept textual updates, expose raw binary bytes, or accept binary writes while providing reusable implementations for common synchronized and owned containers.

## Important APIs, Types, and Functions
`Writer` formats data and has blanket support for `fmt::Debug` plus `Mutex<T>`. `Reader` updates data from a `UserSliceReader`, with implementations for `Mutex<T: FromStr>` and `Atomic<T>`. `BinaryWriter` writes data to a `UserSliceWriter` and is implemented for `AsBytes`, `Mutex`, `Box`, `Pin<Box>`, `Arc`, and `Vec<T: AsBytes>`. `BinaryReaderMut` and `BinaryReader` implement binary input, including mutable container and lock-backed variants.

## Control Flow
Formatted reads call `Writer::write`. Text writes bound the input to a fixed stack buffer, copy from userspace, parse UTF-8, trim whitespace, and then update a mutex-protected or atomic value. Binary reads and writes delegate to `write_slice_file` or `read_slice_file`, using the supplied file offset so normal short I/O semantics are preserved.

## State and Persistence
The traits store no state. They define how debugfs file operations observe or mutate backing data. Persistence is limited to whatever the backing object stores in memory; debugfs itself does not provide durable storage.

## Dependencies and Integration Points
This module depends on allocator/container abstractions, `Mutex`, `Atomic`, `Arc`, `AsBytes`, `FromBytes`, `UserSliceReader`, `UserSliceWriter`, and file offsets. It is the public extension point used by driver data types exported through `debugfs.rs`.

## Risks
Blanket `Writer for Debug` is convenient but output is not stable across Rust versions, as noted in the comments. Text `Reader` implementations use fixed buffers, so large writes are rejected. Binary blanket implementations require correct `AsBytes` and `FromBytes` safety implementations; a wrong implementation can expose padding or accept invalid bit patterns.

## Test Signals
Test formatted output for explicit `Writer` and blanket `Debug`, parse failures for mutex and atomic readers, binary reads/writes with offsets for scalar, vector, mutex, box, and arc-backed values, and safety review of any type implementing `AsBytes` or `FromBytes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/debugfs/traits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/device.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/device.rs

## Purpose
`device.rs` is the Rust abstraction for Linux `struct device` and device-context typing. It provides reference-counted device handles, driver-private data storage and retrieval, firmware-node access, device logging macros, and helper macros for bus-specific device wrappers.

## Important APIs, Types, and Functions
`Device<Ctx = Normal>` is the transparent wrapper. Context marker types are `Normal`, `Bound`, `Core`, and `CoreInternal`, connected by `DeviceContext`. Key methods include `Device::get_device`, `Device::from_raw`, `Device::as_bound`, `Device<CoreInternal>::set_drvdata`, `drvdata_obtain`, `drvdata_borrow`, `Device<Bound>::drvdata`, `parent`, `fwnode`, and `name`. Macros include `impl_device_context_deref!`, `impl_device_context_into_aref!`, `dev_printk!`, and `dev_emerg!` through `dev_dbg!`.

## Control Flow
Bus abstractions create context-specific references during probe/remove callbacks. Probe stores pinned driver data with `set_drvdata`, which also writes a Rust `TypeId` into `struct device_private.driver_type`. Bound callbacks call `drvdata<T>()`, which checks for a stored pointer and matching `TypeId` before borrowing pinned data. Generic logging macros route to `Device::printk`, which calls `_dev_printk` when `CONFIG_PRINTK` is enabled.

## State and Persistence
The wrapper owns no independent state; it refers to kernel-managed `struct device` memory. Refcounting is delegated to `get_device` and `put_device` through `AlwaysRefCounted`. Driver-private data is a heap allocation stored in `dev_set_drvdata` and reclaimed by bus/driver infrastructure.

## Dependencies and Integration Points
This file integrates with `property::FwNode`, `ARef`, `ForeignOwnable`, `Opaque`, kernel device bindings, and bus abstractions such as PCI, platform, auxiliary, and DRM. The context types are used by DMA and devres APIs to require a bound device where unbind ordering matters.

## Risks
The most important risks are misuse of `from_raw`, selecting a stronger context than the current callback guarantees, and type mismatches in driver data. The `TypeId` storage uses unaligned reads/writes into a C field, so layout assumptions are guarded by a static assertion but still central. `as_bound` is unsafe because the caller must prove binding duration.

## Test Signals
Build bus wrappers using the context macros, probe/remove drivers that store and recover private data, verify wrong `drvdata<T>()` returns `EINVAL`, test parent and fwnode access, exercise logging macros under `CONFIG_PRINTK` and without it, and run refcount leak checks through repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/device/property.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/device/property.rs

## Purpose
`device/property.rs` wraps Linux firmware-node (`fwnode_handle`) APIs for Rust drivers. It provides reference-counted fwnode handles, property reads, child iteration, reference-argument parsing, display formatting, and a guard that distinguishes required and optional properties.

## Important APIs, Types, and Functions
`FwNode` wraps `struct fwnode_handle`. Important methods include `is_of_node`, `display_name`, `property_present`, `property_read_bool`, `property_match_string`, `property_read_array_vec`, `property_count_elem`, `property_read`, `get_child_by_name`, `children`, and `property_get_reference_args`. `NArgs` selects fixed or property-derived argument counts. `FwNodeReferenceArgs` owns returned references. `Property`, `PropertyInt`, and `PropertyGuard` implement typed property reads for strings, integer scalars, fixed arrays, and vectors.

## Control Flow
Property reads call the corresponding C fwnode helper, convert kernel return codes through `to_result`, and wrap the result in `PropertyGuard` when using generic reads. Integer array reads fill `MaybeUninit` buffers and only mark them initialized after successful C calls. Child iteration keeps the previous child in an `ARef`, passes ownership back to `fwnode_get_next_child_node`, and returns a new owned reference each step.

## State and Persistence
`FwNode` state is kernel-managed and refcounted through `fwnode_handle_get` and `fwnode_handle_put`. `FwNodeReferenceArgs` drops the reference embedded in the returned C structure. Property values are copied into Rust-owned scalars, arrays, `KVec`, or `CString`; there is no durable persistence.

## Dependencies and Integration Points
The module is reached from `Device::fwnode()` and integrates with Open Firmware, ACPI, software nodes, `KVec`, `CString`, `ARef`, and device logging via `PropertyGuard::required_by`.

## Risks
The key risks are refcount ownership around child iteration and reference arguments, signed integer reads using unsigned fwnode helpers with layout-compatible storage, and assuming string property lifetime beyond the current copy. Required-property logging can be noisy if used for genuinely optional data.

## Test Signals
Test boolean, string, scalar, fixed-array, vector, and missing-property paths on OF and ACPI backed devices. Iterate child nodes while dropping previous references, parse reference args with fixed and property-provided counts, and verify `required_by` logs only on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/device/property.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/device_id.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/device_id.rs

## Purpose
`device_id.rs` provides generic Rust infrastructure for bus-specific device ID tables. It builds zero-terminated C-compatible ID arrays and keeps Rust driver metadata aligned with each raw ID entry.

## Important APIs, Types, and Functions
`RawDeviceId` marks Rust ID wrappers as layout-compatible with a C raw ID type. `RawDeviceIdIndex` adds a `DRIVER_DATA_OFFSET` and `index()` contract for ID types that store table indexes in a raw `driver_data` field. `RawIdArray<T, N>` stores raw IDs plus a zeroed sentinel. `IdArray<T, U, N>` stores raw IDs and parallel `id_infos`. `IdTable<T, U>` type-erases the const length. `module_device_table!` emits a modpost-visible device table alias.

## Control Flow
`IdArray::build` runs in const context, transmute-copies each Rust ID into the raw ID array, optionally writes the table index into the raw driver's data field, moves the associated info into the parallel array, and appends a zero sentinel. Bus adapters pass `raw_ids().as_ptr()` to kernel match helpers and use the index to recover `id_infos`.

## State and Persistence
ID arrays are static data compiled into the driver module. They are not mutated after construction except for const-time initialization. The generated module device table static is also build-time metadata for module alias generation.

## Dependencies and Integration Points
This module is consumed by ACPI, OF, PCI, platform, auxiliary, and other bus abstractions that need C-compatible match tables while preserving Rust-side `IdInfo`. It integrates with `driver::Adapter` lookup helpers.

## Risks
Safety depends on exact layout compatibility between Rust ID wrappers and C ID structs, and on correct byte offsets for `driver_data`. An incorrect offset corrupts raw IDs at compile time and can make match callbacks return the wrong metadata. The `as_ptr` provenance trick must keep the sentinel addressable for C scans.

## Test Signals
Build tests should inspect generated table size, sentinel zeroing, index storage, and modpost aliases. Runtime bus-match tests should confirm matched IDs recover the correct `IdInfo`, including multi-entry tables and no-match behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/device_id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/devres.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/devres.rs

## Purpose
`devres.rs` wraps Linux device-managed resources for Rust. It provides `Devres<T>`, which couples a device-bound resource with `Revocable<T>` so access is revoked before device unbind completes, and a simpler `register` helper for drop-on-unbind resources.

## Important APIs, Types, and Functions
`Inner<T>` embeds a `devres_node` and `Revocable<T>`. `Devres<T>` stores an `ARef<Device>` and an `Arc<Inner<T>>`. Important methods include `Devres::new`, `device`, `access`, `try_access`, `try_access_with`, and `try_access_with_guard`. C callbacks are `devres_node_release` and `devres_node_free_node`. The `base` module provides non-inlined wrappers for devres C symbols. `register_foreign` and public `register` use `devm_add_action_or_reset`.

## Control Flow
`Devres::new` allocates and pins `Inner<T>`, initializes a devres node with release/free callbacks, registers it on a bound device, and leaks an extra `Arc` reference for devres ownership. On device unbind, the devres release callback revokes access, and the free callback drops the extra `Arc`. If the Rust `Devres` handle drops first, it revokes without waiting, removes the devres node if still present, and releases the devres-owned reference.

## State and Persistence
All state is transient kernel memory tied to the device lifetime. The device keeps a devres node; Rust keeps an `Arc` and a device reference. `Revocable<T>` is the access gate and ensures no new accesses after revocation.

## Dependencies and Integration Points
The module depends on `Device<Bound>`, `ARef`, `Arc`, `Revocable`, RCU guards, `ForeignOwnable`, and devres bindings. DMA, DRM registration, IRQ/class/subsystem wrappers, and bus resources can use it to bind cleanup to unbind.

## Risks
The subtle risks are double-free or leaked `Arc` ownership between Rust drop and devres callbacks, using `access` with a different device, and assuming `try_access` remains valid after unbind starts. The comments also note monomorphization/export concerns for direct C binding calls.

## Test Signals
Exercise drop-before-unbind and unbind-before-drop paths, concurrent `try_access` while unbinding, `access` with matching and mismatched devices, `devm_add_action_or_reset` failure cleanup, and leak checks over repeated probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/devres.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/dma.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/dma.rs

## Purpose
`dma.rs` provides Rust abstractions for Linux DMA configuration and coherent memory allocation. It covers DMA masks, mapping attributes, data directions, CPU-staged coherent allocations, shared coherent allocations, no-kernel-mapping handles, and projection macros for hardware-shared structures.

## Important APIs, Types, and Functions
`DmaAddress` aliases `dma_addr_t`. The `dma::Device` trait exposes `dma_set_mask`, `dma_set_coherent_mask`, `dma_set_mask_and_coherent`, and `dma_set_max_seg_size`. `DmaMask`, `Attrs`, `attrs::*`, and `DataDirection` model C DMA constants. `CoherentBox<T>` owns CPU-only staged coherent memory. `Coherent<T>` exposes a DMA handle and unsafe CPU access. `CoherentHandle` represents hardware-only coherent memory with `DMA_ATTR_NO_KERNEL_MAPPING`. Macros `dma_read!` and `dma_write!` project into `Coherent` buffers.

## Control Flow
Drivers set DMA masks from probe before allocating. `CoherentBox` allocates a `Coherent`, lets the CPU safely initialize it before the DMA address is exposed, and then converts into `Coherent`. `Coherent` allocation calls `dma_alloc_attrs`, stores the CPU pointer, DMA address, attrs, and an owning device reference, then frees via `dma_free_attrs` on drop. Binary debugfs reads call `writer.write_dma` for coherent buffers. `CoherentHandle` adds `DMA_ATTR_NO_KERNEL_MAPPING` and exposes only size and DMA address.

## State and Persistence
DMA allocation state is in memory and device/IOMMU state. `Coherent` and `CoherentHandle` hold a refcounted device reference so free calls have a valid device pointer. No durable persistence exists, but hardware may access memory until the driver stops the device.

## Dependencies and Integration Points
The module depends on `Device<Core>` for mask setup, `Device<Bound>` for allocation, debugfs binary writer support, `KnownSize`, `AsBytes`, `FromBytes`, userspace slice writers, and DMA mapping bindings. It is intended for bus drivers and can be exported through debugfs.

## Risks
The file explicitly notes a soundness gap: DMA allocations can carry device/IOMMU resources and ideally need devres-style revocation without making CPU memory access cumbersome. Safe CPU references from `Coherent` are unsafe because callers must prevent device races. Drops require hardware to be halted. Size overflow, zero-length allocations, ZSTs, and architecture-dependent DMA address width are handled but need tests.

## Test Signals
Test mask setup, coherent scalar and slice allocation, zero-length and overflow rejection, initialization failure cleanup, no-kernel-mapping allocation/free, debugfs binary reads with offsets, `dma_read!`/`dma_write!` projections, and remove paths where hardware is stopped before allocations drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/dma.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/driver.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/driver.rs

## Purpose
`driver.rs` is the bus-independent driver registration and adapter framework for Rust kernel drivers. It documents how bus-specific driver traits should be shaped and provides common registration, post-unbind cleanup, module macro support, and OF/ACPI ID matching helpers.

## Important APIs, Types, and Functions
Unsafe `DriverLayout` describes a C driver structure embedding `struct device_driver` and its Rust private data type. Unsafe `RegistrationOps` supplies bus-specific `register` and `unregister`. `Registration<T>` owns a pinned C driver structure. `module_driver!` builds a one-driver module. `Adapter` supplies `IdInfo`, `acpi_id_table`, `of_id_table`, `acpi_id_info`, `of_id_info`, and `id_info`.

## Control Flow
`Registration::new` zero/default-initializes the bus driver structure, attaches a generic `post_unbind_rust` callback to the embedded `struct device_driver`, and calls the bus-specific registration function. On unregistration, `PinnedDrop` calls the matching unregister function. After a device is unbound and remove/devres callbacks are complete, `post_unbind_callback` obtains and drops the Rust driver private data from the device. Adapter ID lookup first checks ACPI, then OF.

## State and Persistence
State is the registered C driver structure plus any driver-private data stored on bound devices through `device.rs`. Registration persists until the Rust `Registration` is dropped. There is no durable storage.

## Dependencies and Integration Points
The module depends on ACPI, OF, `device`, `device_id`, `Opaque`, and `ThisModule`. Bus-specific wrappers such as platform, PCI, and auxiliary implement `RegistrationOps` and their own driver traits on top of this infrastructure.

## Risks
The unsafe layout contracts are central: wrong `DEVICE_DRIVER_OFFSET`, wrong `DriverData`, or non-`repr(C)` driver layouts can corrupt memory. Post-unbind cleanup assumes bus code stored driver data using the generic device helper. Registration/unregistration ordering must be exact; unregister is only valid after successful register.

## Test Signals
Build a minimal bus driver using `module_driver!`, validate successful and failing registration paths, bind/unbind repeatedly and confirm private data drops after devres cleanup, test ACPI/OF table matching and no-match behavior, and run KASAN/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/device.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/drm/device.rs

## Purpose
`drm/device.rs` wraps `struct drm_device` for Rust DRM drivers. It subclasses the DRM device allocation to include typed driver data, installs a Rust-generated `drm_driver` vtable, and provides refcount and workqueue integration.

## Important APIs, Types, and Functions
`Device<T: drm::Driver>` embeds `Opaque<drm_device>` and `T::Data`. `Device::VTABLE` assembles DRM callbacks, GEM allocation hooks, metadata, ioctl list, features, and file operations. `Device::new` allocates and initializes a DRM device. `as_raw`, unsafe `from_raw`, `from_drm_device`, `into_drm_device`, and `release` bridge raw C pointers. The file implements `Deref<Target = T::Data>`, `AlwaysRefCounted`, `AsRef<device::Device>`, `Send`, `Sync`, `WorkItem`, `HasWork`, and `HasDelayedWork`.

## Control Flow
Creation uses `__drm_dev_alloc` with a temporary vtable that lacks `release` until Rust data initialization succeeds. It then initializes `T::Data`, installs the final vtable, and returns an `ARef` owning the initial DRM reference. DRM callbacks open files through `drm::File`, manage GEM operations through `T::Object::ALLOC_OPS`, and call `release` when the final DRM refcount drops.

## State and Persistence
State is in the DRM core object plus inline Rust driver data. The object is refcounted by DRM `drm_dev_get` and `drm_dev_put`. No persistent storage exists; registration with userspace is handled by `drm/driver.rs`.

## Dependencies and Integration Points
This module integrates `device::Device`, `drm::Driver`, `drm::File`, GEM object allocation hooks, DRM file operations, and workqueue traits. It is the central object passed to driver ioctls and GEM object constructors.

## Risks
The main risks are initialization failure cleanup, vtable lifetime, container-of pointer arithmetic, and callback type coherence. The ioctl macro notes that device/file generic matching is not fully enforced by the type system. Workqueue container traits rely on `T::Data` being stored inline and not moving.

## Test Signals
Test successful allocation, failure during `T::Data` initialization, DRM refcount get/put, registration/unregistration, open/postclose callbacks, ioctl dispatch, GEM object creation, and queued work finding the containing DRM device correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/driver.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/drm/driver.rs

## Purpose
`drm/driver.rs` defines the Rust-side DRM driver contract and registration wrapper. It describes driver metadata, memory-manager callbacks, the main `Driver` trait, and a devres-backed registration path.

## Important APIs, Types, and Functions
`DriverInfo` stores version, name, and description. `AllocOps` stores optional C callbacks for GEM object creation, PRIME import/export, dumb buffer operations, and mmap offset handling. `AllocImpl` is implemented by memory managers and links an object type to its driver. The `Driver` trait defines associated `Data`, `Object`, `File`, `INFO`, and `IOCTLS`. `Registration<T>` wraps an `ARef<drm::Device<T>>`.

## Control Flow
`Registration::new` calls `drm_dev_register` and stores a device reference if registration succeeds. `Registration::new_foreign_owned` verifies the DRM device's underlying `struct device` matches the bound device, creates a registration, and hands it to `devres::register` so unregistration runs automatically on device unbind. Drop calls `drm_dev_unregister`.

## State and Persistence
Registration state is an in-memory device reference plus the DRM core registration state visible to userspace. It persists until the `Registration` object is dropped, commonly through devres on unbind.

## Dependencies and Integration Points
The module depends on DRM device wrappers, GEM allocation traits, `device::Device<Bound>`, `devres`, and DRM registration bindings. `drm/device.rs` consumes `Driver::INFO`, `Driver::IOCTLS`, and `Object::ALLOC_OPS` when building the vtable.

## Risks
The devres registration helper assumes the DRM device and bound device are the same underlying object; mismatch returns `EINVAL`. Drop must only unregister devices that were successfully registered. Allocation ops are raw C callbacks, so object memory-manager implementations must provide functions compatible with DRM expectations.

## Test Signals
Register and unregister a minimal DRM device, bind registration to devres and confirm unregistration on remove, validate mismatched-device rejection, expose metadata through DRM tools, and exercise IOCTL/GEM tables installed from the driver trait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/file.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/drm/file.rs

## Purpose
`drm/file.rs` provides typed Rust wrappers for per-client DRM file state. It lets a DRM driver allocate Rust file-private data on open and reclaim it on postclose.

## Important APIs, Types, and Functions
`DriverFile` is implemented by drivers and defines the parent `Driver` plus `open(device) -> Pin<KBox<Self>>`. `File<T: DriverFile>` transparently wraps `struct drm_file`. Important methods are unsafe `File::from_raw`, `as_raw`, private `driver_priv`, `inner`, `open_callback`, and `postclose_callback`.

## Control Flow
When DRM opens a device node, `open_callback` converts the raw DRM device to the typed `drm::Device`, wraps the raw `drm_file`, calls `T::open`, and stores the resulting pinned `KBox<T>` in `drm_file.driver_priv`. On close, `postclose_callback` recovers that pointer and drops the box. IOCTL handlers use `File::from_raw` and `inner()` to access the typed state.

## State and Persistence
The only persistent state is per-open file-private driver data stored in `driver_priv`. It exists from successful open until postclose and is pinned for that entire interval.

## Dependencies and Integration Points
This module integrates with `drm::Device`, `drm::Driver`, DRM open/postclose callbacks installed in `drm/device.rs`, and ioctl dispatch in `drm/ioctl.rs`.

## Risks
The safety contract depends on raw files having been opened through the matching `T::open`. A failed open must not leave `driver_priv` initialized. `Pin::into_inner_unchecked` is used only to leak the box into C; postclose must always reclaim it to avoid leaks. Type matching between ioctl file type and driver is only indirectly enforced.

## Test Signals
Open and close DRM nodes repeatedly, fail `DriverFile::open` and verify no private data leak, call ioctls that read file-private state, and run leak/KASAN checks during process exit and driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/gem/mod.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/drm/gem/mod.rs

## Purpose
`drm/gem/mod.rs` implements the base Rust DRM GEM object abstraction. It defines driver object traits, raw GEM conversion, handle lookup/creation helpers, object lifetime callbacks, and DRM file operations for GEM-capable drivers.

## Important APIs, Types, and Functions
`DriverObject` defines `Driver`, `Args`, `new`, `open`, and `close`. `IntoGEMObject` converts typed objects to and from raw `drm_gem_object`. `BaseObject` provides `size`, `create_handle`, `lookup_handle`, and `create_mmap_offset`. `BaseObjectPrivate` exposes `raw_dma_resv`. `Object<T>` embeds `drm_gem_object` and pinned driver data. `impl_aref_for_gem_obj!` implements GEM refcounting. `create_fops` creates DRM GEM file operations.

## Control Flow
`Object::new` allocates a pinned Rust object, installs object funcs, calls `drm_gem_object_init`, and transfers the initial GEM reference into `ARef<Self>`. GEM open/close callbacks convert raw object and file pointers back to typed wrappers and invoke driver hooks. `free_callback` releases GEM base state and drops the `KBox` when the final GEM reference is gone. Handle lookup takes ownership of the reference returned by `drm_gem_object_lookup`.

## State and Persistence
GEM state is in-memory DRM object state plus typed driver data. Object references are managed by DRM GEM refcounting. Handles and mmap offsets are per-DRM-file/core state, not durable across process or driver lifetime.

## Dependencies and Integration Points
This module integrates with `drm::Driver`, `drm::File`, `drm::driver::AllocImpl`, DRM GEM C helpers, `ARef`, and optional shmem GEM support. `drm/device.rs` installs `create_fops` and allocation ops into the DRM driver vtable.

## Risks
Raw pointer conversion relies on object type coherence: a raw GEM object must actually be embedded in the expected Rust type. The code comments note a typo-level risk around proof assumptions for `lookup_handle`; practically the file and object driver associations must stay aligned. Object initialization failure requires the correct private cleanup path.

## Test Signals
Create and drop GEM objects, open/close handles, look up valid and invalid handles, create mmap offsets, unload with live handles, exercise free callbacks, and run PRIME/dumb-buffer tests for memory managers that fill `AllocOps`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/gem/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/gem/shmem.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/drm/gem/shmem.rs

## Purpose
`drm/gem/shmem.rs` implements Rust support for shmem-backed DRM GEM objects using the kernel DRM shmem helpers. It lets drivers use standard shmem pin/vmap/mmap/dumb-buffer behavior while storing typed Rust object data.

## Important APIs, Types, and Functions
`ObjectConfig<'a, T>` configures object creation with `map_wc` and optional `parent_resv_obj`. `Object<T>` embeds `drm_gem_shmem_object`, optional parent reservation owner, and pinned inner driver object. `Object::VTABLE` points at DRM shmem helper callbacks. Important methods include `Object::new`, `as_raw_shmem`, `dev`, `free_callback`, `IntoGEMObject::as_raw`, and unsafe `from_raw`. The `AllocImpl` implementation enables shmem PRIME import and dumb create callbacks.

## Control Flow
Creation allocates and pins the Rust object, initializes parent reservation ownership and inner driver data, installs the shmem object funcs, and calls `drm_gem_shmem_init`. After taking over the initial reference, it optionally replaces the base reservation object with a parent object's reservation and sets the write-combine map flag before exposing the object. Free callbacks release shmem resources and then recover the Rust allocation.

## State and Persistence
State is in-memory GEM shmem state: the base GEM object, shmem pages, reservation object, optional parent object reference, and typed inner data. The optional parent reference keeps a reused reservation owner alive.

## Dependencies and Integration Points
The module depends on `drm_gem_shmem_helper` bindings, base GEM traits, DRM device and driver traits, `ARef`, and the private sealed trait. It is compiled only when `CONFIG_RUST_DRM_GEM_SHMEM_HELPER` enables the parent module export.

## Risks
Reservation sharing is delicate: the new object mutates `base.resv` before exposure and must hold a parent reference for lifetime. Manual `dma_resv_lock` handling is called out as a TODO for future ww-mutex support. `from_raw` and free callback container arithmetic assume all raw objects came from this shmem object type.

## Test Signals
Create shmem objects with and without `map_wc`, share reservations through `parent_resv_obj`, create dumb buffers, import PRIME sg tables, mmap/vmap/pin/unpin objects, close handles while parents remain alive, and remove the driver with live userspace mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/gem/shmem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/ioctl.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/drm/ioctl.rs

## Purpose
`drm/ioctl.rs` provides helpers for declaring DRM ioctl numbers and generating typed DRM ioctl descriptors for Rust drivers. It bridges DRM's C ioctl dispatch to Rust handlers with typed device, argument, and file references.

## Important APIs, Types, and Functions
Const functions `IO`, `IOR`, `IOW`, and `IOWR` build DRM ioctl numbers using `DRM_IOCTL_BASE`. `DrmIoctlDescriptor` aliases `drm_ioctl_desc`. Flag constants `AUTH`, `MASTER`, `ROOT_ONLY`, and `RENDER_ALLOW` expose DRM ioctl policy bits. The `internal` module re-exports raw C types for macro expansion. `declare_drm_ioctls!` generates a static `IOCTLS` descriptor slice and one C callback per ioctl.

## Control Flow
The macro validates at compile time that declared ioctls are contiguous from `DRM_COMMAND_BASE` and that each UAPI struct size matches the encoded ioctl size. Each generated callback converts raw DRM pointers to a typed `drm::Device`, mutable UAPI argument reference, and typed `drm::File`, calls the Rust handler, then converts `Result<u32>` to a C int errno or return value.

## State and Persistence
The generated ioctl descriptor array is static driver metadata. Per-call state is the C-provided ioctl argument buffer and live DRM device/file references. No persistent state is stored here.

## Dependencies and Integration Points
This module depends on generic ioctl-number helpers, DRM UAPI constants and structs, `drm::Device`, `drm::File`, and the `drm::Driver::IOCTLS` associated constant consumed by `drm/device.rs`.

## Risks
The macro's FIXME is important: the type system does not fully prove that raw device/file pointers match the driver declaring the ioctls. UAPI structs must accept all bit patterns because the macro creates `&mut` references from raw ioctl buffers. Return values that do not fit in C int are mapped to `ERANGE`.

## Test Signals
Compile drivers with ordered and intentionally misordered ioctl declarations, check size assertions, invoke ioctls through primary and render nodes with different flags, verify errno mapping, and fuzz UAPI argument buffers for handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/ioctl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/mod.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/drm/mod.rs

## Purpose
`drm/mod.rs` is the public module facade for Rust DRM abstractions. It organizes the DRM device, driver, file, GEM, and ioctl submodules and re-exports the primary types used by drivers.

## Important APIs, Types, and Functions
The module declares `device`, `driver`, `file`, `gem`, and `ioctl`. It re-exports `Device`, `Driver`, `DriverInfo`, `Registration`, and `File`. The private `Sealed` trait prevents external implementations of internal DRM extension traits.

## Control Flow
This file has no runtime control flow. Its compile-time role is to expose the expected public API surface and keep internal sealing available to submodules.

## State and Persistence
The module owns no state. State lives in the device, registration, file, and GEM object modules.

## Dependencies and Integration Points
It is the import point for Rust DRM drivers and for other kernel modules that need DRM types. Submodules use `drm::private::Sealed` to restrict traits such as GEM object conversion and allocation implementations to crate-controlled types.

## Risks
Risks are API-organization issues rather than runtime bugs. Re-exporting a type makes it part of the intended public Rust kernel API surface, while sealing controls which traits downstream drivers can implement. Feature gating for submodules such as shmem must remain consistent with their internal `cfg` use.

## Test Signals
Build drivers importing only `kernel::drm::*`, verify rustdoc links and cfg-gated modules, ensure sealed traits cannot be implemented externally, and compile with DRM and DRM shmem helper configurations enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/drm/mod.rs -->
