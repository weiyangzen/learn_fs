# Group Research: illumos-gate usr/src/uts/common/sys STREAMS, DDI, NDI, LDI, MDI, swap, synchronization, and syscall headers

This grouped report covers only files listed for subset A in `Docs/research_subset_a.md`. Every source file listed in the work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stream.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stream.h

`stream.h` is the central public/kernel STREAMS interface header. It defines the primary STREAMS queue, message, data-block, module, and ioctl message structures, plus the exported kernel routines used by STREAMS modules and drivers.

The file starts with `queue_t`, whose comments are as important as the fields: the header documents lock ownership classes for each queue member (`Q9S`, `QLK`, `STR`, `SQLK`, `NOLK`, `SVLK`). Publicly documented fields include the processing pointers, queue links, module private pointer, counters, flags, water marks, and packet size bounds. Private fields add band state, per-queue locks/CVs, stream backpointers, syncq scheduling state, drain state, synchronous-UIO support, service priority, syncq message lists, and the module implementation pointer. Queue flags describe flow control, scheduling, reader/write-side identity, syncq model (`QPAIR`, `QPERQ`, `QPERMOD`, `QMTSAFE`, `QMTOUTPERIM`), driver association, module insertion/removal, and single-instance/private direct-transport behavior.

The header defines priority-band state (`qband_t`), `qfields_t` selectors for `strqset()`/`strqget()`, module metadata (`module_info`), queue entry-point function pointer types, `qinit`, and `streamtab`. These provide the ABI by which STREAMS modules and drivers publish read/write queue procedures, open/close routines, service routines, module statistics, and optional synchronous I/O hooks.

Message storage is modeled by `dblk_t` and `mblk_t`. `dblk_t` carries the shared data buffer, reference count, message type, allocator/free routines, checksum offload fields, optional flow-trace header, and credential pointer. `mblk_t` carries queue-chain links, continuation link, read/write pointers, band/tag/flags, and a queue pointer for sync queues. Accessor macros expose selected private dblk fields (`DB_CPID`, `DB_CRED`, `DB_FTHDR`, `DB_TCI`) while `strsun.h` exposes the DDI utility accessors.

The file enumerates STREAMS message types: normal data/protocol (`M_DATA`, `M_PROTO`, `M_PCPROTO`, etc.), ordinary controls (`M_IOCTL`, `M_CTL`, `M_SETOPTS`, etc.), and high-priority controls (`M_IOCACK`, `M_IOCNAK`, `M_FLUSH`, `M_ERROR`, `M_COPYIN`, `M_COPYOUT`, `M_IOCDATA`, `M_CMD`, and others). It also defines message flags (`MSGMARK`, `MSGDELIM`, `MSGWAITSYNC`) and queue class helpers (`QNORM`, `QPCTL`, `datamsg()`, `queclass()`).

STREAMS ioctl protocol structures are defined with explicit LP64/ILP32 layout differences: `iocblk`, `copyreq`, `copyresp`, and `union ioctypes`. The datamodel flags (`IOC_ILP32`, `IOC_LP64`, `IOC_NATIVE`) and `IOC_CONVERT_FROM()` are the conversion hooks for transparent and mixed-model ioctls. `stroptions` carries stream-head option changes sent via `M_SETOPTS`, including read modes, write offsets, watermarks, error policy, copy policy, maximum block size, and tailroom.

Kernel-only declarations provide the message allocator/copy/dup/free API (`allocb`, `esballoc`, `desballoc`, `bcache_allocb`, `freeb`, `freemsg`, `dupb`, `copymsg`, etc.), queue manipulation and flow-control API (`getq`, `putq`, `putbq`, `insq`, `rmvq`, `flushq`, `canput`, `putnext`, `qenable`, etc.), stream freezing/waiting (`freezestr`, `unfreezestr`, `qwait`, `qwriter`), queue-scoped callback wrappers (`qtimeout`, `qbufcall`, `quntimeout`, `qunbufcall`), synchronous UIO helpers, and global `nstrpush`.

