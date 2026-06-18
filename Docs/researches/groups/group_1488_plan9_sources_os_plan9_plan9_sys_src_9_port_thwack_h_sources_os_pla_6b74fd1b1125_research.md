# Group Research: group_1488_plan9_sources_os_plan9_plan9_sys_src_9_port_thwack_h_sources_os_pla_6b74fd1b1125

Scope: `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/thwack.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/thwack.h

## Role

Defines the shared state and public interface for Plan 9's `thwack` block compressor and `unthwack` decompressor. It is a header-only contract used by the encoder and decoder.

## Main Definitions

The constants define the wire and window limits: `ThwMaxBlock` is 1600 bytes, encoder history has `EWinBlocks` 22 blocks, decoder history has `DWinBlocks` 32 blocks, and up to `CompBlocks` 10 blocks may be referenced when decoding one compressed block. Hashing uses a 4096-entry table, with `MinMatch` 3 and sequence acknowledgement mask limits.

`Thwack` owns encoder blocks, per-block hash tables, and backing block data. `Unthwack` owns decoder history blocks and backing data.

## Interfaces

Exports initialization, compression, acknowledgement, decompression, and decoder-state reporting:

- `thwackinit`, `unthwackinit`
- `thwack`, `thwackack`
- `unthwack`, `unthwackstate`

## Risks

All sizing assumptions are compile-time fixed. Callers must respect `ThwMaxBlock`, sequence ordering, and destination buffer sizes; the header does not encode ownership or bounds beyond these constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/thwack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/tod.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/tod.c

## Role

Implements kernel time-of-day conversion around the fastest available tick counter. It converts fast ticks to nanoseconds, microseconds, and back using fixed-point multipliers.

## Main State

A single locked `tod` structure tracks initialization, frequency, fixed-point conversion multipliers/dividers, last tick reading, epoch offset, monotonic last return, and gradual correction state. It assumes multiprocessor fast clocks are synchronized.

## Control Flow

`todinit` samples `fastticks`, sets frequency, and registers `todfix` as a periodic clock callback. `todsetfreq` recomputes conversion factors with `mk64fract`. `todset` either sets absolute time or applies a gradual `delta` over `n * HZ` ticks. `todget` locks around `fastticks`, applies pending correction, converts elapsed ticks to epoch nanoseconds, and clamps time so it never moves backward.

`todfix` periodically folds elapsed ticks into `tod.off` to reduce overflow risk. Public helpers expose seconds, fastticks-to-us/ns, and us/ms/ns-to-fastticks conversions.

## Dependencies

Uses kernel locks, `fastticks`, `MACHP(0)->ticks`, `addclock0link`, `mul64fract`, `HZ`, and Plan 9 fixed-width integer types.

## Risks

The design relies on synchronized CPU tick counters. `todfix` contains a debug `iprint` for large conversions. `mk64fract` uses `(to<<32)/from`, so callers must avoid invalid or overflowing ratios; `todsetfreq` panics on nonpositive frequency.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/tod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/ucalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/ucalloc.c

## Role

Provides an uncached-memory allocator backed by the Plan 9 pool allocator. It is intended for DMA or hardware paths that require cache-inhibited memory.

## Main Data

`ucpool` is a `Pool` named `"Uncached"` with 4 MiB max size, 1 MiB arenas, and 32-byte quantum. A private lock/message buffer serializes pool diagnostics and panic printing.

## Control Flow

`ucarena` allocates a 1 MiB aligned cached arena, maps it uncached with `mmuuncache`, and temporarily increases `mainmem->maxsize` while doing so. `ucallocalign` allocates from `ucpool`, asserts the request fits within an arena, and zeroes successful allocations. `ucalloc` uses 32-byte alignment. `ucfree` returns memory to the pool.

## Dependencies

Depends on `<pool.h>`, `mallocalign`, `mmuuncache`, `mainmem`, `msize`, kernel locks, and Plan 9 panic/print routines.

## Risks

The allocator assumes 1 MiB arena allocation and successful uncached remapping semantics. `ucallocalign` asserts on large requests rather than returning an error. The panic path copies diagnostic text out before unlocking, which is correct but tightly coupled to the pool callback contract.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/ucalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/ucallocb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/ucallocb.c

## Role

Allocates and frees `Block` network buffers from uncached memory, using `ucalloc` underneath. This is for interrupt/DMA paths that need non-cache-coherent buffers.

## Main Data

`Hdrspc` reserves 64 bytes for prepended higher-level headers. `ucialloc.bytes` tracks interrupt-time uncached block allocation. Freed blocks are poisoned with `Bdead` (`"QIOB"`).

## Control Flow

`_ucallocb` allocates `sizeof(Block)+size+Hdrspc`, initializes the `Block`, aligns data start/end to `BLOCKALIGN`, leaves header slack at the front, and sets `rp`/`wp`. `ucallocb` requires `up != nil`, panics on failure, and tags the allocation. `uciallocb` is the interrupt-allocation variant: it may return nil, marks `BINTR`, and accounts bytes. `ucfreeb` decrements the ref count, calls custom free hooks if present, updates interrupt accounting, poisons pointers, and returns memory to `ucfree`.

## Dependencies

Depends on `Block`, atomic ref helpers `_xinc/_xdec`, `msize`, `ucalloc`, `ucfree`, `setmalloctag`, `conf.ialloc`, and kernel allocation conventions.

## Risks

Normal `ucallocb` panics rather than returning nil. The ialloc limit code is compiled out with `if(0)`. Pointer poisoning helps catch use-after-free but assumes no later legitimate inspection of freed blocks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/ucallocb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/unthwack.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/unthwack.c

## Role

Implements the `thwack` decompressor and decoder history management.

## Main Data

Static decode tables map compact bit prefixes to literal/match lengths and offset classes. `Unthwack` keeps a circular, sequence-ordered block history. `unthwackstate` reports the newest decoded sequence and a mask of nearby available prior sequences so the encoder can reference shared history.

## Control Flow

`unthwackinit` clears state and assigns each block its backing buffer. `unthwackinsert` inserts a decoded block by sequence, moving block metadata while preserving backing buffers, then advances the circular slot.

`unthwack` validates compressed size, builds a temporary list of the current output block plus referenced history blocks from the compressed header sequence delta/mask, decodes literals and match references from the bitstream, bounds-checks output and history offsets, copies reconstructed bytes to `dst`, then inserts the new block into decoder history.

## Dependencies

Uses `thwack.h` constants and Plan 9 memory/print routines.

## Risks

Malformed streams return negative errors; one missing-history path prints to console. Decompression is sensitive to bit accounting (`utnbits`, `overbits`) and uses overlapping copy semantics manually. Destination size and sequence continuity are caller-visible correctness requirements.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/unthwack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/usb.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/usb.h

## Role

Defines common USB device, endpoint, and host-controller abstractions for Plan 9 USB controller drivers.

## Main Definitions

Constants cover endpoint/device limits, transfer types, speeds, standard request fields, request codes, device states, and hub-style port status bits. `GET2` and `PUT2` encode little-endian USB 16-bit fields.

## Main Structures

`Hciimpl` is the controller driver vtable: initialization, interrupt handling, endpoint open/close/read/write, root-port control, shutdown, and debug hooks.

`Hci` embeds hardware configuration plus the implementation hooks. `Ep` models a kernel USB endpoint, including stable identity fields, QLock-protected configuration, transfer type, timing, saved toggles, and controller-private `aux`. `Udev` models per-device state and cached endpoints.

## Interfaces

Exports `addhcitype`, `usbmodename`, and `seprintdata`.

## Risks

The header centralizes contracts but does not enforce concurrency. Controller drivers must honor endpoint locking, saved toggle behavior, root-hub status bit format, and half/full/high-speed transfer semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/usb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/usbehci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/usbehci.c

## Role

Implements the USB 2.0 EHCI host-controller backend for the common Plan 9 USB layer. It supports control, bulk, interrupt, and isochronous endpoints, root-port control, scheduling, interrupt handling, and debug dumps.

## Main Data

The file defines software and hardware descriptors: `Qh` queue heads, `Td` queue transfer descriptors, high-speed `Itd`, split/full-speed `Sitd`, `Qio` endpoint-direction I/O state, `Ctlio` control request state, `Isoio` isochronous stream state, and `Qtree` periodic interrupt scheduling. `Edpool` allocates aligned descriptor unions from `xspanalloc`.

## Control Flow

`ehcimeminit` allocates the frame list, initializes the asynchronous QH ring, and builds the periodic QH tree. `init` enables EHCI interrupts, periodic and asynchronous schedules, runs the controller, routes ports, and powers ports.

`epopen` allocates endpoint-specific state and schedules QHs or ISO descriptors. `epread`/`epwrite` dispatch by transfer type. Non-ISO I/O builds QTD chains with `epgettd`, links them into the QH, waits in `epiowait`, handles missing interrupts through polling, copies data back, and frees QTDs. Control transfers are split into setup, data, and status phases. ISO I/O uses ITDs for high-speed and SITDs for full-speed split transactions, with circular frame windows and wakeups from interrupt processing.

`ehciintr` acknowledges controller status, processes ISO descriptors, periodic interrupt QHs, and asynchronous QHs. Port methods enable, reset, hand low/full-speed ownership to companion controllers, and return root-hub-compatible status.

## Dependencies

Depends on `usb.h`, EHCI register definitions in `portusbehci.h`/`usbehci.h`, uncached/aligned memory helpers, cache coherence primitives, Plan 9 locks, timers, sleeps, and controller `Ctlr` fields supplied by platform glue.

## Risks

The file documents known issues: excess delays/interrupt locks, incomplete per-frame bandwidth admission, polling required for some controllers, and no power-overrun warning. ISO sample packing is explicitly imperfect. Several paths panic on internal state corruption. Control read buffering has a `BUG for big transfers`. Correctness relies on descriptor alignment, `coherence()` placement, frame-list pointer manipulation, and careful close/cancel synchronization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/usbehci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/watermarks.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/watermarks.c

## Role

Small utility for tracking current and high-water values with a configured maximum.

## Functions

`initmark` clears a `Watermark`, assigns its max, and stores a display name. `notemark` clamps an input value to `[0, max]`, updates `curr`, raises `highwater` when appropriate, and increments `hitmax` when the max is newly hit from below. `seprintmark` formats the measurement.

## Dependencies

Uses `Watermark` from shared kernel headers and Plan 9 `seprint`.

## Risks

No locking is performed; callers must serialize updates if marks are shared across CPUs or interrupt/process contexts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/watermarks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/xalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/xalloc.c

## Role

Implements an early/kernel physical-memory-backed allocator using a fixed table of free holes. It is used for aligned low-level allocations such as descriptor tables and frame lists.

## Main Data

`Xalloc` holds a lock, a static table of 128 `Hole` records, a free-list of unused hole records, and a sorted table of available memory ranges. Allocations carry an `Xhdr` with size and `Magichole`.

## Control Flow

`xinit` divides configured memory between kernel and user page pools, limits kernel memory to `cankaddr`-addressable pages, sets `Confmem` kernel ranges, and adds kernel ranges to the hole table with `xhole`.

`xallocz` finds the first hole large enough, removes bytes from its front, writes a header, optionally zeroes, and returns user data. `xfree` validates magic and returns the whole header-sized allocation to holes. `xhole` inserts and coalesces free ranges in address order. `xspanalloc` overallocates, aligns to a requested span/alignment, and returns unused portions via `xhole`.

## Dependencies

Uses `conf`, `palloc`, `KADDR`, `PADDR`, `BY2PG`, `BY2V`, `cankaddr`, and kernel locks.

## Risks

The allocator has a fixed hole-table size; if exhausted, it logs a leak. `xspanalloc` panics on allocation failure. `xmerge` only merges adjacent allocated chunks and panics with memory dumps on bad magic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/xalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/blast.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/blast.h

## Role

Board-specific constants for the Crawford Hill Blast PowerPC board.

## Main Definitions

Defines clock input (`CLKIN` 72 MHz), memory/chip-select layout, `IMMR`, flash/DSP/SDRAM/FPGA base and size constants, `PLAN9INI`, TLB entry count, PPC PTE policy bits, SMC UART pins, and FCC Ethernet pin masks/options for multiple ports.

## Dependencies

Consumed by PPC platform initialization, MMU setup, flash, UART, and FCC Ethernet code. It assumes PPC PTE bit definitions and `BIT()` are already available.

## Risks

This is hardware-description data. Incorrect base addresses, sizes, BAT assumptions, or pin masks can cause boot failure or device misconfiguration. `MEM2SIZE` is forced to zero despite a commented 32 MiB value, so local-bus SDRAM is intentionally disabled here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/blast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/clock.c

## Role

Implements PPC clock/decrementer initialization and busy-wait delays.

## Control Flow

`clockinit` sets decrementer frequency to `m->bushz/4`, assumes time-base frequency equals decrementer frequency, calibrates delay loops, computes `clkreload`, and loads the decrementer. `clockintr` accounts elapsed decrementer ticks and reloads the decrementer, handling late interrupts by incrementing `m->ticks` by multiple reload intervals.

`delayloopinit` calibrates `m->loopconst` by measuring a 1 ms delay against the decrementer. `delay` and `microdelay` spin for approximate time using `loopconst`. `perfticks` returns `fastticks`.

## Dependencies

Uses PPC decrementer accessors `getdec`/`putdec`, `fastticks`, `HZ`, and `Mach` frequency fields.

## Risks

Timing accuracy depends on `m->bushz`, the 604e decrementer assumption, and initial loop calibration. Busy waits are CPU-local and not power efficient.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/dat.h

## Role

PPC machine-dependent core type and structure definitions used before and alongside `portdat.h`.

## Main Definitions

Defines architecture versions of `Lock`, `Label`, floating-point save state, memory configuration (`Confmem`, `Conf`), process MMU state (`PMMU`), notification save state, fake `KMap`, and the PPC `Mach` structure. `Mach` includes fields known by assembly for processor id, current proc, TLB miss counters, plus clocks, MMU state, scheduler state, performance, interrupt stats, and stack.

Also defines global `active` state, `ISAConf` parsed configuration entries, interrupt vector control `Vctl`, and externs for `mach0`, register globals `m` and `up`, and `initfp`.

## Dependencies

Included by most PPC kernel sources. Must stay consistent with assembly offsets in `l.s`, FP save/restore routines, and shared `../port/portdat.h`.

## Risks

Layout changes can break assembly. `active` is defined in this header, so include discipline matters. Fake kmap macros assume direct kernel mapping via `KZERO`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devce.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devce.c

## Role

Skeleton Plan 9 device driver for “channel element” DSP-like devices on a Saturn/UCU board.

## Main Data

Defines UCU/DSP state constants, qid types, CPLD register layout, circular buffer and DSP structs, and a global `Ce` containing UCU type and up to 16 DSP/channel entries. CPLD is mapped at `Saturn + 0x6000000`; CE memory at `Saturn + 0x3000000`.

## Control Flow

`ceinit` checks the CPLD UCU version bit and records `Ucu64`, otherwise prints unsupported UCU. The device exposes `#C` with `cectl` and `ce0` through `ce15` entries via `cegen`. Open marks the channel open; read supports directory reads only; writes are a no-op returning 0.

