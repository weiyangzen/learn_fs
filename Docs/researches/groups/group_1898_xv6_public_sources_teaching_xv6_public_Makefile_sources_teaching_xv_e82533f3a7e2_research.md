# Group Research: group_1898_xv6_public_sources_teaching_xv6_public_Makefile_sources_teaching_xv_e82533f3a7e2

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/teaching/xv6-public`, which is included in subset A. Every listed source file was read completely and summarized separately.

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/Makefile -->
# File Research: sources/teaching/xv6-public/Makefile

Read completely: 286 lines, 8445 bytes.

This is the build, run, packaging, and print orchestration file for xv6-public. It defines the kernel object list, user programs, toolchain discovery, QEMU discovery, compiler/linker flags, bootblock generation, kernel image generation, memfs variant, filesystem image construction, emulator targets, GDB targets, distribution targets, and paper/PDF production.

The kernel build links `entry.o`, the kernel object set, binary `initcode`, and binary `entryother` through `kernel.ld`; `xv6.img` is assembled by writing the boot block to sector 0 and the kernel from sector 1 onward. `bootblock` is linked at `0x7C00`, converted to raw binary, and passed through `sign.pl` to enforce the boot-sector signature. `entryother` is linked for low-memory AP startup at `0x7000`, and `initcode` is linked at address 0 for the first user image.

The file creates two kernel variants: normal disk-backed xv6 with `ide.o`, and `kernelmemfs`, which replaces `ide.o` with `memide.o` and embeds `fs.img`. It builds user programs as underscored binaries (`_cat`, `_sh`, etc.) so host commands are not shadowed, then passes them to `mkfs`, which strips leading underscores in directory entries.

Operational targets include `qemu`, `qemu-nox`, `qemu-gdb`, `qemu-memfs`, `bochs`, `clean`, `tags`, `dist`, `dist-test`, and `tar`. It also includes the xv6 print pipeline with `runoff`, `runoff1`, `pr.pl`, and associated document inputs.

Notable risk: this file encodes architecture assumptions for 32-bit x86 (`-m32`, `elf32-i386`, non-PIE, physical boot addresses). Modern host toolchains may require compatible multilib/binutils support, and the QEMU binary detection covers several historical names.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/asm.h -->
# File Research: sources/teaching/xv6-public/asm.h

Read completely: 18 lines, 754 bytes.

Defines assembler macros and constants for x86 segment descriptors used by boot and AP startup assembly. `SEG_NULLASM` emits a null descriptor, and `SEG_ASM(type, base, lim)` emits the packed descriptor fields with 4KB granularity and 32-bit mode bits.

It also defines segment access constants `STA_X`, `STA_W`, and `STA_R`. These are consumed by `bootasm.S` and `entryother.S` to build temporary flat bootstrap GDTs.

Risk: descriptor packing must remain byte-exact; mistakes here can prevent transition from real mode to protected mode.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/asm.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/bio.c -->
# File Research: sources/teaching/xv6-public/bio.c

Read completely: 144 lines, 3397 bytes.

Implements the xv6 buffer cache. The cache is a fixed array of `struct buf` entries linked through an MRU/LRU list protected by `bcache.lock`; each individual buffer has a sleep lock for exclusive block access.

`binit()` initializes the cache list and buffer sleep locks. `bget()` first searches for an existing `(dev, blockno)` buffer and increments its reference count; if absent, it recycles an unused clean buffer from the LRU end. Dirty buffers are not recycled because the log pins them until commit. `bread()` obtains a locked buffer and calls `iderw()` if the data is not valid. `bwrite()` marks a locked buffer dirty and synchronously writes it with `iderw()`. `brelse()` releases the sleep lock, decrements `refcnt`, and moves unused buffers to the MRU head.

This file is the synchronization point between filesystem block users, the IDE/memide device layer, and the logging layer. The API contract is strict: callers must not use a buffer after `brelse()`, and only one process may use a buffer while its sleep lock is held.

Notable risk: the cache can panic with `bget: no buffers` if all buffers are referenced or log-pinned. Correctness depends on `B_DIRTY` pinning, sleep-lock ownership checks, and consistent `bread`/`log_write`/`brelse` pairing.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/bootasm.S -->
# File Research: sources/teaching/xv6-public/bootasm.S

Read completely: 88 lines, 2985 bytes.

This is the first-stage boot assembly loaded by the BIOS at physical `0x7c00`. It starts in 16-bit real mode, disables interrupts, zeros segment registers, enables the A20 line through keyboard-controller ports, loads a temporary flat GDT, sets `CR0_PE`, and far-jumps into 32-bit protected mode.

In 32-bit mode it loads kernel data selectors into `ds/es/ss`, zeros `fs/gs`, uses the boot code address as a temporary stack, and calls `bootmain()`. If `bootmain()` returns, it emits a Bochs breakpoint sequence on port `0x8a00` and spins forever.

The file defines the temporary bootstrap GDT using `SEG_NULLASM` and `SEG_ASM`.

Risk: this code must fit into the signed boot sector with `bootmain.c`. It assumes BIOS disk loading, x86 port I/O, and exact low-memory execution at `0x7c00`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/bootasm.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/bootmain.c -->
# File Research: sources/teaching/xv6-public/bootmain.c

Read completely: 96 lines, 2253 bytes.

Implements the C portion of the bootloader. It reads the kernel ELF image from disk starting at sector 1 into scratch memory at `0x10000`, validates `ELF_MAGIC`, iterates program headers, loads each loadable segment to its physical address, zero-fills `memsz - filesz`, and jumps to the ELF entry point.

Disk I/O is raw PIO against IDE ports `0x1F0` through `0x1F7`. `waitdisk()` waits for ready status, `readsect()` reads one sector using command `0x20`, and `readseg()` rounds down to sector boundaries and reads enough sectors to cover a byte range.

Risk: no filesystem parsing exists here; the kernel must begin at disk sector 1 and be a valid ELF. `readseg()` intentionally may read extra bytes at segment edges.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/bootmain.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/buf.h -->
# File Research: sources/teaching/xv6-public/buf.h

Read completely: 14 lines, 326 bytes.

Defines `struct buf`, the in-memory buffer-cache entry for one disk block. Fields include state flags, device number, block number, per-buffer sleep lock, reference count, LRU list links, disk queue link, and `data[BSIZE]`.

It also defines `B_VALID` and `B_DIRTY`. `B_VALID` means the data field contains disk contents; `B_DIRTY` means the buffer has modified contents that must not be evicted and may need writing.

Risk: this structure is shared by `bio.c`, `ide.c`, `memide.c`, and `log.c`; changing layout or flags affects cache, device, and transaction behavior.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/cat.c -->
# File Research: sources/teaching/xv6-public/cat.c

Read completely: 43 lines, 589 bytes.

User program implementing `cat`. It reads 512-byte chunks from either stdin or each named file and writes them to file descriptor 1. It exits with an error message on open, read, or short write failure.

This is a minimal test of `open`, `read`, `write`, `close`, and process exit.

Risk: intentionally simple; any write short count is treated as fatal.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/cat.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/console.c -->
# File Research: sources/teaching/xv6-public/console.c

Read completely: 299 lines, 5384 bytes.

Implements kernel console output, formatted kernel printing, panic handling, CGA text output, keyboard/serial input buffering, and console device registration. Output goes to both UART and CGA memory. Input arrives via keyboard or serial interrupt handlers calling `consoleintr()`.

`cprintf()` supports `%d`, `%x`, `%p`, `%s`, and `%%`, protected by `cons.lock` once `consoleinit()` enables locking. `panic()` disables interrupts, disables console locking, prints CPU/APIC and call stack PCs, marks `panicked`, and spins. `cgaputc()` writes to CGA memory at `P2V(0xb8000)`, updates the hardware cursor, handles newlines/backspace, and scrolls above row 24.

The input ring has read, write, and edit indices. `consoleintr()` handles `^P` process dump, `^U` line kill, backspace/delete, carriage-return conversion, `^D` EOF, and wakeups for readers. `consoleread()` sleeps until input is available and temporarily unlocks the inode; `consolewrite()` emits bytes while similarly avoiding holding the inode lock. `consoleinit()` installs console read/write handlers in `devsw[CONSOLE]` and enables the keyboard IRQ.

Risk: console code sits in panic and interrupt paths, so locking must avoid recursion and deadlock. `^D` handling intentionally preserves EOF for a subsequent zero-byte read when needed.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/console.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/cuth -->
# File Research: sources/teaching/xv6-public/cuth

Read completely: 48 lines, 934 bytes.

Perl helper that attempts to remove unnecessary `#include` lines from C files. For each input file, it touches the file, verifies that its object builds with `make CC='gcc -Werror'`, temporarily replaces each include line from bottom to top with a marker, rebuilds, and keeps removals that still compile. It saves a backup named `=<file>` during processing and removes it afterward.

