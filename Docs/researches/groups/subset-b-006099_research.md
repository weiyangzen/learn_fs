# Research: subset-b-006099

Grouped research for kernel library files under `sources/distributed-fs/ceph-client/lib`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iomap.c -->
# sources/distributed-fs/ceph-client/lib/iomap.c

Purpose: provides the generic default implementation of the Linux `ioread*()`, `iowrite*()`, repeated I/O, I/O-port mapping, and PCI unmap helpers when an architecture does not provide its own version. The key abstraction is that a `void __iomem *` cookie may represent either MMIO or encoded PIO; `IO_COND()` decodes low cookie values as PIO and higher values as MMIO.

Important APIs: `ioread8/16/16be/32/32be`, 64-bit `__ioread64_*` variants on 64-bit builds, `iowrite8/16/16be/32/32be`, 64-bit `__iowrite64_*`, `ioread*_rep`, `iowrite*_rep`, `ioport_map`, `ioport_unmap`, and `pci_iounmap`. Internal helpers include PIO big-endian fallbacks, split-order 64-bit PIO reads/writes, raw MMIO repeated access loops, and `bad_io_access()` warning throttling.

Control flow: each scalar access calls `IO_COND()`, which either executes PIO instructions (`inb`, `outw`, etc.), MMIO accessors (`readl`, `writeq`, etc.), or emits a bounded warning and returns all-ones for bad reads. Repeated accessors use string I/O for PIO and raw loops for MMIO. Mapping encodes I/O ports as `port + PIO_OFFSET`; unmapping is a no-op for PIO and calls `iounmap()` for MMIO in PCI builds.

State and persistence: state is limited to the static warning counter in `bad_io_access()`. KMSAN integration marks hardware-read data initialized and checks data being written to devices.

Dependencies and integration: depends on `linux/io.h`, PCI support, KMSAN helpers, endian byte swaps, and architecture-provided overrides via preprocessor guards. It is exported for drivers and bus code.

Risks: incorrect cookie ranges can misclassify PIO/MMIO; repeated raw MMIO deliberately lacks barriers and byte-order conversion; 64-bit split access ordering must match device semantics; KMSAN count arithmetic must match element width.

Test signals: build coverage across `CONFIG_64BIT`, `CONFIG_HAS_IOPORT_MAP`, and `CONFIG_PCI`; driver smoke tests for PIO/MMIO devices; KMSAN checks for initialized reads and uninitialized writes; sparse `__iomem` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iomap_copy.c -->
# sources/distributed-fs/ceph-client/lib/iomap_copy.c

Purpose: supplies generic raw copy helpers between normal memory and MMIO address space, in fixed-width units, for architectures that do not override them.

Important APIs: `__iowrite32_copy()` writes 32-bit quantities to MMIO; `__ioread32_copy()` reads 32-bit quantities from MMIO; `__iowrite64_copy()` writes 64-bit quantities on 64-bit builds or delegates to the 32-bit copy helper on 32-bit builds. All are GPL-exported where compiled.

Control flow: each helper casts source and destination to unit pointers, computes an end pointer from `count`, and loops with `__raw_writel`, `__raw_readl`, or `__raw_writeq`. No byte swapping, ordering barrier, or alignment repair is performed.

State and persistence: no persistent state. Progress exists only in local source/destination pointers.

Dependencies and integration: depends on `linux/io.h` raw MMIO accessors and export infrastructure. It backs driver helpers that need fast bulk register/window access while leaving ordering to callers.

Risks: callers must pass correctly aligned buffers and counts in units, not bytes. Raw access means no endian conversion and no memory barrier, so device protocols that need ordering must add barriers externally. The 32-bit fallback for 64-bit writes doubles the 32-bit count, which assumes the device accepts equivalent 32-bit sequencing.

Test signals: compile on 32-bit and 64-bit; architecture override coverage; driver tests that compare expected FIFO/window contents; sparse `__iomem` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iomap_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iomem_copy.c -->
# sources/distributed-fs/ceph-client/lib/iomem_copy.c

Purpose: provides generic byte/word optimized implementations of `memset_io()`, `memcpy_fromio()`, and `memcpy_toio()` when an architecture lacks custom I/O-memory bulk operations.

Important APIs: `memset_io()` fills an MMIO range with a repeated byte value; `memcpy_fromio()` copies from MMIO to RAM; `memcpy_toio()` copies from RAM to MMIO. All are conditionally compiled behind `#ifndef` guards and exported.

Control flow: each routine handles unaligned leading bytes until the I/O address is machine-word aligned, processes full machine words using `__raw_readl/readq` or `__raw_writel/writeq`, then handles trailing bytes. RAM-side unaligned word access uses `get_unaligned()`/`put_unaligned()`.

State and persistence: no persistent state; only pointer/count advancement. The target I/O device state may change as a direct side effect of raw writes.

Dependencies and integration: depends on `linux/io.h`, alignment helpers, unaligned access helpers, and `CONFIG_64BIT` selection. This is a low-level fallback for drivers and subsystems doing memory-like operations on I/O mappings.

Risks: raw accessors provide no implicit barriers or endian conversion. Alignment is only guaranteed for the I/O-side pointer, while RAM-side unaligned helpers must be correct for the architecture. Devices with register side effects may not tolerate bulk reads/writes that look like memory copies.

Test signals: architecture builds with and without overrides; MMIO test devices or emulators validating byte-exact copies; static analysis for `__iomem` annotations and count underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iomem_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iommu-helper.c -->
# sources/distributed-fs/ceph-client/lib/iommu-helper.c

