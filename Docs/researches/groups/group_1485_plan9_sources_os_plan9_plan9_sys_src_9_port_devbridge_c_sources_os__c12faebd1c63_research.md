# Group Research: group_1485_plan9_sources_os_plan9_plan9_sys_src_9_port_devbridge_c_sources_os__c12faebd1c63

Scope checked against `Docs/research_subset_a.md`: these files are within `sources/os/plan9/plan9`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devbridge.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devbridge.c

Implements `#B`, an in-kernel IPv4 Ethernet bridge device with up to four bridge instances and 128 ports per bridge. The exposed namespace is `bridgeN/{ctl,stats,cache,log,<port>/ctl,<port>/local,<port>/status}`.

Key structures are `Bridge`, `Port`, and `Centry`. `Bridge` owns the port table, MAC-address cache, counters, delay settings, TCP MSS clamp flag, and log state. `Port` tracks bound ether/tunnel endpoints, reader process, owner hash, and packet statistics. `Centry` maps Ethernet addresses to bridge ports with expiry and hit counters.

Control operations on `ctl` include `bind ether|tunnel`, `unbind`, `cacheflush`, `set/clear tcpmss`, and `delay delay0 delayn`. Ether ports are opened through an underlying Ethernet clone/control/data path and placed into promiscuous bridge mode. Tunnel ports use separate read/write channels.

Packet flow is handled by a per-port `etherread` kernel process. It reads blocks, learns source MACs, optionally clamps TCP MSS in IPv4 TCP SYN packets, applies artificial delay, then either floods multicast/unknown traffic or forwards known unicast traffic using the cache. The cache avoids multicast/broadcast entries and expires entries after five minutes.

Tunnel output supports IPv4 fragmentation when packets exceed `TunnelMtu`, provided packets are IPv4 without IP options and not DF. `etherwrite` constructs Ethernet/IP fragments, updates IP length/fragment fields/checksums, and pads undersized Ethernet frames.

Dependencies include Plan 9 block I/O, `netif`, Ethernet/IP header definitions, `Log`, `kproc`, `namec`, and device-table dispatch. Main operational risks are all bridge state being protected by a single `QLock`, reader-process lifetime depending on notes during unbind, and low-level packet mutation/fragmentation requiring exact packet layout assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devbridge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devcap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devcap.c

Implements `#¤/cap`, a capability device for changing the current process user when a one-shot capability hash is presented. The namespace contains `capuse` for consumers and `caphash` for privileged capability insertion.

Capabilities are stored as SHA1-length hashes in a global `capalloc` list protected by `QLock`. `addcap` appends hashes and trims the list to `Maxhash` entries. `remcap` atomically removes a matching hash, making capabilities single-use.

Only `eve` may open/write `caphash`; `capremove` lets `eve` remove the `caphash` entry from the namespace. Writing at least `SHA1dlen` bytes to `caphash` registers a raw hash.

Writing to `capuse` expects `from[@to]@key`. The driver computes `hmac_sha1(from, key)` and consumes a matching registered hash. If `from@to` form is used, `from` must match `up->user`; the process user becomes `to`. Without an explicit source user, the same field is used as the target user.

This is small but security-sensitive code: authorization depends on one-shot hash secrecy, correct parsing around `@`, and privileged control of `caphash`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devcons.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devcons.c

Implements `#c`, the central console and miscellaneous kernel pseudo-device. The namespace includes console I/O (`cons`, `consctl`, `kprint`, `kmesg`), time (`time`, `bintime`), identity/configuration (`hostowner`, `hostdomain`, `sysname`, `user`, `config`, `osversion`), process ids, CPU/system stats, memory/swap stats, `random`, `null`, `zero`, `drivers`, and privileged reboot control.

Console output routes through `putstrn0`: it records messages in the `kmesg` ring buffer, sends to `/dev/kprint` if open, otherwise to screen output when available, and also to serial/UART output. `print`, `iprint`, `panic`, `sysfatal`, and `_assert` build on this path.

