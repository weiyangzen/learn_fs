# subset-b-005865 grouped research

This grouped report covers the requested Linux compatibility/API headers under `sources/distributed-fs/ceph-client/include/linux`. Each section preserves the source path and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interrupt.h -->
# sources/distributed-fs/ceph-client/include/linux/interrupt.h

Purpose: This header is the kernel IRQ, softirq, and tasklet API surface. It defines IRQ trigger and handling flags, the `irq_handler_t` callback shape, `struct irqaction`, IRQ request/free helpers, affinity descriptors, softirq vectors, and deprecated tasklet scheduling primitives.

Important APIs, types, and functions: Drivers use `request_irq`, `request_threaded_irq`, `request_any_context_irq`, `request_percpu_irq`, `request_nmi`, `free_irq`, `disable_irq*`, `enable_irq*`, `irq_wake_thread`, and wake controls. SMP builds expose `irq_set_affinity`, affinity hints, notifier registration, and generated affinity masks. Softirq users rely on `open_softirq`, `raise_softirq`, `raise_timer_softirq`, `do_softirq`, and per-CPU `ksoftirqd`/`ktimerd`. Tasklets expose `tasklet_setup`, schedule, disable/enable, and kill helpers.

Control flow: Request helpers register action records with hardirq and optional threaded handlers; inline wrappers add `IRQF_COND_ONESHOT`. Disable/enable calls gate delivery and provide lockdep-specific variants. Softirq state is raised per CPU and later drained by interrupt return paths, ksoftirqd, or ktimerd under forced threading. Tasklet scheduling sets state bits and queues execution once until it runs or is rescheduled.

State and persistence: IRQ action chains persist until freed. Affinity notifiers use `kref` and workqueue release. Softirq pending bits live in per-CPU irq stats. Tasklets persist in caller-owned storage with atomic disable counts and state bits.

Dependencies and integration points: Integrates with arch IRQ entry code, procfs interrupt reporting, power suspend/resume, lockdep, PREEMPT_RT forced threading, workqueues, cpumasks, hrtimers, and resource trigger flags from `ioport.h`.

Risks: Mismatched `dev_id` on shared IRQ free, using sleeping operations in hardirq context, incorrect oneshot flags for threaded handlers, affinity assumptions on non-SMP builds, tasklet lifetime races, and PREEMPT_RT behavior differences. Tasklets are explicitly deprecated for new code.

Test signals: IRQ request/free paths should be tested with shared and threaded handlers, suspend/resume wake behavior, CPU affinity changes and notifier release, softirq raising under forced threading, tasklet disable/kill races, and !SMP/!PROC/!GENERIC_IRQ_PROBE compile configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interval_tree.h -->
# sources/distributed-fs/ceph-client/include/linux/interval_tree.h

Purpose: This header declares the generic augmented red-black interval tree used to index inclusive unsigned-long ranges and query overlap efficiently.

Important APIs, types, and functions: `struct interval_tree_node` stores an `rb_node`, `start`, inclusive `last`, and augmented `__subtree_last`. Core operations are `interval_tree_insert`, `interval_tree_remove`, `interval_tree_subtree_search`, `interval_tree_iter_first`, and `interval_tree_iter_next`. `struct interval_tree_span_iter` and `interval_tree_for_each_span` classify a requested range into alternating hole and used spans.

Control flow: Insert/remove are implemented elsewhere using augmented rbtree maintenance. Overlap iteration starts at the first intersecting node and advances to the next node whose interval intersects `[start,last]`. Span iteration initializes over a full requested range, greedily merges consecutive covered nodes into used spans, and reports gaps as holes until `is_hole == -1`.

State and persistence: Tree state is caller-owned through `rb_root_cached`; nodes must remain stable while linked. Span iterator keeps private node pointers and the current public span boundaries.

Dependencies and integration points: Depends on `linux/rbtree.h` and is the public concrete instance of the generic template in `interval_tree_generic.h`. Filesystems, memory managers, lock managers, and allocators can use it wherever interval overlap queries are needed.

Risks: The range end is inclusive, so off-by-one bugs are likely when callers convert from length-based ranges. Callers must provide external locking, prevent duplicate node misuse, and keep `start <= last`. Span iterator fields marked private should not be mutated by users.

Test signals: Insert/remove/query tests should cover empty trees, non-overlap fast paths, one-point intervals, adjacent-but-not-overlapping ranges, nested intervals, duplicate starts, span holes at beginning/end, and greedy merge of overlapping used spans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interval_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interval_tree_generic.h -->
# sources/distributed-fs/ceph-client/include/linux/interval_tree_generic.h

Purpose: This header is a macro template for generating type-specific interval tree implementations backed by augmented cached red-black trees.

Important APIs, types, and functions: `INTERVAL_TREE_DEFINE(ITSTRUCT, ITRB, ITTYPE, ITSUBTREE, ITSTART, ITLAST, ITSTATIC, ITPREFIX)` expands to callbacks and functions named `<prefix>_insert`, `<prefix>_remove`, `<prefix>_subtree_search`, `<prefix>_iter_first`, and `<prefix>_iter_next`. It uses `RB_DECLARE_CALLBACKS_MAX` to maintain each node's maximum interval end in its subtree.

Control flow: Insert descends by interval start, updates ancestor subtree maxima opportunistically, links the node, and calls `rb_insert_augmented_cached`. Remove erases with augmented callbacks. `iter_first` uses root subtree max and cached leftmost start to reject non-overlapping queries in O(1), then calls subtree search. `iter_next` tries the right subtree, then climbs until a parent from a left branch can intersect.

State and persistence: The generated tree persists in a caller-supplied `rb_root_cached`. Each node must include an rbtree member and a maintained max-end field. The template does not allocate or free nodes.

Dependencies and integration points: Depends on `linux/rbtree_augmented.h`. It underpins the concrete `interval_tree` API and any subsystem needing custom interval endpoint types or struct layouts.

