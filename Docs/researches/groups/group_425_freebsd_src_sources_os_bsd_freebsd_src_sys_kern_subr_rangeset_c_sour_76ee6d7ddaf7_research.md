# Group Research: group_425_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_subr_rangeset_c_sour_76ee6d7ddaf7

Scope checked against `Docs/research_subset_a.md`: these files are inside the included source tree `sources/os/bsd/freebsd-src`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_rangeset.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_rangeset.c

## Purpose

`subr_rangeset.c` implements a compact non-overlapping interval set for kernel consumers. It stores `struct rs_el` ranges in a PCTRIE keyed by `re_start`, with half-open intervals `[re_start, re_end)`. The implementation supports insertion, removal, predicate-filtered removal, lookup by containing address, exact-start lookup, emptiness checks, copying, full destruction, and DDB inspection.

## Main Data Model

The public `struct rangeset` owns:

- `rs_trie`: PCTRIE of `rs_el` nodes.
- `rs_dup_data`: caller-supplied clone function used when a removal splits an existing range or when copying.
- `rs_free_data`: caller-supplied destructor for range payloads.
- `rs_data_ctx`: callback context.
- `rs_alloc_flags`: UMA allocation flags used by pctrie node allocation.

`rs_el` storage itself is supplied by callers through the `data` argument to `rangeset_insert()`. The file treats `data` as `struct rs_el *`, fills `re_start` and `re_end`, and inserts it.

## Initialization And Allocation

`rs_rangeset_init()` creates a UMA zone named `"rangeset pctrie nodes"` sized by `pctrie_node_size()`. The zone is installed by `SYSINIT(rs, SI_SUB_LOCK, SI_ORDER_ANY, ...)`.

`rs_node_alloc()` recovers the owning `struct rangeset` from the embedded pctrie and allocates trie nodes using that rangeset’s allocation flags. `rs_node_free()` frees trie nodes back to the zone. `PCTRIE_DEFINE(RANGESET, rs_el, re_start, ...)` generates the typed trie operations.

## Core Operations

`rangeset_init()` initializes the trie and callback fields. `rangeset_fini()` validates the set under `DIAGNOSTIC` and removes all ranges.

`rangeset_check_empty(rs, start, end)` looks up the range with greatest start less than or equal to `end`; the interval is empty if no such range exists or that range ends at or before `start`.

`rangeset_insert(rs, start, end, data)` first removes any overlapping existing ranges, then inserts the provided node as `[start, end)`. This makes insertion replace overlap rather than fail on overlap.

`rangeset_remove_pred(rs, start, end, pred)` is the important algorithm. It walks backward using `LOOKUP_LE(end - 1)` and handles all interval-overlap cases:

- Existing range ends before `start`: stop.
- Existing range lies fully inside removal span: remove and free it if predicate passes.
- Removal cuts the right side of an existing range: shrink `re_end` to `start`.
- Removal cuts the left side of an existing range: remove/reinsert with `re_start = end`.
- Removal cuts a hole in the middle: duplicate the node, insert the right fragment, and shrink the original left fragment.

If split allocation fails, it returns `ENOMEM` and leaves the original range intact. Predicate false means the matching range is preserved and iteration adjusts around it.

`rangeset_remove()` uses an always-true predicate. `rangeset_remove_all()` reclaims the full trie and calls the user free callback for each leaf.

`rangeset_containing(rs, place)` returns a range whose `re_start <= place < re_end`. `rangeset_beginning(rs, place)` returns only an exact-start range. `rangeset_empty(rs, start, end)` checks for any range beginning after `start` but before `end`; unlike `rangeset_check_empty()`, it does not call diagnostic validation and is start-key oriented.

`rangeset_copy(dst, src)` requires an empty destination and matching duplicate callback, clones each source node in ascending order, and cleans up the destination on failure.

## Invariants And Diagnostics

Under `DIAGNOSTIC`, `rangeset_check()` iterates in ascending start order and asserts:

- `re_start < re_end`.
- Neighbor ranges do not overlap: previous `re_end <= current re_start`.

The DDB `show rangeset <addr>` command prints the rangeset pointer and every element’s start/end pair.

## Dependencies

Key dependencies are `sys/pctrie.h`, `sys/rangeset.h`, UMA allocation, and optional DDB support.

## Maintenance Notes

The code assumes callers serialize access externally; no locks are embedded in `struct rangeset`. Any future caller must also provide correct lifetime callbacks because range payload memory belongs to the caller, while internal trie-node memory belongs to this file.

Split-removal is the highest-risk path: it depends on `rs_dup_data()` preserving all payload fields other than `re_start/re_end`, and on `rs_free_data()` correctly releasing failed duplicate nodes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_rangeset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_rman.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_rman.c

## Purpose

`subr_rman.c` implements FreeBSD’s kernel resource manager for bus and CPU resource ranges. It tracks allocatable hardware-like resources such as I/O ports, memory windows, IRQs, and other indexed ranges. The implementation is for `RMAN_ARRAY` style resources; `RMAN_GAUGE` is explicitly unimplemented.

The manager does not discover or assign hardware by itself. Bus and architecture code use it to manage ranges, and device drivers request allocations through those higher-level layers.

## Main Data Model

Internal resources are `struct resource_i`, which wraps the public `struct resource` and adds:

- `r_start`, `r_end`: inclusive resource range.
- `r_flags`: allocation/share/active flags.
- `r_virtual`, `r_irq_cookie`: mapping and interrupt metadata.
- `r_dev`: owning device.
- `r_rm`: parent resource manager.
- `r_rid`, `r_type`: optional resource ID/type.
- `r_link`: ordered list link in `rm->rm_list`.
- `r_sharelink`, `r_sharehead`: support exact-range shared allocations.

The public `struct resource` stores a back-pointer in `__r_i`.

