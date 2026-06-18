# Group Research: group_1280_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_atomic_h_sources_os_bs_3dc5987c5b87

Scope: subset A from `Docs/research_subset_a.md`, covering the listed NetBSD `sys/sys` headers. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/atomic.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/atomic.h

## Scope

Defines NetBSD's legacy atomic operation prototypes, memory barriers, sanitizer-renamed atomic entry points, and kernel atomic load/store helper macros.

## APIs And Behavior

- Declares `atomic_add_*`, `atomic_and_*`, `atomic_or_*`, `atomic_cas_*`, `atomic_swap_*`, `atomic_inc_*`, and `atomic_dec_*` families for 32-bit, 64-bit, int, long, unsigned variants, and pointers.
- Provides `_nv` variants returning the new value and `_ni` compare-and-swap variants.
- Exposes userland-compatible `atomic_cas_16()` and `atomic_cas_8()`.
- Declares memory barriers: `membar_acquire`, `membar_release`, `membar_producer`, `membar_consumer`, `membar_sync`, deprecated `membar_enter/exit`, and optional `membar_datadep_consumer`.
- Under KASAN, KCSAN, or KMSAN, redirects public atomic names to sanitizer wrapper symbols.
- In kernel builds, defines `atomic_load_relaxed/consume/acquire` and `atomic_store_relaxed/release` using volatile accesses plus barriers, with optional KCSAN instrumentation or hash-locked store fallback.

## Dependencies

- Includes `sys/types.h`, optional `stdint.h`, kernel sanitizer options, `sys/cdefs.h`, and `libkern`.
- Assumes machine atomic implementations and memory barrier functions exist elsewhere.

## Risks And Invariants

- Kernel load/store macros assert object size is at most 4 bytes on ILP32 and 8 bytes on LP64, and that pointers are naturally aligned.
- Non-C11 implementation assumes aligned volatile access of supported sizes is atomic.
- Sanitizer macro redirection must stay complete across all atomic families or instrumentation can miss operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/atomic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/audioio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/audioio.h

## Scope

Defines the public audio and mixer ioctl ABI shared by NetBSD audio drivers and userland.

## APIs And Data Structures

- `audio_prinfo` and `audio_info` describe play/record parameters, buffer sizing, watermarks, pause/error/open/active state, and modes `AUMODE_PLAY`, `AUMODE_RECORD`, `AUMODE_PLAY_ALL`.
- `AUDIO_INITINFO()` initializes `audio_info` fields to all-ones for partial update semantics.
- Defines device identification via `audio_device`, transfer offset reporting via `audio_offset`, and encoding discovery via `audio_encoding`.
- Enumerates audio encodings including u-law, A-law, signed/unsigned linear LE/BE/native, MPEG layers, and AC3.
- `audio_format` describes driver formats: mode, encoding, valid bits, precision, channels, channel mask, supported frequencies, and priority.
- Audio ioctls cover get/set info, drain/flush, offsets, errors, properties, channel selection, and format query/set.
- Mixer ABI includes `mixer_level`, `mixer_devinfo`, `mixer_ctrl`, mixer type constants, and mixer read/write/devinfo ioctls.
- Provides canonical mixer device, class, and encoding names.

## Dependencies

- Includes `sys/types.h`, `sys/ioccom.h`, and userland `string.h` for `AUDIO_INITINFO`.

## Risks And Invariants

- Structure layout is an ABI; field size/order changes affect userland.
- `audio_format` comments constrain validbits, precision, channels, and frequency_type interpretation.
- Native-endian encoding aliases are kernel-only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/audioio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/biohist.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/biohist.h

## Scope

Wraps `kernhist` tracing for buffer I/O history logging.

## APIs And Behavior

- If `BIOHIST_PRINT` is set, forces `KERNHIST_PRINT`.
- When `BIOHIST` is enabled, maps `BIOHIST_DECL`, `DEFINE`, `INIT`, `INITIALIZER`, `LINK_STATIC`, `LOG`, `CALLED`, `CALLARGS`, and `FUNC` to corresponding `KERNHIST_*` macros.
- Defines default `BIOHIST_SIZE` as 500 if not provided.
- When disabled, all macros expand to no-ops.
- Declares global `biohist`.

## Dependencies

