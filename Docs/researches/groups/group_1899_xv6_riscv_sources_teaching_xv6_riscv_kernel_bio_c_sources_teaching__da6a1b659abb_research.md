# Group Research: group_1899_xv6_riscv_sources_teaching_xv6_riscv_kernel_bio_c_sources_teaching__da6a1b659abb

Scope verified against `Docs/research_subset_a.md`: `sources/teaching/xv6-riscv` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/bio.c -->
# File Research: sources/teaching/xv6-riscv/kernel/bio.c

Implements xv6’s buffer cache: a fixed `NBUF` array of `struct buf` objects arranged as an LRU doubly linked list. The cache gives filesystem and log code a synchronized block-level interface through `bread`, `bwrite`, `brelse`, `bpin`, and `bunpin`.

Important behavior:
- `binit()` initializes the global cache lock, each buffer sleeplock, and the LRU list.
- `bget()` first searches for an existing `(dev, blockno)` buffer, otherwise recycles an unused least-recently-used buffer.
- `bread()` loads a block through `virtio_disk_rw()` only when `valid == 0`.
- `bwrite()` requires the buffer sleeplock and writes synchronously to the virtio disk.
- `brelse()` releases the sleeplock, drops `refcnt`, and moves unused buffers to the MRU head.
- `bpin()`/`bunpin()` adjust `refcnt` so the log can keep dirty buffers resident until commit.

Filesystem relevance: this file is the shared synchronization point between inode/block allocation code, the write-ahead log, and the virtio disk driver. The split between a global spinlock and per-buffer sleeplocks is central to avoiding duplicate cached copies while still allowing long block use.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/buf.h -->
# File Research: sources/teaching/xv6-riscv/kernel/buf.h

Defines `struct buf`, the in-memory representation of a cached disk block.

Fields:
- `valid` tracks whether `data` has been loaded from disk.
- `disk` is used by the virtio driver to indicate an in-flight disk operation.
- `dev` and `blockno` identify the cached block.
- `lock` is a sleeplock protecting block contents.
- `refcnt`, `prev`, and `next` support cache lifetime and LRU ordering.
- `data[BSIZE]` stores the 1024-byte filesystem block.

Filesystem relevance: this structure is shared by the buffer cache, log, filesystem, and virtio driver, making it the common unit for block I/O and transaction pinning.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/console.c -->
# File Research: sources/teaching/xv6-riscv/kernel/console.c

Implements console input and output over UART, including the console device entries in `devsw[CONSOLE]`.

Important behavior:
- `consputc()` writes characters synchronously through `uartputc_sync()` and handles backspace display.
- `consolewrite()` copies user/kernel source data in small chunks and sends it through `uartwrite()`.
- `consoleread()` blocks until a complete line, EOF, or full buffer is available, then copies to user/kernel destination.
- `consoleintr()` handles UART input characters, editing controls, EOF, process dump, echoing, and wakeups.
- `consoleinit()` initializes the console lock, UART, and device switch read/write handlers.

Filesystem relevance: console is exposed as a `T_DEVICE` inode via the file/device layer. It participates in normal `read`/`write` paths through `file.c` and `sysfile.c`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/console.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/defs.h -->
# File Research: sources/teaching/xv6-riscv/kernel/defs.h

Central declaration header for kernel-internal functions and forward declarations. It groups prototypes by implementation file.

Major API groups:
- Buffer cache: `binit`, `bread`, `bwrite`, `brelse`, pin/unpin.
- Filesystem: inode allocation, locking, path lookup, read/write, stat, truncation, orphan reclaim.
- File table: allocation, dup, close, read/write/stat dispatch.
- Log: `begin_op`, `end_op`, `log_write`.
- Process, VM, traps, locks, UART, PLIC, virtio disk, and syscall helpers.

Filesystem relevance: this file captures the cross-module contract among `bio.c`, `fs.c`, `log.c`, `file.c`, `sysfile.c`, `proc.c`, and `vm.c`. It also shows the teaching kernel’s intentionally flat internal API surface.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/defs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/elf.h -->
# File Research: sources/teaching/xv6-riscv/kernel/elf.h

Defines the ELF executable metadata consumed by `exec.c`.