All initialized resource managers are linked from global `rman_head`, protected by `rman_mtx`. Each manager has its own `rm_mtx`.

## Initialization And Region Management

`rman_init()` validates type, sets a default full end range if start/end are both zero, initializes the manager list and mutex, and inserts the manager into the global list.

`rman_manage_region(rm, start, end)` adds a free region to the manager. The list remains sorted and adjacent free regions are merged when possible. It rejects ranges outside the manager bounds or overlapping existing ranges.

`rman_init_from_resource()` initializes a manager and manages the exact range from an existing resource.

`rman_fini()` refuses to finalize if any resource is allocated, frees all remaining free entries, removes the manager from the global list, and destroys its mutex.

`rman_first_free_region()` and `rman_last_free_region()` scan the list for the first or last unallocated entry.

## Allocation, Adjustment, And Release

`rman_reserve_resource(rm, start, end, count, flags, dev)` is the core allocator. It:

- Validates nonzero count and flags.
- Computes alignment from `RF_ALIGNMENT(flags)`.
- Searches free regions for a compatible aligned subrange.
- Splits free entries into two or three pieces when allocating from the middle.
- Marks the allocated entry with `RF_ALLOCATED` and caller flags.
- If no unshared region fits and `RF_SHAREABLE` is set, searches for an exact-size compatible shared region.

Shared resources must match exact range length and sharing type (`RF_SHAREABLE | RF_PREFETCHABLE`). The first shared resource owns the list entry and gets `RF_FIRSTSHARE`; additional sharers are separately allocated `resource_i` objects linked on the share list.

`rman_adjust_resource(rr, start, end)` shrinks or extends an allocated resource while preserving at least some overlap with the original range. It does not support shared resources. Growth requires adjacent free space; shrinking may create new free entries before or after the resource.

`int_rman_release_resource()` releases an allocated resource. It clears `RF_ACTIVE`, handles shared-list removal and first-share reassignment, then merges the released range with adjacent free regions where possible. If no merge is possible, the same entry becomes a free region in place. `rman_release_resource()` wraps it with manager locking.

`rman_activate_resource()` and `rman_deactivate_resource()` set or clear `RF_ACTIVE`.

## Metadata Accessors

The file provides getters/setters for resource start/end/size/flags, virtual address, IRQ cookie, bus tag, bus handle, `resource_map`, RID, type, owning device, and manager membership. `rman_make_alignment_flags()` converts a size to the corresponding alignment-log flags.

## Sysctl And Debugging

`sysctl_rman()` exposes resource-manager and resource entries through `hw.bus.rman`. It supports querying manager metadata with resource index `-1`, or individual resources including shared resources.

DDB commands provide:

- `show rman <addr>`: dump one manager.
- `show rmans`: list manager headers.
- `show allrman` / `show all rman`: dump all managers and entries.

## Dependencies

This file depends on the bus/device layer, `sys/rman.h`, mutexes, sysctl, DDB, and machine bus-space types.

## Invariants And Constraints

The resource list is sorted by range and represents both free and allocated spans. Free spans are merged eagerly. Allocated spans are not allowed to partially overlap. Shared allocations are only permitted for exact same range and compatible sharing flags.

Range endpoints are inclusive, so size is always `end - start + 1`. Overflow-sensitive paths check for wrap around `RM_MAX_END` and alignment masks.

## Maintenance Notes

This is shared infrastructure with significant locking and list-shaping complexity. Any change to allocation or release must preserve:

- Sorted list order.
- No overlapping non-shared resources.
- Correct free-region coalescing.
- Exact handling of shared first-owner replacement.
- No sleeping allocation while holding manager locks unless already established by the existing code path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_rman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_rtc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_rtc.c

## Purpose

`subr_rtc.c` provides machine-independent helpers for registering and coordinating real-time clock devices. It orders clocks by resolution, reads the best available RTC during boot time initialization, schedules asynchronous writes back to RTC devices, and exposes debug sysctls for one-shot clock I/O.

## Main Data Model

Each registered clock is represented by `struct rtc_instance`:

- `clockdev`: device implementing `CLOCK_GETTIME`/`CLOCK_SETTIME`.
- `resolution`: clock resolution in microseconds.
- `flags`: behavior modifiers such as no-adjust flags.
- `schedns`: optional nanosecond offset for scheduling writes.
- `resadj`: half-resolution adjustment used for coarse clocks.
- `stask`: timeout task used for asynchronous writes.
- `rtc_entries`: list link.

All instances live in `rtc_list`, protected by `rtc_list_lock` (`sx` lock). The list is sorted by increasing resolution value, so more accurate clocks are queried first.

## Registration And Scheduling

`clock_register_flags(clockdev, resolution, flags)` allocates an instance, computes its half-resolution adjustment, initializes its timeout task, inserts it into the sorted list, and logs registration.

`clock_register(dev, res)` registers with no special flags.

`clock_unregister(clockdev)` removes the instance, cancels and drains its pending timeout task, then frees it.

`clock_schedule(clockdev, offsetns)` records a desired nanosecond offset within each second for future RTC writes. `resettodr()` uses this to delay writes until the target offset.

## Reading Time

`read_clocks(ts, debug_read)` iterates registered clocks in resolution order. For each clock it calls `CLOCK_GETTIME`. Invalid negative seconds or nanoseconds are rejected. Unless the clock says no gettime adjustment is needed, it adds `resadj` and `utc_offset()`.

For normal boot reads, the function stops at the first successful clock and optionally logs the provider. For debug reads, it continues to exercise all registered clocks.

`inittodr(base)` initializes system time. It tries `read_clocks()`. If no RTC succeeds, it reports a warning/error and falls back to `base` if positive, otherwise leaves time invalid. Successful reads call `tc_setclock()`, and `ffclock_reset_clock()` when `FFCLOCK` is enabled.

## Writing Time