This is a developer maintenance utility, not part of the xv6 runtime.

Risk: it mutates source files and shells out to `make`; it should only be used intentionally in a clean tree.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/cuth -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/date.h -->
# File Research: sources/teaching/xv6-public/date.h

Read completely: 8 lines, 102 bytes.

Defines `struct rtcdate` with second, minute, hour, day, month, and year fields. Used by CMOS/RTC code in `lapic.c` and exposed through declarations in `defs.h`.

Risk: simple shared date representation; field type and order are assumed by RTC fill/copy logic.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/date.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/defs.h -->
# File Research: sources/teaching/xv6-public/defs.h

Read completely: 190 lines, 5540 bytes.

Central kernel declaration header. It forward-declares core structs and lists function prototypes grouped by source module: buffer cache, console, exec, file table, filesystem, IDE, IO APIC, allocator, keyboard, local APIC, log, MP, PIC, pipe, process, context switch, spinlock, sleeplock, string, syscall helpers, traps, UART, and VM.

It also declares global symbols such as `ioapicid`, `lapic`, `ticks`, `tickslock`, and the `NELEM` array-size macro.

Risk: this file is the cross-module ABI for the kernel. Prototype drift here can mask or create build failures across the small xv6 codebase.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/defs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/echo.c -->
# File Research: sources/teaching/xv6-public/echo.c

Read completely: 13 lines, 198 bytes.

User `echo` implementation. It prints arguments separated by spaces and ends with a newline. It exits immediately after printing.

Risk: no option handling; exactly the xv6 teaching shell utility behavior.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/echo.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/elf.h -->
# File Research: sources/teaching/xv6-public/elf.h

Read completely: 42 lines, 755 bytes.

Defines the 32-bit ELF structures and constants used by the bootloader and `exec`. Includes `ELF_MAGIC`, `struct elfhdr`, `struct proghdr`, `ELF_PROG_LOAD`, and program header flag bits for execute/write/read.

Risk: xv6 only consumes enough ELF metadata to load program segments; section headers and many ELF features are ignored.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/elf.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/entry.S -->
# File Research: sources/teaching/xv6-public/entry.S

Read completely: 68 lines, 1832 bytes.

Kernel entry assembly after the bootloader jumps into the ELF entry. It includes a Multiboot header for GRUB loading, defines `_start` as the physical address of `entry`, enables 4MB pages with `CR4_PSE`, loads `entrypgdir`, enables paging and write-protect in `CR0`, sets the initial stack, and jumps indirectly to `main` at high virtual addresses.

The file reserves the initial kernel stack with `.comm stack, KSTACKSIZE`.

Risk: this is the transition from physical boot execution to the high-half kernel mapping. It depends on `entrypgdir` having both identity and `KERNBASE` mappings for the first 4MB.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/entry.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/entryother.S -->
# File Research: sources/teaching/xv6-public/entryother.S

Read completely: 93 lines, 2762 bytes.

Startup code for non-boot application processors. `main.c` copies this code to low memory at `0x7000` and writes three words immediately before it: stack pointer at `start-4`, entry function at `start-8`, and physical `entrypgdir` at `start-12`.

The code begins in real mode, disables interrupts, zeros segment registers, loads a temporary GDT, enters protected mode, loads flat segments, enables PSE, loads the supplied page directory, enables paging/write-protect, switches to the supplied stack, and calls the supplied `mpenter()` function. If it returns, it emits a Bochs breakpoint sequence and spins.

Risk: must remain position-compatible with the low-memory copy and with the negative-offset arguments filled by `startothers()`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/entryother.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/exec.c -->
# File Research: sources/teaching/xv6-public/exec.c

Read completely: 114 lines, 2563 bytes.

Implements `exec(path, argv)` for replacing the current process image. It opens the named inode inside a filesystem transaction, validates the ELF header, creates a new kernel/user page table with `setupkvm()`, loads each `ELF_PROG_LOAD` segment into allocated user memory, and then builds a two-page stack with a guard page below it.

Argument strings are copied into the new stack with word alignment, followed by fake return PC, `argc`, and `argv` pointer. After successful setup, it updates the process name, swaps `curproc->pgdir`, updates size, entry EIP, and user ESP, switches page tables, frees the old address space, and returns 0. Error paths free the new page table and unlock/drop the inode.

Risk: commit occurs only after all failure-prone validation and memory setup are complete. Correctness depends on overflow checks, page alignment of program headers, `MAXARG`, `copyout`, and guard-page creation through `clearpteu()`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/fcntl.h -->
# File Research: sources/teaching/xv6-public/fcntl.h

Read completely: 4 lines, 96 bytes.

Defines xv6 open mode flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, and `O_CREATE`. Used by user programs and `sysfile.c`.

Risk: minimal API constants; bit values are interpreted directly by `sys_open()`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/fcntl.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/file.c -->
# File Research: sources/teaching/xv6-public/file.c

Read completely: 157 lines, 2816 bytes.

Implements the global open-file table and file descriptor operations. `fileinit()` initializes the table lock. `filealloc()` finds a free `struct file`; `filedup()` increments references; `fileclose()` drops references and, on last close, closes a pipe or releases an inode inside a transaction.

`filestat()` returns inode metadata. `fileread()` dispatches to pipe read or inode read while advancing the shared file offset. `filewrite()` dispatches to pipe write or writes in transaction-sized chunks so a large user write does not exceed the log reservation. The inode write path locks the inode, calls `writei()`, advances offset, and commits each chunk.

