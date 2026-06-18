# Group Research: group_20_9front_sources_os_plan9_9front_sys_src_9_port_devaoe_c_sources_os_pla_47fc7daa971c

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devaoe.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devaoe.c

Purpose: Plan 9 kernel AoE initiator device, exposed as `#æ/aoe`, implementing ATA-over-Ethernet discovery, device registration, config I/O, identify, and sector reads/writes.

Exposed interface: top-level `ctl` and `log`; per-AoE-unit directories named `<major>.<minor>` with `ctl`, `data`, `config`, `ident`, and `devlink/` entries. Top-level control commands include `bind`, `unbind`, `discover`, `rediscover`, `autodiscover`, `debug`, and deprecated `remove`. Unit control commands include `failio`, `identify`, `jumbo`, `maxbno`, `mtu`, `nofail`, and `setsize`.

Core implementation: maintains global `devs`, `netlinks`, event ring, unit counters, and per-device `Aoedev` state with `Devlink` paths, outstanding `Frame`s, SRB queues, config/identify data, negotiated MTU, open count, and flags. `aoesweepproc` periodically rediscover/resends timed-out frames and adapts RTT/window/MTU behavior. `netrdaoeproc` reads AoE packets from bound Ethernet channels and dispatches config, ATA, and error responses.

Important paths: `rw` creates SRBs for sector-aligned data I/O; `strategy`, `work`, and `atarw` split requests into AoE frames; `atarsp` completes frames and wakes SRBs; `qcfgrsp` creates/updates devices and links; `configwrite` sends AoE config writes; `netbind`/`netunbind` attach and detach Ethernet AoE readers.

Dependencies: Plan 9 device framework, Ethernet/netif, IP headers, AoE protocol definitions, ATA identify helpers from `fis.h`, kernel locking, rendezvous, block queues, and configured `aoeif`.

Research notes: this is a complex, stateful storage path. Review should focus on lock ordering around `devs`, `Aoedev`, and `netlinks`; frame/SRB lifetime; resend behavior under `nofail`; MTU/jumbo fallback; and unbind/remove races with outstanding I/O.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devaoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devaudio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devaudio.c

Purpose: generic audio device front-end `#A`, dispatching to registered hardware drivers through `Audio` callbacks.

Exposed interface: directory with `audio`, `audioctl`, `audiostat`, and `volume`. Attach spec selects controller number. `audio` is bidirectional sample I/O, `audioctl` writes hardware control commands, `audiostat` reads status, and `volume` reads/writes mixer volume text.

Core implementation: `addaudiocard` registers probe functions; `audioreset` probes all registered cards and builds the `audiodevs` list. Each Chan has an `Audiochan` aux structure holding the selected `Audio`, an owner Chan, and a reusable text buffer. `audioopen` enforces one reader and one writer for `Qaudio` with separate refs. `audioread`/`audiowrite` dispatch to hardware callbacks under the per-channel qlock.

Helpers: `genaudiovolread` serializes volume tables to text, translating hardware ranges to percentages. `genaudiovolwrite` parses volume writes, supports defaulting bare values to `master`, accepts optional `in`/`out`, clamps percentages, and calls the driver setter.

Dependencies: `audioif.h` driver contract and Plan 9 device helpers.

Research notes: most policy is in the generic open/exclusive-access layer and volume parser. Hardware-specific correctness depends on callback implementations; this file assumes callbacks tolerate serialized access via `Audiochan` qlock.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devaudio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devbridge.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devbridge.c

Purpose: kernel Ethernet bridge device `#B`, supporting multiple bridge instances, VLAN-aware forwarding, MAC learning, tunnel/bypass ports, logging, stats, and optional TCP MSS clamping.

Exposed interface: `#B<n>/bridge<n>/` with bridge files `ctl`, `stats`, `cache`, `log`, and per-port directories containing `ctl`, `local`, and `status`. `ctl` supports `bind`, `unbind`, `vlan`, `cacheflush`, `set tcpmss`, `clear tcpmss`, and `delay`.

Core implementation: `Bridge` tracks ports, MAC cache, stats, delay parameters, MSS option, and log state. `Port` wraps one or two data Chans, owns a reader proc, identity tuple, owner hash, stats, and VLAN membership bitmap. `etherread` is the receive loop: reads packets, applies delay, strips/validates VLAN tags, learns source MACs, and forwards unicast or floods multicast/unknown traffic. `etherwrite` handles outgoing VLAN tagging, minimum frame sizing, and IPv4 fragmentation for tunnel ports.

