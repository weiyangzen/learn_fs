<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/bug.h

Purpose: Defines s390 BUG/WARN trap emission and bug-table metadata.

Important APIs/types/functions: `BUG()`, `__WARN_FLAGS()`, verbose bug entries, monitor-call trap encodings, vararg warning helpers, and `__WARN_trap()` plumbing. Source-visible declarations include: #define _ASM_S390_BUG_H; #define MONCODE_BUG _AC(0, U); #define MONCODE_BUG_ARG _AC(1, U); #define __BUG_ENTRY_VERBOSE(format, file, line) \; #define __BUG_ENTRY_VERBOSE(format, file, line); #define WARN_CONDITION_STR(cond_str) cond_str; #define WARN_CONDITION_STR(cond_str) ""; #define __BUG_ENTRY(format, file, line, flags, size) \; #define __BUG_ASM(cond_str, flags) \; #define BUG() \.

Control flow: Macros emit bug table records and inline trap/monitor-call sequences; warning paths package format arguments for runtime decoding.

State and persistence behavior: State is linker-collected bug-table metadata and transient pt_regs/argument records during traps.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/const.h>, #include <asm-generic/bug.h>. Integrated with Integrates generic bug handling, traps, lockdep/warnings, module bug tables, and optional verbose file/line records..

Risks: Trap encodings and metadata sizes must match runtime bug decoding. Format-argument capture is ABI-sensitive for warning printing.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 129 lines, 3398 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bug.h -->
