# Research: subset-b-006106

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/scatterlist.c -->
# sources/distributed-fs/ceph-client/lib/scatterlist.c

## Purpose
Implements the kernel scatterlist utility layer: counting and locating SG entries, allocating and freeing chained `sg_table` storage, building SG lists from pages, iterating mapped pages, copying or zeroing linear data through SG entries, and extracting `iov_iter` sources into SG tables. It is generic infrastructure used by block, crypto, networking, DMA, and filesystem paths that need non-contiguous memory represented as a single I/O vector.

## APIs, Control Flow, and State
Major exports include `sg_nents()`, `sg_nents_for_len()`, `sg_nents_for_dma()`, `sg_last()`, `sg_init_table()`, `sg_init_one()`, `__sg_alloc_table()`, `sg_alloc_table()`, `__sg_free_table()`, `sg_free_table()`, `sg_alloc_append_table_from_pages()`, `sg_alloc_table_from_pages_segment()`, optional `sgl_alloc*()`/`sgl_free*()` page-owning helpers, page iterators `__sg_page_iter_start()`, `__sg_page_iter_next()`, `__sg_page_iter_dma_next()`, mapping iterator helpers `sg_miter_start()`, `sg_miter_skip()`, `sg_miter_next()`, `sg_miter_stop()`, copy helpers `sg_copy_buffer()`, `sg_copy_from_buffer()`, `sg_copy_to_buffer()`, partial-copy variants, `sg_zero_buffer()`, and `extract_iter_to_sg()`.

Control flow is mostly linear traversal over chained scatterlists. Allocation splits large tables into chunks, reserving the last entry of non-final chunks as a chain pointer, and unwinds partially allocated state with the same `max_ents` contract. Append-table construction merges physically contiguous pages when PFNs and zone-device pgmaps allow it, grows chained chunks on demand, and marks the final SG only when no `left_pages` remain. Mapping iteration advances page by page, maps the current page with `kmap_atomic()`, `kmap_local_page()`, or `kmap()`, and requires `sg_miter_stop()` to flush and unmap. `extract_iter_to_sg()` dispatches by iterator type: user/iovec pages are extracted and pinned, bvec/kvec/folioq/xarray entries are referenced without pinning, and unsupported iterator classes fail with `-EIO`.

Persistent state is not stored globally, but SG tables embed ownership state in `sgl`, `nents`, `orig_nents`, chain markers, DMA length/address fields, append `prv`/`total_nents`, and iterator progress fields. User-page extraction mutates the source `iov_iter` and may leave pages pinned for caller-directed cleanup.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/scatterlist.h`, slab/page allocation, kmemleak, highmem mapping, bvec/uio/folio queue helpers, xarray RCU traversal, and architecture SG chaining support. Integration points include DMA mapping callers, block layer bio handling, Ceph client network and crypto buffers, filesystem folios, and any code using `sg_table` as an I/O descriptor.

Risks are high around chain entry accounting, mismatched allocation/free `max_ents`, missing end markers, length overflow, improper DMA-length versus physical-length use, failure to stop mapping iterators, stale cache data if `SG_MITER_TO_SG` pages are not flushed, pinned user pages not being unpinned on failure, and xarray or folioq iterator state races. Test signals include scatterlist KUnit/selftests, DMA map/unmap tests, block and crypto SG stress, highmem coverage, fault injection during chained allocation, usercopy extraction failure paths, and I/O workloads using partial offsets and multi-page unaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/scatterlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/seq_buf.c -->
# sources/distributed-fs/ceph-client/lib/seq_buf.c

## Purpose
Provides bounded formatting helpers for `struct seq_buf`, a small reusable descriptor for writing text or raw bytes into a fixed buffer. It bridges formatted printing, binary printf replay, path rendering, hex dumps, printk emission, and userspace copying without requiring a live `seq_file`.

## APIs, Control Flow, and State
Important APIs are `seq_buf_print_seq()`, `seq_buf_vprintf()`, `seq_buf_printf()`, `seq_buf_do_printk()`, optional `seq_buf_bprintf()`, `seq_buf_puts()`, `seq_buf_putc()`, `seq_buf_putmem()`, `seq_buf_putmem_hex()`, `seq_buf_path()`, `seq_buf_to_user()`, and `seq_buf_hex_dump()`. All writers check available capacity through `s->len` and `s->size`, advance `s->len` on success, and set the seq_buf overflow state on truncation. `seq_buf_do_printk()` turns the buffer into a NUL-terminated string and prints it line by line with a caller-supplied log level. `seq_buf_path()` borrows writable space with `seq_buf_get_buf()`, renders a dentry path with `d_path()`, escapes via `mangle_path()`, then commits the actual byte count. `seq_buf_to_user()` copies a requested subrange and returns `-EBUSY` when the requested start is already past the buffer.

The only persistent state is the caller-owned `struct seq_buf`: buffer pointer, size, current length, and overflow marker. No global state is created.

## Dependencies, Integration, Risks, and Tests
Depends on printk, seq_file, vsnprintf/bstr_printf, string/hex helpers, dcache path rendering, and uaccess. Integration points include tracing, debugfs/procfs emitters, diagnostics that collect output before printing, and sysfs-style buffered output. Risks include off-by-one capacity handling, assuming all functions NUL-terminate raw `putmem()` content, failing to inspect overflow, using `seq_buf_to_user()` as if short copies are impossible, and path rendering with too-small buffers. Test signals include seq_buf KUnit coverage, trace output tests, hex dump comparisons, path escaping tests, copy_to_user fault injection, and boundary cases where `s->len == s->size - 1` or `s->size == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/seq_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sg_pool.c -->
# sources/distributed-fs/ceph-client/lib/sg_pool.c

