<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/perf/arm_pmuv3.h -->
# sources/distributed-fs/ceph-client/tools/include/perf/arm_pmuv3.h

## Purpose
Defines the ARMv8 PMUv3 event-number and register-bit vocabulary used by perf tooling when decoding or programming Arm performance-monitoring counters. It is a tools-side mirror of kernel PMU definitions, not an implementation of counter access.

## Important APIs, Types, and Functions
Exports constants for architectural PMUv3 events, SPE events, AMU events, implementation-defined cache/TLB/bus/speculation events, PMCR, PMOVSR, PMXEVTYPER, event filters, PMUSERENR, PMMIR fields, and `ARMV8_PMU_MAX_COUNTERS`. Helper macros `PMEVN_CASE()` and `PMEVN_SWITCH()` let callers generate a switch over event counter indexes 0 through 30.

## Control Flow, State, and Persistence
There is no runtime state or persistence. The only executable behavior is macro expansion: `PMEVN_SWITCH(x, case_macro)` dispatches to `case_macro(n)` for valid programmable counter numbers and otherwise emits `WARN(1, ...)` then `assert(0)`.

## Dependencies and Integration
Depends on `<assert.h>` and `<asm/bug.h>` for invalid-index handling plus `BIT()`/`GENMASK()` style kernel macros supplied through included tooling headers. It integrates with perf/arm64 PMU support and any decoder that must keep event ids aligned with the Arm architecture.

## Risks and Test Signals
Risks are ABI/spec drift, missing counters above 30 because the cycle counter is separate, and invalid assumptions if future Arm PMU revisions add fields not represented here. Test signals include compile checks for macro availability, perf event encoding tests on Arm systems, and invalid-index tests around `PMEVN_SWITCH()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/perf/arm_pmuv3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/be_byteshift.h -->
# sources/distributed-fs/ceph-client/tools/include/tools/be_byteshift.h

## Purpose
Provides unaligned big-endian load/store helpers for 16-, 32-, and 64-bit integers in user-space tools that cannot rely on direct unaligned typed memory access.

## Important APIs, Types, and Functions
Defines internal byte-pointer helpers `__get_unaligned_be16/32/64()` and `__put_unaligned_be16/32/64()`, plus public `void *` wrappers `get_unaligned_be16/32/64()` and `put_unaligned_be16/32/64()`.

## Control Flow, State, and Persistence
All helpers are `static inline` and deterministic. Reads assemble values with shifts from `uint8_t` bytes in network/big-endian order; writes decompose high-order bytes first. No state is stored.

## Dependencies and Integration
Depends only on `<stdint.h>`. It integrates with binary parsers, perf data readers, BPF tooling, and protocol/file-format code that needs endian-stable unaligned access.

## Risks and Test Signals
Risks include passing too-short buffers, relying on integer promotion without preserving unsigned byte semantics, and confusing these helpers with host-endian conversion. Useful tests round-trip known byte arrays such as `01 02 03 04`, exercise unaligned offsets, and compare against `htobe*`/`be*toh` expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/be_byteshift.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/config.h -->
# sources/distributed-fs/ceph-client/tools/include/tools/config.h

## Purpose
Supplies a small tools-side subset of kernel Kconfig expression helpers so C and preprocessor code can test boolean/tristate-style `CONFIG_*` defines safely.

## Important APIs, Types, and Functions
Exports `IS_BUILTIN(option)` via the internal placeholder chain `__is_defined()`, `___is_defined()`, `____is_defined()`, `__ARG_PLACEHOLDER_1`, and `__take_second_arg()`.

## Control Flow, State, and Persistence
There is no runtime behavior. Macro expansion turns a symbol defined as `1` into `1` and an undefined or nonmatching token into `0`, enabling use in `#if` and C expressions.

## Dependencies and Integration
No external includes. It integrates with perf and other Linux tools that compile outside the kernel build but still consume generated or manually supplied `CONFIG_*` symbols.

