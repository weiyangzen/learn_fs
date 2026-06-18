# subset-b-000844 research

This grouped report covers SPARC internal headers, SPARC UAPI ABI headers, and selected SPARC kernel platform/runtime files from the Ceph-client source tree. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vio.h

Purpose: Defines the sun4v virtual I/O protocol structures, descriptor-ring helpers, VIO device/driver objects, and common handshake state used by LDC-backed virtual network, disk, and console drivers.

Important APIs and control flow: message headers use `vio_msg_tag` type/subtype/envelope fields for version, attribute, descriptor-ring registration, ready-to-exchange, and data notifications. Disk and network sections define protocol payloads such as `vio_disk_attr_info`, `vio_disk_desc`, VTOC/geometry/devid/EFI formats, `vio_net_attr_info`, multicast messages, and network descriptors. `vio_dring_state` tracks ring base, producer/consumer cursors, cookies, and sequence numbers; inline helpers return current/indexed entries, free slots, and next/previous ring indexes. `vio_dev`, `vio_driver`, `vio_driver_state`, and `vio_driver_ops` connect the protocol to the Linux driver model and expose `vio_register_driver`, LDC allocation/free/send, handshake control, SID validation, interrupt control, and MDESC node lookup.

State, dependencies, and risks: persistent state lives in each `vio_driver_state`: spinlock-protected handshake flags, local/peer session IDs, LDC channel pointer, descriptor rings, completion wait state, timer, negotiated version, and driver callbacks. Dependencies include `asm/ldc.h`, machine description data, Linux devices, completions, timers, and module ownership. Risks are protocol-version drift, ring-size power-of-two assumptions in `vio_dring_avail`, flexible-array cookie sizing, and lock ordering between handshake and driver-private state. Test signals include successful VIO version/attribute/RDX handshakes, descriptor-ring wraparound under load, SID rejection tests, LDC reset recovery, and vnet/vdisk data-path traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/visasm.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/visasm.h

Purpose: Provides SPARC64 assembly and inline-C entry/exit helpers for VIS routines that need controlled FPU register ownership.

Important APIs and control flow: `VISEntry` reads `%fprs`, calls `VISenter` if FPU state is dirty/enabled, then enables FPRS_FEF for VIS instructions. `VISExit` clears `%fprs`. The half and fast variants support routines that preserve `%o5` and can branch to a failure label if FPU state is already enabled. `save_and_clear_fpu()` emits equivalent inline assembly for C callers, and `vis_emul()` is declared for VIS instruction emulation from trap code.

State, dependencies, and risks: state is CPU-local FPU register state and `%fprs` dirty bits. Dependencies include `asm/pstate.h`, `asm/ptrace.h`, the external `VISenter` routine, and SPARC register conventions. Risks are clobber-list mismatches, using these macros around code that cannot tolerate `%g*` or `%o5` clobbers, and missing save/restore on paths with early exits. Test signals are VIS crypto/copy routines under preemption, FPU-heavy workloads, and emulation traps that preserve user FPU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/visasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vmalloc.h

Purpose: Empty SPARC architecture hook header for vmalloc. It satisfies include contracts where architectures may override generic vmalloc behavior.

Important APIs and control flow: no APIs or macros are defined. Control flow is entirely through generic vmalloc headers.

State, dependencies, and risks: there is no runtime state. The dependency is only the include guard name expected by architecture code. Risk is low; changes here would affect generic header resolution. Test signals are architecture allmodconfig builds and vmalloc users compiling without missing arch hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/winmacro.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/winmacro.h

Purpose: Supplies SPARC32 assembly macros for saving/restoring register windows, trap-frame fields, user window spill bookkeeping, and current-task lookup.

Important APIs and control flow: `STORE_WINDOW`/`LOAD_WINDOW` move locals and ins between registers and memory offsets from `ptrace.h`. `LOAD_PT_*` and `STORE_PT_*` transfer selected `pt_regs` fields around trap return paths. `SAVE_BOLIXED_USER_STACK` records a user stack pointer and stores a register window in thread-info save slots. `LOAD_CURRENT` loads the current task pointer from `current_set`; on SMP it includes `.cpuid_patch` alternatives for SUN4D and LEON CPU-id mechanisms.

State, dependencies, and risks: state touched includes saved register-window arrays, trap frames, `%y`, PSR/PC/NPC fields, thread-info window counters, and per-CPU `current_set`. Dependencies include `asm/ptrace.h`, thread-info offsets, ASI definitions for Viking temporary registers, and boot-time CPU patching. Risks are offset drift, stack alignment assumptions, register clobber mistakes, and CPU-id patch errors on SMP. Test signals are trap/return stress, signal delivery, register-window overflow/underflow tests, SMP boot on sun4m/sun4d/LEON, and user-stack spill recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/winmacro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/Kbuild

Purpose: Declares generated UAPI syscall-number headers for SPARC.

Important APIs and control flow: `generated-y += unistd_32.h` and `generated-y += unistd_64.h` tell Kbuild to export generated syscall tables for 32-bit and 64-bit user ABI consumers.

