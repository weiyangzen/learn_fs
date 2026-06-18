# Group Research: group_441_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_atomic_san_h_sources__1457eb3c0c17

Scope: `Docs/research_subset_a.md`, FreeBSD kernel/public system headers under `sources/os/bsd/freebsd-src/sys/sys`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/atomic_san.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/atomic_san.h

## Purpose
`atomic_san.h` is a sanitizer interposition layer for FreeBSD `atomic(9)` operations. It is not meant to be included directly; it is pulled through `machine/atomic.h` when a sanitizer runtime supplies `SAN_INTERCEPTOR_PREFIX`.

## Main Interfaces
- Declares sanitizer-prefixed atomic functions for `char`, `short`, `int`, `long`, pointer-sized values, explicit `8/16/32/64` widths, `bool` load/store, and thread/interrupt fences.
- Covers add, clear, compare-and-set, fcmpset, fetchadd, load, acquire-load, read-and-clear, set, subtract, store, release-store, swap, test-and-clear, and test-and-set variants.
- When not compiling `SAN_RUNTIME`, remaps normal `atomic_*` names to sanitizer-prefixed interceptors via macros.

## Implementation Notes
The file is almost entirely macro-generated declarations and macro aliases. Pointer load/store receive special casts so typed pointer users retain usable types while the interceptor operates on `uintptr_t`. This header is central for kernel sanitizers because it lets atomic accesses be observed without changing callers.

## Dependencies and Constraints
Requires `_MACHINE_ATOMIC_H_`, `sys/types.h`, `SAN_INTERCEPTOR_PREFIX`, and `__CONCAT`. The aliases are intentionally disabled inside sanitizer runtime code to avoid recursively intercepting the sanitizer's own implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/atomic_san.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/auxv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/auxv.h

## Purpose
`auxv.h` exposes FreeBSD's ELF auxiliary vector lookup API to userland and kernel-adjacent consumers.

## Main Interfaces
- Includes `sys/types.h` and `machine/elf.h`.
- Declares `int elf_aux_info(int aux, void *buf, int buflen);` inside `__BEGIN_DECLS` / `__END_DECLS`.

## Implementation Notes
The header is intentionally minimal: it provides the type context for ELF auxiliary vector constants and one function for copying a requested auxiliary value into a caller-provided buffer. It is a public ABI surface, so the contents are stable and small.

## Dependencies and Constraints
Consumers must provide a correctly sized output buffer for the selected auxiliary vector entry. The implementation lives outside this header.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/auxv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/backlight.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/backlight.h

## Purpose
`backlight.h` defines the user/kernel ioctl ABI for FreeBSD backlight devices.

## Main Interfaces
- `BACKLIGHTMAXLEVELS` is 100, and `struct backlight_props` carries current brightness, number of levels, and the level table.
- `enum backlight_info_type` distinguishes panel and keyboard backlights.
- `struct backlight_info` carries a fixed-size device name and type.
- Ioctls: `BACKLIGHTGETSTATUS`, `BACKLIGHTUPDATESTATUS`, and `BACKLIGHTGETINFO`.

## Implementation Notes
The interface uses fixed-size arrays for ABI simplicity. Brightness and levels are `uint32_t`, which makes this a generic control plane rather than a direct hardware register format.

## Dependencies and Constraints
Includes `sys/types.h`. Callers must not assume more than 100 levels or names longer than `BACKLIGHTMAXNAMELENGTH`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/backlight.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bio.h

## Purpose
`bio.h` defines the kernel block I/O request object used by GEOM, disks, and lower storage layers.

## Main Interfaces
- `BIO_READ`, `BIO_WRITE`, `BIO_DELETE`, `BIO_GETATTR`, `BIO_FLUSH`, `BIO_ZONE`, and `BIO_SPEEDUP` identify I/O operations.
- `BIO_ERROR`, `BIO_DONE`, `BIO_ONQUEUE`, `BIO_ORDERED`, `BIO_UNMAPPED`, `BIO_VLIST`, `BIO_SWAP`, `BIO_EXTERR`, and speedup flags describe request state and memory layout.
- `struct bio` contains command/flags, target device/disk, offset/length/counts, data or page-array backing, completion callback, GEOM links, parent/child accounting, zone command args, timing, task callback, spare fields, optional tracking, physical block number, and extended error state.
- `struct bio_queue_head` provides queue metadata for disk sorting and batching.
- Kernel functions include `biodone`, `biofinish`, `biowait`, `bioq_*`, and `physio`.

