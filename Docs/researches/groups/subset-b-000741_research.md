# subset-b-000741 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/siginfo.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/siginfo.h

### Purpose
This UAPI header specializes Linux `siginfo_t` layout and `si_code` values for the MIPS user ABI. It preserves IRIX-compatible values where MIPS historically diverged from generic Linux.

### Important APIs, Types, And Functions
It defines `__ARCH_SIGEV_PREAMBLE_SIZE`, advertises `__ARCH_HAS_SWAPPED_SIGINFO`, includes `asm-generic/siginfo.h`, and overrides `SI_ASYNCIO`, `SI_TIMER`, and `SI_MESGQ`.

### Control Flow
There is no runtime control flow. Preprocessor order is the important behavior: the generic header is included first, then selected generic `SI_*` values are undefined and replaced.

### State, Persistence, And Dependencies
The file persists ABI constants compiled into libc, userspace, and kernel signal code. It depends on generic signal-info definitions and on MIPS signal-frame code honoring the swapped layout marker.

### Integration Points
Signal delivery, queued signals, POSIX timers, AIO completion, message queues, and user-space headers all rely on these values matching the kernel ABI.

### Risks
Changing the numeric values or preamble size would break user-space binary compatibility. The swapped siginfo marker is subtle because it affects layout interpretation rather than a callable API.

### Test Signals
Useful checks are UAPI header compilation, signal queue/timer/AIO tests that inspect `si_code`, and ABI layout comparisons against libc on O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/siginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/signal.h

### Purpose
`signal.h` defines the MIPS userspace signal ABI: signal numbers, `sigset_t`, legacy signal masks, `sigaction`, alternate signal stack shape, and signal action flags.

### Important APIs, Types, And Functions
Key ABI items are `_NSIG == 128`, `_NSIG_WORDS`, `sigset_t`, `old_sigset_t`, numbered `SIG*` constants, `SIGRTMIN`, `SIGRTMAX`, `SA_*` flags, `MINSIGSTKSZ`, `SIGSTKSZ`, `SIG_BLOCK`, `SIG_UNBLOCK`, `SIG_SETMASK`, `struct sigaction`, and `stack_t`.

### Control Flow
There is no executable logic. Conditional compilation hides `struct sigaction` from kernel builds and includes `asm-generic/signal-defs.h` after MIPS-specific signal numbers and mask operations are defined.

### State, Persistence, And Dependencies
The header persists process-visible ABI numbers and structure layouts. It depends on `linux/types.h` for fixed kernel types and on generic signal helper declarations.

### Integration Points
The signal core, MIPS signal-frame assembly/C code, libc, ptrace tests, and applications using realtime signals or alternate stacks must all agree on this header.

### Risks
The signal numbering differs from some other architectures, and `SA_RESTORER` is intentionally reserved despite removed functionality. Any layout or numeric change is an ABI break.

### Test Signals
Signals tests should validate delivery numbers, mask size, realtime range, alternate stack operation, `sigaction` layout under userspace compilation, and kernel asm offset generation for signal constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/socket.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/socket.h

### Purpose
This header defines MIPS socket-level option numbers and timestamp compatibility aliases for userspace `setsockopt`, `getsockopt`, control messages, and socket timestamp ioctls.

### Important APIs, Types, And Functions
It exports `SOL_SOCKET`, legacy and Linux-specific `SO_*` option values, `SCM_*` aliases, timestamp old/new constants, time64-sensitive aliases for `SO_TIMESTAMP`, `SO_TIMESTAMPNS`, `SO_TIMESTAMPING`, `SO_RCVTIMEO`, and `SO_SNDTIMEO`, and includes `asm/sockios.h`.

### Control Flow
The only control flow is preprocessor selection. For non-kernel userspace, 64-bit long builds keep old timeout/timestamp values, while 32-bit userspace chooses old or new values based on `sizeof(time_t)` relative to `__kernel_long_t`.

### State, Persistence, And Dependencies
All state is ABI state in numeric constants. It depends on Linux POSIX types, MIPS sockios values, and libc exposing compatible `time_t` and kernel-long definitions.

### Integration Points
Networking syscalls, cmsg parsing, timestamping, BPF socket filters, zero-copy, busy polling, device-memory socket options, and libc headers consume these values.

### Risks
The MIPS `SOL_SOCKET` value and many option numbers are architecture ABI rather than generic C enum values. Time64 aliasing is easy to break if libc feature macros do not match kernel UAPI expectations.

### Test Signals
Run socket option ABI tests under O32/N32/N64, timestamp old/new tests with 32-bit and 64-bit `time_t`, and userspace header selftests that compare option numbers to kernel behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sockios.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sockios.h

### Purpose
`sockios.h` defines MIPS socket-related ioctl command numbers for ownership, process groups, out-of-band mark detection, and legacy timestamp retrieval.

### Important APIs, Types, And Functions
The public constants are `FIOGETOWN`, `FIOSETOWN`, `SIOCATMARK`, `SIOCSPGRP`, `SIOCGPGRP`, `SIOCGSTAMP_OLD`, and `SIOCGSTAMPNS_OLD`. The `_IOR` and `_IOW` encodings come from `asm/ioctl.h`.

### Control Flow
There is no runtime logic. The preprocessor expands ioctl encodings with MIPS ioctl layout rules and fixed command numbers.

### State, Persistence, And Dependencies
The persistent state is the ioctl ABI. Dependencies are `asm/ioctl.h` and kernel socket ioctl handlers that decode the same numbers.

### Integration Points
Used by `asm/socket.h`, libc socket headers, old applications using `ioctl()` on sockets, and kernel networking ioctl dispatch.

### Risks
Timestamp values are explicitly old ABI entries; new time64-aware paths live elsewhere. Mixing generic and MIPS ioctl encodings would break userspace compatibility.

### Test Signals
Socket ioctl tests should cover `FIOGETOWN/FIOSETOWN`, `SIOCGPGRP/SIOCSPGRP`, `SIOCATMARK`, and old timestamp ioctl compatibility on 32-bit and 64-bit userlands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sockios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/stat.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/stat.h

### Purpose
This header defines the MIPS `stat` and `stat64` userspace layouts for O32, N32, and N64. It preserves historic padding and nanosecond timestamp fields.

### Important APIs, Types, And Functions
For ABI32/NABI32 it defines `struct stat` and `struct stat64`; for ABI64 it defines `struct stat`. It uses `__kernel_ino_t`, `__kernel_mode_t`, `__kernel_uid32_t`, `__kernel_gid32_t`, and fixed padding around device and inode fields. `STAT_HAVE_NSEC` declares nanosecond timestamp availability.

### Control Flow
Preprocessor branches on `_MIPS_SIM` from `asm/sgidefs.h`. There is no runtime logic, but the chosen structure differs by ABI.

### State, Persistence, And Dependencies
The file is persistent syscall ABI state for `stat`, `fstat`, `lstat`, and related compat conversions. It depends on Linux UAPI integer types and MIPS ABI-selection macros.

### Integration Points
VFS stat syscall copying, libc `struct stat`, filesystem tests, strace decoders, and cross-ABI compat code all depend on these layouts.

### Risks
The padding is deliberate and non-obvious. Changing field sizes, signedness, or ABI conditionals would corrupt file metadata observed by existing binaries.

### Test Signals
ABI tests should compare `sizeof`, offsets, nanosecond fields, large inode/file-size behavior, and syscall output across O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/statfs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/statfs.h

### Purpose
`statfs.h` defines filesystem statistics structures for MIPS user ABIs, including 32-bit large-file variants and 64-bit compat layout.

### Important APIs, Types, And Functions
It exports `fsid_t` for non-strict names, `struct statfs`, ABI32/NABI32 `struct statfs64`, ABI64 `struct statfs64`, and ABI64 `struct compat_statfs64`. `f_fstyp` aliases `f_type`.

### Control Flow
Compile-time branches select structures based on `_MIPS_SIM`. There is no executable flow.

### State, Persistence, And Dependencies
The persistent ABI includes field order for block counts, free counts, file counts, `f_fsid`, name length, flags, and spare words. Dependencies are Linux POSIX types and MIPS ABI macros.

### Integration Points
VFS `statfs`/`fstatfs` syscalls, compat syscall translation, libc, filesystem utilities, and distributed filesystems reporting capacity use these layouts.

### Risks
The 64-bit kernel has both native and compat layouts. Misusing native `long` layouts for compat calls can truncate or misalign filesystem capacity values.

### Test Signals
Validate structure sizes/offsets, large block counts, compat syscall results, and libc/kernel agreement for `statfs64` under O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/swab.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/swab.h

### Purpose
This UAPI header supplies optimized MIPS byte-swap primitives for userspace and kernel headers when the compiler targets MIPS R2-or-newer instructions or Loongson 3A.

### Important APIs, Types, And Functions
It defines `__SWAB_64_THRU_32__`, inline `__arch_swab16`, `__arch_swab32`, and, on `__mips64`, `__arch_swab64`. Assembly uses `wsbh`, `rotr`, `dsbh`, and `dshd`.

