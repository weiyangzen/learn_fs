# Group Research: group_1484_plan9_sources_os_plan9_plan9_sys_src_9_pcboot_mmu_c_sources_os_plan_1a88d59e5b31

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/mmu.c

This file implements the 32-bit x86 MMU setup and mapping services used by the Plan 9 pc bootstrap kernel. It defines the kernel GDT, initializes per-CPU TSS/GDT/IDT state, switches page directories, maintains per-process user page tables, and manages special kernel virtual regions below `KZERO`.

Key responsibilities:
- Establishes the bootstrap memory layout described in the file header: kernel direct map above `KZERO`, virtual page table at `VPT`, per-process temporary `KMAP`, global device mapping range `VMAP`, and one-page `TMPADDR` mapping.
- `mmuinit0` and `mmuinit` install GDT/TSS/IDT state and self-map the page directory at `VPT`.
- `memglobal` marks kernel PDE/PTE entries with `PTEGLOBAL` when the CPU supports PGE.
- `mmuswitch`, `mmurelease`, `putmmu`, and `checkmmu` maintain per-process page-directory and page-table state.
- `mmuwalk`, `pdbmap`, `pdbunmap`, `vmap`, `vunmap`, and `vmapsync` build and synchronize kernel/device mappings.
- `kmap` and `kunmap` provide temporary per-process mappings for individual physical pages.
- `tmpmap` and `tmpunmap` provide a single safe mapping for editing page directories before they are installed.

Important implementation details:
- The page directory self-map lets page tables be edited through `vpt[]` and `vpd[]`.
- Device mappings are globally allocated from `VMAP` using the bootstrap processor’s page directory as the master copy; other processors/processes fault them in via `vmapsync`.
- `vunmap` invalidates copied mappings by forcing process TLB refreshes and setting per-CPU flush flags.
- `putmmu` deliberately runs at high interrupt priority because faults against the VPT during process switching were historically fragile.
- `KADDR` and `PADDR` are wrapped by checked functions `kaddr` and `paddr`.

Filesystem/storage relevance:
- Kernel buffer cache, device drivers, DMA paths, and page-backed VFS data rely on `kmap`, `vmap`, and correct page-table synchronization.
- Device memory mappings created here are used by low-level storage and network drivers during boot and runtime.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/multiboot.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/multiboot.c

This file constructs a Multiboot information block for transferring control from the 32-bit bootstrap to a 64-bit kernel.

Key responsibilities:
- Maintains global `mbhdr`, `multibootheader`, `mmap`, and `nmmap`.
- `mkmultiboot` reuses low BIOS table memory at `BIOSTABLES` for the Multiboot header and memory map.
- Copies the collected memory map into low memory, sets the command-line pointer to `BOOTLINE`, and sets `Fcmdline` and `Fmmap` flags as appropriate.
- Converts the final header pointer to a physical address before handoff.

Filesystem/storage relevance:
- This is not a filesystem component, but it preserves boot command-line and memory-map state needed by the next kernel, including storage boot parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/multiboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/no-inflate.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/no-inflate.c

This tiny file supplies a link-time `gunzip` stub for bootstrap builds that do not include gzip decompression.

Key responsibilities:
- Defines `gunzip` with the expected signature.
- Prints that gzipped kernels are unsupported by this bootstrap.
- Returns `-1` to signal failure.

Filesystem/storage relevance:
- Affects boot image loading behavior only. Kernel images must be uncompressed when this object is linked.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/no-inflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/parts.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/parts.c

This file reads disk partition tables during early boot, especially for bootstrap kernels that do not use newer `9load` partition discovery.

Key responsibilities:
- Wraps an `SDunit` as `PSDunit` with opened `ctl` and `data` channels.
- `psdaddpart` updates both the in-memory `SDunit` partition table and the underlying `devsd` control file.
- `psdread` and `sdreadblk` read bounded sectors from a partition.
- `oldp9part` parses legacy Plan 9 ASCII partition tables near the end of disk.
- `mbrpart` parses DOS MBR partitions, including DMDDO offset handling, extended partitions, first DOS partition naming, and Plan 9 partition discovery.
- `p9part` parses newer Plan 9 partition tables inside a named partition.
- `part9660` detects ISO9660 boot media and creates a `9fat` partition for `bootdisk.img`.
- `rdgeom`, `setpartitions`, and `readparts` open `/ctl` and `/data` files, read geometry, and populate partition state.
- `sdaddconf` serializes discovered partitions into boot configuration for the next kernel.