## Dependencies

Uses Plan 9 `Dev` interface, `msaturn.h`, and standard device helpers.

## Risks

This driver is incomplete. Data-file reads and writes report unsupported/no-op behavior, and several qid constructions appear inconsistent (`QID(Qce, i)` uses type/device fields in a surprising order). It is mainly scaffolding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devce.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devether.c

## Role

Architecture-local Plan 9 Ethernet device frontend for `#l`, built on the generic `netif` layer and pluggable hardware reset routines.

## Main Data

`etherxx[MaxEther]` stores active controllers. `cards` registers hardware types through `addethercard`. Each controller is an `Ether` from `etherif.h`, with queue, callbacks, addresses, stats, and `Netif`.

## Control Flow

Attach parses an optional controller number and calls hardware attach. Walk/stat/open/read/write mostly delegate to `netif`. `etheriq` receives frames, filters multicast/promiscuous/destination matches, fans packets out to matching `Netfile`s, supports bridge/headersonly tracing, and frees or returns the input block. `etheroq` handles outbound frames, loops back local/broadcast/promiscuous packets, queues non-loopback frames, and calls the hardware transmit callback.

`etherreset` reads `etherN` config, matches registered cards, applies configured `ea=`, invokes hardware reset, wires interrupts, initializes `netif` and output queue, and prints device info. `ethercrc` computes Ethernet multicast CRC.

