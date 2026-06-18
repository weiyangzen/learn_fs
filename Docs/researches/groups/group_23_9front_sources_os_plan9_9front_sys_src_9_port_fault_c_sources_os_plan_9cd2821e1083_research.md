# Group Research: group_23_9front_sources_os_plan9_9front_sys_src_9_port_fault_c_sources_os_plan_9cd2821e1083

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/fault.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/fault.c

Portable Plan 9 user fault handling, demand paging, copy-on-write, physical segment mapping, and user address validation.

Key responsibilities:
- Converts trap/fault conditions into notes or process exits through `faultnote()` and `faulterror()`.
- Loads missing text/data/swap pages in `pio()`, including multi-page block reads through device `bread`.
- Resolves segment faults in `fixfault()` for text, data, bss, shared, stack, sticky, fixed, and swapped pages.
- Performs copy-on-write for writable data pages when references or image-cache ownership require private copies.
- Maps `SG_PHYSICAL` segments through `mapphys()` using physical segment attributes.
- Implements the top-level `fault()` loop, including segment lookup, permission checks, low-priority retry, and process-control handling.
- Provides syscall address validation helpers: `okaddr()`, `validaddr()`, `vmemchr()`, `seg()`, and `checkpages()`.

Important behavior:
- Text pages are mapped read-only and cached; writable segments set `PG_MOD|PG_REF`, optionally `PG_PRIV`.
- Stack demand-fill uses byte value `0xfe`; bss/shared use zero-fill.
- On I/O errors while page-in is running, non-interrupt errors become fatal user faults.
- The read/access parameter also drives execute-permission checks for no-exec or non-flushable pages.
- `fixfault()` releases the segment lock before calling `putmmu()`.

Dependencies:
- Depends on `Segment`, `Pte`, `Page`, `Image`, swap helpers, page-cache helpers, `putmmu()`, device read paths, and process note/error machinery.

Notable risks:
- The ternary expression in the permission check is compact and precedence-sensitive.
- `pio()` deliberately unlocks and relocks the segment around I/O, so it must retry because another process or the pager may have raced.
- Physical mappings build a temporary stack `Page` only to satisfy `putmmu()` metadata needs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/fault.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/flashif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/flashif.h

Shared flash-memory driver interface for NOR, NAND, serial flash, and logical flash partitions.

Key contents:
- Defines `Flashpart` for up to 8 logical partitions.
- Defines `Flashregion` for erase-block regions, including erase/page size shifts and spare bytes for ECC.
- Defines `Flashchip` for physical chip geometry, IDs, interleave width, CFI algorithm, and protection state.
- Defines the main `Flash` object with a `QLock`, type/address/size fields, reset hooks, erase/read/write/suspend/resume/attach callbacks, geometry, partitions, and private driver data.
- Declares registration, architecture reset/write-protect, generic flash access, and architecture NAND access routines.

Role:
- Provides the contract between `devflash`, flash-type drivers, and architecture-specific glue.
- Carries both bus-level geometry and flash-operation callback tables.

Notable constraints:
- Region and partition counts are fixed-size arrays.
- NAND operations are intentionally split into architecture callbacks for CLE/ALE, claim/power, byte write, and byte read.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/flashif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/i2c.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/i2c.h

Generic I2C/SMBus interface header for controller and device registration plus common transfer helpers.

Key contents:
- Defines `I2Cbus` with name, speed, private controller pointer, init callback, combined I/O callback, probe flag, and `QLock`.
- Defines `I2Cdev` with bus pointer, 10-bit-address flag, address, subaddress, and device size.
- Declares bus/device registration and lookup APIs.
- Declares generic send/receive helpers over addressable devices.
- Declares SMBus-style quick, byte, word, and 32-bit read/write helpers.

Role:
- Keeps controller drivers, device clients, and generic SMBus helpers behind a small portable interface.

Notable constraints:
- The core bus operation is one callback `io(dev, pkt, olen, ilen)`, so controller implementations own transaction semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/i2c.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/initcode.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/initcode.c

Tiny first user program embedded into the kernel to construct the initial namespace and exec `/boot/boot`.

Key responsibilities:
- Binds core devices into `/dev`, `/fd`, `/env`, `/proc`, `/srv`, and `/shr`.
- Opens `/dev/cons` three times for standard input, output, and error.
- Executes `/boot/boot` with the provided boot argv.
- On exec failure, reads the error string and exits with that message.

Important behavior:
- The file warns not to add library calls because the whole text image must fit in one page and no data segment is available.
- It uses global string literals for mount paths and device specs, including `#σ` for shared memory.

Dependencies:
- Built into architecture startup paths as `initcode[]`.
- Uses Plan 9 user syscalls through libc stubs: `bind`, `open`, `exec`, `rerrstr`, `_exits`.

Notable risks:
- Size and data-segment constraints are strict; ordinary-looking additions can break boot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/initcode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/iomap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/iomap.c

I/O port range allocator and `/dev/arch/ioalloc` reporting support.

