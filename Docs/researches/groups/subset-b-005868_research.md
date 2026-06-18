# subset-b-005868 Research

Grouped source research for Linux kernel `include/linux` key management, debug, sanitizer, KHO ABI, object lifetime, memory management, thread, time, and device support headers in the Ceph client source snapshot. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/key.h -->
# sources/distributed-fs/ceph-client/include/linux/key.h

## Purpose

`key.h` is the internal kernel key-management interface. It defines key serial and permission types, `struct key`, keyring index metadata, possession-carrying `key_ref_t` references, allocation flags, request/search/update/link APIs, RCU payload helpers, and no-op fallbacks when `CONFIG_KEYS` is disabled. The source was read as a complete 520-line file.

## Important APIs, Types, and Functions

Core types include `key_serial_t`, `key_perm_t`, `enum key_need_perm`, `enum key_lookup_flag`, `struct key_tag`, `struct keyring_index_key`, `union key_payload`, `key_ref_t`, `struct key_restriction`, `enum key_state`, and `struct key`. Important APIs are `key_alloc()`, `key_revoke()`, `key_invalidate()`, `key_put()`, `request_key_tag()`, `request_key_rcu()`, `request_key_with_auxdata()`, `wait_for_key_construction()`, `key_validate()`, `key_create()`, `key_create_or_update()`, `key_update()`, `key_link()`, `key_move()`, `key_unlink()`, `keyring_alloc()`, `keyring_search()`, `keyring_restrict()`, `lookup_user_key()`, and `key_set_timeout()`. Inline helpers encode possession in the low bit of `key_ref_t` and use acquire semantics in `key_read_state()`.

## Control Flow

Callers allocate or request keys, optionally wait for construction, validate state and permissions, then link/search/update/unlink keys through keyrings. Payload replacement is protected by the key semaphore and exposed through RCU helpers. Network namespaces can scope searches by using a namespace key domain tag. When keys are disabled, almost every operation compiles into a stub, so callers must tolerate missing key support.

## State and Persistence Behavior

`struct key` persists in kernel memory under refcount control and carries quota, owner UID/GID, permission bits, state, expiry or revocation time, payload pointers, keyring association arrays, and restriction policy. There is no file-backed persistence here; state survives until references, keyrings, quota accounting, and RCU callbacks release it.

## Dependencies and Integration Points

The header integrates credentials, user namespaces, network namespaces, assoc arrays, RCU, rwsems, refcounting, security blobs, key notifications, and the userspace keyctl path. Filesystems, crypto, auth, and networking subsystems use it to request and cache authentication material.

## Risks and Edge Cases

The low-bit `key_ref_t` possession encoding depends on pointer alignment and must never be dereferenced directly. State reads require ordering against instantiation. Payload `datalen` may not match RCU payload internals. Restrictions can be bypassed only with explicit allocation flags. Stubs under `!CONFIG_KEYS` can hide missing feature coverage.

## Test Signals

Useful signals include keyrings selftests, keyctl syscall tests, permission/possession matrix tests, RCU payload replacement stress, namespace-domain request tests, quota and expiry/revocation tests, and `!CONFIG_KEYS` build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/keyboard.h -->
# sources/distributed-fs/ceph-client/include/linux/keyboard.h

## Purpose

`keyboard.h` is the kernel-side keyboard notifier and keymap declaration header. It exposes the global keymap arrays from the VT/keyboard layer and the notifier payload used by consumers that need to observe keyboard events. The source was read as a complete 21-line file.

## Important APIs, Types, and Functions

The header declares `key_maps[MAX_NR_KEYMAPS]`, `plain_map[NR_KEYS]`, `struct keyboard_notifier_param`, `register_keyboard_notifier()`, and `unregister_keyboard_notifier()`. The notifier payload carries the `vc_data` console, key press direction, shift mask, LED state, and event value, which may be keycode, Unicode value, or keysym depending on notification stage.

## Control Flow

There is no local executable flow. Keyboard drivers and VT input paths update state and invoke notifier blocks; interested subsystems register a `notifier_block` and inspect `keyboard_notifier_param` for each keyboard transition.

## State and Persistence Behavior

The header declares global keymap storage but owns no lifetime logic. Notifier registrations persist until unregistered, so clients must unregister before module removal.

## Dependencies and Integration Points

It depends on `uapi/linux/keyboard.h` for keymap sizing and constants and integrates with the console/VT keyboard event pipeline.

## Risks and Edge Cases

The value field is stage-dependent, so consumers must know the notification context. Notifier callbacks run in the input path and should avoid blocking or mutating keymaps without proper synchronization.

## Test Signals

Compile coverage with VT enabled, notifier registration/unregistration smoke tests, keyboard event delivery tests, and module unload tests that verify no stale notifier remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/keyboard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/keyctl.h -->
# sources/distributed-fs/ceph-client/include/linux/keyctl.h

## Purpose

`keyctl.h` defines kernel-private structures for public-key operations used by the keyctl interface. It complements the UAPI keyctl command definitions with in-kernel query and operation parameter blocks. The source was read as a complete 42-line file.

## Important APIs, Types, and Functions

`struct kernel_pkey_query` reports supported operations, key size, maximum raw data size, signature size, encryption size, and decryption size. `enum kernel_pkey_operation` distinguishes encrypt, decrypt, sign, and verify. `struct kernel_pkey_params` carries the key pointer, encoding, hash algorithm, temporary info string, input and output sizes, and selected operation.

## Control Flow

This header has no implementation flow. Keyctl command handlers and asymmetric key implementations fill or consume these structures when dispatching public-key operations.

## State and Persistence Behavior

The structures are transient call descriptors. They hold a borrowed `struct key *` and, for `info`, ownership of a temporary string that the caller must release according to the implementation contract.

## Dependencies and Integration Points

It includes `uapi/linux/keyctl.h` and relies on `struct key` from the key subsystem. It integrates with asymmetric key types, crypto helpers, and keyctl syscall handling.

## Risks and Edge Cases

Size fields are ABI-sensitive and must match user buffer validation. Verify uses a second input length instead of output length through a union, so callers must branch by `op` correctly. Encoding/hash strings require strict validation by key type backends.

## Test Signals

Keyctl public-key selftests, asymmetric key sign/verify/encrypt/decrypt tests, unsupported operation tests, max-size boundary tests, and bad encoding/hash input tests are useful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/keyctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kfence.h -->
# sources/distributed-fs/ceph-client/include/linux/kfence.h

## Purpose

`kfence.h` is the public allocator and fault-handler integration surface for Kernel Electric-Fence. It lets slab allocators occasionally return guarded heap objects, identify KFENCE pool addresses, size and free KFENCE objects, and handle faults raised by guard pages. The source was read as a complete 254-line file.

## Important APIs, Types, and Functions

Important definitions include `KFENCE_POOL_SIZE`, `__kfence_pool`, `kfence_allocation_key`, `kfence_allocation_gate`, and `kfence_sample_interval`. Public hooks include `is_kfence_address()`, `kfence_alloc_pool_and_metadata()`, `kfence_init()`, `kfence_shutdown_cache()`, `kfence_alloc()`, `kfence_ksize()`, `kfence_object_start()`, `kfence_free()`, `kfence_handle_page_fault()`, and `__kfence_obj_info()` under printk.

## Control Flow

Boot code allocates pool/metadata and initializes the sampling gate. Allocator fast paths call `kfence_alloc()`, which checks a static branch and allocation gate before falling into `__kfence_alloc()`. Free paths call `kfence_free()` on arbitrary heap addresses; KFENCE handles only pool addresses. Page faults inside the pool are routed to `kfence_handle_page_fault()` to report memory errors and make the page accessible enough for controlled continuation.

## State and Persistence Behavior

KFENCE owns a fixed pool and metadata for sampled objects. Objects persist as live, freed, or zombie allocation records until the pool slot is reused. The header itself stores only declarations and inline gate checks.

## Dependencies and Integration Points

It integrates with SLAB/SLUB allocation/free paths, memblock boot allocation, static keys, atomics, page fault handling, printk object inspection, and cache destruction.

## Risks and Edge Cases

`is_kfence_address()` is fast-path critical and must keep the range check safe when `__kfence_pool` is NULL. Allocators must never return KFENCE objects to normal freelists. `kfence_shutdown_cache()` handles the difficult case of live sampled objects during cache teardown.

## Test Signals

KFENCE selftests, sampled allocation/free paths, use-after-free and out-of-bounds fault tests, `CONFIG_KFENCE=n` build coverage, cache destroy diagnostics, and fast-path performance checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kfifo.h -->
# sources/distributed-fs/ceph-client/include/linux/kfifo.h

## Purpose