### Control Flow
Preprocessor gates disable the optimized path for MIPS16 and for older architectures. Runtime control flow is absent; the compiler emits inline instructions.

### State, Persistence, And Dependencies
No mutable state exists. The header depends on compiler support for MIPS assembly dialect selection and Linux UAPI integer/compiler attributes.

### Integration Points
Endian conversion helpers, network and filesystem on-disk format code, userspace that includes kernel UAPI byteorder headers, and Loongson builds benefit from these definitions.

### Risks
The instruction gating must exactly match targets that can execute the selected instructions. Incorrect use under MIPS16 or pre-R2 would generate illegal instructions.

### Test Signals
Build tests for MIPS16, MIPS32r1, MIPS32r2, MIPS64r2, and Loongson targets plus runtime byte-swap correctness tests for 16/32/64-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sysmips.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sysmips.h

### Purpose
`sysmips.h` defines the command numbers for the deprecated MIPS-specific `sysmips(2)` syscall subset that Linux still supports for compatibility.

### Important APIs, Types, And Functions
The ABI constants are `SETNAME`, `FLUSH_CACHE`, `MIPS_FIXADE`, `MIPS_RDNVRAM`, and `MIPS_ATOMIC_SET`.

### Control Flow
There is no runtime logic. The kernel syscall implementation switches on these constants elsewhere.

### State, Persistence, And Dependencies
The persistent state is compatibility numbering for old MIPS software. The header has no dependencies beyond its include guard.

### Integration Points
Legacy userspace, libc syscall wrappers, cache-flush tools, unaligned-access policy control, and kernel `sys_sysmips` handling depend on these values.

### Risks
Because the syscall is deprecated, coverage may be thin, but changing command numbers would break old binaries. `MIPS_ATOMIC_SET` has concurrency semantics implemented outside this header.

### Test Signals
Compatibility tests should invoke supported `sysmips` commands, verify unsupported commands fail predictably, and check unaligned-access and cache-flush behavior on real or emulated MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/sysmips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termbits.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termbits.h

### Purpose
This header defines the MIPS termios bit layout: terminal state structures, control-character indexes, input/output/control/local flag bits, baud constants, and tcsetattr action aliases.

### Important APIs, Types, And Functions
It exports `tcflag_t`, `NCCS`, `struct termios`, `struct termios2`, `struct ktermios`, `VINTR` through `VEOL`, input flags such as `IXON` and `IUTF8`, output delay flags, `CBAUD`, `BOTHER`, high baud constants, `CIBAUD`, local flags, `TIOCSER_TEMT`, and `TCSANOW/TCSADRAIN/TCSAFLUSH`.

### Control Flow
There is no runtime logic. The file combines MIPS-specific bit positions with `asm-generic/termbits-common.h`.

### State, Persistence, And Dependencies
The persistent state is tty ioctl ABI state stored and copied through kernel tty structures. It depends on generic common termbits for shared types and ioctl-related constants.

### Integration Points
TTY drivers, pty handling, serial configuration, libc termios APIs, shell utilities, and line discipline code consume these structures and bits.

### Risks
`NCCS` and bit positions are MIPS ABI-specific. The disabled `VDSUSP` slot and high-speed baud encodings must not be casually reused.

### Test Signals
Run tty ioctl tests for structure sizes, baud programming including `BOTHER`, canonical/noncanonical control characters, local flags, and pty behavior under all MIPS ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termios.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termios.h

### Purpose
`termios.h` provides legacy terminal ioctl structures and modem-line constants for MIPS userspace, layering on top of `termbits.h` and `ioctls.h`.

### Important APIs, Types, And Functions
It defines `struct sgttyb`, `struct tchars`, `struct ltchars`, `struct winsize`, `NCC`, `struct termio`, and modem status bits such as `TIOCM_DTR`, `TIOCM_RTS`, `TIOCM_CTS`, `TIOCM_CAR`, `TIOCM_RNG`, `TIOCM_DSR`, `TIOCM_OUT1`, `TIOCM_OUT2`, and `TIOCM_LOOP`.

### Control Flow
No executable logic exists. Includes establish dependencies before structures are declared.

### State, Persistence, And Dependencies
The header preserves old tty ioctl ABI layouts. Dependencies are Linux errno definitions, MIPS termbits, and MIPS ioctl numbers.

### Integration Points
TTY core ioctl compatibility, serial drivers, libc, old BSD/SysV terminal utilities, and terminal-size reporting use this ABI.

### Risks
`struct sgttyb` has an SGI-specific `int sg_flags`, not a short. `struct termio` uses `NCCS` for `c_cc` despite defining `NCC`, so assumptions from other architectures are risky.

### Test Signals
TTY ioctl tests should verify winsize round-trips, modem-line ioctls, old `termio` layout, and legacy `sgttyb` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/types.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/types.h

### Purpose
This UAPI header selects integer type model definitions for MIPS userspace while leaving kernel builds to internal type headers.

### Important APIs, Types, And Functions
For non-kernel builds it includes `asm-generic/int-l64.h` when `_MIPS_SZLONG == 64` and `__SANE_USERSPACE_TYPES__` is not set; otherwise it includes `asm-generic/int-ll64.h`.

### Control Flow
Preprocessor conditionals choose between long-based and long-long-based 64-bit type models. There is no runtime behavior.

### State, Persistence, And Dependencies
The persistent state is userspace C type width and typedef compatibility. It depends on MIPS compiler ABI macros and generic integer type headers.

### Integration Points
UAPI consumers, libc, perf, tracing tools, and any program including kernel headers receive their fixed-width integer typedefs through this selection.

### Risks
The `__SANE_USERSPACE_TYPES__` escape hatch is important for tools expecting `ll64` behavior even on 64-bit long MIPS. Wrong selection can break printf formats, structure layout, or cross-compiled user tools.

### Test Signals
Header selftests should compile with and without `__SANE_USERSPACE_TYPES__` under 32-bit and 64-bit MIPS ABIs and verify typedef sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ucontext.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ucontext.h

### Purpose
`ucontext.h` defines the MIPS userspace signal context container and an extensible trailer for processor state that does not fit inside `sigcontext`, notably MSA vector state.

### Important APIs, Types, And Functions
It exports `struct extcontext`, `struct msa_extcontext`, `MSA_EXTCONTEXT_MAGIC`, `END_EXTCONTEXT_MAGIC`, and `struct ucontext` with `uc_flags`, `uc_link`, `uc_stack`, `uc_mcontext`, `uc_sigmask`, and flexible `uc_extcontext[]`.

### Control Flow
There is no executable logic. Userland walks the extension area by reading each `extcontext.magic` and `extcontext.size` until the end magic is seen.

### State, Persistence, And Dependencies
The state is the signal-frame ABI persisted on user stacks during signal delivery. It depends on `stack_t`, `struct sigcontext`, and `sigset_t` declarations from surrounding UAPI headers.

### Integration Points
Signal delivery/return, context-switching libraries, debuggers, crash dump tools, and MSA-aware runtimes parse this layout.

### Risks
Extension parsing depends on size correctness, alignment, and the end marker. Unknown extensions must be skippable, so future additions must preserve this contract.

### Test Signals
Signal tests should inspect `ucontext_t`, MSA live-state delivery, unknown-extension skipping, end-marker placement, and ABI layout under O32, N32, and N64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/unistd.h

### Purpose
This header chooses the syscall-number table for the active MIPS userspace ABI and establishes the ABI-specific Linux syscall base.

### Important APIs, Types, And Functions
It includes `asm/sgidefs.h`, tests `_MIPS_SIM`, sets `__NR_Linux` to `4000` for O32, `5000` for N64, or `6000` for N32, and includes `asm/unistd_o32.h`, `asm/unistd_n64.h`, or `asm/unistd_n32.h`.

### Control Flow
The preprocessor selects exactly one syscall table according to the compiler ABI. There is no runtime logic.

### State, Persistence, And Dependencies
The persistent state is syscall numbering. Dependencies are generated syscall headers and MIPS ABI-selection macros.

### Integration Points
Libc syscall wrappers, seccomp filters, strace, audit, ptrace, and the MIPS syscall entry assembly must agree with these numbers.

### Risks
Using the wrong `_MIPS_SIM` during header generation or cross-compilation silently targets the wrong syscall table. The base numbers are part of the ABI and cannot change.

### Test Signals
Syscall ABI tests should compare generated numbers against kernel syscall tables, run simple syscalls under O32/N32/N64, and validate seccomp/audit decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ingenic/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/ingenic/Kconfig

### Purpose
This Kconfig file defines selectable Ingenic/XBurst MIPS boards and internal SoC-family capability symbols.