## Dependencies

Depends on `netif`, `etherif.h`, `Block` queues, `intrenable`, `isaconfig`, and hardware drivers such as `etherfcc.c` or `ethersaturn.c`.

## Risks

Packet fanout can allocate copies per consumer and increment overflow counters on failure. Hardware callback correctness is assumed. `parseether` accepts fixed two-hex-digit bytes and does limited validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devflash.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devflash.c

## Role

Implements Plan 9 `#F/flash` access to CFI NOR flash, with partition control files and Intel/Sharp Extended command-set programming support.

## Main Data

`Flash` records physical mapping, CFI algorithm id, manufacturer/device ids, write-buffer size, erase regions, boot protection, and offset in concatenated flash space. `FPart` exposes up to 8 named partitions plus `namectl` files. Width/interleaving macros adapt `Funit`/`Fword` access and byte order.

## Control Flow

`cfiquery` enters CFI query mode, validates `"QRY"`, reads algorithm id, total size, write-buffer size, and erase-region geometry. `flashinit` scans `flashN` configs, maps memory, identifies supported algorithms, enables boot protection, and creates whole-device partitions.

The device exposes a top directory and `flash` directory. Reads of data partitions copy mapped flash bytes under read lock and require `eve`. Control reads report offset, size, write-buffer size, ids, and region geometry. Control writes support `erase`, `add`, `remove`, and `protectboot off`. Data writes validate partition bounds, preserve unaligned surrounding bytes, split writes at erase-block and `Maxwchunk` boundaries, invoke the algorithm write routine, and verify with `memcmp`.