`kfifo.h` provides the generic typed kernel FIFO API. It supports in-place FIFOs, dynamically allocated FIFO buffers, fixed-size element queues, record FIFOs with 1- or 2-byte length fields, spinlocked wrappers, user-copy helpers, and DMA scatterlist preparation. The source was read as a complete 1000-line file.

## Important APIs, Types, and Functions

Core storage is `struct __kfifo` with `in`, `out`, `mask`, element size, and data pointer. Macro types include `STRUCT_KFIFO()`, `STRUCT_KFIFO_PTR()`, `STRUCT_KFIFO_REC_1()`, and `STRUCT_KFIFO_REC_2()`. Main APIs include `DECLARE_KFIFO`, `DEFINE_KFIFO`, `INIT_KFIFO`, `kfifo_alloc()`, `kfifo_alloc_node()`, `kfifo_init()`, `kfifo_free()`, `kfifo_in()`, `kfifo_out()`, `kfifo_put()`, `kfifo_get()`, `kfifo_peek()`, `kfifo_from_user()`, `kfifo_to_user()`, `kfifo_dma_*()`, `kfifo_out_linear()`, and many `__kfifo_*` backend declarations.

## Control Flow

Callers declare or allocate a power-of-two ring, initialize counters and element size, then push and pop by advancing monotonic `in` and `out` counters masked into the buffer. Record FIFOs route through `_r` helpers to prepend/read record lengths. Single producer plus single consumer needs no extra lock; multi-producer or multi-consumer paths wrap calls in spinlock variants.

## State and Persistence Behavior

FIFO state is entirely in memory. Dynamic FIFOs own allocated buffer memory until `kfifo_free()`. In-place FIFOs embed the buffer in the containing object. Counters are free-running `unsigned int` values, so correctness depends on size/mask arithmetic and the assumption that distance between `in` and `out` is bounded by FIFO size.

## Dependencies and Integration Points

It depends on spinlocks, barrier primitives, errno, typed macro extensions, user-copy implementations in the C backend, DMA scatterlists, and NUMA allocation. Drivers use it for byte streams, event queues, DMA staging, and control paths.

## Risks and Edge Cases

Compile-time negative array sizing catches non-power-of-two in-place sizes. `kfifo_reset()` is unsafe with concurrent access. DMA finish helpers do no bounds checking. Record FIFOs reserve length bytes, so availability can be zero even when raw free space exists. Return values are marked must-check in many paths and should not be ignored.

## Test Signals

Kernel kfifo tests, wraparound tests, typed put/get compile tests, record FIFO length boundary tests, spinlocked multi-thread stress, user-copy fault injection, DMA scatterlist preparation tests, and 32-bit counter wrap stress are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kfifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kgdb.h -->
# sources/distributed-fs/ceph-client/include/linux/kgdb.h

## Purpose

`kgdb.h` defines the shared API between KGDB core code, architecture code, and KGDB I/O drivers. It covers breakpoint representation, register conversion, exception handling, CPU roundup, remote GDB packet helpers, and stubs for non-KGDB builds. The source was read as a complete 356-line file.

## Important APIs, Types, and Functions