Key responsibilities:
- Tracks allocated and reserved I/O ranges in a sorted linked list of `IOMap` entries.
- Initializes a small static free-list of map records in `iomapinit()`.
- Reserves future allocation windows with `ioreserve()` and `ioreservewin()`.
- Allocates I/O port ranges with `ioalloc()`, including consumption of reserved ranges.
- Releases ranges with `iofree()`.
- Checks whether a range is unused except for reservations through `iounused()`.
- Exposes a text dump through the `ioalloc` arch file.

Important behavior:
- `iomap.mask` defines valid address bits and rounding/alignment for an architecture.
- `ioalloc(-1, ...)` reserves and then allocates a free range above `0x400`.
- Tags are truncated to 12 visible characters.

Notable risks:
- The range list assumes correct sorted insertion by callers walking insertion points.
- A collision prints the conflicting range and returns `-1`; it does not attempt relocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/iomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/led.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/led.c

Common LED state string conversion and simple control-file read/write helpers.

Key responsibilities:
- Maps IBPI LED state enum values to names like `normal`, `locate`, `fail`, and `rebuild`.
- Converts state names back to enum values.
- Implements `ledr()` to read the current LED state as text.
- Implements `ledw()` to parse a control write and update `Ledport.led`.

Dependencies:
- Uses `parsecmd()` and Plan 9 error `Ebadarg`.
- Paired with `led.h`.

Notable risks:
- `ledw()` updates only the software `Ledport` state; hardware application is left to the embedding driver.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/led.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/led.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/led.h

Common LED state definitions and helper prototypes.

Key contents:
- Defines `Ledport` with LED count, active LED state, and implementation-dependent LED bits.
- Defines IBPI-inspired LED states from `Ibpinone` through `Ibpifailarray`.
- Declares `ledname`, `name2led`, `ledr`, and `ledw`.

Role:
- Provides a small portable API for storage/enclosure-style LED state reporting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/led.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/lib.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/lib.h

Kernel-visible subset of libc declarations, formatting definitions, syscall constants, and core public structs.

Key contents:
- Defines `nelem`, `offsetof`, and kernel `assert`.
- Declares memory, string, UTF/rune, random, formatting, conversion, tokenization, and sorting helpers.
- Defines `Fmt` and vararg format checking pragmas.
- Defines Plan 9 mount/open/note constants.
- Defines `Qid`, `Dir`, old `OWaitmsg`, and `Waitmsg`.
- Defines Qid and Dir permission/type bits.

Role:
- Provides libc-like APIs to portable kernel C files without exposing full user libc.
- Supplies shared userspace/kernel ABI structs and constants used throughout the port layer.

Notable constraints:
- Some prototypes use older Plan 9 pointer types without `const`.
- The file intentionally aggregates declarations for code linked “complete, from libc.”
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/log.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/log.c

Generic circular action log used by devices/subsystems that expose readable debug/event logs.

Key responsibilities:
- Lazily allocates a circular buffer on first open and frees it on last close.
- Serializes readers with `readq`.
- Blocks reads until at least `minread` bytes or requested bytes are available.
- Supports `set` and `clear` log control messages against named `Logflag` masks.
- Appends raw buffers with `logn()` and formatted strings with `log()`.
- Drops oldest data when the circular buffer would overflow.

Important behavior:
- Logging is skipped unless the mask is enabled and the log has open readers.
- Oversized single log records larger than the buffer are dropped.
- Readers receive wrapped data through two `memmove()` operations when needed.

Notable risks:
- `logctl()` silently ignores unknown flag names but rejects malformed verbs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/memmap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/memmap.c

Generic physical/firmware memory map allocator with typed regions and allocated overlays.

Key responsibilities:
- Stores up to 256 `Mapent` records with address, size, and type.
- Adds free/typed regions through `memmapadd()`.
- Normalizes overlaps in `sort()`, where higher type values take precedence and adjacent equal regions merge.
- Marks allocations by overlaying `type|Allocated` records in `memmapalloc()`.
- Frees allocated subranges through `memmapfree()`.
- Reports next matching region and size through `memmapnext()` and `memmapsize()`.
- Dumps normalized map entries with `memmapdump()`.

Important behavior:
- Allocation can request a specific address or first-fit by type and alignment.
- `Allocated` is the high bit and is masked out from requested types before allocation.
- `sort()` can insert split tail entries while resolving overlaps, then repeats until stable.

Notable risks:
- Fixed 256-entry storage can reject complex maps or heavily fragmented allocation history.
- `memmapfree()` only succeeds when the supplied range lies inside a matching allocated entry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/memmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkbootrules -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkbootrules

`rc`/`awk` generator for mkfile rules that embed `bootdir` files into kernel root images.

Key responsibilities:
- Parses configuration sections, collecting indented entries from `bootdir`.
- Derives filesystem-visible names and C-safe symbol names.
- Emits rules for `<CONF>.root.s` using `mkrootall`.
- Emits rules for `<CONF>.rootc.c` using `mkrootc`.
- Passes all collected `name cname file` triples to the root generators.

