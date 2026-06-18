# subset-b-006577 Research

Grouped research for the Ceph-client `tools/include` Linux helper and nolibc header set. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/types.h

## Purpose
Supplies a small userspace-compatible subset of Linux kernel type definitions for tools built from the Ceph-client kernel tree. It lets tools include kernel-style headers without pulling in the full in-kernel type system.

## APIs, Types, and Functions
Defines forward declarations for `struct page` and `struct kmem_cache`, `gfp_t` flag categories, fixed-width aliases `u64/s64/u32/s32/u16/s16/u8/s8`, bitwise-endian aliases `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`, checksum types, `phys_addr_t`, `atomic_t`, `refcount_t`, and simple `list_head`, `hlist_head`, and `hlist_node` containers. Sparse annotations such as `__bitwise`, `__force`, `__user`, `__must_check`, and `__cold` are reduced for tools builds.

## Control Flow, State, and Persistence
There is no executable control flow. State is purely compile-time type layout and annotation state that downstream tools code relies on when compiling kernel-derived helpers. `phys_addr_t` changes width based on `CONFIG_PHYS_ADDR_T_64BIT`, so persisted binary layouts that embed it are configuration-sensitive.

## Dependencies and Integration
Depends on UAPI Linux type headers, C99 integer types, and optional sparse `__CHECKER__` behavior. Integration points are kernel tool headers under `tools/include/linux`, perf/libbpf-style userspace helpers, list/hlist consumers, and any code that expects kernel endian/checksum type spelling.

## Risks and Test Signals
Risks include ABI mismatch with real kernel headers, accidental use of these reduced definitions in contexts that need true kernel-only semantics, and config-dependent `phys_addr_t` width. Test signals are building all tools against this header, sparse builds for bitwise annotations, 32-bit and 64-bit compile coverage, and static checks that list/hlist layout matches tool expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/unaligned.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/unaligned.h

## Purpose
Implements endian-aware unaligned load/store helpers for tool code that parses binary kernel, filesystem, network, or tracing data without assuming pointer alignment.

## APIs, Types, and Functions
The public macros are `get_unaligned()` and `put_unaligned()`. Inline helpers cover little-endian and big-endian 16/32/64-bit access, 24-bit access in both byte orders, big-endian 48-bit put/get, and private byte assembly helpers such as `__get_unaligned_be24()` and `__put_unaligned_le24()`.

## Control Flow, State, and Persistence
Control flow is straight-line byte loading, shifting, endian conversion, and byte storing. The helpers mutate only the caller-provided memory for put operations and retain no state. Reads are deterministic for the bytes at the supplied address and do not perform bounds checks.

## Dependencies and Integration
Depends on `linux/types.h`, `asm/byteorder.h`, and `linux/unaligned/packed_struct.h` for CPU-endian unaligned access primitives. It integrates with tools that decode packed structures where direct typed dereference may fault or violate strict alignment.

## Risks and Test Signals
Risks are caller-provided buffer underruns/overruns, wrong endian helper selection, and assuming 24/48-bit helpers sign-extend. Test signals are byte-pattern round trips for all widths and endian modes, unaligned addresses at every alignment offset, UBSan/ASan runs for parser callers, and cross-endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/unaligned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/unaligned/packed_struct.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/unaligned/packed_struct.h

## Purpose
Provides the low-level CPU-endian unaligned access backend used by `linux/unaligned.h`, using packed wrapper structs to express potentially unaligned typed memory.

## APIs, Types, and Functions
Defines packed wrappers `struct __una_u16`, `struct __una_u32`, and `struct __una_u64`, plus `__get_unaligned_cpu16/32/64()` and `__put_unaligned_cpu16/32/64()` inline helpers.

## Control Flow, State, and Persistence
Each getter casts the address to a packed wrapper pointer and returns the member; each setter assigns through the packed wrapper. There is no retained state and no branchy control flow. The behavior relies on compiler support for packed member access lowering to safe byte-wise or unaligned-capable loads/stores.

## Dependencies and Integration
Depends on kernel-style `u16/u32/u64` aliases and the `__packed` attribute from `linux/compiler.h`. It is intentionally private to the unaligned helper layer and not a general structure-serialization API.

## Risks and Test Signals
Risks are compiler or architecture behavior around packed unaligned access, strict-aliasing surprises if used outside its intended wrapper pattern, and caller buffer size mistakes. Test signals are generated assembly inspection on strict-alignment architectures, round-trip tests for 16/32/64-bit values at misaligned addresses, and sanitizer-backed parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/unaligned/packed_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/zalloc.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/zalloc.h

## Purpose
Declares small allocation helpers for Linux tools code: zeroed allocation and freeing-with-nullification.

## APIs, Types, and Functions
Declares `void *zalloc(size_t size)`, `void __zfree(void **ptr)`, and macro `zfree(ptr)` that casts the address of a typed pointer to `void **` before calling `__zfree()`.

## Control Flow, State, and Persistence
This header contains declarations only. Runtime behavior is supplied by the corresponding tools library implementation: allocate zero-filled memory, free memory, and clear the caller's pointer. Persistent state is limited to heap ownership in callers.

## Dependencies and Integration
Depends on `<stdlib.h>` for `size_t` and normal C allocation semantics. It integrates with tools code that follows kernel-style `kzalloc`/`kfree` patterns while running in userspace.

## Risks and Test Signals
Risks are passing non-pointer lvalues to `zfree`, double-free if aliases still exist, and assuming allocation failure is impossible. Test signals are allocation/failure paths in tool unit tests, pointer-nullification checks, leak detection, and ASan coverage for caller ownership mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/zalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/Makefile -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/Makefile

## Purpose
Builds and exports nolibc headers as a standalone tools include component. It supports installing the header set, producing a combined `nolibc.h`, and validating architecture-specific compiler flags.

## APIs, Types, and Functions
Important variables are `srctree`, `ARCH`, `OUTPUT`, `architectures`, `arch_files`, `all_files`, and per-architecture `CFLAGS_*`. Targets include `all`, `headers`, `headers_standalone`, `headers_install`, `clean`, and generated standalone header fragments.

## Control Flow, State, and Persistence
Make control flow resolves the kernel source root, derives `ARCH` from `SUBARCH` when unset, builds file lists, concatenates headers through scripted preprocessing for standalone mode, and installs output under the selected include destination. State persists only in generated/installed header files under `OUTPUT` or the requested install directory.

## Dependencies and Integration
Depends on kernel build scripts such as `scripts/subarch.include`, standard Make functions, compiler support for architecture flags, and the complete nolibc header set. It is the packaging and developer-test entry point for the nolibc library embedded under `tools/include`.

## Risks and Test Signals
Risks include missing a new architecture header from `architectures`, stale per-arch CFLAGS, incorrect `srctree` inference when invoked from unusual directories, and generated standalone header drift. Test signals are `make -C tools/include/nolibc headers`, install-path checks, all listed architecture compile probes, and diffing generated standalone output after header edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-arm.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-arm.h

## Purpose
Provides the nolibc architecture backend for 32-bit ARM. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It handles ARM and Thumb syscall-number placement in `r7` or a temporary `r6`, declares `__ARCH_WANT_SYS_OLD_SELECT`, and uses `swi 0` with arguments in `r0`-`r5`.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-arm64.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-arm64.h