- Includes optional `opt_biohist.h` and `sys/kernhist.h`.

## Risks And Invariants

- Compile-time options entirely control whether logging exists.
- Format and argument macros inherit `kernhist` semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/biohist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bitops.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/bitops.h

## Scope

Provides inline bit operations, integer log helpers, fast 32-bit division helpers, and typed bitmap macros.

## APIs And Behavior

- Defines fallback `ffs32`, `ffs64`, `fls32`, and `fls64`.
- `ilog2()` uses compile-time expansion for constants and `fls32/fls64` for runtime values, returning `-1` for zero.
- `fast_divide32_prepare()` precomputes multiplier and shifts; `fast_divide32()` and `fast_remainder32()` use them to replace division by a fixed divisor.
- Bitmap helpers define typed bitmap structs and macros for size, word, bit, set, clear, test, and zero.

## Dependencies

- Includes `sys/stdint.h`; uses `NBBY`, `__GNUC_PREREQ__`, `__arraycount`, and compiler builtins from common headers.

## Risks And Invariants

- `fast_divide32_prepare()` expects a valid nonzero divisor.
- Bitmap macros rely on GNU `__typeof__`.
- `ilog2()` macro evaluates size/type paths differently for constants and variables.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/blist.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/blist.h

## Scope

Declares the bitmap resource list allocator interface.

## APIs And Data Structures

- Defines `blist_bitmap_t` and `blist_blkno_t` as `uint32_t`.
- Uses opaque `blist_t`.
- `BLIST_NONE` signals allocation failure.
- `BLIST_BMAP_RADIX` is bits per bitmap word; `BLIST_MAX_ALLOC` equals one radix.
- Declares `blist_create`, `blist_destroy`, `blist_alloc`, `blist_free`, `blist_fill`, `blist_print`, and `blist_resize`.

## Behavior

- New blists start fully reserved; callers free ranges before general allocation.
- Intended for block-like resource allocation, with practical limits far below the theoretical 2^31 block capacity.

## Risks And Invariants

- `BLIST_NONE` is an absolute sentinel, not a flag bit.
- Allocation unit and maximum allocation are tied to `blist_bitmap_t` width.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/blist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/boot_duration.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/boot_duration.h

## Scope

Declares an optional boot-duration timer API.

## APIs

- Includes `sys/types.h`.
- If `__HAVE_BOOT_DURATION` is defined, declares `uint64_t boot_duration_timer(void)`.

## Dependencies And Role

- Used by platforms that provide a machine-specific timer suitable for measuring boot duration.

## Risks And Invariants

- Header intentionally exposes nothing on platforms without `__HAVE_BOOT_DURATION`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/boot_duration.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/boot_flag.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/boot_flag.h

## Scope

Defines a macro for translating single-character boot arguments into reboot/autoboot flags.

## APIs And Behavior

- `BOOT_FLAG(arg, retval)` switches on characters and ORs known flags into `retval`.
- Recognizes machine-dependent `1` through `4` as `RB_MD1` through `RB_MD4`.
- Recognizes `a`, `b`, `c`, `d`, `m`, `q`, `s`, `v`, `x`, and `z` for askname, halt, userconf, debugger, miniroot, quiet, single-user, verbose, debug, and silent boot modes.
- Unknown characters leave `retval` unchanged.

## Dependencies

- Includes `sys/reboot.h` for `RB_*` and `AB_*` constants.

## Risks And Invariants

- Ports may not implement every recognized flag.
- Macro mutates its `retval` argument and should be passed an lvalue without side effects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/boot_flag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bootblock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/bootblock.h

## Scope

Defines on-disk boot block, partition, boot-parameter, and platform-specific boot metadata layouts used by NetBSD installboot, disklabel, and boot code.

## APIs And Data Structures

- MBR constants define sector offsets, magic values, boot selector layout, partition table offsets, GPT protective MBR details, partition flags, and a large catalog of MBR partition type IDs.
- Optional `MBRPTYPENAMES` emits a partition type/name lookup table.
- Provides `MBR_PSECT`, `MBR_PCYL`, and `MBR_IS_EXTENDED`.
- Defines packed FAT12/FAT16/FAT32 BIOS parameter blocks, `mbr_bootsel`, `mbr_partition`, and full `mbr_sector`.
- Declares `xlat_mbr_fstype(int)`.
- Defines `shared_bbinfo` block-location metadata.
- Defines platform records for Alpha boot blocks with checksum macro, Apple driver/partition maps and A/UX block zero data, HP300/HPPA LIF volumes/directories, x86 and landisk boot params, next68k disklabels, pmax boot maps, SGI volume headers, VAX boot blocks, and magic/offset/size constants for ews4800mips, macppc, news, sparc, sparc64, sun68k, x68k.