## Implementation Notes
The structure separates consumer-private and provider-private fields and supports chained or split I/O through `bio_parent`, `bio_children`, and `bio_inbed`. `bio_error` aliases the embedded extended-error structure's errno field, keeping older code compatible while supporting richer error detail.

## Dependencies and Constraints
The full structure is visible only under `_KERNEL`. It depends on GEOM types, disk zone arguments, queue macros, and optional buffer tracking. `BIO_ORDERED` expresses queue ordering semantics and must be honored by providers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bitcount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bitcount.h

## Purpose
`bitcount.h` provides FreeBSD population-count helpers for 16-, 32-, 64-bit, `long`, and `int` values.

## Main Interfaces
- Constant-expression helpers: `__const_bitcount8`, `__const_bitcount16`, `__const_bitcount32`, and `__const_bitcount64`.
- Runtime helpers: `__bitcount16`, `__bitcount32`, `__bitcount64`, `__bitcountl`, and `__bitcount`.

## Implementation Notes
When `__POPCNT__` is available, the header maps to compiler builtins. Otherwise it uses SWAR-style arithmetic masks and shifts. On LP64, 64-bit counts are computed directly; on 32-bit platforms, 64-bit counts are split into two 32-bit halves.

## Dependencies and Constraints
Includes `sys/_types.h`. The names are internal-style double-underscore helpers, commonly used by higher-level bitset and bitstring code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bitcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bitset.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bitset.h

## Purpose
`bitset.h` implements fixed-size bitset operations as macros over structures containing a `__bits[]` long array.

## Main Interfaces
- Primitive operations include clear, set, test, zero, fill, set-of-one, copy, compare, subset, overlap, count, first-set, first-set-at, first-last-set, and foreach iteration.
- Set algebra includes AND, ANDNOT, OR, ORNOT, XOR, and two-source variants.
- Atomic forms include bit set/clear, test-and-set/clear, OR/AND updates, acquire variants, and release copy stores.
- Public `BIT_*` aliases are enabled for `_KERNEL` or `_WANT_FREEBSD_BITSET`.
- Kernel allocation helpers `BITSET_ALLOC` and `BITSET_FREE` wrap `malloc`/`free` with `BITSET_SIZE`.

## Implementation Notes
The header optimizes single-word constant-size bitsets through `__constexpr_cond`, avoiding division/modulo when the compiler can prove one word. Iteration uses a local word cache and `ffsl()` so it can traverse set or clear bits non-destructively. Atomic operations operate word-by-word and rely on `atomic_*_long` semantics.

## Dependencies and Constraints
The consuming bitset type must define `__bits[]`, and the environment must provide `_BITSET_BITS` and `__bitset_words()`. Atomic macros require machine atomic support. Full-set checks compare all backing words to all-ones and do not mask unused high bits in the last word.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bitset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bitstring.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bitstring.h

## Purpose
`bitstring.h` provides the traditional BSD variable-length bit string API over arrays of `unsigned long`.

## Main Interfaces
- Defines `bitstr_t`, `bitstr_size()`, `bit_alloc()`, and `bit_decl()`.
- Single-bit operations: `bit_test`, `bit_set`, and `bit_clear`.
- Range operations: `bit_ntest`, `bit_nset`, and `bit_nclear`.
- Search operations find first set/clear bit from an offset and first set/clear contiguous area of a requested size.
- `bit_count` counts set bits in a bounded range.
- `bit_foreach` and `bit_foreach_unset` iterate over set or unset bits.

## Implementation Notes
The implementation is inline and word-oriented. Range masks are built from start/stop bit offsets, allowing efficient partial-word handling at both ends and full-word loops in the middle. Area search uses bit manipulation to skip unsuitable runs rather than checking one bit at a time.

## Dependencies and Constraints
Kernel builds use `malloc(..., M_ZERO)` and include `sys/libkern.h`; userland builds use `calloc`. Callers pass bit counts explicitly, and out-of-range search returns `-1`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bitstring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/blist.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/blist.h

## Purpose
`blist.h` declares FreeBSD's bitmap resource-list allocator, historically used for swap/block allocation.