## Purpose
Provides the nolibc architecture backend for AArch64. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It places syscall numbers in `x8`, arguments in `x0`-`x5`, uses `svc #0`, and returns the result from `x0`.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-loongarch.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-loongarch.h

## Purpose
Provides the nolibc architecture backend for LoongArch. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It places syscall numbers in `a7`, arguments in `a0`-`a5`, uses `syscall 0`, and defines a clobber list for caller-saved registers.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-loongarch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-m68k.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-m68k.h

## Purpose
Provides the nolibc architecture backend for m68k. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It uses the m68k Linux trap convention, returns through `d0`, and provides a compact `_start` stub that passes the stack pointer to `_start_c()`.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-m68k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-mips.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-mips.h

## Purpose
Provides the nolibc architecture backend for MIPS. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `__start` when `NOLIBC_NO_RUNTIME` is not set. It covers o32-style argument passing with `v0` syscall numbers, `a0`-`a3` plus stack arguments for five- and six-argument calls, error detection through `a3`, and ABI-specific stack reservation. MIPS uses `__start` rather than `_start`.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-powerpc.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-powerpc.h

## Purpose
Provides the nolibc architecture backend for PowerPC. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It binds syscall numbers to `r0`, arguments to `r3` upward, checks the summary overflow condition for errors, and has 32-bit/64-bit startup variants including TOC setup for PPC64. It also overrides `__no_stack_protector` with an optimizer attribute when needed.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-powerpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-riscv.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-riscv.h

## Purpose
Provides the nolibc architecture backend for RISC-V. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It places syscall numbers in `a7`, arguments in `a0`-`a5`, executes `ecall`, and returns through `a0`.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-riscv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-s390.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-s390.h

## Purpose
Provides the nolibc architecture backend for s390. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It places syscall numbers in `r1`, arguments in `r2`-`r7`, uses the s390 supervisor-call path, and provides overrides for `mmap`, `fork`, and `vfork` to match the architecture ABI. The file defines `struct s390_mmap_arg_struct` for the packed mmap argument block.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-s390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-sh.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-sh.h

## Purpose
Provides the nolibc architecture backend for SuperH. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start_wrapper` when `NOLIBC_NO_RUNTIME` is not set. It uses `r3` for syscall numbers, `r4` onward for arguments, `trapa` for syscall entry, and a wrapper symbol so the real assembly `_start` can preserve the initial stack before any C prologue.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-sh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-sparc.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-sparc.h

## Purpose
Provides the nolibc architecture backend for SPARC. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It uses `g1` for syscall numbers, `o0` onward for arguments, trap variants for 32-bit and 64-bit SPARC, carry-bit error reporting, and special `fork`/`vfork` fixups because child return values differ from generic expectations.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-sparc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-x86.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-x86.h

## Purpose
Provides the nolibc architecture backend for x86 and x86_64. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `_start` when `NOLIBC_NO_RUNTIME` is not set. It has separate i386 `int $0x80` and x86_64 `syscall` implementations, declares old `select` support on i386, sets up frame pointers in startup code, and marks x86 as having architecture implementations of `memmove`, `memcpy`, and `memset`.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch-x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/arch.h

## Purpose
Selects the correct nolibc architecture backend for the active compiler target.

## APIs, Types, and Functions
The file has no functions. It conditionally includes `arch-x86.h`, `arch-arm64.h`, `arch-arm.h`, `arch-mips.h`, `arch-riscv.h`, `arch-s390.h`, `arch-loongarch.h`, `arch-powerpc.h`, `arch-sparc.h`, `arch-m68k.h`, or `arch-sh.h`, and emits a preprocessor error for unsupported targets.

## Control Flow, State, and Persistence
All control flow is compile-time preprocessor selection based on architecture macros such as `__x86_64__`, `__aarch64__`, `__arm__`, and similar. No runtime state is created.

## Dependencies and Integration
Depends on compiler predefined architecture macros and the sibling `arch-*.h` headers. It is included by generic nolibc wrappers before any syscall macro is used.

## Risks and Test Signals
Risks are missing aliases for new compiler target spellings, accidentally selecting the wrong ABI variant, and unsupported architectures failing only when this header is reached. Test signals are cross-architecture preprocessing checks and minimal nolibc builds for every listed backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/byteswap.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/byteswap.h

## Purpose
Provides glibc-like byte-swap macro names for nolibc programs.

## APIs, Types, and Functions
Defines `bswap_16`, `bswap_32`, and `bswap_64` as wrappers around Linux `__swab16`, `__swab32`, and `__swab64`.

## Control Flow, State, and Persistence
There is no runtime state; macros expand into constant or inline byte-swap operations. Control flow is purely expression evaluation by callers.

## Dependencies and Integration
Depends on `stdint.h` for fixed-width types and `<linux/swab.h>` for implementation. It integrates with tools code expecting `<byteswap.h>` style names under the nolibc include surface.

## Risks and Test Signals
Risks are multiple evaluation if callers pass expressions with side effects and divergence from libc feature macros. Test signals are compile-time constant swaps, runtime round trips for all widths, and builds on big- and little-endian targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/byteswap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/compiler.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/compiler.h

## Purpose
Centralizes compiler feature detection and attributes used by nolibc headers.

## APIs, Types, and Functions
Defines `__nolibc_has_attribute`, `__nolibc_has_feature`, `__nolibc_aligned`, `__nolibc_aligned_as`, `__nolibc_naked`, stack-protector detection, `__no_stack_protector`, `__fallthrough`, standard-version helpers, optimizer barriers, and sanitizer-suppression attributes.

## Control Flow, State, and Persistence
All behavior is compile-time macro expansion. The header decides which attributes are available and exposes stable internal names so architecture and runtime code can annotate `_start`, stack-check code, packed/aligned data, and undefined-behavior-sensitive startup paths.

## Dependencies and Integration
Depends on GCC/Clang predefined macros, `__has_attribute`, `__has_feature`, and language version macros. It is included by architecture backends, CRT setup, and stack protector support.

## Risks and Test Signals
Risks are compiler-version feature probes that mis-detect support, attributes that differ subtly between GCC and Clang, and stack-protector suppression failing on startup code. Test signals are GCC and Clang builds, stack-protector-enabled nolibc programs, UBSan-enabled builds, and preprocessing checks for C89/C99/C11 modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/crt.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/crt.h

## Purpose
Implements the architecture-independent C runtime startup handoff for nolibc programs.

## APIs, Types, and Functions
Declares weak globals `environ` and `_auxv`, init/fini array symbols, optional `program_invocation_name` and `program_invocation_short_name`, helper `__nolibc_program_invocation_short_name()`, and `_start_c(long *sp)`.

## Control Flow, State, and Persistence
`_start_c()` decodes the initial process stack into `argc`, `argv`, `envp`, and auxiliary vector, initializes stack canary state, sets program invocation names, runs preinit and init arrays, calls `main(argc, argv, envp)`, then runs fini arrays and exits with the returned status. Persistent process state is limited to the weak globals and program-name pointers.

## Dependencies and Integration
Depends on architecture `_start` stubs passing the initial stack pointer, `stackprotector.h`, `stdlib`/`string` helpers, ELF process stack layout, and linker-provided init/fini array boundaries. It is the bridge between raw kernel process entry and normal C `main()`.

## Risks and Test Signals
Risks include incorrect initial-stack parsing, constructor/destructor ordering bugs, missing stack-canary initialization before protected code, and weak symbol conflicts with embedding programs. Test signals are tiny nolibc executable startup tests, argv/envp/auxv validation, constructor/destructor ordering tests, stack-protector builds, and programs with and without `NOLIBC_NO_RUNTIME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/crt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/ctype.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/ctype.h