Risk: file offsets are stored in the shared `struct file`, so duplicated descriptors intentionally share offsets. Write chunking relies on `MAXOPBLOCKS` arithmetic matching log capacity assumptions.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/file.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/file.h -->
# File Research: sources/teaching/xv6-public/file.h

Read completely: 37 lines, 802 bytes.

Defines in-memory `struct file`, in-memory `struct inode`, device switch `struct devsw`, and the `CONSOLE` major number. Files may be `FD_NONE`, `FD_PIPE`, or `FD_INODE`, and track reference count, readability, writability, pipe pointer, inode pointer, and current offset.

The inode cache representation stores identity (`dev`, `inum`), reference count, sleep lock, validity flag, copied disk inode fields, size, and direct/indirect block addresses.

Risk: these structures bridge process descriptors, filesystem internals, devices, and pipes. Locking discipline is split: file table uses `ftable.lock`, inode identity/ref uses `icache.lock`, and inode contents use `ip->lock`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/file.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/forktest.c -->
# File Research: sources/teaching/xv6-public/forktest.c

Read completely: 56 lines, 764 bytes.

Small user test that repeatedly forks until failure, expects graceful failure before 1000 forks, waits for all children, and verifies that an extra `wait()` returns `-1`. It defines a tiny custom `printf` that writes a literal string to keep the binary small.

Risk: intended to fill process-table resources rather than binary memory footprint. It treats unexpected unlimited fork success or wait behavior as fatal.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/forktest.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/fs.c -->
# File Research: sources/teaching/xv6-public/fs.c

Read completely: 670 lines, 15787 bytes.

Implements xv6’s filesystem core in five layers: raw block allocation, logging-aware inode operations, file contents, directories, and path lookup. The single global superblock `sb` is read from disk by `readsb()` during `iinit()`.

The block allocator scans bitmap blocks for a free bit, marks it through `log_write()`, zeroes the newly allocated block, and returns its block number. `bfree()` clears bitmap bits and panics on double free. The inode cache uses `icache.lock` for cache identity/refcounts and per-inode sleep locks for on-disk metadata and file data. `ialloc()`, `iupdate()`, `iget()`, `idup()`, `ilock()`, `iunlock()`, `iput()`, and `iunlockput()` implement allocation, write-through metadata updates, reference management, lazy disk loading, and last-reference truncation.

File content is addressed through 12 direct blocks plus one single-indirect block. `bmap()` allocates blocks on demand. `itrunc()` frees direct and indirect blocks. `readi()` and `writei()` handle device inodes through `devsw` or regular inode block I/O, with size, overflow, and `MAXFILE` checks.

Directory support includes fixed-size `DIRSIZ` names, `dirlookup()`, `dirlink()`, and path parsing through `skipelem()` and `namex()`. `namei()` returns the inode for a path; `nameiparent()` returns the parent and final element.

Risk: many functions require caller-held inode locks or caller-held log transactions. `iput()` can free disk blocks and must run inside a transaction. The path lookup code depends on careful lock/drop ordering to avoid deadlocks while keeping references valid.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/fs.h -->
# File Research: sources/teaching/xv6-public/fs.h

Read completely: 57 lines, 1733 bytes.

Defines the on-disk xv6 filesystem layout and structures shared by the kernel and `mkfs`. Constants include `ROOTINO`, `BSIZE`, `NDIRECT`, `NINDIRECT`, `MAXFILE`, `IPB`, `BPB`, and `DIRSIZ`.

`struct superblock` describes total size, data blocks, inode count, log size/start, inode start, and bitmap start. `struct dinode` is the on-disk inode with type, device numbers, link count, size, and block addresses. `struct dirent` is a directory entry of inode number plus fixed 14-byte name.

Risk: this is an on-disk format contract. Changes require coordinated updates to `mkfs`, kernel filesystem code, and any existing disk images.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/grep.c -->
# File Research: sources/teaching/xv6-public/grep.c

Read completely: 107 lines, 1954 bytes.

User `grep` implementation with a small regular expression engine from Kernighan and Pike. It supports `^`, `.`, `*`, and `$`. Input is buffered in 1024 bytes, accumulated across reads until newline boundaries, and matching lines are written to stdout.

The matcher is recursive: `match()`, `matchhere()`, and `matchstar()` implement unanchored/anchored matching and `c*`.

Risk: long lines larger than the buffer are handled by carrying remaining partial data, but this is a small teaching implementation without full regex syntax or binary-data handling.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/grep.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/ide.c -->
# File Research: sources/teaching/xv6-public/ide.c

Read completely: 168 lines, 3613 bytes.

Implements a simple PIO IDE disk driver. It defines IDE status and command constants, a global request queue protected by `idelock`, and detects the presence of disk 1 at initialization. `ideinit()` initializes locking, routes the IDE IRQ, waits for readiness, probes disk 1, and restores disk 0 selection.

`idestart()` translates xv6 block numbers to IDE sectors, selects read/write or multi-sector commands based on `BSIZE / 512`, writes command registers, and writes data immediately for dirty buffers. `ideintr()` handles completed requests, reads data for reads, marks buffers valid and clean, wakes sleepers, and starts the next queued request. `iderw()` validates locked buffers, appends them to the queue, starts the disk if idle, and sleeps until the buffer becomes valid and clean.

Risk: the queue manipulation must hold `idelock`; `stressfs.c` documents a race if the lock is moved after traversal. The driver panics for out-of-range blocks and missing disk 1.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/ide.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/init.c -->
# File Research: sources/teaching/xv6-public/init.c

Read completely: 37 lines, 649 bytes.

First long-running user process after `initcode.S` execs `/init`. It opens or creates the `console` device, duplicates fd 0 to stdout and stderr, then repeatedly forks and execs `sh`. It waits for the shell and reports unexpected orphaned zombie reaping.

Risk: if `init` exits or cannot start `sh`, the user environment is unusable; the kernel also panics if the init process exits.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/init.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/initcode.S -->
# File Research: sources/teaching/xv6-public/initcode.S

Read completely: 32 lines, 455 bytes.

Tiny first user-space program embedded into the kernel. It invokes `exec("/init", argv)` through `int T_SYSCALL`, with a fake caller PC on the stack. If `exec` returns, it loops issuing `exit` syscalls forever.

Risk: this code is loaded at virtual address 0 by `userinit()`, so its position and syscall ABI are fixed.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/initcode.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/ioapic.c -->
# File Research: sources/teaching/xv6-public/ioapic.c

Read completely: 75 lines, 2047 bytes.

Implements I/O APIC setup and interrupt routing. It maps the APIC MMIO region at physical `0xFEC00000`, accesses indexed registers through `reg` and `data`, reads ID/version, disables all redirection entries at initialization, and can enable a specific IRQ routed to a CPU APIC ID.

`ioapicinit()` warns if the hardware ID differs from `ioapicid` discovered by MP parsing. `ioapicenable()` installs vector `T_IRQ0 + irq` and writes destination CPU in the high redirection register.

Risk: assumes standard x86 I/O APIC MMIO layout and MP-discovered IDs. Incorrect routing can break disk, keyboard, or serial interrupts.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/ioapic.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/kalloc.c -->
# File Research: sources/teaching/xv6-public/kalloc.c

Read completely: 96 lines, 2160 bytes.