## Purpose
Implements small mempool-backed scatterlist chunk pools used by `sg_alloc_table_chained()` for callers that need atomic allocation of chained SG tables. It avoids direct potentially failing slab allocation in I/O paths by pre-creating per-size slab caches and mempools.

## APIs, Control Flow, and State
The exported APIs are `sg_alloc_table_chained()` and `sg_free_table_chained()`. Internal `struct sg_pool` records a chunk size, cache name, slab cache, and mempool. `sg_pool_index()` chooses the smallest configured pool for a requested number of entries, bounded by `SG_CHUNK_SIZE`. Allocation delegates to `__sg_alloc_table()` with `SG_CHUNK_SIZE`, an optional caller-provided first chunk, `GFP_ATOMIC`, and `sg_pool_alloc()`. Freeing calls `__sg_free_table()` with the same chunk size and `sg_pool_free()` unless all entries fit in the caller-owned first chunk. `sg_pool_init()` creates slab caches named `sgpool-*` and two-element mempools during `subsys_initcall`.

State is global and persistent after boot: the `sg_pools[]` array, each `kmem_cache`, and each `mempool_t`. Individual tables own only their chained SG entries and header counts.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/scatterlist.h`, mempool, slab, and the generic scatterlist allocator/free implementation in `scatterlist.c`. It integrates with block and storage code that builds SG tables under atomic constraints. Risks include mismatched `nents_first_chunk` between allocation and free, `SG_CHUNK_SIZE` configuration outside expected bounds, leaking caller-owned first chunks, and expecting the pool to support more entries than its compile-time chunk size. Test signals include boot-time init failures, mempool exhaustion fault injection, chained allocation/free loops with different first-chunk sizes, and block-layer atomic allocation stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sg_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sg_split.c -->
# sources/distributed-fs/ceph-client/lib/sg_split.c

## Purpose
Splits an input scatterlist into multiple newly allocated scatterlists covering consecutive byte ranges. It supports both physical SG metadata and already DMA-mapped SG metadata, making it useful when a larger I/O vector must be divided into protocol or device-sized pieces.

## APIs, Control Flow, and State
The exported API is `sg_split()`. Internal `struct sg_splitter` tracks the first input SG for a split, number of output entries, skip offset in the first input entry, final-entry length, and allocated output SG pointer. `sg_calculate_split()` scans the input list, consumes an initial skip, walks split sizes, and records how many source entries each output needs. `sg_split()` first calculates physical layout with `sg_nents(in)`, allocates each output array, copies and adjusts physical SG fields in `sg_split_phys()`, then, if `in_mapped_nents` is non-zero, recalculates against `sg_dma_len()` and fills DMA address/length fields in `sg_split_mapped()`.

State is transient: allocated output SG arrays are returned to the caller, which must free them with `kfree()`. No global state exists.

## Dependencies, Integration, Risks, and Tests
Depends on scatterlist traversal, `sg_dma_address()`, `sg_dma_len()`, and slab allocation. Integration points include DMA-aware drivers and crypto/block/network paths that need segmented views of a larger SG list. Risks include invalid split sizes returning `-EINVAL`, mismatched physical and DMA segment counts after DMA mapping coalesces entries, off-by-one errors when a split boundary lands inside an SG entry, caller leaks on partial failure if outputs are not cleared, and callers forgetting that outputs are shallow copies of page references. Test signals include split-at-entry-boundary tests, split-inside-entry tests, skip beyond available data, mapped versus unmapped DMA length comparisons, and allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sg_split.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/siphash.c -->
# sources/distributed-fs/ceph-client/lib/siphash.c

## Purpose
Implements SipHash2-4 for keyed 64-bit pseudorandom hashing and HalfSipHash1-3 or SipHash1-3-derived 32-bit hashing for hash table use. These functions protect kernel hash tables and short keyed identifiers from collision attacks when callers use secret per-boot keys.

## APIs, Control Flow, and State
Exports include `__siphash_aligned()`, `__siphash_unaligned()`, `siphash_1u64()` through `siphash_4u64()`, `siphash_1u32()`, `siphash_3u32()`, `__hsiphash_aligned()`, `__hsiphash_unaligned()`, and `hsiphash_1u32()` through `hsiphash_4u32()`. Macros set up SipHash state from constants, xor the key, process full little-endian words with SipHash rounds, pack the tail bytes into the length-tagged final word, and run finalization rounds. Aligned variants are omitted on architectures with efficient unaligned access; unaligned variants use `get_unaligned_le*()`. On 64-bit, HalfSipHash uses the SipHash word engine for performance; on 32-bit, a native 32-bit HalfSipHash engine is used.

The file owns no persistent state. Security depends on caller-owned `siphash_key_t` or `hsiphash_key_t` lifetime and secrecy.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/siphash.h`, unaligned access helpers, endian conversion, and optional dcache word-at-a-time tail loading. Integration points include dcache, networking, hashtables, randomization-sensitive maps, and identifiers that need keyed hashing. Risks include using HalfSipHash where a secure PRF is required, reusing non-secret or predictable keys, endian/tail packing regressions, unaligned reads crossing inaccessible memory when architecture assumptions are wrong, and inconsistent 32-bit versus 64-bit expectations. Test signals include SipHash reference vectors, aligned/unaligned equivalence tests, tail-length coverage from 0 to 7 or 0 to 3 bytes, cross-endian builds, and collision-resistance stress on keyed hash tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/siphash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/smp_processor_id.c -->
# sources/distributed-fs/ceph-client/lib/smp_processor_id.c