## Risks and Test Signals
Risks include assuming support for module `m` values beyond the limited helper, passing expressions rather than simple config tokens, or redefining placeholder macros. Test signals are preprocessor tests for defined `CONFIG_FOO 1`, undefined symbols, and use in both `#if` and ordinary C expressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/dis-asm-compat.h -->
# sources/distributed-fs/ceph-client/tools/include/tools/dis-asm-compat.h

## Purpose
Hides binutils `dis-asm.h` API differences so tools can initialize disassembler state across older and newer libopcodes versions.

## Important APIs, Types, and Functions
Provides fallback `enum disassembler_style` and `fprintf_styled_ftype` when `DISASM_INIT_STYLED` is absent. Defines `fprintf_styled()` as a varargs adapter around `vfprintf()` and `init_disassemble_info_compat()` as the compatibility wrapper for `init_disassemble_info()`.

## Control Flow, State, and Persistence
`fprintf_styled()` ignores style and forwards formatted output to the supplied stream. `init_disassemble_info_compat()` chooses the four-argument or three-argument binutils initializer at compile time. No state is retained by this header itself.

## Dependencies and Integration
Depends on `<stdio.h>` and `<dis-asm.h>`. It integrates with perf disassembly and annotation code that must build against multiple distro binutils releases.

## Risks and Test Signals
Risks include missing `<stdarg.h>` through transitive includes, ABI changes in libopcodes, and losing styled output on old binutils. Test signals are build matrix coverage against old/new binutils and smoke disassembly that verifies output callbacks are invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/dis-asm-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/endian.h -->
# sources/distributed-fs/ceph-client/tools/include/tools/endian.h

## Purpose
Defines little-endian host conversion macros for tools when system headers do not already provide `htole*` and `le*toh`.

## Important APIs, Types, and Functions
Exports fallback `htole16/32/64` and `le16toh/le32toh/le64toh`. On little-endian hosts these are identity macros; on other hosts they map to `__bswap_16/32/64`.

## Control Flow, State, and Persistence
All behavior is compile-time conditional on `__BYTE_ORDER == __LITTLE_ENDIAN`. There is no runtime state.

## Dependencies and Integration
Depends on `<byteswap.h>` and libc byte-order macros. It integrates with tools reading Linux binary formats that are explicitly little-endian.

## Risks and Test Signals
Risks include relying on libc-specific `__BYTE_ORDER` names, macro double evaluation if arguments have side effects, and missing big-endian build coverage. Test signals are compile checks on little- and big-endian targets and known-value conversion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/le_byteshift.h -->
# sources/distributed-fs/ceph-client/tools/include/tools/le_byteshift.h

## Purpose
Provides unaligned little-endian load/store helpers for 16-, 32-, and 64-bit integers in tools code.

## Important APIs, Types, and Functions
Defines `__get_unaligned_le16/32/64()`, `__put_unaligned_le16/32/64()`, and public wrappers `get_unaligned_le16/32/64()` and `put_unaligned_le16/32/64()`.

## Control Flow, State, and Persistence
Reads combine lower-address bytes as low-order bits; writes emit low-order bytes first. The 64-bit helpers compose two 32-bit operations. There is no state or persistence.

## Dependencies and Integration
Depends only on `<stdint.h>`. It integrates with perf data, ELF-related tooling, and other Linux tools that parse packed little-endian structures on hosts where direct unaligned access may trap or violate aliasing.

## Risks and Test Signals
Risks include buffer length errors, side-effect assumptions around inline wrappers, and accidental use for host-endian data. Test signals include round-trip arrays, unaligned addresses, 64-bit split-boundary cases, and comparison with `htole*`/`le*toh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/le_byteshift.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/libc_compat.h -->
# sources/distributed-fs/ceph-client/tools/include/tools/libc_compat.h

## Purpose
Provides libc compatibility shims for tool builds on platforms missing newer libc APIs.

## Important APIs, Types, and Functions
Conditionally defines `reallocarray(void *ptr, size_t nmemb, size_t size)` when `COMPAT_NEED_REALLOCARRAY` is set. The function uses `check_mul_overflow()` before calling `realloc()`.

## Control Flow, State, and Persistence
The shim computes `nmemb * size`, returns `NULL` on overflow, and otherwise delegates to `realloc()`. It keeps no state; allocation state is owned by libc.

## Dependencies and Integration
Depends on `<stdlib.h>` and `<linux/overflow.h>`, including `unlikely()` and overflow helpers. It integrates with BPF/perf tools that want `reallocarray()` semantics without requiring a specific libc baseline.

## Risks and Test Signals
Risks include relying on `errno` behavior not explicitly set on overflow, name collision if libc already declares `reallocarray()`, and allocator semantics for zero-sized requests. Test signals include overflow cases near `SIZE_MAX`, successful growth preserving contents, and builds with and without `COMPAT_NEED_REALLOCARRAY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/tools/libc_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/trace/events/lock.h -->
# sources/distributed-fs/ceph-client/tools/include/trace/events/lock.h

