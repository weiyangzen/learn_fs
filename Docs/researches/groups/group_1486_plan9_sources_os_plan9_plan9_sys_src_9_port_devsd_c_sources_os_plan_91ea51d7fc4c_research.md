# Group Research: group_1486_plan9_sources_os_plan9_plan9_sys_src_9_port_devsd_c_sources_os_plan_91ea51d7fc4c

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devsd.c

Purpose: Generic Plan 9 storage device file server for `#S/sd*`. It discovers `SDifc` controllers, exposes controller/unit directories, partition files, control files, and raw SCSI request access.

Key logic:
- Maintains global storage-device slots named by digits/letters and adds `SDev` chains from each registered `SDifc`.
- Lazily verifies units with `ifc->verify`, enables controllers, initializes unit metadata, and creates default `data` plus boot-configured partitions.
- Encodes dev/unit/partition/type into `Qid.path` and implements attach, walk, stat, open, read, write, wstat, configure, and unconfigure.
- `sdbio` maps partition byte I/O to sector-aligned `ifc->bio` calls, including read-modify-write for unaligned writes.
- `sdrio` and the `raw` file implement direct SCSI-like command/data/status exchange through `ifc->rio`.
- `sdfakescsi`, `sdsetsense`, and `sdmodesense` emulate common SCSI commands for non-SCSI disk drivers.
- Top-level `sdctl` dispatches modern `wtopctl` commands and a legacy `config` parser for controller probing/removal.

Dependencies and integration:
- Depends on `../port/sd.h`, generated `sdifc[]`, Plan 9 device helpers, `DevConf`, partition permission state, and driver callbacks such as `pnp`, `probe`, `enable`, `disable`, `verify`, `online`, `bio`, `rio`, `rctl`, and `wctl`.

Risks and notes:
- `sdbio` has subtle media-change recovery and locking differences for removable vs non-removable media.
- Raw command state is serialized per unit and exclusive-opened.
- Partition `qid.vers` combines unit and partition versions to detect media/partition changes.
- `sdgetdev` can return nil; one error path calls `decref` after nil detection, which is suspicious.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsdp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devsdp.c

Purpose: Secure Datagram Protocol device `#E`, providing encrypted/authenticated/compressed datagram conversations over an underlying packet channel. It exposes clone, per-conversation control/data/control-channel files, status, stats, remote stats, and log files.

Key structures:
- `Sdp`: per-attached filesystem state with conversation table and log.
- `Conv`: conversation state machine, owner/permissions, underlying channel, local/remote stats, retry timers, algorithms, and one-way input/output state.
- `OneWay`: sequence/window state, control-message state, cipher/auth/compression state.
- `Algorithm`, `CipherRc4`, and `AckPkt` implement selectable transforms and stats acknowledgements.

Key logic:
- `sdpclone` allocates/reuses a conversation and initializes permissions and sequence window.
- Control writes configure `dial`, `accept`, simulated `drop`, `cipher`, `auth`, `comp`, `insecret`, and `outsecret`.
- Connection state machine handles open request/ack/ack-ack, close/close-ack, reset, retries, keepalives, and timeout closure.
- Data packets carry type/subtype and 24-bit sequence numbers with wrap tracking, duplicate/reorder detection, optional auth, optional cipher, and optional thwack compression.
- Reliable control channel keeps one outstanding control packet, retransmits until acknowledged, and propagates stats in control ACKs.
- Background `sdpackproc` scans conversations once per second for retry/keepalive work.
- `convreader` drains the underlying channel when no data file is open so control traffic can still progress.

Dependencies and integration:
- Uses Plan 9 `netif.h`, `Log`, `Block`, `Queue`-like block I/O, `libsec` MD5/SHA1/DES/RC4, and `thwack` compression.