Port setup: `portbind` opens Ethernet clone/data channels, configures promiscuous or bypass mode and bridge mode, or opens read/write tunnel endpoints. It inserts the port under bridge write lock and starts a reader kproc. `portunbind` posts a note to the reader and removes the port.

Dependencies: Plan 9 netif/Ethernet, IP/IPv6 helpers, logging helpers, and `tcpmssclamp`.

Research notes: key review areas are bridge lock upgrades in `etherread`, cache mutation under read/write locks, reader shutdown semantics, owner-hash race prevention, VLAN validation, and tunnel fragmentation correctness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devbridge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devcap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devcap.c

Purpose: capability authentication device `#¤`, allowing privileged code to register SHA1 HMAC hashes and users to consume a matching capability to change process user.

Exposed interface: directory with `capuse` and `caphash`. `caphash` is write-only and eve-only; `capuse` accepts capability strings. Eve can remove `caphash` from the directory via `remove`, reducing exposure after setup.

Core implementation: `capalloc` holds a qlocked linked list of `Caphash` records with tick timestamps. `addcap` appends a hash after trimming expired/excess entries. `remcap` trims, finds a hash with `tsmemcmp`, removes it, and returns it for single-use consumption. Limits are `Maxhash` 256 and `Timeout` 60 seconds.

Capability format: writes to `capuse` are copied into secure memory, split at the final `@` into identity string and key, HMAC-SHA1 is computed, and optional `from@to` syntax requires `from` to match `up->user`. On success `procsetuser(to)` is called.

Dependencies: `libsec.h` SHA1/HMAC and secure allocation.

Research notes: this is security-sensitive. The code uses time-safe hash comparison and one-shot removal, but review should focus on capability string grammar, error paths that retain allocated secure memory until unwound, and the trust boundary of eve-only `caphash`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devcons.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devcons.c

Purpose: core console and system-control device `#c`, plus kernel printing, panic, time, random, process identity, driver masking, and shutdown helpers.

Exposed interface: `bintime`, `cons`, `consctl`, `cputime`, `drivers`, `hostdomain`, `hostowner`, `kmesg`, `kprint`, `null`, `osversion`, `pid`, `ppid`, `random`, `reboot`, `sysname`, `sysstat`, `time`, `user`, `zero`, `config`, and `mordor`.

Core implementation: printing flows through `putstrn0`, which appends to `kmesg`, sends to `/dev/kprint` or screen output, and sends to UART/serial queues with newline conversion. `panic` disables kprint, prints diagnostic output, dumps stack, optionally exits/reboots, or hangs. `consread` handles directory reads and each virtual file’s data. `conswrite` handles console output, time setting, host/user/sysname updates, driver masks, reboot/panic/rdb commands, and sysstat reset.

Time support: text `time` returns seconds, nanoseconds, fast ticks, fast frequency, and monotonic value. `bintime` reads/writes big-endian binary time controls for setting time, adjustment, and frequency.

Dependencies: kernel queues, random, TOD/fastticks, auth/hostowner helpers, UART output, reboot/debug hooks, and global machine accounting.

Research notes: this is central kernel plumbing. Important audit areas are privilege checks around reboot/time, nonblocking kprint queue behavior, direct panic paths, and avoiding page faults or blocking in low-level print paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devdraw.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devdraw.c

Purpose: draw device `#i`, implementing Plan 9 draw protocol client management, image/screen/window objects, refresh delivery, colormap access, and drawing message execution.

Exposed interface: top-level `draw`, `winname`, `new`; each client directory exposes `colormap`, `ctl`, `data`, and `refresh`. Opening `new` allocates a client and returns its `ctl`.

Core implementation: global `sdraw` tracks clients and named images under `drawlock`. `Client` holds image hash buckets, screen refs, refresh queue, read buffer, busy flag, operation state, and ids. `DImage`, `DScreen`, `CScreen`, and `DName` manage Memimage/Memscreen ownership, reference counts, names, windows, and public screen sharing.

Drawing protocol: `drawmesg` parses binary commands such as allocate image/screen, draw, affine warp, ellipse, line, polygon, text, read image, write image, name/attach image, move/top/bottom windows, set operator, and visible/flush. It calls memdraw/memlayer primitives and records flush rectangles for screen updates.

Lifecycle: `drawopen` initializes screen image and installs id 0 from the named screen image for a new client. `drawclose` decrements client refs, frees refresh records, screens, names, images, and client slots when last Chan closes. `drawread` returns client ids, image data, refresh messages, colormap data, and winname. `drawwrite` handles colormap writes and draw protocol data.

