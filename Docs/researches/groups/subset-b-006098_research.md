# subset-b-006098

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_ter16x32.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_ter16x32.c

## Purpose
`font_ter16x32.c` provides the compiled-in Terminus 16x32 console bitmap font. It is almost entirely static glyph data: 256 glyphs, each 16 pixels wide by 32 pixels high, stored in the kernel console font format and exposed through a `struct font_desc`.

## Important APIs, Types, and Functions
The file defines `FONTDATAMAX` as 16384 bytes, `static const struct font_data fontdata_ter16x32`, and the exported descriptor `const struct font_desc font_ter_16x32`. The descriptor sets `.idx = TER16x32_IDX`, `.name = "TER16x32"`, `.width = 16`, `.height = 32`, `.charcount = 256`, and `.data = fontdata_ter16x32.data`. On sparc, `.pref` is `5`; elsewhere it is `-1`.

## Control Flow, State, and Persistence
There is no runtime control flow. The byte array is immutable static data linked into the kernel image when `CONFIG_FONT_TER16x32` includes it. Runtime font selection code consumes the descriptor through the font registry in `fonts.c`.

## Dependencies and Integration Points
It includes `<linux/module.h>` and local `font.h` for `struct font_data`, `struct font_desc`, and font indexes. The main integration point is `fonts.c`, which conditionally adds `&font_ter_16x32` to the `fonts[]` lookup table.

## Risks and Test Signals
Risks are data integrity and geometry consistency: `FONTDATAMAX` must match 256 glyphs * 32 rows * 2 bytes per row, and descriptor width/height must match the byte layout. Since this is static asset data, useful signals are build coverage with `CONFIG_FONT_TER16x32`, console/font lookup tests that select `TER16x32`, and visual or checksum validation of rendered glyphs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_ter16x32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/fonts.c -->
# sources/distributed-fs/ceph-client/lib/fonts/fonts.c

## Purpose
`fonts.c` implements Linux console soft-font data management and lookup. It imports user-provided console font glyphs into kernel-owned `font_data_t` buffers, reference-counts non-internal font data, exports font buffers back to userspace layout, compares font data, and chooses or finds built-in fonts.

## Important APIs, Types, and Functions
Font-data helpers use metadata words stored immediately before `font_data_t`: `REFCOUNT`, `FNTSIZE`, and `FNTSUM`. `font_data_import()` allocates a `struct font_data`, checks overflow, copies glyph rows from userspace pitch to kernel glyph pitch, optionally calculates a checksum, and starts refcounting at one. `font_data_get()` and `font_data_put()` manage references for dynamic font data while treating internal static font data as unrefcounted. `font_data_size()`, `font_data_is_equal()`, and `font_data_export()` provide size, equality, and userspace conversion. Lookup APIs are `find_font()` by name and `get_default_font()` by screen geometry and supported width/height bitmaps.

## Control Flow, State, and Persistence
Imported font state persists in heap allocations until the last `font_data_put()` frees the enclosing `struct font_data`. Static fonts have zero refcount metadata and live in read-only data. `font_data_export()` walks glyphs and zero-fills per-glyph trailing pitch bytes. `get_default_font()` scores all configured fonts by preference, screen height, effective rows/columns at the display resolution, platform-specific m68k hints, and caller-supported dimensions.

## Dependencies and Integration Points
The file depends on console font types from `<linux/kd.h>`, overflow helpers, slab allocation, string/memory helpers, and local `font.h`. Built-in descriptors are added to a static `fonts[]` table under `CONFIG_FONT_*` options, including `font_ter_16x32` when enabled. Exports are used by fbcon, console font ioctls, and other console/font consumers.

## Risks and Test Signals
Important risks include integer overflow in glyph-size calculations, mismatched `vpitch`/height causing bad copies, non-atomic reference count updates if callers share dynamic font data without external synchronization, equality deliberately rejecting static-vs-dynamic matches, and default selection surprises from scoring. Tests should cover import/export round trips with padded pitches, overflow rejection, dynamic refcount lifetime, internal font no-op put/get behavior, checksum-assisted equality, `find_font()` for configured fonts, and `get_default_font()` with constrained width/height masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/fonts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fw_table.c -->
# sources/distributed-fs/ceph-client/lib/fw_table.c