## Main Interfaces
- Defines unsigned disk address type `u_daddr_t`.
- `SWAPBLK_MASK` and `SWAPBLK_NONE` encode valid block ranges and allocation failure.
- `blmeta_t` stores bitmap and largest contiguous-block hint for a radix-tree node.
- `struct blist` tracks total blocks, available blocks, radix coverage, next-fit cursor, and root metadata.
- Functions include create/destroy, alloc/free/fill, resize, avail, print, and stats.

## Implementation Notes
Newly created lists start fully reserved; users free ranges to make them allocatable. The tree radix is the number of bits in `u_daddr_t`, and maximum single allocation is `BLIST_RADIX`.

## Dependencies and Constraints
The structure is tuned for power-of-two metadata sizes. `SWAPBLK_NONE` is an absolute sentinel value, not a flag bit, so callers must handle it distinctly from valid block numbers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/blist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/blockcount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/blockcount.h

## Purpose
`blockcount.h` defines kernel inline helpers for a waitable atomic block/reference counter.

## Main Interfaces
- `blockcount_init()` initializes the counter.
- `blockcount_acquire()` increments by `n`, checking overflow under `INVARIANTS`.
- `blockcount_release()` decrements by `n`, uses a release fence, checks underflow, and wakes waiters when the count reaches zero.
- `blockcount_sleep()` and `blockcount_wait()` wrap internal sleep/wakeup machinery.

## Implementation Notes
The counter stores count and waiter state in the private `blockcount_t` layout from `sys/_blockcount.h`. `blockcount_wait()` loops on `EAGAIN`, so callers get a stable wait-for-zero operation.

## Dependencies and Constraints
Kernel-only. Depends on atomic operations, `KASSERT`, `_BLOCKCOUNT_COUNT`, `_BLOCKCOUNT_WAITERS`, and a lock object supplied by the caller for sleep coordination.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/blockcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/boot.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/boot.h

## Purpose
`boot.h` declares helper functions for converting boot environment and command-line arguments into FreeBSD boot flags.

## Main Interfaces
- `PATH_KERNEL` is `/boot/kernel/kernel`.
- Functions: `boot_env_to_howto`, `boot_howto_to_env`, `boot_parse_arg`, `boot_parse_cmdline_delim`, `boot_parse_cmdline`, and `boot_parse_args`.

## Implementation Notes
This header is a small shared interface between boot parsing code and consumers that need to translate text/environment configuration to `howto` flags.

## Dependencies and Constraints
No includes are required by this header. Implementations are external.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/boot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/boottrace.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/boottrace.h

## Purpose
`boottrace.h` defines lightweight boot, run, and shutdown trace interfaces for kernel and userland.

## Main Interfaces
- Sysctl names: `kern.boottrace.boottrace`, `kern.boottrace.runtrace`, and `kern.boottrace.shuttrace`.
- Message format is bounded by thread-name and event-name lengths.
- Userland macros format a message and call `sysctlbyname()`.
- Kernel macros guard trace emission on `boottrace_enabled`.
- Kernel functions include `boottrace`, reset, resize, and console dump.

## Implementation Notes
Userland `_boottrace()` truncates through `vsnprintf()` but still submits any nonnegative formatted result. Kernel `BOOTTRACE_INIT` supplies `"kernel"` as the thread/actor name.

## Dependencies and Constraints
Userland depends on stdarg/stdio/string/sysctl headers. Kernel trace calls are no-ops when disabled and are controlled by global booleans.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/boottrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/buf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/buf.h

## Purpose
`buf.h` defines the FreeBSD kernel buffer-cache buffer header, buffer flags, locking helpers, and the VFS buffer I/O function surface.

## Main Interfaces
- `struct buf` describes cached or active filesystem/block I/O: associated `bufobj`, sizes, data pointer, BIO command/flags, offsets, residual count, callbacks, checksum hash, vnode links, queue state, locks, dirty ranges, VM pages, credentials, cluster/dependency state, optional tracking, and extended errors.
- `B_*`, `BX_*`, and `BV_*` flags describe buffer lifecycle, cache validity, delayed writes, clustering, VMIO, background writes, vnode clean/dirty list state, and filesystem-private state.
- Buffer lock macros wrap `lockmgr`, including timed locks, unlock assertions, ownership transfer to kernel process for async I/O, and invariant assertions.
- Inline helpers call bufobj operations (`bwrite`, `bstrategy`) and softdep-style `bioops` hooks (`buf_start`, `buf_complete`, `buf_deallocate`, `buf_countdeps`).
- Declares bread/getblk/write/release/cluster/vmap/page-busy and vnode association APIs.