Purpose: implements `iommu_area_alloc()`, a bitmap-based allocator for IOMMU aperture ranges with alignment and boundary-span constraints.

Important APIs: `iommu_area_alloc(map, size, start, nr, shift, boundary_size, align_mask)` searches the bitmap for `nr` zero bits starting at `start`, aligned by `align_mask`, rejects candidates that span an IOMMU boundary, sets the selected bits, and returns the index or `-1`.

Control flow: the function subtracts one from `size` to exclude the limit, calls `bitmap_find_next_zero_area()`, checks `iommu_is_span_boundary()`, advances `start` to the next boundary-aligned candidate on conflict, and retries. On success it mutates the bitmap with `bitmap_set()`.

State and persistence: the caller-owned bitmap is the persistent allocation state. There is no internal locking, so synchronization belongs to the caller.

Dependencies and integration: depends on bitmap helpers and the IOMMU helper header. It integrates with IOMMU free-area managers that need boundary-safe DMA/I/O virtual address allocation.

Risks: `size -= 1` assumes nonzero size; callers must serialize concurrent allocation/free; wrong `shift` or `boundary_size` can allow boundary crossings or waste address space; returning `-1` through an unsigned long requires callers to compare appropriately.

Test signals: bitmap allocator unit tests for alignment, exact-boundary, near-limit, full-map, and concurrent caller locking assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iommu-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iov_iter.c -->
# sources/distributed-fs/ceph-client/lib/iov_iter.c

Purpose: implements the core `struct iov_iter` data-movement, import, fault-in, page extraction, and state-advance helpers used by VFS, networking, block, DAX, splice, and filesystem paths to treat user iovecs, kernel vecs, bvecs, xarrays, folio queues, ubufs, and discard sinks uniformly.

Important APIs: iterator initialization (`iov_iter_init`, `iov_iter_kvec`, `iov_iter_bvec`, `iov_iter_xarray`, `iov_iter_folio_queue`, `iov_iter_discard`, `import_iovec`, `import_ubuf`), data movement (`_copy_to_iter`, `_copy_from_iter`, `_copy_from_iter_nocache`, `_copy_from_iter_flushcache`, `_copy_mc_to_iter`, `copy_page_to_iter`, `copy_page_from_iter`, `copy_folio_from_iter_atomic`, `iov_iter_zero`), positioning (`iov_iter_advance`, `iov_iter_revert`, `iov_iter_restore`, `iov_iter_single_seg_count`), layout (`iov_iter_alignment`, `iov_iter_gap_alignment`, `iov_iter_npages`), duplication (`dup_iter`), and page extraction (`iov_iter_get_pages2`, `iov_iter_get_pages_alloc2`, `iov_iter_extract_pages`, `iov_iter_extract_bvecs`).

Control flow: copy helpers validate transfer direction through `data_source`, invoke `might_fault()` for user-backed iterators, and delegate to `iterate_and_advance()` with user-copy or memcpy callbacks. Advance/revert update `count`, `iov_offset`, segment pointers, xarray position, or folio-queue slot according to iterator type. Import paths copy user `iovec` arrays, validate lengths and `access_ok()`, cap total length to `MAX_RW_COUNT`, and optimize a single segment as `ITER_UBUF`. Page-get/extract paths select user GUP/pinning, bvec page references, folio queue walking, xarray RCU lookup, or kvec virtual-to-page conversion.

State and persistence: the iterator itself is mutable cursor state: count, offset, current segment pointer, nr_segs, type, nofault flag, and backing object. Page extraction may acquire user pins or page refs that callers must release according to `iov_iter_extract_will_pin()`. Duplicated vectors allocate independent segment arrays.

Dependencies and integration: depends on user access, fault injection, GUP/pinning, highmem kmap, folios, xarray, bvec, vmalloc, scatterlist, compat ABI, and instrumentation hooks. It is a high fan-out kernel API and is directly relevant to distributed filesystem clients because networked read/write paths commonly copy to and from iterators.

Risks: direction inversions return zero after warnings; partial user-copy and machine-check paths can advance only part of an iterator; revert is illegal past the start for ubuf/xarray and can BUG; missing unpin/ref cleanup leaks pins; xarray/folio queue callers must stabilize pages externally; kvec extraction assumes virtual addresses can be mapped to pages; filter/cap logic must prevent overflow and negative lengths.

Test signals: usercopy fault injection, compat iovec import tests, DAX copy_mc/flushcache coverage, bvec/xarray/folioq extraction tests, pin accounting, short-copy cases, `MAX_RW_COUNT` boundary tests, and filesystem/network integration exercising iterator save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/iov_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/irq_poll.c -->
# sources/distributed-fs/ceph-client/lib/irq_poll.c

Purpose: implements IRQ polling infrastructure for block-layer style completion polling, analogous to NAPI, using a per-CPU pending list and `IRQ_POLL_SOFTIRQ`.

Important APIs: `irq_poll_init()`, `irq_poll_sched()`, `irq_poll_complete()`, `irq_poll_disable()`, and `irq_poll_enable()`. Internal helpers include `irq_poll_softirq()`, `__irq_poll_complete()`, CPU hotplug migration, and setup via `subsys_initcall`.

Control flow: scheduling checks disabled and scheduled bits, appends the poll object to the current CPU list with interrupts disabled, and raises the softirq. The softirq loops while budget and time remain, invokes `iop->poll(iop, weight)` with interrupts enabled, subtracts work from global budget, and either completes disabled items or rotates still-busy items to the tail. CPU-dead handling splices a dead CPU list into the current CPU and raises the softirq.