### Important APIs, Types, And Functions
User-facing choices include `INGENIC_GENERIC_BOARD`, `JZ4740_QI_LB60`, `JZ4740_RS90`, `JZ4770_GCW0`, `JZ4780_CI20`, `X1000_CU1000_NEO`, and `X1830_CU1830_NEO`. Internal symbols include `MACH_INGENIC_GENERIC`, `MACH_JZ4725B`, `MACH_JZ4740`, `MACH_JZ4770`, `MACH_JZ4780`, `MACH_X1000`, and `MACH_X1830`.

### Control Flow
Kconfig dependency flow starts when `MACH_INGENIC_SOC` is enabled, presents one board choice, and selects the relevant SoC symbols. The generic board selects every supported Ingenic SoC family.

### State, Persistence, And Dependencies
The persistent state is the generated `.config`. Selected SoC symbols pull in CPU generation, secondary cache, and highmem capabilities used by Makefiles and platform code.

### Integration Points
This integrates with MIPS platform selection, device-tree board support, CPU probe quirks for Ingenic XBurst, cache setup, and build inclusion of SoC/platform drivers.

### Risks
Incorrect `select` chains can build kernels with unsupported CPU ISA assumptions or missing highmem/cache support. The generic option intentionally widens hardware support and may increase image surface.

### Test Signals
Kconfig tests should build each board option, inspect selected CPU/highmem/cache symbols, and boot representative DTBs under hardware or emulation where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ingenic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/Kconfig

### Purpose
This Kconfig file exposes Jazz-family machine selections: Acer PICA-61, MIPS Magnum 4000, and Olivetti M700.

### Important APIs, Types, And Functions
The symbols are `ACER_PICA_61`, `MIPS_MAGNUM_4000`, and `OLIVETTI_M700`. All depend on `MACH_JAZZ` and select `DMA_NONCOHERENT`; `MIPS_MAGNUM_4000` also selects `SYS_SUPPORTS_BIG_ENDIAN`.

### Control Flow
Kconfig presents each machine option only when Jazz platform support is active. Selection sets architecture capabilities consumed during build and boot.

### State, Persistence, And Dependencies
The output state is `.config`. It controls noncoherent DMA behavior, endianness support, and conditional code such as Olivetti UART clock selection.

### Integration Points
The Jazz platform files in this subset, the DMA mapping implementation, serial setup, interrupt routing, and firmware reset path all depend on these selections.

### Risks
Machine options describe old hardware with limited test coverage. Wrong endianness or DMA coherency selection can produce boot failures or data corruption.

### Test Signals
Build all three machine configurations, verify selected symbols, and boot-test timer, serial, SCSI, network, and reset paths on real hardware or QEMU support if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/Makefile

### Purpose
The Jazz Makefile declares the platform objects that are always linked for the Jazz machine family.

### Important APIs, Types, And Functions
`obj-y := irq.o jazzdma.o reset.o setup.o` pulls in interrupt/timer setup, virtual DMA mapping, keyboard-controller reset, and platform device registration.

### Control Flow
Kbuild includes this Makefile when the Jazz platform directory is selected by the architecture build. There is no runtime control flow in the file.

### State, Persistence, And Dependencies
The build graph state determines which platform initialization symbols are present in the final kernel. It depends on Kbuild and the Jazz Kconfig path.

### Integration Points
The listed objects provide `arch_init_irq`, `plat_time_init`, `plat_mem_setup`, `jazz_dma_ops`, and restart support used by generic MIPS boot and driver code.

### Risks
Because every object is unconditional for Jazz, unresolved symbols or incompatible config assumptions in any file break all Jazz builds.

### Test Signals
Run a Jazz defconfig build and inspect that all four objects link, platform initcalls run, and no optional driver dependency is accidentally required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/irq.c

### Purpose
`irq.c` implements Jazz interrupt initialization, R4030 local interrupt masking, platform IRQ dispatch, and the R4030 periodic clock event.

### Important APIs, Types, And Functions
Important functions and objects are `enable_r4030_irq()`, `disable_r4030_irq()`, `r4030_irq_type`, `init_r4030_ints()`, `arch_init_irq()`, `plat_irq_dispatch()`, `r4030_clockevent`, `r4030_timer_interrupt()`, and `plat_time_init()`.

### Control Flow
Boot maps fixed wired TLB entries for Jazz I/O, initializes i8259 CPU IRQs and R4030 IRQ chips, clears pending R4030 sources, and enables CPU interrupt lines. Runtime dispatch prioritizes timer IRQ4, EISA IRQ2, then R4030 local IRQ1. Timer initialization registers a periodic-only clock event and programs the R4030 interval for 100 Hz.

### State, Persistence, And Dependencies
Mutable state is R4030 enable/source registers, CPU status interrupt masks, wired TLB mappings, and the registered clockevent. The spinlock protects R4030 mask changes.

### Integration Points
It integrates MIPS generic IRQ entry, i8259, R4030 hardware registers, `setup_pit_timer()`, Jazz constants, and the generic clockevents layer.

### Risks
The file assumes `HZ == 100`, hard-coded wired mappings, and fixed interrupt priority. An empty local IRQ source panics, so spurious R4030 local interrupts are fatal.

### Test Signals
Boot Jazz, verify wired mappings, timer ticks, EISA interrupt ack, R4030 device IRQ enable/disable, and PIT registration. Stress interrupt masking under concurrent device IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/jazzdma.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/jazzdma.c

### Purpose
`jazzdma.c` implements the Jazz R4030 virtual DMA translation table, low-level channel programming helpers, and Linux `dma_map_ops` for noncoherent Jazz devices.

### Important APIs, Types, And Functions
Key state and APIs are `pgtbl`, `vdma_lock`, `vdma_init()`, `vdma_alloc()`, `vdma_free()`, `vdma_phys2log()`, `vdma_log2phys()`, `vdma_stats()`, `vdma_enable()`, `vdma_disable()`, `vdma_set_mode()`, `vdma_set_addr()`, `vdma_set_count()`, `vdma_get_residue()`, `vdma_get_enable()`, `jazz_dma_alloc/free/map_phys/unmap_phys/map_sg/unmap_sg/sync_*()`, and exported `jazz_dma_ops`.

### Control Flow
`vdma_init()` allocates uncached page-table memory, initializes entries, and points R4030 registers at it. `vdma_alloc()` validates physical range/size, first-fits empty VDMA pages under a spinlock, writes frames/owner tags, invalidates the translation table, and returns a logical DMA address. DMA map operations wrap cache synchronization around VDMA allocation/free. Channel helpers program R4030 mode, address, count, enable, and error bits.

### State, Persistence, And Dependencies
Persistent runtime state lives in the VDMA page table, R4030 translation/control registers, channel registers, and exported DMA mapping ops. Dependencies include noncoherent cache helpers, Jazz register accessors, scatterlist APIs, and DMA common helpers.

### Integration Points
Jazz SCSI and network platform devices use these mapping operations to translate CPU physical memory into R4030 logical DMA space. Generic DMA API callers reach this file through `jazz_dma_ops`.

### Risks
`vdma_free()` is not locked while mutating owner fields, unlike allocation. Scatter-gather mapping leaks earlier mappings if a later entry fails. `jazz_dma_free()` converts an uncached return address with `virt_to_page()`, which relies on MIPS address translation behavior. MMIO mapping is rejected due limited test confidence.

### Test Signals
Exercise coherent allocation/free, map/unmap single and scatter-gather with partial-failure injection, SCSI/network DMA I/O, cache coherency under read/write directions, channel enable/disable errors, and VDMA table exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/jazzdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/reset.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/reset.c

### Purpose
`reset.c` provides the Jazz machine restart routine by driving the keyboard controller reset command path directly.

### Important APIs, Types, And Functions
Key helpers are `jazz_write_output()`, `jazz_write_command()`, `jazz_read_status()`, `kb_wait()`, and exported platform hook target `jazz_machine_restart()`.

### Control Flow
Writes spin until the keyboard input buffer is clear, then write either data or command register. `kb_wait()` waits up to half a second using `jiffies`. `jazz_machine_restart()` loops forever sending command `0xd1` and output `0x00` to force reset.

### State, Persistence, And Dependencies
State is the hardware keyboard-controller status/data registers and `jiffies` for timeout. It depends on `jazz_kh` from Jazz platform headers.

### Integration Points
`plat_mem_setup()` assigns `_machine_restart = jazz_machine_restart`, so generic reboot paths call this function for Jazz machines.

### Risks
The restart path intentionally never returns. It assumes the keyboard-controller reset mechanism is present and functional, and it has no fallback if firmware or hardware ignores the command.

### Test Signals
Manual reboot tests on each Jazz machine type, watchdog observation for non-returning behavior, and fault injection for stuck input-buffer status are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/setup.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/setup.c

### Purpose
`setup.c` initializes Jazz memory/I/O mappings, reserves legacy I/O resources, sets console and restart hooks, and registers platform devices for serial, SCSI, Ethernet, RTC, and speaker hardware.