Key relationships: `strsubr.h` provides the private stream-head and syncq structures that back the public `queue_t` fields; `stropts.h` defines user-visible stream ioctl constants used by the message protocol here; `strft.h` attaches optional flow-trace state to `dblk_t`; `strsun.h` exposes DDI utility macros over `mblk_t`/`dblk_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strft.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strft.h

`strft.h` defines the private STREAMS flow-trace subsystem used to record how messages move through a stream. It includes `stream.h` and attaches its trace header through `dblk_t` via `DB_FTHDR()`.

The event namespace uses `FTEV_MASK` for event IDs and reserved high bits for write-side/read-side markers, context-switch markers, and processor markers (`FTEV_ISWR`, `FTEV_CS`, `FTEV_PS`). Defined event groups cover message allocation/free/copy/dup events and queue operations such as put, putq, getq, rmvq, insq, flushq, putnext, and rwnext.

Trace storage is a linked list of fixed-size event blocks. `ftevnt_t` records timestamp, module/driver name, next module/driver name, event, event data, and optional stack pointer. `ftstk_t` stores up to `FTSTK_DEPTH` program counters. `ftblk_t` stores `FTBLK_EVNTS` events plus the next index. `fthdr_t` is attached to a data block and holds the tail block, accumulated hash, last thread/CPU, and the first event block.

Kernel-only declarations expose `str_ftevent()`, `str_ftfree()`, and flow-trace switches `str_ftnever` and `str_ftstack`. `STR_FTALLOC()` lazily allocates a trace header from `fthdr_cache`, initializes the first block and ownership metadata, and records an allocation event. `STR_FTEVENT_MSG()` walks an `mblk_t` continuation chain and records an event on each traced block. `STR_FTEVENT_MBLK()` records an event on a single block.

The subsystem is explicitly private and performance-sensitive: all macros check `str_ftnever` before doing work, allocation is non-sleeping, and stack capture is optional.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strft.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strlog.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strlog.h

`strlog.h` defines the STREAMS log driver control interface. Its main data structure, `log_ctl_t`, is the control portion of a log message and carries module ID, sub-ID, trace level, disposition flags, boot/epoch time fields, sequence number, and syslog-style priority. The time field layout is explicitly adjusted for LP64 compatibility using 32-bit clock/time types.

Public log flags (`SL_FATAL`, `SL_NOTIFY`, `SL_ERROR`, `SL_TRACE`, `SL_CONSOLE`, `SL_WARN`, `SL_NOTE`) specify where and how log messages are delivered. Private implementation flags add console-only, log-only, user-terminal, and panic-message routing.

`trace_ids_t` identifies module/sub-ID/level filters used by `I_TRCLOG`. Log-driver I_STR ioctl command numbers are based under `LOGCTL` and define tracer, error logger, and console logger roles (`I_TRCLOG`, `I_ERRLOG`, `I_CONSLOG`).

`STRLOG_MAKE_MSGID()` hashes a printable format string into a six-digit message ID range. Kernel builds declare `strlog()` and `vstrlog()` with printf format checking. The `STRLOG` macro compiles to `strlog` in debug/lint builds and to a short-circuited expression otherwise, making debug trace logging disappear in non-debug builds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strlog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strmdep.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strmdep.h

`strmdep.h` is the STREAMS machine-dependent shim. In this illumos version it is small: `strbcpy()` maps to `bcopy()`, `saveaddr()` is an empty macro retained for historical allocator tracking hooks, and `str_aligned()` checks whether a pointer is aligned to `sizeof (long)`.

The file exists so STREAMS code can refer to machine-dependent operations through stable macros even when the current platform implementation does not need special handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strmdep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stropts.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stropts.h

`stropts.h` is the user/kernel STREAMS options and ioctl ABI header. It defines read/write mode bits, flush flags, signal/poll event bits, getmsg/putmsg flags, stream ioctl command numbers, and the user-visible structures passed to those ioctls.

Read options include normal, message-discard, and message-nondiscard modes (`RNORM`, `RMSGD`, `RMSGN`), plus protocol handling modes (`RPROTDAT`, `RPROTDIS`, `RPROTNORM`) and the private `RFLUSHPCPROT` behavior. Write options define zero-length message and SIGPIPE behavior. Error options control persistent versus nonpersistent read/write-side errors. Copy options advertise zero-copy safety and cache-copy preferences.

The event constants (`S_INPUT`, `S_HIPRI`, `S_OUTPUT`, `S_MSG`, `S_ERROR`, `S_HANGUP`, `S_RDNORM`, `S_RDBAND`, `S_WRBAND`, `S_BANDURG`) are used by `I_SETSIG`/`I_GETSIG` and stream poll/signal delivery. Message flags include classic `RS_HIPRI`, `MSG_HIPRI`, `MSG_ANY`, and `MSG_BAND`, plus kernel-private flags for internal `kstrgetmsg()`/`kstrputmsg()` behavior.

The ioctl namespace is rooted at `STR`. It defines module stack operations (`I_PUSH`, `I_POP`, `I_LOOK`, `I_FIND`, `I_LIST`), flushing and watermarks, `I_STR`, signal registration, mux link/unlink (`I_LINK`, `I_UNLINK`, `I_PLINK`, `I_PUNLINK`), descriptor passing (`I_SENDFD`, `I_RECVFD` with kernel/user numbering differences), message peeking/insertion, band operations, at-mark checks, error option accessors, private module insertion/removal, peer credential lookup, layered-driver plink support, and `_I_CMD`.

Data structures include `strioctl` and `strioctl32`, `strcmd_t` for private in-kernel command payloads, `strbuf` and `strbuf32`, `strpeek`/`strpeek32`, `strfdinsert`/`strfdinsert32`, receive-FD structures, `str_mlist`/`str_list`, private `strmodconf`, `bandinfo`, and extended signal set `strsigset`. The header carefully isolates XPG4.2 namespace variants and remaps `putmsg`/`putpmsg` to XPG4 entry points when needed.

Key relationship: `stream.h` consumes many of these flags in `stroptions`, getmsg/putmsg paths, and kernel helper APIs; `strsubr.h` carries the stream-head internal state that implements these user-visible options.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stropts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strredir.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strredir.h

`strredir.h` declares the STREAMS redirection driver/module interface. It assigns `STRREDIR_MODID` and uses that module ID to form two ioctls: `SRIOCSREDIR` to set a redirection target and `SRIOCISREDIR` to query whether a stream is a redirection target.

The comments note that module ID uniqueness is not centrally administered, which matters because ioctl cookie values are derived from the module ID. Kernel-only content names the close-detection module (`redirmod`) and declares `srpop(vnode_t *, boolean_t)`, used to pop/clean redirection module state from a stream vnode.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strredir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strstat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strstat.h

`strstat.h` defines the historical per-module STREAMS statistics structure `module_stat`. Counters track calls to put, service, open, close, and admin procedures (`ms_pcnt`, `ms_scnt`, `ms_ocnt`, `ms_ccnt`, `ms_acnt`). The structure also provides a private statistics buffer pointer and size (`ms_xptr`, `ms_xsize`).

`stream.h` references `struct module_stat *qi_mstat` from `struct qinit`, making this header part of the module publication ABI even though the contents are small.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strsubr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strsubr.h

`strsubr.h` is the private STREAMS subsystem header. It explicitly warns consumers that including it forfeits release-to-release portability. It extends `stream.h` and `stropts.h` with stream-head state, syncq/perimeter concurrency, mux graph tracking, module/driver implementation records, and internal function declarations.

The opening comments document STREAMS lock hierarchy: stream-level claims protect `q_next`, queue-level claims protect `q_ptr` and single-threading, stream-head locks implement read/write/open/close monitors, and queue locks are taken by utility routines. `sd_lock` ownership is spelled out for many `stdata_t` fields. Stream-level locks must precede queue-level locks. Additional commentary explains distributed `stream_putlocks` used to reduce contention on highly contended streams.

`stdata_t` is the stream-head private state. It holds the write queue, ioctl reply block, vnode, streamtab, flags, ioctl IDs, session/process group IDs, write offset/tailroom, read/write errors, push count, signal/poll state, marked message, close timeout, monitor condition variables, queue packet-size cache, twisted-stream mate/freezer/refcount state, synchronous UIO queues, audit data, maximum block size, parameterized stream-head hook functions, low-contention putnext controls, anchor state, stream-head service scheduling queue, zero-copy wait state, copy flags, anchor zone, `_I_CMD` reply, and cloned-device parent vnode.

The stream-head flag namespace covers ioctl/open/close waits, sleep states, priority message state, hangup, tty behavior, pending getmsg, read/write error persistence, close/plumbing, read notification, old NDELAY/XPG4 TTY behavior, mount/delimiter/atmark/EOF, zero-copy notification, reopen failure, twisted streams, and linked mux state. Additional bitsets describe read-side put behavior, write/putmsg behavior, read options, and hook configuration flags.

`syncq_t` models STREAMS perimeters. It tracks entry counts, state flags, deferred queue/message/event lists, inner/outer perimeter links, callback synchronization, distributed put counters, exclusive waiters, background scheduling, and max queue priority. The header defines state flags (`SQ_EXCL`, `SQ_BLOCKED`, `SQ_FROZEN`, `SQ_WRITER`, `SQ_MESSAGES`, wakeup flags), masks (`SQ_GOAWAY`, `SQ_STAYAWAY`, `SQ_TAIL`), concurrency types (`SQ_CIPUT`, `SQ_CISVC`, `SQ_CIOC`, `SQ_CICB`, and outer equivalents), and entry-type combinations (`SQ_PUT`, `SQ_SVC`, `SQ_OPENCLOSE`, `SQ_CALLBACK`). It also defines callback cancellation flags for qtimeout/qbufcall integration.

The file defines support structures for callbacks (`callbparams_t`, `strbufcall_t`), signal delivery (`strsig_t`), bufcall lists, mux cycle detection (`mux_node`, `mux_edge`), queue allocation bundles (`queinfo_t`), mux links (`linkinfo_t`), frozen-stream syncq lists, per-module syncq sharing (`perdm_t`), module switch implementation records (`fmodsw_impl_t`), character-driver STREAMS implementation records (`cdevsw_impl_t`), job-control access modes, and per-netstack STREAMS state (`str_stack_t`).

Lock and counter macros implement stream/syncq distributed-put locking, debug validation, and syncq message insertion. The private API surface covers stream initialization, ioctl processing, signal/hangup delivery, qattach/qdetach, queue enter/leave/claim/release, mux link/unlink and cycle handling, module and driver syncq setup, message construction and getmsg/putmsg, stream open/close/read/write/ioctl/poll, stream-head put processing, buffer allocation waits, qband/queue allocation, copyin/copyout, flow-control wakeups, syncq enter/leave/drain/flush, outer perimeter enter/exit, qwriter helpers, callback wrappers, credential propagation, vnode/queue conversion, kernel getmsg/putmsg, stream error/eof hooks, checksum/LSO helpers, module registration, message-chain copy/free, and shared tunables.

At the end, internal macros map queues to opposite/read/write sides (`_OTHERQ`, `_WR`, `_RD`, `_SAMESTR`) and expose private checksum/LSO dblk fields. This file is the implementation map for how the public STREAMS ABI in `stream.h`/`stropts.h` is actually synchronized and executed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strsubr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strsun.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strsun.h

`strsun.h` exposes Solaris DDI STREAMS utility macros and kernel helper prototypes for working with `mblk_t`/`dblk_t`. It includes `stream.h` and `types.h`.

The macros provide stable access to data-block base/limit/ref/type/flags and message geometry: `MBLKL()` for bytes currently in an mblk, `MBLKSIZE()` for data-buffer capacity, `MBLKHEAD()` for headroom, `MBLKTAIL()` for tailroom, and `MBLKIN()` to validate a range inside the readable message data.

Kernel-only helper declarations cover STREAMS ioctl copy helpers (`mcopyin`, `mcopyout`, `mcopymsg`), error and ioctl acknowledgment helpers (`merror`, `mioc2ack`, `miocack`, `miocnak`, `miocpullup`), message exchange (`mexchange`), and message sizing (`msgsize`).

This header is the supported utility layer over selected `stream.h` internals, contrasting with `strsubr.h`, which is private implementation detail.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strsun.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strtty.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strtty.h

`strtty.h` defines legacy STREAMS TTY subsystem structures and constants. `t_buf` describes an input or output message/data buffer with message pointer, current buffer pointer, and count. `strtty` aggregates input/output buffers, read queue, ioctl block, large buffer, device number, termios-style flag fields, internal state, line discipline, device status, and control-character array.

The header defines a 512-byte large buffer size, input/output priorities (`TTIPRI`, `TTOPRI`), many internal TTY state bits (`TIMEOUT`, `WOPEN`, `ISOPEN`, `CARR_ON`, `BUSY`, `WIOC`, `TTSTOP`, `EXTPROC`, `RTO`, `TTXON`, `TTXOFF`, etc.), and device command numbers for output, timeout, suspend/resume, flow block/unblock, flushes, break, input, disconnect, parameter changes, and switch.

It also defines STREAMS `M_CTL` control message subtypes for canonicalization negotiation and device-specific service behavior, including POSIX close semantics probes. The constants are legacy-heavy and partly overlapping (`MC_PART_CANON` and `MC_SERVICEIMM` both use value 3), reflecting historical STREAMS TTY module/driver conventions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strtty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunddi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunddi.h

`sunddi.h` is the large Sun-specific Device Driver Interface header. It collects DDI status codes, device-node/minor-node naming constants, devfs/DDI event strings, fault-state enums, property APIs, devinfo traversal and identity APIs, register/memory mapping, DMA, soft-state, callbacks, events, task queues, interrupts, FMA, PCI helpers, devid support, and layered-driver-adjacent helpers.

The public constants start with generic DDI return values (`DDI_SUCCESS`, `DDI_FAILURE`, `DDI_EAGAIN`, `DDI_EINVAL`, etc.), allocation sleep flags, pseudo/persistent/hidden node IDs, and `ddi_create_minor_node()` flags. Device node-type strings cover serial, block/channel/WWN/SAS/blkdev/xVM, CD/floppy/tape, network/wifi, display/DRM, pseudo, audio, mouse, keyboard, parallel/printer, USB generic, SMP, EEPROM, nexus/attachment point variants, fabric devices, AV, AGP, register/intr tool nodes, sensors, GPIO, and I2C.

The event vocabulary defines devfs and DDI event classes/subclasses, event publisher name, and nvlist attribute names used for minor creation/removal, devinfo add/remove, instance changes, branch events, and initiator registration. Fault enums model service impact, fault location, and device state with ordered values for future interpolation.

Kernel-visible definitions include common driver properties, devinfo walk return codes, `DDI_KERNEL_IOCTL`, datamodel conversion constants, `ddi_err()` severity modes, string/memory utility declarations, numeric conversion helpers, and kernel iconv wrappers.

Mapping and memory-management APIs include `ddi_map_regs()`, `ddi_unmap_regs()`, `ddi_map()`, bus map wrappers, register specs, safe peek/poke operations, `ddi_peekpokeio()`, page-size conversions, critical-region entry/exit, devmap setup/load/unload/remap/context management, `ddi_umem_*` allocation/locking/I/O setup, segmap helpers, map-fault handling, and mapping checks.

Property APIs cover typed lookup/update for int, int64, string, byte arrays, boolean existence, freeing lookup buffers, core `ddi_prop_op()` variants for size/nblocks, legacy long property getters, property creation/modification/removal/undefinition, cache invalidation, and bus property propagation. The comments repeatedly stress that underlying drivers must be held when invoking property providers.

Devinfo APIs cover tree walking, name/binding/driver-major queries, driver private data, power-needed/removing-power checks, parent/child/sibling access, child add/remove, driver hold/release and install, instance hold/release, stream queue association, root node, and lookup by name/instance. DMA APIs include sync semantics, burst-size query, attribute merge, handle allocation/free, memory allocation/free, address/buffer bind, unbind, deprecated `ddi_dma_nextcookie()`, window query, SBus64 support, no-DMA stubs, nexus DMA wrappers, DVMA support, and modern cookie iteration/get/one helpers.

Miscellaneous DDI functions include attach reporting, register size/count queries, self-identifying and slave-only checks, device affinity, callback list setup/run, default/no-op driver helpers, current credential/time/pid/thread identity helpers, minor-node creation/removal, panic/streams-driver checks, soft-state by integer or string key, string-ID maps, name-address and parent-data access, child init/uninit, major/name translation, pathname construction, bus control wrappers, layered `ddi_copyin()`/`ddi_copyout()`, process signaling refs, x86 I/O port accessors, console bell hooks, access/DMA handle checks, fault reporting, and device state retrieval.

Register access and PCI helpers include `ddi_regs_map_setup/free`, portable `ddi_get*`/`ddi_put*` and repeated accessors, device zero/copy, byte swapping, PCI config setup/get/put, PCI PM capability reporting, config save/restore, ereport setup/post, x86 peek/poke checking, PCI target queue, suspend/resume hooks, and datamodel inquiry/conversion.

Device ID support includes validation, registration, initialization, retrieval, size/free/compare, SCSI/SMP encoding, GUID conversion, layered devid/minor lookup, devid-to-devlist, string encode/decode/free/compare. The event section exposes device insert/remove/reset event names, add/remove event handlers, event-cookie lookup, sysevent logging, DDI task queues, interface-name parsing, IPL constants, periodic callbacks, quiesce defaults, generic callback registration, memory-update notification, and platform path-alias registration/redirect state.

This header is a broad driver-facing contract. `sunndi.h` builds private nexus operations on top of it; `sunldi.h` uses related device identity/property/event concepts for layered opens; `sunpm.h` is included for power management pieces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunddi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi.h

`sunldi.h` declares the kernel Layered Driver Interface. Its opaque handle types represent layered-driver identities, open handles, callback registrations, and event cookies.

LDI events define success/failure/no-callback return values and event names for offline, degrade, and device removal. `ldi_ev_callback_t` version 1 carries notify and finalize callbacks, allowing a layered consumer to vote on or react to provider events.

Identity functions create/release an `ldi_ident_t` from anonymous context, module linkage, major number, devinfo node, device number, or STREAMS queue. Open functions create `ldi_handle_t` values by `dev_t`, path name, or devid/minor name, and helper functions return vnodes from path or devid. `ldi_close()` releases a handle.

The handle operation surface mirrors common driver entry points: read, write, ioctl, poll, get size, property operations, block strategy, dump, devmap, async read/write, STREAMS putmsg/getmsg, typed property lookups/getters, and queries for target dev_t, open type, devid, and minor name.

The event API lets consumers get event cookies, query event type strings, register/remove callbacks, and lets providers notify/finalize events for a devinfo/minor/spec-type tuple. This header is the public kernel-facing API; `sunldi_impl.h` defines the private backing structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi_impl.h

`sunldi_impl.h` is the private implementation header for LDI. It defines hash sizes for handles and idents, keeps obsolete event support enabled behind `LDI_OBSOLETE_EVENT`, declares handle flags, and exposes `ldi_init()`.

Private STREAMS link helpers bridge LDI handles/files into STREAMS mux linking (`ldi_mlink_lh`, `ldi_mlink_fp`, `ldi_munlink_fp`). `struct ldi_ident` records hash linkage, refcount, module name/id, major number, devinfo pointer, and dev_t. `struct ldi_handle` records hash linkage, refcount, flags, handle type, identity pointer, vnode pointer, and obsolete-event state protected by `lh_lock`.

Obsolete `ldi_event_t` stores per-handle callback linkage and handler information. The newer callback implementation `ldi_ev_callback_impl_t` records handle, devinfo, dev_t/spec type, notify/finalize function pointers, callback argument, cookie/id, and list linkage. `struct ldi_ev_callback_list` documents a careful locking and in-progress-walk protocol: unregistering callbacks during notify/finalize walks is supported by walker-next/walker-prev fields.

Internal event delivery functions invoke notify/finalize callbacks and bridge DDI offline notifications. The device usage interface defines `ldi_usage_t`, which reports source module/name/devinfo/dev_t and target module/name/devinfo/dev_t/spec type. `ldi_usage_count()` and `ldi_usage_walker()` allow devinfo/fuser-style consumers to enumerate kernel device clients without knowing LDI internals.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunmdi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunmdi.h

`sunmdi.h` declares the Multiplexed I/O/MPxIO framework interface. It defines return codes, opaque pathinfo handles, path states, and vHCI class names for SCSI and IB.

Kernel definitions identify MPxIO components as vHCI, pHCI, or client and provide macros to test a devinfo node's component role. `mdi_pathinfo_state_t` carries basic path state, while additional high bits encode transient/user-disabled/driver-disabled state. Separate pathinfo flags mark hidden paths and removed devices.

The API covers device online/offline hotplug notifications, pHCI retirement/unretirement notifications, MDI-aware devinfo locking, vHCI lookup, attach/detach pre/post hooks, path allocation/free/hold/release, state transitions (`online`, `standby`, `fault`, `offline`), path enable/disable, hidden/removed/inserted state, MPxIO power-management operations, bus power hooks, and path walkers for pHCI/client paths.

Pathinfo member accessors expose client and pHCI devinfo nodes, node name, address, state, flags, instance, pathname forms, and OBP pathname controls. Property helpers mirror DDI property operations for pathinfo nodes: update/remove/iterate/lookup typed values and free returned property data.

pHCI/vHCI registration helpers let transport providers register or unregister by class and devinfo. Additional walkers enumerate vHCIs, pHCIs, clients, and pHCI driver lists. This header sits on top of `sunddi.h`/`esunddi.h` and is the multipath storage/device topology layer in this group.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunmdi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunndi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunndi.h

`sunndi.h` defines Sun-specific Nexus Driver Interface operations. It is kernel-only and builds on `sunddi.h`/`esunddi.h` to let nexus drivers create, configure, offline, remove, hotplug, and resource-manage child devinfo nodes.

Return values extend DDI status with NDI-specific errors for no memory, bad handles, copy faults, busy devices, unbound devices, invalid requests, unsupported events, and claimed/unclaimed event delivery.

Property functions provide nexus-owned mutation/removal APIs for boolean, int, int64, string, and byte-array properties. Devinfo lifecycle APIs allocate/free child nodes, lock/unlock/try-enter devinfo nodes, hold/release devinfo and drivers, rename nodes, bind drivers, asynchronously bind persistent nodes, online/offline/config/unconfig children, and perform generic devctl ioctl handling. Flag bits describe removal, attach-on-online, recursive config/unconfig, persistent behavior, PROM naming, event suppression, debug, reprobe, forced online/offline, branch events, detach context, single-threading disable, and user-requested operations.

Devctl convenience functions copy in/out `devctl_iocdata`, extract path/name/address/minor/AP data, return device/AP/bus state, and create devinfo nodes from devctl requests. Bus state getters/setters and child finders support nexus ioctl implementations.

The NDI event framework includes upward event posting, busop event callback registration/removal/cookie lookup, event handles, event definitions/cookies/sets, event attributes, callback list structures, bind/unbind, cookie retrieval, callback add/remove/run/do-one, tag/name conversion helpers, debug dump support, and default bus_config/bus_unconfig helpers.

Hotplug APIs register/unregister connection points, request state changes, and walk connection points. Bus Resource Allocator APIs define allocation request constraints for memory, I/O, PCI bus numbers, prefetchable memory, and interrupts, with map setup/destroy, allocate, and free routines.

Node classification helpers identify PROM, pseudo, persistent, hotplug, and hidden nodes and set/clear hidden state. Fault support defines `DDI:DEVI_FAULT` payload data and access/DMA handle fault mark/clear functions. The end of the file handles driver.conf property merging and NDI "flavor" support for nexus drivers whose children have multiple flavor-specific private-data interpretations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunndi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunos_dhcp_class.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunos_dhcp_class.h

`sunos_dhcp_class.h` defines SunOS/Solaris vendor-class DHCP option numbers used by DHCP clients/tools and network boot paths. `VS_OFFSET` is 256 for `dhcpinfo` option numbering.

Vendor-specific options cover NFS root mount options, root server IP/name, root path, swap server and swap file, boot file, POSIX timezone, boot NFS read size, install server IP/name/path, sysid and JumpStart server paths, terminal type, network boot standalone URI, and WAN boot HTTP proxy. `VS_OPTION_END` is kept equal to the highest defined option.

The file is pure constants and has no kernel-only section.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunos_dhcp_class.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunpm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunpm.h

`sunpm.h` defines Sun-specific power-management interfaces used by kernel drivers. It includes DDI/devctl-related headers and is pulled into `sunddi.h`.

The header defines power-cycle transition check formats for SCSI and SMART devices. `pm_scsi_cycles` stores lifetime maximum cycles, current cycles, service date, and flags. `pm_smart_count` stores normalized allowed and consumed cycle counts. `pm_trans_data` tags the format and carries either structure.

It maps ACPI D-states to Solaris PM component levels: D3/off is level 0 and D0/full power is level 3, with generic property strings for `pm-components`. Kernel declarations include obsolete component creation/destruction/normal-power routines and active interfaces for busy/idle component accounting, current power query, power-change notification, transition checks, lower/raise power requests, and max-power updates.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunpm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/suntpi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/suntpi.h

`suntpi.h` defines private kernel support for Transport Provider Interface capability caching. It is for sockfs and timod internal use.

`tpi_provinfo_t` records provider entries keyed by opaque data, protected by a mutex because the capability bitfields are not atomic. It tracks whether capability, local-name, and peer-name operations are supported, unsupported, or unknown using the two-bit values `PI_DONTKNOW`, `PI_NO`, and `PI_YES`.

Kernel declarations initialize the cache (`tpi_init()`), find provider information from a queue (`tpi_findprov()`), lock/unlock provider entries, and allocate TPI acknowledgement messages (`tpi_ack_alloc()`).
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/suntpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/suntty.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/suntty.h

`suntty.h` is effectively a compatibility placeholder. Its only substantive content is a comment identifying it as a build kludge and showing a historical `TIOCCONS` definition that is not active.

The header keeps the include guard and C++ linkage wrapper so old include paths remain valid even though it exports no active constants or declarations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/suntty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/swap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/swap.h

`swap.h` defines the `swapctl` ABI and kernel swap/anonymous-memory helpers. It rejects use of `swapctl` in 32-bit large-file compilation mode because the ABI structures use `off_t` directly.

`swapctl` commands include add, list, remove, get number of configured swap resources, and anonymous memory information (`SC_ADD`, `SC_LIST`, `SC_REMOVE`, `SC_GETNSWP`, `SC_AINFO`). User-visible structures describe requested swap resources (`swapres_t`), listed swap entries (`swapent_t`), and variable-length swap tables (`swaptbl_t`). 32-bit syscall views (`swapres32_t`, `swapent32_t`, `swaptbl32_t`) are defined for kernel compatibility.

Swap entry flags mark deletion in progress and deletion/re-add behavior (`ST_INDEL`, `ST_DOINGDEL`). Kernel `swapinfo` describes a configured swap area with byte offsets, vnode, next link, allocation counters, flags, total/free pages, path name, bitmap size and slots, allocation hint, and allocation-search counters.

The anon-slot mapping macros convert an anonymous-memory slot into a `(vnode, offset)` page identity. `swap_alloc()` derives a swapfs vnode index and page-aligned offset from the address of the anon slot, deliberately using low address bits for vnode selection to reduce page hash vnode mutex contention. `swap_xlate()` returns the stored vnode/offset and `swap_free()` is currently empty.

Kernel declarations expose physical swap allocation/free/name translation, anon lookup by vnode/offset, global `swapinfo`, and debug controls. `SWAP_PRINT` conditionally prints debug output for rename, reservation, allocation, and control categories.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/swap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/synch.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/synch.h

`synch.h` defines low-level user synchronization object layouts shared by threads, LWPs, and pthread ABI structures. It avoids pulling POSIX namespace pollution into `pthread.h`, so the comments require these layouts to stay synchronized with corresponding pthread types elsewhere.

`lwp_mutex_t` stores flag words, ceiling, type/recursive count union, magic value, owner/lock word in 32-bit or 64-bit-compatible form, and optional data. `lwp_cond_t` stores flags, type, magic, and data. `lwp_sema_t` stores count, type, magic, flags, and data. `lwp_rwlock_t` stores reader state, type, magic, and embedded mutex/condition variables used for process-shared rwlocks and ownership indication.

Synchronization type constants distinguish process-private and process-shared objects (`USYNC_THREAD`, `USYNC_PROCESS`) and lock types/attributes (`LOCK_NORMAL`, `LOCK_SHARED`, `LOCK_ERRORCHECK`, `LOCK_RECURSIVE`, `LOCK_PRIO_INHERIT`, `LOCK_PRIO_PROTECT`, `LOCK_ROBUST`). `USYNC_PROCESS_ROBUST` is a deprecated historical alias mapped by initialization code. Mutex flags describe owner-dead, not-recoverable, initialized, unmapped, and deadlock states.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/synch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syscall.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syscall.h

`syscall.h` defines illumos system call numbers for use with `syscall(SYS_xxx, ...)` and kernel/user syscall tables. The enumeration begins at 1, while `SYS_syscall` remains 0 as the indirect syscall mechanism on SunOS/SPARC.

The file assigns syscall numbers for classic process, file, filesystem, IPC, signal, VM, scheduling, LWP, large-file, zones, socket, port, timer, door, privilege, audit, processor, and administrative interfaces. Many multiplexed syscalls include comments documenting subcodes, including `pgrpsys`, `msgsys`, `shmsys`, `semsys`, `utssys`, `tasksys`, `exacctsys`, `getpagesizes`, `rctlsys`, `sidsys`, `lwp_park`, `sendfilev`, `privsys`, `ucredsys`, `sigpending`, `context`, `utimesys`, `forksys`, `kaio`, `lgrpsys`/`meminfosys`, `rusagesys`, `port`, `lwp_rwlock_sys`, `zone`, and door operations.

Filesystem-relevant entries include open/close/read/write, link/unlink/symlink/readlink variants, stat/fstat/lstat and 64-bit variants, mount/umount2, sync/fdsync, chdir/fchdir/chroot/fchroot, rename/renameat, mkdir/rmdir/mknod and `*at` variants, statvfs/fstatvfs and 64-bit variants, pathconf/fpathconf, getdents/getdents64, mmap/mmap64/mmapobj, mincore, memcntl, sendfilev, sharefs, autofssys, and ACL/facl.

The tail defines `sysset_t` as 16 32-bit words for syscall sets and `sysret_t` with two long return values. User-level declarations expose `syscall()`, `__systemcall()` returning `sysret_t`, and `__set_errno()` when not compiling the kernel.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syscall.h -->