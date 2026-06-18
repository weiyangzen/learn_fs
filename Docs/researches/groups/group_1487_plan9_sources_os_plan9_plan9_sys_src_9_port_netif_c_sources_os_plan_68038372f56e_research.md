# Group Research: group_1487_plan9_sources_os_plan9_plan9_sys_src_9_port_netif_c_sources_os_plan_68038372f56e

Scope verified against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/netif.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/netif.c

Implements the reusable Plan 9 network-interface file-server layer used by network drivers. It exposes a three-level 9P-style namespace: top network directory, second-level `clone`/`addr`/`stats`/`ifstats` plus per-conversation directories, and third-level per-conversation `data`, `ctl`, `stats`, `type`, and `ifstats`.

Key responsibilities:
- `netifinit` initializes `Netif` name, conversation slots, and input queue limit.
- `netifwalk`, `netifopen`, `netifclose`, `netifread`, `netifbread`, `netifwrite`, `netifstat`, and `netifwstat` provide generic device operations for network drivers.
- `openfile` allocates or reopens `Netfile` conversations and input queues.
- `netown` lazily assigns ownership and enforces owner/eve/other permissions.
- `netifwrite` parses control commands: `connect`, `promiscuous`, `scanbs`, `bridge`, `headersonly`, `addmulti`, and `remmulti`.
- Multicast state is reference-counted globally in `Netaddr` lists/hash buckets and per-open in `Netfile.maddr`.
- `activemulti` checks whether a multicast address is actively referenced.
- Provides network byte-order helpers `hnputv`, `hnputl`, `hnputs`, `nhgetv`, `nhgetl`, `nhgets`.

Important behavior:
- Opening `clone` returns a control qid for a newly allocated conversation.
- Opening `data` or `ctl` increments `Netfile.inuse` and reopens its queue.
- Closing the last reference tears down promiscuous mode, scanning, multicast subscriptions, wildcard type count, owner, bridge/headersonly flags, type, and queue state.
- `typeinuse` prevents duplicate positive multiplexor types; negative types increment `nif->all`.
- `netifread` reports device counters and hardware address in text form.
- Driver-specific hardware hooks are invoked through `Netif.promiscuous`, `Netif.multicast`, and `Netif.scanbs`.

Dependencies:
- Queue operations from `qio.c`.
- Permission, channel, directory, and qid helpers from the Plan 9 port device layer.
- `netif.h` for `Netif`, `Netfile`, qid macros, and Ethernet constants.

Cautions:
- `netmulti` only tracks up to `8*sizeof(f->maddr)` multicast membership bits per `Netfile`; global references still exist beyond that index.
- `parseaddr` expects hex octets with optional colon separators and does not validate trailing garbage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/netif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/netif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/netif.h

Defines the generic network interface structures and constants shared by Plan 9 network drivers and `netif.c`.

Main definitions:
- Qid type constants: `Ncloneqid`, `Naddrqid`, `N2ndqid`, `N3rdqid`, `Ndataqid`, `Nctlqid`, `Nstatqid`, `Ntypeqid`, `Nifstatqid`, `Nmtuqid`.
- Qid packing macros: `NETTYPE`, `NETID`, `NETQID`.
- `Netfile`: one multiplexed open/conversation, including owner/mode, type, promiscuous/scan/bridge/headersonly flags, multicast bitmask, and input `Queue`.
- `Netaddr`: multicast address node with allocation-chain link, hash-chain link, fixed-size address storage, and reference count.
- `Netif`: shared interface state: name, `Netfile` table, address/MTU/link data, multicast tables, counters, and hardware callback hooks.
- Ethernet constants and `Etherpkt` layout.

Exported operations:
- `netifinit`, `netifwalk`, `netifopen`, `netifclose`, `netifread`, `netifbread`, `netifwrite`, `netifwstat`, `netifstat`, `activemulti`.

Role in repository:
- This is the portable contract for network device implementations to expose Plan 9 network conversations through a uniform file interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/netif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/page.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/page.c

Implements the physical page allocator, page cache hash, page reference diagnostics, and PTE helpers for the Plan 9 port VM layer.

Key responsibilities:
- `pageinit` builds the global `palloc.pages` array and free list from configured memory banks, assigns cache colors, initializes swap watermarks, and prints memory/swap totals.
- `newpage` allocates a colored page, blocking and kicking the pager when below `swapalloc.highwater`.
- `putpage`, `auxpage`, `pagechainhead`, `pagechaintail`, and `pageunchain` manage the free/LRU list.
- `duppage` opportunistically duplicates image-backed cached pages to preserve cache contents.
- `copypage` copies page contents through temporary kernel mappings.
- `uncachepage`, `cachepage`, `cachedel`, and `lookpage` maintain the image/swap page hash.
- `ptealloc`, `ptecpy`, and `freepte` manage segment PTE tables, including swap references and physical segment free callbacks.
- `checkpagerefs` and `portcountpagerefs` diagnose page reference-count mismatches across process segments.