Contents:
- `ELF_MAGIC` identifies valid ELF binaries.
- `struct elfhdr` defines the ELF file header, including entry point and program header table location.
- `struct proghdr` defines loadable segment metadata.
- `ELF_PROG_LOAD` and segment permission flags map ELF program headers to user PTE permissions.

Filesystem relevance: executable loading reads ELF headers and segments from inodes using `readi()`, making this header part of the filesystem-to-process image path.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/elf.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/entry.S -->
# File Research: sources/teaching/xv6-riscv/kernel/entry.S

Boot entry assembly loaded by QEMU at `0x80000000`.

Important behavior:
- Defines `_entry` in `.text`.
- Computes an initial stack pointer from `stack0 + (hartid + 1) * 4096`.
- Reads `mhartid` to select a per-CPU boot stack.
- Calls `start()` in `start.c`.
- Spins forever if `start()` returns.

Filesystem relevance: indirect. It is part of the boot chain that eventually initializes memory, traps, buffer cache, inode table, file table, virtio disk, and the first process.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/entry.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/exec.c -->
# File Research: sources/teaching/xv6-riscv/kernel/exec.c

Implements `kexec()`, the kernel side of `exec`.

Important behavior:
- Opens an executable through `namei()` inside a filesystem transaction.
- Validates `ELF_MAGIC`, iterates program headers, allocates user memory, and loads segments with `loadseg()`.
- `flags2perm()` maps ELF write/execute flags to PTE bits.
- Builds a guarded user stack and copies argument strings/pointers with `copyout()`.
- Commits the new process image only after all allocation and loading succeeds.
- Frees the old page table after switching `p->pagetable`, `p->sz`, `epc`, and `sp`.

Filesystem relevance: this is a key consumer of inode reads. It relies on `readi()`, path lookup, inode locking, and log transaction boundaries, linking filesystem namespace state to process image creation.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/fcntl.h -->
# File Research: sources/teaching/xv6-riscv/kernel/fcntl.h

Defines open flags used by `sys_open()`:
- `O_RDONLY`
- `O_WRONLY`
- `O_RDWR`
- `O_CREATE`
- `O_TRUNC`

Filesystem relevance: these constants control file creation, read/write permissions, directory open restrictions, and truncation behavior in `sysfile.c`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/fcntl.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/file.c -->
# File Research: sources/teaching/xv6-riscv/kernel/file.c

Implements the global open-file table and high-level file operations over pipes, devices, and inodes.

Important behavior:
- `fileinit()` initializes the table lock.
- `filealloc()` finds a free `struct file` and sets `ref = 1`.
- `filedup()` increments file references.
- `fileclose()` decrements references and closes pipes or drops inode references in a transaction.
- `filestat()` locks an inode and copies `struct stat` to user memory.
- `fileread()` dispatches to pipe, device, or inode read and advances inode offsets.
- `filewrite()` dispatches to pipe/device/inode writes and chunks inode writes to fit log transaction capacity.

Filesystem relevance: this is the VFS-like dispatch layer of xv6. It bridges syscall file descriptors to inode operations, pipe operations, and device switch handlers.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/file.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/file.h -->
# File Research: sources/teaching/xv6-riscv/kernel/file.h

Defines core file-layer structures.

Contents:
- `struct file` represents an open file descriptor target with type, refcount, readability/writability, pipe pointer, inode pointer, offset, and device major number.
- Device-number macros: `major`, `minor`, `mkdev`.
- `struct inode` is the in-memory inode cache entry, with refcount, sleeplock, validity flag, copied disk inode fields, and block addresses.
- `struct devsw` maps major device numbers to read/write functions.
- `CONSOLE` is major device 1.

Filesystem relevance: this header defines the in-memory shape used by both the file table and inode cache. `struct inode` is the primary object shared by `fs.c`, `file.c`, `sysfile.c`, and `exec.c`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/file.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/fs.c -->
# File Research: sources/teaching/xv6-riscv/kernel/fs.c

Implements xv6’s filesystem layers: superblock reading, block allocation, inode cache, inode content, directories, and path lookup.

