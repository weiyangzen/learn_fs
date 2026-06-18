# Group Research: group_571_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__74e9953e8f01

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitmap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitmap.h

This header defines low-level bitmap operations over vectors of `ulong_t`, plus 32-bit word variants on LP64. It provides sizing/indexing macros (`BT_BITOUL`, `BT_SIZEOFMAP`, `BT_WIM`, `BT_BIW`), public bit operations (`BT_TEST`, `BT_SET`, `BT_CLEAR`), and single-word helpers such as `BIT_ONLYONESET` and `BITX`.

Kernel/fake-kernel builds expose bitmap scanning and utility routines (`bt_availbit`, `bt_gethighbit`, `bt_range`, `highbit`, `highbit64`, `lowbit`, `bt_getlowbit`, `bt_copy`, `odd_parity`) and atomic bit mutation macros backed by `<sys/atomic.h>`. Consumers must perform bounds checking and track bitmap sizes themselves.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitset.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitset.h

`bitset.h` wraps bitmap storage in `bitset_t`, with fields for backing words, capacity in words, and fanout. It is available to `_KERNEL`, `_FAKE_KERNEL`, and `_KMEMUSER` consumers.

The API covers lifecycle (`bitset_init`, `bitset_init_fanout`, `bitset_fini`), resizing/capacity, normal and atomic add/delete/test operations, membership/null/find queries, boolean computations (`and`, `or`, `xor`), zero/copy/match helpers. It depends on `bitmap.h` for bit-level representation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bl.h

This is a private FMA blacklist ioctl interface. It defines `BLIOC_INSERT` and `BLIOC_DELETE`, plus `bl_req_t`, which carries a packed FMRI buffer, FMRI size, and event-class reason string. A 32-bit syscall form `bl_req32_t` is provided under `_SYSCALL32`.

`BL_FMRI_MAX_BUFSIZE` caps packed FMRI size at 8192 bytes. Kernel builds also expose `blacklist(int, const char *, nvlist_t *, const char *)`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/blkdev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/blkdev.h

`blkdev.h` defines the common framework interface for simple block-device drivers that need labeling support without full SCSA complexity. It models fixed queue depth, simple linear non-rotating semantics, limited removable-media support, and no cancellation or request priorities.

Key structs are `bd_xfer` for transfer requests, `bd_drive` for drive identity and free-space constraints, `bd_media` for media geometry/state, `bd_ops` for adapter callbacks, and `bd_errstats` for kstats. The current ops version is `BD_OPS_VERSION_2`, adding free-space behavior. Exported functions allocate/free handles, attach/detach handles, report transfer completion/errors, initialize/finalize module state, and notify state changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/blkdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi.h

This is the public ioctl/data contract for the bus-ops fault injector. It defines ioctl command numbers for adding/deleting definitions, start/stop, state checks, broadcasts, clearing logs/errors/definitions, and enumerating handles.

It declares access logging records (`acc_log_elem`, `acc_log` plus 32-bit form), error definitions (`bofi_errdef`), control requests, handle enumeration structures, handle metadata, operation types (`BOFI_EQUAL`, `BOFI_AND`, `BOFI_NO_TRANSFER`, interrupt manipulation modes, etc.), access types (`BOFI_PIO_*`, `BOFI_DMA_*`, `BOFI_INTR`, `BOFI_LOG`), and returned error state (`bofi_errstate`). Several structures have `_SYSCALL32` variants and explicit packing guards for mixed alignment.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi_impl.h

`bofi_impl.h` contains private in-kernel BOFI state. `bofi_errent` stores linked error definitions, live error state, log base, state flags, condition variable, and soft interrupt id. State flags include active device, new message, waiter, and debug.

`bofi_shadow` records saved bus/access/DMA/interrupt operations, hash/list links, matching error-definition links, handle type, original handles, device identity, mapped ranges, pages, flags, and user-memory cookie. Handle type constants distinguish access, DMA, interrupt, and null handles.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootbanner.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootbanner.h