Risks and notes:
- Algorithms are old: DES, RC4, MD5 HMAC, SHA1 HMAC.
- State transitions are lock-sensitive and use background reader processes plus timer scanning.
- Sequence window is 32 packets; older packets are rejected and duplicates counted.
- The file is protocol implementation rather than a general filesystem component, despite living under `port`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsdp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsegment.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devsegment.c

Purpose: Global shared-segment device `#g`. It lets users create named global segment directories, assign virtual address/length metadata, attach them through `segattach`, and read/write segment memory via a helper kernel process.

Key logic:
- Maintains up to 100 `Globalseg` objects with name, uid, permission, optional `Segment`, and a command rendezvous pair.
- `create` on the top directory creates a named segment directory.
- `ctl` accepts `va base length`, rounds to page boundaries, and creates an `SG_SHARED` segment with `newseg`.
- `data` reads/writes copy bytes through `segmentkproc`, whose address space maps the segment and executes `memmove` on requested offsets.
- `_globalsegattach` is installed so normal VM segment attach logic can find named global segments.

Dependencies and integration:
- Uses VM `Segment`, `newseg`, `putseg`, `isphysseg`, `isoverlap`, `segattach` hook, process segments, and Plan 9 device operations.

Risks and notes:
- Data I/O relies on a per-segment kproc to safely access the mapped virtual addresses.
- Segment deletion removes the global table entry and decrefs the object, but open refs keep it alive.
- Permissions are managed on `ctl`/`data`; directory perms are broadly listed as `0777`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsegment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devsrv.c

Purpose: Service registry device `#s`. It lets processes post already-open file descriptors under names so other processes can open those names and receive the underlying channel.

Key logic:
- `create` creates a named service entry and assigns an incrementing qid path.
- `write` to the newly created file parses an fd number, obtains the channel with `fdtochan`, rejects close-on-exec/remove-on-close and auth files, and stores it.
- `open` of an existing service replaces the lookup channel with the posted channel after permission and mode checks.
- `remove` unlinks service entries with special restrictions for `eve`-owned services and `boot`.
- `wstat` allows owner/eve to change permission, owner, and name.

Dependencies and integration:
- Uses Plan 9 `Chan` reference counting, `fdtochan`, `devwalk/devstat`, qid generation, and service lookup helper `srvname`.

Risks and notes:
- Posted channel mode must match requested open mode unless the posted channel is `ORDWR`.
- Service entries exist before a channel is posted; opening an unposted service returns shutdown.
- Removal rules protect system services more strongly than personal services.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devssl.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devssl.c

Purpose: Legacy SSL-style record-layer device `#D/ssl`. It wraps an existing fd, exposes per-conversation `ctl`, `data`, `secretin`, `secretout`, `encalgs`, and `hashalgs`, and applies SSL record framing, optional digesting, and optional encryption.

Key structures:
- `Dstate`: connection state, underlying channel, input/output `OneWay` crypto state, record buffers, owner, and permissions.
- `OneWay`: secret, message id, encryption/hash state, and locks.

Key logic:
- Clone/open creates up to 512 digest/encryption states.
- `ctl` commands set `fd`, configure `alg`, or set base64 secrets.
- `secretin`/`secretout` write raw secrets.
- `data` reads parse SSLv2-like record headers, decrypt, verify digest, remove padding, and return plaintext.
- `data` writes split data into SSL records, add digest and padding, encrypt, and write to the underlying channel.
- Supports clear, digest-only, encryption-only, and digest-plus-encryption modes.

Dependencies and integration:
- Uses `libsec` MD4/MD5/SHA1, DES, RC4, Plan 9 block I/O, and channel wrapping via `fdtochan`.

Risks and notes:
- Cryptography is obsolete: DES, RC4, MD4/MD5/SHA1, including 40-bit variants.
- `NOSPOOKS` enables broader algorithm list.
- Interrupts during writes can desynchronize the remote record stream.
- This is older than `devtls.c` and implements SSL framing rather than modern TLS semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devssl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devtls.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devtls.c