State and persistence: state is in `struct irq_poll` bits (`IRQ_POLL_F_SCHED`, `IRQ_POLL_F_DISABLE`), the per-CPU `blk_cpu_iopoll` lists, and the static budget. No persistent storage.

Dependencies and integration: depends on softirq, CPU hotplug, local IRQ control, bitops, and driver-supplied poll callbacks. Block drivers use it to defer interrupt completion work.

Risks: callbacks must obey ownership rules when consuming a full weight; disable spins with sleep until scheduled state is cleared; wrong list manipulation under interrupt state can corrupt per-CPU lists; long callbacks can exhaust softirq budget and require rearming.

Test signals: block driver polling tests, CPU hotplug stress, lockdep/softirq diagnostics, budget exhaustion behavior, and disable/enable races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/irq_poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/irq_regs.c -->
# sources/distributed-fs/ceph-client/lib/irq_regs.c

Purpose: provides the generic per-CPU saved IRQ register pointer storage for architectures that do not define their own IRQ register handling.

Important APIs/types: defines and exports per-CPU `struct pt_regs *__irq_regs` unless `ARCH_HAS_OWN_IRQ_REGS` is set.

Control flow: no runtime functions; compilation creates per-CPU storage and export metadata.

State and persistence: persistent per-CPU pointer state tracks the current interrupt register frame as maintained by architecture/common IRQ code.

Dependencies and integration: depends on percpu support, export macros, and `asm/irq_regs.h`. Consumers use the exported per-CPU symbol to retrieve or set IRQ context registers.

Risks: only suitable when architecture semantics match the generic pointer model; incorrect updates elsewhere can expose stale register context.

Test signals: architecture build coverage without `ARCH_HAS_OWN_IRQ_REGS`; interrupt entry/exit tracing and oops diagnostics that rely on current IRQ regs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/irq_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/is_single_threaded.c -->
# sources/distributed-fs/ceph-client/lib/is_single_threaded.c

Purpose: implements `current_is_single_threaded()`, which decides whether the current task is the only live user of its `mm_struct` across the system.

Important API: `current_is_single_threaded()` returns false if the thread group has multiple live threads, true if `mm_users == 1`, otherwise scans processes and threads for another task sharing the same `mm`.

Control flow: first checks `signal->live`, then fast-paths `mm_users == 1`, then performs an RCU-protected walk over all processes. It skips kernel threads and the current group leader, scans threads for `t->mm == mm`, and uses `smp_rmb()` when seeing `NULL` mm to order against concurrent CLONE_VM/exiting transitions.

State and persistence: reads scheduler/task/mm reference counters and task lists; no mutation.

Dependencies and integration: depends on scheduler signal/task/mm headers, RCU task traversal, and memory barriers. Security and process-management code can use it before operations requiring private address-space ownership.

Risks: correctness depends on subtle task-list and mm lifetime ordering; the full process scan is expensive; `current->mm` must be valid for callers; racing clone/exit paths rely on the documented barrier.

Test signals: fork/clone/thread stress tests, SELinux or credential-changing paths that require single-thread checks, and lockdep/RCU validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/is_single_threaded.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kasprintf.c -->
# sources/distributed-fs/ceph-client/lib/kasprintf.c

Purpose: implements kernel allocation-backed printf helpers and a const-string optimization variant.

Important APIs: `kvasprintf()`, `kvasprintf_const()`, and `kasprintf()`. `kvasprintf()` computes formatted length, allocates with `kmalloc_track_caller()`, formats into the buffer, and warns if two `vsnprintf()` passes disagree. `kvasprintf_const()` avoids allocation or copying when the format is literal/no-percent or exactly `%s` and the string can be represented by `kstrdup_const()`.

Control flow: `kasprintf()` wraps varargs around `kvasprintf()`. `kvasprintf()` uses `va_copy()` for the sizing pass and the original `va_list` for the formatting pass. `kvasprintf_const()` may consume a string argument when handling `%s`.

State and persistence: returns allocated or const-managed string memory owned by the caller; `kvasprintf_const()` results must be released with `kfree_const()`.

Dependencies and integration: depends on slab allocation, string helpers, and export macros. Kobject naming uses `kvasprintf_const()` to avoid unnecessary allocations for static names.

Risks: callers must use the correct free routine for const-optimized results; formatting side effects or unstable arguments can trigger mismatched `vsnprintf()` sizes; allocation failure returns NULL.