Implements a page-granularity physical memory allocator for kernel stacks, user pages, page tables, and pipe buffers. Free memory is represented as a singly linked list of `struct run` nodes stored in the free pages themselves.

Initialization occurs in two phases: `kinit1()` initializes the freelist without locking for early memory up to 4MB, and `kinit2()` adds the remaining pages and enables locking after other CPUs have started. `kfree()` validates page alignment/range, fills freed pages with junk byte 1, and pushes them onto the freelist. `kalloc()` pops one page or returns 0.

Risk: allocator only handles full 4096-byte pages. Range validation protects against freeing kernel image or out-of-range physical memory.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/kalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/kbd.c -->
# File Research: sources/teaching/xv6-public/kbd.c

Read completely: 50 lines, 925 bytes.

Implements PS/2 keyboard input translation. `kbdgetc()` reads status and data ports, tracks modifier state for shift/control/alt/capslock/e0 escape, handles key release scancodes, maps scancodes through normal/shift/control tables, and applies capslock letter case flipping. `kbdintr()` feeds `kbdgetc` to `consoleintr()`.

Risk: depends on the static tables and scancode constants in `kbd.h`. Only basic keyboard input is supported.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/kbd.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/kbd.h -->
# File Research: sources/teaching/xv6-public/kbd.h

Read completely: 112 lines, 3535 bytes.

Defines keyboard controller constants, modifier bits, special key codes, and scancode translation maps. `normalmap`, `shiftmap`, and `ctlmap` convert set-1 scancodes into ASCII/control/special values; `togglecode` and `shiftcode` update modifier state.

Risk: table indexes are raw scancodes masked by `0x7f`; correctness depends on keeping special key definitions outside normal byte ranges where intended.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/kbd.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/kill.c -->
# File Research: sources/teaching/xv6-public/kill.c

Read completely: 17 lines, 232 bytes.

User `kill` utility. It expects one or more PID arguments, converts each with `atoi`, calls the `kill` syscall, and exits. It prints usage if no PIDs are supplied.

Risk: does not report per-PID failures.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/kill.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/lapic.c -->
# File Research: sources/teaching/xv6-public/lapic.c

Read completely: 229 lines, 6098 bytes.

Implements local APIC setup, interrupt acknowledgement, AP startup IPIs, and CMOS RTC reading. It defines APIC register offsets and bit fields, with `lapic` initialized by MP parsing.

`lapicinit()` enables the APIC, configures periodic timer interrupts, masks local interrupt lines, masks performance counter interrupts when present, maps error interrupts, clears error status, acknowledges pending interrupts, sends a broadcast INIT deassert, and lowers task priority. `lapicid()` returns the APIC ID. `lapiceoi()` acknowledges interrupts. `lapicstartap()` programs the CMOS warm reset vector and sends INIT plus two STARTUP IPIs to boot an AP at a supplied physical address.

RTC support reads CMOS registers safely by checking update-in-progress and comparing two reads, converts BCD when needed, and returns a year offset by 2000.

Risk: timing and AP startup sequences are hardware-specific and simplified. `microdelay()` is empty, which is acceptable for xv6’s teaching/QEMU assumptions but not robust hardware timing.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/lapic.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/ln.c -->
# File Research: sources/teaching/xv6-public/ln.c

Read completely: 15 lines, 264 bytes.

User hard-link utility. It requires exactly `old` and `new` arguments, calls `link(old, new)`, reports failure, and exits.

Risk: no symbolic links exist in xv6; this is strictly hard-link creation.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/ln.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/log.c -->
# File Research: sources/teaching/xv6-public/log.c

Read completely: 234 lines, 5654 bytes.

Implements xv6’s physical redo log for filesystem transactions. The log allows concurrent filesystem syscalls by reserving log space in `begin_op()` and committing only when the outstanding operation count drops to zero in `end_op()`.

The on-disk log consists of a header block containing destination block numbers followed by logged block images. `initlog()` reads the superblock, records log start/size, and recovers. Recovery reads the header, installs any committed transaction to home blocks, clears the header, and writes it back.

Commit flow is `write_log()` to copy dirty cached blocks into log blocks, `write_head()` as the commit point, `install_trans()` to copy log blocks to home locations, then clear the header. `log_write()` absorbs duplicate block writes in the current transaction, records the block number, and marks the buffer `B_DIRTY` to prevent eviction before commit.

Risk: transaction sizing is bounded by `LOGSIZE` and `MAXOPBLOCKS`; callers must wrap metadata-changing operations in `begin_op()`/`end_op()`. Buffer pinning through `B_DIRTY` is essential to avoid losing logged updates.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/log.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/ls.c -->
# File Research: sources/teaching/xv6-public/ls.c

Read completely: 85 lines, 1525 bytes.

User `ls` utility. It formats names to `DIRSIZ` width, opens each path, stats it, prints file entries directly, and for directories reads `struct dirent` records, stats each child path, and prints name, type, inode number, and size.

Risk: path assembly uses a fixed 512-byte buffer and rejects paths too long for `path + "/" + DIRSIZ + NUL`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/ls.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/main.c -->
# File Research: sources/teaching/xv6-public/main.c

Read completely: 116 lines, 3264 bytes.

Kernel bootstrap C entry. `main()` performs early allocator setup, installs kernel page tables, discovers CPUs, initializes APIC/PIC/IOAPIC, console, UART, process table, trap vectors, buffer cache, file table, IDE, starts other CPUs, completes allocator initialization, creates the first user process, and enters `mpmain()`.

`startothers()` copies `entryother` to physical `0x7000`, allocates per-CPU stacks, writes AP bootstrap arguments before the code, sends startup IPIs, and waits for each CPU to set `started`. `mpenter()` is the AP-side C entry; `mpmain()` loads the IDT, marks CPU started, and enters the scheduler.

The file also defines `entrypgdir`, the boot page directory with 4MB identity and high-kernel mappings.

Risk: initialization order is critical, especially allocator phases, page table availability for APs, and filesystem/log initialization deferred to `forkret()` in process context.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/memide.c -->
# File Research: sources/teaching/xv6-public/memide.c

Read completely: 60 lines, 1231 bytes.

Implements an in-memory fake IDE disk for `kernelmemfs`. It uses linker-provided `_binary_fs_img_start` and `_binary_fs_img_size` as the disk image, records its size in blocks, and services `iderw()` by copying between buffer data and the embedded memory disk.

`ideintr()` is a no-op because operations complete synchronously. `iderw()` requires a locked buffer, rejects no-op requests, requires device 1, checks block range, copies data for writes or reads, clears dirty on write, and marks valid.

Risk: writes are not persistent beyond memory. Device number expectations differ from the normal IDE path.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/memide.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/memlayout.h -->
# File Research: sources/teaching/xv6-public/memlayout.h

Read completely: 15 lines, 667 bytes.

Defines xv6 physical and virtual memory layout constants: `EXTMEM`, `PHYSTOP`, `DEVSPACE`, `KERNBASE`, and `KERNLINK`. It also defines virtual/physical conversion macros `V2P`, `P2V`, plus assembler-friendly `V2P_WO` and `P2V_WO`.

