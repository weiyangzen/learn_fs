<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/alternative.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/alternative.h

Purpose: Defines the s390 alternative-instruction metadata format and assembly macros for CPU/facility/speculation patching.

Important APIs/types/functions: `struct alt_instr`, `ALT_FACILITY()`, `ALT_FEATURE()`, `ALT_SPEC()`, `apply_alternative_instructions()`, `ALTERNATIVE`, and `ALTERNATIVE_2` C and assembler macros. Source-visible declarations include: #define _ASM_S390_ALTERNATIVE_H; #define ALT_CTX_EARLY 1; #define ALT_CTX_LATE 2; #define ALT_CTX_ALL (ALT_CTX_EARLY | ALT_CTX_LATE); #define ALT_TYPE_FACILITY 0; #define ALT_TYPE_FEATURE 1; #define ALT_TYPE_SPEC 2; #define ALT_DATA_SHIFT 0; #define ALT_TYPE_SHIFT 20; #define ALT_CTX_SHIFT 28.

Control flow: Compile-time macros place old instructions in text, replacement bytes in `.altinstr_replacement`, and descriptors in `.altinstructions`; early or late patching walks descriptor ranges and overwrites text when feature predicates match.

State and persistence behavior: State is linker-emitted patch metadata and patched kernel text; replacements persist for the running image.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/stddef.h>, #include <linux/stringify.h>. Integrated with Integrates CPU facility probing, decompressor and early kernel patching, speculation mitigations, assembly code, and runtime text patching..

Risks: Descriptor length, alignment, and context bits are text-patching ABI. Bad alternatives can execute partial instructions or apply too early/late.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 238 lines, 7424 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/alternative.h -->