## Implementation Notes
The header documents field protection domains: buffer lock, owning `bufobj` lock, queue lock, or dependency-specific lock. `b_bcount` is the requested valid range, while `b_bufsize` is allocation size. Dirty ranges are byte-granular and normally clipped at `b_bcount`.

## Dependencies and Constraints
Most APIs are kernel-only. Buffer correctness depends on honoring lock ownership, not mixing incompatible flags such as `B_INVALONERR` with async use, and using `bufobj` operation vectors for strategy/write dispatch.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/buf_ring.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/buf_ring.h

## Purpose
`buf_ring.h` implements a power-of-two circular pointer ring used by performance-sensitive queues such as network driver transmit queues.

## Main Interfaces
- `struct buf_ring` stores producer and consumer head/tail indexes, masks, sizes, drop count, optional debug lock, and flexible ring storage.
- `buf_ring_enqueue()` is multi-producer safe.
- `buf_ring_dequeue_mc()` is multi-consumer safe.
- `buf_ring_dequeue_sc()`, `buf_ring_advance_sc()`, `buf_ring_putback_sc()`, `buf_ring_peek()`, and `buf_ring_peek_clear_sc()` are single-consumer or lock-protected operations.
- `buf_ring_full()`, `buf_ring_empty()`, and `buf_ring_count()` inspect state.
- Kernel and userland allocation/free variants are provided.

## Implementation Notes
Head and tail counters are only masked when indexing, leaving high bits as an epoch to reduce ABA-style wrap confusion. Atomic acquire loads and release stores enforce ordering between data publication and tail advancement. Multi-party operations spin until prior operations complete in order.

## Dependencies and Constraints
Ring size must be a power of two. Single-consumer functions assume external serialization. Debug mode checks duplicate enqueues, dangling entries, and lock ownership.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/buf_ring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bufobj.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bufobj.h

## Purpose
`bufobj.h` defines the buffer object abstraction that owns clean and dirty buffers independently of vnodes.

## Main Interfaces
- `struct bufv` combines a TAILQ sorted block list, a pctrie root, and a buffer count.
- `struct buf_ops` supplies write, strategy, sync, and delayed-flush operations.
- `struct bufobj` contains an rwlock, operation vector, VM object pointer, syncer list link, private data, clean and dirty buffer sets, output count, flags, domain, and block size.
- Macros dispatch `BO_STRATEGY`, `BO_SYNC`, `BO_WRITE`, and `BO_BDFLUSH`.
- Lock macros wrap the bufobj rwlock.
- Functions initialize, reference/drop write activity, invalidate buffers, wait for writes, sync, and background flush.

## Implementation Notes
The architectural comment explains why buffer cache ownership moved from vnodes to `bufobj`: GEOM and other non-vnode code also need buffer-cache integration.

## Dependencies and Constraints
Visible for `_KERNEL` or `_KVM_VNODE`. Locking comments mark constant fields, vnode-protected fields, and sync-mutex-protected fields. `BO_DEAD` is intended for invariant checking.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bufobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bus.h

## Purpose
`bus.h` is the main FreeBSD newbus/device/resource interface header, covering user-visible device control structures, kernel driver APIs, resource management, interrupt setup, device classes, module registration, and bus-space convenience macros.

## Main Interfaces
- User ABI: `struct u_businfo`, `struct u_device`, device state enum, exported device flags, `struct devreq`, and `/dev/devctl2` ioctl constants for attach, detach, enable, disable, suspend, resume, driver selection, rescan, delete, freeze/thaw, reset, and path lookup.
- Kernel abstractions: `driver_t`, `devclass_t`, device methods, interrupt filter/handler types, interrupt type/trigger/polarity enums, bus ivar ranges, CPU set selectors, resource map structures, and resource lists.
- Generic bus helpers: child creation, resource allocation/activation/mapping/release, interrupt setup/teardown/suspend/resume, DMA/bus tag lookup, domain lookup, reset helpers, property lookup, and device path generation.
- Device/devclass APIs manage probing, attaching, detaching, softc, flags, state, sysctls, children, quiet/verbose settings, and driver classes.
- Boot pass constants order driver attachment from root and bus discovery through scheduler and default drivers.
- Module macros register drivers with buses, optionally in early passes.
- Generated bus-space wrappers operate on `struct resource *` for read/write/set/copy/barrier/peek/poke at 1/2/4/8-byte widths and stream variants.