Keyboard input is staged at interrupt time into `kbd.istage`, drained by a periodic clock callback, echoed, and then processed into raw or line mode. `consctl` supports `rawon`, `rawoff`, `ctlpon`, and `ctlpoff`. The `^T ^T` escape path triggers debugging actions such as stack dump, process dump, scheduler dump, memory summaries, reboot, and toggling `consdebug`.

`consread` provides formatted views of CPU time, process IDs, system stats, swap/memory status, driver table, kernel config, and time. Reads of `cons` block until line-mode input is available unless raw mode changes flushing behavior. `kprint` is exclusive and uses a queue for kernel output capture.

`conswrite` handles console output, time setting by `eve`, host/user writes via external helpers, reboot/halt/panic commands, sysstat counter reset, swap channel setup, pager start, and sysname update. Time support includes text and binary little-endian formats with fast tick frequency management.

Dependencies span keyboard queues, UART/screen hooks, random/tod APIs, pager/swap, reboot, process structures, and pool stats. This file is a high-centrality kernel device with broad side effects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devdraw.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devdraw.c

Implements `#i/draw`, the in-kernel Plan 9 draw protocol server. It exposes a top-level `draw` directory, `winname`, `new`, per-client directories, and per-client `colormap`, `ctl`, `data`, and `refresh` files.

Core state is in `Draw`, `Client`, `DImage`, `DScreen`, `CScreen`, `DName`, and `Refresh`. `Draw` tracks clients, named images, screen state, blanking state, and saved colormap. `Client` tracks image hash buckets, screens, refresh queue, pending read data, protocol op, and client id. `DImage` wraps `Memimage` with ids, refcounts, font metadata, screen/layer ownership, and optional name inheritance.

Opening `new` allocates a client and returns its `ctl`. Opening `ctl` installs display image id `0` as a named screen image reference. Closing the last client reference frees refresh records, names, screens, images, and flushes the display.

The binary command interpreter in `drawmesg` handles image allocation, screen allocation/use, clipping/repl changes, drawing, ellipses/arcs, lines, polygons, strings/string background, font initialization/loading, named images, window origin/top/bottom ordering, image read/write including compressed writes, freeing resources, and explicit flush. It dispatches to `memdraw`, `memlayer`, and `memimage` primitives.

`drawread` returns image info from `ctl`, colormap text, queued image data from read commands, and refresh rectangles. `drawflush`, `addflush`, and `dstflush` coalesce screen updates before calling `flushmemscreen`.

Screen management includes lazy framebuffer attachment, named screen image creation, screen deletion/reset, default 8-bit colormap setup, screen blanking by hardware plus colormap blackening, and activity/idletime tracking. The implementation is global-lock-heavy through `drawlock` and relies on precise refcounting for images/screens/names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devdraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devdup.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devdup.c

Implements `#d`, the per-process file-descriptor duplication namespace. Each open fd appears as `<fd>`, and each control view appears as `<fd>ctl`; qid path encoding is `2*fd + isctl + 1`.

`dupgen` enumerates the current process `fgrp`, derives permissions from the underlying channel mode for data files, and gives ctl files read permission. Opening a data entry returns the underlying channel via `fdtochan`; the original device channel is closed. Opening a ctl entry opens the synthetic ctl file itself.

Reading a ctl entry formats fd metadata with `procfdprint`, matching `/proc/*/fd` style output. Data entries are not read through this device after open because opening them hands back the real channel.

The device has no write support. It depends directly on `up->fgrp`, `fdtochan`, and `procfdprint`, and is mainly a lightweight fd-to-file namespace adapter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devdup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devenv.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devenv.c

Implements `#e`, the environment variable filesystem. It serves either the current process environment group (`up->egrp`) or, when attached with spec `c`, the global kernel configuration environment `confegrp`.