## Purpose
Provides the DEBUG_PREEMPT implementation behind `smp_processor_id()` diagnostics. It detects callers that read CPU-local identity from preemptible context where migration could make the answer unstable.

## APIs, Control Flow, and State
Exports `debug_smp_processor_id()` and `__this_cpu_preempt_check()`, both routed through `check_preemption_disabled()`. The checker accepts contexts where CPU locality is valid: non-zero preempt count, interrupts disabled, per-CPU kernel threads, migration disabled, or early boot before scheduling. Otherwise it disables preemption without tracing, enters an instrumentation-safe region, rate-limits a BUG diagnostic, prints the caller and stack, then reenables preemption without rescheduling. It returns `raw_smp_processor_id()` regardless so the caller can continue.

There is no durable state beyond printk rate limiting and current task scheduler fields.

## Dependencies, Integration, Risks, and Tests
Depends on scheduler/preemption state, current task metadata, printk, stack dumping, noinstr constraints, and export support. Integration points are debug builds of per-CPU accessors and `this_cpu` checks. Risks include false positives if a new context type legitimately pins CPU locality but is not recognized, recursion through printk or tracing, and missing diagnostics if rate limiting suppresses repeated bugs. Test signals include DEBUG_PREEMPT boot tests, intentional misuse probes, noinstr/objtool validation, and scheduler migration tests that call CPU-local helpers under allowed and disallowed contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/smp_processor_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sort.c -->
# sources/distributed-fs/ceph-client/lib/sort.c

## Purpose
Implements the kernel generic in-place sort helpers. The algorithm is a non-recursive heapsort chosen for bounded O(n log n) worst-case behavior and low stack usage, with optimized swap paths for aligned element sizes.