Important behavior:
- `fsinit()` reads and validates the superblock, initializes the log, and reclaims orphaned inodes.
- `balloc()` and `bfree()` manage bitmap-backed block allocation.
- `ialloc()`, `iget()`, `idup()`, `ilock()`, `iupdate()`, `iput()`, and `iunlock*()` manage disk and in-memory inode lifecycle.
- `ireclaim()` scans for allocated inodes with zero links at boot and forces normal `iput()` cleanup.
- `bmap()` maps logical file blocks to disk blocks, allocating direct or single-indirect blocks as needed.
- `itrunc()` frees all direct and indirect blocks and updates inode size.
- `readi()` and `writei()` perform inode data transfer through the buffer cache and log.
- Directory helpers implement fixed-size directory entries and name comparison.
- `namex()`, `namei()`, and `nameiparent()` implement absolute/relative path traversal with careful inode lock/ref handling.

Filesystem relevance: this is the core local filesystem implementation. It demonstrates xv6’s simple Unix-style inode filesystem with a bitmap allocator, direct plus single-indirect addressing, logged metadata/data updates, and directory-as-file semantics.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/fs.h -->
# File Research: sources/teaching/xv6-riscv/kernel/fs.h

Defines the on-disk filesystem format shared by kernel and `mkfs`.

Contents:
- `ROOTINO`, `BSIZE`, and disk layout comments.
- `struct superblock` describing total size, data block count, inode count, log layout, inode start, and bitmap start.
- `FSMAGIC`.
- File addressing constants: `NDIRECT`, `NINDIRECT`, `MAXFILE`.
- `struct dinode`, the on-disk inode format.
- Addressing macros: `IPB`, `IBLOCK`, `BPB`, `BBLOCK`.
- Directory format: `DIRSIZ` and `struct dirent`.

Filesystem relevance: this is the filesystem ABI. Both kernel `fs.c` and host-side `mkfs.c` must agree exactly on these structures and constants.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/kalloc.c -->
# File Research: sources/teaching/xv6-riscv/kernel/kalloc.c

Implements the kernel physical page allocator.

Important behavior:
- `kinit()` initializes a spinlock and frees physical pages from kernel `end` to `PHYSTOP`.
- `freerange()` rounds the start up to a page boundary and frees each page.
- `kfree()` validates page alignment/range, fills freed memory with junk, and pushes it onto the freelist.
- `kalloc()` pops one page from the freelist and fills allocated memory with junk.

Filesystem relevance: supports page allocations for page tables, process trapframes/stacks, pipe buffers, virtio rings, and lazy user pages. It underpins memory needed by filesystem-facing syscalls such as `pipe`, `exec`, and `sbrk`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/kalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/kernelvec.S -->
# File Research: sources/teaching/xv6-riscv/kernel/kernelvec.S

Supervisor-mode trap vector assembly for traps that occur while already in the kernel.

Important behavior:
- Allocates 256 bytes on the current kernel stack.
- Saves caller-saved registers used by C code.
- Calls `kerneltrap()` in `trap.c`.
- Restores registers and returns with `sret`.

Filesystem relevance: indirect but important for device interrupts. Virtio disk and UART interrupts enter through trap handling and can wake filesystem or console operations blocked in sleep.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/kernelvec.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/log.c -->
# File Research: sources/teaching/xv6-riscv/kernel/log.c

Implements xv6’s physical redo log for filesystem crash recovery.

Important behavior:
- `initlog()` initializes log metadata and replays any committed transaction.
- `recover_from_log()` reads the on-disk header, installs logged blocks, then clears the log.
- `begin_op()` reserves log space and sleeps if a commit is active or space may run out.
- `end_op()` decrements outstanding operations and commits when the last operation exits.
- `log_write()` records modified block numbers, absorbs duplicate writes, and pins buffers in cache.
- `commit()` writes dirty cache blocks to the log, commits by writing the header, installs home blocks, then clears the header.

Filesystem relevance: all mutating filesystem syscalls depend on this file. It provides transaction grouping, log absorption, buffer pinning, recovery, and bounds that shape `filewrite()` chunking.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/log.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/main.c -->
# File Research: sources/teaching/xv6-riscv/kernel/main.c

Kernel supervisor-mode main entry after `start()`.