Important implementation details:
- Partition parsing is intentionally early-boot and channel-based, not a full disk management stack.
- Sector size defaults to 512 but can be overridden by geometry; ISO9660 expects `Cdsec`.
- The code guards partition bounds when reading through `psdread`.
- New MBR/Plan 9 partition parsing is preferred unless `partition=old` is configured.

Filesystem/storage relevance:
- Directly supports early access to disk-backed filesystems and NVRAM/factotum paths by making partitions visible before the normal user startup scripts run.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/parts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/pxe.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/pxe.h

This header defines the minimal BOOTP/TFTP/UDP protocol structures and constants used by the PXE boot loader.

Key contents:
- Ethernet/IP/UDP protocol constants, BOOTP ports, TFTP opcodes, default timeout, and default TFTP segment size.
- BOOTP option constants including end, padding, and subnet mask.
- `Udphdr`, Plan 9’s UDP pseudo-header/control-message layout.
- `Bootp`, matching the BOOTP packet layout with DHCP-style option area.
- `Pxenetaddr`, a compact IP-plus-port tuple used by PXE code.
- External `chatty` declaration.

Filesystem/storage relevance:
- Supports network boot image retrieval rather than local filesystems.
- Provides protocol layout consumed by `pxeload.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/pxe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/pxeload.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/pxeload.c

This file implements the Plan 9 PXE network boot path using BOOTP and TFTP on top of the kernel’s Ethernet/IP device interfaces.

Key responsibilities:
- Discovers Ethernet interfaces, binds their `#I` and `#l` device trees into `/net`, and creates temporary IP/UDP configuration.
- Sends BOOTP broadcasts, validates replies by hardware address and optional server name, and extracts client/server addressing.
- Opens TFTP sessions using either UDP pseudo-headers or connected UDP channels.
- Negotiates TFTP block size via `blksize`, tracks block numbers, ACKs data, handles OACK/error packets, and streams kernel bytes into `bootpass`.
- Reads optional `/cfg/pxe/<etheraddr>` via TFTP, runs `dotini`, and uses `bootfile` or interactive prompts to choose a kernel.
- Retries across Ethernet interfaces and keeps retrying after failures.

Important functions:
- `etheraddr`, `binddevip`, `openetherdev`, `minip4cfg`, `ip4cfg`, and `unminip4cfg` handle temporary network setup.
- `bootpbcast` performs BOOTP discovery.
- `tftpopen`, `tftpread1st`, `tftpread`, `tftprdfile`, and `tftpboot` implement TFTP loading.
- `rdcfgpxe`, `getkernname`, and `parsebootfile` choose the next kernel and preserve arguments in `BOOTLINE`.
- `bootloadproc` is the long-running boot process.

Filesystem/storage relevance:
- Provides a network-backed alternative to disk boot by loading kernels and configuration over TFTP.
- Uses Plan 9 channels and device operations rather than a standalone network stack.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/pxeload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/rand.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/rand.c

This file provides lightweight pseudo-random support for the bootstrap environment.

Key responsibilities:
- Stubs `randomread` and `randominit` because the full kernel random device is not present.
- Implements libc-style `srand` and `lrand` without locks.
- Uses the Mitchell/Reeds lagged Fibonacci generator initialized by a Park-Miller sequence.

Filesystem/storage relevance:
- Used by boot networking for ephemeral local ports and retry variation.
- Not cryptographic and not suitable for security-sensitive filesystem or auth randomness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/rand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/realmode.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/realmode.c

This file wraps the assembly real-mode transition used to invoke BIOS interrupts from the protected-mode bootstrap kernel.

Key responsibilities:
- Serializes BIOS calls with `rmlock`.
- Copies the requested `Ureg` to low memory at `RMUADDR`.
- Patches the interrupt number into `realmodeintrinst`.
- If not PXE-loaded at the expected low address, copies the real-mode assembly code to `RMCODE`.
- Temporarily identity maps low memory, switches CR3 to the bootstrap page directory, disables hardware interrupts, calls `realmode0`, then restores paging and interrupt state.
- Copies the resulting registers back to the caller’s `Ureg`.