## APIs, Control Flow, and State
Exports `sort_r()`, `sort_r_nonatomic()`, `sort()`, and `sort_nonatomic()`. `sort_r*()` accepts comparator and swap functions with a private pointer; `sort*()` wraps legacy comparators and swaps through `struct wrapper`. `__sort_r()` chooses a swap implementation when the caller does not provide one: 64-bit word swaps, 32-bit word swaps, or byte swaps based on element size and base alignment. The main loop first builds a heap using byte offsets, then repeatedly extracts the largest elements using a bottom-up sift that reduces comparator calls. The `_nonatomic` variants call `cond_resched()` inside the loop.

No persistent state is stored. The caller-provided array is mutated in place.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/sort.h`, type definitions, export support, and scheduler rescheduling for nonatomic variants. Integration points are any kernel subsystem sorting arrays without allocating temporary memory. Risks include invalid comparators that violate antisymmetry or transitivity, custom swap functions that do not preserve auxiliary state, zero element size, integer overflow in `num * size`, and using the atomic variant for very large arrays in sleepable contexts. Test signals include lib/sort selftests, randomized ordering tests, adversarial comparator tests, custom swap coverage, alignment-sensitive tests, and latency checks with `sort_r_nonatomic()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/stackdepot.c -->
# sources/distributed-fs/ceph-client/lib/stackdepot.c

## Purpose
Implements Stack Depot, a deduplicating storage service for kernel stack traces. It hashes stack frame arrays, stores unique records in page-sized pools, returns compact handles, optionally refcounts records, and exposes debug statistics.

## APIs, Control Flow, and State
Key APIs are `stack_depot_request_early_init()`, `stack_depot_early_init()`, `stack_depot_init()`, `stack_depot_save_flags()`, `stack_depot_save()`, `__stack_depot_get_stack_record()`, `stack_depot_fetch()`, `stack_depot_put()`, `stack_depot_print()`, `stack_depot_snprint()`, `stack_depot_set_extra_bits()`, and `stack_depot_get_extra_bits()`. Boot parameters `stack_depot_disable` and `stack_depot_max_pools` control availability and pool cap. Initialization allocates a hash table either through memblock in early boot or kvcalloc later, then allocates an array of pool pointers. Saving filters interrupt frames, hashes the stack, does a lockless RCU bucket lookup, optionally preallocates a pool, locks `pool_lock`, rechecks for duplicates, allocates or reuses a `stack_record`, publishes it with `list_add_rcu()`, and returns the encoded handle. Refcounted records can be put; zero-ref records leave the hash under RCU and enter an LRU-style freelist after an RCU grace cookie becomes reusable.

Persistent state includes `stack_table`, `stack_pools`, `new_pool`, `pools_num`, `pool_offset`, `free_stacks`, per-record handles/refcounts/hash entries, and approximate debugfs counters. Debugfs creates `stackdepot/stats` late in boot.

## Dependencies, Integration, Risks, and Tests
Depends on jhash, stacktrace filtering/printing, memblock, kvalloc, raw spinlocks, RCU, refcounting, KMSAN/KASAN hooks, debugfs, early params, and printk-deferred regions. Integration points include KASAN, KMSAN, page owner, leak detectors, allocation tracking, and any subsystem needing stable stack trace handles. Risks include disabled or failed initialization returning zero handles, pool exhaustion, corrupted handles indexing outside pool arrays, refcount imbalance causing use-after-put warnings, NMI best-effort lock failure, memory growth from unfiltered interrupt stacks, and RCU misuse when recycling records. Test signals include stackdepot KUnit/selftests, sanitizer boot tests, refcount get/put stress, debugfs counter inspection, handle extra-bit round trips, early and late init paths, NMI/context stress, and pool-limit fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/stackdepot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/stmp_device.c -->
# sources/distributed-fs/ceph-client/lib/stmp_device.c

## Purpose
Provides a reset helper for STMP-style hardware blocks, primarily used by ARM/Freescale i.MX/SoC drivers that expose soft-reset and clock-gate control bits at a register base.

