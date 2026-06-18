# Group Research: group_24_9front_sources_os_plan9_9front_sys_src_9_port_sdnvme_c_sources_os_pla_db4b94858fb3

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdnvme.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sdnvme.c

Plan 9 `SDifc` block driver for PCI NVMe controllers.

Key responsibilities:
- Discovers PCI NVMe controllers by class code, maps BAR0 registers, validates NVM command-set support, and chooses a controller memory page size.
- Builds admin and I/O submission/completion queues, including one shared completion queue and per-CPU submission queues when possible.
- Issues NVMe commands through `qcmd()`/`wcmd()`, waits through per-command `WS` records, and completes them from `nvmeintr()`.
- Implements block reads/writes in `nvmebio()` using NVMe read/write opcodes and splits transfers around PRP/page constraints.
- Presents NVMe namespaces as Plan 9 `sd` units, faking enough SCSI inquiry/read-write behavior for the shared disk stack.
- Identifies controller and namespace data, fills unit geometry, model, serial, firmware, and namespace sector size.
- Adds a per-unit `smart` file that fetches and formats NVMe SMART / health log page data.

Dependencies:
- Uses Plan 9 kernel PCI, interrupt, DMA, rendezvous, and `sd` infrastructure.
- Calls shared SCSI emulation helpers `sdfakescsi()` and `sdfakescsirw()`.
- Uses `mallocalign`, `dmaflush`, `PCIWADDR`, `intrenable`, `pcisetbme`, and `vmap`.

Notable behavior:
- Admin commands serialize through the controller `QLock`; I/O commands choose a queue by `m->machno % ctlr->nsq`.
- Interrupts mask enabled completion vectors while processing and unmask afterward.
- Namespace list fallback assumes namespace `1` if namespace-list identify fails.
- Disable path requests normal shutdown, disables the controller, tears down interrupts/DMA, and frees queues plus identify buffers.

Research notes:
- The driver supports only simple PRP use: first PRP plus optional second PRP, so `nvmebio()` limits chunk size to fit that model.
- `readsmart()` prints 64-bit counters using the low 64 bits of NVMe 128-bit SMART fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdnvme.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdram.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sdram.c

Plan 9 `SDifc` RAM disk driver backed by reserved physical memory exposed through a segment.

Key responsibilities:
- Supports up to four `ramdiskN` devices configured through kernel configuration strings.
- Parses size values with `K`, `M`, `G`, and `T` suffixes, with optional `+`/`-` adjustment syntax.
- Allocates RAM disk pages either from the end of existing memory banks or by excluding a fixed physical range from `conf.mem`.
- Creates a physical cached, no-exec segment for each online RAM disk.
- Exposes RAM disks as `sd` units with SCSI-style inquiry data and geometry reporting.
- Implements raw block I/O through `segio()`, including sector-size and page-offset handling.
- Implements `rio` by delegating fake SCSI handling and fake SCSI read/write parsing to shared helpers.

Dependencies:
- Uses kernel memory-bank configuration, `Segment`, `Segio`, `Physseg`, and the port `sd` layer.
- Calls `newseg()` and `segio()` from the segment subsystem.

Notable behavior:
- Default sector size is 512 bytes.
- `ramdiskX=size`, `ramdiskX=size ss`, and `ramdiskX=base size ss` are supported.
- The reported alignment includes page size and sector offset derived from the original base address.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdscsi.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sdscsi.c

Shared SCSI helper layer for Plan 9 `sd` device drivers.

Key responsibilities:
- Verifies a SCSI unit by issuing INQUIRY and TEST UNIT READY, with not-ready/no-medium handling.
- Attempts START STOP UNIT for direct-access devices to spin up disks after successful readiness checks.
- Reads capacity using READ CAPACITY(10), falling back to READ CAPACITY(16) for large devices.
- Normalizes device geometry, including converting returned last-LBA to sector count and fudging ATAPI 2352-byte sectors to 2048.
- Builds READ(10)/WRITE(10) or READ(16)/WRITE(16) CDBs for block I/O.
- Provides retry/error classification for common sense keys and ASC/ASCQ cases.
- Detects removable-media change and clears `unit->sectors` to force re-online.