Important behavior:
- If a bootdir entry has a second field, that is the embedded file name; otherwise basename is used.
- C symbol names replace non-alphanumeric/underscore characters with `_`.

Dependencies:
- Uses Plan 9 `rc`, `awk`, and mkfile `$target` conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkbootrules -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkdevc -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkdevc

Kernel configuration generator that emits C tables and stubs from architecture config files.

Key responsibilities:
- Parses `dev`, `ip`, `link`, `misc`, and `port` sections.
- Emits `devtab[]`, link initialization, architecture tables, AD/SD interface tables, UART tables, VGA tables, IP protocol init tables, DTrace provider tables, and config metadata.
- Handles architecture-specific DMA stubs for x86-like targets.
- Emits fallback stubs when ramdisk, VGA screen, or DTrace support is absent.
- Preserves raw lines from the `port` section into generated C.

Important behavior:
- Rejects device counts >= 256 because `Pgrp.devmask` is one byte per 8 device IDs.
- Special-cases device names/prefixes: `ad`, `sd`, `uart`, `vga`, `dtracy`, and architecture entries.
- Generates `conffile` from current working directory and config argument, and `kerndate` from `KERNDATE`.

Dependencies:
- Uses Plan 9 `rc` and `awk`.
- Generated output depends on many headers such as `dat.h`, `fns.h`, `io.h`, `sd.h`, screen headers, and IP headers.

Notable risks:
- The parser is section/indentation-sensitive.
- Generated symbol names depend directly on config tokens.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkdevc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkdevlist -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkdevlist

Small `rc`/`awk` helper that lists object files needed by a kernel configuration.

Key responsibilities:
- Parses indented entries under `dev`, `misc`, `link`, and `ip` sections.
- Prefixes device entries as `dev<name>`.
- Adds non-option secondary tokens that do not begin with `+`, `=`, or `-`.
- Prints each discovered object as `<name>.$O`.

Role:
- Feeds mkfile dependency/object lists from the same kernel config grammar used by `mkdevc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkdevlist -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkerrstr -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkerrstr

Tiny `rc`/`sed` generator for kernel error-string definitions.

Key behavior:
- Reads `../port/error.h`.
- Transforms `extern` declarations with comments into C string definitions of the form `name = "comment";`.

Role:
- Produces `errstr.h`, included by `proc.c`, so portable kernel error symbols become concrete strings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkerrstr -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkextract -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkextract

General section-field extractor for Plan 9 kernel config files.

Key responsibilities:
- Accepts `[-u] field n file...`.
- Finds indented lines under the named top-level section.
- Prints the nth field from each collected line.
- With `-u`, sorts output uniquely.

Important behavior:
- Ignores blank and comment lines.
- Ends a collection when a non-indented top-level line appears.

Role:
- Reusable build helper for deriving mkfile lists from config sections.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkextract -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkfilelist -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkfilelist

`rc` helper that lists C source basenames in a directory while excluding already-present local `*.c` files.

Key behavior:
- Takes one directory argument.
- Builds a regular expression from `*.c` in the current directory.
- Lists `*.c` in the target directory, optionally filtering out names present locally.
- Strips `.c` suffixes and joins names with `|`.

Role:
- Supports mkfile pattern/list generation for shared source directories.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkfilelist -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkroot -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkroot

Single-file root embedding helper.

Key responsibilities:
- Expects `mkroot path name`.
- Copies the input to `<name>.out`.
- Strips it if `file` reports it as executable.
- Converts bytes to assembly data with `aux/data2s`, writing `<name>.root.s`.
- Prints progress messages.

Role:
- Older/single-file variant of the boot file embedding flow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkroot -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkrootall -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkrootall

Multi-file root embedding helper that emits assembly data for each boot file.

Key responsibilities:
- Requires argument triples: `name cname file`.
- Copies each file to a temporary output.
- Strips executable files except `venti`, which intentionally keeps its symbols.
- Runs `aux/data2s <cname>` for each file.
- Removes the temporary file on exit.

Role:
- Produces assembly data symbols consumed by `mkrootc`-generated `bootlinks()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkrootall -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkrootc -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mkrootc

C generator for linking embedded boot files into the kernel boot file table.

Key responsibilities:
- Requires argument triples: `name cname file`.
- Emits kernel includes.
- Emits `extern uchar <cname>code[];` and `extern ulong <cname>len;` for every embedded file.
- Emits `bootlinks()` that calls `addbootfile(name, code, len)` for each file.

Role:
- Bridges `mkrootall` assembly data into the runtime boot file registry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mkrootc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mksystab -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mksystab

System-call table generator from `/sys/src/libc/9syscall/sys.h`.

Key responsibilities:
- Emits syscall include and `typedef uintptr Syscall(va_list);`.
- Generates external syscall function declarations from `#define` names.
- Declares `sysdeath`.
- Generates indexed `systab[]` entries, mapping reserved `sys_x*` slots to `sysdeath`.
- Generates indexed `sysctab[]` syscall-name strings with selected display-name rewrites.
- Emits `nsyscall`.