This small header exposes boot-banner rendering for system and zone consoles. It declares `bootbanner_print(void (*)(const char *, uint_t))`, allowing callers to provide an output callback.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootbanner.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootprops.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootprops.h

`bootprops.h` centralizes boot property names for network boot and iSCSI boot, including host/router/server properties, boot MAC, iSCSI target/initator data, CHAP fields, bootpath, and local MAC address.

It also declares kernel networking helper prototypes (`kdlifconfig`, `ksetifflags`, `kifioctl`) and iSCSI boot property structures for initiator, NIC, target, and combined boot state. Helper declarations load/free iSCSI properties and construct VHCI/physical boot paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootprops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootstat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootstat.h

This header defines booter-neutral file metadata structures usable by ILP32 and LP64 boot code. `boottime_t` uses explicit 64-bit seconds/nanoseconds, and `struct bootstat` mirrors the subset of `stat` fields needed by booters, including mode, inode, size, times, block fields, and filesystem type.

`struct compinfo` carries pre-root compressed-file metadata for `kobj`, before later filesystem-level decompression takes over.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bpp_io.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bpp_io.h

`bpp_io.h` defines the ioctl ABI for the bidirectional parallel port driver for the Zebra SBus card. It includes ioctl commands for getting/setting transfer parameters, output pins, error status, and test I/O.

The file defines handshake modes, maximum timeout, `bpp_transfer_parms` timing/handshake configuration, `bpp_pins` input/output pin masks, and `bpp_error_status` for timeout, bus error, and pin error state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bpp_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/brand.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/brand.h

`brand.h` defines the kernel/user interface for Solaris zones brands. It includes `brandsys` subcommands, native/labeled brand names, brand registration attributes, ELF launch metadata, and user handler registration data.

Kernel-only content defines `brand_ops`, `brand_t`, brand dispatch macros, native brand state, registration/lifecycle functions, Solaris-derived brand helper functions, 32-bit registration/ELF data forms, common per-process brand data, and native linker paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/brand.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/buf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/buf.h

`buf.h` defines the classic block I/O buffer header `buf_t`, including device/block identity, byte counts, mapped data union, page I/O fields, vnode association, semaphores, I/O callback, private driver data, and file/offset association. It also defines buffer hash heads, delayed-write heads, and buffer-cache kstats.

The file is the shared declaration point for many buffer flags (`B_BUSY`, `B_DONE`, `B_ERROR`, `B_PAGEIO`, delayed-write/cache/invalidation/retry/failfast flags), list-manipulation macros, and kernel buffer-cache operations (`bread`, `getblk`, `bwrite`, `bdwrite`, `brelse`, `iodone`, `bioerror`, `pageio_setup`, `bioclone`, mapping/copy helpers, flush/invalidate helpers). It is central to filesystem and block I/O paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bufmod.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bufmod.h

This header defines the STREAMS buffering module control ABI. It provides `SBIOC*` ioctls to set/get/clear buffering timeout, chunk size, snapshot length, and mode flags.

It defines defaults and mode flags such as send-on-write, no header, no protocol conversion, deferred chunking, and no drops. `struct sb_hdr` is the per-chunk header carrying timestamps, original message length, captured length, and drop count; 32-bit time compatibility types are included.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bufmod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bustypes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bustypes.h

`bustypes.h` defines legacy bus-space constants used to identify virtual, onboard memory/I/O, SBus, XBox, Multibus, AT bus, FutureBus, arbitrary user bus, and invalid spaces.

It is a compatibility-style header with no functions or structures, preserving numeric address-space identifiers for old bus and driver interfaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bustypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/byteorder.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/byteorder.h

This header provides host/network and explicit endian conversion support. On big-endian builds, `ntohl`/`htonl`/related macros are identity operations; otherwise functions/prototypes and byte-swap macros handle conversion. It also defines `in_port_t` and `in_addr_t` if not already defined.

It exposes `BSWAP_*`, `BMASK_*`, `BE_*`, `LE_*`, and unaligned-safe load/store macros (`BE_IN*`, `LE_IN*`, `BE_OUT*`, `LE_OUT*`) with architecture-specific optimizations when `_ASM_INLINES` is available.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/byteorder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callb.h