Dependencies: `draw.h`, `memdraw.h`, `memlayer.h`, cursor/screen interfaces, and framebuffer attach/flush hooks.

Research notes: this is a large binary protocol interpreter. Review should focus on length checks in each command, image/screen refcount balance, named-image invalidation, refresh queue wakeups, and operations that temporarily alter clip rectangles or allocate variable-size point arrays.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devdraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devdtracy.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devdtracy.c

Purpose: kernel device `#Δ` for dtracy tracing support, gated by `*dtracy=` configuration.

Exposed interface: top-level `clone` and `probes`; each cloned tracing channel directory exposes `ctl`, `prog`, `buf`, `epid`, and `aggbuf`. `ctl` accepts `stop` and `go`; `prog` loads packed DTrace-like clauses.

Core implementation: `dtracyinit` enables tracing only if configured, allocates per-machine locks, and initializes tracing. `dtknew` allocates a `DTKChan`, stores it in `dtktab`, and creates a `DTChan`. `dtracyopen` creates a channel on `clone`, restricts non-directory channel files to eve, bumps refs, and attaches per-open aux string state. `dtracyclose` frees channels when refs drop to zero.

Read paths: `probesread` caches probe names, `epidread` caches enabled probe ids and record lengths, and `handleread` waits/polls for trace or aggregate buffer data. Writes compile programs with `prog` and control run state through `dtcrun`.

Dependencies: `<dtracy.h>` tracing runtime and kernel memory/locking adapters (`dtmalloc`, `dtfree`, `dtmachlock`, `dtpeek`, etc.).

Research notes: key areas are privilege checks, channel refcounting, cached string lifetime in aux, blocking read behavior, and safe address validation in `dtpeek`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devdtracy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devdup.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devdup.c

Purpose: duplicate-file-descriptor device `#d`, presenting the current process file group as files.

Exposed interface: each fd appears as `<fd>` and `<fd>ctl`. Qid encoding is `(2*fd + isctl) + 1`.

Core implementation: `dupgen` iterates `up->fgrp->fd`, derives permissions from the target Chan mode for fd files, and exposes ctl files as readable. `dupopen` rejects `ORCLOSE`; opening an fd file returns `fdtochan` and closes the original `#d` Chan, while opening a ctl file opens the synthetic Chan. `dupread` on ctl files formats fd metadata using `procfdprint`.

Dependencies: process file group, `fdtochan`, and standard devwalk/devstat helpers.

Research notes: behavior is intentionally process-local and minimal. Review focus is qid/fd decoding, permissions mirroring, and ensuring ctl opens do not accidentally confer operations on the underlying fd.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devdup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devenv.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devenv.c

Purpose: environment variable device `#e`, with per-process environment groups and a special configuration environment `#ec`.

Exposed interface: directory entries are environment variable names. `#e` is writable for the current environment group; `#ec` exposes the global configuration group and is writable by eve or its owner context. Files contain raw variable values.

Core implementation: `Egrp` stores entries in an indexed array plus hash chains. Qids combine a generation path and array index so stale Chans can be detected. `envcreate`, `envremove`, `envread`, `envwrite`, and `envopen` coordinate under the environment group RWLock. `envrealloc` tracks allocation and enforces `Maxenvsize` and `Maxvalsize` for non-configuration groups.

Lifecycle helpers: `newegrp` allocates a group, `envcpy` deep-copies one environment into another, `closeegrp` frees when refs drop, `ksetenv` writes from kernel code through the device interface, and `getconfenv` serializes the configuration environment as name/value strings.

Dependencies: `Egrp`/`Evalue` definitions from kernel data structures, process `up->egrp`, and Plan 9 namec/device operations.

Research notes: important areas are qid stale-entry protection, allocation accounting, permission differences between `#e` and `#ec`, `CRCLOSE` remove behavior, and hash/index consistency on create/remove.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devether.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devether.c

Purpose: generic Ethernet device front-end `#l`, multiplexing hardware NIC drivers into Plan 9 netif channels, plus netconsole and dynamic MAC address translation support.

Exposed interface: standard netif clone/control/data files supplied through `netif*` helpers. Attach specs select controller and may create eve-only configured instances with `ctlr:type/options`.