## Behavior

- Structures mirror disk bytes and are mostly packed.
- Alpha checksum sums little-endian 64-bit data words and writes a little-endian checksum.
- x86 boot params include timeout, console settings, password hash, keyboard map, and flags for video reset, password, modules, bootconf, and LBA64 validity.

## Dependencies

- Includes `sys/cdefs.h`, `sys/endian.h`, and integer headers outside assembler.

## Risks And Invariants

- This is disk ABI; offsets, packing, endian conversions, and magic values must remain exact.
- Several definitions are shared with assembler and boot code, so preprocessor guards matter.
- Some platform formats encode historical firmware quirks and fixed sector sizes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bootblock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bswap.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/bswap.h

## Scope

Defines byte-swap function declarations and optimized macro wrappers for 16-, 32-, and 64-bit values.

## APIs And Behavior

- Declares `bswap16`, `bswap32`, and `bswap64`, with optional userland renaming to `__bswap16`/`__bswap32`.
- Defines constant-expression byte-swap macros for 16/32/64-bit integers.
- Uses inline software versions on architectures where compiler bswap builtins are slow.
- Allows `machine/bswap.h` to override variable implementations.
- For GCC, wraps `bswap*` names to use constant folding when possible and variable implementations otherwise.

## Dependencies

- Includes `sys/stdint.h`, `machine/bswap.h`, and cdefs declarations.

## Risks And Invariants

- Function declarations are always present so addresses can be taken.
- Macro replacement after declarations must preserve type casts and side-effect behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bswap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/buf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/buf.h

## Scope

Defines NetBSD kernel buffer headers, buffer flags, priority helpers, clustered I/O metadata, and buffer I/O/cache APIs.

## APIs And Data Structures

- `struct buf` describes kernel I/O buffers with driver queue linkage, callback, error/residual/count fields, device/block numbers, data pointers, vnode association, condition variables, and object lock.
- Field comments identify ownership locks: holder/busy owner, `bufcache_lock`, and `b_objlock`.
- Flags split into cache-owned `BC_*`, object-owned `BO_*`, and holder-owned `B_*`.
- Provides `BUF_ISREAD`, `BUF_ISWRITE`, `B_MEDIA_FLAGS`, and `clrbuf()`.
- Defines allocation/read hints `B_CLRBUF`, `B_SYNC`, `B_METAONLY`, `B_CONTIG`, `B_MODIFY`.
- Kernel APIs include `biodone`, `biowait`, `getiobuf`, `putiobuf`, nested I/O helpers, `physio`, `bread`, `breadn`, `bwrite`, `bawrite`, `bdwrite`, `getblk`, `geteblk`, `incore`, `allocbuf`, `brelse`, `binvalbuf`, `bufinit`, drain/limit helpers, and debug printing.
- Defines buffer I/O priority levels and access macros.

## Dependencies

- Includes pools, queues, mutexes, condition variables, rbtree, and kernel workqueue support.

## Risks And Invariants

- Lock ownership of fields is central to correctness.
- `B_WRITE` is a pseudo-flag equal to zero, so callers must use helper predicates.
- Union storage asserts `struct work` fits in queue storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bufq.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/bufq.h

## Scope

Declares the kernel device-driver buffer queue interface.

## APIs And Behavior

- Kernel-only header; emits an error outside `_KERNEL`.
- Defines strategy constants `BUFQ_STRAT_ANY` and `BUFQ_DISK_DEFAULT_STRAT`.
- Defines allocation flags for raw-block sorting, cylinder sorting, exact strategy selection, and masks.
- Declares `bufq_init`, `bufq_alloc`, `bufq_drain`, `bufq_free`, `bufq_put`, `bufq_get`, `bufq_peek`, `bufq_cancel`, `bufq_getstrategyname`, and `bufq_move`.

## Dependencies

