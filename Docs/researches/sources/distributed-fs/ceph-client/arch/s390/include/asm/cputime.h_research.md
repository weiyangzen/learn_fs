<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cputime.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cputime.h

Purpose: Maps s390 CPU time accounting to TOD-clock nanoseconds and declares idle IRQ accounting.

Important APIs/types/functions: `cputime_to_nsecs()` and `account_idle_time_irq()`. Source-visible declarations include: #define _S390_CPUTIME_H; #define cputime_to_nsecs(cputime) tod_to_ns(cputime); void account_idle_time_irq(void);.

Control flow: Generic scheduler accounting converts hardware cputime through `tod_to_ns()` and calls the IRQ idle accounting hook.

State and persistence behavior: State is scheduler/accounting counters maintained elsewhere.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <asm/timex.h>. Integrated with Integrates TOD clock helpers, scheduler CPU accounting, and interrupt entry paths..

Risks: Time conversion errors affect accounting, profiling, and cgroup CPU usage.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 21 lines, 393 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cputime.h -->