### Important APIs, Types, And Functions
Important objects are `jazz_io_resources`, `plat_mem_setup()`, `jazz_serial_data`, `jazz_serial8250_device`, `jazz_esp_pdev`, `jazz_sonic_pdev`, `jazz_cmos_pdev`, `pcspeaker_pdev`, and `jazz_setup_devinit()`.

### Control Flow
Early platform setup installs wired TLB entries, sets the I/O port base, marks EISA presence when configured, reserves PC-compatible I/O ranges, assigns restart behavior, and selects `ttyS0` at 9600. Device initcall later registers serial8250, ESP SCSI, Sonic Ethernet, RTC CMOS, and PC speaker devices with fixed resources.

### State, Persistence, And Dependencies
Runtime state is wired TLB mappings, I/O resource reservations, platform device records, DMA masks, console preference, and restart hook. Dependencies include Jazz hardware constants, platform bus, serial8250, DMA mask helpers, and EISA state.

### Integration Points
Registered devices bind to generic drivers and to Jazz DMA operations. The fixed resources connect the platform to interrupt and DMA setup in `irq.c` and `jazzdma.c`.

### Risks
Hard-coded physical addresses, IRQs, and UART clock variants make board identification important. Repeated wired mappings overlap with `arch_init_irq()`, so mapping assumptions must remain aligned.

### Test Signals
Boot tests should confirm console output, serial ports, ESP SCSI probing, Sonic Ethernet DMA, RTC IRQ, PC speaker registration, I/O resource conflicts, and restart hook installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/Makefile

### Purpose
This Makefile defines the core Linux/MIPS kernel object graph, selecting CPU probing, exception entry, syscall, timer, SMP, FPU, tracing, kexec, VDSO, and platform clocksource/clockevent objects according to configuration.

### Important APIs, Types, And Functions
The base `obj-y` includes fundamental files such as `head.o`, `branch.o`, `cmpxchg.o`, `elf.o`, `entry.o`, `irq.o`, `process.o`, `signal.o`, `syscall.o`, `time.o`, `traps.o`, `vdso.o`, and `cacheinfo.o`. Conditional lines select CPU probe variants, clock event/source drivers, SMP/CPS/BMIPS support, syscall ABI objects, kexec/crash, early printk, perf, PM, and VPE loader objects.

### Control Flow
Kbuild evaluates config symbols to assemble the object list. It also removes ftrace flags from selected low-level objects and probes assembler support for `-mdaddi` for `r4k-bugs64.o`.

### State, Persistence, And Dependencies
The persistent state is the kernel link composition. It depends on architecture Kconfig symbols, generated syscall tables, and compiler/assembler feature detection.

### Integration Points
This is the central integration point for all kernel files in this subset and for generic Linux subsystems that need MIPS implementations.

### Risks
Wrong conditional selection can link incompatible syscall ABIs, duplicate CPU probe paths, or instrument fragile low-level code with ftrace. Conditional clock/timer objects must match platform Kconfig.

### Test Signals
Build matrix coverage for 32/64-bit, CPU_R3K_TLB, MIPS32 compat, CPS, BMIPS, early printk, kexec, perf, and tracing configs catches most integration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/access-helper.h -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/access-helper.h

### Purpose
`access-helper.h` centralizes safe reads of addresses and instructions from either user memory or kernel memory for instruction decoding paths.

### Important APIs, Types, And Functions
It provides inline helpers `__get_addr()`, `__get_inst16()`, and `__get_inst32()`. Each accepts an output pointer, source pointer, and `user` boolean.

### Control Flow
Each helper branches on `user`: user accesses call `get_user()`, while kernel accesses call `get_kernel_nofault()`. Errors propagate as the underlying helper return value.

### State, Persistence, And Dependencies
There is no retained state. It depends on `linux/uaccess.h` and on callers treating failed reads as fault conditions.

### Integration Points
Branch emulation, uprobes/kprobes, unaligned access handling, or other instruction-reading code can use this header to avoid open-coding user-versus-kernel access.

### Risks
Callers must pass correctly typed pointers and must not ignore faults. Instruction endianness and ISA mode interpretation are outside this helper, so it only solves safe access.

### Test Signals
Unit-style tests for user valid/invalid addresses, kernel nofault reads, 16-bit and 32-bit instruction fetches, and fault propagation in branch/probe paths are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/access-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/asm-offsets.c

### Purpose
`asm-offsets.c` generates assembly-visible constants for MIPS kernel structures, signal numbers, page-table geometry, KVM FPU state, power-management state, and CPS boot configuration.

### Important APIs, Types, And Functions
The file defines `output_ptreg_defines()`, `output_task_defines()`, `output_thread_info_defines()`, `output_thread_defines()`, `output_thread_fpu_defines()`, `output_mm_defines()`, ABI-specific `output_sc_defines()`, `output_signal_defined()`, `output_octeon_cop2_state_defines()`, `output_pbe_defines()`, `output_pm_defines()`, `output_kvm_defines()`, and `output_cps_defines()`.

### Control Flow
During the build, kbuild compiles this file with `COMPILE_OFFSETS`; `OFFSET()` and `DEFINE()` emit constants derived from C structure layout. Conditional compilation emits only constants relevant to the enabled architecture features.

### State, Persistence, And Dependencies
The generated `asm-offsets.h` is build-time persistent state consumed by assembly. Dependencies include scheduler, mm, ptrace, processor, PM, SMP-CPS, KVM, signal, and page-table headers.

### Integration Points
Exception entry/exit assembly, context switching, signal trampolines, KVM assembly, Octeon COP2 save/restore, hibernation, CPU PM, and CPS boot vectors depend on these offsets.

### Risks
Any C structure layout change that is not reflected through generated offsets can break assembly silently if hard-coded constants exist elsewhere. Conditional offsets must match assembly conditional paths.

### Test Signals
Full MIPS build coverage across configs is the primary test. Runtime signals include successful boot, syscall/interrupt return, signal delivery/return, KVM context operations, CPU suspend/resume, and CPS SMP startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_5xxx_init.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_5xxx_init.S

### Purpose
This BMIPS5000 assembly file initializes secondary Broadcom BMIPS 5xxx cores by sizing and clearing caches, enabling cache modes, programming Broadcom CP0 configuration, and clearing branch predictor state.

### Important APIs, Types, And Functions
Important symbols are `size_i_cache`, `size_d_cache`, `enable_ID`, `l1_init`, `set_other_config`, `set_branch_pred`, `set_luc`, `set_cwf_tse`, `set_clock_ratio`, `set_zephyr`, `set_llmb`, `core_init`, `clear_jump_target_buffer`, and public `bmips_5xxx_init`.

### Control Flow
The entry saves `ra` and `a0`, calls L1 cache initialization, core configuration, and branch target buffer reset, clears CP0 Cause, restores `a0`, and returns. Cache initialization sizes I/D caches from Config1, runs uncached while setting K0 cache mode, invalidates tags, then resumes cached execution. Core init programs Zephyr, low-latency memory bus, branch prediction, link-uncached, CWF/TSE, clock ratio, and cache error behavior.

### State, Persistence, And Dependencies
State is CP0 Config, Broadcom Config0/Mode, cache tag/data registers, ZSC L2 registers, Cause, and predictor structures. Dependencies include BMIPS CP0 encodings, cacheop macros, and `CONFIG_CPU_BMIPS5000`.

### Integration Points
`bmips_vec.S` invokes this path during BMIPS5200 warm boot/secondary startup. SMP BMIPS code and platform reset vectors rely on these settings before entering C.

### Risks
This code executes before normal kernel services and uses raw CP0/ZSC accesses. Wrong cache sizing or mode transitions can hang secondary cores or corrupt memory. Some `.word` CP0 operations are opaque and hardware-specific.

### Test Signals
BMIPS5000/BMIPS5200 SMP boot, secondary CPU online/offline cycles, suspend/resume warm restart, cache coherency stress, and branch predictor reset validation are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_5xxx_init.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_vec.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_vec.S

### Purpose
`bmips_vec.S` implements Broadcom BMIPS reset, NMI, re-entry, warm restart, secondary CPU startup, and XKS01 segment-extension vectors.

### Important APIs, Types, And Functions
Important symbols are `bmips_smp_movevec`, `bmips_reset_nmi_vec`, `bmips_smp_entry`, `bmips_secondary_reentry`, `bmips_reset_nmi_vec_end`, `bmips_smp_int_vec`, `bmips_smp_int_vec_end`, and `bmips_enable_xks01`.

### Control Flow
The move vector relocates CPU1 from the IV vector to the warm restart vector on BMIPS4350-style systems. The reset/NMI vector distinguishes NMI from soft reset, saves state for real NMI, clears status bits, and jumps to `nmi_handler`. SMP reset paths configure CP0 status/config, initialize local I-cache or EBase as needed, enable XKS01, build wired TLB state, load boot stack/global pointer, and jump to `start_secondary`.

### State, Persistence, And Dependencies
State includes CP0 Status, Cause, Config, EBase, Broadcom CP0 register 22 selectors, warm restart vectors copied to fixed addresses, boot stack/global pointer globals, and wired TLB setup.