Risks: This macro assumes valid interval ordering and a correct subtree field. Supplying expressions with side effects for `ITSTART` or `ITLAST` can be dangerous because they are evaluated multiple times. External synchronization is required. The generated functions trust that removed nodes are linked in the target tree.

Test signals: Type-specific users should test insertion order permutations, cached leftmost correctness, subtree max maintenance after rotations/removes, inclusive boundary overlap, no-overlap fast paths, and iteration after deleting root or leftmost nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interval_tree_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-hi-lo.h -->
# sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-hi-lo.h

Purpose: This header supplies fallback non-atomic 64-bit MMIO accessors for hardware that requires the high 32-bit half to be accessed before the low half.

Important APIs, types, and functions: It defines `hi_lo_readq`, `hi_lo_writeq`, relaxed variants, `ioread64_hi_lo`, `iowrite64_hi_lo`, big-endian variants, and conditional aliases for `readq`, `writeq`, `ioread64`, and `iowrite64` when the architecture has not already defined them.

Control flow: Reads perform two 32-bit accesses in high-then-low order and combine as `low + ((u64)high << 32)`. Writes split the 64-bit value and emit high then low. Big-endian helpers reverse address interpretation appropriately. Generic iomap plus 64-bit builds can redirect to `__ioread64_hi_lo`/`__iowrite64_hi_lo`.

State and persistence: No persistent state is held; behavior is entirely compile-time aliasing and inline MMIO operations.

Dependencies and integration points: Depends on `linux/io.h` and `asm-generic/int-ll64.h`. Device drivers include this when register semantics mandate high-low ordering and native 64-bit accessors are absent.

Risks: Accesses are explicitly non-atomic, so hardware registers that change between halves can return torn values. Using this for devices that require low-high order can trigger side effects or wrong latching. Relaxed variants omit normal ordering guarantees.

Test signals: Build tests should verify alias selection across arch/native/generic-iomap combinations. Driver tests should validate hardware register ordering, endian behavior, relaxed-vs-ordered barriers, and read consistency for counters or latch registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-hi-lo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-lo-hi.h -->
# sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-lo-hi.h

Purpose: This header supplies fallback non-atomic 64-bit MMIO accessors for hardware that requires the low 32-bit half to be accessed before the high half.

Important APIs, types, and functions: It defines `lo_hi_readq`, `lo_hi_writeq`, relaxed variants, `ioread64_lo_hi`, `iowrite64_lo_hi`, big-endian variants, and conditional aliases for standard 64-bit I/O accessors when the architecture lacks native definitions.

Control flow: Reads load the low half first, then high, and combine into a 64-bit value. Writes emit low then high. Big-endian helpers map the logical halves to the correct addresses. Generic iomap plus 64-bit builds route aliases through `__ioread64_lo_hi` and related symbols.

State and persistence: No runtime state is stored. The header only establishes inline access sequences and preprocessor aliases.

Dependencies and integration points: Depends on `linux/io.h` and `asm-generic/int-ll64.h`. Drivers include it to match device register latch semantics where low access must precede high access.

Risks: Reads and writes are not atomic. Choosing this header for high-low devices can break register latching or command sequencing. Relaxed helpers reduce ordering constraints, and split writes to command registers may expose transient values to hardware.

Test signals: Test by compiling with and without arch-defined `readq`/`ioread64`, validating generated aliases, exercising endian-specific helpers, and checking device manuals or simulations for half-order side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-lo-hi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-mapping.h -->
# sources/distributed-fs/ceph-client/include/linux/io-mapping.h

Purpose: This header provides an abstraction for efficient CPU mappings of pages from an I/O device, especially write-combining mappings for large device apertures.

Important APIs, types, and functions: `struct io_mapping` records base, size, pgprot, and optionally a permanent `iomem` mapping. APIs include `io_mapping_init_wc`, `io_mapping_fini`, `io_mapping_create_wc`, `io_mapping_free`, `io_mapping_map_atomic_wc`, `io_mapping_unmap_atomic`, `io_mapping_map_local_wc`, `io_mapping_unmap_local`, `io_mapping_map_wc`, and `io_mapping_unmap`.

Control flow: On `CONFIG_HAVE_ATOMIC_IOMAP`, initialization reserves an iomap range and page mappings are created on demand through fixmap/local mapping helpers. Atomic map disables preemption or migration and page faults, then maps one PFN; unmap reverses this. Without atomic iomap, init creates one `ioremap_wc` covering the full range, and map helpers return offsets into it.

State and persistence: An `io_mapping` persists until `io_mapping_fini` or `io_mapping_free`. Atomic/local mappings are short-lived and must be paired with unmap calls in the same execution context.

Dependencies and integration points: Integrates with `ioremap_wc`, `iomap_create_wc`, `kunmap_local_indexed`, pagefault control, PREEMPT_RT migration rules, and device memory consumers such as graphics drivers.

Risks: Offset bounds are checked with `BUG_ON`, so invalid callers crash. Atomic mappings must not sleep and must be unmapped promptly. PREEMPT_RT changes preemption to migration disable. Permanent fallback can consume significant kernel virtual address space.

Test signals: Exercise both config branches, offset-at-end checks, atomic/local nesting, PREEMPT_RT builds, write-combining attributes, and cleanup after failed allocation or mapping initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-pgtable.h -->
# sources/distributed-fs/ceph-client/include/linux/io-pgtable.h

Purpose: This header defines the I/O page-table allocator interface used by IOMMU drivers to create and manipulate hardware-specific translation tables.

Important APIs, types, and functions: Formats are enumerated by `enum io_pgtable_fmt`. `struct io_pgtable_cfg` describes quirks, address sizes, page sizes, coherency, TLB callbacks, optional custom allocators, and backend-private format data. `struct io_pgtable_ops` provides `map_pages`, `unmap_pages`, `iova_to_phys`, optional `pgtable_walk`, and dirty tracking. Allocation is through `alloc_io_pgtable_ops` and `free_io_pgtable_ops`.