Purpose: TLS 1.0 / SSL 3.0 record-layer device `#a/tls`. It wraps an existing fd and exposes record-protected `data`, handshake `hand`, `ctl`, `status`, `stats`, and algorithm-list files.

Key structures:
- `TlsRec`: per-record-layer connection, state, protocol version, underlying channel, statistics, handshake queue, processed/unprocessed input, in/out secrets, owner, permissions.
- `OneWay`: input/output I/O lock, secret lock, sequence number, current secret, and pending secret.
- `Secret`: cipher/MAC algorithm names, encrypt/decrypt callbacks, unpadding callback, MAC callback, block size, MAC key, and cipher key.
- `TlsErrs`: maps internal alert IDs to SSL3/TLS alert codes and user-facing messages.

Key logic:
- `clone` creates a TLS record object; opening `hand` allocates a handshake queue.
- `ctl` commands configure `fd`, negotiated `version`, pending `secret`, `changecipher`, `opened`, `alert`, and `debug`.
- `tlsrecread` parses records, including initial SSL2-format ClientHello compatibility, enforces version/length limits, decrypts, verifies MAC, handles change-cipher-spec, alerts, handshake queueing, and application data.
- `tlsrecwrite` frames handshake/application/alert/change-cipher records, computes MAC, encrypts, changes output cipher at the correct byte boundary, and writes to the underlying channel.
- `hand` reads deliver handshake messages and alert/error messages to user-level handshake code.
- Supports `clear`, `rc4_128`, `3des_ede_cbc`, `aes_128_cbc`, `aes_256_cbc`; MACs are `clear`, `md5`, and `sha1`.
- Provides SSL3 custom MAC packing and TLS HMAC packing.

Dependencies and integration:
- Uses Plan 9 block/channel I/O, `Queue`, `libsec` RC4/3DES/AES/MD5/SHA1/HMAC, and state transitions coordinated by locks and qlocks.

Risks and notes:
- Protocol support is capped at TLS 1.0/SSL3-era mechanisms.
- Record read has explicit interrupt-regurgitation handling to avoid losing consumed header bytes.
- CBC unpadding includes TLS strict pad validation; the comment acknowledges timing-sensitive MAC/pad errors.
- `status` and `stats` expose state, algorithm names, and byte counters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devtls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devuart.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devuart.c

Purpose: Generic UART device `#t` for serial ports discovered by architecture-specific `PhysUart` drivers. It exposes `eiaN`, `eiaNctl`, and `eiaNstatus` files for each port.

Key logic:
- `uartreset` calls each `physuart[i]->pnp`, builds a flat UART list and directory table, enables console/special ports, and starts a periodic staging timer.
- `uartenable` opens input/output queues, initializes staging buffers, default line settings, physical hardware, and enabled-list membership.
- `uartopen` enables ports on first data/control open; `uartclose` drains output, closes queues, disables hardware, and clears hangup flags on final close.
- `uartread` returns queued input, port number, or physical status.
- `uartwrite` sends data to the output queue or parses control commands.
- `uartctl` supports baud, bits, stop bits, parity, break, DTR/RTS, modem control, FIFO, queue limits, nonblocking output, hangup, flush, timer period, and software flow control.
- Interrupt-time helpers `uartrecv`, `uartkick`, and `uartstageoutput` bridge physical UART drivers with generic queues.
- `uartclock` batches staged input, handles hangups, and restarts output after flow-control backoff.

Dependencies and integration:
- Depends on generated `physuart[]`, `PhysUart` methods, `Queue`, `Timer`, console globals (`kbdq`, `serialoq`, `consuart`), and Plan 9 device helpers.

Risks and notes:
- Input staging is intentionally timer-flushed to reduce per-character interrupt overhead.
- Output draining before line-setting changes can sleep and is used broadly in `uartctl`.
- Software XON/XOFF and hardware backoff interact through `blocked`, `cts`, and `ctsbackoff`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devuart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devwd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devwd.c