## Implementation Notes
The header preserves compatibility with older bus resource APIs using `_Generic` and variadic macro dispatch. Device property types let firmware-backed buses normalize byte order or handles. Resource-map requests include size, offset, length, and memory attributes for controlled mapping.

## Dependencies and Constraints
The kernel section depends on `kobj`, eventhandlers, devctl, generated `device_if.h`/`bus_if.h`, and machine bus/DMA types. Many operations require holding the newbus topology lock; the header exposes lock/unlock/assert helpers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus_dma.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bus_dma.h

## Purpose
`bus_dma.h` defines the machine-independent DMA mapping API used by FreeBSD drivers and busdma implementations.

## Main Interfaces
- DMA flags describe sleep behavior, preallocation, coherent/zeroed memory, bus-private flags, no-write/no-cache hints, page-offset preservation, and mbuf loading.
- Sync operations: preread, postread, prewrite, postwrite.
- `bus_dma_segment_t` describes DMA address/length pairs.
- Kernel APIs create/destroy DMA tags, set domains, create/destroy maps, allocate/free DMA memory, load buffers/mbufs/uio/CCBs/bios/crypto/memdesc/page arrays, sync, and unload.
- Template APIs allow stack-allocated `bus_dma_template_t`, parameter key/value filling, clone, and tag creation.
- Callback types report loaded segments and errors, with one variant including total map size.

## Implementation Notes
DMA tags encode constraints such as alignment, boundary, low/high reachable addresses, maximum transfer size, segment count, and max segment size. The newer template fill interface avoids long positional argument lists while keeping the older `bus_dma_tag_create()` ABI.

## Dependencies and Constraints
Always included through machine bus DMA headers rather than directly. Kernel-only sections depend on opaque busdma types from `sys/_bus_dma.h`, VM/page structures, and subsystem buffer descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus_dma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus_dma_internal.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bus_dma_internal.h

## Purpose
`bus_dma_internal.h` declares the internal contract between machine-dependent and machine-independent busdma layers.

## Main Interfaces
- `_bus_dmamap_complete()` finalizes segment loading.
- `_bus_dmamap_load_buffer()` loads virtual buffers with a pmap.
- `_bus_dmamap_load_ma()` loads VM page arrays.
- `_bus_dmamap_load_phys()` loads physical ranges.
- `_bus_dmamap_waitok()` handles deferred waitable loads and callback state.

## Implementation Notes
This is explicitly not driver-facing. It provides the hooks MI code can call into MD implementations for the actual address translation and segment construction work.

## Dependencies and Constraints
Assumes busdma types, `struct pmap`, `struct vm_page`, `struct memdesc`, and DMA callback types are already in scope through the including busdma implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus_dma_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus_san.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/bus_san.h

## Purpose
`bus_san.h` is the sanitizer interposition layer for `bus_space(9)` memory-mapped I/O accessors.

## Main Interfaces
- Declares sanitizer-prefixed bus-space functions for read/write, multi, region, stream, set, copy, peek, poke, and mapping helpers.
- Supports widths 1, 2, 4, and 8 using `uint8_t`, `uint16_t`, `uint32_t`, and `uint64_t`.
- When not compiling `SAN_RUNTIME`, remaps normal `bus_space_*` names to sanitizer-prefixed interceptors.

## Implementation Notes
The header mirrors `atomic_san.h` for bus-space operations. It lets kernel sanitizers observe device memory accesses without changing each bus driver. The miscellaneous mapping helpers include map, unmap, subregion, alloc, free, and barrier.

## Dependencies and Constraints
Requires inclusion through `machine/bus.h` and a `SAN_INTERCEPTOR_PREFIX`. Runtime code disables aliases to avoid intercepting its own interceptor implementations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/bus_san.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/busdma_bufalloc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/busdma_bufalloc.h

## Purpose
`busdma_bufalloc.h` declares a UMA-backed DMA buffer pool manager for platform busdma implementations.

## Main Interfaces
- `struct busdma_bufzone` describes a zone size, UMA zone handle, and name.
- `busdma_bufalloc_t` is an opaque allocator handle.
- `busdma_bufalloc_create()` builds power-of-two buffer zones from a minimum alignment up to page size.
- `busdma_bufalloc_destroy()` tears down an allocator.
- `busdma_bufalloc_findzone()` selects a zone for a requested size.
- Built-in uncacheable alloc/free functions support platforms with `VM_MEMATTR_UNCACHEABLE`.

