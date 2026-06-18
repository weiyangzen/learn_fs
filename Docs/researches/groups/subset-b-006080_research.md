# subset-b-006080 Research

Grouped source research for Linux kernel core library helpers and the CRC library subtree under `sources/distributed-fs/ceph-client/lib`. Each source file section preserves the source path in its title and is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bootconfig.c -->
# sources/distributed-fs/ceph-client/lib/bootconfig.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bootconfig.c` implements the Linux extra boot config parser and query API. It copies bootconfig text into init memory, tokenizes the ASCII key/value syntax in place, builds a compact `struct xbc_node` tree, and exposes lookup/iteration helpers for early boot consumers. The source was read as a complete 1009-line file for this report.

## Important APIs, Types, and Functions

Key public entry points are `xbc_init`, `_xbc_exit`, `xbc_get_info`, `xbc_root_node`, `xbc_node_index`, `xbc_node_get_parent`, `xbc_node_get_child`, `xbc_node_get_next`, `xbc_node_get_data`, `xbc_node_find_subkey`, `xbc_node_find_value`, `xbc_node_compose_key_after`, `xbc_node_find_next_leaf`, and `xbc_node_find_next_key_value`. When `CONFIG_BOOT_CONFIG_EMBED` is enabled, `xbc_get_embedded_bootconfig` exposes linker-provided embedded bootconfig data. Internal parser state is global `__initdata`: `xbc_nodes`, `xbc_node_num`, `xbc_data`, `xbc_data_size`, `last_parent`, `xbc_err_msg`, `xbc_err_pos`, `open_brace`, and `brace_index`.

## Control Flow

`xbc_init()` rejects duplicate initialization and invalid sizes, allocates `xbc_data` and the node array, copies and terminates the input, then calls `xbc_parse_tree()` followed by `xbc_verify_tree()`. `xbc_parse_tree()` repeatedly finds delimiters with `strpbrk()` and dispatches to key, key/value, open-brace, close-brace, comment, semicolon, and newline handlers. Key parsing splits dot-separated names through `__xbc_parse_keys()` and inserts or reuses nodes with `__xbc_add_key()`. Value parsing supports quoted strings, comments, `=`, `:=` overrides, `+=` array append, comma arrays, and brace-close after values. Lookup helpers descend by dotted path, leaf iteration walks depth-first, and key composition walks parents back to the requested root.

## State and Persistence Behavior

All parser output is kept in init-time global memory. The parser mutates its copy of the input by replacing delimiters with NUL terminators and storing node data as 16-bit offsets with an `XBC_VALUE` flag. `_xbc_exit()` frees both buffers through either memblock or libc shims, clears counts, and resets brace tracking. There is no file persistence; lifetime is the boot/init lifecycle unless the tools build uses the user-space allocation path.

## Dependencies and Integration Points

The file depends on `linux/bootconfig.h` limits and node helpers, kernel allocation via memblock under `__KERNEL__`, string/ctype helpers, `WARN_ON`, and the tools/bootconfig user-space test shim. Boot code and `/proc/bootconfig` style consumers integrate through the exported `xbc_*` query functions after early boot passes the appended or embedded bootconfig blob.

## Risks and Edge Cases

The parser is highly stateful and mutates `last_parent`, so malformed brace nesting, empty keys, array appends, and duplicate value operations are the main correctness risks. Node and data offsets are bounded by `XBC_NODE_MAX`, `XBC_DATA_MAX`, `XBC_DEPTH_MAX`, and `XBC_KEYLEN_MAX`; overflow and deep trees must fail cleanly. Quoted values cannot escape quote characters. `+=` and `:=` must preserve subkeys and array ordering. Error offsets depend on the mutated buffer and need to remain meaningful for diagnostics.

## Test Signals

Useful tests are the tools/bootconfig parser sanity tests, malformed input cases for braces, comments, quotes, invalid keywords, depth/key length overflow, duplicate assignment, `:=` override, and `+=` arrays. Runtime signals include successful `xbc_get_info()`, deterministic dotted-key lookup, leaf iteration order, clean `_xbc_exit()`/reinit cycles, and embedded bootconfig size/path coverage when `CONFIG_BOOT_CONFIG_EMBED` is enabled.

## Read Coverage

Source read size: 1009 lines, 22786 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bootconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bsearch.c -->
# sources/distributed-fs/ceph-client/lib/bsearch.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bsearch.c` is the non-inline exported wrapper for the generic kernel binary search helper. It provides a stable symbol for modules or code that cannot use only the inline implementation.

## Important APIs, Types, and Functions

The only runtime function is `bsearch(const void *key, const void *base, size_t num, size_t size, cmp_func_t cmp)`, exported with `EXPORT_SYMBOL` and marked `NOKPROBE_SYMBOL`. It delegates directly to `__inline_bsearch()` from `<linux/bsearch.h>`.

## Control Flow

The wrapper performs no local validation or looping. It receives the search key, base pointer, element count, element size, and comparator, then returns the result of `__inline_bsearch()`. The comparator controls ordering and equality.

## State and Persistence Behavior

There is no owned state. The function reads caller-owned array memory and returns a pointer into that array or `NULL`.

## Dependencies and Integration Points

Dependencies are `linux/bsearch.h`, `linux/export.h`, and `linux/kprobes.h`. Kernel subsystems and modules use this symbol when they need a generic binary search over sorted arrays without duplicating search logic.

## Risks and Edge Cases

Correctness depends entirely on the caller providing sorted input, a stable comparator, a nonzero element size, and a valid memory range. The wrapper cannot detect comparator contract violations or overflow in caller-provided layout.

## Test Signals

Signals are generic bsearch tests over empty arrays, one-element arrays, missing keys, first/last matches, key type different from element type, and module link coverage for the exported symbol. Kprobe blacklisting should keep tracing from instrumenting the wrapper.

## Read Coverage

Source read size: 36 lines, 1247 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/btree.c -->
# sources/distributed-fs/ceph-client/lib/btree.c

## Purpose

`sources/distributed-fs/ceph-client/lib/btree.c` implements a simple in-memory B+tree keyed by 32-bit, 64-bit, or 128-bit integer keys and storing non-NULL pointers. It is a sparse-address-space container similar in role to radix trees but optimized around cacheline-sized nodes.

## Important APIs, Types, and Functions

Important exported geometry objects are `btree_geo32`, `btree_geo64`, and `btree_geo128`. Exported lifecycle and storage functions include `btree_alloc`, `btree_free`, `btree_init_mempool`, `btree_init`, and `btree_destroy`. Core operations are `btree_last`, `btree_lookup`, `btree_update`, `btree_get_prev`, `btree_insert`, `btree_remove`, `btree_merge`, `btree_visitor`, and `btree_grim_visitor`; adapter callbacks include `visitorl`, `visitor32`, `visitor64`, and `visitor128`. Internal helpers manage key arrays, value slots, node growth/shrink, split, merge, rebalance, and traversal.

## Control Flow

Initialization creates or accepts a mempool backed by a `btree_node` slab cache. Lookup descends from `head->node` by scanning a node's sorted key slots until `keycmp() <= 0`, then follows child pointers until the leaf and scans for equality. Insert grows the tree if needed, finds a leaf, rejects duplicate keys through `BUG_ON`, splits full nodes recursively by inserting a new child in the parent, then shifts slots to insert the new pair. Remove finds the level, shifts remaining pairs left, clears the tail slot, and rebalances by merging neighboring nodes when combined fill fits. Merge repeatedly moves the victim's last entry to the target. Visitors recurse in key order and optionally reap nodes.

## State and Persistence Behavior

State is held in caller-owned `struct btree_head`, its mempool, and slab-allocated fixed-size nodes. Nodes store all used pairs on the left and zero-valued unused slots on the right; values cannot be NULL because zero marks empty. There is no locking in this file, so callers own synchronization and lifetime. `btree_grim_visitor()` frees all visited nodes and resets the head.

## Dependencies and Integration Points

The file uses `<linux/btree.h>` ABI types, slab and mempool allocation, module init/exit, cacheline sizing, and `BUG_ON`. It exports GPL symbols for kernel users needing sparse pointer maps, including code that can provide an external mempool for allocation constraints.

## Risks and Edge Cases

The unusual descending key layout and rightmost-lowest convention make parent key updates delicate. Duplicate insertion and NULL values are fatal `BUG_ON` cases. `btree_destroy()` frees only `head->node` plus the mempool, so callers should empty or grim-visit non-empty trees before teardown if nodes remain below the root. No internal locking means concurrent update or traversal is unsafe without external protection.

## Test Signals

Coverage should insert, lookup, update, remove, and iterate 32/64/128-bit keys across split and merge boundaries. Edge tests should cover empty trees, predecessor lookup around zero and gaps, duplicate insert assertions, merge of empty/non-empty trees, grim visitor freeing, and allocation failure during split. Slab init/exit and module link tests confirm lifecycle wiring.

## Read Coverage

Source read size: 795 lines, 19547 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bucket_locks.c -->
# sources/distributed-fs/ceph-client/lib/bucket_locks.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bucket_locks.c` allocates arrays of spinlocks sized for hash-bucket style locking. It centralizes lock-array sizing, initialization, and lockdep class assignment for subsystems that shard locking by hash.

## Important APIs, Types, and Functions

The exported functions are `__alloc_bucket_spinlocks()` and `free_bucket_spinlocks()`. Inputs include output lock pointer, output mask, maximum size, locks-per-CPU multiplier, GFP flags, lockdep name, and lock class key.

## Control Flow

Allocation chooses a size from either `max_size` or `min(num_possible_cpus() * cpu_mult, max_size)`, with `CONFIG_PROVE_LOCKING` forcing a smaller pseudo-CPU count. It allocates with `kvmalloc_objs()`, initializes each spinlock, assigns the lockdep map, stores `size - 1` as the mask, and returns zero or `-ENOMEM`. Freeing delegates to `kvfree()`.

## State and Persistence Behavior

The only persistent state is the caller-owned lock array and mask. The file does not track allocations globally. Lock instances persist until `free_bucket_spinlocks()` is called.

## Dependencies and Integration Points

Dependencies are spinlock APIs, lockdep, CPU count helpers, `kvmalloc_objs`, and `kvfree`. Integration points are hash tables and caches that index locks by `hash & locks_mask`; callers are expected to request power-of-two-compatible sizing.

## Risks and Edge Cases

The function stores `size - 1` as a mask, so a non-power-of-two `max_size` can produce an invalid hash mask despite the comment saying the size is rounded. A zero size would underflow the mask. `sizeof(spinlock_t) == 0` paths keep `locks` NULL but still return a mask.

## Test Signals

Tests should verify allocation success/failure, lockdep class initialization, CPU multiplier sizing, mask correctness for caller-supplied power-of-two sizes, zero and non-power-of-two guard behavior in callers, and clean `kvfree()` teardown.

## Read Coverage

Source read size: 54 lines, 1428 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bucket_locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bug.c -->
# sources/distributed-fs/ceph-client/lib/bug.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bug.c` provides generic BUG/WARN table handling for architectures that emit `__bug_table` entries. It finds bug metadata for trap addresses, reports warnings or fatal bugs, manages module bug tables, and resets one-shot warning state.

## Important APIs, Types, and Functions

Important functions include `module_bug_finalize`, `module_bug_cleanup`, `bug_get_file_line`, `find_bug`, `report_bug_entry`, `report_bug`, and `generic_bug_clear_once`. Internal helpers include `bug_addr`, `module_find_bug`, `bug_get_format`, `__warn_printf`, `__report_bug`, and `clear_once_table`. The file consumes linker symbols `__start___bug_table` and `__stop___bug_table` plus optional module `bug_table` metadata.