`callb.h` defines callback classes and support for checkpoint/resume, panic, halt, uadmin, debugger entry, CPU deep idle, and related system events. Callback classes are numbered through `NCBCLASS`.

It defines `callb_cpr_t`, CPR state flags, timing/retry constants, and macros for initializing CPR state, marking safe/unsafe regions, and exiting. Kernel exports include callback registration/removal/execution, class execution, generic CPR handlers, stopped-thread checking, and callback table locking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callo.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callo.h

`callo.h` is the private kernel header for callout/timeout scheduling. It defines `callout_t`, the 64-bit internal callout id layout, flags, generation/counter/table partitioning, short/long-term ID spaces, realtime/normal table types, hash sizes, heap layout, and callout-list flags.

It also defines locality-aware callout caches, hash/list/heap/table structures, kstat counters, heap sizing policy, and constants for TCP resolution, alignment, maximum ticks, and tolerance. Kernel exports initialize callouts, handle CPU online/offline, react to hrestime changes, and provide `membar_sync`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cap_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cap_util.h

This kernel header defines capacity/utilization accounting support built on CPC performance counters and processor-group hardware relationships. It includes per-counter statistics, per-hardware-PG counter info, multiplexed CPC context state, and per-CPU capacity/utilization state.

Exports initialize/finalize the subsystem, program/unprogram CPC on CPUs, update CPU and processor-group statistics, disable/enable accounting globally, and call platform-specific CPC setup. `CU_CPC_ON` checks whether a CPU has active capacity counters.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cap_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ccompile.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ccompile.h

`ccompile.h` centralizes compiler feature and attribute macros. It computes `__GNUC_VERSION`, defines printf/kprintf format checking attributes, `format_arg`, noreturn, GNU inline behavior, returns-twice, pure/const, alignment, unused, sentinel, used, weak, hidden visibility, cache-line alignment, packed/section, and `__nonstring`.

The header smooths differences between GCC, lint/Sun-style attributes, debug vs release unused-variable handling, and feature tests such as `__has_attribute`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ccompile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cdio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cdio.h

`cdio.h` defines the CD-ROM ioctl ABI and related SCSI command constants. It includes structures for MSF ranges, track/index playback, TOC headers/entries, subchannel data, volume control, raw reads, CD-DA, CD-XA, and subcode reads, with `_SYSCALL32` conversion macros for pointer-bearing forms.

It defines address formats, audio statuses, data/subcode modes, legal block sizes, drive speed constants, `CDROM*` ioctl numbers, optional/vendor SCSI opcodes, READ CD expected sector type constants, and a SCSI command key string table macro for CD I/O debugging.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cladm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cladm.h

`cladm.h` defines private Sun Cluster administration syscall interfaces. Facilities include initialization and configuration; commands expose cluster boot flags, node id, highest node id, global device prefix, and cluster-controlled network addresses.

It defines boot flag bits, cluster network address structures for IPv4/IPv6 plus a 32-bit pointer form, and exports either kernel `cladmin`/`cluster_bootflags` or user `_cladm`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cladm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/class.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/class.h

`class.h` defines the kernel scheduler class switch interface. It groups class-manager operations and per-thread operations into `classfuncs_t`, with functions for class admin, parameter conversion, entering/exiting classes, fork/exit, sleep/wakeup, preemption, swap, tick, nice/priority changes, and process-group handling.

It defines `sclass_t`, scheduler load/install state macros, kernel globals for class tables and ids, loader/lookup/parameter helpers, and many `CL_*` dispatch macros used by core scheduling code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/class.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clconf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clconf.h

This header defines cluster boot configuration access basics. It declares `nodeid_t`, reserves node id zero as `NODEID_UNKNOWN`, and documents that valid node ids run from 1 to `clconf_maximum_nodeid()`.

Kernel exports initialize cluster configuration and fetch current/maximum node ids.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_impl.h