Dependencies:
- Calls the concrete device interface through `unit->dev->ifc->rio`.
- Uses Plan 9 `SDreq`, `SDunit`, status constants, sense flags, and shared allocation helpers.

Notable behavior:
- `scsionline()` retries capacity reads up to 10 times and returns `ok + retries`, preserving retry information in the status value.
- `scsibio()` turns SCSI sense data into Plan 9 errors containing sense key/ASC/ASCQ and sector number.
- The code comments note LUN handling as questionable in several CDB fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdscsi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdvirtio10.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sdvirtio10.c

Plan 9 `SDifc` driver for non-legacy Virtio 1.0 block and SCSI devices.

Key responsibilities:
- Discovers Virtio PCI devices with modern IDs for block and SCSI device types.
- Parses Virtio PCI capability structures and maps common, notify, ISR, and device-specific config regions.
- Resets devices, acknowledges driver status, negotiates minimal feature bits, allocates virtqueues, and publishes descriptor/avail/used rings.
- Implements vring descriptor allocation, completion processing, wakeup, and notify writes.
- Implements virtio-blk request submission, including read, write, and flush-like request handling.
- Implements virtio-scsi command submission with CDB, response, sense, data, and residual handling.
- Presents virtio-blk and virtio-scsi devices through the Plan 9 `sd` interface.
- Delegates virtio-scsi online/verify/bio paths to the shared SCSI helpers.

Dependencies:
- Uses `virtio10.h` accessors and `Vio` mapped-register abstraction.
- Uses PCI discovery/config helpers and Plan 9 `sd` plus SCSI helper routines.
- Uses `PADDR`, `coherence`, interrupts, and kernel rendezvous sleep.

Notable behavior:
- The driver exists specifically for modern virtio devices where legacy I/O-port transport is disabled.
- Block devices are assigned IDs from `'F'`; virtio-scsi devices from `'0'`.
- For virtio-scsi, queue 2 is used for command traffic.
- Completion paths free descriptor chains and clear per-request `rock` records.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdvirtio10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/segment.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/segment.c

Core Plan 9 process segment, page-table, image-cache, and segment-backed I/O implementation.

Key responsibilities:
- Allocates and frees `Segment` objects, including inline or heap segment maps.
- Frees segment pages, swap entries, profile buffers, and associated executable image references.
- Duplicates segments for fork semantics, including shared text/physical segments, copy-on-write BSS/data/stack handling, and text conversion for `TSEG`.
- Inserts pages into segment PTE maps with `segpage()` and relocates pages when moving segments.
- Maintains executable image cache by channel identity with hash and idle lists.
- Reclaims idle images and their pages under `imagereclaim()`.
- Implements `ibrk()` and `mfreeseg()` for data/BSS growth and partial segment freeing.
- Registers and finds named physical segments and implements user `segattach()`.
- Implements `segflush()`/`syssegflush()` for text-cache flushing and executable page invalidation.
- Maintains text profiling counters in `segclock()`.
- Converts between text and data segment forms via `txt2data()` and `data2txt()`.
- Implements `segio()` using a helper kernel process that temporarily maps the segment into its address space and copies data.

Dependencies:
- Uses process segment arrays, `Page`, `Pte`, swap, MMU flush, image/channel identity, and Plan 9 error infrastructure.
- Interacts with `sysproc.c` segment syscalls and `sdram.c` RAM disk I/O.

Notable behavior:
- `putseg()` holds the image lock while dropping the segment ref to prevent races with image cache reuse.
- `ibrk()` refuses to shrink a shared segment because another process may already have passed addresses to the kernel.
- `segattach()` can resolve global segments through `_globalsegattach` before looking up physical segment names.
- `segio()` copies through a bounce buffer when the caller buffer is user-space, avoiding faults in the helper process.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/swcursor.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/swcursor.c