State, dependencies, and risks: state is build-system metadata only. Dependencies are syscall table generation and UAPI header installation. Risks are missing generated headers breaking libc/kernel-header consumers or mismatching `unistd.h` includes. Test signals are `headers_install`, sparc32/sparc64 syscall header generation, and userspace compile checks using `asm/unistd.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/apc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/apc.h

Purpose: User ABI for the Aurora Personality Chip power-management driver on SPARCstation-4/5 style systems.

Important APIs and control flow: defines APC ioctl base `'A'`, get/set commands for fan control, convenience-power outlet, and bit ports, plus register offsets and bit values consumed by `arch/sparc/kernel/apc.c`. The ioctl payloads are integer-sized from the UAPI perspective, while the driver masks values to APC register-width bits.

State, dependencies, and risks: persistent state is in hardware APC registers, not the header. Dependencies include Linux ioctl encoding and the APC misc driver. Risks are ABI value changes, exposing platform-dependent bit ports to userspace, and confusion between active-low values such as `APC_CPOWER_ON`/`OFF`. Test signals are ioctl compatibility tests against `/dev/apc`, fan and outlet state reads/writes, and invalid-command rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/apc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/asi.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/asi.h

Purpose: Enumerates SPARC Address Space Identifier constants for sun4c/sun4m, LEON, V9, UltraSPARC, CMT, sun4v, and later SPARC cores.

Important APIs and control flow: the header is a constant map for alternate address-space load/store instructions. It includes legacy MMU/cache flush ASIs, LEON cache/MMU ASIs, V9 primary/secondary/no-fault/little-endian ASIs, physical bypass and block-load/store ASIs, diagnostic cache/tag ASIs, interrupt queue ASIs, MMU register spaces, ADI/MCD ASIs, and Niagara/T4+ PIC/crypto-era definitions.

State, dependencies, and risks: the state is CPU hardware addressing behavior selected by assembly and inline asm consumers. Dependencies include exact processor manuals and code using `ldxa/stxa/lduwa/lduha`. Risks are catastrophic if constants are altered, because wrong ASIs can access diagnostics, MMU, cache tags, physical memory, or hypervisor-related spaces. Test signals are architecture boot, cache/MMU flush tests, byte-swap inline asm, ADI tag operations, and trap handlers that read/write diagnostic registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/asi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/auxvec.h

Purpose: Defines SPARC-specific ELF auxiliary-vector entries.

Important APIs and control flow: `AT_SYSINFO_EHDR` advertises the vDSO ELF header to userspace, and `AT_ADI_BLKSZ`, `AT_ADI_NBITS`, and `AT_ADI_UEONADI` advertise Application Data Integrity capability details.

State, dependencies, and risks: state is per-process auxv content produced at exec time. Dependencies include ELF loader setup, vDSO mapping, and ADI platform detection. Risks are ABI breakage if values change and incorrect ADI capability exposure causing applications to issue unsupported tagged-memory operations. Test signals are `/proc/self/auxv`, libc/vDSO startup, ADI-aware application probes, and exec tests on non-ADI systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/bitsperlong.h

Purpose: Selects the user-visible long width for SPARC ABIs.

Important APIs and control flow: when building for SPARC64 userspace (`__sparc__ && __arch64__`), `__BITS_PER_LONG` is 64. Otherwise the generic header supplies the 32-bit definition. This feeds time, socket, stat, and ioctl ABI conditionals.

State, dependencies, and risks: no runtime state. Dependencies are compiler ABI defines and `asm-generic/bitsperlong.h`. Risks are high for userspace ABI if the condition is wrong, particularly for time64 socket option selection and struct layouts. Test signals are 32-bit and 64-bit header compile tests and sizeof assertions for UAPI structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/byteorder.h

Purpose: Declares SPARC user ABI byte order.

Important APIs and control flow: includes `linux/byteorder/big_endian.h`, making SPARC UAPI consumers use big-endian integer conversion definitions.

State, dependencies, and risks: no runtime state. Dependencies are generic byteorder headers. Risks are ABI/data corruption if endian assumptions diverge from compiler target, particularly for network, filesystem, and ioctl structures. Test signals are endian macro compile tests and cross-built userspace using kernel headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/display7seg.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/display7seg.h

Purpose: UAPI for Sun 7-segment display control devices.

Important APIs and control flow: defines ioctl base, control/status register bit definitions, conversion-mode flags, and ioctl numbers to read/write the display control register. Drivers use these constants to expose user control over raw display bits or decoded hexadecimal/alphabetic display behavior.

State, dependencies, and risks: state is hardware display mode and latched display value. Dependencies include Linux ioctl encoding and the corresponding platform display driver. Risks include ABI value drift, userspace assuming a display exists across platforms, and unsafe concurrent writes to shared front-panel hardware. Test signals are ioctl read/write round trips, display update observation, and invalid bit/mode handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/display7seg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/envctrl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/envctrl.h

Purpose: User ABI definitions for SPARC environmental-control devices.

Important APIs and control flow: the header defines ioctl commands and data structures for reading environmental status such as fan, power-supply, temperature, and global warning/shutdown conditions. It also encodes device/status constants used by user monitoring tools and platform drivers.

State, dependencies, and risks: persistent state is sensor and controller hardware state. Dependencies include the envctrl driver, ioctl ABI, and platform-specific sensor layout. Risks include structure-size compatibility, interpreting advisory warning bits as control policy, and stale platform constants for rare Sun hardware. Test signals are sensor ioctl enumeration, threshold alarm simulation where possible, and userspace monitoring compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/envctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/errno.h

Purpose: Provides SPARC errno values, including historical SunOS-compatible numbering differences.

Important APIs and control flow: the header defines architecture-specific errno constants and then integrates generic errno definitions. Its values are consumed by syscall return paths, libc, and compatibility layers.

State, dependencies, and risks: no runtime state, but values are ABI state. Dependencies include generic errno headers and userspace libc expectations. Risks are severe if numbers change, because syscall error interpretation changes. Test signals are syscall ABI tests, libc header comparisons, and 32-bit/64-bit compat errno checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fbio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fbio.h

Purpose: SunOS-compatible framebuffer ioctl and mmap-offset ABI for SPARC framebuffer devices.

Important APIs and control flow: defines framebuffer type IDs, `struct fbtype`, color-map and cursor structures, generic FBIO ioctls, WID allocation/list structures, Creator/FFB ioctls, cg14/MDI configuration and map offsets, and Leo CLUT/map constants. Drivers use these to translate legacy Sun framebuffer applications to Linux device operations.

State, dependencies, and risks: state includes framebuffer geometry, color maps, cursor image/position, WID allocations, CLUTs, video enable state, and mmap region selection. Dependencies include user-pointer annotations, SPARC ioctl encoding, and framebuffer drivers for cg/leo/ffb/creator-class devices. Risks are pointer-size compatibility, unsupported ioctls that must still preserve numeric ABI, mappable offset collisions, and stale hardware-specific constants. Test signals are `FBIOGTYPE`/`FBIOGATTR`, color-map set/get, cursor operations, legacy X server startup, and mmap of documented offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fbio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fcntl.h

Purpose: Defines SPARC-specific open and fcntl constants before including generic fcntl definitions.

Important APIs and control flow: preserves Sun/SPARC values for `O_*` flags, including special `O_NDELAY` behavior that differs for 64-bit SPARC, the historical `O_DSYNC`/`O_SYNC` split, file-lock commands, and flock padding macros. Generic fcntl definitions fill in the shared remainder.

State, dependencies, and risks: state is syscall ABI flag values and structure padding. Dependencies include `asm-generic/fcntl.h` and libc headers. Risks include applications using bitwise constants directly, older kernels interpreting `O_SYNC`, and compat differences for nonblocking mode. Test signals are open/fcntl syscall ABI tests, structure-size checks, and 32-bit/64-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctl.h

Purpose: Defines SPARC ioctl number encoding.

Important APIs and control flow: `_IOC` packs direction, type, number, and size using SPARC's overlapping DIR/SIZE layout to preserve nonzero `_IOC_NONE` while retaining a 14-bit decoded size. `_IO`, `_IOR`, `_IOW`, `_IOWR`, and decoder macros are used by drivers and UAPI headers. Legacy `IOC_IN`, `IOC_OUT`, and size masks support PCMCIA/sound-style consumers.

State, dependencies, and risks: state is ABI numbering for every SPARC ioctl. Dependencies are compiler `sizeof` and driver decoder usage. Risks are command-number collisions, incorrect size decoding for `_IOC_NONE`, and cross-architecture assumptions in shared drivers. Test signals are ioctl number compile assertions, strace/driver decoding, and compat ioctl dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctls.h

Purpose: SPARC tty, pty, serial, and file ioctl number ABI.

Important APIs and control flow: defines termio/termios commands under `'T'`, BSD/SunOS-style `TIOC*` commands under `'t'`, file ioctls under `'f'`, Linux serial ioctls, packet-mode constants, and aliases such as `TIOCINQ`. Commands marked with double underscores preserve SunOS numeric space without declaring Linux support.

State, dependencies, and risks: state is tty/serial line discipline, pty lock/packet state, modem control, window size, and file descriptor flags. Dependencies include `asm/ioctl.h`, `termbits.h`, serial structures, and tty core dispatch. Risks are legacy numeric compatibility, struct-size mismatches, and accidental exposure of unsupported SunOS commands. Test signals are tty ioctl ABI tests, pty packet-mode tests, serial modem-line operations, and 32-bit compat ioctl handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ipcbuf.h

Purpose: Defines SPARC `ipc64_perm` layout for SysV IPC user ABI.

Important APIs and control flow: the structure stores key, owner/creator IDs, mode, sequence, and reserved padding. A conditional pad keeps 32-bit and 64-bit layouts aligned with kernel/user exchange expectations.

State, dependencies, and risks: state is IPC object metadata passed through msgctl/semctl/shmctl. Dependencies include Linux POSIX type definitions and the IPC subsystem. Risks are padding changes breaking old binaries and mismatched sequence width. Test signals are IPC permission round trips on 32-bit and 64-bit SPARC and structure layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ipcbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/mman.h

Purpose: SPARC memory-mapping constants layered on common generic mmap definitions.

Important APIs and control flow: adds `PROT_ADI`, SunOS compatibility names such as `MAP_RENAME`, SPARC-specific `MAP_NORESERVE`, `MAP_INHERIT`, `MAP_LOCKED`, `_MAP_NEW`, stack/executable flags, and mlockall flags. These constants feed mmap/mprotect/mlock syscall decoding.

State, dependencies, and risks: state is VMA protection and mapping policy. Dependencies include generic mman common definitions and ADI-capable MM code. Risks include flag collisions, exposing `PROT_ADI` on unsupported platforms, and legacy `_MAP_NEW` compatibility. Test signals are mmap/mprotect flag tests, ADI protected mappings, mlockall behavior, and SunOS-compat application probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/msgbuf.h

Purpose: Defines SPARC `msqid64_ds` SysV message-queue ABI layout.

Important APIs and control flow: embeds `ipc64_perm`, stores send/receive/change times with 64-bit-native longs or high/low 32-bit fields, queue byte/message counts, byte limit, last sender/receiver pids, and reserved fields.

State, dependencies, and risks: state is message-queue metadata returned to userspace. Dependencies include `asm/ipcbuf.h` and SysV IPC control paths. Risks are time-field layout compatibility, unsigned long size variation, and padding changes. Test signals are `msgctl(IPC_STAT)` on 32-bit/64-bit SPARC, y2038/time64 checks, and IPC namespace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/openpromio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/openpromio.h

Purpose: User ABI for `/dev/openprom`, compatible with SunOS/Solaris and BSD openprom interfaces.

Important APIs and control flow: `struct openpromio` carries variable-length property buffers for SunOS-style OPROM ioctls such as get/set option, next property, child/next node, property lookup, console info, framebuffer name, boot args, and Linux extensions for selecting nodes by id, PCI tuple, or path. `struct opiocdesc` supports BSD-style property operations using user pointers.

State, dependencies, and risks: state is PROM/device-tree navigation cursor and firmware properties. Dependencies include Linux ioctl encoding, user-pointer handling, and PROM access drivers. Risks include buffer-size trust, pointer-size compat, exposing firmware mutation, and exact SunOS numeric compatibility. Test signals are property enumeration, path-to-node lookup, boot-args retrieval, console flag retrieval, and compat ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/openpromio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/oradax.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/oradax.h

Purpose: UAPI for Oracle DAX command/completion management.

Important APIs and control flow: defines command codes for kill, info, and dequeue operations; `struct dax_command` passes command type plus completion-area offset; result structures describe kill action, queue state/location, or execution status data. Constants define mmap completion-area length, maximum CCB count, CCB buffer size, device name, submit statuses, CCB states, and kill results.

State, dependencies, and risks: state is DAX hardware/driver command queue and mmapped completion area. Dependencies include Linux integer types, DAX driver ioctl/mmap implementation, and hypervisor state constants noted by comments. Risks are mismatch with hypervisor `HV_CCB_*` values, offset validation into the completion area, and concurrent queue mutation. Test signals are DAX mmap size checks, enqueue/dequeue/kill/info operations, bad-offset rejection, and status propagation from hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/oradax.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/param.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/param.h

Purpose: Defines SPARC UAPI process/system parameter constants.

Important APIs and control flow: sets `EXEC_PAGESIZE` to 8192 for historical sun4 compatibility, then includes generic parameter definitions for HZ and related constants.

State, dependencies, and risks: no runtime state, but values are ABI-visible. Dependencies include `asm-generic/param.h`. Risks are userspace page/executable assumptions if changed. Test signals are header compile tests and legacy binary compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/perfctr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/perfctr.h

Purpose: Historical UltraSPARC `sys_perfctr()` ABI definitions, retained even though perf events superseded the syscall.

Important APIs and control flow: `enum perfctr_opcode` defines enable, disable, read, clear PIC, set PCR, and get PCR operations. Comments document that user pointers refer to 64-bit accumulators/PCR values and that enabled counter state followed fork/clone until exec or explicit disable. The header also defines privilege/user/system mode bits, Ultra-I/II and Ultra-III PIC event encodings for both counter fields, and `vcounter_struct`.

State, dependencies, and risks: state would be per-process performance counter accumulator pointers and PCR/PIC registers in legacy kernels. Dependencies are UltraSPARC PCR/PIC hardware and old syscall implementations. Risks are stale ABI consumers, unsafe user pointers in historical implementations, and event encoding differences across CPU generations. Test signals are mostly compile compatibility now; on old support trees, counter enable/read/clear and fork/exec retention are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/perfctr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/poll.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/poll.h

Purpose: SPARC poll event constants layered on generic poll definitions.

Important APIs and control flow: defines SPARC values/aliases for `POLLWRNORM`, `POLLWRBAND`, `POLLMSG`, `POLLREMOVE`, and `POLLRDHUP`, then includes `asm-generic/poll.h`.

State, dependencies, and risks: state is event masks exchanged by poll/select/epoll paths. Dependencies include generic poll constants. Risks are ABI changes breaking userspace event decoding. Test signals are poll/epoll tests for write band, hangup, and removal events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/posix_types.h

Purpose: Supplies SPARC-specific kernel POSIX typedefs before generic type completion.

Important APIs and control flow: for 64-bit SPARC it defines old UID/GID types, signed `__kernel_suseconds_t`, long/ulong aliases, and old timeval layout. For 32-bit SPARC it defines size, ssize, ptrdiff, IPC pid, UID/GID, mode, disk address, and old device types. Generic POSIX types are included afterward.

State, dependencies, and risks: no runtime state, but the typedefs determine UAPI structure layout. Dependencies include compiler ABI macros and `asm-generic/posix_types.h`. Risks are namespace pollution, libc incompatibility, and subtle layout drift in IPC, stat, signal, and socket time structures. Test signals are userspace header builds and ABI layout assertions for both SPARC modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psr.h

Purpose: Defines SPARC V8 Processor Status Register bit masks and field shifts.

Important APIs and control flow: constants cover CWP, trap enable, privilege bits, interrupt priority level, FPU/coprocessor enable, syscall marker, SuperSPARC little-endian bit, integer condition codes, implementation/version fields, and known implementation IDs for TI and LEON. Assembly and ptrace-style code use these to interpret or synthesize PSR state.

State, dependencies, and risks: state is hardware PSR and trap-frame PSR images. Dependencies include V8 CPU semantics and `ptrace.h` consumers. Risks are wrong privilege/interrupt/FPU interpretation and incompatibility with register dump tools. Test signals are trap-frame decode, ptrace get/set registers, FPU enable paths, and LEON CPU identification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psrcompat.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psrcompat.h

Purpose: Converts between 64-bit V9 `tstate` condition state and old 32-bit PSR-compatible views for compat code.

Important APIs and control flow: duplicates V8 PSR masks, defines fake `PSR_V8PLUS` and `PSR_XCC`, and provides `tstate_to_psr()` and `psr_to_tstate_icc()` inline conversions. The conversion maps CWP, supervisor bit, ICC, optional XCC, syscall marker, and the V8PLUS marker.

State, dependencies, and risks: state is signal/ptrace-visible register condition codes during 32-bit compatibility on 64-bit kernels. Dependencies include `asm/pstate.h`. Risks are lost condition-code bits, incorrect syscall marker preservation, and debugger/signal-frame ABI regressions. Test signals are 32-bit process ptrace, signal return, condition-code-sensitive single stepping, and V8PLUS userspace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psrcompat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/pstate.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/pstate.h

Purpose: Defines SPARC V9 PSTATE, TSTATE, FPRS, version-register, and compatibility-feature bit masks.

Important APIs and control flow: PSTATE constants describe interrupt/MMU globals, endian controls, memory model, RED, FPU enable, address mask, privilege, interrupts, and alternate globals; `PSTATE_MCDE` shares the IG bit on ADI-capable processors. TSTATE constants map global level, condition codes, ASI, PIL, embedded PSTATE, syscall marker, and CWP. FPRS constants expose FPU enable and dirty bits. Version and CFR masks expose CPU implementation and crypto/hash capability features.

State, dependencies, and risks: state is trap-frame and CPU privileged register content. Dependencies include assembly trap code, VIS/FPU helpers, ADI handling, signal/ptrace, and CPU feature reporting. Risks are overlapping IG/MCDE semantics, incorrect memory-model or privilege-bit manipulation, and ABI-visible debugger breakage. Test signals are trap entry/return, ptrace register views, VIS/FPU save/restore, ADI enablement, and CPU capability reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/pstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ptrace.h

Purpose: Defines SPARC trap/register-frame, register-window, stack-frame, offset, and ptrace request ABI for 32-bit and 64-bit users.

Important APIs and control flow: 64-bit `pt_regs` stores globals/ins, tstate, tpc, tnpc, y, and a magic/trap-type word; 32-bit `pt_regs` stores psr, pc, npc, y, and globals/ins. The header defines 64-bit and 32-bit register windows and stack frames, trap-frame helpers, register indexes (`UREG_*`), assembler-visible sizes, field offsets, and SPARC-specific ptrace request numbers including 64-bit register operations for mixed-debugger cases.

State, dependencies, and risks: state is trap stack frames, user register sets, register windows, and debugger-visible process state. Dependencies include `psr.h`/`pstate.h`, syscall/trap assembly, signal code, unwinder magic, and ptrace core. Risks are offset drift breaking assembly, wrong struct layout for compat debuggers, and unwinder false positives if magic semantics change. Test signals are ptrace get/set regs/fpregs for 32-bit and 64-bit tasks, signal frame unwinding, register-window spill tests, and syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/resource.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/resource.h

Purpose: SPARC resource-limit constants and compatibility values.

Important APIs and control flow: preserves SPARC-specific ordering for `RLIMIT_NOFILE` and `RLIMIT_NPROC`. On 32-bit SPARC, `RLIM_INFINITY` remains the old signed-compatible `0x7fffffff`; other definitions come from `asm-generic/resource.h`.

State, dependencies, and risks: state is process rlimit values exchanged through getrlimit/setrlimit. Dependencies include generic resource UAPI and libc. Risks are ABI ordering differences from other architectures and infinity value compatibility. Test signals are rlimit syscall tests on 32-bit and 64-bit SPARC and libc constant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sembuf.h

Purpose: Defines SPARC `semid64_ds` SysV semaphore ABI layout.

Important APIs and control flow: embeds `ipc64_perm`, stores operation/change times as native longs or high/low pairs, semaphore count, and reserved fields. The layout is used by semctl IPC_STAT/IPC_SET paths.

State, dependencies, and risks: state is semaphore-array metadata. Dependencies include `asm/ipcbuf.h` and SysV semaphore code. Risks are time-field and padding compatibility, especially across 32-bit and 64-bit processes. Test signals are semctl structure round trips and ABI layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sembuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/setup.h

Purpose: Defines SPARC command-line buffer size for UAPI consumers.

Important APIs and control flow: `COMMAND_LINE_SIZE` is 2048 for SPARC64 and 256 for SPARC32.

State, dependencies, and risks: state is boot command-line storage sizing. Dependencies are compiler ABI macros and setup code. Risks are truncation expectations and userspace tools assuming a larger command line on 32-bit systems. Test signals are boot command-line length tests and header compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/shmbuf.h

Purpose: Defines SPARC SysV shared-memory ABI structures.

Important APIs and control flow: `shmid64_ds` carries permissions, attach/detach/change times, segment size, creator/last-operation pids, attach count, and reserved fields with 32-bit/64-bit time layout conditionals. `shminfo64` exposes system shared-memory limits and padding.

State, dependencies, and risks: state is shared-memory segment metadata and global limits. Dependencies include `asm/ipcbuf.h`, `asm/posix_types.h`, and SysV shm control code. Risks are structure padding and time-size compatibility. Test signals are shmctl IPC_STAT/IPC_INFO tests, 32-bit compat checks, and large segment size reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/shmbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sigcontext.h

Purpose: Placeholder UAPI header retained for include compatibility.

Important APIs and control flow: defines no structures or constants; comments note it must not be empty enough for patch tooling to delete it.

State, dependencies, and risks: no runtime state. Dependencies are userspace and kernel headers that include `asm/sigcontext.h`. Risk is removal breaking source compatibility even though signal context layouts live elsewhere. Test signals are userspace header builds including signal headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/siginfo.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/siginfo.h

Purpose: SPARC siginfo customizations layered on generic siginfo.

Important APIs and control flow: for 64-bit SPARC, `__ARCH_SI_BAND_T` is `int`; generic siginfo definitions are included; `SI_NOINFO` is defined as 32767.

State, dependencies, and risks: state is signal metadata delivered to userspace. Dependencies include generic siginfo layout and SPARC signal delivery. Risks are siginfo field-size mismatch and value compatibility for no-info signals. Test signals are realtime signal delivery, `sigwaitinfo`, ptrace signal injection, and 32-bit/64-bit siginfo layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/siginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/signal.h

Purpose: Defines SPARC signal numbers, sub-signal codes, signal-set sizes, sigaction layouts, signal-stack structures, and signal mask operations.

Important APIs and control flow: signal numbers follow SunOS-influenced SPARC ordering, including `SIGEMT`, `SIGLOST`, and realtime range 32-64. Subsignal constants distinguish illegal instruction, FP errors, bus/alignment faults, and segmentation causes. Conditional macros select old 32-signal or new 64-signal ABI names depending on kernel/POSIX1B needs. The header defines old/new sigset types, SunOS `sigstack`, sigvec/sa flags, mask operations, minimum/default stack sizes, old/new sigaction layouts, and `stack_t`.

State, dependencies, and risks: state is process signal masks, handler dispositions, alternate stacks, and delivered trap subcodes. Dependencies include `sigcontext.h`, generic signal definitions, and POSIX types. Risks are nonstandard signal numbering, old/new sigset aliasing, unsupported-but-numeric flags, and 32-bit pointer comments in legacy `sigstack`. Test signals are signal number ABI tests, sigaction/sigaltstack, fault delivery subcodes, realtime signal masks, and compat signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/socket.h

Purpose: SPARC socket option and control-message ABI constants.

Important APIs and control flow: defines `SOL_SOCKET`, core `SO_*` values, Linux-specific options, timestamp/timeval old/new variants, security placeholders, zero-copy, BPF, busy-poll, device-memory, and newer ancillary aliases. Outside the kernel, `SO_TIMESTAMP`, `SO_RCVTIMEO`, and related names resolve to old or new values based on long/time_t width.

State, dependencies, and risks: state is socket options, ancillary message types, timeout/timestamp ABI selection, and filter attachment state. Dependencies include `linux/posix_types.h`, `asm/sockios.h`, `__BITS_PER_LONG`, and libc time_t width. Risks are value differences from other architectures, time64 selection mistakes, and new option collisions. Test signals are getsockopt/setsockopt ABI tests, timestamping in 32-bit and 64-bit userspace, BPF filter attach/detach, and SCM control-message decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/stat.h

Purpose: Defines SPARC `stat` and `stat64` user ABI layouts.

Important APIs and control flow: 64-bit SPARC has compact `struct stat` and wider `struct stat64` with nsec fields and reserved padding. 32-bit SPARC has legacy `struct stat` with `STAT_HAVE_NSEC` and a padded `struct stat64` carrying 64-bit dev/ino/rdev/size plus 32-bit timestamps and nsec fields.

State, dependencies, and risks: state is filesystem inode metadata copied to userspace. Dependencies include Linux type definitions and VFS stat translation. Risks are layout drift, y2038 behavior on 32-bit stat64, device/inode truncation, and libc mismatches. Test signals are stat/lstat/fstat/stat64 syscall tests, large inode/device tests, timestamp nsec checks, and 32-bit compat validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/swab.h

Purpose: Provides SPARC byte-swap optimized helpers for pointer loads.

Important APIs and control flow: on 64-bit SPARC, `__arch_swab16p`, `__arch_swab32p`, and `__arch_swab64p` use little-endian primary ASI loads (`ASI_PL`) to fetch swapped values directly. On non-64-bit SPARC, `__SWAB_64_THRU_32__` requests generic 64-bit swapping through 32-bit pieces.

State, dependencies, and risks: state is memory content read through alternate-endian load instructions. Dependencies include `linux/types.h`, `asm/asi.h`, compiler inline assembly, and alignment/fault behavior. Risks are invalid user/kernel pointer use, ASI availability, and inline asm constraints. Test signals are byteorder helper tests, unaligned/access fault coverage where applicable, and cross-endian data structure parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termbits.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termbits.h

Purpose: SPARC termios flag, structure, speed, control-character, and modem-line ABI.

Important APIs and control flow: chooses `tcflag_t` width by 64-bit ABI, defines `NCCS`, `termios`, `termios2`, and `ktermios` layouts, with kernel-only extra VMIN/VTIME slots in `termios`. It assigns SPARC control-character indexes, input/output/control/local flag bits, extended baud rates, modem bits, line-status constants, and tcsetattr action values.

State, dependencies, and risks: state is tty line discipline configuration and serial port settings. Dependencies include generic termbits common definitions and tty core conversion code. Risks are kernel/user `termios` size differences, SPARC-specific baud values, VMIN/VTIME aliasing in userspace, and flag numbering compatibility. Test signals are stty/ioctl round trips, arbitrary baud with `termios2`, modem-line tests, and 32-bit/64-bit structure-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termios.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termios.h

Purpose: SPARC legacy terminal structure definitions layered on ioctl and termbits constants.

Important APIs and control flow: includes `ioctls.h` and `termbits.h`, conditionally exposes BSD `sgttyb`, `tchars`, and `ltchars` when requested or in-kernel, defines `winsize`, and provides legacy `struct termio` with `NCC=8`.

State, dependencies, and risks: state is terminal window size and legacy line settings exchanged with tty drivers. Dependencies include ioctl numbers, termbit layouts, and conditional BSD compatibility macros. Risks are source compatibility versus namespace pollution and legacy structure-size expectations. Test signals are `TCGETA`/`TCSETA`, `TIOCGWINSZ`/`TIOCSWINSZ`, and programs defining `__DEFINE_BSD_TERMIOS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/traps.h