`Egrp` entries are managed as `Evalue` records with name, qid, value, and length. Lookup can be by qid path or name. The environment group is read/write locked for enumeration, create, remove, read, write, and truncate.

The namespace is a directory of variable files. Creating a file adds an `Evalue`; opening with `OTRUNC` clears the existing value; reading copies bytes from the stored value; writing extends up to `Maxenvsize` and bumps qid/group versions. Removing deletes the entry.

Configuration environment writes are restricted: `envwriteable` allows `eve` or normal process environment writes, but prevents non-`eve` writes through attached config env. `ksetenv` provides a kernel helper to create/write variables, and `getconfenv` serializes config env as alternating NUL-terminated name/value strings.

`envcpy` deep-copies one environment group to another for process environment inheritance. `closeegrp` releases entries when the refcount drops. Main concerns are version consistency, strict maximum value size, and safe locking around mutable arrays.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devflash.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devflash.c

Implements `#F`, a flash memory device with up to two banks. Each detected bank exposes a `flash` directory with partition data files and matching `<name>ctl` files.

Flash cards are discovered in `flashreset` through `archflashreset`, matched against registered `Flashtype` drivers from `addflashcard`, reset by the card driver, and initially partitioned as a single `flash` partition spanning the full device. Each `Flash` has regions, erase sizes, width/interleave details, optional read/write/erase callbacks, and write-protect hooks.

Data reads and writes are constrained to partition bounds and translated to absolute flash offsets. `readflash` handles aligned and partial-width reads, using card callbacks when present or memory-mapped access otherwise. `writeflash` performs read-modify-write for unaligned spans, toggles hardware write protect, and refuses writes to protected boot regions. `eraseflash` similarly enforces boot protection and calls region or whole-chip erase operations.

Ctl reads report flash id, device id, width, sort, and overlapping erase/page regions. Ctl writes support `erase`, `add`, `remove` placeholder, `sync` placeholder, and `protectboot [off]`. `add` creates a new named partition within the current partition, validating erase-unit alignment through `flashaddr`.

This file abstracts NOR-style flash geometry and partition management over architecture/card-specific low-level routines. Important edge cases are erase alignment, partial-width writes, and boot-region protection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devflash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devfs.c

Implements `#k/fs`, a kernel block/file composition device rather than an on-disk filesystem. It builds synthetic devices from other files/devices using mirror, concatenation, interleaving, and partition mappings.

The top-level namespace contains trees, with the default persistent tree `fs`. Tree/device qids encode tree number and device number. `Fsdev` records type, name, tree, size, start offset, permissions, and inner devices. `Inner` records the opened backing channel, name, and size. `Tree` groups configured devices under a directory.

Configuration is through `#k/fs/ctl` or an optional boot config file (`fsconfig`, default `/dev/sdC0/fscfg` if present). Commands include `mirror`, `cat`, `inter`, `part`, `disk`, `clear`, and `del`. The `disk` command sets default tree, sector size, and optional default source for sd-style partition commands.

Reads and writes are dispatched by device type. `catio` maps sequential spans across inner devices. `interio` stripes fixed `Blksize` chunks across devices. `part` offsets into one inner device. `mirror` reads from the first successful copy and writes to all copies, retrying transient failures up to `Maxretries`.

Configuration changes are protected by a global `RWlock`; active I/O holds read locks, while add/delete holds write locks. Deletion marks devices gone and defers final free until open references drain. Backing channels are opened while only holding a read lock to permit nested `#k` devices.

Notable behavior: permissions are the intersection of inner device permissions; interleaved devices truncate inner sizes to block boundaries; partition starts/sizes are scaled by current sector size. This is a compact software RAID/partition layer for Plan 9 device files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devkbin.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devkbin.c

Implements `#Ι/kbin`, a privileged write-only keyboard scan-code injection device. It exists to let external keyboard sources, such as USB keyboard handling, feed scan codes into the kernel keyboard map path without duplicating map processing.

The namespace is just a directory and `kbin`. Only `eve` may open it. The file is exclusive via `kbinbusy`, protected by `kbinlck`.