Test signals: allocation failure injection, `%s` rodata optimization checks, and callers validating `kfree_const()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kasprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kfifo.c -->
# sources/distributed-fs/ceph-client/lib/kfifo.c

Purpose: implements the generic kernel FIFO ring-buffer backend for element streams, record streams, user copies, and DMA scatterlist preparation.

Important APIs: allocation/init/free (`__kfifo_alloc_node`, `__kfifo_init`, `__kfifo_free`), stream I/O (`__kfifo_in`, `__kfifo_out_peek`, `__kfifo_out`, `__kfifo_out_linear`), user I/O (`__kfifo_from_user`, `__kfifo_to_user`), DMA preparation (`__kfifo_dma_in_prepare`, `__kfifo_dma_out_prepare`), record helpers (`__kfifo_max_r`, `__kfifo_len_r`, `__kfifo_in_r`, `__kfifo_out_peek_r`, `__kfifo_out_r`, `__kfifo_skip_r`, user and DMA record variants).

Control flow: sizes are normalized to powers of two so `in` and `out` can wrap naturally and indices are masked. Copy helpers split operations at the end of the ring and wrap to offset zero. Record mode stores a one- or two-byte length prefix at `in`, copies payload after the prefix, and advances by prefix plus payload. DMA helpers populate up to two scatterlist entries for the contiguous tail and wrapped head.

State and persistence: persistent state lives in caller-visible `struct __kfifo`: `data`, `mask`, `esize`, `in`, and `out`. Memory barriers ensure data visibility before publishing `in` or after reading before advancing `out`; no locks are internal.

Dependencies and integration: depends on slab allocation, user access, scatterlist, DMA mapping constants, log2 helpers, and exported symbols. Used by drivers and subsystems needing simple lockless single-reader/single-writer buffers.

Risks: caller must provide synchronization beyond supported patterns; element size conversion affects byte counts and partial copy accounting; record length prefix limits payload size; DMA finish must match prepared length; unbounded `in - out` arithmetic relies on unsigned wrap discipline.

Test signals: ring wrap tests, record prefix boundary tests, partial user-copy fault injection, DMA scatterlist offset checks, and concurrent producer/consumer tests under the documented locking model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kfifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/klist.c -->
# sources/distributed-fs/ceph-client/lib/klist.c

Purpose: implements `klist`, a refcounted and lock-protected list abstraction safe for iteration while nodes are being removed.

Important APIs/types: `struct klist`, `struct klist_node`, `struct klist_iter`, `klist_init`, add helpers (`klist_add_head`, `klist_add_tail`, `klist_add_behind`, `klist_add_before`), removal (`klist_del`, `klist_remove`), attachment test, iterator setup/exit, and directional iteration (`klist_next`, `klist_prev`). Internal low bit `KNODE_DEAD` marks nodes logically dead.

Control flow: add initializes the node kref, owner klist pointer, and optional embedder `get()` ref, then inserts under the klist spinlock. Iteration drops the previous node ref and takes the next/prev live node ref under lock, skipping dead nodes. `klist_del()` marks dead and drops a ref; actual list deletion happens when the kref reaches zero. `klist_remove()` installs a waiter and sleeps until release wakes it.

State and persistence: list membership, node kref counts, dead bit, and global removal waiter list are persistent kernel state until callers remove nodes and exit iterators.

Dependencies and integration: depends on list, kref, spinlocks, scheduler sleep/wake, and exported GPL symbols. Device core uses this pattern for safe lists of devices/drivers.

Risks: callers must call `klist_iter_exit()` to drop held refs; embedding object get/put callbacks must be valid outside the lock; removal waits uninterruptibly; low-bit pointer tagging requires aligned klist pointers; double kill and uninitialized nodes warn.

Test signals: concurrent iteration/removal stress, waiter wake tests, lockdep, reference leak detection, and device core hotplug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/klist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kobject.c -->
# sources/distributed-fs/ceph-client/lib/kobject.c

Purpose: implements core kobject and kset lifecycle management: naming, sysfs directory creation/removal, refcounting, kset membership, namespace hooks, sysfs attribute operations, and dynamic object helpers.

Important APIs: namespace/ownership (`kobject_namespace`, `kobject_get_ownership`, `kobj_ns_*`), path/name (`kobject_get_path`, `kobject_set_name`), lifecycle (`kobject_init`, `kobject_add`, `kobject_init_and_add`, `kobject_del`, `kobject_get`, `kobject_get_unless_zero`, `kobject_put`, `kobject_create_and_add`), mutation (`kobject_rename`, `kobject_move`), ksets (`kset_init`, `kset_register`, `kset_unregister`, `kset_find_obj`, `kset_create_and_add`), and `kobj_sysfs_ops`.

Control flow: initialization sets kref/list/state flags. Add sets the name, resolves parent or kset parent, joins the kset list, creates the sysfs directory and default groups, enables namespace filtering if needed, and marks `state_in_sysfs`. Delete removes default groups, auto-emits remove uevents when necessary, removes sysfs, releases sysfs/kset/parent references, and clears state. Put triggers cleanup via kref release, optionally delayed under debug config.

State and persistence: persistent state is the kobject name, kref, parent/kset links, sysfs node reference, state flags for sysfs and uevents, kset lists, and namespace ops table protected by a spinlock.

Dependencies and integration: integrates with sysfs/kernfs, kref, ksets, uevents, namespace operations, ownership callbacks, and dynamic allocation. It is a central object model for devices, buses, and kernel subsystems.

Risks: incorrect lifetime handling leaks or use-after-frees kobjects; missing release callbacks are flagged as broken; rename/move callers must serialize and avoid name collisions; auto cleanup uevents can surprise callers; namespace ops registration is global and one-shot by type; path building retries on concurrent rename.

Test signals: sysfs registration/unregistration tests, kobject refcount debugging, uevent sequence tests, namespace mount/filter tests, duplicate-name failures, and fault injection for allocation/sysfs errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kobject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kobject_uevent.c -->
# sources/distributed-fs/ceph-client/lib/kobject_uevent.c

Purpose: implements userspace event delivery for kobjects through netlink and optional usermode helper execution, including synthetic uevent parsing.

Important APIs/state: global `uevent_seqnum`, optional `uevent_helper`, `kobject_synth_uevent()`, `kobject_uevent_env()`, `kobject_uevent()`, `add_uevent_var()`, per-network-namespace netlink socket setup, and helper sysctl registration. The action string table maps `enum kobject_action` to wire strings.

Control flow: `kobject_uevent_env()` locates the nearest kset, applies suppress/filter/name callbacks, allocates an environment, adds `ACTION`, `DEVPATH`, `SUBSYSTEM`, caller variables, and kset variables, marks add/remove state flags, removes `MODALIAS` for unbind, appends a sequence number, broadcasts to the correct netlink namespace, then optionally invokes the configured helper. Synthetic uevents parse an action, optional UUID, and alphanumeric `KEY=VALUE` arguments into environment variables.

State and persistence: persistent state includes sequence counter, per-net uevent socket list protected by a mutex, per-kobject add/remove sent flags, and optional helper path. Temporary `kobj_uevent_env` buffers hold argv/envp data.

Dependencies and integration: depends on kobject/kset operations, netlink, network namespaces, user namespaces, kmod usermode helpers, sysctl, UUID/ctype parsing, and skb allocation. Device and subsystem code call it after object lifecycle changes.

Risks: environment buffer and envp count limits can return `-ENOMEM`; missing kset or subsystem drops events; net namespace tagging must match kobject namespace ops; helper is filtered for non-init namespaces; synthetic input validation is intentionally strict; netlink `ENOBUFS` is ignored for userspace handling.

Test signals: uevent listener tests, synthetic uevent parser validation, namespace-scoped netlink delivery, helper path/sysctl tests when enabled, add/remove auto-cleanup behavior, and buffer-limit fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kobject_uevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kstrtox.c -->
# sources/distributed-fs/ceph-client/lib/kstrtox.c

Purpose: implements strict string-to-integer and string-to-boolean conversion helpers with overflow detection, base autodetection, and user-copy wrappers.

Important APIs: `_parse_integer_fixup_radix`, `_parse_integer_limit`, `_parse_integer`, `kstrtoull`, `kstrtoll`, `_kstrtoul`, `_kstrtol`, `kstrtouint`, `kstrtoint`, `kstrtou16/s16/u8/s8`, `kstrtobool`, `kstrtobool_from_user`, and macro-generated `*_from_user` integer wrappers.

Control flow: radix fixup chooses 16 for `0x`, 8 for leading zero, or 10 otherwise, then skips the hex prefix. `_parse_integer_limit()` consumes valid digits up to `max_chars`, sets an overflow bit on range overflow, and returns consumed length. Typed wrappers reject no digits, trailing junk except one newline, overflow, sign/type mismatch, and out-of-range narrowing. Boolean parsing accepts common one-character true/false prefixes and `on`/`off`.

State and persistence: no persistent state. Results are only written on successful conversion, preserving caller output on errors.

Dependencies and integration: depends on ctype, errno, math64 division, user access, and exported symbols. Widely used for sysfs, procfs, module parameters, and kernel parsers.

Risks: base support is documented up to 16; unsigned helpers reject minus signs; bool parsing checks only enough characters to distinguish accepted prefixes; from-user wrappers truncate input to fixed local buffers sized for binary representation; callers must check return codes.

Test signals: parser unit tests for base autodetection, signs, newline allowance, overflow boundaries for every type, invalid trailing bytes, user-copy faults, and bool synonyms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kstrtox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kstrtox.h -->
# sources/distributed-fs/ceph-client/lib/kstrtox.h

Purpose: private header for `kstrtox.c` integer parsing internals.

Important declarations: `KSTRTOX_OVERFLOW` high-bit flag, `_parse_integer_fixup_radix()`, `_parse_integer_limit()`, and `_parse_integer()`.

Control flow: not executable itself; it exposes the internal parser contract used by the implementation and possible local tests.

State and persistence: no state.

Dependencies and integration: included by `lib/kstrtox.c`; relies on standard kernel integer and size types from including context.

Risks: because it is an internal header, widening its use can couple external code to low-level return encodings such as consumed-character count ORed with overflow.

Test signals: compile coverage of `kstrtox.c`; direct tests of parser internals if KUnit or lib tests expose them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kstrtox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/Kconfig -->
# sources/distributed-fs/ceph-client/lib/kunit/Kconfig

Purpose: defines build-time configuration for KUnit core, debugfs integration, self-tests, examples, autorun/filter defaults, timeouts, and UML PCI support.

Important symbols: `KUNIT`, `KUNIT_DEBUGFS`, `KUNIT_FAULT_TEST`, `KUNIT_TEST`, `KUNIT_EXAMPLE_TEST`, `KUNIT_ALL_TESTS`, `KUNIT_DEFAULT_ENABLED`, `KUNIT_AUTORUN_ENABLED`, `KUNIT_DEFAULT_FILTER_GLOB`, `KUNIT_DEFAULT_FILTER`, `KUNIT_DEFAULT_FILTER_ACTION`, `KUNIT_DEFAULT_TIMEOUT`, and `KUNIT_UML_PCI`.

Control flow: Kconfig dependencies and defaults determine which KUnit objects compile and how runtime module/core parameters default. `KUNIT_ALL_TESTS` fans into individual tests when dependencies are satisfied. Debugfs depends on `DEBUG_FS`; fault tests avoid UML and default off when panic-on-oops would make them disruptive.

State and persistence: persistent kernel configuration state influences compiled code and default runtime parameters.

Dependencies and integration: integrates with the kernel Kconfig system, UML PCI selection, debugfs availability, and KUnit Makefile object selection.

Risks: enabling all tests in production-like builds can run boot-time tests unexpectedly; default autorun/filter values alter boot behavior; fault tests intentionally produce BUG-like traces.

Test signals: `allnoconfig`, KUnit-enabled, UML, module, and built-in config matrix builds; validation that default filter strings propagate into executor parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/Makefile -->
# sources/distributed-fs/ceph-client/lib/kunit/Makefile

Purpose: maps KUnit configuration symbols to object files for the core framework, hooks, self-tests, and examples.

Important targets: `kunit.o` aggregates `test.o`, `resource.o`, `user_alloc.o`, `static_stub.o`, `string-stream.o`, `assert.o`, `try-catch.o`, `executor.o`, `attributes.o`, `device.o`, and `platform.o`; `debugfs.o` is conditional; `hooks.o` is built-in whenever KUnit is enabled; self-tests include `kunit-test.o`, `platform-test.o`, built-in-only `string-stream-test.o` and `assert_test.o`; examples build from `kunit-example-test.o`.

Control flow: standard kbuild `obj-$(CONFIG_...)` and `kunit-objs` aggregation select objects according to config values.

State and persistence: no runtime state; build artifact composition is the persistent effect.

Dependencies and integration: integrates Kconfig symbols with kbuild and ensures hook symbols exist even if KUnit itself is modular.

Risks: built-in-only test object constraints must match code assumptions; adding new KUnit core files requires updating the aggregate list; hook build rule must remain available for `test-bug` integration.

Test signals: built-in vs module builds, `CONFIG_KUNIT_DEBUGFS` matrix, `CONFIG_KUNIT_TEST=y/m`, and link checks for hook symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/assert.c -->
# sources/distributed-fs/ceph-client/lib/kunit/assert.c

Purpose: serializes KUnit expectation/assertion failures into `string_stream` output, including scalar, pointer, string, and memory comparison diagnostics.

Important APIs: `kunit_assert_prologue`, `kunit_fail_assert_format`, `kunit_unary_assert_format`, `kunit_ptr_not_err_assert_format`, `kunit_binary_assert_format`, `kunit_binary_ptr_assert_format`, `kunit_binary_str_assert_format`, `kunit_assert_hexdump`, and `kunit_mem_assert_format`. KUnit-visible helpers `is_literal`, `is_str_literal`, and `kunit_assert_print_msg` support concise output and tests.

Control flow: formatters downcast the base `struct kunit_assert` to a specific assertion type, emit a standardized message, optionally suppress redundant value lines when operands are literals, and append custom va_format messages. Memory assertions validate NULL sides first, then print two hexdumps marking differing bytes with angle brackets.

State and persistence: no persistent state; output accumulates in the caller-provided `string_stream`.

Dependencies and integration: depends on KUnit assert/test headers, visibility annotations, and `string-stream`. The KUnit macro layer calls these formatters for failed checks.

Risks: formatting must avoid misleading output when operand text is a literal; `is_literal()` allocates temporarily and can suppress output incorrectly only if string conversion matches exactly; hexdump size comes from the assertion and must be trustworthy.

Test signals: `assert_test.c` directly validates literals, prologue output, message appending, pointer/string/memory formatting, and hexdump markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/assert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/assert_test.c -->
# sources/distributed-fs/ceph-client/lib/kunit/assert_test.c

Purpose: KUnit self-test suite for assertion formatting helpers in `assert.c`.

Important APIs/tests: tests cover `is_literal`, `is_str_literal`, `kunit_assert_prologue`, `kunit_assert_print_msg`, unary, not-err pointer, binary integer, binary pointer, binary string, hexdump, and memory assertion formatting. Helpers include `get_str_from_stream()`, `verify_assert_print_msg()`, and `validate_assert()`.

Control flow: each test allocates a managed `string_stream`, invokes a formatter with synthetic assertion structures, extracts the stream text, and checks for expected substrings or absence of hexdump markers. Pointer tests render expected addresses with `%px` to remain architecture-length independent.

State and persistence: managed allocations are tied to the test context using KUnit actions and allocators. Static test buffers provide deterministic hexdump comparisons.

Dependencies and integration: depends on KUnit core, assertion internals exposed to KUnit, and `string-stream`. Registered as suite `kunit-assert`.

Risks: substring-based checks can miss ordering or exact formatting regressions; `%px` output may depend on pointer hashing settings, though both expected and actual use the same formatter style.

Test signals: the file itself is the test signal for assertion diagnostics; it runs when `CONFIG_KUNIT_TEST` is built-in according to the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/assert_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/attributes.c -->
# sources/distributed-fs/ceph-client/lib/kunit/attributes.c

Purpose: implements KUnit test and suite attributes, attribute printing, attribute filter parsing, and filtering of suite test cases by attributes.

Important APIs/types: internal `struct kunit_attr`, `kunit_attr_filter_name`, `kunit_print_attr`, `kunit_get_filter_count`, `kunit_next_attr_filter`, and `kunit_filter_attr_tests`. Supported attributes are `speed`, `module`, and `is_init`.

Control flow: attribute descriptors provide get/to-string/filter/default/print functions. Filters parse comma-separated expressions by locating an operator from `<`, `>`, `!`, or `=`, temporarily NUL-terminating the name, and returning a filter pointing into the mutable input string. Filtering copies the suite, allocates a new test-case array, evaluates default, suite, and case values, includes matching tests, or marks nonmatching tests skipped when action is `skip`.

State and persistence: static attribute descriptor table is immutable after init. Filtering allocates copied suites/test arrays and may mutate original test case status when skip action is used.

Dependencies and integration: depends on KUnit test and attributes headers, string comparison, logging, and suite iteration. Executor code chains glob filtering with these attribute filters.

Risks: filter parsing mutates the input string and requires writable storage; skip action mutates original `struct kunit_case` before copying; string filters only allow `=` and `!=`; empty filtered suites return NULL and must be treated as no match rather than allocation failure.

Test signals: executor self-tests cover filter count, parsing, attribute matching, empty results, and skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/debugfs.c -->
# sources/distributed-fs/ceph-client/lib/kunit/debugfs.c

Purpose: exposes KUnit suite logs and manual run triggers through debugfs under `/sys/kernel/debug/kunit/<suite>/`.

Important APIs: `kunit_debugfs_init`, `kunit_debugfs_cleanup`, `kunit_debugfs_create_suite`, and `kunit_debugfs_destroy_suite`. File operations back `results` and `run` files.

Control flow: initialization creates the root directory. Suite creation allocates suite and per-test `string_stream` logs, enables auto-newline behavior, creates a suite directory, adds read-only `results`, and adds writable `run` unless the suite uses init sections. Reading results emits KTAP headers, per-test logs, suite log, and final suite status. Writing `run` invokes `__kunit_test_suites_init()` for that suite.

State and persistence: persistent state includes `debugfs_rootdir`, suite debugfs dentries, suite/test log streams, and stored last-run output until destroyed or overwritten by another run.

Dependencies and integration: depends on debugfs, seq_file, KUnit core, test-bug hooks, and `string-stream`. Called by KUnit suite lifecycle code when `CONFIG_KUNIT_DEBUGFS` is enabled.

Risks: partial log allocation rolls back streams but debugfs creation errors are not deeply handled; manual rerun excludes init suites; concurrent reading and logging relies on `string_stream` locking; debugfs may be absent or disabled.

Test signals: manual debugfs run/read smoke tests, KTAP parser validation, suite destruction leak checks, and config-disabled inline stub coverage from `debugfs.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/debugfs.h -->
# sources/distributed-fs/ceph-client/lib/kunit/debugfs.h