## Implementation Notes
Buffers in each zone are aligned to their size, making them page-contained and boundary-friendly. The design helps busdma quickly decide whether tag constraints permit using a pooled buffer without bouncing.

## Dependencies and Constraints
Includes `machine/bus.h` and `vm/uma.h`. Minimum alignment is also minimum allocation size and must not be below cache-line size on software-coherent platforms.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/busdma_bufalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/callout.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/callout.h

## Purpose
`callout.h` defines FreeBSD kernel timer/callout flags and scheduling APIs.

## Main Interfaces
- Internal/external callout flags track active, pending, processed, shared-lock, deferred migration, direct execution, and handler lock-return behavior.
- Scheduling flags support direct execution, precision encoding, hardclock alignment, absolute times, precalculated times, and signal-catching sleeps.
- Macros expose `callout_active`, `callout_deactivate`, `callout_pending`, `callout_drain`, reset/schedule variants, and CPU-local scheduling.
- Functions initialize callouts, reset them with sbintime precision, schedule/stop/drain, process callouts, and compute effective time/precision.

## Implementation Notes
The header distinguishes caller-visible `c_flags` from subsystem-owned `c_iflags`. The comments stress that callers must hold their own lock when manipulating visible state to avoid races.

## Dependencies and Constraints
Kernel-only APIs depend on `sys/_callout.h`, lock objects, `PCPU_GET(cpuid)`, and `tick_sbt`. `CALLOUT_MPSAFE` remains as deprecated compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/callout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/caprights.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/caprights.h

## Purpose
`caprights.h` defines the storage type for Capsicum descriptor rights and declares common kernel right sets.

## Main Interfaces
- Defines `CAP_RIGHTS_VERSION_00` and current `CAP_RIGHTS_VERSION`.
- `struct cap_rights` stores rights words in `cr_rights[]`; version 0 uses two `uint64_t` words.
- Declares `cap_rights_t`.
- Kernel builds declare many predefined const right sets, such as read, write, seek, mmap, ioctl, fcntl, socket, process descriptor, and VFS operation rights.

## Implementation Notes
The bit layout reserves high bits for version and index metadata. The version plus array-size encoding allows future extension while retaining compact fixed ABI for version 0.

## Dependencies and Constraints
The header itself does not include other headers for `uint64_t`, so consumers must have suitable type context. Predefined right constants are only declared under `_KERNEL`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/caprights.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/capsicum.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/capsicum.h

## Purpose
`capsicum.h` defines FreeBSD Capsicum capability-mode rights, helper APIs, and kernel enforcement hooks.

## Main Interfaces
- `CAPRIGHT(idx, bit)` encodes a rights word with version/index metadata.
- Rights cover file I/O, seeking, mmap protections, creation/execution/fsync/truncate, lookup and `*at` operations, VFS metadata changes, sockets, MAC labels, semaphores, event/kqueue, ioctl, process descriptors, extattrs, ACLs, inotify, and grouped socket/kqueue rights.
- `CAP_ALL`, `CAP_NONE`, version/index helpers, fcntl masks, and `CAP_IOCTLS_ALL` support rights construction and limits.
- User/kernel common functions initialize, set, clear, validate, merge, remove, test, and compare rights.
- Kernel-only helpers include inline initializers, transient contains checks, `cap_check`, VM protection conversion, filedesc rights extraction, ioctl/fcntl checks, and capability-mode macros/tracing.
- Userland functions include `cap_enter`, `cap_sandboxed`, `cap_getmode`, descriptor rights/ioctl/fcntl limit and query APIs.

## Implementation Notes
Rights are split across indexed 64-bit words. Many compound rights intentionally include prerequisites such as `CAP_LOOKUP`, `CAP_READ`, `CAP_WRITE`, or `CAP_SEEK`. Kernel inline checks optimize the common success path and call failure reporting only when rights are missing.

## Dependencies and Constraints
Depends on `sys/param.h`, `sys/caprights.h`, `sys/file.h`, and `sys/fcntl.h`. Kernel currently statically asserts support for rights version 0 only.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/capsicum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cdefs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cdefs.h

## Purpose
`cdefs.h` is FreeBSD's central compiler, language, ABI, and annotation compatibility header.