Control flow: IOMMU drivers select a format and pass configuration plus a cookie to the allocator. Backends populate format-specific config, return ops, and use `iommu_flush_ops` callbacks for full flushes, walk-cache flushes, and page invalidation batching. Inline helpers call TLB callbacks only when present.

State and persistence: `struct io_pgtable` stores the selected format, cookie, copied config, and operation table. Page-table memory persists until `free_io_pgtable_ops`; TLB dirtiness may remain and must be handled by caller sequencing.

Dependencies and integration points: Depends on `linux/iommu.h` for protection flags, dirty bitmap, and gather state. Integrates with ARM LPAE/v7s, Mali, Apple DART, and AMD backend init functions.

Risks: Wrong quirks or address-size fields can create invalid translations. Custom allocators must return zeroed DMA-mappable memory. TLB callbacks can run in atomic context and must not block. Dirty tracking requires hardware/backend support and correct clear/no-clear flags.

Test signals: Backend tests should cover map/unmap granularity, TLB callback ordering, custom allocator acceptance, unsupported quirks, dirty bit read/clear, `pgtable_walk` output, and allocation/free across every enabled format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io-pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io.h -->
# sources/distributed-fs/ceph-client/include/linux/io.h

Purpose: This header is a generic kernel I/O mapping and memory-remap facade layered over architecture `asm/io.h`.

Important APIs, types, and functions: It declares copy helpers `__iowrite32_copy`, `__ioread32_copy`, `__iowrite64_copy`, `ioremap_page_range`, `vmap_page_range`, devres-managed `devm_ioremap*`, `devm_iounmap`, `devm_memremap`, `memremap`, `memunmap`, `pci_remap_cfgspace`, write-combining reservation helpers, and strict devmem `range_is_allowed`.

Control flow: MMU builds call real range mappers; non-MMU builds return success stubs. PCI config remap prefers non-posted `ioremap_np` and falls back to `ioremap`. `range_is_allowed` walks each PFN through `devmem_is_allowed` when strict devmem is enabled.

State and persistence: Devres-managed mappings are tied to a `struct device`; unmanaged `memremap`/`memunmap` and WC reservation handles require explicit release. Architecture WC handles may represent MTRR/PAT-like state.

Dependencies and integration points: Includes `asm/io.h`, `asm/page.h`, device resource management, PCI, devmem policy, memory encryption flags, and cacheability attributes.

Risks: Incorrect cacheability or posted/non-posted mapping selection can break device ordering. Missing unmap or WC release leaks virtual address or arch tracking resources. Strict devmem checks can reject userspace mappings that worked on permissive configs.

Test signals: Compile across MMU/non-MMU, PCI/non-PCI, strict devmem, and architecture override configurations. Runtime tests should cover devres cleanup, WC reserve/free pairing, `pci_remap_cfgspace` fallback, and user mapping policy for exclusive or restricted ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring.h -->
# sources/distributed-fs/ceph-client/include/linux/io_uring.h

Purpose: This header exposes small task and file lifecycle hooks for the io_uring core to the rest of the kernel.

Important APIs, types, and functions: With `CONFIG_IO_URING`, it declares `__io_uring_cancel`, `__io_uring_free`, `io_uring_unreg_ringfd`, `io_uring_get_opcode`, `io_is_uring_fops`, and `__io_uring_fork`. Inline wrappers are `io_uring_files_cancel`, `io_uring_task_cancel`, `io_uring_free`, and `io_uring_fork`. Disabled builds provide no-op or safe default stubs.

Control flow: File cancellation cancels the current task's io_uring work without forcing all cancellations; task cancellation requests broader cancellation. Freeing only enters core cleanup if the task has io_uring state or restrictions. Fork handling only calls the core when restrictions need inheritance processing.

State and persistence: State lives in `task_struct` fields such as `io_uring` and `io_uring_restrict`; the header itself owns no storage.

Dependencies and integration points: Depends on scheduler/task state, xarray declarations, and UAPI opcode definitions. Integrates with task exit, fork, file table teardown, and file-operation identification.

Risks: Callers must use the inline guards to avoid touching absent io_uring state. Disabled builds silently no-op, so code must not depend on cancellation side effects unless io_uring is enabled. Fork restriction failures must be propagated.

Test signals: Test task exit, file table teardown, restricted ring fork, disabled-config stubs, opcode name lookup, and file operation identification for io_uring ring files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring/cmd.h -->
# sources/distributed-fs/ceph-client/include/linux/io_uring/cmd.h

Purpose: This header defines the in-kernel uring command interface used by drivers, notably block and device drivers, to implement `IORING_OP_URING_CMD` style operations.

Important APIs, types, and functions: `struct io_uring_cmd` carries file, SQE pointer, command opcode, flags, and a 32-byte private data area. Helpers include `io_uring_sqe_cmd`, `io_uring_sqe128_cmd`, `io_uring_cmd_to_pdu`, fixed-buffer import functions, `__io_uring_cmd_done`, task-work scheduling helpers, cancelable marking, blocking issue, multishot buffer selection/CQE posting, `io_uring_cmd_get_task`, context handle access, `io_uring_cmd_done`, `io_uring_cmd_done32`, and bvec buffer registration.

Control flow: Drivers parse command payloads from the SQE, optionally import fixed buffers, issue work inline/blocking/task-work, mark commands cancelable if needed, and complete through CQE posting helpers. Disabled io_uring builds return `-EOPNOTSUPP` or no-op as appropriate.

State and persistence: Command state is embedded in the io_uring request. Driver private state fits in `pdu` or external allocations. Context handles point back to the ring context for per-ring driver resources.

Dependencies and integration points: Depends on io_uring core types, UAPI SQE layout, block multiqueue requests, iov iterators, task work, and buffer selection infrastructure.

Risks: Payload size macros use build-time checks but drivers must choose the right 64-byte or 128-byte SQE mode. Completion must use issue flags supplied by core, not hard-coded values. Multishot commands must manage buffer lifetime and CQE32 mode correctly.

