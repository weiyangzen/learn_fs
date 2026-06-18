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