Filesystem/storage relevance:
- Critical for BIOS INT 13 disk I/O used by early boot storage paths.
- Must be used carefully because it disables normal interrupt handling and temporarily changes low-memory mappings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/realmode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/realmode0.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/realmode0.s

This assembly file performs the low-level protected-mode to real-mode transition, executes a BIOS interrupt, and returns to protected mode with paging enabled.

Key responsibilities:
- Defines descriptor pointers for physical and virtual GDT/IDT state.
- Saves and restores general registers and flags.
- Switches to low physical code and stack, loads a real-mode IDT, disables paging, enters 16-bit compatibility mode, then clears protected mode.
- Loads BIOS call registers from `RMUADDR`, executes the patched `INT`, saves registers and flags back to `RMUADDR`, then re-enters protected mode.
- Restores kernel segment registers, paging, IDT, GDT, and original stack.
- Includes a Multiboot header placed near the image start.
- Defines a small 16-bit-compatible GDT and pointer.

Filesystem/storage relevance:
- Enables BIOS disk services during bootstrap, which can be the only available storage path before native disk drivers are initialized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/realmode0.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/sdbios.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/sdbios.c

This file adapts BIOS disk devices into the Plan 9 `sd` storage interface for read-only bootstrap use.

Key responsibilities:
- Exposes `sdbiosifc`, an `SDifc` named `"bios"`.
- `biospnp` creates an `SDev` for BIOS devices after BIOS initialization.
- `biosonline` populates sector size and sector count using BIOS helper functions.
- `biosrio` handles selected SCSI disk commands over BIOS reads, including extended read and capacity queries.
- Rejects writes because boot programs do not write through BIOS disks.
- Provides big-endian packing helpers for SCSI capacity responses.

Filesystem/storage relevance:
- Lets bootstrap code use standard `sd` partition and block interfaces over BIOS-backed disks.
- Read-only design reduces risk during early boot but limits recovery/write scenarios.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/sdbios.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/stub.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/stub.c

This file supplies stubs and small compatibility helpers so bootstrap kernels can link without the full kernel syscall, swap, mount-auth, environment, and floating-point subsystems.

Key responsibilities:
- Stubs mount authentication/versioning, swap, pager, environment group close, syscall formatting, file descriptor allocation, and floating-point save/restore functions.
- Implements `data2txt` for converting a data segment to a text segment.
- Implements `validstat`, `fdtochan`, and `openmode` subsets needed by file operations.
- Implements boot-time `bind`, `unmount`, `chdir`, channel open/create helpers, `myreadn`, and `readfile`.
- Provides `return0` and endian helper `l2be`.

Filesystem/storage relevance:
- Allows boot code to use enough namespace and channel operations to read files, bind devices, and traverse storage/network devices without carrying the full kernel user-facing syscall layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/trap.c

This file implements x86 trap and interrupt handling for the pc bootstrap kernel.

Key responsibilities:
- Maintains a `vctl[256]` dispatch table for traps and interrupts.
- `trapinit0` builds the IDT early enough to panic cleanly during initialization.
- `trapinit` installs handlers for breakpoint, page fault, double fault, and reserved trap 15, enables NMI, and exposes `irqalloc`.
- `intrenable` and `intrdisable` register and unregister interrupt handlers via architecture-specific hooks.
- `trap` dispatches interrupts, handles spurious interrupts, posts user notes for user exceptions, and panics on unhandled kernel traps.
- `fault386` handles page faults, including lazy `VMAP` synchronization and normal VM faults.
- Provides register dumps, stack dumps, kernel-process setup, fork-child register setup, and debugging PC helpers.
- `syscall` panics because bootstrap kernels do not implement system calls.

Filesystem/storage relevance:
- Page-fault handling is required for VMAP-backed device mappings used by storage/network drivers.
- Interrupt registration supports disk, network, and timer drivers during boot.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/unbindpc -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/unbindpc

This is an `rc` helper script for unbinding pcboot files that were mounted or overlaid from related `pc` build directories.

Key responsibilities:
- Exits quietly if expected local files are absent.
- Uses `rfork e`.
- Unmounts matching `pc?*pxe` entries without dots.
- Unmounts the current mount, `/tmp/blank`, and exits successfully.

