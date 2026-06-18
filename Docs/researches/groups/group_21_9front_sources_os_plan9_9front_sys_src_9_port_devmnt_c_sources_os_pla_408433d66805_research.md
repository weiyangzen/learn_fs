# Group Research: group_21_9front_sources_os_plan9_9front_sys_src_9_port_devmnt_c_sources_os_pla_408433d66805

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devmnt.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devmnt.c

Purpose: Implements the Plan 9 `#M` mount/client device, multiplexing 9P RPCs over an underlying server channel and presenting remote fids as local `Chan`s.

Key logic:
- `mntversion` performs the one-time `Tversion`/`Rversion` negotiation, clamps `msize`, installs `c->mux`, marks the channel `CMSG`, creates the input queue, and records the negotiated 9P version.
- `mntauth` and `mntattach` allocate local mount channels/fids, issue `Tauth`/`Tattach`, and bind returned qids to the server channel via `mchan`.
- Walk, stat, open/create, clunk/remove, wstat, read, write, bread, and bwrite are encoded as 9P requests through `Mntrpc`.
- `mountio`, `mntrpcread`, and `mountmux` serialize the transport reader while allowing multiple pending tags; replies are matched by tag and wake the owning RPC.
- `mntrdwr` chunks I/O by `c->iounit`, integrates with optional `CCACHE`, and fixes directory stat dev/type fields through `mntdirfix`.
- 9front adds deferred mount workers and `Mntrah` read-ahead support through `mntdefer`, `mntproc`, `rahproc`, and `mntrahread`.

Dependencies and integration:
- Depends on 9P `Fcall` conversion, `Queue` block I/O, channel refcounting/lifetime rules, cache helpers, and the generic Plan 9 `Dev` interface.

Risks and notes:
- Interrupt handling is subtle: interrupted RPCs allocate chained `Tflush` requests and then reconcile or abandon clunk/remove fids.
- `Mnt` lifetime is tied to the server channel refcount rather than a standalone `Mnt` refcount.
- Tag allocation excludes tag 0 and `NOTAG`; failed cleanup can strand pending requests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devmnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devmouse.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devmouse.c

Purpose: Implements the `#m` mouse device, exposing `cursor`, `mouse`, `mousein`, and `mousectl` for cursor shape, event reads, injected input, and control.

Key logic:
- Maintains global `Mouseinfo` state with current position/buttons, read counters, resize state, a button-change event ring, and redraw rendezvous.
- `mouseinit` installs the default arrow cursor and starts a redraw kernel process when a monitor exists.
- `mouseread` returns binary cursor data, formatted mouse events (`m`/`r` records), or injected-current state from `mousein`.
- `mousewrite` accepts cursor updates, absolute/scaled/relative injected events, absolute moves through `mouse`, and `mousectl` commands.
- `mousectl` supports button-map changes, button swapping, scroll swapping, screen blanking, blank timeout, and driver-specific wildcard controls.
- `mousetrack`, `absmousetrack`, and `scmousetrack` update state, clamp to screen bounds, queue button events, wake readers, and schedule redraw.
- Serial protocol helpers parse Microsoft 3-byte, IntelliMouse 4-byte wheel, and Logitech 5-byte mouse byte streams.

Dependencies and integration:
- Uses draw/screen globals (`gscreen`, `drawlock`, `cursoroff/on`, `setcursor`, `blankscreen`), queues for serial input callbacks, and Plan 9 device helpers.

Risks and notes:
- `/dev/mouse` is single-open; `/dev/mousein` is eve-only and has per-open injected button state.
- Button and scroll remapping affects only the user-visible event encoding, not raw internal button state.
- Screen blanking is tied to mouse inactivity and read wakeups.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devmouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devpci.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devpci.c

Purpose: Provides a stripped-down PCI-only `#$` device for enumerating PCI devices and reading/writing PCI configuration space.

Key logic:
- Exposes top directory `pci`, then per-device `bus.dev.fnctl` and `bus.dev.fnraw` files.
- `pcidirgen` enumerates PCI devices with `pcimatch` and resolves qids back to devices with `pcimatchtbdf`.
- `ctl` reads summarize class codes, vendor/device IDs, interrupt line, and populated BARs.
- `raw` reads and writes the first 256 bytes of PCI config space, using aligned 32-bit/16-bit accesses when possible and byte accesses otherwise.

Dependencies and integration:
- Depends on `../port/pci.h`, `Pcidev`, `pcimatch`, `pcimatchtbdf`, `pcicfgr*`, and `pcicfgw*`.

