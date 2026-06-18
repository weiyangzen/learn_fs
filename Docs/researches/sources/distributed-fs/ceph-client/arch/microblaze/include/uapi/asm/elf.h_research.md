# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/elf.h

## Purpose

defines user-visible ELF machine constants, relocation numbers, and register/core-dump layouts

## Important APIs, Types, and Functions

Source read size: 123 lines, 3331 bytes. Includes: `linux/elf-em.h`, `asm/ptrace.h`,
`asm/byteorder.h`. Declared functions: `Copyright`. Key macros/defines:
`_UAPI_ASM_MICROBLAZE_ELF_H`, `EM_MICROBLAZE_OLD`, `ELF_ARCH`, `elf_check_arch(x)`, `ELF_CLASS`,
`ELF_GREG_T`, `ELF_NGREG`, `ELF_GREGSET_T`, `ELF_FPREGSET_T`, `ELF_NFPREG`, `ELF_ET_DYN_BASE`,
`ELF_DATA`, `ELF_EXEC_PAGESIZE`, `ELF_CORE_COPY_REGS(_dest, _regs)`, `ELF_HWCAP`, `ELF_PLATFORM`,
`ELF_PLAT_INIT(_r, _f)`. Types visible in this file: `elf_greg_t`, `elf_fpreg_t`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