Filesystem/storage relevance:
- Build/workspace helper only; it affects source-tree namespace setup, not runtime filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/unbindpc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/warp64.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/warp64.c

This file performs the final handoff from the 32-bit bootstrap to a 64-bit kernel entry point.

Key responsibilities:
- Uses CPUID extended function checks to detect long-mode support.
- `warp64` rejects 64-bit kernels on CPUs without long mode.
- Builds the Multiboot handoff block via `mkmultiboot`.
- Calls `impulse` before invoking the assembly `_warp64` entry trampoline.
- Converts the 64-bit kernel entry from high virtual address form by masking with the expected 64-bit `KZERO`.

Filesystem/storage relevance:
- Final boot handoff only. Storage relevance is indirect through preserving bootline and memory-map state for the loaded kernel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/warp64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/alarm.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/alarm.c

This file implements per-process alarm scheduling and delivery.

Key responsibilities:
- Maintains a sorted linked list of processes with pending alarms.
- `procalarm` sets or clears the current process alarm and returns the previous remaining time in milliseconds.
- `checkalarms` wakes the alarm kernel process when the head alarm expires.
- `alarmkproc` posts `"alarm"` notes to processes whose alarm time has arrived.
- Handles tick wraparound using signed subtraction comparisons.

Filesystem/storage relevance:
- Not filesystem-specific, but timers and sleeping behavior are used throughout kernel services and device operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/alarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/alloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/alloc.c

This file provides the normal kernel heap allocation layer backed by `Pool`.

Key responsibilities:
- Defines `mainmem` and `imagmem` pools with xalloc/xmerge backends.
- Wraps pool locking with deferred printing because diagnostics cannot be printed while holding pool locks.
- Implements `smalloc`, `malloc`, `mallocz`, `mallocalign`, `free`, `realloc`, `msize`, and `calloc`.
- Tracks malloc and realloc caller tags using two hidden `ulong` words before returned allocations.
- Provides `mallocsummary` and `poolsummary`.

Important implementation details:
- `smalloc` sleeps and retries until memory is available.
- `malloc` and `mallocz` return `nil` on allocation failure.
- All normal allocations are rounded by the underlying pool and may be zeroed depending on API.
- Caller-visible pointers are offset from the real pool block by `Npadlong`.

Filesystem/storage relevance:
- Core allocator for VFS objects, channels, path strings, mount entries, device state, and storage driver buffers that are not allocated as `Block`s.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/allocb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/allocb.c

This file implements allocation and validation for Plan 9 `Block` packet/buffer objects.

Key responsibilities:
- Computes total memory required for a `Block` plus header slack and alignment via `blocksize`.
- `mem2block` initializes a `Block` over malloced or caller-provided memory.
- `allocb` allocates normal process-context blocks and panics on exhaustion.
- `iallocb` allocates interrupt-context blocks under `conf.ialloc` accounting and returns `nil` on pressure.
- `freeb` reference-counts blocks, calls custom free callbacks when present, updates interrupt allocation accounting, poisons dead blocks, and frees memory.
- `checkb` validates block magic and pointer bounds.
- `iallocsummary` reports interrupt allocation usage.

Filesystem/storage relevance:
- `Block` is the common buffer type for network and some device I/O, including AoE packet transport and generic `devbread`/`devbwrite` wrappers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/allocb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/aoe.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/aoe.h

This header defines ATA-over-Ethernet protocol constants and packet layouts.

Key contents:
- AoE command types for ATA and config/query.
- Config command variants.
- Protocol constants including EtherType `0x88a2`, sector size, version, response/error flags, ATA write and extended-LBA flags.
- `Aoehdr`, the common Ethernet/AoE header.
- `Aoeata`, the ATA command frame.
- `Aoeqc`, the query/config frame.
- `AOEHDRSZ`, `AOEATASZ`, and `AOEQCSZ` offset macros.

Filesystem/storage relevance:
- Shared protocol definition for `devaoe.c`, Plan 9’s AoE block storage initiator.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/aoe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/auth.c

This file implements selected authentication and identity syscalls/helpers.