Risks and notes:
- Raw writes directly mutate PCI config registers and are exposed with `0660` permissions.
- This file intentionally duplicates only the PCI subset of the larger ISA PNP plus PCI device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devpci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devpipe.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devpipe.c

Purpose: Implements `#|`, Plan 9 kernel pipes with two queue-backed endpoints, `data` and `data1`.

Key logic:
- `pipeattach` allocates a `Pipe`, two queues, and a unique qid namespace.
- `pipeopen` tracks per-end open counts and sets `iounit` to `qiomaxatomic`.
- Reads from one endpoint drain that endpoint’s queue; writes to one endpoint enqueue into the opposite queue.
- Closing the final open on either endpoint hangs up the opposite side and closes its own queue; when both sides close, queues are reopened for reuse.
- `pipewstat` uses the stat length field to set both queue limits, bounded by `conf.pipeqsize`.

Dependencies and integration:
- Uses Plan 9 `Queue` primitives (`qread`, `qwrite`, `qbread`, `qbwrite`, `qhangup`, `qclose`, `qreopen`) and net-style qid packing macros.

Risks and notes:
- Writes to a closed pipe post a user note unless the channel is marked `CMSG`, avoiding notes for mounted queues.
- Pipe queue size is rounded up to a multiple of the maximum atomic queue I/O unit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devpipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devpnp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devpnp.c

Purpose: Implements `#$` for ISA Plug-and-Play discovery plus PCI configuration-space access.

Key logic:
- ISA PNP support sends the initiation key, runs serial isolation, assigns CSNs, reads resource data, and exposes `csnNctl`/`csnNraw`.
- Boot-time `pnpN=` configuration strings can predefine card IDs and optional config strings before scanning.
- `pnp/ctl` reports enabled/disabled state and accepts `port` to scan an ISA PNP read-data port plus `debug`.
- PCI directory support mirrors `devpci.c`: per-device `ctl` summaries and `raw` 256-byte config-space access.
- `QID` packs card/device identity and file type; `CSN` extracts ISA card numbers.

Dependencies and integration:
- Uses low-level I/O port access (`inb`, `outb`), ISA config parsing, PCI helpers, and Plan 9 directory generation.

Risks and notes:
- ISA PNP resource configuration is stubbed through `wrconfig`, which currently accepts commands without implementing real resource programming.
- PCI raw writes are direct hardware config writes.
- The file mixes old ISA PNP hardware probing with generic PCI config exposure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devpnp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devproc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devproc.c

Purpose: Implements `#p`, the Plan 9 process filesystem for inspecting and controlling processes.

Key logic:
- Root lists `trace` plus one directory per live process; process qids encode file type, process table slot, and pid/version for stale-channel detection.
- Per-process files expose args, ctl, fd, namespace, memory, notes, note groups, registers, fp registers, status, text, wait records, profile data, syscall traces, and watchpoints.
- `procopen` enforces permissions, handles special `/proc/trace`, protects kernel processes/private memory, and redirects `text` opens to the text image channel.
- `procread` implements status formatting, namespace and fd reconstruction, wait queue consumption, note consumption, user memory reads through `segio`, and privileged kernel memory reads.
- `procwrite` updates args, writes stopped-process memory/registers/fpregs, posts notes, changes note ids, writes watchpoints, and dispatches ctl commands.
- `procctlreq` handles process control: kill, stop/start/startstop/startsyscall, waitstop, priority, wired CPU, private memory, profiling, interrupt flags, fd closing, tracing, and EDF real-time parameters.
- Watchpoint support parses textual `rwx addr len` rows and delegates validation/programming to architecture-specific `setupwatchpts`.

Dependencies and integration:
- Integrates with process tables, segment/page VM, note delivery, fd and namespace groups, scheduler priority/EDF code, tracing, `Segio`, architecture register helpers, and pool secrecy checks.

Risks and notes:
- Permission rules are intentionally uneven: debugging-readable files such as `fd`, `ns`, and `status` remain broadly readable.
- Memory writes require the target to be stopped and can convert text to data via `txt2data`.
- `/proc/trace` is eve-only and single-open; it uses a ring of `Traceevent` records.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devroot.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devroot.c

Purpose: Implements the synthetic root device `#/`, including fixed root directories and boot-file storage.

Key logic:
- Maintains two bounded `Dirlist`s: root entries and `/boot` entries.
- `rootreset` adds standard root directories including `bin`, `dev`, `env`, `fd`, `mnt`, `net`, `proc`, `srv`, and 9front’s `shr`.
- `addbootfile` adds immutable boot files under `/boot`.
- `rootgen`, `rootwalk`, `rootstat`, and `rootread` serve directory entries and file contents from in-memory tables.
- Writes always fail; removal/wstat use default device rejection.