Purpose: Watchdog framework device `#w/wdctl`. It registers a platform watchdog, optionally auto-starts it, lets users enable/disable/restart it, and disables it at shutdown.

Key logic:
- `addwatchdog` installs one global `Watchdog` and disables it initially.
- `wdinit` auto-enables the watchdog unless `*nowatchdog` is set.
- Auto-pet mode adds a clock callback that periodically calls `restart` while watchdog is on.
- Opening `wdctl` stops auto-petting and transfers control to user processes.
- Closing the final `wdctl` reference disables the watchdog.
- Reads call optional `wd->stat`; writes accept `enable`, `disable`, and `restart`.

Dependencies and integration:
- Uses platform `Watchdog` callbacks, `addclock0link`, `getconf`, Plan 9 device helpers, and exported `watchdog/watchdogon` globals for code that must pause long busy loops.

Risks and notes:
- Only one watchdog can be installed.
- User control disables automatic petting to avoid two independent owners.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/ecc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/ecc.c

Purpose: NAND flash ECC calculation and correction for 256-byte data chunks.

Key logic:
- `nandecc` computes a 24-bit ECC using a 256-entry lookup table and line/parity accumulation.
- `nandecccorrect` compares calculated and stored ECC, detects no error, correctable one-bit data error, one-bit ECC error, or uncorrectable multi-bit error.
- Correctable data errors flip the identified byte/bit and update the stored ECC.

Dependencies and integration:
- Includes `nandecc.h`; intended for NAND flash drivers and flash filesystem code.

Risks and notes:
- Corrects only single-bit data errors or single-bit ECC-storage errors.
- Optional reporting prints diagnostic details.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/ecc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/edf.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/edf.c

Purpose: Earliest Deadline First scheduling support for Plan 9 processes with admitted real-time parameters.

Key logic:
- `edfinit` allocates per-process `Edf` state and installs time formatting.
- `edfadmit` validates period/cost/deadline, runs schedulability testing, marks the process admitted, synchronizes release time with same-period admitted tasks when possible, and schedules release/deadline timers.
- `release`, `releaseintr`, and `deadlineintr` manage periodic/sporadic releases, deadlines, rescheduling, and wakeups.
- `edfrun` arms a timer for the earlier of deadline or remaining CPU slice.
- `edfrecord` accounts used time against EDF or extra time and forces deadline when slice is exhausted.
- `edfready` inserts admitted processes into `runq[PriEdf]` ordered by earliest deadline or delays them until release.
- `edfyield` sleeps until the next release.
- `edfstop` expels a process and deletes timers.
- `testschedulability` simulates release/deadline events up to `Maxsteps`.

Dependencies and integration:
- Uses kernel `Proc`, `Timer`, run queues, trace hooks, scheduler state, `µs()`, `todge`t, and `edf.h`.

Risks and notes:
- Time is tracked in low-order microseconds, so wrap behavior is implicit.
- Schedulability testing is bounded and can return “probably not schedulable”.
- Locking is split between `edfschedlock` for admission parameters and `thelock` for runtime EDF state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/edf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/edf.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/edf.h

Purpose: Public EDF scheduler declarations and per-process EDF state structure.

Contents:
- Defines `Maxsteps`, EDF flag bits (`Admitted`, `Sporadic`, `Yieldonblock`, `Sendnotes`, `Deadline`, `Yield`, `Extratime`), and `Infinity`.
- Defines `struct Edf` with deadline/period/cost/slice fields, release/deadline timestamps, schedulability-test links, flags, embedded `Timer`, and accounting counters.
- Declares `edflock` and `edfunlock`.
- Registers format-check pragmas for EDF time formats.

Dependencies and integration:
- Requires `Proc` and `Timer` definitions from kernel headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/edf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/error.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/error.h