## APIs, Control Flow, and State
The exported API is `stmp_reset_block(void __iomem *reset_addr)`. It manipulates `STMP_MODULE_SFTRST` and `STMP_MODULE_CLKGATE` through STMP set/clear register offsets. Control flow clears and polls soft reset, clears clock gate, sets soft reset, polls for clock gate to assert, clears and polls soft reset again, then clears and polls clock gate. `stmp_clear_poll_bit()` writes to the clear register, delays one microsecond, and spins up to a fixed timeout for the bit to clear. Failures log an error and return `-ETIMEDOUT`.

State is entirely device register state. The helper stores no kernel-global data.

## Dependencies, Integration, Risks, and Tests
Depends on MMIO `readl()`/`writel()`, `udelay()`, errno, and `linux/stmp_device.h` register offsets. Integration points are platform device drivers resetting STMP-compatible modules during probe, resume, or error recovery. Risks include passing the wrong register base, insufficient timeout for slow hardware, busy-wait latency, reset ordering assumptions that differ by SoC revision, and racing concurrent driver access to the same block. Test signals include platform boot/probe logs, driver reset recovery tests, suspend/resume coverage, timeout fault injection with mocked MMIO, and hardware register trace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/stmp_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/string.c -->
# sources/distributed-fs/ceph-client/lib/string.c

## Purpose
Provides generic fallback implementations for core kernel string and memory primitives that may be replaced by architecture-specific versions or FORTIFY wrappers. It includes libc-like operations plus `sized_strscpy()` and byte scanning helpers used broadly across the kernel.

## APIs, Control Flow, and State
Conditionally exported fallbacks include `strncasecmp()`, `strcasecmp()`, `strcpy()`, `strncpy()`, `stpcpy()`, `strcat()`, `strncat()`, `strlcat()`, `strcmp()`, `strncmp()`, `strchr()`, `strchrnul()`, `strrchr()`, `strnchr()`, `strlen()`, `strnlen()`, `strspn()`, `strcspn()`, `strpbrk()`, `strsep()`, `memset()`, `memset16()`, `memset32()`, `memset64()`, `memcpy()`, `memmove()`, `memcmp()`, `bcmp()`, `memscan()`, `strstr()`, `strnstr()`, `memchr()`, and `memchr_inv()`. `sized_strscpy()` is an important bounded copy helper using word-at-a-time scanning where alignment and memory-safety configuration allow it, forcing NUL termination and returning `-E2BIG` on truncation or bad sizes. Memory routines are simple byte or word loops except `memcmp()` and `memchr_inv()`, which use word-sized optimizations under suitable architecture conditions.

There is no persistent state. The file is built with `__NO_FORTIFY` so it can provide low-level primitives beneath fortified wrappers.

## Dependencies, Integration, Risks, and Tests
Depends on ctype, errno, word-at-a-time helpers, unaligned access helpers, endian/page definitions, architecture `__HAVE_ARCH_*` selection, and export support. Integration is universal: nearly every subsystem may link to these fallbacks when no architecture override exists. Risks include unsafe legacy APIs such as `strcpy()`/`strcat()`, overlap misuse with `memcpy()`, `strlcat()` BUG when destination length exceeds count, word-at-a-time reads near page boundaries, KMSAN false positives if optimizations are not disabled, and callers misinterpreting `sized_strscpy()` return values. Test signals include string/memory selftests, FORTIFY tests, KASAN/KMSAN coverage, cross-architecture builds with and without efficient unaligned access, and fuzzing around truncation and NUL boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/string_helpers.c -->
# sources/distributed-fs/ceph-client/lib/string_helpers.c

## Purpose
Implements higher-level string utilities that do not belong in low-level `string.c`: size formatting, integer-array parsing, escape/unescape transformations, quotable string allocation, managed string arrays, whitespace/sysfs matching helpers, replacement/padding, and FORTIFY reporting.

