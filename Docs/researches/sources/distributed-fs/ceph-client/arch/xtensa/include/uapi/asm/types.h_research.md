<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/types.h

Purpose: defines Xtensa UAPI integer type inclusion and unsigned-long literal helpers. It includes `asm-generic/int-ll64.h` and provides `__XTENSA_UL` and `__XTENSA_UL_CONST` variants for assembler vs C.

Control flow is preprocessor-only. State is ABI type sizing and constant expression typing in exported headers. Dependencies include generic int-ll64 type definitions and assembler/C compilation contexts. Integration points are all UAPI headers needing fixed-width integer types or Xtensa unsigned long constants, including page/MM constants. Risks are literal suffix misuse in assembler, type-size ABI mismatches, and empty non-assembler extension block suggesting future expansion points. Test signals include headers_install, C and assembler preprocessing, userspace compile tests, and ABI type-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/types.h -->