Test signals: Validate command payload parsing, PDU size checks, fixed buffer import, cancellation, deferred task completions, CQE32 completion, multishot buffer recycling, disabled-config behavior, and bvec register/unregister lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring/net.h -->
# sources/distributed-fs/ceph-client/include/linux/io_uring/net.h

Purpose: This small header exposes the socket-specific io_uring command entry point.

Important APIs, types, and functions: It forward-declares `struct io_uring_cmd` and declares `io_uring_cmd_sock(struct io_uring_cmd *cmd, unsigned int issue_flags)` when io_uring is enabled. Disabled builds return `-EOPNOTSUPP`.

Control flow: Network-capable uring commands are dispatched through `io_uring_cmd_sock` with core-provided issue flags; unsupported configurations fail immediately.

State and persistence: No state is defined here. Command and socket state live in io_uring core and networking code.

Dependencies and integration points: Integrates the io_uring command layer with socket/network command handling while avoiding full networking includes in generic users.

Risks: Callers must propagate `-EOPNOTSUPP` in disabled builds. Issue flags should be treated as an opaque mask from core. The header does not validate that the command's file is a socket.

Test signals: Build with and without `CONFIG_IO_URING`, exercise socket uring command dispatch, verify unsupported errors, and test cancellation/completion paths in networking command implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring_types.h -->
# sources/distributed-fs/ceph-client/include/linux/io_uring_types.h

Purpose: This header defines the main internal io_uring data structures shared across core implementation units: task state, rings, context, submission state, request flags, request objects, and completion overflow records.

Important APIs, types, and functions: Key types include `io_uring_task`, `io_rings`, `io_ring_ctx`, `io_submit_state`, `io_alloc_cache`, `io_file_table`, `io_hash_table`, `io_mapped_region`, `io_restriction`, `io_tw_state`, `io_kiocb`, `io_cqe`, and `io_overflow_cqe`. It defines issue flags (`IO_URING_F_*`), context flags (`IO_RING_F_*`), request flag bit positions, and bitwise `io_req_flags_t` values.

Control flow: The structure layout separates hot submission, completion, task-work, timeout, and cleanup cachelines. User and kernel share `io_rings` through mmap with documented ownership of SQ/CQ heads, tails, flags, drops, and overflow counters. Requests carry opcode, fixed/provided buffer state, CQE data, context/task links, poll/task-work nodes, async data, credentials, and workqueue state through their lifecycle.

State and persistence: Ring context state persists for the life of an io_uring instance and owns resource tables, wait queues, xarrays, mmap regions, restrictions, personalities, and cleanup work. Per-task state tracks registered rings and inflight counters. Requests persist until completion, cancellation, or cache recycling.

Dependencies and integration points: Depends on block, task_work, bitmaps, llist, xarray, UAPI ring layouts, optional futex and network busy-poll support, BPF filter hooks, and io-wq.

Risks: These layouts are concurrency-sensitive and cacheline-sensitive. Ring head/tail ownership and memory barriers are critical. Request flag space is bounded by `__REQ_F_LAST_BIT`. RCU, xarray, waitqueue, and lock nesting mistakes can lead to UAF, lost completions, or stuck cancellation.

Test signals: Stress SQ/CQ mmap ownership, overflow accounting, cancellation, linked requests, poll and IOPOLL, buffer selection, registered file/buffer tables, restrictions and BPF filters, resize-vs-mmap locking, task exit cleanup, and optional futex/NAPI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/io_uring_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioam6.h -->
# sources/distributed-fs/ceph-client/include/linux/ioam6.h

Purpose: This header is the kernel include wrapper for IPv6 IOAM base UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/ioam6.h>` and defines no additional kernel-only structures or helpers.

Control flow: There is no runtime control flow. Inclusion makes UAPI constants and structures available to kernel code.

State and persistence: No state is declared here.

Dependencies and integration points: Integrates IPv6 In-situ Operations, Administration, and Maintenance definitions with kernel networking code while preserving the UAPI source of truth.

Risks: Any semantic change belongs in the UAPI header; adding kernel-only definitions here could create split behavior. Include guard correctness is the only local structural concern.

Test signals: Build tests should verify users include this wrapper successfully and that IOAM code compiles against the UAPI definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioam6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioam6_genl.h -->
# sources/distributed-fs/ceph-client/include/linux/ioam6_genl.h

Purpose: This header is the kernel wrapper for IPv6 IOAM Generic Netlink UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/ioam6_genl.h>` and adds no new kernel-only APIs.

Control flow: There is no runtime flow; inclusion exposes generic-netlink command, attribute, and family definitions from UAPI to kernel networking code.

State and persistence: No persistent state is defined in this wrapper.

Dependencies and integration points: Integrates IOAM control-plane definitions with generic netlink handlers and user/kernel ABI declarations.

Risks: Diverging from the UAPI header would risk ABI confusion. Kernel code should treat this as a forwarding header and keep policy/handler state elsewhere.

Test signals: Compile IOAM generic netlink code, validate UAPI attribute policy consumers, and include this header in both enabled and modular networking configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioam6_genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioam6_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/linux/ioam6_iptunnel.h