## Purpose
Acts as a tools-side placeholder for the kernel trace event header path `trace/events/lock.h`.

## Important APIs, Types, and Functions
Exports no APIs, tracepoint declarations, types, or functions. It only provides the include guard `_TOOLS_INCLUDE_TRACE_EVENTS_LOCK_H`.

## Control Flow, State, and Persistence
No executable logic, state, or persistence exists.

## Dependencies and Integration
Has no includes. Its integration role is build compatibility: code that includes lock trace-event headers can compile in the tools environment without pulling kernel-only tracepoint machinery.

## Risks and Test Signals
The primary risk is silent feature absence if a tools consumer expects actual lock trace event definitions. Test signals are compile-only: any code requiring real lock event fields should fail elsewhere rather than depend on this stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/trace/events/lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/bitsperlong.h

## Purpose
Defines generic UAPI word-size constants for user-space header consumers.

## Important APIs, Types, and Functions
Exports `__BITS_PER_LONG`, derived from `__CHAR_BIT__ * __SIZEOF_LONG__` when available and otherwise defaulting to 32, plus `__BITS_PER_LONG_LONG` fixed at 64.

## Control Flow, State, and Persistence
All behavior is preprocessor-only. Architecture-specific headers may define `__BITS_PER_LONG` before inclusion to override the generic fallback.

## Dependencies and Integration
No includes. It integrates with UAPI bitmask, socket, ioctl, and syscall headers that need to vary constants by userspace ABI width.

## Risks and Test Signals
Risks include defaulting to 32 for older toolchains on 64-bit ABIs unless arch headers override it, and confusing kernel `CONFIG_64BIT` with userspace long size. Test signals include compile probes for 32-bit, 64-bit, and x32-style environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/bpf_perf_event.h

## Purpose
Defines the generic BPF perf-event register context type for architectures that do not provide a specialized tools UAPI header.

## Important APIs, Types, and Functions
Includes `<linux/ptrace.h>` and typedefs `struct pt_regs` as `bpf_user_pt_regs_t`.

## Control Flow, State, and Persistence
No runtime behavior exists. The typedef binds BPF/perf helper interfaces to the architecture's `pt_regs` layout.

## Dependencies and Integration
Depends on `linux/ptrace.h` for `struct pt_regs`. It integrates with BPF programs and perf tooling that inspect sampled register state.

## Risks and Test Signals
Risks include architecture-specific `pt_regs` mismatch and include-path ordering selecting generic definitions when an arch override is required. Test signals are BPF/perf sample builds and register-field access checks on each target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno-base.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno-base.h

## Purpose
Defines the base POSIX/Linux errno values 1 through 34 for generic UAPI consumers.

## Important APIs, Types, and Functions
Exports constants such as `EPERM`, `ENOENT`, `EINTR`, `EIO`, `EAGAIN`, `ENOMEM`, `EACCES`, `EINVAL`, `ENOSPC`, `EPIPE`, `EDOM`, and `ERANGE`.

## Control Flow, State, and Persistence
This is a pure constant header with no runtime behavior or state.

## Dependencies and Integration
No includes. It is included by `asm-generic/errno.h` and by architecture errno wrappers that use generic Linux errno numbering.

## Risks and Test Signals
Risks are ABI breakage if numeric values change and collisions with libc errno definitions when include ordering is wrong. Test signals include preprocessing alongside libc headers and asserting key errno numeric values against Linux UAPI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno.h

