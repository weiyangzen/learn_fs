<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/current.h

Purpose: Defines how s390 obtains the current task pointer.

Important APIs/types/functions: `get_current()` and `current` macro using lowcore/predefined register state. Source-visible declarations include: #define _S390_CURRENT_H; struct task_struct;; static __always_inline struct task_struct *get_current(void); unsigned long ptr, lc_current;; #define current get_current().

Control flow: Hot paths read the current task from s390 lowcore or register-backed storage.

State and persistence behavior: State is per-CPU current task pointer maintained by context switch.

Dependencies and integration points: Direct includes are #include <asm/lowcore.h>, #include <asm/machine.h>. Integrated with Integrates scheduler, lowcore layout, thread_info, and all generic code using `current`..

Risks: The access sequence must match lowcore offsets and context-switch updates or every task-local access is unsafe.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 35 lines, 821 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/current.h -->