`clock_impl.h` contains private lbolt clock implementation definitions for kernel/kmemuser builds. It defines default `HZ`, thresholds for switching between event-driven and cyclic-driven lbolt, and cache-line-conscious per-CPU/global lbolt tracking structures.

It exports lbolt source functions, the hybrid function pointer, soft interrupt hooks, debugger entry/return accounting, and `lb_info`. Macros provide wait-free, fast-path, and no-account lbolt values while compensating for debugger time.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_tick.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_tick.h

This header defines data structures for parallelized clock tick accounting. `clock_tick_cpu_t` tracks per-CPU softint handle, pending tick work, lbolt snapshot, and CPU scan range; `clock_tick_set_t` tracks shared ranges.

It defines CPU offline and xcall-safety macros, maximum CPUs per tick-processing unit, weak softint hooks, `clock_tick`, `membar_sync`, and `hires_tick`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_tick.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb.h

`cmlb.h` defines the common media label/block interface used by target disk drivers. It exposes geometry and media attribute structures, attach behavior flags, validation flags, target callback ops (`tg_rdwr`, `tg_getinfo`), target command constants, VTOC-dependent minor encoding shifts, and opaque `cmlb_handle_t`.

The exported API allocates/frees handles, attaches/detaches devices, validates/invalidates labels, queries partition and EFI capacity information, handles label ioctls, implements label-aware `prop_op`, reports devid storage block, and handles close behavior. The header documents callback contexts and error returns in detail.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb_impl.h

`cmlb_impl.h` is the private state layout for common media labeling. It defines fdisk partition counts, system partition maps, special minor nodes (`P0_RAW_DISK`, fdisk p1-p4), log masks, label validity constants, 1TB/2TB VTOC limits, and minor decoding macros.

The core `cmlb_lun` state tracks device info, target ops/cookie, lock, current label type/state, VTOC/EFI data, maps, geometry, capacity, partition/minor-node state, removable/hotplug flags, and behavior flags. Callback macros wrap target read/write/getinfo operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmn_err.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmn_err.h

This header declares kernel diagnostic printing interfaces. Severity constants include continuation, note, warning, panic, and ignore.

It exports `cmn_err`, zone-aware variants, device-aware variants, `printf`/`zprintf`/`uprintf`, `snprintf`/`sprintf` variants, and `panic`/`vpanic`, with `__KPRINTFLIKE`, `__KVPRINTFLIKE`, and printf-like annotations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmn_err.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmt.h

`cmt.h` defines chip multithreading processor-group support. It declares CMT scheduling policies (`NO_POLICY`, `BALANCE`, `COALESCE`, `AFFINITY`), CMT processor-group data, lgroup linkage, utilization macros, and capacity calculation.

Kernel functions update processor-group load, handle CPU startup, test migration feasibility, ask platform policy/ranking callbacks, balance threads, and enable/disable padding for hardware group types.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/compress.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/compress.h

This small header declares generic compression helpers: `compress`, `decompress`, and `checksum32`. It depends only on `sys/types.h` and exposes byte-count-oriented interfaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar.h

`condvar.h` defines the public kernel condition variable interface. `kcondvar_t` is an opaque 16-bit public representation, and `kcv_type_t` distinguishes default and driver condition variables.

Kernel builds define timeout resolution values for relative waits, validation macro `TIME_RES_VALID`, and prototypes for init/destroy, wait, stop-aware wait, timed waits, high-resolution timed waits, relative timed waits, signal-interruptible waits, swap/core variants, signal/broadcast, and absolute `waituntil` behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar_impl.h

This private condition-variable implementation header defines `condvar_impl_t` with a waiter count and `CV_HAS_WAITERS`.

It also defines `cvwaitlock_t`, a reader/writer-style lock built from a mutex and condition variable, allowing recursive reader entry while a writer may be waiting. Macros initialize/destroy it, enter/exit read or write mode, and downgrade write to read. The comments explicitly note possible writer starvation and no priority inheritance.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conf.h

`conf.h` defines driver/module configuration interfaces and flags. Kernel content declares STREAMS module switch entries, device ops table globals, stream table lookup macros, device attach/detach/probe/quiesce wrappers, non-DDI block/character device call-through helpers, and property/poll/mmap/devmap entry points.