Dependencies:
- Uses `sed`, `tr`, and Plan 9 `sam` scripting.
- Assumes syscall constants are in `/sys/src/libc/9syscall/sys.h`.

Notable risks:
- The generator is tightly coupled to formatting and naming in `sys.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mksystab -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mul64fract.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/mul64fract.c

Portable fallback implementation of 64-bit fixed-point fractional multiplication.

Key behavior:
- `mul64fract(r, a, b)` computes the middle 64 bits of a 128-bit product.
- Splits each operand into high/low 32-bit halves.
- Sums the cross-products corresponding to the middle result.

Role:
- Intended as a C fallback for ports without architecture assembly.
- Useful when one operand is a fixed-point number with integer bits in the high word and fractional bits in the low word.

Notable constraints:
- Comments explicitly prefer architecture-specific assembly versions where available.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/mul64fract.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/nandecc.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/nandecc.h

NAND ECC public declarations.

Key contents:
- Defines `NandEccError` values for bad ECC, good ECC, one-bit data correction, and one-bit ECC correction.
- Declares `nandecc()` over a 256-byte buffer.
- Declares `nandecccorrect()` with calculated/stored ECC and report-bad control.

Role:
- Shared header for NAND flash ECC generation and correction code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/nandecc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/netif.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/netif.c

Generic multiplexed network-interface file hierarchy and common network helper routines.

Key responsibilities:
- Initializes `Netif` instances and allocates `Netfile` slots.
- Provides a three-level devfs hierarchy with interface directory, `clone`/`addr`/`stats`/`ifstats`, and per-conversation `data`/`ctl`/`type`.
- Implements open/read/bread/write/wstat/stat/close helpers for network devices.
- Handles control commands: `connect`, `promiscuous`, `scanbs`, `bridge`, `bypass`, `headersonly`, `addmulti`, and `delmulti`/`remmulti`.
- Tracks per-open ownership and permissions.
- Manages multicast address reference counts and hardware callback transitions.
- Provides host/network byte-order helpers: `hnputv`, `hnputl`, `hnputs`, `nhgetv`, `nhgetl`, `nhgets`.

Important behavior:
- `clone` opens allocate or reuse a free conversation and redirect the channel to its `ctl`.
- `connect <type>` rejects duplicate positive types; negative types count as “all.”
- Promiscuous/scanning callbacks are enabled when first requested and disabled when last user closes.
- Per-conversation multicast tracking uses a fixed 64-bit bitmask, while interface multicast addresses are held in a linked list and hash table.

Notable risks:
- `netifclose()` iterates multicast addresses with an index variable that is not visibly incremented in the loop, so cleanup relies on current code behavior and deserves care if edited.
- The control parser truncates writes to a 63-byte local buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/netif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/netif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/netif.h

Shared structures and constants for generic network interface devices.

Key contents:
- Defines Qid types and macros `NETTYPE`, `NETID`, and `NETQID`.
- Defines `Netfile` per-conversation state: owner, mode, type, flags, multicast bitmask, and input queue.
- Defines `Netaddr` multicast address entries.
- Defines `Netif` with conversation array, address/link fields, statistics, multicast state, and hardware callbacks.
- Declares generic netif operations.
- Defines Ethernet constants and `Etherpkt`.

Role:
- Provides the common shape used by Ethernet-like drivers to expose Plan 9 network files.

Notable constraints:
- Address size is capped at `Nmaxaddr = 64`.
- Multicast hash size is fixed at 31.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/netif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/page.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/page.c

Physical page allocator, free-list manager, and image page-cache support.

Key responsibilities:
- Initializes `palloc.pages` from `conf.mem`, skipping kernel pages and invalid direct-map sentinels.
- Tracks free pages, user page count, and swap high-water/headroom thresholds.
- Allocates pages with color preference in `newpage()`, blocking/kicking pager when low.
- Frees page lists and wakes page waiters in `freepages()`.
- Reclaims unreferenced image-cache pages in `pagereclaim()`.
- Implements page refcount/free helpers: `deadpage()` and `putpage()`.
- Provides `copypage()` and `fillpage()`.
- Maintains image page cache with `cachepage()`, `uncachepage()`, `lookpage()`, and `cachedel()`.
- Clears private pages during panic/sensitive shutdown via `zeroprivatepages()`.

Important behavior:
- `newpage()` can temporarily unlock a caller-provided `QLock` while waiting and returns nil so fault code can retry after relocking.
- `lookpage()` moves found pages to the front of the hash bucket.
- Image-cached pages are not immediately freed by `deadpage()`; their image ref is decremented differently.

Notable risks:
- `zeroprivatepages()` returns early during panic without process context, relying on caller expectations.
- Page initialization assumes `conf.mem` is already stable and correctly excludes kernel ranges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/parse.c

Common control-message parser and command-table lookup helper.

Key responsibilities:
- Estimates field count for a raw byte buffer.
- Allocates one `Cmdbuf` containing pointer array plus a null-terminated copy of the command.
- Strips one trailing newline and tokenizes whitespace-delimited fields.
- Formats command errors with quoted original fields in `cmderror()`.
- Looks up `Cmdtab` entries with optional wildcard `*` and argument-count validation.

Important behavior:
- User-process command buffers larger than `READSTR` are rejected.
- UTF content is not interpreted for field splitting; whitespace bytes are ASCII-only.
- `cmderror()` does not return.

Role:
- Used throughout device control-file implementations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/pci.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/pci.c

Portable PCI discovery, configuration-space access wrappers, BAR sizing/mapping, capability handling, MSI, and power management.

Key responsibilities:
- Provides `%T` formatting for TBDF bus identifiers.
- Allocates and tracks global PCI device lists and bridge children.
- Serializes architecture PCI config reads/writes with `pcicfglock` and `pciparentdev`.
- Sizes BARs and ROM BARs by writing all ones and restoring original values.
- Recursively scans PCI buses, discovers multifunction devices, PCI-PCI bridges, CardBus bridges, and BARs.
- Validates BAR/window ranges against parent bridge windows and clears invalid mappings.
- Allocates bridge windows and BAR addresses with `pcibusmap()` and computes sizing with `pcibussize()`.
- Provides matching helpers by VID/DID or TBDF.
- Dumps PCI hierarchy and resets/disables devices.
- Manipulates command bits: I/O enable, bus master, memory-write-invalidate.
- Enumerates capabilities, including MSI, MSI-X disable, HyperTransport matching, and power management.
- Enables/disables MSI and restores devices from power states in `pcienable()`.

Important behavior:
- `pcienable()` recursively enables parent bridges before a device.
- D3 wake restores saved BARs, interrupt line, latency, cache line size, and command register.
- Bridge scans initialize secondary/subordinate buses when firmware left them zero.
- `pcidisable()` disables MSI/MSI-X and bus mastering but leaves many resources intact.

Notable risks:
- `pcidevfree()` detaches from lists but comments that memory is leaked.
- BAR/window validation and allocation are sensitive to 32-bit vs 64-bit/prefetchable flag encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/pci.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/pci.h

PCI constants, `Pcidev` structure, and public PCI helper prototypes.

Key contents:
- Defines PCI header offsets for type 0, type 1, and type 2 headers.
- Defines common class/subclass codes, capability IDs, BAR flags, and command-register bits.
- Defines `Pcidev` with TBDF, IDs/class fields, interrupt line, BAR/ROM/window resources, parent/bridge links, and cached capability offsets.
- Lists selected vendor IDs.
- Declares config-space access, scan/map/match, BAR, interrupt, command-bit, capability, MSI, power, enable/disable, and inventory functions.
- Defines bus type constants and TBDF encoding/decoding macros.
- Registers `%T` vararg formatting.

Role:
- Shared public interface between architecture PCI access code, portable PCI core, and PCI device drivers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/pci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/pgrp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/pgrp.c

Process group, rendezvous group, file descriptor group, mount, and resource-wait support.

Key responsibilities:
- Allocates/closes `Pgrp` namespace groups and `Rgrp` rendezvous groups.
- Copies namespaces with `pgrpcpy()`, preserving mount order and devmask.
- Inserts/removes mounts in process-group order chains.
- Implements device masking and `canmount()`.
- Duplicates and closes file descriptor groups.
- Handles forced file-group close when a process is killed while stuck closing channels.
- Allocates and frees `Mount` chains.
- Provides `resrcwait()` throttled resource-wait sleep with occasional console warnings.

Important behavior:
- `pgrpcpy()` locks both namespaces for write and uses temporary `Mount.norder` to preserve original order.
- `dupfgrp()` shrinks the new fd table to the current max fd rounded to `DELTAFD`.
- `forceclosefgrp()` moves outstanding channel closes to the close queue to break mount-close deadlocks.
- Masking `Devmnt` is interpreted as blocking all mounts.

Notable risks:
- Namespace copy depends on strict lock ordering and temporary mutation of source mount objects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/pgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/portclock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/portclock.c

Portable timer queue and periodic clock handling.

Key responsibilities:
- Maintains one sorted timer list per `Mach`.
- Adds and deletes relative/periodic timers with `timeradd()` and `timerdel()`.
- Runs due timers in `timerintr()`, requeueing periodic timers.
- Implements the HZ clock path in `hzclock()`: ticks, MMU flush request, accounting, DTrace tick, kmap invalidation, profiling, alarms, user profiling, and scheduling.
- Initializes the per-CPU HZ timer in `timersinit()`.
- Adds periodic CPU0 callbacks through `addclock0link()`.
- Provides overflow-safer `tk2ms()` and approximate `ms2tk()`.

Important behavior:
- Periodic timers with equal frequency can be phase-aligned.
- `timerdel()` handles the rare case where a timer callback is active on another CPU.
- A timer with `tf == nil` represents the HZ clock.
- Timers require lock ordering: `Timer` before `Timers`.

Notable risks:
- Periodic timer minimum is asserted at 100 microseconds.
- Timer callbacks run from interrupt context and must respect that environment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/portclock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/portdat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/portdat.h

Central portable kernel data-structure header for the 9front port layer.

Key contents:
- Forward-declares major kernel types and marks selected incomplete types.
- Defines lock, reference, rendezvous, qlock, rwlock, alarm, channel, path, device, directory, walk, mount, note, page, swap allocator, PTE, physical segment, segment, segio, image, process group, rendezvous group, environment group, file group, page allocator, wait queue, timer, scheduler queue, process, log, command buffer/table, UART, performance, watchdog, watchpoint, and per-mach portable state.
- Defines channel access flags, block flags, segment flags, process clone flags, process states, proc-control values, scheduler priority constants, queue state bits, global externs, and format pragmas.
- Defines key macros such as `BLEN`, `BALLOC`, `pagedout`, `swapaddr`, `PGHASH`, `MOUNTH`, and `REND`.

Role:
- This is the structural ABI tying together VM, VFS, process scheduling, device I/O, queues, timers, notes, environments, mounts, and architecture-specific process/MMU/FPU state.

Notable dependencies:
- Includes `<fcall.h>` and relies on architecture-provided `Mach`, `Label`, `Conf`, `Ureg`, `PFPU`, and `PMMU` definitions.
- Many fields are used by assembly or architecture code and are therefore layout-sensitive.

Notable risks:
- The header is a global coupling point: small field/layout changes can affect process switching, traps, MMU, devproc, and drivers.
- Comments identify several state fields as known to assembly or used for specific subsystems.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/portdat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/portfns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/portfns.h

Central portable kernel function prototype header.

Key contents:
- Declares process, scheduler, timer, VM, page, segment, channel, device, mount, environment, queue, block, PCI-independent I/O, logging, parsing, random, UART, watchdog, syscall, note, memory allocation, and utility functions.
- Defines the `waserror()`/`poperror()` error-stack macros.
- Defines time conversion macros `MS2NS` and `TK2MS`.
- Declares network byte-order helpers and low-level timing helpers.
- Adds vararg checking for `iprint`, `panic`, and `pprint`.

Role:
- Provides portable C modules with a single shared declaration surface for cross-subsystem calls.

Notable risks:
- Very broad declaration surface means stale prototypes can silently affect many modules.
- Contains a duplicate `ms2tk` declaration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/portfns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/print.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/print.c

Small formatting-library glue for kernel print serialization and unsupported `%e/%f/%g`.

Key responsibilities:
- Implements `_fmtlock()` and `_fmtunlock()` using a static kernel `Lock`.
- Implements `_efgfmt()` returning `-1`, disabling floating-point style formatting.

Role:
- Supplies hooks expected by the Plan 9 formatting library in kernel context.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/proc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/proc.c

Core portable process scheduler, process lifecycle, sleep/wakeup, notes, kernel processes, process accounting, and PID management.

Key responsibilities:
- Implements scheduler entry and context switching through `schedinit()`, `sched()`, `runproc()`, and `procswitch()`.
- Maintains priority run queues, CPU-usage decay, load average, affinity/wiring, and EDF integration.
- Handles preemption from clock/interrupt paths.
- Allocates/recycles `Proc` objects and initializes process state in `newproc()`/`procinit0()`.
- Implements `sleep()`, `tsleep()`, `wakeup()`, and `procinterrupt()` with rendezvous and qlock interruption handling.
- Manages notes: creation, posting to a process/group, delivery via `popnote()`, and broken-process retention.
- Implements process exit, wait records, child accounting, debugger wakeups, segment teardown, and PID release in `pexit()`.
- Creates kernel processes through `kproc()`.
- Provides process control for stop/trace/kill requests.
- Implements kernel error unwinding with `error()` and `nexterror()`.
- Tracks CPU/kernel time and load in `accounttime()`.
- Implements reference-counted PID table to avoid unsafe PID reuse on wraparound.

Important behavior:
- Scheduling can be delayed while locks are held, but only up to a threshold and not while holding critical allocator locks.
- `ready()` integrates EDF admission and priority recomputation, then enqueues by priority.
- `sleep()` sets `r->p` before checking the condition, then either backs out or commits the process to `Wakeme`.
- `procinterrupt()` can pull a process out of `sleep`, interruptible `eqlock`, or rendezvous wait.
- `pexit()` separates resource pointers under debug lock, frees them outside, then tears down segments and waits.
- PID entries outlive `Proc` references while parent/note IDs refer to them.

Notable risks:
- This file is concurrency-critical; many routines require specific interrupt level and lock ordering.
- `procflushmmu()` waits for other CPUs to observe MMU flush requests through clock interrupts.
- The PID hash uses fixed-size buckets; full buckets trigger retry with a different generated PID.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/qio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/qio.c

Generic block-list and queued I/O implementation used by devices, networking, console, and streams.

Key responsibilities:
- Defines the opaque `Queue` structure with locks, flow-control state, block list, reader/writer rendezvous, kick/bypass callbacks, and close error.
- Provides block-list helpers: free, length, read, concatenate, pullup, trim, pad, copy, adjust, pack, and discard.
- Implements interrupt-level queue producers/consumers: `qget`, `qconsume`, `qpass`, `qpassnolim`, `qproduce`, `qiwrite`.
- Implements process-level queue reads/writes: `qbread`, `qread`, `qbwrite`, `qwrite`.
- Supports message queues, coalescing reads, bypass callbacks, kick callbacks, nonblocking writes, hangup/close/reopen, and queue limit updates.
- Maintains flow control using logical read/write positions based on allocated block sizes, not only data bytes.

Important behavior:
- `Maxatomic` is 64 KiB; `qwrite()` splits larger writes unless the queue is message-oriented.
- Flow-controlled writers remember their queue position and sleep until their own position drains below the limit.
- `qbwrite()` queues data before sleeping so notes do not interrupt already-queued protocol messages.
- `qclose()` drops queued blocks and wakes readers/writers; `qhangup()` marks closed but preserves queued blocks.
- `qread()` returns zero for initial EOF-style closed reads, then errors on repeated closed reads or non-hangup errors.

Notable risks:
- `qfree()` has no reference accounting and is explicitly marked dangerous.
- Queue positions are unsigned counters; correctness relies on normal wraparound behavior and comparisons cast to `int`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/qio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/qlock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/qlock.c

Blocking `QLock` and reader/writer lock implementation.

Key responsibilities:
- Implements interruptible `eqlock()` and non-interruptible `qlock()`.
- Implements nonblocking `canqlock()` and `qunlock()`.
- Implements `rlock()`, `runlock()`, `wlock()`, `wunlock()`, and `canrlock()` for `RWLock`.
- Queues waiting processes using `Proc.qnext`, process states `Queueing`, `QueueingR`, and `QueueingW`.
- Records caller PCs for lock diagnostics.

Important behavior:
- `eqlock()` can be interrupted by pending notes before or during wait; interrupted waiters are pulled by `procinterrupt()`.
- Unlocking a `QLock` hands ownership directly to the next queued process by preserving `locked` and setting owner PC.
- `RWLock` prefers queued writers: readers only enter immediately if no writer and no queued process.
- `wunlock()` wakes one writer or all consecutive queued readers.

Notable risks:
- Calling these while holding ilocks or normal locks prints diagnostics because sleeping while holding locks is unsafe.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/qlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/random.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/random.c

Kernel random generator seeded from hardware RNG and timer jitter, backed by ChaCha.

Key responsibilities:
- Exposes optional machine-specific `hwrandbuf`.
- Starts a `randomseed` kernel process in `randominit()`.
- Collects seed bytes using a periodic timer with a frequency close to but not equal to HZ and a busy-loop counter.
- Mixes the seed with SHA2-512 and initializes a 20-round ChaCha state.
- Implements `randomread()` by optionally filling with hardware random, copying/rekeying ChaCha state, incrementing IV/counter, and encrypting the caller buffer.
- Provides `genrandom()` wrapper and `lrand()` using xoroshiro128+ seeded from `randomread()`.

Important behavior:
- `randominit()` locks the ChaCha state until `randomseed()` completes; reads block on that qlock.
- `randomread()` zeros the local copied ChaCha state after use.
- `lrand()` seeds only once and retries until the state is nonzero.

Notable risks:
- Entropy collection is timing-dependent if no hardware RNG exists.
- `randomread()` encrypts directly into caller memory, which may fault after state has been copied/rekeyed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/random.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/rdb.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/rdb.c

Minimal serial remote debugger loop.

Key responsibilities:
- Reads line commands from `uartgetc()`.
- Supports `r<addr>` to read four bytes and `w<addr> <value>` to write a 32-bit value.
- Treats small addresses as offsets into the supplied `Ureg`, otherwise as raw virtual addresses.
- Resets console UART state for debugger use and disables serial output queues.
- Enters debugger with interrupts high through `rdb()` and `callwithureg()`.

Important behavior:
- Drops `/dev/kprint` by clearing `kprintoq`.
- Runs an infinite command loop once entered.

Notable risks:
- It performs unchecked raw memory reads/writes from debugger input.
- Intended for emergency/debug use, not normal safe operation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/rdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/rebootcmd.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/rebootcmd.c

Kernel reboot command helper for rebooting into a loaded executable image.

Key responsibilities:
- With no arguments, moves the process to CPU0 and calls `exit(0)`.
- Opens the requested boot file with execute permission.
- Reads and validates the executable header.
- Supports additional header magic handling and architecture-specific text alignment.
- Allocates a text+data image, zero-fills it, reads text and data into place, sets `bootfile`, and calls `reboot(entry, image, size)`.

Important behavior:
- Uses big-endian header fields through `beswal()`.
- ARM64 `R_MAGIC` uses 64 KiB text segment alignment; others use page alignment.
- `readn()` treats zero-length reads before completion as `Eshort`.

Notable risks:
- Relies on architecture `reboot()` to consume the loaded image and transfer control.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/rebootcmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sd.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sd.h

Common storage-device framework header.

Key contents:
- Defines permissions, partitions, extra files, storage units, controllers (`SDev`), controller interface (`SDifc`), requests (`SDreq`), and MMC/SD host controller interface (`SDio`).
- Defines status values, sense flags, max I/O size, partition limits, and read/write directions.
- Provides DMA-friendly allocation macros `sdmalloc` and `sdfree`.
- Declares MMC/SD command descriptors and SDio registration/annex functions.
- Declares `devsd.c` helpers for device registration, fake SCSI, fake SCSI read/write translation, and controller annexing.
- Declares SCSI verify/online/bio helpers.

Role:
- Unifies SCSI-like storage devices, ATA/AoE/loop/MMC transports, and `devsd` user-visible storage namespace.

Notable constraints:
- `SDunit.inquiry` and `sense` are sized to fixed SCSI-compatible buffers.
- `SDifc` mixes block-I/O, raw request, control, pnp/probe, and top-level control hooks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdaoe.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sdaoe.c

`sd` backend exposing ATA-over-Ethernet devices discovered through the AoE filesystem/device interface.

Key responsibilities:
- Tracks AoE controllers by path with global linked-list lookup/add/delete.
- Probes configured AoE targets from `aoedev`, including shorthand expansion to `#æ/aoe/...`.
- Issues AoE discover commands and waits for `ident` files to appear.
- Reads ATA identify data, extracts model/serial/firmware and sector count, and builds SCSI inquiry data.
- Opens the AoE `data` file for block reads/writes.
- Implements `verify`, `online`, `bio`, `rio`, `rctl`, `probew`, `clear`, and top-level control hooks for `SDifc`.
- Uses `sdfakescsi()` and `sdfakescsirw()` for SCSI request emulation.

