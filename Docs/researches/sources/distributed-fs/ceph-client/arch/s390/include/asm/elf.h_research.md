<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/elf.h

Purpose: Defines s390 ELF relocation constants, HWCAP bits, core/register ABI types, and executable personality setup.

Important APIs/types/functions: `R_390_*` relocations, HWCAP bit definitions, ELF class/data/arch macros, greg/fpreg types, `ELF_PLAT_INIT`, `ELF_ET_DYN_BASE`, `ARCH_DLINFO`, and `arch_setup_additional_pages()`. Source-visible declarations include: #define __ASMS390_ELF_H; #define R_390_NONE 0 /* No reloc. */; #define R_390_8 1 /* Direct 8 bit. */; #define R_390_12 2 /* Direct 12 bit. */; #define R_390_16 3 /* Direct 16 bit. */; #define R_390_32 4 /* Direct 32 bit. */; #define R_390_PC32 5 /* PC relative 32 bit. */; #define R_390_GOT12 6 /* 12 bit GOT offset. */; #define R_390_GOT32 7 /* 32 bit GOT offset. */; #define R_390_PLT32 8 /* 32 bit PC relative PLT address. */.

Control flow: The ELF loader validates machine type, initializes registers, chooses randomized mapping bases, exports auxv hardware/platform data, and maps additional vDSO pages.

State and persistence behavior: Persistent ABI state includes auxv HWCAP/platform strings, process personality, mapped vDSO, and core dump register layout.

Dependencies and integration points: Direct includes are #include <asm/ptrace.h>, #include <asm/syscall.h>, #include <asm/user.h>, #include <linux/sched/mm.h>	/* for task_struct */, #include <asm/mmu_context.h>. Integrated with Integrates binfmt_elf, dynamic linker ABI, ptrace/core dumps, vDSO, ASLR, and CPU feature discovery..

Risks: Relocation numbers and HWCAP bits are user ABI; changing them breaks loaders, libc, or feature dispatch.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 245 lines, 9476 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/elf.h -->