- Forward-declares `struct buf` and `struct bufq_state`.

## Risks And Invariants

- Sorting semantics depend on `struct buf` fields such as `b_rawblkno` and `b_cylinder`.
- `BUFQ_EXACT` prevents fallback to other strategies.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bufq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bufq_impl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/bufq_impl.h

## Scope

Defines internal buffer queue strategy state and registration support.

## APIs And Data Structures

- Kernel-only header.
- `struct bufq_state` stores strategy callbacks: put, get, cancel, fini, private data, flags, and selected strategy.
- `bufq_private()` returns strategy-private storage.
- `buf_inorder()` compares buffers by cylinder plus raw block or by raw block only; treats `NULL` as after any non-NULL buffer and returns false for equal ordering.
- `struct bufq_strat` stores strategy name, init function, priority, refcount, and SLIST linkage.
- `BUFQ_DEFINE()` declares static strategy descriptors.
- Declares `bufq_register` and `bufq_unregister`.

## Dependencies

- Depends on `struct buf` fields and `BUFQ_SORT_*` constants from `bufq.h`.

## Risks And Invariants

- `buf_inorder()` asserts at least one operand is non-NULL.
- Strategy registration state includes refcounts, so unload paths must coordinate with active queues.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bufq_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bus.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/bus.h

## Scope

Top-level bus space and bus DMA abstraction header, selecting new-style or legacy machine bus APIs.

## APIs And Data Structures

- Under `__HAVE_NEW_STYLE_BUS_H`, includes machine bus definitions and defines `bus_space_reservation_t` with accessors/init helpers.
- Defines override bit indices for bus space and bus DMA operations.
- `bus_space_overrides` and `bus_dma_overrides` contain optional function pointers for map/unmap/alloc/free/reserve/DMA map/memory operations.
- Declares bus space and DMA tag create/destroy, reserve/release, reservation map/unmap, and subregion reservation.
- Includes `sys/bus_proto.h` and `machine/bus_funcs.h`.
- Legacy path includes `machine/bus.h` and declares equality helpers.
- Provides dummy bus DMA types for ports with `__HAVE_NO_BUS_DMA`.
- Defines `BUS_ADDR_HI32` and `BUS_ADDR_LO32`.

## Dependencies

- Includes `sys/types.h`, machine bus headers, and cdefs bit helpers.

## Risks And Invariants

- Override structures explicitly require adding new members only at the end.
- New-style and legacy paths expose different implementation details but must satisfy MI drivers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bus_proto.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/bus_proto.h

## Scope

Declares machine-independent bus_space(9) and bus_dma(9) function prototypes and flags.

## APIs And Behavior

- Defines bus space map flags: cacheable, linear, prefetchable.
- Defines bus space barrier flags for read and write ordering.
- Declares bus space map/unmap/subregion/alloc/free/mmap/vaddr/barrier.
- Declares scalar read/write accessors for 1/2/4 bytes and optional 8-byte accessors, including stream variants.
- Declares multi and region read/write prototypes via macros, with KASAN/KCSAN/KMSAN wrapper redirection when enabled.
- Declares set/copy multi/region operations for normal and stream access.
- Declares bus space equality helpers.
- Defines bus DMA flags for sleep behavior, allocation timing, coherent/streaming/cache hints, bus-private flags, read/write direction, and sync operation flags.
- Declares DMA map create/destroy/load/unload/sync, DMA memory alloc/free/map/unmap/mmap, DMA tag subregion, and tag destroy.

## Dependencies

- Uses bus types from machine definitions and optional sanitizer config headers.

## Risks And Invariants

- Sanitizer wrapper macros must match every memory accessor width and variant.
- Direction and sync flags encode cache-coherency protocol; misuse can corrupt DMA transfers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/bus_proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/callback.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/callback.h

## Scope

Declares a small callback chain framework.

## APIs And Data Structures

- `callback_entry` stores TAILQ linkage, callback function pointer, and object pointer.
- `callback_head` stores mutex, condition variable, callback queue, next entry pointer, entry count, running count, and flags.
- Callback functions return `CALLBACK_CHAIN_CONTINUE` or `CALLBACK_CHAIN_ABORT`.
- Declares run, register, unregister, init, and destroy operations.

## Dependencies

- Includes queue, mutex, and condition variable headers.