## Purpose
`fw_table.c` provides firmware-table subtable parsing for ACPI and ACPI-like tables, including CDAT. It abstracts differences in subtable header layout and length encoding, then dispatches matching entries to caller-provided handlers.

## Important APIs, Types, and Functions
`enum acpi_subtable_type` distinguishes common ACPI, HMAT, PRMT, CEDT, and CDAT subtables. `struct acpi_subtable_entry` pairs a `union acpi_subtable_headers *` with that type. Helper functions derive entry type, entry length, subtable header length, root table length, and subtable kind from the table signature. `acpi_parse_entries_array()` is the central parser. `cdat_table_parse()` wraps it for CDAT and exports `EXPORT_SYMBOL_FWTBL_LIB`.

## Control Flow, State, and Persistence
Parsing begins by selecting the table type from the four-character signature, reading the root table length, honoring an optional `max_length`, and starting at `table_header + table_size`. It walks subtables until the next minimum header would exceed `table_end`, compares each entry type against each `acpi_subtable_proc`, invokes the matching handler until `max_entries` is reached, increments per-proc and total counts even for ignored overflow entries, and advances by the entry's encoded length. Zero-length entries are rejected to avoid infinite loops.

## Dependencies and Integration Points
The file depends on ACPI/CDAT structure definitions from `<linux/acpi.h>` and `<linux/fw_table.h>`, endian conversion for CDAT lengths, and kernel diagnostics. It integrates with ACPI table consumers that provide `struct acpi_subtable_proc` arrays and with CXL/CDAT users through `cdat_table_parse()`.

## Risks and Test Signals
Risks include malformed firmware lengths, signatures that choose the wrong header interpretation, truncation by `max_length`, handlers receiving entries whose semantic payload length is not otherwise validated here, and warning messages using `proc->id` for aggregate diagnostics. Tests should include common ACPI, HMAT, CEDT, PRMT, and CDAT tables; little-endian CDAT length handling; zero-length subtable rejection; `max_entries` warning behavior; handler and handler_arg dispatch; and truncated table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fw_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/genalloc.c -->
# sources/distributed-fs/ceph-client/lib/genalloc.c

## Purpose
`genalloc.c` implements the generic special-purpose memory pool allocator used for memory outside normal `kmalloc` management, such as device SRAM, uncached memory, or DMA-visible regions. Allocation/free are bitmap-based and designed to be lockless after chunks have been added.

## Important APIs, Types, and Functions
Core APIs include `gen_pool_create()`, `gen_pool_add_owner()`, `gen_pool_destroy()`, `gen_pool_alloc_algo_owner()`, `gen_pool_free_owner()`, `gen_pool_virt_to_phys()`, `gen_pool_avail()`, `gen_pool_size()`, `gen_pool_has_addr()`, and `gen_pool_for_each_chunk()`. DMA wrappers include `gen_pool_dma_alloc*()` and `gen_pool_dma_zalloc*()`. Allocation strategies include `gen_pool_first_fit()`, `gen_pool_first_fit_align()`, `gen_pool_fixed_alloc()`, `gen_pool_first_fit_order_align()`, and `gen_pool_best_fit()`. Device-managed integration is provided by `devm_gen_pool_create()`, `gen_pool_get()`, and `of_gen_pool_get()` under `CONFIG_OF`.

## Control Flow, State, and Persistence
A `struct gen_pool` owns an RCU-protected list of `struct gen_pool_chunk` objects. Each chunk stores virtual and physical base addresses, inclusive end address, owner pointer, an atomic available-byte count, and a bitmap where one bit represents `1 << min_alloc_order` bytes. Adding chunks takes `pool->lock`; allocation walks chunks under RCU, skips chunks with insufficient `avail`, asks the selected algorithm for a start bit, atomically sets bitmap bits with cmpxchg, retries on conflict, subtracts rounded size from `avail`, and returns a virtual address plus optional owner. Freeing finds the containing chunk, atomically clears the bits, restores `avail`, and BUGs on invalid ranges or double-free-like bitmap conflicts. Destroy asserts all bits are clear before freeing chunks and the optional name.