Purpose: internal KUnit debugfs interface header with enabled declarations and disabled no-op stubs.

Important APIs: `kunit_debugfs_create_suite`, `kunit_debugfs_destroy_suite`, `kunit_debugfs_init`, and `kunit_debugfs_cleanup`.

Control flow: preprocessor selects real declarations under `CONFIG_KUNIT_DEBUGFS`; otherwise static inline no-op functions compile callers without conditional code.

State and persistence: no direct state.

Dependencies and integration: includes `kunit/test.h`; consumed by KUnit core and debugfs implementation.

Risks: no-op stubs mean callers must not rely on debugfs side effects when config is disabled.

Test signals: build matrix with `CONFIG_KUNIT_DEBUGFS=y/n` and link checks for callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/device-impl.h -->
# sources/distributed-fs/ceph-client/lib/kunit/device-impl.h

Purpose: internal header for KUnit fake-device bus lifecycle helpers.

Important APIs: declares `kunit_bus_init()` and `kunit_bus_shutdown()` for internal registration/unregistration of the KUnit bus.

Control flow: no runtime logic in the header; it exposes functions implemented in `device.c`.

State and persistence: no direct state.

Dependencies and integration: used by KUnit core/device code to set up and tear down the fake bus for test-managed devices.

Risks: internal-only functions should not become general API; callers must pair init/shutdown around the lifetime of KUnit device helpers.