## Risks And Invariants

- The head tracks current iteration with `ch_next` and `ch_running`, so unregister must coordinate with active callbacks.
- Callback return values control whether a round-robin run continues.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/callback.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/callout.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/callout.h

## Scope

Defines the public callout timer storage ABI and kernel callout APIs.

## APIs And Data Structures

- Public `callout_t` is opaque fixed-size storage of ten pointer slots.
- Defines internal flags `CALLOUT_BOUND`, `PENDING`, `FIRED`, `INVOKING` and user flag `CALLOUT_MPSAFE`.
- Private implementation defines circular queue linkage and `callout_impl_t` with callback, argument, CPU, time, flags, and magic.
- Kernel APIs cover startup, per-CPU init, hardclock processing, init/destroy, set function, reset/schedule, stop/halt, state queries, ack, and CPU binding.

## Dependencies

- Includes `sys/types.h`.

## Risks And Invariants

- `callout_t` must not grow for kernel module ABI compatibility.
- Private structure must fit inside caller-supplied opaque storage.
- MPSAFE flag affects kernel lock expectations for callback execution.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/callout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cctr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cctr.h

## Scope

Declares cycle-counter timecounter state and calibration hooks.

## APIs And Data Structures

- `cctr_state` stores CPU cycle-counter delta, calibration interval, and ticks since calibration.
- Kernel APIs include `cc_init`, `cc_init_secondary`, `cc_get_timecount`, `cc_calibrate_cpu`, and `cc_primary_cc`.
- `cc_hardclock(ci)` increments per-CPU calibration ticks and triggers calibration when the interval is reached.

## Dependencies

- Includes `sys/timetc.h`; uses `struct cpu_info`.

## Risks And Invariants

- `cc_delta` is volatile and used across CPU timecounter calibration paths.
- `cc_hardclock` assumes `ci->ci_cc` layout exists in `cpu_info`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cctr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdbr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cdbr.h

## Scope

Declares the constant database reader API.

## APIs And Behavior

- Defines `CDBR_DEFAULT`.
- Opaque `struct cdbr`.
- Userland-only `cdbr_open(path, flags)` plus shared `cdbr_open_mem`.
- Declares `cdbr_entries`, `cdbr_get`, `cdbr_find`, and `cdbr_close`.
- `cdbr_open_mem` accepts a memory buffer, size, close callback, and callback cookie.

## Dependencies

- Includes `sys/cdefs.h`.
- Kernel/standalone include `sys/types.h`; userland includes `inttypes.h` and `stddef.h`.

## Risks And Invariants

- API returns data by pointer and size, so lifetime is tied to the open database object.
- Userland file-open API is intentionally absent in kernel/standalone builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdbr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdefs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cdefs.h

## Scope

Core NetBSD C portability and compiler-definition header.

## APIs And Behavior

- Provides compiler feature tests `__GNUC_PREREQ__`, `__has_feature`, and `__has_extension`.
- Includes machine cdefs and object-format-specific cdefs for ELF or a.out.
- Defines concatenation/stringification, K&R/ANSI prototype support, reserved keyword compatibility, compile-time assertions, const/volatile/function pointer cast helpers, and `__extension__` fallback.
- Defines attributes for noreturn, pure, const, noinline, always_inline, sentinel, returns_twice, noclone, unused, used, diagnostic/debug usage, no profiling, unreachable, sanitizer suppression, packed/aligned/section, visibility, C++ extern blocks, C99 inline, restrict, and function name fallback.
- Defines symbol renaming outside kernel/standalone builds.
- Provides instruction barrier and branch prediction macros.
- Defines printf/scanf/syslog format attributes and format_arg.
- Provides link set iteration and entry helpers.
- Defines alignment, array count, bit/mask/range helpers, shift-in/out helpers, C/C++ cast helpers, unused-expression helpers, and integer type fit/min/max macros.

## Dependencies

- Pulls in machine and object-format cdefs; relies on compiler predefined integer and char-bit types.

## Risks And Invariants

- This header underpins most other headers; macro compatibility with C, C++, assembler, lint, GCC, Clang, and PCC matters.
- Object-format-specific includes must define aliases, identifiers, and link set primitives expected here.
- Bit/type macros can evaluate arguments in compile-time contexts and must avoid unintended side effects where documented.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdefs_aout.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cdefs_aout.h