## Control Flow

Module load scans ELF section names for `__bug_table`, records the table in `struct module`, and links the module onto an RCU-protected list. Trap handling enters warning RCU context, resolves the `struct bug_entry` either directly or by address, validates arch bug addresses, decodes file/line and optional format strings, handles `BUGFLAG_ONCE` by setting `BUGFLAG_DONE`, emits the cut-here line and warning text when appropriate, then calls `__warn()` for warnings or prints a critical BUG location. Clear-once walks built-in and module tables to clear `BUGFLAG_DONE`.

## State and Persistence Behavior

Built-in bug entries live in the kernel image. Module bug tables live for the module lifetime and are tracked in `module_bug_list` under RCU. `BUGFLAG_DONE` mutates bug entries to suppress repeated one-shot warnings until `generic_bug_clear_once()`.

## Dependencies and Integration Points

The file integrates with architecture trap handlers through `report_bug()`, module loader finalization/cleanup, RCU list traversal, ftrace warning disabling, context tracking around warnings, and optional architecture format argument extraction. It depends on config-controlled `struct bug_entry` layout, relative pointer decoding, and arch `is_valid_bugaddr()`.

## Risks and Edge Cases

Relative pointer decoding, verbose/non-verbose layouts, and optional format argument extraction are ABI-sensitive. Reporting paths intentionally avoid normal locks because BUG handling can run in fragile contexts. Module unload races rely on RCU discipline. A stale or invalid trap address must return `BUG_TRAP_TYPE_NONE` rather than misreporting.

## Test Signals

Signals include arch trap tests for WARN, WARN_ON_ONCE, BUG, invalid bug addresses, verbose and non-verbose builds, module load/unload with `__bug_table`, `generic_bug_clear_once()` re-enabling one-shot warnings, and format-string WARN paths with and without arch argument extraction.

## Read Coverage

Source read size: 305 lines, 7498 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/build_OID_registry -->
# sources/distributed-fs/ceph-client/lib/build_OID_registry

## Purpose

`sources/distributed-fs/ceph-client/lib/build_OID_registry` is a Perl build helper that generates a C registry for ASN.1 object identifiers declared in an input header. It parses enum-style OID declarations and writes encoded OID data plus lookup tables.

## Important APIs, Types, and Functions

The script has no reusable Perl functions; its public interface is the command line `build_OID_registry <in-h-file> <out-c-file>`. It emits `oid_index`, `oid_data`, and `oid_search_table` C definitions keyed by `enum OID` names. It uses `Cwd::abs_path`, `@names`, `@oids`, `@lengths`, `@indices`, `@encoded_oids`, and `@hash_values`.

## Control Flow

The script validates that exactly two arguments were passed, resolves `$ENV{srctree}`, scans the input file for `OID_NAME, /* dotted.oid */` lines, opens the output C file, computes DER-style base-128 encoded lengths and offsets, emits an index table sized as `unsigned char` or `unsigned short`, encodes each OID component into octets, computes a compact hash, sorts lookup entries by hash, encoded length, and reverse byte content, then emits the search table.

## State and Persistence Behavior

All state is process-local arrays. The only persistent output is the generated C file. The generated header comment strips the absolute source-tree prefix when `srctree` is set.

## Dependencies and Integration Points

The script depends on Perl, `bc` for base-2 conversion, `srctree` in the environment, and the expected OID declaration format. It integrates with kernel build rules that generate static OID lookup data consumed by ASN.1 or key/certificate code.

## Risks and Edge Cases

The input regex is narrow and will ignore declarations that do not match the exact comment format. It shells out to `bc` for every component beyond the first two, so missing `bc` or unusual environment behavior breaks generation. Very large OID data changes the index type. Hash collisions are handled by ordering but consumers must compare encoded bytes, not trust the hash alone.

## Test Signals

Useful signals are generation from a known OID header, byte-for-byte stable output, correct base-128 encoding for multi-octet components, behavior when total length crosses 255, missing/wrong argument exit status, and build integration that compiles the generated C output.

## Read Coverage

Source read size: 218 lines, 5098 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/build_OID_registry -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/buildid.c -->
# sources/distributed-fs/ceph-client/lib/buildid.c

## Purpose

`sources/distributed-fs/ceph-client/lib/buildid.c` parses GNU build IDs from ELF files, VMAs, raw note buffers, and the running kernel note section. It supports both faultable and no-fault contexts through a small reader abstraction.

## Important APIs, Types, and Functions

Important exported or visible APIs are `freader_init_from_file`, `freader_init_from_mem`, `freader_fetch`, `freader_cleanup`, `build_id_parse_nofault`, `build_id_parse`, `build_id_parse_file`, `build_id_parse_buf`, `vmlinux_build_id`, and `init_vmlinux_build_id`. Internal helpers include `freader_get_folio`, `freader_put_folio`, `parse_build_id`, `get_build_id_32`, `get_build_id_64`, and `__build_id_parse`.

## Control Flow

File readers either use `__kernel_read()` when faults are allowed or page-cache folio lookup and `kmap_local_folio()` when no faults are allowed. Memory readers return direct pointers after bounds checks. ELF parsing first fetches enough of the ELF header to validate magic and executable/shared-object type, dispatches by ELF class, caps program header iteration at `MAX_PHDR_CNT`, then scans `PT_NOTE` segments. Note parsing walks aligned `Elf32_Nhdr` records, checks for name `GNU`, type `NT_GNU_BUILD_ID` value 3, nonzero descriptor length within `BUILD_ID_SIZE_MAX`, copies the descriptor, and zero-fills the remainder.

## State and Persistence Behavior

`struct freader` owns transient mapping state for one parse operation and must release mapped folios with `freader_cleanup()`. The only persistent kernel state is optional `vmlinux_build_id` under `CONFIG_STACKTRACE_BUILD_ID` or `CONFIG_VMCORE_INFO`, initialized from linker note bounds during init.

## Dependencies and Integration Points

Dependencies include ELF headers, VFS files, page cache folios, local kmap, secretmem rejection, overflow helpers, and kernel note linker symbols. Users include perf, stacktrace, vmcore, BPF, or diagnostics code that needs build IDs without necessarily faulting pages in.

## Risks and Edge Cases

No-fault parsing fails if relevant file pages are absent or not uptodate. Secretmem mappings are intentionally rejected. Pointer results from `freader_fetch()` are invalidated by later fetches, so fields are copied with `READ_ONCE`. Arithmetic overflow in offsets, note bounds, and program header ranges must be rejected. Endianness conversion is not performed here; it assumes native ELF headers in the contexts using it.

## Test Signals

Tests should cover 32-bit and 64-bit ELF build IDs, missing notes, non-ELF buffers, unsupported file types, malformed note sizes, overlong descriptors, page-boundary fetches, no-fault cache-miss failure, faultable file parsing success, secretmem rejection, and `init_vmlinux_build_id()` on builds with note sections.

## Read Coverage

Source read size: 407 lines, 10657 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/buildid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bust_spinlocks.c -->
# sources/distributed-fs/ceph-client/lib/bust_spinlocks.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bust_spinlocks.c` provides the generic `bust_spinlocks()` implementation for architectures without their own version. It helps panic/oops paths get console output out despite normal console locking constraints.

## Important APIs, Types, and Functions

The single function is `bust_spinlocks(int yes)`. It manipulates global `oops_in_progress`, calls `console_unblank()`, and wakes the printk/klogd path with `wake_up_klogd()`.

## Control Flow

When `yes` is nonzero, it increments `oops_in_progress`. When `yes` is zero, it unblanks the console, decrements `oops_in_progress`, and wakes logging if the count reaches zero.

## State and Persistence Behavior

The only persistent state is the global oops nesting count. It is intentionally process-global and affects console/printk behavior during exceptional paths.

## Dependencies and Integration Points

The function integrates with `oops`, `die`, `BUG`, and panic reporting paths, plus console, VT, printk, and waitqueue infrastructure.

## Risks and Edge Cases

The count must remain balanced across nested exceptional paths. Underflow would incorrectly wake logging and mark the system as out of oops context. This function runs when normal locking may already be compromised, so it intentionally stays minimal.

## Test Signals

Signals include arch link coverage, nested `bust_spinlocks(1)`/`bust_spinlocks(0)` balance, console unblank on exit, and printk wakeup only when the nesting counter reaches zero.

## Read Coverage

Source read size: 29 lines, 632 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bust_spinlocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cache_maint.c -->
# sources/distributed-fs/ceph-client/lib/cache_maint.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cache_maint.c` is a small registration framework for memory-system cache coherency maintenance operations. Drivers register invalidation providers; callers request writeback/invalidate for physical memory regions without knowing provider instances.

## Important APIs, Types, and Functions

Exports include `cache_coherency_ops_instance_put`, `_cache_coherency_ops_instance_alloc`, `cache_coherency_ops_instance_register`, `cache_coherency_ops_instance_unregister`, `cpu_cache_invalidate_memregion`, and `cpu_cache_has_invalidate_memregion`. Internal helpers are `__cache_coherency_ops_instance_free`, `cache_inval_one`, `cache_inval_done_one`, and `cache_invalidate_memregion`.

## Control Flow

Allocation validates that ops and `ops->wbinv` exist, zero-allocates a caller-sized `cache_coherency_ops_inst`, initializes its list and kref, and stores ops. Register/unregister adds or removes instances under a write semaphore. `cpu_cache_invalidate_memregion()` builds `cc_inval_params`, takes the read semaphore, calls each provider's `wbinv`, then calls each optional `done` method to wait for completion.

## State and Persistence Behavior

Registered providers live on the global `cache_ops_instance_list` and are protected by `cache_ops_instance_list_lock`. Instance memory is kref-managed and freed when the final put drops. There is no persistence beyond driver registration lifetime.

## Dependencies and Integration Points

The file depends on `linux/cache_coherency.h`, krefs, lists, rwsems, `memregion`, and namespace exports `CACHE_COHERENCY` and `DEVMEM`. It integrates with device memory and platform cache maintenance drivers that implement `wbinv` and optional completion.

## Risks and Edge Cases

`cpu_cache_has_invalidate_memregion()` is explicitly advisory and can race unregister. Invalidation stops on the first provider error, which can leave later providers uncalled. Providers must keep instance lifetime valid while registered and must not sleep or fail in contexts callers cannot tolerate.

## Test Signals

Signals include provider alloc/register/unregister/put lifecycle, one and multiple providers, `wbinv` parameter propagation, optional `done`, error propagation, empty-list behavior, race-sensitive unregister tests, and namespace export build checks.

## Read Coverage

Source read size: 138 lines, 3782 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cache_maint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/check_signature.c -->
# sources/distributed-fs/ceph-client/lib/check_signature.c

## Purpose

`sources/distributed-fs/ceph-client/lib/check_signature.c` compares an MMIO region against a byte signature, typically for firmware or BIOS signature discovery.

## Important APIs, Types, and Functions

The exported API is `check_signature(const volatile void __iomem *io_addr, const unsigned char *signature, int length)`.

## Control Flow

The function loops for `length` bytes, reads each MMIO byte with `readb()`, compares it to the current signature byte, returns 0 on the first mismatch, and returns 1 after all bytes match.

## State and Persistence Behavior

There is no owned state. The function only performs ordered MMIO reads through the caller-provided mapping.

## Dependencies and Integration Points

Dependencies are `linux/io.h` and `linux/export.h`. Callers must obtain a valid `ioremap()` mapping and pass an appropriate signature buffer.

## Risks and Edge Cases