`resettodr()` writes current system time back to all registered clocks unless `machdep.disable_rtc_set` is set. It does not call drivers directly in the caller’s context. Instead, it enqueues each instance’s timeout task on `taskqueue_thread`, optionally delayed so the write happens near `schedns`.

`settime_task_func()` runs in taskqueue context. Unless `CLOCKF_SETTIME_NO_TS` is set, it reads current time, subtracts `utc_offset()`, optionally adds `resadj`, then invokes `CLOCK_SETTIME`. Errors are logged only when `bootverbose`.

## Debugging

The `debug.clock_show_io` sysctl controls printing of RTC I/O:

- `1`: reads.
- `2`: writes.
- `3`: both.

`clock_dbgprint_bcd()`, `clock_dbgprint_ct()`, `clock_dbgprint_err()`, and `clock_dbgprint_ts()` are helper functions for drivers to log formatted clock values.

The `debug.clock_do_io` sysctl triggers one-shot I/O:

- `1`: read all clocks and discard results.
- `2`: schedule writes via `resettodr()`.

## Dependencies

The file depends on clock device interface methods from `clock_if.h`, taskqueues, `sx` locks, timecounter APIs, optional `FFCLOCK`, sysctl, and bus/device infrastructure.

## Maintenance Notes

Clock driver callbacks are intentionally invoked without holding `rtc_list_lock`, through taskqueue or controlled list traversal, so drivers can sleep or take their own locks. The sorted-list invariant matters because the first successful read becomes the system time source.

The half-resolution adjustment is an intentional policy for whole-second or coarse clocks. Any change to adjustment flags must consider both read and write paths to avoid systematic skew.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_rtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sbuf.c

## Purpose

`subr_sbuf.c` implements FreeBSD’s `sbuf` string-buffer abstraction for both kernel and userland builds. An `sbuf` is an append-oriented string builder with optional automatic extension, optional drain callbacks, tracked error state, finish semantics, section accounting, and kernel-only copyin/uio helpers.

## Main Data Model

The implementation operates on `struct sbuf` from `sys/sbuf.h`. Important fields used here include:

- `s_buf`: backing character buffer.
- `s_size`: backing buffer size.
- `s_len`: current logical length.
- `s_error`: accumulated error.
- `s_flags`: dynamic/fixed/finished/drain/section/user flags.
- `s_drain_func`, `s_drain_arg`: optional overflow drain.
- `s_rec_off`, `s_sect_len`: record/section bookkeeping.

Important flags include `SBUF_DYNAMIC`, `SBUF_DYNSTRUCT`, `SBUF_FINISHED`, `SBUF_AUTOEXTEND`, `SBUF_INSECTION`, `SBUF_INCLUDENUL`, `SBUF_DRAINATEOL`, and `SBUF_DRAINTOEOR`.

## Allocation And Growth

Kernel builds allocate from `M_SBUF`; userland builds use `calloc/free`. `sbuf_extendsize()` rounds small buffers up by powers of two and large buffers by page-sized increments.

`sbuf_new(s, buf, length, flags)` initializes a caller-provided or heap-allocated `sbuf`. If no backing buffer is supplied, it allocates one and marks it dynamic. `SBUF_AUTOEXTEND` allows small initial sizes because the function rounds up.

`sbuf_extend(s, addlen)` grows the backing store when auto-extension is enabled. It preserves existing content, frees old dynamic storage, and turns static storage into dynamic storage after the first growth.

`sbuf_delete()` frees dynamic buffer storage, clears the object, and frees the object itself if it was dynamically allocated.

## Append And Copy Operations

`sbuf_put_bytes()` and `sbuf_put_byte()` are the central append helpers. They enforce unfinished state, stop early on prior error, drain or extend on overflow, then copy bytes and update section length.

Public append/copy APIs include:

- `sbuf_bcat()`, `sbuf_bcpy()` for raw bytes.
- `sbuf_cat()`, `sbuf_cpy()` for strings.
- `sbuf_putc()` for one character.
- `sbuf_printf()` and `sbuf_vprintf()` for formatted output.
- Kernel-only `sbuf_bcopyin()`, `sbuf_copyin()`, and `sbuf_uionew()`.

Kernel `sbuf_vprintf()` uses `kvprintf()` with a character callback. Userland `sbuf_vprintf()` uses `vsnprintf()`, extending or draining until enough room exists.

## Draining

`sbuf_set_drain()` installs a drain function and context. It asserts that changing the drain on a non-empty buffer is not allowed unless it is the same function.

`sbuf_drain()` calls the drain callback with either the whole buffer or, with drain-to-end-of-record semantics, only up to `s_rec_off`. It handles positive progress, converts zero progress to `EDEADLK`, records negative callback returns as errors, preserves newline-at-end state, and compacts remaining data to the front.

`sbuf_count_drain()` is a drain callback that only counts bytes, useful for sizing sysctl output without materializing it.

## Finish, Data, And Length

`sbuf_finish()` writes a terminating NUL at `s_len`, optionally includes that NUL in logical length, drains remaining data if a drain is installed, and marks the buffer finished. Kernel builds return the stored error; userland builds set `errno` and return `-1` on error.

`sbuf_data()` requires a finished non-draining buffer and returns `s_buf`.

`sbuf_len()` returns `-1` on error and otherwise reports logical length, accounting for `SBUF_INCLUDENUL`.

`sbuf_done()` tests the finished flag.

## Position, Trimming, And Sections

`sbuf_clear()` resets length, record offset, section length, error, and finished flag.

`sbuf_setpos()` truncates to an existing position and rejects section mode.

`sbuf_trim()` removes trailing whitespace, updating section length if needed.

`sbuf_nl_terminate()` appends a newline to non-empty output if the last emitted byte was not already newline, including the drained-buffer case tracked by `SBUF_DRAINATEOL`.