Risk: these constants are fundamental to boot, VM mappings, allocator bounds, and device mapping. `PHYSTOP` must remain below `DEVSPACE` as checked by `setupkvm()`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/memlayout.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/mkdir.c -->
# File Research: sources/teaching/xv6-public/mkdir.c

Read completely: 23 lines, 327 bytes.

User `mkdir` utility. It requires one or more paths, calls `mkdir()` for each, reports the first failure, and exits.

Risk: stops after the first failed create.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/mkdir.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/mkfs.c -->
# File Research: sources/teaching/xv6-public/mkfs.c

Read completely: 297 lines, 6140 bytes.

Host-side filesystem image builder for xv6. It creates an `fs.img` with boot block, superblock, log, inode blocks, bitmap, and data blocks according to `fs.h` and `param.h`. It uses little-endian conversion helpers `xshort()` and `xint()` so the image matches xv6’s on-disk format.

`main()` computes metadata layout, zeroes all blocks, writes the superblock, allocates root inode, appends `.` and `..`, then adds each supplied file as a root directory entry. Leading underscores are stripped from installed program names. It rounds root directory size to a full block and marks all allocated blocks in the bitmap.

Helpers write/read sectors and inodes, allocate inodes, write the bitmap, and append file data with direct and single-indirect block allocation.

Risk: host and target filesystem constants must match. The code assumes one xv6 block equals one disk sector and asserts format divisibility properties.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/mmu.h -->
# File Research: sources/teaching/xv6-public/mmu.h

Read completely: 181 lines, 6571 bytes.

Defines x86 MMU, segmentation, paging, task-state, gate-descriptor, and trapframe structures/constants. It includes eflags and control-register bits, segment selector indices, descriptor privilege constants, descriptor constructors `SEG` and `SEG16`, page-table indexing macros, page constants, PTE flags, address/flag extraction macros, and `pte_t`.

For C code, it defines `struct segdesc`, `struct taskstate`, `struct gatedesc`, the `SETGATE` macro, and `struct trapframe` matching the stack layout created by hardware and `trapasm.S`.

Risk: structure bitfields and trapframe layout are hardware ABI. `swtch`, traps, TSS setup, and VM code depend on exact definitions.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/mmu.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/mp.c -->
# File Research: sources/teaching/xv6-public/mp.c

Read completely: 139 lines, 3161 bytes.

Implements Intel Multiprocessor Specification discovery. It searches BIOS memory regions for the MP floating pointer structure, validates checksums, locates and validates the MP configuration table, extracts CPU APIC IDs and I/O APIC ID, records `lapic` address, and optionally switches interrupt mode through IMCR.

Global state includes `cpus[NCPU]`, `ncpu`, and `ioapicid`. `mpinit()` requires a suitable MP table and panics otherwise.

Risk: supports MP spec versions 1 and 4, skips/defaults many advanced cases, and assumes an SMP-capable environment.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/mp.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/mp.h -->
# File Research: sources/teaching/xv6-public/mp.h

Read completely: 56 lines, 2146 bytes.

Defines structures for MP floating pointer, MP configuration table header, processor entries, I/O APIC entries, and MP table entry type constants. These correspond to the Intel MP Specification table formats parsed by `mp.c`.

Risk: structure layout must match firmware table bytes exactly.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/mp.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/param.h -->
# File Research: sources/teaching/xv6-public/param.h

Read completely: 14 lines, 760 bytes.

Defines xv6 system sizing constants: max processes, kernel stack size, CPUs, open files per process/system, active inodes, device count, root device, exec args, max log operation blocks, log size, buffer count, and filesystem size.

Risk: many subsystems depend on these fixed bounds. `LOGSIZE`, `NBUF`, and `MAXOPBLOCKS` are especially coupled to logging and file write chunking.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/param.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/picirq.c -->
# File Research: sources/teaching/xv6-public/picirq.c

Read completely: 19 lines, 426 bytes.

Disables the legacy 8259A PIC by masking all interrupts on the master and slave PIC data ports. xv6 assumes SMP/APIC hardware and routes interrupts through the APICs instead.

Risk: no `picenable()` body is present in this file despite its declaration in `defs.h`; normal xv6 operation relies on IOAPIC routing.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/picirq.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/pipe.c -->
# File Research: sources/teaching/xv6-public/pipe.c

Read completely: 121 lines, 2411 bytes.

Implements kernel pipes as fixed 512-byte circular buffers with read/write counters and endpoint-open flags. `pipealloc()` allocates two `struct file` entries plus a pipe page, initializes one read end and one write end, and handles cleanup on failure.

`pipewrite()` writes byte by byte, sleeping when the pipe is full and waking readers. It returns `-1` if the read end is closed or the process is killed. `piperead()` sleeps while empty if a writer remains, copies available bytes, wakes writers, and returns the byte count. `pipeclose()` marks an endpoint closed, wakes the opposite side, and frees the pipe when both ends are closed.

Risk: correctness depends on sleep/wakeup using `p->nread` and `p->nwrite` channels under the pipe lock, and on file close paths supplying whether the closing file is writable.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/pr.pl -->
# File Research: sources/teaching/xv6-public/pr.pl

Read completely: 36 lines, 581 bytes.

Perl formatter for the xv6 print pipeline. It paginates stdin into 50-line pages, prints timestamp/header/page labels, strips `//DOC` annotations, pads pages, and emits optional sheet labels inferred from numbered input.

Risk: depends on line-numbered input from `runoff1` and is used for print/PDF generation only.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/pr.pl -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/printf.c -->
# File Research: sources/teaching/xv6-public/printf.c

Read completely: 85 lines, 1472 bytes.

User-space formatted output helper. `printf(fd, fmt, ...)` supports `%d`, `%x`, `%p`, `%s`, `%c`, and `%%`, writing characters through the `write` syscall. `printint()` handles decimal and hexadecimal conversion.

Risk: no width/precision/long support; argument walking assumes xv6 32-bit calling convention.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/printf.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/printpcs -->
# File Research: sources/teaching/xv6-public/printpcs

Read completely: 14 lines, 367 bytes.

Shell helper for decoding panic program-counter lists. It finds an `addr2line` capable of `elf32-i386`, enables supported pretty-printing flags from help output, and invokes it against the `kernel` binary with supplied addresses.

Risk: depends on host `addr2line` availability and current `kernel` debug symbols.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/printpcs -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/proc.c -->
# File Research: sources/teaching/xv6-public/proc.c

Read completely: 534 lines, 11717 bytes.

Implements process table management, process creation, first user process setup, memory growth, fork/exit/wait, scheduling, sleep/wakeup, kill, and process dumping. The global `ptable` is protected by `ptable.lock`; `initproc` and `nextpid` track init and PID assignment.

`allocproc()` finds an unused slot, assigns PID, allocates a kernel stack, lays out trapframe and initial context so the process starts at `forkret()` and returns through `trapret`. `userinit()` builds the first process running embedded `initcode`. `fork()` copies address space, trapframe, open files, cwd, and name, then marks child runnable. `exit()` closes files, drops cwd in a transaction, reparents children to init, wakes parent, and becomes zombie. `wait()` reaps zombie children and frees kernel stack/page table.

The scheduler loops over runnable processes on each CPU, switches address spaces, marks running, and calls `swtch`. `sleep()` atomically transitions a process to sleeping while avoiding missed wakeups via `ptable.lock`; `wakeup()` marks matching sleepers runnable. `kill()` sets the killed flag and wakes sleepers.