## Purpose
Provides minimal ASCII character classification for nolibc programs.

## APIs, Types, and Functions
Defines inline-style functions `isascii`, `isblank`, `iscntrl`, `isdigit`, `isgraph`, `islower`, `isprint`, `isspace`, `isupper`, `isxdigit`, `isalpha`, `isalnum`, and `ispunct`.

## Control Flow, State, and Persistence
Control flow is simple integer range and equality checks. There is no locale state, no tables, and no persistence; behavior is ASCII-only and deterministic.

## Dependencies and Integration
Depends only on the nolibc include umbrella. It integrates with parsers in `getopt`, `stdio` scanning, and `stdlib` numeric conversion that need libc-like classification without libc.

## Risks and Test Signals
Risks are callers expecting locale-aware classification or undefined behavior for negative `char` values to match glibc exactly. Test signals are exhaustive 0-127 classification checks, negative and >127 inputs, and parser tests that consume whitespace, digits, and hex prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/ctype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/dirent.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/dirent.h

## Purpose
Implements a tiny directory-iteration interface on top of Linux `getdents64` for nolibc programs.

## APIs, Types, and Functions
Defines `struct dirent`, opaque `DIR` carrying a file descriptor plus one `linux_dirent64`, and functions `fdopendir`, `opendir`, `closedir`, and `readdir_r`.

## Control Flow, State, and Persistence
`opendir()` opens a directory, `fdopendir()` allocates a DIR wrapper, `readdir_r()` issues one `getdents64` call into the embedded buffer and copies inode, offset, reclen, type, and name into the caller's `dirent`, and `closedir()` closes the fd and frees the wrapper. Persistent state is the open file descriptor and DIR allocation.

## Dependencies and Integration
Depends on `fcntl.h`, `stdlib.h`, `string.h`, `sys.h`, and `types.h`, especially `struct linux_dirent64`. It integrates with filesystem-walking nolibc tools that only need simple one-entry-at-a-time iteration.

## Risks and Test Signals
Risks include the intentionally limited single-record buffer, `readdir_r` legacy semantics, long names bounded by the embedded kernel record, and fd ownership surprises with `fdopendir`. Test signals are empty/nonempty directory iteration, long filename handling, fd leak checks, error propagation from `getdents64`, and iteration after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/elf.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/elf.h

## Purpose
Exposes Linux UAPI ELF constants and structs through the nolibc include tree.

## APIs, Types, and Functions
It has no local functions or types beyond the include guard; it includes `<linux/elf.h>`.

## Control Flow, State, and Persistence
There is no control flow or state. It is a compatibility facade so nolibc consumers can include an ELF header path without depending on system libc headers.

## Dependencies and Integration
Depends on the kernel UAPI `linux/elf.h`. Integration points include startup/auxv parsing, binary inspection tools, and code that uses ELF constants while building against nolibc.

## Risks and Test Signals
Risks are UAPI availability differences and callers assuming full glibc `<elf.h>` coverage. Test signals are compiling ELF consumers under nolibc and comparing required constants against the kernel UAPI header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/endian.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/endian.h

## Purpose
Provides host-to/from big- and little-endian conversion macro names for nolibc.

## APIs, Types, and Functions
Defines `htobe16`, `htole16`, `be16toh`, `le16toh`, and the corresponding 32- and 64-bit variants, each mapped to Linux byteorder helpers.

## Control Flow, State, and Persistence
Macros expand into endian conversion expressions and keep no state. Control flow is limited to whatever the underlying byteorder helper emits for the target endian.

## Dependencies and Integration
Depends on `stdint.h` and `<asm/byteorder.h>`. It integrates with binary format, network, and filesystem tools that use common endian conversion names.

## Risks and Test Signals
Risks include side-effect arguments, mismatch with libc feature-test expectations, and missing less-common macros such as PDP endian helpers. Test signals are constant-expression conversions, big/little-endian build coverage, and parser round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/err.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/err.h

## Purpose
Implements BSD-style warning and fatal-error helpers for nolibc programs.

## APIs, Types, and Functions
Defines `vwarn`, `vwarnx`, `warn`, `warnx`, `verr`, `verrx`, `err`, and `errx`. The fatal variants are noreturn and terminate through `exit(eval)`.

## Control Flow, State, and Persistence
Warning helpers format to `stderr`, optionally append `errno` text through `perror`, and return. Fatal helpers perform the same reporting and then exit. No persistent state is owned, but output depends on global `errno` and stdio descriptors.

## Dependencies and Integration
Depends on `errno.h`, `stdio.h`, `stdarg.h`, and process exit support. It integrates with small command-line tools that expect `err(3)` style diagnostics without libc.

## Risks and Test Signals
Risks are format-string misuse, global `errno` being overwritten before reporting, and differences from BSD/glibc exact formatting. Test signals are warning/fatal output golden tests, errno and non-errno variants, and exit-status assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/errno.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/errno.h

## Purpose
Defines nolibc errno storage and error-number constants.

## APIs, Types, and Functions
Includes `<asm/errno.h>`, defines `SET_ERRNO(v)` to update `errno` unless `NOLIBC_IGNORE_ERRNO` is set, provides fallback program invocation names in ignore mode, and defines `MAX_ERRNO` as 4095.

## Control Flow, State, and Persistence
There is no function control flow. Syscall wrappers use `__sysret()` from `sys.h` to translate negative kernel errors into `-1` plus `errno`, and this header controls whether that store is real or compiled away.

## Dependencies and Integration
Depends on architecture UAPI errno definitions and optional external `errno` storage supplied by the program or nolibc runtime. It is central to every wrapper that returns libc-style errors.

## Risks and Test Signals
Risks include missing `errno` definition in unusual embedding modes, intentionally ignored errno hiding failures, and assuming all negative values are errno when only `-MAX_ERRNO..-1` are translated. Test signals are failing syscall wrappers, `NOLIBC_IGNORE_ERRNO` builds, and checking errno values against UAPI constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/fcntl.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/fcntl.h

## Purpose
Provides nolibc file-open wrappers and fcntl/open constants from Linux UAPI.

## APIs, Types, and Functions
Defines `_sys_openat`, `openat`, `_sys_open`, and `open`, with varargs mode handling for creation flags. It includes `<linux/fcntl.h>` for flag definitions.

## Control Flow, State, and Persistence
`openat()` and `open()` pick up an optional `mode_t` vararg when needed, issue `openat` or legacy `open` syscalls depending on availability, and return through `__sysret`. No state is persisted except kernel file descriptors returned to callers.

## Dependencies and Integration
Depends on `arch.h`, `stdarg.h`, `types.h`, and syscall numbers. It integrates with `stdio.h`, `dirent.h`, and general filesystem access in nolibc tools.