### Integration Points
BMIPS SMP platform code copies and targets these vectors. It calls `bmips_5xxx_init`, `plat_wired_tlb_setup`, `nmi_handler`, and `start_secondary`.

### Risks
The vector is copied to fixed exception addresses and runs with minimal stack/translation guarantees. PRID-based paths must distinguish BMIPS4350/4380/5000/5200 accurately. Any wrong cacheability or EBase programming can strand secondary CPUs.

### Test Signals
Test CPU1 first boot, hotplug re-entry, NMI handling, BMIPS5200 warm boot, XKS01-enabled high-memory access, and vector copy size/end labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_vec.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/branch.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/branch.c

### Purpose
`branch.c` decodes MIPS, microMIPS, MIPS16e, DSP, FPU, Octeon, and MIPS R6 branch instructions to compute the correct exception return EPC after faults in delay or forbidden slots.

### Important APIs, Types, And Functions
Core functions are `__isa_exception_epc()`, `__mm_isBranchInstr()`, `__microMIPS_compute_return_epc()`, `__MIPS16e_compute_return_epc()`, `__compute_return_epc_for_insn()`, exported `__compute_return_epc()`, and exported `__insn_is_compact_branch()` for kprobes/uprobes.

### Control Flow
The code fetches the instruction at EPC, handles ISA16 mode separately, decodes opcode/function fields, evaluates register/FPU/DSP conditions, sets link registers for call branches, updates `regs->cp0_epc`, and returns whether a branch-likely delay slot was taken. Illegal ISA combinations force `SIGILL`; failed instruction fetches force `SIGSEGV`; unaligned EPC forces `SIGBUS`.

### State, Persistence, And Dependencies
State is the live `pt_regs`, current task FPU state, CP1 status, DSP control register, and CPU feature flags. Dependencies include instruction format definitions, FPU ownership helpers, R2-to-R6 emulation flags, user access, and signal delivery.

### Integration Points
Exception handling, unaligned access emulation, FPU emulation, kprobes/uprobes, and signal generation use this logic to resume correctly after branch delay slot faults.

### Risks
Branch decoding is architecture-sensitive and easy to regress for compact branches, link register updates, ISA mode bits, and branch-likely return values. The R6 compact branch section for `bgtz` tests `blez_op` in one link-register condition, which deserves scrutiny against the ISA comments.

### Test Signals
Instruction-level tests should fault every branch form in delay/forbidden slots across MIPS32/64, microMIPS, MIPS16e, R6 compact branches, DSP `bposge32`, FPU condition branches, and Octeon bit branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/branch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cacheinfo.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cacheinfo.c

### Purpose
`cacheinfo.c` exposes MIPS cache topology to Linux generic cacheinfo sysfs by translating `cpuinfo_mips` cache descriptors into cache leaves and sharing masks.

### Important APIs, Types, And Functions
It defines `populate_cache()` macro, `init_cache_level()`, `fill_cpumask_siblings()`, `fill_cpumask_cluster()`, and `populate_cache_leaves()`.

### Control Flow
Initialization rejects CPUs with uninitialized D-cache data. It counts leaves for split I/D or unified L1, optional victim, secondary, and tertiary caches. Population fills each leaf's type, level, line size, sets, ways, size, and shared CPU mask, using sibling masks for per-core caches and cluster masks for scache.

### State, Persistence, And Dependencies
State is stored in per-CPU `struct cpu_cacheinfo` and `struct cacheinfo` arrays. It depends on `current_cpu_data`, `cpu_data[]`, sibling/cluster helpers, and generic cacheinfo APIs.

### Integration Points
Sysfs cache topology, scheduler/topology consumers, tooling that reads cache sizes, and CPU probe/cache-probe code that fills `cpuinfo_mips` all connect here.

### Risks
The function uses `current_cpu_data` rather than `cpu_data[cpu]`, so callers must run in the expected CPU context. Missing or wrong cache probe data produces absent or incorrect sysfs topology.

### Test Signals
Boot tests should compare `/sys/devices/system/cpu/*/cache` against known hardware for split/unified L1, victim cache, cluster-shared scache, and tertiary cache systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-bcm1480.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-bcm1480.c

### Purpose
This file implements per-CPU clockevent devices for Broadcom/SiByte BCM1480 general-purpose timers.

### Important APIs, Types, And Functions
Key functions are `sibyte_set_periodic()`, `sibyte_shutdown()`, `sibyte_next_event()`, `sibyte_counter_handler()`, and `sb1480_clockevent_init()`. State is per-CPU `sibyte_hpt_clockevent` and per-CPU names.

### Control Flow
Initialization assigns timer IRQ `K_BCM1480_INT_TIMER_0 + cpu`, configures clockevent capabilities, registers it, masks/maps/unmasks the interrupt to IP4, sets affinity to the CPU, and requests the timer IRQ. Runtime oneshot/periodic programming writes timer config/init registers; the IRQ handler acknowledges and calls the event handler.

### State, Persistence, And Dependencies
State lives in SCD timer registers, BCM1480 interrupt mapper, per-CPU clockevent structs, and irq affinity. Dependencies are SiByte register definitions, raw MMIO accessors, clockevents, and IRQ APIs.

### Integration Points
Platform time initialization calls this for BCM1480 systems. Generic clockevents/tick code consumes the registered per-CPU device.

### Risks
The code assumes at most four CPUs/timers. Raw 64-bit register accesses and interrupt map offsets must match hardware. Request IRQ failures only log errors after registration.

### Test Signals
Boot on BCM1480, periodic and oneshot tick tests, per-CPU IRQ affinity checks, CPU hotplug if supported, and interrupt-map register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-bcm1480.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-ds1287.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-ds1287.c

### Purpose
`cevt-ds1287.c` implements a periodic-only clockevent using the DS1287/MC146818 RTC periodic interrupt.

### Important APIs, Types, And Functions
Public functions are `ds1287_timer_state()`, `ds1287_set_base_clock()`, and `ds1287_clockevent_init()`. Internal pieces include `ds1287_shutdown()`, `ds1287_set_periodic()`, `ds1287_interrupt()`, and `ds1287_clockevent`.

### Control Flow
Base clock setup maps selected Hz values to RTC rate codes. Periodic state sets or clears `RTC_PIE` under `rtc_lock`. The interrupt handler acknowledges by reading `RTC_REG_C` and invokes the clockevent handler. Oneshot programming is unsupported and returns `-EINVAL`.

### State, Persistence, And Dependencies
State lives in CMOS RTC registers A/B/C, global `rtc_lock`, and the clockevent struct. Dependencies include MC146818 RTC macros, clockevents, IRQ APIs, and MIPS time setup.

### Integration Points
Used by platforms with DS1287 RTC timer support, and by DEC I/O ASIC clocksource calibration through `ds1287_timer_state()`.

### Risks
Only three base frequencies are accepted. Periodic-only operation limits dynamic tick behavior. RTC register locking must be respected by other RTC users.

### Test Signals
Verify 128/256/1024 Hz setup, periodic interrupt delivery, RTC PIE enable/disable, IRQ request errors, and coexistence with RTC drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-ds1287.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-gt641xx.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-gt641xx.c

### Purpose
This file implements clockevent support for GT641xx timer 0.

### Important APIs, Types, And Functions
Public functions are `gt641xx_set_base_clock()` and `gt641xx_timer0_state()`. Internal functions include `gt641xx_timer0_set_next_event()`, shutdown/oneshot/periodic state setters, `gt641xx_timer0_interrupt()`, and initcall `gt641xx_timer0_clockevent_init()`.

### Control Flow
The base clock must be set before initcall. Init programs timer 0, computes rating and delta bounds, registers the clockevent, and requests `GT641XX_TIMER0_IRQ`. Runtime state setters update timer control under a raw spinlock, choosing periodic select or one-shot behavior.

### State, Persistence, And Dependencies
State includes `gt641xx_base_clock`, GT timer count/control registers, `gt641xx_timer_lock`, and the clockevent device. Dependencies are GT64120 register access macros and clockevents.

### Integration Points
GT641xx-based MIPS boards call the base-clock setter during platform setup; generic tick code uses the registered event device.

### Risks
If the base clock is never set, init silently does nothing. Timer control register updates are shared with hardware, so locking and bit masks are essential.

### Test Signals
Board boot should verify base-clock setup, periodic ticks, oneshot next-event programming, timer0 state detection, and IRQ delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-gt641xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-r4k.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-r4k.c

### Purpose
`cevt-r4k.c` implements the standard MIPS CP0 Count/Compare clockevent device and compare interrupt handling.

### Important APIs, Types, And Functions
Important functions include `mips_next_event()`, `calculate_min_delta()`, `handle_perf_irq()`, `c0_compare_interrupt()`, `mips_event_handler()`, `c0_compare_int_usable()`, `r4k_clockevent_init()`, `r4k_register_clockevent()`, and CPU notifier hooks when enabled. It defines per-CPU `mips_clockevent_device` and `cp0_timer_irq_installed`.