Risk: locking and interrupt state invariants are strict. `sched()` checks that only `ptable.lock` is held, interrupts are disabled, and the process is not still running.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/proc.h -->
# File Research: sources/teaching/xv6-public/proc.h

Read completely: 58 lines, 2270 bytes.

Defines per-CPU and per-process state. `struct cpu` stores APIC ID, scheduler context, TSS, GDT, started flag, nested interrupt-disable state, previous interrupt state, and current process pointer. `struct context` matches the callee-saved register layout used by `swtch.S`.

`enum procstate` defines process lifecycle states. `struct proc` stores memory size, page directory, kernel stack, state, PID, parent, trapframe, context, sleep channel, killed flag, open files, cwd, and debug name.

Risk: `struct context` layout must match `swtch.S`; `struct proc` fields are used across scheduler, traps, syscalls, VM, and filesystem code.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/proc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/rm.c -->
# File Research: sources/teaching/xv6-public/rm.c

Read completely: 23 lines, 322 bytes.

User `rm` utility. It requires at least one path, calls `unlink()` for each, reports the first failure, and exits.

Risk: stops after the first failed deletion.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/rm.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/runoff -->
# File Research: sources/teaching/xv6-public/runoff

Read completely: 246 lines, 5042 bytes.

Shell script for generating the xv6 book-style PDF. It formats files listed in `runoff.list` through `runoff1`, builds a table of contents, checks page alignment rules from `runoff.spec`, extracts definitions and references, produces cross-reference pages, emits PostScript with `mpage`, optionally embeds a nicer typewriter font from git, and converts to `xv6.pdf`.

Risk: depends on host tools such as `awk`, `pr`, `perl`, `mpage`, `ps2pdf`, and git font availability. It is documentation tooling, not runtime code.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/runoff -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/runoff1 -->
# File Research: sources/teaching/xv6-public/runoff1

Read completely: 108 lines, 2318 bytes.

Perl script that numbers and paginates one source file for the print pipeline. It supports `-v` and `-n`, warns on lines of length at least 75, honors `PAGEBREAK!` and `PAGEBREAK:<n>` markers, chooses page breaks near function boundaries or blanks, and pads pages to 50 numbered lines.

Risk: output format is tailored for `runoff` and `pr.pl`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/runoff1 -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/sh.c -->
# File Research: sources/teaching/xv6-public/sh.c

Read completely: 493 lines, 8240 bytes.

User shell implementation. It defines command AST node types for exec, redirection, pipe, list, and background commands, parses command lines, and executes by forking and wiring file descriptors.

`runcmd()` dispatches on command type: `EXEC` calls `exec`, `REDIR` closes and opens the target fd, `PIPE` creates a pipe and forks left/right commands with fd duplication, `LIST` runs left then right, and `BACK` starts a command without waiting. `main()` ensures fds 0, 1, and 2 are open on `console`, reads commands, handles `cd` in the parent process, forks child execution, and waits.

The parser tokenizes whitespace and symbols, supports `;`, `&`, `|`, `<`, `>`, `>>`, grouping with parentheses, and NUL-terminates token spans in-place after parsing.

Risk: parser and executor are intentionally small. `>>` is parsed but maps to the same open mode as `>` because xv6 has no append flag.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/sh.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/show1 -->
# File Research: sources/teaching/xv6-public/show1

Read completely: 3 lines, 135 bytes.

Shell helper that runs `runoff1`, formats through `pr.pl`, renders with `mpage` using the Lucida font, and opens the resulting PostScript in `gv`.

Risk: documentation preview helper only; depends on local print tools and font file.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/show1 -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/sign.pl -->
# File Research: sources/teaching/xv6-public/sign.pl

Read completely: 19 lines, 363 bytes.

Perl script that signs the boot block. It reads up to 1000 bytes, rejects input larger than 510 bytes, pads to 510 bytes with zeros, appends boot signature bytes `0x55 0xAA`, and overwrites the bootblock file.

Risk: enforces BIOS boot-sector size/signature constraints. Build fails if boot code grows beyond 510 bytes.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/sign.pl -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/sleeplock.c -->
# File Research: sources/teaching/xv6-public/sleeplock.c

Read completely: 56 lines, 812 bytes.

Implements sleep locks for long-held kernel locks that may sleep, such as inode and buffer locks. A sleeplock wraps a spinlock protecting `locked`, owner PID, and metadata.

`acquiresleep()` sleeps on the sleeplock while held, then marks it locked by current PID. `releasesleep()` clears ownership and wakes sleepers. `holdingsleep()` checks whether the current process holds it.

Risk: requires a current process for ownership checks; not suitable for early boot or interrupt contexts.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/sleeplock.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/sleeplock.h -->
# File Research: sources/teaching/xv6-public/sleeplock.h

Read completely: 10 lines, 265 bytes.

Defines `struct sleeplock`: locked flag, internal spinlock, debug name, and owner PID. Used for buffers and inodes.

Risk: structure embeds `struct spinlock`, so include order depends on `spinlock.h` being available first.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/sleeplock.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/spinlock.c -->
# File Research: sources/teaching/xv6-public/spinlock.c

Read completely: 126 lines, 2791 bytes.

Implements xv6 spinlocks and interrupt-disable nesting. `acquire()` disables interrupts with `pushcli()`, checks for recursive acquisition, spins with atomic `xchg`, issues a memory barrier, and records CPU/call stack. `release()` checks ownership, clears debug info, barriers, atomically clears `locked`, and restores interrupt state through `popcli()`.

`getcallerpcs()` walks saved frame pointers for debugging. `holding()` checks current CPU ownership with interrupts disabled. `pushcli()` and `popcli()` maintain per-CPU nesting depth and restore interrupts only when the outermost disable is popped and interrupts were previously enabled.

Risk: depends on frame pointers (`-fno-omit-frame-pointer`) for call stack capture. Locking rules are central to scheduler, sleep/wakeup, and interrupt safety.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/spinlock.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/spinlock.h -->
# File Research: sources/teaching/xv6-public/spinlock.h

Read completely: 11 lines, 315 bytes.

Defines `struct spinlock`: locked flag, debug name, owning CPU pointer, and captured call stack PCs. Used throughout the kernel for short critical sections.

Risk: debug fields are written by `spinlock.c`; ownership checks assume `cpu` is reliable while interrupts are disabled.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/spinp -->
# File Research: sources/teaching/xv6-public/spinp

Read completely: 16 lines, 240 bytes.

Shell helper for running SPIN/Promela models. It validates a single `.p` file argument, removes old trail output, runs `spin -a`, compiles `pan.c` with safety/reachability flags, runs `pan -i`, cleans generated files, and if a trail remains, replays it with `spin -t -p`.

Risk: formal-modeling helper only; depends on `spin` and host C compiler.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/spinp -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/stat.h -->
# File Research: sources/teaching/xv6-public/stat.h

Read completely: 11 lines, 294 bytes.

Defines file type constants `T_DIR`, `T_FILE`, and `T_DEV`, plus `struct stat` returned by `fstat`/`stat`: type, device, inode number, link count, and size.