The length is signed; negative values skip the loop and return 1, so callers must validate length. MMIO side effects depend on the target region. The function assumes byte-wise reads are acceptable for the hardware.

## Test Signals

Tests should cover exact match, first/middle/last mismatch, zero length, caller-side validation of negative lengths, and use against mocked or safely mapped IO memory.

## Read Coverage

Source read size: 27 lines, 635 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/check_signature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/checksum.c -->
# sources/distributed-fs/ceph-client/lib/checksum.c

## Purpose

`sources/distributed-fs/ceph-client/lib/checksum.c` provides generic Internet checksum routines for architectures that do not override them. It computes IP header checksums, partial checksums, and TCP/UDP pseudo-header sums.

## Important APIs, Types, and Functions

The exported functions are `ip_fast_csum`, `csum_partial`, `ip_compute_csum`, and `csum_tcpudp_nofold` when not provided by arch headers. Internal helpers include `do_csum()` and `from64to32()`.

## Control Flow

`do_csum()` handles unaligned leading bytes, accumulates 16-bit and 32-bit chunks with carry tracking, handles odd trailing bytes with endian-specific placement, folds to 16 bits, and byte-swaps the result if the original buffer was odd-aligned. `ip_fast_csum()` computes the complement over an IP header length. `csum_partial()` adds a previous sum with carry. `ip_compute_csum()` returns the complemented block checksum. `csum_tcpudp_nofold()` accumulates source/destination addresses, length, protocol, and prior sum without final folding.

## State and Persistence Behavior

There is no persistent state. All checksum state is local accumulator data and caller-supplied seed values.

## Dependencies and Integration Points

The file integrates with networking code through `<net/checksum.h>` and architecture byteorder definitions. Architecture-specific implementations can override `do_csum`, `ip_fast_csum`, or `csum_tcpudp_nofold` through macros.

## Risks and Edge Cases

Unaligned access behavior depends on architecture tolerance for 16-bit and 32-bit loads; the generic code was adjusted for m68knommu but still assumes configured access semantics. Odd lengths and odd starting addresses are the highest-risk paths. Endianness-specific pseudo-header shifts must match network checksum rules.

## Test Signals

Signals include known-vector IP/TCP/UDP checksums, aligned and unaligned buffers, odd and even lengths, incremental `csum_partial()` equivalence, pseudo-header nofold values on little- and big-endian builds, and arch override build coverage.

## Read Coverage

Source read size: 164 lines, 4049 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/closure.c -->
# sources/distributed-fs/ceph-client/lib/closure.c

## Purpose

`sources/distributed-fs/ceph-client/lib/closure.c` implements asynchronous closure refcounting and wait-list coordination used by bcache-style asynchronous flows. It combines reference accounting, continuation scheduling, synchronous waits, and optional debug tracking.

## Important APIs, Types, and Functions

Exports include `closure_sub`, `closure_put`, `__closure_wake_up`, `closure_wait`, `__closure_sync`, `closure_return_sync`, `__closure_sync_timeout`, and under `CONFIG_DEBUG_CLOSURES`, `closure_debug_create` and `closure_debug_destroy`. Internal helpers include `closure_put_after_sub_checks`, `closure_put_after_sub`, `closure_sync_fn`, and debugfs `debug_show`.

## Control Flow

Ref drops use release atomics and then validate guard bits and remaining flags. When remaining references reach zero, the closure either queues its continuation function, runs its destructor, and/or drops its parent reference. `closure_wait()` adds a closure to a lockless waitlist, setting waiting bits and taking an extra reference. `__closure_wake_up()` drains and reverses the llist to preserve FIFO order, clears waiting state, and drops wait references. Synchronous waits install `closure_sync_fn` as the continuation and sleep uninterruptibly until the callback marks completion and wakes the task; timeout handling attempts to undo the continuation if it has not completed.

## State and Persistence Behavior

Persistent state is in caller-owned `struct closure`: atomic `remaining` flags, parent pointer, function pointer, work item, wait-list node, syncer pointer, and debug fields. Debug mode tracks live closures in a global list protected by `closure_list_lock` and exposes them through debugfs.

## Dependencies and Integration Points

The file depends on `linux/closure.h`, workqueue callback conventions, atomics, llist, scheduler sleep/wakeup, RCU in the sync callback, debugfs, and seq_file. It integrates with asynchronous subsystems that model completion dependencies with closures.

## Risks and Edge Cases

The remaining field packs refcount and flags, so incorrect flag arithmetic can queue, destroy, or wait forever. Timeout undo in `__closure_sync_timeout()` races the final put and must only restore the initializer when safe. Parent closure puts must happen exactly once. Debug tracking depends on correct create/destroy calls and magic values.

## Test Signals

Tests should cover continuation queueing after final put, destructor path, parent release, multiple waiters woken FIFO, synchronous wait and timeout, closure return without reinitializing refs, debugfs live closure reporting, and warnings for guard bits or bad zero-ref flags.

## Read Coverage

Source read size: 297 lines, 6914 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/closure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/clz_ctz.c -->
# sources/distributed-fs/ceph-client/lib/clz_ctz.c

## Purpose

`sources/distributed-fs/ceph-client/lib/clz_ctz.c` supplies weak libgcc-compatible count-leading-zero and count-trailing-zero helpers required by compiler builtins on architectures that do not provide optimized versions.

## Important APIs, Types, and Functions

Exported weak functions are `__ctzsi2`, `__clzsi2`, `__clzdi2`, and `__ctzdi2`. They use `__ffs`, `fls`, `fls64`, and `__ffs64`.

## Control Flow

Each helper maps directly to a kernel bit operation: trailing-zero helpers return first-set-bit index, and leading-zero helpers subtract the last-set-bit position from the operand width.

## State and Persistence Behavior

No state is stored. The functions are pure for valid nonzero inputs.

## Dependencies and Integration Points

The functions integrate with compiler-generated calls from `__builtin_ctz*` and `__builtin_clz*`, and can be overridden by arch-specific strong definitions.

## Risks and Edge Cases

Compiler builtin semantics usually leave zero input undefined, and these helpers inherit that risk through `__ffs`/`fls` behavior. Weak symbol ordering must allow arch overrides.

## Test Signals

Signals include link coverage on architectures needing libgcc helpers, known values for 32-bit and 64-bit operands, zero-input caller avoidance, exported symbol checks, and arch override builds.

## Read Coverage

Source read size: 43 lines, 979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/clz_ctz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/clz_tab.c -->
# sources/distributed-fs/ceph-client/lib/clz_tab.c

## Purpose

`sources/distributed-fs/ceph-client/lib/clz_tab.c` provides the `__clz_tab` lookup table used by software count-leading-zero implementations.

## Important APIs, Types, and Functions

The file defines one global object: `const unsigned char __clz_tab[]`, with 256 entries representing leading-zero/count-position helper values for byte-sized inputs.

## Control Flow

There is no executable control flow. Consumers index the table from bit helper code.

## State and Persistence Behavior

The table is read-only static data with kernel image lifetime.

## Dependencies and Integration Points

It integrates with generic bitops/libgcc helper code that performs table-assisted CLZ calculations on byte chunks. There are no includes or local dependencies.

## Risks and Edge Cases

Any table value change silently corrupts bit helper results. Consumers must index with a byte-sized value and handle zero according to their own semantics.

## Test Signals

Signals include bitops/libgcc helper known-vector tests, build/link coverage for consumers of `__clz_tab`, and checksum or generated-table comparison to catch accidental edits.

## Read Coverage

Source read size: 19 lines, 891 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/clz_tab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cmdline.c -->
# sources/distributed-fs/ceph-client/lib/cmdline.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cmdline.c` implements common parsers for kernel command-line and module-option strings. It handles integer lists/ranges, memory-size suffixes, option presence, and argument tokenization.

## Important APIs, Types, and Functions

Exported functions are `get_option`, `get_options`, `memparse`, and `next_arg`; `parse_option_str` is a visible helper without an export in this file. Internal helper `get_range()` expands `M-N` integer ranges.

## Control Flow

`get_option()` parses an optional leading negative sign and integer with `simple_strtoull()`, stores it when requested, and returns a code indicating no value, value, value plus comma, or a range hyphen. `get_options()` loops over comma-separated values and positive ranges, optionally in validation mode when `nints == 0`, storing count in `ints[0]`. `memparse()` parses a number and shifts by 10 for K through E suffixes. `parse_option_str()` scans comma-separated tokens for exact option names. `next_arg()` splits a mutable string into parameter and optional value, tracks quotes, removes quote wrappers, converts the delimiter to NUL, and skips trailing spaces.

## State and Persistence Behavior

There is no global state. Several APIs mutate caller-provided strings by inserting NUL terminators and advancing pointers.

## Dependencies and Integration Points

The file depends on kernel string, ctype, and simple numeric parsing helpers. It is integrated broadly with boot parameter handling, module parameter parsing, and drivers that parse compact numeric lists.

## Risks and Edge Cases

`get_options()` assumes `ints` is usable even in validation mode because it writes `ints[0]`. Negative ranges are not supported as ranges. `memparse()` can overflow silently through left shifts. `next_arg()` does not support escaping quotes, so embedded quotes can terminate parsing unexpectedly.

## Test Signals

Useful tests cover empty input, negative single values, comma lists, ranges, validation mode, full-array truncation, memory suffixes through exabytes, option-name boundary matching, quoted arguments with spaces, value quotes, and mutable string NUL placement.

## Read Coverage

Source read size: 275 lines, 5983 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cmpdi2.c -->
# sources/distributed-fs/ceph-client/lib/cmpdi2.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cmpdi2.c` implements the libgcc `__cmpdi2` helper for signed 64-bit comparisons on architectures that need compiler runtime support.

## Important APIs, Types, and Functions

The exported symbol is `word_type notrace __cmpdi2(long long a, long long b)`. It uses `DWunion` from `<linux/libgcc.h>` to access high and low words.

## Control Flow

The function compares signed high words first, returning 0 when `a < b` and 2 when `a > b`. If high words are equal, it compares low words as unsigned and returns the same ordering codes or 1 for equality.

## State and Persistence Behavior

There is no state. It is a pure comparison helper.

## Dependencies and Integration Points

It integrates with compiler-generated calls for 64-bit comparison on targets lacking native support and exports the symbol for kernel linkage.

## Risks and Edge Cases

Return values follow libgcc convention rather than normal `strcmp` convention. Correct signedness split is critical: high word signed, low word unsigned. `notrace` prevents instrumentation recursion in low-level runtime paths.

## Test Signals

Tests should compare equal, less, greater, negative vs positive, high-word differences, low-word-only differences, and compiler-emitted helper linkage on 32-bit builds.

## Read Coverage

Source read size: 30 lines, 501 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cmpdi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cmpxchg-emu.c -->
# sources/distributed-fs/ceph-client/lib/cmpxchg-emu.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cmpxchg-emu.c` emulates one-byte `cmpxchg()` for architectures that can atomically compare/exchange 32-bit words but not 8-bit bytes.

## Important APIs, Types, and Functions

The exported function is `cmpxchg_emu_u8(volatile u8 *p, uintptr_t old, uintptr_t new)`. The helper union `u8_32` overlays four bytes and one 32-bit word.

## Control Flow

The function aligns the target byte pointer down to a 32-bit word, computes the byte index, reads the word with `READ_ONCE`, and loops. Each iteration checks whether the target byte equals `old`; if not, it returns the observed byte. Otherwise it modifies only that byte in a copied word, instruments an atomic read/write of one byte, and calls 32-bit `cmpxchg()` under `data_race()`. The loop retries until the full word compare/exchange succeeds.

## State and Persistence Behavior

