<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/extable.h

Purpose: Defines runtime exception-table entry layout and fixup helpers.

Important APIs/types/functions: `struct exception_table_entry`, amode31 extable bounds, `extable_fixup()`, `swap_ex_entry_fixup()`, `ex_handler_bpf()`, and `fixup_exception()`. Source-visible declarations include: #define __S390_EXTABLE_H; struct exception_table_entry; int insn, fixup;; extern struct exception_table_entry *__start_amode31_ex_table;; extern struct exception_table_entry *__stop_amode31_ex_table;; static inline unsigned long extable_fixup(const struct exception_table_entry *x); #define ARCH_HAS_RELATIVE_EXTABLE; static inline void swap_ex_entry_fixup(struct exception_table_entry *a,; struct exception_table_entry *b,; struct exception_table_entry tmp,.

Control flow: Fault handling searches relative extable entries, decodes the fixup address and type/data fields, and either applies specialized handlers or redirects execution.

State and persistence behavior: State is linker-built exception tables and transient pt_regs during fault recovery.

Dependencies and integration points: Direct includes are #include <asm/ptrace.h>, #include <linux/compiler.h>. Integrated with Integrates user access, BPF, amode31 code, module extables, sorting, and low-level fault handling..

Risks: Relative offsets and swap logic must preserve sort order and fixup semantics across modules and built-in code.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 72 lines, 1924 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extable.h -->