Purpose: SPARC trap-table constants, instruction encoders, and trap classification macros.

Important APIs and control flow: defines `NUM_SPARC_TRAPS`, instruction-forming helpers for trap-table patching, hardware trap numbers, software trap numbers for SunOS/Solaris/NetBSD/Linux syscalls, PROM breakpoint traps, compatibility aliases, and macros to classify bad, hardware, software, and syscall traps.

State, dependencies, and risks: state is trap table contents and trap-level classification in low-level code. Dependencies include SPARC instruction encoding and architecture trap assignments. Risks are branch helper assumptions that destination follows instruction, wrong syscall trap classification, and debugger/PROM breakpoint incompatibility. Test signals are trap-table patching during boot, syscall entry for supported personalities, illegal/fault trap delivery, and BAD_TRAP_P coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/uctx.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/uctx.h

Purpose: SPARC64 `getcontext`/`setcontext` machine-context register and FPU layout definitions.

Important APIs and control flow: defines general-register indexes for tstate, pc/npc, y, globals, outs, frame pointer, return pc, and count. `mc_fpu` contains single/double/quad views of FPU registers, FSR/FPRS/GSR, FQ pointer, queue count/entry size, and enable state. `mcontext_t` and `ucontext_t` combine registers, stack-link flags, signal mask, and context link.