Software cursor drawing support for framebuffer-backed screens.

Key responsibilities:
- Maintains backing store for the screen rectangle underneath the cursor.
- Maintains cursor image and mask images in GREY8 and GREY1 forms.
- Hides the cursor by restoring saved screen contents and optionally flushing the affected rectangle.
- Avoids drawing overlap with arbitrary rectangles by hiding and scheduling a mouse redraw.
- Draws the cursor by saving the destination pixels, drawing the masked cursor, and flushing the combined old/new rectangle.
- Converts Plan 9 `Cursor` `set`/`clr` bitmaps into image/mask planes.
- Initializes or reinitializes cursor backing images for the current `gscreen`.

Dependencies:
- Uses draw/memdraw kernel interfaces, `gscreen`, `flushmemscreen`, and `mouseredraw`.

Notable behavior:
- Comments acknowledge that kernel prints can call cursor routines without the usual draw lock; the code relies on reentrant `memimagedraw`, accepting possible cursor artifacts.
- Cursor image allocation failure prints but leaves nil checks in draw/hide paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/swcursor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/syscallfmt.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/syscallfmt.c

System call argument and return formatter for Plan 9 syscall tracing.

Key responsibilities:
- Builds human-readable syscall entry strings in `syscallfmt()`.
- Builds syscall return strings, error strings, and timing data in `sysretfmt()`.
- Formats user strings safely after `validaddr()` checks and bounded NUL search.
- Formats read/write buffers as pointer plus printable ASCII preview, replacing non-printables with dots.
- Handles per-syscall argument layouts for file, process, segment, mount, read/write, stat, and compatibility syscalls.
- Stores trace text in `up->syscalltrace` under `up->debug`.

Dependencies:
- Uses syscall number/name tables from `/sys/src/libc/9syscall/sys.h`.
- Uses process debug locks, `validaddr`, `evenaddr`, `fmtstrinit`, `fmtstrflush`, and Plan 9 syscall argument conventions.

Notable behavior:
- Read/write data previews are capped at 64 bytes.
- `EXEC` traces argv by walking user pointers until nil.
- Return formatting knows which syscalls return pointers and which should use `up->syserrstr` on failure.
- A source comment notes “WE ARE OVERRUNNING SOMEHOW,” but the code itself bounds copied string/data previews.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/syscallfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sysfile.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sysfile.c

Plan 9 file, descriptor, namespace, directory, mount, and stat syscall implementation.

Key responsibilities:
- Manages file descriptor allocation, growth, duplication, close-on-exec flags, and descriptor-to-channel lookup.
- Implements `pipe`, `dup`, `open`, `create`, `close`, `read`, `pread`, `write`, `pwrite`, `seek`, and old seek compatibility.
- Implements directory reads across union mounts and rewrites directory entries at mount points to match mounted channels.
- Uses `dirrock` to store directory entries that overflow after mount rewriting.
- Validates stat buffers and names for `stat`, `fstat`, `wstat`, and `fwstat`.
- Implements `chdir`, `bind`, `mount`, old `mount`, `unmount`, and namespace mount semantics.
- Prevents removal or renaming of mount points to avoid ambiguity.
- Implements legacy fixed-size stat packing for old binaries.

Dependencies:
- Uses channel/name resolution (`namec`, `walk`, `devtab`, `cmount`, `cunmount`, `findmount`), process file groups, and mount-head locks.
- Relies on Plan 9 Dir/stat wire-format helpers and error strings.

Notable behavior:
- File descriptor table growth is capped; exceeding descriptor hundreds can print a warning.
- Directory read offsets distinguish `c->devoffset` from logical `c->offset` because mount rewriting can change returned byte counts.
- `write()` advances the channel offset before calling the device and rolls back on error or short write.
- `bindmount()` closes the mounted fd after successful mount.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sysproc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sysproc.c

Plan 9 process, exec, notification, segment, rendezvous, semaphore, time, and syscall dispatch implementation.

