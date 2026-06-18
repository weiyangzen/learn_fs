<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-extable.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-extable.h

Purpose: Defines s390 assembly exception-table entry encodings and helper macros.

Important APIs/types/functions: `EX_TYPE_*`, `EX_DATA_*` fields, `__EX_TABLE()`, `EX_TABLE()`, user-access fixup variants, zeropad, FPC, and MVCOS fixups. Source-visible declarations include: #define __ASM_EXTABLE_H; #define EX_TYPE_NONE 0; #define EX_TYPE_FIXUP 1; #define EX_TYPE_BPF 2; #define EX_TYPE_UA_FAULT 3; #define EX_TYPE_UA_LOAD_REG 5; #define EX_TYPE_UA_LOAD_REGPAIR 6; #define EX_TYPE_ZEROPAD 7; #define EX_TYPE_FPC 8; #define EX_TYPE_UA_MVCOS_TO 9.

Control flow: Assembly sites emit relative fault/target pairs plus encoded type and register metadata into exception table sections; fault handlers decode them to recover from expected traps.

State and persistence behavior: State is linker-collected exception-table metadata used at runtime for fault fixups.

Dependencies and integration points: Direct includes are #include <linux/stringify.h>, #include <linux/bits.h>, #include <asm/asm-const.h>. Integrated with Integrates user access, FPU control validation, BPF/extable handlers, AP/DIAG probing, and low-level assembly..

Risks: The encoded register fields must match handler decoding. Bad entries can recover to wrong PCs or corrupt registers after faults.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 95 lines, 3742 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-extable.h -->