State, dependencies, and risks: state is userspace context saved/restored by libc or signal/context APIs. Dependencies include `sigset_t` from signal headers and exact SPARC64 register semantics. Risks include pointer-size ABI, FPU queue handling, and mismatches with signal frame construction. Test signals are `getcontext`/`setcontext`/`swapcontext`, signal context inspection, FPU state preservation, and 64-bit userspace ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/uctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/unistd.h

Purpose: Selects generated SPARC syscall-number headers and exposes SPARC kernel feature bits.

Important APIs and control flow: defines `__32bit_syscall_numbers__` for non-`__arch64__` builds, includes `unistd_64.h` or `unistd_32.h`, and defines `KERN_FEATURE_MIXED_MODE_STACK` for the `kern_features` syscall.

State, dependencies, and risks: state is syscall number ABI and feature bit reporting. Dependencies include generated Kbuild outputs and libc syscall wrappers. Risks are wrong syscall table selection for compat builds and stale feature bits. Test signals are syscall-number header generation, simple syscall invocation from 32-bit/64-bit userspace, and `kern_features` probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/utrap.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/utrap.h

Purpose: Defines SPARC64 user-trap type numbers and handler types.

Important APIs and control flow: constants enumerate instruction, data, FP, tag, division, alignment, privileged-action, async data, and trap-instruction user trap slots. `UTH_NOCHANGE` denotes no handler change. C consumers get `utrap_entry_t` and `utrap_handler_t` typedefs.