Writes iterate over input bytes and call `kbdputsc(byte, 1)`, marking them as external source input. Reads on the data file return EOF; directory reads use the normal device directory helper.

The device is intentionally narrow and depends on the external keyboard scan-code consumer `kbdputsc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devkbin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devkbmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devkbmap.c

Implements `#κ/kbmap`, a privileged keyboard map inspection and update device. Only `eve` may open it.

Reads return fixed-width text records of keyboard map entries: map/table id, scan code, and resulting rune. Offsets are interpreted in units of `KBLINELEN`, so random-access reads can target map entries.

Writes parse newline-delimited mapping records. Accepted rune forms include quoted characters, control notation like `^X`, mouse/function pseudo-runes `M1` through `M5`, and numeric values. Blank/comment lines are ignored. Partial trailing lines are saved in `c->aux` and completed by later writes.

Parsed mappings are applied through `kbdputmap(map, key, rune)`. This file is a user-facing control surface for the kernel keyboard translation tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devkbmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devkprof.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devkprof.c

Implements `#K/kprof`, a kernel PC sampling profiler. The namespace contains `kpdata` and `kpctl`.

On first attach, it allocates a count buffer covering kernel text from `KTZERO` to `etext`, bucketed by `LRES` bits. `kprofinit` installs `_kproftimer` into the global `kproftimer` hook.

When profiling is enabled, `_kproftimer` adds one tick in milliseconds to total time and either the PC bucket or the overflow bucket. PCs inside `spllo` to `spldone` are replaced with `m->splpc` to attribute time to the high-priority caller.

`kpctl` accepts `startclr`, `start`, and `stop`. `kpdata` reads big-endian 32-bit counters, aligned to four-byte cells. The data length is updated based on allocated bucket count.

The implementation is intentionally simple: one global profiler, no per-CPU separation, and fixed text-range bucketing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devkprof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devloopback.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devloopback.c

Implements `#X`, a configurable two-ended loopback network/link simulator. Up to five loopback instances are available; each exposes `loopbackN/0` and `loopbackN/1`, with each port containing `ctl`, `status`, `stats`, and `data`.

`Loop` owns two `Link` structures. Each `Link` has input/output queues, a transmission queue, packet/byte/drop counters, queue limits, delay settings, drop policy, and a timer. Writes to one side enqueue packets for delivery to the other side.

Control commands tune link behavior: `delay latency bytedelay`, `indrop`, `droprate`, `limit`, and `reset`. Status reports delay, queue limit, input-drop mode, and drop rate. Stats report packets, bytes, deliberate drops, and soft overflows.

Packet writes add an 8-byte timestamp header, optionally pad to `minmtu`, record counters, enqueue into the remote output queue, and call `looper`. `pushlink` moves packets through timed output and receive stages, applying per-byte and fixed latency, random drops, queue overflow behavior, and timer scheduling for future delivery.

Closing either data side hangs up the opposite output queue; when both sides are closed, queues are reopened and state reset. The device is useful for network testing with artificial latency, bandwidth serialization, drops, and queue pressure.

One source-level detail to verify during maintenance: `pushlink` references `link->delayn` while the struct field is named `delaynns`, which looks like a typo unless supplied by an external macro in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devloopback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devmnt.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devmnt.c

Implements `#M`, the Plan 9 9P mount/client device. It multiplexes 9P RPCs over an underlying channel and presents remote files as local `Chan`s.

`mntversion` negotiates `Tversion` once per underlying channel, validates version/msize, creates a `Mnt`, sets `c->mux`, marks the channel `CMSG`, and creates the mount reply queue. `mntauth` and `mntattach` allocate local channels/fids and issue `Tauth`/`Tattach`.

Every filesystem operation creates or reuses an `Mntrpc`, assigns a unique tag, encodes an `Fcall`, writes it to the transport channel, and waits for the matching reply. `mountio` serializes readers through `m->rip` while allowing concurrent pending RPCs; `mountmux` matches replies by tag and wakes the owning request.