## Risks and Test Signals
Risks are varargs misuse when creation flags are present, missing legacy syscalls on modern architectures, and fd leaks in callers. Test signals are open/openat success and permission failures, mode creation tests, `O_CLOEXEC` behavior, and architecture builds with only `openat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/getopt.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/getopt.h

## Purpose
Implements a compact POSIX-like `getopt` parser for nolibc command-line tools.

## APIs, Types, and Functions
Defines weak data symbols `optarg`, `optind`, `opterr`, and `optopt`, plus `getopt(int argc, char * const argv[], const char *optstring)`. It forward-declares `stderr` and `fprintf` to report invalid options.

## Control Flow, State, and Persistence
`getopt()` tracks the current argv index and character offset in static parser state, handles clustered short options, required option arguments, `--` termination, and error reporting. Persistent state is the standard getopt globals plus internal scan position.

## Dependencies and Integration
Depends on nolibc stdio for diagnostics and conventional argv layout from `crt.h`. It integrates with small tools that parse short options without pulling in libc.

## Risks and Test Signals
Risks include limited GNU-extension support, global parser state not being thread-safe, and behavior differences around optional arguments or argument permutation. Test signals are clustered options, missing arguments, `--`, invalid-option reporting, optind reset behavior, and silent mode with leading `:` or `opterr=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/getopt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/inttypes.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/inttypes.h

## Purpose
Compatibility shim for code that includes `<inttypes.h>` while using nolibc.

## APIs, Types, and Functions
The header currently includes `stdint.h` and does not define printf format macros or conversion functions of its own.

## Control Flow, State, and Persistence
There is no runtime control flow or state. Its value is include-path compatibility and fixed-width integer availability.

## Dependencies and Integration
Depends on `nolibc/stdint.h`. It integrates with source files that need integer typedefs but do not rely on full libc `inttypes` formatting support.

## Risks and Test Signals
Risks are callers expecting `PRI*`, `SCN*`, `imaxdiv`, or other full `<inttypes.h>` APIs. Test signals are compile failures in consumers that require missing macros, and simple builds that only need fixed-width types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/inttypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/limits.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/limits.h

## Purpose
Compatibility entry point for nolibc limits definitions.

## APIs, Types, and Functions
The file includes `nolibc.h`; common path and file constants are provided elsewhere, especially `types.h` for `PATH_MAX` and `MAXPATHLEN`.

## Control Flow, State, and Persistence
There is no runtime behavior. All effect is compile-time inclusion of the broader nolibc surface.

## Dependencies and Integration
Depends on the nolibc umbrella header. It integrates with code that includes `<limits.h>` but only needs constants already defined by the nolibc set.

## Risks and Test Signals
Risks are incomplete libc compatibility for numeric limits such as `INT_MAX` or `CHAR_BIT` if consumers expect a full limits header. Test signals are compiling representative nolibc programs and adding targeted checks for every limit macro they require.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/math.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/math.h

## Purpose
Provides minimal floating absolute-value helpers for nolibc.

## APIs, Types, and Functions
Defines `fabs`, `fabsf`, and `fabsl` as inline sign checks returning the positive magnitude of double, float, and long double values.

## Control Flow, State, and Persistence
Control flow is a single comparison and conditional negation. No math library state, errno, floating exception handling, or NaN special handling beyond C comparison semantics is implemented.

## Dependencies and Integration
Depends only on the nolibc include surface. It integrates with small programs that need basic absolute value without linking libm.

## Risks and Test Signals
Risks are callers expecting full libm behavior, signed-zero preservation, NaN payload semantics, or errno/fenv side effects. Test signals are positive/negative values, zero, infinity, NaN behavior, and builds without libm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/math.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/nolibc.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/nolibc.h

## Purpose
Top-level umbrella header for nolibc, a tiny libc-like layer for Linux programs that use raw syscalls and header-only helpers.

## APIs, Types, and Functions
Includes the ordered nolibc components: compiler support, standard integer/types, architecture backend, syscall layer, file/time/string/stdio/stdlib wrappers, and related compatibility headers. It defines `_NOLIBC_H` and `NOLIBC`.

## Control Flow, State, and Persistence
There is no runtime control flow in the umbrella itself. Its include order establishes the compile-time dependency graph so prototypes, typedefs, syscall macros, and startup helpers are visible before consumers use them.

## Dependencies and Integration
Depends on Linux UAPI headers and all sibling nolibc headers. It is the common include for tests and small utilities that want a libc-like API without linking libc.

## Risks and Test Signals
Risks include include-order regressions, duplicate definitions when mixed with system libc headers, and broad namespace exposure. Test signals are building representative programs by including only `nolibc.h`, include-what-you-use checks for individual headers, and mixed include-order smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/nolibc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/poll.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/poll.h

## Purpose
Provides the `poll` wrapper and poll-related UAPI types for nolibc.

## APIs, Types, and Functions
Defines `_sys_poll(struct pollfd *fds, int nfds, int timeout)` and `poll(...)`, using `<linux/poll.h>` for `struct pollfd` and event constants.

## Control Flow, State, and Persistence
The wrapper issues the `poll` syscall when available or falls back to `ppoll`-style availability depending on architecture support, then translates errors with `__sysret`. State lives in the caller's `pollfd` array where the kernel writes `revents`.

## Dependencies and Integration
Depends on `arch.h`, `sys.h`, and Linux poll UAPI. It integrates with stdio/file-descriptor event loops in nolibc programs.

## Risks and Test Signals
Risks are timeout unit confusion, nfds range issues, and architecture syscall availability. Test signals are readable/writable pipe polling, timeout expiration, interrupted polls, invalid fd handling, and cross-architecture builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sched.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sched.h

## Purpose
Provides namespace and scheduling-adjacent wrappers for nolibc.

## APIs, Types, and Functions
Defines `_sys_setns`, `setns`, `_sys_unshare`, and `unshare`, and includes `<linux/sched.h>` for flag constants.

## Control Flow, State, and Persistence
Each wrapper passes fd or flag arguments to the corresponding syscall and returns through `__sysret`. No userspace state is persisted; effects are kernel task namespace or sharing-state changes.

## Dependencies and Integration
Depends on syscall numbers, `arch.h`, `sys.h`, and Linux scheduler UAPI. It integrates with container, namespace, and isolation tests that use nolibc.

## Risks and Test Signals
Risks are irreversible process-context changes in tests, flag availability across kernels, and permission-sensitive failures. Test signals are invalid flag/fd handling, user namespace or mount namespace smoke tests, and expected `EPERM` paths under unprivileged execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/signal.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/signal.h

## Purpose
Provides minimal signal support for nolibc.

## APIs, Types, and Functions
Includes `<linux/signal.h>` and defines weak `raise(int signal)`, implemented by sending a signal to the current process.

## Control Flow, State, and Persistence
`raise()` obtains the process id through nolibc syscall helpers and invokes `kill(pid, signal)`. It keeps no state; signal delivery and disposition are kernel/process state.

## Dependencies and Integration
Depends on `sys.h` for `getpid` and `kill`, and Linux signal constants. It integrates with abort/error paths and small tests needing self-signalling.

## Risks and Test Signals
Risks are limited signal API coverage, process-vs-thread semantics compared with libc `raise`, and async behavior in tests. Test signals are raising ignored, handled, and default-fatal signals, plus invalid signal error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stackprotector.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/stackprotector.h