Important behavior:
- Pages with backing images are returned to the tail; anonymous/swap pages go to the head.
- `newpage` may temporarily release a segment lock during memory pressure to avoid deadlock in page fault paths.
- `lookpage` increments page refs and removes a page from the free list if it was cached but unreferenced.
- `freepte` treats `SG_PHYSICAL` segments specially and uses `pgfree` if supplied.

Cautions:
- `duppage` contains an inline comment describing a suspected race around temporarily putting `np` back on the freelist while copying/caching it.
- Several routines assume specific lock ordering: generally `palloc` before individual `Page`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/parse.c

Provides small command parsing helpers used by device control files.

Key functions:
- `parsecmd(char *p, int n)`: copies an input buffer, strips one trailing newline, tokenizes whitespace-separated fields, and returns a `Cmdbuf` containing the original buffer and `char **f` field vector.
- `cmderror(Cmdbuf *cb, char *s)`: reconstructs the command with `%q` quoting and raises an error with diagnostic text.
- `lookupcmd(Cmdbuf *cb, Cmdtab *ctab, int nctab)`: matches `cb->f[0]` against a command table, supports wildcard `"*"`, verifies argument count when `narg != 0`, and reports unknown/argument errors.

Implementation notes:
- `ncmdfield` computes a conservative number of token slots by scanning whitespace.
- Allocation is a single `smalloc` containing `Cmdbuf`, field pointers, and copied command text.
- If running in a process context, `parsecmd` protects allocation/copy with Plan 9 error unwinding.

Role:
- Shared parser for kernel device control messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/pgrp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/pgrp.c

Implements process group support for namespaces, rendezvous groups, file descriptor groups, mount duplication, and resource-wait throttling.

Key responsibilities:
- `newpgrp`, `closepgrp`: allocate/free namespace groups and all mount heads.
- `newrgrp`, `closergrp`: allocate/free rendezvous groups.
- `pgrpnote`: posts a note to all non-kernel processes sharing a note id.
- `pgrpcpy`: copies a process namespace while preserving parent mount-id allocation order.
- `newmount`, `mountfree`, `pgrpinsert`: allocate/free ordered mount chains.
- `dupfgrp`, `closefgrp`, `forceclosefgrp`: duplicate and tear down file descriptor groups.
- `resrcwait`: sleep briefly during resource exhaustion and rate-limit console complaints.

Important behavior:
- `pgrpcpy` builds a temporary order chain of parent mounts, then allocates copied mount ids in parent order while holding `mountid`.
- `closefgrp` sets `up->closingfgrp` so `forceclosefgrp` can move remaining channels to the close queue if a kill interrupts a deadlocked close path.
- `closepgrp` invalidates `pgrpid`, closes mount source channels, frees mount chains, and drops mount heads under namespace/debug locks.