There is no local persistent state. The function atomically mutates the containing 32-bit memory word and returns the old byte value according to cmpxchg semantics.

## Dependencies and Integration Points

Dependencies include atomic cmpxchg support, `READ_ONCE`, KCSAN instrumentation, and generic cmpxchg emulation headers. It integrates with generic atomics on architectures without byte cmpxchg.

## Risks and Edge Cases

The containing 32-bit word must be safely accessible and properly aligned for 32-bit atomics; bytes near page or object boundaries can still touch neighboring bytes in the same word. Concurrent writers to other bytes in the word can cause retries. Endianness is handled by the union byte indexing in native memory order but must match intended byte address semantics.

## Test Signals

Signals include successful byte exchange, mismatch return without store, concurrent updates to adjacent bytes, all four byte offsets, KCSAN/instrumentation sanity, and fault/alignment expectations on the target architecture.

## Read Coverage

Source read size: 45 lines, 1086 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cmpxchg-emu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/codetag.c -->
# sources/distributed-fs/ceph-client/lib/codetag.c

## Purpose

`sources/distributed-fs/ceph-client/lib/codetag.c` manages typed code-tag sections for built-in code and modules. It lets subsystems register a tag type, discover linker/module section ranges, iterate tags, and invoke type-specific load/unload callbacks.

## Important APIs, Types, and Functions

Important types are `struct codetag_type`, `struct codetag_range`, and `struct codetag_module`. Public functions include `codetag_lock_module_list`, `codetag_trylock_module_list`, `codetag_get_ct_iter`, `codetag_next_ct`, `codetag_to_text`, `codetag_needs_module_section`, `codetag_load_module`, `codetag_unload_module`, `codetag_register_type`, and `codetag_get_type`. Helpers include `get_symbol`, `get_section_range`, `codetag_module_init`, and `codetag_module_unload`.

## Control Flow

Registering a type allocates and initializes a `codetag_type`, adds it to the global list, and immediately initializes the built-in section range. Module load asks each registered type to locate `__start`/`__stop` symbols for its section and add a `codetag_module` entry to an IDR under the type write lock. Iteration requires the module list read lock, walks IDR entries by module id, detects module sequence changes, and advances by `tag_size` within each range. Module unload removes the IDR entry, calls optional unload callbacks, updates counts, and frees module state.

## State and Persistence Behavior

Global state is `codetag_types` protected by `codetag_lock`. Per type state includes count, module IDR, read/write semaphore, descriptor, and monotonically increasing module sequence. Per-module state persists for module lifetime. Built-in code is represented through a pseudo module name `(built-in)`.

## Dependencies and Integration Points

The file depends on `codetag.h`, IDR, kallsyms lookup, module loader hooks, seq_buf formatting, slab allocation, and linker-generated codetag section symbols. It integrates with optional module section allocation decisions through `needs_section_mem`.

## Risks and Edge Cases

Symbol lookup by constructed section names is fragile if linker naming changes. Iterators must hold the module-list read lock or module unload can invalidate ranges. Type-specific load errors must remove IDR entries and avoid count leaks. Empty ranges are valid and ignored.

## Test Signals

Tests should cover type registration, built-in range discovery, module load/unload, iteration across multiple modules, sequence change handling, empty ranges, load callback failure, text formatting with and without module names, and section memory decision callbacks.

## Read Coverage

Source read size: 405 lines, 9050 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/codetag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/compat_audit.c -->
# sources/distributed-fs/ceph-client/lib/compat_audit.c

## Purpose

`sources/distributed-fs/ceph-client/lib/compat_audit.c` supplies audit syscall classification tables and classification logic for compat 32-bit syscalls.

## Important APIs, Types, and Functions

The file defines `compat_dir_class`, `compat_read_class`, `compat_write_class`, `compat_chattr_class`, and `compat_signal_class` arrays, each populated from asm-generic audit headers and terminated by `~0U`. It also defines `audit_classify_compat_syscall(int abi, unsigned syscall)`.

## Control Flow

Classification switches on the compat syscall number and returns specialized classes for `open`, `openat`, `socketcall`, `execve`, and `openat2` when those syscall numbers exist; all other syscalls return `AUDITSC_COMPAT`.

## State and Persistence Behavior

The arrays are static kernel data used by audit logic. There is no runtime mutation in this file.

## Dependencies and Integration Points

Dependencies include compat syscall numbers from `asm/unistd32.h`, audit architecture constants, and asm-generic audit class include files. Audit code consumes the arrays and classifier to apply policy to compat tasks.

## Risks and Edge Cases

Syscall-number availability is architecture-dependent, so conditional cases must match the compat table. Missing a newly special-cased syscall can cause less precise audit classification. The `abi` argument is unused here, so ABI-specific distinctions must be handled elsewhere if needed.

## Test Signals

Signals include build coverage on compat architectures with and without optional syscall numbers, audit classification tests for open/openat/openat2/socketcall/execve/default, and table terminator checks for each class array.

## Read Coverage

Source read size: 56 lines, 1002 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/compat_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cpu_rmap.c -->
# sources/distributed-fs/ceph-client/lib/cpu_rmap.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cpu_rmap.c` maintains reverse maps from CPUs to objects with CPU affinities, especially IRQs. It chooses a nearest object for each CPU based on direct affinity, sibling/core, and NUMA-node topology.

## Important APIs, Types, and Functions

Important exported APIs are `alloc_cpu_rmap`, `cpu_rmap_put`, `cpu_rmap_add`, `cpu_rmap_update`, `free_irq_cpu_rmap`, `irq_cpu_rmap_notify`, `irq_cpu_rmap_release`, and `irq_cpu_rmap_add`. Internal helpers include `cpu_rmap_release`, `cpu_rmap_get`, `cpu_rmap_copy_neigh`, `get_free_index`, and optional `debug_print_rmap`.

## Control Flow

Allocation builds a single object containing per-CPU `near[]` entries and an object pointer array, initializes a kref, and assigns each possible CPU to an initial rotating object with infinite distance. Adding an object fills the first free slot. Updating an object's affinity invalidates CPUs that pointed to that object, marks CPUs in the new affinity at distance zero, marks their NUMA nodes for update, then copies nearest mappings from SMT siblings, core siblings, and node masks at increasing distances. IRQ glue allocates notifier objects, registers affinity notifiers, and updates the rmap when IRQ affinity changes.

## State and Persistence Behavior

State lives in caller-owned `struct cpu_rmap` with kref lifetime, `near[cpu]` distance/index records, and `obj[]` pointers. IRQ integration stores `struct irq_glue` objects in `obj[]` and releases them through IRQ notifier release callbacks. There is no file persistence.

## Dependencies and Integration Points

The file depends on CPU masks, topology masks, NUMA node masks, IRQ affinity notifier APIs, krefs, and allocation helpers. It integrates with network and storage drivers that want per-CPU nearest queue/vector lookup after IRQ affinity changes.

## Risks and Edge Cases

The object count is capped at `u16` range. `alloc_cpu_rmap()` uses `cpu % size`, so callers must not pass size zero. Topology propagation only goes through siblings/core/node and does not compute arbitrary NUMA distances. IRQ notifiers must be unregistered before IRQ teardown to avoid stale callbacks.

## Test Signals

Tests should cover allocation size limits, zero-size caller guards, object add exhaustion, affinity updates for direct CPUs and neighboring CPUs, CPU hotplug assumptions around possible/online masks, IRQ notifier update/release paths, and refcount release.

## Read Coverage

Source read size: 339 lines, 8356 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cpu_rmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cpumask.c -->
# sources/distributed-fs/ceph-client/lib/cpumask.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cpumask.c` provides non-inline cpumask allocation helpers for offstack masks and CPU selection helpers that distribute work across online CPUs.

## Important APIs, Types, and Functions

Under `CONFIG_CPUMASK_OFFSTACK`, exported or init APIs are `alloc_cpumask_var_node`, `alloc_bootmem_cpumask_var`, `free_cpumask_var`, and `free_bootmem_cpumask_var`. Always-present exported helpers are `cpumask_local_spread`, `cpumask_any_and_distribute`, and `cpumask_any_distribute`. The file also defines per-CPU `distribute_cpu_mask_prev`.

## Control Flow

Offstack allocation uses `kmalloc_node(cpumask_size())`, reports allocation failures under debug config, and frees with `kfree`; boot allocation uses memblock. `cpumask_local_spread()` wraps the index by online CPU count and delegates to `sched_numa_find_nth_cpu()`. The distribute helpers read the current CPU's previous selection, find the next CPU in the requested mask or mask intersection with wraparound, and store the new previous value when a CPU is found.

## State and Persistence Behavior

Allocated cpumasks persist until caller free. The spread helper has no state. Distribution state is per-CPU and affects subsequent selections from the same CPU to avoid always choosing the first CPU.

## Dependencies and Integration Points

Dependencies include cpumask, bitops, memblock, NUMA scheduler helpers, per-CPU storage, and slab allocation. The helpers are used by drivers and core code that need masks allocated outside stack limits or need fair-ish CPU selection.

## Risks and Edge Cases

`cpumask_local_spread()` assumes at least one online CPU. The distribute helpers intentionally skip CPU 0 on first selection because previous starts at zero. Offstack allocation behavior differs at compile time; callers must handle the inline always-success version when offstack is disabled.

## Test Signals

Signals include offstack allocation/free on nodes, bootmem allocation/free during init, local-spread order by NUMA hop, distribution wraparound across masks, empty-mask return `>= nr_cpu_ids`, and debug failure reporting.

## Read Coverage

Source read size: 168 lines, 4746 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/cpumask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/Kconfig -->
# sources/distributed-fs/ceph-client/lib/crc/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/Kconfig` declares build-time configuration for the kernel CRC library, including small CRC variants, CRC32, CRC64, architecture accelerations, KUnit tests, and benchmarks.

## Important APIs, Types, and Functions

Important symbols are `CRC4`, `CRC7`, `CRC8`, `CRC16`, `CRC_CCITT`, `CRC_ITU_T`, `CRC_T10DIF`, `CRC_T10DIF_ARCH`, `CRC32`, `CRC32_ARCH`, `CRC64`, `CRC64_ARCH`, `CRC_OPTIMIZATIONS`, `CRC_KUNIT_TEST`, `CRC_ENABLE_ALL_FOR_KUNIT`, and `CRC_BENCHMARK`.

## Control Flow

There is no runtime flow. Kconfig dependency resolution selects generic CRC objects and enables architecture-specific objects when both the base CRC and `CRC_OPTIMIZATIONS` are enabled and the architecture advertises support. KUnit options select the CRC variants needed by tests.

## State and Persistence Behavior

The file persists only build configuration state. Selected symbols determine which objects and architecture headers are compiled into the kernel or modules.

## Dependencies and Integration Points

The file integrates with `lib/crc/Makefile`, architecture feature symbols such as ARM/ARM64/PPC/RISCV/X86/S390/SPARC/LOONGARCH/MIPS, `KUNIT`, and `UML` exclusion for optimizations.

## Risks and Edge Cases

Incorrect defaults can compile unsupported instructions or miss optimized code. `CRC_OPTIMIZATIONS` disabled should fall back cleanly to generic implementations. KUnit select-all must not unintentionally affect production configs.

## Test Signals

Signals include randconfig/allmodconfig build coverage, architecture configs with and without optimization support, `CRC_OPTIMIZATIONS=n` fallback builds, KUnit enable-all coverage, and benchmark option dependency checks.

## Read Coverage