It also defines driver flags for new/old style, tape, MT safety, STREAMS perimeter modes and modifiers, 64-bit offset support, synchronous STREAMS, devmap, hotplug, unsigned 64-bit uio offset, direct transport, interruptible open, and single-instance modules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consconfig_dacf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consconfig_dacf.h

This header defines console autoconfiguration state used by DACF. It declares keyboard/mouse property nodes (`cons_prop_t`) and overall console configuration state (`cons_state_t`) with firmware paths, framebuffer path, input type, keyboard problem state, LDI handles, mux ids, vnode pointers, lock, discovered keyboard/mouse properties, terminal-emulator support, and initialization flags.

It defines console input type bits, boot/driver-loaded configuration states, debug severity levels, `DPRINTF` aliasing, and `prom_io_use_kernel`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consconfig_dacf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consdev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consdev.h

`consdev.h` declares canonical pseudo-device paths and globals for real, virtual, workstation, mouse, keyboard, stdin, framebuffer, and diag console devices/vnodes. It defines console mode constants for firmware vs kernel framebuffer console.

It also defines console polled I/O ioctls, abort-enable ioctls, keyboard type ioctl, polled-I/O ABI version constants, key state enum, opaque argument pointer, and `cons_polledio` callback vector for entering/exiting, reading, and writing polled console I/O. Workstation-console framebuffer open/close ioctls are also included.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conskbd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conskbd.h

`conskbd.h` defines private state for the console keyboard STREAMS aggregation layer. It includes STREAMS, console-device, keyboard, and keyboard-translation dependencies.

The header models lower keyboard queues, queued/pending messages, lower-queue states, ioctl/message tracking, and overall console keyboard state. It is used to multiplex and coordinate keyboard input below the console abstraction.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conskbd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consms.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consms.h

`consms.h` defines private console mouse state. It sets default screen dimensions and pointer acceleration parameters, plus helper `CONSMS_MAX`.

The file defines lower-queue state, ioctl reply callback type, lower queue records, response records, message records, and aggregate console mouse state, covering queued messages, screen/parameter state, and STREAMS coordination.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/console.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/console.h

`console.h` defines console ioctl commands for fetching terminal type and device, plus result structures and 32-bit forms. `MAX_TERM_TYPE_LEN` limits terminal type strings.

Kernel declarations provide console size lookup, formatted printing, raw string output, line input, character input, enter/exit handling, and globals for the console vnode and console taskq.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/console.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consplat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consplat.h

`consplat.h` declares platform callbacks for console discovery and terminal-emulator details. Functions report whether polled debug and serial keyboard/mouse are supported, return keyboard/framebuffer/mouse/stdin/stdout/diag paths, identify stdin/stdout device types, provide terminal colors/inversion/font/size/position information, hide firmware cursor, and resolve virtual console path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consplat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/containerof.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/containerof.h

This header defines the private illumos `__containerof(member_ptr, struct_type, member_name)` macro. With GCC 3.1+ it uses statement expressions and `__typeof` assignment for extra type checking; otherwise it falls back to offset arithmetic.

It depends on `sys/stddef.h` for `offsetof` and returns the containing structure pointer by subtracting the member offset from the member address.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/containerof.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract.h

`contract.h` defines the public base contract ABI. It introduces event ids, maximum parameter size, common event/detail/flag constants, common parameter ids, status field names, contract states, and contract type ids.

Public structures include `ct_event_t`, `ct_status_t`, and `ct_param_t`, carrying event buffers, status buffers, state, type, holder, zone, event counts, detail level, critical/informative masks, cookie, and parameter payload references.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device.h

This header defines the device-contract public interface. It forward-declares device template and contract structures, defines device state transition events (`ONLINE`, `DEGRADED`, `OFFLINE`), accepted parameter bits, nonegotiable/minor terms, parameter operation constants, status field names, and default acknowledgement timeout.