Dependencies and integration:
- Used early by the kernel namespace and boot process; external boot code calls `addbootfile`.

Risks and notes:
- Entry arrays are fixed at 32 root files and 32 boot files; overflow panics.
- Boot file contents are served by pointer without copying in `addbootfile`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsd.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devsd.c

Purpose: Implements the generic storage device server `#S`, exposing storage controllers, units, partitions, control files, raw command files, and driver-added extra files.

Key logic:
- Registers `SDev` controller chains from `sdifc[]`, assigns device letters, lazily enables controllers, verifies units, and creates unit directories.
- Partitions are versioned `SDpart` entries; `sdinitpart` resets stale geometry, calls driver `online`, creates default `data`, and imports boot-configured `sdXpart=` partitions.
- Directory generation exposes top `sdctl`, unit `ctl`, exclusive `raw`, valid partition files, and extra driver files.
- `sdbio` maps partition byte I/O to sector-aligned driver `bio` calls, including bounds checks, removable-media locking, media-change retry, and read-modify-write for unaligned writes.
- `raw` implements a command/data/status state machine for SCSI CDBs and sneaky ATA commands.
- `sdrio`, `sdsetsense`, `sdfakescsi`, and `sdfakescsirw` provide raw command dispatch and SCSI emulation for non-SCSI devices.
- `sdwrite` handles top-level controller commands, legacy `config`, partition creation/deletion, unit driver controls, raw command phases, and partition writes.
- `sdconfig`, `configure`, `unconfigure`, `sdaddfile`, `sdshutdown`, and `sdannexctlr` manage dynamic controller lifetime and driver integration.

Dependencies and integration:
- Depends on `../port/sd.h`, driver callbacks in `SDifc`, `DevConf`, storage allocation helpers, and Plan 9 device/path conventions.

Risks and notes:
- Partition qid versions combine unit and partition versions, so stale opens fail with `Echange`.
- Raw command access is exclusive and stateful; incorrect phase ordering returns errors or resets the state.
- Dynamic unconfigure refuses busy controllers and must disable/clear hardware before freeing controller structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsdp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devsdp.c

Purpose: Implements `#E`, the Secure Datagram Protocol device, providing encrypted/authenticated/compressed datagram conversations over an underlying packet channel.

Key logic:
- Exposes per-instance `sdp`, `clone`, `log`, and per-conversation `ctl`, `data`, `control`, `status`, `stats`, and `rstats`.
- `sdpclone` allocates/reuses conversations, initializes permissions, state, refs, and sequence window state.
- `ctl` commands configure `accept`, `dial`, packet drop simulation, cipher, auth, compression, and per-direction secrets.
- Connection state machine handles open request/ack/ack-ack, close/close-ack, reset, retry, timeout, and keepalive.
- Packet format includes type/subtype, 24-bit sequence numbers with wrap/window tracking, optional auth, optional cipher padding/IV, and optional thwack compression.
- Reliable control channel keeps one outstanding control packet, retransmits by timer, ACKs with local stats, and refreshes remote stats.
- Data path reads underlying blocks, filters control traffic, returns data packets, and starts a background reader when the data file is closed.
- Algorithms include null/DES/RC4 ciphers, null/MD5/SHA1 auth declarations, implemented MD5 HMAC auth, and thwack compression.

Dependencies and integration:
- Uses `netif.h`, `Log`, `Block` I/O, `libsec` DES/RC4/MD5/SHA1 primitives, and `thwack` compression.

Risks and notes:
- Cryptographic algorithms are legacy: DES, RC4, MD5-HMAC, and SHA1-era naming.
- Sequence window is 32 packets; duplicates, reorders, missing packets, bad auth, and bad compression are counted.
- `shaauthinit` only clears auth state in this file; SHA auth is listed but not implemented here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsdp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsegment.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devsegment.c

Purpose: Implements `#g`, a global segment device for creating named VM segments, configuring their address/size, attaching them through `segattach`, and reading/writing segment memory.

Key logic:
- Maintains up to 100 `Globalseg` objects with name, owner, permissions, refcount, and `Segio` state.
- Top-level create makes a named segment directory; each segment directory exposes `ctl` and `data`.
- `ctl` accepts `va base length`, plus eve-only `fixed` and `sticky` variants.
- Normal segments use `newseg(SG_SHARED)`; sticky segments allocate and prefill pages; fixed segments allocate a physically contiguous run of user pages.
- `data` reads and writes memory through `segio`.
- `globalsegattach` is installed into `_globalsegattach` so normal VM attach logic can resolve named global segments.