Intel/Sharp erase and buffered write commands are implemented with program-power toggling, status polling, error decoding, and reset. AMD/Fujitsu identify is present, but erase/write return unimplemented errors.

## Dependencies

Uses Plan 9 device API, locks, CFI flash command sequences, `flashprogpower`, `isaconfig`, `iseve`, and board memory mappings.

## Risks

Flash writes are destructive and require erase discipline. Boot protection only protects the first erase region unless disabled. AMD/Fujitsu programming is not implemented. Some command parsing uses `atoi`. There is no dynamic partition locking separate from flash lock beyond name nil checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devflash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devirq.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devirq.c

## Role

Exposes board external IRQ lines, a millisecond timer, and FPGA reset through a Plan 9 device.

## Main Data

`irqdir` exposes `irq1` through `irq7`, `mstimer`, and `fpgareset`. `Irqconfig` tracks enable state, level/edge or timer interval mode, interrupt counts, wait rendezvous, a linked-list node, and embedded `Timer`. Global `irqconfig[NIRQ]` maps qids to waiter lists.

## Control Flow

Opening an IRQ file allocates an `Irqconfig`; closing disables it and frees state. Writes parse commands: `interrupt on/off`, `mode level/edge` or timer interval, `reset`, `wait`, and `debug`. Enabling a hardware IRQ links the config and installs `intrenable` on `IRQ0 + irq`; enabling `mstimer` installs a periodic timer. Reads block until the interrupt count changes, then return count and mode/interval. The interrupt handler clears pending external IRQ bits, increments all linked configs, and wakes waiters.