## Dependencies and Integration Points
The implementation depends on bitmap helpers, RCU lists, atomic operations, spinlocks, device resources, OF/platform-device lookup, and vmalloc-backed chunk metadata. It is exported for drivers and subsystems that publish special memory pools or consume pools through devres or device-tree phandles.

## Risks and Test Signals
Risks include livelock under heavy atomic contention, BUG-triggering invalid frees, address overflow in `virt + size - 1` or `start + size - 1`, alignment data requiring power-of-two semantics, NMI use on architectures without NMI-safe cmpxchg, and destroy-time BUGs if allocations remain. Tests should exercise concurrent allocation/free, all algorithms, alignment and fixed offsets, owner round trips, DMA physical translation, empty/full pools, devm lookup uniqueness, OF phandle lookup, and misuse cases under debug kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/genalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/generic-radix-tree.c -->
# sources/distributed-fs/ceph-client/lib/generic-radix-tree.c

## Purpose
`generic-radix-tree.c` implements the out-of-line pieces of the generic radix tree abstraction: sparse byte-addressed storage with zeroed node allocation, lockless publication through atomic pointer swaps, iteration helpers, preallocation, and destruction.

## Important APIs, Types, and Functions
Exports include `__genradix_ptr()`, `__genradix_ptr_alloc()`, `__genradix_iter_peek()`, `__genradix_iter_peek_prev()`, `__genradix_prealloc()`, and `__genradix_free()`. Internal helpers from the header provide root packing/unpacking, depth sizing, node allocation/free, and inline pointer lookup.

## Control Flow, State, and Persistence
The tree root encodes both node pointer and depth in low bits. `__genradix_ptr_alloc()` first grows the root depth until the requested offset fits, publishing each new root with `cmpxchg_release()`, then descends by depth, allocating and publishing missing child nodes with compare-exchange. Failed races reuse or free the local `new_node`. Iteration peeks walk from the current iterator offset, skipping missing subtrees and adjusting `iter->offset` and `iter->pos`; the reverse variant backs up to the previous allocated page-sized object region. `__genradix_prealloc()` touches each node-sized offset up to `size`, and `__genradix_free()` swaps the root to NULL before recursively freeing nodes.

## Dependencies and Integration Points
It depends on `<linux/generic-radix-tree.h>`, atomic `READ_ONCE`/`cmpxchg_release`/`xchg`, GFP allocation flags, and node helpers defined in the generic radix tree header. Kernel code using `GENRADIX()` typed wrappers maps typed arrays onto these byte-offset primitives.

## Risks and Test Signals
Risks include offset arithmetic near `SIZE_MAX`, iterator progress over sparse holes, concurrent growth races, allocation failure leaving the tree consistent, and `__genradix_free()` assuming a non-NULL root path. Tests should cover sparse high offsets, concurrent allocations to the same and adjacent offsets, forward and reverse iteration over holes, preallocation failure injection, and free-after-populated-tree cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/generic-radix-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/glob.c -->
# sources/distributed-fs/ceph-client/lib/glob.c

## Purpose
`glob.c` implements small shell-style pattern matching for kernel users that need `fnmatch`-like matching without pathname-specific behavior. It is intended for denylist-style string matching and can be built as a module because ATA users may be modular.

## Important APIs, Types, and Functions
The only exported API is `bool glob_match(const char *pat, const char *str)`. Supported metacharacters are `?`, `*`, bracket classes, bracket ranges, leading `!` class inversion, backslash escapes, and literal fallback for malformed opening brackets.

## Control Flow, State, and Persistence
The matcher is iterative and non-recursive. It consumes one pattern token and one string character at a time. `*` stores a single backtracking point (`back_pat`, `back_str`) and later retries from one character later on mismatch. Character classes scan spans until `]`, support an initial literal `]`, and treat missing terminators as a literal `[`. Matching succeeds only when the whole pattern and whole string end together.