Test signals: KUnit device tests and build coverage when KUnit is modular or built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/device-impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/device.c -->
# sources/distributed-fs/ceph-client/lib/kunit/device.c

Purpose: implements KUnit-managed fake devices and drivers on a dedicated `kunit` bus so tests can exercise driver-model code with automatic cleanup.

Important APIs/types: internal `struct kunit_device`, `kunit_bus_init`, `kunit_bus_shutdown`, `kunit_driver_create`, `kunit_device_register_with_driver`, `kunit_device_register`, and `kunit_device_unregister`. Action wrappers unregister devices and drivers through KUnit cleanup actions.

Control flow: bus init registers a root device and bus type. Driver creation allocates a managed driver, sets name/bus/owner, registers it, and adds a cleanup action. Device registration allocates a `kunit_device`, names it as `<test>.<name>`, sets release/bus/parent, registers it, sets a 32-bit DMA mask, and schedules unregister cleanup. The convenience device path creates both a driver and device and releases the driver action if device registration fails.

State and persistence: persistent state includes global `kunit_bus_device`, registered bus, registered fake devices/drivers, and per-test KUnit actions that own cleanup.

Dependencies and integration: depends on Linux driver core, DMA masks, KUnit resource/action APIs, and device helper headers.

Risks: bus init failure must clean up root device; early unregister must release both device and auto-created driver; driver name memory allocated with KUnit const helpers must be released on manual unregister; device lifetime depends on driver-core release callback.