Role:
- Provides core process-shared namespace/fd/rendezvous state used by `rfork`, process exit, bind/mount, and `/proc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/pgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portclock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/portclock.c

Implements portable high-resolution timer queues and the periodic clock path.

Key responsibilities:
- Maintains one sorted timer list per Mach in `timers[MAXMACH]`.
- `timeradd` and `timerdel` add, modify, or remove relative/periodic timers with required lock ordering.
- `timerintr` dispatches expired timers, reschedules periodic timers, and defers `hzclock` calls for timers whose callback is nil.
- `timersinit` initializes time-of-day support and installs the periodic HZ timer.
- `addclock0link` adds periodic callbacks on CPU 0, synchronized to HZ when `ms == 0`.
- `hzclock` updates ticks, records PC, flushes MMU if requested, accounts time, invalidates kmaps, calls profiling/alarm hooks, and requests scheduling.
- `tk2ms` and `ms2tk` convert ticks and milliseconds with overflow avoidance.

Important behavior:
- Periodic timers of equal period can share phase by copying an existing timer’s `twhen`.
- `timerintr` caps loop iterations with `Maxtimerloops` diagnostics to catch timer/cycle-counter problems.
- `hzclock` exits other processors if `active.exiting` is set.

Dependencies:
- Platform must supply `fastticks`, `ns2fastticks`, `timerset`, `todinit`, and clock interrupt entry.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portclock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portdat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/portdat.h

Central portable data-structure contract for the Plan 9 kernel port layer.

Major contents:
- Common typedefs for kernel objects: `Chan`, `Dev`, `Block`, `Queue`, `Page`, `Segment`, `Proc`, `Pgrp`, `Fgrp`, `Rgrp`, `Image`, `Timer`, `Uart`, and many others.
- Numeric helpers and bitfield macros: `HOWMANY`, `ROUNDUP`, `ROUNDDN`, `ROUND`, `PGROUND`, `FIELD`, `FEXT`, `FINS`, etc.
- Synchronization structures: `Ref`, `Rendez`, `QLock`, `RWlock`.
- Device/channel structures: `Chan`, `Path`, `Dev`, `Dirtab`, `Walkqid`.
- Mount namespace structures: `Mount`, `Mhead`, `Mnt`, `Mntwalk`.
- VM structures: `Page`, `Swapalloc`, `Image`, `Pte`, `Physseg`, `Sema`, `Segment`.
- Process structures: `Pgrp`, `Rgrp`, `Egrp`, `Fgrp`, `Proc`, `Schedq`, `Waitq`.
- Timer and scheduling constants, process states, rfork flags, segment indices, priority levels.
- Global externs for kernel configuration, device table, queues, swap image, syscall names, and system identity.
- UART, performance, watchdog, watermark, command parsing, and queue state structures/constants.

Notable details:
- `struct Proc` embeds scheduler state, memory segments, fd/env/namespace/rendez groups, note/debug state, timer state, MMU-private state, and syscall trace storage.
- `struct Segment` embeds a semaphore list used by user semaphores.
- `struct Swapalloc swapalloc` is defined in this header, not merely declared.
- Queue state bits `Qstarve`, `Qmsg`, `Qclosed`, `Qflow`, `Qcoalesce`, and `Qkick` are shared with `qio.c`.

Role:
- This file is a dependency hub; most port C files include it and rely on its exact layouts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portdat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portfns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/portfns.h

Declares the portable kernel function surface for the Plan 9 port.

Coverage:
- Scheduler/process APIs: `sched`, `ready`, `sleep`, `wakeup`, `newproc`, `pexit`, `procctl`, `kproc`, priority and trace helpers.
- VM/page/segment APIs: `newpage`, `putpage`, `cachepage`, `lookpage`, `fault`, `seg`, `newseg`, `dupseg`, `putseg`, `setswapchan`, `swapinit`.
- Device/channel/name APIs: `namec`, `devwalk`, `devopen`, `devstat`, `cclose`, `fdtochan`, `newfd`, `walk`, `unionread`.
- Queue/block APIs: `allocb`, `freeb`, `qopen`, `qread`, `qwrite`, `qbwrite`, `qhangup`, `qclose`, block manipulation helpers.
- Locking and reference APIs: `lock`, `unlock`, `ilock`, `iunlock`, `qlock`, `qunlock`, `rlock`, `wlock`, `incref`, `decref`.
- Time/timer APIs: `timeradd`, `timerdel`, `todget`, `ms2tk`, `tk2ms`, `fastticks` conversions.
- Device-specific portable interfaces: UART, keyboard, draw, watchdog, boot/reboot, random, logging.
- Byte-order helpers: `hnputv`, `hnputl`, `hnputs`, `nhgetv`, `nhgetl`, `nhgets`.

Notable details:
- Contains macro `MS2NS` and `poperror`.
- Declares `ms2tk` twice.
- Includes a non-ASCII `µs(void)` prototype inherited from Plan 9 source.
- Uses Plan 9 vararg checking pragmas for `iprint`, `panic`, and `pprint`.

Role:
- Shared function declaration layer needed by nearly all port C files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portfns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portusbehci.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/portusbehci.h

Defines portable EHCI USB host-controller register layouts and bit constants.

Contents:
- `Ecapio`: EHCI capability registers: `cap`, `parms`, `capparms`, `portroute`.
- `Edbgio`: EHCI debug port registers: `csw`, `pid`, 8-byte `data`, and `addr`.
- Capability bits for port count, debug port index, 64-bit support, programmable frame list, async park, and extended capability pointer.
- Legacy support register offsets/ids.
- Typed queue link constants for EHCI schedule entries.
- Command/status/interrupt/config/port-status bit definitions.
- Debug port control/status, PID, toggle, device address, and endpoint bit definitions.

Role:
- Header-only hardware contract consumed by EHCI controller/debug-port code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/portusbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/print.c

Small formatting support file.

Functions:
- `_fmtlock`: acquires a static formatting lock.
- `_fmtunlock`: releases the formatting lock.
- `_efgfmt`: placeholder formatter returning `-1`.

Role:
- Provides lock hooks for the Plan 9 formatting library in kernel context.
- `_efgfmt` disables or stubs floating-point format handling in this port context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/proc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/proc.c

Implements the core portable process scheduler, sleep/wakeup, process allocation, exit/wait, notes, and process diagnostics.

Scheduler:
- Uses priority queues `runq[Nrq]` with bitmap `runvec`.
- `schedinit` handles returning from a process to the scheduler and freeing moribund processes.
- `sched` context-switches between `up` and `m->sched`, respects delayed scheduling while locks are held, and switches MMU state.
- `ready`, `queueproc`, `dequeueproc`, and `runproc` manage runnable processes with affinity and wired-CPU constraints.
- `hzsched`, `preempted`, `yield`, and `rebalance` handle periodic/preemptive/cooperative scheduling.
- `updatecpu` and `reprioritize` implement decaying CPU accounting and fair-share priority adjustment.
- EDF hooks are integrated through `edfready`, `edfrun`, `edfrecord`, and `edfstop`.

Process lifecycle:
- `procinit0` allocates the process arena.
- `newproc` initializes a fresh `Proc`, pid/note ids, kernel stack, identity strings, scheduling fields, and default state.
- `pexit` tears down fd/env/rendez/name groups, dot channel, segments, wait records, debuggers, pid hash, and finally enters `Moribund`.
- `pwait` waits for child exit records.
- `kproc` creates kernel processes inheriting selected state from `up`.

Sleep/notes:
- `sleep` atomically links a process to a `Rendez`, tests the condition, and switches to scheduler.
- `wakeup` readies a sleeping process and validates rendezvous state.
- `tsleep` layers relative timers over `sleep`.
- `postnote` queues notes, wakes sleeping processes, and pulls processes out of `Rendezvous` state.
- `procctl` handles `/proc` controls: stop, trace, exit, and insufficient-memory exit.

Diagnostics and support:
- `dumpaproc`, `procdump`, `scheddump`, `procflushseg`.
- `noprocpanic` dumps processes and exits on process exhaustion unless configured otherwise.
- `error`, `nexterror`, and `exhausted` implement kernel error unwinding helpers.
- `killbig` selects and kills a large process under memory pressure.
- `renameuser`, `accounttime`, `procindex`, pid hash helpers.

Cautions:
- Many routines require high interrupt priority or precise lock ordering.
- `sched` intentionally delays rescheduling while locks are held, except for moribund paths and critical allocator locks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/qio.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/qio.c

Implements Plan 9 kernel I/O queues and block-list utilities.

Block utilities:
- `freeblist`, `padblock`, `blocklen`, `blockalloclen`, `concatblock`, `pullupblock`, `pullupqueue`, `trimblock`, `copyblock`, `adjustblock`, `pullblock`, `packblock`.
- `bl2mem` and `mem2bl` convert between memory buffers and block chains.
- Maintains optional debug/stat counters for block transformations.

Queue model:
- `Queue` stores block chains, byte/accounting limits, state bits, read/write locks, rendezvous points, kick/bypass callbacks, and close error text.
- `qopen` creates a normal queue; `qbypass` creates a bypass queue.
- `qread`/`qbread` block until data or close; `qwrite`/`qbwrite` queue data with flow control.
- Interrupt-safe APIs include `qproduce`, `qconsume`, `qpass`, `qpassnolim`, and `qiwrite`.
- `qget`, `qdiscard`, `qcopy`, `qremove`, `qputback`, and `qaddlist` operate on queued blocks.
- `qclose`, `qhangup`, `qreopen`, `qflush`, `qfree` manage lifecycle.
- `qlen`, `qwindow`, `qcanread`, `qfull`, `qisclosed`, `qsetlimit`, and `qnoblock` expose queue state.

Important behavior:
- Message queues preserve message boundaries; byte queues may split and put back partial blocks.
- Flow control wakes writers when queue length falls below thresholds.
- `qbwrite` queues data before sleeping for flow control so notes do not interrupt already-committed writes.
- `qiwrite` is designed for printing from high priority or non-process contexts and drops data above a hard print-buffer threshold.
- `qclose` discards queued blocks; `qhangup` marks closed but preserves queued data.

Role:
- Shared substrate for devices, network input queues, pipes, consoles, and kernel print queues.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/qio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/qlock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/qlock.c

Implements sleepable queued locks and reader/writer locks.

QLock:
- `qlock` acquires immediately if unlocked, otherwise enqueues `up` on FIFO wait queue and schedules away.
- `canqlock` attempts nonblocking acquisition.
- `qunlock` wakes the next queued process or clears the locked state.
- Tracks holder PC in `qpc` for diagnostics.

RWlock:
- `rlock` grants readers when no writer and no waiting queue; otherwise queues as `QueueingR`.
- `runlock` decrements readers and wakes a waiting writer when the last reader exits.
- `wlock` grants writer when no readers/writer; otherwise queues as `QueueingW`.
- `wunlock` prefers a queued writer; otherwise wakes all leading queued readers.
- `canrlock` is a nonblocking reader acquisition that fails if any writer is active or queued.

Diagnostics:
- `rwstats` counts lock acquisitions and queueing.
- `qlock` warns if called while interrupt locks or spin locks are held.

Role:
- Sleepable synchronization primitive used throughout process, namespace, queue, and VM code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/qlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/random.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/random.c

Implements a kernel random-byte source based on timing jitter.

Mechanism:
- `randominit` registers `randomclock` as a periodic clock callback every 13 ms and starts a `genrandom` kernel process.
- `genrandom` busy-counts in `rb.randomcount`, yielding when higher priority work exists and sleeping when the ring buffer is full.
- `randomclock` samples `randomcount`, folds bits into `rb.bits`, and emits a byte into a 1024-byte circular buffer after four 2-bit samples.
- `randomread` consumes bytes from the ring, waking the producer when empty/full transitions occur, and mixes output through a cheap LCG-style update to obscure synchronized clock cycles.

State:
- `rb` contains `QLock`, producer/consumer rendezvous points, ring pointers, entropy counters, and PRNG accumulator.

Role:
- Provides random bytes to kernel consumers, likely exposed by a device elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/random.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/rdb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/rdb.c

Implements a minimal serial remote debugger.

Behavior:
- `rdb` raises interrupt priority, prints `rdb...`, and calls `talkrdb` with a captured `Ureg`.
- `talkrdb` disables serial console output queues, prints `Edebugger reset`, then reads line-oriented commands from `uartgetc`.
- Command `r<hexaddr>` reads 4 bytes at an address and replies with `R<addr> <b0> <b1> <b2> <b3>`.
- Command `w<hexaddr> <hexvalue>` writes a word and replies `W`.
- Addresses below `sizeof(Ureg)` are interpreted as offsets into the saved register frame; otherwise as absolute addresses.
- Unknown commands return `Eunknown message`.

Role:
- Tiny low-level debugging endpoint for memory/register inspection and modification over UART.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/rdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/rebootcmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/rebootcmd.c

Loads a new kernel/program image and invokes the platform reboot hook.

Key functions:
- `readn` repeatedly reads exact byte counts from a channel, advancing `c->offset`.
- `readelfhdr` parses 32-bit ELF headers and extracts entry/text/data sizes.
- `readelf64hdr` does the same for 64-bit ELF headers.
- `setbootcmd` quotes remaining argv into the `bootcmd` kernel environment variable.
- `rebootcmd` opens the requested executable, recognizes a.out or ELF, reads text/data into a contiguous buffer, sets `bootfile` and `bootcmd`, and calls `reboot(entry, image, size)`.

Important behavior:
- Supports optional architecture-specific `parseboothdr`.
- Rounds text placement to page boundary before appending data.
- `argc == 0` exits immediately.
- Panics if `reboot` returns.

Role:
- Portable part of kernel reboot-from-file command handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/rebootcmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sd.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/sd.h

Defines the generic Plan 9 storage-device framework.

Core structures:
- `SDperm`: name/user/permission triple.
- `SDpart`: partition start/end, permissions, validity, version.
- `SDunit`: a unit/LUN with inquiry/sense data, geometry, partitions, raw request state, and permissions.
- `SDev`: controller/device instance with interface, controller private data, unit array, and enable state.
- `SDifc`: controller method table: probe, enable/disable, verify, online, raw I/O, control read/write, block I/O, clear, top-level control.
- `SDreq`: SCSI-like request with command bytes, data buffer, status, transfer length, and sense data.
- `SDio`: host-controller interface for MMC/SD/SDIO.

Constants:
- SCSI inquiry bits and peripheral type values.
- SD status codes, retry/malloc/timeout values, `SDmaxio`, and default partition count.
- Default `sdmalloc`/`sdfree` wrappers, overridable for DMA alignment.

Exports:
- Device registry helpers from `devsd.c`.
- SCSI helpers from `sdscsi.c`.

Role:
- Common storage abstraction used by AoE, MMC, SCSI, and device-layer storage code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sdaoe.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/sdaoe.c

Implements an `sd` interface for ATA-over-Ethernet devices exposed through Plan 9 AoE paths.

Main model:
- `Ctlr` tracks AoE path, data channel, version/media-change flags, feature bits, SMART state, geometry, serial/firmware/model strings, and raw identify data.
- Controllers are kept in a global linked list protected by `ctlrlock`.
- `SDifc sdaoeifc` exports AoE as a storage interface named `"aoe"`.

Key behavior:
- `aoepnp` reads `aoedev` config entries and creates placeholder `SDev` instances.
- `pnpprobe` and `aoeprobe` issue `discover` to the AoE control file, wait for an `ident` file to appear, and create/link a controller.
- `aoeidentify` reads `<path>/ident`, parses ATA identify data, fills SD inquiry model fields, and updates geometry/version on media changes.
- `aoeonline` connects `<path>/data`, refreshes identity, and sets `SDunit` geometry; ATAPI path can delegate online handling to SCSI.
- `aoerio` handles SCSI-like read/write commands by translating command LBA/count into reads/writes on the AoE data channel.
- `sdfakescsi` handles generic fake SCSI requests before direct read/write translation.
- `aoerctl` reports model, serial, firmware, SMART, feature flags, and geometry.
- `aoeprobew`, `aoeclear`, `aoertopctl`, and `aoewtopctl` support dynamic probing and top-level control.

Cautions:
- `delctlr` loop advances with `x = c->next` instead of `x = x->next`; this looks suspicious and could break traversal if not intentional.
- Some ATAPI and cache-flush paths are stubbed or commented out.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sdaoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sdmmc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/sdmmc.c

Implements an `sd` interface for a single MMC/SD memory card over a platform-provided `SDio` host controller.

Key responsibilities:
- `mmcpnp` initializes the `sdio` host and creates one `SDev`/`Ctlr`.
- `mmcverify` fills basic inquiry data using `SDio.inquiry`.
- `mmcenable` invokes the host enable hook.
- `mmconline` initializes the card: idle, SD 2.0 voltage check, operating-condition polling, CID/RCA/CSD reads, capacity identification, card select, block length, and 4-bit bus width.
- `identify` decodes CSD v1/v2 capacity and sector size, normalizing 1024-byte sectors to 512-byte sectors.
- `mmcrctl` reports RCA/OCR/CID/CSD and geometry.
- `mmcbio` performs block reads/writes through `SDio.iosetup`, `SDio.cmd`, and `SDio.io`, using multi-block commands when enabled.
- `mmcrio` is a stub returning `-1`.

Important behavior:
- SDHC/SDXC addressing is selected via OCR `Ccs`: block number for high-capacity cards, byte offset for older cards.
- Multi-block I/O retries setup errors up to three times and sends `STOP_TRANSMISSION`.
- Assumes exactly one card on the bus.

Role:
- Portable MMC/SD storage bridge into the generic `sd` framework.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sdmmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sdscsi.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/sdscsi.c

Provides SCSI helper logic for `sd` storage drivers.

Key functions:
- `scsiverify`: sends INQUIRY, performs TEST UNIT READY retries, and may issue START STOP UNIT for direct-access disks.
- `scsirio`: wraps device `rio` and interprets sense data into failure/ok/no-medium/retry-style outcomes.
- `scsionline`: sends READ CAPACITY, handles retries and not-ready cases, sets unit sectors/secsize, and normalizes 2352-byte ATAPI CD blocks to 2048.
- `scsiexec`: executes an arbitrary SCSI command through the controller `rio`.
- `scsibio`: formats READ/WRITE(10) or READ/WRITE(16), issues the request, handles recovered errors/media changes/not-ready retries, and returns bytes transferred.
- `scsifmt10` and `scsifmt16` construct SCSI CDBs.

Important behavior:
- `scsiverify` tolerates `SDcheck` in some conditions as a valid detected device.
- Removable media changes clear `unit->sectors` to force a later online check.
- 16-byte commands are used for block numbers >= 2^32.

Role:
- Shared SCSI command and retry layer used by storage drivers with SCSI-like command transport.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sdscsi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/segment.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/segment.c

Implements user memory segment management and executable image caching.

Segment management:
- `initseg` initializes the image cache/free lists.
- `newseg` allocates a `Segment`, chooses inline or heap PTE map storage, and initializes semaphore list state.
- `putseg` decrements references, detaches image relationships, frees PTEs/profile/map, and releases the segment.
- `dupseg` implements rfork/fork segment duplication: text/shared/physical share; stack copies; BSS/data copy-on-write unless memory is shared.
- `data2txt` is referenced externally in `portfns.h`; this file handles the `segno == TSEG` conversion path through that helper.
- `segpage` installs a page in the right PTE slot.
- `relocateseg` adjusts page virtual addresses after stack relocation.

Image cache:
- `attachimage` finds or creates an `Image` keyed by qids/mount channel/type and attaches or creates a text segment.
- `putimage` drops image references, removes from hash, and defers channel closes into `freechan`.
- `imagereclaim` uncaches image-backed free-list pages to free image structures.
- `imagechanreclaim` closes deferred image channels outside spin locks.

Address-space operations:
- `ibrk` grows/shrinks a segment, checking overlap and resizing PTE maps.
- `mfreeseg` removes PTEs over a range, delays actual `putpage` until after TLB flush for shared segments.
- `isoverlap` detects address overlap.
- `segattach` attaches named physical/shared/memory segments, choosing an address hole when `va == 0`.
- `addphysseg` and `isphysseg` manage attachable physical segment types.

Other:
- `syssegflush` marks pages for text-cache flush and flushes MMU.
- `segclock` updates text segment profiling counters.

Cautions:
- `putimage` defers channel close because close can block and must not happen under spin locks.
- `segattach` excludes `ESEG` and protects the zero page by rejecting/avoiding `va == 0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/swap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/swap.c