## Scope

Provides a.out object-format support macros for symbol labels, aliases, warnings, IDs, copyright strings, and link sets.

## APIs And Behavior

- Defines C symbol labels with leading underscore.
- Implements `___RENAME`, strong/weak aliases, weak extern/reference support, and warning references using assembler directives/stabs where supported.
- Defines `__IDSTRING`, `__RCSID`, `__COPYRIGHT`, and kernel ID/copyright macros.
- Implements a.out link set entries with stabs records and declares link set structure containing length and item array.
- Provides link set start, end, and count macros.

## Dependencies

- Included by `cdefs.h` on non-ELF builds.

## Risks And Invariants

- Assembler syntax differs by compiler and standard mode; macros contain legacy K&R branches.
- Link set layout differs from ELF and includes an explicit length field.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdefs_aout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdefs_elf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cdefs_elf.h

## Scope

Provides ELF object-format support macros for symbol labels, aliases, warnings, ifuncs, ID sections, link sets, and kernel cacheline annotations.

## APIs And Behavior

- Handles optional leading underscores in C labels.
- Implements symbol renaming, strong/weak aliases, weak references, weak visibility, warning references, and GNU indirect function declarations.
- Defines `__SECTIONSTRING`, `__IDSTRING`, `__RCSID`, `__COPYRIGHT`, and kernel metadata macros using ELF sections.
- Implements link set entries in `link_set_<set>` sections, including indexed array entry variants.
- Declares link set start/end symbols and count calculation.
- In kernel builds, defines `__read_mostly` and `__cacheline_aligned` section/alignment annotations.

## Dependencies

- Included by `cdefs.h` on ELF builds.

## Risks And Invariants

- ARM uses `%progbits` and non-ARM uses `@progbits`; ifunc syntax also varies.
- Link set start/stop symbol visibility and weak stop symbol handling are ABI-sensitive.
- Cacheline annotations depend on `COHERENCY_UNIT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdefs_elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/cdio.h

## Scope

Defines CD-ROM, audio CD, subchannel, TOC, changer/load, and optional MMC ioctl ABI.

## APIs And Data Structures

- `union msf_lba` represents minute/second/frame, LBA, or raw address bytes.
- Defines TOC entries and subchannel headers/data with endian-dependent bitfields.
- CD ioctls support play by tracks, blocks, or MSF; read subchannel; read TOC header/entries; read session start; audio patch/volume/channel controls; pause/resume/reset/start/stop/eject/allow/prevent/close; and load/unload.
- Kernel-only buffered variants embed result buffers after request structs.
- Optional kernel or `_EXPOSE_MMC` API defines `mmc_discinfo`, MMC class/state/capability flags, `mmc_trackinfo`, `mmc_op`, and `mmc_writeparams`.

## Dependencies

- Includes `sys/ioccom.h` and `sys/endian.h`.

## Risks And Invariants

- Endian-dependent bitfield order must match device protocol layout.
- Some ioctl command numbers overlap historical commands with different structs.
- MMC section is intentionally not generally exposed to userland unless requested.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/cdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/chio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/chio.h

## Scope

Defines media changer ioctl ABI for robotic storage devices.

## APIs And Data Structures

- Element type constants: picker, slot, import/export portal, and drive.
- Request structs cover move medium, exchange medium, position picker, changer parameters, element status, and volume tag modification.
- Status structs describe fullness, access, exception state, source element, volume tags, vendor data length, SCSI sense fields, and drive target/LUN.
- Defines status validity flags and per-element masks.
- Defines changer event bitmask size and `CHEV_ELEMENT_STATUS_CHANGED`.
- Ioctls include move, exchange, position, get/set picker, get params, initialize element status, old/new get status, and set volume tag.

## Dependencies

- Includes `sys/ioccom.h`.

## Risks And Invariants

- Element type numeric values are used as array offsets by the SCSI changer driver and must not change.
- Pointer fields in ioctl structs require compat handling across user/kernel and ABI widths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/chio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/clock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/clock.h

## Scope

Defines basic calendrical constants and inline helpers.

## APIs And Behavior

- Constants for seconds per minute/hour/day, days per common/leap year, seconds per common/leap year, and `POSIX_BASE_YEAR`.
- `days_in_month(m)` returns month length for 1-12, assuming February has 28 days, or `-1` for invalid months.
- `is_leap_year(year)` implements Gregorian leap-year logic with branch prediction hints.
- `days_per_year(year)` returns 365 or 366.

## Dependencies

- Userland/standalone distinction controls inclusion of `stdint.h`.

## Risks And Invariants

- `days_in_month` does not account for leap years; callers must add February adjustment separately.
- Year type is `uint64_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/clock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/clockctl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/clockctl.h