## Dependencies and Integration Points
It includes `<linux/glob.h>`, module metadata, and exports `glob_match()`. The comments call out ATA pattern users, but the function is generic and does not special-case `/` or leading `.`.

## Risks and Test Signals
Risks include quadratic worst-case behavior for repeated backtracking, no support for `[^...]` inversion syntax, literal behavior for malformed classes, and full-string rather than substring matching. Tests should include `*` zero/nonzero length matches, trailing-star optimization, `?` not matching NUL, ranges and inverted classes, escaped metacharacters, malformed brackets, and worst-case long patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/glob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/group_cpus.c -->
# sources/distributed-fs/ceph-client/lib/group_cpus.c

## Purpose
`group_cpus.c` groups possible CPUs into a requested number of CPU masks while preserving NUMA, cluster, and sibling locality as much as possible. It is used by subsystems that need to spread queues, interrupts, or other resources over CPUs evenly.

## Important APIs, Types, and Functions
The exported API is `group_cpus_evenly(unsigned int numgrps, unsigned int *nummasks)`. SMP helpers include `grp_spread_init_one()`, `alloc_node_to_cpumask()`, `build_node_to_cpumask()`, `get_nodes_in_cpumask()`, `alloc_groups_to_nodes()`, `alloc_nodes_groups()`, `assign_cpus_to_groups()`, `alloc_cluster_groups()`, `__try_group_cluster_cpus()`, and `__group_cpus_evenly()`. `struct node_groups` stores a node or cluster id and either CPU or group count.

## Control Flow, State, and Persistence
On SMP, the function allocates temporary masks, builds node-to-CPU masks from possible CPUs, snapshots `cpu_present_mask`, groups present CPUs first, then groups non-present possible CPUs. For each mask, if groups are fewer than NUMA nodes it assigns whole node intersections round-robin. Otherwise it allocates a proportional number of groups to nodes, then tries cluster-local grouping before falling back to sibling-aware CPU spreading. `grp_spread_init_one()` picks a CPU, then consumes topology siblings first. On UP/non-SMP, it allocates masks and assigns `cpu_possible_mask` to the first group. The returned mask array persists until the caller frees it.

## Dependencies and Integration Points
The file depends on cpumask, NUMA node masks, CPU topology sibling and cluster masks, `sort()`, slab allocation helpers, and CPU hotplug-visible masks. It exports `group_cpus_evenly()` for IRQ, block, network, or queue mapping code that wants balanced CPU affinity sets.

## Risks and Test Signals
Risks include allocation failure paths, CPU hotplug races tolerated by snapshot semantics, cluster masks that are empty or overlap unexpectedly, divide-by-zero avoidance through active CPU checks, and returning fewer initialized masks than requested. Tests should cover zero groups, one CPU/non-SMP, more groups than CPUs, fewer groups than NUMA nodes, uneven NUMA sizes, sibling and cluster topologies, possible-but-not-present CPUs, and hotplug churn during grouping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/group_cpus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/hexdump.c -->
# sources/distributed-fs/ceph-client/lib/hexdump.c

## Purpose
`hexdump.c` provides common kernel helpers for hexadecimal conversion and formatted hex/ASCII dumps. It supports both in-memory line formatting and printk-based dumping when `CONFIG_PRINTK` is enabled.

## Important APIs, Types, and Functions
It exports `hex_asc`, `hex_asc_upper`, `hex_to_bin()`, `hex2bin()`, `bin2hex()`, `hex_dump_to_buffer()`, and, under `CONFIG_PRINTK`, `print_hex_dump()`. `hex_to_bin()` is written without data-dependent branches or memory accesses for cryptographic-key parsing.

## Control Flow, State, and Persistence
`hex2bin()` consumes two hex characters per output byte and fails fast on invalid input. `bin2hex()` packs each source byte with `hex_byte_pack()`. `hex_dump_to_buffer()` normalizes rowsize to 16 or 32, normalizes unsupported groupsize to 1, limits formatting to one row, writes grouped hex using unaligned loads for 2/4/8-byte groups, optionally pads to the ASCII column, and always NUL-terminates when possible. Its return value follows snprintf-like truncation semantics. `print_hex_dump()` chunks a buffer by rowsize, formats each row, and prefixes by address, offset, or none.

