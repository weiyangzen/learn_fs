<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_64.h

## Purpose
This header defines the SPARC64 ELF ABI, including 64-bit execution, 32-bit compat execution, hardware capabilities, vDSO auxv entries, and process personality setup.

## Important APIs, Types, and Functions
It defines relocation constants, `HWCAP_SPARC_*` and `AV_SPARC_*` bits including crypto and ADI, native and compat `ELF_NGREG` layouts, `elf_check_arch`, `compat_elf_check_arch`, `ELF_ET_DYN_BASE`, `COMPAT_ELF_ET_DYN_BASE`, `ELF_HWCAP`, `SET_PERSONALITY`, `ARCH_DLINFO`, `ARCH_HAS_SETUP_ADDITIONAL_PAGES`, and `arch_setup_additional_pages()`.

## Control Flow
The ELF loader uses these definitions to accept SPARCV9/native and SPARC compat binaries, set 32-bit personality when needed, publish hardware/vDSO auxv entries, and install additional vDSO pages.

## State and Persistence Behavior
The header defines ABI constants. Runtime state includes process personality, auxv contents, and vDSO mapping created elsewhere.

## Dependencies and Integration Points
It depends on processor, ptrace, spitfire, and ADI headers. It integrates with binfmt_elf, compat, vDSO, hardware capability detection, ptrace, and core dumping.

## Risks
Hardware capability bits are visible ABI; changing them can break optimized libc/crypto dispatch. Wrong compat personality setup breaks 32-bit user programs.

## Test Signals
Run native and 32-bit SPARC ELF binaries, inspect auxv, test vDSO mapping, core dumps, PIE base placement, and ADI/crypto HWCAP exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_64.h -->
