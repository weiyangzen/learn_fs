# subset-b-005858 research

Grouped research for Linux header files under `sources/distributed-fs/ceph-client/include/linux`. Each file section is bounded by reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsnotify_backend.h -->
# sources/distributed-fs/ceph-client/include/linux/fsnotify_backend.h

Purpose: Defines the internal backend contract for Linux filesystem notifications. It centralizes event masks, group priorities, event payload typing, mark storage, and public helpers used by VFS hooks and notification backends such as inotify, dnotify, and fanotify.

Important APIs/types/functions: Event masks include `FS_ACCESS`, `FS_MODIFY`, directory entry events, mount namespace events, permission events, `FS_ERROR`, `FS_Q_OVERFLOW`, and reporting flags such as `FS_EVENT_ON_CHILD` and `FS_ISDIR`. Core types are `fsnotify_ops`, `fsnotify_group`, `fsnotify_event`, `fsnotify_mark`, `fsnotify_mark_connector`, `fsnotify_sb_info`, `fsnotify_iter_info`, `fs_error_report`, `file_range`, and `fsnotify_mnt`. The exported surface includes `fsnotify()`, `__fsnotify_parent()`, deletion/free hooks, group lifecycle helpers, event queue helpers, mark add/find/destroy helpers, and `fsnotify_pre_content()`.

Control flow: VFS call sites pass typed event data into `fsnotify()`. The core resolves inode/dentry/path/superblock/mount data using inline accessors, walks matching marks via `fsnotify_iter_info`, applies mark and ignore masks, and dispatches to `fsnotify_ops`. Backend groups queue userspace events through `fsnotify_insert_event()` or implement direct inode handling.

State and persistence behavior: State is in memory: groups hold notification queues, wait queues, fasync state, max queue length, shutdown state, backend-private data, and all marks. Marks are refcounted, protected by group mutexes, mark locks, connector locks, and SRCU-delayed destruction. Superblocks lazily hold watched-object counters by priority.

Dependencies and integration points: Depends on VFS objects, dentries, paths, mount namespaces, refcounts, IDR, mempools, memcg, user namespaces, and nofs allocation scope. Integrates with inode eviction, superblock teardown, mount teardown, dcache parent watched flags, fanotify permission flows, and inotify ID allocation.

Risks: Mask bit overloading (`FS_IN_IGNORED` versus `FS_ERROR`) is backend-specific. Incorrect locking can deadlock reclaim or race mark teardown. Ignore masks have legacy semantics that differ from canonical flag-aware masks. Queue overflow handling depends on a valid group overflow event. Stubbed `!CONFIG_FSNOTIFY` paths silently return success/zero.

Test signals: Exercise inotify/fanotify create, delete, rename, mount, unmount, overflow, child-watch, and permission events; verify dentry parent watched flag updates; run lockdep and KCSAN around mark add/remove; test fanotify pre-content/content permission behavior; build both `CONFIG_FSNOTIFY=y` and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsnotify_backend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsverity.h -->
# sources/distributed-fs/ceph-client/include/linux/fsverity.h

Purpose: Declares the interface between filesystems and the fs-verity support layer for read-only file authenticity verification using Merkle trees and file descriptors/descriptors.

Important APIs/types/functions: `FS_VERITY_MAX_DIGEST_SIZE` and `FS_VERITY_MAX_DESCRIPTOR_SIZE` bound digest and descriptor storage. `fsverity_operations` supplies filesystem callbacks: `begin_enable_verity`, `end_enable_verity`, `get_verity_descriptor`, `read_merkle_tree_page`, optional `readahead_merkle_tree`, and `write_merkle_tree_block`. Public helpers include `fsverity_active()`, `fsverity_get_info()`, ioctls for enable/measure/read-metadata, `fsverity_get_digest()`, `fsverity_file_open()`, read verification helpers, and generic Merkle-tree page helpers.

Control flow: Enabling verity begins with filesystem preparation under `i_rwsem`, writes Merkle blocks through the filesystem, and finishes by storing the descriptor and setting `S_VERITY`. Opening a verity inode calls `__fsverity_file_open()` to initialize verification state and reject writes. Reads call block/folio/bio verification helpers and may trigger Merkle readahead.

State and persistence behavior: Persistent state is filesystem-owned descriptor and Merkle tree storage plus an on-disk verity indicator. Runtime state is `fsverity_info`, fetched only after `S_VERITY` is visible; `fsverity_active()` pairs with flag-setting memory barriers.

Dependencies and integration points: Depends on VFS inode/file APIs, folios, bios, crypto hash metadata, UAPI fsverity structs, and SHA-512 sizing. Filesystems integrate by installing `fsverity_operations` and calling open/read verification hooks, after fscrypt open when encryption is combined.

Risks: Filesystem callbacks must handle concurrent descriptor reads and Merkle reads. Missing memory ordering around `S_VERITY` can expose partially initialized state. `!CONFIG_FS_VERITY` stubs return `-EOPNOTSUPP` or warn on impossible verification calls, so callers must respect config and inode flags.

Test signals: Enable/measure/read metadata ioctls on supported filesystems, corrupted data and corrupted Merkle page reads, encrypted verity file opens, descriptor size boundary tests, concurrent reads during initialization, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsverity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace.h -->
# sources/distributed-fs/ceph-client/include/linux/ftrace.h

Purpose: Provides the main Linux function tracing API, including runtime function callbacks, dynamic call-site patching, module symbol lookup, register access, direct-call support, stack tracing coordination, and function graph tracing interfaces.