Important behavior:
- Drive size or serial changes set `drivechange` and increment `vers`.
- AoE errors `Echange` or `Enotup` during I/O clear `u->sectors` to force rediscovery/online handling.
- Flush-cache SCSI commands are recognized but return check condition because `flushcache()` is stubbed to `-1`.
- PNP probing sends `nofail on` after establishing the target.

Notable risks:
- Controller deletion has a suspicious loop update expression using `x = c->next`; changes should inspect this path carefully.
- Depends heavily on external AoE device files and error strings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdaoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdloop.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sdloop.c

`sd` loopback backend that exposes an ordinary file/channel as a storage device.

Key responsibilities:
- Tracks loop controllers by backing path.
- Opens backing paths as read/write channels and derives geometry from channel length.
- Supports optional sector size suffix after `!`; defaults to 512 bytes.
- Parses configured loop devices from `loopdev`.
- Implements `verify`, `online`, `bio`, `rio`, `rctl`, `probew`, `clear`, and top-level control hooks for `SDifc`.
- Uses fake SCSI helpers to translate storage requests to block reads/writes.

Important behavior:
- Geometry changes set `drivechange` and increment `vers`.
- I/O errors `Echange` or errors containing `device is down` clear `u->sectors`.
- Flush-cache SCSI commands are treated as successful no-ops.