Dependencies and integration:
- Uses VM `Segment`, `Page`, `Pte`, `newseg`, `segpage`, `putseg`, `Segio`, physical segment name checks, and page allocator internals.

Risks and notes:
- Fixed segments require contiguous free pages and are eve-only.
- Segment names must not collide with physical segment names.
- Removing a segment clears the global slot, but open refs keep the underlying object alive until close.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsegment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devshr.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devshr.c

Purpose: Implements `#σ` / `#σc`, a shared mount-table device for publishing named shared trees and mount points.

Key logic:
- `Shr` objects are named shared directories with an embedded `Mhead`; `Mpt` objects wrap `Mount` entries and hold owner/permission metadata.
- Attaching `#σ` exposes read/use view; attaching `#σc` exposes control view for creating/removing/renaming shared roots and mount points.
- Walking a shared root in normal view delegates remaining path walk into mounted channels in that shared mount list.
- Creating under `#σc` creates shared roots; creating under a controlled shared root creates named mount slots.
- Writing an fd to a mount slot attaches the fd through `mntattach` and installs the resulting channel as the mount target.
- Opening a mount-point file returns the posted mounted channel if mode-compatible.
- Read on normal shared roots uses `unionread` over the shared `Mhead`; read on control roots lists control entries.
- `shrrenameuser` updates owners across shared roots and mount points.

Dependencies and integration:
- Integrates directly with Plan 9 mount structures (`Mhead`, `Mount`), `createdir`, `mntattach`, `unionread`, and namespace permission checks.

Risks and notes:
- Creation and removal require `canmount`; `none` cannot create control entries.
- Mount target replacement closes the old backing channel after swapping under the mount lock.
- Permission behavior differs between normal and control views; normal shared roots mask write bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devshr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsrv.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devsrv.c

Purpose: Implements `#s`, the service registry for posting open channels by name so other processes can open them later.

Key logic:
- Uses `Srv` entries for posted channels and `Board` directories for hierarchical lease boards.
- Root board starts as `#s`; `clone` creates a lease board with a generated numeric name and qid type `Qlease`.
- Creating a file reserves a service name; writing an fd stores the referenced channel after rejecting auth files and duplicate posts.
- Opening a service replaces the registry channel with the posted channel after mode and permission checks.
- Closing a lease board marks it closed and closes all posted service channels under it.
- `srvremove` removes service entries owned by the caller or eve; `srvwstat` can rename/change owner/mode subject to conflict checks.
- `srvrenameuser` updates board and service owners globally.

Dependencies and integration:
- Uses `fdtochan`, channel refcounting, path service names, `RWLock`, and Plan 9 device generation.

Risks and notes:
- Posted channels must match requested mode unless they are `ORDWR`.
- Lease boards can persist with zero refs while children exist, then are pruned upward when closed and childless.
- `clone` is reserved and cannot be used as a service or board name.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devswap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devswap.c

Purpose: Implements swap management and the `#¶` swap device, including the pager daemon, swap-slot accounting, encrypted swapfile access, and swap statistics/control.

Key logic:
- `swapinit` allocates the swap reference map and pageout I/O list, initializes `swapalloc`, and starts `pager`.
- Swap slots are byte-refcounted in `swmap`; `newswap`, `putswap`, `dupswap`, and `swapcount` manage slot lifetime, including overflow handling with `xref`.
- `pager` first reclaims filesystem/image/swap cache pages, then pages out eligible process segments, or kills the largest eligible process when memory cannot be recovered.
- `pageout`, `canflush`, and `pagepte` age pages, ensure TLB flushability, allocate swap slots, replace PTEs with `PG_ONSWAP`, and stage pages for I/O.
- `executeio` writes staged pages to the swap image channel and drops the extra swap/page references.
- `swap` file reports memory, page size, kernel/user/swap/reclaim, and pool statistics; writes accept `start` or an fd selecting the backing swap channel.
- `swapfile` is eve-only `ORDWR`; reads decrypt and writes encrypt one page at a time using AES-XTS before delegating to the real swap channel.

Dependencies and integration:
- Integrates with VM page tables, image/cache reclaim, process/segment locks, page allocator state, `libsec` AES-XTS, and pool memory statistics.

Risks and notes:
- The backing swap channel cannot be changed while swap is in use.
- `swapfile` requires exact page-sized I/O and allocates per-open encryption state with random keys.
- Pager locking avoids waiting on segment locks to reduce deadlock risk.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devswap.c -->