Source read size: 129 lines, 3437 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/Makefile -->
# sources/distributed-fs/ceph-client/lib/crc/Makefile

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/Makefile` maps CRC Kconfig symbols to generic objects, architecture-optimized objects, generated lookup-table headers, and tests.

## Important APIs, Types, and Functions

Important build variables are `obj-$(CONFIG_CRC*)`, composite objects `crc-t10dif-y`, `crc32-y`, and `crc64-y`, architecture additions under `CONFIG_CRC*_ARCH`, `hostprogs := gen_crc32table gen_crc64table`, `clean-files`, and generation commands `cmd_crc32` and `cmd_crc64`.

## Control Flow

The build first adds selected small CRC object files. Composite targets build main generic C files and optionally architecture-specific assembly/C objects while adding `-I$(src)/$(SRCARCH)` so main files include the correct arch header. CRC32 and CRC64 main objects depend on generated `crc32table.h` and `crc64table.h`, which are produced by host programs. ARM64 CRC64 removes no-FPU flags and adds FPU/crypto flags for the NEON inner object.

## State and Persistence Behavior

Build outputs include object files and generated table headers, which are cleaned by `clean-files`. There is no runtime state in the Makefile.

## Dependencies and Integration Points

The Makefile integrates with Kbuild, architecture directories, generated autoconf, host compiler support, and `lib/crc/tests/`. It depends on source names matching Kconfig architecture selections.

## Risks and Edge Cases

Mismatch between Kconfig defaults and object names breaks optimized builds. Generated table headers must be built before main objects. FPU flags for ARM64 CRC64 are sensitive because kernel code normally builds with FPU disabled. The PPC T10DIF object name must match the actual generated/included assembly target.

## Test Signals

Signals are per-architecture build tests for T10DIF/CRC32/CRC64 acceleration, clean rebuilds after deleting generated headers, `make clean` removing generated files, KUnit test object inclusion, and FPU flag inspection for `arm64/crc64-neon-inner.o`.

## Read Coverage

Source read size: 68 lines, 2124 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif-core.S -->
# sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif-core.S` implements ARM 32-bit NEON/crypto accelerated CRC-T10DIF folding routines. It supplies both PMULL64 final CRC computation and an 8-bit polynomial-multiply fallback that emits a 16-byte folded buffer for generic finishing.

## Important APIs, Types, and Functions

Exported assembly entry points are `crc_t10dif_pmull64` and `crc_t10dif_pmull8`; local helper `__pmull16x64_p8` implements pairwise 16-by-64 polynomial multiply using 8-bit NEON multiply. Important macros are `pmull16x64_p8`, `pmull16x64_p64`, `fold_32_bytes`, `fold_16_bytes`, and `crct10dif`.

## Control Flow

The shared `crct10dif` macro handles lengths at least 16 bytes. For 256 bytes and larger, it loads the first 128 bytes, byte-swaps into polynomial coefficient order, xors the initial CRC into the high half, then folds 128-byte chunks with precomputed constants. It reduces q0-q6 into q7, folds any remaining 16-byte blocks, and uses a byte-shift table for 1..15 byte tails. The PMULL64 entry then folds the final 128-bit value to 96 bits and applies Barrett reduction to return a 16-bit CRC. The PMULL8 entry stores the final 16-byte folded vector for generic completion.

## State and Persistence Behavior

The file owns read-only fold constants, Barrett constants, byte-shift table, and a p8 permutation table. Runtime state is entirely in NEON registers and caller registers; no global mutable state is stored here.

## Dependencies and Integration Points

It depends on ARM assembler macros, NEON, PMULL/crypto extensions, and the C dispatch in `arm/crc-t10dif.h`. The C wrapper controls SIMD availability and static keys before calling these routines.

## Risks and Edge Cases

The code assumes `len >= 16` and SIMD context is already allowed. Endianness handling through `CPU_LE`, vector swaps, partial-tail table indexes, and CRC bit placement are correctness-critical. Calling without saving/restoring SIMD context would corrupt kernel FPU state.

## Test Signals

Signals include CRC-T10DIF KUnit vectors across 16, 17..31, 32..255, 256+, unaligned caller buffers handled by C path, PMULL and NEON-only feature combinations, big-endian ARM builds, and comparison with `crc_t10dif_generic()`.

## Read Coverage

Source read size: 468 lines, 15008 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif.h -->
# sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif.h` is the ARM dispatch header included by `crc-t10dif-main.c` when architecture optimization is enabled. It selects NEON or PMULL implementations based on runtime CPU features and SIMD availability.

## Important APIs, Types, and Functions

It defines static keys `have_neon` and `have_pmull`, chunk threshold `CRC_T10DIF_PMULL_CHUNK_SIZE`, assembly declarations `crc_t10dif_pmull64` and `crc_t10dif_pmull8`, inline `crc_t10dif_arch`, and `crc_t10dif_mod_init_arch`.

## Control Flow

`crc_t10dif_arch()` checks that the length is at least 16 and `may_use_simd()` is true. If PMULL is available, it enters `scoped_ksimd()` and returns `crc_t10dif_pmull64()`. If only NEON is available and length is greater than 16, it folds into a 16-byte buffer with `crc_t10dif_pmull8()` under SIMD context, then finishes using `crc_t10dif_generic(0, buf, 16)`. Otherwise it falls back to generic.

## State and Persistence Behavior

Runtime feature state is held in read-only-after-init static keys enabled during module/subsys init from `elf_hwcap` and `elf_hwcap2`. No per-call persistent state exists.

## Dependencies and Integration Points

The header depends on ARM SIMD context helpers, hardware capability bits `HWCAP_NEON` and `HWCAP2_PMULL`, and generic T10DIF code in `crc-t10dif-main.c`.

## Risks and Edge Cases

The dispatch must never call assembly when SIMD is unavailable. The NEON-only fallback deliberately uses generic reduction for the final vector; changing that contract can break CRC output. Static key initialization must happen before performance-sensitive use but fallback remains correct before init.

## Test Signals

Signals include feature-detection tests for no NEON, NEON-only, and PMULL systems, preemption/SIMD context assertions, generic equivalence over length thresholds, and module init enabling static keys.

## Read Coverage

Source read size: 46 lines, 1348 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc32-core.S -->
# sources/distributed-fs/ceph-client/lib/crc/arm/crc32-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc32-core.S` provides ARM accelerated CRC32 and CRC32C routines using ARMv8 CRC instructions and PMULL folding.

## Important APIs, Types, and Functions

Exported entry points are `crc32_pmull_le`, `crc32c_pmull_le`, `crc32_armv8_le`, and `crc32c_armv8_le`. The file defines CRC32 and CRC32C PMULL constants and a `__crc32` macro for scalar hardware CRC loops.

## Control Flow

The PMULL routines align the length down to 16-byte multiples, load four vectors, xor the initial CRC into the stream, process 64-byte chunks with carry-less multiplication constants, fold four vectors to one, fold to 64 and then 32 bits, and perform Barrett reduction. The scalar ARMv8 CRC macro handles aligned and unaligned pointers, processes 8-byte pairs through `crc32w`/`crc32cw`, and handles 4/2/1 byte tails with endian fixes under BE8.

## State and Persistence Behavior

The file stores only read-only constants. Per-call state is in general-purpose and NEON registers.

## Dependencies and Integration Points

It depends on ARM assembler support for `.arch_extension crc`, crypto NEON, `linux/linkage.h`, and dispatch from `arm/crc32.h`. The C header handles feature checks, alignment, and SIMD context.

## Risks and Edge Cases

PMULL paths require 16-byte multiple lengths and SIMD permission; scalar paths assume CRC extension availability. Unaligned head and tail handling must match generic CRC32/CRC32C semantics. BE8 byte reversal paths are easy to regress.

## Test Signals

Signals include CRC32 and CRC32C vectors over small tails, unaligned buffers, PMULL threshold lengths, big-endian ARM, generic fallback equivalence, and static-key dispatch coverage.

## Read Coverage

Source read size: 306 lines, 6910 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc32-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/arm/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc32.h` dispatches ARM CRC32/CRC32C calls between generic tables, ARMv8 CRC instructions, and PMULL acceleration.

## Important APIs, Types, and Functions

It defines static keys `have_crc32` and `have_pmull`, threshold `PMULL_MIN_LEN`, assembly declarations for CRC32 and CRC32C PMULL/scalar routines, inline functions `crc32_le_scalar`, `crc32_le_arch`, `crc32c_scalar`, `crc32c_arch`, `crc32_optimizations_arch`, and `crc32_mod_init_arch`.

## Control Flow

Scalar helpers use hardware CRC instructions if `have_crc32` is enabled, else generic base tables. Long little-endian CRC32/CRC32C calls align the buffer to 16 bytes using scalar processing, run PMULL on a rounded-down 16-byte multiple under `scoped_ksimd()`, then process tails through scalar helpers. Big-endian CRC32 falls back to generic.

## State and Persistence Behavior

Static keys are enabled after init based on `elf_hwcap2` bits. There is no per-call persistent state.

## Dependencies and Integration Points

The header depends on ARM hwcap, cpufeature, SIMD helpers, assembly routines in `arm/crc32-core.S`, and generic base functions from `crc32-main.c`.

## Risks and Edge Cases

Feature bits must match actual instruction availability. PMULL dispatch must honor `may_use_simd()` and avoid calling with too-short or unaligned chunks. The reported optimization flags must reflect only enabled runtime capabilities.

## Test Signals

Signals include no-feature generic fallback, CRC instruction-only systems, PMULL systems, unaligned input, length around `PMULL_MIN_LEN + 15`, `crc32_optimizations()` flags, and generic equality tests.

## Read Coverage

Source read size: 96 lines, 2503 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif-core.S -->
# sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif-core.S` implements AArch64 ASIMD/PMULL accelerated CRC-T10DIF. It provides a native PMULL64 final-CRC path and an 8-bit polynomial multiply folding path for CPUs without PMULL64.

## Important APIs, Types, and Functions

Assembly entry points are `crc_t10dif_pmull_p8` and `crc_t10dif_pmull_p64`; local helper `__pmull_p8_16x64` supports the p8 path. Core macros are `pmull16x64_p64`, `pmull16x64_p8`, `fold_32_bytes`, `fold_16_bytes`, and `crc_t10dif_pmull`. Read-only tables include fold constants and byte-shift indexes.

## Control Flow

The shared macro handles buffers of at least 16 bytes. For large buffers it folds 128-byte groups into eight vector accumulators, reduces to one 16-byte vector, folds additional 16-byte blocks, and handles 1..15 byte partial tails through a table-driven redivision. For shorter 16..255 byte inputs it starts with the 16-byte constants directly. `crc_t10dif_pmull_p64` reduces the final vector with PMULL and Barrett reduction to return a 16-bit CRC, while `crc_t10dif_pmull_p8` stores the folded vector for generic finishing.

## State and Persistence Behavior

No mutable global state is owned. Constants live in `.rodata`; vector and scalar registers carry per-call state.

## Dependencies and Integration Points

It depends on AArch64 assembler/linkage macros, `armv8-a+crypto`, ASIMD/PMULL availability, and dispatch from `arm64/crc-t10dif.h`.

## Risks and Edge Cases

Correctness depends on byte reversal into polynomial order, the partial-tail byte-shift table, and exact Barrett constants for polynomial `0x18bb7`. The functions assume the C wrapper has checked length and SIMD context. Any calling-convention register-save mistake can corrupt callers.

## Test Signals

Signals include KUnit CRC-T10DIF vectors for boundary lengths, ASIMD-only and PMULL feature paths, comparison with generic, tail lengths 1..15 after a folded block, and SIMD context checks under preemption.

## Read Coverage