`mntrpcread` reads 9P message frames from the underlying channel into a queue, validates frame length against `msize`, decodes headers, and for `Rread` leaves data as blocks attached to the RPC. `mntrdwr` splits large reads/writes into `msize-IOHDRSZ` chunks and integrates with optional cache reads/writes.

Open/create, walk, stat, read, write, clunk, remove, and wstat map directly to 9P messages. Directory reads validate each returned stat record and call `mntdirfix` so local dev/type fields match the mounted channel.

Interrupt handling sends chained `Tflush` requests and marks unanswered RPCs as `Rflush`. `Mntrpc` headers and buffers are cached on a small free list; tags are allocated from a bitmask, excluding tag 0 and `NOTAG`.

The implementation depends on correct `Fcall` conversion, channel offsets for version negotiation, queue block handling, and tight lifetime rules between server channel `mchan`, local chans, and `Mnt`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devmnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devmouse.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devmouse.c

Implements `#m`, the mouse/cursor device. The namespace contains `cursor`, `mouse`, `mousein`, and `mousectl`.

`Mouseinfo` tracks current position/buttons/time/counter, accumulated deltas, redraw flag, resize generation, one-reader open state, acceleration settings, and a circular queue for button-change events. `Cursorinfo` and `curs` hold the active cursor.

`mouse` reads block until movement/button/resize state changes, then return Plan 9 mouse records (`m...`) or resize records (`r...`). Button states pass through configurable `buttonmap`, and scroll buttons can be swapped. `cursor` reads/writes the binary cursor shape. `mousein` is privileged and injects absolute position/button/time events. Writing `mouse` moves cursor position. `mousectl` supports `swap`, `scrollswap`, `buttonmap`, plus platform-specific `mousectl` passthrough.

`mousetrack` is the interrupt-level update path. It applies acceleration, clamps to screen clip rectangle, merges keyboard-emulated buttons, queues button changes, wakes readers, marks cursor redraw, and records screen activity. `mouseclock` periodically applies accumulated deltas, redraws cursor, and checks draw idle blanking.

The file also contains serial mouse protocol decoders for Microsoft 3-button, IntelliMouse with scroll, and Logitech 5-byte formats. They resynchronize after idle gaps and translate packets into `mousetrack` calls.

Dependencies include draw/screen cursor hooks, global framebuffer state, keyboard mouse emulation, and monitor configuration. The device enforces exclusive `mouse` reader semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devmouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devpipe.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devpipe.c

Implements `#|`, the Plan 9 pipe device. Each attach creates a new `Pipe` with two queue-backed endpoints exposed as `data` and `data1`.

The two data files are connected crosswise: reading `data` consumes queue 0 and writing `data1` writes queue 0; reading `data1` consumes queue 1 and writing `data` writes queue 1. Queue size defaults to `conf.pipeqsize`, with larger default on multiprocessor systems.

`Pipe` tracks qrefs for each endpoint and an overall reference count. Closing the last reference to either side hangs up the opposite queue and closes the local queue; once both qrefs are zero, both queues are reopened for reuse. Final close frees queues and the `Pipe`.

Directory/stat generation reports current queue lengths. `wstat` by `eve` can change endpoint permissions but not owner. Writes to closed pipes post a user note `"sys: write on closed pipe"` unless the channel is marked `CMSG` for mounted queue use.

The implementation provides both byte and block I/O paths (`pipewrite`/`pipebwrite`, `piperead`/`pipebread`) on top of kernel `Queue`s.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devpipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devpnp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devpnp.c

Implements `#$`, a hardware discovery/control device for ISA PnP and PCI configuration space. Top-level directories are `pnp` and `pci`.