It is layered on the generic contract ABI in `contract.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device_impl.h

`device_impl.h` defines kernel-private device contract structures. Device templates store common template data, accepted event set, nonegotiable flags, minor path, and acknowledgement time. Device contracts store common contract data, devinfo pointer, dev_t, spec type, device state, event set, nonegotiable flags, vnode data, minor path, and ack time.

It declares device contract type state and lifecycle/event functions for init, offline negotiation, degrade/undegrade, open, and removing contracts tied to a devinfo node.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process.h

This header defines the process-contract public ABI. It names default service FMRI values, process contract parameters (`INHERIT`, `NOORPHAN`, `PGRPONLY`, `REGENT`), event masks (`EMPTY`, `FORK`, `EXIT`, `CORE`, `SIGNAL`, `HWERR`), all-event/all-fatal masks, parameter ids, status field names, and event field names for pid, parent pid, core files, signal, sender, sending contract, and exit status.

It forward-declares process template and contract structures and depends on the generic contract header plus time definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process_impl.h

`process_impl.h` defines private process-contract structures. Templates hold common template data, fatal event mask, parameters, service FMRI/creator strings, service contract id, and creator auxiliary data. Process contracts hold common contract data, member count, inherited contract count, parameter/fatal masks, service metadata, and creator auxiliary data.

It declares the system process template, process contract type, and functions for init, process exit/hardware-error notification, contract transfer, accept/adopt behavior, and `PRCTID` lookup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract_impl.h

`contract_impl.h` is the main private kernel contract framework header. It defines 32-bit event/status/param forms, kernel parameter wrappers, template operation vectors, templates, queue selection and flags, acknowledgement outcomes, event queues, members, kernel events, contract vnode tracking, contract operation vectors, contract types, contract flags, time accounting, core contract state, and listener state.

It declares template operations, parameter copyin/copyout, contract lifecycle and adoption/abandon/ack functions, event publication and listener management, lookup/ownership helpers, type-level queries, vnode association helpers, and default invalid/notsupported acknowledgement stubs. It is the internal coordination layer for process and device contracts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/copyops.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/copyops.h

`copyops.h` defines the kernel copy-operation interposition vector. `copyops_t` contains hooks for byte copyin/copyout/string copy operations, typed fetch/store of 8/16/32/64-bit user words, and `physio`.

The comments explain this is used for fault handling, watchpoints, and pxfs-style interposition, generally only after page faults to avoid overhead. Kernel exports install/remove/check copyops on a thread and expose `default_physio`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/copyops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/core.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/core.h

`core.h` preserves old core-file constants and, for non-LP64 non-kernel consumers, the obsolete SunOS 4.x a.out `struct core` layout. That structure records register state, executable header, signal, text/data/stack sizes, command name, FPU state, optional SPARC FPU queue, and exception code.

Kernel builds declare `core(int, int)`. Modern consumers should not depend on the old structure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/core.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/corectl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/corectl.h

`corectl.h` defines the `corectl()` system call subcodes, core dump option bits, and content-selection masks for stack, heap, mapping classes, shared memory, CTF, symbols, and debug info. `core_content_t` is a `u_longlong_t`.

It defines refcounted kernel content/path holders and per-zone core globals. Kernel declarations initialize defaults and manage held content/path values; userland declarations expose convenience functions to set/get global, default, and per-process core paths/content/options.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/corectl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_impl.h

`cpc_impl.h` defines private CPU performance counter control interfaces used by libcpc/kernel CPC. It includes bind flags, request flags and validation macros, CPC capability bits, syscall subcodes, ioctl numbers, event/attribute length limits, attribute/PIC/context structures, and 32-bit syscall argument form.

Kernel content defines context hash sizing, context/PIC flags, DTrace CPC interrupt/mask state enums, tick source macro by architecture, global CPC state, and functions for invalidation, passivation, CPU stop/programming, PCBE loading, DCPC registration, context allocation/free, request assignment/configuration, and config cleanup. Error subcodes enumerate invalid events, attributes, unavailable resources, conflicts, privilege failures, processor binding failure, and hypervisor access denial.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_impl.h -->