`sbuf_start_section()` begins a section or subsection, storing prior section length for nested sections. `sbuf_end_section()` pads the section to an alignment with a specified character, returns section length, and restores outer-section accounting.

## Invariants

In kernel invariant builds, helper assertions check non-null initialized buffers, bounds, and whether functions are called in finished or unfinished state. Many operations also assert that drains are absent when random access or direct data inspection would be nonsensical.

## Maintenance Notes

The buffer’s error state is sticky: most append APIs return failure once `s_error` is set. Drain behavior is the most subtle part because it allows output to leave the buffer before finish, so functions that inspect `s_buf` must reject drain-enabled buffers.

Section accounting depends on every append path updating `s_sect_len`; future append helpers must preserve that behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_scanf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_scanf.c

## Purpose

`subr_scanf.c` provides kernel `sscanf()` and `vsscanf()` support derived from BSD `vfscanf`. It parses a NUL-terminated input string according to a subset of scanf-style conversions and writes converted values through a `va_list`.

## Supported Conversions

The implementation supports:

- Literal characters and `%%`.
- Assignment suppression with `*`.
- Width fields.
- Length modifiers: `h`, `hh`, `l`, `ll` via `QUAD`, `q`, `j`, `t`, `z`.
- Integers: `%d`, `%i`, `%o`, `%u`, `%x`, `%p`.
- Strings and characters: `%s`, `%c`, `%[...]`.
- `%n` to store the number of consumed input characters.

Floating-point flags are defined but no floating conversions are implemented in this file.

## Parser Structure

`sscanf()` is a thin wrapper around `vsscanf()`.

`vsscanf(inp, fmt0, ap)` tracks:

- `inr`: remaining input bytes, initialized with `strlen(inp)`.
- `nread`: total consumed characters.
- `nassigned`: number of assigned fields.
- `nconversions`: conversions attempted.
- `width`, `flags`, `base`, and conversion type.
- `buf[32]` for numeric tokens.
- `ccltab[256]` for scansets.

Whitespace in the format consumes any amount of input whitespace. Non-`%` format characters must match literally. For most conversions, leading input whitespace is skipped unless `NOSKIP` is set.

## Integer Conversion

Integer parsing accumulates a bounded token into `buf`, then calls either `strtoq` or `strtouq`. It handles:

- Optional sign.
- `%i` base detection.
- Octal/decimal/hex bases.
- Optional `0x` prefix for `%x`, `%i`, and `%p`.
- Pushback of a lone sign or trailing `x` from `0x`.

Assignment writes to the destination type selected by length flags. `%p` writes through `void **` after converting the integer to `uintptr_t`.

## String, Character, And Scanset Conversion

`%c` copies exactly `width` characters, defaulting to 1, and does not skip whitespace.

`%s` copies non-whitespace characters and NUL-terminates when not suppressed. The implementation permits zero-length string assignment after leading whitespace handling.

`%[...]` uses `__sccl()` to build an inclusion table. It requires at least one matching character unless input failure occurs. Negated scansets with `^`, leading `]`/`-`, ranges such as `a-z`, and historical range behavior are handled.

## Return Semantics

On input failure before any conversion, `vsscanf()` returns `-1`. On later input failure, it returns the number of assigned fields. On match failure, it returns the number of assigned fields.

`%n` counts as a conversion but not an assignment in the `nassigned` return value.

## Dependencies

The file depends on kernel `ctype`, string conversion routines, `stdarg`, and basic system headers.

## Maintenance Notes

The numeric buffer is fixed at 32 bytes, so very long numeric fields are intentionally truncated by width handling. This is traditional scanf behavior for the local implementation, but future extension should preserve bounded token accumulation.

The scanset parser uses a 256-byte table indexed by unsigned input characters. Any change to character signedness paths should keep the explicit casts around table lookup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_scanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sfbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sfbuf.c

## Purpose

`subr_sfbuf.c` implements the machine-independent pool manager for `sf_buf` objects, used to create temporary kernel virtual mappings of VM pages for `sendfile(2)` and similar paths on platforms without a direct map.

If `PMAP_HAS_DMAP` is true, the file mostly bypasses pool management and treats a `vm_page *` as the `sf_buf` handle.

## Main Data Structures

Global state includes:

- `nsfbufs`: configured maximum number of buffers.
- `nsfbufsused`, `nsfbufspeak`: live and peak usage counters.
- `sf_buf_active`: hash table of active page-to-buffer mappings.
- `sf_buf_hashmask`: hash mask.
- `sf_buf_freelist`: tail queue of free buffers.
- `sf_buf_alloc_want`: number of waiters.
- `sf_buf_lock`: mutex protecting hash table, free list, counters, and refs.

The active hash key is derived from the page’s index in `vm_page_array`.

## Initialization

`sf_buf_init()` runs at `SI_SUB_MBUF`. If there is no direct map, it:

- Reads `kern.ipc.nsfbufs` tunable, defaulting to `512 + maxusers * 16`.
- Allocates the active hash table.
- Allocates a contiguous KVA region of `nsfbufs * PAGE_SIZE`.
- Allocates an array of `struct sf_buf`.
- Assigns each buffer one page of KVA and places it on the freelist.
- Initializes `sf_buf_lock`.

Sysctls under `kern.ipc` expose configured, peak, and current buffer counts.

## Allocation

`sf_buf_alloc(m, flags)` returns a buffer mapping for page `m`.

On direct-map systems it returns `(struct sf_buf *)m`.

Otherwise it:

- Requires CPU-private allocations to be made by pinned threads.
- Looks for an existing active mapping for `m`.
- If found, increments its refcount and removes it from the freelist if it was cached with refcount zero.
- If not found, takes the first freelist entry, sleeping unless `SFB_NOWAIT` is set.
- Recycles any old hash entry attached to that buffer.
- Inserts the buffer into the hash list, sets refcount/page, updates counters, and calls machine-dependent `sf_buf_map()`.