Important behavior:
- CPU 0 initializes console, printing, physical memory, kernel page table, process table, traps, PLIC, buffer cache, inode table, file table, virtio disk, and the first process.
- Other CPUs wait for `started`, then initialize paging, trap vector, and PLIC hart state.
- All CPUs enter `scheduler()`.

Filesystem relevance: establishes initialization order. Buffer cache, inode table, file table, and virtio disk are ready before the first process runs; filesystem superblock/log initialization is deferred until `forkret()` in process context.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/memlayout.h -->
# File Research: sources/teaching/xv6-riscv/kernel/memlayout.h

Defines physical and virtual memory layout for QEMU’s RISC-V virt machine.

Contents:
- MMIO addresses and IRQ numbers for UART, virtio disk, and PLIC.
- Kernel physical base and `PHYSTOP`.
- `TRAMPOLINE`, `TRAPFRAME`, and `KSTACK(p)` virtual layout.
- User memory layout comments.

Filesystem relevance: provides device MMIO addresses for UART/virtio disk and constants used by VM/trap code. Virtio disk address and IRQ definitions are essential for block I/O.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/memlayout.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/param.h -->
# File Research: sources/teaching/xv6-riscv/kernel/param.h

Defines global kernel sizing constants.

Filesystem-relevant constants:
- `NOFILE`, `NFILE`: per-process and global open file limits.
- `NINODE`: active inode cache size.
- `NDEV`: major device table limit.
- `ROOTDEV`: root filesystem disk device.
- `MAXOPBLOCKS`, `LOGBLOCKS`, `NBUF`: transaction, log, and buffer cache sizing.
- `FSSIZE`: filesystem image size in blocks.
- `MAXPATH`: maximum path length.

Filesystem relevance: these constants set the capacity and transaction envelope of xv6’s teaching filesystem.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/param.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/pipe.c -->
# File Research: sources/teaching/xv6-riscv/kernel/pipe.c

Implements anonymous pipes as kernel-resident circular buffers exposed through `struct file`.

Important behavior:
- `pipealloc()` allocates two file objects and one page-backed `struct pipe`.
- `pipeclose()` marks read/write ends closed, wakes opposite waiters, and frees the pipe when both ends close.
- `pipewrite()` copies bytes from user memory, sleeps when full, and fails if no reader or process killed.
- `piperead()` sleeps while empty and writer open, copies bytes to user memory, and wakes writers.

Filesystem relevance: pipes share the file descriptor layer with inode and device files. `file.c` dispatches `FD_PIPE` reads/writes here.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/plic.c -->
# File Research: sources/teaching/xv6-riscv/kernel/plic.c

Implements minimal Platform-Level Interrupt Controller setup and interrupt claim/complete operations.

Important behavior:
- `plicinit()` enables nonzero priority for UART and virtio disk IRQs.
- `plicinithart()` enables those IRQs for each hart’s supervisor context and sets priority threshold to zero.
- `plic_claim()` reads the pending interrupt ID.
- `plic_complete()` reports completion.

Filesystem relevance: virtio disk completion interrupts flow through the PLIC and wake blocked disk I/O in `virtio_disk.c`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/plic.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/printk.c -->
# File Research: sources/teaching/xv6-riscv/kernel/printk.c

Implements kernel formatted printing and panic handling.

Important behavior:
- `printk()` supports a small set of format specifiers: integers, hex, pointers, chars, strings, and literal percent.
- A spinlock prevents interleaved output unless panic handling is active.
- `panic()` marks panic state, prints the panic message, marks the system panicked, and spins forever.
- `printkinit()` initializes the print lock.

Filesystem relevance: used throughout filesystem, log, block allocator, trap, and device code for diagnostics and fatal consistency checks.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/printk.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/proc.c -->
# File Research: sources/teaching/xv6-riscv/kernel/proc.c

Implements process table, scheduling, lifecycle, sleep/wakeup, fork/exit/wait, and helpers used by filesystem/user copy paths.