Purpose: This header is the kernel wrapper for IPv6 IOAM lightweight tunnel UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/ioam6_iptunnel.h>` and declares no additional local types.

Control flow: No runtime behavior is implemented. The header exposes tunnel-related IOAM UAPI constants and structures.

State and persistence: No state is owned here; tunnel state lives in networking/lwtunnel implementation code.

Dependencies and integration points: Provides the kernel include path for IOAM lwtunnel code and users of the corresponding netlink tunnel attributes.

Risks: Local edits could desynchronize kernel declarations from userspace ABI. This file should remain a thin wrapper unless a kernel-only helper is strongly justified.

Test signals: Compile IOAM lightweight tunnel support, netlink attribute parsing, and disabled-feature builds that still include the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioam6_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iocontext.h -->
# sources/distributed-fs/ceph-client/include/linux/iocontext.h

Purpose: This header defines per-task block I/O context state and queue-specific `io_cq` associations used by block elevators.

Important APIs, types, and functions: `struct io_context` holds refcounts, active refs, I/O priority, and, under `CONFIG_BLK_ICQ`, a lock, radix tree, hint, ICQ list, and release work. `struct io_cq` links an `io_context` to a `request_queue` with queue and ioc list nodes. APIs include `put_io_context`, `exit_io_context`, `__copy_io`, and `copy_io`.

Control flow: Block core creates and destroys `io_cq` objects when elevators request ICQ storage. Requests hold an extra `io_context` reference while using ICQ state. `copy_io` only calls the real clone helper when the current task has an `io_context`; no-block builds stub out all operations.

State and persistence: `io_context` is refcounted and may be shared between processes. ICQs are not individually refcounted; they are destroyed when either queue or context exits, with RCU used for lookup/free safety.

Dependencies and integration points: Depends on radix trees, RCU, workqueues, block queues, elevators, task clone/exit, and I/O priority code.

Risks: Lock ordering is subtle: ioc lock nests inside queue lock, while ioc exit needs reverse-order handling. ICQ lookup validity ends when the queue lock is released. Elevator-private ICQ extensions must embed `io_cq` first and respect size/alignment requirements.

Test signals: Exercise process clone/exit with shared and unshared I/O contexts, elevator ICQ allocation/destruction, RCU lookup under queue lock, request completion references, and `CONFIG_BLOCK`/`CONFIG_BLK_ICQ` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iocontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iomap.h -->
# sources/distributed-fs/ceph-client/include/linux/iomap.h

Purpose: This header defines the filesystem iomap interface for translating file offsets to storage mappings and driving buffered I/O, writeback, fiemap, hole/data seeking, page faults, DAX, and direct I/O.

Important APIs, types, and functions: Core mapping state is `struct iomap`; operation callbacks are `struct iomap_ops`, `iomap_write_ops`, `iomap_writeback_ops`, `iomap_read_ops`, and `iomap_dio_ops`. Public functions include `iomap_iter`, buffered write/read/readahead helpers, dirty folio handling, zero/truncate/unshare, fiemap/seek/bmap, writeback ioend helpers, direct I/O `iomap_dio_rw`, and swapfile activation.

Control flow: High-level operations initialize `iomap_iter`, call filesystem `iomap_begin` to map a range, process the trimmed length, then call `iomap_end` for commit/unreserve. Buffered paths get folios, fill dirty ranges, and write back via ioends and bios. Direct I/O builds bios from mapped extents and completes through optional filesystem end_io hooks.

State and persistence: `iomap` instances carry mapping type, flags, device/DAX target, inline data, private filesystem state, and validity cookies. `iomap_ioend` tracks writeback completion aggregation and split-parent relationships. `iomap_writepage_ctx` persists current writeback mapping and pending context.

Dependencies and integration points: Integrates with address_space, folios, block devices, bios, DAX, fiemap, swap, readahead, direct I/O, reflink/COW filesystems, and integrity metadata.

Risks: Mapping flags have strong semantics: stale mappings must be remapped, shared extents must be unshared, unwritten extents require completion conversion, and inline data must stay page-bounded. Incorrect ioend merging can corrupt completion accounting. Direct-I/O flags affect alignment, page-fault retry, and stable-data requirements.

Test signals: Cover holes, delalloc, mapped, unwritten, inline, shared COW, stale validation, short writes, writeback split/merge, dirty folio batching, direct I/O alignment/fallback, DAX faults, fiemap, seek hole/data, swap activation, and block/no-block config paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iomap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu-debug-pagealloc.h -->
# sources/distributed-fs/ceph-client/include/linux/iommu-debug-pagealloc.h

Purpose: This header exposes optional IOMMU debug-pagealloc checks that validate pages are unmapped before page allocation debugging frees or reuses them.

Important APIs, types, and functions: Under `CONFIG_IOMMU_DEBUG_PAGEALLOC`, it declares the static key `iommu_debug_initialized`, page extension operations `page_iommu_debug_ops`, and `__iommu_debug_check_unmapped`. The inline `iommu_debug_check_unmapped` calls the heavy checker only when the static key is enabled. Disabled builds provide an empty inline.

Control flow: Callers invoke the inline check with a page and page count. Static-branch gating avoids overhead until debug tracking is initialized.

State and persistence: State is external: static key initialization and page extension metadata track mapping state. The header owns no storage in disabled builds.

Dependencies and integration points: Integrates IOMMU API state with page extension/pagealloc debug infrastructure and static keys.

Risks: False positives can panic or warn during legitimate delayed unmap flows; false negatives miss DMA/IOMMU leaks. The checker must only be active after metadata is initialized.

Test signals: Build with debug enabled/disabled, validate static key transition, free mapped and unmapped pages, multi-page ranges, and page extension registration ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu-debug-pagealloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/iommu-dma.h

Purpose: This header declares DMA API operations implemented through IOMMU-backed address translation.

Important APIs, types, and functions: `use_dma_iommu` reports whether a device uses IOMMU DMA. Declared operations include physical and SG map/unmap, coherent allocation/free, mmap/get_sgtable, merge-boundary and mapping-size queries, noncontiguous allocation/free/vmap/mmap, and CPU/device sync functions.

Control flow: DMA API implementations call these helpers when `dev->dma_iommu` is active. Mapping functions create IOVA mappings for physical pages or scatterlists; unmap functions tear them down. Sync functions handle cache maintenance as needed for the DMA direction and device coherency.

State and persistence: Persistent state is in the device's DMA-IOMMU cookie/domain and allocated IOVA mappings. Noncontiguous allocations return `sg_table` state that must be freed through matching helpers.

Dependencies and integration points: Depends on DMA direction definitions, `struct device`, scatterlists, VMAs, IOMMU domains, and the generic DMA mapping layer.

Risks: Mismatched map/unmap sizes or directions can leak IOVAs or corrupt cache coherency. Noncontiguous mappings require careful vmap/vunmap and mmap handling. Disabled `CONFIG_IOMMU_DMA` makes `use_dma_iommu` false but declarations remain for implementation units.

Test signals: Exercise single and SG mapping, sync direction behavior, allocation/free, mmap and get_sgtable, noncontiguous paths, merge-boundary reporting, and devices with and without `dma_iommu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu-helper.h -->
# sources/distributed-fs/ceph-client/include/linux/iommu-helper.h