Important APIs/types/functions: Key types include `ftrace_ops`, `ftrace_regs`, `dyn_ftrace`, `ftrace_ops_hash`, `ftrace_func_entry`, `ftrace_graph_ent`, `ftrace_graph_ret`, `fgraph_ops`, and `ftrace_ret_stack`. Important functions include `register_ftrace_function()`, `unregister_ftrace_function()`, `ftrace_ops_get_func()`, dynamic filter setters, direct-call registration/modification, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_modify_call()`, module init/enable/release helpers, graph tracer registration, and `ftrace_kill()`. Numerous flags (`FTRACE_OPS_FL_*`, `FTRACE_FL_*`) describe callback capabilities and call-site state.

Control flow: Function entry instrumentation reaches architecture ftrace callers, which dispatch through either a unique ops callback or an ops list depending on architecture support. Dynamic ftrace records describe mcount/fentry sites; filters select records; update functions decide whether to make calls, nops, or modify call targets; architecture hooks patch text under safe synchronization. Function graph tracing replaces return addresses and later dispatches return handlers.

State and persistence behavior: Runtime state includes global `ftrace_enabled`, the RCU-linked `ftrace_ops_list`, dynamic hashes, per-record flags/counters, trampoline addresses, per-task graph return stacks, static keys, and tracing buffers. No state is persistent across boot except build-time instrumentation sections.

Dependencies and integration points: Depends on architecture ftrace support, kallsyms, modules, static keys, tracing buffers, pt_regs/ftrace_regs accessors, stack tracer state, preempt tracing, syscall tracing, and text patching infrastructure. It is a cross-cutting integration point for tracing, live patching, BPF-like direct hooks, perf stack capture, and diagnostics.

Risks: Text patching is architecture-sensitive and must verify expected bytes. `IPMODIFY`, direct calls, save-regs, and graph tracing have exclusivity constraints. Registered `ftrace_ops` must remain allocated after unregister long enough for CPU synchronization. Recursion and RCU flags must match callback behavior. Disabled config paths often return success macros, so build coverage matters.

Test signals: Build matrix over function tracer, dynamic ftrace, regs, direct calls, call ops, graph tracer, modules, and tracing disabled. Run ftrace selftests, filter/notrace writes, module load/unload tracing, direct-call conflict tests with IP modification, stack tracer disable/enable assertions, and graph tracer task lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_irq.h -->
# sources/distributed-fs/ceph-client/include/linux/ftrace_irq.h

Purpose: Supplies tiny NMI enter/exit hooks used by tracing subsystems that need to observe interrupt-disabled or non-maskable-interrupt latency windows.

Important APIs/types/functions: Exports `ftrace_nmi_enter()` and `ftrace_nmi_exit()`. When configured, they consult `trace_hwlat_callback_enabled` and `trace_osnoise_callback_enabled` and call `trace_hwlat_callback(bool enter)` and `trace_osnoise_callback(bool enter)`.

Control flow: Architecture or IRQ/NMI entry code calls the enter helper at NMI entry and the exit helper on return. Each helper conditionally dispatches to enabled latency tracers with `true` or `false`.

State and persistence behavior: This header owns no persistent state. It reads global boolean enable flags from hwlat and osnoise tracers.

Dependencies and integration points: Integrated with `CONFIG_HWLAT_TRACER` and `CONFIG_OSNOISE_TRACER` tracing subsystems and any low-level IRQ/NMI path that wants to bracket latency accounting.

Risks: The callbacks run in NMI context, so implementations must be NMI-safe and cannot sleep. Missing exit calls would leave tracer state unbalanced.

Test signals: Build with each tracer independently and together; verify NMI entry/exit accounting in hwlat/osnoise tests; inspect lockdep/NMI-safety warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/ftrace_regs.h

Purpose: Defines the default architecture wrapper and accessor expectations for `struct ftrace_regs`, the register snapshot abstraction passed to ftrace callbacks.

Important APIs/types/functions: Without `HAVE_ARCH_FTRACE_REGS`, `struct __arch_ftrace_regs` wraps `struct pt_regs`; `arch_ftrace_regs()` casts from `ftrace_regs`. Default accessors expose instruction pointer, arguments, stack pointer, return value, return override, register offset query, and frame pointer. `ftrace_partial_regs_update()` synchronizes changed partial register views. `FTRACE_REGS_MAX_ARGS` defaults to six.

Control flow: Ftrace callbacks use accessor macros rather than touching architecture storage. If an architecture has custom ftrace register layout, it defines `HAVE_ARCH_FTRACE_REGS` and supplies equivalent accessors; otherwise these defaults route through generic `pt_regs` helpers.

State and persistence behavior: No independent state is stored. The header defines how an existing per-callback register snapshot is interpreted and optionally updated.

Dependencies and integration points: Depends on architecture `pt_regs` helpers such as `instruction_pointer()`, `regs_get_kernel_argument()`, `kernel_stack_pointer()`, and return override helpers. Integrated directly by `ftrace.h`.

Risks: Incorrect architecture accessor definitions can corrupt function arguments, return values, or instruction pointer changes used by live patching and tracing. Partial register updates are subtle on architectures that copy rather than embed `pt_regs`.

Test signals: Architecture ftrace regs selftests, callbacks that inspect arguments and modify return values, livepatch/fprobe tests, and compile coverage with and without custom arch ftrace regs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/futex.h -->
# sources/distributed-fs/ceph-client/include/linux/futex.h

Purpose: Declares core futex keying and task lifecycle hooks for fast userspace mutex support.

Important APIs/types/functions: `union futex_key` encodes shared inode-backed keys, private mm/address keys, and common hash fields. Low bits of `offset` encode `FUT_OFF_INODE` or `FUT_OFF_MMSHARED`. `futex_init_task()` initializes robust-list pointers, PI state list/cache, exit state, and exit mutex. Runtime APIs include `do_futex()`, `futex_exit_recursive()`, `futex_exit_release()`, `futex_exec_release()`, `futex_hash_prctl()`, and optional private-hash helpers.

Control flow: Syscall handling passes user addresses, op, values, and timeout into `do_futex()`. Task initialization/exit/exec paths call lifecycle hooks to manage robust futexes and priority-inheritance state. Private hash support may allocate/free per-mm hash tables.

State and persistence behavior: Futex wait queues are runtime-only. Keys may hold references to inode or mm depending on mapping type. Task state includes robust lists, PI state, and `futex_state`.

Dependencies and integration points: Depends on scheduler/task, ktime, mm types, and UAPI futex constants. Integrates with clone/fork task init, exec, process exit, robust-list cleanup, and mm lifetime.

Risks: The key layout is hash-sensitive and must not be rearranged without updating hash code. Incorrect inode/mm reference tagging can cause use-after-free or mismatched wait queues. Disabled `CONFIG_FUTEX` stubs return `-EINVAL`.

Test signals: Futex syscall selftests, robust-list exit cleanup, PI futex tests, private versus shared mappings, `execve()` release tests, private-hash configuration builds, and stress tests under heavy mm teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fw_table.h -->
# sources/distributed-fs/ceph-client/include/linux/fw_table.h

Purpose: Provides shared parsing declarations for ACPI and ACPI-like firmware tables, including CXL CDAT consumers.

Important APIs/types/functions: Handler typedefs are `acpi_tbl_entry_handler` and `acpi_tbl_entry_handler_arg`. `acpi_subtable_proc` binds IDs, handlers, arguments, and count. `fw_table_header` overlays ACPI and CDAT table headers. `acpi_subtable_headers` overlays known subtable header variants. Main functions are `acpi_parse_entries_array()` and `cdat_table_parse()`. `EXPORT_SYMBOL_FWTBL_LIB()` and `__init_or_fwtbl_lib` select export/init attributes depending on ACPI and CXL.

Control flow: Callers supply a firmware table header, max length, and handler array. The parser walks subtables, dispatches matching IDs to handlers, and records counts. CDAT parsing filters by `enum acpi_cdat_type`.

State and persistence behavior: This header defines no stored state; parser state is caller-owned and counts are held in `acpi_subtable_proc`.

Dependencies and integration points: Depends on ACPI table structures and CXL when non-ACPI CDAT parsing is enabled. Used by firmware discovery code that needs consistent subtable iteration.

Risks: Parser correctness depends on length bounds and table header compatibility. Incorrect export namespace selection can break modular CXL consumers.

Test signals: ACPI table parser unit tests, malformed length/table boundary inputs, CDAT parser tests, and build combinations for ACPI-only, CXL-only, and both.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fw_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwctl.h -->
# sources/distributed-fs/ceph-client/include/linux/fwctl.h

Purpose: Defines the kernel driver API for `fwctl`, a character-device framework that exposes controlled firmware RPC/info interfaces to userspace.

Important APIs/types/functions: `fwctl_ops` carries the UAPI `device_type`, user context allocation size, context open/close callbacks, `info()` implementation, and `fw_rpc()` implementation. `fwctl_device` embeds a sysfs `device`, `cdev`, user-context list, registration lock, and ops pointer. `fwctl_uctx` is the per-file-descriptor context. Allocation/lifetime helpers are `_fwctl_alloc_device()`, `fwctl_alloc_device()`, `fwctl_get()`, `fwctl_put()`, `DEFINE_FREE(fwctl, ...)`, `fwctl_register()`, and `fwctl_unregister()`.

Control flow: Drivers allocate an embedding struct with `fwctl_alloc_device()`, register it, and provide ops. Opening a char device allocates a `fwctl_uctx`, calls `open_uctx()`, then ioctl paths call `info()` or `fw_rpc()`. Unregister clears ops under a write lock and waits for in-flight read-locked operations.

State and persistence behavior: State is runtime-only: device references, cdev registration, user contexts linked under `uctx_list_lock`, and driver-private bytes trailing the base structs.

Dependencies and integration points: Depends on device core, cdev, cleanup helpers, rw semaphores, mutex/list infrastructure, and `uapi/fwctl/fwctl.h`. Integrates with hot unplug and module unload through `fwctl_unregister()`.

Risks: Driver ops must not run indefinitely because unregister waits for them. `fw_rpc()` memory ownership is subtle: returned response may alias input or be freed with `kvfree()`. The allocation macro requires the `fwctl_device` member at offset zero.

Test signals: Open/close lifecycle tests, concurrent ioctl versus unregister, hot unplug while RPCs run, info buffer sizing/copy tests, invalid device type/scope handling, and KASAN/lockdep around context list management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode.h -->
# sources/distributed-fs/ceph-client/include/linux/fwnode.h

Purpose: Defines the low-level firmware node abstraction used by ACPI, device tree, and software nodes to expose device properties, graph endpoints, references, DMA capabilities, IRQs, MMIO mapping, and supplier/consumer links.

Important APIs/types/functions: Core types are `fwnode_handle`, `fwnode_link`, `fwnode_endpoint`, `fwnode_reference_args`, and `fwnode_operations`. Flags include link initialization, not-a-device, initialized, child-bound requirements, best effort, and visited. Operation macros `fwnode_has_op()`, `fwnode_call_int_op()`, `fwnode_call_bool_op()`, `fwnode_call_ptr_op()`, and `fwnode_call_void_op()` safely dispatch to providers. Helpers initialize flags and links: `fwnode_init()`, flag setters/testers, `fwnode_dev_initialized()`, `fwnode_link_add()`, `fwnode_links_purge()`, `fw_devlink_purge_absent_suppliers()`, and `fw_devlink_is_strict()`.

Control flow: Provider backends fill `fwnode_operations`; consumer APIs call through the dispatch macros to read properties, walk children, parse graph endpoints, resolve references, map resources, and create device links. Link lists connect suppliers and consumers for probe ordering.

State and persistence behavior: `fwnode_handle` carries provider ops, optional secondary fwnode, associated device pointer, supplier/consumer lists, and flags. Persistence belongs to the firmware backend; link and initialization flags are runtime state.

Dependencies and integration points: Depends on bitops, lists, error-pointer helpers, and device core. Integrates with property APIs, graph APIs, DMA attribute discovery, IRQ/resource discovery, and fw_devlink probe ordering.

Risks: Callers must handle `NULL` and error fwnodes; missing ops return `-ENXIO`, `-EINVAL`, `false`, or `NULL` depending on macro. Supplier cycles and ignored links affect probe deferral. Flag misuse can break device population ordering.

Test signals: Property read tests across ACPI/OF/software nodes, graph endpoint traversal, supplier-cycle detection, device-link purge behavior, missing-op paths, DMA/IRQ/iomap provider tests, and probe ordering tests under strict fw_devlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode_mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/fwnode_mdio.h

Purpose: Declares fwnode-based helpers for registering Ethernet PHY devices on MDIO buses.

Important APIs/types/functions: Exposes `fwnode_mdiobus_phy_device_register()` to register a prepared `phy_device` under a child fwnode/address and `fwnode_mdiobus_register_phy()` to discover/register a PHY from a child node and MDIO address.

Control flow: MDIO bus code passes the bus, child firmware node, and PHY address. If configured, helper implementation reads fwnode properties and binds/registers the PHY device. Disabled stubs return `-EINVAL`.

State and persistence behavior: This header stores no state. Registered PHY state is owned by the PHY/MDIO subsystem and device model.

Dependencies and integration points: Depends on `<linux/phy.h>`, `mii_bus`, `phy_device`, and fwnode handles. Integrates firmware descriptions with network PHY discovery.

Risks: Disabled config stubs make callers fail registration with `-EINVAL`; optional consumers must treat this distinctly from malformed firmware. Address/property mismatches can produce missing PHYs.

Test signals: MDIO registration from ACPI/software-node/device-tree-backed fwnodes, disabled `CONFIG_FWNODE_MDIO` builds, malformed address/property tests, and PHY driver probe checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gameport.h -->
# sources/distributed-fs/ceph-client/include/linux/gameport.h

Purpose: Defines the legacy gameport bus/device API for joystick/gameport hardware and drivers.

Important APIs/types/functions: `struct gameport` stores private data, name/physical path, I/O address/speed/fuzz, hardware callbacks (`trigger`, `read`, `cooked_read`, `calibrate`, `open`, `close`), polling timer fields, parent/child links, bound driver, driver mutex, device, and list node. `struct gameport_driver` defines connect/reconnect/disconnect callbacks and a `device_driver`. APIs include open/close, port register/unregister, name/phys setters, allocate/free, drvdata access, driver pin/unpin, driver register/unregister, polling start/stop, and `module_gameport_driver()`.

Control flow: Port providers allocate and register a `gameport`; bus matching calls driver connect/open; input drivers read raw or cooked values, optionally using periodic polling callbacks. Driver unregister/disconnect tears down binding.

State and persistence behavior: Runtime state lives in `gameport`, including timer/poll counters, parent-child topology, device model registration, and driver binding. No persistent storage is defined.

Dependencies and integration points: Depends on device core, timers, mutexes, lists, slab allocation, and UAPI gameport modes. Integrates with legacy input subsystem drivers.

Risks: Legacy GPIO-like I/O callbacks may sleep or run in timer context depending on use. `gameport_pin_driver()` is interruptible and callers must handle failure. Disabled `CONFIG_GAMEPORT` port registration stubs silently no-op.

Test signals: Build with reachable and disabled gameport configs, driver registration/unregistration, polling start/stop races, cooked-read/calibrate fallback behavior, and module unload while attributes pin the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gameport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gcd.h -->
# sources/distributed-fs/ceph-client/include/linux/gcd.h

Purpose: Declares the kernel greatest-common-divisor helper and a static key related to efficient find-first-set implementations.

Important APIs/types/functions: Exposes `DECLARE_STATIC_KEY_TRUE(efficient_ffs_key)` and `unsigned long gcd(unsigned long a, unsigned long b) __attribute_const__`.

Control flow: Callers invoke `gcd()` as a pure arithmetic helper. Implementation is elsewhere and may use the static key to select optimized bit operations.

State and persistence behavior: No persistent state. The static key is runtime patchable branch state.

Dependencies and integration points: Depends on compiler attributes and jump labels. Used anywhere kernel code needs an unsigned long GCD.

Risks: Inputs of zero must match implementation contract. Static-key behavior can vary by architecture feature detection.

Test signals: Kunit or simple arithmetic tests for zero, equal, coprime, powers of two, and large unsigned long values; build coverage with jump labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genalloc.h -->
# sources/distributed-fs/ceph-client/include/linux/genalloc.h

Purpose: Declares the generic special-purpose memory pool allocator for memory outside normal `kmalloc` management, such as device SRAM, uncached memory, and reserved regions.

Important APIs/types/functions: `gen_pool` owns chunk list, minimum allocation order, allocation algorithm, private algorithm data, and name. `gen_pool_chunk` tracks physical/virtual bounds, owner, availability counter, and allocation bitmap. Allocation callbacks use `genpool_algo_t`; data structs support aligned and fixed allocations. APIs include pool create/destroy, add chunks, virt-to-phys, alloc/free with optional algorithms and owners, DMA alloc/zalloc variants, chunk iteration, availability/size queries, algorithm setters, first/best/fixed-fit algorithms, devm creation, lookup, address containment, and optional OF lookup.

Control flow: A client creates a pool, adds one or more chunks, optionally sets an allocation algorithm, then allocates/free regions. Allocation scans chunk bitmaps with an algorithm and updates bits atomically so prepopulated pools can be used in NMI-like contexts on architectures with NMI-safe cmpxchg.

State and persistence behavior: Pool/chunk state is runtime-only. Chunks persist until removed by pool destruction; owner pointers provide caller metadata on allocation/free.

Dependencies and integration points: Depends on spinlock types, atomics, device and OF declarations. Integrates with platform/device memory providers and managed device lifetime.

Risks: NMI safety only applies when enough memory is already in the pool and architecture cmpxchg is NMI-safe. Extreme contention can livelock. Physical address `-1` sentinel in `gen_pool_add_virt()` users must be interpreted carefully.

Test signals: Allocation/free fragmentation tests, alignment/fixed/best-fit algorithms, owner round-trip, DMA variants, concurrent stress, NMI-safe architecture build checks, OF pool lookup, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic-radix-tree.h -->
# sources/distributed-fs/ceph-client/include/linux/generic-radix-tree.h

Purpose: Implements a typed wrapper interface for simple sparse arrays backed by a radix tree of fixed-size zeroed nodes.

Important APIs/types/functions: `GENRADIX(type)` and `DEFINE_GENRADIX()` declare typed containers. Internal types are `__genradix`, `genradix_root`, `genradix_node`, and `genradix_iter`. APIs/macros include `genradix_init()`, `genradix_free()`, `genradix_ptr()`, `genradix_ptr_inlined()`, `genradix_ptr_alloc()`, preallocated variants, iterator initialization/peek/advance/rewind, forward/reverse iteration, `genradix_last_pos()`, and `genradix_prealloc()`. Constants define 512-byte nodes, child fanout, depth encoding, and maximum depth.

Control flow: Typed macros convert element indexes into byte offsets, respecting non-power-of-two element sizes. Lookup reads the root pointer/depth, descends child pointers by offset bits, and returns a typed pointer into leaf data. Allocation creates missing nodes through `__genradix_ptr_alloc()`. Iterators skip to present nodes and expose logical positions.

State and persistence behavior: State is in memory under `radix->tree.root`, which encodes pointer plus depth in low alignment bits. Nodes are zero-initialized and freed by `genradix_free()`.

Dependencies and integration points: Depends on page constants, bug checks, log2/math helpers, slab allocation, types, and read-once semantics. Used by subsystems needing low-overhead sparse arrays without xarray features.

Risks: Stored element size must not exceed node size. Pointer/depth encoding relies on node alignment. Lookup is mostly lockless and caller synchronization is required around concurrent mutation. Non-power-of-two sizes require page-boundary offset rounding.

Test signals: Sparse allocation/lookup for power-of-two and non-power-of-two types, iteration forward/reverse, preallocation failure paths, maximum index boundaries, free/reinit behavior, and concurrent read/write tests under subsystem locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic-radix-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/common.h -->
# sources/distributed-fs/ceph-client/include/linux/generic_pt/common.h

Purpose: Defines common structures and feature bits for the generic radix page-table framework used by hardware-style page tables.

Important APIs/types/functions: `pt_common` stores encoded top table pointer/level, maximum output and virtual address sizes, and feature bitmap. `PT_TOP_LEVEL_BITS/MASK` define low-bit encoding. `enum pt_features` covers DMA-incoherent table memory, full VA, dynamic top, sign extension, range flush strategies, and a format-private feature start. Format wrappers include `pt_amdv1`, `pt_vtdss`, `pt_riscv_32`, `pt_riscv_64`, and `pt_x86_64`, each embedding `pt_common`; additional enum values describe format-specific features such as encrypted tables, forced coherence, forced writable, and RISC-V Svnapot 64K.

Control flow: Format-specific code stores common capability/configuration in `pt_common`; generic algorithms inspect feature bits to validate addresses, update top levels, flush ranges, and choose format behavior.

State and persistence behavior: Page-table runtime state is the encoded root pointer and immutable or slowly changing capability bits. Actual table page allocation is owned by format/algorithm layers.

Dependencies and integration points: Depends on type definitions, build assertions, and bit macros. It is included by generic IOMMU page-table code and format implementations.

Risks: Low-bit pointer encoding requires table pointer alignment. Incorrect feature combinations can produce invalid address validation or unsafe dynamic-top updates. Format-private features share a common start offset and must not collide inside one format.

Test signals: Compile-time layout assertions, feature matrix tests per format, dynamic-top address coverage, sign-extension valid/invalid ranges, and DMA-incoherent flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/generic_pt/iommu.h

Purpose: Declares the IOMMU-facing API for generic radix page-table implementations, letting drivers wire format-specific page tables into `iommu_domain` operations.

Important APIs/types/functions: `pt_iommu` embeds an `iommu_domain`, generic ops, driver ops, allocation NUMA node, and IOMMU device for cache maintenance. `pt_iommu_ops` provides `map_range`, `unmap_range`, `set_dirty`, `get_info`, and `deinit`. `pt_iommu_driver_ops` provides dynamic top update hooks `change_top()` and `get_top_lock()`. `pt_iommu_cfg` carries requested features and hardware VA/OA limits. Macros generate format structs/prototypes for `amdv1`, `vtdss`, `riscv_64`, `x86_64`, and mock AMDv1, plus `IOMMU_PT_DOMAIN_OPS`, `IOMMU_PT_DIRTY_OPS`, and `PT_IOMMU_CHECK_DOMAIN()`.

Control flow: IOMMU drivers initialize a format-specific table, expose the embedded domain ops, then map/unmap through `pt_iommu_ops` while holding caller-provided VA range locks. Unmap gathers IOTLB invalidations. Dynamic top support calls driver hooks under a provided spinlock.

State and persistence behavior: Runtime state is the page table itself, domain alias, ops pointers, NUMA allocation policy, and device pointer. `pt_iommu_deinit()` is safe before successful init because it only calls `deinit` when ops is set.

Dependencies and integration points: Depends on generic page-table common definitions, IOMMU core, mm types, dirty bitmap APIs, and IOTLB gather. Integrates with DMA API, IOMMUFD, dirty tracking, and hardware domain attachment lists.

Risks: Caller must serialize overlapping VA ranges. `unmap_range()` cannot split mappings created by `map_range()`. Dynamic top requires hardware atomicity and correct lock choice. Domain aliasing via unions must pass offset checks. Atomic-context flushing constraints apply to driver ops.

Test signals: IOMMU map/unmap/iova_to_phys tests, dirty tracking including `set_dirty()` races, dynamic top growth, page-size bitmap validation, unmap aggregation boundaries, IOMMUFD selftests for mock AMDv1, and lockdep around range locks/top locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_func.h -->
# sources/distributed-fs/ceph-client/include/linux/genl_magic_func.h

Purpose: Generates generic-netlink policies, ops, family registration, multicast helpers, struct parsing/serialization, and default initialization from a macro include file.

Important APIs/types/functions: This header repeatedly redefines `GENL_struct`, `GENL_op`, `GENL_notification`, `GENL_mc_group`, `__field`, and `__array` around `GENL_MAGIC_INCLUDE_FILE`. It creates top-level and nested `nla_policy` arrays, `*_from_attrs()` and `*_from_attrs_for_change()` parsers, `*_genl_cmd_to_str()`, kernel `genl_ops`, multicast group arrays/helpers, `*_genl_register()`, `*_genl_unregister()`, `*_to_skb()` plus privileged/unprivileged wrappers, and `set_*_defaults()` functions. Optional `GENL_MAGIC_DEBUG` prints field conversions.

Control flow: A consumer defines family/version/include macros, includes the struct header, then this function header. Macro expansion builds concrete code. Incoming genl messages are validated by generated policies, nested attributes are parsed into structs, invariant/required rules are enforced, and outgoing structs are serialized into nested skb attributes with sensitive fields optionally excluded.

State and persistence behavior: Generated static policies, ops arrays, family struct, multicast groups, and a shared `nested_attr_tb[128]` parse buffer are runtime global state. Serialization itself is per-message.

Dependencies and integration points: Depends on `genl_magic_struct.h`, generic netlink, nlattr helpers, skb helpers, and DRBD-specific attribute flags.

Risks: The shared nested parse buffer assumes serialized generic-netlink message processing. Macro misuse or duplicate numbers may compile but produce wrong UAPI unless struct assertions are included. Sensitive/invariant flags are DRBD-specific policy embedded in generic code. Array max length handling differs for NUL strings.

Test signals: Compile generated family users, netlink policy validation, required/missing/invariant change tests, sensitive-field redaction, multicast helper calls, buffer size boundary tests, and `GENL_MAGIC_DEBUG` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_func.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_struct.h -->
# sources/distributed-fs/ceph-client/include/linux/genl_magic_struct.h

Purpose: Provides the declaration half of the generic-netlink macro generator: it requires family metadata macros, defines attribute helper macros, emits enums, compile-time uniqueness checks, generated structs, and signedness metadata.

Important APIs/types/functions: Requires `GENL_MAGIC_FAMILY`, `GENL_MAGIC_VERSION`, and `GENL_MAGIC_INCLUDE_FILE`. Declares generated register/unregister functions. Defines DRBD flags `DRBD_F_REQUIRED`, `DRBD_F_SENSITIVE`, and `DRBD_F_INVARIANT`. Field macros map logical fields to NLA types: flag, u8/u16/u32/s32/u64, string, and binary arrays. `GENL_doit()` and `GENL_dumpit()` add admin-permission ops. Macro passes generate operation enums, top-level attribute enums, nested attribute enums, `ct_assert_unique_*()` switch helpers, `struct s_name` declarations, and `F_*_IS_SIGNED` enums.

Control flow: Consumers provide a declarative include file. Multiple macro-expansion passes reinterpret the same declarations as enums, switch-case assertions, and structs.

State and persistence behavior: This header defines types and inline helpers only; no dynamic state. Generated structs hold parsed netlink payload values and array lengths.

Dependencies and integration points: Depends on Linux args/types and `<net/genetlink.h>`. It is paired with `genl_magic_func.h` for actual policies and conversion functions.

Risks: The macro DSL is fragile: missing required family macros stops compilation, and duplicate numbers are detected only through generated duplicate `case` labels if assertion functions compile. DRBD-specific semantics leak into all users.

Test signals: Build generated users with duplicate op/attribute numbers to verify compile failures, verify struct layout from field macros, string/binary length handling, signedness metadata, and operation flag generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp.h -->
# sources/distributed-fs/ceph-client/include/linux/gfp.h

Purpose: Declares core page/folio allocation helpers and GFP flag interpretation utilities for the page allocator.

Important APIs/types/functions: Helpers include `default_gfp()`, `gfp_migratetype()`, `gfpflags_allow_blocking()`, `gfpflags_allow_spinning()`, `gfp_zone()`, `gfp_zonelist()`, `gfp_nested_mask()`, `node_zonelist()`, node warning helpers, `gfp_has_flags()`, `gfp_has_io_fs()`, and `gfp_compaction_allowed()`. Allocation APIs wrap no-profile functions through `alloc_hooks()`: `__alloc_pages`, `__folio_alloc`, bulk allocators, node allocators, NUMA/mempolicy folio allocators, `alloc_pages`, `folio_alloc`, `alloc_page`, `alloc_pages_nolock`, `__get_free_pages`, `get_zeroed_page`, exact-page allocators, and contiguous allocation APIs under `CONFIG_CONTIG_ALLOC`. Freeing APIs include `__free_pages`, `free_pages_nolock`, `free_pages`, `__free_page`, and `free_page`.

Control flow: Callers provide GFP flags; helpers derive migratetype, zone, zonelist fallback behavior, reclaim/spinning permissions, and nested-allocation masks. Allocation wrappers choose NUMA node/default node, call underlying allocator implementations, and pass through allocation hooks for profiling/tagging.

State and persistence behavior: Runtime state comes from NUMA node data, zonelists, per-CPU pages, `gfp_allowed_mask`, page grouping flags, and architecture allocation/free hooks. This header declares behavior but does not store pages itself.

Dependencies and integration points: Depends on `gfp_types.h`, memory zones, topology, allocation tags, cleanup helpers, scheduler, mempolicy, and VMA declarations. It is central to MM, filesystems, drivers, and any kernel subsystem allocating pages.

Risks: Invalid zone flag combinations trigger `VM_BUG_ON`; misuse of `__GFP_NOFAIL`, reclaim flags, or nested masks can deadlock or stall. `GFP_NOFS/NOIO` contexts are especially important for filesystem recursion. Node-specific allocation from offline nodes warns.

Test signals: MM page allocator tests, NUMA fallback tests, invalid GFP flag debug builds, allocation failure injection, nofs/noio lockdep scenarios, contiguous allocation tests, allocation hook/profiling builds, and hibernation `gfp_allowed_mask` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_api.h -->
# sources/distributed-fs/ceph-client/include/linux/gfp_api.h

Purpose: Compatibility include wrapper that exposes the GFP allocation API by including `linux/gfp.h`.

Important APIs/types/functions: This file declares no APIs of its own; all visible symbols are inherited from `gfp.h`.

Control flow: Preprocessor-only include indirection.

State and persistence behavior: No state.

Dependencies and integration points: Depends entirely on `linux/gfp.h`; useful for source compatibility where code includes a more API-oriented header name.

Risks: Because it is a one-line include, any include-cycle or layering concern is inherited from `gfp.h`.

Test signals: Header self-include/compile tests and include-what-you-use checks for consumers expecting GFP allocation declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_types.h -->
# sources/distributed-fs/ceph-client/include/linux/gfp_types.h

Purpose: Defines the bit positions, internal masks, public `__GFP_*` modifiers, and common `GFP_*` flag combinations used by the Linux memory allocator.

Important APIs/types/functions: Internal enum values define GFP bit positions for zones, mobility, reclaim, I/O, zeroing, retry policy, accounting, KASAN tag behavior, lockdep, and object extensions. Public flags include zone modifiers (`__GFP_DMA`, `__GFP_HIGHMEM`, `__GFP_DMA32`, `__GFP_MOVABLE`), mobility/placement flags, watermark flags, reclaim flags, action flags, and `__GFP_BITS_MASK`. Common combinations include `GFP_ATOMIC`, `GFP_KERNEL`, `GFP_KERNEL_ACCOUNT`, `GFP_NOWAIT`, `GFP_NOIO`, `GFP_NOFS`, `GFP_USER`, `GFP_DMA`, `GFP_DMA32`, `GFP_HIGHUSER`, `GFP_HIGHUSER_MOVABLE`, `GFP_TRANSHUGE_LIGHT`, and `GFP_TRANSHUGE`.

Control flow: Consumers build `gfp_t` values from these constants; allocator code in `gfp.h` and MM interprets zones, reclaim behavior, compaction/retry policy, and accounting from the bitmask.

State and persistence behavior: Pure compile-time definitions; no runtime state.

Dependencies and integration points: Depends on bit macros and must stay synchronized with tracing/perf MM flag decoders. Integrated into almost every allocation call path.

Risks: Bit changes are ABI-like inside kernel tooling and must update trace event decoders and perf. Some combinations are invalid or dangerous, especially `__GFP_NOFAIL` in non-sleepable contexts and reclaim flags inside filesystem locks.

Test signals: Build-time checks in MM, trace/perf flag rendering tests, allocation behavior tests for common masks, KASAN HW tags builds, lockdep builds, and documentation consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/glob.h -->
# sources/distributed-fs/ceph-client/include/linux/glob.h

Purpose: Declares a pure glob-pattern matcher for kernel string matching.

Important APIs/types/functions: Exposes `bool glob_match(char const *pat, char const *str) __pure`.

Control flow: Callers pass a pattern and candidate string; implementation returns whether the string matches the glob syntax.

State and persistence behavior: No state; pure function contract implies no observable side effects.

Dependencies and integration points: Depends on bool/type definitions and compiler attributes. Used by subsystems needing lightweight pattern matching without regex.

Risks: Callers must know the exact supported glob syntax from implementation/tests; not a security boundary unless inputs and pattern semantics are validated.

Test signals: Pattern matching tests for wildcards, literals, empty strings, escaping if supported, long inputs, and repeated calls validating pure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/glob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gnss.h -->
# sources/distributed-fs/ceph-client/include/linux/gnss.h

Purpose: Defines the GNSS receiver character-device framework used by drivers that expose raw navigation data streams to userspace.

Important APIs/types/functions: `enum gnss_type` covers NMEA, SiRF, UBX, MTK, and count. `gnss_operations` provides open, close, and raw write callbacks. `gnss_device` embeds device/cdev IDs, type, flags, rw semaphore, ops, open count, disconnected flag, read mutex/FIFO/wait queue, write mutex, and write buffer. APIs include allocate/put/register/deregister, `gnss_insert_raw()`, and drvdata accessors.

Control flow: Drivers allocate and register a GNSS device. Userspace opens the cdev, causing driver open; driver receive paths push raw bytes with `gnss_insert_raw()` into a FIFO and wake readers; userspace writes are passed to `write_raw()` under write serialization; close tears down per-open state.

State and persistence behavior: Runtime state includes cdev/device registration, FIFO contents, open count, disconnected flag, and driver-private data. No persistent positioning state is stored here.

Dependencies and integration points: Depends on cdev/device core, kfifo, mutexes, rwsems, waits, and types. Integrates with serial/USB/platform GNSS receiver drivers.

Risks: FIFO overflow/backpressure behavior must be handled by implementation. Disconnect races are guarded by rwsem and flags; driver callbacks must respect lifecycle. Writes are raw protocol data and require device-specific validation.

Test signals: Register/open/read/write/close tests, disconnect during blocking read/write, FIFO overflow handling, multi-reader/writer serialization, and driver unregister cleanup under KASAN/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gnss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/goldfish.h -->
# sources/distributed-fs/ceph-client/include/linux/goldfish.h

Purpose: Provides helper functions for Goldfish virtual platform drivers to write host pointers or DMA addresses into split 32-bit MMIO registers.

Important APIs/types/functions: `gf_ioread32` and `gf_iowrite32` default to `ioread32`/`iowrite32` unless overridden. `gf_write_ptr()` writes lower 32 bits of a kernel pointer and, on 64-bit kernels, upper bits. `gf_write_dma_addr()` writes lower bits of a `dma_addr_t` and upper bits when DMA addresses are 64-bit.

Control flow: A driver passes low/high MMIO register addresses; helpers split the pointer/address and issue MMIO writes in low-then-high order.

State and persistence behavior: No kernel state is stored; effects persist in device MMIO registers according to virtual hardware behavior.

Dependencies and integration points: Depends on kernel bit helpers, types, and MMIO accessors. Used by Goldfish emulator device drivers.

Risks: Register ordering must match device specification. Pointer writes expose kernel virtual addresses to the virtual device and should be used only where the platform expects them. High register is untouched on 32-bit pointer/DMA configurations.

Test signals: Goldfish driver tests on 32-bit and 64-bit configurations, MMIO write tracing for low/high register values, and DMA address width build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/goldfish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio-pxa.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio-pxa.h

Purpose: Declares PXA platform GPIO helper macros and platform data for legacy PXA GPIO controllers.

Important APIs/types/functions: `GPIO_bit(x)` selects a bit within a 32-line bank. `gpio_to_bank(gpio)` maps a GPIO number to a bank. `pxa_last_gpio` exposes the last implemented GPIO number. `pxa_irq_to_gpio()` maps IRQs back to GPIOs. `pxa_gpio_platform_data` carries IRQ base and optional `gpio_set_wake()` callback.

Control flow: PXA GPIO drivers and platform setup code use macros for register bit/bank calculations and platform data to configure IRQ/wakeup behavior.

State and persistence behavior: `pxa_last_gpio` is global runtime/platform state; wake configuration persists in hardware/controller state.

Dependencies and integration points: Integrates with PXA board files, GPIO controller drivers, and IRQ wake management.

Risks: Some PXA SoCs have holes in GPIO numbering, so callers must not assume contiguous valid lines up to a fixed architectural maximum. IRQ-to-GPIO mappings are platform-specific.

Test signals: PXA GPIO driver build tests, bank/bit mapping tests around 31/32 boundaries, IRQ-to-GPIO mapping checks, wake callback tests, and platform data validation for SoC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio-pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio.h

Purpose: Legacy bulk GPIO include that exposes old global-number GPIO APIs while warning new code to use driver or consumer-specific headers.

Important APIs/types/functions: Legacy flags include `GPIOF_IN`, `GPIOF_OUT_INIT_LOW`, and `GPIOF_OUT_INIT_HIGH`. With legacy gpiolib, APIs include `gpio_is_valid()`, `gpio_request()`, `gpio_free()`, direction setters, value get/set raw wrappers, cansleep variants, `gpio_to_irq()`, `gpio_request_one()`, and `devm_gpio_request_one()`. When gpiolib is enabled, most operations bridge through descriptor APIs such as `gpio_to_desc()` and `gpiod_*`. Disabled stubs return `-ENOSYS`/`-EINVAL`, warn, or no-op.

Control flow: Legacy consumers request a global GPIO number, set direction, read/write values, optionally map to IRQ, then free. The header adapts these calls to descriptor-based gpiolib when available.

State and persistence behavior: No state in the header; requested GPIO state lives in gpiolib and hardware. Global numbering is a legacy namespace.

Dependencies and integration points: Depends on `linux/gpio/consumer.h` when `CONFIG_GPIOLIB` is set, and on legacy gpiolib config. Bridges old drivers/platform data to modern descriptor infrastructure.

Risks: New code should avoid this header. Global GPIO numbers are ambiguous and platform-dependent. Disabled stubs may warn if code calls GPIO operations without gpiolib. Raw value APIs bypass active-low semantics.

Test signals: Legacy driver builds, request/direction/value/IRQ tests through descriptor backend, disabled gpiolib build warnings, and migration tests comparing legacy and descriptor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/aspeed.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/aspeed.h

Purpose: Declares Aspeed GPIO coproccessor coordination helpers for GPIO lines shared with a coproccessor.

Important APIs/types/functions: `aspeed_gpio_copro_ops` provides `request_access()` and `release_access()` callbacks. APIs include `aspeed_gpio_copro_grab_gpio()` to claim a descriptor and return value/data register offsets plus bit, `aspeed_gpio_copro_release_gpio()`, and `aspeed_gpio_copro_set_ops()` to install copro access callbacks and private data.

Control flow: A copro-aware user installs access ops, grabs a GPIO descriptor to obtain hardware register coordinates, performs coordinated access, then releases it.

State and persistence behavior: Runtime state is maintained by the Aspeed GPIO implementation, including registered ops and any claimed line ownership. Hardware register offsets identify persistent controller registers, not stored by the header.

Dependencies and integration points: Depends on GPIO descriptors and Aspeed GPIO controller internals. Integrates BMC host/coprocessor coordination with gpiolib.

Risks: Incorrect grab/release pairing can leave GPIO access blocked. Register offsets and bit values must match controller generation. Access callbacks may need strict locking against host GPIO operations.

Test signals: Aspeed GPIO build tests, grab/release lifecycle tests, concurrent host/copro access, invalid descriptor handling, and hardware register offset validation on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/aspeed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/consumer.h

Purpose: Defines the descriptor-based GPIO consumer API for drivers that acquire, configure, read, write, and release GPIO lines without using global GPIO numbers.

Important APIs/types/functions: `gpio_descs` represents arrays from `gpiod_get_array()`. `enum gpiod_flags` describes initial direction/value/open-drain requests. Acquisition APIs include plain, indexed, optional, array, devm, and fwnode variants. Release APIs include `gpiod_put()`, array put, and devm put/unhinge. Direction/value APIs include raw and logical get/set, array variants, and cansleep variants. Other helpers cover debounce/config, active-low toggling/query, sleep capability, IRQ mapping, consumer naming, shared descriptor checks, legacy conversion, hardware GPIO number, equality, hardware timestamp enable/disable, ACPI GPIO mapping, sysfs export, and `gpiod_multi_set_value_cansleep()`.

Control flow: Consumers acquire descriptors by device/connection ID or fwnode, optionally setting initial direction. Runtime paths choose non-sleeping or cansleep accessors based on descriptor capability, use logical APIs for active-low aware values or raw APIs for physical levels, then release descriptors manually or via devm.

State and persistence behavior: Descriptor ownership, direction, active-low, debounce, timestamping, and exported sysfs state are maintained by gpiolib/controller drivers. The header defines acquisition and access contracts.

Dependencies and integration points: Depends on errors, bit macros, GPIO defs, device/fwnode/ACPI declarations, gpiolib, ACPI, HTE, and GPIO sysfs configs. It is the primary consumer integration point for device drivers.

Risks: Non-optional getters return error pointers while optional getters return `NULL` for absent GPIOs. Non-sleeping accessors are invalid for `gpiod_cansleep()` descriptors. Raw APIs bypass active-low translation. Disabled `CONFIG_GPIOLIB` stubs often warn and return `-ENOSYS`, `NULL`, or zero, so callers must distinguish absence from infrastructure failure.

Test signals: GPIO mock/controller tests for acquisition forms, optional absent lines, active-low logical versus raw values, array set/get, cansleep misuse detection, debounce/config, IRQ mapping, fwnode and ACPI mappings, HTE timestamp config, sysfs export, and disabled-config compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/defs.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/defs.h

Purpose: Provides small common GPIO direction constants shared by GPIO headers.

Important APIs/types/functions: Defines `GPIO_LINE_DIRECTION_IN` as `1` and `GPIO_LINE_DIRECTION_OUT` as `0`.

Control flow: Consumers compare or assign direction values using these constants.

State and persistence behavior: No state; compile-time constants only.

Dependencies and integration points: Included by `gpio/consumer.h` and any code needing direction constants without the full GPIO API.

Risks: Direction values are intentionally simple but must stay aligned with gpiolib expectations and UAPI-adjacent representations.

Test signals: Compile coverage and GPIO direction tests that map descriptor direction queries to these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/defs.h -->