Important behavior:
- Maintains global `cpus[]`, `proc[]`, `initproc`, PID allocation, and `wait_lock`.
- `proc_mapstacks()` maps guarded kernel stacks into the kernel page table.
- `allocproc()` allocates trapframe/page table and prepares initial context.
- `userinit()` creates the first process and sets cwd to `/`.
- `kfork()`, `kexit()`, and `kwait()` manage process hierarchy and resource lifetime.
- `scheduler()`, `sched()`, `yield()`, and `forkret()` implement CPU scheduling.
- `forkret()` performs deferred filesystem initialization, then execs `/init`.
- `sleep()` and `wakeup()` provide the core blocking primitive used by pipes, log, console, locks, and virtio.
- `either_copyin()` and `either_copyout()` abstract user-vs-kernel copy for filesystem code.

Filesystem relevance: process cwd, open file duplication/closure, sleep/wakeup synchronization, and user copy helpers are all core to filesystem syscall behavior.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/proc.h -->
# File Research: sources/teaching/xv6-riscv/kernel/proc.h

Defines process, CPU, context switch, and trapframe structures.

Contents:
- `struct context` stores callee-saved registers for `swtch`.
- `struct cpu` tracks current process, scheduler context, interrupt nesting, and prior interrupt state.
- `struct trapframe` is the per-process register save area used by trampoline code.
- `enum procstate` defines lifecycle states.
- `struct proc` stores lock-protected scheduling/lifecycle state plus private process state such as kernel stack, memory size, page table, trapframe, open files, cwd, and name.

Filesystem relevance: `ofile[]` and `cwd` connect processes to the file and inode layers. `trapframe` holds syscall arguments and return values.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/proc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/riscv.h -->
# File Research: sources/teaching/xv6-riscv/kernel/riscv.h

Defines RISC-V CSR helpers, page-table types, status bits, interrupt helpers, and Sv39 paging macros.

Important contents:
- Inline CSR read/write helpers for machine and supervisor registers.
- Interrupt enable/disable helpers: `intr_on`, `intr_off`, `intr_get`.
- Hart/thread pointer helpers: `r_tp`, `w_tp`.
- `sfence_vma()` TLB flush.
- Types: `pte_t`, `pagetable_t`.
- Page constants and rounding macros.
- PTE bits, PA/PTE conversion, page-table index extraction, and `MAXVA`.

Filesystem relevance: supports VM and trap paths needed by syscalls, user copies, lazy page faults, and device interrupt handling. The page constants also define kernel allocation granularity.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/riscv.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sleeplock.c -->
# File Research: sources/teaching/xv6-riscv/kernel/sleeplock.c

Implements sleeping locks used for long-held resources such as inodes and buffers.

Important behavior:
- `initsleeplock()` initializes the internal spinlock and debug metadata.
- `acquiresleep()` sleeps while locked, then records ownership by PID.
- `releasesleep()` clears ownership and wakes waiters.
- `holdingsleep()` checks whether the current process holds the lock.

Filesystem relevance: inode locks and buffer locks are sleeplocks because filesystem operations may block while holding them. This is a key distinction from spinlocks.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sleeplock.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sleeplock.h -->
# File Research: sources/teaching/xv6-riscv/kernel/sleeplock.h

Defines `struct sleeplock`.

Fields:
- `locked` indicates ownership.
- Internal `struct spinlock lk` protects sleeplock state.
- `name` and `pid` provide debug ownership metadata.

Filesystem relevance: embedded in `struct inode` and `struct buf` to serialize long-duration filesystem/block access while allowing the holder to sleep.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sleeplock.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/spinlock.c -->
# File Research: sources/teaching/xv6-riscv/kernel/spinlock.c

Implements low-level spinlocks and interrupt nesting discipline.

Important behavior:
- `initlock()` initializes lock state and debug name.
- `acquire()` disables interrupts with `push_off()`, checks recursive acquisition, and atomically swaps `locked`.
- `release()` verifies ownership, clears owner, atomically stores unlocked, and calls `pop_off()`.
- `holding()` checks current CPU ownership.
- `push_off()`/`pop_off()` provide nested interrupt disabling/restoration.

Filesystem relevance: protects short critical sections across the buffer cache, file table, inode table, log, pipes, console, UART, allocator, and process table. Correct interrupt discipline prevents deadlock with interrupt handlers.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/spinlock.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/spinlock.h -->
# File Research: sources/teaching/xv6-riscv/kernel/spinlock.h

Defines `struct spinlock`.