`SFB_CATCH` controls whether the sleep is interruptible. SMP/SFBUF_CPUSET builds may call `sf_buf_shootdown()` when reusing existing mappings.

## Freeing And Referencing

`sf_buf_free(sf)` decrements the refcount. When it reaches zero, the buffer is returned to the freelist and usage is decremented. If `sf_buf_unmap()` says the mapping was removed, the page association is cleared and the hash entry removed. Waiters are woken when present.

`sf_buf_ref(sf)` increments the refcount and asserts the buffer is allocated.

When `SFBUF_PROCESS_PAGE` is enabled, `sf_buf_process_page(m, cb)` finds the active buffer for page `m` and invokes a callback while holding `sf_buf_lock`.

## Dependencies

The implementation depends on VM page structures, pmap/KVA mapping helpers supplied elsewhere, mutexes, sleep/wakeup, sysctls, and optional SMP shootdown support.

## Maintenance Notes

The design intentionally keeps recently freed buffers mapped until recycling or explicit unmap, which can reduce mapping churn. The active hash and freelist are both protected by a single mutex, simplifying correctness.

Any change to refcount-zero cached mappings must preserve the distinction between “free but still associated with a page” and “unmapped/no page.” That distinction is visible in allocation reuse and `sf_buf_process_page()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sfbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sglist.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sglist.c

## Purpose

`subr_sglist.c` implements scatter/gather list construction and manipulation. It converts kernel buffers, user buffers, bios, mbufs, VM page arrays, uios, physical address ranges, and existing sglist ranges into arrays of contiguous physical segments.

## Main Data Model

An `sglist` owns:

- `sg_nseg`: current number of segments.
- `sg_maxseg`: capacity.
- `sg_refs`: reference count.
- `sg_segs[]`: array of `struct sglist_seg`, each with physical address and length.

A local `struct sgsave` records `sg_nseg` and the old length of the final segment. The `SGLIST_SAVE`/`SGLIST_RESTORE` macros roll back failed append attempts because appends only grow the list or extend the last segment.

## Segment Appending

`_sglist_append_range()` appends a physical range, coalescing with the previous segment when `previous_paddr + previous_len == paddr`. It returns `EFBIG` if capacity is exhausted.

`_sglist_append_buf()` maps a virtual buffer through either kernel pmap extraction or a supplied user pmap, splits by page boundaries, and appends physical runs. It optionally reports how much was appended before a capacity failure.

`sglist_append()`, `sglist_append_user()`, `sglist_append_phys()`, `sglist_append_vmpages()`, `sglist_append_sglist()`, `sglist_append_uio()`, `sglist_append_bio()`, `sglist_append_mbuf()`, `sglist_append_single_mbuf()`, and `sglist_append_mbuf_epg()` are type-specific wrappers. Most save and restore state so failures do not leave partial additions.

`sglist_consume_uio()` is intentionally different: it appends as much as fits, advances the `uio` by the completed amount, and returns success even when it stops due to list capacity.

## Counting And Allocation

`sglist_count()` counts physical runs needed for a kernel virtual buffer.

`sglist_count_vmpages()` counts runs in an array of VM pages.

`sglist_count_mbuf_epg()` counts runs for an `M_EXTPG` mbuf, including header, page array, and trailer.

`sglist_alloc(nsegs, mflags)` allocates a list plus segment storage in one block and initializes it. `sglist_free()` drops a reference and frees on last reference. `sglist_build()` counts, allocates, and populates a list for one kernel buffer. `sglist_clone()` duplicates list metadata and active segments.

`sglist_length()` sums segment lengths.

## List Transformations

`sglist_split(original, head, length, mflags)` moves the first `length` bytes from `original` into `*head`. It rejects shared originals (`sg_refs > 1`) with `EDOOFUS`. It may allocate `*head`, validates capacity/emptiness for caller-provided heads, handles splitting inside a segment, and removes copied segments from the front of the original.

`sglist_join(first, second)` appends all segments from `second` into `first`, coalescing the boundary if adjacent and resetting `second`.

`sglist_slice(original, slice, offset, length, mflags)` copies a logical byte range from `original` into `*slice`, adjusting first and last segments for partial overlap.

## Dependencies

The file depends on VM/pmap extraction, mbuf extended-page layout, `bio` unmapped-buffer conventions, `uio`, malloc, refcounting, and KTR tracing.

## Maintenance Notes

Rollback behavior is central: append wrappers generally leave the destination unchanged on `EFBIG` or `EINVAL`. New append paths should use the existing save/restore pattern unless partial consumption is explicitly desired.

The direct segment-array transformations in split/join/slice are higher-risk than the append wrappers. They must preserve copy direction, segment counts, and in-place overlap behavior, especially when trimming the front of `original` or moving segments between lists.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sglist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sleepqueue.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sleepqueue.c

## Purpose

`subr_sleepqueue.c` implements FreeBSD sleep queues: wait-channel keyed queues of threads blocked in sleep/wakeup and condition-variable style APIs. Sleep queues differ from turnstiles because wait channels have no owner, so they do not propagate priority. They support timeouts, interruptible sleeps, signal aborts, broadcast/signal wakeups, assertions against API misuse, optional profiling, DDB inspection, and stack reporting.

## Main Data Structures

A `struct sleepqueue` contains:

- `sq_blocked[NR_SLEEPQS]`: thread queues, with `NR_SLEEPQS == 2`.
- `sq_blockedcnt[]`: per-queue counts.
- `sq_hash`: link used in both hash-chain and free-list contexts.
- `sq_free`: free sleepqueue objects lent by other waiters.
- `sq_wchan`: associated wait channel.
- `sq_type`: sleepq consumer type.
- `sq_lock`: associated interlock under `INVARIANTS`.

A `struct sleepqueue_chain` contains a list of active queues and a spin mutex. There are 256 hash chains selected by `SC_HASH(wchan)`.

Threads carry their own sleepqueue. The first waiter on a wait channel lends its queue to the channel. Additional waiters lend their queues into the active queue’s free list.

## Initialization

`init_sleepqueues()` initializes all hash chains and creates the UMA zone. `thread0.td_sleepqueue` is allocated immediately. UMA init/dtor functions initialize blocked queues and assert emptiness on free in invariant builds.

`sleepq_alloc()` and `sleepq_free()` allocate/free per-thread queues from UMA.

## Enqueue Path

`sleepq_lock(wchan)` and `sleepq_release(wchan)` lock/unlock the hash-chain spin lock. `sleepq_lookup(wchan)` requires the chain lock and searches for an active queue.

`sleepq_add(wchan, lock, wmesg, flags, queue)` enqueues the current thread. It validates that sleeping is allowed, creates or joins the wait-channel queue, checks consumer type and associated lock consistency, inserts the thread at the tail of the selected blocked queue, clears the thread’s own sleepqueue pointer, records wait metadata, and marks interruptible sleeps with `TDF_SINTR`.

`sleepq_set_timeout_sbt()` arms the current thread’s sleep callout with precomputed sbintime state and the current CPU as target.

## Sleep And Wake Flow

`sleepq_switch(wchan, pri)` performs the actual context switch if the thread remains on the sleepqueue. It handles races where the thread was already woken, already timed out, or the real-time clock changed for absolute real-time sleeps. Otherwise it calls scheduler sleep hooks, switches the thread lock to the sleepqueue chain lock, marks the thread sleeping, and calls `mi_switch()`.

`sleepq_wait()`, `sleepq_wait_sig()`, `sleepq_timedwait()`, and `sleepq_timedwait_sig()` are the public blocking variants. Timed and signal variants clear and report timeout/signal state after resume.

`sleepq_resume_thread(sq, td, pri, srqflags)` removes one thread from the queue, optionally adjusts priority, and makes it runnable if it is actually sleeping. It also handles the race where a thread is in signal-check logic and not yet sleeping.

`sleepq_remove_thread()` performs queue removal, returns a sleepqueue object to the thread, stops callouts where safe, clears wait metadata and interrupt/timeout flags, and emits wakeup probes.

`sleepq_signal()` wakes one thread from a wait channel. Normal behavior chooses the highest-priority waiter, oldest on ties. `SLEEPQ_UNFAIR` selects a recent sleeper while trying to avoid threads still context-switching.

`sleepq_broadcast()` wakes all matching waiters on a queue via `sleepq_remove_matching()`. `sleepq_chains_remove_matching()` scans all chains and removes matching threads globally.

`sleepq_remove(td, wchan)` wakes a specific thread if it is sleeping on the specified channel. `sleepq_remove_nested()` removes a thread and returns with the thread lock held.

## Signals, Timeouts, And Races

`sleepq_check_ast_sc_locked()` checks pending wakeup, signal, and suspension AST state while coordinating process locks and the sleepqueue lock to avoid missed signals.

`sleepq_catch_signals()` either switches to sleep or removes the thread immediately if a signal/suspend condition is pending.

`sleepq_timeout()` is the callout handler. It verifies that the callout still corresponds to the active sleep, sets `TDF_TIMEOUT`, and either wakes the thread if it is asleep or leaves the flag for the thread to notice before switching.

`sleepq_abort(td, intrval)` aborts interruptible sleeps for signal delivery. If the thread has not fully slept yet, it records `td_intrval` and lets the sleeping path observe it; if already sleeping, it wakes the thread.

The real-time-clock generation check in `sleepq_switch()` handles the POSIX race between absolute real-clock sleeps and `clock_settime()`.

## Diagnostics And Profiling

With `STACK`, `sleepq_sbuf_print_stacks()` captures stacks for all threads sleeping on a wait channel/queue. It avoids allocation and sbuf writes while holding the sleepqueue spin lock by preallocating stack/sbuf storage and retrying with larger arrays.

With `SLEEPQUEUE_PROFILING`, the file tracks hash-chain depths and sleep-message frequency through debug sysctls.

DDB `show sleepq` / `show sleepqueue` prints wait channel, type, associated interlock, blocked threads, and expected counts.

## Maintenance Notes

This file is concurrency-critical. Correctness relies on the lock choreography among sleepqueue chain locks, thread locks, process locks, scheduler locks, and callout state. The “thread has not slept yet” versus “thread is already sleeping” distinction appears in timeout, signal, and wakeup paths and must be preserved.

Any new wake path must return the borrowed sleepqueue to the thread exactly once and maintain `sq_blockedcnt`, `td_sleepqueue`, `td_wchan`, `td_wmesg`, `TDF_SINTR`, and `TDF_TIMEOUT` consistently.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_sleepqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_smp.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_smp.c

## Purpose

`subr_smp.c` contains machine-independent SMP support: global CPU state, SMP startup coordination, CPU stop/restart helpers, cross-CPU rendezvous, CPU topology construction and analysis, CPU quiescing helpers, and a sequential-consistency fence broadcast.

It also provides dummy-compatible behavior for UP kernels so modules can call SMP APIs regardless of kernel configuration.

## Global State

Important exported/global state includes:

- `all_cpus`: set of CPUs known to the kernel.
- `mp_ncpus`, `mp_maxcpus`, `mp_maxid`, `mp_ncores`.
- `smp_started`, `smp_disabled`, `smp_cpus`, `smp_threads_per_core`.
- Under SMP: `stopped_cpus`, `started_cpus`, `suspended_cpus`, `hlt_cpus_mask`, `logical_cpus_mask`.
- `stoppcbs`: PCB snapshots saved during panic/stop handling.
- `smp_ipi_mtx`: spin mutex serializing rendezvous and TLB shootdown style busy-wait IPI operations.

Sysctls under `kern.smp` expose active state, CPU counts, max IDs, topology override, and disable state.

## Startup

`mp_setmaxid()` calls machine-dependent `cpu_mp_setmaxid()` very early, validates CPU counters, and sizes cpusets.

`mp_start()` initializes the IPI mutex, checks loader disable/probe result, falls back to one CPU if needed, otherwise calls machine-dependent startup, logs CPU count, allocates `stoppcbs`, and announces CPUs.

UP builds initialize CPU variables with `mp_setvariables_for_up()`.

`forward_signal(td)` sends `IPI_AST` to a running thread on another CPU so it processes pending AST/signal state.

## Stop, Suspend, And Restart

`generic_stop_cpus(map, type)` sends stop/suspend/offline IPIs, serializes concurrent stop operations with a static `stopping_cpu`, and spins until target CPUs report stopped/suspended or a timeout message is printed. x86 suspend/offline paths also take `smp_ipi_mtx` to avoid lost IPI assumptions under virtualization.

Public wrappers include `stop_cpus()`, `stop_cpus_hard()`, and on x86 `suspend_cpus()` / `offline_cpus()`.

`generic_restart_cpus(map, type)` signals stopped/suspended CPUs to resume and waits for stop bits to clear. For normal stop on x86 it also writes monitor buffers to wake CPUs stopped with MWAIT. Public wrappers include `restart_cpus()` and x86 `resume_cpus()`.

## Rendezvous

`smp_rendezvous_cpus(map, setup_func, action_func, teardown_func, arg)` runs callbacks on a CPU set with barriers before action and before teardown unless the callback is `smp_no_rendezvous_barrier`. It:

- Executes locally with spinlock protection before SMP starts.
- Requires interrupts/spinlock state suitable to avoid IPI mutex livelock.
- Intersects the requested map with `all_cpus`.
- Serializes rendezvous with `smp_ipi_mtx`.
- Stores callback parameters in global rendezvous variables.
- Sends `IPI_RENDEZVOUS` to remote CPUs.
- Runs the action on the current CPU if selected.
- Waits for all participants to release-complete.

`smp_rendezvous_action()` is the target-side routine. It uses atomic wait counters, fetches callback state after an acquire barrier, wraps callbacks in a special critical-section pattern, and release-signals completion.

`smp_rendezvous_cpu()` and `smp_rendezvous()` are convenience wrappers.

`smp_rendezvous_cpus_retry()` repeats rendezvous over a CPU set until participants clear themselves through `smp_rendezvous_cpus_done()`, calling a supplied wait function for CPUs that did not complete.

## Topology Helpers

`smp_topo_alloc()` allocates persistent `cpu_group` storage. `smp_topo_none()` builds a flat topology.

`smp_topo()` lazily builds topology once, using a debug override from `kern.smp.topology` or machine-dependent `cpu_topo()`. It validates CPU count and mask against `all_cpus`, collapses single-child levels, fills first/last CPU fields, and returns the root.

`smp_topo_1level()` and `smp_topo_2level()` construct synthetic package/cache/core groupings. `smp_topo_find()` locates the smallest group containing a CPU.

Under SMP, `topo_node` helpers manage richer topology trees: initialization, child add/find by hardware ID, child promotion by rotation, depth-first traversal, PU logical ID assignment, and uniformity analysis through `topo_analyze()`.

## Quiescing And Fences

`quiesce_cpus(map, wmesg, prio)` either waits for selected idle threads to switch once or, with `PDROP`, forces context switches by binding the current thread across CPUs. `quiesce_all_cpus()` targets all CPUs.

`quiesce_all_critical()` spins until every CPU’s current thread is outside a critical section, or until the current thread changes, indicating the critical path exited.

`cpus_fence_seq_cst()` forces a sequentially consistent fence on all CPUs using rendezvous under SMP, or locally under UP.

## Maintenance Notes

The rendezvous implementation relies on global pseudo-structure variables guarded by `smp_ipi_mtx` and atomic barriers. Callback functions must be reentrant and safe in unknown lock context, as documented in the file.

Stop/restart paths are architecture-sensitive. x86 has extra suspend/offline and NMI-broadcast behavior; non-x86 paths are simpler. Any change here needs architecture-specific review.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_smp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_smr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_smr.c

## Purpose

`subr_smr.c` implements FreeBSD’s Safe Memory Reclamation mechanism based on Global Unbounded Sequences. It supports lockless reader sections and deferred reclamation by tracking sequence numbers observed by per-CPU readers and advancing a shared read sequence once all readers have observed a writer’s goal.

The design is intended to integrate with UMA so memory can be tagged on free and reused only after the required grace period.

## Algorithm Summary

The shared state has:

- A monotonic write sequence (`s_wr.seq`), initialized to an odd value.
- A shared read sequence (`s_rd_seq`) representing the lowest observed active reader sequence.
- Per-CPU reader sequence values (`c_seq`), with `SMR_SEQ_INVALID` meaning the CPU is outside an SMR read section.

Writers call `smr_advance()` to obtain a goal sequence. Reclamation waits or polls until `s_rd_seq` reaches that goal. Readers do not update global sequence state; they only record their observed sequence while inside read sections.

The algorithm handles wraparound with bounded deltas, odd valid sequence values, and invariant builds that deliberately force wrapping behavior for testing.

## Sequence Advancement Modes

`smr_shared_advance()` increments the shared write sequence by `SMR_SEQ_INCR`.

`smr_default_advance()` advances normal SMRs. It reads `s_rd_seq`, increments the write sequence, and if the writer gets too far ahead, calls `smr_wait()` to prevent undetectable wraparound. It updates debug counters.

`smr_lazy_advance()` advances lazy SMRs based on kernel ticks, with a two-tick grace window. This reduces write-side sequence churn and assumes periodic clock interrupts flush state sufficiently.

`smr_deferred_advance()` advances only after a per-CPU deferred counter reaches a configured limit. Before that, it returns a future goal relative to current shared state.

`smr_advance()` is the public entry. It asserts the caller is not inside the target SMR, issues a release fence so prior modifications are visible before sequence advancement, enters a critical section, chooses the correct advancement mode from per-CPU flags, and returns the goal.

## Polling

`smr_poll_cpu(c, s_rd_seq, goal, wait)` reads one CPU’s active sequence. Inactive CPUs immediately satisfy the poll. If a stale value below `s_rd_seq` is observed, it is pinned to `s_rd_seq` to handle races where a CPU loaded an older write sequence before publishing it. If `wait` is true, the function spins until the CPU observes the goal or exits.

`smr_poll_scan()` scans all CPUs, finds the minimum active sequence, and advances shared `s_rd_seq` if it observed progress.

`smr_poll(smr, goal, wait)` is the public poll/wait function. It rejects blocking waits from inside SMR sections and from lazy SMRs. It uses a critical section to avoid ABA races from long preemption sleeps, conditionally advances lazy/deferred write state, validates goal range, scans CPUs when needed, updates failure counters, and returns whether the goal has been observed. It issues an acquire fence before returning so subsequent reclamation sees readers’ memory effects.

## Lifecycle

`smr_create(name, limit, flags)` allocates shared state and per-CPU state from UMA zones, initializes shared read/write sequence numbers, initializes every CPU slot up to `mp_maxid`, and publishes with a seq-cst fence.

`smr_destroy(smr)` synchronizes, frees the shared state, and frees per-CPU state.

`smr_init()` creates UMA zones for shared and per-CPU SMR structures with cache-line alignment.

## Instrumentation

Debug sysctls under `debug.smr` expose counters for:

- `advance`
- `advance_wait`
- `poll`
- `poll_scan`
- `poll_fail`

These counters help identify workloads with expensive grace-period waits or failed nonblocking polls.

## Dependencies

The implementation depends on per-CPU UMA zones, counters, CPU iteration, SMP/critical sections, atomic ordering primitives, ticks, and definitions/macros from `sys/smr.h`.

## Maintenance Notes

Memory ordering is the core correctness property. The release fence in `smr_advance()`, acquire loads in polling, and acquire fence after polling are part of the reclamation contract. Changes to these paths must preserve the guarantee that memory freed before a goal is not reused until all pre-goal readers are gone or have observed the goal.

Lazy and deferred modes intentionally decouple writer progress from immediate global sequence increments. Callers must understand that nonblocking polls can fail until the relevant sequence is advanced.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_smr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_stack.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_stack.c

## Purpose

`subr_stack.c` implements generic kernel stack-trace storage, printing, sbuf formatting, and symbol lookup helpers. It provides the `stack` feature and supports normal live-kernel symbol lookup plus DDB-safe lookup paths.

## Main Data Model

`struct stack` is defined in `sys/stack.h` and contains a bounded array of program counters plus a `depth` count. This file enforces `depth <= STACK_MAX` before printing or formatting.

Allocation uses `M_STACK`.

## Basic Operations

`stack_create(flags)` allocates and zeroes a stack object.

`stack_destroy(st)` frees it.

`stack_put(st, pc)` appends a program counter if there is room, returning `0`; otherwise it returns `-1`.

`stack_copy(src, dst)` copies the full stack object by assignment.

`stack_zero(st)` clears the stack.

## Printing

`stack_print(st)` prints one line per frame with frame index, PC, symbol name, and offset. It uses the normal linker symbol lookup path and `M_WAITOK`.

`stack_print_short(st)` prints frames compactly on one line, using symbol+offset where available and raw PC otherwise.

`stack_print_ddb(st)` uses DDB linker lookup and prints long format.

When `DDB` or `WITNESS` is enabled, `stack_print_short_ddb(st)` provides compact DDB-safe output.

## sbuf Formatting

`stack_sbuf_print_flags(sb, st, flags, format)` formats the stack into an `sbuf`. It supports:

- `STACK_SBUF_FMT_LONG`: one line per frame.
- `STACK_SBUF_FMT_COMPACT`: symbol+offset tokens on one line.

If symbol lookup returns `EWOULDBLOCK`, the function returns that error, allowing callers using `M_NOWAIT` to avoid sleeping. It newline-terminates output through `sbuf_nl_terminate()`.

`stack_sbuf_print(sb, st)` uses long format and `M_WAITOK`.

When `DDB` or `WITNESS` is enabled, `stack_sbuf_print_ddb()` formats using DDB lookup.

## KTR Support

With `KTR` and `DDB`, `stack_ktr(mask, file, line, st, depth)` emits stack frames as KTR tracepoints up to the requested depth, or the full captured depth when `depth` is zero or larger than actual depth.

## Symbol Lookup

`stack_symbol(pc, namebuf, buflen, offset, flags)` uses `linker_search_symbol_name_flags()`. If lookup fails, it returns `"??"` with offset zero and `ENOENT`. It preserves `EWOULDBLOCK` distinctly.

`stack_symbol_ddb(pc, name, offset)` uses DDB linker symbol APIs, avoids normal linker locking, and also falls back to `"??"`.

## Dependencies

The file depends on linker symbol APIs, `sbuf`, optional DDB/WITNESS/KTR, malloc, sysctl feature registration, and machine-specific stack capture code supplied elsewhere.

## Maintenance Notes

This file does not capture stacks itself; it stores and renders stacks captured by architecture-specific or caller-specific code. The split between normal and DDB symbol lookup is important because DDB contexts cannot safely take the same locks as live-kernel lookup.

Any new formatter should preserve `STACK_MAX` bounds checks and should keep `EWOULDBLOCK` visible when using nonblocking symbol lookup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_stack.c -->