Key responsibilities:
- Implements `rfork` for both in-place group changes and new process creation.
- Duplicates or shares process segments, file groups, namespace groups, rendezvous groups, and environment groups according to rfork flags.
- Implements `exec`, including `#!` interpreter chaining, a.out header parsing, stack/TOS/argv construction, image cache attachment, segment replacement, close-on-exec, and register setup.
- Implements sleep/yield, alarms, exits, wait/await, errstr exchange, and notify/noted delivery.
- Implements segment syscalls: `segbrk`, `segattach`, `segdetach`, `segfree`, and old `brk`.
- Implements Plan 9 rendezvous by matching sleeping processes by tag in the rendezvous group hash.
- Implements user semaphores with segment-local wait lists, compare-and-swap, blocking/timed acquire, release, and careful wakeup race handling.
- Implements nanosecond time syscall compatibility.
- Implements central syscall dispatch in `dosyscall()`, including argument validation, syscall tracing stop points, error-to-return conversion, and `NOTED` special handling.

Dependencies:
- Interacts heavily with segment/image code, file groups, process groups, scheduler, note/trap architecture hooks, EDF scheduling, and syscall tables.
- Includes generated syscall table definitions through `systab.h`.

Notable behavior:
- `sysexec()` uses a temporary `ESEG` stack until commit, then relocates it to `SSEG`.
- Interpreter recursion is limited to 8 levels.
- User semaphore commentary documents subtle sleep/wakeup races and notes verification with a Spin model.
- `dosyscall()` swaps `errstr`/`syserrstr` on failure so user `errstr` sees the correct error.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sysproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/taslock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/taslock.c

Test-and-set spin lock and interrupt lock implementation.

Key responsibilities:
- Implements normal spin locks with `lock()`, `unlock()`, and `canlock()`.
- Implements interrupt-level locks with `ilock()` and `iunlock()`, saving/restoring interrupt priority state.
- Tracks lock owner process, CPU, caller PC, interrupt-lock status, and last lock fields for diagnostics.
- Prevents scheduling while normal locks are held through `up->nlocks`.
- Emits diagnostics for long lock loops, wrong unlock type, changed owner process, unlock of unlocked lock, and interrupt unlock while interrupts are low.
- Supports optional `LOCKCYCLES` instrumentation for max/cumulative lock hold cycles.

Dependencies:
- Uses architecture `tas`, `splhi`, `splx`, `islo`, `coherence`, scheduler, EDF fields, and process dump helpers.

Notable behavior:
- On uniprocessor EDF priority inversion, `lock()` yields by adjusting the admitted process deadline.
- `unlock()` may call `sched()` if scheduling was delayed while locks were held.
- `ilock()` spins by temporarily restoring the previous spl level while waiting, then reacquiring at high priority.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/taslock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/thwack.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/thwack.c

Thwack encoder: compact LZ77-style block compressor with acknowledged history-window support.

Key responsibilities:
- Initializes encoder block windows and per-block hash tables.
- Records acknowledgements so only decoder-known history blocks are used for compression.
- Builds a history list from current block plus recently acknowledged predecessor blocks.
- Uses multiplicative hashing over three-byte sequences to find candidate matches.
- Encodes literals with adaptive literal history and encodes matches as length plus history offset.
- Emits sequence-delta and mask bytes so the decoder can reconstruct the history set.
- Tracks compression statistics: input bytes, output bytes, literals, matches, offset bits, length bits, delay, and history.
- Rejects blocks that are too large, too small, output larger than input buffer, or insufficiently compressible midway.

Dependencies:
- Uses definitions and window structures from `thwack.h`.

Notable behavior:
- Current source block is copied into the encoder window before compression.
- The encoder only uses acknowledged history blocks, preventing references to data the decoder may not have.
- Match length and offset use custom variable-length coding tables, not a generic Huffman tree despite the local `Huff` table name.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/thwack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/thwack.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/thwack.h