Core implementation: `addethercard` registers driver reset functions. `etherprobe` allocates/configures an `Ether`, parses config/options, calls the matching hardware reset, creates the output queue, initializes netif state, and records MAC/broadcast values. `etherreset` probes configured and auto-detected cards, installs `%E`, and enables netconsole if configured. `ethershutdown` calls hardware shutdown callbacks.

Packet paths: `etheriq` handles received blocks, optional DMAT downstream translation, stats, and `ethermux`. `etherwrite`/`etherbwrite` validate MTU, parse non-data controls such as `nonblocking`, defer driver ctl commands, and queue outbound packets via `etheroq`. `ethermux` delivers packets to matching netif connections, supports promiscuous, bridge, bypass, header-only trace, multicast, MAC learning, and copy avoidance.

Extra support: `netconsole` builds a UDP/IP/Ethernet console output path from `console=net ...`. `dmatproxy` rewrites MACs in ARP, IPv4/IPv6, NDP, and BOOTP cases to support bridging over media that cannot spoof source MACs.

Dependencies: `netif.h`, `etherif.h`, IP/IPv6 helpers, queue subsystem, hardware driver callbacks, and optional DMAT table in `Ether`.

Research notes: review should focus on packet ownership/freeing across `ethermux`, bridge/bypass interactions, q bypass changes on link state, DMAT checksum/address rewriting, and netconsole packet header construction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devflash.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devflash.c

Purpose: flash memory device `#F`, abstracting architecture flash banks and registered flash chip drivers.

Exposed interface: `#F[bank]/flash[bank]/` with partition data files and `<partition>ctl` files. Initial partition is `flash` covering the full bank. Control commands include `erase`, `add`, `remove` placeholder, `sync` placeholder, and `protectboot`.

Core implementation: `addflashcard` registers chip-type reset handlers. `flashreset` asks the architecture for bank mappings, finds a matching flash type, resets it, enables boot protection, and creates the full-bank partition. `flashgen`/`flash2gen` synthesize partition and ctl entries.

I/O paths: `flashread` reads partition data or emits ctl information including chip id, width, sort, regions, erase size, and page size. `flashwrite` writes partition data, erases blocks/all, adds partitions, and toggles boot protection. `readflash`, `writeflash`, and `eraseflash` serialize with the flash qlock, handle device width/alignment, call chip callbacks, and toggle architecture write protection.

Dependencies: `flashif.h`, architecture hooks `archflashreset` and `archflashwp`, and chip-specific flash drivers.

Research notes: critical areas are erase-block alignment, boot-region protection, partition bounds, width/interleave handling, and the placeholders for remove/sync commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devflash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devfs.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devfs.c

Purpose: synthetic block-composition device `#k`, building file-system-like block devices from inner devices as mirrors, concatenations, interleaves, partitions, and encrypted devices.

Exposed interface: top-level trees under `#k`; default tree `#k/fs` always exists and contains `ctl`. Configured devices appear as files in trees. `ctl` accepts `mirror`, `cat`, `inter`, `part`, `crypt`, `clear`, `del`, and `disk`.

Core implementation: `Tree` stores named device directories; `Fsdev` stores type, size, start, inner devices, config name, qid version, refs, and optional AES-XTS key. `mconfig` parses one config line, opens inner devices under read lock, then adds/removes configuration under write lock. `rdconf` initializes `fs` and optionally reads a config file from `fsconfig` or `/dev/sdC0/fscfg`.

I/O paths: `catio` maps linear ranges across inner devices; `interio` stripes fixed 8 KiB blocks; `mirror` reads retry across copies and writes all copies with retry logging; `part` offsets into one inner device; `cryptio` encrypts/decrypts 512-byte sectors using AES-XTS after a default 64 KiB header offset. `mread`/`mwrite` clamp to device size and dispatch by type.

Lifecycle: `mopen` refs active devices, `mclose` decrefs or final-deletes gone devices, and `mdelctl`/`mdeldev` mark devices gone and free trees when safe. Config text is regenerated into `confstr`.

Dependencies: generic Chan I/O, sd allocation for crypt write buffers, AES-XTS from `libsec.h`, and kernel locking.

Research notes: main risks are nested device locking, deletion while open, mirror retry semantics, encryption alignment/key handling, config parsing, and correct close/free ordering outside locks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devi2c.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devi2c.c

Purpose: I2C bus device `#J`, exposing registered I2C buses and probed devices as ctl/data files and providing kernel helper functions for common I2C transactions.

Exposed interface: `#J/<bus>/i2c.<addr>.ctl` and `i2c.<addr>.data`. `ctl` supports `size` and `subaddress`. `data` reads/writes device payloads with optional subaddress offset.