### Control Flow
Next-event programming writes Compare to Count plus delta and detects already-expired events. Initialization verifies usable compare interrupt behavior, computes a virtualization-tolerant minimum delta, configures per-CPU clockevent attributes, and registers the device. The interrupt handler arbitrates shared perf-counter interrupts before acknowledging timer interrupts and calling the event handler.

### State, Persistence, And Dependencies
State is CP0 Count/Compare/Cause, per-CPU clockevents, global IRQ installation flag, CPU frequency notifier state, and perf IRQ sharing state. Dependencies include clockchips, perf IRQ hooks, CPU feature flags, and MIPS time globals.

### Integration Points
This is the common timer for many MIPS CPUs. It feeds Linux tick/nohz, works with perf counter overflow sharing, and is paired with `csrc-r4k.c` for clocksource.

### Risks
Virtualized Count/Compare access can make small deltas unreliable. Pre-R2 CPUs cannot reliably distinguish perf and timer interrupts. CPU frequency changes can invalidate timer assumptions.

### Test Signals
Run clockevent selftests under native and virtual MIPS, perf interrupt sharing tests, CPU frequency transition tests, nohz/oneshot tick tests, and compare-interrupt usability probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-r4k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-sb1250.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-sb1250.c

### Purpose
This file implements per-CPU clockevent devices using SiByte SB1250 general-purpose timers.

### Important APIs, Types, And Functions
Key functions are `sibyte_shutdown()`, `sibyte_set_periodic()`, `sibyte_next_event()`, `sibyte_counter_handler()`, and `sb1250_clockevent_init()`, with per-CPU clockevent/name storage.

### Control Flow
Initialization assigns timer IRQ `K_INT_TIMER_0 + cpu`, rejects CPUs above 2 because timer 3 is reserved for the high-precision clocksource, registers the clockevent, maps timer interrupts to IP4, unmasks, sets affinity, and requests the IRQ. Runtime mode setters program timer config/init registers.

### State, Persistence, And Dependencies
State includes SCD timer registers, interrupt mapper registers, per-CPU clockevent storage, and IRQ affinity. Dependencies are SB1250 register definitions, raw MMIO, and clockevents.

### Integration Points
SB1250 platform time setup uses this for CPU-local ticks while `csrc-sb1250.c` uses timer 3 as a clocksource.

### Risks
Only CPUs 0-2 may use event timers. Request IRQ failures are logged after registration. Timer frequency and IP mapping must match board wiring.

### Test Signals
SB1250 boot, per-CPU periodic/oneshot ticks, IRQ affinity and mapping validation, and coexistence with timer-3 clocksource are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-sb1250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-txx9.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-txx9.c

### Purpose
`cevt-txx9.c` provides both clocksource and clockevent support for Toshiba TXx9 timer blocks, plus a helper to reset timer hardware.

### Important APIs, Types, And Functions
Important types and functions are `struct txx9_clocksource`, `txx9_cs_read()`, `txx9_clocksource_init()`, `struct txx9_clock_event_device`, `txx9tmr_stop_and_clear()`, state setters, `txx9tmr_set_next_event()`, `txx9tmr_interrupt()`, `txx9_clockevent_init()`, and `txx9_tmr_init()`.

### Control Flow
Clocksource init registers a counter, maps timer registers, sets divider/control registers, starts the counter, stores the MMIO pointer, and registers sched_clock. Clockevent init maps the timer, clears it, registers event attributes, and requests the IRQ. State setters stop/clear before programming periodic, oneshot, shutdown, resume, or next event.

### State, Persistence, And Dependencies
State lives in ioremapped TXx9 timer registers, static clocksource/event structures, and the sched_clock registration. Dependencies include `asm/txx9tmr.h`, raw MMIO, clocksource, clockevents, and IRQ APIs.

### Integration Points
TXx9 platform setup calls these init helpers with board-specific base addresses, IRQs, and bus clocks.

### Risks
Both clocksource and clockevent use static singleton structures, so this code assumes one relevant timer instance for each role. Wrong bus clock values produce incorrect timekeeping.

### Test Signals
Validate timer reset, clocksource monotonicity, sched_clock rate, periodic and oneshot events, IRQ acking, and base-address remapping on TXx9 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-txx9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cmpxchg.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cmpxchg.c

### Purpose
`cmpxchg.c` implements sub-word exchange and compare-exchange helpers for MIPS by operating on the containing aligned 32-bit word.

### Important APIs, Types, And Functions
It provides `__xchg_small()` and exported `__cmpxchg_small()`, both using `arch_cmpxchg()` on aligned `u32` storage with masks and shifts.

### Control Flow
Each helper verifies natural alignment with `WARN_ON`, masks inputs to the requested byte/halfword size, computes endian-aware bit position within the containing word, loads the word, then loops with `arch_cmpxchg()` until the exchange succeeds or the compare value does not match.

### State, Persistence, And Dependencies
State is the target memory word. The helpers depend on atomic LL/SC or equivalent `arch_cmpxchg`, Linux bitops, and compile-time endianness.

### Integration Points
Generic atomic/xchg APIs call these when exchanging 1- or 2-byte values on architectures whose native atomics are word-sized.

### Risks
Concurrent updates to different bytes in the same word serialize through full-word compare-exchange and can still cause contention. Misaligned callers get only a warning, so correctness depends on API discipline.

### Test Signals
Atomic tests should cover byte and halfword exchange/cmpxchg, big- and little-endian positions, failure return values, concurrent updates to adjacent bytes, and misalignment warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cmpxchg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec-ns16550.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec-ns16550.S

### Purpose
This assembly file provides a stackless early UART diagnostic path for MIPS CPS BEV exceptions using an NS16550-compatible UART.

### Important APIs, Types, And Functions
Important symbols are `_mips_cps_putc`, `_mips_cps_puts`, `_mips_cps_putx4`, `_mips_cps_putx8`, `_mips_cps_putx16`, `_mips_cps_putx32`, `_mips_cps_putx64` on 64-bit, and `mips_cps_bev_dump`.

### Control Flow
Low-level putc polls UART line status until transmit-empty, then writes the character. Hex helpers recursively emit nibbles/bytes/words. `mips_cps_bev_dump()` builds the UART base from config, prints the exception name, and dumps CP0 Cause, Status, EBase, BadVAddr, and BadInstr.

### State, Persistence, And Dependencies
State is only registers and UART MMIO; the code intentionally avoids stack and normal memory. Dependencies are `CONFIG_MIPS_CPS_NS16550_*` width, shift, and base settings plus serial register definitions.

### Integration Points
`cps-vec.S` invokes `mips_cps_bev_dump` through the `DUMP_EXCEP` macro when configured, helping debug very early CPS core bring-up failures.

### Risks
Wrong UART base/width/shift can hang or print garbage during fatal exception handling. The code uses callee-saved registers without normal ABI stack preservation because it runs in emergency context.

### Test Signals
Force early BEV exception on a CPS system with configured UART, verify readable register dump, and build-test 8/16/32-bit UART width and 32/64-bit kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec-ns16550.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec.S

### Purpose
`cps-vec.S` implements low-level MIPS Coherent Processing System core boot, cache/coherence bring-up, VPE/VP startup, BEV exception stubs, and CPS power-management save/restore assembly.

### Important APIs, Types, And Functions
Important symbols/macros include `mips_cps_core_boot`, BEV stubs `excep_tlbfill`, `excep_xtlbfill`, `excep_cache`, `excep_genex`, `excep_intex`, `excep_ejtag`, `mips_cps_core_init`, `mips_cps_get_bootcfg`, `mips_cps_boot_vpes`, `mips_cps_cache_init`, `mips_cps_pm_save`, and `mips_cps_pm_restore`.

### Control Flow
Core boot saves CCA/GCR base, initializes caches if not already coherent, enters coherence, sets Kseg0 CCA, runs EVA init, retrieves boot config, performs MT core init, boots requested VPEs/VPs, loads target PC/GP/SP, and jumps to C code. VPE boot differs for MIPS R6 VP control via CPC run/stop registers versus classic MIPS MT TC/VPE configuration.

### State, Persistence, And Dependencies
State includes CP0 Config/EBase/MT registers, GCR/CPC registers, cache tags, coherence registers, boot config structures, and per-CPU suspend state. Dependencies include generated asm offsets, CPS SMP structures, EVA and PM macros, and optional NS16550 dumping.

### Integration Points
MIPS CPS SMP startup, CPU hotplug, early exception debugging, coherent domain entry, and CPU PM rely on this file.

### Risks
This executes before normal kernel services with fragile cache/coherence assumptions. Boot config offsets must match `asm-offsets.c`. MT and R6 VP paths have different register semantics, so config mismatches can strand VPEs.