Shared interface and constants for thwack compression and decompression.

Key elements:
- Declares `Thwack`, `Unthwack`, `ThwBlock`, and `UnthwBlock`.
- Defines block/window sizing: `ThwMaxBlock`, encoder/decoder window blocks, compression-history block count, and hash table size.
- Defines minimum match length and match-offset coding parameters.
- Defines sequence-mask limits used to advertise history state.
- Defines encoder and decoder block structs with sequence numbers, data pointers, hash tables, acknowledgement flags, and byte limits.
- Declares public functions for initialization, compression, acknowledgement, decompression, and decoder state reporting.

Dependencies:
- Used by `thwack.c` and `unthwack.c`.

Notable behavior:
- Encoder and decoder windows are intentionally different sizes: 22 encoder blocks and 32 decoder blocks.
- `CompBlocks` limits a compressed packet to current data plus up to nine history blocks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/thwack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/tod.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/tod.c

Time-of-day and fast tick conversion implementation.

Key responsibilities:
- Initializes the time-of-day state from `fastticks()` and registers periodic overflow correction.
- Maintains fixed-point multipliers/dividers for converting between fast ticks, nanoseconds, and microseconds.
- Allows the fast clock frequency to be updated through `todsetfreq()`.
- Sets absolute time or gradual clock adjustments through `todset()`.
- Computes epoch nanoseconds in `todget()` while clamping normal reads so time does not move backward.
- Optionally returns raw fast ticks and monotonic nanoseconds.
- Converts between time-of-day nanoseconds, fast ticks, microseconds, milliseconds, and seconds.
- Builds 64-bit fractional conversion constants in `mk64fract()`.

Dependencies:
- Uses architecture `fastticks`, `mul64fract`, kernel clock ticks, `addclock0link`, and interrupt locks.

Notable behavior:
- Assumes synchronized CPUs on multiprocessor systems; the file comments call this out as architecture-sensitive.
- `todfix()` periodically folds large fast-tick deltas into `tod.off` and `tod.last` to avoid conversion overflows.
- Monotonic time has separate `monooff`/`monolast` state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/tod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ucalloc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/ucalloc.c

Uncached-memory allocator built on a Plan 9 `Pool`.

Key responsibilities:
- Defines a dedicated `Uncached` pool with 4 MiB max size, 1 MiB arenas, 32-byte quantum, and custom lock/print/panic hooks.
- Allocates new 1 MiB arenas from normal memory and maps them uncached with `mmuuncache()`.
- Temporarily increases `mainmem->maxsize` while provisioning uncached arena memory.
- Provides `ucalloc()`, `ucallocalign()`, and `ucfree()` wrappers.
- Zeroes allocated buffers before returning them.

Dependencies:
- Uses kernel `Pool` allocator, `mallocalign`, `mmuuncache`, and interrupt-lock-backed private logging.

Notable behavior:
- `ucarena()` asserts arena size is exactly 1 MiB.
- `ucallocalign()` asserts individual allocations are smaller than `minarena - 128`.
- Pool diagnostic output is buffered under an interrupt lock and printed on unlock.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ucalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/unthwack.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/unthwack.c

Thwack decoder and decoder-history state management.

Key responsibilities:
- Initializes decoder block windows.
- Reports decoder state as newest sequence plus bitmask of nearby prior blocks.
- Inserts decoded blocks into the decoder window in sequence order, replacing the oldest slot.
- Reconstructs the encoder history set from packet sequence delta and mask bytes.
- Decodes adaptive literal encodings and variable-length match lengths.
- Decodes match offsets, finds the referenced block/data position, and copies match bytes into the current output block.
- Copies decoded output to the caller buffer and stores the block in decoder history.

Dependencies:
- Uses structures, constants, and sequence-window rules from `thwack.h`.

Notable behavior:
- Returns `-2` when required history blocks are missing and logs dropped-block information.
- Rejects malformed streams with invalid lengths, offsets beyond available history, output overflow, or insufficient bits.
- The decoder preserves separate compressed-block history from the caller-visible output buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/unthwack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/usb.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/usb.h