## Purpose
Supplies stack protector support when nolibc is built with compiler stack canaries enabled.

## APIs, Types, and Functions
Defines weak `__stack_chk_fail`, `__stack_chk_fail_local`, weak global `__stack_chk_guard`, and `__stack_chk_init()` when stack protector mode is detected; otherwise `__stack_chk_init()` is an empty stub.

## Control Flow, State, and Persistence
Startup code calls `__stack_chk_init()` before `main`. Failure handlers terminate through nolibc abort/exit paths. Persistent state is the canary guard value, usually initialized from auxiliary-vector randomness when available or a fallback value.

## Dependencies and Integration
Depends on compiler stack-protector macros, `compiler.h` attributes, startup ordering in `crt.h`, and syscall/stdlib termination helpers. It integrates with all nolibc code compiled under stack protector flags.

## Risks and Test Signals
Risks are initializing the guard too late, weak symbol collisions, predictable fallback canaries, and architecture startup code accidentally protected before the guard exists. Test signals are stack-protector-enabled builds, deliberate canary corruption tests, auxv randomness presence/absence, and static checks that `_start` paths are `no_stack_protector`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/std.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/std.h

## Purpose
Defines common POSIX-ish scalar typedefs for nolibc.

## APIs, Types, and Functions
Provides `dev_t`, `ino_t`, `mode_t`, `pid_t`, `uid_t`, `gid_t`, `nlink_t`, `off_t`, `blksize_t`, `blkcnt_t`, and `time_t` based on fixed-width and kernel time types.

## Control Flow, State, and Persistence
There is no control flow or runtime state. The header fixes userspace ABI type widths used by stat, filesystem, process, and time wrappers.

## Dependencies and Integration
Depends on `stdint.h` and Linux time type definitions. It integrates with `types.h`, `sys/stat.h`, `fcntl.h`, `time.h`, and many syscall wrappers.

## Risks and Test Signals
Risks are ABI mismatches on unusual architectures, especially `time_t` and file offset width, and divergence from system libc typedefs. Test signals are sizeof/alignment assertions, stat/time wrapper builds, and 32-bit architecture coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/std.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdarg.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/stdarg.h

## Purpose
Provides varargs primitives for nolibc.

## APIs, Types, and Functions
Typedefs `va_list` to `__builtin_va_list` and maps `va_start`, `va_end`, `va_arg`, and `va_copy` to compiler builtins.

## Control Flow, State, and Persistence
There is no runtime state beyond caller-owned varargs traversal objects. Control flow follows compiler ABI lowering for variadic functions.

## Dependencies and Integration
Depends on compiler builtins. It integrates with `stdio` formatting/scanning, `err` diagnostics, and `open`/`openat` mode varargs.

## Risks and Test Signals
Risks are compiler ABI assumptions and misuse after `va_end` or without `va_copy`. Test signals are printf/asprintf/open varargs tests across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdarg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdbool.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/stdbool.h

## Purpose
Provides C boolean compatibility macros for nolibc.

## APIs, Types, and Functions
Defines `bool` as `_Bool`, `true` as `1`, `false` as `0`, and `__bool_true_false_are_defined`.

## Control Flow, State, and Persistence
There is no control flow or state. It is a compile-time compatibility layer.

## Dependencies and Integration
Depends on C99 `_Bool` support. It integrates with code expecting `<stdbool.h>` in a nolibc include path.

## Risks and Test Signals
Risks are compiling in non-C99 modes or clashing with C++ bool semantics if used incorrectly. Test signals are simple C and C++ preprocessing/compile smoke tests where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdbool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stddef.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/stddef.h

## Purpose
Provides minimal standard definitions for null pointers and member offsets.

## APIs, Types, and Functions
Defines `NULL` as `((void *)0)` and `offsetof(TYPE, FIELD)` through `__builtin_offsetof`.

## Control Flow, State, and Persistence
No runtime state exists. `offsetof` is compile-time expression support for structure layout calculations.

## Dependencies and Integration
Depends on compiler `__builtin_offsetof`. It integrates with `container_of` in `types.h` and layout-sensitive syscall structures.

## Risks and Test Signals
Risks are incomplete `<stddef.h>` compatibility, including missing `wchar_t` or `max_align_t`, and C++ null pointer expectations. Test signals are compile checks for `offsetof` on nested structs and consumers requiring only `NULL` and offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stddef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdint.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/stdint.h

## Purpose
Defines fixed-width integer, pointer-width, least/fast-width, and limit macros for nolibc.

## APIs, Types, and Functions
Typedefs `uint8_t/int8_t`, `uint16_t/int16_t`, `uint32_t/int32_t`, `uint64_t/int64_t`, `size_t`, `ssize_t`, `uintptr_t`, `intptr_t`, `ptrdiff_t`, least/fast aliases, and max-width aliases. It also defines integer limit macros such as `INT8_MIN`, `UINT64_MAX`, `SIZE_MAX`, and related constants.

## Control Flow, State, and Persistence
There is no runtime behavior. The header establishes compile-time integer ABI used by every other nolibc header.

## Dependencies and Integration
Depends on compiler predefined `__SIZE_TYPE__` and conventional Linux userspace integer sizes. It integrates with `std.h`, binary parsers, syscall wrappers, and formatting code.

## Risks and Test Signals
Risks are unsupported targets with nonstandard integer widths, incomplete C standard macro coverage, and mismatch between `ssize_t` and kernel ABI on unusual platforms. Test signals are static assertions for sizes and limits, 32/64-bit builds, and compiling code that uses each typedef family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdio.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/stdio.h

## Purpose
Implements a compact stdio-like layer over file descriptors for nolibc, including simple stream wrappers, formatted output, limited scanning, and error text.

## APIs, Types, and Functions
Defines the lightweight `FILE` fd wrapper and constants `stdin`, `stdout`, `stderr`; file helpers `fdopen`, `fopen`, `fileno`, `fflush`, `fclose`, `fgetc`, `getchar`, `fputc`, `putchar`, `fread`, `fwrite`, `fputs`, `puts`, `fgets`, and `fseek`; formatting APIs `vfprintf`, `vprintf`, `fprintf`, `printf`, `vdprintf`, `dprintf`, `vsnprintf`, `snprintf`, `vsprintf`, `sprintf`, `vasprintf`, and `asprintf`; scanning `vsscanf` and `sscanf`; plus `perror`, `setvbuf`, `strerror_r`, and `strerror`.

## Control Flow, State, and Persistence
The stream model stores only an fd in allocated `FILE` wrappers; standard streams are encoded sentinel pointers. I/O helpers call `read`, `write`, `open`, `close`, and `lseek`. The printf engine walks the format string, consumes `va_list` arguments, formats integers/strings/chars/pointers into callback sinks, and tracks truncation for snprintf. `asprintf` performs a sizing pass then allocates. State persists in heap-allocated FILE wrappers and output buffers owned by callers.

## Dependencies and Integration
Depends on `stdarg.h`, `stdlib.h`, `string.h`, `unistd.h`, `fcntl.h`, `errno.h`, and syscall wrappers. It integrates with diagnostics, getopt errors, command-line tools, and any nolibc code needing libc-style fd I/O without buffering.