State, dependencies, and risks: state is userspace trap handler registration and dispatch. Dependencies are SPARC64 user-trap syscall/trap support. Risks include stable numbering for applications using user-level trap handlers and pointer compatibility. Test signals are user trap registration, illegal/divide/alignment trap handling, and handler no-change semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/utrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/watchdog.h

Purpose: Solaris-compatible SPARC hardware-watchdog ioctl ABI.

Important APIs and control flow: includes generic Linux watchdog UAPI, then defines `WIOCSTART`, `WIOCSTOP`, and `WIOCGSTAT` plus status bits for freerun, expired, running, stopped, and serviced states.

State, dependencies, and risks: state is hardware watchdog timer enablement, expiry, and interrupt service status. Dependencies include Linux watchdog ioctl base and Sun board watchdog drivers. Risks are ABI overlap with generic watchdog commands and userspace relying on Solaris-compatible status bits. Test signals are watchdog start/stop/status ioctls, timeout expiry tests, and generic watchdog compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/Makefile

Purpose: Maps SPARC kernel configuration symbols to architecture kernel objects and special build flags.

Important APIs and control flow: sets `CPPFLAGS_vmlinux.lds`, always builds the linker script when built-in, removes function-tracer profiling from low-level timing/perf/ftrace objects, and selects boot heads, trap/IRQ/process/signal/setup/time/prom/of-device objects by `$(BITS)`. It conditionally builds SPARC32 platform support, SPARC64 hypervisor/IOMMU/LDOM/VIO/PCI/perf/ADI/NMI objects, SMP and hotplug pieces, early framebuffer, audit/compat audit, modules, kprobes, uprobes, jump labels, and US3 memory controller support.