### Test Signals
CPS SMP boot, multi-cluster/core/VPE startup, CPU hotplug, early BEV dump, cache initialization, coherent domain entry, and suspend/resume with CPS PM are key test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-probe.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-probe.c

### Purpose
`cpu-probe.c` identifies MIPS CPU implementations and capabilities, programs CP0 feature controls, populates `cpuinfo_mips`, and exports hardware capability data to userspace.

### Important APIs, Types, And Functions
Key globals are `elf_hwcap`, `__cpu_name`, `__elf_platform`, `__elf_base_platform`, `__ua_limit`, and `mmid_disabled_quirk`. Important functions include boot-parameter handlers for `nodsp`, `nohtw`, and `noftlb`; config decoders `decode_config0` through `decode_config5`; guest/VZ decoders; vendor probes for legacy, MIPS, Alchemy, SiByte, Broadcom, Cavium, Loongson, and Ingenic; `cpu_probe()`, `cpu_report()`, `cpu_set_cluster()`, `cpu_set_core()`, `cpu_set_vpe_id()`, and `cpu_disable_mmid()`.

### Control Flow
`cpu_probe()` initializes defaults, reads PRID, dispatches by company ID, decodes CP0 Config registers, applies vendor quirks, validates CPU type, enables RIXI exceptions when available, honors disable boot options, configures FPU/no-FPU state, sets SR sets and ELF HWCAP bits, probes MSA/VZ/vmbits, synthesizes Loongson CPUCFG, updates 64-bit user-address limits, and reserves exception space.

### State, Persistence, And Dependencies
State persists in per-CPU `cpu_data`, global ELF platform strings, HWCAP bits, CP0 Config/PageGrain/PWCtl/GuestCtl/GTOOffset/MemoryMapID registers, TLB sizing, ASID/MMID masks, write-combine modes, and exception reservation state.

### Integration Points
Almost every MIPS subsystem consumes this data: cache/TLB management, FPU/MSA, VZ/KVM, ELF auxv, signal ABI, page tables, perf, SMP topology, timers, and CPU errata handling.

### Risks
CPU probing mutates hardware registers while discovering features; mistakes can disable TLBs, MMID, FTLB, or hardware page walking incorrectly. Vendor PRID tables are broad and hardware-specific. Boot options must remain coherent with decoded feature flags.

### Test Signals
Boot matrix across supported CPU families, HWCAP/auxv validation, FPU/MSA/DSP availability, VZ guest feature probing, TLB/MMID/ASID behavior, `noftlb/nohtw/nodsp` boot options, and CPU hotplug consistency are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-r3k-probe.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-r3k-probe.c

### Purpose
This file is the reduced CPU probe path for R3000/R2000-era MIPS systems selected by `CONFIG_CPU_R3K_TLB`.

### Important APIs, Types, And Functions
It exports `elf_hwcap`, defines `check_bugs32()`, `cpu_has_confreg()`, `set_elf_platform()`, `cpu_probe()`, and `cpu_report()`.

### Control Flow
`cpu_probe()` reads PRID, switches on legacy implementation IDs, distinguishes R3000A from R3081 by toggling the alternate cache bit and comparing cache size, sets CPU name/type/options/FPU flags/TLB size, and BUGs on unknown CPU. `cpu_report()` logs CPU and FPU revisions.

### State, Persistence, And Dependencies
State persists in `current_cpu_data`, `__cpu_name`, `__elf_platform`, and `elf_hwcap`. Dependencies include R3K cache probing, CP0 PRID/conf reads, FPU detection, and CPU feature definitions.

### Integration Points
The kernel Makefile selects this instead of generic `cpu-probe.o` for R3K TLB builds. Early boot, cache/TLB management, ELF platform exposure, and bug checking rely on it.

### Risks
This path supports old hardware with simple feature detection. Misidentifying R3081/R3000 affects cache and TLB assumptions. Unknown PRIDs trigger BUG rather than fallback.

### Test Signals
Build with `CONFIG_CPU_R3K_TLB`, boot R2000/R3000/R3000A/R3081 targets, validate cache-size probing, FPU detection, TLB size, and reported CPU name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-r3k-probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/crash.c

### Purpose
`crash.c` coordinates MIPS crash shutdown for kexec, saving CPU register state and stopping secondary CPUs before rebooting into a crash kernel.

### Important APIs, Types, And Functions
Key state is `crashing_cpu` and `cpus_in_crash`. Important functions are `crash_shutdown_secondary()`, `crash_kexec_prepare_cpus()`, `crash_smp_send_stop()`, and `default_machine_crash_shutdown()`.

### Control Flow
The crashing CPU disables interrupts, saves its registers, sends IPIs to online secondary CPUs, waits up to about 10 seconds for them to enter crash state, marks CPUs stopped, and proceeds to kexec. Secondary CPUs find usable registers, mark themselves offline, disable interrupts, save CPU state once, wait for `kexec_ready_to_reboot`, then call `kexec_reboot()`.

### State, Persistence, And Dependencies
State includes crash CPU id, crash CPU mask, online CPU state, saved crash notes, and kexec readiness. Dependencies include SMP calls, kexec, crash dump, IRQ state, and task stack helpers.

### Integration Points
Generic panic/kexec paths call `default_machine_crash_shutdown()` and override `crash_smp_send_stop()`. Platform-specific `_crash_smp_send_stop` may run before the generic MIPS preparation.

### Risks
Crash paths run under panic conditions with limited synchronization. If secondary CPUs do not respond before timeout, crash dump completeness is reduced. Register fallback may be approximate.

### Test Signals
Kdump tests on SMP MIPS, forced panic with busy secondary CPUs, crash note validation, timeout behavior, and platform `_crash_smp_send_stop` interaction are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash_dump.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/crash_dump.c

### Purpose
`crash_dump.c` implements old-memory page copying for MIPS crash dump readers.

### Important APIs, Types, And Functions
It defines `copy_oldmem_page(struct iov_iter *iter, unsigned long pfn, size_t csize, unsigned long offset)`.

### Control Flow
If `csize` is zero, it returns immediately. Otherwise it maps the old page frame with `kmap_local_pfn()`, copies the requested range to the iterator with `copy_to_iter()`, unmaps, and returns the copied byte count.

### State, Persistence, And Dependencies
There is no persistent state in this file. It depends on highmem local mapping, crash dump infrastructure, and `iov_iter` copying.

### Integration Points
Kdump `/proc/vmcore` or equivalent crash dump readers use this architecture hook to extract pages from the crashed kernel memory image.

### Risks
Bounds are expected to be validated by callers; this function trusts `offset` and `csize` for the mapped page. Partial iterator copies return short counts.

### Test Signals
Kdump vmcore read tests, highmem PFN reads, zero-length reads, offset reads, and short iov iterator behavior validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-bcm1480.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-bcm1480.c

### Purpose
This file registers the BCM1480 ZBbus cycle counter as a 64-bit clocksource and sched_clock.

### Important APIs, Types, And Functions
It defines `bcm1480_hpt_read()`, exported object `bcm1480_clocksource`, `sb1480_read_sched_clock()`, and initializer `sb1480_clocksource_init()`.

### Control Flow
Initialization reads PLL divider from system config, derives ZBbus frequency in 25/50 MHz increments, registers the clocksource at that rate, and registers a 64-bit sched_clock reader.

### State, Persistence, And Dependencies
State is the SCD ZBbus cycle counter and clocksource registration. Dependencies are BCM1480/SB1250 register macros, raw MMIO, clocksource, sched_clock, and MIPS time setup.

### Integration Points
BCM1480 platform time init uses this as the continuous time source, paired with BCM1480 timer clockevents for interrupts.

### Risks
Frequency derivation assumes system configuration encoding and reference rate. Raw 64-bit reads must be safe on the target bus.

### Test Signals
Clocksource registration, monotonicity, sched_clock stability, frequency calibration against external time, and wrap handling are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-bcm1480.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-ioasic.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-ioasic.c

### Purpose
`csrc-ioasic.c` registers the DEC I/O ASIC free-running counter as a clocksource and sched_clock after calibrating it against DS1287 periodic ticks.

### Important APIs, Types, And Functions
Key functions are `dec_ioasic_hpt_read()`, `dec_ioasic_read_sched_clock()`, and `dec_ioasic_clocksource_init()`, with static `clocksource_dec`.

### Control Flow
Initialization synchronizes with an RTC periodic tick, samples the I/O ASIC counter, waits for `HZ / 8` further periodic ticks, samples again, computes frequency as delta times eight, rejects zero-frequency early ASICs, logs frequency, registers clocksource, and registers sched_clock.

### State, Persistence, And Dependencies
State includes I/O ASIC counter register, DS1287 RTC periodic state, computed frequency, and clocksource registration. Dependencies are DEC I/O ASIC accessors and DS1287 timer state.

### Integration Points
DEC MIPS platforms use this for continuous timekeeping when the I/O ASIC counter is present.

### Risks
Calibration depends on DS1287 periodic tick behavior and busy-waits during init. Early ASICs without a counter return `-ENXIO`.