Risk: shared user/kernel ABI for file metadata.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/stressfs.c -->
# File Research: sources/teaching/xv6-public/stressfs.c

Read completely: 49 lines, 1028 bytes.

User stress test for filesystem/IDE queue races. It forks up to four processes, each writing and then reading twenty 512-byte blocks to a distinct `stressfsN` file. The comments document a race demonstration if `iderw()` queue locking is deliberately weakened.

Risk: test intentionally stresses concurrent disk queue and filesystem paths but performs minimal validation of read contents.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/stressfs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/string.c -->
# File Research: sources/teaching/xv6-public/string.c

Read completely: 105 lines, 1441 bytes.

Kernel string/memory helpers. Implements optimized `memset()` using `stosl` for aligned word fills, `memcmp()`, overlap-safe `memmove()`, `memcpy()` as `memmove()`, `strncmp()`, `strncpy()`, NUL-guaranteed `safestrcpy()`, and `strlen()`.

Risk: no libc dependency exists in the kernel, so these routines are foundational. `strncpy()` preserves standard non-guaranteed-NUL behavior, while `safestrcpy()` is used where termination matters.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/string.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/swtch.S -->
# File Research: sources/teaching/xv6-public/swtch.S

Read completely: 29 lines, 542 bytes.

Implements low-level context switch `swtch(struct context **old, struct context *new)`. It saves callee-saved registers on the current stack, stores the old stack pointer through `old`, switches `%esp` to `new`, restores callee-saved registers from the new stack, and returns to the new context’s saved `eip`.

Risk: stack layout must match `struct context` in `proc.h` and the setup performed by `allocproc()`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/swtch.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/syscall.c -->
# File Research: sources/teaching/xv6-public/syscall.c

Read completely: 145 lines, 3470 bytes.

Implements syscall argument fetching and dispatch. `fetchint()` and `fetchstr()` validate user addresses against current process size. `argint()`, `argptr()`, and `argstr()` extract syscall arguments from the saved user stack in the trapframe.

The syscall table maps syscall numbers to `sys_*` handlers. `syscall()` reads the syscall number from `%eax`, invokes the handler if valid, stores the return value back into `%eax`, and reports unknown calls.

Risk: pointer validation is simple bound checking against contiguous user memory. Negative sizes and wraparound are explicitly guarded in `argptr()`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/syscall.h -->
# File Research: sources/teaching/xv6-public/syscall.h

Read completely: 22 lines, 485 bytes.

Defines syscall numbers from `SYS_fork` through `SYS_close`. These constants are shared by user stubs in `usys.S`, kernel dispatch in `syscall.c`, and tests.

Risk: syscall number changes require coordinated user and kernel updates.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/syscall.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/sysfile.c -->
# File Research: sources/teaching/xv6-public/sysfile.c

Read completely: 444 lines, 7377 bytes.

Implements filesystem-related syscalls: descriptor lookup/allocation, `dup`, `read`, `write`, `close`, `fstat`, `link`, `unlink`, `open`, `mkdir`, `mknod`, `chdir`, `exec`, and `pipe`.

`argfd()` validates file descriptor arguments and retrieves `struct file`. `fdalloc()` installs a file in the current process. `sys_link()` increments link count, links the new path, and rolls back on failure. `sys_unlink()` rejects `.`/`..`, rejects non-empty directories, clears the directory entry, updates directory and inode link counts, and relies on `iput()` for final freeing. `create()` handles existing-file open semantics and new inode/directory creation including `.` and `..`.

`sys_open()` creates or looks up inodes, rejects writing directories, allocates a file and fd, and sets readability/writability. `sys_chdir()` validates directory targets and swaps cwd. `sys_exec()` marshals user argv pointers before calling `exec()`. `sys_pipe()` allocates kernel pipe files and returns two fds to user memory.

Risk: transaction boundaries around inode reference drops and metadata changes are critical. Error paths must release inodes/files and undo link counts correctly.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/sysproc.c -->
# File Research: sources/teaching/xv6-public/sysproc.c

Read completely: 91 lines, 1099 bytes.

Implements process/time syscalls: `fork`, `exit`, `wait`, `kill`, `getpid`, `sbrk`, `sleep`, and `uptime`. Most are thin wrappers over process functions after argument extraction.

`sys_sleep()` records current `ticks`, sleeps on `ticks` under `tickslock` until enough timer ticks pass, and aborts if killed. `sys_uptime()` returns a locked snapshot of `ticks`.

Risk: `sys_sbrk()` returns the old break and relies on `growproc()` for allocation/deallocation correctness.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/sysproc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/trap.c -->
# File Research: sources/teaching/xv6-public/trap.c

Read completely: 112 lines, 2657 bytes.

Implements IDT setup and trap/interrupt handling. `tvinit()` installs all 256 vectors as interrupt gates and makes `T_SYSCALL` a user-callable trap gate; it initializes `tickslock`. `idtinit()` loads the IDT.

`trap()` handles syscalls specially, checking killed state before and after dispatch. It handles timer interrupts by incrementing `ticks` on CPU 0 and waking sleepers, IDE, keyboard, serial, and spurious interrupts with EOI handling. Unexpected kernel traps panic; unexpected user traps mark the process killed. Timer interrupts force running processes to yield, and killed user processes exit before returning to user space.

Risk: trapframe state is central to syscall return values, scheduling, and killing misbehaving processes. Correct EOI ordering matters for APIC interrupt delivery.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/trapasm.S -->
# File Research: sources/teaching/xv6-public/trapasm.S

Read completely: 32 lines, 486 bytes.

Common assembly entry/exit path for traps. `alltraps` saves segment registers and general-purpose registers, loads kernel data segments, pushes `%esp` as a `struct trapframe *`, calls `trap()`, then falls through to `trapret`.

`trapret` restores registers and segment registers, skips trap number and error code, and executes `iret`.

Risk: stack layout must match `struct trapframe` in `mmu.h` and vector stubs generated by `vectors.pl`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/trapasm.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/traps.h -->
# File Research: sources/teaching/xv6-public/traps.h

Read completely: 38 lines, 1548 bytes.

Defines x86 trap numbers, xv6 syscall trap number, default trap value, IRQ vector base, and IRQ numbers for timer, keyboard, COM1, IDE, error, and spurious interrupts.

Risk: these constants must align with IDT setup, generated vectors, APIC routing, and user syscall stubs.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/traps.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/types.h -->
# File Research: sources/teaching/xv6-public/types.h

Read completely: 4 lines, 110 bytes.

Defines basic xv6 integer aliases: `uint`, `ushort`, `uchar`, and `pde_t`. Shared by kernel and user code.

Risk: assumes 32-bit `unsigned int` for `uint` and page directory entries.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/types.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/uart.c -->
# File Research: sources/teaching/xv6-public/uart.c

Read completely: 77 lines, 1288 bytes.

Implements 16550-style serial port initialization, output, and interrupt input. `uartinit()` disables interrupts, configures baud divisor, 8N1 format, FIFO, modem control, probes for serial presence, enables interrupts, and drains pending input. `uartputc()` waits for transmit-ready and writes a byte. `uartintr()` passes `uartgetc()` to `consoleintr()`.