Test signals: KUnit device tests in core test infrastructure, driver probe/remove tests, leak checks, and module unload path calling bus shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/executor.c -->
# sources/distributed-fs/ceph-client/lib/kunit/executor.c

Purpose: discovers, filters, lists, runs, and optionally shuts down after KUnit suites registered in linker sections.

Important APIs/state: module/core parameters `action`, `autorun`, `filter_glob`, `filter`, `filter_action`, and `kunit_shutdown`; getters for action/filter values; `kunit_filter_suites`, `kunit_free_suite_set`, `kunit_exec_run_tests`, `kunit_exec_list_tests`, `kunit_merge_suite_sets`, and built-in `kunit_run_all_tests`.

Control flow: glob filters are parsed into suite and optional test globs, then suites are copied with only matching test cases. Attribute filters from `attributes.c` are applied sequentially to copied suites. Built-in execution merges init and normal suite linker sections, marks init suites, checks `kunit_enabled()`, applies filters, then runs tests, lists tests, or lists tests with attributes based on `action`. Shutdown parameter can poweroff/halt/reboot after execution.

State and persistence: parameters persist as runtime configuration. Filtering allocates copied suite sets and may mark test cases skipped through attribute filtering. Init suite `is_init` flags are set in merged arrays.

Dependencies and integration: depends on linker-section suite arrays, glob matching, module parameters, KUnit core, attribute filtering, and reboot APIs.