## APIs, Control Flow, and State
Important exports include `string_get_size()`, `parse_int_array()`, `parse_int_array_user()`, `string_unescape()`, `string_escape_mem()`, `kstrdup_quotable()`, `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, `kstrdup_and_replace()`, `kasprintf_strarray()`, `kfree_strarray()`, `devm_kasprintf_strarray()`, `skip_spaces()`, `strim()`, `sysfs_streq()`, `match_string()`, `__sysfs_match_string()`, `strreplace()`, `memcpy_and_pad()`, and, under FORTIFY, overflow-reporting functions. `string_get_size()` scales block counts into SI or IEC units with three significant figures. Unescape control flow recognizes selected backslash classes in priority order. Escape control flow applies `only`, printable/ascii filters, and class-specific escaping, returning the output size that would have been generated even when truncated. Allocation helpers build escaped copies for logging command lines and file paths. Devres helpers attach string-array cleanup to a device.

Persistent state is limited to devres-managed allocations owned by devices; otherwise allocations are caller-owned and freed with `kfree()`/`kfree_strarray()`.

## Dependencies, Integration, Risks, and Tests
Depends on slab, usercopy, ctype, hex helpers, get_options, task command-line access, file path rendering, devres, KUnit bug support, and optional FORTIFY metadata. Integration points include sysfs parsers, logging/audit paths, device drivers, proc/debug output, and fortified string/memory wrappers. Risks include escape flag priority surprises, non-NUL-terminated `string_escape_mem()` output, allocation leaks on partial string-array failure, sysfs newline matching assumptions, unsynchronized task command-line reads, and FORTIFY panic paths intentionally crashing after reporting. Test signals include string_helpers KUnit tests, sysfs input tests, escape/unescape round trips, usercopy fault injection for `parse_int_array_user()`, devres teardown tests, and FORTIFY overflow tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/string_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/strncpy_from_user.c -->
# sources/distributed-fs/ceph-client/lib/strncpy_from_user.c

## Purpose
Copies a NUL-terminated string from userspace into a kernel buffer with fault handling, object-size checking, and word-at-a-time acceleration. It returns the copied string length excluding the trailing NUL, or a sentinel/error for truncation or faults.

## APIs, Control Flow, and State
The exported API is `strncpy_from_user()`. It calls `might_fault()`, honors fault-injection through `should_fail_usercopy()`, rejects non-positive counts as zero, checks the destination with KASAN and object-size validation, and then chooses masked user access or a normal user access window bounded by `TASK_SIZE_MAX` and `untagged_addr()`. `do_strncpy_from_user()` uses aligned word reads when possible, falls back to byte-at-a-time on unaligned input or user fault, detects NUL with word-at-a-time masks, and clears bytes after the first NUL before writing the final word. If the user count is reached first it returns `count`; if the address-space maximum or fault is hit before the requested count it returns `-EFAULT`.

No persistent state exists; partial destination writes may remain after a fault, as documented.

## Dependencies, Integration, Risks, and Tests
Depends on uaccess access-window helpers, fault-inject-usercopy, KASAN/object-size checking, tagged-address stripping, architecture byte order, and word-at-a-time helpers. Integration points are syscall, procfs, sysfs, ioctl, and BPF-facing paths that need a stable copy of a user string. Risks include callers treating `count` return as success with NUL termination, ignoring partial copies after `-EFAULT`, races where userspace mutates the source during copy, architecture-specific masked access bugs, and failing to size the kernel destination to at least `count`. Test signals include usercopy selftests, KASAN/FORTIFY object-size tests, fault injection, unaligned source/destination tests, page-boundary strings, truncation cases, and BPF map key equivalence tests for post-NUL masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/strncpy_from_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/strnlen_user.c -->
# sources/distributed-fs/ceph-client/lib/strnlen_user.c

## Purpose
Measures a NUL-terminated userspace string up to a caller-supplied limit, returning a length that includes the trailing NUL. The file explicitly warns that callers should usually prefer copying because userspace can change concurrently.

## APIs, Control Flow, and State
The exported API is `strnlen_user()`. It rejects non-positive counts with zero, then either uses masked user access or starts a normal user read window bounded by `TASK_SIZE_MAX` and `untagged_addr()`. `do_strnlen_user()` aligns the pointer downward, expands the maximum by the alignment offset, masks bytes before the original pointer, then scans word-at-a-time for a zero byte. It returns the length including NUL when found, `count + 1` when the user-supplied limit is hit first, and zero on exception or address-space limit before the requested count.

The function maintains no state and does not stabilize the user string.

## Dependencies, Integration, Risks, and Tests
Depends on uaccess, MM address limits, tagged-address handling, bitops, and word-at-a-time zero detection. Integration points include legacy syscall or proc paths that need to validate approximate user string lengths. Risks include time-of-check/time-of-use races, callers forgetting that too-long is `> count` rather than an errno, zero meaning fault or invalid count, allowed overshoot inside aligned word reads, and reliance on architecture user-access behavior. Test signals include page-boundary tests, invalid pointer faults, masked-access coverage, too-long sentinel cases, count zero/negative cases, and race-aware tests that pair length with a later copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/strnlen_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sys_info.c -->
# sources/distributed-fs/ceph-client/lib/sys_info.c

## Purpose
Implements a configurable diagnostic dump facility selected by `SYS_INFO_*` bits. It can dump task state, memory, timers, locks, ftrace buffers, all-CPU backtraces, and blocked tasks, with an optional sysctl default mask for callers that pass zero.

## APIs, Control Flow, and State
Exports `sys_info_parse_param()` and `sys_info()`, and under `CONFIG_SYSCTL` provides `sysctl_sys_info_handler()`. `sys_info_parse_param()` splits a comma-separated string and maps names through `match_string()` into bit positions derived from `ilog2(SYS_INFO_*)`. Sysctl writes parse the supplied string into `kernel_si_mask` with `WRITE_ONCE`; reads rebuild a comma-separated string from the current mask and pass it through `proc_dostring()`. The `kernel/kernel_sys_info` sysctl is registered at `subsys_initcall`. `sys_info()` invokes `__sys_info()` with the supplied mask or the global default, then calls each selected dump routine.

Persistent state is the unsynchronized global `kernel_si_mask`. The sysctl handler allocates a temporary names buffer per operation.

## Dependencies, Integration, Risks, and Tests
Depends on bitops/log2, console and scheduler debug dumping, sysrq timer listing, lockdep debug, ftrace dump, NMI all-CPU backtrace, string matching, and sysctl. Integration points are panic/oops/driver diagnostics and module parameters that want standardized debug dumps. Risks include very noisy or expensive dumps, unsynchronized global mask updates, empty name for `SYS_INFO_PANIC_CONSOLE_REPLAY` not round-tripping through sysctl text, sysctl buffer sizing mistakes, and use in contexts where dump helpers are unsafe or reentrant. Test signals include sysctl read/write tests, parser tests for comma-separated masks, panic/debug dump smoke tests, lockdep/ftrace enabled and disabled builds, and concurrency tests around updating `kernel_si_mask`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/sys_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/syscall.c -->
# sources/distributed-fs/ceph-client/lib/syscall.c

## Purpose
Provides a helper to inspect the current syscall state of a task, primarily for diagnostics that need to describe what a blocked task is doing without using unsafe user register APIs while a syscall is in progress.

## APIs, Control Flow, and State
The exported API is `task_current_syscall()`. For `current`, it directly calls `collect_syscall()`. For another task, it snapshots `target->__state`, rejects runnable tasks with `-EAGAIN`, waits for the task to be inactive, collects registers and syscall data, then waits again and verifies the context-switch count is unchanged. `collect_syscall()` pins the task stack with `try_get_task_stack()`, obtains `task_pt_regs()`, records user stack pointer and instruction pointer, gets the syscall number, fetches up to six arguments when in a syscall, releases the stack, and fills `info->data.nr = -1` when the task has no stack or is not in a syscall.

No persistent state is stored; all output is written into the caller-provided `struct syscall_info`.

## Dependencies, Integration, Risks, and Tests
Depends on task stacks, ptrace register helpers, scheduler inactive waits, architecture `asm/syscall.h`, and task state fields. Integration points include `/proc`, scheduler debug, hung-task reporting, tracing, and crash diagnostics. Risks include races if the task wakes or changes syscall state between waits, architecture register helpers returning unavailable data, current-task inspection being less stable than blocked-task inspection, and callers treating `nr == -1` as an error instead of a valid non-syscall result. Test signals include proc syscall reporting tests, blocked syscall scenarios, runnable task `-EAGAIN` cases, architecture syscall argument tests, and race stress with rapidly waking tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test-kstrtox.c -->
# sources/distributed-fs/ceph-client/lib/test-kstrtox.c

## Purpose
Defines a load-time module selftest for kernel string-to-integer conversion APIs. It checks accepted values, rejected syntax, sign handling, base handling, newline rules, and overflow boundaries across unsigned and signed integer widths.

## APIs, Control Flow, and State
The module uses macros `TEST_OK()` and `TEST_FAIL()` over static `__initconst` tables. It tests `kstrtoull()`, `kstrtoll()`, `kstrtou64()`, `kstrtos64()`, `kstrtou32()`, `kstrtos32()`, `kstrtou16()`, `kstrtos16()`, `kstrtou8()`, and `kstrtos8()`. Each ok table records input string, base, and expected result; each fail table records strings expected to return a negative error. The init function invokes all test groups and returns `-EINVAL`, intentionally causing module load to fail after running the tests so the module does not remain resident.

State is limited to static test vectors and stack-local temporaries. Failures are reported through `WARN()`.

## Dependencies, Integration, Risks, and Tests
Depends on kernel module infrastructure, integer conversion helpers, limits constants, and warning output. Integration is with lib selftest builds and CI that loads test modules. Risks include missing base/autodetection combinations for narrower types, no aggregate pass/fail counter, warning-only failure reporting, and intentional init failure being misread as test failure by harnesses that do not know this convention. Test signals are the warnings emitted for mismatches, module load logs, and CI coverage across 32-bit and 64-bit builds to catch type-width assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test-kstrtox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_bitmap.c -->
# sources/distributed-fs/ceph-client/lib/test_bitmap.c

## Purpose
Implements an extensive bitmap API module selftest. It validates bitmap mutation, copying, parsing, printing, region allocation, scatter/gather, array conversion, iteration macros, range scans, bit reads/writes, compile-time constant folding, zero-length behavior, and simple performance timing.

## APIs, Control Flow, and State
The file uses the kselftest module harness and helper assertions that increment `total_tests` and `failed_tests`. `selftest()` runs many focused tests: `test_zero_clear()`, `test_fill_set()`, `test_copy()`, `test_bitmap_region()`, `test_replace()`, `test_bitmap_sg()`, arr32/arr64 round trips, hex and list parsing, list printing, memory-optimization equivalence, `bitmap_cut()`, buffered print helpers, constant-evaluation build assertions, `bitmap_read()`/`bitmap_write()`, read/write timing, weight tests, zero-nbits calls, nth-bit search, set/clear bit iterators, bitrange iterators, clump iteration, and wraparound iteration. Static expected bitmaps and strings cover little slices, multiword layouts, all/empty inputs, malformed ranges, overflow, and very large printed lists.

State is test-only: static buffers in `__initdata`, expected vectors in `__initconst`, and kselftest counters. The module does not persist runtime state after loading.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/bitmap.h`, module/kselftest harness, printk, slab, string helpers, and uaccess headers. It integrates with kernel selftest module loading and validates shared bitmap primitives used by CPU masks, nodemasks, allocators, drivers, and filesystems. Risks include architecture-sensitive expectations around word size and tail clearing, very large expected strings being brittle, performance logs not enforcing thresholds, and NULL pointer zero-nbits tests relying on APIs not dereferencing pointers in that case. Test signals are direct: kselftest pass/fail counters, detailed `pr_err`/`pr_warn` lines, build-time `BUILD_BUG_ON()` failures, and timing output for parser/read/write loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_bitops.c -->
# sources/distributed-fs/ceph-client/lib/test_bitops.c

