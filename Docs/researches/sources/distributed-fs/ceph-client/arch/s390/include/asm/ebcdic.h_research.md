<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ebcdic.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ebcdic.h

Purpose: Declares EBCDIC/ASCII conversion tables and inline conversion helpers.

Important APIs/types/functions: `_ascebc*`, `_ebcasc*`, `_ebc_tolower`, `_ebc_toupper`, `codepage_convert()`, and `ASCEBC/EBCASC` macros. Source-visible declarations include: #define _EBCDIC_H; extern __u8 _ascebc_500[256]; /* ASCII -> EBCDIC 500 conversion table */; extern __u8 _ebcasc_500[256]; /* EBCDIC 500 -> ASCII conversion table */; extern __u8 _ascebc[256]; /* ASCII -> EBCDIC conversion table */; extern __u8 _ebcasc[256]; /* EBCDIC -> ASCII conversion table */; extern __u8 _ebc_tolower[256]; /* EBCDIC -> lowercase */; extern __u8 _ebc_toupper[256]; /* EBCDIC -> uppercase */; static inline void; #define ASCEBC(addr,nr) codepage_convert(_ascebc, addr, nr); #define EBCASC(addr,nr) codepage_convert(_ebcasc, addr, nr).

Control flow: Conversion helpers walk a byte buffer in place and translate each byte through the selected 256-entry table.

State and persistence behavior: Persistent state is read-only conversion tables defined elsewhere; caller buffers are modified in place.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with Integrates hypfs, IPL/firmware strings, device identifiers, and z/VM/firmware text handling..

Risks: Callers must pass correct buffer lengths because conversion is in-place and binary data would be mangled.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 47 lines, 1431 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ebcdic.h -->