Source read size: 469 lines, 15814 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif.h -->
# sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif.h` dispatches CRC-T10DIF on arm64 between generic, ASIMD p8 folding, and PMULL p64 acceleration.

## Important APIs, Types, and Functions

It defines static keys `have_asimd` and `have_pmull`, `CRC_T10DIF_PMULL_CHUNK_SIZE`, assembly declarations `crc_t10dif_pmull_p8` and `crc_t10dif_pmull_p64`, inline `crc_t10dif_arch`, and `crc_t10dif_mod_init_arch`.

## Control Flow

For lengths at least 16 and allowed SIMD context, PMULL-enabled CPUs call `crc_t10dif_pmull_p64()`. ASIMD-only CPUs with length greater than 16 call `crc_t10dif_pmull_p8()` into a stack buffer and finish with generic CRC over that folded buffer. Other cases use `crc_t10dif_generic()`.

## State and Persistence Behavior

Feature state is stored in read-only-after-init static keys enabled from `cpu_have_named_feature(ASIMD)` and `cpu_have_named_feature(PMULL)`.

## Dependencies and Integration Points

The header depends on arm64 cpufeature and SIMD helpers, the assembly implementation, and the generic T10DIF main file.

## Risks and Edge Cases

Dispatch must respect `may_use_simd()` and length constraints. The ASIMD-only path's stack buffer must be valid for generic finishing. Static key setup must match CPU feature alternatives.

## Test Signals

Signals include generic/ASIMD/PMULL path equivalence, length thresholds 15/16/17, runtime feature flags, SIMD-disabled context fallback, and KUnit coverage with benchmarks for acceleration paths.

## Read Coverage

Source read size: 48 lines, 1398 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc32-core.S -->
# sources/distributed-fs/ceph-client/lib/crc/arm64/crc32-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc32-core.S` implements AArch64 hardware CRC32, CRC32C, big-endian CRC32, and four-way PMULL-combined long-buffer variants.

## Important APIs, Types, and Functions

Exported symbols are `crc32_le_arm64`, `crc32c_le_arm64`, `crc32_be_arm64`, `crc32c_le_arm64_4way`, `crc32_le_arm64_4way`, and `crc32_be_arm64_4way`. Macros include byte/bit order conversion helpers, `__crc32`, and `crc4way`. Constant tables `.L0` and `.L1` hold folding coefficients.

## Control Flow

`__crc32` handles normal hardware CRC processing: it applies bit/byte order transforms for BE mode, handles sub-16 byte tails, processes 32-byte chunks with `crc32x`/`crc32cx`, and returns with order restored. `crc4way` processes long inputs as groups of up to 64 64-byte blocks, splits each group into four contiguous lanes, computes partial CRCs in parallel with hardware CRC instructions, combines them with PMULL coefficients, and loops until all 64-byte blocks are consumed.

## State and Persistence Behavior

State is local to registers and read-only coefficient tables. No mutable global state is stored.

## Dependencies and Integration Points

The file depends on AArch64 CRC and crypto instruction support, assembler macros, and dispatch from `arm64/crc32.h`. The wrapper decides whether CRC and PMULL features are available and handles remaining tails after four-way processing.

## Risks and Edge Cases

The four-way path assumes length in full 64-byte blocks and relies on the caller to process remainders. BE transforms must correctly reverse both bit and byte order. PMULL coefficient table indexing is sensitive to block counts.

## Test Signals

Signals include CRC32 LE, CRC32C, and CRC32 BE vectors, lengths below and above the four-way threshold, non-multiple-of-64 tails via wrapper, PMULL/no-PMULL feature combinations, and comparison to generic tables.

## Read Coverage

Source read size: 357 lines, 9848 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc32-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/arm64/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc32.h` dispatches arm64 CRC32, CRC32C, and big-endian CRC32 between generic table implementations, single-stream CRC instructions, and four-way PMULL-combined long-buffer routines.

## Important APIs, Types, and Functions

It declares six assembly functions for single-stream and four-way CRC paths, defines `min_len = 1024`, and provides inline `crc32_le_arch`, `crc32c_arch`, `crc32_be_arch`, and `crc32_optimizations_arch`.

## Control Flow

Each arch wrapper first checks `ARM64_HAS_CRC32`; if absent it calls the generic base function. For buffers at least 1024 bytes, PMULL feature present, and SIMD allowed, it enters `scoped_ksimd()`, processes the rounded-down 64-byte multiple with the four-way routine, advances the pointer, and returns early if no tail remains. Tails and smaller buffers use the single-stream hardware CRC function.

## State and Persistence Behavior

No global mutable state is defined here; runtime feature state is supplied by arm64 alternatives/cpufeature.

## Dependencies and Integration Points

Dependencies include arm64 alternatives, cpufeature, SIMD helpers, generic CRC base functions, and assembly functions in `arm64/crc32-core.S`.

## Risks and Edge Cases

The wrapper must not enter SIMD code when `may_use_simd()` is false. The four-way path must process only full 64-byte chunks and then correctly handle tail bytes. Optimization flags report CRC32 support even when PMULL is absent because single-stream acceleration still exists.

## Test Signals

Signals include generic fallback when CRC32 is absent, hardware CRC path for short buffers, four-way path for >=1024 bytes, tail processing after four-way calls, BE CRC vectors, and `crc32_optimizations()` output.

## Read Coverage

Source read size: 85 lines, 2168 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc64-neon-inner.c -->
# sources/distributed-fs/ceph-client/lib/crc/arm64/crc64-neon-inner.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc64-neon-inner.c` implements the inner arm64 NEON/PMULL routine for accelerated CRC64-NVME over 16-byte chunks.

## Important APIs, Types, and Functions

The visible function is `crc64_nvme_arm64_c(u64 crc, const u8 *p, size_t len)`. Helpers are `pmull64`, `pmull64_high`, and `pmull64_hi_lo`. Constants `fold_consts_val` and `bconsts_val` hold polynomial reduction values.

## Control Flow

The function loads fold constants and initializes a 128-bit vector with the incoming CRC. It xors each 16-byte block into the accumulator, folds the previous accumulator with carry-less multiplication while more blocks remain, then multiplies the final 128-bit value by `x^64`, reduces it back to 128 bits, performs Barrett reduction using `bconsts`, and returns the high lane as the reflected CRC state.

## State and Persistence Behavior

Only read-only constants are stored. All CRC state is local vector state. The caller owns complementing and tail processing.

## Dependencies and Integration Points

The file depends on arm64 NEON intrinsics and is compiled with FPU/crypto flags by the CRC Makefile. It integrates with `arm64/crc64.h`, which checks PMULL and SIMD availability and handles generic tails.

## Risks and Edge Cases

The function assumes the length is a nonzero 16-byte multiple selected by the wrapper. It uses kernel-mode SIMD, so wrong compile flags or missing SIMD guards would be unsafe. Constants are specific to the NVME reflected CRC64 polynomial, not ECMA big-endian CRC64.

## Test Signals

Signals include CRC64-NVME known vectors, lengths 16, 32, 128, and non-multiple tails through the wrapper, generic equivalence, PMULL feature gating, and build verification that FPU flags are applied only to this object.

## Read Coverage

Source read size: 65 lines, 1714 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc64-neon-inner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc64.h -->
# sources/distributed-fs/ceph-client/lib/crc/arm64/crc64.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc64.h` dispatches arm64 CRC64 support, accelerating CRC64-NVME with PMULL while leaving big-endian ECMA CRC64 on the generic path.

## Important APIs, Types, and Functions

It declares `crc64_nvme_arm64_c`, defines `crc64_be_arch` as `crc64_be_generic`, and provides inline `crc64_nvme_arch`.

## Control Flow

For CRC64-NVME, the wrapper checks for length at least 128 bytes, PMULL feature, and allowed SIMD. It processes the 16-byte-aligned prefix with `crc64_nvme_arm64_c()` under `scoped_ksimd()`, advances the pointer, leaves a 0..15 byte tail, and finishes the tail with `crc64_nvme_generic()`. Big-endian CRC64 always uses generic.

## State and Persistence Behavior

No persistent state is defined. Feature state comes from arm64 cpufeature.

## Dependencies and Integration Points

Dependencies include arm64 cpufeature, SIMD helpers, min/max and size headers, the NEON inner C function, and generic CRC64 functions in `crc64-main.c`.

## Risks and Edge Cases

Only the NVME variant is accelerated; callers must not expect ECMA CRC64 acceleration. The wrapper must preserve the generic complementing convention from `crc64-main.c`. SIMD must not be used in disallowed contexts.

## Test Signals

Signals include CRC64-NVME vectors around the 128-byte threshold, tails 1..15, PMULL absent fallback, `may_use_simd()` false fallback, and ECMA CRC64 generic behavior.

## Read Coverage

Source read size: 28 lines, 612 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/arm64/crc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc-ccitt.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc-ccitt.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc-ccitt.c` implements the table-driven CRC-CCITT variant used by kernel users of `<linux/crc-ccitt.h>`.

## Important APIs, Types, and Functions

The exported symbols are `crc_ccitt_table[256]` and `crc_ccitt(u16 crc, u8 const *buffer, size_t len)`.

## Control Flow

The function iterates over the buffer and updates the running CRC with `crc_ccitt_byte()`, which indexes the exported table. The table represents the reflected 0x8408 form of the CRC-CCITT polynomial.

## State and Persistence Behavior

The table is read-only module/kernel data. CRC state is caller-supplied and returned; no global mutable state exists.

## Dependencies and Integration Points

Dependencies include `linux/crc-ccitt.h`, module metadata, and export support. Drivers and protocols use the exported function or table for incremental checksums.

## Risks and Edge Cases

Variant naming is easy to confuse with ITU-T/X.25 forms; callers must supply the correct seed and final xor convention. The function assumes `buffer` is valid for `len`.

## Test Signals

Signals include known CRC-CCITT vectors, incremental update equivalence, zero-length behavior, exported table access, and module build/load coverage.

## Read Coverage

Source read size: 66 lines, 2984 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc-ccitt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc-itu-t.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc-itu-t.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc-itu-t.c` implements table-driven CRC ITU-T V.41 using polynomial 0x1021.

## Important APIs, Types, and Functions

The exported symbols are `crc_itu_t_table[256]` and `crc_itu_t(u16 crc, const u8 *buffer, size_t len)`.

## Control Flow

The function loops over bytes and updates the running CRC through `crc_itu_t_byte()`, which uses the exported table.

## State and Persistence Behavior

The lookup table is read-only data. The running CRC is provided and returned by value.

## Dependencies and Integration Points

Dependencies include `linux/crc-itu-t.h`, module metadata, and export support. Kernel users select `CRC_ITU_T` when they need this V.41 polynomial.

## Risks and Edge Cases

This implementation is a specific polynomial/orientation variant; callers must not substitute it for other 16-bit CRCs. Seed/finalization conventions remain caller-owned.

## Test Signals

Signals include ITU-T known vectors, zero-length return of the input CRC, chunked-update equivalence, and exported table visibility.

## Read Coverage