## Dependencies and Integration Points
The file depends on ctype, hex helpers, unaligned accessors, printk, min/max, and exported symbols used widely by kernel parsers, debug code, crypto/key loading paths, drivers, and diagnostics.

## Risks and Test Signals
Risks include callers misinterpreting truncation return values, endian-visible grouped output from native unaligned integer formatting, invalid groupsize fallback, and line buffer size requirements when ASCII is enabled. Tests should include invalid hex input, upper/lowercase conversion, zero-length dumps, tiny line buffers, every rowsize/groupsize mode, ASCII sanitization of non-printable bytes, truncation return values, and printk prefix formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/hexdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/hweight.c -->
# sources/distributed-fs/ceph-client/lib/hweight.c

## Purpose
`hweight.c` implements software Hamming-weight/popcount helpers for 8-, 16-, 32-, and 64-bit words. These are fallback routines for architectures or call sites that do not use faster native popcount instructions.

## Important APIs, Types, and Functions
The exported functions are `__sw_hweight8()`, `__sw_hweight16()`, `__sw_hweight32()`, and `__sw_hweight64()`. The 32- and 64-bit versions have `CONFIG_ARCH_HAS_FAST_MULTIPLIER` paths that use multiplication by byte-summing constants; fallback paths use shift/add reductions.

## Control Flow, State, and Persistence
Each function is pure arithmetic with no persistent state. The algorithms fold adjacent bit counts into fields using masks, then sum fields to produce the number of set bits. On 32-bit `BITS_PER_LONG`, `__sw_hweight64()` computes the sum of two 32-bit halves; on 64-bit it processes the full word directly.

## Dependencies and Integration Points
The file includes `<linux/bitops.h>`, `<asm/types.h>`, and exports generic software helpers used by bitops implementations and callers needing architecture-independent popcount behavior.

## Risks and Test Signals
Risks are low but include type-width assumptions, constant suffix correctness on 32- versus 64-bit builds, and configuration-specific code paths. Tests should compare all functions against compiler builtins or exhaustive ranges for 8/16-bit, plus representative 32/64-bit patterns such as zero, all ones, alternating bits, single-bit values, and random values on both fast-multiplier and fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/hweight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/idr.c -->
# sources/distributed-fs/ceph-client/lib/idr.c

## Purpose
`idr.c` implements two ID allocation facilities. IDR maps integer IDs to pointers using radix-tree/XArray machinery. IDA allocates integer IDs only, storing compact bitmaps or value entries in an XArray and handling its own locking.

## Important APIs, Types, and Functions
IDR exports `idr_alloc_u32()`, `idr_alloc()`, `idr_alloc_cyclic()`, `idr_remove()`, `idr_find()`, `idr_for_each()`, `idr_get_next_ul()`, `idr_get_next()`, and `idr_replace()`. IDA exports `ida_alloc_range()`, `ida_find_first_range()`, `ida_free()`, and `ida_destroy()`. IDA internals use `struct ida_bitmap`, `IDA_BITMAP_BITS`, value entries for low sparse IDs, and `XA_FREE_MARK` to find non-full chunks.

## Control Flow, State, and Persistence
IDR allocation normalizes by `idr_base`, asks `idr_get_free()` for a free radix-tree slot up to an inclusive max, stores the ID in `*nextid` before publishing the pointer, replaces the slot, and clears `IDR_FREE`. Cyclic allocation starts from `idr_next` and wraps once. Lookups and iteration use radix-tree traversal and RCU dereference rules; writers require caller synchronization. IDA allocation locks the XArray, finds a marked free chunk, sets a free bit in either a value entry or allocated bitmap, converts value entries to bitmaps when needed, clears the free mark when full, and retries through XArray allocation handling. `ida_free()` validates the bit, clears it, restores the free mark, and deletes empty entries.