Fields:
- `locked` stores lock state.
- `name` is debug metadata.
- `cpu` records the owning CPU for `holding()` and diagnostics.

Filesystem relevance: spinlocks appear in all core shared filesystem-adjacent tables and queues: buffer cache, inode table, log state, file table, pipe state, console, and virtio disk.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/start.c -->
# File Research: sources/teaching/xv6-riscv/kernel/start.c

Machine-mode startup code called from `entry.S`.

Important behavior:
- Allocates `stack0`, one boot stack per CPU.
- Sets machine previous privilege to supervisor and `mepc` to `main`.
- Disables paging initially.
- Delegates interrupts/exceptions to supervisor mode.
- Enables supervisor external and timer interrupts.
- Configures PMP to allow supervisor access to physical memory.
- Initializes timer interrupt support and stores hart ID in `tp`.
- Enters supervisor mode with `mret`.

Filesystem relevance: indirect. It establishes privilege, timer interrupts, and CPU identity needed before the kernel can initialize storage and filesystem subsystems.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/start.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/stat.h -->
# File Research: sources/teaching/xv6-riscv/kernel/stat.h

Defines file type constants and user-visible `struct stat`.

Contents:
- `T_DIR`, `T_FILE`, `T_DEVICE`.
- `struct stat` with device, inode number, type, link count, and size.

Filesystem relevance: inode metadata is converted into this structure by `stati()` and exposed to user programs through `fstat`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/string.c -->
# File Research: sources/teaching/xv6-riscv/kernel/string.c

Provides minimal C string and memory routines for the kernel.

Functions:
- `memset`, `memcmp`, `memmove`, `memcpy`.
- `strncmp`, `strncpy`, `safestrcpy`, `strlen`.

Filesystem relevance: used heavily by filesystem code for inode/block structure copies, directory names, superblock reads, bitmap zeroing, and path/name handling.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/string.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/swtch.S -->
# File Research: sources/teaching/xv6-riscv/kernel/swtch.S

Implements low-level context switching.

Important behavior:
- `swtch(old, new)` saves `ra`, `sp`, and all callee-saved registers into `old`.
- Loads the same registers from `new`.
- Returns into the newly restored context.

Filesystem relevance: indirect but foundational. Filesystem operations can sleep on locks, log space, pipes, console input, and disk I/O; sleeping depends on scheduler context switches through this routine.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/swtch.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/syscall.c -->
# File Research: sources/teaching/xv6-riscv/kernel/syscall.c

Implements syscall argument fetching and syscall dispatch.

Important behavior:
- `fetchaddr()` copies a 64-bit user value with bounds checks.
- `fetchstr()` copies a NUL-terminated user string.
- `argraw()`, `argint()`, `argaddr()`, and `argstr()` retrieve syscall arguments from trapframe registers.
- `syscalls[]` maps syscall numbers to handler functions.
- `syscall()` dispatches by `a7` and stores return value in `a0`.

Filesystem relevance: all filesystem syscalls enter through this dispatcher. Path strings, user buffers, file descriptors, and mode flags are fetched here or by helpers built on this API.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/syscall.h -->
# File Research: sources/teaching/xv6-riscv/kernel/syscall.h

Defines syscall numbers.

Filesystem-related syscall numbers include:
- `SYS_pipe`, `SYS_read`, `SYS_exec`, `SYS_fstat`, `SYS_chdir`, `SYS_dup`, `SYS_open`, `SYS_write`, `SYS_mknod`, `SYS_unlink`, `SYS_link`, `SYS_mkdir`, `SYS_close`.

Filesystem relevance: this is the ABI mapping between user stubs and kernel syscall dispatch.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/syscall.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sysfile.c -->
# File Research: sources/teaching/xv6-riscv/kernel/sysfile.c

Implements filesystem and file-descriptor syscalls.

Important behavior:
- `argfd()` validates a user file descriptor and returns `struct file`.
- `fdalloc()` installs a file reference into the current process table.
- Implements `dup`, `read`, `write`, `close`, and `fstat`.
- `sys_link()` increments inode link count, links into new parent directory, and rolls back on failure.
- `sys_unlink()` removes directory entries, handles directory emptiness, decrements links, and triggers inode cleanup through `iput()`.
- `create()` handles file/device/directory inode creation plus `.` and `..`.
- `sys_open()` handles create, directory write restrictions, device validation, file allocation, flags, and truncation.
- `sys_mkdir()`, `sys_mknod()`, `sys_chdir()`, `sys_exec()`, and `sys_pipe()` bridge user arguments to lower layers.