## Main Interfaces
- Provides feature-test fallbacks for `__has_attribute`, `__has_extension`, `__has_feature`, `__has_include`, and `__has_builtin`.
- Defines compiler/version checks, compiler barriers, inline/volatile compatibility, stringification, token concatenation, and K&R/ANSI prototype macros.
- Declares common attributes: weak, noreturn, const/pure, unused/used, deprecated, packed, aligned, section, alloc-size, malloc-like, always-inline, noinline, warn-unused-result, format checking, visibility, and more.
- Supplies C11/C++ compatibility for `_Alignas`, `_Alignof`, `_Noreturn`, `_Static_assert`, `_Thread_local`, `_Generic`-like `__generic`, and `__min_size`.
- Defines branch prediction, `__containerof`, offsetof/range helpers, symbol references/versioning, RCS/COPYRIGHT embedding, dequalification casts, rename support, visibility settings, nullability macros, type tags, lock annotations, sanitizer opt-outs, stack protector opt-out, and alignment builtins/fallbacks.

## Implementation Notes
This header deliberately centralizes compiler-specific conditionals so the wider source tree can use stable FreeBSD macros. It handles GCC, Clang, TinyCC, C, and C++ modes with extensive fallbacks.

## Dependencies and Constraints
It errors if `_KERNEL` and `_STANDALONE` are both defined. Includes `sys/_decls.h` and `sys/_visible.h`. Some macros expand to compiler attributes only when the active compiler supports them.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cdio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cdio.h

## Purpose
`cdio.h` defines the shared kernel/userland ioctl ABI for CD-ROM audio, TOC, subchannel, volume, tray, and drive capability operations.

## Main Interfaces
- Address and TOC structures include `union msf_lba`, `struct cd_toc_entry`, subchannel headers, position data, media catalog data, track info, and aggregate subchannel info.
- Play requests support track/index, block range, and minute/second/frame ranges.
- TOC and subchannel ioctls read headers, entries, single entries, and subchannel data.
- Audio controls include patch routing, get/set volume, mono/stereo/mute/left/right, pause/resume/start/stop/reset, pitch, debug toggles, media allow/prevent/eject/close.
- `struct ioc_capability` reports play, routing, and special function capabilities.

## Implementation Notes
The header preserves legacy spellings such as `CDIOCSETSTERIO` alongside corrected aliases. Bitfields in `cd_toc_entry` account for byte order. Pointer-bearing ioctl structures let userland provide output buffers for variable-size TOC/subchannel results.

## Dependencies and Constraints
Includes `sys/ioccom.h`, and userland includes `sys/types.h`. The ABI is old and hardware-oriented, so callers must handle unsupported ioctls and drive capability variation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cdrio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cdrio.h

## Purpose
`cdrio.h` defines ioctl structures and constants for CD-R/CD-RW writer control.

## Main Interfaces
- `struct cdr_track` describes track data block type, audio preemphasis, and test-write mode.
- `struct cdr_cue_entry` and `struct cdr_cuesheet` describe cue-sheet entries, session format, session type, and test write behavior.
- Format capacity structures describe available formatting layouts and selected format parameters.
- Ioctls cover blanking, next writable address, writer/track initialization, cue sending, flush, fixation, read/write speed, block size get/set, progress, read format capacities, and formatting.

## Implementation Notes
Data block constants enumerate raw, subchannel, Mode 1/2, XA, reserved, and vendor-specific layouts. Session constants distinguish CD-ROM, CDI, XA, final, multisession, and none/reserved modes.

## Dependencies and Constraints
Includes `sys/ioccom.h`. The header only defines the ABI; driver support varies by optical device capability.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cdrio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cfictl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/cfictl.h

## Purpose
`cfictl.h` defines ioctls for Common Flash Interface query access and Intel StrataFlash protection registers.

## Main Interfaces
- `struct cfiocqry` requests a CFI query read using offset, byte count, and caller buffer pointer.
- `CFIOCQRY` reads CFI query data.
- Protection register ioctls get factory PR, get/set OEM PR, get protection lock register, and set protection lock register.

## Implementation Notes
The interface is small and direct, exposing low-level flash metadata/control operations through ioctl numbers in the `'q'` group.

## Dependencies and Constraints
The header assumes `u_char`, `uint64_t`, `uint32_t`, and ioctl macros are already available from surrounding includes. Protection register operations are hardware-specific.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/cfictl.h -->