## Risks and Test Signals
Risks include incomplete printf/scanf format support, no real buffering despite `setvbuf`, allocation failure in `asprintf`, format-string type mismatches, and differences from libc stream semantics. Test signals are formatted-output golden tests, snprintf truncation boundaries, fd-backed read/write tests, asprintf allocation failures, sscanf conversion tests, and stderr/perror errno output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdlib.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/stdlib.h

## Purpose
Implements minimal stdlib functionality for nolibc: process abort, environment lookup, heap allocation, integer formatting, and string-to-integer conversion.

## APIs, Types, and Functions
Defines `struct nolibc_heap`, `abs/labs/llabs`, weak `abort`, `atol`, `atoi`, `free`, `getenv`, `malloc`, `calloc`, `realloc`, integer-to-string helpers `utoh_r`, `utoa_r`, `itoa_r`, `u64toa_r`, `i64toa_r` and buffer-returning variants, internal `_nolibc_u64toa_base`, parser `__strtox`, and `strtol`, `strtoul`, `strtoll`, `strtoull`, `strtoimax`, `strtoumax`.

## Control Flow, State, and Persistence
`malloc` maps heap chunks with `mmap` and prefixes them with `struct nolibc_heap`; `free` unmaps the whole chunk, and `realloc` allocates/copies/frees when needed. Environment lookup scans global `environ`. Numeric formatting repeatedly divides or uses reciprocal multiplication for bases, writing caller buffers or a shared static `itoa_buffer`. String conversion handles whitespace, sign, base autodetection, overflow limits, and end pointers.

## Dependencies and Integration
Depends on `arch.h`, `types.h`, `sys.h`, `string.h`, and Linux auxv definitions. It is used by stdio formatting, CRT startup, directory wrappers, and most higher-level nolibc helpers requiring heap or conversion support.

## Risks and Test Signals
Risks include one-mmap-per-allocation overhead, no allocator reuse, static conversion buffer not being thread-safe, overflow and base edge cases in `__strtox`, and `realloc` copy-size dependence on stored heap metadata. Test signals are malloc/calloc/realloc/free under ASan/strace, conversion boundary tests for every signed/unsigned limit, base 0/8/10/16 parsing, environment lookup, and concurrent calls to buffer-returning conversion helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/stdlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/string.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/string.h

## Purpose
Provides core memory and string routines for nolibc, with weak implementations that architecture backends may override.

## APIs, Types, and Functions
Defines `memcmp`, weak `memmove`, weak `memcpy`, weak `memset`, `memchr`, `strchr`, `strcmp`, `strcpy`, weak `strlen`, `strnlen`, `strdup`, `strndup`, `strlcat`, `strlcpy`, `strncat`, `strncmp`, `strncpy`, `strrchr`, `strstr`, `tolower`, and `toupper`. It also has a `strlen` macro optimization for constant strings.

## Control Flow, State, and Persistence
Memory functions perform byte-wise forward/backward copies or fills. String functions scan until NUL or a requested limit, duplicate via `malloc`, and return libc-like pointers or lengths. Persistent state is only caller-owned buffers and heap allocations returned by duplication functions.

## Dependencies and Integration
Depends on `std.h`, `stddef.h`, and `stdlib` allocation for duplication. Architecture headers can mark `NOLIBC_ARCH_HAS_MEMMOVE`, `MEMCPY`, or `MEMSET` to replace weak generic versions.

## Risks and Test Signals
Risks include performance on large buffers, overlap misuse with `memcpy`, unsigned/signed char comparison differences, non-thread-safe assumptions around caller buffers, and incomplete locale handling for case conversion. Test signals are exhaustive small-buffer memory tests, overlap `memmove` cases, string boundary tests without NUL inside limits, strdup allocation failure paths, and architecture override builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys.h

## Purpose
Provides the main nolibc syscall wrapper layer for process, filesystem, fd, identity, and basic memory-management operations.

## APIs, Types, and Functions
Defines `__sysret()` for libc-style error translation and `__nolibc_enosys()` for unavailable calls. Wrappers include `brk`, `sbrk`, `chdir`, `fchdir`, `chmod`, `chown`, `chroot`, `close`, `dup`, `dup2`, `dup3`, `execve`, `_exit`, `exit`, `fork`, `vfork`, `fsync`, `getdents64`, `geteuid`, `getpgid`, `getpgrp`, `getpid`, `getppid`, `gettid`, `getpagesize`, `getuid`, `kill`, `link`, `lseek`, `mkdir`, `rmdir`, `mknod`, `pipe2`, `pipe`, `pivot_root`, `read`, `sched_yield`, `setpgid`, `setpgrp`, `setsid`, `symlink`, `umask`, `umount2`, `unlink`, `write`, and `memfd_create`.

## Control Flow, State, and Persistence
Each `_sys_*` helper issues the raw syscall or architecture override; public wrappers pass results through `__sysret` when errno translation is needed. Many wrappers choose modern `*at` syscalls when legacy syscalls are missing, and `sbrk` persists the current break in static state after probing with `brk(NULL)`. Process-exit wrappers never return.

## Dependencies and Integration
Depends on `arch.h` syscall macros, errno handling, `types.h`, Linux syscall numbers, and architecture-specific overrides for special ABIs. It is the central dependency for stdio, stdlib, dirent, unistd, fcntl, and `sys/*` compatibility headers.

## Risks and Test Signals
Risks include syscall availability differences, subtle fallback semantics for `dup2`, `link`, `mkdir`, `mknod`, `lseek`, and old UID syscalls, static `sbrk` state racing with direct `brk`, and errno translation of raw negative values. Test signals are nolibc syscall selftests across architectures, ENOSYS fallback paths, fd lifecycle tests, process creation/wait tests, and filesystem operation round trips in temporary directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/auxv.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/auxv.h

## Purpose
Provides nolibc compatibility for auxiliary-vector lookup.

## APIs, Types, and Functions
Defines `getauxval(unsigned long type)` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper scans the `_auxv` array populated by CRT startup and returns the value for the requested key or zero, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/auxv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/ioctl.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/ioctl.h

## Purpose
Provides nolibc compatibility for ioctl command dispatch.

## APIs, Types, and Functions
Defines `_sys_ioctl` and `ioctl` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper passes fd, command, and unsigned long argument to the `ioctl` syscall, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mman.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mman.h

## Purpose
Provides memory mapping wrappers for nolibc.

## APIs, Types, and Functions
Defines `_sys_mmap`/`mmap`, `_sys_mremap`/`mremap`, and `_sys_munmap`/`munmap`, including architecture-specific mmap argument handling when an arch backend overrides `_sys_mmap`.