Implements swap-slot allocation and the pager daemon.

Swap allocation:
- `swapinit` allocates the swap reference map and page I/O list; initializes `swapimage.notext`.
- `newswap` finds a free swap slot, marks it referenced, and returns disk address.
- `putswap`, `dupswap`, and `swapcount` maintain per-slot reference counts.
- `setswapchan` installs the swap channel, optionally shrinking configured swap to file/partition size.
- `swapfull` reports when free swap falls below 10%.

Pager:
- `kickpager` starts or wakes the `pager` kproc.
- `pager` sleeps until memory pressure, then scans processes/segments, pages out eligible pages, or kills a large process if no swap channel exists.
- `needpages` compares `palloc.freecount` with `swapalloc.headroom`.
- `canflush` verifies all processes sharing a segment can flush TLBs before paging.
- `pageout` scans PTEs, uses reference-generation aging, and calls `pagepte`.
- `pagepte` drops text pages back to demand-load or assigns swap addresses for data/BSS/stack/shared pages, caching pages under `swapimage` while I/O is pending.
- `executeio` sorts pages by swap address and writes them to the swap channel in batches.
- `pagersummary` reports memory/swap/iolist counts.

Important behavior:
- Text pages are discarded rather than written to swap.
- Dirty anonymous/shared pages are written to swap and represented in PTEs as `daddr|PG_ONSWAP`.
- A page is temporarily refcounted while being written to prevent reuse.
- Page aging uses `genclock`, `genage`, and `PG_REF` clearing.