## Dependencies

Uses MPC8260 interrupt registers in `iomem`, Plan 9 timers, `intrenable`/`intrdisable`, `fpgareset`, and command parsing helpers.

## Risks

Several `irqdir` entries for irq3-irq7 have qid `{Qirq1}`, which looks like a copy-paste bug. Hardware register writes are board-specific. Each open gets independent counters, but shared interrupt mode is global hardware state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devirq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devtls.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devtls.c

## Role

Implements Plan 9 `#a/tls`, a kernel TLS 1.0 / SSL 3.0 record-layer device layered over an existing open channel. User-space handshake code drives protocol setup through control commands, while this device encrypts/decrypts records.

## Main Data

`TlsRec` stores the underlying channel, state, negotiated version, byte counters, inbound/outbound `OneWay` cipher state, pending application data, raw unprocessed bytes, handshake queue, ownership, and permissions. `Secret` describes one cipher/MAC direction. Supported record types, alerts, and state bits are local enums. The device keeps a growable table of up to 1024 conversations.

Supported algorithms are `clear`, `rc4_128`, `3des_ede_cbc` and MACs `clear`, `md5`, `sha1`, with SSL3 custom MAC or TLS HMAC depending on version.

## Control Flow

`clone` creates a conversation. `ctl` commands bind an fd and version, set exact protocol version, install pending secrets, send ChangeCipherSpec, mark application data opened, and send alerts. `hand` exposes handshake records via a queue; `data` exposes application records; `status` and `stats` report state and counters.

