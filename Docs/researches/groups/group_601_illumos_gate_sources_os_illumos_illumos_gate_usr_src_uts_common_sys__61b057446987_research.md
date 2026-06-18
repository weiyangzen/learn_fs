# Group Research: illumos sys headers lgrp/link/lofi/log/MAC batch

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`. This grouped report covers exactly the requested files under `usr/src/uts/common/sys`.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp.h

## Role

Kernel-facing locality group (lgroup/NUMA locality) header. For normal userland it exposes only an opaque `lgrp_mem_policy_info_t`; for `_KERNEL`, `_FAKE_KERNEL`, or `_KMEMUSER` it defines the internal lgroup topology, load, statistics, memory-policy, and platform callback interfaces.

## Structure

- Defines `LGRP_NONE`, root/null/default handles, `NLGRPS_MAX` 64, lgroup load scaling constants, and lpl increment/decrement actions.
- Defines per-lgroup counter and snapshot statistic enums, CPU-bucketed stats storage, `LGRP_KSTAT_NAMES`, and stat access/reset macros.
- Defines core kernel types: `klgrpset_t`, `mnodeset_t`, `lgrp_t`, `lpl_t`, memory-policy and search-scope enums, memory-node cookie, shared-memory policy segments, and memory rename arguments.
- Provides bitset macros for lgroup sets, lgroup/memory helper macros, and CPU/resource membership checks.
- Declares global lgroup topology state and generic/platform functions for init, config, kstats, memory placement, thread placement, topology updates, and platform latency/memory hooks.

## Dependencies And Consumers

Kernel builds include CPU, bitmap, vnode, anon, segment, `lgrp_user.h`, and param headers. The header is consumed by scheduler placement, VM memory allocation, shared memory policy, kstats, processor-set/lgroup topology, and platform NUMA support.

## Important Details

The internal lgroup set representation is a 64-bit mask, so `NLGRPS_MAX` and bit shifts are coupled. Counter stats are bucketed by `CPU->cpu_id` to reduce cache contention, and readers must sum buckets. Several macros are statement macros and depend on globals such as `lgrp_alloc_max`, `lgrp_table`, and `PAGESIZE`.

## Research Notes

Read completely: 642 lines, 19968 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp_user.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp_user.h

## Role

Public/user ABI definitions for lgroup discovery, affinity, latency, and memory-size queries. It also defines the kernel-visible snapshot layout used to transfer lgroup hierarchy state to userland.

## Structure

- Defines current lgroup interface version 2 and lgroup syscall subcodes for meminfo, generation, version, snapshot, affinity, latency, and home queries.
- Defines resource identifiers (`CPU`, `MEM`), affinity values, content/view enums, latency query type, memory-size type/flags, and `lgrp_affinity_args_t`.
- Defines `lgrp_info_t` and `lgrp_snapshot_header_t` with pointers to per-lgroup info, CPU arrays, bitsets, parent/child/resource sets, and latency matrix.
- Under `_SYSCALL32`, provides ILP32-compatible `lgrp_info32_t` and `lgrp_snapshot_header32_t`.
- For non-kernel consumers, declares the `lgrp_*` public library/API functions.

## Dependencies And Consumers

Includes `sys/lgrp.h`, procset, processor, pset, integer, and type headers. Userland consumers use it through liblgrp-style calls; kernel syscall handlers and compatibility code use the concrete snapshot and 32-bit layouts.

## Important Details

`LGRP_CONTENT_HIERARCHY` aliases `LGRP_CONTENT_ALL` for compatibility. Snapshot structures contain native pointers in the LP64 layout and explicit `caddr32_t` fields in the ILP32 layout. `lgrp_mem_size_t` is `longlong_t`, while the 32-bit snapshot stores page counts as `uint32_t`.

## Research Notes

Read completely: 295 lines, 8298 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lgrp_user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/libc_kernel.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/libc_kernel.h

## Role

Consolidation-private libc/kernel contract header. It documents interfaces that are not stable for applications and should only be shared between libc and the kernel.

## Structure

The file contains only the C linkage wrapper and `_EVAPORATE` definition. `_EVAPORATE` is an `_exit()` status used by a `vfork()` child in libc `posix_spawn()` paths so the child disappears without normal SIGCHLD-visible exit semantics when no `execve()` has occurred.

## Dependencies And Consumers

No included headers. The relevant consumer is libc process-spawn implementation and kernel exit handling that recognizes the special status.

## Important Details

The comment explicitly warns that these definitions may change even in a patch. Applications should not include or depend on this header.

## Research Notes

Read completely: 53 lines, 1696 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/libc_kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/limits.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/limits.h

## Role

Small illumos system limits header for scatter/gather I/O vector limits.

## Structure

Defines `IOV_MAX` as 1024. Kernel builds also define `IOV_MAX_STACK` as 16, the maximum IOV count intended for on-stack allocation.

## Dependencies And Consumers

No included headers. Consumers are kernel and userland code that need the platform `iovec` count limit; kernel code can use `IOV_MAX_STACK` as an allocation threshold.

## Important Details

This is not the full POSIX `<limits.h>` surface; it is a narrow `sys/limits.h` definition used by illumos components.

## Research Notes

Read completely: 32 lines, 734 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/link.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/link.h

## Role

ELF runtime-linker ABI header. It defines dynamic-section structures/tags, object flags, versioning structures, debugger rendezvous structures, and bootstrapping attributes used by `ld.so.1`, debuggers, link-edit tools, and compatibility code.

## Structure

- Defines `Elf32_Dyn` and, when available, `Elf64_Dyn`.
- Enumerates standard `DT_*` dynamic tags, Sun/OS-specific tags, value/address tag ranges, GNU compatibility tags, version tags, processor-specific tags, and deprecated compatibility values.
- Defines `DF_*`, `DF_P1_*`, `DF_1_*`, and obsolete `DTF_1_*` flag bits.
- Defines 32-bit and 64-bit version definition/need/symbol and syminfo structures plus version indexes and flags.
- Defines `Link_map`, `Link_map32`, `r_debug`, `r_debug32`, runtime-linker states/events/flags, and `R_DEBUG_VERSION`.
- Defines `Elf32_Boot`/`Elf64_Boot` and `EB_*` attributes for dynamic linker bootstrap, then declares `_ld_libc()`.

## Dependencies And Consumers

Non-assembly consumers include `sys/types.h` and `sys/elftypes.h`. Assembly can include the tag/constant portions without structure definitions. Consumers include runtime linker internals, debuggers via `r_debug`, ELF inspection tools, kernel runtime linker code, and compatibility layers.

## Important Details

The comments document dynamic tag encoding rules and exception ranges; tools must special-case OS and processor ranges instead of assuming even/odd pointer/value rules everywhere. Several constants remain for old binary compatibility even when illumos no longer uses them actively.

## Research Notes

Read completely: 641 lines, 23406 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/link.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/linker_set.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/linker_set.h

## Role

FreeBSD-derived linker-set helper macros for collecting pointers into named ELF sections and iterating them through weak start/stop symbols.

## Structure

Defines concatenation/stringification helpers, weak/global assembly symbol helpers, `__MAKE_SET()`, public set-entry macros (`TEXT_SET`, `DATA_SET`, `BSS_SET`, `ABS_SET`, `SET_ENTRY`), declaration and begin/limit macros, iteration, indexing, and count helpers.

## Dependencies And Consumers

Includes `sys/ccompile.h` for compiler attributes such as `__section`, `__used`, and `__weak_symbol`. Consumers register pointers into `set_<name>` sections and later walk `__start_set_<name>` to `__stop_set_<name>`.

## Important Details

Set entries are addresses of symbols, so iterator variables are pointer-to-pointer style. Start and stop symbols are weak so an empty set can link, but consumers must still account for platform/linker behavior.

## Research Notes

Read completely: 99 lines, 3535 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/linker_set.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list.h

## Role

Public intrusive doubly-linked list API for illumos kernel/user common code.

## Structure

Includes `list_impl.h`, typedefs opaque `list_node_t` and `list_t`, and declares create/destroy, insert/remove, move, head/tail, next/prev, empty test, link initialization/replacement, and active-link test functions.

## Dependencies And Consumers

The implementation layout comes from `list_impl.h`. Consumers embed `list_node_t` in their own objects and initialize a `list_t` with object size and node offset.

## Important Details

This is an intrusive list API: objects own their link node, and the list knows only the node offset. The header declares functions only; locking, if needed, is the caller's responsibility.

## Research Notes

Read completely: 65 lines, 1843 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list_impl.h

## Role

Concrete layout backing `sys/list.h`.

## Structure

Defines `struct list_node` with next/previous pointers and `struct list` with element size, node offset, and sentinel head node.

## Dependencies And Consumers

Includes `sys/types.h` for `size_t`. Direct consumers are the list implementation and code that needs the concrete list layout, usually through `sys/list.h`.

## Important Details

The sentinel node is embedded in `struct list`, so an empty list does not require allocation. ABI/layout consumers rely on `list_size` and `list_offset` matching `list_create()` expectations.

## Research Notes

Read completely: 51 lines, 1293 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/llc1.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/llc1.h

## Role

Internal LLC Class 1 STREAMS mux header compatible with SunConnect LLC2/DLPI expectations.

## Structure

Defines LLC statistics and stat indexes, multicast table entries, per-lower-MAC state (`llc_mac_info_t`), per-stream state (`llc1_t`), per-device state (`llc1dev_t`), link/stream/debug flags, module watermarks, LLC/SNAP address and header structures, protocol constants, special LLC ioctls, and a local `qelem` queue structure.

## Dependencies And Consumers

The header assumes surrounding kernel networking/STREAMS types such as `queue_t`, `mblk_t`, `kmutex_t`, `krwlock_t`, `kstat_t`, and `ETHERADDRL` are available from including implementation files.

## Important Details

The structures embed STREAMS queues and mblk pointers directly, so they are driver-private implementation state rather than stable user ABI. The ioctl values (`L_GETPPA`, `L_SETPPA`, `L_GETSTATS`, `L_ZEROSTATS`) are retained for LLC2 conformance behavior.

## Research Notes

Read completely: 278 lines, 8102 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/llc1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/loadavg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/loadavg.h

## Role

Load-average constants, kernel accumulator layout, and kernel/user `getloadavg()` declarations.

## Structure

Defines indexes for 1, 5, and 15 minute load averages, number of stats, sample-table sizes, and `struct loadavg_s` containing current index, recorded length, temporary total, and an `hrtime_t` ring/table of load samples.

## Dependencies And Consumers

The file assumes `hrtime_t` is already available to consumers. Kernel builds declare `getloadavg(int *, int)`; user builds declare `getloadavg(double [], int)`.

## Important Details

The kernel and user prototypes intentionally differ in result type. Code including this header must be compiled with the correct `_KERNEL` context.

## Research Notes

Read completely: 68 lines, 1686 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/loadavg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lock.h

## Role

Legacy process/text/data locking interface constants and prototypes.

## Structure

Defines `UNLOCK`, `PROCLOCK`, `TXTLOCK`, and `DATLOCK`. Kernel builds add `MEMLOCK` and declare `punlock()`. User builds declare `plock(int)`.

## Dependencies And Consumers

No included headers. Userland consumers are legacy `plock(3C)` callers; kernel consumers use internal process/memory unlock support.

## Important Details

`MEMLOCK` is kernel-only. The public ABI surface is intentionally small and inherited from older UNIX behavior.

## Research Notes

Read completely: 60 lines, 1345 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockfs.h

## Role

Filesystem lock ioctl data structures and constants, historically used by UFS-style lockfs operations.

## Structure

Defines native `struct lockfs`, `_SYSCALL32` `struct lockfs32`, lock types from unlock through write/name/delete/hard/error/read-only-error lock, flags for busy and modified state, max comment length, and convenience macros to test/set/clear flags and lock type.

## Dependencies And Consumers

Relies on base illumos integer/pointer typedefs from including context. Kernel ioctl translation code uses `lockfs32` when supporting 32-bit applications in an LP64 kernel.

## Important Details

`LOCKFS_ROELOCK` is documented as unimplemented but still assigned a value and included in `LOCKFS_MAXLOCK`. The macros evaluate their `LF` argument multiple times only through pointer dereference expressions, so callers should pass stable pointers.

## Research Notes

Read completely: 101 lines, 3081 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockstat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockstat.h

## Role

DTrace lockstat probe ID/name definitions and kernel macros for recording lock acquisition, release, spin, block, upgrade, and downgrade events.

## Structure

Defines 25 probe IDs, string names for lock operations/events/types, composed provider names, and under non-assembly kernel builds declares `lockstat_probemap`, `lockstat_probe`, and support functions. Provides `LOCKSTAT_RECORD*`, `LOCKSTAT_START_TIME`, and `LOCKSTAT_RECORD_TIME` macros.

## Dependencies And Consumers

Includes `sys/dtrace.h`, and in C builds includes types, inttypes, systm, and atomic headers. Consumers are synchronization primitives and lockstat/DTrace support code.

## Important Details

The record macros guard on `lockstat_probemap[probe]`, increment `curthread->t_lockstat`, use `membar_enter()`, re-read the probe ID, then call the DTrace probe. On ILP32, elapsed spin time is clamped to `UINT_MAX`.

## Research Notes

Read completely: 192 lines, 5707 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi.h

## Role

Loopback file block-device (`lofi`) ioctl ABI and kernel state header, including support for compressed and encrypted lofi images.

## Structure

- Defines device/node names for `/dev/lofictl`, block lofi devices, and raw lofi devices.
- Defines compression constants, partition/minor conversion macros, and private lofiadm ioctl usage.
- Defines `iv_method_t`, `struct lofi_ioctl`, ioctl command numbers, and file/vnode type eligibility macros.
- Defines crypto metadata offset/magic/version and, under `_KERNEL`, compressed segment cache entries, compression buffers, crypto metadata, and the large `struct lofi_state`.
- Defines compression function signature, compression info table structure, and known compression algorithm indexes.

## Dependencies And Consumers

Includes time, taskq, dkio, vnode, list, crypto API, and zone headers; kernel builds include cmlb and open headers. Userland `lofiadm(8)` uses the private ioctl structure; the lofi driver uses the kernel-only state.

## Important Details

The comments call the ioctls private and for `lofiadm(8)`. Forced unmap can close the backing vnode while busy and cause later operations to see `DKIO_DEV_GONE`; cleanup unmap defers teardown until last close. `struct lofi_ioctl` embeds fixed-size path, algorithm, cipher, and key buffers, so ABI size matters.

## Research Notes

Read completely: 342 lines, 10807 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi_impl.h

## Role

Small private lofi implementation header for nvlist-backed custom data/cache state.

## Structure

Includes `sys/nvpair.h`, defines `lofi_nvl_t` with mutex, condition variable, and `nvlist_t *`, and declares global `lofi_devlink_cache`.

## Dependencies And Consumers

Consumed by lofi implementation files that maintain device-link/custom data in an nvlist. It relies on kernel synchronization types being visible in the build context.

## Important Details

The structure is explicitly private implementation detail. Synchronization ownership is in the driver; the header only provides storage layout.

## Research Notes

Read completely: 41 lines, 884 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/log.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/log.h

## Role

Kernel log device/STREAMS internal header for `/dev/conslog` and `/dev/log` clone handling.

## Structure

Defines minor numbers, clone index range, module ID, packet sizes, queue watermarks, dump-message magic, recent/free cache sizes, `log_t`, `log_filter_t`, per-zone clone array `log_zone_t`, and dump-message header `log_dump_t`. Kernel builds declare global queues, filters, and log management functions.

## Dependencies And Consumers

Includes `sys/types.h`, `sys/strlog.h`, and `sys/stream.h`. Consumers are kernel log driver and console/log message paths.

## Important Details

`log_t` is zone-aware via `zoneid_t`, and `log_zone_t` tracks active clone types. `log_dump_t` stores checksums for queued unsent messages and is tied to `dump_messages()` layout.

## Research Notes

Read completely: 123 lines, 3932 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux.h

## Role

Public ioctl/data header for logindmux, the STREAMS module that exchanges queue pairs between a pty master stream and a network stream.

## Structure

Defines `struct protocol_arg`, `_SYSCALL32` `protocol_arg32`, telnet magic cookie `M_CTL_MAGIC_NUMBER`, `TELIOC` base if not already defined, and `LOGDMX_IOC_QEXCHANGE`.

## Dependencies And Consumers

Uses device typedefs from including context. User/kernel ioctl paths use the protocol argument structures; STREAMS logindmux implementation uses the ioctl constant.

## Important Details

The ioctl base comment carries an old "fixme" note. The 32-bit structure preserves device and flag width for LP64 kernel compatibility.

## Research Notes

Read completely: 64 lines, 1528 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux_impl.h

## Role

Private implementation header for logindmux peer unlink coordination and per-instance STREAMS state.

## Structure

Includes types and STREAMS headers, defines `unlinkinfo_t` shared between peers, `struct tmx` per open instance, module ID, timer wait constants, peer linkage states, protocol message values, and `LOGDMUX_PROTO_MBLK()` to identify unlink protocol messages.

## Dependencies And Consumers

Depends on STREAMS `queue_t`, `mblk_t`, `struct iocblk`, `DB_TYPE`, `M_CTL`, `M_IOCTL`, `I_UNLINK`, mutexes, bufcall IDs, and timeout IDs. Consumed by logindmux module implementation.

## Important Details

`unlinkinfo_t` serializes I_UNLINK handling so only one peer actively processes unlink at a time. `LOGDMUX_PROTO_MBLK()` assumes the message has a continuation block and checks for an embedded `I_UNLINK` ioctl.

## Research Notes

Read completely: 109 lines, 3258 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lom_io.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lom_io.h

## Role

LOMlite/TSalarm/BSCV user-kernel ioctl ABI header for platform alarm, watchdog, event log, LED, voltage, temperature, serial, and field-programming controls.

## Structure

- Defines TSalarm monitor/control ioctls and small alarm/watchdog/debug structures.
- Defines LOMlite legacy aliases and newer monitor/control ioctls for PSU, event log, fan, fault LED, info, control, programming, daemon/debug monitor, GPIO inputs, manufacturing programming, and LED state.
- Defines fixed-size data structures for alarm, watchdog, PSU, fan, event log, LED state, info, control, manufacturing/programming buffers, and LOMlite2 extensions.
- Defines event-code constants and encoding macros for fault LED, alarm, fan, and PSU events.
- Defines LOMlite2 ioctls/structures for serial event control, voltages, status flags, temperatures, console buffer, extended event log, extended info, test commands, manufacturing read/write, sleep, and lomp field-programming controls.

## Dependencies And Consumers

Includes `sys/ioccom.h` for ioctl encoding macros. Consumers are LOM/BSCV platform drivers and management utilities that pass the fixed-size structures across ioctl boundaries.

## Important Details

Many structs use fixed array limits (`MAX_PSUS`, `MAX_FANS`, `MAX_EVENTS`, `MAX_EVENT_STR`, etc.) that are part of the ABI. Event encoding macros do not validate alarm/fan/PSU numbers beyond masking low status bits, so callers/drivers must validate ranges.

## Research Notes

Read completely: 633 lines, 14574 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lom_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lombus.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lombus.h

## Role

LOMbus child-driver interface definitions for register spaces, register specs, internally generated error codes, and timing constants.

## Structure

Defines `lombus_regspec_t` triples, register space IDs for virtual registers, watchdog pat, and async event info, register ranges and special negative fault/probe/async registers, `enum lombus_errs`, and nanosecond timeout/pat constants.

## Dependencies And Consumers

No includes beyond C wrapper. Consumed by LOMbus parent/child drivers to interpret regspecs and fault conditions.

## Important Details

Error codes start at `0x100` to avoid LOM-generated `0x00-0x7f` and SunVTS `0x80-0xff` ranges. Time constants are `long long` nanoseconds.

## Research Notes

Read completely: 125 lines, 3275 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lombus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lpif.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lpif.h

## Role

SCSI Target Mode Framework (STMF) logical-unit provider interface header.

## Structure

Includes STMF definitions, defines LPIF revisions, `stmf_lu_t` with provider/private fields and LU callback vector, abort commands, LU active/standby states, proxy message types and read/write flags, ITL removal reasons, `stmf_lu_provider_t`, and STMF LU/provider registration and helper function prototypes.

## Dependencies And Consumers

Depends on `sys/stmf_defines.h` and `sys/stmf.h`, including SCSI task/data buffer types. Consumers are logical unit provider drivers and STMF core.

## Important Details

The LU callback table is the core contract: allocation, new task, dbuf transfer completion, status completion, task free, abort, poll, control, info, event handling, dbuf free, and task done. `lp_lpif_rev` is currently expected to be `LPIF_REV_2`.

## Research Notes

Read completely: 146 lines, 4506 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lpif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp.h

## Role

Lightweight process public definitions for `_lwp_*` interfaces, LWP creation flags, and LWP accounting info.

## Structure

Includes synchronization and ucontext headers, defines LWP creation flags, `struct lwpinfo`, `_SYSCALL32` `struct lwpinfo32`, `lwpid_t`, private FS/GS base selector constants, private get/set constants, and userland `_lwp_*` prototypes.

## Dependencies And Consumers

Userland consumes the `_lwp_*` declarations. Kernel compatibility code uses `lwpinfo32`. The header relies on `timestruc_t`, `timestruc32_t`, and integer typedefs.

## Important Details

`struct lwpinfo` reserves `lwpinfo_pad[64]`, giving the ABI room for expansion. The `_lwp_*` function prototypes are hidden from `_KERNEL` builds.

## Research Notes

Read completely: 90 lines, 1979 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_timer_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_timer_impl.h

## Role

Private kernel implementation state for LWP timed waits/sleeps.

## Structure

Includes thread, lwp, time, and systm headers; defines `lwp_timer_t` with target thread, user timespec pointer, requested time, timecheck flags, immediate-timeout flag, error field, and callout ID. Kernel builds declare copyin/enqueue/dequeue/copyout helpers.

## Dependencies And Consumers

Consumed by kernel LWP timer code. Depends on `kthread_t`, `timespec_t`, `callout_id_t`, and `clock_t`.

## Important Details

The state bridges user timespec copyin/copyout with kernel callout scheduling. `lwpt_id` tracks the scheduled callout for dequeue/cancel paths.

## Research Notes

Read completely: 61 lines, 1647 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_timer_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_upimutex_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_upimutex_impl.h

## Role

Private implementation header for user-priority-inheritance mutex tracking.

## Structure

Includes thread and LWP headers, forward declares `upimutex_t` and `upib_t`, defines hash bucket `upib` and tracked mutex `upimutex`, hash sizing/macros based on `lwpchan_t`, try/block constants, and kernel cleanup prototype.

## Dependencies And Consumers

Consumed by kernel synchronization code implementing user PI mutex behavior. Depends on `kmutex_t`, `_kthread`, `lwp_mutex_t`, `lwpchan_t`, and the global `upimutextab` expected by `UPI_CHAIN()`.

## Important Details

`UPILWPCHAN_HASH()` hashes both lwpchan words and masks into a 512-bucket table. The macros assume side-effect-free `lwpchan` expressions because fields are referenced multiple times.

## Research Notes

Read completely: 75 lines, 2235 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_upimutex_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwpchan_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwpchan_impl.h

## Role

Private process cache for translating process-shared LWP synchronization object virtual addresses into logical `lwpchan_t` addresses.

## Structure

Defines CV/MP pool IDs, initial and maximum hash bits, `lwpchan_entry_t`, hash bucket structure, process-level `lwpchan_data_t`, and exported cache maintenance functions `lwpchan_delete_mapping()` and `lwpchan_destroy_cache()`.

## Dependencies And Consumers

The header is consumed by kernel LWP synchronization and VM mapping teardown/exec/exit paths. It relies on `proc_t`, `caddr_t`, `lwpchan_t`, `kmutex_t`, and integer typedefs from including context.

## Important Details

The cache avoids repeated `as_getmemid()` calls for shared sync objects. Resizing requires acquiring all bucket locks; a comment notes `p->p_lcp` cannot change while any bucket lock is held.

## Research Notes

Read completely: 94 lines, 3279 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwpchan_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac.h

## Role

Core MAC Services public/kernel header. It defines common datalink types, properties, statistics, plugin interfaces, resource callbacks, MAC type registration, hardware emulation flags, and core MAC provider/client-facing kernel functions.

## Structure

- Defines MAC module info/version, opaque handles, datalink ID constants, link state/duplex/flow-control/FEC/tag-mode enums, property range types, address limits, secondary address container, log types, and public property IDs.
- Kernel section defines MAC and MAC-type statistic ranges, common statistics, immutable `mac_info_t`, VNIC/aggr capabilities, bridge callbacks, notification types, RX/resource callback types, interrupt/resource structures, address/header info, direct RX callback, resource callbacks, and MAC-type plugin ops.
- Defines ndd mapping and stat info structures, `mactype_register_t`, packet hardware-emulation flags, driver interface functions, mactype register/unregister functions, log usage, VNIC helpers, packet hash flags, bridge linkage, and TRILL snoop hook.

## Dependencies And Consumers

Includes `sys/types.h`; kernel builds include DDI definitions. Consumers are GLDv3 MAC providers, MAC-type plugins, datalink/VNIC/aggr/bridge code, and networking subsystems.

## Important Details

Property and statistic enums warn to append only and not reorder, preserving ABI/semantic numbering. Optional MAC-type callbacks are negotiated through `mtops_ops` bits to preserve plugin compatibility.

## Research Notes

Read completely: 758 lines, 21739 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_6to4.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_6to4.h

## Role

Identifier header for the 6to4 tunneling MAC plugin.

## Structure

Includes `sys/mac_ipv4.h` and defines `MAC_PLUGIN_IDENT_6TO4` as `"mac_6to4"`.

## Dependencies And Consumers

Consumers are MAC plugin registration code and tunnel code that need the plugin identity. It shares IPv4 plugin helpers through the included IPv4 header.

## Important Details

No kernel guard is used around the identifier, so the plugin name is visible to all C consumers.

## Research Notes

Read completely: 45 lines, 1180 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_6to4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client.h

## Role

Kernel MAC client API header for consumers that open MAC handles, add addresses, receive/transmit packets, manage promiscuous callbacks, notifications, resources, and hardware emulation.

## Structure

Defines opaque client/unicast/promisc/perimeter handles, Tx notify cookie/callback, diagnostic enum, ring request constants, promiscuous types, unicast/open/close/promisc/Tx flags, and a broad set of `mac_client_*`, unicast, multicast, rx, tx, notify, stat, primary address, factory address, resource, bridge, share, MTU, ring, and hardware-emulation prototypes.

## Dependencies And Consumers

Includes `sys/mac.h` and `sys/mac_flow.h`; all substantive declarations are under `_KERNEL`. Consumers include IP, DLS, VNIC, aggregation, bridging, and other kernel clients of MAC Services.

## Important Details

Ring constants distinguish "none" from "don't care". Unicast flags control duplicate checks, primary/VNIC roles, hardware classification, VLAN tag/strip behavior, and TX VID checks. `mac_tx()` returns a cookie that can later be tested for flow blockage.

## Research Notes

Read completely: 212 lines, 7361 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_impl.h

## Role

Private implementation layout for MAC clients, unicast entries, promiscuous callbacks, per-CPU Tx references, VLAN validation/cache, protection state, and internal client helper APIs.

## Structure

- Declares kmem caches and defines `mac_unicast_impl_t`, `mac_promisc_impl_t`, `mac_tx_percpu_t`, client role flags, and client implementation state flags.
- Defines `mac_client_impl_t` with client identity, associated MACs, flow entries, RX callbacks, promiscuous/unicast lists, resource callbacks, Tx notify callbacks, stats, subflows, priorities, HIO share, multicast, protection AVL trees, Tx quiesce state, and variable-size per-CPU Tx refs.
- Provides size/accessor macros, resource property accessors, VID validation/tagging helpers, single-entry VID cache encoding macros, protection flags, and internal function prototypes.

## Dependencies And Consumers

Includes modhash, public/private MAC provider headers, MAC implementation, MAC stats, network interface, and MAC flow implementation headers. Consumers are MAC client internals, not general MAC clients.

## Important Details

The comments annotate locking discipline (`WO`, `SL`, specific locks, RX quiescence). The variable-length `mci_tx_pcpu[1]` must remain last and is sized by `MAC_CLIENT_IMPL_SIZE`. `MAC_VID_CHECK()` is a statement macro that inspects Ethernet/VLAN headers directly.

## Research Notes

Read completely: 436 lines, 13945 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_priv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_priv.h

## Role

Private MAC client API for GLDv3 stack components only: dld, dls, aggr, and softmac.

## Structure

Under `_KERNEL`, declares APIs for RX bypass, MAC info, start/stop/ioctl/link, resources, devinfo/driver access, capability/SAP/header operations, perimeter entry/exit, VNIC VLAN handling, polling, flow management, quiesce/restart, hardware ring/group operations, hardware VLAN/promisc, upper MAC setup, exclusivity, ring availability, interrupt CPU assignment, property get/set/info, and pseudo-ring stats.

## Dependencies And Consumers

Includes `sys/mac.h` and `sys/mac_flow.h`. Intended consumers are private GLDv3 implementation modules, not arbitrary drivers.

## Important Details

`MAC_PERIM_HELD()` checks perimeter ownership only in DEBUG builds. Several APIs expose low-level hardware ring passthrough and classifier manipulation, so misuse outside the MAC stack could violate synchronization/resource assumptions.

## Research Notes

Read completely: 208 lines, 8124 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ether.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ether.h

## Role

Ethernet MAC plugin header, defining Ethernet media values and kernel Ethernet-specific statistics.

## Structure

Defines `mac_ether_media_t`, covering unknown/none, 10/100/1G modes, 2.5G/5G, 10G, 25G, 40G, 50G, 100G, 200G, and 400G variants. Kernel builds define `MAC_PLUGIN_IDENT_ETHER`, Ethernet stat IDs appended from `MACTYPE_STAT_MIN`, `ETHER_NSTAT`, and `ETHER_STAT_ISACOUNTER()`.

## Dependencies And Consumers

User/kernel code can use media enum values for `MAC_PROP_MEDIA` and `ETHER_STAT_XCVR_INUSE`. Kernel MAC Ethernet plugin and drivers use the stat IDs.

## Important Details

The stat enum explicitly says not to reorder and to append only. Media enum values are public property values, so additions are compatible only when appended and interpreted by matching tooling.

## Research Notes

Read completely: 370 lines, 8882 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ether.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow.h

## Role

Public flow descriptor and resource-control types for MAC packet classification, bandwidth/CPU/ring assignment, priority, and protection settings.

## Structure

Defines flow selector mask bits, `flow_desc_t`, maximum rings and flow name lengths, CPU/fanout/resource structures, transmit interrupt CPU state, priority levels, protection flags and data structures, resource property mask bits/defaults/minimums, `mac_resource_props_t`, field alias macros, and `MAC_COPY_CPUS()`.

## Dependencies And Consumers

Includes types, param, IP protocol definitions, and Ethernet definitions. Used by MAC client APIs, flow management, dladm/dld plumbing, and internal classifier/resource code.

## Important Details

`flow_desc_t` is packed to 4-byte alignment on mixed 64/32-bit long-long alignment platforms, preserving ABI layout. `MRP_MAXBW_RESETVAL` disables bandwidth control, and `MRP_MAXBW_MINVAL` rejects sub-megabit limits below current implementation capability.

## Research Notes

Read completely: 266 lines, 7835 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow_impl.h

## Role

Private MAC flow implementation header for flow reference handling, quiescence, bandwidth control, flow entries, packet parse state, flow-table operations, and statistics helpers.

## Structure

Defines flow refhold/release/user-ref macros, flow mark/unmark macros, bandwidth/priority helpers, flow table size, flow lookup flags, callback/match signatures, flow states, entry flags/types, bandwidth control state and `mac_bw_ctl_t`, `flow_entry_t`, layer parse info, `flow_state_t`, `flow_ops_t`, `flow_tab_t`, flow table info, stats update macros, and flow lifecycle/table/bandwidth helper prototypes.

## Dependencies And Consumers

Includes param, atomic, time, synchronization, public flow, STREAMS, SDT, and net interface headers. Consumed by MAC flow/classifier, soft-ring, client, bandwidth, and datalink internals.

## Important Details

`FLOW_TRY_REFHOLD()` rejects incipient, quiesced, condemned, and no-datapath flows before data-path use. `FLOW_REFRELE()` may call `mac_flow_destroy()` while holding/releasing through the macro path, so callers must understand ownership. Bandwidth control is shared across related SRS queues and combines drop-threshold policing with bytes-per-tick shaping.

## Research Notes

Read completely: 597 lines, 17487 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ib.h

## Role

InfiniBand/IPoIB MAC plugin header for kernel-only plugin identity, limits, and soft header metadata.

## Structure

Under `_KERNEL`, defines `MAC_PLUGIN_IDENT_IB`, SAP/ethertype/GID constants, `ib_addrs_t`, `ib_header_info_t`, and accessor aliases for destination/source/GRH fields.

## Dependencies And Consumers

Consumers are IPoIB/MAC plugin implementation files that already provide `ipoib_mac_t`, `ipoib_pgrh_t`, and `ipoib_hdr_t` definitions.

## Important Details

The comment explains the "soft" header: IB does not provide a normal link-layer header path compatible with GLDv3, so this structure carries destination/source metadata needed by the MAC layer.

## Research Notes

Read completely: 76 lines, 2064 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_impl.h

## Role

Primary private MAC Services implementation header. It defines core MAC provider state, callback list infrastructure, rings/groups, addresses, registered MAC instance layout, resource accounting, property-info state, and many internal MAC routines.

## Structure

- Defines MAC private/minor ranges, margin/MTU request nodes, generic chains, callback list structures/macros, mactype registration state, group/ring state enums, `mac_ring_t`, ring ref macros, group-client and `mac_group_t`.
- Defines factory/multicast/address/VLAN structures, global MAC instance registry variables, and the large `mac_impl_t` with locks, identity, driver callbacks, link state, perimeter, notify callbacks, ring groups/capabilities, transceiver/LED state, address lists, flow table, clients, SDU/margin/MTU, factory addresses, promiscuous callbacks, resources, minor/open refs, legacy/share/bridge state, and DEBUG perimeter stack.
- Defines default group macros, ring/group resource accounting macros, MAC state flags, callback aliases, perimeter handle encode/decode, property info flags/state, protection helper, and extensive internal function prototypes for MAC core, callbacks, broadcast/multicast, rings/groups, flows, datapath, VLAN tags, Tx/Rx, shares, perimeter, notifications, protection, resources, bridging, transceivers, LEDs, direct RX, and broadcast groups.

## Dependencies And Consumers

Includes cpupart, modhash, MAC client/provider, note, AVL, network interface, MAC flow implementation, IPv6, and packet attribute headers. Consumed only by MAC Services implementation and closely related GLDv3 internals.

## Important Details

The header documents field protection discipline: write-once, serializer-protected, and lock-protected members. `MAC_DEFAULT_TX_GROUP(mip)` points one past `mi_tx_groups + mi_tx_group_count`, which reflects the local convention for default Tx group placement and must match allocation logic. The perimeter handle encodes a low-bit `need_close` flag into an aligned pointer.

## Research Notes

Read completely: 948 lines, 31646 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4.h

## Role

Identifier header for the IPv4 tunneling MAC plugin.

## Structure

Defines `MAC_PLUGIN_IDENT_IPV4` as `"mac_ipv4"` inside the standard guard and C linkage wrapper.

## Dependencies And Consumers

No includes. Consumed by IPv4 tunnel MAC plugin registration and code that refers to the plugin identity.

## Important Details

The header intentionally contains only the plugin identifier; operational helper prototypes live in `mac_ipv4_impl.h`.

## Research Notes

Read completely: 43 lines, 1153 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4_impl.h

## Role

Shared implementation declarations for IPv4-style tunnel MAC plugins, used by `mac_ipv4`, `mac_6to4`, and `mac_ipv6`.

## Structure

Includes `sys/mac.h` and declares address verification, SAP verification, header construction, header parsing, and plugin-data validation functions: `mac_ipv4_unicst_verify()`, `mac_ipv4_multicst_verify()`, `mac_ipv4_sap_verify()`, `mac_ipv4_header()`, `mac_ipv4_header_info()`, and `mac_ipv4_pdata_verify()`.

## Dependencies And Consumers

Consumed by tunnel MAC plugin implementation files. Depends on MAC header types such as `mac_header_info_t`, `mblk_t`, and `boolean_t`.

## Important Details

Despite the file name, comments state the helpers are shared by 6to4 and IPv6 tunnel plugins as well as the IPv4 plugin.

## Research Notes

Read completely: 55 lines, 1632 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv6.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv6.h

## Role

Identifier header for the IPv6 tunneling MAC plugin.

## Structure

Defines `MAC_PLUGIN_IDENT_IPV6` as `"mac_ipv6"` inside the standard guard and C linkage wrapper.

## Dependencies And Consumers

No includes. Consumed by IPv6 tunnel MAC plugin registration and code that refers to the plugin identity.

## Important Details

The header is deliberately minimal and pairs with shared implementation declarations from `mac_ipv4_impl.h`.

## Research Notes

Read completely: 43 lines, 1153 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv6.h -->