Role:
- Memory-pressure backstop for the Plan 9 VM system.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/syscallfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/syscallfmt.c

Formats syscall entry and return traces.

Entry formatting:
- `syscallfmt` builds a string in `up->syscalltrace` containing pid, process text, syscall name/number, PC, and decoded arguments.
- Handles strings, argv arrays, fd/path/stat buffers, read/write buffers, offsets, segment operations, mount/bind arguments, semaphores, rendezvous, and time calls.
- `fmtuserstring` validates and copies a user NUL-terminated string.
- `fmtrwdata` validates and formats up to a bounded data buffer as printable ASCII with non-printables replaced by `.`.

Return formatting:
- `sysretfmt` formats return values, output buffers for read/errstr/await/fd2path, error string, and start/stop timestamps.
- For failed calls, it uses `up->syserrstr`.

Important behavior:
- Frees any previous `up->syscalltrace` before replacing it.
- Uses `validaddr`, `validalign`, and `vmemchr`, so tracing itself touches user memory and can raise kernel errors if invalid.
- Write data and read data are capped at 64 bytes in trace output.

Role:
- Debug/tracing support for Plan 9 syscalls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/syscallfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sysfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/sysfile.c

Implements file, fd, directory, mount, and stat-related syscalls.

File descriptor management:
- `growfd`, `findfreefd`, `newfd`, `newfd2`, `fdtochan`, `fdclose`, `sysdup`, `sysclose`, `sysfd2path`.
- Enforces mode checks, close-on-exec flags, and descriptor-table growth in `DELTAFD` chunks with a hard practical cap.