Purpose: Shared extern declarations for kernel error-string symbols.

Contents:
- Declares common Plan 9 kernel error strings such as mount errors, filesystem lookup errors, permission errors, fd errors, I/O errors, memory errors, networking errors, media-change errors, USB endpoint errors, and AoE-down errors.
- Used by kernel/device code to raise stable textual errors through `error()` without duplicating string definitions.

Dependencies and integration:
- Consumed broadly by device, filesystem, VM, and syscall code.
- `mkerrstr` transforms this file into error-string definitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fault.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/fault.c

Purpose: Architecture-neutral virtual memory fault handling, demand paging, copy-on-write, address validation, and segment lookup.

Key logic:
- `fault` locates the user segment for an address, rejects invalid/write-to-readonly faults, and calls `fixfault`.
- `fixfault` handles segment types: text demand load, BSS/shared/stack zero-fill, data demand/page-in/copy-on-write, and physical mappings.
- `pio` loads pages from executable image or swap, handles races while segment locks are dropped, caches loaded pages, and zero-fills short image pages.
- `okaddr` and `validaddr` validate syscall user ranges across segments and post debug notes on invalid access.
- `vmemchr` searches memory while validating crossed user pages.
- `seg` finds a segment containing an address, optionally returning it locked.
- `checkpages` debug-checks mapped pages against MMU state.

Dependencies and integration:
- Uses `Segment`, `Page`, `Pte`, swap/image page cache, `newpage`, `putmmu`, `devtab` reads, process notes, and machine fault counters.

Risks and notes:
- `pio` deliberately drops the segment lock around I/O and rechecks races afterward.
- Copy-on-write behavior depends on page refs and swap refs.
- Physical segments can call architecture-specific page allocators.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fault.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/flashif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/flashif.h

Purpose: Shared flash/NAND interface definitions for Plan 9 flash drivers and `devflash`-style code.

Contents:
- Defines logical `Flashpart`, physical `Flashregion`, per-chip `Flashchip`, and runtime `Flash`.
- `Flash` includes card type, mapped address, size, XIP flag, reset hook, erase/read/write/suspend/resume/attach hooks, width/interleave/command parameters, partition table, protection state, and flash sort.
- Declares flash card registration, architecture flash reset/write-protect, width-aware flash accessors, and NAND-specific architecture hooks.

Dependencies and integration:
- Used by architecture flash probes, CFI/NAND/NOR/serial drivers, and flash device code.

Risks and notes:
- Header defines the contract only; hardware drivers fill function pointers and geometry.
- NAND hooks abstract claim/power, CLE/ALE, byte reads, and byte writes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/flashif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fpi.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/fpi.c

Purpose: Software floating-point interpreter arithmetic over the internal representation defined in `fpi.h`.

Key logic:
- `fpiround` implements guard-bit rounding with carry propagation.
- `matchexponents`, `shift`, `normalise`, and `renormalise` align and normalize operands/results.
- `fpiadd`, `fpisub`, `fpimul`, and `fpidiv` implement IEEE-like addition, subtraction, multiplication, and division with NaN/infinity/zero handling.
- `fpicmp` compares internal floating values, including signed zero, infinities, and NaNs.
- Note in file warns `fpisub` and `fpidiv` argument order computes `y-x` and `y/x`.

Dependencies and integration:
- Uses only `fpi.h`; designed as portable arithmetic support where hardware floating point is absent or trapped.

Risks and notes:
- Internal precision uses two 28-bit chunks plus guard bits.
- Some weird cases intentionally return quiet NaN.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fpi.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/fpi.h

Purpose: Type definitions, constants, macros, and prototypes for the floating-point interpreter.

Contents:
- Defines `Word`, `Vlong`, `Single`, and `Double` mapping to `FPdbleword`.
- Defines fraction, carry, hidden-bit, guard-bit, exponent-bias, and infinity constants.
- Defines `Internal` representation with sign, exponent, low fraction, and high fraction.
- Provides macros for zero, NaN, infinity tests and setters.
- Declares arithmetic routines from `fpi.c` and conversion routines from `fpimem.c`.