Inbound `tlsrecread` reads record headers and bodies without losing sync on interrupt, accepts initial SSL2-format ClientHello, validates version and length, decrypts, checks MAC, applies cipher change, queues handshake records, handles alerts, or stores application data. Outbound `tlsrecwrite` fragments to `MaxRecLen`, prepends headers, computes MAC, encrypts, and writes blocks to the underlying channel.

## Dependencies

Depends on Plan 9 device, queue, block, fd/channel APIs and `<libsec.h>` RC4, DES3, MD5, SHA1, HMAC helpers.

## Risks

Only legacy SSL3/TLS1.0-era algorithms are supported. CBC padding/MAC handling is hand-coded and comments acknowledge timing-attack concerns. State transitions rely on user-space handshake correctness. `tlshangup` frees only the head of `unprocessed` with `freeb`, not `freeblist`, if it can be a chain.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/devtls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/etherfcc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/etherfcc.c

## Role

Hardware Ethernet driver for MPC8260 FCC Ethernet controllers, registered as Ethernet card type `"fcc"`.

## Main Data

Defines FCC Ethernet buffer descriptor bits, FCC mode/event bits, `Etherparam` matching parameter RAM, and `Ctlr` holding FCC identity, port, MII GPIO pins, ring state, receive buffers, PHY state, timer, and hardware statistics. Uses 128 RX and 128 TX descriptors with cache-line-aligned receive buffers.

## Control Flow

`reset` validates CPU speed and port, allocates controller state and descriptor rings, allocates RX buffers, runs `fccsetup`, and wires Ethernet callbacks. `fccsetup` configures board port pins and clock routing for FCC1-3, initializes parameter RAM, sets station address, clears events, enables FCC events, issues `InitRxTx`, allocates/probes MII, and starts autonegotiation.

`attach` enables RX/TX and starts a periodic link timer. `transmit` calls `txstart`, which dequeues outbound blocks into TX descriptors and hands them to hardware. `interrupt` handles RX frames, RX errors, TX completions/errors, descriptor freeing, restart-on-error, and stats. `ifstat` prints driver and PHY state. MII read/write is bit-banged over configured port pins. `fccltimer` updates link speed and duplex from PHY status.