Open/create/pipe:
- `sysopen`, `syscreate`, `syspipe`.
- `openmode` validates and normalizes Plan 9 open modes.

Read/write:
- Internal `read` supports normal read and pread-style fixed offset.
- Internal `write` supports normal write and pwrite-style fixed offset.
- `sys_read`, `syspread`, `sys_write`, `syspwrite` expose old and pread/pwrite variants.
- Directory reads are postprocessed through union reads and mount rewriting.

Directory/mount rewriting:
- `unionread` reads across union mount chains.
- `unionrewind`, `mountrewind`, `mountrock`, and `mountrockread` preserve directory-entry continuity when mount rewriting changes entry sizes.
- `mountfix` replaces directory entries corresponding to current mount points with stat data for mounted targets while preserving original names.

Seek/stat/wstat:
- `sysseek` and `sysoseek` implement 64-bit and old seek.
- `validstat` checks stat buffer structure and validates names.
- `sysstat`, `sysfstat`, `syswstat`, `sysfwstat`.
- Old compatibility calls `sys_stat`, `sys_fstat`, `sys_wstat`, `sys_fwstat` convert or reject old formats.

Namespace operations:
- `bindmount` implements both bind and mount common logic.
- `sysbind`, `sysmount`, `sys_mount`, `sysunmount`.
- Mounting uses devmnt attach with channel/auth/spec metadata.
- Removing or renaming mount points is disallowed to avoid ambiguity.