Filesystem relevance: this is the user-facing filesystem syscall layer. It enforces basic Unix semantics and transaction boundaries while delegating storage mechanics to `file.c` and `fs.c`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sysproc.c -->
# File Research: sources/teaching/xv6-riscv/kernel/sysproc.c

Implements process-related syscalls.

Important behavior:
- Wraps process lifecycle syscalls: `exit`, `fork`, `wait`, `kill`, `getpid`.
- `sys_sbrk()` supports eager and lazy allocation modes using `SBRK_EAGER`/`SBRK_LAZY`.
- `sys_pause()` sleeps for timer ticks and aborts if killed.
- `sys_uptime()` returns tick count under lock.

Filesystem relevance: process lifecycle closes files and drops cwd in `kexit()`. `fork()` duplicates file descriptors and cwd. Lazy allocation affects user buffers used by filesystem syscalls through `copyin`/`copyout`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/sysproc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/trampoline.S -->
# File Research: sources/teaching/xv6-riscv/kernel/trampoline.S

Assembly trampoline mapped at the same high virtual address in user and kernel page tables for trap entry and return.

Important behavior:
- `uservec` saves user registers into the per-process trapframe.
- Switches from user page table to kernel page table using trapframe `kernel_satp`.
- Restores kernel stack, hart ID, and jumps to `usertrap()`.
- `userret` switches to the user page table, restores user registers, restores `a0`, and executes `sret`.

Filesystem relevance: syscall entry and return use this path. Every filesystem syscall depends on this code preserving user register state and safely switching page tables.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/trampoline.S -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/trap.c -->
# File Research: sources/teaching/xv6-riscv/kernel/trap.c

Implements user/kernel trap handling, timer ticks, syscall dispatch entry, page fault handling, and device interrupt routing.

Important behavior:
- `trapinit()` initializes tick lock.
- `trapinithart()` installs `kernelvec`.
- `usertrap()` handles syscalls, device interrupts, lazy page faults, unexpected traps, kill checks, and timer yields.
- `prepare_return()` configures trampoline return state and user trap vector.
- `kerneltrap()` handles kernel-mode device interrupts and panics on unexpected traps.
- `clockintr()` increments ticks and schedules next timer interrupt.
- `devintr()` claims PLIC interrupts, dispatches UART or virtio disk interrupts, completes PLIC claims, and handles timer interrupts.

Filesystem relevance: virtio disk completion interrupts wake block I/O. Syscalls enter through `usertrap()`. Lazy page faults can allocate user buffers touched by read/write paths.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/types.h -->
# File Research: sources/teaching/xv6-riscv/kernel/types.h

Defines fixed-width and kernel convenience integer types:
- `uint`, `ushort`, `uchar`.
- `uint8`, `uint16`, `uint32`, `uint64`.
- `pde_t` as `uint64`.

Filesystem relevance: these types are used throughout on-disk structures, block numbers, inode metadata, virtual addresses, and device descriptors.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/types.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/uart.c -->
# File Research: sources/teaching/xv6-riscv/kernel/uart.c

Implements the low-level 16550a UART driver.

Important behavior:
- Defines MMIO register accessors for UART registers.
- `uartinit()` configures baud rate, word length, FIFOs, interrupts, and transmit lock.
- `uartwrite()` writes bytes using transmit-complete interrupts and sleeps while busy.
- `uartputc_sync()` writes a byte synchronously for panic/print/echo paths.
- `uartintr()` acknowledges interrupts, wakes transmit waiters, and feeds received characters to `consoleintr()`.

Filesystem relevance: console device reads/writes depend on UART. Console is reachable through normal filesystem device-file paths.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/uart.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/virtio.h -->
# File Research: sources/teaching/xv6-riscv/kernel/virtio.h

Defines virtio MMIO register offsets, status bits, feature bits, queue structures, descriptor flags, and block request format.