## Dependencies and Integration Points
The file depends on radix tree, XArray, bitmap, spinlock/irqsave locking, slab allocation, RCU access patterns, and IDR/IDA public headers. These allocators are widely integrated with driver core, device numbering, minor numbers, handles, and kernel object indexes.

## Risks and Test Signals
Risks include IDR caller-side locking mistakes, base/end inclusive-versus-exclusive confusion, cyclic wrap behavior, pointer validity constraints for XArray entries, IDA warnings on freeing unallocated IDs, memory allocation retries under lock drop/retry paths, and signed `INT_MAX` limits. Tests should cover boundary ranges, `idr_base`, allocation failure, cyclic wrap, replace/remove/find races under documented locking, IDA value-to-bitmap conversion, full chunk marking, first-used search, freeing invalid IDs, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/idr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/inflate.c -->
# sources/distributed-fs/ceph-client/lib/inflate.c

## Purpose
`inflate.c` is the kernel boot-time gzip/deflate decompressor derived from early gzip inflate code. It parses a gzip wrapper, inflates deflate blocks using stored, fixed-Huffman, and dynamic-Huffman modes, maintains CRC32, and validates the gzip trailer.

## Important APIs, Types, and Functions
The key type is `struct huft`, a Huffman decode table entry with operation bits, consumed bits, and either a literal/base value or next-table pointer. Core routines are `huft_build()`, `huft_free()`, `inflate_codes()`, `inflate_stored()`, `inflate_fixed()`, `inflate_dynamic()`, `inflate_block()`, `inflate()`, `makecrc()`, and `gunzip()`. Static tables include literal length bases/extras, distance bases/extras, bit-length-code order, and bit masks. The file expects environment-provided gzip/unzip symbols such as `get_byte()`, `flush_window()`, `window`, `outcnt`, `bytes_out`, `inptr`, `free_mem_ptr`, `free_mem_end_ptr`, `memzero()`, and `error()`.

## Control Flow, State, and Persistence
`gunzip()` reads and validates gzip magic, method, flags, optional extra/name/comment fields, then calls `inflate()`. `inflate()` initializes the sliding window and bit buffer, loops over deflate blocks until the last-block bit, services an optional decompression watchdog, backs up excess byte lookahead, flushes output, and returns an error code. Block dispatch in `inflate_block()` reads the block type and calls stored, fixed, or dynamic handlers. Dynamic blocks read code-length metadata, build an intermediate bit-length tree, expand literal/distance lengths, build actual Huffman tables, then decode with `inflate_codes()`. Global/static state includes the bit buffer `bb`, bit count `bk`, Huffman allocation counter `hufts`, CRC table, CRC accumulator, and the sliding window position alias `wp`.

## Dependencies and Integration Points
It includes `"gzip.h"` when not built `STATIC`, relies on Linux boot decompressor conventions, and can use either a small bump allocator over `free_mem_ptr` or `kmalloc/kfree` under `NO_INFLATE_MALLOC`. It integrates with architecture decompression code and optional `ARCH_HAS_DECOMP_WDOG`.

## Risks and Test Signals
Risks include malformed Huffman tables, incomplete input underruns, memory exhaustion in table construction, overlapping sliding-window copies, CRC/length trailer mismatches, unsupported gzip flags, and reliance on global decompressor state. Tests should cover valid gzip streams using stored/fixed/dynamic blocks, optional gzip fields, truncated input at every stage, invalid block types, invalid length complements, oversubscribed and incomplete Huffman trees, CRC and length failures, allocator exhaustion, and boot decompressor smoke tests on architectures using this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/inflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/interval_tree.c -->
# sources/distributed-fs/ceph-client/lib/interval_tree.c

## Purpose
`interval_tree.c` instantiates the generic augmented red-black interval tree for `struct interval_tree_node` and optionally implements span iteration over used and hole ranges. It provides efficient intersection queries over unsigned long `[start, last]` intervals.