Dependencies and integration:
- Includes `<u.h>` if needed and assumes Plan 9 floating bit layout types.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fpimem.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/fpimem.c

Purpose: Memory-format conversions between native single/double/integer values and the `Internal` format used by the floating-point interpreter.

Key logic:
- `fpis2i` and `fpid2i` decode IEEE single/double bit layouts into `Internal`.
- `fpiw2i` and `fpiv2i` convert signed 32-bit and 64-bit integers to `Internal`.
- `fpii2s` and `fpii2d` round and encode internal values to single/double memory formats.
- `fpii2w` and `fpii2v` round and convert internal values back to signed integer types, saturating on overflow.

Dependencies and integration:
- Includes `fpi.h`; explicitly depends on memory format, not CPU arithmetic.

Risks and notes:
- Output conversions mutate the supplied `Internal`; caller should pass a disposable copy.
- 64-bit conversion uses shifts that assume the interpreter’s fraction constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/fpimem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/initcode.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/initcode.c

Purpose: Tiny initial user-mode boot code that sets up minimal namespace bindings and execs `/boot/boot`.

Key logic:
- Opens `#c/cons` three times for standard input/output/error.
- Binds console, environment, and service devices onto `/dev`, `/env`, and `/srv`.
- Executes `/boot/boot` with supplied argv.
- On failure, captures `rerrstr` into a stack buffer and exits with that message.

Dependencies and integration:
- Uses user-space Plan 9 libc calls but warns not to add library calls because the text image must fit in one page and has no data segment assumptions.

Risks and notes:
- Static string data exists in this source, but comment stresses size and data constraints for the boot image.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/initcode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/latin1.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/latin1.c

Purpose: Latin-1/compose-key style rune lookup helper.

Key logic:
- Builds `latintab[]` by including `latin1.h`.
- `unicode` parses hex digits after `X`/`x` prefixes into a rune value.
- `latin1` maps a sequence of 2 or 3 runes to a composed rune, returns `-1` on invalid sequence, or a negative required-length value when more input is needed.
- Handles `X` as fixed 4-hex-digit input and `x` as `UTFmax*2` hex digits.

Dependencies and integration:
- Uses `Rune` and `UTFmax` from port library definitions.
- Used by keyboard/console compose logic.

Risks and notes:
- Relies on ordering and prefix assumptions documented at the top of the file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/latin1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/latin1.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/latin1.h

Purpose: Data table included by `latin1.c` to implement compose-key mappings.

Contents:
- Contains 100 table entries of lead sequence, selectable input characters, and corresponding rune string.
- Covers punctuation/math symbols, accented Latin letters, Greek letters, Cyrillic letters, fractions, chess/music symbols, currency symbols, arrows, set operators, and other Plan 9 compose mappings.

Dependencies and integration:
- Intended to be included inside `latintab[]`; it is not a standalone C header with guards.

Risks and notes:
- Entry order matters because `latin1.c` assumes prefixes appear earlier when one lead sequence prefixes another.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/latin1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/lib.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/lib.h

Purpose: Kernel-side declarations and constants for libc-like routines and user-visible Plan 9 ABI structures.

Contents:
- Defines utility macros `nelem`, `offsetof`, and `assert`.
- Declares memory, string, UTF/rune, formatting, conversion, tokenization, base64 decode, qsort, and miscellaneous libc-derived routines.
- Defines UTF constants, mount flags, open flags, note actions, `ERRMAX`, `KNAMELEN`, qid type bits, dir mode bits.
- Defines `Qid`, `Dir`, old wait message, and wait message structures.
- Provides vararg-check pragmas for kernel formatting.

Dependencies and integration:
- Included throughout port and architecture kernel code.
- Bridges kernel code to libc-style helper implementations linked into the kernel.