Purpose: This header provides small generic helpers for IOMMU bitmap allocation and DMA boundary calculations.

Important APIs, types, and functions: `iommu_device_max_index` clamps an allocation size against a DMA mask and offset. `iommu_is_span_boundary` detects whether an indexed range crosses a power-of-two boundary. `iommu_area_alloc` allocates from a bitmap subject to start, length, shift, boundary, and alignment constraints. `iommu_num_pages` computes covered I/O pages for an address/length pair.

Control flow: Allocation users compute page counts and boundary constraints, then call `iommu_area_alloc` to find a suitable bitmap span. Boundary detection BUGs if the boundary size is not power-of-two.

State and persistence: The helpers operate on caller-owned bitmaps and have no internal state.

Dependencies and integration points: Depends on `bug.h`, `log2.h`, `math.h`, and generic types. Used by IOMMU/DMA implementations that maintain bitmap-based aperture allocators.

Risks: Invalid boundary sizes crash via `BUG_ON`. Offsets and masks must be in compatible units. Integer overflow in size+offset or address+length calculations must be considered by callers.

Test signals: Test DMA mask clamping, boundary-crossing at exact edges, non-crossing spans, page count rounding for unaligned starts, alignment masks, and failure when no bitmap span is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/iommu.h

Purpose: This is the central Linux IOMMU API header, defining domain types, protection flags, device/group abstractions, fault reporting, dirty tracking, PASID/SVA/IOPF hooks, and driver operation tables.

Important APIs, types, and functions: Key types include `iommu_domain`, `iommu_ops`, `iommu_domain_ops`, `iommu_device`, `dev_iommu`, `iommu_group`, `iommu_resv_region`, `iommu_iotlb_gather`, `iommu_dirty_bitmap`, `iommu_user_data`, `iopf_queue`, and `iopf_group`. Public APIs cover domain allocation/free, attach/detach, map/unmap/map_sg, IOVA translation, reserved regions, group management, default domain use, DMA ownership claims, PASID attach/detach, SVA bind/unbind, IOPF queueing, page responses, dirty tracking, and MSI cookie preparation.

Control flow: IOMMU drivers register `iommu_device` instances with `iommu_ops`. Core code probes devices, groups them, allocates domains, attaches devices or PASIDs, and routes map/unmap calls to domain ops. IOTLB gather helpers batch invalidation ranges and sync when granularity changes or ranges become disjoint. Fault paths collect page requests into groups and respond through device/queue handlers.

State and persistence: Domains hold type, owner ops, page-size bitmap, geometry, cookie union, and optional dirty/fault handlers. Devices hold `dev_iommu` state including fwspec, private data, fault params, and flags. Groups and global PASIDs persist until explicit release. SVA domains link into mm-associated data.

Dependencies and integration points: Integrates with devices, buses, firmware nodes, OF, PCI, MSI, scatterlists, mm, iommufd UAPI, IOVA bitmaps, debugfs, lockdep, and optional CONFIG stubs.

Risks: Domain type flags must match operation support. Missing TLB sync after unmap can leave stale DMA translations. User-data copy helpers enforce type and length for ABI compatibility; misuse can reject valid extensions or accept invalid buffers. Non-IOMMU configs return stubs that often report `-ENODEV`.

Test signals: Cover every domain type, map/unmap/TLB gather, attach error codes, group lifetime, reserved-region merging, dirty tracking, PASID/SVA, IOPF fault response, iommufd user data copy, non-IOMMU stubs, MSI isolation, and lockdep assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommufd.h -->
# sources/distributed-fs/ceph-client/include/linux/iommufd.h

Purpose: This header defines the in-kernel interface to iommufd, the user-facing IOMMU file descriptor subsystem used by VFIO, virtual IOMMUs, nested translation, access objects, and driver-managed hardware queues.

Important APIs, types, and functions: Core objects include `iommufd_object`, `iommufd_viommu`, `iommufd_vdevice`, and `iommufd_hw_queue`. APIs bind/unbind devices, attach/replace/detach page tables, create/destroy/attach access objects, pin/unpin pages, read/write IOAS memory, get contexts from files/fds, and report vIOMMU events. `iommufd_viommu_ops` defines driver callbacks for nested domains, cache invalidation, vdevice init, and hardware queue init.

Control flow: Kernel users obtain or create an `iommufd_ctx`, bind devices into it, attach devices or access objects to IO address spaces, and manage object dependencies. vIOMMU drivers allocate sanitized embedded structures via size macros, initialize virtual devices/queues, optionally allocate mmap offsets, and report events back to userspace.

State and persistence: Every userspace-visible object carries an ID, type, user refs, and wait count. vIOMMU state owns xarrays of virtual devices, event queues, hardware page table links, and driver ops. Access objects may pin pages or perform IOAS reads/writes until detached/destroyed.

Dependencies and integration points: Depends on IOMMU core, xarray, refcounting, UAPI iommufd definitions, VFIO compatibility, device model, and optional `CONFIG_IOMMUFD_DRIVER_CORE`.

Risks: Object dependency and wait-count rules are critical to avoid UAF during concurrent destroy. Driver structures must embed the core member at the checked offset/type. Disabled configs return `-EOPNOTSUPP` or NULL-like stubs. Access pinning can leak pins if detach/destroy is mishandled.