Important contents:
- Virtio MMIO offsets for device discovery, feature negotiation, queue setup, interrupts, and queue addresses.
- Status bits for acknowledge, driver, features-ok, and driver-ok.
- Block and ring feature bits intentionally negotiated away by the driver.
- `NUM` queue size.
- `struct virtq_desc`, `virtq_avail`, `virtq_used`, and `virtio_blk_req`.
- Block request types `VIRTIO_BLK_T_IN` and `VIRTIO_BLK_T_OUT`.

Filesystem relevance: defines the hardware-facing format used by `virtio_disk.c`, which provides block I/O for the buffer cache and filesystem.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/virtio.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/virtio_disk.c -->
# File Research: sources/teaching/xv6-riscv/kernel/virtio_disk.c

Implements the QEMU virtio block device driver used as xv6’s disk.

Important behavior:
- `virtio_disk_init()` validates the MMIO device, negotiates features, allocates descriptor/avail/used rings, configures queue 0, and marks the driver ready.
- Maintains descriptor free state, used index, per-request status, and associated `struct buf`.
- `alloc_desc()`, `free_desc()`, `free_chain()`, and `alloc3_desc()` manage descriptor lifecycle.
- `virtio_disk_rw()` builds a three-descriptor block request, publishes it to the avail ring, notifies the device, sleeps until completion, then frees descriptors.
- `virtio_disk_intr()` acknowledges interrupts, processes used-ring completions, verifies status, clears `b->disk`, and wakes sleepers.

Filesystem relevance: this is the physical block I/O endpoint below `bio.c`. All filesystem reads/writes eventually pass through this driver.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/virtio_disk.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/vm.c -->
# File Research: sources/teaching/xv6-riscv/kernel/vm.c

Implements kernel and user virtual memory management.

Important behavior:
- `kvmmake()` builds the kernel direct-map page table for UART, virtio, PLIC, kernel text/data/RAM, trampoline, and kernel stacks.
- `kvminit()` and `kvminithart()` install kernel paging.
- `walk()` traverses/allocates Sv39 page tables.
- `walkaddr()` resolves user virtual pages.
- `mappages()` maps page-aligned ranges.
- `uvmcreate()`, `uvmalloc()`, `uvmdealloc()`, `uvmunmap()`, `uvmfree()`, and `freewalk()` manage user page tables and memory.
- `uvmcopy()` implements fork memory copying.
- `uvmclear()` makes the exec stack guard inaccessible to user mode.
- `copyout()`, `copyin()`, and `copyinstr()` move data across user/kernel boundaries.
- `vmfault()` lazily allocates pages for `sbrk`.
- `ismapped()` checks PTE validity.

Filesystem relevance: user path strings, I/O buffers, `stat` outputs, exec loading, and lazy user memory all depend on these copy and mapping routines.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/vm.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/kernel/vm.h -->
# File Research: sources/teaching/xv6-riscv/kernel/vm.h

Defines `sbrk` allocation mode constants:
- `SBRK_EAGER`
- `SBRK_LAZY`

Filesystem relevance: lazy allocation affects whether user buffers passed to file syscalls are physically mapped before `copyin()`/`copyout()` touches them.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/kernel/vm.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/xv6-riscv/mkfs/mkfs.c -->
# File Research: sources/teaching/xv6-riscv/mkfs/mkfs.c

Host-side tool that creates an xv6 filesystem image.

Important behavior:
- Computes filesystem layout from `FSSIZE`, `LOGBLOCKS`, inode blocks, and bitmap blocks.
- Writes zeroed blocks, then writes the superblock.
- Allocates root inode, creates `.` and `..`, and appends requested input files into the root directory.
- Strips leading `user/` and leading `_` from installed program names.
- Uses `xshort()` and `xint()` to emit little-endian on-disk fields.
- `ialloc()` initializes on-disk inodes.
- `iappend()` allocates direct or indirect blocks and appends file data.
- `balloc()` writes the bitmap marking all used blocks.

Filesystem relevance: this tool must exactly match `kernel/fs.h` and the kernel’s inode/block interpretation. It builds the initial root filesystem consumed by `fsinit()`, path lookup, and `exec("/init")`.
<!-- END FILE RESEARCH: sources/teaching/xv6-riscv/mkfs/mkfs.c -->