## Purpose
Provides a small module selftest for basic bit operations and order helpers. It exercises set/clear/find behavior on a global bitmap and validates `get_count_order()` and `get_count_order_long()` for selected boundary values.

## APIs, Control Flow, and State
The module declares enum bit positions, a global `DECLARE_BITMAP(g_bitmap, BITOPS_LENGTH)`, 32-bit order test vectors, and 64-bit vectors under `CONFIG_64BIT`. `test_bitops_startup()` sets several bits, checks order helper results, clears those bits, verifies `find_first_bit()` returns the sentinel end position, runs `test_fns()`, and logs completion. `test_fns()` allocates 10,000 random words, repeatedly calls `fns(word, n)` for every `n < BITS_PER_LONG`, stores the volatile result to prevent optimization, and logs elapsed time. Exit is a no-op.

Persistent state is only the module-global test bitmap while the module is loaded; allocated random buffers are freed automatically via cleanup attribute.

## Dependencies, Integration, Risks, and Tests
Depends on bitops, random bytes, ktime, slab allocation, module init/exit, and cleanup attributes. Integration is with kernel lib selftests and CI module loading. Risks include warning-only failures instead of a formal aggregate result, limited coverage of order-helper inputs, performance timing variability, and dependence on architecture word size for 64-bit vectors. Test signals are module logs: order mismatch warnings, unexpected set-bit errors, and the `fns` timing line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_bitops.c -->