State, dependencies, and risks: state is build composition and object ordering. Dependencies are Kconfig symbols, generated syscall/linker assets, and low-level assembly names. Risks include unresolved symbols from mismatched config selections, profiling low-level trap/time paths, and missing compat audit objects. Test signals are SPARC32/SPARC64 defconfig and allmodconfig builds, linker-script preprocessing, ftrace-enabled builds, and config combinations for PCI, LDOMS, AUDIT, COMPAT, and US3_MC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/adi_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/adi_64.c

Purpose: Implements SPARC64 Application Data Integrity tag capability discovery and swap-out/swap-in tag persistence.

Important APIs and control flow: `mdesc_adi_init()` grabs the machine description, checks CPU `hwcap-list` for `adp`, reads platform `adp-blksz`, `adp-nbits`, and `ue-on-adp`, and disables ADI if tag width exceeds the two-tags-per-byte assumption. `find_tag_store()` looks for an existing descriptor covering a VMA address. `alloc_tag_store()` allocates a page of descriptors per mm, finds holes, reserves a range of tag storage sized for up to `TAG_STORAGE_PAGES`, and maintains `tag_users`. `adi_save_tags()` reads physical-page ADI tags with `ASI_MCD_REAL` and packs two 4-bit tags per byte. `adi_restore_tags()` unpacks saved tags, writes them to the new physical page, clears saved bytes, issues a sync membar, and releases descriptor references.

State, dependencies, and risks: global `adi_state` exports platform capability state. Per-mm state includes `mm->context.tag_store` and `tag_lock`; descriptor entries persist tag ranges and buffers across swap. Dependencies include MDESC, MM context fields, SPARC page-table physical address bits, ADI block size helpers, `ASI_MCD_REAL`, GFP_NOWAIT allocation, and swap/VMA paths. Risks include allocation failure losing tags (`-1`), descriptor exhaustion, address overflow/underflow range math, the 4-bit tag packing assumption, and concurrency around tag descriptor reuse. Test signals are ADI auxv/capability exposure, `mprotect(PROT_ADI)`, swapping tagged pages out and back in, descriptor exhaustion/failure injection, and non-ADI platform boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/adi_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/apc.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/apc.c

Purpose: Platform driver and misc-device interface for Aurora Personality Chip power-management functions on SPARCstation-4/5 derivatives.

Important APIs and control flow: `apc_setup()` parses `apc=noidle`. `apc_swift_idle()` enters CPU standby by setting `APC_IDLE_ON`. `apc_ioctl()` implements fan, convenience-power, and bit-port get/set commands using UAPI masks. `apc_probe()` maps the `power-management` OF resource, registers `/dev/apc`, and installs `sparc_idle` unless disabled. The driver registers as a platform driver at `__initcall`.

State, dependencies, and risks: state includes global mapped `regs`, `apc_no_idle`, misc-device registration, and possibly the global `sparc_idle` callback. Dependencies include OF platform resources, SBus byte I/O, APC UAPI constants, user-copy helpers, and optional AUXIO debug LED. Risks include no remove path, global singleton registers, platform-specific bit-port side effects, and idle instability on prototype systems. Test signals are `/dev/apc` ioctl read/write tests, boot with and without `apc=noidle`, idle/resume behavior, and OF match/resource mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/apc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/asm-offsets.c

Purpose: Generates C-derived constants consumed by SPARC assembly.

Important APIs and control flow: under `COMPILE_OFFSETS`, build-time functions emit `DEFINE`/`OFFSET` records for `thread_struct`, `task_struct`, `mm_struct`, `vm_area_struct`, and SPARC64 hibernation `saved_context` fields. The compiled assembler output is post-processed by Kbuild into offset headers.

State, dependencies, and risks: state is build-time metadata, not runtime state. Dependencies include scheduler/mm structure definitions, `linux/kbuild.h`, and optional hibernation structures. Risks are assembly/C layout mismatches if offsets are omitted or conditionals are wrong. Test signals are successful generation of asm-offset headers, SPARC32/SPARC64 builds, hibernation-enabled builds, and low-level assembly using the emitted symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/audit.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/audit.c

Purpose: Registers SPARC audit syscall classes and classifies native and compat syscalls.