Risks and notes:
- `assert(x)` stringifies as literal `"x"` in this header’s macro.
- This file carries ABI-shaped definitions used by filesystem/device code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/log.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/log.c

Purpose: Shared in-kernel circular log buffer implementation for devices such as `devsdp`.

Key logic:
- `logopen` allocates a default 4 KiB ring buffer and initializes pointers on first open.
- `logclose` frees the buffer on final close.
- `logread` blocks until at least `minread` bytes are available, then copies from the circular buffer with wrap handling.
- `logctl` accepts `set`/`clear` followed by named flags and updates `logmask`.
- `logn` appends raw bytes if the mask is enabled and log is open, dropping oldest bytes on overflow.
- `log` formats into a stack buffer then calls `logn`.

Dependencies and integration:
- Uses `Log` and `Logflag` structures from kernel headers, `Rendez`, `QLock`, and `Lock`.

Risks and notes:
- Logs are not retained when no file is open.
- Messages larger than the log buffer are silently dropped by `logn`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkbootrules -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkbootrules

Purpose: rc/awk build helper that generates mk rules for embedding boot directory files as root images.

Key logic:
- Reads kernel config sections and collects entries under `bootdir`.
- Produces rules for `$CONF.root.s` using `../port/mkrootall`.
- Produces rules for `$CONF.rootc.c` using `../port/mkrootc`.
- Sanitizes file paths into C symbol names by replacing non-alphanumeric/underscore characters.

Dependencies and integration:
- Uses `rc`, `awk`, `$objtype`, `$CONF`, and kernel config file format.

Risks and notes:
- Assumes `bootdir` section indentation and section-boundary conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkbootrules -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkdevc -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkdevc

Purpose: rc/awk generator for kernel device configuration C source.

Key logic:
- Parses config sections `dev`, `ip`, `link`, `misc`, and `port`.
- Emits includes, external `Dev` declarations, `devtab[]`, link initializers, architecture table, storage interface tables, UART physical driver table, VGA tables, IP protocol init table, custom port lines, `conffile`, and `kerndate`.
- Tracks special devices (`ad`, `sd`, `uart`, `vga`) to emit matching support arrays.
- On 386/alpha/amd64, emits i8237 DMA allocator state when any device asks for `dma`.

Dependencies and integration:
- Uses `rc`, `awk`, config files, `$objtype`, `pwd`, and generated kernel build C.

Risks and notes:
- Section parsing is indentation-sensitive.
- Device names are transformed into symbol names by convention, e.g. `foo` -> `foodevtab`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkdevc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkdevlist -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkdevlist

Purpose: rc/awk helper that emits object-file names needed by a kernel config.

Key logic:
- Parses `dev`, `misc`, `link`, and `ip` sections.
- Emits device object names as `dev<name>.$O`; other listed object names as `<name>.$O`.
- Includes extra object dependencies from additional fields unless marked with `+`, `=`, or `-` prefixes.
- Adds `bios32.$O` for 386 when `pci.$O` is present.

Dependencies and integration:
- Uses `$objtype` and config section conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkdevlist -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkerrstr -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkerrstr

Purpose: Tiny rc/sed generator that converts `error.h` extern declarations into string definitions.

Key logic:
- Reads `../port/error.h`.
- Removes `extern`.
- Converts comments into assigned string literal values.

Dependencies and integration:
- Depends on the exact `error.h` declaration/comment shape.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkerrstr -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkextract -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkextract

Purpose: rc helper for extracting a numbered field from a named section in one or more config files.

Key logic:
- Usage: `mkextract [-u] field n file...`.
- Finds indented lines under a top-level section named by `field`.
- Prints field `n` from those lines.
- With `-u`, sorts uniquely.

Dependencies and integration:
- Uses `rc`, `awk`, `sort`, and kernel config indentation rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkextract -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkfilelist -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkfilelist

Purpose: rc helper that lists `.c` files in a directory excluding files already present in the current directory.

Key logic:
- With one argument, builds a regex from local `*.c`.
- Lists `*.c` in the target directory, filters out matching local files, removes `.c` suffixes, and joins names with `|`.
- If local `*.c` glob is literal, lists all target `.c` files.

Dependencies and integration:
- Uses `rc`, `ls`, `grep`, and `sed`.

Risks and notes:
- Intended for build-rule generation; output is a regex-style alternation string.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkfilelist -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkroot -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkroot

Purpose: rc helper that embeds one boot file as an assembly root image.

Key logic:
- Usage: `mkroot path name`.
- Copies the file to `name.out`.
- Strips it if `file` reports it as executable.
- Runs `aux/data2s name` to produce `name.root.s`.

Dependencies and integration:
- Uses Plan 9 `file`, `strip`, `aux/data2s`, and build naming conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkroot -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkrootall -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkrootall

Purpose: rc helper that embeds multiple boot files as assembly data.

Key logic:
- Arguments are repeated triples: `name cname file`.
- Validates argument count is a multiple of three.
- Copies each file to a temp file, strips executables except `venti`, and emits assembly with `aux/data2s cname`.
- Removes temp file on exit.

Dependencies and integration:
- Used by `mkbootrules` to build `$CONF.root.s`.

Risks and notes:
- Does not emit the boot link table; `mkrootc` handles C registration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkrootall -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkrootc -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mkrootc

Purpose: rc generator that emits C code linking embedded boot-file data into the kernel.

Key logic:
- Arguments are repeated triples: `name cname file`.
- Emits standard kernel includes.
- Declares `extern uchar <cname>code[];` and `extern ulong <cname>len;`.
- Emits `bootlinks()` that calls `addbootfile(name, cnamecode, cnamelen)` for each boot file.

Dependencies and integration:
- Paired with `mkrootall` output and used by generated `mkbootrules`.

Risks and notes:
- It parses filenames only to emit names/symbols; actual file contents are embedded elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mkrootc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mksystab -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mksystab

Purpose: rc/sed/sam generator for syscall declarations and syscall name tables.

Key logic:
- Reads `/sys/src/libc/9syscall/sys.h`.
- Emits include, `typedef long Syscall(ulong*)`, and syscall function declarations.
- Generates `systab[]` indexed by syscall numbers, mapping unused `SYS_X*` entries to `sysdeath`.
- Generates `sysctab[]` string names, with some display-name rewrites.
- Emits `nsyscall`.

Dependencies and integration:
- Uses Plan 9 `sed`, `tr`, and `sam`; depends on exact formatting of libc syscall header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mksystab -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mul64fract.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/mul64fract.c

Purpose: Portable C fallback for `mul64fract`, returning the middle 64 bits of a 64x64 -> 128-bit product.

Key logic:
- Splits both 64-bit operands into high/low 32-bit halves.
- Accumulates the middle product terms:
  `hi(al*bl) + al*bh + ah*bl + lo-shifted ah*bh`.
- Stores the fixed-point product result in `*r`.

Dependencies and integration:
- Includes `<u.h>` for `uvlong`.
- Intended to be replaced by architecture-specific assembler where available.

Risks and notes:
- Written for fixed-point multiplication where one operand’s integer portion is in the high word and fraction in the low word.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/mul64fract.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/nandecc.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/nandecc.h

Purpose: Public NAND ECC interface for `ecc.c`.

Contents:
- Defines `NandEccError` values: bad, good, corrected one-bit data error, and corrected one-bit ECC error.
- Declares `nandecc` for 256-byte buffers.
- Declares `nandecccorrect` for checking/correcting a 256-byte buffer given calculated and stored ECC plus optional reporting.

Dependencies and integration:
- Used by NAND flash code that needs ECC generation and correction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/nandecc.h -->