Core implementation: global arrays track up to 16 buses and 1024 devices. `addi2cbus` and `addi2cdev` register objects. `probebus` initializes a bus once and probes 7-bit addresses 0x08-0x77 plus all 10-bit addresses, creating copied `I2Cdev` records for responding addresses. `i2cgen` builds the synthetic hierarchy.

Transaction helpers: `putaddr` encodes 7-bit/10-bit address and optional subaddress. `i2csend`, `i2crecv`, quick, byte, word, and 32-bit helpers build small packets and call `i2cbusio`. `i2cbusio` serializes access with qlock/canqlock depending on context and calls the bus `io` callback.

Dependencies: `i2c.h` bus/device structures and callbacks.

Research notes: review should focus on bus probing side effects, fixed packet buffer size truncation, subaddress byte order, user/non-user locking behavior, and consistency of the `devs` array while generating directories.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devi2c.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devkprof.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devkprof.c

Purpose: kernel profiling device `#K`, collecting timer samples by program counter.

Exposed interface: directory with `kpdata` and `kpctl`. `kpctl` accepts `startclr`, `start`, and `stop`. `kpdata` returns big-endian 32-bit counters.

Core implementation: `kprofattach` lazily allocates a counter buffer covering `[KTZERO, etext)`, with one counter per PC offset plus special counters. `kprofinit` installs `_kproftimer` as the global profiling timer. `_kproftimer` increments elapsed-time count and either the PC bucket or out-of-range bucket; PCs in `spllo`/`splx` range use `m->splpc`.

Dependencies: kernel text symbols, timer callback hook `kproftimer`, and xalloc.

Research notes: this is simple but low-level. Review should focus on buffer sizing, architecture assumptions about PC range and counter width, and read alignment (`SZ` enforced at 4 bytes).
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devkprof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devloopback.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devloopback.c

Purpose: virtual loopback link device `#λ`, providing paired endpoints with configurable delay, byte delay, queue limits, input drop behavior, and deliberate drop rate.

Exposed interface: up to five loopback instances. Each `loopback<n>` has endpoint directories `0` and `1`; each endpoint exposes `ctl`, `status`, `stats`, and `data`. Data written to one endpoint is delivered to the other.

Core implementation: `Loop` owns two `Link`s. Each `Link` has input/output queues, transmission queue, timer, counters, drop/delay settings, and queue limit. `loopbackattach` initializes queues and defaults on first ref. Opening `data` is exclusive per endpoint. Closing one data side hangs up the opposite output and drains/schedules; closing both resets queues and settings.

Packet scheduling: `loopoput` pads a timestamp header, updates counters, queues to the opposite link, and calls `looper`. `pushlink` moves blocks from output queue to delayed transmit queue and then into input queue when their timestamp expires, scheduling a timer for the next event. Delay is `delay0ns + len * delaynns`; drop behavior is controlled by `indrop` and `droprate`.

Dependencies: kernel queues, timers, TOD nanosecond time, block manipulation helpers.

Research notes: important review areas are timer locking, block ownership on drops and queue overflow, close/hangup interactions, timestamp header accounting, and control command validation for negative or extreme delay/limit values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devloopback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devmii.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devmii.c

Purpose: Ethernet MII/SMI/MDIO PHY debug device `#Φ`, exposing registered MII buses and PHY registers.

Exposed interface: `#Φ/<bus>/<phy>/ctl`, `mii`, and `mmd`. `ctl` reads PHY status/dump and accepts `reset`, `status`, and `autoneg`. `mii` reads/writes Clause 22 16-bit registers; `mmd` reads/writes Clause 45 device/register space.

Core implementation: `linkage` installs `addmiibus` and `delmiibus` callbacks. `addbus`/`delbus` maintain a locked bus table keyed by pointer or name. `miigen` builds the bus/phy/register-file hierarchy. `getphy` validates qid-derived bus and PHY. `phystatus` emits id, OUI, link, speed, duplex, and a register dump.

Register I/O: `miiread` and `miiwrite` require exact two-byte accesses, enforce offset ranges, convert little-endian 16-bit values, and call `miimir`/`miimiw` or `miimmdr`/`miimmdw`.

Dependencies: `ethermii.h` MII structures and functions.

Research notes: review should focus on offset masking/range checks, byte-order expectations for register files, bus table lifetime vs driver removal, and privilege expectations because files are mode `0600`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devmii.c -->