Notable risks:
- Controller deletion has the same suspicious linked-list loop update pattern as `sdaoe.c`.
- The backing object must support ordinary read/write at byte offsets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdloop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdmmc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/sdmmc.c

Generic MMC/SD card backend over registered `SDio` host controllers.

Key responsibilities:
- Defines common MMC/SD command descriptors.
- Registers SDio host controllers with `addmmcio()` and enumerates them through `mmcpnp()`.
- Allocates `SDev`/`Card`/host-controller copies, supports annexing a controller, and clears controllers.
- Initializes cards by trying SD first, then MMC, reading OCR/CID/CSD/EXT_CSD as appropriate.
- Parses CSD/EXT_CSD to determine card version, sector size, total user sectors, and MMC boot areas.
- Selects card, sets block length, switches bus speed and width, and attempts high-speed modes.
- Implements retry kproc after online/init failures.
- Exposes card status through `rctl`.
- Implements single- and multi-block reads/writes through host `iosetup`, `cmd`, and `io`.
- Switches MMC boot partition selection based on unit subnumber.
- Provides fake SCSI request handling through `mmcrio()`.

Important behavior:
- `Card.sectors[0..2]` represent user and boot areas.
- SD high-capacity cards use block addressing when OCR `Ccs` is set; otherwise byte addressing is used.
- MMC 4.0+ cards attempt high-speed timing and 8-bit/4-bit/1-bit bus width fallback.
- Multi-block write is disabled if host has `nomultiwrite`.
- LED callbacks are toggled around data transfers when available.

Notable risks:
- Retry handling uses a background kproc and `card->retry` coordination; clear/free waits for it by repeatedly locking.
- Many command sequences are hardware timing-sensitive and use sleeps between bus/card state changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/sdmmc.c -->