## Control Flow, State, and Persistence
Wrappers issue mapping syscalls, return `MAP_FAILED` with errno on failure, and otherwise return mapped addresses or zero success. Persistent state is kernel VMA state owned by the process, not the header.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h`, and `<linux/mman.h>`. It is used by nolibc `malloc`, tests, and any program needing raw mappings.

## Risks and Test Signals
Risks include page-size alignment, offset width on 32-bit, architecture-specific mmap ABI differences, and leaking mappings on error paths. Test signals are anonymous/file-backed mappings, mremap growth/move behavior, munmap boundaries, and 32-bit offset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mount.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mount.h

## Purpose
Provides nolibc compatibility for mount operations.

## APIs, Types, and Functions
Defines `_sys_mount`, `mount`, `_sys_umount2`, and `umount2` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper forwards filesystem type, source, target, flags, data, and unmount flags to kernel mount syscalls, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/prctl.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/prctl.h

## Purpose
Provides nolibc compatibility for process-control operations.

## APIs, Types, and Functions
Defines `_sys_prctl` and `prctl` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper passes option plus four unsigned long arguments to the kernel, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/ptrace.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/ptrace.h

## Purpose
Provides nolibc compatibility for ptrace operations.

## APIs, Types, and Functions
Defines `_sys_ptrace` and `ptrace` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper passes operation, pid, address, and data pointer to `ptrace`, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/random.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/random.h

## Purpose
Provides nolibc compatibility for kernel random byte retrieval.

## APIs, Types, and Functions
Defines `_sys_getrandom` and `getrandom` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper fills a caller buffer with `getrandom` and returns a byte count or errno, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/reboot.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/reboot.h

## Purpose
Provides nolibc compatibility for system reboot requests.

## APIs, Types, and Functions
Defines `_sys_reboot` and `reboot` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper passes Linux reboot magic constants and command values to the `reboot` syscall, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/resource.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/resource.h

## Purpose
Provides resource-limit wrappers for nolibc.

## APIs, Types, and Functions
Includes Linux resource UAPI and defines `getrlimit` and `setrlimit`, using `prlimit64` when needed.

## Control Flow, State, and Persistence
Calls query or update kernel rlimit state for the current process and translates errors. No userspace state persists beyond caller-provided `struct rlimit` values.

## Dependencies and Integration
Depends on syscall macros, `sys.h`, and Linux resource definitions. It integrates with tests or tools that constrain address space, file size, or descriptor counts.

## Risks and Test Signals
Risks include 32-bit vs 64-bit limit layout, privilege-sensitive limit increases, and kernel support differences. Test signals are reading `RLIMIT_NOFILE`, lowering/restoring soft limits, invalid resource ids, and cross-architecture struct-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/select.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/select.h

## Purpose
Implements `select` and fd-set manipulation for nolibc.

## APIs, Types, and Functions
Defines `fd_set` plus `FD_ZERO`, `FD_SET`, `FD_CLR`, `FD_ISSET`, private `_sys_select`, and public `select`.

## Control Flow, State, and Persistence
Fd-set macros mutate caller-provided bitsets. `select` chooses the old `select` syscall on architectures that request it or uses `pselect6`/modern alternatives where available, then writes readiness bits and timeout state as the kernel dictates.

## Dependencies and Integration
Depends on `../types.h`, `../sys.h`, and architecture `__ARCH_WANT_SYS_OLD_SELECT` declarations. It integrates with event loops and `poll` alternatives in tiny tools.

## Risks and Test Signals
Risks include `FD_SETSIZE` assumptions, nfds exceeding the local bitset, timeout mutation differences, and old-select ABI packing. Test signals are pipe readiness, timeout-only selects, invalid fd errors, and arch coverage for both old and modern syscall paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/select.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/stat.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/stat.h

## Purpose
Provides file-status wrappers for nolibc using modern `statx` where possible.

## APIs, Types, and Functions
Defines `_sys_statx`, `statx`, `fstatat`, `stat`, `fstat`, and `lstat`, converting `struct statx` results into nolibc `struct stat` for legacy APIs.

## Control Flow, State, and Persistence
The wrappers query kernel metadata, translate errors, and populate caller buffers. Conversion maps device, inode, mode, link count, uid/gid, size, block size, block count, and timestamps. No persistent userspace state is held.

## Dependencies and Integration
Depends on `../types.h`, `../sys.h`, Linux stat UAPI, and fd/path syscall support. It integrates with directory walkers, file tools, and stdio/file tests.

## Risks and Test Signals
Risks include incomplete stat field conversion, timestamp width, symlink-following flags, and kernels lacking `statx`. Test signals are stat/fstat/lstat comparisons against libc, symlink behavior, device/inode fields, timestamp checks, and old-kernel fallback coverage if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/syscall.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/syscall.h

## Purpose
Compatibility shim for code including `<sys/syscall.h>` under nolibc.

## APIs, Types, and Functions
Includes `<asm/unistd.h>` to expose `__NR_*` syscall numbers and defines no local wrappers.

## Control Flow, State, and Persistence
There is no runtime control flow or state. It simply makes syscall-number constants available through a libc-like include path.

## Dependencies and Integration
Depends on architecture UAPI unistd headers. It integrates with programs that occasionally issue raw nolibc architecture syscall macros or need numeric syscall constants.

## Risks and Test Signals
Risks are architecture-specific syscall-number differences and callers expecting libc's variadic `syscall()` function, which this header does not provide. Test signals are compile checks for required `__NR_*` constants and raw syscall smoke tests through arch macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/sysmacros.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/sysmacros.h

## Purpose
Provides device-number composition and extraction helpers for nolibc.

## APIs, Types, and Functions
Defines inline `__nolibc_makedev`, `__nolibc_major`, and `__nolibc_minor`, then maps public `makedev`, `major`, and `minor` macros to them.

## Control Flow, State, and Persistence
Control flow is bit manipulation matching Linux device number encoding. No runtime state is retained.

## Dependencies and Integration
Depends on `dev_t` from nolibc types. It integrates with `stat`, `mknod`, and tools that inspect device ids.

## Risks and Test Signals
Risks are encoding drift if Linux changes device-number layout and truncation of large major/minor values. Test signals are round trips for boundary major/minor values and comparison with libc/sysmacros on Linux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/sysmacros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/time.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/time.h

## Purpose
Provides `gettimeofday` compatibility for nolibc.

## APIs, Types, and Functions
Defines `_sys_gettimeofday` and `gettimeofday`, with a fallback through `_sys_clock_gettime` when native gettimeofday is not available.

## Control Flow, State, and Persistence
The wrapper populates caller-provided `timeval` and optional timezone data, translating syscall errors. It persists no state.

## Dependencies and Integration
Depends on `../time.h`, `../types.h`, and syscall availability. It integrates with programs expecting `<sys/time.h>` rather than `<time.h>`.

## Risks and Test Signals
Risks include timezone argument compatibility, time64 conversion on 32-bit, and syscall fallback precision differences. Test signals are non-null and null timeval calls, monotonicity sanity checks, 32-bit builds, and invalid pointer fault handling in negative tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/timerfd.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/timerfd.h

## Purpose
Provides Linux timerfd wrappers for nolibc.

## APIs, Types, and Functions
Defines `_sys_timerfd_create`/`timerfd_create`, `_sys_timerfd_gettime`/`timerfd_gettime`, and timerfd settime wrappers, using `itimerspec` structures.

## Control Flow, State, and Persistence
Create returns a kernel timerfd descriptor. Get/set wrappers query or update timer state and copy `itimerspec` values through caller buffers. Persistent state is the kernel timerfd associated with the returned fd.

## Dependencies and Integration
Depends on `../time.h`, `../sys.h`, and Linux timerfd syscall numbers. It integrates with event loops using poll/select on timer fds.

## Risks and Test Signals
Risks include time64 syscall availability, flags validation, descriptor leaks, and absolute vs relative timer confusion. Test signals are one-shot and periodic timerfd reads, gettime after settime, invalid clock/flag errors, and poll integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/timerfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/types.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/types.h

## Purpose
Compatibility shim for `<sys/types.h>` under nolibc.

## APIs, Types, and Functions
Includes `../types.h` and defines no additional APIs.

## Control Flow, State, and Persistence
No runtime control flow or state exists. It exposes nolibc's POSIX-ish typedefs and structs through the conventional include path.

## Dependencies and Integration
Depends on `types.h`. It integrates with portable code that includes system type definitions before other headers.

## Risks and Test Signals
Risks are incomplete typedef coverage compared with glibc and include-order conflicts if mixed with system libc headers. Test signals are compiling representative portable sources and checking every required typedef is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/uio.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/uio.h

## Purpose
Provides vectored I/O wrappers for nolibc.

## APIs, Types, and Functions
Includes Linux UIO definitions and defines `_sys_readv`/`readv` and `_sys_writev`/`writev`.

## Control Flow, State, and Persistence
Wrappers pass fd, iovec array, and count to the kernel and return byte counts through `__sysret`. State is in caller buffers and fd offsets updated by the kernel.

## Dependencies and Integration
Depends on `../sys.h`, `../types.h`, and Linux `struct iovec`. It integrates with stdio alternatives and protocols that naturally scatter/gather buffers.

## Risks and Test Signals
Risks include invalid iovec pointers, count overflow, partial reads/writes, and fd offset side effects. Test signals are pipe/file readv-writev round trips, partial write handling, invalid iovec errors, and large count rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/uio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/utsname.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/utsname.h

## Purpose
Provides `uname` support for nolibc.

## APIs, Types, and Functions
Defines `struct utsname` with Linux `_UTSNAME_LENGTH` fields and `_sys_uname`/`uname` wrappers.

## Control Flow, State, and Persistence
The wrapper fills caller-provided system-name fields from the kernel and translates errors. There is no persistent state.

## Dependencies and Integration
Depends on `../sys.h` and `<linux/utsname.h>`. It integrates with tools that report kernel and machine identity.

## Risks and Test Signals
Risks are structure length/layout mismatch with libc and callers assuming domainname availability semantics beyond this definition. Test signals are uname smoke tests, buffer field NUL termination checks, and comparison with libc `uname` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/utsname.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/wait.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/wait.h

## Purpose
Provides child-process wait wrappers and wait-status decoding for nolibc.

## APIs, Types, and Functions
Defines `_sys_waitid`, `waitid`, `waitpid`, and `wait`. Status macros such as `WIFEXITED` and `WEXITSTATUS` are supplied by `types.h`.

## Control Flow, State, and Persistence
`waitpid()` uses `wait4` when available or emulates through `waitid`, translating `siginfo_t` into traditional status words. `wait()` delegates to `waitpid(-1, ...)`. Persistent state is kernel child-process state consumed by wait operations.

## Dependencies and Integration
Depends on `../arch.h`, `../types.h`, `../sys.h`, and Linux wait/signal UAPI. It integrates with `fork`/`vfork` users and process-control tests.

## Risks and Test Signals
Risks include status-word emulation mistakes, option support differences, rusage omission in public `waitid`, and child reaping races in callers. Test signals are child exit/signal/stop/continue cases, `WNOHANG`, invalid pid/options, and architecture paths with and without native `wait4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/sys/wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/time.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/time.h