Important state and types include `kgdb_connected`, `kgdb_active`, `kgdb_setting_breakpoint`, `kgdb_cpu_doing_single_step`, `enum kgdb_bptype`, `enum kgdb_bpstate`, `struct kgdb_bkpt`, `struct dbg_reg_def_t`, `struct kgdb_arch`, and `struct kgdb_io`. APIs include `kgdb_breakpoint()`, `kgdb_arch_init()`, `kgdb_arch_exit()`, `pt_regs_to_gdb_regs()`, `sleeping_thread_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, `kgdb_arch_handle_exception()`, `kgdb_roundup_cpus()`, `kgdb_arch_set_pc()`, `kgdb_register_io_module()`, `kgdb_handle_exception()`, `kgdb_nmicallback()`, and `kgdb_panic()`.

## Control Flow

An exception or explicit breakpoint enters KGDB, architecture code converts registers and handles arch-specific commands, the I/O module exchanges packets with GDB, and KGDB may single-step, continue, set breakpoints, or round up other CPUs. `kgdb_within_blocklist()` optionally shares the kprobe blacklist to avoid probing/debugging unsafe addresses.

## State and Persistence Behavior

Breakpoint slots preserve original instructions and state while active. KGDB connection, selected threads, active CPU, and registered I/O module are global kernel state. There is no durable persistence.

## Dependencies and Integration Points

It integrates with `asm/kgdb.h`, `pt_regs`, kprobes blacklist logic, consoles or serial drivers implementing `struct kgdb_io`, NMI callbacks, SMP CPU coordination, and architecture breakpoint/register code.

## Risks and Edge Cases

KGDB runs in exception/NMI-like contexts, so callbacks must be reentrant and avoid unsafe locks. Breakpoint instruction sizes and register layouts are architecture-specific. Missing blocklist support may permit breakpoints in unsafe code. Non-KGDB builds stub many APIs, hiding runtime behavior from generic compilation.

## Test Signals

Architecture KGDB selftests, remote GDB attach/continue/single-step tests, hardware breakpoint tests, SMP roundup tests, panic entry tests, I/O module register/unregister tests, and `CONFIG_KGDB=n` build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_handover.h -->
# sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_handover.h

## Purpose

`kexec_handover.h` defines the stable Kexec Handover ABI for passing preserved data from one kernel to the next. It specifies the root FDT compatible string and properties, serializable pointer macros, vmalloc preservation layouts, and radix-tree ABI nodes for preserved physical memory tracking. The source was read as a complete 289-line file.

## Important APIs, Types, and Functions

Important constants include `KHO_FDT_COMPATIBLE`, `KHO_FDT_MEMORY_MAP_PROP_NAME`, `KHO_SUB_TREE_PROP_NAME`, `KHO_SUB_TREE_SIZE_PROP_NAME`, `KHO_VMALLOC_SIZE`, and `KHO_TREE_MAX_DEPTH`. Types include `struct kho_vmalloc_hdr`, `struct kho_vmalloc_chunk`, `struct kho_vmalloc`, `enum kho_radix_consts`, `struct kho_radix_node`, and `struct kho_radix_leaf`. Helper macros are `DECLARE_KHOSER_PTR()`, `KHOSER_STORE_PTR()`, and `KHOSER_LOAD_PTR()`.

## Control Flow

The old kernel builds an FDT with physical addresses for preserved memory map data and subsystem blobs. Serializable pointers are stored as physical addresses before handover and loaded through `phys_to_virt()` by the new kernel. Vmalloc preservation walks chunks of physical page addresses; preserved-page tracking uses a multi-level page-sized radix tree with bitmap leaves.

## State and Persistence Behavior

Everything in this header is ABI state that intentionally persists across kexec. The packed physical references, page-sized chunks, and radix layout must remain interpretable by another kernel supporting the same compatible version.

## Dependencies and Integration Points

It depends on page geometry, bit helpers, log2 math, and physical/virtual address conversion. It is consumed by KHO core, preserved-memory map code, vmalloc preservation, and subsystem subtree registration.

## Risks and Edge Cases

Any incompatible FDT property, compatible string, or structure layout change requires a version bump. Pointer serialization assumes the referenced memory is preserved and identity-mappable enough for `phys_to_virt()` in the new kernel. Radix constants depend on page size and 64-bit key encoding.

## Test Signals

KHO boot/kexec handover tests, FDT compatibility validation, static structure size checks such as `kho_vmalloc_chunk == PAGE_SIZE`, radix tree encode/decode tests, and cross-version rejection tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_handover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_metadata.h -->
# sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_metadata.h

## Purpose

`kexec_metadata.h` defines a small optional KHO metadata ABI that records the previous kernel release and kexec count across a kexec chain. The source was read as a complete 46-line file.

## Important APIs, Types, and Functions

The header defines `KHO_KEXEC_METADATA_VERSION`, `KHO_METADATA_NODE_NAME`, and packed `struct kho_kexec_metadata` with `version`, `previous_release[__NEW_UTS_LEN + 1]`, and `kexec_count`.

## Control Flow

There is no executable flow. The previous kernel registers a `kexec-metadata` subtree through KHO and stores this struct in preserved memory; the next kernel reads it to identify its predecessor and update the count.

## State and Persistence Behavior

The struct is preserved across kexec as plain C data. `version` must remain first so future readers can safely decide how to interpret the remaining bytes.

## Dependencies and Integration Points

It includes `linux/types.h` and `linux/utsname.h`. It integrates with KHO subtree registration and kernel release identification.

## Risks and Edge Cases

Because the data is not an FDT payload, layout and packing are the ABI. `previous_release` uses the UAPI-sized `__NEW_UTS_LEN`, so changes must maintain the version contract. Readers should reject unsupported versions and validate string termination.

## Test Signals

Kexec metadata preservation tests, version mismatch tests, string length/termination checks, and repeated-kexec count increment tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/luo.h -->
# sources/distributed-fs/ceph-client/include/linux/kho/abi/luo.h

## Purpose

`luo.h` defines the Live Update Orchestrator ABI built on Kexec Handover. It specifies FDT node names and compatible strings plus packed serialization structures for live-update sessions, preserved files, and file-lifecycle-bound global objects. The source was read as a complete 247-line file.

## Important APIs, Types, and Functions

Key constants include `LUO_FDT_KHO_ENTRY_NAME`, `LUO_FDT_COMPATIBLE`, `LUO_FDT_LIVEUPDATE_NUM`, `LUO_FDT_SESSION_NODE_NAME`, `LUO_FDT_SESSION_COMPATIBLE`, `LUO_FDT_SESSION_HEADER`, `LUO_FDT_FLB_NODE_NAME`, `LUO_FDT_FLB_COMPATIBLE`, and `LUO_FDT_FLB_HEADER`. Types include packed `struct luo_file_ser`, `struct luo_file_set_ser`, `struct luo_session_header_ser`, `struct luo_session_ser`, `struct luo_flb_header_ser`, and `struct luo_flb_ser`.

## Control Flow

The old kernel serializes sessions and global file-bound objects into preserved memory, publishes physical addresses through an FDT subtree named `LUO`, and increments `liveupdate-number`. The new kernel parses compatible nodes, walks session/file arrays and FLB arrays, then invokes matching liveupdate handlers by compatible string.

## State and Persistence Behavior

All structs are packed ABI payloads. They persist across kexec and carry names, handler compatibility strings, opaque handler data, tokens, counts, file-set pointers, and page counts.

## Dependencies and Integration Points

It depends on `uapi/linux/liveupdate.h` for session name sizing and integrates with LUO core, KHO subtree handover, memfd preservation, and handler registration by compatible strings.

## Risks and Edge Cases

The documentation says session examples use v1, while the constant is `luo-session-v2`; consumers must follow constants. Layout changes require compatible-string bumps. Count fields must be validated before array walking to avoid interpreting corrupted preserved memory.

## Test Signals

Live update serialization/restore tests, FDT compatible/version validation, session and FLB count bounds tests, handler lookup tests, and cross-kernel compatibility tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/luo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/memblock.h -->
# sources/distributed-fs/ceph-client/include/linux/kho/abi/memblock.h

## Purpose

`memblock.h` defines the KHO ABI constants for preserving `reserve_mem` memblock reservations across kexec. The source was read as a complete 73-line file.

## Important APIs, Types, and Functions

The file defines `MEMBLOCK_KHO_FDT`, `MEMBLOCK_KHO_NODE_COMPATIBLE`, and `RESERVE_MEM_KHO_NODE_COMPATIBLE`. The documented FDT schema has a root `memblock` entry compatible with `memblock-v1`, with child reserve-memory nodes compatible with `reserve-mem-v1` and `start`/`size` u64 properties.

## Control Flow

There is no local code. The old kernel serializes named reserve-mem regions into the memblock KHO FDT; the new kernel parses those nodes and recreates reservations at the same physical addresses.

## State and Persistence Behavior

The ABI persists physical reservation names, start addresses, and sizes across kexec. The header owns no runtime state.

## Dependencies and Integration Points

It integrates with memblock reservation handling, command-line `reserve_mem`, KHO subtree registration, and FDT parsing.

## Risks and Edge Cases

FDT node names are user-defined reservation names and must be validated. Any property or compatible-string change requires versioning. The new kernel must reject overlapping, unavailable, or malformed reservations rather than blindly trusting preserved data.

## Test Signals

Kexec handover tests for named reserve-mem regions, malformed FDT property tests, overlap rejection tests, and compatible-version checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/memblock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/memfd.h -->
# sources/distributed-fs/ceph-client/include/linux/kho/abi/memfd.h

## Purpose

`memfd.h` defines the memfd Live Update ABI for serializing memfd file state across kexec through LUO and KHO. It preserves file position, size, seals, flags, folio state, and a KHO vmalloc descriptor for the folio array. The source was read as a complete 93-line file.

## Important APIs, Types, and Functions

Constants include `MEMFD_LUO_FOLIO_DIRTY`, `MEMFD_LUO_FOLIO_UPTODATE`, `MEMFD_LUO_ALL_SEALS`, and `MEMFD_LUO_FH_COMPATIBLE`. Types include packed `struct memfd_luo_folio_ser` with bitfield `pfn:52`, `flags:12`, and `index`, and packed `struct memfd_luo_ser` with `pos`, `size`, `seals`, `flags`, `nr_folios`, and `struct kho_vmalloc folios`.

## Control Flow

The old kernel serializes each relevant folio, stores the array through KHO vmalloc preservation, and hands the top-level `memfd_luo_ser` to the LUO file handler. The new kernel validates the compatible string and reconstructs the shmem/memfd file from folio PFNs and state flags.

## State and Persistence Behavior

The serialized file state persists across kexec. Seal bits are UAPI values; unsupported new seals require updating `MEMFD_LUO_ALL_SEALS` and bumping the compatible string.

## Dependencies and Integration Points

It depends on `linux/types.h`, KHO vmalloc ABI, file seal constants, LUO file handlers, and shmem/memfd internals.

## Risks and Edge Cases

The 52-bit PFN and 12-bit flags layout is packed ABI. Non-dirty but uptodate folios need correct zeroing semantics during restore. Unknown seal or flag bits must be rejected or masked by versioned rules.

## Test Signals

Memfd LUO restore tests with dirty, clean, fallocated, sealed, sparse, and large files; folio index ordering tests; unsupported seal tests; and compatible-string validation are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho/abi/memfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho_radix_tree.h -->
# sources/distributed-fs/ceph-client/include/linux/kho_radix_tree.h

## Purpose

`kho_radix_tree.h` declares the runtime API for a KHO-oriented radix tree that tracks preserved physical pages by PFN and order. It is the non-ABI wrapper around the ABI node layouts from `kho/abi/kexec_handover.h`. The source was read as a complete 70-line file.

## Important APIs, Types, and Functions

`struct kho_radix_tree` contains a root node and a mutex protecting tree structure. `kho_radix_tree_walk_callback_t` receives physical addresses and orders. Public APIs are `kho_radix_add_page()`, `kho_radix_del_page()`, and `kho_radix_walk_tree()`, with `-EOPNOTSUPP` stubs when `CONFIG_KEXEC_HANDOVER` is disabled.

## Control Flow

Client code initializes the root and mutex, adds preserved pages as they are reserved, deletes them when no longer preserved, and walks the tree to emit or consume a memory map. The implementation serializes structural mutation under the embedded mutex.

## State and Persistence Behavior

The tree root and nodes are in kernel memory; the node layout is compatible with KHO preserved-memory ABI. The header owns no allocation logic.

## Dependencies and Integration Points

It depends on errno, mutex types, physical-address types, and the KHO handover core. It integrates with preserved memory tracking before and during kexec.

## Risks and Edge Cases

Callers must initialize the mutex and root correctly. PFN/order encoding must match the ABI constants. Disabled builds return `-EOPNOTSUPP`, so callers must not assume preservation exists.

## Test Signals

Add/delete/walk radix tests, multi-order page coverage, duplicate deletion tests, disabled-config build coverage, and KHO memory-map roundtrip tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kho_radix_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/khugepaged.h -->
# sources/distributed-fs/ceph-client/include/linux/khugepaged.h

## Purpose

`khugepaged.h` declares the khugepaged transparent hugepage scanning interface. It lets memory-management paths start/stop khugepaged, enroll or remove address spaces and VMAs, update memory thresholds, and collapse PTE-mapped THPs. The source was read as a complete 60-line file.

## Important APIs, Types, and Functions

Important declarations under `CONFIG_TRANSPARENT_HUGEPAGE` include `khugepaged_attr_group`, `khugepaged_init()`, `khugepaged_destroy()`, `start_stop_khugepaged()`, `__khugepaged_enter()`, `__khugepaged_exit()`, `khugepaged_enter_vma()`, `khugepaged_min_free_kbytes_update()`, `current_is_khugepaged()`, and `collapse_pte_mapped_thp()`. Inline helpers are `khugepaged_fork()` and `khugepaged_exit()`. `khugepaged_max_ptes_none` is always declared.

## Control Flow

Process memory setup and VMA changes call enter helpers when hugepage flags are set. Fork inherits eligibility through `khugepaged_fork()`, and mm teardown calls exit. The khugepaged thread scans eligible ranges and may collapse mappings.

## State and Persistence Behavior

State lives in `mm_struct` flags, VMA flags, khugepaged sysfs tunables, and the khugepaged worker thread. No persistent storage exists.

## Dependencies and Integration Points

It integrates with THP, sysfs attribute groups, mm lifecycle, fork/exit, VMA policy, and PTE/PMD collapse paths.

## Risks and Edge Cases

Disabled THP builds stub out most behavior. Fork enrollment is best-effort and depends on `MMF_VM_HUGEPAGE`. Collapse paths must handle races with page faults, unmaps, and memory pressure.

## Test Signals

THP selftests, khugepaged sysfs toggling, fork/exit enrollment tests, collapse of PTE-mapped THP, and `CONFIG_TRANSPARENT_HUGEPAGE=n` build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/khugepaged.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/klist.h -->
# sources/distributed-fs/ceph-client/include/linux/klist.h

## Purpose

`klist.h` declares a generic list abstraction with per-node reference counting and optional get/put callbacks. It is used where list iteration must remain safe while objects can be removed concurrently, notably driver-core style object lists. The source was read as a complete 67-line file.

## Important APIs, Types, and Functions

Types include `struct klist`, `struct klist_node`, and `struct klist_iter`. Macros are `KLIST_INIT()` and `DEFINE_KLIST()`. APIs include `klist_init()`, `klist_add_tail()`, `klist_add_head()`, `klist_add_behind()`, `klist_add_before()`, `klist_del()`, `klist_remove()`, `klist_node_attached()`, `klist_iter_init()`, `klist_iter_init_node()`, `klist_iter_exit()`, `klist_prev()`, and `klist_next()`.

## Control Flow

Clients initialize a klist with optional callbacks, add nodes, then iterate with `klist_iter`. Iteration pins nodes through `kref` and releases them via iterator exit or movement. Remove paths detach nodes and coordinate final release through refcounts.

## State and Persistence Behavior

`struct klist` owns a spinlock and list head. Each node tracks the owning list through private `n_klist`, list links, and a `kref`. Lifetime depends on callers honoring get/put callback semantics.

## Dependencies and Integration Points

It depends on `spinlock`, `list_head`, and `kref`. It integrates with driver core and any subsystem needing stable iteration over mutable object lists.

## Risks and Edge Cases

Callers must not access `n_klist` directly. Iterator users must call `klist_iter_exit()` to drop references. Callback implementations must avoid deadlocks with list locks and object release paths.

## Test Signals

Concurrent add/remove/iterate stress, iterator leak checks, callback order tests, and driver-core list traversal tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/klist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmemleak.h -->
# sources/distributed-fs/ceph-client/include/linux/kmemleak.h

## Purpose

`kmemleak.h` declares allocation/free annotation hooks for the kernel memory leak detector. It lets allocators, percpu/vmalloc paths, physical-memory users, and special objects register, ignore, scan, or erase tracked pointers. The source was read as a complete 129-line file.

## Important APIs, Types, and Functions

With `CONFIG_DEBUG_KMEMLEAK`, APIs include `kmemleak_init()`, `kmemleak_alloc()`, `kmemleak_alloc_percpu()`, `kmemleak_vmalloc()`, `kmemleak_free()`, `kmemleak_free_part()`, `kmemleak_free_percpu()`, `kmemleak_update_trace()`, `kmemleak_not_leak()`, `kmemleak_transient_leak()`, `kmemleak_ignore()`, `kmemleak_ignore_percpu()`, `kmemleak_scan_area()`, `kmemleak_no_scan()`, `kmemleak_alloc_phys()`, `kmemleak_free_part_phys()`, and `kmemleak_ignore_phys()`. Recursive helpers skip caches marked `SLAB_NOLEAKTRACE`.

## Control Flow

Allocation paths annotate new memory, free paths remove it, and scanner configuration helpers adjust what kmemleak treats as roots or ignored objects. In disabled builds all hooks compile away.

## State and Persistence Behavior

Tracked allocations are kept in kmemleak's in-memory object database. `kmemleak_erase()` clears stored pointers to avoid false retention. No state persists across reboot.

## Dependencies and Integration Points

It integrates with slab, percpu, vmalloc, memblock/physical allocations, and debug scanning.

## Risks and Edge Cases

Missing annotations cause false positives or false negatives. `SLAB_NOLEAKTRACE` must be respected for recursive allocation paths. Partial frees and physical allocations need exact size/address accounting.

## Test Signals

Kmemleak selftests, allocator annotation tests, false-positive regression tests for ignored objects, partial-free tests, and disabled-config build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmemleak.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmod.h -->
# sources/distributed-fs/ceph-client/include/linux/kmod.h

## Purpose

`kmod.h` exposes the kernel module autoload request API. It lets subsystems ask userspace module loading infrastructure to run modprobe synchronously or asynchronously, with compile-time stubs when module support is disabled. The source was read as a complete 32-line file.

## Important APIs, Types, and Functions

Under `CONFIG_MODULES`, `__request_module()` is the printf-style backend. Macros `request_module()`, `request_module_nowait()`, and `try_then_request_module()` select wait behavior and retry an expression after requesting a module. Without module support, request functions return `-ENOSYS` and `try_then_request_module()` leaves the original expression unchanged.

## Control Flow

Callers typically try a lookup, request the module if the lookup fails, and then retry. Synchronous requests wait for modprobe exit; nowait requests just initiate the helper.

## State and Persistence Behavior

This header owns no state. Runtime state is in usermode-helper execution, module loader state, and loaded modules.

## Dependencies and Integration Points

It includes usermode helper, GFP, errno, compiler, workqueue, and sysctl headers. It integrates with subsystem autoload paths such as protocol families, filesystems, and device drivers.

## Risks and Edge Cases

Return status from modprobe is documented as usually not useful. Callers must avoid recursive module requests and must handle `-ENOSYS`. Format strings must not be user-controlled without validation.

## Test Signals

Module autoload tests, `request_module_nowait()` lifetime tests, recursion/rate-limit tests, disabled-module build coverage, and lookup-then-request retry tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan-checks.h -->
# sources/distributed-fs/ceph-client/include/linux/kmsan-checks.h

## Purpose

`kmsan-checks.h` declares one-off KMSAN annotation helpers for poisoning, unpoisoning, checking memory, user copies, and metadata propagation after non-instrumented memory moves. The source was read as a complete 98-line file.

## Important APIs, Types, and Functions

With `CONFIG_KMSAN`, APIs are `kmsan_poison_memory()`, `kmsan_unpoison_memory()`, `kmsan_check_memory()`, `kmsan_copy_to_user()`, and `kmsan_memmove()`. Disabled builds provide empty inline stubs.

## Control Flow

Subsystems call these helpers around memory whose initialization state cannot be inferred by compiler instrumentation. User-copy paths call `kmsan_copy_to_user()` after copy attempts, and assembly or non-instrumented memcpy paths call `kmsan_memmove()` to copy shadow/origin metadata.

## State and Persistence Behavior

KMSAN shadow and origin metadata are updated in memory. There is no durable persistence; metadata tracks runtime initialization state.

## Dependencies and Integration Points

It depends on kernel types and integrates with KMSAN runtime, uaccess, assembly string operations, and subsystem-specific annotation sites.

## Risks and Edge Cases

Incorrect poisoning or unpoisoning can hide real leaks or create false positives. `kmsan_copy_to_user()` must use the actual copied byte count derived from `left`. Non-instrumented copies require metadata propagation or shadow state diverges from data.

## Test Signals

KMSAN selftests, intentional uninitialized-use tests, user-copy leak tests, non-instrumented memcpy metadata tests, and disabled-config build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan-checks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan.h -->
# sources/distributed-fs/ceph-client/include/linux/kmsan.h

## Purpose

`kmsan.h` is the primary subsystem API for Kernel Memory Sanitizer. It declares task, page, slab, vmalloc, ioremap, DMA, USB, entry-regs, metadata, and per-task enable/disable hooks used to maintain initialization shadow/origin state. The source was read as a complete 411-line file.

## Important APIs, Types, and Functions

Key APIs include `kmsan_task_create()`, `kmsan_task_exit()`, `kmsan_init_shadow()`, `kmsan_init_runtime()`, `kmsan_memblock_free_pages()`, `kmsan_alloc_page()`, `kmsan_free_page()`, `kmsan_copy_page_meta()`, `kmsan_slab_alloc()`, `kmsan_slab_free()`, `kmsan_kmalloc_large()`, `kmsan_kfree_large()`, `kmsan_vmap_pages_range_noflush()`, `kmsan_vunmap_range_noflush()`, `kmsan_ioremap_page_range()`, `kmsan_iounmap_page_range()`, `kmsan_handle_dma()`, `kmsan_handle_dma_sg()`, `kmsan_handle_urb()`, `kmsan_unpoison_entry_regs()`, `kmsan_get_metadata()`, `kmsan_enable_current()`, `kmsan_disable_current()`, `memset_no_sanitize_memory()`, and `KMSAN_WARN_ON()`.

## Control Flow

Boot initializes shadow metadata, then allocator and mapping paths notify KMSAN as memory changes ownership. DMA and USB hooks check outgoing buffers and initialize incoming buffers. Entry code unpoisons register frames. Runtime sections can temporarily disable KMSAN for the current task and re-enable it with nested depth accounting.

## State and Persistence Behavior

KMSAN maintains shadow and origin metadata for kernel memory and per-task context. `kmsan_enabled` and `panic_on_kmsan` control runtime behavior. Disabled builds stub hooks and return success.

## Dependencies and Integration Points

It integrates with page allocator, slab, vmalloc/ioremap, DMA API, scatterlists, USB URBs, low-level entry, and LLVM/MSan instrumentation.

## Risks and Edge Cases

Must-check return values on metadata mapping paths are important; missed failures break sanitizer correctness. DMA direction handling must match hardware ownership. Nested `kmsan_disable_current()`/`kmsan_enable_current()` pairs must balance. `KMSAN_WARN_ON()` may disable KMSAN or BUG based on policy.

## Test Signals

KMSAN boot and runtime selftests, allocator poisoning tests, DMA direction tests, USB transfer tests, vmalloc/ioremap metadata mapping tests, balanced disable/enable tests, and disabled-config builds are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan_string.h -->
# sources/distributed-fs/ceph-client/include/linux/kmsan_string.h

## Purpose

`kmsan_string.h` centralizes prototypes for KMSAN-provided string/memory routines. It exists so headers that need the MSan function names do not duplicate declarations. The source was read as a complete 21-line file.

## Important APIs, Types, and Functions

The header declares `__msan_memcpy()`, `__msan_memset()`, and `__msan_memmove()`.

## Control Flow

There is no local flow. Instrumented or overridden string operations call into these routines to update both data and KMSAN metadata consistently.

## State and Persistence Behavior

No state is owned here. The declared routines affect KMSAN shadow/origin metadata at runtime.

## Dependencies and Integration Points

It integrates with KMSAN instrumentation and generic string operation declarations. Consumers include headers or C files that must refer to MSan-backed copy/fill/move functions.

## Risks and Edge Cases

Prototype drift from the actual KMSAN runtime implementation would cause build or ABI mismatches. Callers must pass correct byte lengths because metadata propagation follows the requested size.

## Test Signals

KMSAN string operation tests, build coverage for headers that include this file, and metadata propagation checks for memcpy/memset/memmove are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan_types.h -->
# sources/distributed-fs/ceph-client/include/linux/kmsan_types.h

## Purpose

`kmsan_types.h` defines the minimal KMSAN context types embedded in existing kernel structs. It mirrors TLS sizing expected by LLVM MemorySanitizer instrumentation. The source was read as a complete 37-line file.

## Important APIs, Types, and Functions

It defines temporary constants `KMSAN_RETVAL_SIZE` and `KMSAN_PARAM_SIZE`, `struct kmsan_context_state` containing parameter, return value, vararg, origin, and overflow TLS areas, and `struct kmsan_ctx` with context state, runtime recursion flag, and depth.

## Control Flow

There is no control flow. The compiler instrumentation and KMSAN runtime read and write these fields when tracking function parameters, return values, varargs, and origins.

## State and Persistence Behavior

The state is per-context, commonly per-task, and persists only for the lifetime of the owning task/context. The constants are undefined after struct definition to avoid leaking local sizing macros.

## Dependencies and Integration Points

It depends on fixed-width kernel types and integrates with LLVM MSan instrumentation, task state, and KMSAN runtime entry/exit logic.

## Risks and Edge Cases

The TLS sizes must match compiler pass expectations. Struct layout drift can corrupt sanitizer state. `kmsan_in_runtime` and `depth` must prevent recursive instrumentation while still restoring state on exit.

## Test Signals

KMSAN build tests with instrumentation, context switch tests, vararg metadata tests, nested runtime recursion tests, and compiler/runtime layout compatibility checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsan_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsg_dump.h -->
# sources/distributed-fs/ceph-client/include/linux/kmsg_dump.h

## Purpose

`kmsg_dump.h` declares the printk crash/emergency message dumper interface. It allows dumpers to register callbacks and retrieve kernel log records during panic, oops, shutdown, or other dump reasons. The source was read as a complete 126-line file.

## Important APIs, Types, and Functions

Types include `enum kmsg_dump_reason`, `struct kmsg_dump_iter`, `struct kmsg_dump_detail`, and `struct kmsg_dumper`. APIs under `CONFIG_PRINTK` include `kmsg_dump_desc()`, `kmsg_dump_get_line()`, `kmsg_dump_get_buffer()`, `kmsg_dump_rewind()`, `kmsg_dump_register()`, `kmsg_dump_unregister()`, `kmsg_dump_reason_str()`, and inline `kmsg_dump()`.

## Control Flow

Crash or shutdown paths call `kmsg_dump_desc()`, which dispatches registered dumpers. A dumper's callback uses an iterator to retrieve lines or buffers from the printk ring and may rewind as needed.

## State and Persistence Behavior

Registered dumpers live on a global list and persist until unregistered. Iterators carry sequence positions for a single dump operation. The header owns no storage.

## Dependencies and Integration Points

It integrates with printk, panic/oops handling, pstore, crash dump backends, and any platform dumper that saves logs.

## Risks and Edge Cases

Dump callbacks may run in distressed contexts and must avoid blocking or allocation assumptions. `max_reason` filters lower-priority events. Without `CONFIG_PRINTK`, registration fails with `-EINVAL` and reads return false.

## Test Signals

Pstore/kmsg dump tests, panic/oops dump path tests, iterator rewind tests, unregister tests, reason filtering tests, and `CONFIG_PRINTK=n` build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kmsg_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobj_map.h -->
# sources/distributed-fs/ceph-client/include/linux/kobj_map.h

## Purpose

`kobj_map.h` declares the device-number-to-kobject mapping API used by character and block device lookup code. It lets subsystems register probe ranges and resolve `dev_t` values to kobjects. The source was read as a complete 20-line file.

## Important APIs, Types, and Functions

The header defines `kobj_probe_t`, opaque `struct kobj_map`, and APIs `kobj_map()`, `kobj_unmap()`, `kobj_lookup()`, and `kobj_map_init()`.

## Control Flow

Subsystems initialize a map, register a range with a module pointer, probe callback, optional lock callback, and private data, then lookup paths call `kobj_lookup()` with a device number and receive a kobject plus partition/index information through the integer pointer.

## State and Persistence Behavior

Map state lives in an allocated `struct kobj_map` implementation. Registered ranges persist until explicitly unmapped. The module pointer participates in owner lifetime management in the implementation.

## Dependencies and Integration Points

It depends on mutex declarations, kobjects, device numbers, and modules. It integrates with block/char device open paths and sysfs object lookup.

## Risks and Edge Cases

Overlapping ranges and stale module/private pointers are primary risks. Probe callbacks must be safe under lookup locking and handle missing devices. Unmap must exactly match registered ranges.

## Test Signals

Device lookup tests, register/unregister range tests, overlapping range handling, module unload races, and invalid `dev_t` lookup tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobj_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobject.h -->
# sources/distributed-fs/ceph-client/include/linux/kobject.h

## Purpose

`kobject.h` defines the generic kernel object infrastructure used by sysfs, ksets, uevents, and reference-counted kernel object lifetime management. The source was read as a complete 222-line file.

## Important APIs, Types, and Functions

Core types include `struct kobject`, `struct kobj_type`, `struct kobj_uevent_env`, `struct kset_uevent_ops`, `struct kobj_attribute`, and `struct kset`. APIs include `kobject_set_name()`, `kobject_init()`, `kobject_add()`, `kobject_init_and_add()`, `kobject_del()`, `kobject_create_and_add()`, `kobject_rename()`, `kobject_move()`, `kobject_get()`, `kobject_get_unless_zero()`, `kobject_put()`, `kobject_namespace()`, `kobject_get_ownership()`, `kobject_get_path()`, `kset_init()`, `kset_register()`, `kset_unregister()`, `kset_create_and_add()`, `kset_find_obj()`, `kobject_uevent()`, `kobject_uevent_env()`, `kobject_synth_uevent()`, and `add_uevent_var()`.

## Control Flow

Objects are initialized with a type, named, added under a parent or kset, exposed in sysfs, and refcounted with `kobject_get()`/`kobject_put()`. Uevents are emitted for lifecycle changes. Release is delegated to the type's `release()` callback when the final reference drops.

## State and Persistence Behavior

`struct kobject` stores name, parent, kset, type, sysfs `kernfs_node`, refcount, and lifecycle flags. Ksets hold a list of member objects plus their own embedded kobject. State persists in memory and sysfs until deletion and reference release complete.

## Dependencies and Integration Points

It integrates with sysfs/kernfs, krefs, namespaces, wait/workqueue debug release, uevent helper/netlink handling, UID/GID ownership, and global `/sys/kernel`, `/sys/kernel/mm`, `/sys/hypervisor`, `/sys/power`, and `/sys/firmware` roots.

## Risks and Edge Cases

Kobject lifetime bugs are high risk: every type needs a valid release callback, and objects must not be freed before final `kobject_put()`. Uevent action strings are constrained by driver-core policy. Namespace and ownership callbacks must match sysfs expectations.

## Test Signals

Driver-core tests, sysfs add/remove/rename/move tests, kobject refcount leak/UAF tests, uevent environment tests, namespace sysfs tests, and `CONFIG_DEBUG_KOBJECT_RELEASE` coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobject_api.h -->
# sources/distributed-fs/ceph-client/include/linux/kobject_api.h

## Purpose

`kobject_api.h` is a one-line compatibility/include-forwarding header for the kobject API. It simply includes `linux/kobject.h`. The source was read as a complete 1-line file.

## Important APIs, Types, and Functions

It directly exposes all declarations from `kobject.h`; no independent APIs or types are defined here.

## Control Flow

There is no local flow. Include processing forwards consumers to the main kobject header.

## State and Persistence Behavior

No state is owned by this file. Runtime behavior is entirely that of `kobject.h`.

## Dependencies and Integration Points

Its sole dependency and integration point is `linux/kobject.h`. It likely exists for include path compatibility with code expecting a `_api` wrapper.

## Risks and Edge Cases

The only meaningful risk is include-cycle or compatibility breakage if this forwarding header is removed or stops including `kobject.h`.

## Test Signals

Compile coverage for code including `linux/kobject_api.h` and include-order tests are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobject_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobject_ns.h -->
# sources/distributed-fs/ceph-client/include/linux/kobject_ns.h

## Purpose

`kobject_ns.h` defines namespace operations used by kobjects and sysfs entries. It lets sysfs determine namespace type, current namespace ownership, netlink namespace, initial namespace, and reference dropping behavior. The source was read as a complete 58-line file.

## Important APIs, Types, and Functions

Types include `enum kobj_ns_type` with `KOBJ_NS_TYPE_NONE` and `KOBJ_NS_TYPE_NET`, and `struct kobj_ns_type_operations`. APIs include `kobj_ns_type_register()`, `kobj_ns_type_registered()`, `kobj_child_ns_ops()`, `kobj_ns_ops()`, `kobj_ns_current_may_mount()`, `kobj_ns_grab_current()`, and `kobj_ns_drop()`.

## Control Flow

Namespace providers register operations. Kobject/sysfs paths ask parent or object types for namespace operations, check whether current context may mount, grab the current namespace reference, and drop it after use.

## State and Persistence Behavior

Registered namespace operation tables persist for the kernel lifetime. Individual namespace references are acquired and dropped through callbacks.

## Dependencies and Integration Points

It integrates with sysfs, kobjects, network namespaces, sockets/netlink, and `struct ns_common` reference handling.

## Risks and Edge Cases

Callbacks must maintain namespace reference counts exactly. Unsupported namespace types must be rejected. Mount permission logic affects visibility and isolation of sysfs entries.

## Test Signals

Network namespace sysfs visibility tests, namespace registration tests, reference leak tests, mount permission checks, and include-order coverage with `kobject.h` are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kobject_ns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kprobes.h -->
# sources/distributed-fs/ceph-client/include/linux/kprobes.h

## Purpose

`kprobes.h` defines the generic kernel dynamic instrumentation interface for kprobes, kretprobes, optimized probes, ftrace-backed probes, instruction slots, blacklists, and page-fault handling. The source was read as a complete 594-line file.

## Important APIs, Types, and Functions

Core types include `struct kprobe`, `struct kretprobe`, `struct kretprobe_instance`, `struct kprobe_blacklist_entry`, `struct kprobe_insn_cache`, and `struct optimized_kprobe`. Important APIs include `register_kprobe()`, `unregister_kprobe()`, `register_kprobes()`, `register_kretprobe()`, `disable_kprobe()`, `enable_kprobe()`, `get_kprobe()`, `kprobe_running()`, `kprobe_lookup_name()`, `arch_adjust_kprobe_addr()`, `within_kprobe_blacklist()`, `kprobe_add_ksym_blacklist()`, `kprobe_add_area_blacklist()`, `kprobe_ftrace_handler()`, `kprobe_ftrace_kill()`, `kretprobe_trampoline_handler()`, `kretprobe_find_ret_addr()`, and `kprobe_page_fault()`.

## Control Flow

A registered kprobe replaces or routes execution at an address through architecture breakpoint/ftrace machinery, invokes pre/post handlers, and tracks per-CPU current probe state. Kretprobes install return trampolines or rethooks and call handlers on function return. Optimized probes may replace breakpoints with direct jumps after safety checks. Fault handling only claims kernel-mode, non-preemptible faults while a kprobe is running.

## State and Persistence Behavior

Registered probes persist in global hash/list structures until unregistered. Per-CPU `current_kprobe` and `kprobe_ctlblk` track active execution. Instruction slot caches allocate executable pages. Kretprobe instances come from pools and carry per-instance data.

## Dependencies and Integration Points

It depends on architecture kprobe support, notifier paths, percpu data, ftrace, objpool, rethook, RCU, mutexes, and exception/page-fault handling. KGDB shares blacklist concepts with kprobes.

## Risks and Edge Cases

Instrumentation can recurse, hit blacklisted text, race with module unload, or fault in probe handlers. Disabled configs return `-EOPNOTSUPP` and treat blacklist as closed. Optimized/ftrace paths must be killed safely when ftrace is disabled.

## Test Signals

Kprobes selftests, kretprobe maxactive/nmissed tests, optimized probe tests, ftrace-backed probe tests, blacklist rejection tests, module unload tests, fault-in-handler tests, and disabled-config build coverage are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kref.h -->
# sources/distributed-fs/ceph-client/include/linux/kref.h

## Purpose

`kref.h` provides a small generic wrapper around `refcount_t` for reference-counted object lifetime management. It standardizes initialization, increment, decrement-with-release, and get-unless-zero behavior. The source was read as a complete 135-line file.

## Important APIs, Types, and Functions

The header defines `struct kref`, `KREF_INIT()`, `kref_init()`, `kref_read()`, `kref_get()`, `kref_put()`, `kref_put_mutex()`, `kref_put_lock()`, and `kref_get_unless_zero()`.

## Control Flow

Objects embed `struct kref`, initialize it to one, increment before sharing, and call `kref_put()` when a reference is dropped. The final put calls the supplied release callback. Mutex and spinlock variants acquire the lock only when the final reference is dropped and require the release function to release that lock.

## State and Persistence Behavior

The only stored state is the embedded `refcount_t`. Object lifetime persists until the final release callback runs.

## Dependencies and Integration Points

It depends on `refcount_t` and spinlock/mutex helpers. It is used by kobjects, klists, device model objects, and many kernel subsystems.

## Risks and Edge Cases

The release function must not be NULL or plain `kfree()` and must match the containing object. Return value from `kref_put()` only proves this caller released the object when it returns true. `kref_get_unless_zero()` callers must check its return value.

## Test Signals

Reference-count unit tests, final-release callback tests, lock-held release tests, get-unless-zero race tests, and refcount saturation/underflow diagnostics are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kref_api.h -->
# sources/distributed-fs/ceph-client/include/linux/kref_api.h

## Purpose

`kref_api.h` is a one-line compatibility/include-forwarding header for the kref API. It simply includes `linux/kref.h`. The source was read as a complete 1-line file.

## Important APIs, Types, and Functions

It defines no independent symbols; it re-exports `struct kref` and helpers from `kref.h`.

## Control Flow

There is no local control flow. Compilation continues through the main kref header.

## State and Persistence Behavior

No state is owned by this file.

## Dependencies and Integration Points

The sole dependency is `linux/kref.h`. The integration role is source compatibility for code including `linux/kref_api.h`.

## Risks and Edge Cases

Removing or changing the forwarding include can break external or generated include users even though no runtime behavior is present.

## Test Signals

Compile coverage for include users and include-order tests are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kref_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ks0108.h -->
# sources/distributed-fs/ceph-client/include/linux/ks0108.h

## Purpose

`ks0108.h` declares the low-level API for a KS0108 LCD controller driver. It exposes byte writes and simple display position/state controls for consumers of the LCD controller module. The source was read as a complete 35-line file.

## Important APIs, Types, and Functions

APIs are `ks0108_writedata()`, `ks0108_writecontrol()`, `ks0108_displaystate()`, `ks0108_startline()`, `ks0108_address()`, `ks0108_page()`, and `ks0108_isinited()`.

## Control Flow

Client display code checks initialization, selects page/address/start line or display state, writes control bytes, and writes display data bytes through the controller driver.

## State and Persistence Behavior

Controller state is hardware-visible: display enabled state, start line, current address, and page persist in the controller until changed or reset. The header owns no state.

## Dependencies and Integration Points

It integrates with the KS0108 driver implementation and any framebuffer or auxiliary display code using the controller.

## Risks and Edge Cases

Documented ranges are narrow: display state 0..1, startline/address 0..63, page 0..7. Callers must avoid writes before initialization and must obey hardware timing/ordering handled by the implementation.

## Test Signals

Driver compile tests, initialization checks, boundary value tests for address/page/startline, and hardware or emulator display smoke tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ks0108.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ks8842.h -->
# sources/distributed-fs/ceph-client/include/linux/ks8842.h

## Purpose

`ks8842.h` defines platform data for the KS8842 network driver. The source was read as a complete 26-line file.

## Important APIs, Types, and Functions

It defines `struct ks8842_platform_data` with `macaddr[ETH_ALEN]`, `rx_dma_channel`, and `tx_dma_channel`.

## Control Flow

There is no executable flow. Board/platform setup supplies this structure to the KS8842 driver, which uses it during probe to select MAC address and optional DMA channels.

## State and Persistence Behavior

The platform data persists as device configuration for the lifetime of the platform device. It does not change runtime packet state.

## Dependencies and Integration Points

It depends on Ethernet address sizing from `linux/if_ether.h` and integrates with platform-device registration and the KS8842 Ethernet driver.

## Risks and Edge Cases

All-zero MAC address means use the chip MAC. DMA channel `-1` disables DMA, so probe code must distinguish absent channels from valid channel zero. Invalid MACs or channel IDs can break networking or DMA setup.

## Test Signals

Driver probe tests with explicit and chip MAC addresses, DMA/no-DMA configuration tests, platform data validation, and network transmit/receive smoke tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ks8842.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ks8851_mll.h -->
# sources/distributed-fs/ceph-client/include/linux/ks8851_mll.h

## Purpose

`ks8851_mll.h` defines platform data for the KS8851 MLL network driver. The source was read as a complete 21-line file.

## Important APIs, Types, and Functions

It defines `struct ks8851_mll_platform_data` with `mac_addr[ETH_ALEN]`.

## Control Flow

There is no local flow. Platform setup passes the structure to the KS8851 MLL driver, which uses the supplied MAC address or falls back to the chip address when all zeros are supplied.

## State and Persistence Behavior

The platform data is static device configuration for probe and driver lifetime. Runtime network state is owned by the driver.

## Dependencies and Integration Points

It depends on `linux/if_ether.h` and integrates with platform-device registration and the KS8851 MLL Ethernet driver.

## Risks and Edge Cases

Invalid or duplicate MAC addresses can cause network issues. The all-zero fallback convention must match driver behavior.

## Test Signals

Probe tests with configured and default MAC, MAC validation checks, and network link/transmit/receive smoke tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ks8851_mll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ksm.h -->
# sources/distributed-fs/ceph-client/include/linux/ksm.h

## Purpose

`ksm.h` declares Kernel Samepage Merging interfaces for marking VMAs/MMs mergeable, handling fork/exec/exit, tracking KSM zero pages, copying swapped KSM pages, reverse mapping, migration, and process profitability. The source was read as a complete 164-line file.

## Important APIs, Types, and Functions

With `CONFIG_KSM`, APIs include `ksm_madvise()`, `ksm_vma_flags()`, `ksm_enable_merge_any()`, `ksm_disable_merge_any()`, `ksm_disable()`, `__ksm_enter()`, `__ksm_exit()`, `ksm_map_zero_page()`, `ksm_might_unmap_zero_page()`, `mm_ksm_zero_pages()`, `ksm_fork()`, `ksm_execve()`, `ksm_exit()`, `ksm_might_need_to_copy()`, `rmap_walk_ksm()`, `folio_migrate_ksm()`, `collect_procs_ksm()`, `ksm_process_profit()`, and `ksm_process_mergeable()`.

## Control Flow

`madvise()` and merge-any paths set mm/VMA mergeability, mm lifecycle hooks enroll or remove address spaces, ksmd scans and merges identical anonymous pages, and fault/swap paths call `ksm_might_need_to_copy()` when a former KSM page may need private ownership.

## State and Persistence Behavior

KSM state is in mm flags, counters such as `ksm_zero_pages`, per-mm KSM fields, rmap items, and merged folios. State persists while address spaces and merged pages exist.

## Dependencies and Integration Points

It integrates with MM, pagemap, rmap, scheduler/mm lifecycle, folio migration, zero page accounting, and `madvise()`.

## Risks and Edge Cases

KSM zero page tracking reuses PTE dirty bit semantics. Fork enrollment is best effort. Swap-in of former KSM pages can require copying because anon_vma context may no longer match. Disabled builds stub most behavior.

## Test Signals

KSM selftests, madvise merge/unmerge tests, fork/exec/exit tests, zero-page accounting tests, swap-in copy tests, folio migration tests, and disabled-config build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ksm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kstack_erase.h -->
# sources/distributed-fs/ceph-client/include/linux/kstack_erase.h

## Purpose

`kstack_erase.h` declares stack erasure helpers for clearing unused kernel stack contents and tracking stack depth. It is part of the stackleak hardening path. The source was read as a complete 89-line file.

## Important APIs, Types, and Functions

Constants are `KSTACK_ERASE_POISON` and `KSTACK_ERASE_SEARCH_DEPTH`. Under `CONFIG_KSTACK_ERASE`, helpers include `stackleak_task_low_bound()`, `stackleak_task_high_bound()`, `stackleak_find_top_of_poison()`, `stackleak_task_init()`, `stackleak_erase()`, `stackleak_erase_on_task_stack()`, `stackleak_erase_off_task_stack()`, and `__sanitizer_cov_stack_depth()`.

## Control Flow

Task creation initializes the lowest erasable stack pointer. Instrumentation updates stack depth. On syscall/exit-style paths, erase functions find the region above recently used stack and overwrite unused stack memory while preserving `STACK_END_MAGIC` and top-of-stack `pt_regs`.

## State and Persistence Behavior

Per-task `lowest_stack` and optional metrics persist in `task_struct`. Stack poison values persist only until overwritten by later stack usage or erasure.

## Dependencies and Integration Points

It depends on task stack helpers, architecture stacktrace support, linkage/noinstr annotations, and sanitizer coverage instrumentation.

## Risks and Edge Cases

The poison value must point into an unused virtual hole for the platform. Bounds must avoid corrupting stack canaries, `STACK_END_MAGIC`, or `pt_regs`. The poison search depth trades performance against stale stack retention.

## Test Signals

Stackleak selftests, boot tests with hardening enabled, syscall stack erasure checks, metrics validation, architecture stack-bound tests, and disabled-config build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kstack_erase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kstrtox.h -->
# sources/distributed-fs/ceph-client/include/linux/kstrtox.h

## Purpose

`kstrtox.h` declares safe string-to-number conversion helpers for kernel strings and userspace buffers, plus legacy `simple_strto*` functions that should be avoided when strict parsing/range checking is needed. The source was read as a complete 151-line file.

## Important APIs, Types, and Functions

Primary APIs include `_kstrtoul()`, `_kstrtol()`, `kstrtoull()`, `kstrtoll()`, `kstrtoul()`, `kstrtol()`, `kstrtouint()`, `kstrtoint()`, typed wrappers for u64/s64/u32/s32/u16/s16/u8/s8, `kstrtobool()`, and corresponding `_from_user()` helpers. Legacy APIs are `simple_strtoul()`, `simple_strntoul()`, `simple_strtol()`, `simple_strtoull()`, and `simple_strtoll()`.

## Control Flow

Callers pass a NUL-terminated kernel string or counted userspace buffer and base. Base zero auto-detects decimal/octal/hex. Inline long wrappers dispatch to long-long implementations when sizes/alignments match, otherwise use internal long-specific helpers.

## State and Persistence Behavior

No state is stored. Successful conversions write to caller-provided result storage and return zero; errors report parse failure or range overflow.

## Dependencies and Integration Points

It depends on compiler attributes, fixed-width types, and uaccess in implementations. It is widely used by sysfs/procfs/module parameter parsing and kernel text configuration.

## Risks and Edge Cases

Return codes are must-check. Accepted syntax allows a single trailing newline. Base is limited to 16. Legacy simple converters do not check overflow and stop at the first non-digit, so they can silently accept malformed input.

## Test Signals

Conversion unit tests for each width/sign, overflow/underflow tests, invalid character tests, newline handling, base autodetection, `_from_user()` fault tests, and must-check warning coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kstrtox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ksysfs.h -->
# sources/distributed-fs/ceph-client/include/linux/ksysfs.h

## Purpose

`ksysfs.h` declares initialization for the kernel sysfs root support. The source was read as a complete 8-line file.

## Important APIs, Types, and Functions

The only API is `ksysfs_init()`.

## Control Flow

Boot/init code calls `ksysfs_init()` to create or populate kernel sysfs structures. The implementation supplies the actual setup sequence.

## State and Persistence Behavior

State is sysfs/kobject state established by the implementation and persists until kernel shutdown. The header owns none.

## Dependencies and Integration Points

It integrates with sysfs, kobjects, and `/sys/kernel` initialization.

## Risks and Edge Cases

The main risk is boot ordering: sysfs and kobject roots must be ready when this initializer runs, and consumers must not assume entries before initialization completes.

## Test Signals

Boot tests, `/sys/kernel` presence checks, initcall ordering coverage, and sysfs registration failure-path tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ksysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kthread.h -->
# sources/distributed-fs/ceph-client/include/linux/kthread.h

## Purpose

`kthread.h` declares the kernel thread creation, binding, stopping, parking, freezer, worker, delayed-work, mm borrowing, and block-cgroup association APIs. The source was read as a complete 293-line file.

## Important APIs, Types, and Functions

Important APIs include `tsk_is_kthread()`, `kthread_create_on_node()`, `kthread_create()`, `kthread_create_on_cpu()`, `kthread_run()`, `kthread_run_on_cpu()`, `kthread_bind()`, `kthread_stop()`, `kthread_stop_put()`, `kthread_should_stop()`, `kthread_should_park()`, `kthread_freezable_should_stop()`, `kthread_park()`, `kthread_unpark()`, `kthread_parkme()`, `kthread_complete_and_exit()`, `kthread_worker_fn()`, `kthread_create_worker_on_node()`, `kthread_run_worker()`, `kthread_queue_work()`, `kthread_queue_delayed_work()`, `kthread_mod_delayed_work()`, `kthread_flush_work()`, `kthread_cancel_work_sync()`, `kthread_destroy_worker()`, `kthread_use_mm()`, and `kthread_unuse_mm()`. Types include opaque `struct kthread`, `struct kthread_worker`, `struct kthread_work`, and `struct kthread_delayed_work`.

## Control Flow

Creation helpers allocate a stopped task, set kthread-private state, optionally bind it, and callers wake it. Thread functions loop until stop/park/freezer helpers indicate state changes. Worker APIs queue work under raw spinlock and a kthread executes each work function; delayed work uses timers.

## State and Persistence Behavior

Kthread state is attached to `task_struct->worker_private` when `PF_KTHREAD` is set. Worker state includes work lists, delayed list, current work, and task pointer. State persists until stopped/destroyed.

## Dependencies and Integration Points

It integrates with scheduler tasks, NUMA/CPU affinity, completions, timers, raw spinlocks, freezer, housekeeping CPUs, mm borrowing, and blk-cgroup association.

## Risks and Edge Cases

Created threads are stopped until woken. Stop/park protocols require cooperative checks by the thread. Delayed work cancellation races must use sync helpers. Borrowed mm and blkcg association must be undone appropriately. CPU-bound name format is restricted.

## Test Signals

Kthread lifecycle tests, stop/park/freezer tests, CPU binding tests, worker queue/flush/cancel tests, delayed work timer tests, mm borrow tests, blkcg association tests, and module unload races are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kthread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ktime.h -->
# sources/distributed-fs/ceph-client/include/linux/ktime.h

## Purpose

`ktime.h` defines nanosecond-resolution `ktime_t` helpers for construction, arithmetic, comparison, conversion to/from timespec and scalar units, safe addition, and division. The source was read as a complete 237-line file.

## Important APIs, Types, and Functions

Helpers include `ktime_set()`, `ktime_sub()`, `ktime_add()`, `ktime_add_unsafe()`, `ktime_add_ns()`, `ktime_sub_ns()`, `timespec64_to_ktime()`, `ktime_to_timespec64()`, `ktime_to_ns()`, `ktime_compare()`, `ktime_after()`, `ktime_before()`, `ktime_divns()`, `ktime_to_us()`, `ktime_to_ms()`, `ktime_us_delta()`, `ktime_ms_delta()`, `ktime_add_us()`, `ktime_add_ms()`, `ktime_sub_us()`, `ktime_sub_ms()`, `ktime_add_safe()`, `ktime_to_timespec64_cond()`, `ns_to_ktime()`, `us_to_ktime()`, and `ms_to_ktime()`.

## Control Flow

Callers construct nanosecond values, perform arithmetic, compare timestamps, divide into units, or convert to/from `timespec64`. On 32-bit systems, `ktime_divns()` optimizes constant 32-bit divisors and otherwise calls `__ktime_divns()`.

## State and Persistence Behavior

No state is stored. `ktime_t` values are scalar nanoseconds. `ktime_set()` saturates large seconds to `KTIME_MAX`.

## Dependencies and Integration Points

It depends on time constants, jiffies/time headers, bug/warn helpers, `vdso/ktime.h`, and timekeeping. It is used by timers, schedulers, drivers, tracing, and timeout code.

## Risks and Edge Cases

`ktime_add()` can overflow; use `ktime_add_safe()` where overflow matters. `ktime_add_unsafe()` deliberately avoids undefined behavior but leaves overflow checking to callers. Negative divisors warn or BUG. Multiplying usec/msec can overflow for huge inputs.

## Test Signals

Time conversion unit tests, overflow/saturation tests, 32-bit division tests, negative divisor checks, comparison/delta tests, and compile coverage across 32/64-bit architectures are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ktime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ktime_api.h -->
# sources/distributed-fs/ceph-client/include/linux/ktime_api.h

## Purpose

`ktime_api.h` is a one-line compatibility/include-forwarding header for ktime helpers. It simply includes `linux/ktime.h`. The source was read as a complete 1-line file.

## Important APIs, Types, and Functions

It defines no independent symbols and re-exports the `ktime.h` API.

## Control Flow

There is no local control flow. Include processing forwards consumers to `linux/ktime.h`.

## State and Persistence Behavior

No state is owned here.

## Dependencies and Integration Points

The sole dependency is `linux/ktime.h`. It exists as an include compatibility layer.

## Risks and Edge Cases

The practical risk is source compatibility breakage if the forwarding include changes or disappears.

## Test Signals

Compile coverage for consumers including `linux/ktime_api.h` and include-order tests are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ktime_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kvm_dirty_ring.h -->
# sources/distributed-fs/ceph-client/include/linux/kvm_dirty_ring.h

## Purpose

`kvm_dirty_ring.h` declares KVM's per-VM or per-vCPU dirty page ring interface. It supports dirty logging through a compact ring of `struct kvm_dirty_gfn` entries, with bitmap fallback stubs when the architecture does not support dirty rings. The source was read as a complete 94-line file.

## Important APIs, Types, and Functions

`struct kvm_dirty_ring` stores `dirty_index`, `reset_index`, ring `size`, `soft_limit`, pointer to `dirty_gfns`, and ring `index`. APIs include `kvm_cpu_dirty_log_size()`, `kvm_use_dirty_bitmap()`, `kvm_arch_allow_write_without_running_vcpu()`, `kvm_dirty_ring_get_rsvd_entries()`, `kvm_dirty_ring_alloc()`, `kvm_dirty_ring_reset()`, `kvm_dirty_ring_push()`, `kvm_dirty_ring_check_request()`, `kvm_dirty_ring_get_page()`, and `kvm_dirty_ring_free()`, with no-op or fallback stubs under `!CONFIG_HAVE_KVM_DIRTY_RING`.

## Control Flow

KVM allocates a ring, pushes dirty GFNs as guest pages become dirty, exits to userspace when the soft limit is reached, and userspace harvests entries. Reset paths re-enable dirty trapping for consumed entries and advance `reset_index`.

## State and Persistence Behavior

Ring indices are free-running counters and the `dirty_gfns` buffer persists while the VM/vCPU dirty ring is allocated. Dirty information is transient migration/logging state, not durable storage.

## Dependencies and Integration Points

It depends on `linux/kvm.h`, KVM VM/vCPU structs, architecture dirty-ring support, vm_operations page lookup, and dirty logging/migration userspace ABI.

## Risks and Edge Cases

Reserved entries and soft limits must prevent producer overrun. Unsupported architectures must fall back to dirty bitmaps. Reset must match userspace harvest order to avoid losing dirty information or re-enabling writes too early.

## Test Signals

KVM dirty-ring selftests, live migration dirty logging tests, ring full/soft-limit tests, reset/retrap tests, mmap page lookup tests, and dirty-bitmap fallback builds are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/kvm_dirty_ring.h -->