ISA PnP support uses the standard initiation key, isolation protocol, card serial/checksum reading, CSN assignment, and resource-data reads through a configured READ_DATA port. Discovered `Card` records store CSN, ids, optional config string, and raw resource byte count. `pnpreset` can preload expected cards/config strings from kernel configuration and then scan.

The `pnp` directory exposes `ctl`, plus per-card `csnNctl` and `csnNraw`. `ctl` reports enabled/disabled state and accepts `port <addr>` to scan and `debug <n>`. `csnNctl` reports the serial identifier and accepts configuration writes, though `wrconfig` is currently a stub. `csnNraw` reads raw resource data after waking the selected card.

PCI support enumerates `Pcidev` entries under `pci`, exposing `<bus>.<dev>.<fn>ctl` and `<bus>.<dev>.<fn>raw`. `ctl` reports class codes, vendor/device id, interrupt line, and BARs. `raw` reads/writes PCI config space up to 256 bytes, using 32/16/8-bit accesses depending on offset and length alignment.

The device is highly platform-specific and depends on ISA I/O port access, PCI config helpers, and kernel config strings. ISA PnP configuration writing is explicitly unimplemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devpnp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devproc.c

Implements `#p`, the process filesystem. Top-level entries are `trace` and one directory per live process pid. Per-process files include `args`, `ctl`, `fd`, `fpregs`, `kregs`, `mem`, `note`, `noteid`, `notepg`, `ns`, `proc`, `regs`, `segment`, `status`, `text`, `wait`, `profile`, and `syscall`.

Qids encode file type, process slot, and pid/version for stale-channel detection. `procgen` enumerates processes, builds per-process file permissions from static `procdir` permissions plus `p->procmode`, and computes dynamic lengths for wait/profile files.

Access control is strict around cross-process inspection: user `none` cannot inspect/control other processes unless `eve`; private-memory processes deny `mem`, `ctl`, and `note`; many operations require matching process owner or `eve`. Opening `text` returns the underlying executable channel rather than the synthetic proc channel.

Reads provide process args, syscall trace text, user memory or selected kernel memory through `mem`, profiling buffers, queued notes, raw `Proc`, user/kernel/fp registers, status records, segment listings, wait records, namespace reconstruction, note id, fd table, and global trace events. Directory reads are normal devdir reads.

Writes allow changing args, writing stopped-process memory/registers/fpregs, posting notes, changing noteid, group notes through `notepg`, and extensive control through `ctl`. `procctlreq` supports killing, stopping/waiting, starting with tracing, closing fds, priority/fixed priority, wired processor, noswap/private/hang flags, profiling allocation, scheduler trace toggling, and EDF real-time parameters/admission/expulsion.

`procctlmemio` performs controlled user memory access by locating segments, faulting pages in, mapping pages, copying bytes, converting text to data for writes, and marking TLB/text-cache flush state. `txt2data` and `data2txt` convert segment types while preserving image metadata.

The file also implements global process trace buffering (`Traceevent` ring), per-process profiling clock hooks, namespace mount scanning, fd table formatting used by `devdup`, and wait queue consumption. This is one of the broadest kernel introspection/control surfaces in the group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devroot.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devroot.c

Implements `#/`, the synthetic root device. It provides a fixed initial root namespace plus a `boot` directory containing boot-time files added by the kernel.

`rootdir` starts with `#/` and `boot`; `rootreset` adds standard directories such as `bin`, `dev`, `env`, `fd`, `mnt`, `net`, `net.alt`, `proc`, `root`, and `srv`. `bootlist` starts with its directory entry, and `addbootfile` appends named immutable boot files with content pointers and lengths.

`Dirlist` tracks a base qid path, `Dirtab` array, data pointer array, current count, and max count. `addlist` assigns qids sequentially, records permissions, and marks directory qids when needed.

`rootgen` enumerates root and boot directories and handles dot-dot behavior. `rootread` serves directory reads or copies bytes from in-memory boot/root file data. Writes always fail.

This device is the seed namespace for early system operation, before normal filesystem mounts populate standard directories.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devroot.c -->