## Purpose
Implements POSIX time and timer wrappers for nolibc with explicit time64 checks.

## APIs, Types, and Functions
Defines time64 assertion macros, `_sys_clock_getres`/`clock_getres`, `_sys_clock_gettime`/`clock_gettime`, `_sys_clock_settime`/`clock_settime`, sleep helpers, `difftime`, `nanosleep`, `time`, POSIX timer create/delete/gettime/settime wrappers, and related `itimerspec` use.

## Control Flow, State, and Persistence
Wrappers choose native time64 syscalls where required, copy `timespec` and `itimerspec` values through caller buffers, and translate errors. `time()` calls `clock_gettime(CLOCK_REALTIME)` and optionally stores the seconds value. Timer wrappers persist state in kernel timer ids, not in userspace.

## Dependencies and Integration
Depends on `types.h`, `sys.h`, Linux time UAPI, and syscall availability. It integrates with `sys/time.h`, `timerfd.h`, sleeps, and tests needing clock/timer functionality.

## Risks and Test Signals
Risks include 32-bit time overflow, unsupported legacy syscalls, clock id permission errors, interrupted sleeps, and timer id type mismatch. Test signals are realtime/monotonic gettime, nanosleep interruption, timer create/set/get/delete, 32-bit time64 builds, and invalid clock id paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/types.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/types.h

## Purpose
Defines nolibc's POSIX/Linux structure and constant surface shared by syscall wrappers.

## APIs, Types, and Functions
Defines `struct timespec`, `struct timeval`, file type and permission macros, directory entry type constants, `PATH_MAX`, `MAXPATHLEN`, `MAP_FAILED`, seek constants, reboot command aliases, wait-status macros, `EXIT_SUCCESS`/`EXIT_FAILURE`, `struct linux_dirent64`, nolibc `struct stat`, `clockid_t`, `timer_t`, and `container_of`.

## Control Flow, State, and Persistence
There is no executable control flow. The header fixes ABI layouts for stat, dirent, time, wait, and container calculations. Persistent meaning is compile-time layout and constant values shared with kernel syscalls.

## Dependencies and Integration
Depends on `std.h`, Linux `mman.h`, `stat.h`, `time_types.h`, `wait.h`, and selected time UAPI headers. It integrates with nearly every syscall and compatibility header.

## Risks and Test Signals
Risks include struct layout drift from kernel expectations, 32-bit time compatibility, `container_of` misuse, and incomplete libc constant coverage. Test signals are sizeof/offsetof checks for `stat`, dirent parsing with `getdents64`, time wrapper tests, wait-status decoding, and compile checks for all constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/unistd.h -->
# sources/distributed-fs/ceph-client/tools/include/nolibc/unistd.h

## Purpose
Provides unistd-style constants and small wrappers not housed in the main syscall header.

## APIs, Types, and Functions
Defines standard fd constants `STDIN_FILENO`, `STDOUT_FILENO`, `STDERR_FILENO`, access mode constants `F_OK`, `X_OK`, `W_OK`, `R_OK`, `_sys_faccessat`, `faccessat`, `access`, `msleep`, `sleep`, `usleep`, and `tcsetpgrp`.

## Control Flow, State, and Persistence
`access` delegates to `faccessat`; sleep helpers build `timespec` values and call `nanosleep`, returning remaining seconds for `sleep` semantics; `tcsetpgrp` issues the relevant terminal ioctl. No persistent state is held outside kernel fd/process/session state.

## Dependencies and Integration
Depends on `sys.h`, `time.h`, `fcntl`/AT constants, and ioctl definitions. It integrates with portable code expecting common `<unistd.h>` names under nolibc.

## Risks and Test Signals
Risks are incomplete unistd coverage, sleep interruption rounding, access checks differing from open-time permissions, and terminal ioctl availability. Test signals are access success/failure cases, interrupted and full sleeps, standard fd use, and terminal process-group tests where a tty is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/nolibc/unistd.h -->