Other:
- `syschdir` replaces `up->dot`.
- `sysremove` handles remove semantics where remove clunks the fid, then neutralizes channel close.

Role:
- Core Plan 9 syscall bridge between fd/name APIs and device `Dev` methods.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sysproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/sysproc.c

Implements process, exec, memory, synchronization, wait, note, and time syscalls.

Process creation:
- `sysrfork` validates rfork flags, supports in-place group changes when `RFPROC` is absent, and creates child processes when present.
- Duplicates or shares memory, fd, namespace, rendezvous, and environment groups based on flags.
- Builds child return frame through `forkchild`, copies identity/debug/note state, inherits priority/wiring, and readies the child.

Exec:
- `sysexec` opens an executable, supports a.out and `#!` script indirection, validates text/entry/layout, counts/copies argv, creates a temporary stack, commits new text/data/BSS/stack segments, closes `CCEXEC` fds, attaches shared text image, resets notify/debug state, flushes MMU, and returns through `execregs`.
- `shargs` parses interpreter lines.

Exit/wait/error/notify:
- `sysexits` validates/caps exit status and calls `pexit`.
- `sys_wait` returns old wait format.
- `sysawait` returns modern formatted wait text.
- `werrstr`, `generrstr`, `syserrstr`, and old `sys_errstr` swap user/kernel error strings.
- `sysnotify` installs a notify handler; `sysnoted` validates note return protocol.