Important APIs and control flow: static arrays include generic syscall-class lists for directory writes, reads, writes, attribute changes, and signals. `audit_classify_arch()` identifies 32-bit SPARC compat arch when enabled. `audit_classify_syscall()` routes compat syscalls to `sparc32_classify_syscall()` and classifies native open/openat/socketcall/execve/openat2 specially, defaulting to native. `audit_classes_init()` registers native and compat class arrays at init.

State, dependencies, and risks: state is audit class registry configuration. Dependencies include generated syscall numbers, generic audit include lists, `CONFIG_COMPAT`, and `kernel.h` declarations. Risks are syscall-number table drift, missed new special syscall classes, and compat arch misclassification. Test signals are audit rules for open/read/write/chattr/signal classes, 32-bit process audit under compat, and openat2/socketcall classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_32.c

Purpose: Probes and controls SPARC32 auxiliary I/O and power-control registers.

Important APIs and control flow: `auxio_probe()` skips LEON/sun4d, finds `auxiliary-io` or `obio/auxio` PROM nodes, maps the register with OBIO ranges, applies sun4m address fixup, and turns on the LED bit. `get_auxio()` returns the byte register. `set_auxio()` spinlock-protects read/modify/write on sun4m and preserves `AUXIO_ORMEIN4M`; unsupported models panic if called. `auxio_power_probe()` finds `obio/power`, maps the power register, and reports power-off control availability.

State, dependencies, and risks: global `auxio_register` is exported for assembly floppy completion, and `auxio_power_register` is a volatile mapped pointer. Dependencies include PROM traversal, OBIO range translation, SBus byte I/O, CPU model selection, and `asm/auxio.h` masks. Risks include PROM node absence halting non-PCI systems, singleton global mapping, model-specific panic path, and address alignment fixups. Test signals are sun4m boot, LED set/clear, floppy interrupt paths using `auxio_register`, poweroff register discovery, and VME chassis without auxio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_64.c

Purpose: SPARC64 platform driver for AUXIO LED and link-test enable controls on SBus/EBus systems.

Important APIs and control flow: `auxio_probe()` matches `auxio`, identifies parent bus as `ebus` or `sbus`, maps a 32-bit or 8-bit register, sets device type, and enables the EBus LED. `__auxio_rmw()` spinlock-protects register updates and uses readl/writel for EBus or SBus byte access for SBus. `auxio_set_led()` and `auxio_set_lte()` expose exported control functions; LTE only applies to SBus.

State, dependencies, and risks: state includes exported `auxio_register`, device type enum, and spinlock. Dependencies include OF platform resources, parent bus naming, `asm/auxio.h`, and platform-device ordering; `fs_initcall` ensures availability before device drivers such as floppy. Risks include singleton behavior when multiple auxio nodes exist, bus-type name assumptions, and EBus/SBus bit polarity differences. Test signals are OF auxio probe on both bus types, LED state changes, LTE no-op on EBus, and early consumers linking against exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/auxio_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/btext.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/btext.c

Purpose: Early boot framebuffer text console for PROM display devices.

Important APIs and control flow: `btext_find_display()` checks PROM stdout for `device_type = display`, initializes framebuffer geometry/address from PROM properties, clears the screen, and registers a boot console. Drawing uses `font_sun_8x16`; `btext_drawchar()` handles control characters, wraparound, and line clearing; `draw_byte_32`, `draw_byte_16`, and `draw_byte_8` expand font bits into framebuffer pixels. Scrolling code exists but is disabled by `NO_SCROLL`, so output wraps to the top.

State, dependencies, and risks: state is static console cursor, display dimensions, depth, row bytes, rectangle, and framebuffer base stored in `.data`. Dependencies include PROM properties `width`, `height`, `depth`, `linebytes`, and `address`, direct framebuffer access, console registration, and font data. Risks include only supporting PROM address property rather than PCI `reg`, no locking, unsupported depths silently drawing nothing, and wraparound erasing old lines. Test signals are early console output on display-backed PROM stdout, 8/16/32-bit framebuffer rendering, line wrap behavior, and fallback when stdout is not a display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/btext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/central.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/central.c

Purpose: Sunfire/Starfire/Wildfire central clock-board and FireHose Controller platform support, mainly registering LED child devices and normalizing FHC control state.

Important APIs and control flow: `clock_board_probe()` maps clock frequency/control/version resources, determines slot count from status/version registers, creates a `sunfire-clockboard-leds` platform device using the clock control register, and logs system slot count. `fhc_probe()` maps FHC PREGS, identifies central versus board FHC, derives board number from BSR or `board#`, detects JTAG master, optionally registers `sunfire-fhc-leds`, clears power/line control bits, sets `IXIST` for non-central boards, and logs ID fields. `sunfire_init()` registers both platform drivers at `fs_initcall`.

State, dependencies, and risks: state is per-device mapped UPA register pointers and child LED platform devices. Dependencies include OF resources/names, UPA byte/word accessors, `asm/fhc.h`, and platform device registration. Risks include resource-count assumptions, no remove path for child devices, board-number heuristics, and register writes affecting chassis LEDs/power lines. Test signals are Sunfire boot logs, LED child device creation, slot-count detection, and FHC control register state after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/central.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cherrs.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/cherrs.S

Purpose: UltraSPARC Cheetah/Cheetah+ low-level trap vectors and handlers for fast ECC, correctable ECC, deferred errors, and instruction/data cache parity errors.

Important APIs and control flow: boot-time patched vectors disable relevant caches in the DCU and branch to C handlers or assembly logging paths. Cheetah+ parity vectors enter trap frames and call `cheetah_plus_parity_error`; TL1 variants check whether interrupt globals are already in use, repair cache parity by clearing D-cache or I-cache tags/data when recoverable, or call fatal paths when not. `__cheetah_log_error` stamps TL1 into AFSR, indexes `cheetah_error_log` by CPU and trap level, stores AFSR/AFAR, captures matching D-cache, I-cache, and E-cache diagnostic state via ASIs, then dispatches to the correct C handler (`cheetah_fecc_handler`, `cheetah_cee_handler`, or `cheetah_deferred_handler`) through normal trap entry.

State, dependencies, and risks: state includes DCU control, ESTATE error-enable, AFSR/AFAR, cache diagnostic arrays, TL/PIL/PSTATE, `dcache_parity_tl1_occurred`, `icache_parity_tl1_occurred`, and `cheetah_error_log`. Dependencies include SPARC64 trap entry/return labels, ASI constants, cache sizes/line sizes, Cheetah/Jalapeno configuration ASIs, and C handlers. Risks are extreme: register clobbering, recursive errors if reporting is not disabled, cache corruption during logging, wrong CPU log indexing, and unrecoverable TL1 interrupt-global conflicts. Test signals are mostly hardware/error-injection: ECC/parity trap handling, cache re-enable/retry, error log population, `/proc/cpuinfo` parity counters, and boot on Cheetah/Jalapeno variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cherrs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/chmc.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/chmc.c

Purpose: UltraSPARC-III memory-controller driver that maps physical ECC syndrome addresses to DIMM labels/pins and registers a DIMM printer for memory error reporting.