Source read size: 68 lines, 2829 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc-itu-t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc-t10dif-main.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc-t10dif-main.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc-t10dif-main.c` provides the generic CRC-T10DIF implementation and architecture dispatch point for SCSI/Data Integrity Field CRC16.

## Important APIs, Types, and Functions

The main exported API is `crc_t10dif_update(u16 crc, const u8 *p, size_t len)`. Internal data/functionality includes `t10_dif_crc_table[256]`, `crc_t10dif_generic()`, optional inclusion of `$(SRCARCH)/crc-t10dif.h`, and optional `crc_t10dif_mod_init()` when the arch header defines `crc_t10dif_mod_init_arch`.

## Control Flow

The generic helper iterates bytes with the T10 polynomial table, shifting the CRC high byte into the table index. If architecture optimization is enabled, the arch header defines `crc_t10dif_arch`; otherwise it aliases to generic. The exported update function simply dispatches to `crc_t10dif_arch`. Optional init calls the arch feature setup at subsys init.

## State and Persistence Behavior

The generic table is read-only. Runtime mutable state, if any, is supplied by architecture static keys in included headers. CRC state is passed by value.

## Dependencies and Integration Points

Dependencies include `linux/crc-t10dif.h`, module exports, and architecture headers for ARM, ARM64, PPC, RISCV, or X86 when selected. Storage stacks use this CRC for protection information.

## Risks and Edge Cases

Architecture wrappers must exactly match generic output for all seeds and lengths. Init ordering must enable static keys without breaking early callers, which still need generic fallback. This CRC variant is not interchangeable with other CRC16 forms.

## Test Signals

Signals include CRC-T10DIF known vectors, incremental/chunked equivalence, generic-vs-arch comparison, feature-disabled fallback, and KUnit coverage across selected architectures.

## Read Coverage

Source read size: 89 lines, 3374 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc-t10dif-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc16.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc16.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc16.c` implements a table-driven CRC-16 using polynomial 0x8005.

## Important APIs, Types, and Functions

The exported API is `crc16(u16 crc, const u8 *p, size_t len)`. The file owns a static `crc16_table[256]`.

## Control Flow

The function iterates through each byte, indexes the table with `(crc & 0xff) ^ *p`, shifts the CRC right by 8, xors the table value, and returns the final CRC.

## State and Persistence Behavior

The table is read-only static data. CRC state is caller-provided and returned by value.

## Dependencies and Integration Points

Dependencies include `linux/crc16.h`, module metadata, and export support. Kernel modules select `CRC16` to use this helper.

## Risks and Edge Cases

CRC16 variants differ by polynomial reflection, seed, and final xor; callers must use the matching convention. The buffer pointer must be valid for `len`.

## Test Signals

Signals include known CRC16 vectors, zero-length behavior, incremental equivalence, and module export coverage.

## Read Coverage

Source read size: 65 lines, 2768 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc32-main.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc32-main.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc32-main.c` provides generic table-driven CRC32, big-endian CRC32, and CRC32C, and dispatches to architecture accelerators when configured.

## Important APIs, Types, and Functions

Exported APIs are `crc32_le`, `crc32_be`, `crc32c`, and when arch support is enabled `crc32_optimizations`. Internal generic helpers are `crc32_le_base`, `crc32_be_base`, and `crc32c_base`. It includes generated `crc32table.h` for `crc32table_le`, `crc32table_be`, and `crc32ctable_le`.

## Control Flow

Each generic helper loops byte-by-byte through the appropriate lookup table and shift direction. With `CONFIG_CRC32_ARCH`, the file includes `$(SRCARCH)/crc32.h`, which defines `crc32_*_arch` wrappers and optimization reporting. Without arch support, those names alias to the base helpers. Optional module init delegates to arch static-key setup.

## State and Persistence Behavior

Generated lookup tables are read-only. Architecture headers may define static keys. CRC state is passed and returned by value.

## Dependencies and Integration Points

Dependencies include generated host-program output, `linux/crc32.h`, module exports, and architecture headers for ARM, ARM64, LoongArch, MIPS, PPC, RISCV, S390, SPARC, or X86. Many filesystems, networking code, and storage protocols use these helpers.

## Risks and Edge Cases

The generic functions do not perform final xor; callers own seed/finalization conventions. Architecture wrappers must preserve exact semantics for LE, BE, and CRC32C variants. Generated table freshness is required for correct builds.

## Test Signals

Signals include standard CRC32/CRC32C vectors, BE vectors, zero and chunked updates, generated-table rebuilds, arch fallback/acceleration comparisons, `crc32_optimizations()` flags, and KUnit benchmark coverage.

## Read Coverage

Source read size: 105 lines, 2763 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc32-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc4.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc4.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc4.c` computes a 4-bit CRC over a caller-supplied integer value using polynomial `0b10111`.

## Important APIs, Types, and Functions

The exported GPL API is `crc4(uint8_t c, uint64_t x, int bits)`. The file owns a 16-entry nibble table `crc4_tab`.

## Control Flow

The function masks bits above the requested width, rounds the bit count up to a nibble boundary, then processes four-bit nibbles from most significant to least significant by xoring the current CRC with the nibble and indexing `crc4_tab`.

## State and Persistence Behavior

The nibble table is read-only. CRC state is carried in the input/output byte.

## Dependencies and Integration Points

Dependencies include `linux/crc4.h`, module metadata, and export support. Callers use it for compact hardware/protocol fields rather than byte buffers.

## Risks and Edge Cases

`(1ull << bits)` is undefined for `bits >= 64`, so callers must constrain bit counts. Left-aligned interpretation must match protocol expectations. The returned CRC is only four bits wide but stored in a byte.

## Test Signals

Signals include known polynomial vectors, bit widths not divisible by four, zero bits, maximum safe bit width, initial CRC variation, and caller validation for 64-bit widths.

## Read Coverage

Source read size: 45 lines, 1029 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc64-main.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc64-main.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc64-main.c` implements generic CRC64 ECMA big-endian and CRC64-NVME reflected variants, with optional architecture dispatch.

## Important APIs, Types, and Functions

Exported GPL APIs are `crc64_be(u64 crc, const void *p, size_t len)` and `crc64_nvme(u64 crc, const void *p, size_t len)`. Internal generic helpers are `crc64_be_generic` and `crc64_nvme_generic`. The file includes generated `crc64table.h`.

## Control Flow

The ECMA helper shifts left and indexes `crc64table` with the high byte. The NVME helper shifts right and indexes `crc64nvmetable` with the low byte. With architecture support, `$(SRCARCH)/crc64.h` defines arch wrappers; otherwise they alias to generic. The exported NVME function complements the input and output around `crc64_nvme_arch()`.

## State and Persistence Behavior

Lookup tables are generated read-only data. Arch dispatch may use static feature state in included headers. Per-call CRC state is by value.

## Dependencies and Integration Points

Dependencies include `linux/crc64.h`, generated table headers, module exports, and arch implementations for ARM64, RISCV, or X86 when selected. NVME and other storage code consume the reflected variant.

## Risks and Edge Cases

ECMA and NVME variants differ in polynomial and bit order. The complement convention for NVME must remain at the exported wrapper boundary. Architecture acceleration currently may cover only one variant, as arm64 accelerates NVME but not ECMA.

## Test Signals

Signals include ECMA and NVME known vectors, zero-length complement behavior for NVME, chunked equivalence, generated table regeneration, and generic-vs-arch comparisons.

## Read Coverage

Source read size: 93 lines, 2654 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc64-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc7.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc7.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc7.c` implements big-endian CRC7, commonly used by MMC/SD style protocols.

## Important APIs, Types, and Functions

The exported API is `crc7_be(u8 crc, const u8 *buffer, size_t len)`. The file owns `crc7_be_syndrome_table[256]`.

## Control Flow

The function iterates through the input bytes and updates the left-aligned CRC with `crc7_be_syndrome_table[crc ^ *buffer++]`.

## State and Persistence Behavior

The table is read-only static data. CRC state is caller-supplied and returned in left-aligned byte form with the low bit unused.

## Dependencies and Integration Points

Dependencies include `linux/crc7.h`, module metadata, and export support. Protocol code selects `CRC7` to use this helper.

## Risks and Edge Cases

The CRC is left-aligned in the returned byte; callers expecting right-aligned CRC7 must shift appropriately. Variant seed/final bit handling remains caller-owned.

## Test Signals

Signals include known CRC7 command vectors, zero-length return, chunked update equivalence, left-alignment checks, and module export coverage.

## Read Coverage

Source read size: 73 lines, 2566 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc8.c -->
# sources/distributed-fs/ceph-client/lib/crc/crc8.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc8.c` provides generic CRC8 table population and update helpers, supporting both MSB-first and LSB-first polynomial table construction.

## Important APIs, Types, and Functions

Exported functions are `crc8_populate_msb`, `crc8_populate_lsb`, and `crc8`. Tables are caller-owned arrays of `CRC8_TABLE_SIZE` bytes.

## Control Flow

The populate helpers construct a 256-entry table by repeated doubling/xor of the current polynomial term, one in reverse bit order from `0x80`, the other in regular bit order from `1`. `crc8()` then iterates over input bytes and updates `crc = table[(crc ^ *pdata++) & 0xff]`.

## State and Persistence Behavior

No global table is stored; callers allocate and persist the table they need. The CRC accumulator is passed by value.

## Dependencies and Integration Points

Dependencies include `linux/crc8.h`, printk/module metadata, and exports. Drivers with custom CRC8 polynomials call a populate helper once and reuse the table for data updates.

## Risks and Edge Cases

Callers must choose the correct bit order and polynomial. Using an uninitialized or transient table produces wrong CRCs. The helper does not protect concurrent table population and use.

## Test Signals

Signals include table generation for known MSB/LSB polynomials, CRC8 known vectors, zero-length behavior, incremental equivalence, and callers caching tables safely.

## Read Coverage

Source read size: 87 lines, 2504 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/crc8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/gen_crc32table.c -->
# sources/distributed-fs/ceph-client/lib/crc/gen_crc32table.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/gen_crc32table.c` is a host build program that generates the CRC32 lookup-table header consumed by `crc32-main.c`.

## Important APIs, Types, and Functions

Important functions are `crc32init_le_generic`, `crc32init_le`, `crc32cinit_le`, `crc32init_be`, `output_table`, and `main`. Generated arrays are `crc32table_le`, `crc32table_be`, and `crc32ctable_le`.

## Control Flow

The program initializes little-endian CRC32 and CRC32C tables from `CRC32_POLY_LE` and `CRC32C_POLY_LE`, initializes the big-endian table from `CRC32_POLY_BE`, prints a generated-file banner, and emits three cacheline-aligned static `u32` arrays in C syntax.

## State and Persistence Behavior

State is process-local table arrays. Persistent output is written to stdout and redirected by Kbuild to `crc32table.h`.

## Dependencies and Integration Points

Dependencies include the host C library, `crc32poly.h`, generated `autoconf.h`, and Kbuild hostprog rules in the CRC Makefile.

## Risks and Edge Cases

Generated output must match kernel C types and cacheline alignment macros. Any polynomial constant change affects all generic CRC32 users. Host/compiler differences should not change deterministic output.

## Test Signals

Signals include regenerating `crc32table.h`, compiling `crc32-main.o`, diffing known table output, and CRC32/CRC32C KUnit vectors using the generated tables.

## Read Coverage

Source read size: 89 lines, 2032 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/gen_crc32table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/gen_crc64table.c -->
# sources/distributed-fs/ceph-client/lib/crc/gen_crc64table.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/gen_crc64table.c` is a host build program that generates lookup tables for generic CRC64 ECMA and CRC64-NVME.

## Important APIs, Types, and Functions

Important functions are `generate_reflected_crc64_table`, `generate_crc64_table`, `output_table`, `print_crc64_tables`, and `main`. Constants are `CRC64_ECMA182_POLY` and `CRC64_NVME_POLY`; generated arrays are `crc64table` and `crc64nvmetable`.

## Control Flow

The program fills the ECMA table in MSB-first order and the NVME table in reflected LSB-first order, then prints a generated-file banner, required includes, and two cacheline-aligned `u64` arrays.

## State and Persistence Behavior