### Test Signals
DEC platform boot, measured frequency sanity, monotonic counter reads, sched_clock registration, and fallback behavior on zero-frequency ASICs are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-ioasic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-r4k.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-r4k.c

### Purpose
`csrc-r4k.c` registers CP0 Count as the common MIPS R4K-style clocksource, optional VDSO clock mode, and sched_clock source.

### Important APIs, Types, And Functions
Important functions are `c0_hpt_read()`, `r4k_read_sched_clock()`, `rdhwr_count()`, `rdhwr_count_usable()`, `count_can_be_sched_clock()`, CPU-frequency notifier helpers, and `init_r4k_clocksource()`.

### Control Flow
Initialization checks for a CPU counter and known high-precision timer frequency, computes rating, verifies user-mode `rdhwr $2` is not broken before enabling VDSO R4K mode, registers the clocksource, and registers sched_clock only when CPU frequency/SMP stability conditions allow. CPU frequency transitions mark the clocksource unstable.

### State, Persistence, And Dependencies
State includes CP0 Count, `clocksource_mips`, optional `r4k_clock_unstable`, cpufreq notifier registration, and sched_clock state. Dependencies include CPU feature flags, MIPS timer frequency, VDSO clock mode, and cpufreq.

### Integration Points
Generic timekeeping, VDSO time reads, sched_clock, and R4K compare clockevents rely on this source.

### Risks
Broken RDHWR implementations are explicitly filtered. CPU frequency changes and unsynchronized per-CPU counters can make sched_clock or clocksource unstable.

### Test Signals
Clocksource monotonicity, VDSO clock_gettime under R2/R6, QEMU RDHWR workaround, CPU frequency transition tests, and SMP sched_clock stability checks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-r4k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-sb1250.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-sb1250.c

### Purpose
This file registers SiByte SB1250 timer 3 as a free-running high-precision clocksource and sched_clock.

### Important APIs, Types, And Functions
It defines `sb1250_hpt_get_cycles()`, `sb1250_hpt_read()`, exported `bcm1250_clocksource`, `sb1250_read_sched_clock()`, and `sb1250_clocksource_init()`.

### Control Flow
Initialization stops timer 3, loads its maximum counter value, starts it in continuous mode, registers the 23-bit clocksource at `V_SCD_TIMER_FREQ`, and registers a 23-bit sched_clock. Reads invert the down-counter into an increasing cycle value.

### State, Persistence, And Dependencies
State is SCD timer 3 registers and clocksource registration. Dependencies are SB1250 register macros, raw MMIO, clocksource, and sched_clock.

### Integration Points
SB1250 timekeeping uses timer 3 as a clocksource while CPUs use other timers for clockevents.

### Risks
Timer 3 is reserved here, so event code must not use it. The 23-bit width wraps quickly and depends on clocksource framework handling.

### Test Signals
Monotonic clocksource tests, sched_clock wrap tests, timer 3 reservation checks, and frequency validation against wall-clock time are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-sb1250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk.c

### Purpose
`early_printk.c` registers a minimal boot console that writes characters through the platform `prom_putchar()` hook.

### Important APIs, Types, And Functions
It defines `early_console_write()`, static console `early_console_prom`, and initializer `setup_early_printk()`.

### Control Flow
The write callback emits carriage return before newline, then sends each character to `prom_putchar()`. Setup returns if an early console already exists; otherwise it assigns `early_console` and registers the boot console.

### State, Persistence, And Dependencies
State is the global `early_console` pointer and console registration. Dependencies include `prom_putchar()` from platform or 8250 early code, console core, and MIPS setup globals.

### Integration Points
Early boot printk uses this before full console drivers bind. `early_printk_8250.c` can provide the `prom_putchar()` backend.

### Risks
If `prom_putchar()` blocks or is unconfigured, early output can disappear or stall. This console should be boot-only and not confused with the final console.

### Test Signals
Boot with early printk, verify newline translation, duplicate setup avoidance, printbuffer replay, and handoff to normal console drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk_8250.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk_8250.c

### Purpose
This file provides a `prom_putchar()` backend for early printk using an already-mapped 8250/16550 UART.

### Important APIs, Types, And Functions
It defines setup state `serial8250_base`, `serial8250_reg_shift`, `serial8250_tx_timeout`, public `setup_8250_early_printk_port()`, helpers `serial_in()` and `serial_out()`, and `prom_putchar()`.

### Control Flow
Setup records UART base, register shift, and timeout. `prom_putchar()` returns if no base is configured; otherwise it polls LSR for `UART_LSR_TEMT | UART_LSR_THRE` until timeout and writes the byte if ready.

### State, Persistence, And Dependencies
State is static UART configuration. Dependencies include MMIO `readb/writeb`, serial register constants, and the early console using `prom_putchar()`.

### Integration Points
Platform early setup calls `setup_8250_early_printk_port()`, and `early_printk.c` uses the exported `prom_putchar()` symbol to emit boot messages.

### Risks
The base address must already be usable with `readb/writeb`; no ioremap is performed here. Too-small timeout drops characters, too-large timeout can delay boot on bad UARTs.

### Test Signals
Boot tests with valid and missing UART setup, different register shifts, timeout behavior, and early console output integrity are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk_8250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/elf.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/elf.c

### Purpose
`elf.c` validates and applies MIPS-specific ELF ABI properties, especially FPU ABI mode, NaN encoding personality, and read-implies-exec behavior.

### Important APIs, Types, And Functions
Important globals are `mips_use_nan_legacy` and `mips_use_nan_2008`. Key functions are `arch_elf_pt_proc()`, `arch_check_elf()`, `set_thread_fp_mode()`, `mips_set_personality_fp()`, `mips_set_personality_nan()`, and exported `mips_elf_read_implies_exec()`.

### Control Flow
Program-header processing reads `PT_MIPS_ABIFLAGS` and records program/interpreter FP ABIs. ELF check validates NaN2008 compatibility, enforces matching interpreter NaN mode, computes allowable FP mode for O32 FP64 support, and rejects incompatible ABI combinations. Personality setup writes thread FP mode flags and FCSR NaN/ABS mode. Read-implies-exec is set only on CPUs lacking RIXI when `PT_GNU_STACK` did not specify a state.

### State, Persistence, And Dependencies
State is per-exec `arch_elf_state`, current thread flags, task FPU FCSR, global NaN policy, CPU FPU capabilities, and ELF flags. Dependencies include binfmt ELF, MIPS ABI flags, FPU ownership helpers, and CPU feature data.

### Integration Points
The Linux ELF loader calls these hooks during exec. Signal/FPU context, VDSO, user ABI compatibility, and security executable-stack policy depend on the decisions.

### Risks
O32 FP mode compatibility is subtle, especially with interpreters. Incorrect NaN policy can allow binaries that produce incompatible floating-point semantics. `kernel_read()` failures in ABI flags must propagate correctly.

### Test Signals
Exec tests for FP32/FP64/FPXX/soft-float/unknown ABI, interpreter mismatch, NaN2008 vs legacy policy, FCSR initialization, thread flags, and read-implies-exec on RIXI/non-RIXI CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/entry.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/entry.S

### Purpose
`entry.S` implements MIPS low-level return paths from exceptions, interrupts, syscalls, forks, and kernel threads, plus the instruction hazard barrier helper.

### Important APIs, Types, And Functions
Important exported labels are `ret_from_exception`, `ret_from_irq`, `__ret_from_irq`, `ret_from_kernel_thread`, `ret_from_fork`, `syscall_exit`, `restore_all`, `restore_partial`, `work_pending`, `syscall_exit_partial`, and `mips_ihb`.

### Control Flow
Return paths inspect saved status to determine user versus kernel return. User returns disable interrupts, check thread flags for reschedule, signal, notify, and syscall-trace work, call `schedule`, `do_notify_resume`, or `syscall_trace_leave` as needed, then restore registers. Kernel returns optionally perform preemption scheduling if interrupts were enabled and preempt count permits. Fork paths call `schedule_tail` then either kernel-thread function or syscall exit.

### State, Persistence, And Dependencies
State is the saved `pt_regs` frame on stack, `thread_info` flags/preempt count/current regs, IRQ flags, rseq debug state, and trace IRQ state. Dependencies include generated asm offsets, stackframe macros, irqflags, thread-info layout, and scheduler/tracing C functions.

### Integration Points
All exception/syscall/interrupt entry code returns through these labels. Signal delivery, ptrace/syscall tracing, preemption, rseq, and scheduler integration depend on this file.

### Risks
Ordering around interrupt disable and thread-flag sampling prevents missed reschedules/signals. Offset mismatches or instrumentation in this file would be catastrophic. Partial restore paths must preserve static registers around trace calls.

### Test Signals
Boot, syscall stress, signal delivery during syscalls, ptrace/seccomp tracing, preemption on interrupt return, rseq debug, fork/kernel-thread startup, and IRQ flag tracing validate this code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/entry.S -->