## Purpose
Extends base errno definitions with Linux-specific generic error numbers through `EHWPOISON`.

## Important APIs, Types, and Functions
Includes `asm-generic/errno-base.h` and defines errors such as `ENOSYS`, `EWOULDBLOCK`, socket/network errors, filesystem errors, key errors, robust mutex errors, `ERFKILL`, and aliases including `EDEADLOCK`, `EFSBADCRC`, and `EFSCORRUPTED`.

## Control Flow, State, and Persistence
No runtime logic. The comments around `ENOSYS` document syscall ABI behavior: nonexistent syscalls return `-ENOSYS`, so real syscall implementations should avoid using it for ordinary failures.

## Dependencies and Integration
Depends on the base errno header. It integrates with syscall wrappers, tools, and architecture wrappers that need Linux error-number constants independent of host libc drift.

## Risks and Test Signals
Risks include arch-specific errno values being different for some targets, alias expectations changing, and duplicate definitions with system headers. Test signals are compile tests through `uapi/asm/errno.h` on arch-specific include paths and numeric checks for common errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/ioctls.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/ioctls.h

## Purpose
Provides generic tty, pty, serial, and file ioctl command numbers for UAPI consumers.

## Important APIs, Types, and Functions
Includes `<linux/ioctl.h>` and defines `TCGETS`, `TCSETS*`, `TIOC*`, `FION*`, RS485 and ISO7816 ioctls, packet-mode flags `TIOCPKT_*`, and `TIOCSER_TEMT`. Some commands use `_IO`, `_IOR`, `_IOW`, or `_IOWR` with structures such as `termios2` and `serial_iso7816`.

## Control Flow, State, and Persistence
No runtime behavior. Conditional guards preserve architecture or libc-provided `TIOCSRS485` and `FIOQSIZE`.

## Dependencies and Integration
Depends on Linux ioctl encoding macros and externally declared ioctl payload structs. It integrates with terminal, pty, serial, and console tooling.

## Risks and Test Signals
Risks are ABI value drift, missing payload struct declarations at include sites, and architecture exceptions with historical ioctl values. Test signals include compile tests with termios headers and runtime smoke tests issuing harmless tty ioctls on pseudo-terminals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman-common-tools.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman-common-tools.h

## Purpose
Restores common mmap type flags for tools builds whose local UAPI include path shadows system headers after those flags moved to `linux/mman.h`.

## Important APIs, Types, and Functions
Includes `asm-generic/mman-common.h` and conditionally defines `MAP_SHARED`, `MAP_PRIVATE`, and `MAP_SHARED_VALIDATE` if `MAP_SHARED` is absent.

## Control Flow, State, and Persistence
Preprocessor-only compatibility behavior. No runtime state.

## Dependencies and Integration
Depends on the generic mmap common header and is included by per-architecture `mman.h` wrappers in the tools tree. It integrates with perf and related tools that include both system `sys/mman.h` and tools UAPI headers.