Important APIs and control flow: the driver supports Safari CHMC and Jalapeno/Serrano JBUS controllers. It stores controllers in `mctrl_list`, converts syndrome codes to bus bit positions, and uses OBP `memory-layout` dimm/pin maps to build printable DIMM strings. JBUS probing reads `/memory` ranges, controller `portid`, `memory-control-register-1`, maps registers, copies layout, constructs DIMM groups, and registers the controller. Safari probing skips Jalapeno/Serrano, reads `portid`, layout, maps controller registers, reads timing/address-control/decode registers through same-CPU ASI or bypass ASI, interprets bank masks/interleave/size, and registers the controller. `us3mc_init()` chooses controller type by CPU version, registers the proper DIMM printer, and registers the platform driver.

State, dependencies, and risks: global state includes `mc_type`, selected `us3mc_dimm_printer`, and spinlock-protected `mctrl_list`. Per-controller state includes mapped registers, layout properties, decode registers, logical banks or DIMM groups. Dependencies include OF memory-controller and memory nodes, OBP memory-layout encoding, ASI_MCU_CTRL_REG/ASI_PHYS_BYPASS_EC_E, CPU version/tlb type, and `register_dimm_printer`. Risks include firmware property format drift, list traversal without holding the lock in lookup paths, physical-address decode math errors, resource leaks on some error paths, and disabled support outside Cheetah/Cheetah+. Test signals are module load/unload, memory-controller probe logs, ECC error reports naming expected DIMMs/pins, JBUS/Safari platform coverage, and malformed/missing OF property failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/chmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/compat_audit.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/compat_audit.c

Purpose: Provides 32-bit SPARC syscall audit classes and syscall classification for compat tasks on SPARC64.

Important APIs and control flow: forces `__32bit_syscall_numbers__` before including syscall numbers, builds exported class arrays from generic audit include fragments, and classifies 32-bit `open`, `openat`, `socketcall`, `execve`, and `openat2` specially while returning `AUDITSC_COMPAT` for all others.

State, dependencies, and risks: state is audit class data used by the native audit initializer. Dependencies include 32-bit syscall-number generation, `linux/audit_arch.h`, generic audit fragments, and declarations in `kernel.h`. Risks are syscall-number mismatch if the 32-bit define is omitted, stale special-case coverage, and class arrays not matching native registrations. Test signals are 32-bit compat audit rules and syscall classification for open/socket/exec paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/compat_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpu.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/cpu.c

Purpose: Detects SPARC CPU/FPU/PMU identity and exposes `/proc/cpuinfo` data.

Important APIs and control flow: `manufacturer_info` tables map PSR or V9 version implementation values to CPU/FPU/PMU names. `set_cpu_and_fpu()` selects names and logs unknown implementations. `show_cpuinfo()` prints CPU, FPU, PROM, platform type, probed/online CPU counts, optional clocks, MMU/SMP/capability data, and SPARC64 parity TL1 counters. SPARC32 `cpu_type_probe()` reads PSR/FSR with temporary FPU enablement. SPARC64 `cpu_type_probe()` either maps `sun4v_chip_type` through `sun4v_cpu_probe()` or reads `%ver` for sun4u-style systems. The probe runs as an early initcall.

State, dependencies, and risks: exported per-CPU `__cpu_data`, `ncpus_probed`, `fsr_storage`, CPU/FPU/PMU name pointers, and SPARC64 parity counters persist globally. Dependencies include PROM data, PSR/FSR or `%ver`, `tlb_type`, `sun4v_chip_type`, SMP/MMU info helpers, and seq_file. Risks include incomplete CPU tables, FPU probing side effects, unknown PMU names reducing perf integration, and proc output ABI expectations. Test signals are `/proc/cpuinfo` on SPARC32, sun4u, and sun4v, unknown CPU fallback logs, FPU version detection, and parity counter updates after Cheetah+ traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.c

Purpose: Builds a topology-aware CPU distribution map for SPARC SMP work placement.

Important APIs and control flow: CPU topology is modeled as root, NUMA node, core, and proc/strand levels using `cpu_data(cpu).core_id`, `proc_id`, and `cpu_to_node()`. `enumerate_cpuinfo_nodes()` counts sorted online topology nodes. `build_cpuinfo_tree()` allocates a flexible tree and links parent/child ranges. `iterate_cpu()` walks rovers with Niagara-optimized or generic increment policies; Niagara spreads work across cores/pipelines before sibling strands. `_cpu_map_rebuild()` rebuilds the tree and fills `cpu_distribution_map`. `map_to_cpu()` spinlock-protects lookups, rebuilds on hotplug count mismatch, and falls back to linear online mapping if allocation fails.

State, dependencies, and risks: state includes global `cpuinfo_tree`, `cpu_distribution_map`, and `cpu_map_lock`. Dependencies include per-CPU topology fields, online/possible CPU masks, `sun4v_chip_type`, GFP_ATOMIC allocation, and optional CPU hotplug. Risks include assumptions that online CPU data is sorted by node/core/proc, `simple_map_to_cpu()` edge-case behavior, stale tree during hotplug, and allocation failure reducing placement quality. Test signals are map distribution on Niagara/T-series systems, CPU hotplug rebuilds, offline CPU avoidance, allocation-failure fallback, and exported `map_to_cpu()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.h

Purpose: Local header for SPARC CPU distribution mapping.

Important APIs and control flow: under `CONFIG_SMP`, declares `cpu_map_rebuild()` and `map_to_cpu()` and maps `cpu_map_init()` to rebuild. Without SMP, `cpu_map_init()` is a no-op and `map_to_cpu()` returns `raw_smp_processor_id()`.

State, dependencies, and risks: SMP state is owned by `cpumap.c`; non-SMP has no extra state. Dependencies include `CONFIG_SMP` and raw CPU-id helpers. Risks are callers assuming `map_to_cpu()` can select arbitrary CPUs on UP builds and missing rebuild calls after topology changes. Test signals are compile coverage for SMP and UP builds and exported mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/devices.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/devices.c

Purpose: Early SPARC32 PROM device scan helpers for CPU node lookup and AUXIO/power discovery.

Important APIs and control flow: `cpu_mid_prop()` selects `cpu-id` on sun4d and `mid` otherwise. `__cpu_find_by()` iterates OF CPU nodes with comparison callbacks; `cpu_find_by_instance()` and `cpu_find_by_mid()` expose instance/MID searches, with sun4m MID truncation compatibility. `cpu_get_hwmid()` returns the full hardware MID. `device_scan()` prints the boot banner, initializes CPU0 clock tick on non-SMP by reading the first CPU node, then probes AUXIO and AUXIO power control.

State, dependencies, and risks: state updated includes `cpu_data(0).clock_tick` and global AUXIO mappings through called probes. Dependencies include PROM/OF CPU nodes, CPU model, `auxio_probe()`, `auxio_power_probe()`, and SMP conditionals. Risks include halting if no CPU node on non-SMP, sun4m MID truncation ambiguity, and relying on PROM property names. Test signals are boot on sun4m/sun4d, CPU instance/MID lookup for SMP bring-up, CPU clock reporting, and AUXIO/power probe side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/devices.c -->