## Scope

Defines `/dev/clockctl` ioctl ABI for privileged time adjustment delegation.

## APIs And Data Structures

- `clockctl_settimeofday` wraps pointers for `settimeofday`.
- `clockctl_adjtime` wraps delta and old-delta pointers.
- `clockctl_clock_settime` wraps clock id and timespec pointer.
- `clockctl_ntp_adjtime` wraps `timex` pointer plus syscall return value.
- Defines ioctls `CLOCKCTL_SETTIMEOFDAY`, `CLOCKCTL_ADJTIME`, `CLOCKCTL_CLOCK_SETTIME`, and `CLOCKCTL_NTP_ADJTIME`.
- Kernel declarations cover attach/open/close/ioctl/init.

## Dependencies

- Includes `sys/ioccom.h`, `sys/time.h`, and `sys/timex.h`.

## Risks And Invariants

- Ioctl structs intentionally contain user pointers; kernel handlers must copy and validate them.
- ABI mirrors time-related system calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/clockctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_ansi.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_ansi.h

## Scope

Defines internal typedef source macros for fundamental ANSI/POSIX types shared by standard headers.

## APIs And Behavior

- Requires compiler predefined `__PTRDIFF_TYPE__`, `__SIZE_TYPE__`, `__WCHAR_TYPE__`, and `__WINT_TYPE__`.
- Includes machine integer types.
- Defines `_BSD_CLOCK_T_`, `_BSD_PTRDIFF_T_`, `_BSD_SSIZE_T_`, `_BSD_SIZE_T_`, `_BSD_TIME_T_`, `_BSD_CLOCKID_T_`, `_BSD_TIMER_T_`, `_BSD_SUSECONDS_T_`, `_BSD_USECONDS_T_`, `_BSD_WCHAR_T_`, and `_BSD_WINT_T_`.

## Dependencies

- Includes `sys/cdefs.h` and `machine/int_types.h`.

## Risks And Invariants

- Standard headers consume and undef these macros to avoid duplicate typedefs.
- Type selections are ABI-sensitive, especially `time_t`, `size_t`, and pointer-difference types.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_ansi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_const.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_const.h

## Scope

Defines C99 integer constant macros for fixed-width, least/fast-width, and max-width integer types.

## APIs And Behavior

- Requires compiler integer constant suffix macros.
- Uses token-pasting helpers to append suffixes.
- Defines `INT8_C`, `INT16_C`, `INT32_C`, `INT64_C`, `UINT8_C`, `UINT16_C`, `UINT32_C`, `UINT64_C`, `INTMAX_C`, and `UINTMAX_C`.

## Dependencies

- Relies on compiler-provided `__INT*_C_SUFFIX__`, `__UINT*_C_SUFFIX__`, and max suffix macros.

## Risks And Invariants

- Incorrect suffix macros would produce constants with wrong type/rank.
- Header intentionally only defines constant macros, not typedefs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_const.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_fmtio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_fmtio.h

## Scope

Defines C99 `<inttypes.h>` format-string macros for fixed-width integer printf/scanf operations.

## APIs And Behavior

- Requires compiler format macro support, checked via `__INTPTR_FMTd__`.
- Defines `PRI*` macros for signed decimal/integer, unsigned octal/decimal/hex/HEX, least-width, fast-width, max-width, and pointer-width integer formatting.
- Defines `SCN*` macros for scanf decimal/integer/octal/unsigned/hex/HEX variants across the same width families.

## Dependencies

- Relies on compiler-provided `__INT*_FMT*__`, `__UINT*_FMT*__`, least/fast/max/pointer format macros.

## Risks And Invariants

- These macros are string fragments; consumers concatenate them into format strings.
- Format macro correctness is ABI-sensitive for pointer and max-width integer types.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/common_int_fmtio.h -->