Only process-local arrays are mutated. Kbuild redirects stdout to the persistent generated header `crc64table.h`.

## Dependencies and Integration Points

Dependencies include host `stdio.h` and `inttypes.h`. The Makefile builds and runs this host program before compiling `crc64-main.o`.

## Risks and Edge Cases

The two polynomial orientations are different; swapping generator functions or constants would silently corrupt one variant. Output formatting must remain valid kernel C and deterministic.

## Test Signals

Signals include generated header rebuild, known CRC64 ECMA and NVME vectors, deterministic output diffs, and successful compilation of `crc64-main.c` after clean builds.

## Read Coverage

Source read size: 88 lines, 1864 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/gen_crc64table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/loongarch/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/loongarch/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/loongarch/crc32.h` dispatches CRC32 and CRC32C to LoongArch hardware CRC instructions when available, otherwise falling back to generic tables.

## Important APIs, Types, and Functions

It defines inline assembly macros `_CRC32`, `CRC32`, and `CRC32C`, static key `have_crc32`, and inline functions `crc32_le_arch`, `crc32c_arch`, `crc32_mod_init_arch`, and `crc32_optimizations_arch`. Big-endian CRC32 aliases to generic.

## Control Flow

Each wrapper checks `have_crc32`; if false, it calls the generic base function. If true, it processes unaligned little-endian chunks in 64-bit, 32-bit, 16-bit, and 8-bit widths with `get_unaligned_le*()` and LoongArch `crc` or `crcc` instructions. Init enables the static key when `cpu_has_crc32`.

## State and Persistence Behavior

Runtime feature state is a read-only-after-init static key. No per-call state persists beyond the returned CRC.

## Dependencies and Integration Points

Dependencies include LoongArch CPU feature macros, unaligned access helpers, generic CRC32 base functions, and inclusion from `crc32-main.c`.

## Risks and Edge Cases

Hardware instructions are little-endian CRC32/CRC32C only; BE falls back. Inline assembly clobbers memory and must match instruction operand order. Feature detection must not enable instructions on unsupported CPUs.

## Test Signals

Signals include hardware/generic equivalence for CRC32 and CRC32C, unaligned buffers, all tail widths, no-feature fallback, and `crc32_optimizations()` flags.

## Read Coverage

Source read size: 115 lines, 2335 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/loongarch/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/mips/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/mips/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/mips/crc32.h` dispatches CRC32 and CRC32C to optional MIPSr6 CRC instructions, with assembler compatibility for toolchains lacking CRC mnemonic support.

## Important APIs, Types, and Functions

Important macros are `_ASM_SET_CRC`, `_ASM_UNSET_CRC`, `__CRC32`, `_CRC32_crc32*`, `_CRC32_crc32c*`, `CRC32`, and `CRC32C`. It defines static key `have_crc32` and inline wrappers `crc32_le_arch`, `crc32c_arch`, `crc32_mod_init_arch`, and `crc32_optimizations_arch`. Big-endian CRC32 uses generic.

## Control Flow

If the static key is disabled, wrappers call generic base functions. With hardware support, 64-bit builds process 64-bit chunks first, then 32/16/8 tails; 32-bit builds process 32-bit chunks, then smaller tails. Inline assembly emits CRC opcodes either through assembler macros or explicit instruction encodings. Init enables the static key when `MIPS_CRC32` is present.

## State and Persistence Behavior

The only persistent state is the runtime static key. CRC accumulators are local.

## Dependencies and Integration Points

Dependencies include MIPS CPU feature detection, MIPS register/opcode assembler helpers, unaligned little-endian loads, generic CRC base functions, and inclusion by `crc32-main.c`.

## Risks and Edge Cases

Toolchain-support fallbacks must encode the exact CRC opcodes. 32-bit and 64-bit chunk paths must advance pointers consistently. Hardware support is LE CRC32/CRC32C only; BE remains generic.

## Test Signals

Signals include builds with and without `TOOLCHAIN_SUPPORTS_CRC`, 32-bit and 64-bit MIPS configs, hardware/generic vector equivalence, unaligned buffers, tails, and feature flag reporting.

## Read Coverage

Source read size: 162 lines, 4068 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/mips/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-t10dif.h -->
# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-t10dif.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-t10dif.h` dispatches CRC-T10DIF on PowerPC to VMX/VPMSUM acceleration when vector crypto is available.

## Important APIs, Types, and Functions

It defines `VMX_ALIGN`, `VMX_ALIGN_MASK`, `VECTOR_BREAKPOINT`, static key `have_vec_crypto`, assembly declaration `__crct10dif_vpmsum`, inline `crc_t10dif_arch`, and `crc_t10dif_mod_init_arch`.

## Control Flow

The wrapper falls back to generic if length is below threshold plus alignment, vector crypto is unavailable, or SIMD use is disallowed. Otherwise it processes a generic prealignment prefix to 16-byte alignment, disables preemption and page faults, enables kernel Altivec, calls `__crct10dif_vpmsum()` on the aligned multiple after shifting CRC placement, disables Altivec, then processes any tail generically.

## State and Persistence Behavior

Feature state is stored in a read-only-after-init static key. Per-call vector state is protected by explicit Altivec enable/disable and preemption/pagefault guards.

## Dependencies and Integration Points

Dependencies include PowerPC SIMD/Altivec context helpers, CPU feature flags `CPU_FTR_ARCH_207S` and `PPC_FEATURE2_VEC_CRYPTO`, generic T10DIF, and VPMSUM assembly.

## Risks and Edge Cases

Alignment and CRC bit placement (`crc <<= 16`/`>>= 16`) are critical. SIMD context must be protected exactly or kernel vector state can be corrupted. The wrapper must not pass unaligned or tail bytes to the assembly routine.

## Test Signals

Signals include generic equivalence over prealigned, unaligned, threshold, and tail lengths; vector-feature fallback; preemption/pagefault guard checks; and KUnit T10DIF vectors on PPC64 with vector crypto.

## Read Coverage

Source read size: 70 lines, 1740 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-t10dif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-vpmsum-template.S -->
# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-vpmsum-template.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-vpmsum-template.S` is a parameterized PowerPC VPMSUM assembly template for accelerated CRC algorithms. Including files define constants, reflection mode, and `CRC_FUNCTION_NAME`.

## Important APIs, Types, and Functions

The template emits one function named by `CRC_FUNCTION_NAME`. Key constants/macros include `MAX_SIZE`, `BYTESWAP_DATA`, vector offset registers, `VPERM`, and labels for warm-up, main loop, cool-down, short input, Barrett reduction, and output.

## Control Flow

The function saves nonvolatile GPRs and VMX registers, moves the initial CRC into vector state, conditionally loads byte-swap masks, and chooses a short path for inputs below 256 bytes. The main path processes up to 32 KiB at a time in eight parallel 16-byte lanes to reduce data to 1024 bits, folds the accumulated lanes with constants and optional tails, xors lanes together, then performs reflected or non-reflected Barrett reduction. The short path reduces smaller aligned inputs with `.short_constants`, handles partial lane counts through branch labels, then shares the Barrett/output code.

## State and Persistence Behavior

The template itself owns no concrete constants; includers provide `.constants`, `.short_constants`, and `.barrett_constants`. Runtime state is in VMX/GPR registers, restored before return.

## Dependencies and Integration Points

Dependencies include `asm/ppc_asm.h`, `asm/ppc-opcode.h`, VPMSUM instructions, and includer-defined polynomial constants. It integrates with PPC CRC32C and T10DIF assembly glue.

## Risks and Edge Cases

Because this is a template, macro definitions must match the polynomial orientation and output convention. Register save/restore, endian byte swapping, reflected vs non-reflected Barrett reduction, and tail lane dispatch are all high-risk. The caller must guarantee 16-byte alignment and length multiple requirements documented by the template.

## Test Signals

Signals include includer-specific CRC vectors, short and long inputs, 32 KiB boundary loops, all tail lane counts, big- and little-endian PPC builds, reflected and non-reflected modes, and VMX register preservation checks.

## Read Coverage

Source read size: 746 lines, 14068 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-vpmsum-template.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32.h` dispatches PowerPC CRC32C to VPMSUM vector crypto acceleration. Plain little- and big-endian CRC32 remain generic on this architecture header.

## Important APIs, Types, and Functions

It defines `VMX_ALIGN`, `VMX_ALIGN_MASK`, `VECTOR_BREAKPOINT`, static key `have_vec_crypto`, assembly declaration `__crc32c_vpmsum`, inline `crc32c_arch`, `crc32_mod_init_arch`, and `crc32_optimizations_arch`. `crc32_le_arch` and `crc32_be_arch` alias to generic base functions.

## Control Flow

`crc32c_arch()` falls back to generic for short buffers, missing vector crypto, or disallowed SIMD. Otherwise it consumes a generic prealignment prefix, disables preemption and page faults, enables kernel Altivec, calls `__crc32c_vpmsum()` on the aligned multiple, disables Altivec, then finishes the tail generically. Init enables the static key on POWER8-class vector crypto support.

## State and Persistence Behavior

Persistent state is the static key. Vector state is protected per call by preemption/pagefault disabling and Altivec context management.

## Dependencies and Integration Points

Dependencies include PowerPC SIMD context helpers, feature flags, generic CRC32C base code, and `powerpc/crc32c-vpmsum_asm.S`.

## Risks and Edge Cases

Only CRC32C is accelerated, so optimization reporting must not claim CRC32 LE/BE. Alignment splitting and tail handling must preserve generic semantics. SIMD context misuse can corrupt vector state or fault in disabled contexts.

## Test Signals

Signals include CRC32C generic equivalence across unaligned, threshold, and tail lengths; fallback without vector crypto; `crc32_optimizations()` reporting only CRC32C; and PPC vector context stress tests.

## Read Coverage

Source read size: 70 lines, 1757 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32c-vpmsum_asm.S -->
# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32c-vpmsum_asm.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32c-vpmsum_asm.S` supplies the concrete PowerPC VPMSUM constants and function instantiation for accelerated CRC32C.

## Important APIs, Types, and Functions

The emitted function is `__crc32c_vpmsum`, created by defining `CRC_FUNCTION_NAME __crc32c_vpmsum`, defining `REFLECT`, and including `crc-vpmsum-template.S`. The file provides `.byteswap_constant`, a large `.constants` table for reducing large inputs, `.short_constants` for 1024-2048 bit reductions, and `.barrett_constants` for reflected CRC32C reduction.

## Control Flow

Runtime control flow is in the included template. This file contributes the constants that let the template reduce chunks of CRC32C data using reflected polynomial arithmetic, byte-swap as needed, process large aligned multiples in parallel lanes, handle short inputs, and perform final Barrett reduction.

## State and Persistence Behavior

All data in this file is read-only assembly constant data. There is no mutable state beyond the included function's register-local execution.

## Dependencies and Integration Points

It depends on the VPMSUM template and the PowerPC CRC32 dispatch header. `powerpc/crc32.h` calls `__crc32c_vpmsum()` only after alignment, length, feature, and SIMD-context checks.

## Risks and Edge Cases

The constant table is mathematically tied to the CRC32C reflected polynomial; any value corruption causes silent checksum failures. Because the template is included after data definitions, label names and section layout must remain compatible. The function assumes caller-enforced 16-byte alignment and length multiple.

## Test Signals

Signals include CRC32C known vectors, generic-vs-VPMSUM equivalence over large and short aligned inputs, endian builds with byte-swap behavior, table integrity checks through KUnit, and wrapper tests for unaligned/tail bytes.

## Read Coverage

Source read size: 842 lines, 27724 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32c-vpmsum_asm.S -->