Key responsibilities:
- Stores global `eve` and `hostdomain`.
- `iseve` tests whether the current user is the host owner.
- `sysfversion` negotiates a 9P version on a file descriptor by calling `mntversion`.
- `sys_fsession` is a deprecated compatibility stub.
- `sysfauth` performs mount authentication through `mntauth` and returns a close-on-exec auth fd.
- `userwrite` allows switching to user `"none"`.
- `hostownerwrite` changes host owner and current user, restricted to `eve`.
- `hostdomainwrite` updates host domain, restricted to `eve`.

Filesystem/storage relevance:
- 9P mount versioning and authentication affect remote filesystem access.
- Identity checks feed file permission behavior in generic device and namespace code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/cache.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/cache.c

This file implements a page-backed file data cache for mount channels.

Key responsibilities:
- Defines `Mntcache` entries keyed by qid/dev/type and linked in an LRU list.
- Represents cached byte ranges as `Extent` records pointing to cached `Page`s in the private `fscache` image.
- `cinit` allocates file cache headers and scales `maxcache` based on memory size.
- `copen` attaches a channel to an existing cache entry or recycles an LRU entry.
- `cread` copies cached extents into a caller buffer when present and contiguous.
- `cupdate` inserts data read from a server into the cache without invalidating unrelated ranges.
- `cwrite` updates/invalidate-overwrites cached data and bumps qid versions.
- `cnodata` invalidates all extents for a cached file.

Important implementation details:
- The cache only handles non-directory, non-append files.
- It uses `kmap` to access cached pages and `lookpage/cachepage/putpage` to integrate with the page cache.
- Cached ranges are capped by `maxcache`.
- Extent records are pooled separately through `Ecache`.

Filesystem/storage relevance:
- Directly part of Plan 9’s mounted-file caching path.
- Bridges VFS channel identity, qid versioning, and VM page storage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/chan.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/chan.c

This file is the core Plan 9 channel, path, namespace, mount, and name-resolution implementation.

Key responsibilities:
- Allocates, recycles, references, closes, and asynchronously clunks `Chan` objects.
- Manages `Path` objects with copy-on-write strings and mount-point ancestry.
- Initializes and shuts down all devices in `devtab`.
- Implements reference helpers, kernel string helpers, and name validation.
- Implements mount table operations through `Mhead` and `Mount`: `cmount`, `cunmount`, `findmount`, `domount`, and `undomount`.
- Implements `walk`, including mount crossing, union traversal, `..` handling, and all-or-nothing walk semantics.
- Implements `namec`, the central path-to-channel resolver for bind, mount target, directory, access, open, create, and remove modes.
- Handles create/open race behavior so concurrent `create(2)` calls preserve expected Plan 9 semantics.
- Enforces attach restrictions for `#` device paths under `noattach`.

Important implementation details:
- Paths remember mount points in `Path.mtpt` so `..` can uncross mounts correctly.
- `namec` starts from root, current directory, or a `#` device attach depending on the first path character.
- `validname0` protects against malicious user-space strings by optionally duplicating before rescanning.
- Union directories are handled by trying additional mount elements when a walk fails.
- `ccloseq` defers expensive close operations to `closeproc`.

Filesystem/storage relevance:
- This is the central VFS/namespace file for Plan 9.
- Every local, remote, synthetic, and storage-backed file access flows through channels and path resolution implemented here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/chan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/cis.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/cis.c

This file parses PCMCIA Card Information Structure tuples.

Key responsibilities:
- Reads CIS bytes from attribute or memory space through `pcmmap`.
- `pcmcistuple` fetches a requested tuple/subtuple.
- `pcmcisread` parses all relevant tuples into a `PCMslot`.
- Handles version strings, configuration register metadata, configuration table entries, voltage/current descriptors, timing descriptors, I/O ranges, IRQ masks, and memory windows.
- Supports multifunction CIS long-link traversal.

Filesystem/storage relevance:
- Supports PCMCIA device configuration, including storage/network cards that may later expose filesystems or block devices.
- Not itself a filesystem component.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/cis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/debugalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/debugalloc.c

This file provides an alternate/debugging pool allocator implementation.

Key responsibilities:
- Defines `Pool` internals with arena chains, boundary headers, free-tree organization, and allocation counters.
- `poolalloc` finds exact or best-fit free blocks, splits blocks, allocates new arenas with `xalloc`, and optionally compacts.
- `poolfree` coalesces adjacent free blocks and reinserts them into the free tree.
- Implements `malloc`, `smalloc`, `mallocz`, `free`, `realloc`, `msize`, and `calloc` on top of the debug pool.
- Tracks allocation call sites for small blocks through the `pcx` table.
- Supports pool compaction through a caller-provided move callback.