## Risks and Test Signals
Risks include masking inconsistencies with newer system headers and incomplete recovery if only one of the three macros is missing. Test signals are builds with tools UAPI first in the include path and compile checks using `MAP_SHARED`, `MAP_PRIVATE`, and `MAP_SHARED_VALIDATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman-common-tools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman-common.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman-common.h

## Purpose
Defines common memory-protection, mapping, locking, sync, `madvise()`, and protection-key constants shared by generic Linux UAPI architectures.

## Important APIs, Types, and Functions
Exports `PROT_*`, `MAP_TYPE`, `MAP_FIXED`, `MAP_ANONYMOUS`, `MAP_POPULATE`, `MAP_HUGETLB`, `MAP_SYNC`, `MAP_FIXED_NOREPLACE`, `MLOCK_ONFAULT`, `MS_*`, `MADV_*`, `MAP_FILE`, and `PKEY_*` constants.

## Control Flow, State, and Persistence
No runtime logic. Constants directly encode syscall flag values consumed by `mmap()`, `mprotect()`, `msync()`, `madvise()`, `mlock*()`, and pkey APIs.

## Dependencies and Integration
No includes. It is included by `mman-common-tools.h` and generic/arch `mman.h` headers, integrating with memory-management syscall callers and tools that inspect mmap flags.

## Risks and Test Signals
Risks include flag-value ABI drift, reserved arch-specific bit conflicts, and tools using flags unavailable on the running kernel. Test signals include compile-time numeric assertions and syscall smoke tests expecting `EINVAL` or success according to kernel support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman.h

## Purpose
Adds generic architecture mmap and mlock constants on top of common mmap definitions.

## Important APIs, Types, and Functions
Includes `asm-generic/mman-common-tools.h` and defines `MAP_GROWSDOWN`, `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_LOCKED`, `MAP_NORESERVE`, `MCL_CURRENT`, `MCL_FUTURE`, `MCL_ONFAULT`, and shadow-stack setup flags `SHADOW_STACK_SET_TOKEN` and `SHADOW_STACK_SET_MARKER`.

## Control Flow, State, and Persistence
Pure macro constants. No state or runtime behavior exists.

## Dependencies and Integration
Depends on the tools mmap-common wrapper. It integrates with syscall wrappers and tools that compile against generic architecture memory-management flags.

## Risks and Test Signals
Risks include architecture-specific deviations, collision with hugetlb-encoded bits in the reserved high range, and consumers assuming shadow-stack flags are supported by all kernels. Test signals are compile checks and targeted `mmap()`/`mlockall()`/shadow-stack syscall probes where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/socket.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/socket.h

## Purpose
Defines generic Linux `SOL_SOCKET` option numbers and control-message aliases for user-space socket consumers.

## Important APIs, Types, and Functions
Includes `<linux/posix_types.h>` and `<asm/sockios.h>`. Exports `SO_*` options from legacy options through newer BPF, zerocopy, timestamp, busy-poll, netns-cookie, pidfd, devmem, and rights-passing options. Defines timestamp/timeo old/new selector macros based on `__BITS_PER_LONG`, x32, `time_t`, and `__kernel_long_t`, then maps `SCM_TIMESTAMP*`.

## Control Flow, State, and Persistence
No runtime code. Conditional macro selection handles ABI differences for 32-bit time64 transitions and keeps powerpc overrides for credential/low-water options.

## Dependencies and Integration
Depends on socket ioctl and kernel type headers plus `__BITS_PER_LONG`. It integrates with networking tools, BPF socket options, timestamping users, and code that sends or receives ancillary data.

## Risks and Test Signals
Risks include selecting wrong old/new timestamp option on unusual ABIs, arch overrides hidden by include order, and using option numbers unsupported by the running kernel. Test signals include compile probes for 32-bit, 64-bit, and x32 and runtime `getsockopt()`/`setsockopt()` checks for representative options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/unistd.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/unistd.h

## Purpose
Defines the generic Linux syscall-number table and macro expansion hooks used by architectures that follow the generic syscall ABI layout.

## Important APIs, Types, and Functions
Includes `<asm/bitsperlong.h>`. Defines `__SYSCALL` default hook, selection helpers `__SC_3264`, `__SC_COMP`, and `__SC_COMP_3264`, hundreds of `__NR_*` syscall numbers from `io_setup` through `rseq_slice_yield`, `__NR_arch_specific_syscall`, `__NR_syscalls 472`, and 32/64-bit alias mappings such as `__NR_fcntl` versus `__NR_fcntl64`.

## Control Flow, State, and Persistence
This header has no executable runtime flow, but its preprocessor control flow is central: `__BITS_PER_LONG`, `__SYSCALL_COMPAT`, `__ARCH_WANT_*`, and `__ARCH_NOMMU` select time32/time64, compat, legacy, MMU-only, and architecture-reserved syscall entries.

## Dependencies and Integration
Depends on arch word-size definitions and on includers optionally redefining `__SYSCALL` to generate tables. It integrates with libc syscall numbers, seccomp/BPF tooling, syscall tracers, audit/perf decoders, and kernel syscall table generation.

## Risks and Test Signals
Risks are severe ABI breakage if numbers or aliases change, stale `__NR_syscalls`, incorrect time64 exposure on 32-bit ABIs, and accidental use of generic numbers on an architecture with overrides. Test signals include generated table diffs against kernel headers, seccomp compile tests, syscall smoke tests for selected numbers, and preprocessing under 32-bit, 64-bit, compat, and NOMMU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm/bitsperlong.h

## Purpose
Selects the correct architecture-specific `bitsperlong.h` for tools builds, falling back to the generic definition when no specialized architecture branch matches.

## Important APIs, Types, and Functions
Uses preprocessor architecture tests for x86, powerpc, s390, sparc, mips, ia64, and alpha, then includes the matching `arch/*/include/uapi/asm/bitsperlong.h`; otherwise includes `<asm-generic/bitsperlong.h>`.

## Control Flow, State, and Persistence
Preprocessor include routing only. No runtime state exists.

## Dependencies and Integration
Depends on relative paths into the source tree and compiler-defined architecture macros. It integrates with generic UAPI headers that include `<asm/bitsperlong.h>` from the tools include path.

## Risks and Test Signals
Risks include broken relative include paths after tree moves, missing architecture branches, and host-vs-target confusion during cross-compilation. Test signals are preprocessing checks for each supported architecture macro and fallback builds for generic targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm/bpf_perf_event.h

## Purpose
Routes BPF perf-event UAPI includes to architecture-specific register-context definitions when available, otherwise to the generic fallback.

## Important APIs, Types, and Functions
Branches on `__aarch64__`, `__arc__`, `__s390__`, `__riscv`, and `__loongarch__`, including the corresponding `arch/*/include/uapi/asm/bpf_perf_event.h`; otherwise includes `<uapi/asm-generic/bpf_perf_event.h>`.

## Control Flow, State, and Persistence
Preprocessor include selection only. No runtime behavior or persistent state exists.

## Dependencies and Integration
Depends on compiler target macros and relative arch header paths. It integrates with BPF/perf sample code that needs the correct `bpf_user_pt_regs_t` for the build target.

## Risks and Test Signals
Risks include incomplete arch coverage, misspelled target macros, and generic fallback hiding a target-specific register layout need. Test signals are arch matrix preprocessing and BPF program builds that access expected register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/asm/errno.h

## Purpose
Routes errno definitions to architecture-specific UAPI headers where Linux errno numbering differs, with generic errno as the default.

## Important APIs, Types, and Functions
Branches for x86, powerpc, sparc, alpha, mips, and hppa/parisc, including the matching arch errno header; otherwise includes `<asm-generic/errno.h>`.

## Control Flow, State, and Persistence
Preprocessor routing only. No runtime state.

## Dependencies and Integration
Depends on compiler architecture macros and relative source-tree arch headers. It integrates with tools that need target Linux errno values rather than host libc values.

## Risks and Test Signals
Risks include cross-compilation selecting the build host arch, missing arch-specific mappings, and duplicate definitions with libc headers. Test signals include preprocessing under each supported arch macro and numeric checks for errno values known to differ by architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/bits.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bits.h

## Purpose
Provides low-level UAPI bitmask construction macros for unsigned long, unsigned long long, and optional 128-bit masks.

## Important APIs, Types, and Functions
Defines `__GENMASK(h, l)`, `__GENMASK_ULL(h, l)`, and `__GENMASK_U128(h, l)`. These depend on `_UL()`, `_ULL()`, `_BIT128()`, `__BITS_PER_LONG`, and `__BITS_PER_LONG_LONG` from surrounding UAPI includes.

## Control Flow, State, and Persistence
All behavior is macro arithmetic. The macros form masks by shifting all-ones values or subtracting a low-bit marker from one-past-high for 128-bit masks. There is no state.

## Dependencies and Integration
This header assumes foundational type-width macros are already available. It integrates with UAPI headers that need compile-time masks but cannot include full kernel internals.

## Risks and Test Signals
Risks include undefined behavior for invalid ranges or shifts at/above type width, missing `_UL`/`_ULL` definitions at include sites, and 128-bit support dependence. Test signals are compile-time assertions for boundary masks and negative tests for invalid high/low inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/bits.h -->