Test signals: Test object lifetime under concurrent destroy, device bind/attach/replace/detach, access pin/RW, VFIO compat IOAS creation, vIOMMU vdevice/queue init, mmap allocation teardown, event reporting, dependency helpers, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iommufd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iopoll.h -->
# sources/distributed-fs/ceph-client/include/linux/iopoll.h

Purpose: This header provides generic polling macros for repeatedly executing an operation or reading an MMIO value until a condition becomes true or a timeout expires.

Important APIs, types, and functions: Generic macros are `poll_timeout_us` and `poll_timeout_us_atomic`. Read wrappers include `read_poll_timeout`, `read_poll_timeout_atomic`, `readx_poll_timeout`, `readx_poll_timeout_atomic`, and typed MMIO helpers for `readb/readw/readl/readq` and relaxed variants.

Control flow: Non-atomic polling computes an absolute `ktime` deadline, optionally sleeps before the first operation, executes `op`, checks `cond`, checks timeout, sleeps between iterations, and calls `cpu_relax`. Atomic polling uses `udelay` and an approximate remaining-nanoseconds counter rather than timekeeping, making it usable while timekeeping is suspended.

State and persistence: No state persists beyond local macro temporaries. The last read value is stored in the caller-supplied variable even on timeout.

Dependencies and integration points: Depends on kernel time, delay, errno, CPU relax, and MMIO accessors from `io.h`. Used broadly by device drivers waiting for hardware bits.

Risks: Macros evaluate operation and condition in caller context, so side effects must be deliberate. Sleeping variants must not be used in atomic context when delay or timeout can sleep. A zero timeout means never timeout. Atomic timeout underestimates wall-clock time.

Test signals: Test immediate success, timeout, sleep-before-read, zero-timeout loops with external completion, atomic and non-atomic contexts, relaxed accessors, readq availability, and preservation of the last read value on timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iopoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioport.h -->
# sources/distributed-fs/ceph-client/include/linux/ioport.h

Purpose: This header defines the kernel resource tree abstraction used to describe, reserve, allocate, and walk I/O ports, MMIO ranges, IRQs, DMA channels, buses, and system RAM resources.

Important APIs, types, and functions: `struct resource` stores start/end, name, flags, descriptor, and tree links. The header defines `IORESOURCE_*` type, attribute, IRQ, DMA, MEM, PCI, SYSRAM, and busy flags; descriptor IDs; resource initializer macros; global roots `ioport_resource`, `iomem_resource`, and `soft_reserve_resource`; request/insert/remove/allocate/adjust helpers; managed devres wrappers; walkers; and intersection helpers.

Control flow: Callers create resource descriptors, request or insert them into a parent tree, allocate free space under constraints, and release on teardown. Helper macros route I/O port and memory requests to the correct global root. Walkers traverse RAM, soft-reserve, or descriptor-matched regions for subsystem queries.

State and persistence: Resource nodes persist as caller-owned structures linked into global or device-specific trees. Devres wrappers bind release to device lifetime. Flags and descriptors are visible through interfaces such as PCI sysfs resource files.

Dependencies and integration points: Integrates with PCI/PNP, memory hotplug, devres, iomem mapping policy, `/proc/iomem`, sysfs resource reporting, strict devmem, and IRQ trigger definitions used by interrupt code.

Risks: `resource_size` assumes inclusive end and valid start. Overlap/union helpers ignore type unless callers use contains variants. Flags are ABI-sensitive for PCI sysfs. Incorrect release or parent linkage leaks busy regions or corrupts resource trees.

Test signals: Test request conflicts, nested insertions, allocation constraints, boundary/size alignment, devres release, exclusive memory checks, RAM walkers, soft-reserve intersections, hotremove adjustable release, and unset/disabled IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioprio.h -->
# sources/distributed-fs/ceph-client/include/linux/ioprio.h

Purpose: This header defines kernel helpers for deriving and validating block I/O priority values for tasks.

Important APIs, types, and functions: It imports UAPI priority encoding, defines `IOPRIO_DEFAULT`, `ioprio_valid`, `task_nice_ioprio`, `task_nice_ioclass`, `__get_task_ioprio`, `get_current_ioprio`, `set_task_ioprio`, and `ioprio_check_cap`.

Control flow: If a task has an `io_context` with an explicit class, `__get_task_ioprio` returns it. Otherwise it derives best-effort/idle/realtime class from scheduler policy and derives priority from nice value. For non-current tasks, block builds assert `task_lock` via `alloc_lock`. Non-block builds return defaults or `-ENOTBLK`.

State and persistence: Explicit priority is stored in the task's `io_context`. Derived priorities are computed on demand from task scheduling state.

Dependencies and integration points: Integrates with scheduler policy, realtime/deadline detection, block I/O context, and UAPI ioprio encoding.

Risks: Callers reading another task's priority must hold the expected task lock to keep `io_context` stable. Class validation rejects `IOPRIO_CLASS_NONE` as an explicit class. Non-block configurations cannot enforce or set real I/O priority.

Test signals: Test explicit and derived priority, idle and RT/DL policies, nice-to-priority mapping, capability checks, concurrent task priority reads under lockdep, and `CONFIG_BLOCK` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioprio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioremap.h -->
# sources/distributed-fs/ceph-client/include/linux/ioremap.h

Purpose: This header provides a helper to identify whether an address lies in the architecture's ioremap virtual address area.

Important APIs, types, and functions: `is_ioremap_addr(const void *x)` strips KASAN pointer tags with `kasan_reset_tag` and compares against `IOREMAP_START` and `IOREMAP_END`. If the architecture does not define them, they default to `VMALLOC_START` and `VMALLOC_END` when I/O memory or generic ioremap support is enabled.

Control flow: Enabled configurations perform a range check; unsupported configurations always return false.

State and persistence: No state is stored. The function depends on compile-time address range constants.

Dependencies and integration points: Depends on KASAN tag handling, architecture page table/vmalloc definitions, and generic ioremap support. Used by debug, memory-management, or sanitizer code that must classify virtual addresses.