## Dependencies

Depends on `imm.h`, `blast.h` pin masks, descriptor-ring helper `ioringinit`, CPM command `cpmop`, cache flush/zap functions, `etherif.h`, and `ethermii`.

## Risks

Descriptor/data cache coherence is critical. TX path panics on unexpected descriptor or alignment state. Multicast filtering falls back to promiscuous behavior. MII bit-banging uses fixed delays and assumes MDIO pins on port 3 in read/write helpers, despite setup differences.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/etherfcc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/etherif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/etherif.h

## Role

Defines the PPC Ethernet controller interface shared by `devether.c` and hardware drivers.

## Main Definitions

`MaxEther` is 24 and `Ntypes` is 8. `Ether` embeds `ISAConf`, controller identity, MTU bounds, Ethernet address, hardware callbacks (`attach`, `transmit`, `interrupt`, `ifstat`, `ctl`), controller-private pointer, output queue, and `Netif`.

It declares `etheriq`, `addethercard`, and `ethercrc`, plus ring index macros `NEXT` and `PREV`.

## Risks

Hardware drivers are responsible for filling callbacks and `ctlr` consistently before registration. The queue and netif lifecycle is handled by `devether.c`, so drivers must not bypass those expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.c

## Role

Generic MII/PHY probing, reset, autonegotiation, and link-status helper for Ethernet drivers.

## Control Flow

`mii` scans PHY addresses from a mask, skips already-known PHYs, reads ID registers, filters invalid OUIs, allocates `MiiPhy`, initializes advertised capability caches, and selects the first PHY. `miimir` and `miimiw` call the current PHY read/write callbacks. `miireset` sets BMCR reset.

`miiane` checks autonegotiation support, chooses advertised 10/100 and optionally 1000Base-T capabilities from caller overrides, cached values, or PHY status registers, writes `Anar` and `Mscr`, then enables/restarts autonegotiation. `miistatus` reads status twice, determines link, speed, duplex, and pause-flow-control result from negotiated local/partner capabilities.

## Dependencies

Depends on `ethermii.h` register bits and driver-supplied `Mii.mir`/`Mii.miw`.

## Risks

Memory for discovered PHYs is never freed here. Status depends on cached advertisement fields being initialized through `miiane`. Return values are simple `-1/0`, so callers must decide how much degradation to tolerate.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.h

## Role

Defines MII register numbers, bit masks, and data structures for generic PHY management.

## Main Definitions

Includes BMCR/BMSR, PHY ID, autonegotiation, master/slave 1000Base-T, and extended-status registers. Bit masks cover reset, loopback, power-down, autonegotiation, 10/100/1000 capabilities, pause/asymmetric pause, and link partner status.

`Mii` stores PHY count, mask, per-address `MiiPhy` pointers, current PHY, controller pointer, and read/write callbacks. `MiiPhy` stores OUI, address, cached advertisement/flow-control/master-slave settings, status, link, speed, duplex, and flow-control result.

## Interfaces

Declares `mii`, `miiane`, `miimir`, `miimiw`, `miireset`, and `miistatus`.

## Risks

The header abstracts register access only; drivers must supply correct bus timing and serialization. Constants assume standard IEEE MII register layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ethersaturn.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ethersaturn.c

## Role

Ethernet hardware driver for the Saturn board Ethernet block, registered as card type `"saturn"`.

## Main Data

Maps Saturn Ethernet control/status, interrupt, MAC, and MII registers. Uses a fixed packet memory window at `Ethermem`, with 14 RX slots and 2 TX slots. `Ctlr` tracks TX ring state, RX last index, active flag, interrupt count, and overflow stats. A default global `etheraddr` is provided.

## Control Flow