Risk: output waits with a bounded spin loop and panics if transmit readiness does not appear. If serial hardware is absent, output is skipped.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/uart.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/ulib.c -->
# File Research: sources/teaching/xv6-public/ulib.c

Read completely: 106 lines, 1280 bytes.

User-space library helpers: `strcpy`, `strcmp`, `strlen`, `memset`, `strchr`, `gets`, `stat`, `atoi`, and `memmove`. `stat()` opens the path, calls `fstat`, then closes it. `gets()` reads from stdin until newline/carriage return or buffer limit.

Risk: `memmove()` here copies forward only and is not overlap-safe like the kernel version. `gets()` is bounded by caller-supplied max.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/ulib.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/umalloc.c -->
# File Research: sources/teaching/xv6-public/umalloc.c

Read completely: 90 lines, 1652 bytes.

User-space K&R-style allocator. It maintains a circular free list of `Header` blocks, coalesces adjacent free blocks in `free()`, requests more memory from `sbrk()` in `morecore()`, and allocates by first-fit in `malloc()`.

`morecore()` requests at least 4096 header units, not bytes, from `sbrk()`.

Risk: allocator assumes valid frees and a linear heap grown by `sbrk()`. No double-free detection exists.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/umalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/user.h -->
# File Research: sources/teaching/xv6-public/user.h

Read completely: 39 lines, 922 bytes.

User-space declarations for system calls and user library functions. It declares process, file, directory, memory, sleep/time, and utility APIs used by xv6 user programs.

Risk: this is the user ABI declaration surface and must stay aligned with `usys.S`, `syscall.h`, and library implementations.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/user.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/usertests.c -->
# File Research: sources/teaching/xv6-public/usertests.c

Read completely: 1803 lines, 34697 bytes.

Comprehensive xv6 user-level regression test program. It exercises filesystem transactions, inode reference handling, open/write/read/unlink/link/mkdir/chdir edge cases, concurrent creation/deletion, pipes, fork/exit/wait, memory allocation and `sbrk`, syscall argument validation, BSS zeroing, exec argument limits, user I/O privilege faults, and process preemption/kill behavior.

Filesystem-focused tests include `iputtest`, `exitiputtest`, `openiputtest`, `opentest`, `writetest`, `writetest1`, `createtest`, `dirtest`, `sharedfd`, `fourfiles`, `createdelete`, `unlinkread`, `linktest`, `concreate`, `linkunlink`, `bigdir`, `subdir`, `bigwrite`, `bigfile`, `fourteen`, `rmdot`, `dirfile`, `iref`, and disabled-style `fsfull`. These cover transaction-wrapped `iput`, directory emptiness, hard link semantics, concurrent metadata operations, direct/indirect blocks, `DIRSIZ` truncation behavior, invalid directory/file path operations, and large write log splitting.

Process/memory/syscall tests include `pipe1`, `preempt`, `exitwait`, `mem`, `forktest`, `sbrktest`, `validatetest`, `bsstest`, `bigargtest`, `uio`, and `argptest`. They verify pipe data ordering, scheduler preemption, wait/exit races, graceful memory exhaustion, heap growth/shrink/reuse, kernel memory protection, pointer validation, zeroed BSS, exec stack bounds, I/O privilege enforcement, and negative-size syscall argument handling.

`main()` prevents repeated runs using `usertests.ran`, then runs the suite in a fixed order and finally calls `exectest()`, which replaces the test process with `echo ALL TESTS PASSED`.

Risk: tests are destructive to the filesystem image and intentionally create/unlink many names. Some tests assume small xv6 constants such as `NINODE`, `MAXFILE`, `DIRSIZ`, `MAXARG`, and `KERNBASE`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/usertests.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/usys.S -->
# File Research: sources/teaching/xv6-public/usys.S

Read completely: 31 lines, 461 bytes.

Defines user-space syscall stubs with a `SYSCALL(name)` macro. Each stub loads the syscall number into `%eax`, executes `int $T_SYSCALL`, and returns. Stubs cover all syscalls declared in `user.h`.

Risk: syscall names and numbers must match `syscall.h` and kernel dispatch.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/usys.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/vectors.pl -->
# File Research: sources/teaching/xv6-public/vectors.pl

Read completely: 47 lines, 989 bytes.

Perl generator for `vectors.S`. It emits 256 vector entry labels, pushes a synthetic zero error code for traps that do not provide one, pushes the trap number, and jumps to `alltraps`. It then emits a `vectors` table containing pointers to all vector labels.

Risk: the set of x86 traps with hardware error codes must be correct so `trapasm.S` can uniformly skip `trapno` and `errcode`.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/vectors.pl -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/vm.c -->
# File Research: sources/teaching/xv6-public/vm.c

Read completely: 394 lines, 9918 bytes.

Implements x86 segmentation and paging for xv6. `seginit()` installs flat kernel/user code/data descriptors and per-CPU GDT. `walkpgdir()` locates or allocates page tables. `mappages()` maps virtual ranges to physical ranges.

`setupkvm()` creates a page directory with kernel mappings for I/O space, kernel text/rodata, kernel data/free memory, and high device space. `kvmalloc()` installs the kernel page table. `switchkvm()` and `switchuvm()` load `cr3`; `switchuvm()` also installs a TSS so traps from user mode use the process kernel stack and blocks user I/O instructions.

User memory helpers include `inituvm()`, `loaduvm()`, `allocuvm()`, `deallocuvm()`, `freevm()`, `clearpteu()`, `copyuvm()`, `uva2ka()`, and `copyout()`. Address spaces are contiguous from 0 upward and copied eagerly on fork.

Risk: no demand paging or COW. Pointer safety depends on PTE_U checks in `uva2ka()` and contiguous `proc->sz` bounds in syscall argument validation.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/vm.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/wc.c -->
# File Research: sources/teaching/xv6-public/wc.c

Read completely: 54 lines, 820 bytes.

User `wc` utility. It counts lines, words, and bytes from stdin or named files, using whitespace detection through `strchr(" \r\t\n\v", c)`, and prints counts plus name.

Risk: simple byte-oriented counting; no Unicode or locale handling.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/wc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/x86.h -->
# File Research: sources/teaching/xv6-public/x86.h

Read completely: 183 lines, 3269 bytes.

Defines inline assembly helpers for x86 port I/O, string I/O/fill operations, descriptor-table loads, task-register load, flags reads, interrupt enable/disable, atomic exchange, `cr2` read, and `cr3` load. It includes `inb`, `insl`, `outb`, `outw`, `outsl`, `stosb`, `stosl`, `lgdt`, `lidt`, `ltr`, `readeflags`, `loadgs`, `cli`, `sti`, `xchg`, `rcr2`, and `lcr3`.

Risk: these functions expose privileged x86 instructions to kernel C code and rely on GCC inline assembly constraints for correctness.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/x86.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-public/zombie.c -->
# File Research: sources/teaching/xv6-public/zombie.c

Read completely: 14 lines, 214 bytes.

Small user program that forks, lets the child exit first while the parent sleeps briefly, then exits. It demonstrates zombie creation and reparenting behavior.

Risk: used as a teaching/demo utility for process lifecycle rather than a validation-heavy test.
<!-- END FILE RESEARCH: sources/teaching/xv6-public/zombie.c -->