Risks: filter strings must be writable for attribute parsing; empty filtered sets are valid; ownership of copied vs linker-section suite arrays differs and cleanup must match; unknown actions only log errors; shutdown behavior is powerful and must be explicit.

Test signals: `executor_test.c` covers glob parsing, suite/test filtering, empty sets, attribute filters, and skip action; boot-time KTAP output and `kunit.py` listing modes validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/executor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/executor_test.c -->
# sources/distributed-fs/ceph-client/lib/kunit/executor_test.c

Purpose: self-tests KUnit executor filtering and attribute-filter behavior.

Important tests/helpers: `parse_filter_test`, `filter_suites_test`, `filter_suites_test_glob_test`, `filter_suites_to_empty_test`, `parse_filter_attr_test`, `filter_attr_test`, `filter_attr_empty_test`, `filter_attr_skip_test`, plus fake suite allocation and suite-set cleanup helpers.

Control flow: tests create fake suites over dummy cases, invoke `kunit_filter_suites()` with glob or attribute filters, register cleanup with KUnit actions, and assert resulting suite/test counts, names, and skip status.

State and persistence: fake suites are KUnit-managed allocations; copied suite sets are freed through registered actions. Some tests use mutable local filter strings because parser mutates input.

Dependencies and integration: included directly by `executor.c` for built-in KUnit test builds and registered as suite `kunit_executor_test`.

Risks: fake cases only validate filtering metadata, not real execution; direct inclusion means static executor helpers are visible but can complicate build boundaries; expected skip behavior relies on mutation in attribute filtering.

Test signals: this file is the primary regression signal for executor filter semantics and empty-set handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/executor_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/hooks-impl.h -->
# sources/distributed-fs/ceph-client/lib/kunit/hooks-impl.h

Purpose: internal header that wires KUnit runtime hook implementations into the globally exported hook table used by code that may be built when KUnit is modular.

Important APIs: declarations for `__kunit_fail_current_test_impl()` and `__kunit_get_static_stub_address_impl()`, plus inline `kunit_install_hooks()` assigning them to `kunit_hooks.fail_current_test` and `kunit_hooks.get_static_stub_address`.

Control flow: callers invoke `kunit_install_hooks()` during KUnit initialization to populate function pointers.

State and persistence: mutates global `kunit_hooks` table declared in `hooks.c`.

Dependencies and integration: includes `kunit/test-bug.h`; integrates KUnit failure reporting and static stubbing hooks with code compiled outside the KUnit module.

Risks: hook table must be installed before users rely on it; stale pointers would be dangerous across module unload if not cleared elsewhere; declarations must match implementation signatures.

Test signals: static stub example tests, current-test failure hook tests, module/built-in KUnit build matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/hooks-impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/hooks.c -->
# sources/distributed-fs/ceph-client/lib/kunit/hooks.c

Purpose: provides built-in KUnit hook state even when KUnit core is built as a module.

Important APIs/state: defines and exports static key `kunit_running` and global `struct kunit_hooks_table kunit_hooks`.

Control flow: no active runtime logic; exported symbols are initialized statically and later manipulated by KUnit core/hook installation.

State and persistence: `kunit_running` is a static branch indicating active KUnit execution; `kunit_hooks` stores function pointers for failure and static stub callbacks.

Dependencies and integration: includes `kunit/test-bug.h`, uses static keys and export macros. Built through Makefile as built-in when KUnit is enabled.

Risks: consumers must tolerate NULL hook function pointers before installation; static branch state must be toggled consistently by core test execution.

Test signals: KUnit current-test failure tests, static stub tests, and build/link tests with modular KUnit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/kunit-example-test.c -->
# sources/distributed-fs/ceph-client/lib/kunit/kunit-example-test.c

Purpose: example KUnit suite demonstrating expectations/assertions, skipping, suite/test fixtures, static stubs, private test data, resources, parameterized tests, dynamic parameter arrays, slow-test attributes, and init-section suites.

Important APIs/patterns: `KUNIT_EXPECT_*`, `KUNIT_ASSERT_*`, `kunit_skip`, `kunit_mark_skipped`, `kunit_activate_static_stub`, `kunit_deactivate_static_stub`, `KUNIT_ARRAY_PARAM`, `KUNIT_CASE_PARAM`, `KUNIT_CASE_PARAM_WITH_INIT`, `kunit_alloc_resource`, `kunit_find_resource`, `kunit_put_resource`, `kunit_register_params_array`, `KUNIT_CASE_SLOW`, `kunit_test_suites`, and `kunit_test_init_section_suites`.

Control flow: the main `example` suite runs suite init/exit around per-test init/exit and several cases. Static stub tests redirect `add_one()` to `subtract_one()`. Parameterized tests iterate over static and dynamically generated arrays, optionally using parent test resources. An init-section suite tests `__init` code but keeps suite/case metadata in `__refdata` for debugfs result access.

State and persistence: test state lives in `struct kunit`, `test->priv`, managed allocations/resources, active static stubs, parameter arrays, and suite metadata. Most state is automatically cleaned by KUnit at test or parameterized-test teardown.

Dependencies and integration: depends on KUnit core and static stub support. It is built under `CONFIG_KUNIT_EXAMPLE_TEST` as documentation-through-code and a smoke test for many KUnit features.

Risks: example tests intentionally include skipped cases; `example_params_test()` skips non-power-of-two values and then divides by the value, relying on skip abort semantics for zero; static stubs must be deactivated; dynamic parameter allocation must be tied to the correct parent context.

Test signals: running the example suite validates broad KUnit API behavior, KTAP output for skip/slow/parameterized cases, static stubs, resources, and init-suite support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/kunit/kunit-example-test.c -->
