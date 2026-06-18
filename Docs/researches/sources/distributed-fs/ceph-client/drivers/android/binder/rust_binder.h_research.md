# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder.h

Purpose: declares the public C-facing ABI used between Rust Binder, binderfs C code, and tracepoint C code. It exposes binderfs helper functions, opaque Rust object handles, layout descriptors, and inline field accessors for tracing.

Important APIs/types/functions: declarations include `init_rust_binderfs`, `rust_binderfs_create_proc_file`, and `rust_binderfs_remove_file`. Opaque typedefs are `rust_binder_transaction`, `rust_binder_process`, and `rust_binder_node`. `rb_process_layout`, `rb_transaction_layout`, `rb_node_layout`, and `rust_binder_layout` describe offsets exported by Rust as `RUST_BINDER_LAYOUT`. Inline helpers read transaction debug id, code, flags, target node, target process, process task, node debug id, and node userspace pointer.

Control flow: there is no runtime control flow beyond inline pointer arithmetic. C tracepoints receive opaque Rust pointers, add exported offsets, and dereference fields for trace payload formatting.

State and persistence: the header owns no state. It depends on `RUST_BINDER_LAYOUT` matching the in-memory Rust structs for the loaded module instance.

Dependencies and integration points: included by `rust_binder_events.c`, `rust_binder_events.h`, and binderfs glue. It includes Binder UAPI headers for `binder_uintptr_t` and binderfs types. Rust defines the corresponding layout static in `rust_binder_main.rs` from `TRANSACTION_LAYOUT`, `PROCESS_LAYOUT`, and `NODE_LAYOUT`.

Risks: this is an unsafe ABI contract. Any Rust struct layout, wrapper offset, or arc offset change must update the exported layout constants or C tracepoints will read invalid memory. Inline arithmetic on `void *` relies on compiler extensions used in the kernel. Nullable target-node handling is explicit but other pointers are assumed valid.

Test signals: build with bindgen and tracepoints enabled, boot/load the module, emit transaction trace events, and verify trace output fields match Rust debug output. Layout-sensitive changes should be checked with compile-time offset tests or targeted runtime trace smoke tests.