Risks: Some architectures may use ioremap space outside generic vmalloc defaults and must override the range. Tagged pointers must be reset before comparison. False classification can misroute memory handling or diagnostics.

Test signals: Build on generic and arch-overridden ioremap ranges, KASAN tagged pointer checks, boundary addresses at start/end, and disabled `CONFIG_HAS_IOMEM`/`CONFIG_GENERIC_IOREMAP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ioremap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iosys-map.h -->
# sources/distributed-fs/ceph-client/include/linux/iosys-map.h

Purpose: This header defines `struct iosys_map`, an abstraction for code that can operate on either normal system memory or I/O memory through one typed handle.

Important APIs, types, and functions: `struct iosys_map` stores either `vaddr` or `vaddr_iomem` plus `is_iomem`. Initializers and setters include `IOSYS_MAP_INIT_VADDR`, `IOSYS_MAP_INIT_VADDR_IOMEM`, `IOSYS_MAP_INIT_OFFSET`, `iosys_map_set_vaddr`, and `iosys_map_set_vaddr_iomem`. Helpers cover equality/null checks, clear, increment, memcpy to/from, memset, typed read/write, and struct-field read/write.

Control flow: Every helper branches on `is_iomem` to choose normal memory operations (`memcpy`, `READ_ONCE`, `WRITE_ONCE`) or I/O operations (`memcpy_toio`, `readb/readw/readl/readq`, `write*`, `memset_io`). Offset initializers make shallow copies before incrementing.

State and persistence: The map is a lightweight caller-owned value. Clearing zeros it and returns it to NULL system-memory state. It does not manage allocation or mapping lifetime.

Dependencies and integration points: Depends on compiler types, `linux/io.h`, and string helpers. Used by DRM/dma-buf and drivers that pass buffers without exposing whether they live in system or MMIO memory.

Risks: Direct field access is discouraged because `is_iomem` must match the active pointer. Typed read/write only supports u8/u16/u32/u64 and may be unsafe for unaligned packed fields on strict architectures. Pointer arithmetic on `__iomem` is intentionally encapsulated here.

Test signals: Test system and I/O paths for copy, memset, increment, equality, NULL, typed access, field access, 32-bit u64 fallback, and offset initializer independence from the source map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iosys-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iov_iter.h -->
# sources/distributed-fs/ceph-client/include/linux/iov_iter.h

Purpose: This header provides low-level iteration helpers that advance `struct iov_iter` across user buffers, iovecs, kvecs, bvecs, folio queues, xarrays, and discard iterators.

Important APIs, types, and functions: Callback types are `iov_step_f` for kernel addresses and `iov_ustep_f` for user addresses. Per-kind helpers are `iterate_ubuf`, `iterate_iovec`, `iterate_kvec`, `iterate_bvec`, `iterate_folioq`, `iterate_xarray`, and `iterate_discard`. Public dispatchers are `iterate_and_advance`, `iterate_and_advance2`, and `iterate_and_advance_kernel`.

Control flow: Dispatch clamps length to `iter->count`, skips zero-length work, selects the iterator kind, maps pages/folios locally where needed, calls a step function with segment base/progress/length, advances iterator offsets and segment pointers by consumed bytes, and stops early if the step reports remaining bytes.

State and persistence: The iterator is mutated in place: `count`, `iov_offset`, segment pointer, segment count, folio queue slot, or xarray offset are advanced. Temporary kmap mappings are created and released per page-sized chunk.

Dependencies and integration points: Depends on UIO, bvecs, folio queues, xarray/RCU, kmap-local APIs, and copy/checksum consumers that implement step callbacks.

Risks: User iterators pass faultable `__user` pointers without pinning. Step callbacks must return unprocessed bytes, not processed bytes. Xarray iteration runs under RCU and rejects value/hugetlb entries with warnings. Kernel-only dispatcher must not receive UBUF/IOVEC.

Test signals: Cover partial consumption, segment boundary advancement, zero-length segments, bvec page splitting, folio queue extension, xarray gaps/retries, discard iterators, user fault handling by callbacks, and count/offset consistency after early stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iov_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iova.h -->
# sources/distributed-fs/ceph-client/include/linux/iova.h

Purpose: This header defines IOVA range and domain structures plus allocation APIs for managing I/O virtual address PFN ranges, typically for IOMMU DMA.

Important APIs, types, and functions: `struct iova` stores an rbtree node and inclusive PFN low/high range. `struct iova_domain` stores the rbtree lock/root, cached allocation nodes, granule, start and 32-bit PFN limits, last failed 32-bit size, anchor, rcaches, and CPU hotplug node. Helpers compute size, shift, mask, offset, alignment, DMA address, and PFN. APIs include cache get/put, reserve/find/free, fast alloc/free, domain init, rcache init, and domain teardown.

Control flow: Enabled `CONFIG_IOMMU_IOVA` builds allocate and free PFN ranges from a domain rbtree, with fast paths using per-CPU rcaches. Disabled builds provide NULL/zero/no-op stubs. Address conversion shifts PFNs by the domain granule shift.

State and persistence: IOVA allocations persist as rbtree nodes until freed. The domain tracks cached search nodes and rcache state across allocations, plus CPU hotplug cleanup linkage.

Dependencies and integration points: Depends on rbtree, DMA mapping types, spinlocks, IOMMU DMA code, and CPU hotplug for rcache maintenance.

Risks: PFN ranges are inclusive, so size/free calculations must match allocation size. Granule must be a power-of-two for `__ffs`, mask, and alignment helpers. Fast alloc/free require correct rcache flushing to avoid stale or leaked IOVAs. Disabled stubs can hide missing config support.

Test signals: Test aligned and unaligned sizes, 32-bit limit behavior, reserve conflicts, find/free, fast rcache reuse and flush, domain teardown, CPU hotplug rcache drain, and disabled-config fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iova.h -->