`reset` disables RX, allocates controller state, installs callbacks, reads MAC address from hardware, enables RX and interrupts, and marks active. `transmit` locks the controller, fills TX packet memory from the output queue, and starts transmission if idle. `interrupt` acknowledges events, handles TX done/retry state, loops over RX slots until hardware index catches up, allocates blocks for received frames, sends them to `etheriq`, and logs unhandled interrupts.

## Dependencies

Depends on `msaturn.h`, `etherif.h`, Plan 9 queues/blocks, and board interrupt `Vecether`.

## Risks

Uses fixed shared packet memory and small TX ring. Some interrupt conditions only log. MII registers are defined but not used in this file. `reset` prints register state during initialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ethersaturn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/fns.h

## Role

PPC architecture function prototype header, extending `../port/portfns.h`.

## Contents

Declares CPU/register accessors, cache controls, delay and clock routines, trap/interrupt setup, MMU/TLB routines, floating-point save/restore, PCI config helpers, console/debug output, process save/restore, timers, alignment validation, and platform helpers. Defines `userureg`, `waserror`, `KADDR`, `PADDR`, `coherence`, `idlehands`, and no-op `kmapinval`.

## Dependencies

Used by nearly all PPC kernel C files. Many declarations correspond to assembly implementations or platform-specific code.

## Risks

Duplicate prototypes exist for several functions (`geticmp`, `puticmp`, `putsdr1`). Macro correctness for `KADDR`/`PADDR` underpins physical/virtual address handling across low-level drivers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/imm.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/imm.h

## Role

Register and data-structure map for the MPC8260 internal memory map, CPM, communication controllers, buffer descriptors, and command encodings.

## Main Definitions

Defines interrupt vector numbers, generic buffer descriptor layout and flags, ring descriptor state, MCC/IOC/SCC/FCC parameter RAM structures, SCC/FCC/SMC/SPI register layouts, memory-controller bank maps, I/O ports, IDMA, parameter-base areas, UART SMC parameter RAM, serial interface registers, and the large `RegMap`/`IMM` layout matching documented offsets.

Also defines `FCCextra`, CPM command register fields, sub-block/page codes, operation codes such as `InitRxTx`, channel IDs like `FCC1ID`, and clock route identifiers.

## Interfaces

Declares global `IMM *imm`, `uartsmcoffset[]`, and low-level helpers `bdalloc`, `cpmop`, `ioplock`, `iopunlock`, and `kreboot`.

## Dependencies

Consumed by CPM serial, FCC Ethernet, IRQ, timers, and board code. Requires offset accuracy against MPC8260 hardware documentation and surrounding macros such as `SBIT`.

## Risks

This is a hardware ABI. Structure packing, reserved padding sizes, and field widths must remain exact. Any compiler/layout drift can redirect hardware accesses to wrong registers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/imm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/init9.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/init9.s

## Role

Tiny PPC assembly entry wrapper equivalent to calling `startboot(argv0, &argv0)`.

## Control Flow

`_main` sets the static base register `R2` with `setSB(SB)`, allocates a small frame, stores incoming `argv0` from `R3` on the stack, passes its address as the second argument, branches to `startboot`, then loops forever if it returns.

## Dependencies

Uses Plan 9 PPC assembler syntax and ABI assumptions: `R3` holds first argument, `R2` is SB, and `startboot` is available.

## Risks

This exists specifically to avoid C runtime dependencies before SB setup. Stack offsets are ABI-sensitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/io.h

## Role

Defines generic bus type encodings and helpers for PPC kernel device identifiers.

## Main Definitions

Enumerates bus types including ISA, PCI, PCMCIA, VME, and `BusPPC`. Defines `MKBUS(t,b,d,f)` to pack type, bus, device, and function into a `tbdf`, with extractors `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`, and sentinel `BUSUNKNOWN`.

## Dependencies

Used by device configuration and drivers such as Ethernet to tag controller bus identity.

## Risks

The bit layout is shared convention. Incorrect packing/extraction would break PCI/device matching and printed hardware identity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/io.h -->