Memory syscalls:
- `syssegbrk`, `syssegattach`, `syssegdetach`, `syssegfree`, and compatibility `sysbrk_`.
- Detach rejects the initial stack segment and flushes MMU after removing mappings.

Rendezvous and semaphores:
- `sysrendezvous` matches waiters by tag in the current `Rgrp`, otherwise sleeps in `Rendezvous` state.
- Semaphore implementation uses `Sema` nodes in the owning `Segment`, compare-and-swap on user memory, explicit wait-list locking, and careful wakeup passing.
- `syssemacquire`, `systsemacquire`, and `syssemrelease` expose blocking, timed, and release operations.

Time and misc:
- `syssleep` yields for nonpositive sleep, otherwise sleeps at least one tick.
- `sysalarm` delegates to `procalarm`.
- `sysnsec` writes `todget(nil)` to user memory.
- `sysr1` invokes `checkpagerefs` for diagnostics.
- `l2be` converts old executable header fields.

Cautions:
- The semaphore block has extensive race documentation; it depends on `cmpswap`, `coherence`, and strict wakeup handoff.
- `sysexec` commits in phases with nested error handlers; after commit, old memory/fds may already be released.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/sysproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/systab.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/systab.h

Defines the syscall dispatch table and syscall-name table.

Contents:
- `typedef long Syscall(ulong*)`.
- Forward declarations for each syscall handler.
- `systab[]`: indexed by syscall numbers from `/sys/src/libc/9syscall/sys.h`, mapping to handler functions.
- `sysctab[]`: matching syscall name strings used by tracing/debug formatting.
- `nsyscall`: number of entries in `systab`.

Coverage:
- Includes current syscalls such as `Open`, `Read`, `Pread`, `Pwrite`, `Mount`, `Await`, `Tsemacquire`, `Nsec`.
- Includes deprecated/compatibility syscalls with leading underscores: `_errstr`, `_fsession`, `_fstat`, `_mount`, `_read`, `_stat`, `_write`, `_wstat`, `_fwstat`, `_wait`.

Role:
- Central portable dispatch metadata consumed by syscall entry code and `syscallfmt.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/systab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/taslock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/taslock.c

Implements low-level spin locks, interrupt locks, and reference count atomics.

Spin locks:
- `lock` uses `tas` to acquire, increments `up->nlocks` to prevent scheduling, records holder PC/proc, and spins with diagnostics on long contention.
- `canlock` attempts nonblocking acquisition.
- `unlock` validates state, clears the lock, performs coherence, decrements `up->nlocks`, and calls `sched` if a delayed reschedule is pending at low interrupt level.

Interrupt locks:
- `ilock` raises priority with `splhi`, spins, records saved status register, holder PC/proc/Mach, and increments `m->ilockdepth`.
- `iunlock` validates interrupt-lock state, clears lock, decrements `ilockdepth`, clears `lastilock`, and restores priority with `splx`.

Reference helpers:
- `incref`/`decref` are implemented via static `inccnt`/`deccnt` around architecture atomics `_xinc`/`_xdec` in this file’s local helpers.
- `deccnt` panics if a reference count goes negative.

Diagnostics:
- Tracks lock statistics and optional lock-cycle maxima under `LOCKCYCLES`.
- `lockloop` prints lock holder and current process data on prolonged spin.
- Detects common misuse such as unlocking an `ilock` with `unlock`, `iunlock` while low, or unlocking from a different `up`.

Role:
- Foundational synchronization layer under all higher-level locks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/taslock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/thwack.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/thwack.c

Implements the Thwack LZ77/Huffman-style compressor.

Core structures and constants:
- Uses `Thwack`, `ThwBlock`, and constants from `thwack.h`.
- Local `Huff` table `lentab` encodes short match lengths.
- Maintains an encoder window of acknowledged blocks and per-block hash tables.

Key functions:
- `thwackinit` clears compressor state and initializes block data/hash pointers.
- `thwackack` marks a block sequence and selected predecessor blocks as acknowledged for future history use.
- `thwmatch` searches current/history blocks for a match using hashed 3-byte sequences and returns an offset into history.
- `thwack` compresses one source block:
  - Adds source to the circular window.
  - Builds a history list from acknowledged recent blocks.
  - Writes sequence-delta and history mask prefix.
  - Emits literal codes or match length/offset codes.
  - Updates hash entries as source advances.
  - Aborts with `-1` if data is too small/large, output would not fit, or compression progress is poor.
  - Updates stats for input bytes, output bytes, literals, matches, offset bits, length bits, delay, and history.

Important behavior:
- Only acknowledged previous blocks are used as compression history, making it suitable for lossy/unreliable transport contexts where receiver history must be known.
- Hash uses Knuth-style multiplicative hashing over 3-byte values.
- Literal encoding adapts based on recent literal history to vary 8/9/10/11-bit forms.
- Match length uses fast table for short matches and expanding big-length encoding for longer ones.

Role:
- Portable compression helper, likely used by network or remote display/file protocols in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/thwack.c -->