Filesystem/storage relevance:
- Alternative allocator for diagnosing memory behavior in kernel subsystems, including VFS and storage drivers.
- Helps detect allocation pressure and fragmentation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/debugalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/dev.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/dev.c

This file provides generic helpers for Plan 9 kernel device implementations.

Key responsibilities:
- Creates qids via `mkqid` and resolves device letters via `devno`.
- Builds `Dir` records with `devdir`.
- Provides default no-op reset/init/shutdown hooks.
- Implements generic attach and clone behavior for synthetic devices.
- Implements `devgen`, `devwalk`, `devstat`, and `devdirread` for table- or generator-backed directory trees.
- Implements permission checking and `devopen`.
- Provides default failing create/remove/wstat/power/config operations.
- Provides `devbread` and `devbwrite` wrappers converting read/write calls to `Block` operations.

Important implementation details:
- Comments document the subtle expectations around `Devgen` behavior for children versus siblings.
- `devwalk` handles `.` and `..`, partial walks, and cloned channels.
- Directory opens are read-only.

Filesystem/storage relevance:
- This is shared scaffolding for synthetic filesystem-like devices in Plan 9.
- Storage drivers such as AoE and BIOS/audio devices use this pattern to expose control/data files under the namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devaoe.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devaoe.c

This file implements Plan 9’s ATA-over-Ethernet storage initiator as a namespace device.

Key responsibilities:
- Exposes an AoE device tree under device character `æ`, including top-level `aoe`, `ctl`, `log`, per-unit directories, `data`, `config`, `ident`, and `devlink` files.
- Binds Ethernet netlinks, opens AoE EtherType conversations, reads local Ethernet addresses, and spawns per-netlink reader kernel processes.
- Sends AoE config discovery packets, tracks discovered shelves/slots as `Aoedev` units, and maintains per-device links to network interfaces and target Ethernet addresses.
- Implements ATA read/write request scheduling with `Srb` request blocks and `Frame` transmit slots.
- Supports retransmission, round-trip tracking, adaptive max outstanding requests, jumbo-frame fallback, and device-down behavior.
- Parses ATA identify data, stores serial/firmware/model fields, updates device size, flags LBA/power/smart/nop capabilities, and changes qid versions on media changes.
- Reads and writes AoE config strings.
- Provides control commands for bind/unbind, discover, rediscover, debug, remove, identify, failio, jumbo, nofail, mtu/max block count, and setsize.
- Maintains an event log readable from `log`.

Important implementation details:
- Data I/O requires sector-aligned offset and length.
- `rw` splits large requests into bounded SRB chunks and uses copying for user buffers but can reference kernel buffers directly.
- `aoesweepproc` periodically rediscovers devices and resends timed-out frames.
- `netunbind` disables links, waits for reader exit, reschedules packets, compacts devlink arrays, and removes orphan devices.
- `eventlogread` avoids copying to pageable memory while holding the event lock.

Filesystem/storage relevance:
- This is a full block-storage device driver surfaced through the Plan 9 file namespace.
- The `data` file is the block device surface used by higher-level partition/filesystem tooling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devaoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devaudio.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/port/devaudio.c

This file implements a Sound Blaster 16 / ESS1688 audio device exposed as Plan 9 files.

Key responsibilities:
- Exposes `audio`, `volume`, and `audiostat` files under device character `A`.
- Initializes SB16/ESS1688 hardware from ISA configuration, allocates I/O ports, sets IRQ/DMA, resets the DSP, and configures mixer state.
- Manages fixed DMA buffers through empty/full queues.
- Handles playback and recording using autoinit DMA.
- Handles SB16 and ESS1688 interrupt paths.
- Implements text-based volume control parsing and status reporting.
- Provides `audioread`, `audiowrite`, open/close logic, and optional byte swapping.

Filesystem/storage relevance:
- Not a filesystem/storage driver, but it is a representative Plan 9 synthetic device using `Dev`, `Chan`, directory entries, `Block` wrappers, and namespace exposure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/port/devaudio.c -->