Common USB host-controller, endpoint, and device definitions for the Plan 9 kernel USB stack.

Key elements:
- Defines debug-print macros and little-endian 16-bit get/put helpers.
- Declares `Udev`, `Ep`, `Hci`, and `Hciimpl`.
- Defines USB constants for endpoint counts, controller counts, transfer types, speeds, request fields, standard requests, device states, and root-hub port status bits.
- Defines `Hciimpl`, the controller-driver callback table for init, interrupt, endpoint open/stop/close, endpoint read/write, debug formatting, device close, root-port operations, shutdown, and debug control.
- Defines `Hci`, embedding hardware config and the implementation callback table.
- Defines `Ep`, the shared endpoint object with endpoint identity, per-open state, transfer configuration, toggles, polling/iso parameters, timeout, and controller-private aux pointer.
- Defines `Udev`, the shared USB device object with address/state/speed/topology, transaction-translator metadata, endpoint cache, and fake root-hub state.
- Declares `addhcitype()`, `usbmodename`, `Estalled`, and `seprintdata()`.

Dependencies:
- Included by USB controller drivers such as `usbehci.c` and the generic USB device layer.

Notable behavior:
- The header documents ownership expectations: endpoint open prepares hardware state, stop cancels in-flight I/O, close releases hardware state, and stopped endpoints preserve toggles in `Ep`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/usb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/usbehci.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/usbehci.c

USB 2.0 EHCI host-controller implementation for the Plan 9 USB stack.

Key responsibilities:
- Defines EHCI hardware register bits, queue states, descriptor flags, and timing/scheduling constants.
- Defines software and hardware descriptor structures for queue heads, queue transfer descriptors, high-speed isochronous TDs, split-transaction isochronous TDs, endpoint I/O state, iso I/O state, descriptor pools, and periodic scheduling trees.
- Allocates aligned EHCI descriptors from a shared pool using controller-provided allocation hooks.
- Starts/stops the controller and initializes async plus periodic schedules.
- Builds and maintains the periodic interrupt scheduling tree with bandwidth accounting.
- Allocates, links, unlinks, and frees queue heads, including async-advance doorbell synchronization.
- Builds TD chains for control, bulk, and interrupt transfers, including embedded buffers for small transfers and DMA buffers for larger transfers.
- Implements transfer wait, timeout, cancellation, polling fallback, and interrupt completion processing.
- Implements control transfers as setup, optional data, and status phases.
- Implements bulk, interrupt, and isochronous endpoint read/write paths.
- Implements high-speed and full-speed isochronous scheduling, descriptor setup, interrupt processing, buffering, delay limiting, and cancellation.
- Handles root-hub port power, reset, enable, and status operations.
- Hands low-speed and full-speed devices off to companion controllers when EHCI should not own them.
- Exposes debug formatting for endpoints and internal dump helpers for queue/TD/iso state.
- Wires EHCI callbacks into `Hci` through `ehcilinkage()`.

Dependencies:
- Uses `usb.h`, `usbehci.h`, Plan 9 locks/rendezvous, DMA flushes, kernel memory allocators, interrupt hooks, and HCI root-port callbacks.
- Depends on controller-specific `Ctlr` fields and register definitions supplied by `usbehci.h`.

Notable behavior:
- The file comments list known limitations: many delays/ilocks, incomplete bandwidth admission control, polling required on some controllers, and missing power-overrun warnings.
- `ehcipoll()` exists because some controllers fail to post completion interrupts reliably.
- `epio()` may detect that polling is required after manually discovering a completed queue in the wait path.
- Isochronous schedules use a virtual 64-frame window replicated across the hardware frame list.
- `epstop()` preserves data toggles for bulk/interrupt endpoints so reopening can resume correctly.
- `ehcimeminit()` initializes frame lists, the async list, the periodic tree, and descriptor preallocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/usbehci.c -->