## Important APIs, Types, and Functions
The `INTERVAL_TREE_DEFINE()` macro generates `interval_tree_insert()`, `interval_tree_remove()`, `interval_tree_subtree_search()`, `interval_tree_iter_first()`, and `interval_tree_iter_next()`, all exported GPL. Under `CONFIG_INTERVAL_TREE_SPAN_ITER`, the file exports `interval_tree_span_iter_first()`, `interval_tree_span_iter_next()`, and `interval_tree_span_iter_advance()`. Span iteration uses `struct interval_tree_span_iter` with `nodes[0]` for the current merged used span and `nodes[1]` for the next used span.

## Control Flow, State, and Persistence
The generated interval tree maintains each node's `__subtree_last` augmentation so searches can skip subtrees that cannot intersect a query. Span iteration starts from the first intersecting node and alternates between hole and used states within `[first_index, last_index]`. `interval_tree_span_iter_next_gap()` merges contiguous or overlapping used intervals by advancing until a gap appears. `interval_tree_span_iter_advance()` updates an existing iterator to a new index when possible, otherwise reinitializes from the tree.

## Dependencies and Integration Points
It depends on `<linux/interval_tree.h>` and `<linux/interval_tree_generic.h>`, red-black tree cached roots, and compiler/export helpers. Consumers include memory managers and range-tracking subsystems that need interval intersection or used/hole span walks.

## Risks and Test Signals
Risks include off-by-one errors around inclusive `last`, overflow at `last + 1` or `nodes[0]->last + 1`, incorrect merging of adjacent spans, stale iterators after tree mutation, and configuration skew when span iteration is disabled. Tests should cover overlapping, adjacent, disjoint, leading-hole, trailing-hole, whole-hole, whole-used, single-point, and near-`ULONG_MAX` ranges, plus advancing within and across current spans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/interval_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/interval_tree_test.c -->
# sources/distributed-fs/ceph-client/lib/interval_tree_test.c

## Purpose
`interval_tree_test.c` is a loadable kernel test/benchmark module for the interval tree implementation. It measures insert/remove and search costs, validates intersection iteration against brute-force bitmaps, and validates span iteration against Maple Tree behavior when enabled.

## Important APIs, Types, and Functions
Module parameters control workload size and randomness: `nnodes`, `perf_loops`, `nsearches`, `search_loops`, `search_all`, `max_endpoint`, and `seed`. Static state includes a cached root, allocated node array, query array, and `rnd_state`. Test routines are `init()`, `basic_check()`, `search_check()`, `intersection_range_check()`, `span_iteration_check()`, and module `interval_tree_test_init()`/`interval_tree_test_exit()`. Under span-iterator config, `mas_cur_span()` derives comparable spans from a Maple Tree.

## Control Flow, State, and Persistence
Module init allocates nodes and queries, seeds the PRNG, then runs the benchmark and validation routines. `init()` fills random intervals and query points. `basic_check()` repeatedly inserts and removes all nodes while timing cycles. `search_check()` inserts once, repeatedly counts query intersections, times the work, then removes nodes. `intersection_range_check()` repeatedly rebuilds the tree, computes brute-force intersecting node bitmaps for random ranges, compares them to interval-tree iteration results, and removes nodes. Span testing builds a Maple Tree from the same ranges and compares each interval-tree span's hole/used boundaries to Maple Tree traversal. The module returns `-EAGAIN` intentionally so it unloads after running.

## Dependencies and Integration Points
It depends on module parameters, interval tree APIs, pseudo-random state, slab allocation, cycle counters, bitmaps, and Maple Tree under span testing. It is an in-kernel validation and performance signal for `interval_tree.c`.

## Risks and Test Signals
Risks include random generation using modulo `b` and `% max_endpoint`, which requires nonzero effective endpoints, WARN-only failure reporting, benchmark noise from `get_cycles()`, and limited coverage based on random seeds. Useful signals are absence of WARNs, cycle logs for insert/remove and search, successful brute-force bitmap comparisons, successful Maple Tree span comparisons, and running multiple seeds plus edge parameter values such as small node counts, single-point ranges, and broad `search_all` queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/interval_tree_test.c -->
